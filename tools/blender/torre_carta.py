"""Carta ao Povo Brasileiro (Ninguem Sobe a Rampa, chapa R, motor 'archer', familia 'arqueiros'): niveis 1 a 3 e o
Malote. Simbolo amigo da Chapa Vermelha (a carta aberta de 2002): a mesma torre de concreto branco modernista de
Brasilia do Mensalinho (fuste hiperbolico, colunas do Alvorada e a cuia da Camara no alto, aberta), com guiche de
agencia de correio na frente e dois funcionarios de camiseta vermelha e bone vermelho que arremessam CARTAS lacradas
(lacre vermelho com estrela branca). Nada de dinheiro: caixa de correio vermelha, macos de cartas, caixa de cartas,
malotes de lona e uma carta gigante tremulando no mastro. O Malote troca a dupla por uma catapulta de carrinho de
correio cuja concha e um malote de lona vermelha gigante, que arremessa malotes.
Pecas em tools/blender/carta_pecas.py (a geometria de concreto vem de mensalinho_pecas.py, que fica intacto).
Mesmos conjuntos, postos, luzes e modos do Mensalinho/Mirante dos Arqueiros (js/sprites.js depende deles).
So a chapa R (a V usa o Laranjal):

  CHAPA=R Blender -b -P tools/blender/torre_carta.py -- render arte/render_r/arqueiros [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_carta.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_carta.py -- crew <arquivo.png> [amostras] [show|pose0]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib as _lib
from carta_pecas import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto de Brasilia (o mesmo das outras torres)

FAM = 'arqueiros'
BAL_BOOST = 1.12
BAL_DIRS, BAL_FRAMES = 16, 8
LUZ = '#ffd896'      # luz quente da agencia (lanterna do guiche)

_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811 - concreto branco e correio
    return mats_carta(_orig_palette2())


_lib.palette2 = palette2


def bandeira_parapeito(root, P, tag, fz, R, rail, ang_deg, h=0.42):
    """Bandeirinha da chapa em pe no parapeito da cuia (lado direito, pano para fora)."""
    a = math.radians(ang_deg)
    r = R - 0.0375
    bandeira_chapa(root, P, tag + '_bandeiraChapa', (r * math.cos(a), r * math.sin(a), fz + rail - 0.004), h=h)


def tower(key, fn):
    def build(P, root):
        B = fn(P, root)
        B['lights'] = B.get('lights', [])
        return B
    return build


def corpo(root, P, tag, fz, r0, rw, r1, R, rail, vidro=0.0, aletas=(), s_aleta=None, w_aleta=0.22, podio=0.5, trim=None):
    """Torre inteira de concreto: podio, fuste, faixa de vidro (opcional), cuia aberta e colunas do Alvorada."""
    cyl(root, tag + '_podio', podio, 0.05, (0, 0, 0.175), m=P['concreto_s'], v=56, bev=0.015)
    zb = fz - 0.3
    if vidro:
        zg = zb - vidro
        fuste(root, P, tag, 0.18, zg - 0.02, r0, rw, r1)
        faixa_vidro(root, P, tag, zg, zb + 0.01, r1)
    else:
        fuste(root, P, tag, 0.18, zb + 0.02, r0, rw, r1)
    cuia(root, P, tag, zb, fz, r1, R, rail=rail, trim=trim)
    sc = s_aleta or R * 0.8
    for k, a in enumerate(aletas):
        aleta(root, P, f'{tag}_aleta{k}', a, sc, 0.17, fz - 0.05, wmax=w_aleta)


# ---------------------------------------------------------------- Carta ao Povo N1 a N3 e Malote
def build_n1(P, root):
    plot(root, P, 'n1')
    fz = 1.05
    corpo(root, P, 'n1', fz, 0.36, 0.27, 0.29, 0.6, 0.18, aletas=(math.radians(-38), math.radians(-142)), s_aleta=0.47, w_aleta=0.2)
    lamp = guiche_correio(root, P, 'n1', -0.31, z0=0.18, w=0.38, d=0.22, h=0.4)
    caixa_correio(root, P, 'n1_correio', (0.56, -0.44, 0.15), s=0.95, rz=0.25)
    caixa_cartas(root, P, 'n1_bandeja', (0.24, 0.3, fz), rz=0.3)
    pilha_cartas(root, 'n1_maco', P, (0.0, 0.42, fz), n=2, rz=0.4)
    bandeira_carta(root, P, 'n1_bandeira', -0.4, 0.36, fz, size=0.4, h_pole=0.82)
    bandeira_parapeito(root, P, 'n1', fz, 0.6, 0.18, 15, h=0.42)
    slots = [(-0.2, -0.12, fz + 0.01), (0.18, -0.14, fz + 0.01)]
    return {'slots': slots, 'lights': [(lamp, LUZ, 12.0, 1)]}


def build_n2(P, root):
    plot(root, P, 'n2')
    fz = 1.42
    a4 = [math.radians(a) for a in (-36, -144, 36, 144)]
    corpo(root, P, 'n2', fz, 0.4, 0.29, 0.31, 0.7, 0.2, vidro=0.17, aletas=a4, s_aleta=0.56, w_aleta=0.22, podio=0.54)
    lamp = guiche_correio(root, P, 'n2', -0.35, z0=0.18, w=0.42, d=0.22, h=0.44)
    caixa_correio(root, P, 'n2_correio', (0.6, -0.42, 0.15), rz=0.25)
    ipe(root, P, 'n2_ipe', (-0.62, -0.38, 0.15), s=0.8)
    caixa_cartas(root, P, 'n2_bandeja', (0.3, 0.34, fz), rz=0.3)
    pilha_cartas(root, 'n2_maco', P, (-0.34, 0.34, fz), n=3, rz=-0.3)
    m_ = malote(root, 'n2_malote', P, h=0.26, R=0.1)
    m_.location = (0.02, 0.5, fz)
    m_.rotation_euler = (0, 0, 0.3)
    bandeira_parapeito(root, P, 'n2', fz, 0.7, 0.2, 0, h=0.42)    # de lado: atras subiria o topo do quadro
    slots = [(-0.24, -0.16, fz + 0.01), (0.22, -0.18, fz + 0.01)]
    return {'slots': slots, 'lights': [(lamp, LUZ, 12.0, 1)]}


def build_n3(P, root):
    plot(root, P, 'n3')
    fz = 1.95
    a5 = [math.radians(a) for a in (-32, -148, 32, 148, 90)]
    corpo(root, P, 'n3', fz, 0.46, 0.33, 0.35, 0.82, 0.22, vidro=0.24, aletas=a5, s_aleta=0.66, w_aleta=0.26, podio=0.58, trim=P['gold'])
    guiche_correio(root, P, 'n3', -0.42, z0=0.18, w=0.46, d=0.22, h=0.46)
    for k, x in enumerate((-0.42, 0.42)):
        estandarte_chapa(root, f'n3_estandarte{k}', P, x, -0.86, fz - 0.1, w=0.26, h=0.5)
    caixa_correio(root, P, 'n3_correio', (0.62, -0.44, 0.15), rz=0.25)
    ipe(root, P, 'n3_ipe', (-0.66, -0.34, 0.15), s=1.0)
    caixa_cartas(root, P, 'n3_bandeja', (0.34, 0.38, fz), rz=0.3, n=7)
    pilha_cartas(root, 'n3_maco', P, (-0.1, 0.52, fz), n=3, rz=0.2)
    bandeira_carta(root, P, 'n3_bandeira', -0.5, 0.5, fz, size=0.48, h_pole=0.95)
    bandeira_parapeito(root, P, 'n3', fz, 0.82, 0.22, 35, h=0.5)
    lights = []
    for k, a in enumerate((-0.22, math.pi + 0.22)):
        r = 0.82 - 0.04
        lights.append((globo(root, P, f'n3_poste{k}', r * math.cos(a), r * math.sin(a), fz + 0.2, h=0.18), '#ffd896', 16.0, 1))
    slots = [(-0.24, -0.18, fz + 0.01), (0.22, -0.2, fz + 0.01)]
    return {'slots': slots, 'lights': lights}


def build_n4(P, root):
    plot(root, P, 'n4')
    fz = 2.05
    a5 = [math.radians(a) for a in (-32, -148, 32, 148, 90)]
    corpo(root, P, 'n4', fz, 0.5, 0.36, 0.38, 0.88, 0.2, vidro=0.26, aletas=a5, s_aleta=0.7, w_aleta=0.28, podio=0.62, trim=P['gold'])
    guiche_correio(root, P, 'n4', -0.46, z0=0.18, w=0.48, d=0.22, h=0.46)
    for k, x in enumerate((-0.46, 0.46)):
        estandarte_chapa(root, f'n4_estandarte{k}', P, x, -0.92, fz - 0.1, w=0.26, h=0.5)
    # malotes empilhados no pe da torre (o Malote)
    for k, (x, y, z, rx, rz, hh, R) in enumerate(((0.6, -0.46, 0.15, 0.0, 0.35, 0.3, 0.12), (0.72, -0.24, 0.15, 0.0, 1.2, 0.26, 0.105),
                                                   (0.5, -0.3, 0.15 + 0.06, -1.25, 0.6, 0.24, 0.095))):
        m_ = malote(root, f'n4_malotePe{k}', P, h=hh, R=R, cartas=(k != 2), seed=k + 3)
        m_.location = (x, y, z)
        m_.rotation_euler = (rx, 0, rz)
    ipe(root, P, 'n4_ipe', (-0.68, -0.32, 0.15), s=1.0)
    pilha_cartas(root, 'n4_maco', P, (0.5, 0.5, fz), n=3, rz=0.5)
    pilha_cartas(root, 'n4_maco2', P, (0.62, 0.3, fz), n=2, rz=-0.2, seed=4)
    bandeira_carta(root, P, 'n4_bandeira', -0.56, 0.52, fz, size=0.48, h_pole=0.95)
    bandeira_parapeito(root, P, 'n4', fz, 0.88, 0.2, 35, h=0.5)
    lights = []
    for k, a in enumerate((-0.22, math.pi + 0.22)):
        r = 0.88 - 0.04
        lights.append((globo(root, P, f'n4_poste{k}', r * math.cos(a), r * math.sin(a), fz + 0.18, h=0.18), '#ffd896', 16.0, 1))
    slots = [(0.0, 0.0, fz)]   # pivo da catapulta giratoria
    return {'slots': slots, 'lights': lights}


# ---------------------------------------------------------------- Malote: catapulta de carrinho de correio
OP_O, OP_F = (-0.39, -0.3, 0.065), 0.25     # operador (local ao pivo) e para onde olha
ALAV = (-0.2, -0.25, 0.07)                   # pe da alavanca (local ao recuo)
ALAV_L = 0.32
EIXO = (0.0, 0.0, 0.37)                      # eixo do braco (local ao recuo)
BRACO_L = 0.45                               # do eixo ao malote
BETA_F, BETA_C = math.radians(118), math.radians(-12)   # braco disparado (no batente) e armado (para tras)


def vis(o, on):
    for c in [o] + list(o.children_recursive):
        c.hide_render = c.hide_viewport = not on


def concha_malote(root, P, name, R=0.2, H=0.28):
    """Concha da catapulta: malote de lona vermelha gigante e aberto (boca para +Z local), bainha enrolada, cordao
    branco franzido, estrelas brancas costuradas dos lados e cartas aparecendo na boca."""
    piv = empty(root, name)

    def fold(a, z):
        return 0.08 * math.sin(10 * a) * max(0.0, (z - 0.55 * H) / (0.45 * H))
    prof = [(0.0, 0.0, 0.0), (0.02 * H, 0.6 * R, 0.52 * R), (0.14 * H, 0.94 * R, 0.8 * R), (0.42 * H, R, 0.86 * R), (0.7 * H, 0.93 * R, 0.8 * R),
            (0.9 * H, 0.84 * R, 0.74 * R), (H, 0.88 * R, 0.78 * R)]
    kids(piv, lathe(root, name + '_lona', prof, P['malote'], segs=24, wobble=fold, caps=False, lv=2, solid=0.014))
    kids(piv, cyl(root, name + '_fundoDentro', 0.8 * R, 0.01, (0, 0, 0.5 * H), m=P['malote_esc'], v=20, bev=0.003))
    kids(piv, torus(root, name + '_bainha', (0, 0, H), 0.87 * R, 0.022, P['malote_esc'], n=28, segs=8))
    kids(piv, torus(root, name + '_cordao', (0, 0, 0.82 * H), 0.86 * R, 0.008, P['cordao'], n=28, segs=6))
    for k, sg in enumerate((-1, 1)):
        kids(piv, tube(root, f'{name}_cordaoPonta{k}', [(-0.87 * R, sg * 0.03, 0.82 * H), (-0.95 * R, sg * 0.05, 0.62 * H), (-0.93 * R, sg * 0.07, 0.48 * H)],
                       0.008, P['cordao'], segs=6))
    for k, (sx, sy) in enumerate(((0, -1), (0, 1), (-1, 0))):
        e = estrela(root, f'{name}_estrela{k}', 0.07, 0.008, m=P['estrela'], bev=0.002)
        e.parent = piv
        if sx:
            e.location = (-(0.98 * R + 0.003), 0, 0.42 * H)
            e.rotation_euler = (0, 0, math.pi / 2)
        else:
            e.location = (0, sy * (0.84 * R + 0.003), 0.42 * H)
    # cartas apontando na boca (sempre: o malote vive cheio)
    rr = random.Random(8)
    for k in range(4):
        a = TAU * k / 4 + 0.4
        e = envelope(root, f'{name}_carta{k}', P, w=0.13, h=0.1, th=0.01, aba=(k % 2 == 0), selo=(k % 2 == 0))
        e.parent = piv
        e.location = (0.5 * R * math.cos(a), 0.42 * R * math.sin(a), 0.7 * H)
        e.rotation_euler = (rr.uniform(-0.3, 0.3), rr.uniform(-0.35, 0.35), a + math.pi + rr.uniform(-0.3, 0.3))
    return piv


def build_ballista(P, root):
    piv = empty(root, 'bal_pivo')
    rec = empty(root, 'bal_recuo', parent=piv)
    parts = {'pivot': piv, 'recoil': rec}

    def p(o, par=rec):
        o.parent = par
        return o
    # prato giratorio de concreto com aro de ouro e tapete vermelho
    p(cyl(root, 'bal_prato', 0.36, 0.06, (0, 0, 0.03), m=P['concreto'], v=40, bev=0.015), piv)
    p(torus(root, 'bal_pratoAro', (0, 0, 0.056), 0.352, 0.016, P['gold'], n=40, segs=6), piv)
    p(cyl(root, 'bal_pratoTapete', 0.27, 0.012, (0, 0, 0.064), m=P['tapete'], v=40, bev=0.004), piv)
    # carrinho de correio branco (contrasta com o tapete e o malote) com faixa e estrela vermelhas e rodinhas
    p(box(root, 'bal_carro', (0.5, 0.26, 0.075), (0.0, 0, 0.135), m=mat('carrinho_branco', '#f4f0e6', rough=0.5, var=0.02, bump=0.03), bev=0.025, seg=3))
    p(box(root, 'bal_carroFaixa', (0.504, 0.264, 0.014), (0.0, 0, 0.152), m=P['chapa'], bev=0.005))
    for k, sy in enumerate((-1, 1)):
        e = estrela(root, f'bal_carroEstrela{k}', 0.024, 0.006, m=cor('pri', rough=0.45), bev=0.0015)
        p(e)
        e.location = (0.1, sy * 0.132, 0.12)
        for j, sx in enumerate((-1, 1)):
            p(cyl(root, f'bal_roda{k}{j}', 0.045, 0.03, (sx * 0.17, sy * 0.145, 0.112), rot=(math.pi / 2, 0, 0), m=P['iron_d'], v=18, bev=0.008))
            p(sphere(root, f'bal_rodaCubo{k}{j}', 0.016, (sx * 0.17, sy * 0.162, 0.112), m=P['gold'], seg=8))
    # cavaletes de madeira com o eixo de ouro e o batente acolchoado na frente
    for k, sy in enumerate((-0.1, 0.1)):
        p(tube(root, f'bal_cavaleteT{k}', [(-0.13, sy, 0.17), (EIXO[0], sy, EIXO[2])], 0.018, P['wood_l'], segs=8))
        p(tube(root, f'bal_cavaleteM{k}', [(0.1, sy, 0.17), (EIXO[0], sy, EIXO[2])], 0.018, P['wood_l'], segs=8))
        p(tube(root, f'bal_poste{k}', [(0.2, sy, 0.17), (0.16, sy, 0.555)], 0.017, P['wood_l'], segs=8))
    p(tube(root, 'bal_eixo', [(EIXO[0], -0.13, EIXO[2]), (EIXO[0], 0.13, EIXO[2])], 0.016, P['gold'], segs=8))
    p(tube(root, 'bal_batente', [(0.16, -0.12, 0.555), (0.16, 0.12, 0.555)], 0.017, P['wood_l'], segs=8))
    p(cyl(root, 'bal_batenteAlmofada', 0.032, 0.13, (0.16, 0, 0.555), rot=(math.pi / 2, 0, 0), m=P['malote'], v=14, bev=0.012))
    # braco (aponta para -X local; gira em Y: armado para tras, disparado contra o batente)
    arm = empty(root, 'bal_bracoPivo', loc=EIXO, parent=rec)
    kids(arm, box(root, 'bal_braco', (BRACO_L + 0.08, 0.042, 0.036), (-(BRACO_L + 0.08) / 2 + 0.06, 0, 0), m=P['wood_l'], bev=0.012),
         cyl(root, 'bal_bracoCubo', 0.034, 0.06, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['gold'], v=14, bev=0.006),
         box(root, 'bal_bracoCinta', (0.03, 0.05, 0.044), (-0.2, 0, 0), m=P['malote_esc'], bev=0.006))
    parts['arm'] = arm
    concha = concha_malote(root, P, 'bal_malote')
    concha.parent = arm
    concha.location = (-BRACO_L, 0, 0.012)
    # o malote (projetil) pronto na boca da concha
    mal = malote(root, 'bal_malinha', P, h=0.2, R=0.085, cartas=True, estrelas=(-1, 1), seed=9)
    mal.parent = concha
    mal.location = (0, 0, 0.14)
    mal.rotation_euler = (0, 0, 0.4)
    parts['malinha'] = mal
    # estouro de cartas no disparo
    bills = []
    for k in range(6):
        b = envelope(root, f'bal_estouro{k}', P, w=0.1, h=0.072, th=0.008, selo=(k % 2 == 0))
        b.parent = rec
        bills.append(b)
    parts['bills'] = bills
    # alavanca de ouro com bola vermelha (o operador puxa na recarga)
    lev = empty(root, 'bal_alavancaPivo', loc=ALAV, parent=rec)
    kids(lev, tube(root, 'bal_alavanca', [(0, 0, 0), (0, 0, ALAV_L)], 0.014, P['gold'], segs=8),
         sphere(root, 'bal_alavancaBola', 0.034, (0, 0, ALAV_L + 0.01), m=P['chapa'], seg=12))
    p(cyl(root, 'bal_alavancaBase', 0.045, 0.04, (ALAV[0], ALAV[1], ALAV[2] - 0.0), m=P['gold'], v=14, bev=0.008))
    parts['lever'] = lev
    # operador (gira junto)
    op = build_carteiro(P, root, 'op', tag='balop')
    op['body'].parent = piv
    parts['op'] = op
    return parts


def pose_ballista(parts, P, root, yaw, draw=1.0, recoil=0.0, bolt=True, op_ph=0.0):
    parts['pivot'].rotation_euler = (0, 0, yaw)
    parts['recoil'].location = (-0.06 * recoil, 0, 0)
    t = draw * draw * (3 - 2 * draw)
    parts['arm'].rotation_euler = (0, BETA_F + (BETA_C - BETA_F) * t - 0.05 * recoil, 0)
    vis(parts['malinha'], bolt or draw >= 0.45)
    # cartas voando na frente da concha disparada (so nos dois primeiros quadros)
    e = 1.0 - recoil
    rr = random.Random(9)
    for k, b in enumerate(parts['bills']):
        a = (k - 2.5) * 0.42
        d = 0.42 + 0.06 * (k % 3) + 0.34 * e
        b.location = (d * math.cos(a * 0.5), 0.08 * (k - 2.5) * (1 + 1.6 * e), 0.66 + 0.07 * (k % 2) + 0.1 * e - 0.3 * e * e)
        b.rotation_euler = (rr.uniform(-1.2, 1.2), rr.uniform(-0.8, 0.8), rr.uniform(0, 3))
        vis(b, recoil >= 0.5)
    crank = 0.0 if bolt or draw == 0 else math.sin(math.pi * draw)
    c = -0.5 * crank
    parts['lever'].rotation_euler = (0, c, 0)
    # maos na bola da alavanca (contas no referencial do corpo do operador)
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


BAL_SEQ = [  # disparo: o braco bate no batente e o malote voa, o carrinho recua, assenta; o operador puxa a alavanca,
    dict(draw=0.0, recoil=1.0, bolt=False),     # o braco desce para tras e outro malote entra na concha
    dict(draw=0.0, recoil=0.55, bolt=False),
    dict(draw=0.0, recoil=0.15, bolt=False),
    dict(draw=0.2, recoil=0.0, bolt=False),
    dict(draw=0.45, recoil=0.0, bolt=False),
    dict(draw=0.7, recoil=0.0, bolt=False),
    dict(draw=0.9, recoil=0.0, bolt=False),
    dict(draw=1.0, recoil=0.0, bolt=True),
]


# ---------------------------------------------------------------- projeteis (2x, o jogo gira e reduz; +X = direcao do voo)
def env_voo(root, P, name, L=0.32, Hh=0.2, th=0.024):
    """Carta deitada ao longo de +X, face para a camera: aba em seta e lacre vermelho com estrela."""
    e = envelope(root, name, P, w=Hh, h=L, th=th)
    e.rotation_euler = Matrix(((0, 0, -1), (-1, 0, 0), (0, 1, 0))).to_euler()
    e.location = (L / 2, 0, 0)
    return e


def build_flecha(P, root):
    piv = empty(root, 'fl_pivo', rot=(math.radians(-24), math.radians(-6), 0))
    env_voo(root, P, 'fl_env').parent = piv
    return {}


def build_virote(P, root):
    piv = empty(root, 'vi_pivo', rot=(math.radians(-26), 0, 0))
    h = 0.48
    m_ = malote(root, 'vi_malote', P, h=h, R=0.195, cartas=True, estrelas=(-1, 1), seed=6)
    m_.parent = piv
    m_.rotation_euler = (0, -math.pi / 2, 0)    # fundo na frente do voo, boca amarrada e cartas atras
    m_.location = (h * 0.5, 0, 0)
    return {}


def build_cravada(P, root):
    piv = empty(root, 'cr_pivo')
    env_voo(root, P, 'cr_env').parent = piv
    rot = Euler((0, math.radians(50), math.radians(-22))).to_matrix()
    tip = rot @ Vector((0.32, 0, 0))
    piv.rotation_euler = rot.to_euler()
    piv.location = Vector((0.0, 0.0, -0.025)) - tip
    terra = mat('terra_impacto', '#c4a07c', rough=0.95, var=0.06, bump=0.3)
    sphere(root, 'cr_monte', 0.075, (0.0, 0, 0.0), scale=(1.3, 1.1, 0.35), m=terra, seg=14)
    for k in range(3):
        a = TAU * k / 3 + 0.5
        sphere(root, f'cr_grao{k}', 0.018, (0.1 * math.cos(a), 0.08 * math.sin(a), 0.005), scale=(1.2, 1, 0.6), m=terra, seg=8)
    # duas cartinhas que cairam do maco, deitadas no chao (lacre para cima)
    for k, (x, y, rz, s) in enumerate(((0.17, -0.06, 0.5, 1.0), (-0.15, 0.03, -0.7, 0.9))):
        e = envelope(root, f'cr_carta{k}', P, w=0.075 * s, h=0.12 * s, th=0.008, selo=(k == 0))
        e.rotation_euler = (0, -math.pi / 2 + 0.05, rz)
        e.location = (x + 0.06 * s * math.cos(rz), y + 0.06 * s * math.sin(rz), 0.006)
    return {}


def caixa_crew(v):
    return {'key': v, 'label': 'Atendente ' + v, 'build': lambda P, root, v=v: build_carteiro(P, root, v), 'boost': CREW_BOOST,
            'margin': (0.06, 0.06, 0.08, 0.05),
            'pose0': lambda parts, P, root: pose_caixa(parts, P, root, 'idle', 0),
            'show': lambda parts, P, root: pose_caixa(parts, P, root, 'aim', 0),
            'modes': [(m, n, (lambda parts, P, root, f, m=m: pose_caixa(parts, P, root, m, f))) for m, n in (('idle', IDLE), ('aim', AIM), ('shoot', SHOOT))]}


def ballista_turret():
    modes = []
    for i in range(BAL_DIRS):
        modes.append((f'd{i:02d}', BAL_FRAMES, (lambda parts, P, root, f, i=i: pose_ballista(parts, P, root, yaw=TAU * i / BAL_DIRS, op_ph=f / BAL_FRAMES, **BAL_SEQ[f]))))
    return {'key': 'bal', 'label': 'Catapulta do Malote', 'build': build_ballista, 'boost': BAL_BOOST, 'margin': (0.08, 0.2, 0.1, 0.06),
            'pose0': lambda parts, P, root: pose_ballista(parts, P, root, yaw=math.radians(-30)), 'modes': modes, 'dirs': BAL_DIRS}


def still(key, label, fn, shadow=False):
    return {'key': key, 'label': label, 'build': fn, 'boost': PROJ_PX, 'pxk': PROJ_PX, 'shadow': shadow,
            'margin': (0.04, 0.12 if shadow else 0.04, 0.05, 0.04), 'modes': [('still', 1, lambda parts, P, root, f: None)]}


CREW_VARIANTS = ('a1', 'a2', 'a3', 'a3b')

SPEC = {
    'show_crew': {'n1': ['a1', 'a1'], 'n2': ['a2', 'a2'], 'n3': ['a3', 'a3b'], 'n4': ['bal']},
    'towers': [('n1', 'Carta ao Povo N1', tower('n1', build_n1)), ('n2', 'Carta ao Povo N2', tower('n2', build_n2)),
               ('n3', 'Carta ao Povo N3', tower('n3', build_n3)), ('n4', 'Malote', tower('n4', build_n4))],
    'crews': [caixa_crew(v) for v in CREW_VARIANTS],
    'turrets': [ballista_turret()],
    'stills': [still('flecha', 'Carta', build_flecha), still('virote', 'Malote', build_virote), still('cravada', 'Carta cravada', build_cravada, shadow=True)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
