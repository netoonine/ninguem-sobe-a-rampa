"""Torre de Arqueiros no estilo "soft relaxante" -> sprites pre-renderizados para o jogo.

Tudo e gerado por codigo (deterministico): modelos, materiais, luz, camera e animacoes.

Uso:
  No Blender aberto (para ver a cena):
      exec(open('<caminho>/tools/blender/arqueiros.py').read()); build(showcase=True)
  Linha de comando (renderiza todos os quadros):
      Blender -b -P tools/blender/arqueiros.py -- render <pasta_saida> [conjuntos...]

Convencoes:
  - Z para cima, a camera olha para +Y (frente da torre = -Y), elevacao de 35 graus, ortografica.
  - 1 unidade do Blender (BU) = 31 unidades do jogo; renderiza a 3 px por unidade do jogo (93 px/BU).
  - Cada conjunto (n1..n4, lote, a1..a3, bal) tem um objeto raiz; tudo dentro dele e filho da raiz.
"""
import bpy, bmesh, math, random, os, sys, json
from mathutils import Vector, Matrix, Euler

TAU = math.tau
ELEV = math.radians(35)
GAME_PER_BU = 41.0     # torres ~32% maiores que a primeira versao
ARCHER_BOOST = 1.3     # arqueiros desenhados 30% maiores que a escala do deque (exagero do genero)
BAL_BOOST = 1.12       # balestra um pouco maior
PROJ_PX = 2.0          # flechas renderizadas em 2x (sao giradas no jogo)
LIFT = 0.08            # a plataforma de pedra e mais alta que o lote antigo: a torre sobe junto
PX_PER_GAME = 3.0
PX_PER_BU = GAME_PER_BU * PX_PER_GAME
LOOP = 24          # quadros do loop de tecido (torres e lote)
IDLE = 12          # quadros do arqueiro parado
SHOOT = 8          # quadros do disparo do arqueiro
BAL_DIRS = 16      # direcoes da balestra
BAL_FRAMES = 8     # quadros do disparo da balestra
BUILD = 12         # quadros da construcao (pecas sobem de baixo para cima)

FRONT_ARCH_Y = -0.0  # referencia

# ---------------------------------------------------------------- utilidades
def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)


R = random.Random(7)
CLOTH = {}      # nome do objeto -> (coords base, funcao(co, fase) -> co)
SETS = {}       # conjunto -> objeto raiz
ANIM = {}       # conjunto -> funcao(modo, quadro, extra)
COLL = None


def coll_for(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        COLL.children.link(c)
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
    """Plataforma de pedra (a mesma em todas as torres e no lote vazio): meio-fio de blocos de arenito
    arredondados, piso de lajotas, rampa de areia e tufos de capim. Topo em z = 0.15."""
    made = []

    def mk(o):
        o['plot'] = 1
        made.append(o)
        return o
    laje = mat('laje', '#d2b48a', rough=0.85, var=0.12, bump=0.3)
    curb = mat('meiofio', '#e3b87c', rough=0.8, var=0.09, bump=0.25)
    grass = mat('capim', '#8f9b4c', rough=0.9, var=0.15, bump=0.1)
    rr = random.Random(11)
    mk(cyl(root, tag + '_rampa', 0.98, 0.05, (0, 0, 0.025), r2=0.86, m=P['sand'], v=48, bev=0.02))
    mk(cyl(root, tag + '_miolo', 0.74, 0.13, (0, 0, 0.065), m=P['mortar'], v=40, bev=0.0))
    n = 20
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.02, 0.02)
        arc = TAU * 0.8 / n - 0.022
        hgt = 0.165 + rr.uniform(-0.012, 0.012)
        mk(box(root, f'{tag}_meiofio{k}', (arc, 0.17, hgt), (0.8 * math.cos(a), 0.8 * math.sin(a), hgt / 2),
               rot=(0, 0, a + math.pi / 2 + rr.uniform(-0.03, 0.03)), m=curb, bev=0.045))
    mk(cyl(root, tag + '_lajeCentro', 0.15, 0.04, (0, 0, 0.13), m=laje, v=20, bev=0.012))
    for ring, (r0, r1, cnt) in enumerate(((0.19, 0.44, 7), (0.47, 0.71, 12))):
        for k in range(cnt):
            a = TAU * (k + 0.5 * ring) / cnt
            rm = (r0 + r1) / 2
            arc = TAU * rm / cnt * 0.9
            mk(box(root, f'{tag}_laje{ring}_{k}', (arc, (r1 - r0) * 0.9, 0.04),
                   (rm * math.cos(a), rm * math.sin(a), 0.13 + rr.uniform(-0.004, 0.004)),
                   rot=(rr.uniform(-0.02, 0.02), rr.uniform(-0.02, 0.02), a + math.pi / 2), m=laje, bev=0.014))
    # tufos de capim e seixos no pe da plataforma (nunca na frente, para nao cobrir a torre)
    for k, ang in enumerate((150, 205, 30, 330, 100)):
        a = math.radians(ang + rr.uniform(-10, 10))
        cx, cy = 0.95 * math.cos(a), 0.95 * math.sin(a)
        for j in range(4):
            b = rr.uniform(0, TAU)
            tip = (cx + 0.05 * math.cos(b), cy + 0.05 * math.sin(b), 0.13 + rr.uniform(0, 0.05))
            mk(tube(root, f'{tag}_capim{k}_{j}', [(cx + 0.015 * math.cos(b), cy + 0.015 * math.sin(b), 0.0), tip], 0.012, grass,
                    segs=5, rfun=lambda t: 0.014 * (1 - t) + 0.002))
    for k in range(6):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0.92, 1.02)
        mk(sphere(root, f'{tag}_seixo{k}', 0.025 + 0.015 * rr.random(), (d * math.cos(a), d * math.sin(a), 0.01),
                  scale=(1.3, 1, 0.6), m=P['stone'], seg=10))
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
        ring = [(cx + 0.06 * math.cos(a), -0.014, cz + 0.06 * math.sin(a)) for a in [TAU * k / 16 for k in range(17)]]
        tube_into(bm, ring, 0.016, segs=6, caps=True, mat_index=1)
        for k in range(8):
            a = TAU * k / 8
            p0 = (cx + 0.095 * math.cos(a), -0.014, cz + 0.095 * math.sin(a))
            p1 = (cx + 0.15 * math.cos(a), -0.014, cz + 0.15 * math.sin(a))
            tube_into(bm, [p0, p1], 0.012, segs=5, caps=True, mat_index=1, rfun=lambda t: 0.014 * (1 - 0.8 * t))
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


# ---------------------------------------------------------------- N1: posto de vigia de madeira
def build_n1(P, root):
    plot(root, P, 'n1')
    dz = 1.1
    S = 0.45
    corners = [(-S, -S), (S, -S), (S, S), (-S, S)]
    for k, (x, y) in enumerate(corners):
        tube(root, f'n1_estaca{k}', [(x * 1.06, y * 1.06, 0.06), (x, y, dz + 0.02)], 0.06, P['wood'], segs=10,
             rfun=lambda t: 0.068 - 0.014 * t)
        for zz in (0.5, dz - 0.08):
            torus(root, f'n1_amarra{k}_{zz}', (x * (1.06 - 0.06 * zz / dz), y * (1.06 - 0.06 * zz / dz), zz), 0.072, 0.017, P['rope'], n=16, segs=6)
    # travessas horizontais e X em cada face
    faces = [((-S, -S), (S, -S)), ((S, -S), (S, S)), ((S, S), (-S, S)), ((-S, S), (-S, -S))]
    for k, (a, b) in enumerate(faces):
        za, zb = 0.14, dz - 0.1
        tube(root, f'n1_xA{k}', [(a[0] * 1.05, a[1] * 1.05, za), (b[0] * 1.0, b[1] * 1.0, zb)], 0.032, P['wood'], segs=8)
        tube(root, f'n1_xB{k}', [(b[0] * 1.05, b[1] * 1.05, za), (a[0] * 1.0, a[1] * 1.0, zb)], 0.032, P['wood'], segs=8)
        tube(root, f'n1_trav{k}', [(a[0] * 1.03, a[1] * 1.03, 0.5), (b[0] * 1.03, b[1] * 1.03, 0.5)], 0.035, P['wood'], segs=8)
    # deque de tabuas
    rr = random.Random(5)
    for i in range(8):
        x = -0.56 + 0.16 * i + 0.08
        box(root, f'n1_tabua{i}', (0.15, 1.24, 0.055), (x, 0, dz + rr.uniform(-0.006, 0.006)),
            rot=(0, 0, rr.uniform(-0.02, 0.02)), m=P['wood_l'], bev=0.016)
    for k, (a, b) in enumerate(faces):
        box(root, f'n1_viga{k}', (abs(b[0] - a[0]) * 1.3 + 0.1, abs(b[1] - a[1]) * 1.3 + 0.1, 0.07),
            ((a[0] + b[0]) * 0.65, (a[1] + b[1]) * 0.65, dz - 0.06), m=P['wood'], bev=0.015)
    # parapeito: tras e lados normais, frente baixa (camada da frente)
    E = 0.6
    posts = [(-E, -E), (0, -E), (E, -E), (E, 0), (E, E), (0, E), (-E, E), (-E, 0)]
    for k, (x, y) in enumerate(posts):
        front = y < -0.1
        hgt = 0.2 if front else 0.3
        tube(root, f'n1_pilar{k}', [(x, y, dz), (x, y, dz + hgt + 0.03)], 0.03, P['wood'], segs=8, front=front)
        sphere(root, f'n1_pilarTopo{k}', 0.036, (x, y, dz + hgt + 0.035), m=P['wood'], seg=10, front=front)
    rails = [((-E, -E), (E, -E), 0.18), ((E, -E), (E, E), 0.28), ((E, E), (-E, E), 0.28), ((-E, E), (-E, -E), 0.28)]
    for k, (a, b, hgt) in enumerate(rails):
        front = a[1] < -0.1 and b[1] < -0.1
        tube(root, f'n1_corrimao{k}', [(a[0], a[1], dz + hgt), (b[0], b[1], dz + hgt)], 0.025, P['wood_l'], segs=8, front=front)
        tube(root, f'n1_corrimaoB{k}', [(a[0], a[1], dz + hgt * 0.5), (b[0], b[1], dz + hgt * 0.5)], 0.018, P['wood_l'], segs=8, front=front)
    # escada no lado direito
    for side, yy in enumerate((-0.2, 0.08)):
        tube(root, f'n1_escadaTrilho{side}', [(0.86, yy, 0.07), (0.63, yy, dz + 0.1)], 0.024, P['wood_l'], segs=8)
    for k in range(7):
        t = (k + 0.7) / 8
        x = 0.86 + (0.63 - 0.86) * t
        z = 0.07 + (dz + 0.1 - 0.07) * t
        tube(root, f'n1_degrau{k}', [(x, -0.21, z), (x, 0.09, z)], 0.016, P['wood_l'], segs=6)
    # mastro e bandeirola
    tube(root, 'n1_mastro', [(-E, E, dz), (-E, E, dz + 0.95)], 0.022, P['wood'], segs=8)
    sphere(root, 'n1_mastroTopo', 0.036, (-E, E, dz + 0.97), m=P['gold'], seg=12)
    pen = cloth_grid(root, 'n1_bandeirola', 0.48, 0.24, 16, 4, [P['cream']],
                     shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.24 * (1 - u * 0.92))), thick=0.012)
    pen.location = (-E + 0.02, E, dz + 0.8)
    register_cloth(pen, flag_wave(0.48, amp=0.075, cycles=1, waves=1.2))
    # barril de flechas, aljava, corda, lanterna
    barrel(root, 'n1_barril', P, (0.24, 0.32, dz + 0.03))
    arrows_bundle(root, 'n1_flechas', P, (0.24, 0.32, dz + 0.2), n=7)
    torus(root, 'n1_rolo', (-0.33, 0.33, dz + 0.05), 0.07, 0.022, P['rope'], n=18, segs=6)
    torus(root, 'n1_rolo2', (-0.33, 0.33, dz + 0.085), 0.055, 0.02, P['rope'], n=18, segs=6)
    tube(root, 'n1_suporteLant', [(E, -E, dz + 0.22), (E + 0.14, -E - 0.04, dz + 0.22)], 0.012, P['iron'], segs=6)
    lantern(root, 'n1_lanterna', P, (E + 0.14, -E - 0.04, dz + 0.08), hang=0.13)
    # caixote no chao
    box(root, 'n1_caixote', (0.2, 0.2, 0.16), (-0.6, -0.18, 0.15), rot=(0, 0, 0.3), m=P['wood_l'], bev=0.02)
    box(root, 'n1_caixoteTampa', (0.22, 0.22, 0.03), (-0.6, -0.18, 0.235), rot=(0, 0, 0.3), m=P['wood'], bev=0.01)
    slots = [(-0.22, -0.12, dz + 0.03), (0.2, -0.14, dz + 0.03)]
    return {'slots': slots, 'lanterns': [(E + 0.14, -E - 0.04, dz + 0.08)]}


