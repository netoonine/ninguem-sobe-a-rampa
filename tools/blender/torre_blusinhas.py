"""Taxa das Blusinhas (Ninguem Sobe a Rampa, so a Chapa Vermelha): a arte da familia mercado (engine 'market') do lado R.
Meme: a taxa sobre as comprinhas internacionais pequenas ("taxa das blusinhas"). Guiche da Receita de concreto branco
com laje vermelha, esteira trazendo pacotinhos de papelao, blusinhas dobradas e envelopes de plastico (tudo generico,
sem marca), o carimbo que desce e marca cada pacote com o simbolo de porcentagem (so o desenho do %, sem letra) e o %
grande no telhado. Os fiscais usam colete vermelho com a estrela branca, bone vermelho e jeans. As moedas da renda
(pilhas, moeda girando, saco de moedas) continuam: agora sao o imposto arrecadado.

  niveis 1 a 3 (mk1, mk2, mk3): o guiche cresce ate o predio da Receita com brises de Brasilia; esteira e carimbo
  Receita do Taxad (mkB, 'bazaar'): galpao da alfandega com a montanha de pacotes, o painel aceso com o %, o balcao
                                    e o carimbo gigante (dois fiscais atras do balcao)
  Arcabouco Fiscal (mkT, 'treasury'): o cofrinho de porquinho vermelho (estrela branca no flanco) dentro de um andaime
                                      de tubos e tabuas (o arcabouco), com moedas caindo pela fenda

Nomes de conjuntos, postos, pontos, modos e quadros iguais aos do Banco Vorcash (js/sprites.js depende deles): mk1, mk2,
mk3, mkB, mkT e a tripulacao mkM (fiscal da Receita) e mkG (mestre do arcabouco), modos idle 12 e act 8.
So existe na chapa R (o lado V continua com o Banco Vorcash de torre_mercado.py):

  CHAPA=R Blender -b -P tools/blender/torre_blusinhas.py -- render arte/render_r/mercado [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_blusinhas.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_blusinhas.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('CHAPA', 'R')   # torre so da Chapa Vermelha
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, prism_xz, hard_hat, G   # noqa: F811
from pecas_zcv import slab, HC, glasses, shoes
from chapa import CHAPA, PAL, cor, emblema, estrela, bandeirinha, estrela_peito

FRONT = -math.pi / 2
FAM = 'mercado'

import lib as _lib
_orig_palette2 = palette2

BLUSAS = ['#f49ab9', '#b9a3ea', '#86d8bd', '#ffd368', '#8ec9f3', '#ffa77a']


def palette2():   # noqa: F811 - concreto branco, laje vermelha, papelao, blusinhas e o ouro da arrecadacao
    P = _orig_palette2()
    P['coin'] = mat('moeda_ouro', '#f0bd43', rough=0.28, metal=0.75, var=0.04, bump=0.02)
    P['coin_d'] = mat('moeda_ouro_borda', '#d39a2c', rough=0.32, metal=0.7, var=0.03, bump=0.02)
    P['roof'] = mat('laje_receita_' + CHAPA, PAL['pri'], rough=0.35, metal=0.15, var=0.02, bump=0.01)
    P['roof_d'] = cor('escuro', rough=0.45)
    P['trim'] = cor('sec', rough=0.35)
    P['wall'] = mat('parede_receita', '#f4f0e8', rough=0.4, var=0.03, bump=0.03)
    P['wall_d'] = mat('parede_receita_base', '#ddd5c6', rough=0.45, var=0.04, bump=0.04)
    P['glass_w'] = mat('vidro_guiche', '#86a4bd', rough=0.12, metal=0.1, var=0.02, bump=0.0)
    P['ink'] = mat('tinta_carimbo', PAL['pri'], rough=0.7, var=0.0, bump=0.0)
    P['kraft'] = mat('papelao', '#c9995c', rough=0.8, var=0.06, bump=0.05)
    P['kraft_d'] = mat('papelao_escuro', '#b0814a', rough=0.8, var=0.04, bump=0.05)
    P['tape'] = mat('fita_pacote', '#efe2b8', rough=0.4, var=0.0, bump=0.0)
    P['mailer'] = mat('envelope_plastico', '#a7b1bc', rough=0.35, var=0.05, bump=0.02, sheen=0.2)
    P['blusas'] = [mat(f'blusinha{k}', c, rough=0.85, var=0.03, bump=0.06, sheen=0.5) for k, c in enumerate(BLUSAS)]
    P['belt'] = mat('esteira_borracha', '#2f3237', rough=0.7, var=0.0, bump=0.08)
    P['steel'] = mat('aco_esteira', '#c9cfd4', rough=0.3, metal=0.8, var=0.02, bump=0.0)
    P['wood_s'] = mat('cabo_carimbo', '#a86b3a', rough=0.55, var=0.04, bump=0.05)
    P['rubber'] = mat('borracha_carimbo', '#3a2a2a', rough=0.7, var=0.0, bump=0.02)
    P['strip'] = mat('cortina_tiras', '#d5dde3', rough=0.25, var=0.03, bump=0.0)
    P['lamp'] = glow_mat('globo_receita', '#fff1c8', 0.8, 9.0, rough=0.4, var=0.0, bump=0.0)
    P['screen'] = glow_mat('painel_receita_' + CHAPA, '#e2443c', 0.5, 3.0, rough=0.2, var=0.0, bump=0.0)
    P['screen_w'] = glow_mat('painel_receita_simbolo', '#fff4ec', 1.2, 5.0, rough=0.2, var=0.0, bump=0.0)
    P['pig'] = cor('pri', rough=0.28, var=0.02, bump=0.01)
    P['pig_d'] = cor('escuro', rough=0.4)
    P['scaf'] = mat('tubo_andaime', '#c3c9ce', rough=0.3, metal=0.75, var=0.03, bump=0.02)
    P['clamp'] = mat('abracadeira_andaime', '#f0a22a', rough=0.4, metal=0.3, var=0.02, bump=0.0)
    P['plank'] = mat('tabua_andaime', '#c9995a', rough=0.75, var=0.08, bump=0.2)
    P['slot'] = mat('fenda_cofrinho', '#2a1a1a', rough=0.7, var=0.0, bump=0.0)
    P['conc'] = concrete()
    P['teal'] = cor('pri', rough=0.6, sheen=0.4)
    P['stripes'] = mat('toldo_receita_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(3.6, PAL['claro'], PAL['pri']), sheen=0.4)
    P['_emblem'] = 'coin'
    return P


_lib.palette2 = palette2


# ---------------------------------------------------------------- moedas (a arrecadacao)
def coin_stack(root, P, tag, x, y, n, r=0.055, z0=G, seed=1):
    """Pilha de moedas de ouro (cada uma com a borda mais escura e um leve desalinho)."""
    rr = random.Random(seed)
    h = 0.019
    for k in range(n):
        cyl(root, f'{tag}{k}', r, h * 0.92, (x + rr.uniform(-0.005, 0.005), y + rr.uniform(-0.005, 0.005), z0 + h * 0.5 + h * k),
            m=P['coin'] if k % 3 else P['coin_d'], v=24, bev=0.005)
    torus(root, tag + '_relevo', (x, y, z0 + h * n - 0.001), r * 0.68, 0.0045, P['coin_d'], n=22, segs=4)
    return z0 + h * n


def loose_coins(root, P, tag, x, y, n=5, spread=0.12, z0=G, seed=3, r=0.045):
    rr = random.Random(seed)
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = spread * math.sqrt(rr.random())
        cyl(root, f'{tag}{k}', r, 0.014, (x + d * math.cos(a), y + d * math.sin(a), z0 + 0.008 + 0.004 * (k % 2)),
            rot=(rr.uniform(-0.25, 0.25), rr.uniform(-0.25, 0.25), 0), m=P['coin'], v=22, bev=0.004)


def spinning_coin(root, P, tag, loc, r=0.06, ph0=0.0):
    """Moeda em pe girando no proprio eixo (o brilho da arrecadacao)."""
    e = empty(root, tag, loc=loc)
    kids(e, cyl(root, tag + '_moeda', r, 0.016, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['coin'], v=26, bev=0.005),
         torus(root, tag + '_relevo', (0, 0, 0), r * 0.68, 0.005, P['coin_d'], axis='Y', n=22, segs=4))

    def fn(o, mb, ph, p0=ph0):
        o.matrix_basis = Matrix.Translation((0, 0, 0.015 * math.sin(TAU * (ph + p0)))) @ mb @ Matrix.Rotation(math.pi * ph, 4, 'Z')
    register_anim(e, fn)
    return e


def globe_lamp(root, P, tag, x, y, z0, h=0.36, lights=None):
    """Poste baixo com globo de luz (luminaria de reparticao publica)."""
    cyl(root, tag + '_base', 0.04, 0.03, (x, y, z0 + 0.015), r2=0.032, m=P['roof_d'], v=16, bev=0.006)
    tube(root, tag + '_haste', [(x, y, z0), (x, y, z0 + h)], 0.012, P['steel'], segs=8)
    torus(root, tag + '_aro', (x, y, z0 + h), 0.03, 0.008, P['roof_d'], n=14, segs=4)
    sphere(root, tag, 0.05, (x, y, z0 + h + 0.045), m=P['lamp'], seg=16)
    if lights is not None:
        lights.append(((x, y - 0.04, z0 + h + 0.05), '#ffe7b0', 9.0, 1))


def flag_left(root, name, loc, h=0.34):
    """Bandeirinha da chapa com o pano para a esquerda (espelhada: a face com o emblema inteiro fica para a camera)."""
    m = bandeirinha(root, name, loc, h=h)
    m.scale = (-1, 1, 1)
    return m


# ---------------------------------------------------------------- o simbolo de porcentagem (desenho, sem letra)
def percent(root, tag, s, loc, m, rot=(0, 0, 0), depth=None, parent=None, front=False, flat=False):
    """Simbolo % no plano XZ (de frente para -Y): duas bolinhas vazadas e a barra inclinada. s = altura total.
    flat: versao fina (marca de carimbo). Devolve o empty."""
    e = empty(root, tag, loc=loc, rot=rot, parent=parent)
    d = depth or (0.006 if flat else s * 0.16)
    rr_, th = s * 0.15, s * (0.055 if flat else 0.062)
    objs = []
    for k, (u, v) in enumerate(((-0.27, 0.27), (0.27, -0.27))):
        o = torus(root, f'{tag}_o{k}', (u * s, 0, v * s), rr_, th, m, axis='Y', n=20, segs=6, front=front)
        o.scale = (1, d / (2 * th), 1)
        objs.append(o)
    b = box(root, tag + '_barra', (th * 2.1, d, s * 1.0), (0, 0, 0), rot=(0, 0.62, 0), m=m, bev=min(0.006, th * 0.5), front=front)
    objs.append(b)
    kids(e, *objs)
    return e


# ---------------------------------------------------------------- pacotinhos, blusinhas, envelopes
def pacote(root, P, tag, s=1.0, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, stamp=False, front=False):
    """Caixinha de papelao com a fita no meio (base em z = 0). stamp: ja carimbada (o % vermelho na tampa)."""
    w, d, h = 0.1 * s, 0.08 * s, 0.07 * s
    e = empty(root, tag, loc=loc, rot=rot, parent=parent)
    kids(e, box(root, tag + '_caixa', (w, d, h), (0, 0, h / 2), m=P['kraft'], bev=0.008 * s, front=front),
         box(root, tag + '_fita', (w + 0.002, d * 0.26, 0.004), (0, 0, h + 0.0005), m=P['tape'], bev=0.0015, front=front),
         box(root, tag + '_fitaFrente', (0.004, d * 0.26 + 0.002, h * 0.5), (-w / 2 - 0.001, 0, h * 0.72), m=P['tape'], bev=0.0015, front=front))
    if stamp:
        percent(root, tag + '_marca', 0.05 * s, (w * 0.22, -d * 0.12, h + 0.004), P['ink'], rot=(-math.pi / 2, 0, 0), flat=True, parent=e, front=front)
    e['h'] = h
    return e


def blusinha(root, P, tag, k, s=1.0, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, folded=True, front=False):
    """Blusinha dobrada deitada (silhueta de camiseta: corpo, mangas curtas e a gola), cor pastel generica."""
    w = 0.1 * s
    pts = [(-0.5, -0.55), (0.5, -0.55), (0.5, 0.22), (0.78, 0.12), (0.92, 0.36), (0.55, 0.6), (0.18, 0.6), (0.0, 0.46), (-0.18, 0.6), (-0.55, 0.6),
           (-0.92, 0.36), (-0.78, 0.12), (-0.5, 0.22)]
    pts = [(x * w * 0.6, z * w * 0.75) for x, z in pts]
    if folded:
        pts = [(x * 0.85, z * 0.8) for x, z in pts]
    e = empty(root, tag, loc=loc, rot=rot, parent=parent)
    m = P['blusas'][k % len(P['blusas'])]
    o = prism_xz(root, tag + '_blusa', pts, 0.018 * s, m, bev=0.006 * s, front=front)
    o.rotation_euler = (-math.pi / 2, 0, 0)   # deitada, a gola para tras
    o.location = (0, 0, 0.009 * s)
    gola = torus(root, tag + '_gola', (0, 0, 0), 0.016 * s, 0.004 * s, mat('gola_blusinha', '#fbf7f2', rough=0.8, var=0, bump=0), n=14, segs=4, front=front)
    gola.location = (0, 0.026 * s, 0.019 * s)
    gola.scale = (1.0, 0.8, 0.5)
    dobra = box(root, tag + '_dobra', (w * 0.7, 0.006 * s, 0.004 * s), (0, -0.012 * s, 0.0185 * s), m=m, bev=0.002, front=front)
    kids(e, o, gola, dobra)
    e['h'] = 0.02 * s
    return e


def envelope_plastico(root, P, tag, s=1.0, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, front=False):
    """Envelope de plastico cinza estufado (os pacotinhos de fora), com a aba de cima."""
    e = empty(root, tag, loc=loc, rot=rot, parent=parent)
    kids(e, sphere(root, tag + '_corpo', 1.0, (0, 0, 0.02 * s), scale=(0.065 * s, 0.05 * s, 0.022 * s), m=P['mailer'], seg=16, front=front),
         box(root, tag + '_aba', (0.11 * s, 0.022 * s, 0.006 * s), (0, 0.035 * s, 0.022 * s), m=P['mailer'], bev=0.003, front=front))
    e['h'] = 0.04 * s
    return e


def item_esteira(root, P, tag, k, s=1.0, loc=(0, 0, 0), parent=None):
    kind = ('pacote', 'blusa', 'envelope', 'blusa', 'pacote')[k % 5]
    if kind == 'pacote':
        return pacote(root, P, tag, s=s, loc=loc, parent=parent)
    if kind == 'blusa':
        return blusinha(root, P, tag, k, s=s * 1.05, loc=loc, parent=parent)
    return envelope_plastico(root, P, tag, s=s, loc=loc, parent=parent)


def pilha_pacotes(root, P, tag, x, y, z0, n=6, seed=1, s=1.0, front=False):
    """Monte de pacotes ja taxados (caixinhas carimbadas, blusinhas e envelopes)."""
    rr = random.Random(seed)
    spots = [(-0.06, -0.03, 0), (0.05, -0.04, 0), (0.0, 0.05, 0), (-0.01, 0.0, 1), (0.08, 0.04, 0), (-0.09, 0.05, 0), (0.04, 0.01, 1), (-0.03, 0.02, 2)]
    for k in range(n):
        u, v, lv = spots[k % len(spots)]
        z = z0 + lv * 0.07 * s
        if k % 3 == 2:
            blusinha(root, P, f'{tag}{k}', k + seed, s=s, loc=(x + u * s, y + v * s, z), rot=(0, 0, rr.uniform(-0.6, 0.6)), front=front)
        else:
            pacote(root, P, f'{tag}{k}', s=s * rr.uniform(0.9, 1.1), loc=(x + u * s, y + v * s, z), rot=(0, 0, rr.uniform(-0.5, 0.5)), stamp=True, front=front)


# ---------------------------------------------------------------- carimbo
def carimbo(root, P, tag, s=1.0, front=False):
    """Carimbo de borracha (base em z = 0, cabo para cima): borracha com o % em relevo por baixo, bloco vermelho,
    pescoco e o pegador redondo de madeira. Devolve os objetos (o chamador poe no grupo)."""
    objs = [box(root, tag + '_borracha', (0.2 * s, 0.14 * s, 0.025 * s), (0, 0, 0.0125 * s), m=P['ink'], bev=0.006 * s, front=front),
            box(root, tag + '_bloco', (0.22 * s, 0.16 * s, 0.07 * s), (0, 0, 0.06 * s), m=P['roof'], bev=0.018 * s, front=front),
            box(root, tag + '_blocoFilete', (0.224 * s, 0.164 * s, 0.014 * s), (0, 0, 0.032 * s), m=P['trim'], bev=0.004 * s, front=front),
            cyl(root, tag + '_pescoco', 0.035 * s, 0.11 * s, (0, 0, 0.145 * s), r2=0.028 * s, m=P['wood_s'], v=16, bev=0.008 * s, front=front),
            sphere(root, tag + '_pegador', 0.065 * s, (0, 0, 0.23 * s), scale=(1, 1, 0.85), m=P['wood_s'], seg=20, front=front)]
    objs.append(percent(root, tag + '_face', 0.1 * s, (0, -0.081 * s, 0.062 * s), P['trim'], flat=True, depth=0.006 * s, front=front))
    # o % em relevo na borracha (aparece quando o carimbo aponta para a camera)
    objs.append(percent(root, tag + '_relevo', 0.1 * s, (0, 0, -0.002), P['trim'], rot=(math.pi / 2, 0, 0), flat=True, depth=0.006 * s, front=front))
    return objs


# ---------------------------------------------------------------- esteira com o carimbo automatico
def esteira(root, P, tag, x0, x1, y, z, zf, n=4, w=0.15, ps=0.5, s=1.0, curtain=True):
    """Esteira ao longo de X (topo em z, pes ate o piso zf) trazendo n itens; o carimbo desce sobre cada um quando
    ele passa no ponto ps (fracao do percurso) e o item sai com o % vermelho. Os itens entram pela cortina de tiras
    (esquerda) e caem no fim. Devolve x do carimbo e a altura do topo da prensa."""
    L = x1 - x0
    cx = (x0 + x1) / 2
    box(root, tag + '_chassi', (L, w + 0.02, 0.05), (cx, y, z - 0.035), m=P['roof'], bev=0.012)
    box(root, tag + '_lona', (L - 0.02, w, 0.014), (cx, y, z - 0.004), m=P['belt'], bev=0.005)
    for k, xx in enumerate((x0 + 0.005, x1 - 0.005)):
        cyl(root, f'{tag}_rolo{k}', 0.032, w + 0.01, (xx, y, z - 0.03), rot=(math.pi / 2, 0, 0), m=P['steel'], v=16, bev=0.004)
    nl = max(2, int(L / 0.32) + 1)
    for k in range(nl):
        xx = x0 + 0.05 + (L - 0.1) * k / (nl - 1)
        for sy in (-1, 1):
            tube(root, f'{tag}_pe{k}{sy}', [(xx, y + sy * (w / 2 - 0.01), zf), (xx, y + sy * (w / 2 - 0.01), z - 0.05)], 0.012, P['steel'], segs=6)
    tube(root, tag + '_guarda', [(x0 + 0.02, y + w / 2 + 0.015, z + 0.035), (x1 - 0.02, y + w / 2 + 0.015, z + 0.035)], 0.008, P['steel'], segs=6)
    # cortina de tiras na entrada
    if curtain:
        for sy in (-1, 1):
            box(root, f'{tag}_cortinaPoste{sy}', (0.03, 0.03, 0.22), (x0 + 0.03, y + sy * (w / 2 + 0.03), z + 0.1), m=P['roof'], bev=0.008)
        box(root, tag + '_cortinaTopo', (0.05, w + 0.1, 0.04), (x0 + 0.03, y, z + 0.22), m=P['roof'], bev=0.01)
        for k in range(5):
            box(root, f'{tag}_tira{k}', (0.008, w / 5 - 0.004, 0.18), (x0 + 0.012, y - w / 2 + (k + 0.5) * w / 5, z + 0.11), m=P['strip'], bev=0.002)
    # itens andando
    a0, a1 = x0 + 0.03, x1 - 0.03
    for k in range(n):
        e = empty(root, f'{tag}_itemPivo{k}', loc=(a0, y, z + 0.003))
        it = item_esteira(root, P, f'{tag}_item{k}', k, s=s, parent=e)
        mk = percent(root, f'{tag}_itemMarca{k}', 0.045 * s, (0.012 * s, -0.008 * s, it['h'] + 0.003), P['ink'], rot=(-math.pi / 2, 0, 0.0), flat=True,
                     parent=it)

        def show(o, mb, ph, k=k):
            p = (k / n + ph) % 1.0
            sc = 1.0 if p > ps + 0.02 else 0.001
            o.matrix_basis = mb @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(mk, show)

        def move(o, mb, ph, k=k):
            p = (k / n + ph) % 1.0
            sc = max(0.001, min(1.0, (1 - p) / 0.1, p / 0.06 + 0.4))
            o.matrix_basis = Matrix.Translation(((a1 - a0) * p, 0, -0.04 * max(0.0, (p - 0.92) / 0.08))) @ mb @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(e, move)
    # prensa do carimbo: coluna atras da esteira, braco por cima e o carimbo que desce n vezes por loop
    xs = a0 + (a1 - a0) * ps
    yb = y + w / 2 + 0.06
    zt = z + 0.36 * s
    box(root, tag + '_prensaColuna', (0.07, 0.07, zt - zf), (xs, yb, (zt + zf) / 2), m=P['roof'], bev=0.014)
    box(root, tag + '_prensaFilete', (0.074, 0.074, 0.016), (xs, yb, zt - 0.06), m=P['trim'], bev=0.004)
    box(root, tag + '_prensaBraco', (0.09, yb - y + 0.08, 0.07), (xs, (y + yb) / 2 - 0.01, zt), m=P['roof'], bev=0.016)
    cyl(root, tag + '_prensaCilindro', 0.03, 0.08, (xs, y, zt - 0.06), m=P['steel'], v=16, bev=0.006)
    st = empty(root, tag + '_carimboPivo', loc=(xs, y, z + 0.05 * s))
    piston = tube(root, tag + '_pistao', [(0, 0, 0.12 * s), (0, 0, zt - z - 0.05 * s - 0.07)], 0.016, P['steel'], segs=8)
    kids(st, piston, *carimbo(root, P, tag + '_carimbo', s=0.55 * s))
    up = 0.1 * s

    def press(o, mb, ph):
        q = (n * (ph - ps)) % 1.0
        qq = min(q, 1 - q)
        k = min(1.0, qq / 0.22)
        o.matrix_basis = Matrix.Translation((0, 0, up * k)) @ mb
    register_anim(st, press)
    return xs, zt


# ---------------------------------------------------------------- o guiche / o predio da Receita
def plinth(root, P, tag, cx, cy, w, d, steps=2, h=0.06, z0=G):
    """Base de concreto em degraus (cada degrau um pouco menor)."""
    z = z0
    for k in range(steps):
        ww, dd = w - 0.08 * k, d - 0.08 * k
        slab(root, f'{tag}{k}', ww, dd, h, P['wall_d'] if k == 0 else P['wall'], r=0.04, loc=(cx, cy + 0.02 * k, z + h / 2), rot=(math.pi / 2, 0, 0), bev=0.014)
        z += h
    return z


def receita(root, P, tag, cx, cy, w, d, h, z0, windows=1, fins=0, sign=0.3, lights=None):
    """Guiche da Receita: caixa de concreto branco, rodape, guiche(s) com vidro e balcaozinho, laje vermelha com
    filete branco, o % grande no telhado (balanca de leve) e a bandeirinha da chapa. Devolve o topo (x, y, z)."""
    yf = cy - d / 2
    box(root, tag + '_parede', (w, d, h), (cx, cy, z0 + h / 2), m=P['wall'], bev=0.015)
    box(root, tag + '_rodape', (w + 0.02, d + 0.02, 0.04), (cx, cy, z0 + 0.02), m=P['wall_d'], bev=0.01)
    ww = min(0.22, (w - 0.12) / windows - 0.06)
    for k in range(windows):
        wx = cx + (k - (windows - 1) / 2) * (w - 0.1) / windows
        box(root, f'{tag}_guicheMoldura{k}', (ww + 0.04, 0.02, h * 0.42 + 0.04), (wx, yf - 0.006, z0 + h * 0.56), m=P['roof_d'], bev=0.008)
        box(root, f'{tag}_guicheVidro{k}', (ww, 0.02, h * 0.42), (wx, yf - 0.012, z0 + h * 0.56), m=P['glass_w'], bev=0.004)
        box(root, f'{tag}_guicheFala{k}', (ww * 0.3, 0.022, 0.03), (wx, yf - 0.016, z0 + h * 0.42), m=P['wall_d'], bev=0.004)
        box(root, f'{tag}_guicheBalcao{k}', (ww + 0.06, 0.06, 0.02), (wx, yf - 0.03, z0 + h * 0.33), m=P['roof'], bev=0.006)
        # reflexo no vidro
        box(root, f'{tag}_guicheReflexo{k}', (0.012, 0.004, h * 0.32), (wx - ww * 0.25, yf - 0.023, z0 + h * 0.58), rot=(0, -0.5, 0),
            m=mat('reflexo_vidro', '#d8e6f0', rough=0.1, var=0, bump=0), bev=0.0)
    for k in range(fins):
        fx = cx - w / 2 + 0.03 + (w - 0.06) * k / (fins - 1)
        box(root, f'{tag}_brise{k}', (0.022, 0.05, h - 0.06), (fx, yf - 0.03, z0 + h / 2 + 0.02), m=P['wall'], bev=0.006)
    # laje vermelha com o filete branco
    box(root, tag + '_laje', (w + 0.1, d + 0.1, 0.06), (cx, cy, z0 + h + 0.03), m=P['roof'], bev=0.016)
    box(root, tag + '_lajeFilete', (w + 0.104, 0.012, 0.016), (cx, yf - 0.051, z0 + h + 0.03), m=P['trim'], bev=0.004)
    zr = z0 + h + 0.06
    # emblema da chapa na testeira (estrela branca)
    emblema(root, tag + '_testeiraEmblema', 0.07, 0.07, loc=(cx + w / 2 - 0.06, yf - 0.058, z0 + h + 0.03), depth=0.006)
    flag_left(root, tag + '_bandeirinha', (cx - w / 2 + 0.02, cy + 0.02, zr), h=0.3)
    # o % grande no telhado, num pedestalzinho branco
    box(root, tag + '_sinalBase', (sign * 0.7, 0.1, 0.05), (cx, cy + 0.02, zr + 0.025), m=P['wall'], bev=0.012)
    with grupo(root, tag + '_sinal', loc=(cx, cy + 0.02, zr + 0.05 + sign * 0.55)) as g:
        percent(root, tag + '_sinalPct', sign, (0, 0, 0), P['roof'])
        percent(root, tag + '_sinalPctBorda', sign * 1.02, (0, 0.012, 0), P['trim'], depth=sign * 0.12)

    def fn(o, mb, ph):
        a = TAU * ph
        o.matrix_basis = Matrix.Translation((0, 0, 0.018 * math.sin(a))) @ mb @ Matrix.Rotation(0.06 * math.sin(a + 1), 4, 'Y')
    register_anim(g, fn)
    return (cx, cy, zr)


# ---------------------------------------------------------------- nivel 1: o guiche
def build_mk1(P, root):
    plot(root, P, 'mk1')
    lights = []
    zp = plinth(root, P, 'mk1_base', -0.02, 0.16, 0.76, 0.56, steps=1)
    rx, ry, rz = receita(root, P, 'mk1_guiche', -0.02, 0.24, 0.5, 0.3, 0.4, zp, windows=1, sign=0.36)
    esteira(root, P, 'mk1_esteira', -0.42, 0.3, -0.06, zp + 0.13, zp, n=4, w=0.14, ps=0.5, s=0.95)
    pilha_pacotes(root, P, 'mk1_pilha', 0.42, -0.1, G, n=4, seed=2, s=0.9)
    coin_stack(root, P, 'mk1_pilhaMoeda1', -0.46, -0.34, 5, seed=1)
    coin_stack(root, P, 'mk1_pilhaMoeda2', -0.34, -0.44, 3, seed=2)
    loose_coins(root, P, 'mk1_moeda', 0.06, -0.46, n=3, spread=0.08)
    globe_lamp(root, P, 'mk1_poste', -0.56, -0.12, G, h=0.34, lights=lights)
    return {'slots': [(0.46, -0.48, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (rx, ry - 0.1, rz)}}


# ---------------------------------------------------------------- nivel 2: guiche duplo e a esteira maior
def build_mk2(P, root):
    plot(root, P, 'mk2')
    lights = []
    zp = plinth(root, P, 'mk2_base', 0.06, 0.16, 0.92, 0.64, steps=2, h=0.05)
    rx, ry, rz = receita(root, P, 'mk2_guiche', 0.06, 0.26, 0.7, 0.34, 0.52, zp, windows=2, sign=0.44)
    esteira(root, P, 'mk2_esteira', -0.4, 0.46, -0.08, zp + 0.13, zp, n=4, w=0.15, ps=0.5, s=1.0)
    pilha_pacotes(root, P, 'mk2_pilha', 0.6, -0.3, G, n=6, seed=3, s=0.95)
    coin_stack(root, P, 'mk2_pilhaMoeda1', 0.26, -0.48, 6, seed=4)
    coin_stack(root, P, 'mk2_pilhaMoeda2', 0.38, -0.42, 3, seed=5)
    loose_coins(root, P, 'mk2_moeda', -0.12, -0.5, n=4, spread=0.08)
    for sx in (-1, 1):
        globe_lamp(root, P, f'mk2_poste{sx}', 0.06 + sx * 0.44, 0.04, zp, h=0.34, lights=lights)
    return {'slots': [(-0.54, -0.4, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (rx, ry - 0.12, rz)}}


# ---------------------------------------------------------------- nivel 3: o predio da Receita com brises de Brasilia
def build_mk3(P, root):
    plot(root, P, 'mk3')
    lights = []
    zp = plinth(root, P, 'mk3_base', 0.04, 0.14, 1.02, 0.68, steps=2, h=0.055)
    rx, ry, rz = receita(root, P, 'mk3_predio', 0.04, 0.26, 0.82, 0.36, 0.7, zp, windows=3, fins=10, sign=0.56)
    esteira(root, P, 'mk3_esteira', -0.44, 0.5, -0.1, zp + 0.13, zp, n=4, w=0.16, ps=0.5, s=1.05)
    spinning_coin(root, P, 'mk3_moedaGira', (-0.64, -0.2, G + 0.19 + 0.07), r=0.06)
    coin_stack(root, P, 'mk3_pilhaMoeda1', -0.64, -0.2, 10, seed=6)
    coin_stack(root, P, 'mk3_pilhaMoeda2', -0.66, -0.4, 6, seed=7)
    coin_stack(root, P, 'mk3_pilhaMoeda3', -0.7, -0.02, 4, seed=8)
    pilha_pacotes(root, P, 'mk3_pilha', 0.56, -0.38, G, n=8, seed=4, s=1.0)
    loose_coins(root, P, 'mk3_moeda', 0.06, -0.54, n=4, spread=0.1)
    for sx in (-1, 1):
        globe_lamp(root, P, f'mk3_poste{sx}', 0.04 + sx * 0.5, 0.02, zp, h=0.36, lights=lights)
    return {'slots': [(-0.44, -0.52, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (rx, ry - 0.12, rz)}}


# ---------------------------------------------------------------- Receita do Taxad: o galpao da alfandega, a montanha de
# pacotes, o painel com o %, o balcao (os dois fiscais atras) e o carimbo gigante
def build_mkB(P, root):
    plot(root, P, 'mkB')
    lights = []
    # fachada do galpao (chapa canelada branca) com a faixa vermelha e o painel aceso
    box(root, 'mkB_parede', (1.16, 0.12, 0.86), (0.0, 0.42, G + 0.43), m=P['wall'], bev=0.02)
    for k in range(13):
        box(root, f'mkB_canelura{k}', (0.026, 0.02, 0.62), (-0.54 + k * 0.09, 0.356, G + 0.36), m=P['wall_d'], bev=0.008)
    box(root, 'mkB_paredeFriso', (1.2, 0.15, 0.08), (0.0, 0.42, G + 0.88), m=P['roof'], bev=0.014)
    box(root, 'mkB_paredeFilete', (1.204, 0.012, 0.016), (0.0, 0.343, G + 0.85), m=P['trim'], bev=0.004)
    slab(root, 'mkB_painelMoldura', 0.5, 0.34, 0.03, P['roof_d'], r=0.04, loc=(0.0, 0.345, G + 0.64), bev=0.008)
    slab(root, 'mkB_painel', 0.44, 0.28, 0.02, P['screen'], r=0.03, loc=(0.0, 0.33, G + 0.64), bev=0.004)
    percent(root, 'mkB_painelPct', 0.2, (0.0, 0.318, G + 0.64), P['screen_w'], depth=0.012)
    for sx in (-1, 1):
        # flamula da chapa na parede, ao lado do painel
        box(root, f'mkB_flamula{sx}', (0.13, 0.012, 0.3), (sx * 0.4, 0.34, G + 0.6), m=cor('pri', rough=0.8, sheen=0.4), bev=0.004)
        box(root, f'mkB_flamulaBarra{sx}', (0.15, 0.02, 0.018), (sx * 0.4, 0.336, G + 0.755), m=P['steel'], bev=0.004)
        emblema(root, f'mkB_flamulaEmblema{sx}', 0.12, 0.12, loc=(sx * 0.4, 0.33, G + 0.63), depth=0.005)
    # a montanha de pacotes encostada no galpao (esquerda): piramide de caixas carimbadas, blusinhas e envelopes
    rr = random.Random(31)
    k = 0
    for lv in range(6):
        nx, ny = max(1, 4 - lv * 0.7), max(1, 3 - lv * 0.5)
        nx, ny = int(round(nx)), int(round(ny))
        for i in range(nx):
            for j in range(ny):
                x = -0.56 + (i - (nx - 1) / 2) * 0.12 + rr.uniform(-0.015, 0.015)
                y = 0.2 + (j - (ny - 1) / 2) * 0.1 + rr.uniform(-0.015, 0.015) - 0.02 * lv
                z = G + lv * 0.085
                if k % 5 == 3:
                    blusinha(root, P, f'mkB_monte{k}', k, s=1.25, loc=(x, y, z), rot=(0, 0, rr.uniform(-0.6, 0.6)))
                elif k % 5 == 1:
                    envelope_plastico(root, P, f'mkB_monte{k}', s=1.25, loc=(x, y, z), rot=(0, 0, rr.uniform(-0.6, 0.6)))
                else:
                    pacote(root, P, f'mkB_monte{k}', s=1.2 * rr.uniform(0.92, 1.08), loc=(x, y, z), rot=(0, 0, rr.uniform(-0.35, 0.35)), stamp=k % 2 == 0)
                k += 1
    pilha_pacotes(root, P, 'mkB_pilhaDir', 0.6, 0.18, G, n=6, seed=9, s=1.1)
    # balcao na frente (camada da frente: cobre as pernas dos fiscais)
    zc = G + 0.34
    box(root, 'mkB_balcao', (1.06, 0.2, 0.32), (0.0, -0.16, G + 0.16), m=P['wall'], bev=0.02, front=True)
    box(root, 'mkB_balcaoTampo', (1.12, 0.26, 0.04), (0.0, -0.17, zc - 0.02), m=P['roof'], bev=0.012, front=True)
    for k in range(4):
        box(root, f'mkB_balcaoPainel{k}', (0.2, 0.012, 0.2), (-0.39 + 0.26 * k, -0.265, G + 0.15), m=P['wall_d'], bev=0.006, front=True)
        box(root, f'mkB_balcaoFriso{k}', (0.21, 0.014, 0.014), (-0.39 + 0.26 * k, -0.27, G + 0.26), m=P['roof'], bev=0.003, front=True)
    emblema(root, 'mkB_balcaoEmblema', 0.12, 0.12, loc=(0.0, -0.274, G + 0.15), depth=0.006)
    for o in [o for o in bpy.data.objects if o.name.startswith('mkB_balcaoEmblema')]:
        o['front'] = 1
    # o carimbo gigante no meio do balcao, cravado na caixinha (fica na camada da frente, parado: o que esta em cima do
    # balcao nao pode mexer, senao some atras da camada da frente); o ponto 'top' e o pegador
    pk = pacote(root, P, 'mkB_pacoteBalcao', s=1.6, loc=(0.0, -0.17, zc), front=True)
    st = empty(root, 'mkB_carimboPivo', loc=(0.0, -0.17, zc + pk['h'] + 0.004), rot=(0, 0.06, 0))
    kids(st, *carimbo(root, P, 'mkB_carimbo', s=1.25, front=True))
    for k, (dx, dz) in enumerate(((-0.13, 0.03), (0.14, 0.0))):
        for j in range(3):
            a = (j - 1) * 0.5 + (0 if dx < 0 else math.pi)
            box(root, f'mkB_impacto{k}{j}', (0.05, 0.012, 0.012), (dx + 0.03 * math.cos(a) * (1 if dx > 0 else -1), -0.26, zc + pk['h'] + 0.03 + dz + 0.03 * j),
                rot=(0, -0.5 + 0.5 * j if dx > 0 else 0.5 - 0.5 * j, 0), m=P['trim'], bev=0.004, front=True)
    # simbolos de % vermelhos subindo do carimbo (cada um no seu tempo, acima do balcao)
    for k in range(3):
        e = percent(root, f'mkB_pctSobe{k}', 0.1, (0.0, -0.2, zc + 0.5), P['coin'])

        def rise(o, mb, ph, k=k):
            p = (ph + k / 3) % 1.0
            sc = max(0.001, math.sin(math.pi * p) ** 0.6)
            dx = (k - 1) * 0.14 * p + 0.03 * math.sin(TAU * p)
            o.matrix_basis = Matrix.Translation((dx, 0, 0.32 * p)) @ mb @ Matrix.Rotation(0.3 * (k - 1) * p, 4, 'Y') @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(e, rise)
    coin_stack(root, P, 'mkB_pilhaBalcao', 0.38, -0.18, 4, r=0.045, z0=zc, seed=11)
    for o in [o for o in bpy.data.objects if o.name.startswith('mkB_pilhaBalcao')]:
        o['front'] = 1
    # pacotes e blusinhas voando para a montanha (cada um no seu tempo)
    for k, (x, y, z, rz) in enumerate(((-0.24, -0.22, 0.98, 0.3), (0.26, -0.26, 1.06, -0.4), (-0.5, -0.3, 0.74, 0.6), (0.52, -0.32, 0.8, -0.2),
                                       (0.02, -0.3, 1.24, 0.1))):
        if k % 2:
            e = blusinha(root, P, f'mkB_voa{k}', k + 2, s=1.4, loc=(x, y, z), rot=(0.9, 0.25 * (k % 3 - 1), rz), folded=False)
        else:
            e = pacote(root, P, f'mkB_voa{k}', s=1.15, loc=(x, y, z), rot=(0.2, 0.25 * (k % 3 - 1), rz), stamp=True)

        def fly(o, mb, ph, p0=0.21 * k, sg=1 if k % 2 else -1):
            a = TAU * (ph + p0)
            o.matrix_basis = Matrix.Translation((0.02 * sg * math.sin(a), 0, 0.035 * math.sin(a))) @ mb @ Matrix.Rotation(0.25 * math.sin(a + 0.7), 4, 'Y')
        register_anim(e, fly)
    coin_stack(root, P, 'mkB_pilha1', 0.6, -0.44, 5, seed=12)
    loose_coins(root, P, 'mkB_moeda', 0.36, -0.56, n=3, spread=0.06)
    pilha_pacotes(root, P, 'mkB_pilhaChao', -0.56, -0.44, G, n=4, seed=13, s=0.95)
    globe_lamp(root, P, 'mkB_poste', -0.7, -0.14, G, h=0.4, lights=lights)
    lights.append(((0.0, 0.25, G + 0.64), '#ff9a8a', 8.0, 1))
    return {'slots': [(-0.26, 0.08, G), (0.27, 0.1, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (0.0, -0.18, zc + 0.42)}}


# ---------------------------------------------------------------- Arcabouco Fiscal: o cofrinho de porquinho no andaime
def porquinho(root, P, tag, cx, cy, z0, L=0.84, D=0.56, H=0.52):
    """Cofrinho de porquinho vermelho de perfil (focinho para a esquerda), estrela branca no flanco, a fenda das moedas
    no lombo, orelhas, perninhas, rabinho enrolado e o olhinho. Devolve o topo do lombo (z)."""
    zc = z0 + 0.1 + H / 2
    sphere(root, tag + '_corpo', 1.0, (cx, cy, zc), scale=(L / 2, D / 2, H / 2), m=P['pig'], seg=40)
    # focinho
    fx = cx - L / 2 + 0.01
    cyl(root, tag + '_focinho', 0.1, 0.1, (fx - 0.02, cy, zc - 0.03), rot=(0, math.pi / 2, 0), r2=0.09, m=P['pig'], v=28, bev=0.03)
    cyl(root, tag + '_focinhoPonta', 0.085, 0.02, (fx - 0.075, cy, zc - 0.03), rot=(0, math.pi / 2, 0), m=P['pig_d'], v=28, bev=0.008)
    for sy in (-1, 1):
        sphere(root, f'{tag}_narina{sy}', 0.018, (fx - 0.087, cy + sy * 0.03, zc - 0.03), scale=(0.5, 1, 1.3), m=P['slot'], seg=10)
    # olho e orelhas
    sphere(root, tag + '_olho', 0.026, (fx + 0.13, cy - D * 0.36, zc + 0.08), m=P['eye'], seg=12)
    sphere(root, tag + '_olhoBrilho', 0.008, (fx + 0.126, cy - D * 0.36 - 0.022, zc + 0.09), m=P['trim'], seg=8)
    for sy in (-1, 1):
        cyl(root, f'{tag}_orelha{sy}', 0.07, 0.11, (fx + 0.2, cy + sy * 0.12, zc + H / 2 - 0.02), r2=0.0, rot=(sy * 0.3, -0.35, 0), m=P['pig'], v=4, bev=0.02)
    # pernas
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(root, f'{tag}_perna{sx}{sy}', 0.065, 0.16, (cx + sx * L * 0.27, cy + sy * D * 0.24, z0 + 0.08), r2=0.06, m=P['pig'], v=20, bev=0.02)
            cyl(root, f'{tag}_casco{sx}{sy}', 0.062, 0.025, (cx + sx * L * 0.27, cy + sy * D * 0.24, z0 + 0.012), m=P['pig_d'], v=20, bev=0.008)
    # rabinho enrolado
    tx = cx + L / 2 - 0.01
    pts = [(tx + 0.02 + 0.05 * t + 0.03 * math.cos(TAU * 1.5 * t), cy + 0.03 * math.sin(TAU * 1.5 * t), zc + 0.05 + 0.08 * t) for t in [j / 16 for j in range(17)]]
    tube(root, tag + '_rabo', pts, 0.014, P['pig'], segs=8)
    # estrela no flanco (de frente para a camera)
    sx_ = -0.1
    yf_ = cy - D / 2 * math.sqrt(1 - (sx_ / (L / 2)) ** 2)
    estrela(root, tag + '_estrela', 0.12, 0.05, loc=(cx + sx_, yf_ + 0.006, zc - 0.01), rot=(-0.1, 0, 0.0))
    # fenda das moedas no lombo
    zt = zc + H / 2
    box(root, tag + '_fenda', (0.16, 0.03, 0.02), (cx + 0.04, cy, zt - 0.002), m=P['slot'], bev=0.008)
    box(root, tag + '_fendaAro', (0.19, 0.055, 0.012), (cx + 0.04, cy, zt - 0.008), m=P['pig_d'], bev=0.006)
    return zt


def andaime(root, P, tag, x0, x1, y0, y1, levels, zf=G, plank_z=None):
    """O arcabouco: andaime de tubos (montantes, travessas, diagonais em X atras) com abracadeiras laranja e as tabuas."""
    xs = (x0, x1)
    ys = (y0, y1)
    ztop = levels[-1]
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            tube(root, f'{tag}_montante{i}{j}', [(x, y, zf), (x, y, ztop + 0.06)], 0.022, P['scaf'], segs=10)
            cyl(root, f'{tag}_sapata{i}{j}', 0.04, 0.02, (x, y, zf + 0.01), m=P['clamp'], v=12, bev=0.004)
    for li, z in enumerate(levels):
        for j, y in enumerate(ys):
            tube(root, f'{tag}_travessaX{li}{j}', [(x0 - 0.03, y, z), (x1 + 0.03, y, z)], 0.017, P['scaf'], segs=8)
        for i, x in enumerate(xs):
            tube(root, f'{tag}_travessaY{li}{i}', [(x, y0 - 0.03, z + 0.02), (x, y1 + 0.03, z + 0.02)], 0.017, P['scaf'], segs=8)
            for j, y in enumerate(ys):
                sphere(root, f'{tag}_abracadeira{li}{i}{j}', 0.03, (x, y, z), scale=(1, 1, 0.8), m=P['clamp'], seg=10)
    # diagonais (no fundo e nos lados; na frente so uma, para nao esconder o porquinho)
    for li in range(len(levels) - 1):
        za, zb = levels[li], levels[li + 1]
        tube(root, f'{tag}_diagFundo{li}', [(x0, y1, za) if li % 2 else (x1, y1, za), (x1, y1, zb) if li % 2 else (x0, y1, zb)], 0.011, P['scaf'], segs=6)
        for i, x in enumerate(xs):
            tube(root, f'{tag}_diagLado{li}{i}', [(x, y0, za), (x, y1, zb)], 0.011, P['scaf'], segs=6)
    tube(root, f'{tag}_diagFrente', [(x0, y0, levels[-2]), (x0 + (x1 - x0) * 0.32, y0, levels[-1])], 0.011, P['scaf'], segs=6)
    for pi_, pz in enumerate(plank_z or []):
        for k in range(2):
            yy = y0 + 0.07 + k * (y1 - y0 - 0.14)
            box(root, f'{tag}_tabua{pi_}{k}', (x1 - x0 + 0.12, 0.1, 0.022), (0.5 * (x0 + x1), yy, pz + 0.04), m=P['plank'], bev=0.006)
        box(root, f'{tag}_rodape{pi_}', (x1 - x0 + 0.12, 0.015, 0.07), (0.5 * (x0 + x1), y0 - 0.005, pz + 0.085), m=P['plank'], bev=0.004)
        # faixa listrada de obra no rodape (vermelho e branco)
        for k in range(8):
            box(root, f'{tag}_listra{pi_}{k}', ((x1 - x0) / 8 * 0.5, 0.004, 0.07), (x0 - 0.06 + (k + 0.5) * (x1 - x0 + 0.12) / 8, y0 - 0.014, pz + 0.085),
                m=P['pig'], bev=0.0)


def build_mkT(P, root):
    plot(root, P, 'mkT')
    lights = []
    cx, cy = -0.04, 0.12
    z0 = G
    zt = porquinho(root, P, 'mkT_porco', cx, cy, z0)
    # o andaime em volta e a plataforma la em cima
    levels = [G + 0.48, G + 1.04, G + 1.64]
    andaime(root, P, 'mkT_andaime', cx - 0.5, cx + 0.5, cy - 0.34, cy + 0.34, levels, plank_z=[levels[1], levels[2]])
    box(root, 'mkT_baldeObra', (0.08, 0.08, 0.09), (cx + 0.34, cy + 0.12, levels[1] + 0.105), m=P['roof_d'], bev=0.012)
    pilha_pacotes(root, P, 'mkT_pilhaAndaime', cx - 0.26, cy + 0.12, levels[1] + 0.06, n=3, seed=21, s=0.9)
    # bandeirinha da chapa no alto do andaime
    flag_left(root, 'mkT_bandeirinha', (cx - 0.5, cy - 0.34, levels[-1] + 0.06), h=0.34)
    # moedas caindo na fenda (giram e somem dentro do porquinho)
    for k in range(3):
        e = empty(root, f'mkT_moedaCai{k}', loc=(cx + 0.04, cy, zt + 0.02))
        kids(e, cyl(root, f'mkT_moedaCai{k}_moeda', 0.05, 0.014, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['coin'], v=24, bev=0.004),
             torus(root, f'mkT_moedaCai{k}_relevo', (0, 0, 0), 0.034, 0.004, P['coin_d'], axis='Y', n=20, segs=4))

        def fall(o, mb, ph, k=k):
            p = (ph + k / 3) % 1.0
            zz = 0.26 * (1 - p) ** 1.6
            sc = max(0.001, min(1.0, (1 - p) / 0.12))
            o.matrix_basis = Matrix.Translation((0.04 * math.sin(TAU * p) * (1 - p), 0, zz)) @ mb @ Matrix.Rotation(TAU * p, 4, 'Z') @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(e, fall)
    # moedas no chao, pacotes taxados e o poste
    coin_stack(root, P, 'mkT_pilha1', -0.62, -0.36, 7, seed=13)
    coin_stack(root, P, 'mkT_pilha2', -0.48, -0.5, 4, seed=14)
    loose_coins(root, P, 'mkT_moedaChao', -0.64, -0.18, n=6, spread=0.12, seed=15)
    pilha_pacotes(root, P, 'mkT_pilha', 0.54, -0.36, G, n=6, seed=16, s=1.0)
    lights.append(((cx, cy - 0.38, z0 + 0.4), '#ffe0a0', 8.0, 1))
    globe_lamp(root, P, 'mkT_poste', 0.68, -0.06, G, h=0.4, lights=lights)
    return {'slots': [(0.3, -0.52, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (cx, cy, zt + 0.3)}}


# ---------------------------------------------------------------- os fiscais (tripulacao)
def coin_bag(root, P, tag):
    """Saco de moedas amarrado (pendurado pela boca na mao: o saco fica embaixo) com o % carimbado."""
    sack_m = mat('saco_moedas', '#d8c08a', rough=0.85, var=0.03, bump=0.15)
    objs = [sphere(root, tag + '_saco', 0.06, (0, 0, 0.085), scale=(1, 1, 1.05), m=sack_m, seg=16),
            cyl(root, tag + '_sacoBoca', 0.034, 0.04, (0, 0, 0.02), r2=0.026, m=sack_m, v=12, bev=0.006),
            torus(root, tag + '_sacoCordao', (0, 0, 0.03), 0.028, 0.006, P['coin_d'], n=12, segs=4)]
    return objs


def carimbo_mao(root, P, tag):
    """Carimbo de mao (pegador na mao, borracha para a frente: eixo Z local)."""
    e = empty(root, tag + '_carimboMao', rot=(math.pi, 0, 0))   # o pegador fica na mao e a borracha aponta para fora
    for o in carimbo(root, P, tag + '_cm', s=0.38):
        o.parent = e
        o.location.z -= 0.23 * 0.38
    return [e]


def chave_inglesa(root, P, tag):
    """Chave inglesa gigante (o fiscal do arcabouco aperta o andaime), segurada em pe como um bastao."""
    return [tube(root, tag + '_chaveCabo', [(0, 0, -0.28), (0, 0, 0.26)], 0.018, P['scaf'], segs=10),
            tube(root, tag + '_chaveEmpunhadura', [(0, 0, -0.27), (0, 0, -0.08)], 0.023, P['roof'], segs=10),
            box(root, tag + '_chaveCabeca', (0.03, 0.12, 0.06), (0, 0.01, 0.29), m=P['scaf'], bev=0.01),
            box(root, tag + '_chaveMandibula1', (0.03, 0.03, 0.07), (0, 0.055, 0.35), m=P['scaf'], bev=0.008),
            box(root, tag + '_chaveMandibula2', (0.03, 0.03, 0.05), (0, -0.035, 0.34), m=P['scaf'], bev=0.008),
            cyl(root, tag + '_chaveRosca', 0.014, 0.05, (0, 0.0, 0.26), rot=(math.pi / 2, 0, 0), m=P['clamp'], v=10, bev=0.003)]


def cap_bill(root, pr, tag, m):
    o = cyl(root, tag + '_aba', 0.06, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.18, 0)
    return o


def colete(root, P, pr, tag):
    """Colete de fiscal: faixa refletiva clara e a estrela branca no peito."""
    t = torus(root, tag + '_coleteFaixa', (0, 0, 0.36), 0.088, 0.007, mat('faixa_refletiva', '#eef2f4', rough=0.25, var=0, bump=0), n=24, segs=4)
    t.scale = (1.0, 1.17, 1.0)
    t.parent = pr['body']
    estrela_peito(root, tag, pr['body'], (0.1, -0.03, 0.408), r=0.027, rot=(0, 0, math.pi / 2 - 0.3))


def build_fiscal(P, root):
    """Fiscal da Receita: camisa clara, colete vermelho com estrela, bone vermelho, jeans; carimbo numa mao e o saco
    de moedas da arrecadacao na outra."""
    tag = root['set']
    shirt = mat('camisa_fiscal', '#f4f1ea', rough=0.8, var=0.0, bump=0.03, sheen=0.2)
    pr = build_person(P, root, tag, dict(tunic=shirt, vest=cor('pri', rough=0.7, sheen=0.3), sleeve=shirt, bracer=P['skin'], head='cap', head_m=cor('bone'),
                                         belt=None, skirt_m=cor('calca'), pants=cor('calca'), boot_m=shoes(), boot_cuff=cor('calca'), bare_hands=True))
    cap_bill(root, pr, tag, cor('bone'))
    colete(root, P, pr, tag)
    glasses(root, pr, tag)
    hold(pr, 'L', *coin_bag(root, P, tag))
    hold(pr, 'R', *carimbo_mao(root, P, tag))
    return pr


def build_mestre(P, root):
    """Mestre do arcabouco: grandao de colete vermelho, capacete de obra vermelho, oculos escuros e a chave inglesa."""
    tag = root['set']
    shirt = cor('camisa')
    pr = build_person(P, root, tag, dict(tunic=shirt, vest=cor('escuro', rough=0.7, sheen=0.3), sleeve=shirt, bracer=P['skin'], head='bald', belt=None,
                                         skirt_m=cor('calca'), pants=cor('calca'), boot_m=mat('botina', '#4a3426', rough=0.6, var=0, bump=0.05),
                                         boot_cuff=cor('calca'), bare_hands=True, big=1.06))
    hard_hat(root, pr, tag, cor('bone', rough=0.35), ridge=cor('sec', rough=0.4))
    colete(root, P, pr, tag)
    glasses(root, pr, tag, mat('lente_escura_receita', '#141418', rough=0.15, var=0, bump=0), dark=True)
    hold(pr, 'R', *chave_inglesa(root, P, tag))
    return pr


IDLE_N, ACT_N = 12, 8


def gerente_state(mode, f):
    """idle: mostra o carimbo com a mao direita; act: ergue o saco de moedas (a arrecadacao da onda)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.18, -0.12, 0.36 + 0.04 * s), grip_R=(1.0, 0, 0.3), hand_L=(0.06, 0.13, 0.3), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.15, ph=ph)
    k = math.sin(TAU * f / ACT_N)
    return dict(hand_L=(0.12, 0.1, 0.56 + 0.05 * k), grip_L=(0.0, 0.0, 1.0), hand_R=(0.14, -0.1, 0.4), head_pitch=-0.25, head_yaw=0.1, breathe=0.5, ph=f / ACT_N)


def seguranca_state(mode, f):
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.06, -0.14, 0.3 + 0.006 * s), grip_R=(0.05, 0.0, 1.0), hand_L=(0.04, 0.13, 0.27), breathe=s,
                    head_yaw=0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_R=(0.08, -0.14, 0.3 + 0.12 * k), grip_R=(0.05, 0.0, 1.0), hand_L=(0.1, 0.12, 0.3 + 0.08 * k), head_pitch=-0.2 * k, ph=f / ACT_N)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'mk1': 'mkM', 'mk2': 'mkM', 'mk3': 'mkM', 'mkB': ['mkM', 'mkM'], 'mkT': 'mkG'},
    'towers': [('mk1', 'Taxa das Blusinhas N1', build_mk1), ('mk2', 'Taxa das Blusinhas N2', build_mk2), ('mk3', 'Taxa das Blusinhas N3', build_mk3),
               ('mkB', 'Receita do Taxad', build_mkB), ('mkT', 'Arcabouco Fiscal', build_mkT)],
    'crews': [crew('mkM', 'Fiscal da Receita', build_fiscal, gerente_state), crew('mkG', 'Mestre do arcabouco', build_mestre, seguranca_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
