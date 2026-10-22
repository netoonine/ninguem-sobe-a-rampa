"""Fundo da tela de inicio (Guardioes da Mata): margem do rio ao entardecer, mata densa e a Fumaca Negra no horizonte.

Camera baixa em perspectiva (nao a ortografica de 35 graus das fases): 40 mm, 2,2 m de altura, 1,5 grau para baixo.
Os pes dos herois (x 190, 330, 950, 1090; y 650 na tela de 1280x720) ficam numa clareira plana a ~9,5 m, vistos a ~13 graus.
Unidades em metros. Tres camadas para a paralaxe (o jogo anima vaga-lumes, fumaca e folhas por cima):
  titulo_fundo.png   ceu, horizonte, fumaca, rio e a clareira
  titulo_frente.png  moldura de folhas em primeiro plano, com alfa
  titulo_luz.png     so as brasas e as luzes (passe de brilho, fundo preto)

  Blender -b -P tools/blender/titulo.py -- titulo arte/render/titulo [amostras] [k]     (k=3 -> 3840x2160)
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix, Euler, noise
from lib import (TAU, ST, GLOW_MATS, lin, mat, glow_mat, sphere, tube, tube_into, cyl, box, bm_to_obj, mtx, make_root, coll_for,
                 setup_scene, clear_scene, render_to)
from cenario_props import Lote, rock, frond
from mata_props import mats as mata_mats, fern, bromeliad, heliconia, big_leaves, grass_tuft, flowers, jungle_tree, log, mossy_rock, palafita, canoe, vitoria_regia
from mata_vila import vmats, samauma

# ---------------------------------------------------------------- camera e tela (coordenadas da tela de 1280x720)
W, H = 1280, 720
CAM_H = 2.2
PITCH = math.radians(1.5)
LENS, SENSOR = 40.0, 36.0
FPX = LENS / SENSOR * W
CAM_ROT = Euler((math.pi / 2 - PITCH, 0, 0)).to_matrix()
CAM_O = Vector((0, 0, CAM_H))
FEET = [(190, 650), (330, 650), (950, 650), (1090, 650)]
WATER_Z = -0.45
SUN_DIR = Vector((-0.787, -0.552, 0.276)).normalized()   # da cena para o sol: esquerda, atras da camera, 16 graus de altura


def ray(sx, sy):
    return (CAM_ROT @ Vector(((sx - W / 2) / FPX, -(sy - H / 2) / FPX, -1.0))).normalized()


def ground_at(sx, sy, z=0.0):
    d = ray(sx, sy)
    return CAM_O + d * ((z - CAM_O.z) / d.z)


def to_screen(p):
    q = CAM_ROT.transposed() @ (Vector(p) - CAM_O)
    return (W / 2 + FPX * q.x / -q.z, H / 2 - FPX * q.y / -q.z)


def at_depth(sx, sy, y):
    """Ponto do mundo na profundidade y (distancia a frente) que cai no pixel (sx, sy)."""
    d = ray(sx, sy)
    return CAM_O + d * (y / d.y)


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def hexc(h):
    return np.array(lin(h)[:3], np.float32)


# ---------------------------------------------------------------- terreno: clareira, margens, leito do rio
def shore(X, Y):
    """> 0 dentro d'agua (distancia aproximada ate a margem, em m)."""
    yb = 15.2 + 0.03 * X ** 2 + 0.35 * np.sin(X * 0.9)
    xl = -(4.2 + 0.30 * (Y - 15)) + 1.4 * np.sin(Y * 0.045)
    xr = 4.2 + 0.5 * (Y - 15) + 1.2 * np.sin(Y * 0.07)
    yf = 700 + 25 * np.sin(X / 80) + 9 * np.sin(X / 23)
    return np.minimum.reduce([Y - yb, X - xl, xr - X, yf - Y])


def nz(X, Y, sc, seed=0.0):
    return np.array([noise.noise(Vector((x * sc + seed, y * sc - seed, 0.37))) for x, y in zip(X.ravel(), Y.ravel())], np.float32).reshape(X.shape)


FEET_W = []   # posicoes dos pes no mundo (preenchido em build)


def terrain_eval(X, Y):
    s = shore(X, Y)
    n1, n2, n3 = nz(X, Y, 0.35, 1.3), nz(X, Y, 1.4, 7.1), nz(X, Y, 0.06, 3.3)
    side = sstep(4.2, 9.0, np.abs(X)) * (Y < 30)
    land = 0.03 * n2 + 0.35 * side * (0.6 + 0.4 * n1) + (0.2 + 0.5 * n3) * sstep(18, 40, Y)
    # clareira dos herois: plana e limpa
    flat = np.zeros_like(X)
    for (fx, fy) in FEET_W:
        flat = np.maximum(flat, 1 - sstep(0.7, 1.4, np.hypot(X - fx, (Y - fy) * 0.8)))
    land = land * (1 - flat)
    bed = WATER_Z - 0.35 - 0.9 * sstep(0.5, 6, s)
    t = sstep(-2.4, 0.5, s)
    h = land * (1 - t) + bed * t
    # na margem oposta quem encosta na agua e a copa (o chao raso de longe furava a agua em tracejado)
    h = np.where(Y > 600, np.minimum(h, WATER_Z - 0.6), h)
    # cor
    moss, moss_d, moss_l = hexc('#7e9e4a'), hexc('#5e853e'), hexc('#97b057')
    earth, earth_d = hexc('#b48659'), hexc('#8d6543')
    mud, mud_w, sand, bedc = hexc('#7d6448'), hexc('#4f3f31'), hexc('#bfa077'), hexc('#3a3326')
    a = (0.5 + 0.5 * n1)[..., None]
    col = moss_d * (1 - a) + moss * a
    pm = sstep(0.15, 0.55, n2 * 0.6 + n1 * 0.5)[..., None] * (Y < 16)[..., None]
    col = col * (1 - pm * 0.6) + moss_l * pm * 0.6
    # terra batida: caminho do meio ate a agua e um gasto sob os pes
    px = 0.55 * np.sin((Y - 7) * 0.33) + 0.06 * (Y - 7)
    path = (1 - sstep(0.45, 0.85, np.abs(X - px))) * (Y < 16.5)
    worn = flat * 0.75
    e = np.maximum(path, worn)[..., None]
    ec = earth * (1 - 0.35 * (0.5 + 0.5 * n2))[..., None] + earth_d * (0.35 * (0.5 + 0.5 * n2))[..., None]
    col = col * (1 - e) + ec * e
    edge = ((sstep(0.3, 0.6, np.abs(X - px)) * (1 - sstep(0.6, 0.95, np.abs(X - px)))) * (Y < 16.5))[..., None]
    col = col * (1 - 0.25 * edge) + earth_d * 0.25 * edge
    # beira: areia e lama molhada, depois o leito
    b1 = sstep(-2.6, -1.2, s)[..., None]
    col = col * (1 - b1) + sand * b1
    b2 = sstep(-1.4, -0.2, s)[..., None]
    col = col * (1 - b2) + mud * b2
    b3 = sstep(-0.4, 0.4, s)[..., None]
    col = col * (1 - b3) + mud_w * b3
    b4 = sstep(0.5, 3, s)[..., None]
    col = col * (1 - b4) + bedc * b4
    far = sstep(25, 60, Y)[..., None]
    col = col * (1 - far * 0.5) + moss_d * 0.6 * far * 0.5
    return h.astype(np.float32), col.astype(np.float32), s