# ---------------------------------------------------------------- N2: base de arenito + toldo
def build_n2(P, root):
    plot(root, P, 'n2')
    dz = 1.1
    block_ring(root, 'n2_tambor', P, 0.76, 0.72, 0.07, 1.02, rows=5, per_row=13, depth=0.16)
    cyl(root, 'n2_nucleo', 0.66, 0.95, (0, 0, 0.55), m=P['mortar'], v=32, bev=0)
    torus(root, 'n2_aro', (0, 0, 1.04), 0.77, 0.045, P['wood'], n=40, segs=8)
    rr = random.Random(9)
    r_deck = 0.8
    for i in range(10):
        x = -r_deck + 0.16 * (i + 0.5)
        half = math.sqrt(max(0.01, r_deck ** 2 - x ** 2))
        box(root, f'n2_tabua{i}', (0.15, 2 * half, 0.055), (x, 0, dz - 0.02 + rr.uniform(-0.005, 0.005)),
            rot=(0, 0, rr.uniform(-0.015, 0.015)), m=P['wood_l'], bev=0.016)
    # postes e toldo
    top = 2.3
    posts = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        x, y = 0.56 * math.cos(a), 0.56 * math.sin(a)
        front = y < 0
        posts.append((x, y))
        tube(root, f'n2_poste{k}', [(x, y, dz - 0.05), (x, y, top + 0.02)], 0.05, P['wood'], segs=10, front=front,
             rfun=lambda t: 0.056 - 0.008 * t)
        torus(root, f'n2_amarra{k}', (x, y, dz + 0.08), 0.06, 0.016, P['rope'], n=14, segs=6, front=front)
        torus(root, f'n2_amarraT{k}', (x, y, top - 0.06), 0.058, 0.016, P['rope'], n=14, segs=6, front=front)
        sphere(root, f'n2_posteTopo{k}', 0.05, (x, y, top + 0.04), m=P['wood'], seg=12, front=front)
    Wd = 1.36

    def canopy_shape(u, v, co):
        x = (u - 0.5) * Wd
        y = (v - 0.5) * Wd
        peak = 0.2 * (1 - max(abs(u - 0.5), abs(v - 0.5)) * 2) ** 1.2
        return Vector((x, y, peak))
    can = cloth_grid(root, 'n2_toldo', 1, 1, 16, 16, [P['stripes']], shape=canopy_shape, thick=0.02)
    can.location = (0, 0, top + 0.04)

    def canopy_wave(co, ph):
        e = max(abs(co.x), abs(co.y)) / (Wd / 2)
        w = max(0.0, e - 0.55) / 0.45
        a = TAU * (ph + 0.9 * co.x + 0.6 * co.y)
        return Vector((co.x, co.y, co.z + 0.022 * w * math.sin(a)))
    register_cloth(can, canopy_wave)
    # sanefas recortadas nos 4 lados
    for k in range(4):
        rot = k * math.pi / 2

        def val_shape(u, v, co, rot=rot):
            sc = 0.07 * abs(math.sin(math.pi * u * 7))
            z = -v * (0.1 + sc)
            x = (u - 0.5) * Wd
            p = Vector((x, -Wd / 2, z))
            p.rotate(Euler((0, 0, rot)))
            return p
        vo = cloth_grid(root, f'n2_sanefa{k}', 1, 1, 42, 3, [P['stripes']], shape=val_shape, thick=0.016)
        vo.location = (0, 0, top + 0.04)

        def val_wave(co, ph, rot=rot):
            d = Vector((0, -1, 0))
            d.rotate(Euler((0, 0, rot)))
            w = max(0.0, -co.z) / 0.17
            a = TAU * (ph + 1.6 * (co.x + co.y))
            return co + d * (0.03 * w * math.sin(a))
        register_cloth(vo, val_wave)
    sphere(root, 'n2_pinaculo', 0.05, (0, 0, top + 0.3), m=P['gold'], seg=14)
    cyl(root, 'n2_pinaculoP', 0.025, 0.12, (0, 0, top + 0.38), r2=0.0, m=P['gold'], v=10, bev=0)
    # cordas penduradas no tambor (guirlanda)
    for k in range(3):
        a0 = math.radians(-150 + 60 * k)
        a1 = a0 + math.radians(60)
        pts = []
        for s in range(13):
            t = s / 12
            a = a0 + (a1 - a0) * t
            pts.append((0.8 * math.cos(a), 0.8 * math.sin(a), 0.95 - 0.1 * math.sin(math.pi * t)))
        tube(root, f'n2_guirlanda{k}', pts, 0.016, P['rope'], segs=6)
    # adereços no deque
    clay_pot(root, 'n2_pote1', P, (-0.56, 0.04, dz + 0.02))
    clay_pot(root, 'n2_pote2', P, (-0.5, 0.22, dz + 0.02), s=0.8)
    box(root, 'n2_suporte', (0.34, 0.06, 0.04), (0.05, 0.54, dz + 0.3), m=P['wood'], bev=0.01)
    for sx in (-1, 1):
        tube(root, f'n2_suportePe{sx}', [(0.05 + sx * 0.15, 0.54, dz), (0.05 + sx * 0.15, 0.54, dz + 0.34)], 0.018, P['wood'], segs=6)
    for k in range(5):
        x = -0.07 + 0.06 * k
        tube(root, f'n2_flechaR{k}', [(x, 0.52, dz + 0.02), (x + 0.01, 0.56, dz + 0.42)], 0.007, P['wood_l'], segs=5)
        cone = cyl(root, f'n2_penaR{k}', 0.02, 0.06, (x + 0.01, 0.56, dz + 0.4), r2=0.0, m=P['teal'] if k % 2 else P['cream'], v=4, bev=0)
    px, py = posts[3]
    lx, ly = px + 0.12, py - 0.06
    tube(root, 'n2_suporteLant', [(px, py, top - 0.12), (lx, ly, top - 0.12)], 0.01, P['iron'], segs=6)
    lantern(root, 'n2_lanterna', P, (lx, ly, top - 0.34), hang=0.2)
    torus(root, 'n2_rolo', (-0.62, 0.42, 0.7), 0.08, 0.02, P['rope'], axis='X', n=18, segs=6)
    slots = [(-0.24, -0.18, dz + 0.02), (0.22, -0.2, dz + 0.02)]
    return {'slots': slots, 'lanterns': [(lx, ly, top - 0.34)]}


# ---------------------------------------------------------------- N3: torre de arenito com ameias
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


