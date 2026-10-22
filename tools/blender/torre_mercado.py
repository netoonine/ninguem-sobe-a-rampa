"""Banco Vorcash (Mercado, Ninguem Sobe a Rampa): niveis 1 a 3, Emenda Pix e CDB de 140%. Agencia bancaria pequena e
brilhante de marmore branco com telhado na cor da chapa, colunas de capitel dourado, porta de cofre redonda (o volante gira),
pilhas de moedas, barras de ouro e a seta de grafico subindo no telhado (sem texto, sem logo, sem nome), sobre o lote
de concreto branco de Brasilia (conceito: arte/conceitos/torres/vorcash.png).
Nomes de conjuntos, postos, pontos e modos sao os mesmos do Barco-Feira (js/sprites.js depende deles).
Cores da chapa (chapa.py): o ouro do dinheiro fica (moedas, barras, chave, cofre redondo, seta do grafico); telhado,
friso, balcao, aco do cofre e a turma saem na cor da chapa. CHAPA=V (padrao): telhado verde com filete amarelo, medalhao
com o losango amarelo e o circulo azul, gerente de terno verde e gravata amarela; CHAPA=R: telhado vermelho com filete
branco, medalhao com a estrela branca, gerente de terno vermelho com a estrela branca na lapela. Bandeirinha da chapa no
beiral (ou flamulas na parede, ou espetada no monte de moedas). Tamanho, ancora, postos e pontos iguais nas duas.

  Blender -b -P tools/blender/torre_mercado.py -- render arte/render/mercado [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_mercado.py -- render arte/render_r/mercado [conjuntos...]
  Blender -b -P tools/blender/torre_mercado.py -- still <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, prism_xz, G   # noqa: F811 - lote de concreto de Brasilia
from pecas_zcv import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, emblema, bandeirinha   # cores da chapa: CHAPA=V (padrao) ou CHAPA=R

FRONT = -math.pi / 2
FAM = 'mercado'

import lib as _lib
_orig_palette2 = palette2


# aco do cofre e tela por chapa (o resto sai de chapa.cor)
VC = {'V': dict(steel='#2e5c41', steel_d='#1f3f2c', screen='#38c06a', luz='#8fe8a8'),
      'R': dict(steel='#7a2b2d', steel_d='#561c1e', screen='#e24a40', luz='#ff9a8a')}[CHAPA]


def palette2():   # noqa: F811 - ouro do dinheiro, marmore branco e as cores da chapa (telhado, friso, aco do cofre)
    P = _orig_palette2()
    P['coin'] = mat('moeda_ouro', '#f0bd43', rough=0.28, metal=0.75, var=0.04, bump=0.02)
    P['coin_d'] = mat('moeda_ouro_borda', '#d39a2c', rough=0.32, metal=0.7, var=0.03, bump=0.02)
    P['bar'] = mat('barra_ouro', '#f6c752', rough=0.2, metal=0.85, var=0.03, bump=0.01)
    P['roof'] = mat('telhado_chapa_' + CHAPA, PAL['pri'], rough=0.3, metal=0.25, var=0.02, bump=0.01)   # telhado, friso e balcao
    P['trim'] = cor('sec', rough=0.35)                                                                  # filete do friso
    P['marble'] = mat('marmore_vorcash', '#f4f0e8', rough=0.3, var=0.03, bump=0.03)
    P['marble_d'] = mat('marmore_vorcash_base', '#ddd5c6', rough=0.35, var=0.04, bump=0.04)
    P['chart'] = mat('barra_grafico_' + CHAPA, PAL['claro'], rough=0.3, var=0.02, bump=0.01)
    P['steel_b'] = mat('aco_cofre_' + CHAPA, VC['steel'], rough=0.35, metal=0.5, var=0.03, bump=0.02)
    P['steel_bd'] = mat('aco_cofre_escuro_' + CHAPA, VC['steel_d'], rough=0.4, metal=0.45, var=0.03, bump=0.02)
    P['crack'] = mat('rachadura', '#2a2220', rough=0.9, var=0.0, bump=0.0)
    P['kraft'] = mat('envelope_pardo', '#c9995c', rough=0.8, var=0.05, bump=0.04)
    P['lamp'] = glow_mat('globo_vorcash', '#fff1c8', 0.8, 9.0, rough=0.4, var=0.0, bump=0.0)
    P['screen'] = glow_mat('tela_maquininha_' + CHAPA, VC['screen'], 0.5, 3.0, rough=0.2, var=0.0, bump=0.0)
    P['pos'] = mat('maquininha', '#3a3f48', rough=0.45, var=0.02, bump=0.02)
    P['key'] = mat('tecla', '#e4e6e8', rough=0.5, var=0.0, bump=0.0)
    P['conc'] = concrete()
    P['teal'] = cor('pri', rough=0.6, sheen=0.4)   # pano de assinatura na cor da chapa
    P['stripes'] = mat('toldo_vorcash_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(3.6, PAL['claro'], PAL['pri']), sheen=0.4)
    P['_emblem'] = 'coin'
    return P


_lib.palette2 = palette2


# ---------------------------------------------------------------- moedas, barras, seta do grafico
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


def frustum(root, name, size, top, h, loc, rz=0.0, m=None, bev=0.012):
    """Tronco de piramide retangular (barra de ouro): base size=(w, d), topo top=(wt, dt), altura h."""
    bm = bmesh.new()
    (w, d), (wt, dt) = size, top
    a = [bm.verts.new((sx * w / 2, sy * d / 2, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    b = [bm.verts.new((sx * wt / 2, sy * dt / 2, h)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], a[j], b[j], b[i]))
    o = bm_to_obj(bm, name, root, [m], bev=bev, angle=30)
    o.location = loc
    o.rotation_euler = (0, 0, rz)
    return o


def gold_bars(root, P, tag, x, y, rows=(3, 2, 1), rz=0.0, z0=G, s=1.0):
    """Barras de ouro empilhadas em piramide."""
    w, d, h = 0.2 * s, 0.09 * s, 0.06 * s
    c, sn = math.cos(rz), math.sin(rz)
    for r_, n in enumerate(rows):
        for k in range(n):
            u = (k - (n - 1) / 2) * (d + 0.006)
            frustum(root, f'{tag}{r_}{k}', (w, d), (w * 0.8, d * 0.68), h, (x - sn * u, y + c * u, z0 + h * r_), rz=rz, m=P['bar'], bev=0.01 * s)
    return z0 + h * len(rows)


def zigzag_arrow(root, P, tag, pts, r=0.03, head=0.11, m=None, crack=None):
    """Seta de grafico subindo em zigue-zague (tubo grosso de ponta a ponta) com a ponta triangular no fim, no plano XZ.
    crack = indice do segmento com a rachadura discreta."""
    m = m or P['bar']   # a seta do lucro e sempre de ouro
    pts = [Vector(p) for p in pts]
    tube(root, tag, pts, r, m, segs=10)
    for k, p in enumerate(pts[1:-1]):
        sphere(root, f'{tag}_junta{k}', r * 1.02, p, m=m, seg=12)
    d = (pts[-1] - pts[-2]).normalized()
    hd = cyl(root, tag + '_ponta', head * 0.8, head * 1.1, (0, 0, 0), r2=0.0, m=m, v=4, bev=0.008)
    hd.matrix_basis = Matrix.Translation(pts[-1] + d * head * 0.4) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4() @ Matrix.Diagonal((1.0, 0.4, 1.0, 1.0))
    if crack is not None:
        a, b = pts[crack], pts[crack + 1]
        t = (b - a)
        nrm = Vector((-t.z, 0, t.x)).normalized()
        cp = [a.lerp(b, 0.45 + 0.05 * j) + nrm * (r * (0.9 if j % 2 else -0.9)) + Vector((0, -r * 0.95, 0)) for j in range(4)]
        tube(root, tag + '_rachadura', cp, r * 0.12, P['crack'], segs=4)
    return pts[-1]


def chart(root, P, tag, x, y, z, s=1.0, bars=(0.18, 0.3, 0.42), bob=True, ph0=0.0, crack=None):
    """Grafico em cima do telhado: barras claras subindo e a seta dourada passando por cima (balanca, anim)."""
    bw = 0.09 * s
    n = len(bars)
    x0 = x - (n - 1) * bw * 0.65
    for k, hh in enumerate(bars):
        slab(root, f'{tag}_barra{k}', bw, hh * s, 0.05 * s, P['chart'], r=0.015 * s, loc=(x0 + k * bw * 1.3, y + 0.04 * s, z + hh * s / 2), bev=0.008)
    with grupo(root, tag + '_seta', loc=(x, y - 0.03 * s, z)) as g:
        xs = [-(n - 1) * bw * 0.65 - bw * 0.9 + j * ((n - 1) * bw * 1.3 + bw * 1.8) / 4 for j in range(5)]
        zs = [0.1, 0.26, 0.2, 0.42, 0.52]
        top = zigzag_arrow(root, P, tag + '_zigue', [(xs[j], 0, zs[j] * s * (max(bars) / 0.42)) for j in range(5)], r=0.026 * s, head=0.1 * s, crack=crack)
    if bob:
        def fn(o, mb, ph, p0=ph0):
            a = TAU * (ph + p0)
            o.matrix_basis = Matrix.Translation((0, 0, 0.025 * s * math.sin(a))) @ mb @ Matrix.Rotation(0.04 * math.sin(a + 1), 4, 'Y')
        register_anim(g, fn)
    return (x + top.x, y, z + top.z)


def spinning_coin(root, P, tag, loc, r=0.06, ph0=0.0):
    """Moeda em pe girando no proprio eixo (o brilho do lucro)."""
    e = empty(root, tag, loc=loc)
    kids(e, cyl(root, tag + '_moeda', r, 0.016, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['coin'], v=26, bev=0.005),
         torus(root, tag + '_relevo', (0, 0, 0), r * 0.68, 0.005, P['coin_d'], axis='Y', n=22, segs=4))

    def fn(o, mb, ph, p0=ph0):
        o.matrix_basis = Matrix.Translation((0, 0, 0.015 * math.sin(TAU * (ph + p0)))) @ mb @ Matrix.Rotation(math.pi * ph, 4, 'Z')
    register_anim(e, fn)
    return e


def globe_lamp(root, P, tag, x, y, z0, h=0.36, lights=None):
    """Poste baixo de latao com globo de luz (a fachada de banco antigo)."""
    cyl(root, tag + '_base', 0.04, 0.03, (x, y, z0 + 0.015), r2=0.032, m=P['gold'], v=16, bev=0.006)
    tube(root, tag + '_haste', [(x, y, z0), (x, y, z0 + h)], 0.012, P['gold'], segs=8)
    torus(root, tag + '_aro', (x, y, z0 + h), 0.03, 0.008, P['gold'], n=14, segs=4)
    sphere(root, tag, 0.05, (x, y, z0 + h + 0.045), m=P['lamp'], seg=16)
    if lights is not None:
        lights.append(((x, y - 0.04, z0 + h + 0.05), '#ffe7b0', 9.0, 1))


def flag_left(root, name, loc, h=0.34):
    """Bandeirinha da chapa com o pano para a esquerda (espelhada: a face com o emblema inteiro fica para a camera)."""
    m = bandeirinha(root, name, loc, h=h)
    m.scale = (-1, 1, 1)
    return m


# ---------------------------------------------------------------- a agencia: base de marmore, colunas, telhado de ouro
def vault_door(root, P, tag, x, y, zc, r=0.16, spin_wheel=True):
    """Porta de cofre redonda de ouro na fachada (voltada para -Y): aro grosso, parafusos e o volante que gira."""
    cyl(root, tag + '_moldura', r * 1.18, 0.03, (x, y - 0.012, zc), rot=(math.pi / 2, 0, 0), m=P['steel_bd'], v=36, bev=0.008)
    cyl(root, tag, r, 0.05, (x, y - 0.035, zc), rot=(math.pi / 2, 0, 0), m=P['gold'], v=36, bev=0.012)
    torus(root, tag + '_aro', (x, y - 0.062, zc), r * 0.9, r * 0.07, P['coin_d'], axis='Y', n=36, segs=6)
    for k in range(10):
        a = TAU * k / 10
        sphere(root, f'{tag}_parafuso{k}', r * 0.06, (x + r * 0.78 * math.cos(a), y - 0.064, zc + r * 0.78 * math.sin(a)), scale=(1, 0.5, 1), m=P['coin'], seg=8)
    for sz in (-1, 1):
        box(root, f'{tag}_dobradica{sz}', (r * 0.3, 0.05, r * 0.16), (x - r * 1.05, y - 0.03, zc + sz * r * 0.5), m=P['coin_d'], bev=0.008)
    wp = empty(root, tag + '_volante', loc=(x, y - 0.075, zc), rot=(math.pi / 2, 0, 0))
    kids(wp, torus(root, tag + '_volanteAro', (0, 0, 0), r * 0.42, r * 0.06, P['coin'], n=24, segs=6),
         cyl(root, tag + '_volanteCubo', r * 0.14, 0.03, (0, 0, 0.0), m=P['coin_d'], v=18, bev=0.006))
    for k in range(4):
        a = TAU * k / 4
        kids(wp, tube(root, f'{tag}_volanteRaio{k}', [(0, 0, 0), (r * 0.55 * math.cos(a), r * 0.55 * math.sin(a), 0)], r * 0.045, P['coin'], segs=5),
             sphere(root, f'{tag}_volantePunho{k}', r * 0.07, (r * 0.58 * math.cos(a), r * 0.58 * math.sin(a), 0), m=P['coin'], seg=10))
    if spin_wheel:
        register_anim(wp, spin('Z', sym=4, turns=-1))
    return wp


def column(root, P, tag, x, y, z0, h, r=0.04):
    """Coluna de marmore com base e capitel dourados."""
    cyl(root, tag + '_base', r * 1.45, 0.035, (x, y, z0 + 0.0175), m=P['gold'], v=20, bev=0.008)
    cyl(root, tag, r, h - 0.07, (x, y, z0 + h / 2), r2=r * 0.9, m=P['marble'], v=20, bev=0.006)
    for k in range(6):
        a = TAU * k / 6 + 0.3
        tube(root, f'{tag}_canelura{k}', [(x + r * 1.0 * math.cos(a), y + r * 1.0 * math.sin(a), z0 + 0.05), (x + r * 0.9 * math.cos(a), y + r * 0.9 * math.sin(a), z0 + h - 0.05)],
             0.004, P['marble_d'], segs=4)
    cyl(root, tag + '_capitel', r * 1.5, 0.035, (x, y, z0 + h - 0.0175), r2=r * 1.6, m=P['gold'], v=20, bev=0.008)


def plinth(root, P, tag, cx, cy, w, d, steps=2, h=0.06, z0=G):
    """Base de marmore em degraus (cada degrau um pouco menor)."""
    z = z0
    for k in range(steps):
        ww, dd = w - 0.08 * k, d - 0.08 * k
        slab(root, f'{tag}{k}', ww, dd, h, P['marble_d'] if k == 0 else P['marble'], r=0.04, loc=(cx, cy + 0.02 * k, z + h / 2), rot=(math.pi / 2, 0, 0), bev=0.014)
        z += h
    return z


def bank(root, P, tag, cx, cy, w, d, h, z0, cols=4, roof_h=0.2, door_r=0.16, col_r=0.04, lights=None):
    """Agencia: caixa de marmore, colunata na frente, friso e frontao dourado (telhado de duas aguas, cumeeira de frente
    para tras), medalhao de moeda no frontao e a porta de cofre redonda no meio da fachada. Devolve a cumeeira (x, y, z)."""
    yf = cy - d / 2
    box(root, tag + '_parede', (w - 0.08, d - 0.1, h), (cx, cy + 0.04, z0 + h / 2), m=P['marble'], bev=0.015)
    box(root, tag + '_rodape', (w - 0.06, d - 0.08, 0.04), (cx, cy + 0.04, z0 + 0.02), m=P['marble_d'], bev=0.01)
    # colunas na frente da parede: nas quinas (e em pares, com 4), deixando o meio livre para a porta do cofre
    xc = w / 2 - 0.06
    xs = [cx - xc, cx + xc] if cols == 2 else [cx - xc, cx - xc + 0.115, cx + xc - 0.115, cx + xc]
    for k, x in enumerate(xs):
        column(root, P, f'{tag}_coluna{k}', x, yf + 0.04, z0, h, r=col_r)
    # friso (entablamento) dourado em cima das colunas
    box(root, tag + '_friso', (w + 0.04, d + 0.02, 0.07), (cx, cy, z0 + h + 0.035), m=P['roof'], bev=0.012)
    box(root, tag + '_frisoFaixa', (w + 0.05, 0.012, 0.022), (cx, yf - 0.006, z0 + h + 0.035), m=P['trim'], bev=0.004)
    zr = z0 + h + 0.07
    # telhado: prisma triangular (frente para tras) e o timpano de marmore com o medalhao
    roof = prism_xz(root, tag + '_telhado', [(-w / 2 - 0.05, 0.0), (w / 2 + 0.05, 0.0), (0.0, roof_h)], d + 0.08, P['roof'], bev=0.014)
    roof.location = (cx, cy, zr)
    tim = prism_xz(root, tag + '_timpano', [(-w / 2 + 0.04, 0.025), (w / 2 - 0.04, 0.025), (0.0, roof_h - 0.045)], 0.02, P['marble'], bev=0.006)
    tim.location = (cx, yf - 0.035, zr)
    rm = roof_h * 0.26
    cyl(root, tag + '_medalhao', rm, 0.02, (cx, yf - 0.05, zr + roof_h * 0.38), rot=(math.pi / 2, 0, 0), m=cor('pri', rough=0.35), v=28, bev=0.005)
    torus(root, tag + '_medalhaoAro', (cx, yf - 0.06, zr + roof_h * 0.38), rm * 0.98, 0.005, P['coin_d'], axis='Y', n=22, segs=4)
    # emblema da chapa no medalhao (V losango amarelo e circulo azul, R estrela branca)
    emblema(root, tag + '_medalhaoEmblema', rm * 1.9, rm * 1.9, loc=(cx, yf - 0.064, zr + roof_h * 0.38), depth=0.006)
    # bandeirinha da chapa no beiral esquerdo (abaixo do grafico: nao muda o enquadramento)
    flag_left(root, tag + '_bandeirinha', (cx - w / 2 + 0.03, cy, zr), h=0.3)
    # porta de cofre redonda no meio da fachada
    vault_door(root, P, tag + '_cofre', cx, yf + 0.09, z0 + door_r + 0.06, r=door_r)
    return (cx, cy, zr + roof_h)


# ---------------------------------------------------------------- nivel 1: o quiosque do Vorcash
def build_mk1(P, root):
    plot(root, P, 'mk1')
    lights = []
    zp = plinth(root, P, 'mk1_base', -0.02, 0.12, 0.74, 0.54, steps=1)
    rx, ry, rz = bank(root, P, 'mk1_agencia', -0.02, 0.14, 0.52, 0.38, 0.38, zp, cols=2, roof_h=0.15, door_r=0.11, col_r=0.032)
    top = chart(root, P, 'mk1_grafico', rx, ry + 0.06, rz - 0.05, s=0.95, bars=(0.16, 0.26))
    coin_stack(root, P, 'mk1_pilha1', -0.5, -0.24, 5, seed=1)
    coin_stack(root, P, 'mk1_pilha2', -0.4, -0.36, 3, seed=2)
    loose_coins(root, P, 'mk1_moeda', 0.1, -0.44, n=3, spread=0.08)
    globe_lamp(root, P, 'mk1_poste', 0.36, -0.1, zp, h=0.28, lights=lights)
    return {'slots': [(0.46, -0.48, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (rx, ry - 0.1, rz)}}


# ---------------------------------------------------------------- nivel 2: agencia com duas colunas e barras de ouro
def build_mk2(P, root):
    plot(root, P, 'mk2')
    lights = []
    zp = plinth(root, P, 'mk2_base', 0.06, 0.12, 0.9, 0.62, steps=2, h=0.05)
    rx, ry, rz = bank(root, P, 'mk2_agencia', 0.06, 0.14, 0.7, 0.44, 0.44, zp, cols=4, roof_h=0.18, door_r=0.12, col_r=0.034)
    chart(root, P, 'mk2_grafico', rx, ry + 0.08, rz - 0.07, s=1.1, bars=(0.16, 0.26, 0.36))
    gold_bars(root, P, 'mk2_barra', 0.56, -0.4, rows=(2, 1), rz=0.3, s=0.9)
    coin_stack(root, P, 'mk2_pilha1', -0.3, -0.42, 4, seed=3)
    coin_stack(root, P, 'mk2_pilha2', 0.3, -0.46, 6, seed=4)
    coin_stack(root, P, 'mk2_pilha3', 0.4, -0.36, 3, seed=5)
    loose_coins(root, P, 'mk2_moeda', -0.1, -0.5, n=4, spread=0.08)
    for sx in (-1, 1):
        globe_lamp(root, P, f'mk2_poste{sx}', 0.06 + sx * 0.42, -0.14, zp, h=0.3, lights=lights)
    return {'slots': [(-0.54, -0.4, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (rx, ry - 0.12, rz)}}


# ---------------------------------------------------------------- nivel 3: a agencia completa do conceito
def build_mk3(P, root):
    plot(root, P, 'mk3')
    lights = []
    zp = plinth(root, P, 'mk3_base', 0.04, 0.12, 1.0, 0.66, steps=2, h=0.055)
    rx, ry, rz = bank(root, P, 'mk3_agencia', 0.04, 0.14, 0.8, 0.48, 0.5, zp, cols=4, roof_h=0.22, door_r=0.15, col_r=0.04)
    top = chart(root, P, 'mk3_grafico', rx, ry + 0.08, rz - 0.09, s=1.3, bars=(0.18, 0.3, 0.42))
    spinning_coin(root, P, 'mk3_moedaGira', (-0.64, -0.2, G + 0.19 + 0.07), r=0.06)
    coin_stack(root, P, 'mk3_pilha1', -0.64, -0.2, 10, seed=6)
    coin_stack(root, P, 'mk3_pilha2', -0.66, -0.4, 6, seed=7)
    coin_stack(root, P, 'mk3_pilha3', -0.7, -0.02, 4, seed=8)
    gold_bars(root, P, 'mk3_barra', 0.5, -0.38, rows=(3, 2, 1), rz=0.35, s=0.95)
    coin_stack(root, P, 'mk3_pilha4', 0.66, -0.12, 7, seed=9)
    loose_coins(root, P, 'mk3_moeda', 0.06, -0.52, n=4, spread=0.1)
    for sx in (-1, 1):
        globe_lamp(root, P, f'mk3_poste{sx}', 0.04 + sx * 0.47, -0.16, zp, h=0.32, lights=lights)
    return {'slots': [(-0.44, -0.52, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (rx, ry - 0.12, rz)}}


# ---------------------------------------------------------------- Emenda Pix: o balcao com a maquininha e os
# envelopes voando (os dois atendentes ficam atras do balcao)
def envelope(root, P, tag, loc, rot=(0, 0, 0), s=1.0, parent=None):
    """Envelope pardo fechado com o lacre dourado (voltado para -Y)."""
    with grupo(root, tag, loc=loc, rot=rot, parent=parent) as e:
        slab(root, tag + '_corpo', 0.2 * s, 0.13 * s, 0.022 * s, P['kraft'], r=0.012 * s, bev=0.006 * s)
        prism = prism_xz(root, tag + '_aba', [(-0.096 * s, 0.06 * s), (0.096 * s, 0.06 * s), (0.0, -0.01 * s)], 0.006 * s, mat('envelope_aba', '#b5864c', rough=0.8,
                                                                                                                              var=0.03, bump=0.04), bev=0.002)
        prism.location = (0, -0.013 * s, 0)
        cyl(root, tag + '_lacre', 0.022 * s, 0.008 * s, (0, -0.018 * s, -0.005 * s), rot=(math.pi / 2, 0, 0), m=P['coin'], v=16, bev=0.002)
    return e


def card_machine(root, P, tag, x, y, z, s=1.0, rz=0.0):
    """Maquininha de cartao gigante (sem numeros nas teclas): corpo grafite inclinado, tela acesa, teclado, o cartao
    dourado enfiado em cima e o comprovante saindo."""
    with grupo(root, tag, loc=(x, y, z), rot=(math.radians(-14), 0, rz)):
        slab(root, tag + '_corpo', 0.22 * s, 0.38 * s, 0.07 * s, P['pos'], r=0.05 * s, loc=(0, 0, 0.19 * s), bev=0.022 * s)
        slab(root, tag + '_tela', 0.16 * s, 0.12 * s, 0.01, P['screen'], r=0.015 * s, loc=(0, -0.037 * s, 0.29 * s), bev=0.003)
        sphere(root, tag + '_telaSeta', 0.022 * s, (0, -0.044 * s, 0.29 * s), scale=(1, 0.3, 1), m=P['key'], seg=10)
        cols = [P['key']] * 9 + [mat('tecla_vermelha', '#e05a4a', rough=0.5, var=0, bump=0), mat('tecla_amarela', '#f2c84a', rough=0.5, var=0, bump=0),
                                 mat('tecla_verde', '#4cc46a', rough=0.5, var=0, bump=0)]
        for k in range(12):
            i, j = k % 3, k // 3
            slab(root, f'{tag}_tecla{k}', 0.04 * s, 0.026 * s, 0.014 * s, cols[k], r=0.01 * s, loc=((i - 1) * 0.05 * s, -0.04 * s, (0.18 - j * 0.036) * s), bev=0.004)
        box(root, tag + '_cartao', (0.12 * s, 0.008 * s, 0.08 * s), (0, 0.0, 0.41 * s), m=P['coin'], bev=0.003)
        box(root, tag + '_chip', (0.02 * s, 0.01 * s, 0.016 * s), (-0.03 * s, -0.004 * s, 0.43 * s), m=P['coin_d'], bev=0.001)
        tube(root, tag + '_comprovante', [(0.0, 0.03 * s, 0.38 * s), (0.0, 0.05 * s, 0.44 * s), (0.0, 0.1 * s, 0.47 * s), (0.0, 0.14 * s, 0.44 * s)], 0.004 * s,
             P['cream'], segs=4)
        box(root, tag + '_papel', (0.1 * s, 0.006, 0.12 * s), (0.0, 0.035 * s, 0.44 * s), rot=(-0.4, 0, 0), m=P['cream'], bev=0.002)


def build_mkB(P, root):
    plot(root, P, 'mkB')
    lights = []
    # parede do fundo de marmore com moldura de ouro e a tela com a seta subindo
    box(root, 'mkB_parede', (1.16, 0.12, 0.86), (0.0, 0.42, G + 0.43), m=P['marble'], bev=0.02)
    box(root, 'mkB_paredeFriso', (1.2, 0.15, 0.06), (0.0, 0.42, G + 0.88), m=P['roof'], bev=0.012)
    slab(root, 'mkB_painelMoldura', 0.54, 0.34, 0.02, P['gold'], r=0.04, loc=(0.0, 0.355, G + 0.58), bev=0.006)
    slab(root, 'mkB_painel', 0.48, 0.28, 0.02, P['screen'], r=0.03, loc=(0.0, 0.345, G + 0.58), bev=0.004)
    zigzag_arrow(root, P, 'mkB_painelSeta', [(-0.18, 0.33, G + 0.48), (-0.06, 0.33, G + 0.58), (0.02, 0.33, G + 0.54), (0.14, 0.33, G + 0.66)], r=0.016, head=0.06,
                 m=P['coin'])
    for sx in (-1, 1):
        column(root, P, f'mkB_coluna{sx}', sx * 0.52, 0.34, G, 0.84, r=0.038)
        # flamula da chapa na parede, entre o painel e a coluna (com o emblema)
        box(root, f'mkB_flamula{sx}', (0.13, 0.012, 0.3), (sx * 0.395, 0.354, G + 0.6), m=cor('pri', rough=0.8, sheen=0.4), bev=0.004)
        box(root, f'mkB_flamulaBarra{sx}', (0.15, 0.02, 0.018), (sx * 0.395, 0.35, G + 0.755), m=P['gold'], bev=0.004)
        emblema(root, f'mkB_flamulaEmblema{sx}', 0.12, 0.12, loc=(sx * 0.395, 0.344, G + 0.63), depth=0.005)
    # balcao na frente (camada da frente: cobre as pernas dos atendentes)
    zc = G + 0.34
    box(root, 'mkB_balcao', (1.06, 0.2, 0.32), (0.0, -0.16, G + 0.16), m=P['marble'], bev=0.02, front=True)
    box(root, 'mkB_balcaoTampo', (1.12, 0.26, 0.04), (0.0, -0.17, zc - 0.02), m=P['roof'], bev=0.012, front=True)
    for k in range(4):
        box(root, f'mkB_balcaoPainel{k}', (0.2, 0.012, 0.2), (-0.39 + 0.26 * k, -0.265, G + 0.15), m=P['marble_d'], bev=0.006, front=True)
        box(root, f'mkB_balcaoFriso{k}', (0.21, 0.014, 0.014), (-0.39 + 0.26 * k, -0.27, G + 0.26), m=P['gold'], bev=0.003, front=True)
    card_machine(root, P, 'mkB_maquininha', 0.0, -0.18, zc, s=0.95)
    for o in [o for o in bpy.data.objects if o.name.startswith('mkB_maquininha') and o.type == 'MESH']:
        o['front'] = 1
    coin_stack(root, P, 'mkB_pilhaBalcao', 0.38, -0.18, 4, r=0.045, z0=zc, seed=11)
    for o in [o for o in bpy.data.objects if o.name.startswith('mkB_pilhaBalcao')]:
        o['front'] = 1
    # envelopes voando para fora da maquininha (cada um no seu tempo)
    for k, (x, y, z, rz) in enumerate(((-0.24, -0.22, 0.98, 0.3), (0.26, -0.26, 1.06, -0.4), (-0.5, -0.3, 0.74, 0.6), (0.52, -0.32, 0.8, -0.2),
                                       (0.02, -0.3, 1.24, 0.1))):
        e = envelope(root, P, f'mkB_envelope{k}', (x, y, z), rot=(0.2, 0.25 * (k % 3 - 1), rz), s=1.05)

        def fly(o, mb, ph, p0=0.21 * k, sg=1 if k % 2 else -1):
            a = TAU * (ph + p0)
            o.matrix_basis = Matrix.Translation((0.02 * sg * math.sin(a), 0, 0.035 * math.sin(a))) @ mb @ Matrix.Rotation(0.25 * math.sin(a + 0.7), 4, 'Y')
        register_anim(e, fly)
    gold_bars(root, P, 'mkB_barra', -0.6, -0.46, rows=(2, 1), rz=-0.3, s=0.8)
    coin_stack(root, P, 'mkB_pilha1', 0.6, -0.44, 5, seed=12)
    loose_coins(root, P, 'mkB_moeda', 0.36, -0.56, n=3, spread=0.06)
    globe_lamp(root, P, 'mkB_poste', -0.66, -0.12, G, h=0.4, lights=lights)
    lights.append(((0.0, 0.25, G + 0.58), VC['luz'], 8.0, 1))
    return {'slots': [(-0.26, 0.08, G), (0.27, 0.1, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (0.0, -0.18, zc + 0.42)}}


# ---------------------------------------------------------------- CDB de 140%: o cofre enorme transbordando e a seta
# gigante subindo (com uma rachadura discreta: bom demais para ser verdade)
def build_mkT(P, root):
    plot(root, P, 'mkT')
    lights = []
    cx, cy = -0.04, 0.14
    W, D, H = 0.86, 0.6, 0.56
    z0 = G + 0.05
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(root, f'mkT_pe{sx}{sy}', 0.05, 0.05, (cx + sx * (W / 2 - 0.08), cy + sy * (D / 2 - 0.08), G + 0.025), r2=0.04, m=P['coin_d'], v=14, bev=0.008)
    box(root, 'mkT_cofre', (W, D, H), (cx, cy, z0 + H / 2), m=P['steel_b'], bev=0.04)
    # cantoneiras e cintas de ouro com rebites
    for sx in (-1, 1):
        box(root, f'mkT_cinta{sx}', (0.06, D + 0.02, H + 0.02), (cx + sx * (W / 2 - 0.1), cy, z0 + H / 2), m=P['gold'], bev=0.012)
        for k in range(4):
            sphere(root, f'mkT_rebite{sx}{k}', 0.012, (cx + sx * (W / 2 - 0.1), cy - D / 2 - 0.012, z0 + 0.08 + k * (H - 0.16) / 3), scale=(1, 0.5, 1), m=P['coin'], seg=8)
    box(root, 'mkT_borda', (W + 0.04, D + 0.04, 0.05), (cx, cy, z0 + H - 0.01), m=P['gold'], bev=0.014)
    vault_door(root, P, 'mkT_porta', cx, cy - D / 2 + 0.06, z0 + H * 0.48, r=0.2)
    # rachadura discreta no aco, saindo da quina de cima
    tube(root, 'mkT_rachadura', [(cx + 0.3, cy - D / 2 - 0.004, z0 + H - 0.04), (cx + 0.27, cy - D / 2 - 0.004, z0 + H - 0.1), (cx + 0.3, cy - D / 2 - 0.004, z0 + H - 0.15),
                                 (cx + 0.26, cy - D / 2 - 0.004, z0 + H - 0.22)], 0.005, P['crack'], segs=4)
    # o monte de moedas transbordando por cima (e escorrendo pela frente e pelo lado)
    zt = z0 + H + 0.01
    sphere(root, 'mkT_monte', 1.0, (cx, cy, zt), scale=(W * 0.5, D * 0.5, 0.2), m=P['coin_d'], seg=28)
    rr = random.Random(21)
    for k in range(46):
        a = rr.uniform(0, TAU)
        d = math.sqrt(rr.random())
        u, v = W * 0.47 * d * math.cos(a), D * 0.47 * d * math.sin(a)
        zz = zt + 0.2 * math.sqrt(max(0.0, 1 - d * d)) + 0.008
        nx, ny = -u / (W * 0.5) * 0.6, -v / (D * 0.5) * 0.6
        cyl(root, f'mkT_moedaMonte{k}', 0.05, 0.014, (cx + u, cy + v, zz), rot=(ny * 0.9 + rr.uniform(-0.3, 0.3), -nx * 0.9 + rr.uniform(-0.3, 0.3), 0), m=P['coin'],
            v=22, bev=0.004)
    for k in range(9):
        t = k / 8
        x = cx - W / 2 + 0.06 - 0.12 * t
        y = cy - D / 2 + 0.06 - 0.08 * t
        z = zt - (zt - G - 0.02) * t ** 1.3
        cyl(root, f'mkT_cascata{k}', 0.045, 0.014, (x + 0.02 * math.sin(k), y, z), rot=(1.2 * (k % 2) - 0.6, 0.5, 0.3 * k), m=P['coin'], v=20, bev=0.004)
    coin_stack(root, P, 'mkT_pilha1', -0.6, -0.36, 7, seed=13)
    coin_stack(root, P, 'mkT_pilha2', -0.46, -0.48, 4, seed=14)
    loose_coins(root, P, 'mkT_moedaChao', -0.6, -0.2, n=6, spread=0.12, seed=15)
    gold_bars(root, P, 'mkT_barra', 0.54, -0.36, rows=(3, 2, 1), rz=0.35, s=0.9)
    # moedas pulando do monte (anim)
    for k, (dx, dy, dz) in enumerate(((-0.18, -0.08, 0.3), (0.12, -0.12, 0.34), (0.3, 0.02, 0.24))):
        spinning_coin(root, P, f'mkT_moedaPula{k}', (cx + dx, cy + dy, zt + dz), r=0.055, ph0=0.33 * k)
    # seta gigante subindo atras do cofre, com as barras do grafico e a rachadura no ultimo trecho
    yb = cy + D / 2 - 0.02
    for k, (x, hh) in enumerate(((-0.3, 0.7), (-0.06, 0.95), (0.18, 1.2), (0.42, 1.5))):
        slab(root, f'mkT_barraGrafico{k}', 0.13, hh, 0.06, P['chart'], r=0.02, loc=(x, yb + 0.06, G + hh / 2), bev=0.01)
    with grupo(root, 'mkT_seta', loc=(0, yb - 0.02, 0)) as g:
        top = zigzag_arrow(root, P, 'mkT_zigue', [(-0.5, 0, 0.82), (-0.24, 0, 1.12), (-0.04, 0, 1.0), (0.22, 0, 1.42), (0.42, 0, 1.68)], r=0.045, head=0.17, crack=3)

    def fn(o, mb, ph):
        a = TAU * ph
        o.matrix_basis = Matrix.Translation((0, 0, 0.03 * math.sin(a))) @ mb @ Matrix.Rotation(0.025 * math.sin(a + 1), 4, 'Y')
    register_anim(g, fn)
    lights.append(((cx, cy - D / 2 - 0.1, z0 + H * 0.5), '#ffe0a0', 8.0, 1))
    # bandeirinha da chapa espetada no monte de moedas (abaixo da seta: nao muda o enquadramento)
    flag_left(root, 'mkT_bandeirinha', (cx - 0.28, cy + 0.12, zt + 0.08), h=0.34)
    globe_lamp(root, P, 'mkT_poste', 0.66, -0.06, G, h=0.4, lights=lights)
    return {'slots': [(0.3, -0.52, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (cx, cy, zt + 0.3)}}


# ---------------------------------------------------------------- tripulacao do banco
def coin_bag(root, P, tag):
    """Saco de moedas amarrado (pendurado pela boca na mao: o saco fica embaixo)."""
    sack_m = mat('saco_moedas', '#d8c08a', rough=0.85, var=0.03, bump=0.15)
    return [sphere(root, tag + '_saco', 0.06, (0, 0, 0.085), scale=(1, 1, 1.05), m=sack_m, seg=16),
            cyl(root, tag + '_sacoBoca', 0.034, 0.04, (0, 0, 0.02), r2=0.026, m=sack_m, v=12, bev=0.006),
            torus(root, tag + '_sacoCordao', (0, 0, 0.03), 0.028, 0.006, P['coin_d'], n=12, segs=4)]


def gold_card(root, P, tag):
    return [box(root, tag + '_cartao', (0.006, 0.075, 0.05), (0, 0, 0.03), m=P['coin'], bev=0.003),
            box(root, tag + '_cartaoChip', (0.008, 0.016, 0.012), (0.001, -0.016, 0.034), m=P['coin_d'], bev=0.001)]


def giant_key(root, P, tag):
    """Chave dourada gigante do cofre, segurada em pe como um bastao (ao longo do Z local)."""
    return [tube(root, tag + '_chaveHaste', [(0, 0, -0.3), (0, 0, 0.32)], 0.014, P['gold'], segs=8),
            torus(root, tag + '_chaveArgola', (0, 0, 0.38), 0.05, 0.014, P['gold'], axis='X', n=20, segs=6),
            box(root, tag + '_chaveDente1', (0.012, 0.06, 0.03), (0, 0.03, -0.27), m=P['gold'], bev=0.004),
            box(root, tag + '_chaveDente2', (0.012, 0.045, 0.025), (0, 0.022, -0.21), m=P['gold'], bev=0.004)]


def build_gerente(P, root):
    """Gerente do banco: terno da chapa (V verde com gravata amarela, R vermelho com gravata vinho e estrela branca na
    lapela), cabelo de gel; saco de moedas numa mao e o cartao dourado na outra."""
    tag = root['set']
    s_ = cor('pri', rough=0.72, sheen=0.3)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=mat('cabelo_gel_vorcash', '#1a120c', rough=0.25, var=0.0, bump=0.05), belt=None,
                                         skirt_m=s_, pants=s_, boot_m=shoes(), boot_cuff=s_, sleeve=s_, bracer=s_, bare_hands=True))
    tie(root, pr, tag, cor('sec' if CHAPA == 'V' else 'escuro', rough=0.5))
    broche(root, pr, tag)
    hold(pr, 'L', *coin_bag(root, P, tag))
    hold(pr, 'R', *gold_card(root, P, tag))
    return pr


def build_seguranca(P, root):
    """Seguranca do cofre: terno escuro da chapa (V verde-escuro com gravata amarela, R vinho com gravata vermelha e
    estrela branca), oculos escuros, ponto no ouvido e a chave dourada gigante."""
    tag = root['set']
    s_ = cor('escuro', rough=0.72, sheen=0.3)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=mat('cabelo_raspado', '#2a1d14', rough=0.8, var=0.02, bump=0.3), belt=None,
                                         skirt_m=s_, pants=s_, boot_m=shoes(), boot_cuff=s_, sleeve=s_, bracer=s_, bare_hands=True, big=1.06))
    tie(root, pr, tag, cor('sec' if CHAPA == 'V' else 'pri', rough=0.5))
    broche(root, pr, tag)
    glasses(root, pr, tag, mat('lente_escura_vorcash', '#141418', rough=0.15, var=0, bump=0), dark=True)
    o = tube(root, tag + '_ponto', [HC + Vector((0.0, -0.07, 0.0)), HC + Vector((0.01, -0.075, -0.05)), HC + Vector((-0.02, -0.07, -0.1))], 0.004,
             mat('fio_ponto', '#e8e4dc', rough=0.5, var=0, bump=0), segs=4)
    o.parent = pr['head']
    hold(pr, 'R', *giant_key(root, P, tag))
    return pr


IDLE_N, ACT_N = 12, 8


def gerente_state(mode, f):
    """idle: oferece o cartao dourado com a mao direita; act: ergue o saco de moedas (o rendimento da onda)."""
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
    'towers': [('mk1', 'Banco Vorcash N1', build_mk1), ('mk2', 'Banco Vorcash N2', build_mk2), ('mk3', 'Banco Vorcash N3', build_mk3),
               ('mkB', 'Emenda Pix', build_mkB), ('mkT', 'CDB de 140%', build_mkT)],
    'crews': [crew('mkM', 'Gerente do banco', build_gerente, gerente_state), crew('mkG', 'Seguranca do cofre', build_seguranca, seguranca_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
