"""Lava a Jato (Cisterna, Ninguem Sobe a Rampa): niveis 1 a 3, Forca-Tarefa e Vaza Jato, com o canhao de agua de alta
pressao que mira o alvo. Lava-jato de carros sobre o lote de concreto branco de Brasilia: portico azul de lavagem com
escovas giratorias, espuma branca, o carro oficial preto sendo lavado, poca d'agua (conceito:
arte/conceitos/torres/lava_a_jato.png). Azul de assinatura. A Forca-Tarefa tem arcos de bicos e canhoes de espuma; o
Vaza Jato e um cano estourado, remendado com fita, vazando em alta pressao.
Nomes de conjuntos, postos, pontos e modos sao os mesmos da Roda d'Agua (js/sprites.js depende deles).
Chapa (tools/blender/chapa.py): a estrutura (portico, pilares, cano, arcos, paredes), as escovas, o canhao, a placa/emblema
e a turma seguem a chapa: CHAPA=V verde e amarelo (camisa amarela da selecao, bone/capacete verde), CHAPA=R vermelho com
estrela branca (camiseta vermelha com estrela, bone/capacete vermelho). A agua azul, a espuma, o balde azul, o carro
oficial preto e a placa amarela de piso molhado nao mudam.

  Blender -b -P tools/blender/torre_cisterna.py -- render arte/render/cisterna [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_cisterna.py -- render arte/render_r/cisterna [conjuntos...]
  Blender -b -P tools/blender/torre_cisterna.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_cisterna.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, hazard_mat, hard_hat, work_lamp, concrete, grupo, hide_tree, prism_xz, G   # noqa: F811 - lote de Brasilia
from chapa import CHAPA, cor, emblema, estrela_peito   # cores da chapa (CHAPA=V ou R no ambiente)

FRONT = -math.pi / 2
FAM = 'cisterna'

import lib as _lib
_orig_palette2 = palette2


def palette2():   # noqa: F811 - azul de lava-jato, cromado e espuma branca
    P = _orig_palette2()
    P['blue'] = mat('azul_lavajato', '#3d82d8', rough=0.45, var=0.03, bump=0.04)
    P['blue_d'] = mat('azul_lavajato_escuro', '#2b5fa8', rough=0.5, var=0.03, bump=0.04)
    P['blue_l'] = mat('azul_lavajato_claro', '#a9d2f2', rough=0.35, var=0.02, bump=0.03)
    P['trim'] = mat('friso_cinza', '#dfe4ea', rough=0.35, metal=0.25, var=0.02, bump=0.02)
    P['chrome'] = mat('cromado', '#d9e0e6', rough=0.22, metal=0.75, var=0.02, bump=0.01)
    P['water'] = mat('agua_lavajato', '#5ab4e8', rough=0.06, var=0.02, bump=0.04, emit=0.18)
    P['water_l'] = mat('agua_lavajato_clara', '#c4e8fb', rough=0.05, var=0.0, bump=0.02, emit=0.12)
    next(n for n in P['water_l'].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Alpha'].default_value = 0.72
    P['foam'] = mat('espuma_lavajato', '#f8fbff', rough=0.55, var=0.03, bump=0.35, sheen=0.3)
    P['bubble'] = mat('bolha_sabao', '#e6f4ff', rough=0.08, var=0.0, bump=0.0, emit=0.1)
    next(n for n in P['bubble'].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Alpha'].default_value = 0.55
    # escovas na cor da chapa: V verde com a faixa amarela, R vermelha com a faixa branca
    P['bristle'] = cor('pri', rough=0.9, var=0.05, bump=0.6, sheen=0.5)
    P['bristle_l'] = cor('sec', rough=0.9, var=0.04, bump=0.6, sheen=0.5)
    P['car'] = mat('carro_oficial', '#26282f', rough=0.22, metal=0.35, var=0.02, bump=0.01)
    P['car_glass'] = mat('vidro_carro', '#8ec3e6', rough=0.08, var=0.0, bump=0.0)
    P['tire'] = mat('pneu', '#242427', rough=0.8, var=0.02, bump=0.05)
    P['headlight'] = glow_mat('farol_carro', '#fff2c0', 0.8, 6.0, rough=0.3, var=0.0, bump=0.0)
    P['tape'] = mat('fita_silver', '#d6d9dd', rough=0.45, metal=0.25, var=0.06, bump=0.15)
    P['hose'] = mat('mangueira', '#2d3447', rough=0.7, var=0.02, bump=0.05)
    P['rubber_y'] = mat('galocha_amarela', '#f2c230', rough=0.6, var=0.02, bump=0.04)
    P['dial'] = mat('mostrador', '#f6f4ee', rough=0.4, var=0.0, bump=0.0)
    P['conc'] = concrete()
    P['grate'] = mat('ralo', '#5a5f66', rough=0.6, metal=0.3, var=0.02, bump=0.05, stripes=(40.0, '#6a7078', '#3c4046'))
    # cores da chapa (CHAPA=V verde e amarelo / CHAPA=R vermelho e branco). O azul fica so no que e agua e sabao
    # (agua, bolhas, bombonas de sabao, balde, janelas); a espuma continua branca.
    P['cA'] = cor('pri')       # estrutura: pilares, viga, pedestal, cano, arcos, paredes, corpo do canhao
    P['cB'] = cor('sec')       # detalhe: friso da boca, flanges, bico, tampas
    P['cD'] = cor('escuro')    # paineis e base (o tom escuro da mesma cor, como era o azul escuro)
    P['camisa'], P['calca'], P['bone'], P['gola'] = cor('camisa'), cor('calca'), cor('bone'), cor('gola')
    # o pano de assinatura do lib (bandeirolas, faixas) vira a cor da chapa
    P['teal'] = P['cA']
    P['_emblem'] = 'drop'
    return P


_lib.palette2 = palette2


def placa_chapa(root, name, w, h, loc, rot=(0, 0, 0), plate=True, th=0.014, parent=None):
    """Placa da chapa olhando para -Y (para a camera) antes do giro `rot`: V = bandeira verde com o losango amarelo e o
    circulo azul, R = vermelha com a estrela branca. plate=False poe so o emblema (sobre uma superficie ja na cor)."""
    e = empty(root, name + '_piv', loc=loc, rot=rot, parent=parent)
    if plate:
        kids(e, box(root, name + '_placa', (w, th, h), (0, 0, 0), m=cor('pri', rough=0.6), bev=min(0.006, th * 0.4)))
    for o in emblema(root, name, w * 0.92, h * 0.92, loc=(0, -th / 2 - 0.002 if plate else -0.002, 0)):
        if o.parent == root:
            o.parent = e
    return e
NOZ_FACE = math.radians(-35)


# ---------------------------------------------------------------- agua e espuma
def water_disc(root, P, tag, x, y, z, r, ry=None, ripple=0.006):
    """Poca d'agua com ondinhas (vertices animados) e um brilho que gira."""
    ry = ry or r

    def shape(u, v, co):
        a = TAU * u
        return Vector((r * v * math.cos(a), ry * v * math.sin(a), 0))
    w = cloth_grid(root, tag, 1, 1, 24, 6, [P['water']], shape=shape, thick=0.0)
    w.location = (x, y, z)

    def wave(co, ph):
        d = math.hypot(co.x / r, co.y / ry)
        return Vector((co.x, co.y, ripple * math.sin(TAU * (ph * 2 - d * 2.2)) * (1 - d * 0.6)))
    register_cloth(w, wave)
    hp = empty(root, tag + '_brilhoPivo', loc=(x, y, z + 0.004))
    hl = sphere(root, tag + '_brilho', 1.0, (r * 0.45, 0, 0), scale=(0.18 * r, 0.06 * r, 0.002), m=P['water_l'], seg=10)
    hl.parent = hp
    register_anim(hp, spin('Z', sym=1, turns=1))
    return w