def build_n3(P, root):
    plot(root, P, 'n3')
    fz = 2.02
    FRONT = -math.pi / 2

    def skip(a, z):
        if ang_near(a, FRONT, 0.3) and z < 0.72:
            return True
        if ang_near(a, math.radians(-50), 0.12) and 1.08 < z < 1.42:
            return True
        return False
    cyl(root, 'n3_rodape', 0.84, 0.14, (0, 0, 0.13), r2=0.8, m=P['sandstone'], v=40, bev=0.03)
    block_ring(root, 'n3_corpo', P, 0.74, 0.64, 0.2, 1.72, rows=9, per_row=14, depth=0.15, skip=skip)
    cyl(root, 'n3_nucleo', 0.66, 1.6, (0, 0, 0.98), r2=0.58, m=P['mortar'], v=36, bev=0)
    door(root, 'n3', P, FRONT, 0.72, 0.2, w=0.3, h=0.4)
    # janela seteira
    a = math.radians(-50)
    box(root, 'n3_seteira', (0.05, 0.1, 0.24), (0.62 * math.cos(a), 0.62 * math.sin(a), 1.25), rot=(0, 0, a + math.pi / 2), m=P['dark'], bev=0.01)
    # cornija com faixa entalhada
    cyl(root, 'n3_cornija', 0.7, 0.24, (0, 0, 1.84), r2=0.8, m=P['sandstone_l'], v=48, bev=0.025)
    for k in range(24):
        a = TAU * k / 24 - math.pi / 2
        tri_prism(root, f'n3_entalhe{k}', P, (0.755 * math.cos(a), 0.755 * math.sin(a), 1.84), a, 0.055, 1 if k % 2 else -1, P['terracotta'])
    for k in range(10):
        a = TAU * k / 10 - math.pi / 2 + 0.31
        box(root, f'n3_misula{k}', (0.06, 0.14, 0.09), (0.7 * math.cos(a), 0.7 * math.sin(a), 1.66), rot=(0, 0, a + math.pi / 2), m=P['wood'], bev=0.012)
    cyl(root, 'n3_piso', 0.8, 0.07, (0, 0, fz - 0.03), m=P['stone'], v=48, bev=0.02)
    # ameias
    n = 8
    for k in range(n):
        a = TAU * k / n - math.pi / 2 + math.pi / n
        front = math.sin(a) < -0.2
        box(root, f'n3_ameia{k}', (0.27, 0.15, 0.3), (0.72 * math.cos(a), 0.72 * math.sin(a), fz + 0.15), rot=(0, 0, a + math.pi / 2), m=P['sandstone'], bev=0.035, front=front)
        box(root, f'n3_ameiaTopo{k}', (0.3, 0.18, 0.05), (0.72 * math.cos(a), 0.72 * math.sin(a), fz + 0.31), rot=(0, 0, a + math.pi / 2), m=P['sandstone_l'], bev=0.02, front=front)
    for k in range(n):
        a = TAU * (k + 0.5) / n - math.pi / 2 + math.pi / n
        front = math.sin(a) < -0.2
        box(root, f'n3_mureta{k}', (0.24, 0.13, 0.12), (0.74 * math.cos(a), 0.74 * math.sin(a), fz + 0.06), rot=(0, 0, a + math.pi / 2), m=P['sandstone'], bev=0.03, front=front)
    banner(root, 'n3_estandarte', P, 0.0, -0.8, 1.62, w=0.36, h=0.6)
    a = math.radians(-128)
    tube(root, 'n3_suporteLant', [(0.68 * math.cos(a), 0.68 * math.sin(a), 0.86), (0.82 * math.cos(a), 0.82 * math.sin(a), 0.86)], 0.012, P['iron'], segs=6)
    lantern(root, 'n3_lanterna', P, (0.84 * math.cos(a), 0.84 * math.sin(a), 0.74), hang=0.1)
    clay_pot(root, 'n3_pote', P, (0.5, -0.62, 0.07), s=1.1)
    barrel(root, 'n3_barril', P, (0.3, 0.3, fz + 0.0), r=0.09, h=0.18)
    arrows_bundle(root, 'n3_flechas', P, (0.3, 0.3, fz + 0.16), n=6, seed=8)
    slots = [(-0.22, -0.16, fz + 0.01), (0.2, -0.2, fz + 0.01)]
    return {'slots': slots, 'lanterns': [(0.84 * math.cos(a), 0.84 * math.sin(a), 0.74)]}


# ---------------------------------------------------------------- N4: fortaleza da balestra
def build_n4(P, root):
    plot(root, P, 'n4')
    fz = 2.2
    box(root, 'n4_degrau1', (1.26, 1.26, 0.13), (0, 0, 0.13), m=P['sandstone'], bev=0.035)
    box(root, 'n4_degrau2', (1.18, 1.18, 0.13), (0, 0, 0.26), m=P['sandstone_l'], bev=0.035)
    # paredes em blocos (4 faces)
    rows, z0, z1 = 9, 0.33, 1.92
    h = (z1 - z0) / rows
    rr = random.Random(4)
    box(root, 'n4_nucleo', (1.08, 1.08, z1 - z0), (0, 0, (z0 + z1) / 2), m=P['mortar'], bev=0)
    for i in range(rows):
        zc = z0 + h * (i + 0.5)
        hw = 0.62 - 0.07 * (zc - z0) / (z1 - z0)
        per = 5
        for f in range(4):
            ang = f * math.pi / 2
            off = (i % 2) * 0.5
            for j in range(per + (1 if i % 2 else 0)):
                u0 = -hw + (2 * hw) * (j - off) / per
                u1 = u0 + 2 * hw / per
                u0, u1 = max(u0, -hw), min(u1, hw)
                if u1 - u0 < 0.05:
                    continue
                uc = (u0 + u1) / 2
                if f == 0 and abs(uc) < 0.22 and zc < 0.95:
                    continue
                p = Vector((uc, -hw, zc))
                p.rotate(Euler((0, 0, ang)))
                box(root, f'n4_bloco{i}_{f}_{j}', (u1 - u0 - 0.014, 0.14, h - 0.014), (p.x, p.y, zc), rot=(0, 0, ang), m=P['sandstone'], bev=0.026)
    # contrafortes nos cantos
    for k in range(4):
        a = math.radians(45 + 90 * k) + math.pi
        p = Vector((0.72 * math.cos(a), 0.72 * math.sin(a), 0.75))
        cb = cyl(root, f'n4_contraforte{k}', 0.22, 0.95, p, r2=0.1, m=P['sandstone_l'], v=4, bev=0.03)
        cb.rotation_euler = (0, 0, a + math.pi / 4)
        box(root, f'n4_contraOuro{k}', (0.2, 0.2, 0.05), (0.66 * math.cos(a), 0.66 * math.sin(a), 1.24), rot=(0, 0, a + math.pi / 4), m=P['gold'], bev=0.012)
    # faixas de ouro
    for k, zz in enumerate((1.22, 1.9)):
        hw = 0.62 - 0.07 * (zz - z0) / (z1 - z0) + 0.075
        box(root, f'n4_faixa{k}', (2 * hw + 0.02, 2 * hw + 0.02, 0.05), (0, 0, zz), m=P['gold'], bev=0.012)
    box(root, 'n4_cornija', (1.42, 1.42, 0.16), (0, 0, 2.02), m=P['sandstone_l'], bev=0.035)
    box(root, 'n4_piso', (1.3, 1.3, 0.06), (0, 0, fz - 0.06), m=P['stone'], bev=0.02)
    # torreoes de canto com capitel de ouro e ameias do meio
    C = 0.56
    for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        front = sy < 0
        box(root, f'n4_torreao{k}', (0.32, 0.32, 0.4), (sx * C, sy * C, fz + 0.18), m=P['sandstone'], bev=0.04, front=front)
        cap = cyl(root, f'n4_capitel{k}', 0.25, 0.12, (sx * C, sy * C, fz + 0.44), r2=0.05, m=P['gold'], v=4, bev=0.012, front=front)
        cap.rotation_euler = (0, 0, math.pi / 4)
        sphere(root, f'n4_capitelBola{k}', 0.035, (sx * C, sy * C, fz + 0.52), m=P['gold'], seg=10, front=front)
    for f in range(4):
        ang = f * math.pi / 2
        for j, u in enumerate((-0.2, 0.2)):
            p = Vector((u, -0.6, fz + 0.1))
            p.rotate(Euler((0, 0, ang)))
            front = f == 0
            box(root, f'n4_ameia{f}_{j}', (0.2, 0.12, 0.2), (p.x, p.y, p.z), rot=(0, 0, ang), m=P['sandstone'], bev=0.03, front=front)
        p = Vector((0, -0.62, fz + 0.03))
        p.rotate(Euler((0, 0, ang)))
        box(root, f'n4_mureta{f}', (0.9, 0.1, 0.08), (p.x, p.y, p.z), rot=(0, 0, ang), m=P['sandstone_l'], bev=0.025, front=(f == 0))
    for k, x in enumerate((-0.33, 0.33)):
        banner(root, f'n4_estandarte{k}', P, x, -0.72, 1.78, w=0.3, h=0.72)
    door(root, 'n4', P, -math.pi / 2, 0.6, 0.33, w=0.32, h=0.42, gold_key=True)
    for k, sx in enumerate((-1, 1)):
        tube(root, f'n4_suporteLant{k}', [(sx * 0.3, -0.62, 0.82), (sx * 0.3, -0.78, 0.82)], 0.012, P['iron'], segs=6)
        lantern(root, f'n4_lanterna{k}', P, (sx * 0.3, -0.8, 0.7), hang=0.1)
    # suporte de virotes e barril
    box(root, 'n4_rack', (0.36, 0.08, 0.04), (-0.32, 0.42, fz + 0.24), m=P['wood'], bev=0.01)
    for sx in (-1, 1):
        tube(root, f'n4_rackPe{sx}', [(-0.32 + sx * 0.16, 0.42, fz), (-0.32 + sx * 0.16, 0.42, fz + 0.26)], 0.02, P['wood'], segs=6)
    for k in range(4):
        x = -0.44 + 0.08 * k
        tube(root, f'n4_virote{k}', [(x, 0.4, fz + 0.02), (x, 0.46, fz + 0.44)], 0.012, P['wood_l'], segs=6)
        cyl(root, f'n4_viroteP{k}', 0.025, 0.07, (x, 0.465, fz + 0.47), r2=0.0, m=P['steel'], v=4, bev=0)
    barrel(root, 'n4_barril', P, (0.4, 0.38, fz), r=0.09, h=0.18)
    slots = [(0.0, 0.0, fz)]   # pivo da balestra
    return {'slots': slots, 'lanterns': [(-0.3, -0.8, 0.7), (0.3, -0.8, 0.7)]}


