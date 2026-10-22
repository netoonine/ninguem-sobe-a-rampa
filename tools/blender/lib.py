"""Biblioteca comum dos sprites do Bastiao das Areias (estilo "soft relaxante"), usada por cada familia de torre.

Cada familia (tools/blender/torre_<nome>.py) declara torres, tripulacao, pecas que giram e projeteis, e chama
run_family(). Tudo e deterministico: modelos, materiais, luz, camera e animacoes saem do codigo.

Uso:
  Blender -b -P tools/blender/torre_<nome>.py -- render <pasta_saida> [conjuntos...]
  No Blender aberto: exec(open('<caminho>/tools/blender/torre_<nome>.py').read()); show()

Convencoes (as mesmas da Torre de Arqueiros, tools/blender/arqueiros.py):
  - Z para cima, a camera olha para +Y (frente da torre = -Y), elevacao de 35 graus, ortografica.
  - 1 unidade do Blender (BU) = 41 unidades do jogo; renderiza a 3 px por unidade do jogo.
  - Cada conjunto tem um objeto raiz; tudo dentro dele e filho da raiz e guarda o nome do conjunto em o['set'].

Passes de cada torre (o jogo recompoe por cima):
  base   1 quadro com tudo o que fica parado
  anim   N quadros so com as pecas que mexem (tecido, pas, orbes); o resto vira recorte (holdout)
  front  o que fica na frente da tripulacao
  glow   so a luz (lanternas, braseiros, cristais), somada no jogo conforme o clima
"""
import bpy, bmesh, math, random, os, sys, json
from mathutils import Vector, Matrix, Euler

TAU = math.tau
ELEV = math.radians(35)
GAME_PER_BU = 41.0
PX_PER_GAME = 3.0
LIFT = 0.08            # a plataforma de pedra tem topo em z = 0.15: a torre sobe junto
CREW_BOOST = 1.3       # tripulacao desenhada 30% maior que a escala da torre (exagero do genero)
PROJ_PX = 2.0          # projeteis renderizados em 2x (sao girados e reduzidos no jogo)
ANIM_N = 16            # quadros do loop das pecas que mexem
ST = {'px': GAME_PER_BU * PX_PER_GAME, 'coll': None}
BUILT = {}


# ---------------------------------------------------------------- utilidades
def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)


R = random.Random(7)
CLOTH = {}      # nome do objeto -> (coords base, funcao(co, fase) -> co)
SETS = {}       # conjunto -> objeto raiz
ANIM = {}       # conjunto -> funcao(modo, quadro, extra)


def coll_for(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        ST["coll"].children.link(c)
    return c


def new_obj(name, me, root, mats, front=False, bev=0.0, seg=3, angle=40, smooth=True, sharp=None):
    o = bpy.data.objects.new(name, me)
    root.users_collection[0].objects.link(o)
    o.parent = root
    o['set'] = root['set']
    if front:
        o['front'] = 1
    for m in mats:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
        try:
            me.set_sharp_from_angle(angle=math.radians(sharp if sharp is not None else angle))
        except Exception:
            pass
    if bev > 0:
        md = o.modifiers.new('Bevel', 'BEVEL')
        md.width = bev
        md.segments = seg
        md.limit_method = 'ANGLE'
        md.angle_limit = math.radians(angle)
        md.harden_normals = True
    return o


def bm_to_obj(bm, name, root, mats, **kw):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return new_obj(name, me, root, mats, **kw)


def mtx(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    return Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*scale, 1))


def box(root, name, size, loc, rot=(0, 0, 0), m=None, bev=0.02, front=False, seg=3):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((*size, 1)))
    o = bm_to_obj(bm, name, root, [m], front=front, bev=bev, seg=seg, angle=35)
    o.location = loc
    o.rotation_euler = rot
    return o


def cyl(root, name, r1, depth, loc, r2=None, rot=(0, 0, 0), m=None, v=24, bev=0.02, front=False, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=v, radius1=r1,
                          radius2=r1 if r2 is None else r2, depth=depth)
    o = bm_to_obj(bm, name, root, [m], front=front, bev=bev, angle=50)
    o.location = loc
    o.rotation_euler = rot
    return o


def sphere(root, name, r, loc, scale=(1, 1, 1), m=None, seg=20, front=False, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r,
                              matrix=Matrix.Diagonal((*scale, 1)))
    o = bm_to_obj(bm, name, root, [m], front=front, angle=80)
    o.location = loc
    o.rotation_euler = rot
    return o


def tube_into(bm, pts, r, segs=8, closed=False, caps=True, rfun=None, mat_index=0):
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    prev = None
    for i, p in enumerate(pts):
        if closed:
            t = (pts[(i + 1) % n] - pts[(i - 1) % n])
        else:
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        t = t.normalized() if t.length > 1e-9 else Vector((0, 0, 1))
        if prev is None:
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            nn = t.cross(ref).normalized()
        else:
            nn = prev - t * prev.dot(t)
            nn = nn.normalized() if nn.length > 1e-9 else t.cross(Vector((0, 0, 1))).normalized()
        b = t.cross(nn)
        prev = nn
        rr = rfun(i / max(1, n - 1)) if rfun else r
        rings.append([bm.verts.new(p + (nn * math.cos(a) + b * math.sin(a)) * rr)
                      for a in [TAU * k / segs for k in range(segs)]])
    last = n if closed else n - 1
    for i in range(last):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(segs):
            f = bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
            f.material_index = mat_index
    if caps and not closed:
        f = bm.faces.new(list(reversed(rings[0])))
        f.material_index = mat_index
        f = bm.faces.new(rings[-1])
        f.material_index = mat_index
    return rings


def tube(root, name, pts, r, m, segs=8, closed=False, rfun=None, front=False, smooth=True):
    bm = bmesh.new()
    tube_into(bm, pts, r, segs, closed, rfun=rfun)
    return bm_to_obj(bm, name, root, [m], front=front, angle=75)


def ring_pts(center, radius, n=24, axis='Z', a0=0, a1=TAU, closed=True):
    c = Vector(center)
    out = []
    cnt = n if closed else n + 1
    for k in range(cnt):
        a = a0 + (a1 - a0) * k / n
        if axis == 'Z':
            out.append(c + Vector((math.cos(a), math.sin(a), 0)) * radius)
        elif axis == 'Y':
            out.append(c + Vector((math.cos(a), 0, math.sin(a))) * radius)
        else:
            out.append(c + Vector((0, math.cos(a), math.sin(a))) * radius)
    return out


def torus(root, name, center, R_, r, m, axis='Z', n=28, segs=8, front=False):
    return tube(root, name, ring_pts(center, R_, n, axis), r, m, segs=segs, closed=True, front=front)