def foam_pile(root, P, tag, x, y, z, r=0.08, n=7, seed=1, flat=0.75):
    """Monte de espuma: bolotas brancas de tamanhos diferentes."""
    rr = random.Random(seed)
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0, r * 0.9) if k else 0.0
        rk = r * rr.uniform(0.45, 0.8) * (1.15 if k == 0 else 1.0)
        sphere(root, f'{tag}_espuma{k}', rk, (x + d * math.cos(a), y + d * math.sin(a), z + rk * flat * 0.7 + (r * 0.3 if k == 0 else 0)),
               scale=(1, 1, flat), m=P['foam'], seg=14)


def bubbles(root, P, tag, x, y, z, n=5, spread=0.25, h=0.35, seed=3):
    """Bolhas de sabao subindo e balancando (pecas animadas)."""
    rr = random.Random(seed)
    for k in range(n):
        p = (x + rr.uniform(-spread, spread), y + rr.uniform(-spread * 0.5, spread * 0.5), z + rr.uniform(0.05, h))
        b = sphere(root, f'{tag}_bolha{k}', rr.uniform(0.014, 0.026), p, m=P['bubble'], seg=10)
        register_anim(b, bob(amp=rr.uniform(0.015, 0.03), turns=1 + k % 2))


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


def foam_arc(root, P, tag, p0, p1, h=0.3, n=10, r0=0.03, r1=0.07, seed=8):
    """Arco largo de espuma: bolotas brancas crescendo ao longo de uma parabola de p0 a p1 (cada uma balanca)."""
    rr = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    for k in range(n):
        t = (k + 0.5) / n
        p = p0.lerp(p1, t) + Vector((rr.uniform(-0.015, 0.015), rr.uniform(-0.015, 0.015), h * math.sin(math.pi * t) * (1 - 0.3 * t)))
        o = sphere(root, f'{tag}_{k}', r0 + (r1 - r0) * t, tuple(p), scale=(1.15, 1.0, 0.85), m=P['foam'], seg=12)
        register_anim(o, bob(amp=0.012, turns=1 + k % 2))


def drops(root, P, tag, p, n=5, spread=0.08, seed=5):
    """Gotinhas espirrando no fim do jato (balancam)."""
    rr = random.Random(seed)
    for k in range(n):
        q = (p[0] + rr.uniform(-spread, spread), p[1] + rr.uniform(-spread, spread), p[2] + rr.uniform(-spread * 0.5, spread))
        o = sphere(root, f'{tag}_gota{k}', rr.uniform(0.012, 0.022), q, scale=(1, 1, 1.3), m=P['water_l'], seg=8)
        register_anim(o, bob(amp=0.02, turns=2, axis='Z'))


# ---------------------------------------------------------------- lava-jato: escovas, portico e o carro
def brush(root, P, tag, loc, h, r, horizontal=False, rot_z=0.0):
    """Escova giratoria de cerdas azuis e claras em faixas (peca animada: gira no proprio eixo).
    Vertical (eixo Z) ou horizontal (eixo X local do grupo); loc = centro da base (vertical) ou do eixo (horizontal)."""
    piv = empty(root, tag + '_escovaPivo', loc=loc, rot=((0, math.pi / 2, rot_z) if horizontal else (0, 0, rot_z)))
    z0 = -h / 2 if horizontal else 0.0
    cuts = [0.0, 0.4, 0.62, 1.0]
    shag = lambda ang, z: 0.13 * math.sin(10 * ang + 14 * z) + 0.06 * math.sin(20 * ang + 30 * z)
    for k in range(3):
        a, b = z0 + h * cuts[k], z0 + h * cuts[k + 1]
        e = (b - a) * 0.12
        prof = [(a, r * 0.86, r * 0.86), (a + e, r, r), ((a + b) / 2, r * 1.03, r * 1.03), (b - e, r, r), (b, r * 0.86, r * 0.86)]
        o = lathe(root, f'{tag}_cerdas{k}', prof, P['bristle_l'] if k == 1 else P['bristle'], segs=30, wobble=shag, lv=1, caps=True)
        kids(piv, o)
    kids(piv, cyl(root, tag + '_eixoEscova', r * 0.18, h + 0.06, (0, 0, z0 + h / 2), m=P['chrome'], v=10, bev=0.004))
    register_anim(piv, spin('Z', sym=10, turns=1))
    return piv