# ---------------------------------------------------------------- lote vazio
def build_lote(P, root):
    plot(root, P, 'lote')
    x, y = 0.5, 0.18
    z = 0.15
    tube(root, 'lote_estaca', [(x, y, z), (x, y, z + 0.8)], 0.024, P['wood'], segs=8)
    sphere(root, 'lote_estacaTopo', 0.034, (x, y, z + 0.82), m=P['gold'], seg=10)
    pen = cloth_grid(root, 'lote_bandeirola', 0.34, 0.18, 12, 3, [P['teal']],
                     shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.18 * (1 - u * 0.92))), thick=0.012)
    pen.location = (x + 0.01, y, z + 0.69)
    register_cloth(pen, flag_wave(0.34, amp=0.06, cycles=1, waves=1.1))
    # material de obra: tabuas empilhadas e blocos de arenito
    for k in range(3):
        box(root, f'lote_tabua{k}', (0.5, 0.09, 0.035), (-0.28, 0.3 + 0.004 * k, z + 0.02 + 0.037 * k),
            rot=(0, 0, 0.35 + 0.06 * k), m=P['wood_l'], bev=0.01)
    for k, (bx, by, bz) in enumerate(((-0.05, 0.42, 0), (0.1, 0.4, 0), (0.02, 0.41, 0.1))):
        box(root, f'lote_bloco{k}', (0.16, 0.12, 0.1), (bx, by, z + 0.05 + bz), rot=(0, 0, 0.2 * k), m=P['sandstone'], bev=0.025)
    torus(root, 'lote_corda', (-0.42, 0.05, z + 0.02), 0.07, 0.02, P['rope'], n=18, segs=6)
    return {'slots': [], 'lanterns': []}


# ---------------------------------------------------------------- arqueiro (figura esculpida, animada por codigo)
ARCHER_FACE = math.radians(-55)   # 3/4 de frente: olha para a direita e para a camera
ARCHER_VARIANTS = ('a1', 'a2', 'a3', 'a3b')
AIM = 4                           # quadros do arqueiro mirando (loop)


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


def build_archer(P, root, variant, tag=None):
    """Arqueiro de ~0.6 BU no estilo do conceito: figura de argila suave, com figurino em camadas.
    a1: capuz creme e mascara teal; a2: gorro e colete de couro; a3: capuz de elite com ouro;
    a3b: cabeca descoberta e cabelo preso; op: operador da balestra (elmo e armadura de bronze)."""
    tag = tag or root['set']
    parts = {'tag': tag, 'variant': variant}
    leather = P['leather']
    leather_d = mat('couro_escuro', '#6a4026', rough=0.6, var=0.05, bump=0.15)
    tunic = P['tunic']
    if variant == 'a3':
        tunic = mat('tunica_a3', '#efe2c4', rough=0.85, var=0.02, bump=0.08, sheen=0.3)
    if variant == 'op':
        tunic = mat('tunica_op', '#c9b48e', rough=0.85, var=0.02, bump=0.08, sheen=0.3)
    hood_m = P['hood'] if variant != 'a3' else mat('capuz_a3', '#f1e6c8', rough=0.85, var=0.02, bump=0.08, sheen=0.3)
    scarf_m = P['teal']
    body = bpy.data.objects.new(tag + '_corpo', None)
    root.users_collection[0].objects.link(body)
    body.parent = root
    body['set'] = root['set']
    body.rotation_euler = (0, 0, ARCHER_FACE)
    parts['body'] = body

    def p(o):
        o.parent = body
        return o
    # pernas e botas
    for s, yy in enumerate((-0.046, 0.046)):
        p(tube(root, f'{tag}_perna{s}', [(0.0, yy, 0.05), (0.0, yy * 0.9, 0.17)], 0.033, P['pants'], segs=10))
        p(blob(root, f'{tag}_bota{s}', 0.05, (0.018, yy * 1.05, 0.04), (1.35, 0.85, 0.85), leather))
        p(torus(root, f'{tag}_botaAba{s}', (0.004, yy, 0.085), 0.036, 0.012, leather_d if variant != 'op' else P['bronze'], n=14, segs=6))
    # tunica (saia rodada com dobras) e tronco
    fold = lambda a, z: 0.045 * math.sin(7 * a) * max(0.0, (0.28 - z) / 0.18)
    p(lathe(root, f'{tag}_saia', [(0.1, 0.122, 0.13), (0.15, 0.112, 0.12), (0.21, 0.098, 0.108), (0.27, 0.084, 0.096), (0.32, 0.076, 0.09)],
            tunic if variant != 'op' else leather, segs=14, wobble=fold, lv=2))
    p(lathe(root, f'{tag}_tronco', [(0.29, 0.072, 0.088), (0.34, 0.077, 0.094), (0.39, 0.081, 0.103), (0.43, 0.08, 0.108),
                                   (0.455, 0.066, 0.102), (0.475, 0.045, 0.064), (0.495, 0.03, 0.032)], tunic, segs=12, lv=2))
    if variant in ('a2', 'a3', 'op'):
        vest = P['bronze'] if variant == 'op' else (leather if variant == 'a2' else leather_d)
        p(lathe(root, f'{tag}_colete', [(0.295, 0.08, 0.096), (0.34, 0.085, 0.101), (0.39, 0.089, 0.109), (0.43, 0.087, 0.112),
                                        (0.452, 0.072, 0.106)], vest, segs=12, lv=2, caps=False, solid=0.006))
        for s, yy in enumerate((-0.1, 0.1)):
            p(blob(root, f'{tag}_ombreira{s}', 0.05, (0.0, yy, 0.452), (1.0, 0.8, 0.5), P['bronze'] if variant in ('op', 'a3') else leather))
        if variant == 'a3':
            p(torus(root, f'{tag}_coleteOuro', (0, 0, 0.452), 0.08, 0.006, P['gold'], n=20, segs=5))
    # cinto / faixa
    if variant == 'a1':
        p(lathe(root, f'{tag}_faixa', [(0.285, 0.083, 0.099), (0.33, 0.08, 0.096)], scarf_m, segs=12, lv=1))
        sash = cloth_grid(root, f'{tag}_faixaPonta', 0.04, 0.12, 2, 5, [scarf_m], thick=0.012)
        sash.parent = body
        sash.location = (0.06, 0.05, 0.3)
        sash.rotation_euler = (0, 0, math.radians(15))
        register_cloth(sash, hang_wave(0.12, amp=0.012, axis='Y', cycles=1, waves=0.5, top=0.0))
        parts['cloth'] = [sash]
    else:
        parts['cloth'] = []
        p(lathe(root, f'{tag}_cinto', [(0.29, 0.086, 0.102), (0.315, 0.084, 0.1)], leather_d, segs=12, lv=1))
        p(blob(root, f'{tag}_fivela', 0.022, (0.088, 0.0, 0.302), (0.5, 1.0, 0.85), P['gold'] if variant in ('a3', 'op') else P['iron']))
        flap = cloth_grid(root, f'{tag}_aba', 0.07, 0.15, 2, 5, [scarf_m if variant != 'op' else P['plume']], thick=0.012)
        flap.parent = body
        flap.location = (0.085, -0.035, 0.29)
        flap.rotation_euler = (0, 0, math.radians(90))
        register_cloth(flap, hang_wave(0.15, amp=0.01, axis='X', cycles=1, waves=0.4, top=0.0))
        parts['cloth'].append(flap)
    # aljava e alca
    if variant != 'op':
        p(tube(root, f'{tag}_aljava', [(-0.095, 0.045, 0.31), (-0.125, 0.075, 0.55)], 0.036, leather, segs=12,
               rfun=lambda t: 0.034 + 0.006 * t))
        p(torus(root, f'{tag}_aljavaBoca', (-0.125, 0.075, 0.55), 0.04, 0.009, leather_d, n=14, segs=5))
        for k in range(4):
            a = k * 1.6
            q = Vector((-0.125 + 0.016 * math.cos(a), 0.075 + 0.016 * math.sin(a), 0.56))
            tube(root, f'{tag}_aljavaHaste{k}', [q, q + Vector((-0.01, 0.006, 0.06))], 0.005, P['wood_l'], segs=5).parent = body
            fe = cyl(root, f'{tag}_aljavaPena{k}', 0.016, 0.045, q + Vector((-0.012, 0.007, 0.08)), r2=0.004,
                     m=P['cream'] if k % 2 else P['teal'], v=5, bev=0)
            fe.parent = body
        p(tube(root, f'{tag}_alca', [(-0.05, 0.1, 0.46), (0.02, 0.098, 0.455), (0.086, 0.04, 0.4), (0.092, -0.03, 0.34), (0.06, -0.09, 0.3)],
               0.011, leather_d, segs=6))
    # lenco no pescoco + caida nas costas
    p(lathe(root, f'{tag}_lenco', [(0.455, 0.07, 0.085), (0.47, 0.072, 0.086), (0.49, 0.06, 0.07), (0.5, 0.048, 0.055)],
            scarf_m if variant != 'op' else P['plume'], segs=12, lv=2))
    scarf = cloth_grid(root, f'{tag}_lencoPonta', 0.045, 0.14, 2, 6, [scarf_m if variant != 'op' else P['plume']], thick=0.014)
    scarf.parent = body
    scarf.location = (-0.07, -0.03, 0.48)
    scarf.rotation_euler = (0, 0, math.pi / 2)
    register_cloth(scarf, hang_wave(0.14, amp=0.035, axis='Y', cycles=1, waves=0.6, top=0.0))
    parts['scarf'] = scarf
    # cabeca (pivo no pescoco)
    head = bpy.data.objects.new(tag + '_cabecaPivo', None)
    root.users_collection[0].objects.link(head)
    head.parent = body
    head.location = (0, 0, 0.49)
    head['set'] = root['set']
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    hc = Vector((0.006, 0, 0.055))   # centro da cabeca, local ao pivo
    ph(blob(root, f'{tag}_cabeca', 0.066, hc, (1.0, 0.96, 1.06), P['skin']))
    if variant not in ('a1', 'a3'):
        ph(blob(root, f'{tag}_nariz', 0.013, hc + Vector((0.062, 0, -0.006)), (1, 0.8, 1.1), P['skin']))
    for s, yy in enumerate((-0.024, 0.024)):
        ph(blob(root, f'{tag}_olho{s}', 0.0095, hc + Vector((0.061, yy, 0.012)), (0.6, 1.0, 1.2), P['eye']))
        ph(box(root, f'{tag}_sobrancelha{s}', (0.008, 0.022, 0.006), hc + Vector((0.056, yy, 0.031)), rot=(math.radians(-12 if yy > 0 else 12), 0, 0),
               m=mat('sobrancelha', '#4a2c18', rough=0.8, var=0, bump=0), bev=0.002))
    masked = variant in ('a1', 'a3')
    if masked:
        # mascara de pano cobrindo nariz e boca
        mk = lathe(root, f'{tag}_mascara', [(-0.07, 0.07, 0.07), (-0.04, 0.071, 0.07), (-0.01, 0.071, 0.07), (0.004, 0.066, 0.064)],
                   scarf_m, segs=14, lv=2, caps=False, solid=0.008)
        mk.parent = head
        mk.location = hc
    if variant in ('a1', 'a3'):
        # capuz pontudo com abertura para o rosto e manto nos ombros
        def hood_cut(c):
            ang = math.atan2(c.y, c.x)
            return abs(ang) < math.radians(52) and -0.045 < c.z < 0.06 and c.x > 0
        hood_prof = [(-0.07, 0.105, 0.118), (-0.045, 0.092, 0.1), (-0.01, 0.084, 0.088), (0.03, 0.082, 0.085, -0.004),
                     (0.06, 0.074, 0.078, -0.012), (0.09, 0.056, 0.058, -0.025), (0.115, 0.034, 0.034, -0.042),
                     (0.135, 0.014, 0.014, -0.062), (0.145, 0.0, 0.0, -0.075)]
        hd = lathe(root, f'{tag}_capuz', hood_prof, hood_m, segs=16, lv=2, caps=False, solid=0.01, cut=hood_cut)
        hd.parent = head
        hd.location = hc
        if variant == 'a3':
            tr = tube(root, f'{tag}_capuzOuro', [hc + Vector((0.07 * math.cos(a), 0.075 * math.sin(a), 0.055 * math.sin(abs(a)) * 0 + 0.0))
                                                 for a in [math.radians(x) for x in range(-55, 56, 10)]], 0.006, P['gold'], segs=5)
            tr.parent = head
    elif variant == 'a2':
        cap = lathe(root, f'{tag}_gorro', [(0.012, 0.072, 0.072), (0.04, 0.071, 0.071), (0.065, 0.058, 0.058), (0.085, 0.032, 0.032), (0.092, 0.0, 0.0)],
                    mat('gorro', '#7a5233', rough=0.85, var=0.04, bump=0.15), segs=14, lv=2, caps=False, solid=0.008)
        cap.parent = head
        cap.location = hc
        for k, zz in enumerate((0.018, 0.034)):
            t = torus(root, f'{tag}_turbante{k}', hc + Vector((0, 0, zz)), 0.072 - 0.004 * k, 0.012, mat('turbante', '#e8d8b4', rough=0.85, var=0.02, bump=0.1), n=18, segs=6)
            t.parent = head
    elif variant == 'a3b':
        hair = mat('cabelo', '#4a2c18', rough=0.7, var=0.03, bump=0.25)
        def hair_cut(c):
            ang = math.atan2(c.y, c.x)
            return abs(ang) < math.radians(48) and c.z < 0.03 and c.x > 0
        hr = lathe(root, f'{tag}_cabelo', [(-0.05, 0.07, 0.072), (-0.01, 0.073, 0.075), (0.03, 0.07, 0.072), (0.06, 0.05, 0.052), (0.074, 0.0, 0.0)],
                   hair, segs=14, lv=2, caps=False, solid=0.008, cut=hair_cut)
        hr.parent = head
        hr.location = hc
        tl = tube(root, f'{tag}_rabo', [hc + Vector((-0.07, 0, 0.0)), hc + Vector((-0.09, 0.005, -0.05)), hc + Vector((-0.085, 0.01, -0.1))],
                  0.02, hair, segs=8, rfun=lambda t: 0.022 - 0.012 * t)
        tl.parent = head
        tie = torus(root, f'{tag}_amarra', hc + Vector((-0.075, 0.002, -0.012)), 0.017, 0.006, scarf_m, axis='X', n=12, segs=5)
        tie.parent = head
    elif variant == 'op':
        hm = lathe(root, f'{tag}_elmo', [(-0.02, 0.078, 0.078), (0.02, 0.078, 0.078), (0.06, 0.064, 0.064), (0.09, 0.034, 0.034), (0.1, 0.0, 0.0)],
                   P['bronze'], segs=16, lv=2, caps=False, solid=0.01)
        hm.parent = head
        hm.location = hc
        nb = box(root, f'{tag}_nasal', (0.012, 0.014, 0.05), hc + Vector((0.08, 0, -0.005)), m=P['bronze'], bev=0.004)
        nb.parent = head
        crest = [hc + Vector((-0.09 + 0.17 * t, 0, 0.085 + 0.05 * math.sin(math.pi * t))) for t in [k / 10 for k in range(11)]]
        cr = tube(root, f'{tag}_crista', crest, 0.024, P['plume'], segs=8, rfun=lambda t: 0.028 - 0.014 * abs(t - 0.45))
        cr.parent = head
    # bracos: recriados a cada quadro (IK de dois ossos); luvas grandes de couro
    parts['sleeve'] = tunic if variant != 'op' else P['bronze']
    parts['glove'] = leather if variant != 'a3' else leather_d
    parts['bracer'] = leather_d
    for side in ('Arco', 'Corda'):
        parts['luva' + side] = blob(root, f'{tag}_luva{side}', 0.032, (0, 0, 0), (1.25, 0.95, 1.0), parts['glove'])
    return parts


