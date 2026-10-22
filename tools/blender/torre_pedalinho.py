"""Pedalinho do Sitio (Ninguem Sobe a Rampa, so a CHAPA=R): no lugar do Lava a Jato, na familia 'cisterna' (motor
'cistern'). O meme publico dos pedalinhos de cisne no lago do sitio: um gramado redondo sobre o lote de concreto de
Brasilia, um laguinho de agua azul com borda de pedras e vitorias-regias, dois pedalinhos de cisne fofos (um branco de
asa vermelha, outro vermelho de asa branca, cada um com a estrelinha da chapa), o deque de madeira, a cerca rustica,
a mangueira carregada de mangas e o canhao de agua de alta pressao em cima de um barril no deque.
  cs1 / cs2 / cs3  laguinho com o deque; o mirante salva-vidas sobre palafitas; a garagem dos pedalinhos (canhao
                   na lanterninha do telhado)
  csF  Lago do Sitio: o lago grande com o chafariz no meio e mais pedalinhos
  csG  Pedalada Fiscal: a caixa d'agua com o canhao no alto, a bomba de volante (a valvula de alivio espirra: ponto
       'steam') e o militante pedalando a bicicleta ergometrica que alimenta a bomba (tripulacao csE)
Tripulacao: csC caseiro (balde d'agua; act: joga a agua) e csE ciclista da pedalada (idle: pedala devagar; act:
pedala com tudo, suando). Camiseta vermelha com a estrela branca, bone vermelho, calca jeans escura.

Nomes de conjuntos, postos, pontos e modos sao os mesmos do torre_cisterna.py (js/sprites.js depende deles). A agua
continua azul. So existe a versao R (a V continua o Lava a Jato do torre_cisterna.py):
  CHAPA=R Blender -b -P tools/blender/torre_pedalinho.py -- render arte/render_r/cisterna [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_pedalinho.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_pedalinho.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, G   # noqa: F811 - lote de Brasilia
from chapa import CHAPA, PAL, cor, estrela, estrela_peito

FAM = 'cisterna'
NOZ_FACE = math.radians(-35)

import lib as _lib
_orig_palette2 = palette2


def palette2():   # noqa: F811 - sitio: grama, agua azul, madeira e os cisnes vermelho e branco
    P = _orig_palette2()
    P['blue'] = mat('azul_balde', '#3d82d8', rough=0.45, var=0.03, bump=0.04)
    P['blue_l'] = mat('azul_claro_sitio', '#a9d2f2', rough=0.35, var=0.02, bump=0.03)
    P['trim'] = mat('friso_cinza', '#dfe4ea', rough=0.35, metal=0.25, var=0.02, bump=0.02)
    P['chrome'] = mat('cromado', '#d9e0e6', rough=0.22, metal=0.75, var=0.02, bump=0.01)
    P['water'] = mat('agua_lago', '#4aa8e4', rough=0.06, var=0.02, bump=0.04, emit=0.16)
    P['water_l'] = mat('agua_lago_clara', '#c4e8fb', rough=0.05, var=0.0, bump=0.02, emit=0.12)
    next(n for n in P['water_l'].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Alpha'].default_value = 0.72
    P['water_r'] = mat('agua_marola', '#e6f6ff', rough=0.2, var=0.0, bump=0.0, emit=0.1)
    P['foam'] = mat('espuma_lago', '#f8fbff', rough=0.55, var=0.03, bump=0.35, sheen=0.3)
    P['hose'] = mat('mangueira', '#2d3447', rough=0.7, var=0.02, bump=0.05)
    P['hose_g'] = mat('mangueira_jardim', '#3f9a4a', rough=0.55, var=0.02, bump=0.05)
    P['rubber_y'] = mat('galocha_amarela', '#f2c230', rough=0.6, var=0.02, bump=0.04)
    P['dial'] = mat('mostrador', '#f6f4ee', rough=0.4, var=0.0, bump=0.0)
    P['conc'] = concrete()
    P['lawn'] = mat('grama_sitio', '#8fbf57', rough=0.92, var=0.05, bump=0.3)
    P['lawn_d'] = mat('grama_sitio_escura', '#77a845', rough=0.92, var=0.06, bump=0.3)
    P['stone'] = mat('pedra_lago', '#c9bfae', rough=0.85, var=0.12, bump=0.3)
    P['stone_l'] = mat('pedra_lago_clara', '#e2dacb', rough=0.85, var=0.1, bump=0.3)
    P['plank'] = mat('tabua_deque', '#c08a57', rough=0.75, var=0.12, bump=0.3)
    P['plank_d'] = mat('tabua_deque_escura', '#94603a', rough=0.78, var=0.1, bump=0.3)
    P['swan_w'] = mat('cisne_branco', '#fbf9f4', rough=0.3, var=0.02, bump=0.02)
    P['swan_r'] = cor('pri', rough=0.3)
    P['beak'] = mat('bico_cisne', '#f49a26', rough=0.35, var=0.02, bump=0.02)
    P['black'] = mat('preto_cisne', '#1e1c1c', rough=0.3, var=0.0, bump=0.0)
    P['leaf'] = mat('folha_mangueira', '#4f8f3c', rough=0.8, var=0.12, bump=0.15)
    P['leaf_l'] = mat('folha_mangueira_clara', '#6eac4c', rough=0.8, var=0.12, bump=0.15)
    P['mango'] = mat('manga', '#f2a127', rough=0.5, var=0.1, bump=0.05)
    P['mango_r'] = mat('manga_vermelha', '#e2542e', rough=0.5, var=0.1, bump=0.05)
    P['lily'] = mat('vitoria_regia', '#5fa24a', rough=0.6, var=0.08, bump=0.08)
    P['lily_f'] = mat('flor_lotus', '#f7a8c4', rough=0.6, var=0.05, bump=0.05)
    P['towel'] = mat('toalha_branca', '#f7f5ef', rough=0.95, var=0.02, bump=0.3, sheen=0.4)
    P['sneaker'] = mat('tenis_branco', '#f1efe8', rough=0.6, var=0.02, bump=0.04)
    P['bike_d'] = mat('bicicleta_preta', '#2a2a30', rough=0.45, var=0.02, bump=0.02)
    # cores da chapa (vermelho e branco): estrutura, detalhes e o tom escuro
    P['cA'] = cor('pri')
    P['cB'] = cor('sec')
    P['cD'] = cor('escuro')
    P['red_cloth'] = cor('pri', rough=0.8, sheen=0.4)
    P['white_cloth'] = mat('pano_branco_estrela', '#ffffff', rough=0.7, var=0.0, bump=0.02, sheen=0.3)
    P['camisa'], P['calca'], P['bone'], P['gola'] = cor('camisa'), cor('calca'), cor('bone'), cor('gola')
    P['teal'] = P['cA']
    P['_emblem'] = 'drop'
    return P


_lib.palette2 = palette2


# ---------------------------------------------------------------- agua
def water_disc(root, P, tag, x, y, z, r, ry=None, ripple=0.006):
    """Espelho d'agua com ondinhas (vertices animados) e um brilho que gira."""
    ry = ry or r

    def shape(u, v, co):
        a = TAU * u
        return Vector((r * v * math.cos(a), ry * v * math.sin(a), 0))
    w = cloth_grid(root, tag, 1, 1, 28, 6, [P['water']], shape=shape, thick=0.0)
    w.location = (x, y, z)

    def wave(co, ph):
        d = math.hypot(co.x / r, co.y / ry)
        return Vector((co.x, co.y, ripple * math.sin(TAU * (ph * 2 - d * 2.2)) * (1 - d * 0.6)))
    register_cloth(w, wave)
    hp = empty(root, tag + '_brilhoPivo', loc=(x, y, z + 0.004))
    hl = sphere(root, tag + '_brilho', 1.0, (r * 0.45, 0, 0), scale=(0.16 * r, 0.05 * r, 0.002), m=P['water_l'], seg=10)
    hl.parent = hp
    hp.scale = (1.0, ry / r, 1.0)
    register_anim(hp, spin('Z', sym=1, turns=1))
    return w


def spray(root, P, tag, p0, p1, w0=0.02, w1=0.14, arc=0.12, m=None, waves=3, nv=10):
    """Jato d'agua em leque: faixa que abre de p0 ate p1 com barriga para cima (arc) e ondas correndo (animado)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0)
    side = Vector((-d.y, d.x, 0))
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))

    def shape(u, v, co):
        p = p0.lerp(p1, v) + Vector((0, 0, arc * math.sin(math.pi * v)))
        return p + side * ((u - 0.5) * (w0 + (w1 - w0) * v))
    f = cloth_grid(root, tag, 1, 1, 3, nv, [m or P['water_l']], shape=shape, thick=0.008)

    def flow(co, ph):
        v = max(0.0, min(1.0, (co - p0).dot(d) / max(1e-6, d.length_squared)))
        return co + Vector((0, 0, 0.012 * math.sin(TAU * (ph * waves - v * 2.5)) * v))
    register_cloth(f, flow)
    return f


def drops(root, P, tag, p, n=5, spread=0.08, seed=5):
    """Gotinhas espirrando (balancam)."""
    rr = random.Random(seed)
    for k in range(n):
        q = (p[0] + rr.uniform(-spread, spread), p[1] + rr.uniform(-spread, spread), p[2] + rr.uniform(-spread * 0.5, spread))
        o = sphere(root, f'{tag}_gota{k}', rr.uniform(0.012, 0.022), q, scale=(1, 1, 1.3), m=P['water_l'], seg=8)
        register_anim(o, bob(amp=0.02, turns=2, axis='Z'))


def ripple_ring(root, P, tag, x, y, z, rx, ry, rot=0.0):
    """Marola branca em volta de quem boia (anel achatado na linha d'agua)."""
    c, sn = math.cos(rot), math.sin(rot)
    pts = []
    for k in range(28):
        a = TAU * k / 28
        u, v = rx * math.cos(a), ry * math.sin(a)
        pts.append((x + u * c - v * sn, y + u * sn + v * c, z))
    return tube(root, tag, pts, 0.01, P['water_r'], segs=5, closed=True)


# ---------------------------------------------------------------- o sitio: gramado, lago, deque, cerca, mangueira, lampiao
def lawn(root, P, tag, r=0.69):
    """Gramado redondo do sitio por cima da laje (a borda de concreto e a faixa da chapa continuam a mostra)."""
    cyl(root, tag + '_gramado', r, 0.014, (0, 0, G + 0.006), m=P['lawn'], v=56, bev=0.006)
    rr = random.Random(len(tag))
    for k in range(7):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0.3, r - 0.06)
        cx_, cy_ = d * math.cos(a), d * math.sin(a)
        for j in range(4):
            b = TAU * j / 4 + rr.uniform(-0.4, 0.4)
            tube(root, f'{tag}_tufo{k}_{j}', [(cx_, cy_, G + 0.012), (cx_ + 0.022 * math.cos(b), cy_ + 0.022 * math.sin(b), G + 0.05)], 0.008, P['lawn_d'], segs=4,
                 rfun=lambda t: 0.009 * (1 - t) + 0.001)