def portal(root, P, tag, w, h, depth=0.24, t=0.13, bt=0.15, y=0.0, z0=G, beacon=True, emblem=True):
    """Portico de lavagem: pilares e viga arredondados na cor da chapa, o emblema da chapa na frente da viga, friso de
    detalhe na boca e o giroflex amarelo no alto."""
    for sx in (-1, 1):
        box(root, f'{tag}_pilar{sx}', (t, depth, h + bt), (sx * (w / 2), y, z0 + (h + bt) / 2), m=P['cA'], bev=0.045)
        box(root, f'{tag}_pilarPainel{sx}', (t * 0.7, depth * 0.08, h * 0.7), (sx * (w / 2), y - depth / 2 - 0.004, z0 + h * 0.45), m=P['cD'], bev=0.012)
    box(root, tag + '_viga', (w + t, depth, bt), (0, y, z0 + h + bt / 2), m=P['cA'], bev=0.045)
    if emblem:
        # emblema pintado na frente da viga (V: verde com losango amarelo e circulo azul = bandeira; R: estrela branca)
        placa_chapa(root, tag + '_vigaEmblema', min(0.32, w * 0.32), bt * 0.86, (0, y - depth / 2 - 0.002, z0 + h + bt / 2), plate=False)
    # friso contornando a boca do portico (frente)
    ins = w / 2 - t / 2 - 0.012
    pts = [(-ins, y - depth / 2 - 0.006, z0 + 0.02), (-ins, y - depth / 2 - 0.006, z0 + h - 0.012), (ins, y - depth / 2 - 0.006, z0 + h - 0.012),
           (ins, y - depth / 2 - 0.006, z0 + 0.02)]
    tube(root, tag + '_friso', pts, 0.018, P['cB'], segs=8)
    for sx in (-1, 1):
        box(root, f'{tag}_sapata{sx}', (t + 0.04, depth + 0.04, 0.03), (sx * (w / 2), y, z0 + 0.015), m=P['trim'], bev=0.01)
    if beacon:
        cyl(root, tag + '_giroflexBase', 0.035, 0.02, (w * 0.3, y, z0 + h + bt + 0.01), m=P['iron_d'], v=14, bev=0.004)
        sphere(root, tag + '_giroflex', 0.032, (w * 0.3, y, z0 + h + bt + 0.03), scale=(1, 1, 0.9), m=P['glow'], seg=12)
    return z0 + h + bt


def car(root, P, tag, loc, rot=0.0, s=1.0, foam=True):
    """Carro oficial preto (sedan arredondado) com a frente para -Y local, farois acesos e espuma no teto e no capo."""
    with grupo(root, tag + '_carro', loc=loc, rot=(0, 0, rot)) as e:
        box(root, tag + '_lataria', (0.34 * s, 0.68 * s, 0.13 * s), (0, 0, 0.115 * s), m=P['car'], bev=0.055 * s)
        box(root, tag + '_cabine', (0.3 * s, 0.34 * s, 0.11 * s), (0, 0.04 * s, 0.225 * s), m=P['car'], bev=0.05 * s)
        box(root, tag + '_vidros', (0.312 * s, 0.3 * s, 0.075 * s), (0, 0.04 * s, 0.22 * s), m=P['car_glass'], bev=0.03 * s)
        box(root, tag + '_parabrisa', (0.27 * s, 0.02 * s, 0.07 * s), (0, -0.13 * s, 0.215 * s), rot=(0.55, 0, 0), m=P['car_glass'], bev=0.01 * s)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl(root, f'{tag}_pneu{sx}{sy}', 0.07 * s, 0.06 * s, (sx * 0.16 * s, sy * 0.21 * s, 0.07 * s), rot=(0, math.pi / 2, 0),
                    m=P['tire'], v=18, bev=0.02 * s)
                cyl(root, f'{tag}_calota{sx}{sy}', 0.036 * s, 0.065 * s, (sx * 0.162 * s, sy * 0.21 * s, 0.07 * s), rot=(0, math.pi / 2, 0),
                    m=P['chrome'], v=14, bev=0.006 * s)
            sphere(root, f'{tag}_farol{sx}', 0.03 * s, (sx * 0.11 * s, -0.335 * s, 0.13 * s), scale=(1.2, 0.6, 0.8), m=P['headlight'], seg=12)
            sphere(root, f'{tag}_lanterna{sx}', 0.024 * s, (sx * 0.12 * s, 0.338 * s, 0.13 * s), scale=(1.2, 0.6, 0.7), m=P['red'], seg=10)
        box(root, tag + '_grade', (0.14 * s, 0.02 * s, 0.04 * s), (0, -0.338 * s, 0.11 * s), m=P['chrome'], bev=0.008 * s)
        for k, yy in enumerate((-0.35, 0.35)):
            box(root, f'{tag}_parachoque{k}', (0.33 * s, 0.03 * s, 0.035 * s), (0, yy * s, 0.07 * s), m=P['chrome'], bev=0.012 * s)
        if foam:
            foam_pile(root, P, tag + '_teto', 0.0, 0.06 * s, 0.27 * s, r=0.09 * s, n=6, seed=2)
            foam_pile(root, P, tag + '_capo', 0.04 * s, -0.2 * s, 0.17 * s, r=0.06 * s, n=4, seed=4)
            foam_pile(root, P, tag + '_portaMala', -0.05 * s, 0.26 * s, 0.17 * s, r=0.05 * s, n=3, seed=6)
    return e


def L2W(c, a, p):
    """Ponto do grupo (centro c, giro a em Z) para as coordenadas da torre."""
    x, y, z = p
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a), z)


def wash_bay(root, P, tag, c, a, w=0.92, h=0.7, depth=0.24, br=0.085, car_s=0.95, top_brush=False, extra_brushes=0, beacon=True,
             emblem=True):
    """Box de lavagem completo (no grupo girado): ralo, poca, portico, escovas, carro e espuma. Devolve o topo do portico."""
    with grupo(root, tag + '_box', loc=(c[0], c[1], 0), rot=(0, 0, a)):
        box(root, tag + '_ralo', (0.12, 0.86, 0.008), (0, -0.04, G + 0.004), m=P['grate'], bev=0.0)
        water_disc(root, P, tag + '_poca', 0.0, -0.12, G + 0.006, 0.42 * w / 0.92, ry=0.6 * w / 0.92, ripple=0.004)
        top = portal(root, P, tag + '_portico', w, h, depth=depth, y=0.06, beacon=beacon, emblem=emblem)
        bx = w / 2 - 0.13 / 2 - br - 0.03
        ys = [0.02] + [0.02 + 0.2 * (k + 1) for k in range(extra_brushes)]
        for j, yy in enumerate(ys):
            for sx in (-1, 1):
                brush(root, P, f'{tag}_escova{j}{sx}', (sx * bx, yy, G + 0.03), h - 0.12, br)
                tube(root, f'{tag}_bracoEscova{j}{sx}', [(sx * bx, yy, G + h - 0.1), (sx * bx, yy, G + h - 0.04), (sx * (bx + 0.06), 0.06, G + h)],
                     0.016, P['chrome'], segs=8)
                foam_pile(root, P, f'{tag}_pe{j}{sx}', sx * bx, yy - 0.04, G, r=0.09, n=6, seed=3 + j * 2 + sx)
        if top_brush:
            brush(root, P, tag + '_escovaTopo', (0, 0.06, G + h - 0.12), 2 * bx - 0.2, 0.075, horizontal=True)
            for sx in (-1, 1):
                tube(root, f'{tag}_bracoTopo{sx}', [(sx * (bx - 0.08), 0.06, G + h - 0.12), (sx * (bx - 0.08), 0.06, G + h)], 0.014, P['chrome'], segs=6)
        car(root, P, tag, (0, -0.1, G), s=car_s)
        foam_pile(root, P, tag + '_frente', -0.14, -0.5, G, r=0.08, n=5, seed=9)
        foam_pile(root, P, tag + '_lado', 0.2, -0.42, G, r=0.06, n=4, seed=11)
        bubbles(root, P, tag + '_bolhas', 0.0, -0.05, G + 0.25, n=6, spread=0.3, h=0.45)
    return top


