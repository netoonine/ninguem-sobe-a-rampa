"""Laranjal (Ninguem Sobe a Rampa, motor 'archer', familia 'arqueiros', SO A CHAPA V): niveis 1 a 3 e o Laranjao.
Substitui, so na chapa Verde-Amarela, a arte do Mensalinho (a chapa R continua com tools/blender/torre_arqueiros.py).
Piada: as "candidaturas laranja" (candidato de fachada). Pomar de campanha no lote de concreto de Brasilia: uma
laranjeira robusta cuja copa e a plataforma de tiro (deck de tabuas cercado de sebe), caixotes de feira cheios de
laranja, a banquinha de campanha com a bandeirinha da chapa e dois apoiadores de camisa amarela e bone verde que
arremessam laranjas (mesmo arremesso e mesmos quadros do Mensalinho). O Laranjao troca a dupla por um caixote-catapulta
de rodas de rodela de laranja que cospe caixotes inteiros. Pecas em tools/blender/laranjal_pecas.py.
Mesmos conjuntos, postos, luzes, modos e enquadramento do Mensalinho (js/sprites.js depende deles).

  CHAPA=V Blender -b -P tools/blender/torre_laranjal.py -- render arte/render/arqueiros [conjuntos...]
  CHAPA=V Blender -b -P tools/blender/torre_laranjal.py -- still <arquivo.png> [amostras]
  CHAPA=V Blender -b -P tools/blender/torre_laranjal.py -- crew <arquivo.png> [amostras] [show|pose0]
NAO renderize com CHAPA=R (a pasta arte/render_r/arqueiros e do Mensalinho).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib as _lib
from laranjal_pecas import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto de Brasilia (o mesmo das outras torres)

FAM = 'arqueiros'
BAL_BOOST = 1.12
BAL_DIRS, BAL_FRAMES = 16, 8

_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811 - laranja, folhagem, madeira de caixote e as cores da chapa
    return mats_laranjal(_orig_palette2())


_lib.palette2 = palette2


def tower(key, fn):
    def build(P, root):
        B = fn(P, root)
        B['lights'] = B.get('lights', [])
        return B
    return build


def bandeira_deck(root, P, tag, fz, R, ang_deg, h=0.42):
    """Bandeirinha da chapa em pe na sebe do deck (pano parado)."""
    a = math.radians(ang_deg)
    r = R - 0.04
    bandeira_chapa(root, P, tag + '_bandeiraDeck', (r * math.cos(a), r * math.sin(a), fz + 0.05), h=h)


# ---------------------------------------------------------------- Laranjal N1 a N3 e a base do Laranjao
def build_n1(P, root):
    plot(root, P, 'n1')
    fz, R = 1.05, 0.6
    laranjeira(root, P, 'n1_arvore', fz, R, seed=11, frutos=0.55, trunk_r=0.1)
    lamp = banca(root, P, 'n1_banca', (-0.34, -0.46, G), w=0.38, d=0.18, h=0.22, flag_h=0.3)
    caixote(root, P, 'n1_municao', s=0.8, seed=21).location = (0.26, 0.3, fz)
    pilha_caixotes(root, P, 'n1_caixote', [(0.56, -0.36, G, 0.35, 1.0, True, True), (0.6, -0.1, G, 1.2, 0.95, True, False)])
    laranjas_chao(root, P, 'n1_caida', [(0.22, -0.6, G, 0.04), (0.06, -0.3, G, 0.042), (-0.6, -0.1, G, 0.04)])
    bandeira_pano(root, P, 'n1_bandeira', -0.4, 0.36, fz, size=0.4, h_pole=0.82)
    slots = [(-0.2, -0.12, fz + 0.01), (0.18, -0.14, fz + 0.01)]
    return {'slots': slots, 'lights': [(lamp, '#ffcf7a', 12.0, 1)]}


def build_n2(P, root):
    plot(root, P, 'n2')
    fz, R = 1.42, 0.7
    laranjeira(root, P, 'n2_arvore', fz, R, seed=12, frutos=0.62, trunk_r=0.115, galhos_lat=2)
    lamp = banca(root, P, 'n2_banca', (-0.32, -0.48, G), w=0.4, d=0.18, h=0.23, flag_h=0.3)
    m_ = caixote(root, P, 'n2_municao', s=0.82, seed=22)
    m_.location, m_.rotation_euler = (0.3, 0.34, fz), (0, 0, 0.3)
    pilha_caixotes(root, P, 'n2_caixote', [(0.58, -0.34, G, 0.35, 1.0, True, True), (0.6, -0.08, G, 1.25, 0.95, True, False),
                                           (0.59, -0.21, G + 0.13, 0.75, 0.92, True, False)])
    mudinha(root, P, 'n2_muda', (-0.68, -0.04, G), s=0.9)
    laranjas_chao(root, P, 'n2_caida', [(0.24, -0.62, G, 0.04), (0.06, -0.32, G, 0.04), (0.28, 0.32, G, 0.04)])
    bandeira_deck(root, P, 'n2', fz, R, 0, h=0.42)     # de lado: atras subiria o topo do quadro
    slots = [(-0.24, -0.16, fz + 0.01), (0.22, -0.18, fz + 0.01)]
    return {'slots': slots, 'lights': [(lamp, '#ffcf7a', 12.0, 1)]}


def build_n3(P, root):
    plot(root, P, 'n3')
    fz, R = 1.95, 0.82
    laranjeira(root, P, 'n3_arvore', fz, R, seed=13, frutos=0.7, trunk_r=0.13, galhos_lat=2)
    lamp = banca(root, P, 'n3_banca', (-0.32, -0.5, G), w=0.42, d=0.19, h=0.24, flag_h=0.32)
    m_ = caixote(root, P, 'n3_municao', s=0.85, seed=23, adesivo=True)
    m_.location, m_.rotation_euler = (0.34, 0.38, fz), (0, 0, 0.3)
    for k, x in enumerate((-0.42, 0.42)):
        estandarte_chapa(root, f'n3_estandarte{k}', P, x, -0.86, fz - 0.25, w=0.26, h=0.5)
    pilha_caixotes(root, P, 'n3_caixote', [(0.6, -0.34, G, 0.35, 1.0, True, True), (0.62, -0.08, G, 1.25, 0.95, True, False),
                                           (0.6, -0.21, G + 0.13, 0.75, 0.92, True, True)])
    mudinha(root, P, 'n3_muda', (-0.7, -0.02, G), s=1.0)
    laranjas_chao(root, P, 'n3_caida', [(0.24, -0.66, G, 0.04), (0.08, -0.34, G, 0.04), (0.3, 0.34, G, 0.042)])
    bandeira_pano(root, P, 'n3_bandeira', -0.5, 0.5, fz, size=0.48, h_pole=0.95)
    bandeira_deck(root, P, 'n3', fz, R, 35, h=0.5)
    lights = []
    for k, a in enumerate((-0.22, math.pi + 0.22)):
        r = R - 0.04
        lights.append((lanterna_poste(root, P, f'n3_poste{k}', r * math.cos(a), r * math.sin(a), fz + 0.06, h=0.32), '#ffd896', 16.0, 1))
    slots = [(-0.24, -0.18, fz + 0.01), (0.22, -0.2, fz + 0.01)]
    return {'slots': slots, 'lights': lights}


def build_n4(P, root):
    plot(root, P, 'n4')
    fz, R = 2.05, 0.88
    laranjeira(root, P, 'n4_arvore', fz, R, seed=14, frutos=0.72, trunk_r=0.14, galhos_lat=2)
    banca(root, P, 'n4_banca', (-0.32, -0.52, G), w=0.42, d=0.19, h=0.24, lamp=False, flag_h=0.32)
    for k, x in enumerate((-0.46, 0.46)):
        estandarte_chapa(root, f'n4_estandarte{k}', P, x, -0.92, fz - 0.25, w=0.26, h=0.5)
    # a reserva do Laranjao: pilha de caixotes no pe da arvore
    pilha_caixotes(root, P, 'n4_caixote', [(0.6, -0.4, G, 0.35, 1.05, True, True), (0.63, -0.12, G, 1.25, 1.0, True, False),
                                           (0.61, -0.27, G + 0.137, 0.6, 1.0, True, True), (0.4, -0.66, G, -0.3, 0.9, True, False)])
    mudinha(root, P, 'n4_muda', (-0.72, -0.0, G), s=1.0)
    laranjas_chao(root, P, 'n4_caida', [(0.12, -0.36, G, 0.04), (-0.06, -0.7, G, 0.04), (0.3, 0.36, G, 0.042)])
    bandeira_pano(root, P, 'n4_bandeira', -0.56, 0.52, fz, size=0.48, h_pole=0.95)
    bandeira_deck(root, P, 'n4', fz, R, 35, h=0.5)
    lights = []
    for k, a in enumerate((-0.22, math.pi + 0.22)):
        r = R - 0.04
        lights.append((lanterna_poste(root, P, f'n4_poste{k}', r * math.cos(a), r * math.sin(a), fz + 0.06, h=0.3), '#ffd896', 16.0, 1))
    slots = [(0.0, 0.0, fz)]   # pivo do Laranjao
    return {'slots': slots, 'lights': lights}


# ---------------------------------------------------------------- Laranjao: o caixote-catapulta que cospe caixotes
OP_O, OP_F = (-0.39, -0.3, 0.065), 0.25     # operador (local ao pivo) e para onde olha
ALAV = (-0.2, -0.25, 0.07)                   # pe da alavanca (local ao recuo)
ALAV_L = 0.32


def vis(o, on):
    for c in [o] + list(o.children_recursive):
        c.hide_render = c.hide_viewport = not on


def adesivo_chapa(root, P, name, parent, loc, w, h):
    """Adesivo da chapa colado na tampa (face +Z do pivo `parent`): fundo na cor principal e o emblema."""
    b = box(root, name, (w, h, 0.003), (0, 0, 0), m=P['chapa'], bev=0.001)
    b.parent = parent
    b.location = loc
    for o in emblema(root, name + '_emblema', w * 0.9, h * 0.9, depth=0.003):
        if o.parent == root:
            o.parent = b
            o.location = (0, 0, 0.002)
            o.rotation_euler = (-math.pi / 2, 0, 0)    # plano XZ -> face para +Z
    return b


def build_ballista(P, root):
    piv = empty(root, 'bal_pivo')
    rec = empty(root, 'bal_recuo', parent=piv)
    parts = {'pivot': piv, 'recoil': rec}

    def p(o, par=rec):
        o.parent = par
        return o
    # prato giratorio de madeira com aro amarelo e feltro verde
    p(cyl(root, 'bal_prato', 0.36, 0.06, (0, 0, 0.03), m=P['madeira'], v=40, bev=0.015), piv)
    p(torus(root, 'bal_pratoAro', (0, 0, 0.056), 0.352, 0.016, P['chapa2'], n=40, segs=6), piv)
    p(cyl(root, 'bal_pratoVerde', 0.27, 0.012, (0, 0, 0.064), m=P['chapa'], v=40, bev=0.004), piv)
    p(cyl(root, 'bal_pedestal', 0.13, 0.1, (0, 0, 0.11), r2=0.09, m=P['madeira_cl'], v=24, bev=0.02))
    # o caixotao deitado, mirando +X um pouco para cima; a tampa de ripas abre como uma boca
    mb = empty(root, 'bal_caixaPivo', loc=(0.05, 0, 0.21), parent=rec, rot=(0, -0.12, 0))
    mb.scale = (1.22, 1.22, 1.22)
    L, W, H = 0.66, 0.38, 0.16
    x0 = -0.29
    xc = x0 + L / 2
    kids(mb, box(root, 'bal_fundo', (L, W, 0.024), (xc, 0, -H / 2 + 0.012), m=P['caixote_esc'], bev=0.006),
         box(root, 'bal_dentro', (L - 0.06, W - 0.04, H - 0.03), (xc, 0, -0.005), m=P['caixote_int'], bev=0.0))
    for k, x in enumerate((x0 + 0.018, x0 + L - 0.018)):
        kids(mb, box(root, f'bal_cab{k}', (0.036, W, H), (x, 0, 0), m=P['caixote'], bev=0.008),
             box(root, f'bal_alcaVazada{k}', (0.04, W * 0.36, 0.034), (x, 0, H * 0.22), m=P['caixote_int'], bev=0.012))
    for sy in (-1, 1):
        for j, zz in enumerate((-H * 0.3, H * 0.05, H * 0.38)):
            kids(mb, box(root, f'bal_ripa{sy}{j}', (L - 0.02, 0.022, H * 0.24), (xc, sy * (W / 2 - 0.011), zz), m=P['caixote'] if j % 2 else P['caixote_esc'], bev=0.005))
        for k, x in enumerate((x0 + 0.03, x0 + L - 0.03)):
            kids(mb, box(root, f'bal_quina{sy}{k}', (0.05, 0.05, H + 0.012), (x, sy * (W / 2 - 0.006), 0), m=P['madeira_cl'], bev=0.01))
    # monte de laranjas dentro
    rr = random.Random(4)
    mats = [P['laranja'], P['laranja_cl'], P['laranja_esc']]
    nx, ny = 6, 3
    for i in range(nx):
        for j in range(ny):
            x = x0 + 0.07 + (L - 0.14) * i / (nx - 1) + rr.uniform(-0.01, 0.01)
            y = -0.11 + 0.11 * j + rr.uniform(-0.01, 0.01)
            if i >= nx - 2 and j == 1:
                continue    # a boca: o caixotinho sobe por aqui
            laranja(root, P, f'bal_lar{i}{j}', 0.054, (x, y, H / 2 - 0.02 + rr.uniform(0, 0.02)), m=rr.choice(mats), seg=12, parent=mb,
                    folhas=1 if (i + j) % 5 == 0 else 0, rot=(0, 0, rr.uniform(0, TAU)))
    # rodas de rodela de laranja
    for sy in (-1, 1):
        for k, x in enumerate((x0 + 0.13, x0 + L - 0.13)):
            w_ = fatia(root, P, f'bal_roda{sy}{k}', 0.1, th=0.034, gomos=8)
            w_.parent = mb
            w_.location = (x, sy * (W / 2 + 0.02), -H / 2 + 0.02)
            w_.rotation_euler = (-sy * math.pi / 2, 0, 0.0)
            kids(mb, cyl(root, f'bal_eixo{sy}{k}', 0.018, 0.05, (x, sy * (W / 2 + 0.0), -H / 2 + 0.02), rot=(math.pi / 2, 0, 0), m=P['madeira'], v=10, bev=0.004))
    # tampa de ripas (dobradica atras), rodela gigante e o adesivo da chapa por cima
    lid = empty(root, 'bal_tampaPivo', loc=(x0, 0, H / 2), parent=mb)
    for j, yy in enumerate((-W / 3, 0.0, W / 3)):
        kids(lid, box(root, f'bal_tampaRipa{j}', (L, W / 3 - 0.012, 0.03), (L / 2, yy, 0.016), m=P['caixote'] if j != 1 else P['caixote_esc'], bev=0.006))
    for k, x in enumerate((0.07, L - 0.07)):
        kids(lid, box(root, f'bal_tampaTrava{k}', (0.05, W + 0.01, 0.026), (x, 0, 0.042), m=P['madeira_cl'], bev=0.007))
    kids(lid, box(root, 'bal_forro', (L - 0.04, W - 0.04, 0.01), (L / 2, 0, -0.002), m=P['caixote_int'], bev=0.003))
    rod = fatia(root, P, 'bal_tampaRodela', 0.13, th=0.03, gomos=8)
    rod.parent = lid
    rod.location = (L * 0.36, 0, 0.044)
    parts['lid'] = lid
    adesivo_chapa(root, P, 'bal_adesivo', lid, (L * 0.74, 0, 0.034), 0.16, 0.12)
    # o caixotinho (projetil) pronto na boca
    cx = caixote(root, P, 'bal_caixotinho', s=0.78, seed=7)
    cx.parent = mb
    parts['caixotinho'] = cx
    # estouro de laranjas e suco no disparo
    burst = []
    for k in range(6):
        if k % 2 == 0:
            b = laranja(root, P, f'bal_estouro{k}', 0.046, (0, 0, 0), seg=12, folhas=1 if k == 2 else 0)
        else:
            b = sphere(root, f'bal_estouro{k}', 0.028, (0, 0, 0), scale=(1.5, 1, 1), m=P['suco'], seg=10)
        b.parent = rec
        burst.append(b)
    parts['burst'] = burst
    # alavanca de madeira com uma laranja na ponta (o operador puxa na recarga)
    lev = empty(root, 'bal_alavancaPivo', loc=ALAV, parent=rec)
    kids(lev, tube(root, 'bal_alavanca', [(0, 0, 0), (0, 0, ALAV_L)], 0.015, P['madeira_cl'], segs=8))
    laranja(root, P, 'bal_alavancaBola', 0.036, (0, 0, ALAV_L + 0.012), seg=12, parent=lev, folhas=1)
    p(cyl(root, 'bal_alavancaBase', 0.05, 0.045, (ALAV[0], ALAV[1], ALAV[2]), m=P['madeira'], v=14, bev=0.01))
    parts['lever'] = lev
    # operador (gira junto)
    op = build_apoiador(P, root, 'op', tag='balop')
    op['body'].parent = piv
    parts['op'] = op
    return parts


def pose_ballista(parts, P, root, yaw, draw=1.0, recoil=0.0, bolt=True, op_ph=0.0):
    parts['pivot'].rotation_euler = (0, 0, yaw)
    parts['recoil'].location = (-0.06 * recoil, 0, 0)
    parts['lid'].rotation_euler = (0, -(0.62 + 0.36 * (1 - draw)), 0)
    cx = parts['caixotinho']
    cx.location = (0.2, 0, 0.065 + 0.075 - 0.14 * (1 - draw) - 0.052)
    cx.rotation_euler = (0, 0, 0)
    vis(cx, bolt or draw >= 0.45)
    e = 1.0 - recoil
    rr = random.Random(9)
    for k, b in enumerate(parts['burst']):
        a = (k - 2.5) * 0.42
        d = 0.5 + 0.06 * (k % 3) + 0.32 * e
        b.location = (d * math.cos(a * 0.5), 0.07 * (k - 2.5) * (1 + 1.6 * e), 0.36 + 0.06 * (k % 2) + 0.12 * e - 0.25 * e * e)
        b.rotation_euler = (rr.uniform(-1.2, 1.2), rr.uniform(-0.8, 0.8), rr.uniform(0, 3))
        vis(b, recoil >= 0.5)
    crank = 0.0 if bolt or draw == 0 else math.sin(math.pi * draw)
    c = -0.5 * crank
    parts['lever'].rotation_euler = (0, c, 0)
    kx = ALAV[0] - 0.06 * recoil + (ALAV_L + 0.01) * math.sin(c)
    kz = ALAV[2] + (ALAV_L + 0.01) * math.cos(c)
    dx, dy = kx - OP_O[0], ALAV[1] - OP_O[1]
    bx = dx * math.cos(-OP_F) - dy * math.sin(-OP_F)
    by = dx * math.sin(-OP_F) + dy * math.cos(-OP_F)
    bz = kz - OP_O[2]
    s = math.sin(TAU * op_ph)
    pose_person(parts['op'], P, root, dict(offset=OP_O, face=OP_F, hand_R=(bx - 0.01, by - 0.03, bz - 0.01), hand_L=(bx - 0.01, by + 0.03, bz + 0.01),
                                           grip_R=(0.0, 1.0, 0.2), grip_L=(0.0, -1.0, 0.2), pole_R=(-0.4, -1.0, -0.6), pole_L=(-0.4, 1.0, -0.6),
                                           lean=0.06 * crank, breathe=s, head_yaw=0.15 * s - 0.1, head_pitch=0.15, ph=op_ph))


BAL_SEQ = [  # disparo: a tampa escancara e cospe o caixotinho, o caixotao recua, assenta, o operador puxa a alavanca e sobe outro
    dict(draw=0.0, recoil=1.0, bolt=False),
    dict(draw=0.0, recoil=0.55, bolt=False),
    dict(draw=0.0, recoil=0.15, bolt=False),
    dict(draw=0.2, recoil=0.0, bolt=False),
    dict(draw=0.45, recoil=0.0, bolt=False),
    dict(draw=0.7, recoil=0.0, bolt=False),
    dict(draw=0.9, recoil=0.0, bolt=False),
    dict(draw=1.0, recoil=0.0, bolt=True),
]


# ---------------------------------------------------------------- projeteis (2x, o jogo gira e reduz; +X = direcao do voo)
def build_flecha(P, root):
    """Uma laranja com folhinha (o jogo gira o sprite: redonda, le bem girando)."""
    piv = empty(root, 'fl_pivo', rot=(math.radians(-24), math.radians(-6), 0))
    o = laranja(root, P, 'fl_laranja', 0.115, (0, 0, 0), seg=24, rot=(0, math.radians(-70), 0))
    o.parent = piv
    f1 = folha(root, P, 'fl_folha0', 0.13, (-0.04, 0.0, 0.11), rot=(0.25, -0.55, math.pi), m=P['folha'])
    f2 = folha(root, P, 'fl_folha1', 0.1, (-0.03, 0.035, 0.1), rot=(0.6, -0.3, math.pi * 0.8), m=P['folha_cl'])
    cab = tube(root, 'fl_cabinho', [(0.0, 0.0, 0.1), (-0.03, 0.0, 0.13)], 0.008, P['casca'], segs=6)
    for x in (f1, f2, cab):
        x.parent = piv
    return {}


def build_virote(P, root):
    """Caixote inteiro de laranjas voando (laranjas escapando para tras)."""
    piv = empty(root, 'vi_pivo', rot=(math.radians(-26), 0, 0))
    s = 1.35
    c = caixote(root, P, 'vi_caixa', s=s, seed=4, adesivo=True)
    c.parent = piv
    c.location = (0, 0, -0.13 * s / 2)
    for k, (x, y, z, r) in enumerate(((-0.24, 0.02, 0.1, 0.044), (-0.31, -0.05, 0.02, 0.04), (-0.2, -0.08, 0.16, 0.036))):
        laranja(root, P, f'vi_solta{k}', r, (x, y, z), m=[P['laranja'], P['laranja_cl'], P['laranja_esc']][k], seg=12, parent=piv, folhas=1 if k == 0 else 0,
                rot=(0.5 * k, 0.3, 1.1 * k))
    return {}


def build_cravada(P, root):
    """Laranja esborrachada no chao: casca achatada aberta, poca de suco, gomo solto, sementes e pingos."""
    piv = empty(root, 'cr_pivo')
    kids(piv, sphere(root, 'cr_laranja', 0.1, (0, 0, 0.032), scale=(1.3, 1.12, 0.42), m=P['laranja'], seg=22),
         sphere(root, 'cr_polpa', 0.088, (0.005, 0, 0.058), scale=(1.18, 1.0, 0.2), m=P['polpa'], seg=20))
    rr = random.Random(5)
    # coroa de casca rasgada em volta
    for k in range(7):
        a = TAU * k / 7 + rr.uniform(-0.2, 0.2)
        o = sphere(root, f'cr_lasca{k}', 0.04, (0.13 * math.cos(a), 0.11 * math.sin(a), 0.04), scale=(1.0, 0.55, 0.22), m=P['laranja'] if k % 2 else P['laranja_esc'],
                   seg=10, rot=(rr.uniform(-0.3, 0.3), -0.7, a))
        o.parent = piv
    # poca de suco
    for k, (x, y, r, sx, sy) in enumerate(((0.1, -0.06, 0.09, 1.4, 1.0), (-0.12, 0.04, 0.075, 1.2, 1.0), (0.02, 0.1, 0.07, 1.3, 0.9), (-0.06, -0.1, 0.06, 1.1, 1.0))):
        kids(piv, sphere(root, f'cr_poca{k}', r, (x, y, 0.0), scale=(sx, sy, 0.07), m=P['suco'], seg=16))
    # pingos no chao e gotas saltando
    for k in range(7):
        a = TAU * k / 7 + 0.3
        d = rr.uniform(0.22, 0.3)
        kids(piv, sphere(root, f'cr_pingo{k}', rr.uniform(0.012, 0.02), (d * math.cos(a), d * 0.85 * math.sin(a), 0.004), scale=(1, 1, 0.5), m=P['suco'], seg=10))
    for k, (a, h) in enumerate(((0.4, 0.17), (2.0, 0.14), (3.4, 0.2), (5.0, 0.12))):
        kids(piv, sphere(root, f'cr_gota{k}', 0.017, (0.17 * math.cos(a), 0.14 * math.sin(a), h), scale=(1, 1, 1.4), m=P['suco'], seg=10))
    # gomo solto, sementes e uma folha
    kids(piv, sphere(root, 'cr_gomo', 0.045, (0.2, 0.06, 0.012), scale=(1.4, 0.7, 0.4), m=P['polpa'], seg=12, rot=(0, 0, 0.6)))
    for k, (x, y) in enumerate(((-0.17, -0.07), (0.07, -0.16))):
        kids(piv, sphere(root, f'cr_semente{k}', 0.012, (x, y, 0.006), scale=(1.6, 1, 0.6), m=P['semente'], seg=8, rot=(0, 0, k)))
    f = folha(root, P, 'cr_folha', 0.12, (-0.16, 0.12, 0.012), rot=(0, 0, 0.7))
    f.parent = piv
    return {}


def apoiador_crew(v):
    return {'key': v, 'label': 'Apoiador ' + v, 'build': lambda P, root, v=v: build_apoiador(P, root, v), 'boost': CREW_BOOST,
            'margin': (0.06, 0.06, 0.08, 0.05),
            'pose0': lambda parts, P, root: pose_apoiador(parts, P, root, 'idle', 0),
            'show': lambda parts, P, root: pose_apoiador(parts, P, root, 'aim', 0),
            'modes': [(m, n, (lambda parts, P, root, f, m=m: pose_apoiador(parts, P, root, m, f))) for m, n in (('idle', IDLE), ('aim', AIM), ('shoot', SHOOT))]}


def ballista_turret():
    modes = []
    for i in range(BAL_DIRS):
        modes.append((f'd{i:02d}', BAL_FRAMES, (lambda parts, P, root, f, i=i: pose_ballista(parts, P, root, yaw=TAU * i / BAL_DIRS, op_ph=f / BAL_FRAMES, **BAL_SEQ[f]))))
    return {'key': 'bal', 'label': 'Caixotao do Laranjao', 'build': build_ballista, 'boost': BAL_BOOST, 'margin': (0.08, 0.2, 0.1, 0.06),
            'pose0': lambda parts, P, root: pose_ballista(parts, P, root, yaw=math.radians(-30)), 'modes': modes, 'dirs': BAL_DIRS}


def still(key, label, fn, shadow=False):
    return {'key': key, 'label': label, 'build': fn, 'boost': PROJ_PX, 'pxk': PROJ_PX, 'shadow': shadow,
            'margin': (0.04, 0.12 if shadow else 0.04, 0.05, 0.04), 'modes': [('still', 1, lambda parts, P, root, f: None)]}


CREW_VARIANTS = ('a1', 'a2', 'a3', 'a3b')

SPEC = {
    'show_crew': {'n1': ['a1', 'a1'], 'n2': ['a2', 'a2'], 'n3': ['a3', 'a3b'], 'n4': ['bal']},
    'towers': [('n1', 'Laranjal N1', tower('n1', build_n1)), ('n2', 'Laranjal N2', tower('n2', build_n2)), ('n3', 'Laranjal N3', tower('n3', build_n3)),
               ('n4', 'Laranjao', tower('n4', build_n4))],
    'crews': [apoiador_crew(v) for v in CREW_VARIANTS],
    'turrets': [ballista_turret()],
    'stills': [still('flecha', 'Laranja', build_flecha), still('virote', 'Caixote de laranjas', build_virote),
               still('cravada', 'Laranja esborrachada', build_cravada, shadow=True)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
