"""Pecas comuns a todas as torres de sprite, no canteiro de obras de Brasilia: o chao do lote (a mesma laje redonda de
concreto branco das torres, lote_brasilia.plot), o lote vazio com a estaca da bandeirola de obra, o andaime metalico com
tela laranja, a tabua, a pilha de blocos de concreto e tijolos, o pedreiro martelando (capacete amarelo e colete laranja),
o marco do lote vazio e os escombros da obra parada.

  Blender -b -P tools/blender/comum.py -- render arte/render/comum
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, hard_hat   # noqa: F811 - o lote de concreto branco das torres (lib.py continua o da mata)

FAM = 'comum'
G0 = 0.07           # chao do lote no codigo (topo 0.15 menos o LIFT de 0.08 que o build_family soma)

import lib as _lib
_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811 - canteiro de Brasilia: aco galvanizado, laranja de obra, concreto e tijolo
    P = _orig_palette2()
    P['scaf'] = mat('andaime_aco', '#b7bec4', rough=0.32, metal=0.6, var=0.03, bump=0.04)
    P['scaf_d'] = mat('andaime_abracadeira', '#6f767c', rough=0.4, metal=0.55, var=0.03, bump=0.04)
    P['obra'] = mat('laranja_obra', '#f07a22', rough=0.55, var=0.03, bump=0.05)
    P['obra_d'] = mat('laranja_obra_esc', '#c85a14', rough=0.6, var=0.03, bump=0.05)
    P['fita'] = mat('fita_zebrada', '#f07a22', rough=0.6, var=0.0, bump=0.03, stripes=(10.0, '#f07a22', '#f6f1e6'), sheen=0.3)
    P['pinus'] = mat('tabua_pinus', '#d9b07a', rough=0.75, var=0.1, bump=0.25)
    P['pinus_d'] = mat('tabua_pinus_esc', '#b88a52', rough=0.78, var=0.1, bump=0.25)
    P['block'] = mat('bloco_concreto', '#a19d96', rough=0.92, var=0.06, bump=0.35)
    P['block_d'] = mat('bloco_furo', '#4a4744', rough=0.95, var=0.0, bump=0.0)
    P['brick'] = mat('tijolo', '#c4573a', rough=0.85, var=0.08, bump=0.25)
    P['cement'] = mat('saco_cimento', '#d9d2c3', rough=0.92, var=0.04, bump=0.2)
    P['cement_s'] = mat('saco_cimento_faixa', '#3f6fb0', rough=0.85, var=0.0, bump=0.05)
    P['conc'] = mat('concreto_obra', '#e6e3db', rough=0.88, var=0.06, bump=0.3)
    P['conc_d'] = mat('concreto_quebrado', '#c9c3b6', rough=0.9, var=0.08, bump=0.35)
    P['rust'] = mat('vergalhao', '#9a4e2c', rough=0.75, var=0.06, bump=0.2)
    P['dust'] = mat('entulho_po', '#cdbba4', rough=0.95, var=0.04, bump=0.35)
    P['grass_d'] = mat('capim_cerrado_obra', '#a8a446', rough=0.9, var=0.18, bump=0.1)
    P['hat'] = mat('capacete_amarelo', '#ffc531', rough=0.35, var=0.02, bump=0.03)
    P['vest_o'] = mat('colete_laranja', '#f26b1d', rough=0.75, var=0.02, bump=0.06, sheen=0.3)
    P['refl'] = mat('faixa_refletiva', '#e3e8ea', rough=0.3, metal=0.2, var=0.0, bump=0.02)
    P['shirt'] = mat('camisa_brim', '#5a7fb6', rough=0.85, var=0.03, bump=0.08, sheen=0.3)
    P['jeans'] = mat('calca_jeans', '#34507e', rough=0.85, var=0.03, bump=0.08)
    P['boot'] = mat('botina', '#3b2a1f', rough=0.6, var=0.03, bump=0.1)
    P['glove'] = mat('luva_obra', '#d9c27a', rough=0.85, var=0.03, bump=0.15)
    P['tela'] = tela_mat()
    return P


_lib.palette2 = palette2
SC_H = 3.1          # altura do andaime (o jogo recorta na altura da obra)
POLES_B = [(-0.62, 0.5), (0.62, 0.5)]
POLES_F = [(-0.86, -0.36), (0.86, -0.36)]
Z_PE = 0.15         # pe do andaime (topo da laje)
STEP = 0.5          # distancia entre as travessas do andaime


def tela_mat():
    """Tela de obra laranja: malha em losango com furos transparentes, em qualquer face (usa x + y e z do objeto)."""
    key = 'tela_obra'
    if key in _lib._M:
        return _lib._M[key]
    m = mat(key, '#f07a22', rough=0.7, var=0.0, bump=0.0, sheen=0.3)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Object'], sep.inputs[0])

    def op(kind, a, b=None, val=None):
        n = N.new('ShaderNodeMath')
        n.operation = kind
        L.new(a, n.inputs[0])
        if b is not None:
            L.new(b, n.inputs[1])
        elif val is not None:
            n.inputs[1].default_value = val
        return n.outputs[0]
    u = op('ADD', sep.outputs['X'], sep.outputs['Y'])
    fio = []
    for kind in ('ADD', 'SUBTRACT'):
        d = op(kind, u, sep.outputs['Z'])
        f = op('FRACT', op('MULTIPLY', d, val=15.0))
        fio.append(op('LESS_THAN', f, val=0.34))
    fill = op('MAXIMUM', fio[0], fio[1])
    tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader')
    L.new(fill, mix.inputs['Fac'])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(bsdf.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return m


def panel(root, name, a, b, z0, z1, m):
    """Placa fina vertical entre os pontos a e b do chao (x, y), de z0 a z1 (a tela do andaime)."""
    bm = bmesh.new()
    vs = [bm.verts.new((a[0], a[1], z0)), bm.verts.new((b[0], b[1], z0)), bm.verts.new((b[0], b[1], z1)), bm.verts.new((a[0], a[1], z1))]
    bm.faces.new(vs)
    return bm_to_obj(bm, name, root, [m], smooth=False)


def traffic_cone(root, name, P, loc, s=1.0, rot=(0, 0, 0)):
    """Cone de transito laranja com a faixa branca e a base quadrada."""
    e = empty(root, name, loc=loc, rot=rot)
    e.scale = (s, s, s)
    kids(e, box(root, name + '_base', (0.17, 0.17, 0.02), (0, 0, 0.01), m=P['obra_d'], bev=0.008),
         lathe(root, name + '_corpo', [(0.0, 0.07, 0.07), (0.02, 0.066, 0.066), (0.24, 0.018, 0.018), (0.25, 0.0, 0.0)], P['obra'], segs=20, lv=1),
         lathe(root, name + '_faixa', [(0.09, 0.054, 0.054), (0.14, 0.042, 0.042)], P['white'], segs=20, lv=1, caps=False))
    return e


def concrete_block(root, name, P, loc, rot=0.0, s=1.0):
    """Bloco de concreto com os dois furos por cima."""
    x, y, z = loc
    box(root, name, (0.2 * s, 0.1 * s, 0.1 * s), (x, y, z + 0.05 * s), rot=(0, 0, rot), m=P['block'], bev=0.008)
    for k, d in enumerate((-0.05, 0.05)):
        box(root, f'{name}_furo{k}', (0.065 * s, 0.05 * s, 0.006), (x + d * s * math.cos(rot), y + d * s * math.sin(rot), z + 0.1 * s), rot=(0, 0, rot),
            m=P['block_d'], bev=0.0)


def stake_flag(root, P, tag, x, y, z):
    """Estaca de obra com a ponta pintada e a bandeirola zebrada (laranja e branca) que tremula."""
    tube(root, tag + '_estaca', [(x, y, z - 0.02), (x, y, z + 0.78)], 0.024, P['pinus'], segs=8)
    tube(root, tag + '_estacaPonta', [(x, y, z + 0.66), (x, y, z + 0.8)], 0.027, P['obra'], segs=8)
    pen = cloth_grid(root, tag + '_bandeirola', 0.36, 0.19, 12, 3, [P['fita']],
                     shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.19 * (1 - u * 0.92))), thick=0.012)
    pen.location = (x + 0.01, y, z + 0.68)
    register_cloth(pen, flag_wave(0.36, amp=0.06, cycles=1, waves=1.1))


def site_kit(root, P, tag, z, planks, blocks, cone):
    """Material de obra de um lote vazio: tabuas de pinus, blocos de concreto e o cone."""
    for k in range(2):
        box(root, f'{tag}_tabua{k}', (0.44, 0.08, 0.032), (planks[0], planks[1] + 0.004 * k, z + 0.018 + 0.034 * k), rot=(0, 0, 0.4 + 0.08 * k),
            m=P['pinus'] if k else P['pinus_d'], bev=0.01)
    bx, by = blocks
    for k, (dx, dz, a) in enumerate(((-0.11, 0.0, 0.05), (0.11, 0.0, -0.04), (0.0, 0.1, 0.12))):
        concrete_block(root, f'{tag}_bloco{k}', P, (bx + dx, by, z + dz), rot=a)
    traffic_cone(root, tag + '_cone', P, (cone[0], cone[1], z), s=1.0)


def build_chao(P, root):
    plot(root, P, 'chao')
    return {}


def build_lote(P, root):
    plot(root, P, 'lote')
    stake_flag(root, P, 'lote', 0.5, 0.18, G0)
    site_kit(root, P, 'lote', G0, planks=(-0.28, 0.3), blocks=(0.0, 0.42), cone=(-0.46, 0.04))
    return {}


def build_marker(P, root):
    """Lote vazio sobre o cenario do Blender: so a estaca com a bandeirola e o material de obra
    (o chao do lote ja vem no fundo da fase)."""
    tag = root['set']
    stake_flag(root, P, tag, 0.5, 0.26, 0.0)
    site_kit(root, P, tag, 0.0, planks=(-0.34, 0.36), blocks=(0.0, 0.5), cone=(-0.5, 0.12))
    return {}


def build_rubble(P, root):
    """Escombros da obra parada sobre um lote de ruina (pagos para limpar): monte de entulho, toco de pilar de concreto
    com a ferragem enferrujada para fora, viga caida, cacos de bloco, o cone tombado, um pedaco de tela e capim seco."""
    tag = root['set']
    rr = random.Random(21)
    sphere(root, tag + '_monte', 0.62, (0, 0.05, -0.05), scale=(1.05, 0.95, 0.22), m=P['dust'], seg=28)
    # toco de pilar quebrado (topo em dentes) com os vergalhoes
    lathe(root, tag + '_pilar', [(0, 0.15, 0.15), (0.5, 0.14, 0.14), (0.56, 0.12, 0.13)], P['conc'], segs=24,
          wobble=lambda a, z: 0.08 * math.cos(a * 7) * max(0.0, (z - 0.45) / 0.11), lv=1)
    bpy.data.objects[tag + '_pilar'].location = (0.2, 0.24, 0.04)
    for k in range(4):
        a = TAU * k / 4 + 0.4
        x, y = 0.2 + 0.075 * math.cos(a), 0.24 + 0.075 * math.sin(a)
        bend = 0.08 if k % 2 else -0.06
        tube(root, f'{tag}_vergalhao{k}', [(x, y, 0.5), (x, y, 0.78 + 0.04 * k), (x + bend, y, 0.86 + 0.04 * k)], 0.013, P['rust'], segs=6)
    # viga caida atravessada, com a ferragem na ponta
    box(root, tag + '_viga', (0.62, 0.16, 0.14), (-0.22, 0.02, 0.13), rot=(0.12, 0.08, 0.35), m=P['conc_d'], bev=0.02)
    for k, dy in enumerate((-0.04, 0.04)):
        tube(root, f'{tag}_vigaFerro{k}', [(-0.5, -0.1 + dy, 0.1), (-0.6, -0.14 + dy, 0.14), (-0.64, -0.14 + dy, 0.22)], 0.011, P['rust'], segs=5)
    for k in range(6):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0.28, 0.58)
        box(root, f'{tag}_caco{k}', (0.17, 0.09, 0.09), (d * math.cos(a), d * math.sin(a) * 0.85, 0.07 + 0.03 * (k % 2)),
            rot=(rr.uniform(-0.4, 0.4), rr.uniform(-0.3, 0.3), rr.uniform(0, TAU)), m=P['block'] if k % 2 else P['conc_d'], bev=0.02)
    for k in range(3):
        a = rr.uniform(0, TAU)
        box(root, f'{tag}_tijolo{k}', (0.12, 0.06, 0.05), (0.45 * math.cos(a), 0.4 * math.sin(a), 0.05), rot=(0.2, 0.1, rr.uniform(0, TAU)), m=P['brick'], bev=0.01)
    traffic_cone(root, tag + '_cone', P, (0.36, -0.26, 0.09), s=1.0, rot=(0, math.radians(80), math.radians(-35)))
    tl = panel(root, tag + '_tela', (-0.5, 0.3, 0), (-0.12, 0.42, 0), 0.06, 0.3, P['tela'])
    tl.rotation_euler = (0.35, 0, 0)
    for k, ang in enumerate((150, 205, 30, 120, 300)):
        a = math.radians(ang + rr.uniform(-10, 10))
        cx, cy = 0.6 * math.cos(a), 0.55 * math.sin(a)
        for j in range(5):
            b = rr.uniform(0, TAU)
            tube(root, f'{tag}_capim{k}_{j}', [(cx + 0.015 * math.cos(b), cy + 0.015 * math.sin(b), 0.0),
                                                (cx + 0.08 * math.cos(b), cy + 0.08 * math.sin(b), 0.13 + rr.uniform(0, 0.1))], 0.014,
                 P['grass_d'], segs=5, rfun=lambda t: 0.016 * (1 - t) + 0.002)
    return {}


# ---------------------------------------------------------------- andaime metalico (tubo galvanizado, abracadeiras e tela)
def pole(root, P, name, x, y, z0, z1):
    tube(root, name, [(x, y, z0), (x, y, z1)], 0.032, P['scaf'], segs=10)
    box(root, name + '_sapata', (0.13, 0.13, 0.02), (x, y, z0 + 0.01), m=P['scaf_d'], bev=0.004)
    cyl(root, name + '_topo', 0.036, 0.04, (x, y, z1), m=P['scaf_d'], v=10, bev=0.005)


def clamp(root, P, name, x, y, z):
    sphere(root, name, 0.042, (x, y, z), scale=(1, 1, 0.8), m=P['scaf_d'], seg=10)


def bar(root, P, name, a, b, r=0.022):
    tube(root, name, [a, b], r, P['scaf'], segs=8)


def build_and_back(P, root):
    (bx0, by0), (bx1, by1) = POLES_B
    for k, (x, y) in enumerate(POLES_B):
        pole(root, P, f'andT_poste{k}', x, y, Z_PE, SC_H)
    n = int((SC_H - Z_PE) / STEP)
    for j in range(1, n + 1):
        z = Z_PE + j * STEP
        bar(root, P, f'andT_trav{j}', (bx0, by0, z), (bx1, by1, z))
        for k, (x, y) in enumerate(POLES_B):
            clamp(root, P, f'andT_abr{k}_{j}', x, y, z)
        # diagonal de travamento, alternando o sentido a cada vao
        za, zb = z - STEP, z
        a, b = ((bx0, by0, za), (bx1, by1, zb)) if j % 2 else ((bx1, by1, za), (bx0, by0, zb))
        bar(root, P, f'andT_diag{j}', a, b, r=0.016)
    # tela laranja atras, presa nos postes, com a bainha de cima e de baixo
    panel(root, 'andT_tela', (bx0, by0 + 0.03), (bx1, by1 + 0.03), Z_PE + 0.05, SC_H - 0.05, P['tela'])
    for k, z in enumerate((Z_PE + 0.06, SC_H - 0.06)):
        box(root, f'andT_bainha{k}', (bx1 - bx0, 0.012, 0.04), (0, by0 + 0.03, z), m=P['obra'], bev=0.004)
    return {}


def build_and_front(P, root):
    for k, (x, y) in enumerate(POLES_F):
        pole(root, P, f'andF_poste{k}', x, y, Z_PE, SC_H)
    n = int((SC_H - Z_PE) / STEP)
    # quadros laterais (do poste da frente ao de tras): travessas, diagonais alternadas, abracadeiras e a tela
    for s, (fx, fy) in enumerate(POLES_F):
        bx, by = POLES_B[s]
        for j in range(1, n + 1):
            z = Z_PE + j * STEP
            bar(root, P, f'andF_trav{s}_{j}', (fx, fy, z), (bx, by, z))
            clamp(root, P, f'andF_abr{s}_{j}', fx, fy, z)
            za = z - STEP
            a, b = ((fx, fy, za), (bx, by, z)) if (j + s) % 2 else ((bx, by, za), (fx, fy, z))
            bar(root, P, f'andF_diag{s}_{j}', a, b, r=0.016)
        ox = -0.025 if fx < 0 else 0.025
        panel(root, f'andF_tela{s}', (fx + ox, fy), (bx + ox, by), Z_PE + 0.05, SC_H - 0.05, P['tela'])
        for k, z in enumerate((Z_PE + 0.06, SC_H - 0.06)):
            tube(root, f'andF_bainha{s}_{k}', [(fx + ox, fy, z), (bx + ox, by, z)], 0.016, P['obra'], segs=6)
    return {}


def build_plank(P, root):
    """Plataforma do andaime na altura da fiada: tres tabuas de pinus sobre dois tubos, com o rodape zebrado."""
    for k in range(3):
        box(root, f'tabua{k}', (1.9, 0.12, 0.05), (0, -0.4 + 0.13 * k, 0.0), m=P['pinus'] if k % 2 else P['pinus_d'], bev=0.012)
    for s in (-1, 1):
        tube(root, f'tabuaTubo{s}', [(s * 0.86, -0.56, -0.05), (s * 0.86, 0.0, -0.05)], 0.022, P['scaf'], segs=8)
        sphere(root, f'tabuaAbr{s}', 0.035, (s * 0.86, -0.48, -0.05), m=P['scaf_d'], seg=10)
    box(root, 'tabuaRodape', (1.9, 0.02, 0.06), (0, -0.475, 0.045), m=P['fita'], bev=0.006)
    return {}


def build_pile(P, root):
    """Pilha de material: palete com blocos de concreto, tijolos e o saco de cimento."""
    for k in range(3):
        box(root, f'paleteRipa{k}', (0.46, 0.08, 0.02), (0.0, -0.11 + 0.11 * k, 0.04), m=P['pinus_d'], bev=0.005)
    for k in range(3):
        box(root, f'paleteBarrote{k}', (0.06, 0.32, 0.03), (-0.19 + 0.19 * k, 0.0, 0.015), m=P['pinus'], bev=0.005)
    for k, (x, y, z, a) in enumerate(((-0.11, -0.055, 0, 0), (0.11, -0.055, 0, 0), (-0.11, 0.055, 0, 0), (0.11, 0.055, 0, 0),
                                       (-0.02, -0.04, 0.1, 0.25), (0.08, 0.06, 0.1, 0.1))):
        concrete_block(root, f'pilhaBloco{k}', P, (x, y, 0.05 + z), rot=a, s=1.0)
    for k, (x, y, z, a) in enumerate(((0.33, 0.02, 0, 0.1), (0.33, 0.1, 0, 0.1), (0.33, 0.06, 0.06, -0.2))):
        box(root, f'pilhaTijolo{k}', (0.12, 0.07, 0.06), (x, y, z + 0.03), rot=(0, 0, a), m=P['brick'], bev=0.008)
    sk = box(root, 'pilhaSaco', (0.2, 0.13, 0.08), (-0.34, -0.03, 0.045), rot=(0, 0, 0.3), m=P['cement'], bev=0.035, seg=4)
    box(root, 'pilhaSacoFaixa', (0.06, 0.135, 0.085), (-0.34, -0.03, 0.045), rot=(0, 0, 0.3), m=P['cement_s'], bev=0.02)
    return {}


def build_mason(P, root):
    """Pedreiro de capacete amarelo, colete laranja com faixas refletivas, camisa de brim e calca jeans."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(tunic=P['shirt'], vest=P['vest_o'], head='bald', pants=P['jeans'], boot_m=P['boot'],
                                         belt=P['leather'], bracer=P['skin'], glove=P['glove'], face=math.radians(-30)))
    for k, (z0, z1, rx, ry) in enumerate(((0.345, 0.37, 0.091, 0.107), (0.395, 0.42, 0.094, 0.115))):
        o = lathe(root, f'{tag}_refletiva{k}', [(z0, rx, ry), (z1, rx, ry)], P['refl'], segs=14, lv=1, caps=False)
        o.parent = pr['body']
    hard_hat(root, pr, tag, P['hat'])
    hm = [tube(root, tag + '_cabo', [(0, 0, -0.05), (0, 0, 0.17)], 0.012, P['wood'], segs=6),
          box(root, tag + '_cabeca_martelo', (0.1, 0.04, 0.045), (0.0, 0, 0.18), m=P['iron'], bev=0.008)]
    hold(pr, 'R', *hm)
    return pr