def pond(root, P, tag, cx, cy, rx, ry, skip=None, pads=(), seed=3, ripple=0.005):
    """Laguinho: espelho d'agua azul com borda de pedras arredondadas (skip(x, y) pula as que ficam embaixo do deque)
    e vitorias-regias (x, y, raio, flor)."""
    water_disc(root, P, tag + '_agua', cx, cy, G + 0.016, rx, ry=ry, ripple=ripple)
    # fundo um pouco mais escuro na beirada (da profundidade ao espelho)
    o = cyl(root, tag + '_leito', 1.0, 0.01, (cx, cy, G + 0.011), m=mat('leito_lago', '#2f7fbf', rough=0.4, var=0.0, bump=0.0), v=40, bev=0.0)
    o.scale = (rx + 0.01, ry + 0.01, 1.0)
    rr = random.Random(seed)
    per = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
    n = int(per / 0.062)
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.04, 0.04)
        x = cx + (rx + 0.018) * math.cos(a)
        y = cy + (ry + 0.018) * math.sin(a)
        if skip and skip(x, y):
            continue
        sphere(root, f'{tag}_pedra{k}', rr.uniform(0.03, 0.04), (x, y, G + 0.018), scale=(1.25, 1.0, 0.6), rot=(0, 0, a),
               m=P['stone'] if k % 3 else P['stone_l'], seg=10)
    for k, (x, y, r, flor) in enumerate(pads):
        cyl(root, f'{tag}_folhaLago{k}', r, 0.006, (x, y, G + 0.02), m=P['lily'], v=18, bev=0.002)
        if flor:
            for j in range(5):
                a = TAU * j / 5
                sphere(root, f'{tag}_petala{k}_{j}', 0.012, (x + 0.012 * math.cos(a), y + 0.012 * math.sin(a), G + 0.032), scale=(1.3, 0.8, 0.7),
                       rot=(0, 0, a), m=P['lily_f'], seg=8)
            sphere(root, f'{tag}_miolo{k}', 0.008, (x, y, G + 0.038), m=P['rubber_y'], seg=8)


def deck(root, P, tag, cx, cy, L, W, rot=0.0, z=G + 0.05, posts=True, rails=False):
    """Deque de tabuas (L ao longo do X local, W de largura) apoiado em estacas; devolve a altura do piso."""
    with grupo(root, tag, loc=(cx, cy, 0), rot=(0, 0, rot)) as e:
        n = max(2, int(L / 0.058))
        pw = L / n
        rr = random.Random(int(L * 100))
        for k in range(n):
            x = -L / 2 + pw * (k + 0.5)
            box(root, f'{tag}_tabua{k}', (pw - 0.008, W, 0.022), (x, 0, z - 0.011 + rr.uniform(-0.002, 0.002)), m=P['plank'] if k % 3 else P['plank_d'], bev=0.005)
        for sy in (-1, 1):
            box(root, f'{tag}_viga{sy}', (L, 0.028, 0.03), (0, sy * (W / 2 - 0.02), z - 0.035), m=P['plank_d'], bev=0.006)
        if posts:
            nx = max(2, int(L / 0.32) + 1)
            for i in range(nx):
                x = -L / 2 + 0.03 + (L - 0.06) * i / (nx - 1)
                for sy in (-1, 1):
                    cyl(root, f'{tag}_estaca{i}{sy}', 0.018, z - G + 0.01, (x, sy * (W / 2 - 0.02), G + (z - G) / 2 - 0.005), m=P['plank_d'], v=10, bev=0.004)
        if rails:
            for sy in (-1, 1) if rails == 2 else (1,):
                for i in range(int(L / 0.2) + 1):
                    x = -L / 2 + 0.02 + (L - 0.04) * i / int(L / 0.2)
                    tube(root, f'{tag}_balaustre{i}{sy}', [(x, sy * (W / 2 - 0.015), z), (x, sy * (W / 2 - 0.015), z + 0.12)], 0.011, P['plank_d'], segs=6)
                tube(root, f'{tag}_corrimao{sy}', [(-L / 2 + 0.02, sy * (W / 2 - 0.015), z + 0.12), (L / 2 - 0.02, sy * (W / 2 - 0.015), z + 0.12)], 0.012, P['plank'], segs=6)
    return z


def fence(root, P, tag, r, a0, a1, n, h=0.15, seed=2):
    """Cerca rustica de madeira (mourao e duas tabuas) num arco de raio r, dos angulos a0 a a1 (graus)."""
    rr = random.Random(seed)
    pts = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / (n - 1))
        x, y = r * math.cos(a), r * math.sin(a)
        pts.append((x, y))
        box(root, f'{tag}_mourao{i}', (0.032, 0.032, h + 0.03), (x, y, G + (h + 0.03) / 2), rot=(rr.uniform(-0.06, 0.06), rr.uniform(-0.06, 0.06), a),
            m=P['plank_d'], bev=0.008)
    for j, zz in enumerate((G + h * 0.45, G + h * 0.85)):
        tube(root, f'{tag}_ripa{j}', [(x * 0.995, y * 0.995, zz + rr.uniform(-0.006, 0.006)) for x, y in pts], 0.011, P['plank'], segs=5)


def mango_tree(root, P, tag, x, y, s=1.0, seed=4):
    """Mangueira (arvore) do sitio: tronco torto, copa de bolotas verdes e as mangas penduradas."""
    rr = random.Random(seed)
    tube(root, tag + '_tronco', [(x, y, G), (x + 0.03 * s, y, G + 0.25 * s), (x - 0.01 * s, y + 0.01 * s, G + 0.45 * s)], 0.05 * s, P['wood'], segs=10,
         rfun=lambda t: s * (0.052 - 0.022 * t))
    for k in range(3):
        a = TAU * k / 3 + 0.5
        tube(root, f'{tag}_galho{k}', [(x, y, G + 0.4 * s), (x + 0.15 * s * math.cos(a), y + 0.12 * s * math.sin(a), G + 0.56 * s)], 0.018 * s, P['wood'], segs=6)
    c = Vector((x, y, G + 0.62 * s))
    blobs = [((0, 0, 0.08), 0.2), ((0.15, -0.05, -0.02), 0.15), ((-0.15, 0.02, -0.01), 0.16), ((0.04, 0.13, 0.0), 0.15), ((-0.05, -0.12, 0.0), 0.15),
             ((0.08, 0.04, 0.17), 0.13), ((-0.08, 0.0, 0.14), 0.13)]
    for k, (o, r) in enumerate(blobs):
        sphere(root, f'{tag}_copa{k}', r * s, tuple(c + Vector(o) * s), scale=(1, 1, 0.85), m=P['leaf'] if k % 2 else P['leaf_l'], seg=16)
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.42 + rr.uniform(-0.12, 0.12)   # do lado da camera, penduradas embaixo da copa
        d = rr.uniform(0.16, 0.24) * s
        mx, my, mz = x + d * math.cos(a), y + d * math.sin(a) * 0.8, G + (0.44 + rr.uniform(-0.02, 0.03)) * s
        tube(root, f'{tag}_cabinho{k}', [(mx, my, mz + 0.02 * s), (mx, my, mz + 0.06 * s)], 0.004 * s, P['wood'], segs=4)
        sphere(root, f'{tag}_manga{k}', 0.03 * s, (mx, my, mz), scale=(0.8, 0.8, 1.15), m=P['mango'] if k % 3 else P['mango_r'], seg=10)


def lantern_post(root, P, tag, x, y, h=0.42, face=0.0):
    """Lampiao num poste de madeira com o braco para `face` (radianos); devolve o centro da luz."""
    d = Vector((math.cos(face), math.sin(face), 0))
    tube(root, tag + '_poste', [(x, y, G), (x, y, G + h)], 0.018, P['plank_d'], segs=8)
    tube(root, tag + '_braco', [(x, y, G + h - 0.03), (x + d.x * 0.1, y + d.y * 0.1, G + h - 0.03)], 0.009, P['iron_d'], segs=6)
    lx, ly, lz = x + d.x * 0.1, y + d.y * 0.1, G + h - 0.1
    tube(root, tag + '_gancho', [(lx, ly, G + h - 0.03), (lx, ly, lz + 0.05)], 0.004, P['iron_d'], segs=4)
    cyl(root, tag + '_chapeu', 0.04, 0.02, (lx, ly, lz + 0.045), r2=0.012, m=P['cA'], v=12, bev=0.004)
    sphere(root, tag + '_vidro', 0.03, (lx, ly, lz), scale=(1, 1, 1.25), m=P['glow'], seg=14)
    cyl(root, tag + '_baseLampiao', 0.026, 0.014, (lx, ly, lz - 0.04), m=P['iron_d'], v=12, bev=0.003)
    cyl(root, tag + '_pe', 0.04, 0.03, (x, y, G + 0.015), m=P['conc'], v=12, bev=0.006)
    return (lx, ly, lz)


def life_ring(root, P, tag, loc, rot=(0, 0, 0), r=0.06):
    """Boia salva-vidas vermelha e branca (quatro gomos)."""
    e = empty(root, tag + '_piv', loc=loc, rot=rot)
    for k in range(4):
        a0 = TAU * k / 4
        pts = [(r * math.cos(a0 + TAU / 4 * t / 6), 0, r * math.sin(a0 + TAU / 4 * t / 6)) for t in range(7)]
        kids(e, tube(root, f'{tag}_gomo{k}', pts, r * 0.32, P['cA'] if k % 2 else P['white_cloth'], segs=10))
    return e


def star_shape(R, cx, cz, y):
    """Leque de 10 colunas (as 10 quinas da estrela) no plano XZ do pano: a malha fecha a estrela exata."""
    def fn(u, v, co):
        k = int(round(u * 10))
        a = math.pi / 2 + TAU * k / 10
        r = R * (1.0 if k % 2 == 0 else 0.42) * v
        return Vector((cx + r * math.cos(a), y, cz + r * math.sin(a)))
    return fn