def between(o, p1, p2):
    """Posiciona um objeto de comprimento 1 ao longo de Z entre dois pontos."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    o.location = p1
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.scale = (1, 1, max(d.length, 1e-4))


# ---------------------------------------------------------------- materiais
_M = {}


def mat(key, hexcol, rough=0.72, metal=0.0, var=0.06, bump=0.12, emit=0.0, stripes=None, border=None, sheen=0.0):
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(key)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next((n for n in N if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        N.clear()
        bsdf = N.new('ShaderNodeBsdfPrincipled')
        outn = N.new('ShaderNodeOutputMaterial')
        L.new(bsdf.outputs['BSDF'], outn.inputs['Surface'])
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if sheen:
        bsdf.inputs['Sheen Weight'].default_value = sheen
    if stripes:
        # listras ao longo de X local (toldos): stripes = (freq, corA, corB)
        tc = N.new('ShaderNodeTexCoord')
        sep = N.new('ShaderNodeSeparateXYZ')
        mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = stripes[0]
        fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'
        ramp = N.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        ramp.color_ramp.elements[0].color = lin(stripes[1])
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = lin(stripes[2])
        L.new(tc.outputs['Object'], sep.inputs[0])
        L.new(sep.outputs['X'], mul.inputs[0])
        L.new(mul.outputs[0], fr.inputs[0])
        L.new(fr.outputs[0], ramp.inputs['Fac'])
        col_out = ramp.outputs['Color']
    else:
        rgb = N.new('ShaderNodeRGB')
        rgb.outputs[0].default_value = lin(hexcol)
        col_out = rgb.outputs[0]
    hsv = N.new('ShaderNodeHueSaturation')
    oi = N.new('ShaderNodeObjectInfo')
    mr = N.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 1 - var
    mr.inputs['To Max'].default_value = 1 + var
    L.new(oi.outputs['Random'], mr.inputs['Value'])
    L.new(mr.outputs['Result'], hsv.inputs['Value'])
    L.new(col_out, hsv.inputs['Color'])
    L.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    if emit:
        bsdf.inputs['Emission Color'].default_value = lin(hexcol)
        bsdf.inputs['Emission Strength'].default_value = emit
    if bump:
        nz = N.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 22
        nz.inputs['Detail'].default_value = 3
        bp = N.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = bump
        bp.inputs['Distance'].default_value = 0.02
        L.new(nz.outputs['Fac'], bp.inputs['Height'])
        L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    _M[key] = m
    return m


def palette():
    return {
        'sand': mat('areia', '#e6c690', rough=0.9, var=0.03, bump=0.25),
        'stone': mat('pedra', '#bba98e', rough=0.85, var=0.12, bump=0.3),
        'sandstone': mat('arenito', '#e0ab6c', rough=0.82, var=0.08, bump=0.22),
        'sandstone_l': mat('arenito_claro', '#ecc58e', rough=0.82, var=0.05, bump=0.2),
        'mortar': mat('argamassa', '#946640', rough=0.95, var=0.0, bump=0.1),
        'wood': mat('madeira', '#7a4a2a', rough=0.75, var=0.1, bump=0.3),
        'wood_l': mat('madeira_clara', '#ab7442', rough=0.72, var=0.1, bump=0.3),
        'rope': mat('corda', '#dcc290', rough=0.9, var=0.05, bump=0.4),
        'teal': mat('teal', '#23968f', rough=0.8, var=0.04, bump=0.08, sheen=0.4),
        'cream': mat('creme', '#f4e7c9', rough=0.85, var=0.03, bump=0.08, sheen=0.4),
        'stripes': mat('toldo', '#23968f', rough=0.85, var=0.0, bump=0.06, stripes=(3.6, '#f4e7c9', '#23968f'), sheen=0.4),
        'gold': mat('ouro', '#e8b84a', rough=0.35, metal=0.65, var=0.03, bump=0.05),
        'iron': mat('ferro', '#4a4440', rough=0.55, metal=0.5, var=0.05, bump=0.1),
        'steel': mat('aco', '#cfd6db', rough=0.3, metal=0.8, var=0.02, bump=0.02),
        'terracotta': mat('terracota', '#c86d42', rough=0.8, var=0.08, bump=0.2),
        'dark': mat('escuro', '#3a2412', rough=0.9, var=0.0, bump=0.0),
        'glow': mat('lanterna', '#ffc46b', rough=0.5, var=0.0, bump=0.0, emit=4.0),
        'skin': mat('pele', '#c98d5e', rough=0.7, var=0.05, bump=0.02),
        'tunic': mat('tunica', '#dcc39a', rough=0.85, var=0.03, bump=0.08, sheen=0.3),
        'hood': mat('capuz', '#cdb187', rough=0.85, var=0.03, bump=0.08, sheen=0.3),
        'leather': mat('couro', '#8b5a35', rough=0.65, var=0.05, bump=0.15),
        'pants': mat('calca', '#5a3b26', rough=0.85, var=0.03, bump=0.05),
        'bronze': mat('bronze', '#b8773d', rough=0.35, metal=0.7, var=0.03, bump=0.05),
        'eye': mat('olho', '#2a1a10', rough=0.4, var=0.0, bump=0.0),
        'plume': mat('pluma', '#1f8f8a', rough=0.9, var=0.0, bump=0.1, sheen=0.6),
    }


# ---------------------------------------------------------------- tecido (bandeiras, toldos)
def cloth_grid(root, name, w, h, nx, ny, mats, shape=None, front=False, thick=0.018):
    """Malha retangular no plano XZ (x de 0 a w, z de 0 a -h). shape(u, v, co) ajusta cada vertice."""
    bm = bmesh.new()
    verts = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            co = Vector((u * w, 0, -v * h))
            if shape:
                co = shape(u, v, co)
            row.append(bm.verts.new(co))
        verts.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
    o = bm_to_obj(bm, name, root, mats, front=front, angle=89)
    if thick:
        sm = o.modifiers.new('Espessura', 'SOLIDIFY')
        sm.thickness = thick
        sm.offset = 0
    return o


def register_cloth(o, fn):
    o['anim'] = 1
    CLOTH[o.name] = ([v.co.copy() for v in o.data.vertices], fn)


def apply_cloth(phase):
    for name, (base, fn) in CLOTH.items():
        o = bpy.data.objects.get(name)
        if not o:
            continue
        me = o.data
        for v, b in zip(me.vertices, base):
            v.co = fn(b, phase)
        me.update()


def flag_wave(length, amp=0.07, cycles=1, waves=1.3, droop=0.02):
    """Bandeirola presa em x=0, balanca em Y. fase em [0,1) -> loop perfeito."""
    def fn(co, ph):
        w = max(0.0, co.x / length) ** 1.3
        a = TAU * (cycles * ph - waves * co.x / length)
        return Vector((co.x - w * 0.02 * (1 + math.cos(a)), co.y + amp * w * math.sin(a), co.z - droop * w * (1 - math.cos(a)) * 0.5))
    return fn


def hang_wave(height, amp=0.035, axis='Y', cycles=1, waves=0.8, top=0.0):
    """Tecido pendurado pelo topo (z = top): a ponta de baixo balanca."""
    def fn(co, ph):
        w = max(0.0, (top - co.z) / height) ** 1.6
        a = TAU * (cycles * ph + waves * (top - co.z) / height + co.x * 0.7)
        off = amp * w * math.sin(a)
        if axis == 'Y':
            return Vector((co.x + off * 0.25, co.y + off, co.z))
        return Vector((co.x + off, co.y + off * 0.3, co.z))
    return fn


# ---------------------------------------------------------------- pecas comuns
def make_root(name, set_name, coll):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.3
    coll.objects.link(e)
    e['set'] = set_name
    SETS[set_name] = e
    return e


def plot(root, P, tag):
    """Lote da mata (o mesmo em todas as torres e no lote vazio): deck redondo de tabuas sobre uma base de terra,
    anel de pedras de rio arredondadas, tufos de capim e uma samambaia atras. Topo em z = 0.15."""
    made = []

    def mk(o):
        o['plot'] = 1
        made.append(o)
        return o
    earth = mat('terra_lote', '#6a4a32', rough=0.95, var=0.06, bump=0.35)
    plank = mat('tabua_lote', '#b27a48', rough=0.78, var=0.16, bump=0.3)
    plank2 = mat('tabua_lote2', '#c08a54', rough=0.78, var=0.14, bump=0.3)
    beam = mat('viga_lote', '#7a4e2e', rough=0.8, var=0.1, bump=0.3)
    stone = mat('pedra_rio_lote', '#a7a397', rough=0.8, var=0.16, bump=0.25)
    stone2 = mat('pedra_rio_lote2', '#8a877c', rough=0.8, var=0.14, bump=0.25)
    grass = mat('capim_lote', '#6f9f40', rough=0.9, var=0.15, bump=0.1)
    rr = random.Random(11)
    mk(cyl(root, tag + '_rampa', 0.98, 0.05, (0, 0, 0.025), r2=0.88, m=earth, v=48, bev=0.02))
    mk(cyl(root, tag + '_viga', 0.76, 0.09, (0, 0, 0.075), m=beam, v=40, bev=0.02))
    # tabuas paralelas cortadas no circulo (topo em 0.15)
    n = 9
    R = 0.74
    w = 2 * R / n
    for k in range(n):
        y = -R + w * (k + 0.5)
        half = math.sqrt(max(0.0, R * R - y * y)) * 0.98
        mk(box(root, f'{tag}_tabua{k}', (half * 2, w * 0.9, 0.045), (rr.uniform(-0.01, 0.01), y, 0.128 + rr.uniform(-0.003, 0.003)),
               rot=(0, 0, rr.uniform(-0.01, 0.01)), m=plank if k % 2 else plank2, bev=0.012))
        for sx in (-1, 1):
            mk(sphere(root, f'{tag}_prego{k}{sx}', 0.012, (sx * half * 0.8, y, 0.152), m=P['iron'], seg=6))
    # anel de pedras de rio
    m = 20
    for k in range(m):
        a = TAU * k / m + rr.uniform(-0.04, 0.04)
        r = 0.86 + rr.uniform(-0.015, 0.015)
        mk(sphere(root, f'{tag}_pedra{k}', rr.uniform(0.085, 0.11), (r * math.cos(a), r * math.sin(a), 0.06), scale=(1.3, 1.0, 0.62),
                  m=stone if k % 3 else stone2, seg=14, rot=(0, 0, a + rr.uniform(-0.3, 0.3))))
    # capim no pe da plataforma (nunca na frente, para nao cobrir a torre)
    for k, ang in enumerate((150, 205, 30, 330, 100, 75)):
        a = math.radians(ang + rr.uniform(-10, 10))
        cx, cy = 0.97 * math.cos(a), 0.97 * math.sin(a)
        for j in range(5):
            b = rr.uniform(0, TAU)
            tip = (cx + 0.07 * math.cos(b), cy + 0.07 * math.sin(b), 0.12 + rr.uniform(0, 0.08))
            mk(tube(root, f'{tag}_capim{k}_{j}', [(cx + 0.015 * math.cos(b), cy + 0.015 * math.sin(b), 0.0), tip], 0.014, grass,
                    segs=5, rfun=lambda t: 0.016 * (1 - t) + 0.002))
    return made


def lantern(root, name, P, loc, hang=0.0):
    x, y, z = loc
    if hang:
        tube(root, name + '_fio', [(x, y, z + hang), (x, y, z + 0.06)], 0.006, P['iron'], segs=6)
    box(root, name + '_topo', (0.08, 0.08, 0.025), (x, y, z + 0.055), m=P['iron'], bev=0.008)
    box(root, name + '_vidro', (0.06, 0.06, 0.08), (x, y, z), m=P['glow'], bev=0.01)
    box(root, name + '_base', (0.08, 0.08, 0.02), (x, y, z - 0.05), m=P['iron'], bev=0.006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tube(root, f'{name}_haste{sx}{sy}', [(x + sx * 0.035, y + sy * 0.035, z - 0.05), (x + sx * 0.035, y + sy * 0.035, z + 0.05)], 0.006, P['iron'], segs=5)


def arrows_bundle(root, name, P, base, n=7, spread=0.06, length=0.32, lean=0.18, seed=3):
    rr = random.Random(seed)
    bx, by, bz = base
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.3, 0.3)
        d = spread * rr.uniform(0.3, 1.0)
        p0 = Vector((bx + d * math.cos(a), by + d * math.sin(a), bz))
        tip = p0 + Vector((math.cos(a) * lean * d * 3, math.sin(a) * lean * d * 3, length))
        tube(root, f'{name}_haste{k}', [p0, tip], 0.007, P['wood_l'], segs=5)
        dirv = (tip - p0).normalized()
        cone = cyl(root, f'{name}_pena{k}', 0.022, 0.07, tip - dirv * 0.03, r2=0.0, m=P['cream'] if k % 2 else P['teal'], v=4, bev=0)
        cone.rotation_euler = dirv.to_track_quat('Z', 'Y').to_euler()


def clay_pot(root, name, P, loc, s=1.0):
    x, y, z = loc
    sphere(root, name + '_bojo', 0.08 * s, (x, y, z + 0.075 * s), scale=(1, 1, 0.95), m=P['terracotta'], seg=18)
    cyl(root, name + '_gargalo', 0.04 * s, 0.06 * s, (x, y, z + 0.16 * s), r2=0.05 * s, m=P['terracotta'], v=16, bev=0.006)


def barrel(root, name, P, loc, r=0.11, h=0.22):
    x, y, z = loc
    cyl(root, name, r, h, (x, y, z + h / 2), m=P['wood_l'], v=20, bev=0.015)
    for k, zz in enumerate((0.25, 0.75)):
        torus(root, f'{name}_aro{k}', (x, y, z + h * zz), r + 0.004, 0.009, P['iron'], n=24, segs=6)


def block_ring(root, tag, P, r_bot, r_top, z0, z1, rows, per_row, depth=0.15, gap=0.014, skip=None, m=None, bev=0.028):
    m = m or P['sandstone']
    h = (z1 - z0) / rows
    rr = random.Random(hash(tag) & 0xffff)
    for i in range(rows):
        zc = z0 + h * (i + 0.5)
        f = (zc - z0) / (z1 - z0)
        r = r_bot + (r_top - r_bot) * f
        off = (i % 2) * 0.5
        for j in range(per_row):
            a = TAU * (j + off) / per_row - math.pi / 2
            if skip and skip(a, zc):
                continue
            arc = TAU * r / per_row - gap
            out = rr.uniform(-0.008, 0.012)
            box(root, f'{tag}_bloco{i}_{j}', (arc, depth, h - gap),
                ((r + out) * math.cos(a), (r + out) * math.sin(a), zc), rot=(0, 0, a + math.pi / 2), m=m, bev=bev)


def ang_near(a, b, tol):
    d = (a - b + math.pi) % TAU - math.pi
    return abs(d) < tol


def emblem_into(bm, kind, cx, cz, k=1.0, y=-0.014, mat_index=1):
    """Emblema da familia em ouro sobre o pano (plano XZ): sun, bow, star, flame, drop, swirl, spears, coin."""
    def line(pts, r=0.014, closed=False, rfun=None):
        pts = [(cx + px * k, y, cz + pz * k) for px, pz in pts]
        if closed:
            pts = pts + [pts[0]]
        tube_into(bm, pts, r * k, segs=6, caps=True, mat_index=mat_index, rfun=rfun)
    if kind == 'sun':
        line([(0.06 * math.cos(a), 0.06 * math.sin(a)) for a in [TAU * j / 16 for j in range(17)]], 0.016)
        for j in range(8):
            a = TAU * j / 8
            line([(0.095 * math.cos(a), 0.095 * math.sin(a)), (0.15 * math.cos(a), 0.15 * math.sin(a))], 0.012, rfun=lambda t: 0.014 * k * (1 - 0.8 * t))
    elif kind == 'bow':
        line([(0.06 + 0.13 * math.cos(math.radians(a)), 0.13 * math.sin(math.radians(a))) for a in range(125, 236, 10)], 0.016)
        tip_t, tip_b = (0.06 + 0.13 * math.cos(math.radians(125)), 0.13 * math.sin(math.radians(125))), (0.06 + 0.13 * math.cos(math.radians(235)), 0.13 * math.sin(math.radians(235)))
        line([tip_t, (-0.02, 0.0), tip_b], 0.006)
        line([(-0.1, 0.0), (0.1, 0.0)], 0.009)
        line([(0.09, 0.0), (0.14, 0.0)], 0.022, rfun=lambda t: 0.024 * k * (1 - t) + 0.002)
        for sz in (-1, 1):
            line([(-0.1, 0.0), (-0.13, 0.03 * sz)], 0.008)
    elif kind == 'star':
        pts = []
        for j in range(10):
            a = math.pi / 2 + TAU * j / 10
            r = 0.12 if j % 2 == 0 else 0.05
            pts.append((r * math.cos(a), r * math.sin(a)))
        line(pts, 0.014, closed=True)
        line([(0.025 * math.cos(a), 0.025 * math.sin(a)) for a in [TAU * j / 12 for j in range(13)]], 0.012)
    elif kind == 'flame':
        line([(0.0, 0.14), (0.06, 0.05), (0.075, -0.02), (0.05, -0.08), (0.0, -0.1), (-0.05, -0.08), (-0.075, -0.02), (-0.06, 0.05), (-0.02, 0.09), (0.0, 0.14)], 0.014)
        line([(0.0, 0.06), (0.03, 0.0), (0.0, -0.05), (-0.03, 0.0), (0.0, 0.06)], 0.01)
    elif kind == 'drop':
        pts = [(0.0, 0.13)]
        for j in range(15):
            a = math.radians(-30 - 240 * j / 14)
            pts.append((0.065 * math.cos(a) * -1, -0.03 + 0.065 * math.sin(a)))
        pts.append((0.0, 0.13))
        line(pts, 0.015)
    elif kind == 'swirl':
        line([(0.012 * t * math.cos(t * 0.9), 0.012 * t * math.sin(t * 0.9)) for t in [j * 0.5 for j in range(22)]], 0.013)
    elif kind == 'spears':
        for sx in (-1, 1):
            line([(-0.1 * sx, -0.12), (0.1 * sx, 0.12)], 0.009)
            line([(0.1 * sx, 0.12), (0.13 * sx, 0.155)], 0.02, rfun=lambda t: 0.022 * k * (1 - t) + 0.002)
        line([(0.05 * math.cos(a), -0.01 + 0.05 * math.sin(a)) for a in [TAU * j / 14 for j in range(15)]], 0.014)
    elif kind == 'coin':
        line([(0.09 * math.cos(a), 0.09 * math.sin(a)) for a in [TAU * j / 18 for j in range(19)]], 0.016)
        line([(0.05 * math.cos(a), 0.05 * math.sin(a)) for a in [TAU * j / 14 for j in range(15)]], 0.011)
        line([(0.0, -0.035), (0.0, 0.035)], 0.01)


def moss(root, P, tag, objs, frac=0.22, seed=3):
    """Musgo e folhinhas no topo de alguns blocos visiveis (detalhe dos arqueiros)."""
    rr = random.Random(seed)
    m = P.get('moss') or mat('musgo', '#7f9f52', rough=0.9, var=0.12, bump=0.35)
    k = 0
    for o in objs:
        loc = o.matrix_world.translation if o.parent is None else o.location
        a = math.atan2(loc.y, loc.x)
        if math.sin(a) > 0.2 or rr.random() > frac:
            continue
        d = o.dimensions
        r = 0.75 * max(d.x, d.y) / 2
        sphere(root, f'{tag}_musgo{k}', r * 0.6, (loc.x, loc.y, loc.z + d.z * 0.5), scale=(1.4, 0.9, 0.35), m=m, seg=10,
               rot=(0, 0, a + math.pi / 2))
        k += 1


def banner(root, name, P, x, y, z_top, w=0.36, h=0.85, emblem=True, front=False, rod=True, depth_y=-1):
    """Estandarte teal com borda de ouro e sol, pendurado numa haste. Plano XZ, voltado para -Y."""
    def shape(u, v, co):
        # ponta em V na base
        if v > 0.82:
            dv = (v - 0.82) / 0.18
            co.z -= 0.0
            co.z += abs(u - 0.5) * 2 * dv * h * 0.16
        return co
    o = cloth_grid(root, name, w, h, 6, 14, [P['teal'], P['gold']], shape=shape, front=front, thick=0.016)
    me = o.data
    # borda e sol em ouro: geometria extra na mesma malha (acompanha o balanco)
    bm = bmesh.new()
    bm.from_mesh(me)
    bw = 0.018
    edge = [(0.03, -0.02), (0.03, -h * 0.84), (w / 2, -h * 0.99), (w - 0.03, -h * 0.84), (w - 0.03, -0.02)]
    tube_into(bm, [(ex, -0.012, ez) for ex, ez in edge], bw * 0.5, segs=5, caps=True, mat_index=1)
    if emblem:
        cx, cz = w / 2, -h * 0.38
        kind = emblem if isinstance(emblem, str) else P.get('_emblem', 'sun')
        emblem_into(bm, kind, cx, cz, min(1.0, w / 0.36))
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o.location = (x - w / 2, y, z_top)
    register_cloth(o, hang_wave(h, amp=0.045, axis='Y', cycles=1, waves=0.7, top=0.0))
    if rod:
        tube(root, name + '_haste', [(x - w / 2 - 0.05, y, z_top + 0.01), (x + w / 2 + 0.05, y, z_top + 0.01)], 0.014, P['gold'], segs=8)
        for sx in (-1, 1):
            sphere(root, f'{name}_ponta{sx}', 0.022, (x + sx * (w / 2 + 0.06), y, z_top + 0.01), m=P['gold'], seg=10)
    return o




def door(root, name, P, ang, r, z0, w=0.3, h=0.46, gold_key=False):
    """Porta em arco na parede, voltada para a direcao ang."""
    out = Vector((math.cos(ang), math.sin(ang), 0))
    tan = Vector((-math.sin(ang), math.cos(ang), 0))
    rot = (0, 0, ang + math.pi / 2)
    c = out * r
    box(root, name + '_porta', (w, 0.06, h), (c.x, c.y, z0 + h / 2), rot=rot, m=P['wood'], bev=0.01)
    cyl(root, name + '_portaArco', w / 2, 0.06, (c.x, c.y, z0 + h), rot=(math.pi / 2, 0, ang + math.pi / 2), m=P['wood'], v=20, bev=0.01)
    for k, zz in enumerate((0.15, 0.62)):
        p = c + out * 0.008
        box(root, f'{name}_faixa{k}', (w + 0.01, 0.06, 0.03), (p.x, p.y, z0 + h * zz), rot=rot, m=P['iron'], bev=0.006)
    p = c + tan * 0.07 + out * 0.04
    sphere(root, name + '_argola', 0.018, (p.x, p.y, z0 + h * 0.5), m=P['iron'], seg=8)
    R_ = w / 2 + 0.05
    pts = [c + out * 0.035 - tan * R_]
    for k in range(17):
        a = math.pi - math.pi * k / 16
        q = c + out * 0.035 + tan * (R_ * math.cos(a))
        pts.append(Vector((q.x, q.y, z0 + h + R_ * math.sin(a))))
    pts.append(c + out * 0.035 + tan * R_)
    pts[0].z = z0
    pts[-1].z = z0
    tube(root, name + '_moldura', pts, 0.035, P['gold'] if gold_key else P['sandstone_l'], segs=8)
    if gold_key:
        p = c + out * 0.05
        box(root, name + '_chave', (0.08, 0.08, 0.1), (p.x, p.y, z0 + h + R_), rot=rot, m=P['gold'], bev=0.012)


def tri_prism(root, name, P, center, ang, size, up, m, depth=0.03):
    """Triangulo saliente na parede (entalhe), apontando para cima (up=1) ou para baixo (-1)."""
    out = Vector((math.cos(ang), math.sin(ang), 0))
    tan = Vector((-math.sin(ang), math.cos(ang), 0))
    c = Vector(center)
    tri = [c + Vector((0, 0, up * size)), c + tan * size * 0.95 - Vector((0, 0, up * size * 0.6)),
           c - tan * size * 0.95 - Vector((0, 0, up * size * 0.6))]
    bm = bmesh.new()
    back = [bm.verts.new(p) for p in tri]
    front = [bm.verts.new(p + out * depth) for p in tri]
    bm.faces.new(back[::-1])
    bm.faces.new(front)
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((back[i], back[j], front[j], front[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm_to_obj(bm, name, root, [m], bev=0.004, angle=30)




def lathe_into(bm, prof, segs=12, wobble=None, caps=True, mat_index=0):
    """Superficie de revolucao com secao eliptica. prof: [(z, rx, ry, cx=0), ...] de baixo para cima."""
    rings = []
    for row in prof:
        z, rx, ry = row[0], row[1], row[2]
        cx = row[3] if len(row) > 3 else 0.0
        if rx <= 1e-6 and ry <= 1e-6:
            rings.append([bm.verts.new((cx, 0, z))])
            continue
        ring = []
        for k in range(segs):
            a = TAU * k / segs
            w = 1 + (wobble(a, z) if wobble else 0)
            ring.append(bm.verts.new((cx + rx * w * math.cos(a), ry * w * math.sin(a), z)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) > 1:
            for k in range(segs):
                bm.faces.new((A[0], B[k], B[(k + 1) % segs])).material_index = mat_index
        elif len(B) == 1 and len(A) > 1:
            for k in range(segs):
                bm.faces.new((A[k], A[(k + 1) % segs], B[0])).material_index = mat_index
        elif len(A) > 1:
            for k in range(segs):
                bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k])).material_index = mat_index
    if caps:
        if len(rings[0]) > 1:
            bm.faces.new(list(reversed(rings[0]))).material_index = mat_index
        if len(rings[-1]) > 1:
            bm.faces.new(rings[-1]).material_index = mat_index
    return rings


def set_mesh_tube(o, pts, r, segs=8, rfun=None):
    bm = bmesh.new()
    tube_into(bm, pts, r, segs, rfun=rfun)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.update()


def ensure_mesh(root, name, m):
    o = bpy.data.objects.get(name)
    if o:
        return o
    me = bpy.data.meshes.new(name)
    return new_obj(name, me, root, [m], angle=80)


def subsurf(o, lv=2):
    md = o.modifiers.new('Suave', 'SUBSURF')
    md.levels = lv
    md.render_levels = lv
    return o


def lathe(root, name, prof, m, segs=12, wobble=None, caps=True, lv=2, solid=0.0, cut=None):
    bm = bmesh.new()
    lathe_into(bm, prof, segs, wobble, caps)
    if cut:
        dead = [f for f in bm.faces if cut(f.calc_center_median())]
        bmesh.ops.delete(bm, geom=dead, context='FACES')
    o = bm_to_obj(bm, name, root, [m], angle=89)
    if solid:
        sm = o.modifiers.new('Espessura', 'SOLIDIFY')
        sm.thickness = solid
        sm.offset = 0
    subsurf(o, lv)
    return o


def blob(root, name, r, loc, scale, m, rot=(0, 0, 0)):
    o = sphere(root, name, r, loc, scale=scale, m=m, seg=16, rot=rot)
    return o


def two_bone(S, H, L1, L2, pole):
    """IK de dois ossos: devolve o cotovelo entre ombro S e mao H."""
    S, H, pole = Vector(S), Vector(H), Vector(pole)
    d = H - S
    dist = min(max(d.length, 1e-4), (L1 + L2) * 0.999)
    dn = d.normalized()
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    pv = pole - dn * pole.dot(dn)
    pv = pv.normalized() if pv.length > 1e-6 else Vector((0, 0, -1))
    return S + dn * a + pv * h, S + dn * dist




def setup_scene():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = 'GPU'
    except Exception:
        pass
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.film_transparent = True
    sc.render.filter_size = 1.1
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.resolution_percentage = 100
    w = sc.world or bpy.data.worlds.new('Mundo')
    sc.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    WN = w.node_tree.nodes
    bg = next((n for n in WN if n.type == 'BACKGROUND'), None)
    if bg is None:
        WN.clear()
        bg = WN.new('ShaderNodeBackground')
        wo = WN.new('ShaderNodeOutputWorld')
        w.node_tree.links.new(bg.outputs['Background'], wo.inputs['Surface'])
    bg.inputs['Color'].default_value = lin('#f3dfc2')
    bg.inputs['Strength'].default_value = 0.7
    # sol: vem da esquerda, um pouco da frente, alto
    sun_d = bpy.data.lights.get('Sol') or bpy.data.lights.new('Sol', 'SUN')
    sun_d.energy = 3.8
    sun_d.angle = math.radians(18)
    sun_d.color = lin('#fff0d8')[:3]
    sun = bpy.data.objects.get('Sol') or bpy.data.objects.new('Sol', sun_d)
    if sun.name not in sc.collection.objects:
        sc.collection.objects.link(sun)
    L = Vector((-1.0, -0.45, 2.2)).normalized()   # sol alto: sombra curta, que nao invade o caminho
    sun.rotation_euler = L.to_track_quat('Z', 'Y').to_euler()
    # preenchimento frio e suave do lado direito
    fill_d = bpy.data.lights.get('Preenchimento') or bpy.data.lights.new('Preenchimento', 'SUN')
    fill_d.energy = 0.6
    fill_d.angle = math.radians(40)
    fill_d.color = lin('#d8e6ff')[:3]
    fill = bpy.data.objects.get('Preenchimento') or bpy.data.objects.new('Preenchimento', fill_d)
    if fill.name not in sc.collection.objects:
        sc.collection.objects.link(fill)
    F = Vector((1.0, -0.6, 0.6)).normalized()
    fill.rotation_euler = F.to_track_quat('Z', 'Y').to_euler()
    try:
        fill_d.use_shadow = False
    except Exception:
        pass
    # chao que so recebe sombra
    g = bpy.data.objects.get('ChaoSombra')
    if not g:
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=12)
        me = bpy.data.meshes.new('ChaoSombra')
        bm.to_mesh(me)
        bm.free()
        g = bpy.data.objects.new('ChaoSombra', me)
        sc.collection.objects.link(g)
    g.is_shadow_catcher = True
    # camera ortografica
    cam_d = bpy.data.cameras.get('CamJogo') or bpy.data.cameras.new('CamJogo')
    cam_d.type = 'ORTHO'
    cam_d.sensor_fit = 'HORIZONTAL'
    cam = bpy.data.objects.get('CamJogo') or bpy.data.objects.new('CamJogo', cam_d)
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.rotation_euler = (math.pi / 2 - ELEV, 0, 0)
    sc.camera = cam
    return cam


def cam_axes():
    rot = Euler((math.pi / 2 - ELEV, 0, 0)).to_matrix()
    return rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0)), rot @ Vector((0, 0, -1))


def frame_camera(cam, lo, hi, margin=(0.12, 0.12, 0.12, 0.12)):
    """lo/hi: extremos (direita, cima) no plano da camera. margin: esq, dir, baixo, cima (BU)."""
    Rv, Uv, Fv = cam_axes()
    x0, x1 = lo[0] - margin[0], hi[0] + margin[1]
    y0, y1 = lo[1] - margin[2], hi[1] + margin[3]
    wpx = int(math.ceil((x1 - x0) * ST["px"]))
    hpx = int(math.ceil((y1 - y0) * ST["px"]))
    x1 = x0 + wpx / ST["px"]
    y1 = y0 + hpx / ST["px"]
    sc = bpy.context.scene
    sc.render.resolution_x = wpx
    sc.render.resolution_y = hpx
    cam.data.ortho_scale = wpx / ST["px"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cam.location = Rv * cx + Uv * cy - Fv * 20
    return wpx, hpx, (x0, y1)  # canto superior esquerdo no plano da camera


def project(pt, origin_tl):
    """Ponto do mundo -> pixel (x para a direita, y para baixo) na imagem enquadrada."""
    Rv, Uv, Fv = cam_axes()
    p = Vector(pt)
    return ((p.dot(Rv) - origin_tl[0]) * ST["px"], (origin_tl[1] - p.dot(Uv)) * ST["px"])


def bounds_of(objs):
    Rv, Uv, Fv = cam_axes()
    bpy.context.view_layer.update()
    xs, ys = [], []
    for o in objs:
        if o.type != 'MESH' or o.hide_render:
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.dot(Rv))
            ys.append(w.dot(Uv))
    return (min(xs), min(ys)), (max(xs), max(ys))



def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for d in list(blk):
            if d.users == 0:
                blk.remove(d)
    _M.clear()
    CLOTH.clear()
    SETS.clear()
    BUILT.clear()



def set_visible(keys, front_only=False):
    for o in bpy.data.objects:
        if o.type not in ('MESH',):
            continue
        if o.name == 'ChaoSombra':
            o.hide_render = front_only
            continue
        st = o.get('set')
        on = st in keys
        o.hide_render = not on
        o.visible_camera = True
        if on and front_only and not o.get('front'):
            o.visible_camera = False
    # objetos de arco/flecha escondidos por pose continuam respeitando hide_render da pose
    return


def render_to(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def ease_out_back(x, k=1.7):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2



# ---------------------------------------------------------------- materiais extras das torres novas
GLOW_MATS = {'lanterna': 16.0}   # material -> forca da emissao no passe de luz


def glow_mat(key, hexcol, day, night, **kw):
    """Material que brilha um pouco de dia (day) e forte no passe de luz (night)."""
    m = mat(key, hexcol, emit=day, **kw)
    GLOW_MATS[key] = night
    return m


def palette2():
    P = palette()
    P.update({
        'copper': mat('cobre', '#c9804a', rough=0.32, metal=0.75, var=0.04, bump=0.05),
        'crystal': glow_mat('cristal', '#62e3d6', 1.6, 12.0, rough=0.12, var=0.0, bump=0.0),
        'glass': mat('vidro', '#d6f2f0', rough=0.06, var=0.0, bump=0.0),
        'water': glow_mat('agua', '#3db4c2', 0.25, 0.8, rough=0.06, var=0.02, bump=0.04),
        'water_l': mat('agua_clara', '#9fe6ea', rough=0.05, var=0.0, bump=0.02),
        'foam': mat('espuma', '#f2fbfb', rough=0.4, var=0.0, bump=0.05),
        'tile': mat('azulejo', '#2f7fb0', rough=0.3, var=0.02, bump=0.04, stripes=(9.0, '#2f7fb0', '#f4e7c9')),
        'tile_b': mat('azulejo_azul', '#3b86b8', rough=0.3, var=0.08, bump=0.05),
        'saffron': mat('acafrao', '#e08a2c', rough=0.85, var=0.03, bump=0.08, sheen=0.4),
        'robe': mat('manto_teal', '#1f8a84', rough=0.82, var=0.03, bump=0.08, sheen=0.4),
        'robe_d': mat('manto_escuro', '#22585a', rough=0.82, var=0.03, bump=0.08, sheen=0.4),
        'fire': glow_mat('fogo', '#ffa040', 5.0, 22.0, rough=0.5, var=0.0, bump=0.0),
        'ember': glow_mat('brasa', '#ff6a2a', 2.0, 10.0, rough=0.6, var=0.1, bump=0.1),
        'straw': mat('palha', '#d9b66c', rough=0.95, var=0.06, bump=0.35),
        'leaf': mat('folha', '#6c9a40', rough=0.8, var=0.12, bump=0.1),
        'iron_d': mat('ferro_escuro', '#2f2b29', rough=0.5, metal=0.4, var=0.04, bump=0.06),
        'white': mat('barba', '#eeeae0', rough=0.85, var=0.02, bump=0.25),
        'red': mat('vermelho', '#b84a3a', rough=0.82, var=0.04, bump=0.08, sheen=0.3),
        'purple': mat('roxo', '#7a4f8f', rough=0.82, var=0.04, bump=0.08, sheen=0.3),
        'cactus': mat('cacto', '#5f9a52', rough=0.75, var=0.08, bump=0.2),
        'window': glow_mat('janela', '#ffcf7a', 0.6, 9.0, rough=0.5, var=0.0, bump=0.0),
    })
    return P


# ---------------------------------------------------------------- pecas que mexem no loop (alem do tecido)
ANIMS = {}   # nome do objeto -> (matriz base, funcao(o, matriz_base, fase))


def flag_tree(o):
    o['anim'] = 1
    for ch in o.children:
        flag_tree(ch)


def register_anim(o, fn):
    """fn(o, mb, fase) posiciona o objeto; fase em [0, 1) fecha o loop. Filhos acompanham e tambem viram 'anim'."""
    flag_tree(o)
    ANIMS[o.name] = (o.matrix_basis.copy(), fn)


def refresh_anims():
    for name, (mb, fn) in list(ANIMS.items()):
        o = bpy.data.objects.get(name)
        if o:
            ANIMS[name] = (o.matrix_basis.copy(), fn)


def apply_anim(phase):
    apply_cloth(phase)
    for name, (mb, fn) in ANIMS.items():
        o = bpy.data.objects.get(name)
        if o:
            fn(o, mb, phase)


def spin(axis='Z', sym=1, turns=1):
    """Gira em torno do eixo local; com simetria `sym` basta girar 1/sym de volta por loop."""
    def fn(o, mb, ph):
        o.matrix_basis = mb @ Matrix.Rotation(TAU * turns * ph / sym, 4, axis)
    return fn


def bob(amp=0.02, turns=1, axis='Z', spin_axis=None, sym=1, spin_turns=1):
    def fn(o, mb, ph):
        off = Vector((0, 0, 0))
        off['XYZ'.index(axis)] = amp * math.sin(TAU * turns * ph)
        m = Matrix.Translation(off) @ mb
        if spin_axis:
            m = m @ Matrix.Rotation(TAU * spin_turns * ph / sym, 4, spin_axis)
        o.matrix_basis = m
    return fn


def empty(root, name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    root.users_collection[0].objects.link(e)
    e.parent = parent or root
    e.location = loc
    e.rotation_euler = rot
    e['set'] = root['set']
    return e


def kids(parent, *objs):
    for o in objs:
        o.parent = parent
    return objs[0] if len(objs) == 1 else objs


# ---------------------------------------------------------------- adereços comuns do estilo
def potted_cactus(root, name, P, loc, s=1.0):
    x, y, z = loc
    cyl(root, name + '_vaso', 0.07 * s, 0.1 * s, (x, y, z + 0.05 * s), r2=0.085 * s, m=P['terracotta'], v=16, bev=0.012)
    torus(root, name + '_borda', (x, y, z + 0.1 * s), 0.085 * s, 0.012 * s, P['terracotta'], n=16, segs=5)
    tube(root, name + '_cacto', [(x, y, z + 0.08 * s), (x, y, z + 0.3 * s)], 0.04 * s, P['cactus'], segs=10,
         rfun=lambda t: (0.042 - 0.012 * t * t) * s)
    tube(root, name + '_braco', [(x + 0.03 * s, y, z + 0.17 * s), (x + 0.075 * s, y, z + 0.19 * s), (x + 0.08 * s, y, z + 0.26 * s)],
         0.022 * s, P['cactus'], segs=8, rfun=lambda t: (0.024 - 0.006 * t) * s)


def cushion(root, name, P, loc, m=None, rot=0.0, s=1.0):
    o = box(root, name, (0.2 * s, 0.16 * s, 0.06 * s), (loc[0], loc[1], loc[2] + 0.03 * s), rot=(0, 0, rot), m=m or P['teal'], bev=0.028 * s, seg=4)
    return o


def crate(root, name, P, loc, s=1.0, rot=0.0):
    x, y, z = loc
    box(root, name, (0.2 * s, 0.2 * s, 0.18 * s), (x, y, z + 0.09 * s), rot=(0, 0, rot), m=P['wood_l'], bev=0.012)
    for k, zz in enumerate((0.03, 0.15)):
        box(root, f'{name}_ripa{k}', (0.206 * s, 0.206 * s, 0.025 * s), (x, y, z + zz * s), rot=(0, 0, rot), m=P['wood'], bev=0.006)


def sack(root, name, P, loc, s=1.0):
    x, y, z = loc
    sphere(root, name, 0.09 * s, (x, y, z + 0.08 * s), scale=(1, 0.9, 1.0), m=P['rope'], seg=16)
    torus(root, name + '_no', (x, y, z + 0.16 * s), 0.03 * s, 0.01 * s, P['leather'], n=12, segs=5)


def rope_coil(root, name, P, loc, s=1.0):
    x, y, z = loc
    for k in range(3):
        torus(root, f'{name}{k}', (x, y, z + 0.015 * s + k * 0.022 * s), (0.075 - 0.01 * k) * s, 0.013 * s, P['rope'], n=20, segs=6)


def brazier(root, name, P, loc, s=1.0, lights=None):
    """Braseiro de bronze com chamas (fogo emissivo; luz no passe de glow)."""
    x, y, z = loc
    tube(root, name + '_pe', [(x, y, z), (x, y, z + 0.12 * s)], 0.018 * s, P['iron_d'], segs=8)
    cyl(root, name + '_base', 0.06 * s, 0.02 * s, (x, y, z + 0.01 * s), m=P['iron_d'], v=14, bev=0.005)
    lathe(root, name + '_bacia', [(0.12 * s, 0.03 * s, 0.03 * s), (0.15 * s, 0.085 * s, 0.085 * s), (0.19 * s, 0.11 * s, 0.11 * s)],
          P['bronze'], segs=16, lv=1, caps=False, solid=0.012)
    o = bpy.data.objects[name + '_bacia']
    o.location = (x, y, z)
    cyl(root, name + '_brasa', 0.095 * s, 0.03 * s, (x, y, z + 0.175 * s), m=P['ember'], v=14, bev=0.01)
    fl = []
    for k in range(4):
        a = TAU * k / 4 + 0.4
        r = 0.035 * s
        c = cyl(root, f'{name}_chama{k}', 0.035 * s, 0.12 * s, (x + r * math.cos(a), y + r * math.sin(a), z + 0.24 * s),
                r2=0.0, m=P['fire'], v=10, bev=0.0)
        fl.append(c)
    c = cyl(root, name + '_chamaC', 0.05 * s, 0.17 * s, (x, y, z + 0.265 * s), r2=0.0, m=P['fire'], v=12, bev=0.0)
    fl.append(c)
    for k, c in enumerate(fl):
        def flick(o, mb, ph, k=k):
            s_ = 1 + 0.18 * math.sin(TAU * (ph * 3 + k * 0.27)) + 0.08 * math.sin(TAU * (ph * 5 + k * 0.6))
            o.matrix_basis = mb @ Matrix.Diagonal((1 - 0.08 * (s_ - 1), 1 - 0.08 * (s_ - 1), s_, 1))
        register_anim(c, flick)
    if lights is not None:
        lights.append(((x, y, z + 0.3 * s), '#ff9a40', 26.0 * s, 1))
    return fl


def arch_window(root, name, P, ang, r, zc, w=0.12, h=0.2, depth=0.06, glow=True):
    """Janela em arco embutida numa parede cilindrica de raio r, voltada para o angulo ang."""
    x, y = r * math.cos(ang), r * math.sin(ang)
    rot = (0, 0, ang + math.pi / 2)
    o1 = box(root, name + '_vao', (w, depth, h * 0.7), (x, y, zc - h * 0.15), rot=rot, m=P['window'] if glow else P['dark'], bev=0.006)
    o2 = cyl(root, name + '_arco', w / 2, depth, (x, y, zc + h * 0.2), rot=(math.pi / 2, 0, ang + math.pi / 2),
             m=P['window'] if glow else P['dark'], v=16, bev=0.0)
    # moldura em U invertido
    pts = []
    for k in range(13):
        t = math.pi * k / 12
        lx = (w / 2 + 0.018) * math.cos(t)
        lz = (w / 2 + 0.018) * math.sin(t)
        pts.append(Vector((lx, 0, zc + h * 0.2 + lz)))
    pts = [Vector((w / 2 + 0.018, 0, zc - h * 0.5))] + pts + [Vector((-(w / 2 + 0.018), 0, zc - h * 0.5))]
    R_ = Matrix.Rotation(ang + math.pi / 2, 3, 'Z')
    off = Vector((x, y, 0)) + Vector((math.cos(ang), math.sin(ang), 0)) * (depth * 0.45)
    tube(root, name + '_moldura', [R_ @ Vector((p.x, 0, 0)) + Vector((0, 0, p.z)) + off for p in pts], 0.016, P['sandstone_l'], segs=6)
    return o1, o2


def merlons(root, tag, P, r, z, n, w=None, h=0.16, depth=0.16, m=None, a0=0.0, front_cut=None):
    """Ameias arredondadas em volta de um circulo de raio r com base em z."""
    m = m or P['sandstone_l']
    w = w or TAU * r / n * 0.5
    out = []
    for k in range(n):
        a = a0 + TAU * k / n
        o = box(root, f'{tag}_ameia{k}', (w, depth, h), (r * math.cos(a), r * math.sin(a), z + h / 2),
                rot=(0, 0, a + math.pi / 2), m=m, bev=0.04, seg=4)
        if front_cut and front_cut(a):
            o['front'] = 1
        out.append(o)
    return out


def dome(root, name, r, z, m, h=None, pointed=0.0, segs=32):
    h = h or r
    prof = []
    for k in range(9):
        t = k / 8
        a = t * math.pi / 2
        rr = r * math.cos(a)
        zz = z + h * math.sin(a)
        if pointed:
            zz += pointed * t ** 6
        prof.append((zz, max(rr, 0.0), max(rr, 0.0)))
    prof[-1] = (prof[-1][0], 0.0, 0.0)
    return lathe(root, name, prof, m, segs=segs, lv=1)


def stucco_body(root, tag, P, r0, r1, z0, z1, m=None, stones=12, seed=1, avoid=None, base_course=True, segs=40):
    """Torre de reboco liso (levemente abaulada) com pedras aparentes salpicadas e uma fiada de blocos no pe.
    avoid(a, z) -> True onde nao pode ter pedra (porta, janelas)."""
    m = m or P['sandstone']
    prof = []
    for k in range(9):
        t = k / 8
        r = r0 + (r1 - r0) * t + 0.012 * math.sin(math.pi * t)
        prof.append((z0 + (z1 - z0) * t, r, r))
    body = lathe(root, tag + '_reboco', prof, m, segs=segs, lv=1, caps=True)
    rr = random.Random(seed)
    placed = 0
    tries = 0
    while placed < stones and tries < stones * 20:
        tries += 1
        a = rr.uniform(-math.pi, math.pi)
        z = rr.uniform(z0 + 0.25, z1 - 0.12)
        if math.sin(a) > 0.35:     # costas: ninguem ve
            continue
        if avoid and avoid(a, z):
            continue
        t = (z - z0) / (z1 - z0)
        r = r0 + (r1 - r0) * t + 0.012 * math.sin(math.pi * t)
        w = rr.uniform(0.09, 0.15)
        h = rr.uniform(0.06, 0.09)
        box(root, f'{tag}_pedra{placed}', (w, 0.05, h), ((r + 0.004) * math.cos(a), (r + 0.004) * math.sin(a), z),
            rot=(0, 0, a + math.pi / 2), m=P['sandstone_l'], bev=0.018)
        placed += 1
    if base_course:
        block_ring(root, tag + '_fiada', P, r0 + 0.035, r0 + 0.03, z0, z0 + 0.13, rows=1, per_row=max(10, int(r0 * 22)), depth=0.1,
                   skip=(lambda a, z: avoid(a, z)) if avoid else None, m=P['sandstone_l'], bev=0.03)
    return body


# ---------------------------------------------------------------- personagens (figura esculpida, animada por codigo)
PERSON_FACE = math.radians(-55)   # 3/4 de frente: olha para a direita e para a camera


def build_person(P, root, tag, sp):
    """Figura de ~0.6 BU no estilo do conceito: argila suave, figurino em camadas.
    sp: tunic, robe (manto ate o chao), robe_m, trim, vest, pauldron, belt, sash, scarf, head
    ('hood'|'turban'|'cap'|'helmet'|'hair'|'bald'|'keffiyeh'), head_m, mask, beard, jewel, crest, skin, glove, bracer,
    sleeve, boot_m, face, big (escala do corpo, ex. 1.08 para o tamboreiro)."""
    parts = {'tag': tag, 'sp': sp, 'cloth': []}
    skin = sp.get('skin', P['skin'])
    tunic = sp.get('tunic', P['tunic'])
    leather = P['leather']
    leather_d = mat('couro_escuro', '#6a4026', rough=0.6, var=0.05, bump=0.15)
    body = empty(root, tag + '_corpo', rot=(0, 0, sp.get('face', PERSON_FACE)))
    k = sp.get('big', 1.0)
    body.scale = (k, k, k)
    parts['body'] = body

    def p(o):
        o.parent = body
        return o
    if sp.get('robe'):
        fold = lambda a, z: 0.04 * math.sin(8 * a) * max(0.0, (0.3 - z) / 0.28)
        p(lathe(root, f'{tag}_manto', [(0.0, 0.138, 0.148), (0.05, 0.13, 0.14), (0.12, 0.114, 0.124), (0.2, 0.099, 0.11),
                                       (0.27, 0.086, 0.099), (0.32, 0.078, 0.092)], sp.get('robe_m', tunic), segs=16, wobble=fold, lv=2))
        if sp.get('trim'):
            p(torus(root, f'{tag}_barra', (0, 0, 0.014), 0.139, 0.009, sp['trim'], n=28, segs=5))
        for s, yy in enumerate((-0.05, 0.05)):
            p(blob(root, f'{tag}_sapato{s}', 0.036, (0.115, yy, 0.018), (1.3, 0.8, 0.55), sp.get('boot_m', leather)))
    else:
        for s, yy in enumerate((-0.046, 0.046)):
            p(tube(root, f'{tag}_perna{s}', [(0.0, yy, 0.05), (0.0, yy * 0.9, 0.17)], 0.033, sp.get('pants', P['pants']), segs=10))
            p(blob(root, f'{tag}_bota{s}', 0.05, (0.018, yy * 1.05, 0.04), (1.35, 0.85, 0.85), sp.get('boot_m', leather)))
            p(torus(root, f'{tag}_botaAba{s}', (0.004, yy, 0.085), 0.036, 0.012, sp.get('boot_cuff', leather_d), n=14, segs=6))
        fold = lambda a, z: 0.045 * math.sin(7 * a) * max(0.0, (0.28 - z) / 0.18)
        p(lathe(root, f'{tag}_saia', [(0.1, 0.122, 0.13), (0.15, 0.112, 0.12), (0.21, 0.098, 0.108), (0.27, 0.084, 0.096), (0.32, 0.076, 0.09)],
                sp.get('skirt_m', tunic), segs=14, wobble=fold, lv=2))
    p(lathe(root, f'{tag}_tronco', [(0.29, 0.072, 0.088), (0.34, 0.077, 0.094), (0.39, 0.081, 0.103), (0.43, 0.08, 0.108),
                                   (0.455, 0.066, 0.102), (0.475, 0.045, 0.064), (0.495, 0.03, 0.032)], tunic, segs=12, lv=2))
    if sp.get('vest'):
        p(lathe(root, f'{tag}_colete', [(0.295, 0.08, 0.096), (0.34, 0.085, 0.101), (0.39, 0.089, 0.109), (0.43, 0.087, 0.112),
                                        (0.452, 0.072, 0.106)], sp['vest'], segs=12, lv=2, caps=False, solid=0.006))
    if sp.get('pauldron'):
        for s, yy in enumerate((-0.1, 0.1)):
            p(blob(root, f'{tag}_ombreira{s}', 0.05, (0.0, yy, 0.452), (1.0, 0.8, 0.5), sp['pauldron']))
    if sp.get('mantle'):
        fold = lambda a, z: 0.03 * math.sin(10 * a) * max(0.0, (0.45 - z) / 0.08)
        p(lathe(root, f'{tag}_mantelete', [(0.37, 0.104, 0.124), (0.4, 0.1, 0.12), (0.43, 0.092, 0.115), (0.455, 0.075, 0.1), (0.475, 0.05, 0.068)],
                sp['mantle'], segs=16, wobble=fold, lv=2, caps=False, solid=0.008))
        if sp.get('mantle_trim'):
            p(torus(root, f'{tag}_manteleteBarra', (0, 0, 0.372), 0.112, 0.008, sp['mantle_trim'], n=24, segs=5)).scale = (1.0, 1.15, 1.0)
    if sp.get('gold_collar'):
        p(torus(root, f'{tag}_golaOuro', (0, 0, 0.452), 0.08, 0.007, P['gold'], n=20, segs=5))
    belt = sp.get('belt', leather_d)
    if sp.get('sash'):
        p(lathe(root, f'{tag}_faixa', [(0.285, 0.083, 0.099), (0.33, 0.08, 0.096)], sp['sash'], segs=12, lv=1))
        sa = cloth_grid(root, f'{tag}_faixaPonta', 0.04, 0.12, 2, 5, [sp['sash']], thick=0.012)
        sa.parent = body
        sa.location = (0.06, 0.05, 0.3)
        sa.rotation_euler = (0, 0, math.radians(15))
        register_cloth(sa, hang_wave(0.12, amp=0.012, axis='Y', cycles=1, waves=0.5, top=0.0))
        parts['cloth'].append(sa)
    elif belt:
        p(lathe(root, f'{tag}_cinto', [(0.29, 0.086, 0.102), (0.315, 0.084, 0.1)], belt, segs=12, lv=1))
        p(blob(root, f'{tag}_fivela', 0.022, (0.088, 0.0, 0.302), (0.5, 1.0, 0.85), sp.get('buckle', P['iron'])))
    if sp.get('scarf'):
        p(lathe(root, f'{tag}_lenco', [(0.455, 0.07, 0.085), (0.47, 0.072, 0.086), (0.49, 0.06, 0.07), (0.5, 0.048, 0.055)],
                sp['scarf'], segs=12, lv=2))
        sc = cloth_grid(root, f'{tag}_lencoPonta', 0.045, 0.14, 2, 6, [sp['scarf']], thick=0.014)
        sc.parent = body
        sc.location = (-0.07, -0.03, 0.48)
        sc.rotation_euler = (0, 0, math.pi / 2)
        register_cloth(sc, hang_wave(0.14, amp=0.035, axis='Y', cycles=1, waves=0.6, top=0.0))
        parts['cloth'].append(sc)
    if sp.get('cape'):
        cp = cloth_grid(root, f'{tag}_capa', 0.2, 0.36, 4, 8, [sp['cape']], thick=0.014,
                        shape=lambda u, v, co: Vector((co.x, -0.02 * math.sin(math.pi * u) * (1 - v * 0.3), co.z)))
        cp.parent = body
        cp.location = (-0.09, 0.1, 0.47)
        cp.rotation_euler = (0, 0, -math.pi / 2)
        register_cloth(cp, hang_wave(0.36, amp=0.03, axis='Y', cycles=1, waves=0.6, top=0.0))
        parts['cloth'].append(cp)
    # cabeca (pivo no pescoco)
    head = empty(root, tag + '_cabecaPivo', loc=(0, 0, 0.49), parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    hc = Vector((0.006, 0, 0.055))
    ph(blob(root, f'{tag}_cabeca', 0.066, hc, (1.0, 0.96, 1.06), skin))
    masked = sp.get('mask')
    if not masked:
        ph(blob(root, f'{tag}_nariz', 0.013, hc + Vector((0.062, 0, -0.006)), (1, 0.8, 1.1), skin))
    for s, yy in enumerate((-0.024, 0.024)):
        ph(blob(root, f'{tag}_olho{s}', 0.0095, hc + Vector((0.061, yy, 0.012)), (0.6, 1.0, 1.2), P['eye']))
        ph(box(root, f'{tag}_sobrancelha{s}', (0.008, 0.022, 0.006), hc + Vector((0.056, yy, 0.031)), rot=(math.radians(-12 if yy > 0 else 12), 0, 0),
               m=sp.get('brow_m', mat('sobrancelha', '#4a2c18', rough=0.8, var=0, bump=0)), bev=0.002))
    if masked:
        mk = lathe(root, f'{tag}_mascara', [(-0.07, 0.07, 0.07), (-0.04, 0.071, 0.07), (-0.01, 0.071, 0.07), (0.004, 0.066, 0.064)],
                   masked if not isinstance(masked, bool) else P['teal'], segs=14, lv=2, caps=False, solid=0.008)
        ph(mk).location = hc
    if sp.get('beard'):
        bm_ = sp['beard']
        ph(blob(root, f'{tag}_barba', 0.05, hc + Vector((0.035, 0, -0.06)), (0.85, 1.05, 1.25), bm_))
        ph(blob(root, f'{tag}_barbaPonta', 0.032, hc + Vector((0.045, 0, -0.115)), (0.8, 0.9, 1.3), bm_))
        for s, yy in enumerate((-0.022, 0.022)):
            ph(blob(root, f'{tag}_bigode{s}', 0.016, hc + Vector((0.064, yy, -0.025)), (0.7, 1.4, 0.7), bm_))
    hm = sp.get('head', 'bald')
    head_m = sp.get('head_m')
    if hm in ('hood', 'keffiyeh'):
        def hood_cut(c):
            ang = math.atan2(c.y, c.x)
            return abs(ang) < math.radians(52) and -0.045 < c.z < 0.06 and c.x > 0
        if hm == 'hood':
            prof = [(-0.07, 0.105, 0.118), (-0.045, 0.092, 0.1), (-0.01, 0.084, 0.088), (0.03, 0.082, 0.085, -0.004),
                    (0.06, 0.074, 0.078, -0.012), (0.09, 0.056, 0.058, -0.025), (0.115, 0.034, 0.034, -0.042),
                    (0.135, 0.014, 0.014, -0.062), (0.145, 0.0, 0.0, -0.075)]
        else:
            prof = [(-0.09, 0.1, 0.112), (-0.05, 0.088, 0.096), (-0.01, 0.082, 0.086), (0.03, 0.08, 0.083, -0.004),
                    (0.06, 0.072, 0.075, -0.008), (0.085, 0.052, 0.054, -0.01), (0.1, 0.0, 0.0, -0.01)]
        hd = lathe(root, f'{tag}_capuz', prof, head_m or P['hood'], segs=16, lv=2, caps=False, solid=0.01, cut=hood_cut)
        ph(hd).location = hc
        if hm == 'keffiyeh':
            ph(torus(root, f'{tag}_agal', hc + Vector((-0.004, 0, 0.05)), 0.078, 0.011, sp.get('agal', P['dark']), n=18, segs=6))
        if sp.get('hood_trim'):
            tr = tube(root, f'{tag}_capuzOuro', [hc + Vector((0.07 * math.cos(a), 0.075 * math.sin(a), 0.0))
                                                 for a in [math.radians(x) for x in range(-55, 56, 10)]], 0.006, sp['hood_trim'], segs=5)
            ph(tr)
    elif hm in ('turban', 'cap'):
        tm = sp.get('turban_m', mat('turbante', '#e8d8b4', rough=0.85, var=0.02, bump=0.1))
        big = sp.get('turban_big', 1.0)
        if hm == 'turban':
            prof = [(0.0, 0.074, 0.074), (0.04, 0.08, 0.08), (0.08, 0.074, 0.074), (0.11, 0.05, 0.05), (0.125, 0.0, 0.0)]
            cap = lathe(root, f'{tag}_gorro', [(z * big + 0.006, rx * big, ry * big, -0.012) for z, rx, ry in prof], tm, segs=16, lv=2, caps=False, solid=0.008)
        else:
            cap = lathe(root, f'{tag}_gorro', [(0.034, 0.071, 0.071), (0.055, 0.07, 0.07), (0.077, 0.057, 0.057), (0.095, 0.032, 0.032), (0.102, 0.0, 0.0)],
                        head_m or mat('gorro', '#7a5233', rough=0.85, var=0.04, bump=0.15), segs=14, lv=2, caps=False, solid=0.008)
        ph(cap).location = hc
        if hm == 'turban':
            for j, (zz, rr_, tilt) in enumerate(((0.016, 0.078, 0.12), (0.044, 0.083, -0.1), (0.072, 0.072, 0.14))):
                t_ = torus(root, f'{tag}_turbante{j}', (0, 0, 0), rr_ * big, 0.016 * big, tm, n=20, segs=6)
                ph(t_).location = hc + Vector((-0.012, 0, zz * big))
                t_.rotation_euler = (tilt, 0, 0)
            if sp.get('jewel'):
                ph(blob(root, f'{tag}_joia', 0.016, hc + Vector((0.078 * big, 0, 0.036 * big)), (0.6, 1.0, 1.2), P['gold']))
                ph(blob(root, f'{tag}_joiaPedra', 0.01, hc + Vector((0.088 * big, 0, 0.036 * big)), (0.6, 1.0, 1.0), sp['jewel']))
            if sp.get('plume'):
                ph(tube(root, f'{tag}_pluma', [hc + Vector((0.06, 0, 0.05)), hc + Vector((0.03, 0, 0.14)), hc + Vector((-0.02, 0, 0.17))],
                        0.016, sp['plume'], segs=6, rfun=lambda t: 0.018 * (1 - t) + 0.004))
    elif hm == 'helmet':
        hm_o = lathe(root, f'{tag}_elmo', [(0.0, 0.078, 0.078, -0.01), (0.035, 0.077, 0.077, -0.006), (0.07, 0.063, 0.063), (0.098, 0.034, 0.034), (0.108, 0.0, 0.0)],
                     head_m or P['bronze'], segs=16, lv=2, caps=False, solid=0.01)
        ph(hm_o).location = hc
        ph(box(root, f'{tag}_nasal', (0.012, 0.014, 0.05), hc + Vector((0.08, 0, -0.005)), m=head_m or P['bronze'], bev=0.004))
        if sp.get('crest'):
            crest = [hc + Vector((-0.09 + 0.17 * t, 0, 0.085 + 0.05 * math.sin(math.pi * t))) for t in [j / 10 for j in range(11)]]
            ph(tube(root, f'{tag}_crista', crest, 0.024, sp['crest'], segs=8, rfun=lambda t: 0.028 - 0.014 * abs(t - 0.45)))
    elif hm == 'hair':
        hair = sp.get('hair_m', mat('cabelo', '#4a2c18', rough=0.7, var=0.03, bump=0.25))

        def hair_cut(c):
            ang = math.atan2(c.y, c.x)
            return abs(ang) < math.radians(48) and c.z < 0.03 and c.x > 0
        hr = lathe(root, f'{tag}_cabelo', [(-0.05, 0.07, 0.072), (-0.01, 0.073, 0.075), (0.03, 0.07, 0.072), (0.06, 0.05, 0.052), (0.074, 0.0, 0.0)],
                   hair, segs=14, lv=2, caps=False, solid=0.008, cut=hair_cut)
        ph(hr).location = hc
        if sp.get('topknot'):
            ph(blob(root, f'{tag}_coque', 0.03, hc + Vector((-0.04, 0, 0.07)), (1, 1, 0.9), hair))
    elif hm == 'bald' and sp.get('topknot'):
        ph(blob(root, f'{tag}_coque', 0.025, hc + Vector((-0.03, 0, 0.07)), (1, 1, 0.9), sp.get('hair_m', P['dark'])))
    if sp.get('goggles'):
        for s, yy in enumerate((-0.026, 0.026)):
            ph(torus(root, f'{tag}_oculos{s}', hc + Vector((0.064, yy, 0.014)), 0.018, 0.006, P['bronze'], axis='X', n=12, segs=5))
            ph(blob(root, f'{tag}_lente{s}', 0.015, hc + Vector((0.066, yy, 0.014)), (0.4, 1, 1), P['glass']))
        ph(torus(root, f'{tag}_oculosFaixa', hc + Vector((0, 0, 0.014)), 0.07, 0.007, P['leather'], n=18, segs=5))
    parts['sleeve'] = sp.get('sleeve', tunic)
    parts['glove'] = sp.get('glove', skin if sp.get('bare_hands') else leather)
    parts['bracer'] = sp.get('bracer', parts['sleeve'] if sp.get('robe') else leather_d)
    for side in 'LR':
        parts['luva' + side] = blob(root, f'{tag}_luva{side}', 0.031, (0, 0, 0), (1.2, 0.95, 1.0), parts['glove'])
        parts['mao' + side] = empty(root, f'{tag}_mao{side}')
    return parts


def hold(parts, side, *objs):
    """Prende objetos (construidos ao longo do eixo Z local, empunhadura em z=0) na mao L ou R."""
    for o in objs:
        o.parent = parts['mao' + side]
    parts.setdefault('props', []).extend(objs)
    return objs


def pose_person(parts, P, root, st):
    """st: face, lean, breathe, head_yaw/pitch/roll, ph (tecido), hand_L/hand_R (local do corpo), pole_L/pole_R,
    grip_L/grip_R (direcao do eixo do objeto na mao, local do corpo), hide (nomes escondidos), show."""
    tag = parts['tag']
    body = parts['body']
    br = st.get('breathe', 0.0)
    k = parts['sp'].get('big', 1.0)
    body.scale = (k, k, k * (1 + 0.018 * br))
    body.rotation_euler = (0, st.get('lean', 0.0), st.get('face', parts['sp'].get('face', PERSON_FACE)))
    body.location = Vector(st.get('offset', (0, 0, 0)))
    parts['head'].rotation_euler = (st.get('head_roll', 0.0), st.get('head_pitch', 0.0) + 0.03 * br, st.get('head_yaw', 0.0))
    bpy.context.view_layer.update()
    M = body.matrix_world.copy()
    Mi = root.matrix_world.inverted()
    MR = (Mi @ M).to_3x3()

    def W(v):
        return Mi @ (M @ Vector(v))
    ph = st.get('ph', 0.0)
    for c in parts['cloth']:
        base, fn = CLOTH[c.name]
        for v, b in zip(c.data.vertices, base):
            v.co = fn(b, ph)
        c.data.update()
    shoulders = {'L': Vector((0.0, 0.098, 0.448 + 0.008 * br)), 'R': Vector((0.0, -0.098, 0.448 + 0.008 * br))}
    rest = {'L': (0.04, 0.135, 0.27 + 0.004 * br), 'R': (0.04, -0.135, 0.27 + 0.004 * br)}
    poles = {'L': (-0.3, 1.0, -0.6), 'R': (-0.3, -1.0, -0.6)}
    for side in 'LR':
        S = shoulders[side]
        H = Vector(st.get('hand_' + side, rest[side]))
        E, Hh = two_bone(S, H, 0.125, 0.12, st.get('pole_' + side, poles[side]))
        up = ensure_mesh(root, f'{tag}_bracoSup{side}', parts['sleeve'])
        set_mesh_tube(up, [W(S), W(S.lerp(E, 0.5)), W(E)], 0.034, segs=10, rfun=lambda t: 0.036 - 0.01 * t)
        lo = ensure_mesh(root, f'{tag}_antebraco{side}', parts['bracer'])
        rob = parts['sp'].get('robe')
        set_mesh_tube(lo, [W(E), W(E.lerp(Hh, 0.5)), W(Hh)], 0.026, segs=10,
                      rfun=(lambda t: 0.029 + 0.012 * t) if rob else (lambda t: 0.027 - 0.004 * t + 0.006 * max(0, t - 0.75) / 0.25))
        el = ensure_mesh(root, f'{tag}_cotovelo{side}', parts['sleeve'])
        set_mesh_tube(el, [W(E - (E - S).normalized() * 0.012), W(E + (Hh - E).normalized() * 0.012)], 0.03, segs=10)
        for o in (up, lo, el):
            o['set'] = root['set']
        g = parts['luva' + side]
        hp = Hh + (Hh - E).normalized() * 0.018
        g.location = W(hp)
        d = (W(Hh) - W(E)).normalized()
        g.rotation_euler = d.to_track_quat('X', 'Z').to_euler()
        hand = parts['mao' + side]
        hand.location = W(hp)
        gd = Vector(st.get('grip_' + side, tuple(Hh - E)))
        hand.rotation_euler = (MR @ gd).normalized().to_track_quat('Z', 'X').to_euler()
        hand.scale = (k, k, k)
    hide = set(st.get('hide', ()))
    for o in parts.get('props', []):
        hid = o.name in hide or any(o.name.startswith(h) for h in hide)
        o.hide_render = o.hide_viewport = hid
        for ch in o.children_recursive:
            ch.hide_render = ch.hide_viewport = hid


# ---------------------------------------------------------------- passes de render
def reset_vis():
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.is_holdout = False
            o.visible_shadow = True
            o.visible_camera = True


def set_px(k):
    ST['px'] = GAME_PER_BU * PX_PER_GAME * k


def meshes_of(keys, anim=None):
    out = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.get('set') not in keys:
            continue
        if anim is None or bool(o.get('anim')) == anim:
            out.append(o)
    return out


def union(boxes):
    return ((min(b[0][0] for b in boxes), min(b[0][1] for b in boxes)),
            (max(b[1][0] for b in boxes), max(b[1][1] for b in boxes)))


def render_glow_pass(key, path):
    """So a luz (lanternas, braseiros, cristais, janelas), sem sol nem ceu: somada no jogo conforme o clima."""
    sc = bpy.context.scene
    bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
    old = (bg.inputs['Strength'].default_value, bpy.data.lights['Sol'].energy, bpy.data.lights['Preenchimento'].energy)
    bg.inputs['Strength'].default_value = 0.0
    bpy.data.lights['Sol'].energy = 0.0
    bpy.data.lights['Preenchimento'].energy = 0.0
    bpy.data.objects['ChaoSombra'].hide_render = True
    olds = {}
    for name, val in GLOW_MATS.items():
        gm = bpy.data.materials.get(name)
        if not gm:
            continue
        gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        olds[name] = gb.inputs['Emission Strength'].default_value
        gb.inputs['Emission Strength'].default_value = val
    temp = []
    for i, L_ in enumerate(BUILT[key].get('lights', [])):
        pos, col, watts = L_[0], L_[1], L_[2]
        ld = bpy.data.lights.new(f'luz{i}', 'POINT')
        ld.energy = watts
        ld.shadow_soft_size = 0.05
        ld.color = lin(col)[:3]
        lo = bpy.data.objects.new(f'luz{i}', ld)
        sc.collection.objects.link(lo)
        lo.location = Vector(pos)
        temp.append(lo)
    render_to(path)
    for lo in temp:
        ld = lo.data
        bpy.data.objects.remove(lo, do_unlink=True)
        bpy.data.lights.remove(ld)
    for name, v in olds.items():
        gb = next(n for n in bpy.data.materials[name].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        gb.inputs['Emission Strength'].default_value = v
    bg.inputs['Strength'].default_value = old[0]
    bpy.data.lights['Sol'].energy = old[1]
    bpy.data.lights['Preenchimento'].energy = old[2]
    bpy.data.objects['ChaoSombra'].hide_render = False


def has_glow(key):
    names = set(GLOW_MATS) - {'agua'}
    for o in meshes_of({key}):
        for m in o.data.materials:
            if m and m.name in names:
                return True
    return bool(BUILT[key].get('lights'))


def render_tower(key, out):
    """Torre: base parada, loop das pecas que mexem, camada da frente e luz."""
    cam = bpy.context.scene.camera
    d = os.path.join(out, key)
    os.makedirs(d, exist_ok=True)
    reset_vis()
    set_visible({key})
    set_px(1.0)
    B = BUILT[key]
    moving = meshes_of({key}, anim=True)
    boxes = []
    for ph in (0.0, 0.25, 0.5, 0.75):
        apply_anim(ph)
        boxes.append(bounds_of(meshes_of({key})))
    apply_anim(0.0)
    lo, hi = union(boxes)
    wpx, hpx, tl = frame_camera(cam, lo, hi, margin=B.get('margin', (0.15, 0.95, 0.2, 0.3)))
    info = {'w': wpx, 'h': hpx, 'anchor': project((0, 0, 0), tl),
            'slots': [project(s, tl) for s in B.get('slots', [])],
            'lanterns': [list(project(L_[0], tl)) + [L_[1], L_[3] if len(L_) > 3 else 1] for L_ in B.get('lights', []) if (len(L_) < 4 or L_[3])]}
    for name, pt in B.get('points', {}).items():
        info.setdefault('points', {})[name] = project(pt, tl)
    for o in moving:
        o.hide_render = True
    render_to(os.path.join(d, 'base.png'))
    info['base'] = 1
    for o in moving:
        o.hide_render = False
    if moving:
        still = meshes_of({key}, anim=False)
        for o in still:
            o.is_holdout = True
            o.visible_shadow = False
        # a sombra das pecas que mexem so entra quando a peca e grande (pas do catavento); senao atravessa a torre
        bpy.data.objects['ChaoSombra'].hide_render = not B.get('anim_shadow')
        for f in range(ANIM_N):
            apply_anim(f / ANIM_N)
            render_to(os.path.join(d, f'anim_{f:02d}.png'))
        apply_anim(0.0)
        bpy.data.objects['ChaoSombra'].hide_render = False
        for o in still:
            o.is_holdout = False
            o.visible_shadow = True
        info['anim'] = ANIM_N
    if any(o.get('front') for o in meshes_of({key})):
        set_visible({key}, front_only=True)
        render_to(os.path.join(d, 'front.png'))
        info['front'] = 1
        set_visible({key})
    if has_glow(key):
        render_glow_pass(key, os.path.join(d, 'glow.png'))
        info['glow'] = 1
    return info


def render_frames(key, out, frames, boost=1.0, margin=(0.06, 0.06, 0.08, 0.05), shadow=True, extra=None):
    """Conjunto animado (tripulacao, torreta, projetil): frames = [(nome_arquivo, funcao_pose)], camera unica."""
    cam = bpy.context.scene.camera
    d = os.path.join(out, key)
    os.makedirs(d, exist_ok=True)
    reset_vis()
    set_visible({key})
    bpy.data.objects['ChaoSombra'].hide_render = not shadow
    set_px(boost)
    boxes = []
    for name, fn in frames:
        fn()
        boxes.append(bounds_of(meshes_of({key})))
    lo, hi = union(boxes)
    wpx, hpx, tl = frame_camera(cam, lo, hi, margin=margin)
    info = {'w': wpx, 'h': hpx, 'anchor': project((0, 0, 0), tl), 'boost': boost}
    if extra:
        info.update(extra(tl))
    for name, fn in frames:
        fn()
        render_to(os.path.join(d, name + '.png'))
    set_px(1.0)
    bpy.data.objects['ChaoSombra'].hide_render = False
    return info


# ---------------------------------------------------------------- familia: monta tudo e renderiza
def build_family(spec):
    clear_scene()
    ANIMS.clear()
    sc = bpy.context.scene
    ST['coll'] = sc.collection
    setup_scene()
    P = palette2()
    for key, label, fn in spec.get('towers', []):
        root = make_root('raiz_' + key, key, coll_for(label))
        B = fn(P, root) or {}
        for o in bpy.data.objects:
            if o.get('set') == key and o.parent == root and not o.get('plot'):
                o.location.z += LIFT
        lift = lambda v: (v[0], v[1], v[2] + LIFT)
        B['slots'] = [lift(s) for s in B.get('slots', [])]
        B['lights'] = [(lift(L_[0]),) + tuple(L_[1:]) for L_ in B.get('lights', [])]
        B['points'] = {k: lift(v) for k, v in B.get('points', {}).items()}
        BUILT[key] = B
    for grp in ('crews', 'turrets', 'stills'):
        for it in spec.get(grp, []):
            root = make_root('raiz_' + it['key'], it['key'], coll_for(it.get('label', it['key'])))
            BUILT[it['key']] = it['build'](P, root) or {}
            if it.get('pose0'):
                it['pose0'](BUILT[it['key']], P, root)
    refresh_anims()
    apply_anim(0.0)
    bpy.context.view_layer.update()
    return P


def render_family(fam, spec, out, only=None):
    os.makedirs(out, exist_ok=True)
    P = palette2()
    meta = {'family': fam, 'px_per_game': PX_PER_GAME, 'game_per_bu': GAME_PER_BU, 'sets': {}}
    want = lambda k: (only is None) or (k in only)
    for k in SETS:
        SETS[k].location = (0, 0, 0)
    for key, label, fn in spec.get('towers', []):
        if want(key):
            meta['sets'][key] = render_tower(key, out)
            print('OK', key, flush=True)
    for it in spec.get('crews', []) + spec.get('turrets', []) + spec.get('stills', []):
        key = it['key']
        if not want(key):
            continue
        root = SETS[key]
        parts = BUILT[key]
        frames = []
        counts = {}
        for mode, n, fn in it['modes']:
            counts[mode] = n
            for f in range(n):
                frames.append((f'{mode}_{f:02d}', (lambda fn=fn, f=f: fn(parts, P, root, f))))
        info = render_frames(key, out, frames, boost=it.get('boost', 1.0), margin=it.get('margin', (0.06, 0.06, 0.08, 0.05)),
                             shadow=it.get('shadow', True), extra=it.get('extra') and (lambda tl, it=it, parts=parts: it['extra'](parts, tl)))
        info['modes'] = counts
        if it.get('pxk'):
            info['pxk'] = it['pxk']
        if it.get('dirs'):
            info['dirs'] = it['dirs']
        meta['sets'][key] = info
        print('OK', key, flush=True)
    mp = os.path.join(out, 'meta.json')
    old = {}
    if os.path.exists(mp):
        with open(mp) as fh:
            old = json.load(fh)
    old.setdefault('sets', {}).update(meta['sets'])
    old.update({k: v for k, v in meta.items() if k != 'sets'})
    with open(mp, 'w') as fh:
        json.dump(old, fh, indent=1)
    return old


def layout_show(spec, gap=2.4):
    """Organiza tudo lado a lado para ver no Blender; a tripulacao vai para os postos (spec['show_crew'])."""
    x = 0.0
    for key, label, fn in spec.get('towers', []):
        SETS[key].location = (x, 0, 0)
        x += gap
    x = 0.0
    for grp in ('crews', 'turrets', 'stills'):
        for it in spec.get(grp, []):
            SETS[it['key']].location = (x, 40.0, 0)
            x += 1.0
    for tk, cks in spec.get('show_crew', {}).items():
        for j, s in enumerate(BUILT[tk].get('slots', [])):
            ck = cks if isinstance(cks, str) else cks[min(j, len(cks) - 1)]
            if not ck:
                continue
            coll = SETS[ck].users_collection[0]
            e = bpy.data.objects.new(f'inst_{tk}_{j}', None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = coll
            SETS[tk].users_collection[0].objects.link(e)
            e.parent = SETS[tk]
            k = next((it.get('boost', 1.0) for grp in ('crews', 'turrets') for it in spec.get(grp, []) if it['key'] == ck), 1.0)
            e.scale = (k, k, k)
            e.location = Vector(s) - SETS[ck].location * k
            e['set'] = tk
    cam = bpy.data.objects['CamJogo']
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'ChaoSombra']
    objs = [o for o in objs if abs(o.matrix_world.translation.y) < 20 or o.parent is None and abs(o.location.y) < 20]
    objs = [o for o in objs if not (o.get('set') and SETS.get(o['set']) and SETS[o['set']].location.y > 20)]
    lo, hi = bounds_of(objs)
    frame_camera(cam, lo, hi, margin=(0.4, 0.4, 0.4, 0.4))
    sc = bpy.context.scene
    sc.render.resolution_percentage = max(10, min(100, int(1600 / sc.render.resolution_x * 100)))


def layout_crew(spec, pose='show'):
    """Close dos personagens lado a lado (para conferir rosto, figurino e pose)."""
    for k in SETS:
        SETS[k].location = (0, 60, 0)
    x = 0.0
    keys = []
    for it in spec.get('crews', []):
        SETS[it['key']].location = (x, 0, 0)
        it[pose](BUILT[it['key']], palette2(), SETS[it['key']])
        keys.append(it['key'])
        x += 0.75
    set_visible(set(keys))
    bpy.context.view_layer.update()
    lo, hi = bounds_of(meshes_of(set(keys)))
    set_px(4.0)
    frame_camera(bpy.data.objects['CamJogo'], lo, hi, margin=(0.1, 0.1, 0.1, 0.1))


def main(fam, spec):
    if '--' not in sys.argv:
        return
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'render':
        build_family(spec)
        out = args[1]
        only = set(args[2:]) or None
        render_family(fam, spec, out, only)
        print('RENDER_OK', out)
    elif args and args[0] == 'still':
        # uma vitrine rapida: tudo lado a lado num quadro so (para conferir modelagem)
        build_family(spec)
        for it in spec.get('crews', []):
            if it.get('show'):
                it['show'](BUILT[it['key']], palette2(), SETS[it['key']])
        layout_show(spec)
        bpy.context.scene.cycles.samples = int(args[2]) if len(args) > 2 else 32
        render_to(args[1])
        print('STILL_OK', args[1])
    elif args and args[0] == 'crew':
        build_family(spec)
        layout_crew(spec, args[3] if len(args) > 3 else 'show')
        bpy.context.scene.cycles.samples = int(args[2]) if len(args) > 2 else 32
        render_to(args[1])
        print('CREW_OK', args[1])