HIT_N = 8


def mason_state(f):
    """Martelada: ergue (0..4) e desce com forca (5..7); o quadro 6 e a batida."""
    lift = [0.0, 0.35, 0.7, 0.92, 1.0, 0.6, 0.0, 0.05][f]
    hz = 0.28 + 0.3 * lift
    return dict(hand_R=(0.18 - 0.06 * lift, -0.1, hz), grip_R=(1.0 - 1.4 * lift, 0, 0.3 + 0.9 * lift), hand_L=(0.16, 0.06, 0.26),
                lean=0.25 - 0.18 * lift, head_pitch=0.1, head_yaw=0.0, ph=f / HIT_N, breathe=0.0)


SPEC = {
    'towers': [('chao', 'Chao do lote', build_chao), ('lote', 'Lote vazio', build_lote)],
    'crews': [
        {'key': 'andT', 'label': 'Andaime tras', 'build': build_and_back, 'modes': [('still', 1, lambda parts, P, root, f: None)], 'margin': (0.1, 0.1, 0.1, 0.1)},
        {'key': 'andF', 'label': 'Andaime frente', 'build': build_and_front, 'modes': [('still', 1, lambda parts, P, root, f: None)], 'margin': (0.1, 0.1, 0.1, 0.1)},
        {'key': 'tabua', 'label': 'Tabua', 'build': build_plank, 'modes': [('still', 1, lambda parts, P, root, f: None)], 'margin': (0.1, 0.1, 0.1, 0.1)},
        {'key': 'pilha', 'label': 'Pilha de blocos', 'build': build_pile, 'modes': [('still', 1, lambda parts, P, root, f: None)]},
        {'key': 'marco', 'label': 'Marco do lote', 'build': build_marker, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('tremula', ANIM_N, lambda parts, P, root, f: apply_anim(f / ANIM_N))]},
        {'key': 'ruina', 'label': 'Escombros do lote', 'build': build_rubble, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('still', 1, lambda parts, P, root, f: None)]},
        {'key': 'pedreiro', 'label': 'Pedreiro', 'build': build_mason, 'boost': CREW_BOOST,
         'pose0': lambda parts, P, root: pose_person(parts, P, root, mason_state(0)),
         'show': lambda parts, P, root: pose_person(parts, P, root, mason_state(3)),
         'modes': [('bate', HIT_N, lambda parts, P, root, f: pose_person(parts, P, root, mason_state(f)))]},
    ],
}


if __name__ == '__main__':
    main(FAM, SPEC)