def flag_pole(root, P, tag, x, y, z, h=0.36, w=0.24):
    """Mastro com a bandeira da chapa (vermelha com a estrela branca dos dois lados), balancando ao vento."""
    tube(root, tag + '_mastro', [(x, y, z), (x, y, z + h)], 0.01, P['steel'], segs=8)
    sphere(root, tag + '_topo', 0.018, (x, y, z + h + 0.01), m=P['rubber_y'], seg=10)
    fh = w * 0.68
    wave = flag_wave(w, amp=0.045, cycles=1, waves=1.1)
    objs = [cloth_grid(root, tag + '_pano', w, fh, 14, 4, [P['red_cloth']], thick=0.008)]
    for sg in (-1, 1):
        objs.append(cloth_grid(root, f'{tag}_estrela{sg}', w, fh, 10, 2, [P['white_cloth']], shape=star_shape(fh * 0.36, w / 2, -fh / 2, sg * 0.008), thick=0.004))
    for o in objs:
        o.location = (x + 0.01, y, z + h - 0.02)
        register_cloth(o, wave)
    return objs


# ---------------------------------------------------------------- o pedalinho de cisne
def swan(root, P, tag, x, y, rot=0.0, s=0.7, red=False, z=G + 0.016, ph=0.0, anim=True):
    """Pedalinho de cisne fofo (frente para +X local): casco oval, banco de dois lugares, asas levantadas com a
    estrelinha, pescoco em S, cabeca com bico laranja. red=True: corpo vermelho de asa branca (estrela vermelha)."""
    body = P['swan_r'] if red else P['swan_w']
    wing = P['white_cloth'] if red else P['swan_r']
    star_m = P['cA'] if red else None
    seat = P['swan_w'] if red else P['swan_r']
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot)) as e:
        S = lambda *v: tuple(c * s for c in v)
        o = lathe(root, tag + '_casco', [(z_ * s, rx * s, ry * s, xo * s) for z_, rx, ry, xo in
                                          ((-0.05, 0.13, 0.085, -0.01), (0.0, 0.18, 0.118, -0.01), (0.05, 0.2, 0.13, -0.015), (0.09, 0.195, 0.125, -0.02),
                                           (0.11, 0.175, 0.11, -0.02))], body, segs=24, lv=2, caps=True)
        box(root, tag + '_banco', S(0.11, 0.17, 0.03), S(-0.03, 0, 0.122), m=seat, bev=0.01 * s)
        box(root, tag + '_encosto', S(0.03, 0.17, 0.085), S(-0.1, 0, 0.16), rot=(0, 0.28, 0), m=seat, bev=0.01 * s)
        for sy in (-1, 1):
            sphere(root, f'{tag}_asa{sy}', 1.0, S(-0.04, sy * 0.122, 0.105), scale=S(0.15, 0.04, 0.07), rot=(sy * 0.35, -0.3, 0), m=wing, seg=16)
            estrela(root, f'{tag}_estrelaAsa{sy}', 0.032 * s, 0.006 * s, loc=S(-0.03, sy * 0.165, 0.11), rot=(sy * 0.35, -0.3, 0), m=star_m)
        sphere(root, tag + '_cauda', 1.0, S(-0.2, 0, 0.115), scale=S(0.065, 0.07, 0.035), rot=(0, -0.55, 0), m=body, seg=12)
        tube(root, tag + '_pescoco', [S(0.14, 0, 0.06), S(0.21, 0, 0.15), S(0.2, 0, 0.25), S(0.17, 0, 0.31), S(0.19, 0, 0.36)], 0.04 * s, body, segs=12,
             rfun=lambda t: s * (0.044 - 0.018 * t))
        sphere(root, tag + '_cabeca', 0.045 * s, S(0.205, 0, 0.375), scale=(1.2, 0.95, 0.95), m=body, seg=16)
        cyl(root, tag + '_bico', 0.019 * s, 0.06 * s, S(0.27, 0, 0.362), r2=0.006 * s, rot=(0, math.pi / 2 + 0.28, 0), m=P['beak'], v=12, bev=0.004 * s)
        sphere(root, tag + '_bicoBase', 0.014 * s, S(0.243, 0, 0.382), m=P['black'], seg=8)
        for sy in (-1, 1):
            sphere(root, f'{tag}_olho{sy}', 0.0105 * s, S(0.228, sy * 0.036, 0.39), m=P['black'], seg=8)
            sphere(root, f'{tag}_brilhoOlho{sy}', 0.0035 * s, S(0.233, sy * 0.044, 0.395), m=P['white_cloth'], seg=6)
            sphere(root, f'{tag}_bochecha{sy}', 0.012 * s, S(0.222, sy * 0.04, 0.37), scale=(1, 0.4, 0.7), m=mat('bochecha_cisne', '#ff9a9a', rough=0.6, var=0, bump=0), seg=8)
    if anim:
        def fn(o, mb, p, ph=ph):
            a = TAU * (p + ph)
            o.matrix_basis = Matrix.Translation((0, 0, 0.006 * math.sin(a))) @ mb @ Matrix.Rotation(0.05 * math.sin(a + 1.2), 4, 'X') @ \
                Matrix.Rotation(0.035 * math.sin(a), 4, 'Z')
        register_anim(e, fn)
    ripple_ring(root, P, tag + '_marola', x, y, z + 0.002, 0.2 * s, 0.13 * s, rot=rot)
    return e


def barrel(root, P, tag, x, y, z0, zt, r=0.1, reel=True):
    """Barril de madeira com cintas vermelhas (pedestal do canhao) e o carretel de mangueira do lado; topo em zt."""
    h = zt - z0
    lathe(root, tag, [(z0, r * 0.86, r * 0.86), (z0 + h * 0.5, r, r), (zt - 0.012, r * 0.86, r * 0.86)], P['plank'], segs=22, lv=1, caps=True)
    for k, t in enumerate((0.16, 0.84)):
        rr_ = r * (0.86 + 0.14 * math.sin(math.pi * t))
        torus(root, f'{tag}_cinta{k}', (0, 0, 0), rr_ + 0.004, 0.009, P['cA'], n=24, segs=5).location = (x, y, z0 + h * t)
    bpy.data.objects[tag].location = (x, y, 0)
    cyl(root, tag + '_tampa', r * 0.88, 0.014, (x, y, zt - 0.007), m=P['plank_d'], v=22, bev=0.004)
    estrela(root, tag + '_estrela', 0.035, 0.008, loc=(x, y - r - 0.002, z0 + h * 0.5), rot=(0, 0, 0))
    if reel:
        for k in range(3):
            torus(root, f'{tag}_mangueira{k}', (x + r + 0.02 + 0.014 * k, y, z0 + h * 0.5), 0.06 - 0.004 * k, 0.013, P['hose'], axis='X', n=20, segs=6)
        cyl(root, tag + '_carretel', 0.026, 0.06, (x + r + 0.03, y, z0 + h * 0.5), rot=(0, math.pi / 2, 0), m=P['chrome'], v=12, bev=0.004)
    return zt


def L2W(c, a, p):
    """Ponto do grupo (centro c, giro a em Z) para as coordenadas da torre."""
    x, y, z = p
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a), z)


# ---------------------------------------------------------------- canhao de agua de alta pressao (conjunto separado: espelha e recua)
def build_nozzle(P, root, size=1.0, big=0):
    """Pistola de agua num pe giratorio: corpo vermelho com a estrela branca e o manometro, lanca cromada, bico e a
    mangueira; aponta +X."""
    tag = root['set']
    s = size
    piv = empty(root, tag + '_giro', rot=(0, 0, NOZ_FACE))
    kids(piv, cyl(root, tag + '_base', 0.085 * s, 0.06 * s, (0, 0, 0.03 * s), r2=0.07 * s, m=P['cD'], v=18, bev=0.008))
    kids(piv, cyl(root, tag + '_eixo', 0.035 * s, 0.1 * s, (0, 0, 0.1 * s), m=P['chrome'], v=14, bev=0.006))
    rec = empty(root, tag + '_recuo', loc=(0, 0, 0.16 * s), parent=piv)
    tilt = empty(root, tag + '_incl', parent=rec, rot=(0, math.radians(-18), 0))
    L = (0.34 + 0.08 * big) * s
    with grupo(root, tag + '_pistola', parent=tilt):
        box(root, tag + '_corpo', (0.16 * s, 0.075 * s, 0.085 * s), (-0.03 * s, 0, 0), m=P['cA'], bev=0.03 * s)
        box(root, tag + '_cabo', (0.04 * s, 0.05 * s, 0.1 * s), (-0.07 * s, 0, -0.075 * s), rot=(0, 0.3, 0), m=P['hose'], bev=0.012 * s)
        box(root, tag + '_gatilho', (0.016 * s, 0.02 * s, 0.04 * s), (-0.035 * s, 0, -0.06 * s), rot=(0, 0.2, 0), m=P['rubber_y'], bev=0.005 * s)
        tube(root, tag + '_lanca', [(0.04 * s, 0, 0.01 * s), (L * 0.88, 0, 0.01 * s)], 0.016 * s, P['chrome'], segs=10)
        if big >= 1:
            tube(root, tag + '_lanca2', [(0.04 * s, 0, -0.025 * s), (L * 0.5, 0, -0.025 * s), (L * 0.84, 0, 0.0)], 0.012 * s, P['chrome'], segs=8)
            cyl(root, tag + '_espumador', 0.034 * s, 0.09 * s, (0.13 * s, 0, -0.06 * s), rot=(0, math.pi / 2, 0), m=P['foam'], v=16, bev=0.012 * s)
            cyl(root, tag + '_espumadorTampa', 0.036 * s, 0.02 * s, (0.08 * s, 0, -0.06 * s), rot=(0, math.pi / 2, 0), m=P['cB'], v=16, bev=0.004 * s)
        tip_r = (0.028 + 0.006 * big) * s
        cyl(root, tag + '_bico', tip_r, 0.07 * s, (L * 0.9 + 0.025 * s, 0, 0.005 * s), r2=tip_r * 0.7, rot=(0, math.pi / 2, 0), m=P['cA'], v=16, bev=0.006 * s)
        torus(root, tag + '_bicoAnel', (L * 0.88, 0, 0.005 * s), tip_r * 1.05, 0.006 * s, P['rubber_y'], axis='X', n=14, segs=5)
        cyl(root, tag + '_boca', tip_r * 0.55, 0.012 * s, (L * 0.9 + 0.062 * s, 0, 0.005 * s), rot=(0, math.pi / 2, 0), m=P['water'], v=14, bev=0)
        cyl(root, tag + '_manometro', 0.026 * s, 0.014 * s, (-0.02 * s, -0.042 * s, 0.035 * s), rot=(math.pi / 2, 0, 0), m=P['dial'], v=16, bev=0.003 * s)
        torus(root, tag + '_manometroAro', (-0.02 * s, -0.049 * s, 0.035 * s), 0.026 * s, 0.005 * s, P['chrome'], axis='Y', n=16, segs=5)
        tube(root, tag + '_ponteiro', [(-0.02 * s, -0.051 * s, 0.035 * s), (-0.004 * s, -0.051 * s, 0.045 * s)], 0.003 * s, P['red'], segs=4)
        estrela(root, tag + '_estrelaCorpo', 0.02 * s, 0.006 * s, loc=(-0.075 * s, -0.04 * s, -0.008 * s))
    hose = tube(root, tag + '_mangueira', [(-0.1 * s, 0, 0.0), (-0.16 * s, 0.03 * s, -0.06 * s), (-0.12 * s, 0.05 * s, -0.13 * s), (-0.03 * s, 0.04 * s, -0.15 * s)],
                0.014 * s, P['hose'], segs=8)
    kids(rec, hose)
    return {'piv': piv, 'rec': rec, 'tilt': tilt, 'L': L, 's': s}