def pedestal(root, P, tag, x, y, h, w=0.18, reel=True):
    """Pedestal do canhao na cor da chapa (com o carretel de mangueira do lado); devolve o topo."""
    box(root, tag, (w, w, h), (x, y, G + h / 2), m=P['cA'], bev=0.04)
    box(root, tag + '_painel', (w * 0.6, 0.012, h * 0.4), (x, y - w / 2 - 0.004, G + h * 0.55), m=P['cB'], bev=0.006)
    cyl(root, tag + '_tampo', w * 0.55, 0.025, (x, y, G + h + 0.012), m=P['chrome'], v=20, bev=0.006)
    if reel:
        for k in range(3):
            torus(root, f'{tag}_mangueira{k}', (x + w / 2 + 0.02 + 0.014 * k, y, G + h * 0.5), 0.07 - 0.004 * k, 0.014, P['hose'], axis='X', n=20, segs=6)
        cyl(root, tag + '_carretel', 0.03, 0.06, (x + w / 2 + 0.03, y, G + h * 0.5), rot=(0, math.pi / 2, 0), m=P['chrome'], v=12, bev=0.004)
    return G + h + 0.025


def soap_tank(root, P, tag, x, y, h=0.3, r=0.1, m=None):
    """Bombona de sabao (azul ou branca) com tampa e alca na cor da chapa."""
    cyl(root, tag, r, h, (x, y, G + h / 2), m=m or P['blue_l'], v=22, bev=0.03)
    cyl(root, tag + '_tampa', r * 0.35, 0.04, (x, y, G + h + 0.015), m=P['cA'], v=12, bev=0.006)
    torus(root, tag + '_alca', (x, y, G + h + 0.01), r * 0.6, 0.012, P['cA'], axis='Y', n=14, segs=5)


# ---------------------------------------------------------------- canhao de agua de alta pressao (conjunto separado: espelha e recua)
def build_nozzle(P, root, size=1.0, big=0):
    """Pistola de lava-jato num pe giratorio: corpo na cor da chapa com manometro, lanca cromada, bico e a mangueira;
    aponta +X."""
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
        # manometro no lado do corpo (de frente para a camera)
        cyl(root, tag + '_manometro', 0.026 * s, 0.014 * s, (-0.02 * s, -0.042 * s, 0.035 * s), rot=(math.pi / 2, 0, 0), m=P['dial'], v=16, bev=0.003 * s)
        torus(root, tag + '_manometroAro', (-0.02 * s, -0.049 * s, 0.035 * s), 0.026 * s, 0.005 * s, P['chrome'], axis='Y', n=16, segs=5)
        tube(root, tag + '_ponteiro', [(-0.02 * s, -0.051 * s, 0.035 * s), (-0.004 * s, -0.051 * s, 0.045 * s)], 0.003 * s, P['red'], segs=4)
    # mangueira saindo de tras do corpo e descendo ate o pe
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


# ---------------------------------------------------------------- nivel 1: box de lavagem com duas escovas
def build_cs1(P, root):
    plot(root, P, 'cs1')
    lights = []
    c, a = (-0.12, 0.14), math.radians(-25)
    top = wash_bay(root, P, 'cs1', c, a, w=0.92, h=0.66, br=0.08, car_s=0.92)
    lights.append((L2W(c, a, (0.92 * 0.3, 0.06, top + 0.04)), '#ffc04a', 10.0, 1))
    zt = pedestal(root, P, 'cs1_pedestal', 0.5, -0.38, 0.3)
    soap_tank(root, P, 'cs1_sabao', 0.58, 0.36, h=0.26, r=0.09)
    soap_tank(root, P, 'cs1_sabao2', 0.68, 0.16, h=0.2, r=0.07, m=P['foam'])
    tube(root, 'cs1_mangueiraSabao', [(0.58, 0.36, G + 0.28), (0.5, 0.42, G + 0.4), (0.3, 0.36, G + 0.5)], 0.012, P['hose'], segs=6)
    slot = (0.5, -0.38, zt)
    return {'slots': [slot, (-0.52, -0.5, G)], 'lights': lights, 'points': {'top': top_of(slot, size=0.85)}}


