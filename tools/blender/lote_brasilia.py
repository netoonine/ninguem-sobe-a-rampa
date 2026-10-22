"""Pecas de Brasilia para as torres do Ninguem Sobe a Rampa: o lote de concreto branco (troca o deck da mata do
lib.plot, com o mesmo tamanho e o topo em z = 0.15), listras de advertencia, capacete de obra e luminaria de obra.

Uso nos scripts das torres (sobrescreve so localmente, o lib.py continua o da mata):
    from lote_brasilia import plot, hazard_mat, hard_hat, work_lamp
"""
import math, random
from mathutils import Vector
from lib import TAU, mat, lin, cyl, box, tube, torus, sphere, lathe, empty, bm_to_obj, _M
import bpy, bmesh

G = 0.07   # chao do lote no codigo das torres (topo 0.15 menos o LIFT de 0.08 que o build_family soma)


def concrete():
    return mat('concreto_brasilia', '#ecebe5', rough=0.86, var=0.04, bump=0.16)


def plot(root, P, tag):
    """Lote de Brasilia: laje redonda de concreto branco com a borda curva (o "pe" de concreto descendo em curva
    ate a terra vermelha do cerrado), juntas de dilatacao e tufos de capim seco atras. Topo em z = 0.15."""
    made = []

    def mk(o):
        o['plot'] = 1
        made.append(o)
        return o
    earth = mat('terra_cerrado_lote', '#b0603e', rough=0.95, var=0.06, bump=0.35)
    conc = concrete()
    conc_d = mat('concreto_junta', '#cfcbc1', rough=0.9, var=0.02, bump=0.05)
    grass = mat('capim_cerrado', '#a8a446', rough=0.9, var=0.18, bump=0.1)
    grass2 = mat('capim_cerrado_verde', '#7d9a3e', rough=0.9, var=0.15, bump=0.1)
    rr = random.Random(11)
    mk(cyl(root, tag + '_terra', 0.98, 0.05, (0, 0, 0.025), r2=0.9, m=earth, v=48, bev=0.02))
    # pe de concreto em curva (saia) e a laje com a quina bem arredondada
    mk(lathe(root, tag + '_saia', [(0.0, 0.93, 0.93), (0.02, 0.9, 0.9), (0.05, 0.85, 0.85), (0.08, 0.815, 0.815), (0.1, 0.8, 0.8)],
             conc, segs=56, lv=1, caps=False, solid=0.02))
    mk(cyl(root, tag + '_laje', 0.8, 0.1, (0, 0, 0.1), m=conc, v=56, bev=0.035))
    # juntas de dilatacao (sulcos finos) e um anel rebaixado
    R = 0.76
    for k, u in enumerate((-0.27, 0.27)):
        half = math.sqrt(R * R - u * u)
        mk(box(root, f'{tag}_juntaX{k}', (0.008, 2 * half, 0.004), (u, 0, 0.1505), m=conc_d, bev=0.0))
        mk(box(root, f'{tag}_juntaY{k}', (2 * half, 0.008, 0.004), (0, u, 0.1505), m=conc_d, bev=0.0))
    mk(torus(root, tag + '_anel', (0, 0, 0.151), 0.7, 0.005, conc_d, n=56, segs=4))
    # faixa pintada da chapa na borda da laje (verde com filete amarelo / vermelho com filete branco)
    from chapa import cor
    mk(cyl(root, tag + '_faixaChapa', 0.803, 0.034, (0, 0, 0.098), m=cor('pri'), v=56, bev=0.004, caps=False))
    mk(cyl(root, tag + '_fileteChapa', 0.804, 0.009, (0, 0, 0.124), m=cor('sec'), v=56, bev=0.002, caps=False))
    # capim seco do cerrado no pe do lote (nunca na frente, para nao cobrir a torre)
    for k, ang in enumerate((150, 205, 30, 330, 100, 75)):
        a = math.radians(ang + rr.uniform(-10, 10))
        cx, cy = 0.95 * math.cos(a), 0.95 * math.sin(a)
        for j in range(6):
            b = rr.uniform(0, TAU)
            tip = (cx + 0.08 * math.cos(b), cy + 0.08 * math.sin(b), 0.12 + rr.uniform(0, 0.1))
            mk(tube(root, f'{tag}_capim{k}_{j}', [(cx + 0.015 * math.cos(b), cy + 0.015 * math.sin(b), 0.0), tip], 0.014,
                    grass if (j + k) % 3 else grass2, segs=5, rfun=lambda t: 0.016 * (1 - t) + 0.002))
    return made