def nozzle_tip(size=1.0, big=0):
    """Boca do canhao em repouso (BU relativas ao posto, com o CREW_BOOST): origem do jato no jogo (DATA.TOWER_TOP)."""
    s = size
    L = (0.34 + 0.08 * big) * s
    p = Vector((0, 0, 0.16 * s)) + Matrix.Rotation(math.radians(-18), 3, 'Y') @ Vector((L * 0.9 + 0.07 * s, 0, 0.005 * s))
    return Matrix.Rotation(NOZ_FACE, 3, 'Z') @ p * CREW_BOOST


def nozzle_points(parts, tl):
    bpy.context.view_layer.update()
    s = parts['s']
    m = parts['tilt'].matrix_world @ Vector((parts['L'] * 0.9 + 0.07 * s, 0, 0.005 * s))
    return {'points': {'muzzle': project(m, tl)}}


def pose_nozzle(parts, f):
    rec = [0.0, -0.05, -0.035, -0.02, -0.01, -0.004, 0.0, 0.0][f] if f is not None else 0.0
    parts['rec'].location = (rec * parts['s'], 0, 0.16 * parts['s'])
    parts['tilt'].rotation_euler = (0, math.radians(-18 - 60 * abs(rec)), 0)


NOZ_N = 8


def nozzle_spec(key, label, **kw):
    return {'key': key, 'label': label, 'build': lambda P, root: build_nozzle(P, root, **kw), 'boost': CREW_BOOST, 'extra': nozzle_points,
            'pose0': lambda parts, P, root: pose_nozzle(parts, None),
            'modes': [('fire', NOZ_N, lambda parts, P, root, f: pose_nozzle(parts, f))]}


def top_of(slot, **kw):
    t = nozzle_tip(**kw)
    return (slot[0], slot[1], slot[2] + t.z)


# ---------------------------------------------------------------- nivel 1: o laguinho com dois pedalinhos e o deque
def build_cs1(P, root):
    plot(root, P, 'cs1')
    lawn(root, P, 'cs1')
    lights = []
    zd = G + 0.05
    pond(root, P, 'cs1_lago', -0.04, 0.06, 0.56, 0.38, skip=lambda x, y: y < -0.27, seed=3,
         pads=[(-0.42, 0.14, 0.05, True), (-0.34, 0.3, 0.04, False), (0.4, 0.3, 0.045, True), (0.08, 0.36, 0.035, False)])
    deck(root, P, 'cs1_deque', 0.0, -0.42, 1.3, 0.2, z=zd)
    swan(root, P, 'cs1_cisneA', -0.22, 0.1, rot=math.radians(-20), s=0.72, red=False, ph=0.0)
    swan(root, P, 'cs1_cisneB', 0.24, 0.16, rot=math.radians(200), s=0.72, red=True, ph=0.4)
    zt = barrel(root, P, 'cs1_barril', 0.5, -0.38, zd, G + 0.325)
    lp = lantern_post(root, P, 'cs1_lampiao', 0.64, -0.12, h=0.46, face=math.radians(160))
    lights.append((lp, '#ffc04a', 10.0, 1))
    mango_tree(root, P, 'cs1_mangueira', -0.5, 0.48, s=0.9)
    fence(root, P, 'cs1_cerca', 0.66, 15, 110, 9)
    slot = (0.5, -0.38, zt)
    return {'slots': [slot, (-0.52, -0.46, zd)], 'lights': lights, 'points': {'top': top_of(slot, size=0.85)}}


# ---------------------------------------------------------------- nivel 2: o mirante salva-vidas sobre palafitas, tres pedalinhos
def lookout(root, P, tag, cx, cy, zp, s=0.34, rot=0.0, lights=None):
    """Mirante salva-vidas: palafitas de madeira com travas em X, a casinha vermelha de friso branco e janela, o deque
    do teto com guarda-corpo (onde fica o canhao), escada na frente e a boia pendurada."""
    zc0 = zp - 0.3
    with grupo(root, tag, loc=(cx, cy, 0), rot=(0, 0, rot)) as e:
        h = s / 2
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(root, f'{tag}_palafita{sx}{sy}', (0.04, 0.04, zc0 - G + 0.02), (sx * (h - 0.02), sy * (h - 0.02), G + (zc0 - G) / 2), m=P['plank_d'], bev=0.008)
        for k, (ax, ay, L, rz) in enumerate(((0, -h + 0.02, s, 0), (0, h - 0.02, s, 0), (-h + 0.02, 0, s, math.pi / 2), (h - 0.02, 0, s, math.pi / 2))):
            for sg in (-1, 1):
                ang = math.atan2(zc0 - G - 0.06, L - 0.04)
                box(root, f'{tag}_trava{k}{sg}', (math.hypot(L - 0.04, zc0 - G - 0.06), 0.018, 0.022), (ax, ay, (G + zc0) / 2),
                    rot=(0, sg * ang, rz), m=P['plank'], bev=0.004)
        box(root, tag + '_piso', (s + 0.04, s + 0.04, 0.03), (0, 0, zc0 + 0.015), m=P['plank_d'], bev=0.006)
        # casinha
        ch = zp - zc0 - 0.05
        box(root, tag + '_casinha', (s - 0.03, s - 0.03, ch), (0, 0, zc0 + 0.03 + ch / 2), m=P['cA'], bev=0.02)
        for zz in (zc0 + 0.04, zc0 + 0.03 + ch - 0.01):
            box(root, f'{tag}_friso{zz:.2f}', (s - 0.015, s - 0.015, 0.022), (0, 0, zz), m=P['white_cloth'], bev=0.006)
        box(root, tag + '_janela', (0.14, 0.02, 0.1), (0.04, -h + 0.008, zc0 + 0.03 + ch * 0.6), m=P['window'], bev=0.006)
        box(root, tag + '_janelaMoldura', (0.17, 0.016, 0.13), (0.04, -h + 0.012, zc0 + 0.03 + ch * 0.6), m=P['white_cloth'], bev=0.006)
        box(root, tag + '_janela2', (0.02, 0.12, 0.09), (-h + 0.008, 0.02, zc0 + 0.03 + ch * 0.6), m=P['window'], bev=0.006)
        estrela(root, tag + '_estrela', 0.04, 0.01, loc=(-0.09, -h + 0.006, zc0 + 0.03 + ch * 0.55))
        # teto-deque com guarda-corpo branco e o tampo do canhao
        box(root, tag + '_teto', (s + 0.06, s + 0.06, 0.03), (0, 0, zp - 0.015), m=P['plank'], bev=0.008)
        rail = []
        for k in range(12):
            t = k / 12
            side = int(t * 4)
            u = t * 4 - side
            cx_, cy_ = [(-1, -1), (1, -1), (1, 1), (-1, 1)][side]
            nx_, ny_ = [(-1, -1), (1, -1), (1, 1), (-1, 1)][(side + 1) % 4]
            px = (cx_ + (nx_ - cx_) * u) * (h + 0.015)
            py = (cy_ + (ny_ - cy_) * u) * (h + 0.015)
            rail.append((px, py))
            tube(root, f'{tag}_balaustre{k}', [(px, py, zp), (px, py, zp + 0.1)], 0.009, P['white_cloth'], segs=6)
        tube(root, tag + '_corrimao', [(x, y, zp + 0.1) for x, y in rail], 0.012, P['cA'], segs=6, closed=True)
        cyl(root, tag + '_plataforma', 0.11, 0.025, (0, 0, zp + 0.012), m=P['chrome'], v=20, bev=0.006)
        # escada na frente (lado direito) e a boia
        for sg in (-1, 1):
            tube(root, f'{tag}_escadaLado{sg}', [(h - 0.03 + sg * 0.05, -h - 0.16, G), (h - 0.03 + sg * 0.05, -h - 0.01, zc0 + 0.02)], 0.011, P['plank'], segs=6)
        for k in range(6):
            t = (k + 0.5) / 6
            tube(root, f'{tag}_degrau{k}', [(h - 0.08, -h - 0.16 + 0.15 * t, G + (zc0 - G) * t), (h + 0.02, -h - 0.16 + 0.15 * t, G + (zc0 - G) * t)], 0.008,
                 P['plank_d'], segs=5)
    life_ring(root, P, tag + '_boia', L2W((cx, cy), rot, (-0.06, -h - 0.012, zc0 - 0.08)), rot=(0, 0, rot))
    if lights is not None:
        lp = L2W((cx, cy), rot, (h + 0.06, -0.06, zc0 + 0.03 + ch * 0.7))
        tube(root, tag + '_bracoLuz', [L2W((cx, cy), rot, (h - 0.01, -0.06, lp[2] + 0.02)), (lp[0], lp[1], lp[2] + 0.02)], 0.008, P['iron_d'], segs=5)
        sphere(root, tag + '_luz', 0.028, lp, m=P['glow'], seg=12)
        cyl(root, tag + '_luzChapeu', 0.034, 0.016, (lp[0], lp[1], lp[2] + 0.035), r2=0.01, m=P['cA'], v=12, bev=0.003)
        lights.append((lp, '#ffc04a', 10.0, 1))
    return e


