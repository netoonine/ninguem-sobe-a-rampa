"""Mensalinho (Ninguem Sobe a Rampa, motor 'archer', familia 'arqueiros'): niveis 1 a 3 e o Mensalao, no pipeline das
familias (tools/blender/lib.py). Torre de concreto branco modernista de Brasilia (fuste hiperbolico, colunas do
Alvorada e a cuia da Camara no alto, aberta), guiche de caixa na frente e dois funcionarios de viseira que
arremessam envelopes de dinheiro (conceito: arte/conceitos/torres/mensalinho.png). O Mensalao troca a dupla por uma
mala de dinheiro gigante que gira e cospe malas. Pecas comuns em tools/blender/mensalinho_pecas.py.
Mesmos conjuntos, postos, luzes e modos do Mirante dos Arqueiros do Guardioes da Mata (js/sprites.js depende deles).
Duas versoes, uma por chapa (tools/blender/chapa.py): faixa da cuia, guiche, estandartes, bandeirinha no parapeito,
tapete, adesivo da mala e a roupa da turma mudam de cor; enquadramento, postos e quadros sao os mesmos.

  Blender -b -P tools/blender/torre_arqueiros.py -- render arte/render/arqueiros [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_arqueiros.py -- render arte/render_r/arqueiros [conjuntos...]
  Blender -b -P tools/blender/torre_arqueiros.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_arqueiros.py -- crew <arquivo.png> [amostras] [show|pose0]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib as _lib
from mensalinho_pecas import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto de Brasilia (o mesmo das outras torres)

FAM = 'arqueiros'
BAL_BOOST = 1.12
BAL_DIRS, BAL_FRAMES = 16, 8
FRENTE = (-math.pi + 0.32, -0.32)   # angulos da frente (sin < -0.3): vao na camada da frente

_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811 - verde-dinheiro e concreto branco
    return mats_mensalinho(_orig_palette2())


_lib.palette2 = palette2


def bandeira_parapeito(root, P, tag, fz, R, rail, ang_deg, h=0.42):
    """Bandeirinha da chapa em pe no parapeito da cuia (lado direito, pano para fora). Angulo e altura escolhidos
    por nivel para nao passar do topo nem da direita do quadro atual (o enquadramento nao muda)."""
    a = math.radians(ang_deg)
    r = R - 0.0375
    bandeira_chapa(root, P, tag + '_bandeiraChapa', (r * math.cos(a), r * math.sin(a), fz + rail - 0.004), h=h)


def adesivo_chapa(root, P, name, parent, loc, w, h):
    """Adesivo da chapa colado na tampa da mala (face +Z do pivo `parent`): fundo na cor principal e o emblema."""
    b = box(root, name, (w, h, 0.003), (0, 0, 0), m=P['chapa'], bev=0.001)
    b.parent = parent
    b.location = loc
    for o in emblema(root, name + '_emblema', w * 0.9, h * 0.9, depth=0.003):
        if o.parent == root:
            o.parent = b
            o.location = (0, 0, 0.002)
            o.rotation_euler = (-math.pi / 2, 0, 0)    # plano XZ -> face para +Z
    return b


def na_frente(a):
    return math.sin(a) < -0.3


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


# ---------------------------------------------------------------- Mensalinho N1 a N3 e Mensalao
def build_n1(P, root):
    plot(root, P, 'n1')
    fz = 1.05
    corpo(root, P, 'n1', fz, 0.36, 0.27, 0.29, 0.6, 0.18, aletas=(math.radians(-38), math.radians(-142)), s_aleta=0.47, w_aleta=0.2)
    lamp = guiche(root, P, 'n1', -0.31, z0=0.18, w=0.38, d=0.22, h=0.4)
    canteiro_dinheiro(root, P, 'n1_canteiro', (0.56, -0.44, 0.15), s=0.95)
    bandeja_envelopes(root, P, 'n1_bandeja', (0.24, 0.3, fz), rz=0.3)
    pilha(root, 'n1_maco', P, (0.0, 0.42, fz), n=2, rz=0.4)
    nota_bandeira(root, P, 'n1_bandeira', -0.4, 0.36, fz, size=0.4, h_pole=0.82)
    bandeira_parapeito(root, P, 'n1', fz, 0.6, 0.18, 15, h=0.42)
    slots = [(-0.2, -0.12, fz + 0.01), (0.18, -0.14, fz + 0.01)]
    return {'slots': slots, 'lights': [(lamp, '#8affa6', 12.0, 1)]}


def build_n2(P, root):
    plot(root, P, 'n2')
    fz = 1.42
    a4 = [math.radians(a) for a in (-36, -144, 36, 144)]
    corpo(root, P, 'n2', fz, 0.4, 0.29, 0.31, 0.7, 0.2, vidro=0.17, aletas=a4, s_aleta=0.56, w_aleta=0.22, podio=0.54)
    lamp = guiche(root, P, 'n2', -0.35, z0=0.18, w=0.42, d=0.22, h=0.44)
    canteiro_dinheiro(root, P, 'n2_canteiro', (0.6, -0.42, 0.15))
    ipe(root, P, 'n2_ipe', (-0.62, -0.38, 0.15), s=0.8)
    bandeja_envelopes(root, P, 'n2_bandeja', (0.3, 0.34, fz), rz=0.3)
    pilha(root, 'n2_maco', P, (-0.34, 0.34, fz), n=3, rz=-0.3)
    lampada_banqueiro(root, P, 'n2_abajur', (0.02, 0.5, fz), rz=-1.2)
    bandeira_parapeito(root, P, 'n2', fz, 0.7, 0.2, 0, h=0.42)    # de lado: atras subiria o topo do quadro
    slots = [(-0.24, -0.16, fz + 0.01), (0.22, -0.18, fz + 0.01)]
    return {'slots': slots, 'lights': [(lamp, '#8affa6', 12.0, 1)]}


def build_n3(P, root):
    plot(root, P, 'n3')
    fz = 1.95
    a5 = [math.radians(a) for a in (-32, -148, 32, 148, 90)]
    corpo(root, P, 'n3', fz, 0.46, 0.33, 0.35, 0.82, 0.22, vidro=0.24, aletas=a5, s_aleta=0.66, w_aleta=0.26, podio=0.58, trim=P['gold'])
    guiche(root, P, 'n3', -0.42, z0=0.18, w=0.46, d=0.22, h=0.46)
    for k, x in enumerate((-0.42, 0.42)):
        estandarte_chapa(root, f'n3_estandarte{k}', P, x, -0.86, fz - 0.1, w=0.26, h=0.5)
    canteiro_dinheiro(root, P, 'n3_canteiro', (0.62, -0.44, 0.15))
    ipe(root, P, 'n3_ipe', (-0.66, -0.34, 0.15), s=1.0)
    bandeja_envelopes(root, P, 'n3_bandeja', (0.34, 0.38, fz), rz=0.3, n=7)
    pilha(root, 'n3_maco', P, (-0.1, 0.52, fz), n=3, rz=0.2)
    nota_bandeira(root, P, 'n3_bandeira', -0.5, 0.5, fz, size=0.48, h_pole=0.95)
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
    guiche(root, P, 'n4', -0.46, z0=0.18, w=0.48, d=0.22, h=0.46)
    for k, x in enumerate((-0.46, 0.46)):
        estandarte_chapa(root, f'n4_estandarte{k}', P, x, -0.92, fz - 0.1, w=0.26, h=0.5)
    # malas empilhadas no pe da torre (o Mensalao)
    for k, (x, y, z, rz) in enumerate(((0.62, -0.42, 0.15 + 0.07, 0.35), (0.6, -0.4, 0.15 + 0.21, 0.2), (0.7, -0.18, 0.15 + 0.07, 1.2))):
        m_ = mala(root, f'n4_malaPe{k}', P, w=0.3, h=0.14, d=0.22, alca=(k == 1), notas=(k == 1))
        m_.location = (x, y, z)
        m_.rotation_euler = (0, 0, rz)
    ipe(root, P, 'n4_ipe', (-0.68, -0.32, 0.15), s=1.0)
    pilha(root, 'n4_maco', P, (0.5, 0.5, fz), n=3, rz=0.5)
    pilha(root, 'n4_maco2', P, (0.62, 0.3, fz), n=2, rz=-0.2)
    nota_bandeira(root, P, 'n4_bandeira', -0.56, 0.52, fz, size=0.48, h_pole=0.95)
    bandeira_parapeito(root, P, 'n4', fz, 0.88, 0.2, 35, h=0.5)
    lights = []
    for k, a in enumerate((-0.22, math.pi + 0.22)):
        r = 0.88 - 0.04
        lights.append((globo(root, P, f'n4_poste{k}', r * math.cos(a), r * math.sin(a), fz + 0.18, h=0.18), '#ffd896', 16.0, 1))
    slots = [(0.0, 0.0, fz)]   # pivo da mala giratoria
    return {'slots': slots, 'lights': lights}


# ---------------------------------------------------------------- Mensalao: a mala gigante que gira e cospe malas
OP_O, OP_F = (-0.39, -0.3, 0.065), 0.25     # operador (local ao pivo) e para onde olha
ALAV = (-0.2, -0.25, 0.07)                   # pe da alavanca (local ao recuo)
ALAV_L = 0.32


def vis(o, on):
    for c in [o] + list(o.children_recursive):
        c.hide_render = c.hide_viewport = not on


def build_ballista(P, root):
    tag = 'bal'
    piv = empty(root, 'bal_pivo')
    rec = empty(root, 'bal_recuo', parent=piv)
    parts = {'pivot': piv, 'recoil': rec}

    def p(o, par=rec):
        o.parent = par
        return o
    # prato giratorio de concreto com aro de ouro e tapete verde
    p(cyl(root, 'bal_prato', 0.36, 0.06, (0, 0, 0.03), m=P['concreto'], v=40, bev=0.015), piv)
    p(torus(root, 'bal_pratoAro', (0, 0, 0.056), 0.352, 0.016, P['gold'], n=40, segs=6), piv)
    p(cyl(root, 'bal_pratoVerde', 0.27, 0.012, (0, 0, 0.064), m=P['tapete'], v=40, bev=0.004), piv)
    # pedestal redondo (fica escondido debaixo da mala)
    p(cyl(root, 'bal_pedestal', 0.13, 0.1, (0, 0, 0.11), r2=0.09, m=P['concreto_s'], v=24, bev=0.02))
    # a mala grande deitada, mirando +X um pouco para cima; a tampa abre como uma boca
    mb = empty(root, 'bal_malaPivo', loc=(0.05, 0, 0.21), parent=rec, rot=(0, -0.12, 0))
    mb.scale = (1.22, 1.22, 1.22)     # mala grande: e ela que da nome ao Mensalao
    L, W, H = 0.66, 0.38, 0.13
    x0 = -0.29
    kids(mb, box(root, 'bal_malaBaixo', (L, W, H), (x0 + L / 2, 0, 0.0), m=P['mala'], bev=0.04, seg=4),
         box(root, 'bal_dinheiro', (L - 0.07, W - 0.07, 0.03), (x0 + L / 2, 0, H / 2 + 0.005), m=P['nota'], bev=0.01))
    rr = random.Random(4)
    for k in range(7):
        x = x0 + 0.1 + (L - 0.2) * rr.random()
        y = rr.uniform(-0.12, 0.12)
        rz = rr.uniform(-0.6, 0.6)
        kids(mb, box(root, f'bal_maco{k}', (0.12, 0.06, 0.03), (x, y, H / 2 + 0.03), rot=(0, 0, rz), m=P['nota'] if k % 2 else P['nota_esc'], bev=0.006),
             box(root, f'bal_macoCinta{k}', (0.026, 0.064, 0.034), (x, y, H / 2 + 0.03), rot=(0, 0, rz), m=P['cinta'], bev=0.004))
    for k, x in enumerate((x0 + 0.16, x0 + L - 0.16)):
        kids(mb, box(root, f'bal_cinta{k}', (0.05, W + 0.014, H + 0.014), (x, 0, 0), m=P['mala_esc'], bev=0.008))
    for sx in (0, 1):
        for sy in (-1, 1):
            kids(mb, sphere(root, f'bal_canto{sx}{sy}', 0.034, (x0 + L * sx, sy * W / 2, -H / 2 + 0.01), m=P['gold'], seg=10))
    for sy in (-1, 1):
        kids(mb, box(root, f'bal_fecho{sy}', (0.03, 0.05, 0.05), (x0 + L + 0.005, sy * 0.1, H / 2 - 0.01), m=P['gold'], bev=0.006))
    kids(mb, tube(root, 'bal_alca', [(-0.06, -W / 2, -0.01), (-0.05, -W / 2 - 0.06, -0.01), (0.09, -W / 2 - 0.06, -0.01), (0.1, -W / 2, -0.01)], 0.016, P['mala_esc'], segs=8))
    lid = empty(root, 'bal_tampaPivo', loc=(x0, 0, H / 2), parent=mb)
    kids(lid, box(root, 'bal_tampa', (L, W, 0.1), (L / 2, 0, 0.05), m=P['mala'], bev=0.04, seg=4),
         box(root, 'bal_forro', (L - 0.05, W - 0.05, 0.014), (L / 2, 0, -0.004), m=P['forro'], bev=0.005),
         box(root, 'bal_tampaCinta0', (0.05, W + 0.014, 0.114), (0.16, 0, 0.05), m=P['mala_esc'], bev=0.008),
         box(root, 'bal_tampaCinta1', (0.05, W + 0.014, 0.114), (L - 0.16, 0, 0.05), m=P['mala_esc'], bev=0.008))
    for sy in (-1, 1):
        kids(lid, sphere(root, f'bal_tampaCanto{sy}', 0.034, (L, sy * W / 2, 0.08), m=P['gold'], seg=10))
    parts['lid'] = lid
    adesivo_chapa(root, P, 'bal_adesivo', lid, (L / 2, 0, 0.1), 0.22, 0.15)
    # a malinha (projetil) pronta na boca da mala
    mal = mala(root, 'bal_malinha', P, w=0.22, h=0.16, d=0.085, notas=False)
    mal.parent = mb
    parts['malinha'] = mal
    # estouro de notas no disparo
    bills = []
    for k in range(6):
        b = box(root, f'bal_estouro{k}', (0.11, 0.055, 0.006), (0, 0, 0), m=P['nota'] if k % 2 else P['nota_esc'], bev=0.002)
        b.parent = rec
        bills.append(b)
    parts['bills'] = bills
    # alavanca de ouro com bola verde (o operador puxa na recarga)
    lev = empty(root, 'bal_alavancaPivo', loc=ALAV, parent=rec)
    kids(lev, tube(root, 'bal_alavanca', [(0, 0, 0), (0, 0, ALAV_L)], 0.014, P['gold'], segs=8),
         sphere(root, 'bal_alavancaBola', 0.034, (0, 0, ALAV_L + 0.01), m=P['chapa'], seg=12))
    p(cyl(root, 'bal_alavancaBase', 0.045, 0.04, (ALAV[0], ALAV[1], ALAV[2] - 0.0), m=P['gold'], v=14, bev=0.008))
    parts['lever'] = lev
    # operador (gira junto)
    op = build_funcionario(P, root, 'op', tag='balop')
    op['body'].parent = piv
    parts['op'] = op
    return parts


def pose_ballista(parts, P, root, yaw, draw=1.0, recoil=0.0, bolt=True, op_ph=0.0):
    parts['pivot'].rotation_euler = (0, 0, yaw)
    parts['recoil'].location = (-0.06 * recoil, 0, 0)
    parts['lid'].rotation_euler = (0, -(0.62 + 0.36 * (1 - draw)), 0)
    mal = parts['malinha']
    mal.location = (0.18, 0, 0.065 + 0.075 - 0.14 * (1 - draw))
    vis(mal, bolt or draw >= 0.45)
    e = 1.0 - recoil
    rr = random.Random(9)
    for k, b in enumerate(parts['bills']):
        a = (k - 2.5) * 0.42
        d = 0.5 + 0.06 * (k % 3) + 0.32 * e
        b.location = (d * math.cos(a * 0.5), 0.07 * (k - 2.5) * (1 + 1.6 * e), 0.36 + 0.06 * (k % 2) + 0.12 * e - 0.25 * e * e)
        b.rotation_euler = (rr.uniform(-1.2, 1.2), rr.uniform(-0.8, 0.8), rr.uniform(0, 3))
        b.hide_render = b.hide_viewport = recoil < 0.5
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


BAL_SEQ = [  # disparo: a tampa escancara e cospe a malinha, a mala recua, assenta, o operador puxa a alavanca e sobe outra
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
def env_voo(root, P, name, L=0.32, Hh=0.2, th=0.024):
    """Envelope deitado ao longo de +X, face para a camera: aba em seta para a frente, notas saindo pela borda de tras."""
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
    m_ = mala(root, 'vi_mala', P, w=0.44, h=0.32, d=0.14, notas_em='z')
    m_.parent = piv
    m_.rotation_euler = (0, math.pi / 2, 0)    # alca na frente do voo, notas escapando atras
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
    nota(root, 'cr_nota0', P, (0.16, -0.06, 0.006), rot=(0.06, 0.04, 0.5))
    nota(root, 'cr_nota1', P, (-0.14, 0.03, 0.006), rot=(-0.05, 0.03, -0.7), m=P['nota_esc'])
    return {}


def caixa_crew(v):
    return {'key': v, 'label': 'Caixa ' + v, 'build': lambda P, root, v=v: build_funcionario(P, root, v), 'boost': CREW_BOOST,
            'margin': (0.06, 0.06, 0.08, 0.05),
            'pose0': lambda parts, P, root: pose_caixa(parts, P, root, 'idle', 0),
            'show': lambda parts, P, root: pose_caixa(parts, P, root, 'aim', 0),
            'modes': [(m, n, (lambda parts, P, root, f, m=m: pose_caixa(parts, P, root, m, f))) for m, n in (('idle', IDLE), ('aim', AIM), ('shoot', SHOOT))]}


def ballista_turret():
    modes = []
    for i in range(BAL_DIRS):
        modes.append((f'd{i:02d}', BAL_FRAMES, (lambda parts, P, root, f, i=i: pose_ballista(parts, P, root, yaw=TAU * i / BAL_DIRS, op_ph=f / BAL_FRAMES, **BAL_SEQ[f]))))
    return {'key': 'bal', 'label': 'Mala do Mensalao', 'build': build_ballista, 'boost': BAL_BOOST, 'margin': (0.08, 0.2, 0.1, 0.06),
            'pose0': lambda parts, P, root: pose_ballista(parts, P, root, yaw=math.radians(-30)), 'modes': modes, 'dirs': BAL_DIRS}


def still(key, label, fn, shadow=False):
    return {'key': key, 'label': label, 'build': fn, 'boost': PROJ_PX, 'pxk': PROJ_PX, 'shadow': shadow,
            'margin': (0.04, 0.12 if shadow else 0.04, 0.05, 0.04), 'modes': [('still', 1, lambda parts, P, root, f: None)]}


CREW_VARIANTS = ('a1', 'a2', 'a3', 'a3b')

SPEC = {
    'show_crew': {'n1': ['a1', 'a1'], 'n2': ['a2', 'a2'], 'n3': ['a3', 'a3b'], 'n4': ['bal']},
    'towers': [('n1', 'Mensalinho N1', tower('n1', build_n1)), ('n2', 'Mensalinho N2', tower('n2', build_n2)), ('n3', 'Mensalinho N3', tower('n3', build_n3)),
               ('n4', 'Mensalao', tower('n4', build_n4))],
    'crews': [caixa_crew(v) for v in CREW_VARIANTS],
    'turrets': [ballista_turret()],
    'stills': [still('flecha', 'Envelope', build_flecha), still('virote', 'Mala', build_virote), still('cravada', 'Envelope caido', build_cravada, shadow=True)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