# ---------------------------------------------------------------- nivel 2: portico grande com tres escovas e o canhao no teto
def build_cs2(P, root):
    plot(root, P, 'cs2')
    lights = []
    c, a = (-0.04, 0.12), math.radians(-20)
    w, h = 1.08, 0.74
    top = wash_bay(root, P, 'cs2', c, a, w=w, h=h, depth=0.28, br=0.085, car_s=1.0, top_brush=True)
    # plataforma do canhao em cima da viga (lado direito, na frente)
    sl = L2W(c, a, (w * 0.27, -0.02, top))
    cyl(root, 'cs2_plataforma', 0.12, 0.03, (sl[0], sl[1], top + 0.015), m=P['chrome'], v=20, bev=0.008)
    rail_pts = [L2W(c, a, (w * 0.27 + 0.13 * math.cos(t), -0.02 + 0.13 * math.sin(t), top)) for t in [math.radians(x) for x in range(20, 181, 32)]]
    tube(root, 'cs2_guarda', [(p[0], p[1], top + 0.1) for p in rail_pts], 0.01, P['trim'], segs=6)
    for k, p in enumerate(rail_pts):
        tube(root, f'cs2_guardaPoste{k}', [(p[0], p[1], top), (p[0], p[1], top + 0.1)], 0.009, P['trim'], segs=5)
    lights.append((L2W(c, a, (w * 0.3, 0.06, top + 0.04)), '#ffc04a', 10.0, 1))
    soap_tank(root, P, 'cs2_sabao', -0.66, 0.3, h=0.32, r=0.1)
    soap_tank(root, P, 'cs2_sabao2', -0.62, 0.06, h=0.24, r=0.08, m=P['foam'])
    soap_tank(root, P, 'cs2_sabao3', 0.66, 0.38, h=0.22, r=0.075)
    tube(root, 'cs2_mangueiraSabao', [(-0.66, 0.3, G + 0.34), (-0.6, 0.36, G + 0.6), (-0.44, 0.3, G + 0.74)], 0.012, P['hose'], segs=6)
    foam_pile(root, P, 'cs2_espumaChao', 0.5, -0.48, G, r=0.09, n=6, seed=21)
    slot = (sl[0], sl[1], top + 0.03)
    return {'slots': [slot], 'lights': lights, 'points': {'top': top_of(slot, size=1.0, big=1)}, 'margin': (0.2, 0.95, 0.2, 0.3)}


