"""Rachadinha (Ninguem Sobe a Rampa): o gabinete de gaveteiros rachado ao meio. Niveis 1 a 3, Chefe de Gabinete
(lancers) e Funcionarios Fantasmas (monks), com o seguranca na porta. Um arquivo de gavetas na cor da chapa partido em
duas metades que tombam cada uma para o seu lado (a rachadura abre no alto), sobre calcada, laje e marquise de concreto
branco de Brasilia; a porta fica no pe da metade direita, de onde saem os assessores, e a gaveta da esquerda vive
aberta, cheia de macos de dinheiro (conceito: arte/conceitos/torres/rachadinha.png).

Os nomes de conjuntos, postos e pontos sao os mesmos da Palafita dos Guardioes (js/sprites.js depende deles):
qt1, qt2, qt3, qtL (lancers), qtM (monks) e a tripulacao qtG, qtS, qtL_c, qtM_c (modos idle e act).

Cores da chapa (chapa.py): o arquivo sai na cor da chapa. CHAPA=V (padrao): corpo verde com gavetas amarelas, marquise
verde, bandeira verde com losango amarelo e circulo azul, ipe amarelo, tapete azul no Chefe de Gabinete, assessores de
terno verde (ou azul) com gravata amarela e o broche do losango; CHAPA=R: corpo vermelho com gavetas vermelho-claras e
moldura branca, bandeira vermelha com estrela branca, ipe rosa, tapete vermelho, assessores de terno vermelho (ou vinho)
com a estrela branca na lapela; o fantasma ganha o bone da chapa. O dinheiro, o carimbo, a prancheta e a pasta ficam.
Tamanho, ancora, postos, porta e pontos iguais nas duas.

  Blender -b -P tools/blender/torre_quartel.py -- render arte/render/quartel [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_quartel.py -- render arte/render_r/quartel [conjuntos...]
  Blender -b -P tools/blender/torre_quartel.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_quartel.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto branco de Brasilia (padrao de todas as torres)
from chapa import CHAPA, PAL, cor   # cores da chapa: CHAPA=V (padrao) ou CHAPA=R
from pecas_zcv import broche        # broche da chapa na lapela (V losango, R estrela)

FAM = 'quartel'
ROT = math.radians(12)      # o predio gira um pouco para mostrar a lateral esquerda (a que pega sol)
TILT = math.radians(4.0)    # cada metade tomba para o seu lado: a rachadura fica bem aberta no alto
Z0 = 0.07                   # chao do lote de Brasilia no codigo (topo 0.15 menos o LIFT que o build_family soma)

import lib as _lib
_orig_palette2 = palette2


# cores do arquivo por chapa: (corpo, frente das gavetas, rodape, moldura da etiqueta) nas tres versoes, ipe, tapete
QC = {'V': dict(main=('#1f8f47', '#ffd21f', '#0f5a2b'), dark=('#0f4a26', '#16572f', '#08301a'), pale=('#94c9a0', '#f2df8e', '#6f9a78'),
                frame='#2453c4', ipe=('#f5c531', '#ffdc5a'), carpet='#2a4fae', rope='#1f3f8f', flag=('#2f9a4a', '#f6cf3a', '#2e4f9e')),
      'R': dict(main=('#b81f22', '#ec4a43', '#7a1417'), dark=('#5c1214', '#7a1a1d', '#3a0a0c'), pale=('#e39a92', '#f4bcb4', '#a8665f'),
                frame='#ffffff', ipe=('#e8649a', '#f59cc0'), carpet='#b3302d', rope='#8e1f22', flag=('#d6282b', '#ffffff', '#ffffff'))}[CHAPA]


def palette2():   # noqa: F811 - cores da chapa (V verde e amarelo, R vermelho e branco) e o concreto branco de Brasilia
    P = _orig_palette2()
    P['teal'] = cor('pri', rough=0.8, sheen=0.4)
    P['stripes'] = mat('toldo_chapa_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(3.6, PAL['claro'], PAL['pri']), sheen=0.4)
    P['plume'] = mat('pluma_chapa_' + CHAPA, PAL['pri'], rough=0.9, var=0.0, bump=0.1, sheen=0.6)
    P['concrete'] = mat('concreto', '#efebe2', rough=0.88, var=0.03, bump=0.18)
    P['concrete_d'] = mat('concreto_junta', '#c9c2b4', rough=0.9, var=0.02, bump=0.1)
    P['crack'] = mat('rachadura', '#2a1812', rough=0.95, var=0.0, bump=0.15)
    P['paper'] = mat('papel', '#f6efdc', rough=0.85, var=0.04, bump=0.03)
    P['cash'] = mat('dinheiro', '#86b86a', rough=0.75, var=0.06, bump=0.05)
    P['cash_d'] = mat('dinheiro_esc', '#5f9a4e', rough=0.75, var=0.06, bump=0.05)
    P['cash_band'] = mat('cinta_dinheiro', '#f1e2b8', rough=0.8, var=0.0, bump=0.02)
    P['door_wood'] = mat('porta_madeira', '#6b4128', rough=0.6, var=0.05, bump=0.12)
    P['ipe'] = mat('ipe_' + CHAPA, QC['ipe'][0], rough=0.8, var=0.12, bump=0.1, sheen=0.4)        # V ipe amarelo, R ipe rosa
    P['ipe_l'] = mat('ipe_claro_' + CHAPA, QC['ipe'][1], rough=0.8, var=0.1, bump=0.1, sheen=0.4)
    P['flag_g'] = mat('bandeira_fundo_' + CHAPA, QC['flag'][0], rough=0.8, var=0.0, bump=0.04, sheen=0.4)
    P['flag_y'] = mat('bandeira_emblema_' + CHAPA, QC['flag'][1], rough=0.8, var=0.0, bump=0.04, sheen=0.4)
    P['flag_b'] = mat('bandeira_circulo_' + CHAPA, QC['flag'][2], rough=0.8, var=0.0, bump=0.04, sheen=0.4)
    P['carpet'] = mat('tapete_' + CHAPA, QC['carpet'], rough=0.9, var=0.02, bump=0.12, sheen=0.7)
    P['rope_v'] = mat('cordao_veludo_' + CHAPA, QC['rope'], rough=0.85, var=0.0, bump=0.06, sheen=0.6)
    P['awning'] = cor('pri' if CHAPA == 'V' else 'sec', rough=0.7)   # marquise da porta (R: branca, o vermelho some no arquivo)
    P['sheet'] = mat('lencol', '#f7f4ec', rough=0.85, var=0.02, bump=0.06, sheen=0.5)
    P['_emblem'] = 'spears'
    return P


_lib.palette2 = palette2


def cab_mats(P, kind='laranja'):
    """Materiais do arquivo (cores da chapa): corpo, frente das gavetas, rodape, puxador, moldura da etiqueta e etiqueta."""
    c = CHAPA
    if kind == 'escuro':   # Chefe de Gabinete: laca escura da chapa (V verde, R vinho) com ouro
        b, f, t = QC['dark']
        return dict(body=mat('gaveteiro_laca_' + c, b, rough=0.4, var=0.03, bump=0.04),
                    front=mat('gaveta_laca_' + c, f, rough=0.35, var=0.05, bump=0.04),
                    toe=mat('rodape_laca_' + c, t, rough=0.5, var=0.0, bump=0.04),
                    metal=P['gold'], frame=P['gold'], label=mat('etiqueta_creme', '#f3e6c4', rough=0.8, var=0.02, bump=0.02))
    if kind == 'palido':   # Funcionarios Fantasmas: o mesmo arquivo, desbotado
        b, f, t = QC['pale']
        return dict(body=mat('gaveteiro_palido_' + c, b, rough=0.75, var=0.04, bump=0.08),
                    front=mat('gaveta_palida_' + c, f, rough=0.75, var=0.06, bump=0.08),
                    toe=mat('rodape_palido_' + c, t, rough=0.8, var=0.0, bump=0.06),
                    metal=mat('puxador_gasto', '#b9b2a8', rough=0.5, metal=0.5, var=0.02, bump=0.05),
                    frame=mat('moldura_gasta', '#a99a80', rough=0.5, metal=0.4, var=0.02, bump=0.05),
                    label=mat('etiqueta_vazia', '#f1ece2', rough=0.85, var=0.02, bump=0.02))
    b, f, t = QC['main']   # V corpo verde e gavetas amarelas; R corpo vermelho e gavetas vermelho-claras
    return dict(body=mat('gaveteiro_' + c, b, rough=0.62, var=0.03, bump=0.06),
                front=mat('gaveta_' + c, f, rough=0.58, var=0.06, bump=0.05),
                toe=mat('rodape_gaveteiro_' + c, t, rough=0.7, var=0.0, bump=0.05),
                metal=mat('puxador', '#e6e0d6', rough=0.28, metal=0.85, var=0.02, bump=0.02),
                frame=mat('moldura_etiqueta_' + c, QC['frame'], rough=0.35, metal=0.2, var=0.02, bump=0.02),
                label=mat('etiqueta', '#f7f0dc', rough=0.8, var=0.02, bump=0.02))


# ---------------------------------------------------------------- pecas do gabinete
def prism_xz(root, name, outline, y0, y1, m, bev=0.02, front=False):
    """Prisma: contorno no plano XZ (lista de (x, z)) extrudado de y0 (frente) a y1 (fundo)."""
    bm = bmesh.new()
    F = [bm.verts.new((x, y0, z)) for x, z in outline]
    B = [bm.verts.new((x, y1, z)) for x, z in outline]
    n = len(outline)
    caps = [bm.faces.new(F), bm.faces.new(list(reversed(B)))]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((F[j], F[i], B[i], B[j]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=caps, quad_method='BEAUTY', ngon_method='BEAUTY')
    return bm_to_obj(bm, name, root, [m], bev=bev, front=front, angle=35)


def crack_line(H, amp, seed, step=0.1):
    """Zigue-zague da rachadura, do pe (z = 0) ao topo (z = H): lista de (x, z)."""
    rr = random.Random(seed)
    n = max(4, int(round(H / step)))
    pts = [(0.0, 0.0)]
    for k in range(1, n):
        side = 1 if k % 2 else -1
        pts.append((side * amp * rr.uniform(0.55, 1.0), H * k / n + rr.uniform(-0.2, 0.2) * H / n))
    pts.append((rr.uniform(-0.3, 0.3) * amp, H))
    return pts


def hairline(root, P, tag, pts, r=0.006, parent=None):
    """Trinca fina (tubo escuro rente a superficie)."""
    o = tube(root, tag, pts, r, P['crack'], segs=5, rfun=lambda t: r * (1.0 - 0.6 * t))
    if parent:
        o.parent = parent
    return o


def drawer(root, M, tag, par, c, w, h, open_=0.0):
    """Gaveta na frente do arquivo (voltada para -Y): frente, porta-etiqueta sem texto e puxador em U.
    c = centro da frente no espaco do pai; open_ > 0 puxa a gaveta (aparecem as laterais e o fundo)."""
    x, y, z = c
    y -= open_
    objs = [box(root, tag, (w, 0.04, h), (x, y, z), m=M['front'], bev=0.016)]
    lz = z + h * 0.2
    objs.append(box(root, tag + '_moldura', (w * 0.36, 0.012, h * 0.27), (x, y - 0.022, lz), m=M['frame'], bev=0.004))
    objs.append(box(root, tag + '_etiqueta', (w * 0.28, 0.012, h * 0.17), (x, y - 0.026, lz), m=M['label'], bev=0.003))
    hz = z - h * 0.2
    hw = w * 0.2
    objs.append(tube(root, tag + '_puxador', [(x - hw, y - 0.02, hz), (x - hw, y - 0.05, hz - 0.006), (x + hw, y - 0.05, hz - 0.006), (x + hw, y - 0.02, hz)],
                     0.012, M['metal'], segs=6))
    if open_ > 0:
        d = open_ + 0.03
        for sx in (-1, 1):
            objs.append(box(root, f'{tag}_lado{sx}', (0.022, d, h * 0.78), (x + sx * (w / 2 - 0.03), y + d / 2, z - h * 0.08), m=M['body'], bev=0.006))
        objs.append(box(root, tag + '_fundo', (w - 0.05, d, 0.022), (x, y + d / 2, z - h * 0.44), m=M['body'], bev=0.006))
    for o in objs:
        o.parent = par
    return objs


def cash_pile(root, P, tag, par, c, w, d, n=5, seed=3):
    """Macos de dinheiro (verde, com cinta creme, sem numero nenhum) transbordando da gaveta."""
    rr = random.Random(seed)
    x, y, z = c
    out = []
    for k in range(n):
        bx = x + rr.uniform(-w * 0.32, w * 0.32)
        by = y + rr.uniform(-d * 0.25, d * 0.25)
        bz = z + 0.03 + 0.046 * (k // 2) + rr.uniform(0, 0.01)   # a pilha transborda acima da frente da gaveta
        rot = (rr.uniform(-0.25, 0.25), rr.uniform(-0.2, 0.2), rr.uniform(-0.6, 0.6))
        m_ = P['cash'] if k % 2 else P['cash_d']
        out.append(box(root, f'{tag}_maco{k}', (0.11, 0.06, 0.03), (bx, by, bz), rot=rot, m=m_, bev=0.008))
        out.append(box(root, f'{tag}_cinta{k}', (0.026, 0.064, 0.034), (bx, by, bz), rot=rot, m=P['cash_band'], bev=0.004))
    for o in out:
        o.parent = par
    return out


def lamp(root, P, tag, par, c, lights, side=1):
    """Arandela de bronze com globo de luz quente na fachada."""
    x, y, z = c
    objs = [tube(root, tag + '_braco', [(x, y + 0.03, z - 0.03), (x, y - 0.03, z - 0.03), (x, y - 0.05, z)], 0.008, P['bronze'], segs=6),
            sphere(root, tag + '_globo', 0.036, (x, y - 0.05, z + 0.03), m=P['glow'], seg=14),
            cyl(root, tag + '_chapeu', 0.03, 0.018, (x, y - 0.05, z + 0.068), r2=0.012, m=P['bronze'], v=12, bev=0.004)]
    for o in objs:
        o.parent = par
    lights.append(('obj', objs[1], '#ffb25a', 14.0, 1))
    return objs


def flag(root, P, tag, par, base, h=0.5, w=0.3):
    """Bandeira da chapa num mastro (sem texto), balancando ao vento: V verde com losango amarelo e circulo azul, R
    vermelha com a estrela branca de 5 pontas."""
    x, y, z = base
    objs = [tube(root, tag + '_mastro', [(x, y, z), (x, y, z + h)], 0.012, P['steel'], segs=8),
            sphere(root, tag + '_topo', 0.022, (x, y, z + h + 0.012), m=P['gold'], seg=10)]
    fh = w * 0.68
    pieces = [(tag + '_bandeira', P['flag_g'], None, 0.0, 0.012)]
    rw, rh = w * 0.8, fh * 0.76

    def losango(u, v, co):
        k = 1 - abs(2 * v - 1)
        return Vector((w / 2 + (u - 0.5) * rw * k, -0.009, -(fh - rh) / 2 - v * rh))

    def disco(u, v, co):
        a = TAU * u
        r = fh * 0.2 * v
        return Vector((w / 2 + r * math.cos(a), -0.013, -fh / 2 + r * math.sin(a)))

    def star(u, v, co):
        # 10 colunas = as 10 quinas da estrela (ponta, vale, ponta...): a malha em leque fecha a estrela exata
        k = int(round(u * 10))
        a = math.pi / 2 + TAU * k / 10
        r = fh * 0.36 * (1.0 if k % 2 == 0 else 0.42) * v
        return Vector((w / 2 + r * math.cos(a), -0.011, -fh / 2 + r * math.sin(a)))
    marks = [(tag + '_losango', P['flag_y'], losango, 0, 0.004), (tag + '_disco', P['flag_b'], disco, 0, 0.003)] if CHAPA == 'V' else \
        [(tag + '_estrela', P['flag_y'], star, 0, 0.004)]
    grid = {losango: (14, 8), disco: (16, 3), star: (10, 2)}
    for name, m_, fn, dy, th in pieces + marks:
        if fn is None:
            o = cloth_grid(root, name, w, fh, 14, 4, [m_], thick=th)
        else:
            o = cloth_grid(root, name, w, fh, grid[fn][0], grid[fn][1], [m_], shape=fn, thick=th)
        o.parent = par
        o.location = (x + 0.01, y, z + h - 0.02)
        register_cloth(o, flag_wave(w, amp=0.05, cycles=1, waves=1.1))
        objs.append(o)
    return objs


def ipe(root, P, tag, loc, s=1.0, pot=True, seed=5):
    """Ipe amarelo florido de Brasilia num vaso de concreto (a mancha de cor do lote)."""
    rr = random.Random(seed)
    x, y, z = loc
    if pot:
        box(root, tag + '_vaso', (0.2 * s, 0.2 * s, 0.13 * s), (x, y, z + 0.065 * s), m=P['concrete'], bev=0.02)
        box(root, tag + '_terra', (0.17 * s, 0.17 * s, 0.02), (x, y, z + 0.125 * s), m=mat('terra_vaso', '#8a4a2a', rough=0.95, var=0.05, bump=0.3), bev=0.005)
        z += 0.13 * s
    tube(root, tag + '_tronco', [(x, y, z), (x + 0.03 * s, y, z + 0.22 * s), (x - 0.02 * s, y, z + 0.4 * s)], 0.026 * s, P['wood'], segs=8,
         rfun=lambda t: s * (0.028 - 0.012 * t))
    for k in range(3):
        a = TAU * k / 3 + 0.4
        tube(root, f'{tag}_galho{k}', [(x - 0.02 * s, y, z + 0.38 * s), (x + 0.14 * s * math.cos(a), y + 0.1 * s * math.sin(a), z + 0.5 * s)], 0.01 * s, P['wood'], segs=6)
    for k in range(9):
        a = TAU * k / 9 + rr.uniform(-0.3, 0.3)
        rad = rr.uniform(0.06, 0.15) * s
        sphere(root, f'{tag}_flor{k}', rr.uniform(0.07, 0.1) * s, (x + rad * math.cos(a), y + rad * math.sin(a) * 0.8, z + (0.5 + rr.uniform(-0.05, 0.08)) * s),
               scale=(1, 1, 0.8), m=P['ipe'] if k % 3 else P['ipe_l'], seg=14)
    sphere(root, tag + '_florTopo', 0.1 * s, (x, y, z + 0.6 * s), scale=(1, 1, 0.8), m=P['ipe_l'], seg=14)


def gabinete(root, P, tag, M, rows, W, D=0.6, cy=0.14, dh=0.29, door='single', lights=None, seed=1, cash_row=0, empty_rows=(),
             roof_m=None, roof_trim=None, flag_on=False, plaque=False, ac=False, papers=3):
    """Arquivo de gavetas partido ao meio (uma coluna de gavetas por metade) sobre calcada de concreto.
    Devolve: predio (empty girado), metades {-1, 1}, ponto da porta e funcoes de coordenada."""
    lights = lights if lights is not None else []
    toe, band = 0.05, 0.05
    H = toe + rows * dh + band
    bld = empty(root, tag + '_predio', loc=(0, cy, 0), rot=(0, 0, ROT))
    amp = 0.04
    crack = crack_line(H, amp, seed)
    g0 = 0.016
    inner = amp + g0 + 0.03
    col_w = W / 2 - 0.05 - inner
    halves = {}
    for s in (-1, 1):
        piv = empty(root, f'{tag}_metade{"E" if s < 0 else "D"}', loc=(s * g0, 0, Z0), parent=bld, rot=(0, s * TILT, 0))
        halves[s] = piv
        L = lambda x, y, z, s=s: (x - s * g0, y, z - Z0)
        # contorno: pe externo, rachadura subindo, canto quebrado no topo, topo externo
        chip = (0.07 + 0.03 * (s > 0), 0.07 + 0.04 * (s < 0))
        pts = [(s * W / 2, 0.0)] + [(x + s * g0, z) for x, z in crack[:-1]]
        xt, zt = crack[-1]
        pts += [(xt + s * g0, zt - chip[0]), (xt + s * (g0 + chip[1] * 0.6), zt - chip[0] * 0.45), (xt + s * (g0 + chip[1]), zt), (s * W / 2, zt)]
        pts = [(x - s * g0, z) for x, z in pts]
        body = prism_xz(root, f'{tag}_corpo{s}', pts, -D / 2, D / 2, M['body'], bev=0.018)
        body.parent = piv
        # rodape escuro e frisos
        o = box(root, f'{tag}_rodape{s}', (W / 2 - inner - 0.02, 0.02, toe * 0.7), L(s * (W / 2 + inner) / 2, -D / 2 - 0.004, Z0 + toe * 0.45), m=M['toe'], bev=0.006)
        o.parent = piv
        # laje de concreto no topo (para no canto quebrado)
        x_in = xt + s * (g0 + chip[1])
        x_out = s * (W / 2 + 0.015)
        sw = abs(x_out - x_in)
        o = box(root, f'{tag}_laje{s}', (sw, D + 0.03, 0.04), L((x_out + x_in) / 2, -0.005, Z0 + H + 0.02), m=roof_m or M['front'], bev=0.014)
        o.parent = piv
        if roof_trim:
            o = box(root, f'{tag}_lajeFriso{s}', (sw + 0.004, 0.012, 0.016), L((x_out + x_in) / 2, -D / 2 - 0.022, Z0 + H + 0.02), m=roof_trim, bev=0.004)
            o.parent = piv
        # gavetas
        cx_col = s * (W / 2 + inner) / 2 + s * 0.005
        for r in range(rows):
            zc = Z0 + toe + dh * (r + 0.5)
            if s > 0 and r == 0:
                continue   # a porta fica aqui
            if r in empty_rows:
                empty_window(root, P, M, f'{tag}_janela{s}_{r}', piv, L(cx_col, -D / 2, zc), col_w, dh - 0.04)
                continue
            op = 0.16 if (s < 0 and r == cash_row) else 0.0
            if op:
                dp = empty(root, f'{tag}_gavetaPivo', loc=L(cx_col, -D / 2 - 0.005, zc), parent=piv)
                drawer(root, M, f'{tag}_gaveta{s}_{r}', dp, (0, 0, 0), col_w, dh - 0.035, open_=op)
                cash_pile(root, P, f'{tag}_dinheiro', dp, (0, -op / 2 - 0.005, -(dh - 0.035) * 0.44), col_w - 0.06, op, n=12, seed=seed + 2)
                register_anim(dp, lambda o, mb, ph: setattr(o, 'matrix_basis', Matrix.Translation((0, -0.035 * (0.5 - 0.5 * math.cos(TAU * ph)), 0)) @ mb))
            else:
                drawer(root, M, f'{tag}_gaveta{s}_{r}', piv, L(cx_col, -D / 2 - 0.005, zc), col_w, dh - 0.035)
        # trincas finas na lateral (a esquerda aparece de lado)
        if s < 0:
            rr = random.Random(seed + 9)
            for k in range(2):
                z_a = Z0 + H * rr.uniform(0.25, 0.75)
                ptsc = []
                yy = -D / 2 + 0.06
                zz = z_a
                for j in range(5):
                    ptsc.append(L(-W / 2 - 0.004, yy, zz))
                    yy += rr.uniform(0.08, 0.14)
                    zz += rr.uniform(-0.09, 0.09)
                hairline(root, P, f'{tag}_trinca{k}', ptsc, parent=piv)
        # trinca do topo da laje continuando a rachadura
    # miolo escuro visto pela rachadura e papeis presos nela
    o = box(root, f'{tag}_miolo', (0.24, D - 0.1, H - 0.04), (0, 0.02, Z0 + (H - 0.04) / 2), m=P['crack'], bev=0.0)
    o.parent = bld
    rr = random.Random(seed + 4)
    for k in range(papers):
        z = Z0 + H * rr.uniform(0.3, 0.85)
        o = box(root, f'{tag}_papel{k}', (0.12, 0.006, 0.15), (crack_x(crack, z - Z0), -D / 2 + 0.03, z), rot=(rr.uniform(-0.3, 0.3), rr.uniform(-0.9, 0.9), rr.uniform(-0.5, 0.5)),
                m=P['paper'], bev=0.002)
        o.parent = bld
    # rachadura continua pela calcada ate a borda da frente
    pc = [(crack[0][0], -D / 2 + 0.02, Z0 + 0.003)]
    yy = -D / 2
    k = 0
    while yy > -D / 2 - 0.3:
        yy -= 0.06
        k += 1
        pc.append(((0.025 if k % 2 else -0.02), yy, Z0 + 0.003))
    pc.append((0.0, -D / 2 - 0.36, Z0 + 0.002))
    o = tube(root, f'{tag}_rachaChao', pc, 0.012, P['crack'], segs=5)
    o.parent = bld
    # porta no pe da metade direita
    s = 1
    piv = halves[s]
    L = lambda x, y, z: (x - g0, y, z - Z0)
    dx = (W / 2 + inner) / 2
    door_h = toe + dh - 0.03
    dw = col_w * (0.84 if door == 'double' else 0.68)
    for sx in (-1, 1):
        o = box(root, f'{tag}_batente{sx}', (0.035, 0.05, door_h + 0.02), L(dx + sx * (dw / 2 + 0.0175), -D / 2 - 0.015, Z0 + (door_h + 0.02) / 2), m=P['concrete'], bev=0.008)
        o.parent = piv
    leaves = [(dx, dw)] if door != 'double' else [(dx - dw / 4, dw / 2 - 0.006), (dx + dw / 4, dw / 2 - 0.006)]
    for i, (lx, lw) in enumerate(leaves):
        o = box(root, f'{tag}_folha{i}', (lw, 0.03, door_h), L(lx, -D / 2 + 0.002, Z0 + door_h / 2), m=P['door_wood'] if door != 'double' else mat('porta_mogno', '#3b2016', rough=0.35, var=0.03, bump=0.05), bev=0.008)
        o.parent = piv
        o = box(root, f'{tag}_vidro{i}', (lw * 0.6, 0.012, door_h * 0.36), L(lx, -D / 2 - 0.016, Z0 + door_h * 0.68), m=P['window'], bev=0.004)
        o.parent = piv
        kx = lx + (lw * 0.32 if (door != 'double' or i == 0) else -lw * 0.32)
        if door == 'double':
            kx = lx + (lw * 0.36 if i == 0 else -lw * 0.36)
            o = tube(root, f'{tag}_macaneta{i}', [L(kx, -D / 2 - 0.02, Z0 + door_h * 0.32), L(kx, -D / 2 - 0.02, Z0 + door_h * 0.52)], 0.009, P['gold'], segs=6)
        else:
            o = sphere(root, f'{tag}_macaneta{i}', 0.014, L(kx, -D / 2 - 0.02, Z0 + door_h * 0.45), m=P['gold'], seg=8)
        o.parent = piv
    # marquise curva de concreto sobre a porta
    o = box(root, f'{tag}_marquise', (dw + 0.18, 0.2, 0.035), L(dx, -D / 2 - 0.08, Z0 + door_h + 0.04), m=P['awning'], bev=0.016)
    o.parent = piv
    if plaque:
        o = box(root, f'{tag}_placa', (dw * 0.9, 0.014, 0.075), L(dx, -D / 2 - 0.17, Z0 + door_h + 0.1), m=P['gold'], bev=0.006)
        o.parent = piv
        o = box(root, f'{tag}_placaMiolo', (dw * 0.72, 0.008, 0.045), L(dx, -D / 2 - 0.178, Z0 + door_h + 0.1), m=mat('placa_fundo', '#3c2a1e', rough=0.4, var=0, bump=0), bev=0.004)
        o.parent = piv
    lamp(root, P, f'{tag}_luz', piv, L(dx + dw / 2 + 0.055, -D / 2, Z0 + door_h - 0.05), lights)
    if flag_on:
        flag(root, P, f'{tag}_bandeira', halves[-1], (-W / 2 + 0.16 + g0, 0.05, H + 0.05), h=0.5, w=0.3)
    if ac:
        # ar-condicionado pendurado na lateral esquerda
        piv = halves[-1]
        L = lambda x, y, z: (x + g0, y, z - Z0)
        zc = Z0 + toe + dh * (rows - 1.5)
        o = box(root, f'{tag}_arCond', (0.1, 0.26, 0.15), L(-W / 2 - 0.05, -D / 2 + 0.2, zc), m=mat('ar_cond', '#ece4d2', rough=0.6, var=0.02, bump=0.04), bev=0.016)
        o.parent = piv
        for k in range(4):
            o = box(root, f'{tag}_arGrade{k}', (0.004, 0.2, 0.01), L(-W / 2 - 0.101, -D / 2 + 0.2, zc - 0.045 + 0.028 * k), m=P['iron'], bev=0.0)
            o.parent = piv
        o = tube(root, f'{tag}_arCano', [L(-W / 2 - 0.05, -D / 2 + 0.2, zc - 0.075), L(-W / 2 - 0.06, -D / 2 + 0.2, zc - 0.2), L(-W / 2 - 0.02, -D / 2 + 0.22, zc - 0.28)], 0.008, P['iron'], segs=5)
        o.parent = piv
    bpy.context.view_layer.update()

    def at(x, y, z=Z0):
        """Ponto do predio (antes do giro) -> coordenada da raiz."""
        c, sn = math.cos(ROT), math.sin(ROT)
        return (x * c - y * sn, cy + x * sn + y * c, z)
    return {'bld': bld, 'halves': halves, 'H': H, 'W': W, 'D': D, 'at': at, 'door': at(dx, -D / 2 - 0.12), 'lights': lights}


def crack_x(crack, z):
    for (x0, z0), (x1, z1) in zip(crack, crack[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / max(1e-6, z1 - z0)
            return x0 + (x1 - x0) * t
    return 0.0


def empty_window(root, P, M, tag, par, c, w, h):
    """Janela vazia (Funcionarios Fantasmas): moldura de concreto e o vao escuro, sem ninguem."""
    x, y, z = c
    objs = [box(root, tag + '_moldura', (w, 0.04, h), (x, y - 0.012, z), m=P['concrete'], bev=0.012),
            box(root, tag + '_vao', (w - 0.07, 0.04, h - 0.07), (x, y - 0.02, z), m=P['crack'], bev=0.004),
            box(root, tag + '_peitoril', (w + 0.02, 0.06, 0.025), (x, y - 0.03, z - h / 2 + 0.01), m=P['concrete'], bev=0.006)]
    # teia de aranha no canto
    tw = mat('teia', '#e8e4dc', rough=0.6, var=0.0, bump=0.0)
    cx0, cz0 = x - (w - 0.07) / 2, z + (h - 0.07) / 2
    for k in range(3):
        a = -math.pi / 2 * (k + 0.5) / 3
        objs.append(tube(root, f'{tag}_teia{k}', [(cx0, y - 0.044, cz0), (cx0 + 0.09 * math.cos(a), y - 0.044, cz0 + 0.09 * math.sin(a))], 0.002, tw, segs=4))
    for j in (0.04, 0.07):
        objs.append(tube(root, f'{tag}_teiaArco{j}', [(cx0 + j * math.cos(-math.pi / 2 * t / 6), y - 0.044, cz0 + j * math.sin(-math.pi / 2 * t / 6)) for t in range(7)],
                         0.002, tw, segs=4))
    for o in objs:
        o.parent = par
    return objs


def resolve_lights(lights):
    """Luzes registradas como ('obj', objeto, cor, watts, halo) viram (posicao na raiz, cor, watts, halo)."""
    bpy.context.view_layer.update()
    out = []
    for L_ in lights:
        if L_[0] == 'obj':
            out.append((tuple(L_[1].matrix_world.translation),) + tuple(L_[2:]))
        else:
            out.append(L_)
    return out


# ---------------------------------------------------------------- nivel 1: o gaveteiro de duas gavetas
def build_qt1(P, root):
    plot(root, P, 'qt1')
    M = cab_mats(P)
    lights = []
    g = gabinete(root, P, 'qt1', M, rows=2, W=0.98, D=0.56, dh=0.3, lights=lights, seed=2, papers=2)
    at = g['at']
    return {'slots': [at(0.6, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- nivel 2: tres andares de gavetas e a plaquinha
def build_qt2(P, root):
    plot(root, P, 'qt2')
    M = cab_mats(P)
    lights = []
    g = gabinete(root, P, 'qt2', M, rows=3, W=1.06, D=0.58, dh=0.29, lights=lights, seed=4, plaque=True, papers=3)
    at = g['at']
    ipe(root, P, 'qt2_ipe', (-0.68, 0.16, 0.07), s=0.75, seed=3)
    return {'slots': [at(-0.64, -0.46), at(0.64, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- nivel 3: quatro andares, bandeirinha, ar-condicionado e o ipe
def build_qt3(P, root):
    plot(root, P, 'qt3')
    M = cab_mats(P)
    lights = []
    g = gabinete(root, P, 'qt3', M, rows=4, W=1.14, D=0.6, dh=0.28, lights=lights, seed=7, plaque=True, flag_on=True, ac=True, papers=4)
    at = g['at']
    ipe(root, P, 'qt3_ipe', (-0.7, 0.18, 0.07), s=0.95, seed=8)
    return {'slots': [at(-0.67, -0.46), at(0.67, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- Chefe de Gabinete: mogno, ouro, porta dupla e tapete vermelho
def build_qtL(P, root):
    plot(root, P, 'qtL')
    M = cab_mats(P, 'escuro')
    lights = []
    g = gabinete(root, P, 'qtL', M, rows=4, W=1.14, D=0.6, dh=0.28, door='double', lights=lights, seed=11, plaque=True, flag_on=True, papers=2,
                 roof_m=mat('laje_marmore', '#f4efe6', rough=0.22, var=0.02, bump=0.03), roof_trim=P['gold'])
    at = g['at']
    W, D = g['W'], g['D']
    inner = 0.04 + 0.016 + 0.03
    dx = (W / 2 + inner) / 2
    # tapete vermelho da porta ate a beira do lote, com debrum de ouro
    bld = g['bld']
    y0, y1 = -D / 2 - 0.02, -D / 2 - 0.5
    o = box(root, 'qtL_tapete', (0.26, y0 - y1, 0.014), (dx, (y0 + y1) / 2, Z0 + 0.007), m=P['carpet'], bev=0.004)
    o.parent = bld
    for sx in (-1, 1):
        o = box(root, f'qtL_tapeteOuro{sx}', (0.014, y0 - y1, 0.016), (dx + sx * 0.12, (y0 + y1) / 2, Z0 + 0.008), m=P['gold'], bev=0.003)
        o.parent = bld
    # pedestais de bronze com cordao de veludo vermelho
    rope = P['rope_v']
    for sx in (-1, 1):
        xs = dx + sx * 0.2
        ys = (-D / 2 - 0.14, -D / 2 - 0.44)
        for j, yy in enumerate(ys):
            o = cyl(root, f'qtL_pedestal{sx}{j}', 0.04, 0.02, (xs, yy, Z0 + 0.01), m=P['gold'], v=16, bev=0.006)
            o.parent = bld
            o = tube(root, f'qtL_haste{sx}{j}', [(xs, yy, Z0 + 0.02), (xs, yy, Z0 + 0.22)], 0.011, P['gold'], segs=8)
            o.parent = bld
            o = sphere(root, f'qtL_bola{sx}{j}', 0.022, (xs, yy, Z0 + 0.235), m=P['gold'], seg=10)
            o.parent = bld
        o = tube(root, f'qtL_cordao{sx}', [(xs, ys[0], Z0 + 0.2), (xs, (ys[0] + ys[1]) / 2, Z0 + 0.13), (xs, ys[1], Z0 + 0.2)], 0.012, rope, segs=6)
        o.parent = bld
    # segunda arandela do outro lado da porta
    piv = g['halves'][1]
    L = lambda x, y, z: (x - 0.016, y, z - Z0)
    col_w = W / 2 - 0.05 - inner
    lamp(root, P, 'qtL_luz2', piv, L(dx - col_w * 0.42 - 0.055, -D / 2, Z0 + 0.27), lights)
    return {'slots': [at(-0.68, -0.46), at(0.68, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- Funcionarios Fantasmas: janelas vazias e lencois no varal
def sheet_ghost(root, P, tag, x0, top, w=0.2, h=0.34, seed=1):
    """Lencol de fantasma pendurado no varal: pano com dobras e dois furos de olho (material 2 da mesma malha)."""
    rr = random.Random(seed)
    hole = P['crack']

    def shp(u, v, co):
        return Vector((co.x, 0.018 * math.sin(u * TAU * 1.5 + seed) * (0.3 + v), co.z - 0.02 * math.sin(math.pi * u) * (1 - v)))
    o = cloth_grid(root, tag, w, h, 12, 16, [P['sheet'], hole], shape=shp, thick=0.008)
    me = o.data
    eyes = [(0.34, 0.3), (0.66, 0.3)]
    for p in me.polygons:
        c = p.center
        u, v = c.x / w, -c.z / h
        for ex, ev in eyes:
            if ((u - ex) / 0.09) ** 2 + ((v - ev) / 0.07) ** 2 < 1.0:
                p.material_index = 1
    # boca em O, mais embaixo
    for p in me.polygons:
        c = p.center
        u, v = c.x / w, -c.z / h
        if ((u - 0.5) / 0.07) ** 2 + ((v - 0.5) / 0.06) ** 2 < 1.0:
            p.material_index = 1
    o.location = (x0, 0, top)
    register_cloth(o, hang_wave(h, amp=0.03, axis='Y', cycles=1, waves=0.5 + 0.2 * rr.random(), top=0.0))
    return o


def build_qtM(P, root):
    plot(root, P, 'qtM')
    M = cab_mats(P, 'palido')
    lights = []
    g = gabinete(root, P, 'qtM', M, rows=3, W=1.06, D=0.58, dh=0.29, lights=lights, seed=13, empty_rows=(1, 2), cash_row=0, papers=2)
    at = g['at']
    bld = g['bld']
    D = g['D']
    # varal na frente da metade esquerda: dois postes, o fio e tres lencois de fantasma
    yv = -D / 2 - 0.25
    xa, xb = -0.68, -0.04
    zt = 0.86
    for k, xx in enumerate((xa, xb)):
        o = tube(root, f'qtM_varalPoste{k}', [(xx, yv, Z0), (xx, yv, zt + 0.06)], 0.016, P['wood'], segs=8)
        o.parent = bld
        o = tube(root, f'qtM_varalTrava{k}', [(xx - 0.05, yv, zt + 0.02), (xx + 0.05, yv, zt + 0.02)], 0.01, P['wood'], segs=6)
        o.parent = bld
    o = tube(root, 'qtM_varalFio', [(xa, yv, zt), ((xa + xb) / 2, yv, zt - 0.03), (xb, yv, zt)], 0.005, P['rope'], segs=5)
    o.parent = bld
    for k, (x0, w, h) in enumerate(((xa + 0.04, 0.2, 0.36), (xa + 0.27, 0.2, 0.4), (xa + 0.48, 0.17, 0.3))):
        sh = sheet_ghost(root, P, f'qtM_lencol{k}', x0, zt - 0.02 * math.sin(math.pi * (x0 + w / 2 - xa) / (xb - xa)), w=w, h=h, seed=k + 2)
        sh.parent = bld
        sh.location = (x0, yv, zt - 0.025 * math.sin(math.pi * (x0 + w / 2 - xa) / (xb - xa)))
        for j in (0.15, 0.85):
            o = box(root, f'qtM_pregador{k}{j}', (0.012, 0.016, 0.03), (x0 + w * j, yv - 0.01, sh.location.z + 0.004), m=P['wood_l'], bev=0.003)
            o.parent = bld
    return {'slots': [at(0.06, -0.5), at(0.64, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- a tripulacao: seguranca, assessor-chefe, chefe de gabinete e o fantasma
def tie(root, pr, tag, m, knot=None):
    """Gravata no peito (filha do corpo; o corpo olha para +X local) e a gola branca da camisa."""
    body = pr['body']
    shirt = mat('camisa_branca', '#f6f2ea', rough=0.8, var=0.0, bump=0.02)
    objs = [box(root, tag + '_gola', (0.012, 0.05, 0.035), (0.068, 0.0, 0.466), rot=(0, -0.5, 0), m=shirt, bev=0.006),
            blob(root, tag + '_gravataNo', 0.014, (0.08, 0.0, 0.452), (0.7, 1.0, 1.0), knot or m),
            box(root, tag + '_gravata', (0.01, 0.026, 0.12), (0.087, 0.0, 0.385), rot=(0, 0.08, 0), m=m, bev=0.005)]
    for o in objs:
        o.parent = body
    return objs


def sunglasses(root, pr, tag):
    """Oculos escuros de seguranca (no pivo da cabeca)."""
    hc = Vector((0.006, 0, 0.055))
    lens = mat('lente_escura', '#16161a', rough=0.15, var=0.0, bump=0.0)
    objs = []
    for s, yy in enumerate((-0.026, 0.026)):
        objs.append(blob(root, f'{tag}_lente{s}', 0.017, hc + Vector((0.064, yy, 0.012)), (0.45, 1.1, 0.8), lens))
    objs.append(box(root, tag + '_ponte', (0.006, 0.024, 0.005), hc + Vector((0.07, 0, 0.016)), m=lens, bev=0.001))
    for o in objs:
        o.parent = pr['head']
    return objs


def stamp(root, P, tag):
    """Carimbo (cabo de madeira, base com borracha vermelha) ao longo do Z local, empunhadura em z = 0."""
    return [sphere(root, tag + '_carimboBola', 0.022, (0, 0, 0.03), m=P['wood_l'], seg=10),
            tube(root, tag + '_carimboCabo', [(0, 0, 0.02), (0, 0, -0.05)], 0.012, P['wood_l'], segs=8),
            box(root, tag + '_carimboBase', (0.06, 0.045, 0.022), (0, 0, -0.065), m=P['wood'], bev=0.005),
            box(root, tag + '_carimboTinta', (0.056, 0.041, 0.008), (0, 0, -0.08), m=mat('tinta_carimbo', '#c8382e', rough=0.6, var=0, bump=0), bev=0.002)]


def clipboard(root, P, tag, m=None):
    """Prancheta com papel timbrado (sem texto), presa pela borda: se estende ao longo do Z local."""
    return [box(root, tag + '_prancheta', (0.012, 0.11, 0.15), (0, 0, 0.06), m=m or P['wood_l'], bev=0.004),
            box(root, tag + '_folha', (0.006, 0.09, 0.12), (0.008, 0, 0.055), m=mat('papel_timbrado', '#fbf6ea', rough=0.85, var=0, bump=0), bev=0.001),
            box(root, tag + '_presilha', (0.016, 0.05, 0.02), (0.006, 0, 0.13), m=P['steel'], bev=0.003)]


def briefcase(root, P, tag, m=None):
    """Pasta 007 pendurada pela alca (alca em z = 0, a pasta embaixo)."""
    m = m or mat('pasta_couro', '#3a2418', rough=0.45, var=0.03, bump=0.08)
    return [torus(root, tag + '_alca', (0, 0, -0.012), 0.018, 0.005, P['iron_d'], axis='Y', n=12, segs=5),
            box(root, tag + '_pasta', (0.15, 0.03, 0.11), (0, 0, -0.085), m=m, bev=0.01),
            box(root, tag + '_fecho', (0.03, 0.034, 0.012), (0, 0, -0.04), m=P['gold'], bev=0.003)]


def badge(root, P, tag):
    """Carteira funcional aberta (couro escuro com distintivo de ouro): a carteirada."""
    leather = mat('carteira_couro', '#2a1a14', rough=0.5, var=0.02, bump=0.05)
    return [box(root, tag + '_carteira', (0.01, 0.1, 0.075), (0, 0, 0.04), m=leather, bev=0.004),
            cyl(root, tag + '_distintivo', 0.024, 0.01, (0.008, -0.022, 0.042), m=P['gold'], v=10, bev=0.002, rot=(0, math.pi / 2, 0)),
            box(root, tag + '_cartao', (0.006, 0.036, 0.05), (0.007, 0.026, 0.04), m=mat('cartao_creme', '#f2ead6', rough=0.8, var=0, bump=0), bev=0.002)]


def suit(P, hexcol, key):
    return mat('terno_' + key, hexcol, rough=0.7, var=0.03, bump=0.06, sheen=0.3)


def build_guard(P, root):
    """Seguranca do gabinete: terno escuro da chapa (V verde-escuro com gravata amarela, R vinho com gravata vermelha),
    broche da chapa, oculos escuros, carimbo e prancheta."""
    tag = root['set']
    s_ = cor('escuro', rough=0.7, sheen=0.3)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=mat('cabelo_escuro', '#2e1d12', rough=0.7, var=0.03, bump=0.25), belt=None,
                                         pants=s_, boot_m=mat('sapato_preto', '#1e1a18', rough=0.35, var=0.0, bump=0.02), boot_cuff=s_,
                                         sleeve=s_, bracer=s_))
    tie(root, pr, tag, cor('sec' if CHAPA == 'V' else 'pri', rough=0.6))
    broche(root, pr, tag)
    sunglasses(root, pr, tag)
    hold(pr, 'R', *stamp(root, P, tag))
    hold(pr, 'L', *clipboard(root, P, tag))
    return pr


def build_sergeant(P, root):
    """Assessor-chefe: terno da chapa (V verde com gravata amarela, R vermelho com gravata vinho), broche da chapa,
    barba grisalha, carimbo e prancheta."""
    tag = root['set']
    s_ = cor('pri', rough=0.7, sheen=0.3)
    grey = mat('barba_grisalha', '#b9b2a6', rough=0.85, var=0.02, bump=0.25)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=grey, beard=grey, brow_m=grey, belt=None, pants=s_,
                                         boot_m=mat('sapato_marrom', '#4a2a18', rough=0.35, var=0.0, bump=0.02), boot_cuff=s_, sleeve=s_, bracer=s_))
    tie(root, pr, tag, cor('sec' if CHAPA == 'V' else 'escuro', rough=0.6))
    broche(root, pr, tag)
    hold(pr, 'R', *stamp(root, P, tag))
    hold(pr, 'L', *clipboard(root, P, tag, m=mat('prancheta_couro', '#6a3a22', rough=0.5, var=0.02, bump=0.05)))
    return pr


def build_lancer(P, root):
    """Chefe de Gabinete: terno da chapa (V azul com gravata amarela, R vinho com gravata vermelha), no de ouro, broche
    da chapa, carteira funcional e pasta."""
    tag = root['set']
    s_ = cor('ter', rough=0.7, sheen=0.3)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=mat('cabelo_gel', '#1a120c', rough=0.25, var=0.0, bump=0.05), belt=None, pants=s_,
                                         boot_m=mat('sapato_verniz', '#141010', rough=0.15, var=0.0, bump=0.0), boot_cuff=s_, sleeve=s_, bracer=s_,
                                         pauldron=s_))
    tie(root, pr, tag, cor('sec' if CHAPA == 'V' else 'pri', rough=0.5), knot=P['gold'])
    broche(root, pr, tag)
    hold(pr, 'R', *badge(root, P, tag))
    hold(pr, 'L', *briefcase(root, P, tag))
    return pr


def build_monk(P, root):
    """Funcionario fantasma: um lencol branco com dois furos de olho (e o crachá pendurado, claro)."""
    tag = root['set']
    sheet = P['sheet']
    pr = build_person(P, root, tag, dict(robe=True, robe_m=sheet, tunic=sheet, sleeve=sheet, glove=sheet, bracer=sheet, head='bald',
                                         skin=sheet, boot_m=sheet, belt=None, brow_m=sheet))
    # lencol: cupula redonda sobre a cabeca que desce em dobras ate os ombros (nunca pontuda)
    fold = lambda a, z: 0.06 * math.sin(7 * a + 0.5) * max(0.0, (0.5 - z) / 0.2)
    dr = lathe(root, tag + '_lencol', [(0.29, 0.135, 0.145), (0.34, 0.125, 0.135), (0.4, 0.112, 0.12), (0.45, 0.096, 0.1), (0.5, 0.082, 0.084),
                                       (0.55, 0.08, 0.08), (0.6, 0.066, 0.066), (0.63, 0.04, 0.04), (0.642, 0.0, 0.0)], sheet, segs=16, wobble=fold, lv=2, caps=False, solid=0.006)
    dr.parent = pr['body']
    hole = P['crack']
    for s, yy in enumerate((-0.03, 0.03)):
        o = blob(root, f'{tag}_furo{s}', 0.019, (0.08, yy, 0.565), (0.3, 0.8, 1.2), hole)
        o.parent = pr['body']
    o = blob(root, tag + '_boca', 0.014, (0.082, 0.0, 0.52), (0.3, 1.0, 0.8), hole)
    o.parent = pr['body']
    # cracha pendurado no pescoco
    lan = cor('pri', rough=0.7)
    o = tube(root, tag + '_crachaCordao', [(0.05, -0.05, 0.47), (0.098, -0.02, 0.4), (0.1, 0.0, 0.37), (0.098, 0.02, 0.4), (0.05, 0.05, 0.47)], 0.004, lan, segs=4)
    o.parent = pr['body']
    o = box(root, tag + '_cracha', (0.006, 0.04, 0.05), (0.104, 0.0, 0.345), m=mat('cracha', '#f8f4ea', rough=0.6, var=0, bump=0), bev=0.003)
    o.parent = pr['body']
    # bone da chapa por cima do lencol (V verde, R vermelho), sem passar do topo do lencol (nao muda o enquadramento)
    cap_m = cor('bone')
    o = lathe(root, tag + '_bone', [(0.595, 0.074, 0.074), (0.612, 0.066, 0.066), (0.628, 0.05, 0.05), (0.638, 0.026, 0.026), (0.641, 0.0, 0.0)],
              cap_m, segs=16, lv=2, caps=False, solid=0.006)
    o.parent = pr['body']
    o = cyl(root, tag + '_boneAba', 0.05, 0.008, (0.07, 0.0, 0.597), m=cap_m, v=18, bev=0.003)
    o.scale = (1.2, 0.9, 1.0)
    o.rotation_euler = (0, -0.12, 0)
    o.parent = pr['body']
    return pr


IDLE_N, ACT_N = 12, 8


def guard_state(mode, f):
    """idle: em guarda, carimbo baixo e prancheta no peito; act: carimba a ficha de contratacao (quando o assessor sai)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.06, -0.14, 0.3 + 0.006 * s), grip_R=(0.05, 0.0, 1.0), hand_L=(0.14, 0.08, 0.34 + 0.006 * s),
                    grip_L=(0.6, -0.2, 0.8), breathe=s, head_yaw=0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    seq = [
        dict(hand_R=(0.08, -0.13, 0.33), hand_L=(0.17, 0.06, 0.32), grip_L=(1.0, -0.3, 0.2)),
        dict(hand_R=(0.12, -0.1, 0.46), hand_L=(0.19, 0.04, 0.31), grip_L=(1.0, -0.4, 0.1)),
        dict(hand_R=(0.16, -0.06, 0.52), hand_L=(0.2, 0.03, 0.31), grip_L=(1.0, -0.4, 0.1)),
        dict(hand_R=(0.2, -0.0, 0.42), hand_L=(0.2, 0.03, 0.3), grip_L=(1.0, -0.4, 0.1), lean=0.08),
        dict(hand_R=(0.2, 0.01, 0.4), hand_L=(0.2, 0.03, 0.3), grip_L=(1.0, -0.4, 0.1), lean=0.1),
        dict(hand_R=(0.16, -0.05, 0.46), hand_L=(0.19, 0.04, 0.31), grip_L=(1.0, -0.3, 0.2), lean=0.05),
        dict(hand_R=(0.1, -0.11, 0.38), hand_L=(0.16, 0.06, 0.33), grip_L=(0.8, -0.2, 0.5)),
        dict(hand_R=(0.07, -0.14, 0.31), hand_L=(0.14, 0.08, 0.34), grip_L=(0.6, -0.2, 0.8)),
    ][f]
    st = dict(grip_R=(0.05, 0.0, 1.0), head_pitch=-0.25, head_yaw=0.1, ph=f / ACT_N)
    st.update(seq)
    return st