def grid_mesh(name, root, X, Y, Z, col, m, bands=6):
    nyy, nxx = X.shape
    cuts = np.linspace(0, nyy - 1, bands + 1).astype(int)
    out = []
    for b in range(bands):
        r0, r1 = cuts[b], cuts[b + 1]
        rows = r1 - r0 + 1
        verts = np.stack([X[r0:r1 + 1].ravel(), Y[r0:r1 + 1].ravel(), Z[r0:r1 + 1].ravel()], 1)
        idx = np.arange(rows * nxx).reshape(rows, nxx)
        q = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1)
        me = bpy.data.meshes.new(f'{name}{b}')
        me.vertices.add(len(verts))
        me.vertices.foreach_set('co', verts.ravel())
        me.loops.add(q.size)
        me.loops.foreach_set('vertex_index', q.ravel().astype(np.int32))
        me.polygons.add(len(q))
        me.polygons.foreach_set('loop_start', (np.arange(len(q)) * 4).astype(np.int32))
        me.update(calc_edges=True)
        if col is not None:
            ca = me.color_attributes.new('cor', 'FLOAT_COLOR', 'POINT')
            c = col[r0:r1 + 1].reshape(-1, 3)
            ca.data.foreach_set('color', np.concatenate([c, np.ones((len(c), 1), np.float32)], 1).ravel())
        me.polygons.foreach_set('use_smooth', np.ones(len(q), bool))
        o = bpy.data.objects.new(f'{name}{b}', me)
        root.users_collection[0].objects.link(o)
        o.parent = root
        o['set'] = root['set']
        me.materials.append(m)
        out.append(o)
    return out


def frustum_grid(y0, y1, nv, nu, spread=0.75, pad=6.0, k=3.2):
    t = np.linspace(0, 1, nv, dtype=np.float32)
    ys = y0 + (y1 - y0) * (np.exp(k * t) - 1) / (np.exp(k) - 1)
    u = np.linspace(-1, 1, nu, dtype=np.float32)
    Y = np.repeat(ys[:, None], nu, 1)
    X = u[None, :] * (spread * Y + pad)
    return X, Y