# ---------------------------------------------------------------- nivel 3: tunel de lavagem com a abobada de concreto (Brasilia)
def vault(root, name, R, Rz, y0, y1, z, m, thick=0.04, n=20):
    """Casca de concreto em abobada (meio cilindro achatado) ao longo de Y, apoiada em z."""
    bm = bmesh.new()
    rows = []
    for yy in (y0, y1):
        rows.append([bm.verts.new((R * math.cos(math.pi * k / n), yy, z + Rz * math.sin(math.pi * k / n))) for k in range(n + 1)])
    for k in range(n):
        bm.faces.new((rows[0][k], rows[0][k + 1], rows[1][k + 1], rows[1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, name, root, [m], angle=60)
    sm = o.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = thick
    sm.offset = 0
    bv = o.modifiers.new('Bevel', 'BEVEL')
    bv.width = 0.012
    bv.segments = 2
    return o


def build_cs3(P, root):
    plot(root, P, 'cs3')
    lights = []
    c, a = (0.0, 0.1), math.radians(-18)
    w, h = 1.0, 0.7
    with grupo(root, 'cs3_tunel', loc=(c[0], c[1], 0), rot=(0, 0, a)):
        # paredes laterais na cor da chapa com a faixa de janelas, e a abobada de concreto por cima
        for sx in (-1, 1):
            box(root, f'cs3_parede{sx}', (0.1, 0.62, h), (sx * w / 2, 0.24, G + h / 2), m=P['cA'], bev=0.035)
            box(root, f'cs3_janelas{sx}', (0.104, 0.44, 0.1), (sx * w / 2, 0.26, G + h * 0.7), m=P['blue_l'], bev=0.012)
        vault(root, 'cs3_abobada', w / 2 + 0.1, 0.32, -0.12, 0.6, G + h, P['conc'], thick=0.05)
        box(root, 'cs3_frisoAbobada', (w + 0.24, 0.05, 0.04), (0, -0.12, G + h - 0.01), m=P['cB'], bev=0.01)
        # placa da chapa na boca do tunel, debaixo da abobada
        placa_chapa(root, 'cs3_placa', 0.26, 0.16, (0.0, -0.15, G + h + 0.15), th=0.018)
    top = wash_bay(root, P, 'cs3', (c[0] + 0.0, c[1] - 0.0), a, w=w - 0.04, h=h - 0.02, depth=0.2, br=0.085, car_s=1.02, top_brush=True,
                   extra_brushes=1, beacon=False, emblem=False)
    zt = G + h + 0.32
    sl = L2W(c, a, (0.0, -0.02, zt))
    cyl(root, 'cs3_plataforma', 0.13, 0.04, (sl[0], sl[1], zt + 0.0), m=P['chrome'], v=20, bev=0.01)
    cyl(root, 'cs3_plataformaPe', 0.06, 0.08, (sl[0], sl[1], zt - 0.04), m=P['trim'], v=16, bev=0.008)
    for sx in (-1, 1):
        p = L2W(c, a, (sx * 0.34, 0.5, zt - 0.08))
        sphere(root, f'cs3_giroflex{sx}', 0.03, p, scale=(1, 1, 0.9), m=P['glow'], seg=12)
    lights.append((L2W(c, a, (0.0, 0.5, zt)), '#ffc04a', 12.0, 1))
    soap_tank(root, P, 'cs3_sabao', -0.7, 0.2, h=0.3, r=0.09)
    soap_tank(root, P, 'cs3_sabao2', 0.7, 0.24, h=0.26, r=0.085, m=P['foam'])
    foam_pile(root, P, 'cs3_espumaChao', 0.52, -0.5, G, r=0.1, n=6, seed=31)
    foam_pile(root, P, 'cs3_espumaChao2', -0.56, -0.42, G, r=0.08, n=5, seed=33)
    slot = (sl[0], sl[1], zt + 0.02)
    return {'slots': [slot], 'lights': lights, 'points': {'top': top_of(slot, size=1.1, big=2)}}


# ---------------------------------------------------------------- Forca-Tarefa: arcos de bicos e canhoes de espuma
def build_csF(P, root):
    plot(root, P, 'csF')
    lights = []
    c, a = (0.02, 0.16), math.radians(-15)
    with grupo(root, 'csF_lavagem', loc=(c[0], c[1], 0), rot=(0, 0, a)):
        box(root, 'csF_ralo', (0.14, 0.9, 0.008), (0, 0.08, G + 0.004), m=P['grate'], bev=0.0)
        water_disc(root, P, 'csF_poca', 0.0, 0.06, G + 0.006, 0.5, ry=0.62, ripple=0.005)
        # tres arcos de cano azul com bicos cromados; cada bico solta um leque de agua para o carro
        for j, yy in enumerate((-0.18, 0.12, 0.42)):
            R, H = 0.5, 0.8
            pts = [(-R, yy, G)] + [(-R * math.cos(math.pi * k / 12), yy, G + 0.45 + (H - 0.45) * math.sin(math.pi * k / 12) * 1.0) for k in range(13)] + [(R, yy, G)]
            tube(root, f'csF_arco{j}', pts, 0.035, P['cA'], segs=10)
            for sx in (-1, 1):
                box(root, f'csF_arcoPe{j}{sx}', (0.1, 0.1, 0.04), (sx * R, yy, G + 0.02), m=P['trim'], bev=0.01)
            for k in (2, 6, 10):
                t = math.pi * k / 12
                p = Vector((-R * math.cos(t), yy, G + 0.45 + (H - 0.45) * math.sin(t)))
                inward = Vector((math.cos(t) * 0.9, 0, -0.4 - 0.6 * math.sin(t))).normalized()
                q = p + inward * 0.05
                cyl(root, f'csF_bico{j}_{k}', 0.018, 0.04, tuple(q), m=P['chrome'], v=10, bev=0.004,
                    rot=inward.to_track_quat('Z', 'Y').to_euler())
                end = p + inward * (0.3 if k == 6 else 0.26)
                spray(root, P, f'csF_leque{j}_{k}', tuple(q), (end.x, end.y, max(G + 0.3, end.z)), w0=0.02, w1=0.16, arc=0.02, waves=2 + (k % 3), nv=6)
        # placa da chapa em pe no alto do arco da frente
        placa_chapa(root, 'csF_placa', 0.24, 0.14, (0.0, -0.18, G + 0.835 + 0.072), th=0.016)
        car(root, P, 'csF', (0, 0.1, G), s=1.0)
        for k, (x, y) in enumerate(((-0.34, -0.32), (0.34, -0.3), (-0.36, 0.6), (0.34, 0.62))):
            foam_pile(root, P, f'csF_espuma{k}', x, y, G, r=0.1, n=6, seed=40 + k)
        bubbles(root, P, 'csF_bolhas', 0.0, 0.1, G + 0.3, n=8, spread=0.4, h=0.55)
    # canhoes de espuma nos postes da frente: arcos largos de espuma cruzando por cima do carro
    for sx in (-1, 1):
        px, py = sx * 0.66, -0.3
        tube(root, f'csF_poste{sx}', [(px, py, G), (px, py, G + 0.5)], 0.03, P['trim'], segs=8)
        cyl(root, f'csF_canhaoEspuma{sx}', 0.05, 0.14, (px - sx * 0.03, py, G + 0.54), rot=(0, -sx * 0.9, 0), m=P['cA'], v=16, bev=0.015)
        foam_arc(root, P, f'csF_arcoEspuma{sx}', (px - sx * 0.1, py + 0.01, G + 0.6), (sx * 0.06, 0.12, G + 0.42), h=0.36, n=11, r0=0.03, r1=0.075)
    zt = pedestal(root, P, 'csF_pedestal', 0.0, -0.6, 0.3, w=0.2)
    lights.append(((0.0, -0.66, G + 0.2), '#ffc04a', 8.0, 0))
    lights.append(((0.0, 0.5, G + 0.85), '#ffc04a', 10.0, 1))
    sphere(root, 'csF_giroflex', 0.032, L2W(c, a, (0.0, 0.42, G + 0.86)), scale=(1, 1, 0.9), m=P['glow'], seg=12)
    slot = (0.0, -0.6, zt)
    return {'slots': [slot], 'lights': lights, 'points': {'top': top_of(slot, size=1.1, big=2)}}


# ---------------------------------------------------------------- Vaza Jato: cano estourado remendado com fita
def tape_wrap(root, P, tag, center, r, axis_vec, n=3, w=0.035, seed=1):
    """Voltas de fita silver em volta do cano (aneis meio tortos) e uma tira em X por cima."""
    rr = random.Random(seed)
    c = Vector(center)
    ax = Vector(axis_vec).normalized()
    q = ax.to_track_quat('Z', 'Y')
    for k in range(n):
        o = torus(root, f'{tag}_volta{k}', (0, 0, 0), r * 1.03, w * 0.5, P['tape'], n=24, segs=4)
        o.scale = (1.0, 1.0, 0.45)
        o.location = c + ax * ((k - (n - 1) / 2) * w * 0.8)
        o.rotation_euler = (q.to_matrix() @ Matrix.Rotation(rr.uniform(-0.15, 0.15), 3, 'X')).to_euler()
    side = ax.cross(Vector((0, -1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0))).normalized()
    for sg in (-1, 1):
        a = c - ax * (w * 1.4) + side * (r * 0.45 * sg) + ax.cross(side) * (-r * 0.95)
        b = c + ax * (w * 1.4) - side * (r * 0.45 * sg) + ax.cross(side) * (-r * 0.95)
        tube(root, f'{tag}_tiraX{sg}', [tuple(a), tuple(b)], w * 0.32, P['tape'], segs=4)


def build_csG(P, root):
    plot(root, P, 'csG')
    lights = []
    R = 0.15
    cx, cy = 0.0, 0.08
    zt = G + 1.0
    # cano mestre: sai do concreto quebrado atras, faz o cotovelo e sobe ate o canhao
    tube(root, 'csG_canoChao', [(-0.72, 0.5, G), (-0.4, 0.34, G + 0.02), (-0.12, 0.16, G + 0.1), (cx, cy, G + 0.3), (cx, cy, G + 0.5)], R * 0.85,
         P['cA'], segs=18)
    for k, (x, y) in enumerate(((-0.74, 0.42), (-0.66, 0.6), (-0.82, 0.52), (-0.58, 0.48))):
        box(root, f'csG_caco{k}', (0.1, 0.08, 0.04), (x, y, G + 0.01), rot=(0.2 * (k - 1.5), 0.15 * k, 0.6 * k), m=P['conc'], bev=0.015)
    cyl(root, 'csG_riser', R, zt - G - 0.42, (cx, cy, (zt + G + 0.42) / 2), m=P['cA'], v=28, bev=0.02)
    for k, zz in enumerate((G + 0.5, G + 0.72, zt - 0.06)):
        cyl(root, f'csG_flange{k}', R * 1.25, 0.045, (cx, cy, zz), m=P['cB'], v=28, bev=0.01)
        for j in range(8):
            aj = TAU * j / 8
            sphere(root, f'csG_parafuso{k}_{j}', 0.014, (cx + R * 1.17 * math.cos(aj), cy + R * 1.17 * math.sin(aj), zz + 0.024), m=P['chrome'], seg=8)
    cyl(root, 'csG_topo', R * 1.1, 0.04, (cx, cy, zt - 0.02), m=P['chrome'], v=28, bev=0.01)
    # emblema da chapa pintado no cano, entre as flanges de cima (de frente para a camera)
    placa_chapa(root, 'csG_emblema', 0.17, 0.15, (cx, cy - R - 0.004, G + 0.83), plate=False)
    # o estouro na frente do cano, remendado com fita, com o jato vazando em alta pressao (e as gotas)
    zb = G + 0.6
    tape_wrap(root, P, 'csG_fitaA', (cx, cy, zb + 0.1), R, (0, 0, 1), n=4, w=0.045, seed=2)
    tape_wrap(root, P, 'csG_fitaB', (cx, cy, zb - 0.11), R, (0, 0, 1), n=3, w=0.045, seed=4)
    a_b = math.radians(-60)
    hole = (cx + R * math.cos(a_b), cy + R * math.sin(a_b), zb)
    sphere(root, 'csG_rasgo', 0.04, hole, scale=(0.6, 0.6, 1.2), m=P['iron_d'], seg=10)
    spray(root, P, 'csG_vazamento', hole, (cx + 0.66, cy - 0.5, G + 0.62), w0=0.04, w1=0.3, arc=0.3, waves=4, nv=14)
    spray(root, P, 'csG_vazamento2', hole, (cx + 0.56, cy - 0.62, G + 0.5), w0=0.03, w1=0.2, arc=0.2, waves=3, nv=12, m=P['water'])
    drops(root, P, 'csG_gotas', (cx + 0.62, cy - 0.5, G + 0.6), n=8, spread=0.14, seed=13)
    foam_arc(root, P, 'csG_espumaJato', hole, (cx + 0.6, cy - 0.52, G + 0.55), h=0.3, n=7, r0=0.018, r1=0.04)
    water_disc(root, P, 'csG_poca', 0.42, -0.4, G + 0.006, 0.3, ry=0.22, ripple=0.006)
    foam_pile(root, P, 'csG_espuma', 0.54, -0.46, G, r=0.07, n=5, seed=17)
    # segundo vazamento no cano do chao: esguicho para cima (o ponto 'steam'), com fita
    gx, gy = -0.4, 0.34
    tape_wrap(root, P, 'csG_fitaC', (-0.344, 0.304, G + 0.036), R * 0.85, (0.28, -0.18, 0.08), n=2, seed=6)
    jet = cloth_grid(root, 'csG_esguicho', 1, 1, 3, 12, [P['water_l']], thick=0.012,
                     shape=lambda u, v, co: Vector((gx - 0.04 + (u - 0.5) * (0.04 + 0.12 * (1 - v)), gy - 0.06, G + 0.16 + 0.56 * (1 - v))))
    register_cloth(jet, lambda co, ph: Vector((co.x + 0.02 * math.sin(TAU * (ph * 2 + co.z * 3)), co.y, co.z)))
    drops(root, P, 'csG_gotasTopo', (gx - 0.04, gy - 0.06, G + 0.66), n=5, spread=0.08, seed=19)
    # manometro (no vermelho) e o registro com volante
    tube(root, 'csG_ramal', [(cx - R, cy, G + 0.85), (cx - R - 0.12, cy, G + 0.85)], 0.025, P['cD'], segs=8)
    cyl(root, 'csG_manometro', 0.07, 0.03, (cx - R - 0.14, cy - 0.01, G + 0.85), rot=(math.pi / 2, 0, 0), m=P['dial'], v=24, bev=0.006)
    torus(root, 'csG_manometroAro', (cx - R - 0.14, cy - 0.027, G + 0.85), 0.07, 0.012, P['chrome'], axis='Y', n=24, segs=6)
    box(root, 'csG_faixaVermelha', (0.04, 0.004, 0.02), (cx - R - 0.1, cy - 0.03, G + 0.88), rot=(0, -0.7, 0), m=P['red'], bev=0.0)
    tube(root, 'csG_ponteiro', [(cx - R - 0.14, cy - 0.033, G + 0.85), (cx - R - 0.09, cy - 0.033, G + 0.885)], 0.006, P['red'], segs=4)
    vx, vy = cx + R * 0.7, cy - R * 0.7
    tube(root, 'csG_registroCano', [(vx, vy, G + 0.36), (vx + 0.06, vy - 0.12, G + 0.36)], 0.03, P['cD'], segs=8)
    torus(root, 'csG_volante', (vx + 0.065, vy - 0.13, G + 0.36), 0.075, 0.014, P['red'], axis='Y', n=20, segs=6)
    for k in range(3):
        aa = TAU * k / 3
        tube(root, f'csG_volanteRaio{k}', [(vx + 0.065, vy - 0.13, G + 0.36), (vx + 0.065 + 0.07 * math.cos(aa), vy - 0.13, G + 0.36 + 0.07 * math.sin(aa))],
             0.008, P['red'], segs=4)
    # rolo de fita e o balde no chao, perto do encanador; e a placa amarela de piso molhado (sem letras)
    torus(root, 'csG_roloFita', (-0.28, -0.56, G + 0.02), 0.05, 0.022, P['tape'], n=18, segs=6)
    box(root, 'csG_placaA', (0.12, 0.012, 0.2), (0.62, 0.1, G + 0.1), rot=(0.25, 0, 0.3), m=P['rubber_y'], bev=0.01)
    box(root, 'csG_placaB', (0.12, 0.012, 0.2), (0.6, 0.16, G + 0.1), rot=(-0.25, 0, 0.3), m=P['rubber_y'], bev=0.01)
    work_lamp(root, P, 'csG_refletor', (-0.62, -0.1, G + 0.5), face=-0.6)
    tube(root, 'csG_posteRefletor', [(-0.66, -0.06, G), (-0.66, -0.06, G + 0.5)], 0.016, P['iron_d'], segs=6)
    lights.append(((-0.6, -0.14, G + 0.48), '#ffcf7a', 12.0, 1))
    slot = (cx, cy, zt + 0.0)
    return {'slots': [slot, (-0.46, -0.52, G)], 'lights': lights,
            'points': {'top': top_of(slot, size=1.15, big=2), 'steam': (gx - 0.04, gy - 0.06, G + 0.68)}}


# ---------------------------------------------------------------- equipe do lava-jato
def bucket(root, tag, P):
    """Balde azul de espuma (empunhadura na alca, em z = 0)."""
    objs = [lathe(root, tag + '_balde', [(-0.13, 0.055, 0.055), (-0.06, 0.065, 0.065), (-0.02, 0.07, 0.07)], P['blue'], segs=18, lv=1, caps=False, solid=0.008),
            cyl(root, tag + '_baldeFundo', 0.055, 0.008, (0, 0, -0.13), m=P['blue'], v=16, bev=0.0),
            torus(root, tag + '_alca', (0, 0, -0.02), 0.068, 0.005, P['chrome'], axis='X', n=16, segs=4)]
    rr = random.Random(4)
    for k in range(4):
        a = TAU * k / 4
        objs.append(sphere(root, f'{tag}_espumaBalde{k}', 0.032, (0.03 * math.cos(a), 0.03 * math.sin(a), -0.01), scale=(1, 1, 0.75), m=P['foam'], seg=10))
    return objs


def peito_chapa(root, pr, tag, P):
    """Detalhe da camisa da chapa (R: estrela branca no peito; V: gola verde redonda com o decote em V da camisa da
    selecao). A gola em V e local (a do chapa.estrela_peito fica pequena e de ponta-cabeca neste boneco)."""
    if CHAPA == 'R':
        return estrela_peito(root, tag, pr['body'], (0.084, 0, 0.395), r=0.03, rot=(0, 0, math.pi / 2))
    gm = P['gola']
    out = [tube(root, tag + '_golaV', [(0.05, -0.038, 0.468), (0.085, 0.0, 0.415), (0.05, 0.038, 0.468)], 0.009, gm, segs=6)]
    ring = torus(root, tag + '_golaAnel', (0, 0, 0.474), 0.06, 0.009, gm, n=20, segs=5)
    ring.scale = (0.8, 1.0, 1.0)
    out.append(ring)
    return kids(pr['body'], *out)


def build_carrier(P, root):
    """Lavadora: camisa da chapa de manga curta (V amarela da selecao, R vermelha com estrela), bermuda/calca da chapa,
    bone da chapa, galochas amarelas, toalha branca no pescoco e o balde azul de espuma."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(tunic=P['camisa'], skirt_m=P['calca'], vest=None, head='cap', head_m=P['bone'], belt=P['hose'],
                                         pants=P['calca'], bracer=P['skin'], boot_m=P['rubber_y'], glove=P['rubber_y'], scarf=P['foam']))
    peito_chapa(root, pr, tag, P)
    hold(pr, 'L', *bucket(root, tag, P))
    return pr


def build_engineer(P, root):
    """Encanador: camisa da chapa, capacete da chapa (V verde com crista amarela, R vermelho com crista branca), chave
    inglesa e o rolo de fita na cintura."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(tunic=P['camisa'], skirt_m=P['calca'], vest=None, head='bald', belt=P['hose'], pants=P['calca'],
                                         bracer=P['skin'], boot_m=P['rubber_y'], glove=P['rubber_y']))
    peito_chapa(root, pr, tag, P)
    hard_hat(root, pr, tag, P['bone'], ridge=P['cB'])
    fita = torus(root, tag + '_fitaCinto', (0.0, -0.1, 0.3), 0.035, 0.016, P['tape'], axis='Y', n=16, segs=5)
    fita.parent = pr['body']
    hold(pr, 'R', tube(root, tag + '_cabo', [(0, 0, -0.06), (0, 0, 0.14)], 0.013, P['chrome'], segs=6),
         box(root, tag + '_boca', (0.06, 0.03, 0.05), (0.012, 0, 0.17), m=P['chrome'], bev=0.008),
         box(root, tag + '_mandibula', (0.03, 0.028, 0.03), (0.03, 0, 0.2), m=P['chrome'], bev=0.005))
    return pr