def chief_state(mode, f):
    """idle: pasta na mao, carteira junto ao peito; act: estende a carteira funcional para a frente (carteirada)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.12, 0.36 + 0.006 * s), grip_R=(0.4, 0.0, 1.0), hand_L=(0.04, 0.14, 0.3 + 0.004 * s),
                    grip_L=(0.0, 0.0, 1.0), breathe=s, head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.18, ph=ph)
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_R=(0.1 + 0.14 * k, -0.12 + 0.04 * k, 0.36 + 0.08 * k), grip_R=(0.4 + 0.6 * k, 0.0, 1.0 - 0.3 * k), hand_L=(0.04, 0.14, 0.3),
                grip_L=(0.0, 0.0, 1.0), lean=0.06 * k, head_pitch=-0.18 - 0.12 * k, ph=f / ACT_N)


def ghost_state(mode, f):
    """idle: flutua de leve, bracos murchos; act: ergue os bracos e da o 'buuu' (e some do expediente)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.08, -0.13, 0.3 + 0.01 * s), hand_L=(0.08, 0.13, 0.3 - 0.01 * s), breathe=1.4 * s, head_yaw=0.15 * math.sin(TAU * ph),
                    head_pitch=-0.1, head_roll=0.08 * s, offset=(0, 0, 0.03 + 0.015 * s), ph=ph)
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_R=(0.1 + 0.08 * k, -0.15 - 0.03 * k, 0.32 + 0.22 * k), hand_L=(0.1 + 0.08 * k, 0.15 + 0.03 * k, 0.32 + 0.22 * k),
                pole_R=(-0.3, -1.0, -0.2), pole_L=(-0.3, 1.0, -0.2), lean=-0.08 * k, head_pitch=-0.1 - 0.15 * k, offset=(0, 0, 0.03 + 0.04 * k), ph=f / ACT_N)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'qt1': 'qtG', 'qt2': 'qtG', 'qt3': ['qtS', 'qtG'], 'qtL': 'qtL_c', 'qtM': 'qtM_c'},
    'towers': [('qt1', 'Rachadinha N1', build_qt1), ('qt2', 'Rachadinha N2', build_qt2), ('qt3', 'Rachadinha N3', build_qt3),
               ('qtL', 'Chefe de Gabinete', build_qtL), ('qtM', 'Funcionarios Fantasmas', build_qtM)],
    'crews': [crew('qtG', 'Seguranca', build_guard, guard_state), crew('qtS', 'Assessor-chefe', build_sergeant, guard_state),
              crew('qtL_c', 'Chefe (tripulacao)', build_lancer, chief_state), crew('qtM_c', 'Funcionario fantasma', build_monk, ghost_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