def bow_points(G, up, back, L, flex, n=17):
    pts = []
    for k in range(n):
        t = (k / (n - 1)) * 2 - 1
        rec = 0.025 * max(0.0, (abs(t) - 0.72) / 0.28) ** 2
        pts.append(G + up * (L * t) + back * ((0.075 + flex) * t * t - rec))
    return pts


def pose_archer(parts, P, root, st):
    """st: dict com grip, hand (local do corpo), up (inclinacao do arco), draw (0..1), arrow ('nocked'|'hand'|None),
    breathe, head_yaw, head_pitch, face, ph (fase do tecido), bow (bool), pole_bow/pole_str."""
    tag = parts['tag']
    body = parts['body']
    br = st.get('breathe', 0.0)
    body.scale = (1, 1, 1 + 0.018 * br)
    body.rotation_euler = (0, 0, st.get('face', ARCHER_FACE))
    parts['head'].rotation_euler = (0, st.get('head_pitch', 0.0) + 0.03 * br, st.get('head_yaw', 0.0))
    bpy.context.view_layer.update()
    M = body.matrix_world.copy()
    Mi = root.matrix_world.inverted()

    def W(v):
        return Mi @ (M @ Vector(v))
    ph = st.get('ph', 0.0)
    for c in [parts['scarf']] + parts.get('cloth', []):
        base, fn = CLOTH[c.name]
        for v, b in zip(c.data.vertices, base):
            v.co = fn(b, ph)
        c.data.update()
    G = Vector(st['grip'])
    H = Vector(st['hand'])
    shoulders = {'Arco': Vector((0.0, 0.098, 0.448 + 0.008 * br)), 'Corda': Vector((0.0, -0.098, 0.448 + 0.008 * br))}
    poles = {'Arco': Vector(st.get('pole_bow', (-0.2, 1.0, -0.8))), 'Corda': Vector(st.get('pole_str', (-1.0, -0.7, 0.1)))}
    targets = {'Arco': G + Vector((-0.012, 0, 0)), 'Corda': H}
    for side in ('Arco', 'Corda'):
        S = shoulders[side]
        E, Hh = two_bone(S, targets[side], 0.125, 0.12, poles[side])
        up = ensure_mesh(root, f'{tag}_bracoSup{side}', parts['sleeve'])
        set_mesh_tube(up, [W(S), W(S.lerp(E, 0.5)), W(E)], 0.034, segs=10, rfun=lambda t: 0.036 - 0.01 * t)
        lo = ensure_mesh(root, f'{tag}_antebraco{side}', parts['bracer'])
        set_mesh_tube(lo, [W(E), W(E.lerp(Hh, 0.5)), W(Hh)], 0.026, segs=10, rfun=lambda t: 0.027 - 0.004 * t + 0.006 * max(0, t - 0.75) / 0.25)
        el = ensure_mesh(root, f'{tag}_cotovelo{side}', parts['sleeve'])
        set_mesh_tube(el, [W(E - (E - S).normalized() * 0.012), W(E + (Hh - E).normalized() * 0.012)], 0.03, segs=10)
        g = parts['luva' + side]
        g.location = W(Hh + (Hh - E).normalized() * 0.018)
        d = (W(Hh) - W(E)).normalized()
        g.rotation_euler = d.to_track_quat('X', 'Z').to_euler()
    bow_objs = [f'{tag}_arco', f'{tag}_arcoPunho', f'{tag}_corda', f'{tag}_flecha', f'{tag}_flechaPonta', f'{tag}_flechaPena']
    if not st.get('bow', True):
        for nm in bow_objs:
            o = bpy.data.objects.get(nm)
            if o:
                o.hide_render = o.hide_viewport = True
        return
    up_v = Vector(st.get('up', (0.0, 0.1, 1.0))).normalized()
    bc = Vector(st.get('bow_back', (0, 0, 0)))
    if bc.length < 1e-6:
        bc = Vector((0, 0, G.z)) - G
    back = (bc - up_v * bc.dot(up_v)).normalized()
    draw = st.get('draw', 0.0)
    flex = 0.03 * draw
    L = 0.2
    pts = bow_points(G, up_v, back, L, flex)
    bow = ensure_mesh(root, f'{tag}_arco', P['wood'])
    set_mesh_tube(bow, [W(q) for q in pts], 0.013, segs=8, rfun=lambda t: 0.007 + 0.009 * (1 - abs(t - 0.5) * 2))
    grip_m = ensure_mesh(root, f'{tag}_arcoPunho', parts['bracer'])
    set_mesh_tube(grip_m, [W(G - up_v * 0.035), W(G + up_v * 0.035)], 0.019, segs=8)
    tip_top, tip_bot = pts[-1], pts[0]
    rest_mid = (tip_top + tip_bot) / 2
    nock = Vector(st['nock']) if st.get('nock') else rest_mid
    string = ensure_mesh(root, f'{tag}_corda', P['cream'])
    set_mesh_tube(string, [W(tip_top), W(nock), W(tip_bot)], 0.0055, segs=5)
    ar = ensure_mesh(root, f'{tag}_flecha', P['wood_l'])
    hd = ensure_mesh(root, f'{tag}_flechaPonta', P['steel'])
    fe = ensure_mesh(root, f'{tag}_flechaPena', P['teal'])
    mode = st.get('arrow')
    if mode == 'nocked':
        a0 = nock
        dirv = (G + up_v * 0.012 - nock).normalized()
    elif mode == 'hand':
        a0 = H + Vector((0.0, 0.0, -0.06))
        dirv = Vector((0.25, 0.05, 1)).normalized()
    if mode in ('nocked', 'hand'):
        a1 = a0 + dirv * 0.4
        set_mesh_tube(ar, [W(a0), W(a1)], 0.0075, segs=6)
        set_mesh_tube(hd, [W(a1), W(a1 + dirv * 0.05)], 0.017, segs=4, rfun=lambda t: 0.017 * (1 - t) + 0.001)
        set_mesh_tube(fe, [W(a0 + dirv * 0.01), W(a0 + dirv * 0.07)], 0.016, segs=3, rfun=lambda t: 0.004 + 0.014 * (1 - t))
        for o in (ar, hd, fe):
            o.hide_render = o.hide_viewport = False
    else:
        for o in (ar, hd, fe):
            o.hide_render = o.hide_viewport = True
    for o in (bow, grip_m, string):
        o.hide_render = o.hide_viewport = False