IDLE_N, ACT_N = 12, 8


def carrier_state(mode, f):
    """idle: balde na mao, olha em volta; act: ergue o balde e joga a espuma para frente (ajuda a lavar)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.05, 0.15, 0.32 + 0.008 * s), grip_L=(0.0, 0.0, 1.0), hand_R=(0.06, -0.13, 0.28), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.15, ph=ph)
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_L=(0.08 + 0.14 * k, 0.12, 0.32 + 0.12 * k), grip_L=(0.7 * k, 0.0, 1.0 - 0.6 * k), hand_R=(0.1 + 0.08 * k, -0.06, 0.3 + 0.12 * k),
                lean=0.14 * k, head_pitch=-0.2, ph=f / ACT_N)


def engineer_state(mode, f):
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.12, -0.12, 0.28 + 0.01 * s), grip_R=(0.4, 0, 1.0), hand_L=(0.03, 0.13, 0.27),
                    breathe=s, head_yaw=0.4 * math.sin(TAU * ph), head_pitch=-0.05 + 0.15 * max(0, math.sin(TAU * ph * 2)), ph=ph)
    t = f / (ACT_N - 1)
    k = math.sin(math.pi * min(1, t * 1.6))
    return dict(hand_R=(0.2, -0.06 + 0.04 * k, 0.4 + 0.08 * k), grip_R=(1.0, 0.3 * k, 0.4), hand_L=(0.16, 0.1, 0.34 + 0.05 * k),
                lean=0.12 * k - 0.1 * max(0, t - 0.5), head_pitch=-0.12 * k, head_yaw=0.1, ph=t)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'cs1': ['csB1', 'csC'], 'cs2': ['csB2'], 'cs3': ['csB3'], 'csF': ['csB3'], 'csG': ['csBG', 'csE']},
    'towers': [('cs1', 'Lava a Jato N1', build_cs1), ('cs2', 'Lava a Jato N2', build_cs2), ('cs3', 'Lava a Jato N3', build_cs3),
               ('csF', 'Forca-Tarefa', build_csF), ('csG', 'Vaza Jato', build_csG)],
    'crews': [crew('csC', 'Lavadora', build_carrier, carrier_state), crew('csE', 'Encanador', build_engineer, engineer_state)],
    'turrets': [nozzle_spec('csB1', 'Canhao N1', size=0.85), nozzle_spec('csB2', 'Canhao N2', size=1.0, big=1),
                nozzle_spec('csB3', 'Canhao N3', size=1.1, big=2), nozzle_spec('csBG', 'Canhao do Vaza Jato', size=1.15, big=2)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