def build_cs2(P, root):
    plot(root, P, 'cs2')
    lawn(root, P, 'cs2')
    lights = []
    zp = G + 0.92
    cx, cy = 0.24, -0.02
    pond(root, P, 'cs2_lago', -0.2, 0.1, 0.5, 0.42, skip=lambda x, y: (x > 0.0 and -0.3 < y < 0.0), seed=5,
         pads=[(-0.5, 0.24, 0.05, True), (-0.3, 0.38, 0.04, False), (-0.04, 0.4, 0.045, True), (-0.56, 0.0, 0.035, False)])
    zd = deck(root, P, 'cs2_deque', 0.22, -0.2, 0.62, 0.2, rot=math.radians(-10), z=G + 0.05)
    deck(root, P, 'cs2_pier', -0.02, -0.04, 0.34, 0.15, rot=math.radians(80), z=G + 0.05)
    lookout(root, P, 'cs2_mirante', cx, cy, zp, s=0.34, rot=math.radians(-12), lights=lights)
    swan(root, P, 'cs2_cisneA', -0.42, 0.06, rot=math.radians(-30), s=0.72, red=False, ph=0.0)
    swan(root, P, 'cs2_cisneB', -0.14, 0.3, rot=math.radians(190), s=0.72, red=True, ph=0.35)
    swan(root, P, 'cs2_cisneC', -0.2, -0.14, rot=math.radians(10), s=0.66, red=True, ph=0.7)
    mango_tree(root, P, 'cs2_mangueira', 0.5, 0.42, s=0.9, seed=6)
    fence(root, P, 'cs2_cerca', 0.66, 100, 165, 7, seed=4)
    slot = (cx, cy, zp + 0.025)
    return {'slots': [slot], 'lights': lights, 'points': {'top': top_of(slot, size=1.0, big=1)}, 'margin': (0.2, 0.95, 0.2, 0.3)}


# ---------------------------------------------------------------- nivel 3: a garagem dos pedalinhos (canhao na lanterninha do telhado)
def planks_wall(root, P, tag, x0, y0, x1, y1, z0, z1, n=None, alt=None):
    """Parede de tabuas verticais vermelhas (alternando o tom) de (x0, y0) a (x1, y1)."""
    L = math.hypot(x1 - x0, y1 - y0)
    n = n or max(2, int(L / 0.06))
    ang = math.atan2(y1 - y0, x1 - x0)
    alt = alt or mat('tabua_vermelha_escura', '#b51f22', rough=0.6, var=0.04, bump=0.12)
    for k in range(n):
        t = (k + 0.5) / n
        box(root, f'{tag}_{k}', (L / n - 0.006, 0.035, z1 - z0), (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, (z0 + z1) / 2), rot=(0, 0, ang),
            m=P['cA'] if k % 2 else alt, bev=0.006)


def build_cs3(P, root):
    plot(root, P, 'cs3')
    lawn(root, P, 'cs3')
    lights = []
    c, a = (0.0, 0.1), math.radians(-18)
    W, D, hw = 0.84, 0.56, 0.5
    zr = G + hw + 0.3
    zt = G + 0.7 + 0.32
    pond(root, P, 'cs3_lago', 0.02, -0.24, 0.62, 0.34, skip=lambda x, y: y > 0.0 and abs(x) < 0.5, seed=9,
         pads=[(-0.46, -0.3, 0.045, True), (0.42, -0.36, 0.04, False), (0.5, -0.2, 0.035, True)])
    with grupo(root, 'cs3_garagem', loc=(c[0], c[1], 0), rot=(0, 0, a)):
        # agua entrando na garagem e as passarelas dos lados
        o = box(root, 'cs3_aguaDentro', (W - 0.1, D - 0.04, 0.01), (0, 0.0, G + 0.014), m=P['water'], bev=0.0)
        for sx in (-1, 1):
            box(root, f'cs3_passarela{sx}', (0.08, D - 0.06, 0.022), (sx * (W / 2 - 0.09), 0.0, G + 0.04), m=P['plank'], bev=0.005)
        planks_wall(root, P, 'cs3_fundo', -W / 2, D / 2, W / 2, D / 2, G, G + hw)
        for sx in (-1, 1):
            planks_wall(root, P, f'cs3_lado{sx}', sx * W / 2, -D / 2, sx * W / 2, D / 2, G, G + hw)
            box(root, f'cs3_pilar{sx}', (0.06, 0.06, hw + 0.02), (sx * W / 2, -D / 2, G + (hw + 0.02) / 2), m=P['white_cloth'], bev=0.012)
            box(root, f'cs3_frisoLado{sx}', (0.05, D + 0.02, 0.03), (sx * W / 2, 0, G + hw), m=P['white_cloth'], bev=0.008)
        box(root, 'cs3_verga', (W + 0.06, 0.06, 0.05), (0, -D / 2, G + hw - 0.01), m=P['white_cloth'], bev=0.01)
        # telhado de duas aguas vermelho escuro com a cumeeira branca e o oitao branco da frente com a estrela vermelha
        rw = W / 2 + 0.08
        slope = math.atan2(zr - G - hw, rw)
        Ls = math.hypot(rw, zr - G - hw)
        for sx in (-1, 1):
            box(root, f'cs3_telhado{sx}', (Ls + 0.02, D + 0.14, 0.035), (sx * rw / 2, 0, (G + hw + zr) / 2 + 0.02), rot=(0, sx * slope, 0),
                m=P['cD'], bev=0.01)
            box(root, f'cs3_beiral{sx}', (Ls + 0.03, 0.02, 0.05), (sx * rw / 2, -D / 2 - 0.075, (G + hw + zr) / 2 + 0.02), rot=(0, sx * slope, 0),
                m=P['white_cloth'], bev=0.006)
        box(root, 'cs3_cumeeira', (0.06, D + 0.16, 0.04), (0, 0, zr + 0.03), m=P['white_cloth'], bev=0.012)
        from lote_brasilia import prism_xz
        tri = prism_xz(root, 'cs3_oitao', [(-W / 2 - 0.02, 0.0), (W / 2 + 0.02, 0.0), (0.0, zr - G - hw + 0.01)], 0.03, P['white_cloth'], bev=0.008)
        tri.location = (0, -D / 2 + 0.01, G + hw + 0.012)
        estrela(root, 'cs3_estrela', 0.075, 0.012, loc=(0, -D / 2 - 0.012, G + hw + 0.12), m=P['cA'])
        # lanterninha (cupula) na cumeeira: o canhao fica em cima
        box(root, 'cs3_lanterninha', (0.2, 0.2, zt - zr - 0.02), (0, 0.0, zr + (zt - zr - 0.02) / 2), m=P['white_cloth'], bev=0.014)
        for k, (px, py, rz) in enumerate(((0, -0.101, 0), (-0.101, 0, math.pi / 2))):
            box(root, f'cs3_lanterninhaJanela{k}', (0.1, 0.012, 0.09), (px, py, zr + (zt - zr) * 0.55), rot=(0, 0, rz), m=P['window'], bev=0.005)
        box(root, 'cs3_lanterninhaTopo', (0.24, 0.24, 0.025), (0, 0, zt - 0.012), m=P['cA'], bev=0.008)
        cyl(root, 'cs3_plataforma', 0.11, 0.02, (0, 0, zt + 0.01), m=P['chrome'], v=20, bev=0.005)
        # remos encostados e a boia na parede da direita
        for k, (px, rz) in enumerate(((0.12, 0.25), (0.2, 0.35))):
            tube(root, f'cs3_remo{k}', [(W / 2 + 0.04, -0.2 + px, G), (W / 2 + 0.04 + 0.03, -0.2 + px - 0.02, G + 0.42)], 0.01, P['plank'], segs=6)
            box(root, f'cs3_pa{k}', (0.02, 0.05, 0.12), (W / 2 + 0.042, -0.2 + px + 0.004, G + 0.07), m=P['cA'], bev=0.008)
        life_ring(root, P, 'cs3_boia', (-W / 2 - 0.02, 0.05, G + 0.28), rot=(0, 0, math.pi / 2))
    # dois pedalinhos estacionados na garagem (cabecas para fora) e um no lago
    swan(root, P, 'cs3_cisneA', *L2W(c, a, (-0.17, -0.02, 0))[:2], rot=a - math.pi / 2, s=0.66, red=False, ph=0.1)
    swan(root, P, 'cs3_cisneB', *L2W(c, a, (0.17, -0.02, 0))[:2], rot=a - math.pi / 2, s=0.66, red=True, ph=0.55)
    swan(root, P, 'cs3_cisneC', -0.36, -0.36, rot=math.radians(-150), s=0.7, red=True, ph=0.3)
    lp = L2W(c, a, (0.0, -D / 2 - 0.1, G + hw - 0.1))
    tube(root, 'cs3_bracoLuz', [L2W(c, a, (0.0, -D / 2 - 0.01, G + hw + 0.02)), (lp[0], lp[1], G + hw + 0.02), (lp[0], lp[1], lp[2] + 0.04)], 0.007, P['iron_d'], segs=5)
    cyl(root, 'cs3_luzChapeu', 0.036, 0.018, (lp[0], lp[1], lp[2] + 0.04), r2=0.01, m=P['cA'], v=12, bev=0.003)
    sphere(root, 'cs3_luz', 0.028, lp, m=P['glow'], seg=12)
    lights.append((lp, '#ffc04a', 12.0, 1))
    mango_tree(root, P, 'cs3_mangueira', -0.6, 0.36, s=0.8, seed=9)
    fp = L2W(c, a, (0.0, D / 2 + 0.03, zr + 0.03))
    flag_pole(root, P, 'cs3_bandeira', fp[0], fp[1], zr + 0.03, h=0.4, w=0.24)
    sl = L2W(c, a, (0.0, 0.0, zt + 0.02))
    slot = (sl[0], sl[1], zt + 0.02)
    return {'slots': [slot], 'lights': lights, 'points': {'top': top_of(slot, size=1.1, big=2)}}