NOCK_FULL = (0.015, -0.04, 0.485)


def archer_state(mode, f):
    """Pose do arqueiro para cada quadro. idle: parado olhando em volta (arco baixo);
    aim: mirando (corda puxada); shoot: solta no quadro 0, pega flecha na aljava, encaixa e puxa."""
    aim_grip = (0.235, 0.06, 0.43)
    aim_up = (0.04, 0.16, 1.0)
    if mode == 'idle':
        ph = f / IDLE
        s = math.sin(TAU * ph)
        return dict(grip=(0.085, 0.13, 0.25 + 0.006 * s), up=(0.28, 0.05, 1.0), bow_back=(-0.05, -0.08, 0.0),
                    hand=(0.075, -0.12, 0.27 + 0.005 * s), pole_str=(-0.3, -1.0, -0.6), pole_bow=(-0.4, 1.0, -0.4),
                    draw=0.0, arrow=None, breathe=s, head_yaw=0.32 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    if mode == 'aim':
        ph = f / AIM
        s = math.sin(TAU * ph)
        return dict(grip=(aim_grip[0], aim_grip[1], aim_grip[2] + 0.004 * s), up=aim_up, hand=NOCK_FULL, nock=NOCK_FULL,
                    draw=0.9, arrow='nocked', breathe=0.4 * s, head_yaw=0.12, head_pitch=-0.04, ph=ph)
    nock_rest = Vector(aim_grip) + Vector((-0.085, -0.012, 0.0))
    seq = [
        dict(hand=(-0.07, -0.1, 0.5), nock=None, draw=0.0, arrow=None, grip=(0.255, 0.06, 0.445), pole_str=(-1.0, -0.8, 0.3)),
        dict(hand=(-0.09, -0.11, 0.48), nock=None, draw=0.0, arrow=None, grip=(0.245, 0.06, 0.437), pole_str=(-1.0, -0.8, 0.2)),
        dict(hand=(-0.11, -0.01, 0.6), nock=None, draw=0.0, arrow=None, pole_str=(-0.4, -1.0, 0.5)),
        dict(hand=(-0.07, 0.0, 0.62), nock=None, draw=0.0, arrow='hand', pole_str=(-0.3, -1.0, 0.4)),
        dict(hand=tuple(nock_rest), nock=tuple(nock_rest), draw=0.0, arrow='nocked', pole_str=(-0.6, -1.0, -0.3)),
        dict(hand=tuple(nock_rest.lerp(Vector(NOCK_FULL), 0.4)), nock=tuple(nock_rest.lerp(Vector(NOCK_FULL), 0.4)), draw=0.35, arrow='nocked'),
        dict(hand=tuple(nock_rest.lerp(Vector(NOCK_FULL), 0.75)), nock=tuple(nock_rest.lerp(Vector(NOCK_FULL), 0.75)), draw=0.65, arrow='nocked'),
        dict(hand=NOCK_FULL, nock=NOCK_FULL, draw=0.9, arrow='nocked'),
    ][f]
    st = dict(grip=aim_grip, up=aim_up, breathe=0.0, head_yaw=0.12, head_pitch=-0.04, ph=f / SHOOT)
    st.update(seq)
    return st


def archer_frame(parts, P, root, mode, f):
    pose_archer(parts, P, root, archer_state(mode, f))


def pose_operator(op, P, root, ph=0.0, crank=0.0):
    s = math.sin(TAU * ph)
    pose_archer(op, P, root, dict(bow=False, face=0.25, grip=(0.1, 0.11, 0.3 + 0.03 * abs(crank)), hand=(0.11 + 0.05 * crank, -0.11, 0.3 + 0.04 * abs(crank)),
                                  pole_bow=(-0.5, 1.0, -0.6), pole_str=(-0.5, -1.0, -0.6), breathe=s, head_yaw=0.05 * s, ph=ph))


# ---------------------------------------------------------------- balestra (gira e dispara)
def build_ballista(P, root):
    tag = 'bal'
    piv = bpy.data.objects.new('bal_pivo', None)
    root.users_collection[0].objects.link(piv)
    piv.parent = root
    piv['set'] = tag
    parts = {'pivot': piv}
    rec = bpy.data.objects.new('bal_recuo', None)
    root.users_collection[0].objects.link(rec)
    rec.parent = piv
    rec['set'] = tag
    parts['recoil'] = rec

    def p(o, par=rec):
        o.parent = par
        return o
    p(cyl(root, 'bal_prato', 0.36, 0.06, (0, 0, 0.03), m=P['wood'], v=36, bev=0.015), piv)
    p(torus(root, 'bal_pratoAro', (0, 0, 0.05), 0.36, 0.018, P['iron'], n=36, segs=6), piv)
    for k in range(8):
        a = TAU * k / 8
        p(sphere(root, f'bal_rebite{k}', 0.02, (0.33 * math.cos(a), 0.33 * math.sin(a), 0.065), m=P['gold'], seg=8), piv)
    # cavalete em A
    for s in (-1, 1):
        p(tube(root, f'bal_caval{s}', [(-0.12, s * 0.14, 0.06), (0.02, s * 0.03, 0.34)], 0.026, P['wood'], segs=8))
        p(tube(root, f'bal_cavalB{s}', [(0.16, s * 0.14, 0.06), (0.02, s * 0.03, 0.34)], 0.026, P['wood'], segs=8))
    p(tube(root, 'bal_eixo', [(0.02, -0.06, 0.34), (0.02, 0.06, 0.34)], 0.03, P['iron'], segs=8))
    # coronha
    p(box(root, 'bal_coronha', (0.74, 0.1, 0.075), (0.04, 0, 0.4), m=P['wood_l'], bev=0.018))
    p(box(root, 'bal_trilho', (0.62, 0.03, 0.02), (0.06, 0, 0.445), m=P['wood'], bev=0.006))
    p(cyl(root, 'bal_guincho', 0.05, 0.16, (-0.3, 0, 0.4), rot=(math.pi / 2, 0, 0), m=P['wood'], v=16, bev=0.01))
    for s in (-1, 1):
        p(tube(root, f'bal_manivela{s}', [(-0.3, s * 0.09, 0.4), (-0.3, s * 0.11, 0.48), (-0.34, s * 0.13, 0.5)], 0.012, P['iron'], segs=6))
    p(box(root, 'bal_frente', (0.08, 0.14, 0.1), (0.4, 0, 0.42), m=P['gold'], bev=0.015))
    # operador (gira junto)
    op = build_archer(P, root, 'op', tag='balop')
    op['body'].parent = piv
    op['body'].location = (-0.4, -0.26, 0.06)
    parts['op'] = op
    return parts


def pose_ballista(parts, P, root, yaw, draw=1.0, recoil=0.0, bolt=True, op_ph=0.0):
    piv = parts['pivot']
    piv.rotation_euler = (0, 0, yaw)
    parts['recoil'].location = (-0.05 * recoil, 0, 0)
    bpy.context.view_layer.update()
    M = parts['recoil'].matrix_world.copy()
    Mi = root.matrix_world.inverted()

    def W(v):
        return Mi @ (M @ Vector(v))
    flex = 0.05 * draw
    arms = []
    for s in (-1, 1):
        pts = []
        for k in range(9):
            t = k / 8
            y = s * 0.42 * t
            x = 0.36 - (0.08 + flex) * t ** 1.6
            pts.append(W((x, y, 0.43)))
        arms.append(pts)
    a = ensure_mesh(root, 'bal_bracoE', P['wood'])
    set_mesh_tube(a, list(reversed(arms[0])) + arms[1][1:], 0.03, segs=8, rfun=lambda t: 0.034 - 0.016 * abs(t - 0.5) * 2)
    for s, pts in zip((-1, 1), arms):
        cap = ensure_mesh(root, f'bal_ponteira{s}', P['gold'])
        tip = pts[-1]
        set_mesh_tube(cap, [tip, tip + (tip - pts[-2]).normalized() * 0.04], 0.022, segs=6)
    nock_x = 0.36 - 0.5 * draw
    tipL, tipR = arms[0][-1], arms[1][-1]
    corda = ensure_mesh(root, 'bal_corda', P['cream'])
    set_mesh_tube(corda, [tipL, W((nock_x, 0, 0.45)), tipR], 0.009, segs=5)
    bt = ensure_mesh(root, 'bal_virote', P['wood_l'])
    bh = ensure_mesh(root, 'bal_virotePonta', P['steel'])
    if bolt:
        set_mesh_tube(bt, [W((nock_x, 0, 0.47)), W((0.6, 0, 0.47))], 0.016, segs=6)
        set_mesh_tube(bh, [W((0.6, 0, 0.47)), W((0.7, 0, 0.47))], 0.034, segs=4, rfun=lambda t: 0.034 * (1 - t) + 0.002)
    bt.hide_render = bh.hide_render = not bolt
    bt.hide_viewport = bh.hide_viewport = not bolt
    # operador: parado com as maos a frente; na recarga puxa a alavanca (mao vai e volta)
    crank = 0.0 if bolt or draw == 0 else math.sin(TAU * draw * 1.5)
    pose_operator(parts['op'], P, root, ph=op_ph, crank=crank)


BAL_SEQ = [  # disparo: solta, recua, assenta, gira o guincho, recarrega
    dict(draw=0.0, recoil=1.0, bolt=False),
    dict(draw=0.0, recoil=0.55, bolt=False),
    dict(draw=0.0, recoil=0.15, bolt=False),
    dict(draw=0.2, recoil=0.0, bolt=False),
    dict(draw=0.45, recoil=0.0, bolt=False),
    dict(draw=0.7, recoil=0.0, bolt=False),
    dict(draw=0.9, recoil=0.0, bolt=False),
    dict(draw=1.0, recoil=0.0, bolt=True),
]


# ---------------------------------------------------------------- projeteis (flecha, virote, flecha cravada)
def arrow_into(root, name, P, length, r, fletch, head_m, band=None, fin_w=None):
    """Flecha ao longo de +X, centrada na origem. Ponta em folha, penas largas e macias."""
    h = length / 2
    fin_w = fin_w or 0.055 * length / 0.55
    tube(root, name + '_haste', [(-h, 0, 0), (h - 0.06 * length / 0.55, 0, 0)], r, P['wood_l'], segs=8)
    hl = 0.13 * length
    tube(root, name + '_ponta', [(h - hl, 0, 0), (h - hl * 0.55, 0, 0), (h, 0, 0)], r * 2.6, head_m, segs=6,
         rfun=lambda t: r * (2.6 * math.sin(math.pi * min(1, t * 1.25)) * (1 - t) + 0.25))
    tube(root, name + '_colar', [(h - hl - 0.012, 0, 0), (h - hl + 0.012, 0, 0)], r * 1.5, P['iron'] if band is None else band, segs=8)
    for k in range(3):
        a = (math.pi / 2, -math.pi / 2, 0.0)[k]
        pts = []
        for j in range(7):
            t = j / 6
            pts.append((-h + 0.03 + 0.2 * length * t, 0, 0))
        fin = tube(root, f'{name}_pena{k}', pts, 0.02, fletch[k % len(fletch)], segs=4,
                   rfun=lambda t: 0.006 + fin_w * math.sin(math.pi * (0.15 + 0.85 * t)) * (1 - 0.35 * t))
        fin.scale = (1, 0.16, 1)
        fin.rotation_euler = (a, 0, 0)
        fin.location = (0, -0.015 * math.sin(a), 0.015 * math.cos(a)) if k < 2 else (0, -0.012, 0)
    sphere(root, name + '_nock', r * 1.4, (-h, 0, 0), m=P['wood'], seg=10)


def build_proj(P):
    out = {}
    for key, label in (('flecha', 'Flecha'), ('virote', 'Virote'), ('cravada', 'Flecha cravada')):
        c = coll_for(label)
        out[key] = make_root('raiz_' + key, key, c)
    arrow_into(out['flecha'], 'fl', P, 0.6, 0.026, [P['teal'], P['teal'], P['cream']], P['steel'], fin_w=0.075)
    arrow_into(out['virote'], 'vi', P, 0.95, 0.03, [P['terracotta'], P['cream'], P['terracotta']], P['steel'], band=P['gold'])
    # flecha cravada na areia: inclinada, meio enterrada, com um montinho de areia
    r = out['cravada']
    arrow_into(r, 'cr', P, 0.6, 0.026, [P['teal'], P['teal'], P['cream']], P['steel'], fin_w=0.075)
    piv = bpy.data.objects.new('cr_pivo', None)
    r.users_collection[0].objects.link(piv)
    piv.parent = r
    piv['set'] = 'cravada'
    for o in list(r.children):
        if o is not piv:
            o.parent = piv
    piv.rotation_euler = (0, math.radians(52), math.radians(-25))
    piv.location = (-0.17 * math.cos(math.radians(52)), 0, 0.17 * math.sin(math.radians(52)) - 0.02)
    sphere(r, 'cr_monte', 0.07, (0.0, 0, 0.0), scale=(1.3, 1.1, 0.35), m=P['sand'], seg=14)
    for k in range(3):
        a = TAU * k / 3 + 0.5
        sphere(r, f'cr_grao{k}', 0.018, (0.1 * math.cos(a), 0.08 * math.sin(a), 0.005), scale=(1.2, 1, 0.6), m=P['sand'], seg=8)
    return out


# ---------------------------------------------------------------- cena, luz, camera
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
    wpx = int(math.ceil((x1 - x0) * PX_PER_BU))
    hpx = int(math.ceil((y1 - y0) * PX_PER_BU))
    x1 = x0 + wpx / PX_PER_BU
    y1 = y0 + hpx / PX_PER_BU
    sc = bpy.context.scene
    sc.render.resolution_x = wpx
    sc.render.resolution_y = hpx
    cam.data.ortho_scale = wpx / PX_PER_BU
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cam.location = Rv * cx + Uv * cy - Fv * 20
    return wpx, hpx, (x0, y1)  # canto superior esquerdo no plano da camera


def project(pt, origin_tl):
    """Ponto do mundo -> pixel (x para a direita, y para baixo) na imagem enquadrada."""
    Rv, Uv, Fv = cam_axes()
    p = Vector(pt)
    return ((p.dot(Rv) - origin_tl[0]) * PX_PER_BU, (origin_tl[1] - p.dot(Uv)) * PX_PER_BU)


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


# ---------------------------------------------------------------- montagem
BUILT = {}


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


def build(showcase=False):
    global COLL
    clear_scene()
    sc = bpy.context.scene
    COLL = sc.collection
    cam = setup_scene()
    P = palette()
    spec = [('n1', 'Torre N1', build_n1), ('n2', 'Torre N2', build_n2), ('n3', 'Torre N3', build_n3),
            ('n4', 'Torre N4 Balestra', build_n4), ('lote', 'Lote vazio', build_lote)]
    for key, label, fn in spec:
        c = coll_for(label)
        root = make_root('raiz_' + key, key, c)
        BUILT[key] = fn(P, root)
        for o in bpy.data.objects:
            if o.get('set') == key and o.parent == root and not o.get('plot'):
                o.location.z += LIFT
        BUILT[key]['slots'] = [(x, y, z + LIFT) for x, y, z in BUILT[key]['slots']]
        BUILT[key]['lanterns'] = [(x, y, z + LIFT) for x, y, z in BUILT[key]['lanterns']]
    for v in ARCHER_VARIANTS:
        c = coll_for('Arqueiro ' + v)
        root = make_root('raiz_' + v, v, c)
        BUILT[v] = build_archer(P, root, v)
        archer_frame(BUILT[v], P, root, 'idle', 0)
    c = coll_for('Balestra')
    root = make_root('raiz_bal', 'bal', c)
    BUILT['bal'] = build_ballista(P, root)
    pose_ballista(BUILT['bal'], P, root, yaw=math.radians(-30))
    BUILT['proj'] = build_proj(P)
    apply_cloth(0.0)
    if showcase:
        layout_showcase(P)
    bpy.context.view_layer.update()
    return {'objetos': len(bpy.data.objects)}


def layout_showcase(P):
    """Organiza tudo lado a lado para ver no Blender, com arqueiros nos postos."""
    xs = {'lote': -6.6, 'n1': -4.2, 'n2': -1.5, 'n3': 1.3, 'n4': 4.2}
    for k, x in xs.items():
        SETS[k].location = (x, 0, 0)
    for i, k in enumerate(('flecha', 'virote', 'cravada')):
        SETS[k].location = (-6.6 + 1.2 * i, -1.6, 0.3 if k != 'cravada' else 0)
    tier_archer = {'n1': ('a1', 'a1'), 'n2': ('a2', 'a2'), 'n3': ('a3', 'a3b')}
    # arqueiros "de verdade" ficam enfileirados atras; nos postos vao instancias
    for i, v in enumerate(ARCHER_VARIANTS):
        SETS[v].location = (-1.5 + 1.0 * i, 3.0, 0)
    for k, vs in tier_archer.items():
        for j, s in enumerate(BUILT[k]['slots']):
            v = vs[j]
            coll = SETS[v].users_collection[0]
            e = bpy.data.objects.new(f'inst_{k}_{j}', None)
            e.instance_type = 'COLLECTION'
            e.instance_collection = coll
            SETS[k].users_collection[0].objects.link(e)
            e.parent = SETS[k]
            e.location = Vector(s) - SETS[v].location
            e['set'] = k
    s = BUILT['n4']['slots'][0]
    SETS['bal'].location = Vector(s) + SETS['n4'].location
    # camera de vitrine
    cam = bpy.data.objects['CamJogo']
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'ChaoSombra']
    lo, hi = bounds_of(objs)
    frame_camera(cam, lo, hi, margin=(0.4, 0.4, 0.4, 0.4))
    sc = bpy.context.scene
    f = 1600 / sc.render.resolution_x
    sc.render.resolution_percentage = max(10, min(100, int(f * 100)))