def hazard_mat(key='listra_advertencia', a='#f2b52e', b='#2c2a2c', freq=16.0):
    """Listras diagonais de advertencia (amarelo e preto) em qualquer face: fract((x + y + z) * freq)."""
    if key in _M:
        return _M[key]
    m = mat(key, a, rough=0.55, var=0.02, bump=0.04)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    add1 = N.new('ShaderNodeMath'); add1.operation = 'ADD'
    add2 = N.new('ShaderNodeMath'); add2.operation = 'ADD'
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = freq
    fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].color = lin(a)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = lin(b)
    L.new(tc.outputs['Object'], sep.inputs[0])
    L.new(sep.outputs['X'], add1.inputs[0])
    L.new(sep.outputs['Y'], add1.inputs[1])
    L.new(add1.outputs[0], add2.inputs[0])
    L.new(sep.outputs['Z'], add2.inputs[1])
    L.new(add2.outputs[0], mul.inputs[0])
    L.new(mul.outputs[0], fr.inputs[0])
    L.new(fr.outputs[0], ramp.inputs['Fac'])
    hsv = next(n for n in N if n.type == 'HUE_SAT')
    L.new(ramp.outputs['Color'], hsv.inputs['Color'])
    return m


def hard_hat(root, parts, tag, m, ridge=None, band=None):
    """Capacete de obra: casco arredondado, aba curta na frente e a crista no meio (preso no pivo da cabeca)."""
    head = parts['head']
    hc = Vector((0.006, 0, 0.055))
    dome = lathe(root, f'{tag}_capacete', [(0.026, 0.08, 0.08), (0.05, 0.078, 0.078), (0.08, 0.066, 0.066), (0.105, 0.042, 0.042), (0.118, 0.0, 0.0)],
                 m, segs=18, lv=2, caps=False, solid=0.01)
    dome.parent = head
    dome.location = hc
    aba = cyl(root, f'{tag}_capaceteAba', 0.086, 0.012, (0, 0, 0), m=m, v=24, bev=0.004)
    aba.parent = head
    aba.location = hc + Vector((0.016, 0, 0.03))
    aba.scale = (1.18, 1.0, 1.0)
    cr = tube(root, f'{tag}_capaceteCrista', [hc + Vector((-0.07, 0, 0.09)), hc + Vector((0.0, 0, 0.122)), hc + Vector((0.07, 0, 0.09))],
              0.011, ridge or m, segs=6)
    cr.parent = head
    if band:
        fx = torus(root, f'{tag}_capaceteFaixa', (0, 0, 0), 0.079, 0.009, band, n=20, segs=5)
        fx.parent = head
        fx.location = hc + Vector((0, 0, 0.04))
    return dome


def work_lamp(root, P, name, loc, face=-math.pi / 2, housing=None, tilt=0.35):
    """Refletor de obra: caixinha com a face acesa (material 'lanterna', entra no passe de luz)."""
    x, y, z = loc
    hs = housing or P['iron_d']
    d = Vector((math.cos(face), math.sin(face), 0))
    b = box(root, name + '_caixa', (0.07, 0.09, 0.07), (x, y, z), rot=(0, tilt, face), m=hs, bev=0.012)
    gl = box(root, name + '_vidro', (0.012, 0.075, 0.055), (x + d.x * 0.038, y + d.y * 0.038, z - 0.01), rot=(0, tilt, face), m=P['glow'], bev=0.004)
    return b, gl


# ---------------------------------------------------------------- utilidades de modelagem
class grupo:
    """Bloco com coordenadas locais: tudo o que nasce filho da raiz dentro do `with` vira filho de um empty
    (posicao e giro do grupo). Ex.: with grupo(root, 'x', loc, rot): box(...)"""
    def __init__(self, root, name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
        self.root = root
        self.e = empty(root, name, loc=loc, parent=parent, rot=rot)

    def __enter__(self):
        self.before = set(o.name for o in bpy.data.objects)
        return self.e

    def __exit__(self, *a):
        for o in list(bpy.data.objects):
            if o.name not in self.before and o.parent == self.root and o != self.e:
                o.parent = self.e


def hide_tree(o, hid):
    o.hide_render = hid
    for c in o.children_recursive:
        c.hide_render = hid


def prism_xz(root, name, pts, depth, m, bev=0.01, front=False):
    """Placa grossa: poligono no plano XZ extrudado em Y (centrada em y = 0)."""
    bm = bmesh.new()
    a = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]
    b = [bm.verts.new((x, depth / 2, z)) for x, z in pts]
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm_to_obj(bm, name, root, [m], bev=bev, angle=30, front=front)