# ---------------------------------------------------------------- Lago do Sitio: o lago grande, o chafariz e mais pedalinhos
def fountain(root, P, tag, x, y, lights=None):
    """Chafariz de tres pratos (pedra clara com a borda vermelha): jato alto para cima no meio e bicas caindo de prato
    em prato ate a bacia (tudo animado)."""
    stone = P['stone_l']
    lathe(root, tag + '_bacia', [(G + 0.005, 0.22, 0.22), (G + 0.07, 0.235, 0.235), (G + 0.08, 0.22, 0.22)], stone, segs=32, lv=1, caps=True,
          ).location = (x, y, 0)
    torus(root, tag + '_baciaBorda', (x, y, G + 0.078), 0.226, 0.014, P['cA'], n=40, segs=6)
    cyl(root, tag + '_baciaAgua', 0.205, 0.01, (x, y, G + 0.076), m=P['water'], v=32, bev=0.0)
    lathe(root, tag + '_coluna', [(G + 0.08, 0.06, 0.06), (G + 0.16, 0.04, 0.04), (G + 0.3, 0.035, 0.035), (G + 0.34, 0.05, 0.05)], stone, segs=18, lv=1, caps=True
          ).location = (x, y, 0)
    tiers = ((G + 0.37, 0.13), (G + 0.58, 0.075))
    for k, (zp, rp) in enumerate(tiers):
        lathe(root, f'{tag}_prato{k}', [(zp - 0.05, 0.035, 0.035), (zp - 0.015, rp * 0.85, rp * 0.85), (zp, rp, rp)], stone, segs=24, lv=1, caps=True
              ).location = (x, y, 0)
        torus(root, f'{tag}_pratoBorda{k}', (x, y, zp), rp - 0.002, 0.01, P['cA'], n=30, segs=5)
        cyl(root, f'{tag}_pratoAgua{k}', rp - 0.012, 0.008, (x, y, zp - 0.002), m=P['water'], v=24, bev=0.0)
    lathe(root, tag + '_coluna2', [(G + 0.37, 0.03, 0.03), (G + 0.5, 0.022, 0.022), (G + 0.54, 0.035, 0.035)], stone, segs=14, lv=1, caps=True).location = (x, y, 0)
    cyl(root, tag + '_pinha', 0.02, 0.06, (x, y, G + 0.61), r2=0.01, m=stone, v=12, bev=0.005)
    # jato central alto (duas fitas cruzadas que ondulam) e as gotas no alto
    for k, rz in enumerate((0.0, math.pi / 2)):
        jet = cloth_grid(root, f'{tag}_jato{k}', 1, 1, 3, 14, [P['water_l']], thick=0.012,
                         shape=lambda u, v, co, rz=rz: Vector((x + math.cos(rz) * (u - 0.5) * (0.03 + 0.06 * (1 - v)), y + math.sin(rz) * (u - 0.5) * (0.03 + 0.06 * (1 - v)),
                                                              G + 0.62 + 0.4 * (1 - v))))
        register_cloth(jet, lambda co, ph, k=k: Vector((co.x + 0.012 * math.sin(TAU * (ph * 2 + co.z * 3 + k * 0.5)), co.y, co.z)))
    drops(root, P, tag + '_gotasTopo', (x, y, G + 1.04), n=6, spread=0.07, seed=19)
    # bicas: do prato de cima para o do meio e do meio para a bacia
    for k in range(4):
        ang = TAU * k / 4 + math.pi / 4
        spray(root, P, f'{tag}_bicaA{k}', (x + 0.07 * math.cos(ang), y + 0.07 * math.sin(ang), G + 0.575), (x + 0.11 * math.cos(ang), y + 0.11 * math.sin(ang), G + 0.38),
              w0=0.025, w1=0.035, arc=0.03, waves=2, nv=6)
        ang += math.pi / 4
        spray(root, P, f'{tag}_bicaB{k}', (x + 0.12 * math.cos(ang), y + 0.12 * math.sin(ang), G + 0.365), (x + 0.2 * math.cos(ang), y + 0.2 * math.sin(ang), G + 0.09),
              w0=0.03, w1=0.05, arc=0.05, waves=2, nv=8)
    if lights is not None:
        lights.append(((x, y - 0.12, G + 0.45), '#ffc04a', 10.0, 1))


def build_csF(P, root):
    plot(root, P, 'csF')
    lawn(root, P, 'csF')
    lights = []
    pond(root, P, 'csF_lago', 0.0, 0.08, 0.64, 0.5, skip=lambda x, y: y < -0.3 and abs(x) < 0.12, seed=13, ripple=0.006,
         pads=[(-0.5, 0.2, 0.045, True), (0.46, 0.3, 0.05, False), (0.24, 0.44, 0.04, True), (-0.26, 0.46, 0.035, False), (-0.52, -0.12, 0.035, False)])
    fountain(root, P, 'csF_chafariz', 0.0, 0.14, lights=lights)
    zd = deck(root, P, 'csF_pier', 0.0, -0.58, 0.32, 0.22, rot=math.pi / 2, z=G + 0.05)
    for k, (ang, red, ph) in enumerate(((198, False, 0.0), (150, True, 0.3), (100, False, 0.55), (45, True, 0.8), (-12, False, 0.15), (240, True, 0.65))):
        a = math.radians(ang)
        sx, sy = 0.0 + 0.47 * math.cos(a), 0.12 + 0.36 * math.sin(a)
        swan(root, P, f'csF_cisne{k}', sx, sy, rot=a + math.pi / 2, s=0.62, red=red, ph=ph)
    zt = barrel(root, P, 'csF_barril', 0.0, -0.6, zd, G + 0.325)
    lp = lantern_post(root, P, 'csF_lampiao', 0.16, -0.66, h=0.34, face=math.radians(120))
    lights.insert(0, (lp, '#ffc04a', 8.0, 0))
    slot = (0.0, -0.6, zt)
    return {'slots': [slot], 'lights': lights, 'points': {'top': top_of(slot, size=1.1, big=2)}}