def ground_material():
    m = bpy.data.materials.new('chao_titulo')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.92
    a = N.new('ShaderNodeAttribute'); a.attribute_name = 'cor'
    tc = N.new('ShaderNodeTexCoord')
    nzt = N.new('ShaderNodeTexNoise'); nzt.inputs['Scale'].default_value = 3.0; nzt.inputs['Detail'].default_value = 6
    L.new(tc.outputs['Object'], nzt.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.9; mr.inputs['To Max'].default_value = 1.08
    L.new(nzt.outputs['Fac'], mr.inputs['Value'])
    hsv = N.new('ShaderNodeHueSaturation')
    L.new(a.outputs['Color'], hsv.inputs['Color'])
    L.new(mr.outputs['Result'], hsv.inputs['Value'])
    L.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; bp.inputs['Distance'].default_value = 0.02
    L.new(nzt.outputs['Fac'], bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def water_material():
    m = bpy.data.materials.new('agua_titulo')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.035
    bsdf.inputs['IOR'].default_value = 1.33
    a = N.new('ShaderNodeAttribute'); a.attribute_name = 'cor'
    L.new(a.outputs['Color'], bsdf.inputs['Base Color'])
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.25, 1.4, 1.0)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    nzt = N.new('ShaderNodeTexNoise'); nzt.inputs['Scale'].default_value = 1.6; nzt.inputs['Detail'].default_value = 2
    L.new(mp.outputs['Vector'], nzt.inputs['Vector'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.07; bp.inputs['Distance'].default_value = 0.05
    L.new(nzt.outputs['Fac'], bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def build_terrain(root):
    X, Y = frustum_grid(6.0, 1150.0, 900, 420, k=4.5)
    Z, col, s = terrain_eval(X, Y)
    grid_mesh('Chao', root, X, Y, Z, col, ground_material(), bands=8)
    # agua: um plano em grade (cor clara rente a margem, escura no fundo)
    Xw, Yw = frustum_grid(10.0, 2600.0, 160, 140, spread=0.9, pad=8.0, k=4.0)
    sw = shore(Xw, Yw)
    deep, shal = hexc('#203c37'), hexc('#5a6a48')
    t = np.maximum(sstep(0.0, 4.0, sw), sstep(150, 300, Yw))[..., None]   # agua rasa so na margem de perto
    cw = shal * (1 - t) + deep * t
    grid_mesh('Rio', root, Xw, Yw, np.full_like(Xw, WATER_Z), cw, water_material(), bands=2)
    return Z


# ---------------------------------------------------------------- bruma (perspectiva aerea) em todos os materiais
def haze_group():
    g = bpy.data.node_groups.get('Bruma')
    if g:
        return g
    g = bpy.data.node_groups.new('Bruma', 'ShaderNodeTree')
    g.interface.new_socket(name='Shader', in_out='INPUT', socket_type='NodeSocketShader')
    sk = g.interface.new_socket(name='Escala', in_out='INPUT', socket_type='NodeSocketFloat')
    sk.default_value = 1100.0
    g.interface.new_socket(name='Shader', in_out='OUTPUT', socket_type='NodeSocketShader')
    N, L = g.nodes, g.links
    gi, go = N.new('NodeGroupInput'), N.new('NodeGroupOutput')
    cd = N.new('ShaderNodeCameraData')
    dv = N.new('ShaderNodeMath'); dv.operation = 'DIVIDE'
    L.new(cd.outputs['View Distance'], dv.inputs[0]); L.new(gi.outputs['Escala'], dv.inputs[1])
    ng = N.new('ShaderNodeMath'); ng.operation = 'MULTIPLY'; ng.inputs[1].default_value = -1.0
    L.new(dv.outputs[0], ng.inputs[0])
    ex = N.new('ShaderNodeMath'); ex.operation = 'EXPONENT'
    L.new(ng.outputs[0], ex.inputs[0])
    om = N.new('ShaderNodeMath'); om.operation = 'SUBTRACT'; om.inputs[0].default_value = 1.0
    L.new(ex.outputs[0], om.inputs[1])
    lp = N.new('ShaderNodeLightPath')
    mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    L.new(lp.outputs['Is Camera Ray'], mx.inputs[0]); L.new(lp.outputs['Is Glossy Ray'], mx.inputs[1])
    fac = N.new('ShaderNodeMath'); fac.operation = 'MULTIPLY'
    L.new(om.outputs[0], fac.inputs[0]); L.new(mx.outputs[0], fac.inputs[1])
    # cor da bruma: quente do lado do sol (esquerda), neutra e mais suja do lado da fumaca
    sx = N.new('ShaderNodeSeparateXYZ')
    L.new(cd.outputs['View Vector'], sx.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.45; mr.inputs['From Max'].default_value = 0.45
    L.new(sx.outputs['X'], mr.inputs['Value'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = lin('#f0c9a0')
    ramp.color_ramp.elements[1].color = lin('#b8b4a8')
    L.new(mr.outputs['Result'], ramp.inputs['Fac'])
    em = N.new('ShaderNodeEmission'); em.name = 'BrumaEmissao'
    L.new(ramp.outputs['Color'], em.inputs['Color'])
    ms = N.new('ShaderNodeMixShader')
    L.new(fac.outputs[0], ms.inputs[0]); L.new(gi.outputs[0], ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], go.inputs[0])
    return g


HAZE_K = {}   # material -> escala da bruma (m); None = sem bruma


def apply_haze():
    g = haze_group()
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        k = HAZE_K.get(m.name, 1600.0)
        if k is None:
            continue
        N, L = m.node_tree.nodes, m.node_tree.links
        out = next((n for n in N if n.type == 'OUTPUT_MATERIAL'), None)
        if out is None or not out.inputs['Surface'].links:
            continue
        src = out.inputs['Surface'].links[0].from_socket
        if src.node.type == 'GROUP':
            continue
        gn = N.new('ShaderNodeGroup'); gn.node_tree = g
        gn.inputs['Escala'].default_value = k
        L.new(src, gn.inputs[0])
        L.new(gn.outputs[0], out.inputs['Surface'])


# ---------------------------------------------------------------- ceu (pintado para a camera e reflexos; luz ambiente fria para o resto)
def _mixc(N, L, fac, a, b, blend='MIX'):
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = blend; mx.clamp_result = True
    fi = next(s for s in mx.inputs if s.identifier == 'Factor_Float')
    ai = next(s for s in mx.inputs if s.identifier == 'A_Color')
    bi = next(s for s in mx.inputs if s.identifier == 'B_Color')
    for sock, v in ((fi, fac), (ai, a), (bi, b)):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = v
        else:
            L.new(v, sock)
    return next(s for s in mx.outputs if s.identifier == 'Result_Color')


def setup_sky():
    w = bpy.context.scene.world
    N, L = w.node_tree.nodes, w.node_tree.links
    N.clear()
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Generated'], sep.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.01; mr.inputs['From Max'].default_value = 0.5
    L.new(sep.outputs['Z'], mr.inputs['Value'])
    ramp = N.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.interpolation = 'B_SPLINE'
    stops = [(0.0, '#ffd99e'), (0.05, '#ffc68c'), (0.12, '#fab595'), (0.22, '#eeb8a6'), (0.34, '#c4c2cb'), (0.48, '#97b6d3'), (1.0, '#6d95c4')]
    cr.elements[0].position, cr.elements[0].color = stops[0][0], lin(stops[0][1])
    cr.elements[1].position, cr.elements[1].color = stops[-1][0], lin(stops[-1][1])
    for p, c in stops[1:-1]:
        e = cr.elements.new(p)
        e.color = lin(c)
    L.new(mr.outputs['Result'], ramp.inputs['Fac'])
    col = ramp.outputs['Color']

    def lobe(direc, lo, hi, pw):
        dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
        L.new(tc.outputs['Generated'], dot.inputs[0])
        dot.inputs[1].default_value = tuple(Vector(direc).normalized())
        m2 = N.new('ShaderNodeMapRange'); m2.inputs['From Min'].default_value = lo; m2.inputs['From Max'].default_value = hi
        L.new(dot.outputs['Value'], m2.inputs['Value'])
        pwn = N.new('ShaderNodeMath'); pwn.operation = 'POWER'; pwn.inputs[1].default_value = pw
        L.new(m2.outputs['Result'], pwn.inputs[0])
        return pwn.outputs[0]
    # brilho do sol baixo a esquerda (fora do quadro)
    a = math.radians(-36)
    glow = lobe((math.sin(a), math.cos(a), 0.05), 0.45, 1.0, 2.0)
    mulg = N.new('ShaderNodeMath'); mulg.operation = 'MULTIPLY'; mulg.inputs[1].default_value = 0.9
    L.new(glow, mulg.inputs[0])
    col = _mixc(N, L, mulg.outputs[0], col, lin('#fff0c4'), 'SCREEN')
    # nuvens pintadas: faixas finas e macias perto do horizonte (o ceu do logo fica limpo)
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.4, 2.4, 18.0)
    L.new(tc.outputs['Generated'], mp.inputs['Vector'])
    cn = N.new('ShaderNodeTexNoise'); cn.inputs['Scale'].default_value = 1.7; cn.inputs['Detail'].default_value = 4; cn.inputs['Roughness'].default_value = 0.55
    L.new(mp.outputs['Vector'], cn.inputs['Vector'])
    cm = N.new('ShaderNodeMapRange'); cm.inputs['From Min'].default_value = 0.5; cm.inputs['From Max'].default_value = 0.7
    L.new(cn.outputs['Fac'], cm.inputs['Value'])
    b1 = N.new('ShaderNodeMapRange'); b1.inputs['From Min'].default_value = 0.012; b1.inputs['From Max'].default_value = 0.05
    L.new(sep.outputs['Z'], b1.inputs['Value'])
    b2 = N.new('ShaderNodeMapRange'); b2.inputs['From Min'].default_value = 0.16; b2.inputs['From Max'].default_value = 0.08
    L.new(sep.outputs['Z'], b2.inputs['Value'])
    bm_ = N.new('ShaderNodeMath'); bm_.operation = 'MULTIPLY'
    L.new(b1.outputs['Result'], bm_.inputs[0]); L.new(b2.outputs['Result'], bm_.inputs[1])
    cf = N.new('ShaderNodeMath'); cf.operation = 'MULTIPLY'
    L.new(cm.outputs['Result'], cf.inputs[0]); L.new(bm_.outputs[0], cf.inputs[1])
    cf2 = N.new('ShaderNodeMath'); cf2.operation = 'MULTIPLY'; cf2.inputs[1].default_value = 0.6
    L.new(cf.outputs[0], cf2.inputs[0])
    col = _mixc(N, L, cf2.outputs[0], col, lin('#ffe6cc'), 'MIX')
    # ceu sujo de fumaca do lado direito
    b = math.radians(19)
    smk = lobe((math.sin(b), math.cos(b), 0.12), 0.8, 1.0, 1.4)
    muls = N.new('ShaderNodeMath'); muls.operation = 'MULTIPLY'; muls.inputs[1].default_value = 0.45
    L.new(smk, muls.inputs[0])
    col = _mixc(N, L, muls.outputs[0], col, lin('#a38a7c'), 'MIX')
    paint = N.new('ShaderNodeBackground'); paint.inputs['Strength'].default_value = 1.0
    L.new(col, paint.inputs['Color'])
    amb = N.new('ShaderNodeBackground'); amb.name = 'Ambiente'
    amb.inputs['Color'].default_value = lin('#b4c2d0')
    amb.inputs['Strength'].default_value = 0.55
    lp = N.new('ShaderNodeLightPath')
    mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    L.new(lp.outputs['Is Camera Ray'], mx.inputs[0]); L.new(lp.outputs['Is Glossy Ray'], mx.inputs[1])
    ms = N.new('ShaderNodeMixShader'); ms.name = 'CeuMix'
    L.new(mx.outputs[0], ms.inputs[0]); L.new(amb.outputs[0], ms.inputs[1]); L.new(paint.outputs[0], ms.inputs[2])
    wo = N.new('ShaderNodeOutputWorld'); wo.name = 'SaidaMundo'
    L.new(ms.outputs[0], wo.inputs['Surface'])


def setup_sun():
    sun = bpy.data.objects['Sol']
    sun.data.energy = 3.4
    sun.data.color = lin('#ffc690')[:3]
    sun.data.angle = math.radians(5)
    sun.rotation_euler = SUN_DIR.to_track_quat('Z', 'Y').to_euler()
    bpy.data.lights['Preenchimento'].energy = 0.0


def soft_mat(name, hexcol, edge=(0.5, 0.97), sheen=0.7, emit=0.0, emit_col=None):
    """Bola de fumaca: borda que some (Layer Weight) para a silhueta ficar macia, sem cara de pedra."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
    bsdf.inputs['Base Color'].default_value = lin(hexcol)
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Sheen Weight'].default_value = sheen
    if emit:
        bsdf.inputs['Emission Color'].default_value = lin(emit_col or hexcol)
        bsdf.inputs['Emission Strength'].default_value = emit
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = edge[0]; mr.inputs['From Max'].default_value = edge[1]
    L.new(lw.outputs['Facing'], mr.inputs['Value'])
    tr = N.new('ShaderNodeBsdfTransparent')
    ms = N.new('ShaderNodeMixShader')
    L.new(mr.outputs['Result'], ms.inputs[0]); L.new(bsdf.outputs[0], ms.inputs[1]); L.new(tr.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs['Surface'])
    return m


def far_canopy(root, rr, burn=(205, 330)):
    """Mata da margem oposta como uma copa continua: cupulas de copa somadas num campo de altura (couve-flor),
    com o pe escuro rente a agua e emergentes acima da linha. O trecho em chamas fica baixo e queimado."""
    dx, dv = 1.0, 1.0
    xs = np.arange(-430, 780, dx, dtype=np.float32)
    vs = np.arange(0, 120, dv, dtype=np.float32)
    nx_, nv_ = len(xs), len(vs)
    Hm = np.zeros((nv_, nx_), np.float32)
    Ci = np.zeros((nv_, nx_), np.int32)
    greens = [hexc(c) for c in ('#4c8a4e', '#3d7446', '#5f9656', '#467f3e', '#6c9c4c', '#38683f')]
    char = hexc('#2b2422')
    for k in range(14000):
        xc = -430 + rr.random() * 1210
        vc = (rr.random() ** 1.3) * 118
        isburn = burn[0] < xc < burn[1]
        if isburn:
            hc, rc = rr.uniform(3, 10), rr.uniform(2.5, 4.5)
        elif rr.random() < 0.02 and vc > 12:
            hc, rc = rr.uniform(30, 37), rr.uniform(6, 8.5)
        else:
            hc = rr.uniform(5, 13) + min(1.0, vc / 25) * rr.uniform(5, 12)
            rc = rr.uniform(2.6, 5.0)
        R2 = 2.2 * rc
        i0, i1 = max(0, int((vc - R2) / dv)), min(nv_, int((vc + R2) / dv) + 2)
        j0, j1 = max(0, int((xc - R2 + 430) / dx)), min(nx_, int((xc + R2 + 430) / dx) + 2)
        if i0 >= i1 or j0 >= j1:
            continue
        VV, XX = np.meshgrid(vs[i0:i1], xs[j0:j1], indexing='ij')
        q = ((XX - xc) ** 2 + (VV - vc) ** 2) / rc ** 2
        # cupula que desce em paraboloide e emenda nas vizinhas (sem paredes verticais entre copas)
        sq_ = np.sqrt(q)
        cap = np.where(q < 1, hc + 0.7 * rc * (np.sqrt(np.clip(1 - q, 0, 1)) - 1), hc - 0.7 * rc - 2.2 * rc * (sq_ - 1))
        sub = Hm[i0:i1, j0:j1]
        upd = cap > sub
        sub[upd] = cap[upd]
        Ci[i0:i1, j0:j1][upd] = -1 if isburn else rr.randrange(len(greens))
    Hm = np.maximum(Hm, 0.0)
    for _ in range(1):
        pd = np.pad(Hm, 1, mode='edge')
        Hm = (pd[:-2, :-2] + pd[:-2, 1:-1] + pd[:-2, 2:] + pd[1:-1, :-2] + pd[1:-1, 1:-1] * 4 + pd[1:-1, 2:] + pd[2:, :-2] + pd[2:, 1:-1] + pd[2:, 2:]) / 12.0
    Hm[0, :] = -1.0
    # cor: tom da copa, mais escuro nas dobras (onde a copa fica abaixo da media em volta) e no pe
    k_ = 5
    pad = np.pad(Hm, k_, mode='edge')
    cs = pad.cumsum(0).cumsum(1)
    blur = (cs[2 * k_:, 2 * k_:] - cs[:-2 * k_, 2 * k_:] - cs[2 * k_:, :-2 * k_] + cs[:-2 * k_, :-2 * k_]) / (2 * k_) ** 2
    blur = blur[:nv_, :nx_]
    crev = np.clip((blur - Hm) / 5.0, 0, 1)[..., None]
    base = np.stack([np.where(Ci == -1, 0, 1)] * 3, -1).astype(np.float32)
    G = np.array(greens, np.float32)[np.clip(Ci, 0, None)]
    col = G * base + char * (1 - base)
    low = (1 - np.clip(Hm / 10.0, 0, 1))[..., None]
    col = col * (1 - 0.45 * crev) * (1 - 0.35 * low)
    XX, VV = np.meshgrid(xs, vs)
    YY = 700 + 25 * np.sin(XX / 80) + 9 * np.sin(XX / 23) - 2.0 + VV
    m = bpy.data.materials.new('copa_horiz')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Sheen Weight'].default_value = 0.3
    a = N.new('ShaderNodeAttribute'); a.attribute_name = 'cor'
    L.new(a.outputs['Color'], bsdf.inputs['Base Color'])
    tc = N.new('ShaderNodeTexCoord')
    nzt = N.new('ShaderNodeTexNoise'); nzt.inputs['Scale'].default_value = 0.35; nzt.inputs['Detail'].default_value = 5
    L.new(tc.outputs['Object'], nzt.inputs['Vector'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6; bp.inputs['Distance'].default_value = 1.2
    L.new(nzt.outputs['Fac'], bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    HAZE_K['copa_horiz'] = 1400.0
    return grid_mesh('CopaHoriz', root, XX.astype(np.float32), YY.astype(np.float32), Hm, col.astype(np.float32), m, bands=4)


def smoke_volume(root):
    """Fumaca Negra volumetrica: densidade = mascara da pluma (sobe e deita para a direita) x ruido; pe em brasa."""
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    x0, x1, y0, y1, z0, z1 = 170.0, 640.0, 700.0, 930.0, 0.0, 340.0
    bmesh.ops.transform(bm, matrix=mtx(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (0, 0, 0), (x1 - x0, y1 - y0, z1 - z0)), verts=res['verts'])
    m = bpy.data.materials.new('fumaca_vol')
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    for n in list(N):
        if n.type == 'BSDF_PRINCIPLED':
            N.remove(n)
    out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
    tc = N.new('ShaderNodeTexCoord')
    sp = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Object'], sp.inputs[0])

    def op(o, a, b=None):
        n = N.new('ShaderNodeMath'); n.operation = o
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    X, Y, Z = sp.outputs['X'], sp.outputs['Y'], sp.outputs['Z']
    zr = op('SUBTRACT', Z, 10.0)
    xc = op('ADD', op('MULTIPLY', zr, 0.12), op('MULTIPLY', op('MULTIPLY', zr, zr), 0.0013))
    xc = op('ADD', xc, 250.0)
    yc = op('ADD', op('MULTIPLY', Z, 0.2), 800.0)
    rad = op('ADD', op('MULTIPLY', op('MAXIMUM', zr, 0.0), 0.36), 16.0)
    ddx = op('SUBTRACT', X, xc)
    ddy = op('MULTIPLY', op('SUBTRACT', Y, yc), 0.8)
    d = op('DIVIDE', op('SQRT', op('ADD', op('MULTIPLY', ddx, ddx), op('MULTIPLY', ddy, ddy))), rad)
    # ruido que sobe com a pluma (deslocado em z), em duas escalas
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 0.8)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.022; n1.inputs['Detail'].default_value = 6; n1.inputs['Roughness'].default_value = 0.62
    L.new(mp.outputs['Vector'], n1.inputs['Vector'])
    warp = op('MULTIPLY', op('SUBTRACT', n1.outputs['Fac'] if False else n1.outputs[0], 0.5), 0.9)
    dw = op('ADD', d, warp)
    mask = N.new('ShaderNodeMapRange'); mask.interpolation_type = 'SMOOTHSTEP'
    mask.inputs['From Min'].default_value = 0.45; mask.inputs['From Max'].default_value = 1.0
    mask.inputs['To Min'].default_value = 1.0; mask.inputs['To Max'].default_value = 0.0
    L.new(dw, mask.inputs['Value'])
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 0.08; n2.inputs['Detail'].default_value = 4; n2.inputs['Roughness'].default_value = 0.55
    L.new(mp.outputs['Vector'], n2.inputs['Vector'])
    det = N.new('ShaderNodeMapRange'); det.inputs['From Min'].default_value = 0.3; det.inputs['From Max'].default_value = 0.75
    det.inputs['To Min'].default_value = 0.25; det.inputs['To Max'].default_value = 1.0
    L.new(n2.outputs[0], det.inputs['Value'])
    topfade = N.new('ShaderNodeMapRange'); topfade.inputs['From Min'].default_value = 335.0; topfade.inputs['From Max'].default_value = 260.0
    L.new(Z, topfade.inputs['Value'])
    den = op('MULTIPLY', op('MULTIPLY', mask.outputs['Result'], det.outputs['Result']), topfade.outputs['Result'])
    dens = op('MULTIPLY', den, 0.045)
    pv = N.new('ShaderNodeVolumePrincipled')
    pv.inputs['Color'].default_value = lin('#4a3f3a')
    pv.inputs['Anisotropy'].default_value = 0.25
    pv.inputs['Emission Color'].default_value = lin('#ff7a2a')
    L.new(dens, pv.inputs['Density'])
    low = N.new('ShaderNodeMapRange'); low.interpolation_type = 'SMOOTHSTEP'
    low.inputs['From Min'].default_value = 70.0; low.inputs['From Max'].default_value = 8.0
    L.new(Z, low.inputs['Value'])
    em = op('MULTIPLY', op('MULTIPLY', low.outputs['Result'], den), 0.04)
    em.node.name = 'VolGlow'
    em2 = op('MULTIPLY', em, 1.0)
    L.new(em2, pv.inputs['Emission Strength'])
    L.new(pv.outputs[0], out.inputs['Volume'])
    o = bm_to_obj(bm, 'FumacaVol', root, [m], angle=10)
    HAZE_K['fumaca_vol'] = None
    return o


# ---------------------------------------------------------------- pecas em lote (copas, nuvens, fumaca)
_ICO = {}


def ico(sub):
    if sub not in _ICO:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
        bm.verts.index_update()
        V = np.array([v.co[:] for v in bm.verts], np.float32)
        F = np.array([[v.index for v in f.verts] for f in bm.faces], np.int32)
        bm.free()
        _ICO[sub] = (V, F)
    return _ICO[sub]


class Bolas(Lote):
    """Lote que tambem junta bolas (icosferas deformadas) em arrays: o bmesh.ops fica O(n^2) com milhares delas."""

    def __init__(self, name):
        super().__init__(name)
        self.parts = {}

    def add(self, m, loc, r, rr, sq=(1.0, 1.0, 0.8), sub=2, rough=0.14):
        V0, F0 = ico(sub)
        seed = rr.random() * 50
        n = np.array([noise.noise(Vector((x * 1.4 + seed, y * 1.4 + seed * 0.6, z * 1.4))) for x, y, z in V0], np.float32)
        V = V0 * (1 + rough * n)[:, None] * np.array(sq, np.float32) * r
        a = rr.uniform(0, TAU)
        c, s_ = math.cos(a), math.sin(a)
        V = np.stack([c * V[:, 0] - s_ * V[:, 1], s_ * V[:, 0] + c * V[:, 1], V[:, 2]], 1) + np.array(loc, np.float32)
        e = self.parts.setdefault(m.name, [m, [], [], 0])
        e[1].append(V)
        e[2].append(F0 + e[3])
        e[3] += len(V0)

    def done(self, root, smooth=True):
        out = super().done(root, smooth)
        for key, (m, Vs, Fs, cnt) in self.parts.items():
            V, F = np.concatenate(Vs), np.concatenate(Fs)
            me = bpy.data.meshes.new(f'{self.name}_bolas_{key}')
            me.vertices.add(len(V))
            me.vertices.foreach_set('co', V.ravel())
            me.loops.add(F.size)
            me.loops.foreach_set('vertex_index', F.ravel())
            me.polygons.add(len(F))
            me.polygons.foreach_set('loop_start', (np.arange(len(F)) * 3).astype(np.int32))
            me.update(calc_edges=True)
            me.polygons.foreach_set('use_smooth', np.ones(len(F), bool))
            o = bpy.data.objects.new(f'{self.name}_bolas_{key}', me)
            root.users_collection[0].objects.link(o)
            o.parent = root
            o['set'] = root['set']
            me.materials.append(m)
            out.append(o)
        self.parts = {}
        return out


def blob_into(lote, m, loc, r, rr, sq=(1.0, 1.0, 0.8), sub=2, rough=0.14):
    lote.add(m, loc, r, rr, sq, sub, rough)


def canopy_tree(lote, M, loc, Hh, cr, rr, kind='mata', trunk=True, fill=0, segs=6):
    """Arvore de longe: tronco fino e copa de bolas (verde, ou queimada com brasa); fill = bolas de sub-bosque embaixo."""
    x, y, z = loc
    if trunk:
        lote.tube(M['tronco'] if kind != 'queimada' else M['carvao'], [(x, y, z - 0.5), (x + rr.uniform(-1, 1), y, z + Hh * 0.75)], cr * 0.09, segs=segs,
                  rfun=lambda t: cr * (0.1 - 0.05 * t))
    for k in range(fill):
        a = rr.uniform(0, TAU)
        d = cr * rr.uniform(0.0, 0.6)
        r = cr * rr.uniform(0.4, 0.6)
        blob_into(lote, rr.choice(M['copas'][1:]), (x + d * math.cos(a), y + d * math.sin(a) * 0.6, z + Hh * rr.uniform(0.15, 0.6)), r, rr, sq=(1.0, 1.0, 0.8))
    if kind == 'queimada':
        for k in range(rr.randrange(2, 4)):
            blob_into(lote, M['carvao'], (x + rr.uniform(-cr, cr) * 0.6, y + rr.uniform(-cr, cr) * 0.4, z + Hh * rr.uniform(0.6, 0.85)), cr * rr.uniform(0.35, 0.55), rr)
        return
    greens = M['copas']
    n = rr.randrange(4, 8)
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = cr * rr.uniform(0.2, 0.75) if k else 0
        r = cr * rr.uniform(0.45, 0.7)
        blob_into(lote, rr.choice(greens), (x + d * math.cos(a), y + d * math.sin(a) * 0.7, z + Hh - r * 0.3 + rr.uniform(-0.15, 0.2) * cr), r, rr,
                  sq=(1.0, 1.0, rr.uniform(0.7, 0.85)))


def acai(root, tag, Mt, base, Hh, rr, lean=(0.0, 0.0)):
    """Acaizeiro: estipe fino e curvo, coroa de folhas pinadas pendentes e cacho escuro."""
    bx, by, bz = base
    pts = [Vector((bx + lean[0] * Hh * (k / 10) ** 2, by + lean[1] * Hh * (k / 10) ** 2, bz + Hh * k / 10)) for k in range(11)]
    tube(root, tag + '_estipe', pts, 0.16, Mt['bark_l'], segs=8, rfun=lambda t: 0.17 - 0.06 * t)
    top = pts[-1]
    tube(root, tag + '_palmito', [top, top + Vector((0, 0, 1.4))], 0.13, Mt['leaf_d'], segs=8, rfun=lambda t: 0.13 - 0.07 * t)
    for k in range(11):
        a = TAU * k / 11 + rr.uniform(-0.15, 0.15)
        piv = bpy.data.objects.new(f'{tag}_f{k}_piv', None)
        root.users_collection[0].objects.link(piv)
        piv.parent = root
        piv['set'] = root['set']
        piv.location = top + Vector((0, 0, 0.6))
        piv.rotation_euler = (0, 0, a)
        f = frond(root, f'{tag}_f{k}', rr.uniform(3.0, 3.8), 2.3, rr.uniform(0.25, 0.5), Mt['leaf'] if k % 2 else Mt['leaf_l'], rr)
        f.parent = piv
    for k in range(2):
        a = rr.uniform(0, TAU)
        sphere(root, f'{tag}_cacho{k}', 0.35, tuple(top + Vector((0.35 * math.cos(a), 0.35 * math.sin(a), -0.3))), scale=(1, 1, 1.4), m=Mt['acai'], seg=12)


# ---------------------------------------------------------------- folhas grandes do primeiro plano (moldura)
def leaf_into(bm, base, yaw, pitch, roll, L, Wd, droop=0.25, rise=0.15, fold=0.3, n=16, m=4, tip=0.75):
    R = Euler((roll, pitch, yaw)).to_matrix()
    rows = []
    for i in range(n + 1):
        t = i / n
        x = L * t
        z = L * (rise * t * (1 - t) * 4 - droop * t * t)
        w = Wd * 0.5 * (math.sin(math.pi * min(1.0, t)) ** tip) * (1 - 0.1 * t) + 0.004
        row = []
        for j in range(-m, m + 1):
            s = j / m
            p = Vector((x, w * s, z - abs(s) ** 1.6 * w * fold))
            row.append(bm.verts.new(Vector(base) + R @ p))
        rows.append(row)
    for i in range(n):
        for j in range(2 * m):
            bm.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]))
    return [Vector(base) + R @ Vector((L * i / n, 0, L * (rise * (i / n) * (1 - i / n) * 4 - droop * (i / n) ** 2) + 0.004)) for i in range(n + 1)]


def leaf(root, name, mlf, mrib, base, yaw, pitch, roll, L, Wd, **kw):
    bm = bmesh.new()
    rib = leaf_into(bm, base, yaw, pitch, roll, L, Wd, **kw)
    o = bm_to_obj(bm, name, root, [mlf], angle=89)
    sm = o.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.006 + 0.004 * L
    if mrib is not None:
        tube(root, name + '_nervura', rib, 0.01 + 0.006 * L, mrib, segs=6, rfun=lambda t: (0.012 + 0.008 * L) * (1 - 0.8 * t))
    return o


def heliconia_sem_folhas(root, name, Mt, loc, s_, rr):
    """Heliconia do mata_props sem as duas folhas largas (de perto elas cobrem o canto inteiro)."""
    objs = heliconia(root, name, Mt, loc, s_, rr)
    for o in list(bpy.data.objects):
        if o.name.startswith(name + '_folha'):
            bpy.data.objects.remove(o, do_unlink=True)


def build_frente(root, Mt):
    """Moldura: quatro cantos de folhas, longe dos herois (x 140-390 e 890-1140) e do miolo."""
    rr = random.Random(41)
    lf, lfd, lfl = Mt['leaf'], Mt['leaf_d'], Mt['leaf_l']
    # canto superior esquerdo: galho saindo do quadro com folhas penduradas
    br = [at_depth(-80, 20, 3.0), at_depth(90, 8, 3.05), at_depth(230, -30, 3.1)]
    tube(root, 'galhoTE', br, 0.05, Mt['bark'], segs=10, rfun=lambda t: 0.06 - 0.03 * t)
    for k in range(11):
        t = k / 10
        p = br[0].lerp(br[1], t * 2) if t < 0.5 else br[1].lerp(br[2], (t - 0.5) * 2)
        p = p + Vector((0, rr.uniform(-0.05, 0.05), -0.02))
        leaf(root, f'folhaTE{k}', lf if k % 3 else lfd, lfl, p, rr.uniform(-0.7, 0.7) + (math.pi if k % 2 else 0), math.radians(rr.uniform(55, 78)), rr.uniform(-0.3, 0.3),
             rr.uniform(0.24, 0.36) * (1.15 - 0.4 * t), 0.13, droop=0.12, rise=0.05)
    # canto inferior esquerdo: taioba alta (folhas em coracao sobre talos longos)
    tb = at_depth(-160, 790, 3.4); tb.z = 0.0
    for k, (yaw, pitch, hgt) in enumerate([(0.5, -0.75, 1.5), (0.15, -0.45, 1.7), (1.0, -0.3, 1.35)]):
        top = tb + Vector((0.12 * math.cos(yaw), 0.12 * math.sin(yaw), hgt))
        tube(root, f'taiobaE_talo{k}', [tb, tb + Vector((0.05, 0, hgt * 0.6)), top], 0.025, Mt['leaf_d'], segs=6)
        leaf(root, f'taiobaE_f{k}', lf if k % 2 else lfl, Mt['moss'], top, yaw, pitch, 0, 0.55, 0.44, droop=0.3, rise=0.1, fold=0.2, tip=0.5)
    # canto superior direito: cipos finos pendurados com folhinhas
    for k, (sx, ln) in enumerate([(1150, 0.55), (1196, 0.85), (1238, 0.5), (1265, 1.05)]):
        top = at_depth(sx, -30, 3.2)
        pts = [top + Vector((0.03 * math.sin(i * 1.3 + k), 0, -ln * i / 10)) for i in range(11)]
        tube(root, f'cipo{k}', pts, 0.005, Mt['leaf_d'], segs=5)
        for i in range(2, 11, 2):
            leaf(root, f'cipo{k}_f{i}', lf if i % 4 else lfl, None, pts[i], rr.uniform(0, TAU), math.radians(rr.uniform(35, 60)), 0, 0.09, 0.075,
                 droop=0.1, rise=0.05, n=8, m=3, tip=0.6)
    brr = [at_depth(1360, 40, 3.0), at_depth(1210, 6, 3.05), at_depth(1110, -40, 3.1)]
    tube(root, 'galhoTD', brr, 0.045, Mt['bark'], segs=10, rfun=lambda t: 0.055 - 0.025 * t)
    for k in range(7):
        p = brr[0].lerp(brr[1], k / 6) + Vector((0, 0, -0.02))
        leaf(root, f'folhaTD{k}', lfd if k % 2 else lf, lfl, p, rr.uniform(0, TAU), math.radians(rr.uniform(55, 78)), 0, rr.uniform(0.2, 0.3), 0.12, droop=0.12)
    # canto inferior direito: helicônia (só as brácteas) e uma folha larga
    hb = at_depth(1290, 760, 4.0); hb.z = 0.0
    heliconia_sem_folhas(root, 'heliconiaD', Mt, tuple(hb), 1.6, rr)
    hb2 = at_depth(1250, 760, 4.8); hb2.z = 0.0
    heliconia_sem_folhas(root, 'heliconiaD2', Mt, tuple(hb2), 1.35, rr)
    tb2 = at_depth(1440, 790, 3.3); tb2.z = 0.0
    for k, (yaw, pitch, hgt) in enumerate([(math.pi * 0.7, -0.6, 1.55), (math.pi * 0.95, -0.35, 1.4)]):
        top = tb2 + Vector((0.12 * math.cos(yaw), 0.12 * math.sin(yaw), hgt))
        tube(root, f'taiobaD_talo{k}', [tb2, tb2 + Vector((-0.05, 0, hgt * 0.6)), top], 0.025, Mt['leaf_d'], segs=6)
        leaf(root, f'taiobaD_f{k}', lfl if k % 2 else lf, Mt['moss'], top, yaw, pitch, 0, 0.5, 0.4, droop=0.3, rise=0.1, fold=0.2, tip=0.5)


# ---------------------------------------------------------------- cena
def build(out):
    sc = bpy.context.scene
    rr = random.Random(7)
    Mt = mata_mats()
    V = vmats()
    Mt['acai'] = mat('acai_cacho', '#3a2a2a', rough=0.5, var=0.06, bump=0.05)
    FEET_W[:] = [tuple(ground_at(x, y)[:2]) for (x, y) in FEET]
    root = make_root('raiz_titulo', 'fundo', coll_for('Titulo'))
    root['camada'] = 'fundo'
    front = make_root('raiz_frente', 'frente', coll_for('TituloFrente'))
    front['camada'] = 'frente'
    build_terrain(root)

    def gz(x, y):
        Z, _, _ = terrain_eval(np.array([[x]], np.float32), np.array([[y]], np.float32))
        return float(Z[0, 0])

    def free(x, y, r=0.9):
        for (fx, fy) in FEET_W:
            if math.hypot(x - fx, y - fy) < r:
                return False
        return True

    lote = Bolas('miudos')
    # materiais da mata de longe
    FM = {'tronco': mat('tronco_longe', '#6e5442', rough=0.9, var=0.08, bump=0.1),
          'carvao': mat('carvao_longe', '#2a2220', rough=0.95, var=0.08, bump=0.1),
          'copas': [mat('copa_longe_a', '#4f8a3c', rough=0.85, var=0.12, bump=0.05, sheen=0.2),
                    mat('copa_longe_b', '#3d7434', rough=0.85, var=0.12, bump=0.05, sheen=0.2),
                    mat('copa_longe_c', '#6a9c44', rough=0.85, var=0.12, bump=0.05, sheen=0.2)]}
    FMF = dict(FM, copas=[mat('copa_horiz_a', '#4f8a50', rough=0.9, var=0.12, bump=0.05, sheen=0.2),
                          mat('copa_horiz_b', '#3f7448', rough=0.9, var=0.12, bump=0.05, sheen=0.2),
                          mat('copa_horiz_c', '#62935a', rough=0.9, var=0.12, bump=0.05, sheen=0.2)])
    HAZE_K.update({'copa_horiz_a': 760.0, 'copa_horiz_b': 760.0, 'copa_horiz_c': 760.0, 'carvao_longe': 1400.0})
    ember = glow_mat('brasa_titulo', '#ff7a2a', 3.5, 16.0, rough=0.6, var=0.12, bump=0.0)
    fire = glow_mat('fogo_titulo', '#ffae4a', 5.0, 22.0, rough=0.6, var=0.08, bump=0.0)
    HAZE_K.update({'brasa_titulo': 4000.0, 'fogo_titulo': 4000.0})
    GLOW_MATS.update({'brasa_titulo': 5.0, 'fogo_titulo': 6.0})   # no passe de luz: sem estourar o reflexo nem as copas vizinhas
    lights = []

    # ---- margem esquerda: parede de mata
    for k in range(900):
        y = 18 + (rr.random() ** 1.6) * 690
        xl = -(4.2 + 0.30 * (y - 15)) + 1.4 * math.sin(y * 0.045)
        x = xl - 2.0 - rr.random() * (0.25 * y + 12)
        if x / y < -0.62:
            continue
        Hh = rr.uniform(18, 34) * (1.25 if rr.random() < 0.08 else 1.0)
        z = gz(x, y)
        canopy_tree(lote, FM, (x, y, z), Hh, rr.uniform(5, 9), rr, trunk=y < 250, fill=2 if y > 60 else 1, segs=10 if y < 120 else 6)
    # samauma na borda esquerda (so o tronco e as sapopemas entram no quadro)
    sb = at_depth(-70, 400, 30.0)
    samauma(root, 'samauma', V, (sb.x, sb.y, gz(sb.x, sb.y) - 0.2), 34.0, 1.5, crown=13, seeds=0, seed=4, buttress=6, vines=0)
    # ---- margem oposta (horizonte): faixa de mata; a parte da direita esta queimando
    far_canopy(root, rr)
    for k in range(260):
        x = 205 + rr.random() * 125
        yf = 700 + 25 * math.sin(x / 80) + 9 * math.sin(x / 23)
        y = yf + 3 + rr.random() * 40
        canopy_tree(lote, FM, (x, y, 0.3), rr.uniform(8, 18), rr.uniform(4, 6), rr, kind='queimada')
        if rr.random() < 0.45:
            blob_into(lote, fire if rr.random() < 0.4 else ember, (x + rr.uniform(-3, 3), y - 2, rr.uniform(1, 8)), rr.uniform(1.2, 2.6), rr, sq=(1.4, 1, 0.7))
    # fumaca negra: coluna que sobe da mata queimando e deita para a direita com o vento
    smoke_volume(root)
    sl = Bolas('fumaca')
    # brasas subindo num fio dentro da fumaca (o jogo anima outras por cima)
    for k in range(16):
        u = rr.random() ** 2.2
        zc = 8 + u * 90
        xc = 250 + 0.1 * (zc - 10) + rr.gauss(0, 1) * (4 + 0.08 * zc)
        blob_into(sl, fire if rr.random() < 0.35 else ember, (xc, 770 + rr.uniform(-10, 10), zc), rr.uniform(0.7, 1.3), rr, sq=(1, 1, 1), sub=2, rough=0.0)
    sl.done(root)
    for (x, z, wt) in ((232, 20, 5e4), (258, 26, 6e4), (282, 18, 4e4)):   # no meio da queimada: longe das copas verdes
        ld = bpy.data.lights.new(f'brasaFumaca{x}', 'POINT')
        ld.energy = wt
        ld.color = lin('#ff7a30')[:3]
        ld.shadow_soft_size = 8.0
        lo = bpy.data.objects.new(f'brasaFumaca{x}', ld)
        sc.collection.objects.link(lo)
        lo.location = (x, 760, z)
        lo.visible_glossy = False   # a esfera de 8 m aparecia no reflexo do rio como um borrao branco
    # ---- margem direita perto: acaizeiros recortados contra a fumaca, moitas e capim
    for k, (sx, y, Hh, ln) in enumerate([(1180, 62, 15.5, (0.06, 0.02)), (1215, 70, 17.5, (-0.04, 0.03)), (1252, 66, 14.0, (0.09, -0.02)),
                                          (1235, 80, 16.5, (0.0, 0.05)), (1160, 85, 13.0, (-0.08, 0.0))]):
        p = at_depth(sx, 330, y)
        acai(root, f'acai{k}', Mt, (p.x, p.y, gz(p.x, p.y)), Hh, rr, lean=ln)
    for k in range(40):
        y = 18 + rr.random() * 70
        xr = 4.2 + 0.5 * (y - 15) + 1.2 * math.sin(y * 0.07)
        x = xr + 0.5 + rr.random() * 8
        z = gz(x, y)
        if rr.random() < 0.5:
            big_leaves(root, f'moitaD{k}', Mt, (x, y, z), rr.uniform(1.4, 2.4), rr)
        else:
            mossy_rock(root, f'pedraD{k}', Mt, (x, y, z), rr.uniform(0.5, 1.1), rr)
    # ---- palafita com lanterna e canoa na margem esquerda
    pp = at_depth(262, 360, 88.0)
    pp.z = WATER_Z
    palafita(root, 'palafita', Mt, tuple(pp), 4.0, rr, ang=0.25)
    lant = glow_mat('lanterna_titulo', '#ffcf7a', 2.2, 18.0, rough=0.4, var=0.0, bump=0.0)
    win = pp + Vector((-0.25 * 4 * math.cos(0.25) + 0.35, -0.8 * 4 * 0.33 - 0.06, 0.45 * 4 + 0.3 * 4))
    box(root, 'palafita_luz', (0.6, 0.05, 0.45), tuple(win), rot=(0, 0, 0.25), m=lant, bev=0.0)
    lam = pp + Vector((1.2, -1.9, 0.45 * 4 + 1.6))
    sphere(root, 'palafita_lampiao', 0.18, tuple(lam), scale=(1, 1, 1.25), m=lant, seg=14)
    lights.append((tuple(lam), '#ffc060', 300.0))
    cp = pp + Vector((3.6, -3.0, 0))
    canoe(root, 'canoaT', Mt, (cp.x, cp.y, WATER_Z - 0.05), 4.2, 0.35, rr)
    # ponte de tabuas da palafita ate a margem
    for k in range(9):
        q = pp + Vector((-2.2 - 1.0 * k, -0.6 - 0.25 * k, 0))
        box(root, f'ponte{k}', (1.0, 1.1, 0.08), (q.x, q.y, 0.75), rot=(0, 0, 0.25), m=Mt['plank'] if k % 2 else Mt['wood_l'], bev=0.01)
        if k % 3 == 0:
            for sy in (-0.5, 0.5):
                tube(root, f'ponteEstaca{k}{sy}', [(q.x, q.y + sy, WATER_Z - 0.4), (q.x, q.y + sy, 0.8)], 0.06, Mt['bark_d'], segs=6)
    # ---- clareira: capim baixo, flores, pedras com musgo, um tronco caido; nada nos pes dos herois nem no caminho
    for k in range(1500):
        y = 7.0 + rr.random() * 9.5
        x = rr.uniform(-1, 1) * (0.48 * y + 2.5)
        px = 0.55 * math.sin((y - 7) * 0.33) + 0.06 * (y - 7)
        if abs(x - px) < 0.95 or not free(x, y, 1.05):
            continue
        if shore(np.array([x]), np.array([y]))[0] > -1.2:
            continue
        z = gz(x, y)
        grass_tuft(lote, Mt, (x, y, z), rr.uniform(0.08, 0.24), rr, n=rr.randrange(4, 8))
        if rr.random() < 0.08:
            flowers(lote, Mt, (x, y, z), 0.5, rr, n=4)
    for k, (sx, sy, s_) in enumerate([(30, 610, 0.8), (500, 604, 0.36), (1250, 590, 0.7), (455, 560, 0.3), (840, 640, 0.3)]):
        p = ground_at(sx, sy)
        for j in range(rr.randrange(1, 4)):
            q = (p.x + rr.uniform(-0.6, 0.6) * s_, p.y + rr.uniform(-0.4, 0.4) * s_, gz(p.x, p.y))
            rock(root, f'pedraC{k}_{j}', Mt['stone'] if j % 2 else Mt['stone_d'], q, s_ * rr.uniform(0.5, 1.0), rr, squash=0.55)
    for k, (sx, sy, s_) in enumerate([(70, 520, 1.3), (1200, 535, 1.6), (40, 480, 1.4)]):
        p = ground_at(sx, sy)
        if rr.random() < 0.5:
            fern(root, f'samambaiaC{k}', Mt, (p.x, p.y, gz(p.x, p.y)), s_, rr)
        else:
            bromeliad(root, f'bromeliaC{k}', Mt, (p.x, p.y, gz(p.x, p.y)), s_, rr)
    # beira d'agua: aninga, capim flutuante e vitorias-regias
    for k in range(160):
        y = 15 + rr.random() * 30
        x = rr.uniform(-0.5, 0.5) * (0.9 * y)
        sh = shore(np.array([x]), np.array([y]))[0]
        if not (-0.6 < sh < 0.8):
            continue
        sxp, syp = to_screen((x, y, 0))
        if 505 < sxp < 775:
            continue
        for j in range(rr.randrange(4, 9)):
            a = rr.uniform(0, TAU)
            hgt = rr.uniform(0.5, 1.2)
            lote.blade(Mt['leaf_l'] if j % 3 else Mt['leaf'], (x + rr.uniform(-0.1, 0.1), y + rr.uniform(-0.1, 0.1), WATER_Z - 0.1),
                       (x + 0.25 * math.cos(a), y + 0.25 * math.sin(a), WATER_Z + hgt), 0.035)
    for k in range(46):
        sx = rr.choice((rr.uniform(400, 505), rr.uniform(780, 880)))
        p = ground_at(sx, rr.uniform(556, 575), WATER_Z)
        if shore(np.array([p.x]), np.array([p.y]))[0] < -0.6:
            continue
        hgt = rr.uniform(0.5, 1.1)
        a = rr.uniform(0, TAU)
        lote.blade(Mt['leaf_l'] if k % 3 else Mt['leaf'], (p.x, p.y, WATER_Z - 0.1), (p.x + 0.15 * math.cos(a), p.y + 0.15 * math.sin(a), WATER_Z + hgt), 0.03)
    # pedras de pisar no fim do caminho
    for k, (dx, dy) in enumerate([(0.15, 0.4), (-0.25, 1.1), (0.3, 1.8)]):
        pe = ground_at(650, 572, 0.0)
        q = (pe.x + dx, pe.y + dy, WATER_Z - 0.06)
        lote.pebble(Mt['stone'] if k % 2 else Mt['stone_d'], q, 0.32, squash=0.45, rr=rr)
    lote.done(root)
    build_frente(front, Mt)
    return lights


# ---------------------------------------------------------------- camadas e render
def top_root(o):
    while o.parent:
        o = o.parent
    return o.get('camada')


def set_layer(mode):
    """fundo: tudo menos a moldura. frente: so a moldura (o resto ilumina mas nao aparece). luz: fundo sem sol nem ceu."""
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE'):
            continue
        cam = top_root(o)
        if cam is None:
            continue
        is_front = cam == 'frente'
        if mode == 'frente':
            o.hide_render = False
            o.visible_camera = is_front
        else:
            o.hide_render = is_front
            o.visible_camera = True


def make_camera(k):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('CamTitulo')
    cd.type = 'PERSP'
    cd.lens = LENS
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = SENSOR
    cd.clip_start = 0.3
    cd.clip_end = 20000
    cam = bpy.data.objects.new('CamTitulo', cd)
    sc.collection.objects.link(cam)
    cam.location = CAM_O
    cam.rotation_euler = (math.pi / 2 - PITCH, 0, 0)
    sc.camera = cam
    sc.render.resolution_x = int(W * k)
    sc.render.resolution_y = int(H * k)
    return cam


def glow_pass(path, lights):
    sc = bpy.context.scene
    N = sc.world.node_tree.nodes
    ms = N['CeuMix']
    old_sun = bpy.data.lights['Sol'].energy
    bpy.data.lights['Sol'].energy = 0.0
    wo = N['SaidaMundo']
    link = wo.inputs['Surface'].links[0]
    sc.world.node_tree.links.remove(link)
    em = bpy.data.node_groups['Bruma'].nodes['BrumaEmissao']
    old_em = em.inputs['Strength'].default_value
    em.inputs['Strength'].default_value = 0.0
    olds = {}
    for name, val in GLOW_MATS.items():
        gm = bpy.data.materials.get(name)
        if not gm:
            continue
        gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        olds[name] = gb.inputs['Emission Strength'].default_value
        gb.inputs['Emission Strength'].default_value = val
    vg = bpy.data.materials['fumaca_vol'].node_tree.nodes['VolGlow']
    old_vg = vg.inputs[1].default_value   # constante da emissao do pe da fumaca
    vg.inputs[1].default_value = old_vg * 1.5
    smk = [l for l in bpy.data.lights if l.name.startswith('brasaFumaca')]
    old_smk = [l.energy for l in smk]
    for l in smk:
        l.energy *= 0.5
    temp = []
    for i, (pos, col, watts) in enumerate(lights):
        ld = bpy.data.lights.new(f'luzT{i}', 'POINT')
        ld.energy = watts
        ld.shadow_soft_size = 0.1
        ld.color = lin(col)[:3]
        lo = bpy.data.objects.new(f'luzT{i}', ld)
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
    em.inputs['Strength'].default_value = old_em
    vg.inputs[1].default_value = old_vg
    for l, e in zip(smk, old_smk):
        l.energy = e
    sc.world.node_tree.links.new(ms.outputs[0], wo.inputs['Surface'])
    bpy.data.lights['Sol'].energy = old_sun


def render_titulo(out, samples=128, k=3.0, only=None):
    os.makedirs(out, exist_ok=True)
    clear_scene()
    sc = bpy.context.scene
    ST['coll'] = sc.collection
    setup_scene()
    try:
        bpy.context.preferences.addons['cycles'].preferences.metalrt = 'OFF'
    except Exception:
        pass
    bpy.data.objects['ChaoSombra'].hide_render = True
    sc.cycles.samples = samples
    sc.cycles.transparent_max_bounces = 48
    sc.view_settings.exposure = 0.0
    setup_sky()
    setup_sun()
    lights = build(out)
    apply_haze()
    make_camera(k)
    layers = only or ['fundo', 'frente', 'luz']
    if 'fundo' in layers:
        set_layer('fundo')
        sc.render.film_transparent = False
        sc.render.image_settings.color_mode = 'RGB'
        render_to(os.path.join(out, 'titulo_fundo.png'))
    if 'frente' in layers:
        set_layer('frente')
        sc.render.film_transparent = True
        sc.render.image_settings.color_mode = 'RGBA'
        render_to(os.path.join(out, 'titulo_frente.png'))
    if 'luz' in layers:
        set_layer('fundo')
        sc.render.film_transparent = False
        sc.render.image_settings.color_mode = 'RGB'
        glow_pass(os.path.join(out, 'titulo_luz.png'), lights)
    meta = {'lens_mm': LENS, 'sensor_mm': SENSOR, 'cam_h_m': CAM_H, 'pitch_deg': math.degrees(PITCH),
            'feet_world': FEET_W, 'sun_dir': list(SUN_DIR),
            'feet_view_deg': [math.degrees(math.atan2(CAM_H, math.hypot(*fw))) for fw in FEET_W],
            'px_per_m_at_feet': [FPX / (CAM_ROT.transposed() @ (Vector((fw[0], fw[1], 0)) - CAM_O)).z * -1 for fw in FEET_W]}
    with open(os.path.join(out, 'titulo.json'), 'w') as fh:
        json.dump(meta, fh, indent=1)
    print('TITULO_OK', json.dumps(meta))


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'titulo':
        only = args[4].split(',') if len(args) > 4 else None
        render_titulo(args[1], int(args[2]) if len(args) > 2 else 128, float(args[3]) if len(args) > 3 else 3.0, only)