# ---------------------------------------------------------------- render de todos os quadros
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


def render_build(key, d):
    """Construcao: cada peca surge com um quique, das mais baixas para as mais altas."""
    bpy.context.view_layer.update()
    info = []
    for o in bpy.data.objects:
        if o.get('set') != key or o.type != 'MESH' or o.hide_render or o.get('plot'):
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        cen = sum(bb, Vector()) / 8
        # o miolo de argamassa so entra no fim (fica escondido atras dos blocos)
        zref = max(v.z for v in bb) if 'nucleo' in o.name else min(v.z for v in bb)
        info.append((o, o.matrix_basis.copy(), zref, cen))
    zlo = min(i[2] for i in info)
    zhi = max(i[2] for i in info)
    for f in range(BUILD):
        prog = (f + 1) / BUILD
        for o, mb, zmin, cen in info:
            t0 = 0.62 * (zmin - zlo) / max(1e-6, zhi - zlo)
            sv = min(1.0, max(0.0, (prog - t0) / 0.38))
            o.hide_render = sv <= 0
            if sv <= 0:
                continue
            k = ease_out_back(sv)
            T = Matrix.Translation(cen + Vector((0, 0, 0.4 * (1 - sv) ** 2))) @ Matrix.Diagonal((k, k, k, 1)) @ Matrix.Translation(-cen)
            o.matrix_basis = T @ mb
        render_to(os.path.join(d, f'build_{f:02d}.png'))
    for o, mb, *_ in info:
        o.matrix_basis = mb
        o.hide_render = False