# ---------------------------------------------------------------- Pedalada Fiscal: caixa d'agua, bomba de volante e a bicicleta
def build_csG(P, root):
    plot(root, P, 'csG')
    lawn(root, P, 'csG')
    lights = []
    cx, cy = 0.0, 0.08
    zt = G + 1.0
    zl = G + 0.58
    # caixa d'agua vermelha sobre a torre de ferro
    h = 0.17
    for sx in (-1, 1):
        for sy in (-1, 1):
            tube(root, f'csG_perna{sx}{sy}', [(cx + sx * (h + 0.03), cy + sy * (h + 0.03), G), (cx + sx * h, cy + sy * h, zl)], 0.018, P['cD'], segs=8)
            cyl(root, f'csG_sapata{sx}{sy}', 0.04, 0.025, (cx + sx * (h + 0.03), cy + sy * (h + 0.03), G + 0.012), m=P['conc'], v=12, bev=0.005)
    for k, (ax, ay, rz) in enumerate(((0, -1, 0), (0, 1, 0), (-1, 0, math.pi / 2), (1, 0, math.pi / 2))):
        for sg in (-1, 1):
            L = 2 * h + 0.03
            ang = math.atan2(zl - G - 0.1, L)
            box(root, f'csG_trava{k}{sg}', (math.hypot(L, zl - G - 0.1), 0.014, 0.018), (cx + ax * (h + 0.015), cy + ay * (h + 0.015), (G + zl) / 2),
                rot=(0, sg * ang, rz), m=P['white_cloth'], bev=0.004)
    box(root, 'csG_plataforma', (2 * h + 0.1, 2 * h + 0.1, 0.03), (cx, cy, zl + 0.015), m=P['plank_d'], bev=0.006)
    zt0 = zl + 0.03
    cyl(root, 'csG_tanque', 0.2, zt - zt0 - 0.09, (cx, cy, zt0 + (zt - zt0 - 0.09) / 2), m=P['cA'], v=32, bev=0.03)
    for k, t in enumerate((0.25, 0.8)):
        torus(root, f'csG_tanqueFaixa{k}', (cx, cy, zt0 + (zt - zt0 - 0.09) * t), 0.203, 0.012, P['white_cloth'], n=32, segs=5)
    lathe(root, 'csG_tampa', [(zt - 0.095, 0.205, 0.205), (zt - 0.06, 0.17, 0.17), (zt - 0.035, 0.09, 0.09), (zt - 0.02, 0.06, 0.06)], P['white_cloth'],
          segs=28, lv=1, caps=True).location = (cx, cy, 0)
    cyl(root, 'csG_topo', 0.075, 0.02, (cx, cy, zt - 0.01), m=P['chrome'], v=20, bev=0.005)
    estrela(root, 'csG_estrela', 0.075, 0.012, loc=(cx, cy - 0.205, zt0 + (zt - zt0 - 0.09) * 0.52), rot=(0, 0, 0))
    for k in range(6):   # escada de marinheiro na perna da frente direita
        tube(root, f'csG_degrau{k}', [(cx + h + 0.01, cy - h - 0.015, G + 0.08 + 0.085 * k), (cx + h - 0.06, cy - h - 0.015, G + 0.08 + 0.085 * k)], 0.006,
             P['steel'], segs=4)
    # cano da bomba ate a caixa (sobe pela perna de tras esquerda) e a bomba de volante no fundo a esquerda
    bx, by = -0.44, 0.34
    tube(root, 'csG_cano', [(bx + 0.08, by - 0.02, G + 0.1), (cx - h - 0.02, cy + h - 0.02, G + 0.1), (cx - h + 0.02, cy + h - 0.02, zl - 0.02),
                            (cx - 0.12, cy + 0.1, zt0 + 0.04)], 0.022, P['cA'], segs=10)
    for k, pt in enumerate(((cx - h - 0.0, cy + h - 0.02, G + 0.3), (cx - h + 0.01, cy + h - 0.02, G + 0.48))):
        cyl(root, f'csG_flange{k}', 0.032, 0.02, pt, m=P['white_cloth'], v=14, bev=0.004)
    box(root, 'csG_bombaBase', (0.3, 0.22, 0.03), (bx, by, G + 0.015), m=P['conc'], bev=0.008)
    box(root, 'csG_bomba', (0.24, 0.17, 0.17), (bx + 0.01, by, G + 0.115), m=P['cA'], bev=0.035)
    box(root, 'csG_bombaFaixa', (0.245, 0.175, 0.03), (bx + 0.01, by, G + 0.14), m=P['white_cloth'], bev=0.01)
    estrela(root, 'csG_bombaEstrela', 0.03, 0.008, loc=(bx + 0.08, by - 0.088, G + 0.09))
    cyl(root, 'csG_bombaCilindro', 0.05, 0.13, (bx + 0.02, by + 0.01, G + 0.26), m=P['cD'], v=16, bev=0.012)
    cyl(root, 'csG_bombaTampa', 0.056, 0.02, (bx + 0.02, by + 0.01, G + 0.33), m=P['white_cloth'], v=16, bev=0.005)
    # volante grande que gira (aro preto, raios brancos) e o manometro no vermelho
    fly = empty(root, 'csG_volantePiv', loc=(bx - 0.06, by - 0.105, G + 0.15), rot=(math.pi / 2, 0, 0))
    kids(fly, torus(root, 'csG_volanteAro', (0, 0, 0), 0.115, 0.016, P['bike_d'], n=30, segs=6))
    for k in range(5):
        aa = TAU * k / 5
        kids(fly, tube(root, f'csG_volanteRaio{k}', [(0, 0, 0), (0.11 * math.cos(aa), 0.11 * math.sin(aa), 0)], 0.008, P['white_cloth'], segs=5))
    kids(fly, cyl(root, 'csG_volanteCubo', 0.024, 0.035, (0, 0, 0), m=P['chrome'], v=12, bev=0.004))
    register_anim(fly, spin('Z', sym=5, turns=1))
    cyl(root, 'csG_manometro', 0.05, 0.025, (bx + 0.09, by - 0.1, G + 0.24), rot=(math.pi / 2 - 0.4, 0, 0), m=P['dial'], v=24, bev=0.005)
    torus(root, 'csG_manometroAro', (0, 0, 0), 0.05, 0.009, P['chrome'], axis='Y', n=24, segs=5).location = (bx + 0.09, by - 0.112, G + 0.24)
    tube(root, 'csG_manometroCano', [(bx + 0.09, by - 0.06, G + 0.2), (bx + 0.09, by - 0.09, G + 0.22)], 0.01, P['chrome'], segs=6)
    box(root, 'csG_faixaVermelha', (0.03, 0.004, 0.014), (bx + 0.115, by - 0.118, G + 0.255), rot=(-0.4, -0.7, 0), m=P['red'], bev=0.0)
    ptr = empty(root, 'csG_ponteiroPiv', loc=(bx + 0.09, by - 0.122, G + 0.24), rot=(-0.4, 0, 0))
    kids(ptr, tube(root, 'csG_ponteiro', [(0, 0, 0), (0.04, 0, 0.03)], 0.005, P['red'], segs=4))
    register_anim(ptr, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.18 * math.sin(TAU * ph * 2), 4, 'Y')))
    # valvula de alivio no topo do cilindro espirrando para cima (o ponto 'steam')
    gx, gy = bx + 0.02, by
    gy -= 0.01
    cyl(root, 'csG_valvula', 0.016, 0.05, (gx, gy, G + 0.36), m=P['chrome'], v=10, bev=0.004)
    torus(root, 'csG_valvulaAnel', (0, 0, 0), 0.02, 0.006, P['rubber_y'], n=14, segs=4).location = (gx, gy, G + 0.37)
    jet = cloth_grid(root, 'csG_esguicho', 1, 1, 3, 12, [P['water_l']], thick=0.012,
                     shape=lambda u, v, co: Vector((gx + (u - 0.5) * (0.03 + 0.1 * (1 - v)), gy - 0.01, G + 0.385 + 0.295 * (1 - v))))
    register_cloth(jet, lambda co, ph: Vector((co.x + 0.02 * math.sin(TAU * (ph * 2 + co.z * 3)), co.y, co.z)))
    drops(root, P, 'csG_gotasTopo', (gx, gy - 0.01, G + 0.67), n=5, spread=0.07, seed=19)
    # a mangueira da bicicleta ate a bomba (no chao, pela esquerda)
    tube(root, 'csG_mangueira', [(-0.42, -0.5, G + 0.015), (-0.6, -0.36, G + 0.015), (-0.62, -0.1, G + 0.015), (-0.56, 0.12, G + 0.015), (bx - 0.06, by - 0.06, G + 0.05)],
         0.016, P['hose_g'], segs=8)
    # laguinho de onde sai a agua, com um pedalinho
    pond(root, P, 'csG_lago', 0.42, -0.32, 0.26, 0.2, seed=17, pads=[(0.56, -0.24, 0.035, True)])
    swan(root, P, 'csG_cisne', 0.38, -0.34, rot=math.radians(200), s=0.58, red=False, ph=0.2)
    # lampiao
    # lampiao pendurado no canto da plataforma da caixa d'agua
    lx, ly, lz = cx - h - 0.08, cy - h - 0.08, zl - 0.09
    tube(root, 'csG_bracoLuz', [(cx - h - 0.02, cy - h - 0.02, zl - 0.005), (lx, ly, zl - 0.005), (lx, ly, lz + 0.04)], 0.007, P['iron_d'], segs=5)
    cyl(root, 'csG_luzChapeu', 0.036, 0.018, (lx, ly, lz + 0.04), r2=0.01, m=P['cA'], v=12, bev=0.003)
    sphere(root, 'csG_luz', 0.03, (lx, ly, lz), scale=(1, 1, 1.2), m=P['glow'], seg=12)
    lights.append(((lx, ly, lz), '#ffcf7a', 12.0, 1))
    mango_tree(root, P, 'csG_mangueira', 0.5, 0.44, s=0.85, seed=11)
    slot = (cx, cy, zt)
    return {'slots': [slot, (-0.46, -0.52, G)], 'lights': lights,
            'points': {'top': top_of(slot, size=1.15, big=2), 'steam': (gx, gy - 0.01, G + 0.68)}}


# ---------------------------------------------------------------- a turma do sitio
def peito_chapa(root, pr, tag, P):
    """Estrela branca no peito da camiseta vermelha."""
    return estrela_peito(root, tag, pr['body'], (0.084, 0, 0.395), r=0.03, rot=(0, 0, math.pi / 2))


def cap_brim(root, pr, tag, back=False):
    """Aba do bone vermelho (a 'cap' do lib e so a copa); back=True vira o bone para tras."""
    m = cor('bone')
    aba = cyl(root, tag + '_boneAba', 0.05, 0.008, (0, 0, 0), m=m, v=18, bev=0.003)
    aba.parent = pr['head']
    hc = Vector((0.006, 0, 0.055))
    aba.location = hc + Vector((-0.062 if back else 0.062, 0, 0.036))
    aba.scale = (1.3, 0.95, 1.0)
    aba.rotation_euler = (0, 0.14 if back else -0.14, 0)
    if not back:
        e = estrela(root, tag + '_boneEstrela', 0.016, 0.006, rot=(0, -0.55, math.pi / 2))
        e.parent = pr['head']
        e.location = hc + Vector((0.066, 0, 0.068))
    return aba


def bucket(root, tag, P):
    """Balde azul cheio d'agua (empunhadura na alca, em z = 0)."""
    return [lathe(root, tag + '_balde', [(-0.13, 0.055, 0.055), (-0.06, 0.065, 0.065), (-0.02, 0.07, 0.07)], P['blue'], segs=18, lv=1, caps=False, solid=0.008),
            cyl(root, tag + '_baldeFundo', 0.055, 0.008, (0, 0, -0.13), m=P['blue'], v=16, bev=0.0),
            torus(root, tag + '_alca', (0, 0, -0.02), 0.068, 0.005, P['chrome'], axis='X', n=16, segs=4),
            cyl(root, tag + '_baldeAgua', 0.064, 0.006, (0, 0, -0.035), m=P['water'], v=18, bev=0.0)]


def build_carrier(P, root):
    """Caseiro do sitio: camiseta vermelha com a estrela, bone vermelho, calca jeans, galochas amarelas, toalha no
    pescoco e o balde d'agua (act: joga a agua para a frente)."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(tunic=P['camisa'], skirt_m=P['calca'], vest=None, head='cap', head_m=P['bone'], belt=None,
                                         pants=P['calca'], bracer=P['skin'], boot_m=P['rubber_y'], glove=P['skin'], bare_hands=True, scarf=P['towel']))
    peito_chapa(root, pr, tag, P)
    cap_brim(root, pr, tag)
    hold(pr, 'L', *bucket(root, tag, P))
    # o jorro d'agua do balde (so aparece no meio do act)
    rr = random.Random(3)
    splash = []
    for k in range(11):
        t = k / 10
        sp_ = (k % 3 - 1) * 0.035 * t
        p = (0.2 + 0.24 * t, 0.12 - 0.06 * t + sp_, 0.44 + 0.12 * math.sin(math.pi * t) - 0.14 * t + rr.uniform(-0.01, 0.01))
        o = sphere(root, f'{tag}_jorro{k}', 0.036 - 0.014 * t + rr.uniform(-0.004, 0.004), p, scale=(1.4, 1.0, 0.85), m=P['water_l'] if k % 2 else P['water'], seg=10)
        o.parent = pr['body']
        splash.append(o)
    pr.setdefault('props', []).extend(splash)
    return pr


IDLE_N, ACT_N = 12, 8
JORRO = 'csC_jorro'


def carrier_state(mode, f):
    """idle: balde na mao, olha em volta; act: ergue o balde e joga a agua para a frente."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.05, 0.15, 0.32 + 0.008 * s), grip_L=(0.0, 0.0, 1.0), hand_R=(0.06, -0.13, 0.28), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.15, ph=ph, hide=(JORRO,))
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_L=(0.08 + 0.14 * k, 0.12, 0.32 + 0.12 * k), grip_L=(0.7 * k, 0.0, 1.0 - 0.6 * k), hand_R=(0.1 + 0.08 * k, -0.06, 0.3 + 0.12 * k),
                lean=0.14 * k, head_pitch=-0.2, ph=f / ACT_N, hide=() if 3 <= f <= 5 else (JORRO,))


# ---------------------------------------------------------------- o ciclista da pedalada (bicicleta ergometrica na propria tripulacao)
BIKE_FACE = math.radians(-30)
CRANK = Vector((0.035, 0.0, 0.1))
CR = 0.048
FLY = Vector((0.14, 0.0, 0.13))
GRIP = Vector((0.1, 0.085, 0.33))
LEAN = 0.24
SEAT_OFF = Vector((-0.115, 0.0, 0.085))


