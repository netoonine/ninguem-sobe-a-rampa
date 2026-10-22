"""Candidatura Laranja (especializacao do Laranjal, Ninguem Sobe a Rampa; motor 'archer' spec 'blowgun', familia
'zarabatana', SO A CHAPA V): uma laranja gigante sorridente vestida de candidata (faixa da chapa atravessada no peito,
medalha, luvinhas brancas, acenando) num palanque de madeira com faixa verde e amarela, e dois apoiadores de camisa
amarela e bone verde que cospem caroco de laranja por um canudo comprido listrado (mesmo papel e mesmos quadros da
Zarabatana). Substitui, so na chapa V, o Dolar na Cueca (a chapa R continua com tools/blender/torre_zarabatana.py).
Mesmos conjuntos, postos, luzes e pontos da Zarabatana (js/sprites.js depende deles). Pecas em laranjal_pecas.py.

  CHAPA=V Blender -b -P tools/blender/torre_laranjal_zb.py -- render arte/render/zarabatana [conjuntos...]
  CHAPA=V Blender -b -P tools/blender/torre_laranjal_zb.py -- still <arquivo.png> [amostras]
  CHAPA=V Blender -b -P tools/blender/torre_laranjal_zb.py -- crew <arquivo.png> [amostras] [show|pose0]
NAO renderize com CHAPA=R (a pasta arte/render_r/zarabatana e do Dolar na Cueca).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib as _lib
from laranjal_pecas import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto de Brasilia (o mesmo das outras torres)

FAM = 'zarabatana'

_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811
    return mats_laranjal(_orig_palette2())


_lib.palette2 = palette2


# ---------------------------------------------------------------- adesivos que seguem a curva da laranja gigante
def decal(root, name, R, x0, x1, zfun, m, lift=0.004, thick=0.007, nx=14, nz=6, parent=None):
    """Remendo fino colado na esfera de raio R (face para -Y, coordenadas locais do pivo do rosto): para cada x em
    [x0, x1], zfun(x) da o trecho (z0, z1) coberto. Serve para olhos, boca, bochechas e sobrancelhas."""
    bm = bmesh.new()
    rows = []
    rr = R + lift
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * (0.002 + 0.996 * i / nx)
        z0, z1 = zfun(x)
        col = []
        for j in range(nz + 1):
            z = z0 + (z1 - z0) * j / nz
            y = -math.sqrt(max(1e-6, rr * rr - x * x - z * z))
            col.append(bm.verts.new((x, y, z)))
        rows.append(col)
    for i in range(nx):
        for j in range(nz):
            bm.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, name, root, [m], angle=80)
    if thick:
        sm = o.modifiers.new('Espessura', 'SOLIDIFY')
        sm.thickness = thick
        sm.offset = 0
    if parent is not None:
        o.parent = parent
    return o


def elipse(cx, cz, hx, hz):
    return lambda x: (cz - hz * math.sqrt(max(0.0, 1 - ((x - cx) / hx) ** 2)), cz + hz * math.sqrt(max(0.0, 1 - ((x - cx) / hx) ** 2)))


def no_rosto(R, x, z, out=0.0):
    """Ponto na superficie da esfera (local do rosto) e a normal."""
    y = -math.sqrt(max(1e-6, R * R - x * x - z * z))
    n = Vector((x, y, z)).normalized()
    return n * (R + out), n


def laranja_candidata(root, P, tag, c, R=0.4):
    """A Candidatura Laranja: laranja gigante de casca com poros, cabinho com duas folhas de topete, olhos grandes de
    brilho, bochechas, sorrisao de campanha, faixa da chapa atravessada com medalha de ouro, luvinhas brancas (uma
    acenando: pivo animado) e pezinhos de sapato. c = centro da laranja."""
    cx, cy, cz = c
    body = laranja(root, P, tag + '_corpo', R, c, seg=40)
    for o in body.children:      # o calice padrao some dentro do cabinho
        o.scale = (1.6, 1.6, 1.6)
    tube(root, tag + '_cabinho', [(cx, cy, cz + R * 0.9), (cx - 0.01, cy, cz + R * 0.98 + 0.04), (cx - 0.03, cy + 0.01, cz + R + 0.07)], 0.018, P['casca'], segs=8)
    folha(root, P, tag + '_topete0', 0.22, (cx - 0.1, cy - 0.02, cz + R + 0.045), rot=(0.25, -0.3, math.radians(160)))
    folha(root, P, tag + '_topete1', 0.17, (cx + 0.06, cy + 0.02, cz + R + 0.045), rot=(-0.2, -0.4, math.radians(30)), m=P['folha_cl'])
    # rosto: pivo no centro, frente (-Y) inclinada para a camera
    face = empty(root, tag + '_rosto', loc=c, rot=(-0.36, 0, 0))
    for s, ex in enumerate((-0.12, 0.12)):
        decal(root, f'{tag}_olho{s}', R, ex - 0.052, ex + 0.052, elipse(ex, 0.09, 0.052, 0.075), P['eye'], parent=face, nz=8)
        decal(root, f'{tag}_brilho{s}', R, ex - 0.034, ex - 0.006, elipse(ex - 0.02, 0.122, 0.014, 0.02), P['olho_br'], lift=0.009, parent=face, nx=6, nz=4)
        decal(root, f'{tag}_brilhoB{s}', R, ex + 0.014, ex + 0.028, elipse(ex + 0.021, 0.06, 0.007, 0.01), P['olho_br'], lift=0.009, parent=face, nx=4, nz=3)
        decal(root, f'{tag}_sobrancelha{s}', R, ex - 0.05, ex + 0.05,
              (lambda x, ex=ex: (0.2 + 0.028 * (1 - ((x - ex) / 0.05) ** 2), 0.218 + 0.03 * (1 - ((x - ex) / 0.05) ** 2))), P['boca'], parent=face, nz=2)
        decal(root, f'{tag}_bochecha{s}', R, ex * 1.75 - 0.05, ex * 1.75 + 0.05, elipse(ex * 1.75, -0.01, 0.05, 0.032), P['bochecha'], lift=0.002, parent=face, nz=5)
    # sorrisao em D: borda de cima reta (levemente curva), de baixo em arco; dentes em cima e lingua embaixo
    W, top, deep = 0.15, -0.04, 0.12
    lip = lambda x: top + 0.025 * (x / W) ** 2
    decal(root, tag + '_boca', R, -W, W, lambda x: (lip(x) - deep * math.sqrt(max(0.0, 1 - (x / W) ** 2)), lip(x)), P['boca'], parent=face, nx=18, nz=6)
    Wd = W * 0.84
    decal(root, tag + '_dentes', R, -Wd, Wd, lambda x: (lip(x) - 0.03, lip(x) - 0.004), P['dente'], lift=0.008, parent=face, nx=12, nz=2)
    Wl = W * 0.5
    decal(root, tag + '_lingua', R, -Wl, Wl, lambda x: (top - deep + 0.012, top - deep + 0.012 + 0.05 * math.sqrt(max(0.0, 1 - (x / Wl) ** 2))), P['lingua'],
          lift=0.008, parent=face, nx=10, nz=3)
    # faixa da chapa atravessada (do ombro esquerdo dela ao quadril direito), com filetes amarelos e medalha de ouro
    sash = empty(root, tag + '_faixaPivo', loc=c, rot=(0.2, 0.62, 0.0))
    d = -0.16

    def band(name, z0, z1, m, out):
        prof = []
        for k in range(4):
            z = z0 + (z1 - z0) * k / 3
            r = math.sqrt(max(1e-6, R * R - z * z)) + out
            prof.append((z, r, r))
        o = lathe(root, name, prof, m, segs=48, caps=False, lv=1, solid=0.008)
        o.parent = sash
        return o
    band(tag + '_faixa', d - 0.055, d + 0.055, P['chapa'], 0.007)
    band(tag + '_faixaFiletA', d + 0.05, d + 0.068, P['chapa2'], 0.01)
    band(tag + '_faixaFiletB', d - 0.068, d - 0.05, P['chapa2'], 0.01)
    # medalha (roseta) na faixa, do lado de baixo-direito do rosto
    mpos, mn = no_rosto(R, 0.19, -0.26, out=0.012)
    med = empty(root, tag + '_medalhaPivo', parent=face)
    med.location = mpos
    med.rotation_euler = mn.to_track_quat('-Y', 'Z').to_euler()
    kids(med, cyl(root, tag + '_medalhaFita', 0.05, 0.012, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['chapa3'], v=16, bev=0.003),
         cyl(root, tag + '_medalha', 0.035, 0.016, (0, -0.008, 0), rot=(math.pi / 2, 0, 0), m=P['gold'], v=16, bev=0.004))
    for k, a in enumerate((-0.35, 0.35)):
        kids(med, box(root, f'{tag}_medalhaPonta{k}', (0.026, 0.008, 0.06), (0.02 * math.sin(a), 0.004, -0.05), rot=(0, a, 0), m=P['chapa3'], bev=0.003))
    # bracinhos: o esquerdo (lado da camera a esquerda) acena; o direito faz joinha
    sh = (cx - R * 0.93, cy - 0.08, cz - 0.02)
    arm = empty(root, tag + '_bracoAceno', loc=sh)
    kids(arm, tube(root, tag + '_bracoA', [(0, 0, 0), (-0.09, -0.02, 0.07), (-0.13, -0.04, 0.17)], 0.034, P['laranja_esc'], segs=10),
         blob(root, tag + '_luvaA', 0.064, (-0.145, -0.05, 0.235), (0.8, 0.55, 1.0), P['luva']),
         blob(root, tag + '_dedaoA', 0.024, (-0.095, -0.07, 0.21), (1, 0.8, 1.3), P['luva']),
         torus(root, tag + '_punhoA', (-0.137, -0.045, 0.18), 0.04, 0.015, P['luva'], n=14, segs=5))
    def aceno(o, mb, ph):
        o.matrix_basis = mb @ Matrix.Rotation(0.32 * math.sin(TAU * ph * 2), 4, Vector((0.0, -1.0, 0.25)).normalized())
    register_anim(arm, aceno)
    sh2 = (cx + R * 0.93, cy - 0.08, cz - 0.04)
    tube(root, tag + '_bracoB', [sh2, (sh2[0] + 0.1, sh2[1] - 0.04, sh2[2] - 0.04), (sh2[0] + 0.12, sh2[1] - 0.1, sh2[2] + 0.04)], 0.034, P['laranja_esc'], segs=10)
    hb = (sh2[0] + 0.12, sh2[1] - 0.12, sh2[2] + 0.09)
    blob(root, tag + '_luvaB', 0.056, hb, (0.9, 0.8, 0.85), P['luva'])
    blob(root, tag + '_joinha', 0.022, (hb[0] - 0.005, hb[1] - 0.012, hb[2] + 0.062), (1, 1, 1.6), P['luva'])
    torus(root, tag + '_punhoB', (sh2[0] + 0.12, sh2[1] - 0.1, sh2[2] + 0.035), 0.038, 0.014, P['luva'], n=14, segs=5)
    # pezinhos
    for s, sx in enumerate((-1, 1)):
        top_ = (cx + sx * 0.11, cy - 0.04, cz - R * 0.9)
        bot = (cx + sx * 0.13, cy - 0.06, cz - R - 0.06)
        tube(root, f'{tag}_perna{s}', [top_, bot], 0.024, P['laranja_esc'], segs=8)
        blob(root, f'{tag}_sapato{s}', 0.05, (bot[0] + sx * 0.01, bot[1] - 0.035, bot[2] - 0.012), (1.0, 1.45, 0.6), P['dark'])
    return body


def canudo(root, P, tag, z0=-0.32, z1=0.1, r=0.013, n=11):
    """Canudo comprido listrado (branco e verde) ao longo do Z local da mao, com sanfoninha perto da boca."""
    out = []
    for k in range(n):
        a = z0 + (z1 - z0) * k / n
        b = z0 + (z1 - z0) * (k + 1) / n
        out.append(tube(root, f'{tag}_canudo{k}', [(0, 0, a), (0, 0, b)], r, P['canudo'] if k % 2 == 0 else P['chapa'], segs=10))
    for k in range(3):
        out.append(torus(root, f'{tag}_sanfona{k}', (0, 0, z1 - 0.07 + 0.018 * k), r * 1.05, 0.0045, P['canudo'], n=12, segs=4))
    return out


def sementes(root, P, tag, z_bico=-0.32):
    """Carocos de laranja saindo pela ponta do canudo (so no sopro)."""
    out = []
    for k, (dz, dx, dy) in enumerate(((-0.025, 0.0, 0.0), (-0.055, 0.01, -0.006), (-0.085, -0.008, 0.008))):
        out.append(sphere(root, f'{tag}_semente{k}', 0.011, (dx, dy, z_bico + dz), scale=(0.8, 0.8, 1.5), m=P['semente'], seg=8))
    return out


def palanque(root, P, fz, zf):
    """Palanque de madeira com saia verde de babado amarelo, piso de tabuas e guarda-corpo; a frente do guarda-corpo
    (com a faixa da chapa) vai na camada da frente."""
    z0 = G
    box(root, 'zb_rodape', (0.98, 0.76, 0.06), (0, 0.04, z0 + 0.03), m=P['madeira'], bev=0.02)
    hb = fz - 0.035 - (z0 + 0.06)
    box(root, 'zb_corpo', (0.9, 0.68, hb), (0, 0.06, z0 + 0.06 + hb / 2), m=P['deck'], bev=0.02)
    for k, x in enumerate((-0.44, 0.44)):
        box(root, f'zb_pilar{k}', (0.07, 0.07, hb + 0.02), (x, -0.27, z0 + 0.06 + hb / 2), m=P['madeira'], bev=0.012)
    box(root, 'zb_laje', (1.1, 0.88, 0.07), (0, 0.04, fz), m=P['madeira'], bev=0.02)
    box(root, 'zb_piso', (1.02, 0.8, 0.02), (0, 0.04, zf - 0.01), m=P['deck'], bev=0.006)
    # saia de pano verde com o emblema e babado amarelo/verde
    yf = 0.04 - 0.44 - 0.006
    hs = 0.24
    box(root, 'zb_saia', (1.08, 0.014, hs), (0, yf, fz - 0.035 - hs / 2), m=P['chapa'], bev=0.004)
    emblema(root, 'zb_saiaEmblema', 0.34, hs * 0.85, loc=(0, yf - 0.01, fz - 0.035 - hs / 2), depth=0.008)
    nb = 12
    for i in range(nb):
        xx = -0.54 + 1.08 * (i + 0.5) / nb
        cyl(root, f'zb_babado{i}', 1.08 / (2 * nb), 0.012, (xx, yf - 0.002, fz - 0.035 - hs), rot=(math.pi / 2, 0, 0), m=P['chapa2'] if i % 2 == 0 else P['chapa'],
            v=12, bev=0.002)
    # guarda-corpo de madeira: fundo e lados na base; a frente (mais baixa, com a faixa) na camada da frente
    for k, (sx, sy, lx, ly, fr) in enumerate(((0, 0.45, 1.06, 0.05, False), (-0.52, 0.04, 0.05, 0.84, False), (0.52, 0.04, 0.05, 0.84, False),
                                              (0, -0.37, 1.06, 0.05, True))):
        hh = 0.12 if fr else 0.16
        box(root, f'zb_corrimao{k}', (lx + 0.02, ly + 0.02, 0.03), (sx, sy, zf + hh), m=P['madeira_cl'], bev=0.01, front=fr)
        n = 6 if lx > ly else 5
        for j in range(n):
            t = j / (n - 1)
            px = sx - lx / 2 + 0.02 + (lx - 0.04) * t if lx > ly else sx
            py = sy if lx > ly else sy - ly / 2 + 0.02 + (ly - 0.04) * t
            box(root, f'zb_balaustre{k}_{j}', (0.035, 0.035, hh), (px, py, zf + hh / 2), m=P['madeira'], bev=0.008, front=fr)
    # faixa da chapa amarrada na frente do guarda-corpo (sem letras)
    box(root, 'zb_faixaFrente', (0.84, 0.012, 0.085), (0, -0.4, zf + 0.07), m=P['chapa'], bev=0.003, front=True)
    for k, zz in enumerate((zf + 0.11, zf + 0.03)):
        tube(root, f'zb_faixaFilete{k}', [(-0.42, -0.408, zz), (0.42, -0.408, zz)], 0.006, P['chapa2'], segs=6, front=True)
    for o in emblema(root, 'zb_faixaEmblema', 0.2, 0.075, loc=(0, -0.41, zf + 0.07), depth=0.006):
        o['front'] = 1
        for ch in o.children:
            ch['front'] = 1


def build_zb(P, root):
    plot(root, P, 'zb')
    fz = 1.06
    zf = fz + 0.035                     # piso do palanque (os postos ficam aqui)
    palanque(root, P, fz, zf)
    # a candidata: pedestal redondo verde e a laranja gigante sorridente
    hp = 0.22
    cyl(root, 'zb_pedestal', 0.23, hp, (0, 0.3, zf + hp / 2), r2=0.2, m=P['chapa'], v=36, bev=0.02)
    torus(root, 'zb_pedestalAro', (0, 0.3, zf + hp), 0.205, 0.016, P['chapa2'], n=36, segs=6)
    torus(root, 'zb_pedestalAroB', (0, 0.3, zf + 0.03), 0.232, 0.014, P['chapa2'], n=36, segs=6)
    R = 0.4
    laranja_candidata(root, P, 'zb_candidata', (0, 0.32, zf + hp + 0.07 + R * 0.94), R=R)
    # postes de lampiao nos cantos de tras e a bandeira da chapa na direita
    lights = []
    for k, (x, y) in enumerate(((0.52, 0.2), (-0.52, 0.2))):     # nos guarda-corpos dos lados, abaixo das luvas
        lights.append((lanterna_poste(root, P, f'zb_poste{k}', x, y, zf + 0.17, h=0.12), '#ffcf7a', 10.0, 1))
    bandeira_pano(root, P, 'zb_bandeira', 0.52, -0.08, zf + 0.15, size=0.3, h_pole=0.5)
    # no chao: banquinha na frente, caixotes a direita e o copao de suco com canudos (a municao) a esquerda
    banca(root, P, 'zb_banca', (-0.06, -0.55, G), w=0.38, d=0.17, h=0.21, lamp=False, flag=False)
    pilha_caixotes(root, P, 'zb_caixote', [(0.62, -0.4, G, 0.35, 0.95, True, True), (0.66, -0.15, G, 1.2, 0.9, True, False)])
    copo_suco(root, P, 'zb_copo', (-0.62, -0.42, G))
    laranjas_chao(root, P, 'zb_caida', [(0.36, -0.66, G, 0.04), (-0.42, -0.66, G, 0.038)])
    return {'slots': [(-0.24, -0.2, fz + 0.04), (0.24, -0.22, fz + 0.04)], 'lights': lights, 'points': {'top': (0.0, -0.22, fz + 0.62)}}


def copo_suco(root, P, tag, loc):
    """Copao de suco de laranja com rodela na borda e canudos listrados."""
    x, y, z = loc
    vidro = mat('copo_vidro', '#e8f6f4', rough=0.08, var=0.0, bump=0.0)
    cyl(root, tag, 0.1, 0.26, (x, y, z + 0.13), r2=0.115, m=vidro, v=28, bev=0.012)
    cyl(root, tag + '_suco', 0.096, 0.2, (x, y, z + 0.112), r2=0.108, m=P['suco'], v=28, bev=0.01)
    torus(root, tag + '_borda', (x, y, z + 0.26), 0.114, 0.008, vidro, n=28, segs=6)
    f = fatia(root, P, tag + '_rodela', 0.07, th=0.02)
    f.location = (x + 0.1, y - 0.03, z + 0.25)
    f.rotation_euler = (math.pi / 2, 0, -0.5)
    for k, (dx, dy, lx, ly) in enumerate(((-0.03, 0.02, -0.08, 0.04), (0.02, 0.03, 0.03, 0.06), (0.0, -0.03, 0.06, -0.02))):
        segs = 6
        for j in range(segs):
            t0, t1 = j / segs, (j + 1) / segs
            p0 = (x + dx + lx * t0, y + dy + ly * t0, z + 0.1 + 0.32 * t0)
            p1 = (x + dx + lx * t1, y + dy + ly * t1, z + 0.1 + 0.32 * t1)
            tube(root, f'{tag}_canudo{k}_{j}', [p0, p1], 0.009, P['canudo'] if j % 2 == 0 else P['chapa'], segs=8)


def build_soprador(P, root, variant):
    """Apoiador do canudo: camisa amarela da selecao, bone verde, calcao azul e meiao; canudo comprido listrado na mao
    direita e os carocos que saem no sopro. za: oculos escuros; zb: grisalho de bigode."""
    tag = root['set']
    pr = build_apoiador(P, root, variant, tag=tag, municao=False)
    hold(pr, 'R', *canudo(root, P, tag))
    hold(pr, 'R', *sementes(root, P, tag))
    return pr


IDLE_N, AIM_N, SHOOT_N = 12, 4, 8


def hunter_state(mode, f, tag):
    """Igual a Zarabatana: idle: canudo de pe, olhando em volta; aim: na boca, mirando; shoot: sopra (0, os carocos
    saem), baixa, pega outro caroco e volta a mirar."""
    hide = (f'{tag}_semente',)
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.13, 0.3 + 0.006 * s), grip_R=(0.1, 0.0, 1.0), hand_L=(0.08, 0.12, 0.3), breathe=s,
                    head_yaw=-0.1 + 0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph, hide=hide)
    aim = dict(hand_R=(0.13, -0.03, 0.5), grip_R=(-1.0, 0.0, -0.08), hand_L=(0.28, 0.02, 0.49), pole_L=(-0.2, 1.0, -0.6),
               head_pitch=-0.02, head_yaw=0.05, hide=hide)
    if mode == 'aim':
        ph = f / AIM_N
        st = dict(aim)
        st.update(breathe=0.4 * math.sin(TAU * ph), ph=ph)
        return st
    seq = [
        dict(lean=-0.06, breathe=1.0, hide=()),
        dict(lean=-0.03, breathe=0.6, hide=()),
        dict(hand_R=(0.1, -0.08, 0.38), grip_R=(-0.5, 0.0, 0.8), hand_L=(0.06, 0.12, 0.34)),
        dict(hand_R=(0.08, -0.12, 0.34), grip_R=(0.0, 0.0, 1.0), hand_L=(-0.02, 0.1, 0.3)),
        dict(hand_R=(0.08, -0.12, 0.34), grip_R=(0.0, 0.0, 1.0), hand_L=(0.06, 0.02, 0.5)),
        dict(hand_R=(0.1, -0.08, 0.4), grip_R=(-0.6, 0.0, 0.6), hand_L=(0.16, 0.02, 0.45)),
        dict(hand_R=(0.12, -0.05, 0.46), grip_R=(-0.9, 0.0, 0.2), hand_L=(0.24, 0.02, 0.48)),
        dict(),
    ][f]
    st = dict(aim)
    st.update(ph=f / SHOOT_N)
    st.update(seq)
    return st


def crew(key, label, variant):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, hunter_state(mode, f, parts['tag']))
    return {'key': key, 'label': label, 'build': lambda P, root: build_soprador(P, root, variant), 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'aim'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('aim', AIM_N, lambda parts, P, root, f: pose(parts, P, root, f, 'aim')),
                      ('shoot', SHOOT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'shoot'))]}


SPEC = {
    'show_crew': {'zb': ['zbA', 'zbB']},
    'towers': [('zb', 'Candidatura Laranja', build_zb)],
    'crews': [crew('zbA', 'Apoiador do canudo A', 'za'), crew('zbB', 'Apoiador do canudo B', 'zb')],
}


if __name__ == '__main__':
    main(FAM, SPEC)