def render_glow(key, d):
    """So a luz das lanternas (sem sol nem ceu): somada no jogo a noite, na tempestade e no por do sol."""
    sc = bpy.context.scene
    bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
    old = (bg.inputs['Strength'].default_value, bpy.data.lights['Sol'].energy, bpy.data.lights['Preenchimento'].energy)
    bg.inputs['Strength'].default_value = 0.0
    bpy.data.lights['Sol'].energy = 0.0
    bpy.data.lights['Preenchimento'].energy = 0.0
    bpy.data.objects['ChaoSombra'].hide_render = True
    gm = bpy.data.materials['lanterna']
    gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    old_e = gb.inputs['Emission Strength'].default_value
    gb.inputs['Emission Strength'].default_value = 16.0
    temp = []
    for i, pos in enumerate(BUILT[key]['lanterns']):
        ld = bpy.data.lights.new(f'luzLanterna{i}', 'POINT')
        ld.energy = 18.0
        ld.shadow_soft_size = 0.05
        ld.color = lin('#ffb25a')[:3]
        lo = bpy.data.objects.new(f'luzLanterna{i}', ld)
        sc.collection.objects.link(lo)
        lo.location = Vector(pos)
        temp.append(lo)
    render_to(os.path.join(d, 'glow.png'))
    for lo in temp:
        ld = lo.data
        bpy.data.objects.remove(lo, do_unlink=True)
        bpy.data.lights.remove(ld)
    gb.inputs['Emission Strength'].default_value = old_e
    bg.inputs['Strength'].default_value = old[0]
    bpy.data.lights['Sol'].energy = old[1]
    bpy.data.lights['Preenchimento'].energy = old[2]
    bpy.data.objects['ChaoSombra'].hide_render = False


def render_all(out, only=None):
    global PX_PER_BU
    os.makedirs(out, exist_ok=True)
    sc = bpy.context.scene
    cam = sc.camera
    P = palette()
    meta = {'px_per_game': PX_PER_GAME, 'game_per_bu': GAME_PER_BU, 'sets': {}}
    for k in ('n1', 'n2', 'n3', 'n4', 'lote', 'bal', 'flecha', 'virote', 'cravada') + ARCHER_VARIANTS:
        SETS[k].location = (0, 0, 0)
    want = lambda k: (only is None) or (k in only)

    def objs_of(keys):
        return [o for o in bpy.data.objects if o.get('set') in keys and o.type == 'MESH']

    # ---- torres e lote: loop do tecido + camada da frente
    for key in ('lote', 'n1', 'n2', 'n3', 'n4'):
        if not want(key):
            continue
        set_visible({key})
        apply_cloth(0.0)
        lo, hi = bounds_of(objs_of({key}))
        wpx, hpx, tl = frame_camera(cam, lo, hi, margin=(0.15, 0.95, 0.2, 0.3))
        anchor = project((0, 0, 0), tl)
        slots = [project(s, tl) for s in BUILT[key]['slots']]
        lants = [project(s, tl) for s in BUILT[key]['lanterns']]
        d = os.path.join(out, key)
        os.makedirs(d, exist_ok=True)
        for f in range(LOOP):
            apply_cloth(f / LOOP)
            render_to(os.path.join(d, f'loop_{f:02d}.png'))
        apply_cloth(0.0)
        info = {'w': wpx, 'h': hpx, 'anchor': anchor, 'slots': slots, 'lanterns': lants, 'loop': LOOP}
        if key != 'lote':
            set_visible({key}, front_only=True)
            render_to(os.path.join(d, 'front.png'))
            info['front'] = True
            set_visible({key})
            render_build(key, d)
            info['build'] = BUILD
            render_glow(key, d)
            info['glow'] = True
        meta['sets'][key] = info
    # ---- arqueiros: parado + disparo (virados para a direita; a esquerda e espelhada no jogo)
    for v in ARCHER_VARIANTS:
        if not want(v):
            continue
        root = SETS[v]
        parts = BUILT[v]
        set_visible({v})
        boxes = []
        px0 = PX_PER_BU
        PX_PER_BU = px0 * ARCHER_BOOST
        for mode, n in (('idle', IDLE), ('aim', AIM), ('shoot', SHOOT)):
            for f in range(n):
                archer_frame(parts, P, root, mode, f)
                boxes.append(bounds_of(objs_of({v})))
        lo = (min(b[0][0] for b in boxes), min(b[0][1] for b in boxes))
        hi = (max(b[1][0] for b in boxes), max(b[1][1] for b in boxes))
        wpx, hpx, tl = frame_camera(cam, lo, hi, margin=(0.06, 0.06, 0.08, 0.05))
        anchor = project((0, 0, 0), tl)
        d = os.path.join(out, v)
        os.makedirs(d, exist_ok=True)
        for mode, n in (('idle', IDLE), ('aim', AIM), ('shoot', SHOOT)):
            for f in range(n):
                archer_frame(parts, P, root, mode, f)
                render_to(os.path.join(d, f'{mode}_{f:02d}.png'))
        PX_PER_BU = px0
        meta['sets'][v] = {'w': wpx, 'h': hpx, 'anchor': anchor, 'idle': IDLE, 'aim': AIM, 'shoot': SHOOT, 'boost': ARCHER_BOOST}
    # ---- balestra: 16 direcoes x 8 quadros
    if want('bal'):
        root = SETS['bal']
        parts = BUILT['bal']
        set_visible({'bal'})
        boxes = []
        px0 = PX_PER_BU
        PX_PER_BU = px0 * BAL_BOOST
        for i in range(BAL_DIRS):
            for f in (0, 7):
                pose_ballista(parts, P, root, yaw=TAU * i / BAL_DIRS, **BAL_SEQ[f])
                boxes.append(bounds_of(objs_of({'bal'})))
        lo = (min(b[0][0] for b in boxes), min(b[0][1] for b in boxes))
        hi = (max(b[1][0] for b in boxes), max(b[1][1] for b in boxes))
        wpx, hpx, tl = frame_camera(cam, lo, hi, margin=(0.08, 0.2, 0.1, 0.06))
        anchor = project((0, 0, 0), tl)
        d = os.path.join(out, 'bal')
        os.makedirs(d, exist_ok=True)
        for i in range(BAL_DIRS):
            for f in range(BAL_FRAMES):
                pose_ballista(parts, P, root, yaw=TAU * i / BAL_DIRS, op_ph=f / BAL_FRAMES, **BAL_SEQ[f])
                render_to(os.path.join(d, f'd{i:02d}_{f:02d}.png'))
        PX_PER_BU = px0
        meta['sets']['bal'] = {'w': wpx, 'h': hpx, 'anchor': anchor, 'dirs': BAL_DIRS, 'frames': BAL_FRAMES, 'boost': BAL_BOOST}
    # ---- projeteis: 1 quadro cada, em 2x (o jogo gira e reduz)
    for key in ('flecha', 'virote', 'cravada'):
        if not want(key):
            continue
        set_visible({key})
        bpy.data.objects['ChaoSombra'].hide_render = key != 'cravada'
        px0 = PX_PER_BU
        PX_PER_BU = px0 * PROJ_PX
        lo, hi = bounds_of(objs_of({key}))
        wpx, hpx, tl = frame_camera(cam, lo, hi, margin=(0.04, 0.12 if key == 'cravada' else 0.04, 0.05, 0.04))
        anchor = project((0, 0, 0), tl)
        d = os.path.join(out, key)
        os.makedirs(d, exist_ok=True)
        render_to(os.path.join(d, 'still.png'))
        PX_PER_BU = px0
        bpy.data.objects['ChaoSombra'].hide_render = False
        meta['sets'][key] = {'w': wpx, 'h': hpx, 'anchor': anchor, 'still': 1, 'pxk': PROJ_PX}
    old = {}
    mp = os.path.join(out, 'meta.json')
    if os.path.exists(mp):
        with open(mp) as fh:
            old = json.load(fh)
    old.setdefault('sets', {}).update(meta['sets'])
    old.update({k: v for k, v in meta.items() if k != 'sets'})
    with open(mp, 'w') as fh:
        json.dump(old, fh, indent=1)
    return old


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'render':
        build(showcase=False)
        out = args[1]
        only = set(args[2:]) or None
        render_all(out, only)
        print('RENDER_OK', out)