def build_cyclist(P, root):
    """Ciclista da Pedalada Fiscal: militante de camiseta vermelha com a estrela, bone virado para tras e toalha no
    pescoco, pedalando a bicicleta ergometrica vermelha (volante com a estrela branca, mangueira saindo para tras)."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(face=BIKE_FACE, tunic=P['camisa'], skirt_m=P['calca'], vest=None, head='cap', head_m=P['bone'], belt=None,
                                         pants=P['calca'], bracer=P['skin'], glove=P['skin'], bare_hands=True, scarf=P['towel']))
    for nm in ('perna0', 'perna1', 'bota0', 'bota1', 'botaAba0', 'botaAba1'):
        o = bpy.data.objects.get(f'{tag}_{nm}')
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    peito_chapa(root, pr, tag, P)
    cap_brim(root, pr, tag, back=True)
    # suor (so no act)
    sweat = []
    for k, (dx, dy, dz) in enumerate(((0.03, -0.075, 0.09), (-0.02, 0.075, 0.1), (0.05, 0.06, 0.12))):
        o = sphere(root, f'{tag}_suor{k}', 0.011, (dx, dy, dz), scale=(1, 1, 1.4), m=P['water'], seg=8)
        o.parent = pr['head']
        sweat.append(o)
    pr.setdefault('props', []).extend(sweat)
    # bicicleta (coordenadas locais: +X para a frente)
    bike = empty(root, tag + '_bike', rot=(0, 0, BIKE_FACE))
    frame = P['cA']
    dark = P['bike_d']

    def K(o):
        o.parent = bike
        return o
    for k, x in enumerate((-0.15, 0.17)):
        K(tube(root, f'{tag}_pe{k}', [(x, -0.08, 0.014), (x, 0.08, 0.014)], 0.014, dark, segs=8))
        for sy in (-1, 1):
            K(sphere(root, f'{tag}_ponteira{k}{sy}', 0.017, (x, sy * 0.08, 0.014), m=dark, seg=8))
    K(tube(root, f'{tag}_quadro', [(-0.15, 0, 0.02), (-0.08, 0, 0.1), (CRANK.x, 0, CRANK.z), (0.13, 0, 0.1), (0.17, 0, 0.02)], 0.016, frame, segs=10))
    K(tube(root, f'{tag}_canoSelim', [(-0.08, 0, 0.1), (-0.095, 0, 0.2)], 0.013, frame, segs=8))
    K(sphere(root, f'{tag}_selim', 1.0, (-0.1, 0, 0.21), scale=(0.07, 0.045, 0.02), m=dark, seg=12))
    K(tube(root, f'{tag}_coluna', [(0.13, 0, 0.1), (0.09, 0, 0.3)], 0.015, frame, segs=8))
    K(tube(root, f'{tag}_guidao', [(GRIP.x + 0.01, -GRIP.y, GRIP.z + 0.01), (0.085, -0.03, 0.305), (0.09, 0, 0.3), (0.085, 0.03, 0.305), (GRIP.x + 0.01, GRIP.y, GRIP.z + 0.01)],
               0.009, dark, segs=6))
    K(box(root, f'{tag}_painel', (0.03, 0.05, 0.035), (0.095, 0, 0.32), rot=(0, -0.5, 0), m=dark, bev=0.006))
    K(box(root, f'{tag}_painelTela', (0.004, 0.036, 0.022), (0.105, 0, 0.327), rot=(0, -0.5, 0), m=P['window'], bev=0.002))
    # capa do volante (meia lua) e o volante que gira com a estrela
    fly = empty(root, tag + '_volante', loc=FLY, parent=bike)
    kids(fly, cyl(root, f'{tag}_volanteDisco', 0.075, 0.03, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['white_cloth'], v=28, bev=0.006))
    kids(fly, torus(root, f'{tag}_volanteAro', (0, 0, 0), 0.075, 0.01, frame, axis='Y', n=28, segs=5))
    for sy in (-1, 1):
        e = estrela(root, f'{tag}_volanteEstrela{sy}', 0.045, 0.006, loc=(0, sy * 0.017, 0), m=frame)
        kids(fly, e)
    kids(fly, cyl(root, f'{tag}_volanteCubo', 0.012, 0.05, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['chrome'], v=10, bev=0.003))
    K(tube(root, f'{tag}_corrente', [(CRANK.x, 0.022, CRANK.z), (FLY.x, 0.022, FLY.z)], 0.006, dark, segs=5))
    # pedivela: dois bracos opostos com os pedais (os pes seguem os pedais)
    crank = empty(root, tag + '_pedivela', loc=CRANK, parent=bike)
    kids(crank, cyl(root, f'{tag}_coroa', 0.03, 0.012, (0, 0.03, 0), rot=(math.pi / 2, 0, 0), m=P['chrome'], v=16, bev=0.003))
    pedals = {}
    for side, sg in (('L', 1), ('R', -1)):
        x = CR * sg
        kids(crank, tube(root, f'{tag}_braco{side}', [(0, sg * 0.04, 0), (x, sg * 0.06, 0)], 0.008, P['chrome'], segs=6))
        pe = empty(root, f'{tag}_pedal{side}', loc=(x, sg * 0.075, 0), parent=crank)
        kids(pe, box(root, f'{tag}_pedalCaixa{side}', (0.04, 0.03, 0.01), (0, 0, 0), m=dark, bev=0.003))
        pedals[side] = pe
    # mangueira saindo de tras da bicicleta (vai para a bomba)
    K(tube(root, f'{tag}_mangueira', [(0.14, 0.03, 0.06), (0.05, 0.07, 0.016), (-0.1, 0.1, 0.016), (-0.26, 0.12, 0.016)], 0.014, P['hose_g'], segs=8))
    # pernas (malha refeita a cada quadro) e os tenis
    legs = {}
    for side in 'LR':
        legs[side] = (ensure_mesh(root, f'{tag}_coxa{side}', P['calca']), ensure_mesh(root, f'{tag}_canela{side}', P['calca']),
                      sphere(root, f'{tag}_tenis{side}', 0.045, (0, 0, 0), scale=(1.35, 0.8, 0.7), m=P['sneaker'], seg=14),
                      torus(root, f'{tag}_barra{side}', (0, 0, 0), 0.034, 0.011, P['calca'], n=14, segs=5))
    pr.update(bike=bike, crank=crank, fly=fly, pedals=pedals, legs=legs)
    return pr


def cyclist_state(mode, f):
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return TAU * ph, dict(lean=LEAN, breathe=0.6 * s, head_yaw=0.15 * math.sin(TAU * ph), head_pitch=-0.12, ph=ph, hide=('csE_suor',))
    ph = f / ACT_N
    return TAU * 2 * ph, dict(lean=LEAN + 0.12, breathe=1.2 * math.sin(TAU * ph * 2), head_pitch=0.05, head_yaw=0.05, ph=ph,
                              head_roll=0.08 * math.sin(TAU * ph * 2))


def pose_cyclist(parts, P, root, f, mode):
    th, st = cyclist_state(mode, f)
    off = SEAT_OFF + (Vector((0.012, 0, -0.008)) * (1 if mode == 'act' else 0))
    bob_z = 0.006 * math.sin(2 * th)
    rz = Matrix.Rotation(BIKE_FACE, 3, 'Z')
    st['offset'] = tuple(rz @ (off + Vector((0, 0, bob_z))))
    st['face'] = BIKE_FACE
    # maos no guidao: ponto da bicicleta -> espaco do corpo (sem o giro do rosto, que a bicicleta ja tem)
    ry_inv = Matrix.Rotation(-st['lean'], 3, 'Y')
    for side, sg in (('L', 1), ('R', -1)):
        g = Vector((GRIP.x, sg * GRIP.y, GRIP.z))
        st['hand_' + side] = tuple(ry_inv @ (g - off - Vector((0, 0, bob_z))))
        st['pole_' + side] = (-0.4, sg * 1.0, -0.5)
    pose_person(parts, P, root, st)
    parts['crank'].rotation_euler = (0, th, 0)
    parts['fly'].rotation_euler = (0, th * 2.4, 0)
    bpy.context.view_layer.update()
    Mi = root.matrix_world.inverted()
    Mb = parts['body'].matrix_world
    fwd = rz @ Vector((1, 0, 0))
    for side, sg in (('L', 1), ('R', -1)):
        hip = Mi @ (Mb @ Vector((0.0, sg * 0.047, 0.17)))
        ped = Mi @ parts['pedals'][side].matrix_world.translation
        foot = ped + Vector((0, 0, 0.022))
        knee, ank = two_bone(hip, foot, 0.13, 0.125, tuple(fwd * 1.0 + Vector((0, 0, 0.6))))
        thigh, shin, shoe, cuff = parts['legs'][side]
        set_mesh_tube(thigh, [hip, hip.lerp(knee, 0.5), knee], 0.036, segs=10, rfun=lambda t: 0.04 - 0.006 * t)
        set_mesh_tube(shin, [knee, knee.lerp(ank, 0.5), ank], 0.031, segs=10)
        shoe.location = ank + fwd * 0.018 + Vector((0, 0, -0.01))
        shoe.rotation_euler = (0, 0, BIKE_FACE)
        cuff.location = ank + Vector((0, 0, 0.012))
        for o in (thigh, shin):
            o['set'] = root['set']


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


def cyclist_crew(key, label):
    return {'key': key, 'label': label, 'build': build_cyclist, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose_cyclist(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose_cyclist(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose_cyclist(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose_cyclist(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'cs1': ['csB1', 'csC'], 'cs2': ['csB2'], 'cs3': ['csB3'], 'csF': ['csB3'], 'csG': ['csBG', 'csE']},
    'towers': [('cs1', 'Pedalinho do Sitio N1', build_cs1), ('cs2', 'Pedalinho do Sitio N2', build_cs2), ('cs3', 'Pedalinho do Sitio N3', build_cs3),
               ('csF', 'Lago do Sitio', build_csF), ('csG', 'Pedalada Fiscal', build_csG)],
    'crews': [crew('csC', 'Caseiro', build_carrier, carrier_state), cyclist_crew('csE', 'Ciclista da pedalada')],
    'turrets': [nozzle_spec('csB1', 'Canhao N1', size=0.85), nozzle_spec('csB2', 'Canhao N2', size=1.0, big=1),
                nozzle_spec('csB3', 'Canhao N3', size=1.1, big=2), nozzle_spec('csBG', 'Canhao da Pedalada', size=1.15, big=2)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
