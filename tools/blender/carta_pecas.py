"""Pecas comuns da torre Carta ao Povo Brasileiro (Ninguem Sobe a Rampa, so a chapa R): a mesma torre de concreto
branco de Brasilia do Mensalinho (fuste hiperbolico, cuia da Camara, colunas do Alvorada; a geometria vem de
mensalinho_pecas.py, que fica intacto), mas tudo o que era dinheiro vira correio: cartas brancas/creme com lacre
vermelho e estrela branca, macos de cartas amarrados com barbante vermelho, caixa de correio vermelha, malotes de lona
vermelha, caixa de cartas, bandeira-carta tremulando e a turma de camiseta vermelha com estrela branca e bone vermelho.
Usado por torre_carta.py (Carta ao Povo N1-N3 e Malote) e torre_carta_zb.py (Panfletagem). Nada de texto, numero,
logo, cedula ou dinheiro na arte.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, emblema, estrela, estrela_peito   # noqa: F401
from mensalinho_pecas import (TAPETE, lathe_arc, fuste, cuia, faixa_vidro, aleta, ipe, globo, estandarte_chapa,   # noqa: F401
                              bandeira_chapa, peito_chapa, oculos, bigode, _poly_into, caixa_state, pose_caixa, IDLE, AIM,
                              SHOOT, MIRA, HEAD_K)

HC = Vector((0.006, 0, 0.055))     # centro da cabeca no pivo do pescoco (lib.build_person)


# ---------------------------------------------------------------- materiais (concreto branco, correio e a chapa)
def mats_carta(P):
    P['concreto'] = mat('concreto_bsb', '#efebe2', rough=0.86, var=0.03, bump=0.1)
    P['concreto_s'] = mat('concreto_bsb_sombra', '#d6cfc0', rough=0.9, var=0.03, bump=0.12)
    P['vidro_v'] = mat('vidro_bsb', '#6d9f97', rough=0.12, var=0.02, bump=0.0)
    P['vidro_esc'] = mat('vidro_guiche', '#3f6a6c', rough=0.1, var=0.0, bump=0.0)
    P['tapete'] = mat('tapete_chapa_' + CHAPA, TAPETE[CHAPA], rough=0.95, var=0.03, bump=0.25, sheen=0.5)
    P['stripes'] = mat('toldo_chapa_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(14.0, PAL['sec'], PAL['pri']), sheen=0.4)
    P['chapa'] = cor('pri')        # vermelho: moldura, placa, caixa de cartas, faixa, caixa de correio
    P['chapa2'] = cor('sec')       # branco da estrela
    P['chapa3'] = cor('ter')       # vinho
    P['envelope'] = mat('carta_papel', '#fbf6e8', rough=0.85, var=0.03, bump=0.03, sheen=0.2)
    P['envelope_d'] = mat('carta_aba', '#e8dcbe', rough=0.85, var=0.02, bump=0.03)
    P['lacre'] = mat('lacre_vermelho', '#c4161c', rough=0.32, var=0.03, bump=0.06)
    P['estrela'] = cor('sec', rough=0.45)
    P['barbante'] = mat('barbante_vermelho', '#c8262b', rough=0.85, var=0.02, bump=0.1)
    P['malote'] = mat('malote_lona', '#cc2b2e', rough=0.92, var=0.04, bump=0.35, sheen=0.5)
    P['malote_esc'] = mat('malote_lona_esc', '#8f1a1d', rough=0.92, var=0.03, bump=0.3, sheen=0.4)
    P['cordao'] = mat('cordao_branco', '#f4efe2', rough=0.9, var=0.03, bump=0.3)
    P['panfleto'] = mat('panfleto_vermelho', '#dc2f33', rough=0.75, var=0.04, bump=0.03, sheen=0.2)
    P['panfleto_cl'] = mat('panfleto_creme', '#fbf6e8', rough=0.8, var=0.03, bump=0.03, sheen=0.2)
    P['camisa'] = cor('camisa')                                  # camiseta vermelha
    P['calca'] = cor('calca')                                    # jeans escuro
    P['bone'] = cor('bone')                                      # bone vermelho
    P['saia_v'] = cor('calca')
    P['sapato'] = mat('sapato_social', '#2b2320', rough=0.4, var=0.02, bump=0.02)
    P['cinto'] = mat('cinto_social', '#2e2522', rough=0.5, var=0.02, bump=0.02)
    P['lente'] = mat('oculos_aro', '#2a2a2e', rough=0.4, var=0.0, bump=0.0)
    P['oculos_esc'] = mat('oculos_escuros', '#1d1d22', rough=0.15, var=0.0, bump=0.0)
    P['cabelo_c'] = mat('cabelo_castanho', '#5a3a22', rough=0.7, var=0.03, bump=0.25)
    P['cabelo_p'] = mat('cabelo_preto', '#2b2220', rough=0.7, var=0.03, bump=0.25)
    P['cabelo_g'] = mat('cabelo_grisalho', '#8f8a84', rough=0.7, var=0.03, bump=0.25)
    P['ipe'] = mat('ipe_amarelo', '#f2c230', rough=0.85, var=0.1, bump=0.15, sheen=0.4)
    P['ipe_cl'] = mat('ipe_amarelo_cl', '#ffd95a', rough=0.85, var=0.08, bump=0.15, sheen=0.4)
    P['casca'] = mat('casca_ipe', '#6a4a36', rough=0.85, var=0.1, bump=0.4)
    P['lamp_q'] = glow_mat('lampada_correio', '#ffe2a8', 1.0, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['globo'] = glow_mat('globo_bsb', '#fff0cc', 0.8, 14.0, rough=0.3, var=0.0, bump=0.0)
    P['vime'] = mat('cesto_vime', '#d4ae6a', rough=0.9, var=0.08, bump=0.4)
    P['sandstone'] = P['concreto']
    P['sandstone_l'] = P['concreto']
    P['mortar'] = P['concreto_s']
    P['_emblem'] = 'coin'
    return P


# ---------------------------------------------------------------- correio
def estrelinha(root, name, P, r, parent, loc, rot=(0, 0, 0), depth=0.004):
    """Estrela branca de 5 pontas (placa fina no plano XZ, espessura em Y) presa no pivo `parent`."""
    e = estrela(root, name, r, depth, m=P['estrela'], bev=depth * 0.3)
    e.parent = parent
    e.location = loc
    e.rotation_euler = rot
    return e


def envelope(root, name, P, w=0.13, h=0.09, th=0.012, aba=True, selo=True):
    """Carta fechada no plano YZ (espessura em X, face para +X), base em z=0, centrada em Y: papel creme, aba em V
    e o lacre de cera vermelha com a estrela branca na ponta da aba. Devolve o pivo (empty) com tudo pendurado."""
    piv = empty(root, name)
    kids(piv, box(root, name + '_papel', (th, w, h), (0, 0, h / 2), m=P['envelope'], bev=min(0.006, th * 0.45)))
    if aba:
        bm = bmesh.new()
        tri = [(th / 2 + 0.0015, -w / 2 + 0.006, h - 0.005), (th / 2 + 0.0015, w / 2 - 0.006, h - 0.005), (th / 2 + 0.0015, 0.0, h * 0.4)]
        a = [bm.verts.new(p) for p in tri]
        b = [bm.verts.new((p[0] + 0.004, p[1], p[2])) for p in tri]
        bm.faces.new(a[::-1])
        bm.faces.new(b)
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        kids(piv, bm_to_obj(bm, name + '_aba', root, [P['envelope_d']], bev=0.0015, angle=30))
    if selo:
        rs = 0.17 * min(w, h)
        kids(piv, cyl(root, name + '_selo', rs, 0.007, (th / 2 + 0.0065, 0, h * 0.42), rot=(0, math.pi / 2, 0), m=P['lacre'], v=14, bev=0.0025))
        estrelinha(root, name + '_seloEstrela', P, rs * 0.72, piv, (th / 2 + 0.0105, 0, h * 0.42), rot=(0, 0, math.pi / 2), depth=0.003)
    return piv


def maco_cartas(root, name, P, loc, rz=0.0, s=1.0, n=3, seed=2):
    """Maco de cartas deitadas (n envelopes) amarrado com barbante vermelho, a de cima com o lacre para cima."""
    rr = random.Random(seed)
    x, y, z = loc
    piv = empty(root, name, loc=(x, y, z), rot=(0, 0, rz))
    L, W, T = 0.13 * s, 0.09 * s, 0.012 * s
    for k in range(n - 1):
        kids(piv, box(root, f'{name}_c{k}', (L, W, T), (rr.uniform(-0.006, 0.006) * s, rr.uniform(-0.005, 0.005) * s, T / 2 + T * k),
                      rot=(0, 0, rr.uniform(-0.08, 0.08)), m=P['envelope'], bev=T * 0.4))
    top = envelope(root, name + '_topo', P, w=W, h=L, th=T)
    top.parent = piv
    top.rotation_euler = (0, -math.pi / 2, 0)          # face para +Z, altura ao longo de -X
    top.location = (L / 2, 0, T * (n - 1) + T / 2)
    hz = T * n
    kids(piv, box(root, name + '_barbanteY', (0.008 * s, W + 0.006 * s, hz + 0.006 * s), (-0.04 * s, 0, hz / 2), m=P['barbante'], bev=0.002 * s),
         box(root, name + '_barbanteX', (L + 0.006 * s, 0.008 * s, hz + 0.006 * s), (0, 0.027 * s, hz / 2), m=P['barbante'], bev=0.002 * s),
         sphere(root, name + '_no', 0.011 * s, (-0.04 * s, 0.027 * s, hz + 0.006 * s), scale=(1.3, 1.0, 0.6), m=P['barbante'], seg=8))
    return piv


def pilha_cartas(root, tag, P, loc, n=2, s=1.0, rz=0.0, seed=1):
    """Macos de cartas empilhados (troca a pilha de dinheiro)."""
    rr = random.Random(seed)
    x, y, z = loc
    for k in range(n):
        maco_cartas(root, f'{tag}{k}', P, (x + rr.uniform(-0.01, 0.01) * s, y + rr.uniform(-0.01, 0.01) * s, z + 0.044 * s * k),
                    rz=rz + rr.uniform(-0.2, 0.2), s=s, seed=seed + k)


def caixa_cartas(root, P, tag, loc, rz=0.0, n=6, s=1.0, seed=5):
    """Caixa vermelha de correspondencia cheia de cartas em pe (a municao)."""
    rr = random.Random(seed)
    x, y, z = loc
    piv = empty(root, tag, loc=(x, y, z), rot=(0, 0, rz))
    kids(piv, box(root, tag + '_caixa', (0.2 * s, 0.16 * s, 0.1 * s), (0, 0, 0.05 * s), m=P['chapa'], bev=0.012 * s))
    estrelinha(root, tag + '_caixaEstrela', P, 0.032 * s, piv, (0, -0.0815 * s, 0.05 * s), depth=0.004)
    for k in range(n):
        e = envelope(root, f'{tag}_env{k}', P, w=0.12 * s, h=0.11 * s, th=0.012 * s, aba=(k == 0), selo=(k == 0))
        e.parent = piv
        e.location = (rr.uniform(-0.02, 0.02) * s, -0.055 * s + 0.11 * s * k / max(1, n - 1), 0.05 * s + rr.uniform(0.0, 0.025) * s)
        e.rotation_euler = (0, rr.uniform(-0.2, 0.05), -math.pi / 2 + rr.uniform(-0.15, 0.15))   # de frente para -Y, em fila
    return piv


def caixa_correio(root, P, tag, loc, s=1.0, rz=0.0):
    """Caixa de correio vermelha de coluna (cupula, anel branco, boca com uma carta entrando e a estrela branca)."""
    x, y, z = loc
    piv = empty(root, tag, loc=(x, y, z), rot=(0, 0, rz))
    R, H = 0.085 * s, 0.26 * s
    zb = 0.03 * s
    kids(piv, cyl(root, tag + '_base', 0.12 * s, zb, (0, 0, zb / 2), m=P['concreto_s'], v=24, bev=0.01 * s),
         cyl(root, tag + '_pe', R + 0.012 * s, 0.03 * s, (0, 0, zb + 0.015 * s), m=P['chapa3'], v=24, bev=0.008 * s),
         cyl(root, tag + '_corpo', R, H, (0, 0, zb + H / 2), m=P['chapa'], v=28, bev=0.012 * s),
         torus(root, tag + '_anel', (0, 0, zb + H - 0.004 * s), R + 0.004 * s, 0.011 * s, P['chapa2'], n=28, segs=6),
         sphere(root, tag + '_cupula', R + 0.008 * s, (0, 0, zb + H + 0.004 * s), scale=(1, 1, 0.62), m=P['chapa'], seg=20),
         sphere(root, tag + '_botao', 0.016 * s, (0, 0, zb + H + 0.06 * s), m=P['chapa2'], seg=10))
    zs = zb + H * 0.76
    kids(piv, box(root, tag + '_boca', (0.1 * s, 0.03 * s, 0.022 * s), (0, -R + 0.006 * s, zs), m=P['dark'], bev=0.004 * s),
         box(root, tag + '_bocaAba', (0.116 * s, 0.02 * s, 0.012 * s), (0, -R - 0.004 * s, zs + 0.018 * s), m=P['chapa2'], bev=0.004 * s))
    e = envelope(root, tag + '_carta', P, w=0.075 * s, h=0.065 * s, th=0.008 * s)
    e.parent = piv
    e.rotation_euler = (0, 0.2, -math.pi / 2)              # face para -Y (camera), metade dentro da boca
    e.location = (0.004 * s, -R + 0.004 * s, zs - 0.012 * s)
    estrelinha(root, tag + '_estrela', P, 0.034 * s, piv, (0, -R - 0.003 * s, zb + H * 0.4), depth=0.006)
    return piv


def malote(root, name, P, h=0.34, R=0.14, cartas=True, estrelas=(-1,), seed=4):
    """Malote de lona vermelha em pe (base em z=0): barriga redonda, pescoco franzido amarrado com cordao branco,
    boca em tufo com cartas aparecendo e estrela branca costurada na frente (lado -Y; estrelas=(-1, 1) nos dois)."""
    piv = empty(root, name)
    zn = 0.8 * h

    def fold(a, z):
        return 0.16 * math.sin(9 * a) * max(0.0, (z - 0.6 * h) / (0.4 * h)) ** 1.2
    prof = [(0.0, 0.0, 0.0), (0.02 * h, 0.55 * R, 0.5 * R), (0.12 * h, 0.92 * R, 0.84 * R), (0.36 * h, R, 0.9 * R), (0.58 * h, 0.9 * R, 0.82 * R),
            (0.72 * h, 0.55 * R, 0.5 * R), (zn, 0.27 * R, 0.25 * R), (0.88 * h, 0.36 * R, 0.33 * R), (0.97 * h, 0.5 * R, 0.46 * R), (h, 0.42 * R, 0.4 * R)]
    kids(piv, lathe(root, name + '_saco', prof, P['malote'], segs=20, wobble=fold, lv=2))
    kids(piv, torus(root, name + '_amarra', (0, 0, zn), 0.29 * R, 0.022 * R + 0.004, P['cordao'], n=16, segs=6))
    for k, sg in enumerate((-1, 1)):
        kids(piv, tube(root, f'{name}_ponta{k}', [(0.2 * R, sg * 0.18 * R, zn), (0.36 * R, sg * 0.3 * R, zn - 0.08 * h), (0.38 * R, sg * 0.36 * R, zn - 0.16 * h)],
                       0.012 * R + 0.003, P['cordao'], segs=6))
    for k, sg in enumerate(estrelas):
        estrelinha(root, f'{name}_estrela{k}', P, 0.38 * R, piv, (0, sg * (0.9 * R + 0.001), 0.36 * h), rot=(0, 0, 0 if sg < 0 else math.pi), depth=0.008)
    if cartas:
        rr = random.Random(seed)
        for k in range(2):
            e = envelope(root, f'{name}_carta{k}', P, w=0.55 * R, h=0.5 * R, th=0.006 + 0.02 * R, aba=(k == 0), selo=(k == 0))
            e.parent = piv
            e.location = ((k - 0.5) * 0.14 * R, -0.06 * R * (1 - k), 0.9 * h)
            e.rotation_euler = (rr.uniform(-0.2, 0.2), (k - 0.5) * 0.5, -math.pi / 2 + rr.uniform(-0.2, 0.2))
    return piv


def bandeira_carta(root, P, tag, x, y, z, size=0.42, h_pole=0.9):
    """Mastro com uma carta gigante tremulando (pano animado): papel creme com a borda e a aba em V marcadas e o lacre
    vermelho com a estrela branca no meio (dos dois lados)."""
    tube(root, tag + '_mastro', [(x, y, z), (x, y, z + h_pole)], 0.02, P['concreto_s'], segs=8)
    sphere(root, tag + '_topo', 0.035, (x, y, z + h_pole + 0.02), m=P['gold'], seg=12)
    hh = size * 0.62
    o = cloth_grid(root, tag + '_carta', size, hh, 16, 8, [P['envelope'], P['envelope_d'], P['lacre'], P['estrela']], thick=0.012)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    q = 0.03
    edge = [(q, -q), (size - q, -q), (size - q, -hh + q), (q, -hh + q)]
    tip = (size * 0.5, -hh * 0.56)
    for sy in (-0.009, 0.009):
        tube_into(bm, [(ex, sy, ez) for ex, ez in edge] + [(edge[0][0], sy, edge[0][1])], 0.007, segs=5, caps=True, mat_index=1)
        tube_into(bm, [(q + 0.01, sy, -q - 0.006), (tip[0], sy, tip[1]), (size - q - 0.01, sy, -q - 0.006)], 0.008, segs=5, caps=True, mat_index=1)
    rs = hh * 0.2
    for sy in (-1, 1):
        _poly_into(bm, [(tip[0] + rs * math.cos(a), tip[1] + rs * math.sin(a)) for a in [TAU * j / 20 for j in range(20)]], sy * 0.012, 2)
        r, ri = rs * 0.72, rs * 0.72 * 0.42
        _poly_into(bm, [(tip[0] + (r if i % 2 == 0 else ri) * math.cos(math.pi / 2 + i * math.pi / 5),
                         tip[1] + (r if i % 2 == 0 else ri) * math.sin(math.pi / 2 + i * math.pi / 5)) for i in range(10)], sy * 0.0175, 3)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o.location = (x + 0.02, y, z + h_pole - 0.04)
    register_cloth(o, flag_wave(size, amp=0.06, cycles=1, waves=1.1))
    return o


def guiche_correio(root, P, tag, y_body, z0=0.15, w=0.42, d=0.22, h=0.44, lamp=True, balcao='cartas'):
    """Guiche de agencia de correio na frente da torre: janela de vidro com grade de ouro, fenda de cartas com aba de
    latao, balcao com um maco de cartas (ou santinhos), toldo listrado da chapa e placa vermelha com a estrela branca.
    Devolve a posicao da lampada (luz quente)."""
    cy = y_body - d / 2 + 0.04
    yf = cy - d / 2
    box(root, tag + '_guiche', (w, d, h), (0, cy, z0 + h / 2), m=P['concreto'], bev=0.05, seg=4)
    box(root, tag + '_rodape', (w + 0.03, d + 0.03, 0.05), (0, cy, z0 + 0.025), m=P['concreto_s'], bev=0.015)
    zc = z0 + h * 0.62
    box(root, tag + '_janela', (w - 0.13, 0.03, h * 0.38), (0, yf + 0.006, zc), m=P['vidro_esc'], bev=0.006)
    pts = [(-(w - 0.13) / 2 - 0.012, yf - 0.006, zc - h * 0.19 - 0.012), (-(w - 0.13) / 2 - 0.012, yf - 0.006, zc + h * 0.19 + 0.012),
           ((w - 0.13) / 2 + 0.012, yf - 0.006, zc + h * 0.19 + 0.012), ((w - 0.13) / 2 + 0.012, yf - 0.006, zc - h * 0.19 - 0.012)]
    tube(root, tag + '_moldura', pts, 0.014, P['chapa'], segs=6, closed=True)
    for k in range(3):
        xx = -(w - 0.13) / 2 + (w - 0.13) * (k + 1) / 4
        tube(root, f'{tag}_grade{k}', [(xx, yf - 0.012, zc - h * 0.19), (xx, yf - 0.012, zc + h * 0.19)], 0.006, P['gold'], segs=6)
    # fenda de cartas (no lugar da boquinha do passa-dinheiro)
    box(root, tag + '_fenda', (0.1, 0.02, 0.022), (-0.06, yf - 0.002, zc - h * 0.19 - 0.006), m=P['dark'], bev=0.004)
    box(root, tag + '_fendaAba', (0.112, 0.012, 0.01), (-0.06, yf - 0.012, zc - h * 0.19 + 0.012), m=P['gold'], bev=0.003)
    zb = zc - h * 0.19 - 0.02
    box(root, tag + '_balcao', (w - 0.04, 0.11, 0.028), (0, yf - 0.045, zb), m=P['concreto'], bev=0.01)
    if balcao == 'cartas':
        maco_cartas(root, tag + '_maco', P, (0.09, yf - 0.05, zb + 0.014), rz=0.2, s=0.8, n=3)
    else:
        pilha_panfletos(root, tag + '_santinhos', P, (0.09, yf - 0.05, zb + 0.014), rz=0.2, s=0.8, n=4)
        pilha_panfletos(root, tag + '_santinhos2', P, (-0.1, yf - 0.05, zb + 0.014), rz=-0.3, s=0.7, n=3, seed=6)
    # toldo listrado inclinado com babado (listras e babado nas cores da chapa)
    zt = z0 + h + 0.01
    box(root, tag + '_toldo', (w + 0.06, 0.15, 0.02), (0, yf - 0.05, zt), rot=(math.radians(24), 0, 0), m=P['stripes'], bev=0.006)
    for k in range(7):
        xx = -(w + 0.06) / 2 + (w + 0.06) * (k + 0.5) / 7
        cyl(root, f'{tag}_babado{k}', (w + 0.06) / 14, 0.012, (xx, yf - 0.118, zt - 0.035), rot=(math.pi / 2, 0, 0),
            m=P['chapa'] if k % 2 == 0 else P['chapa2'], v=12, bev=0.002)
    zp = zt + 0.075
    box(root, tag + '_placa', (w * 0.7, 0.03, 0.1), (0, yf + 0.04, zp), m=P['chapa'], bev=0.012)
    emblema(root, tag + '_placaEmblema', w * 0.62, 0.1, loc=(0, yf + 0.0225, zp), depth=0.006)
    lp = None
    if lamp:
        lx, lz = w / 2 - 0.02, zp + 0.01
        tube(root, tag + '_bracoLamp', [(lx - 0.04, yf + 0.03, lz - 0.05), (lx + 0.03, yf - 0.03, lz - 0.05), (lx + 0.03, yf - 0.03, lz - 0.02)], 0.008, P['gold'], segs=6)
        sphere(root, tag + '_lampada', 0.032, (lx + 0.03, yf - 0.03, lz + 0.01), m=P['lamp_q'], seg=14)
        lp = (lx + 0.03, yf - 0.03, lz + 0.01)
    return lp


# ---------------------------------------------------------------- santinhos (panfletos de campanha, sem texto)
def panfleto(root, name, P, w=0.1, h=0.13, th=0.006, m=None, star_m=None):
    """Santinho dobrado em pe no plano XZ (espessura em Y, frente para -Y), base em z=0: papel vermelho com a estrela
    branca (ou creme com estrela vermelha) e o vinco da dobra no meio. Devolve o pivo."""
    piv = empty(root, name)
    m = m or P['panfleto']
    kids(piv, box(root, name + '_a', (w / 2, th, h), (-w / 4, 0, h / 2), rot=(0, 0, -0.1), m=m, bev=th * 0.4),
         box(root, name + '_b', (w / 2, th, h), (w / 4, 0, h / 2), rot=(0, 0, 0.1), m=m, bev=th * 0.4))
    estrelinha(root, name + '_estrela', P, min(w, h) * 0.3, piv, (0, -th / 2 - 0.025 * w - 0.002, h * 0.55), depth=0.004)
    if star_m is not None:
        bpy.data.objects[name + '_estrela'].data.materials[0] = star_m
    return piv


def pilha_panfletos(root, tag, P, loc, n=4, s=1.0, rz=0.0, seed=3):
    """Pilha de santinhos deitados (vermelhos e creme alternados) amarrada com cordao branco, estrela no de cima."""
    rr = random.Random(seed)
    x, y, z = loc
    piv = empty(root, tag, loc=(x, y, z), rot=(0, 0, rz))
    L, W, T = 0.11 * s, 0.08 * s, 0.01 * s
    for k in range(n):
        kids(piv, box(root, f'{tag}_f{k}', (L, W, T), (rr.uniform(-0.006, 0.006) * s, rr.uniform(-0.005, 0.005) * s, T / 2 + T * k),
                      rot=(0, 0, rr.uniform(-0.12, 0.12)), m=P['panfleto'] if k % 2 == 0 or k == n - 1 else P['panfleto_cl'], bev=T * 0.35))
    hz = T * n
    estrelinha(root, tag + '_estrela', P, 0.026 * s, piv, (0.012 * s, 0, hz + 0.001), rot=(-math.pi / 2, 0, 0), depth=0.003)
    kids(piv, box(root, tag + '_cordao', (0.007 * s, W + 0.006 * s, hz + 0.006 * s), (-0.034 * s, 0, hz / 2), m=P['cordao'], bev=0.002 * s))
    return piv


# ---------------------------------------------------------------- a turma (camiseta vermelha, estrela, bone vermelho)
def bone(root, pr, tag, m, botao=None):
    """Bone vermelho: copa justa na cabeca inclinada para tras, aba curta para a frente e o botao branco no topo."""
    hd = pr['head']
    c = lathe(root, tag + '_bone', [(0.0, 0.072, 0.07), (0.022, 0.069, 0.067), (0.042, 0.058, 0.056), (0.058, 0.036, 0.035), (0.066, 0.0, 0.0)],
              m, segs=18, lv=2, caps=False, solid=0.008)
    c.parent = hd
    c.location = HC + Vector((-0.004, 0, 0.018))
    c.rotation_euler = (0, -0.28, 0)
    o = cyl(root, tag + '_aba', 0.058, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = hd
    o.location = HC + Vector((0.074, 0, 0.044))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.16, 0)
    b = sphere(root, tag + '_boneBotao', 0.01, HC + Vector((-0.026, 0, 0.088)), m=botao or cor('sec', rough=0.45), seg=10)
    b.parent = hd
    # estrelinha branca na frente da copa
    e = estrela(root, tag + '_boneEstrela', 0.017, 0.004, m=cor('sec', rough=0.45), bev=0.001)
    e.parent = hd
    e.location = HC + Vector((0.057, 0, 0.064))
    e.rotation_euler = (-0.714, 0, math.pi / 2)           # deitada na frente da copa, ponta para cima
    return c


def cabelo_curto(root, pr, tag, m):
    """Cabelo curto aparecendo por baixo do bone: nuca e costeletas."""
    hd = pr['head']
    o = blob(root, f'{tag}_nuca', 0.042, HC + Vector((-0.034, 0, 0.006)), (0.85, 1.38, 0.95), m)
    o.parent = hd
    for s, yy in enumerate((-0.058, 0.058)):
        o = blob(root, f'{tag}_costeleta{s}', 0.019, HC + Vector((-0.002, yy, 0.014)), (1.1, 0.55, 1.25), m)
        o.parent = hd


def rabo_cavalo(root, pr, tag, m):
    """Rabo de cavalo saindo por tras do bone."""
    hd = pr['head']
    o = blob(root, f'{tag}_rabo', 0.026, HC + Vector((-0.078, 0, 0.026)), (1.0, 0.9, 1.0), m)
    o.parent = hd
    t = tube(root, f'{tag}_raboPonta', [HC + Vector((-0.083, 0, 0.028)), HC + Vector((-0.106, 0, -0.008)), HC + Vector((-0.1, 0, -0.055))], 0.02, m, segs=8,
             rfun=lambda t: 0.022 * (1 - t) + 0.006)
    t.parent = hd


def env_mao(root, P, parts, tag, side='R', s=1.0):
    """Carta na mao (eixo Z local da mao): o que vai ser arremessado."""
    e = envelope(root, f'{tag}_env{side}', P, w=0.14 * s, h=0.1 * s, th=0.012 * s)
    e.location = (0, 0, -0.014)
    e.rotation_euler = (0, 0, math.pi / 2)    # face para o lado da mao (aparece para a camera)
    hold(parts, side, e)
    return e


def leque(root, P, parts, tag, side='L', s=1.0):
    """Leque de tres cartas na outra mao (o estoque do arremessador)."""
    piv = empty(root, f'{tag}_leque')
    for k, ang in enumerate((-0.38, 0.0, 0.38)):
        e = envelope(root, f'{tag}_leque{k}', P, w=0.13 * s, h=0.095 * s, th=0.01 * s, selo=(k == 1))
        e.parent = piv
        e.location = (0.004 * (k - 1), 0, -0.012)
        e.rotation_euler = (ang, 0, 0)
    piv.rotation_euler = (0, 0, math.pi / 2)
    hold(parts, side, piv)
    return piv


SKINS = {'a1': '#d9a578', 'a2': '#a8714a', 'a3': '#e3b48c', 'a3b': '#8c5a3c', 'op': '#c98d5e'}


def build_carteiro(P, root, variant, tag=None):
    """Funcionario da agencia (~0.6 BU, cabecao): camiseta vermelha com estrela branca no peito, jeans escuro e bone
    vermelho; carta lacrada na mao direita e um leque de cartas na esquerda.
    a1: cabelo castanho; a2: cabelo preto e oculos; a3: grisalho de bigode; a3b: funcionaria de rabo de cavalo, saia e
    brincos de ouro; op: suspensorio (opera o Malote)."""
    tag = tag or root['set']
    hair = {'a1': P['cabelo_c'], 'a2': P['cabelo_p'], 'a3': P['cabelo_g'], 'a3b': P['cabelo_p'], 'op': P['cabelo_c']}[variant]
    skin = mat('pele_' + variant, SKINS[variant], rough=0.7, var=0.05, bump=0.02)
    sp = dict(skin=skin, tunic=P['camisa'], sleeve=P['camisa'], bracer=skin, skirt_m=P['saia_v'] if variant == 'a3b' else P['calca'],
              pants=P['calca'] if variant != 'a3b' else skin, boot_m=P['sapato'], boot_cuff=P['calca'] if variant != 'a3b' else P['sapato'],
              belt=P['cinto'] if variant != 'a3b' else None, buckle=P['gold'], head='hair' if variant == 'a3b' else 'bald', hair_m=hair,
              bare_hands=True)
    pr = build_person(P, root, tag, sp)
    pr['head'].scale = (HEAD_K, HEAD_K, HEAD_K)
    sa = bpy.data.objects.get(f'{tag}_saia')
    if sa and variant != 'a3b':
        sa.scale = (0.86, 0.86, 1.0)    # calca, nao tunica
    peito_chapa(root, P, pr, tag)       # estrela branca no peito
    bone(root, pr, tag, P['bone'])
    if variant == 'a3b':
        rabo_cavalo(root, pr, tag, hair)
        hd = pr['head']
        for s, yy in enumerate((-0.066, 0.066)):
            b = sphere(root, f'{tag}_brinco{s}', 0.009, Vector((0.006, yy, 0.03)), m=P['gold'], seg=8)
            b.parent = hd
    else:
        cabelo_curto(root, pr, tag, hair)
    if variant == 'op':
        for s, yy in enumerate((-0.05, 0.05)):
            o = tube(root, f'{tag}_suspensorio{s}', [(0.085, yy, 0.3), (0.09, yy * 1.1, 0.4), (0.05, yy * 1.3, 0.462), (-0.04, yy * 1.2, 0.46), (-0.085, yy * 0.8, 0.38),
                                                    (-0.085, yy * 0.6, 0.3)], 0.009, P['calca'], segs=6)
            o.parent = pr['body']
    if variant == 'a2':
        oculos(root, P, pr, tag)
    if variant == 'a3':
        bigode(root, P, pr, tag, P['cabelo_g'])
    if variant != 'op':
        env_mao(root, P, pr, tag, 'R')
        leque(root, P, pr, tag, 'L')
    pr['variant'] = variant
    return pr
