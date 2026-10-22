"""Petrolao (Artilharia, Ninguem Sobe a Rampa): niveis 1 a 3, Refinaria Superfaturada e Sonda do Pre-Sal.
Mini plataforma de petroleo em preto e amarelo sobre o lote de concreto branco de Brasilia: deck de aco com pernas
amarelas, sonda de trelica, barris pretos com faixa amarela (conceito: arte/conceitos/torres/petrolao.png).
As torretas sao cavaletes de bombeio que viram catapulta: o balancim da o tranco e o barril sai da concha em cima da
cabeca de cavalo. A Sonda do Pre-Sal bate a broca no poco de oleo (conjunto arH, modo 'slam').
Nomes de conjuntos, postos, pontos e modos sao os mesmos da Catapulta de Castanhas (js/sprites.js depende deles).
Chapa (tools/blender/chapa.py): a pintura (pernas, coroas, guarda-corpo, flanges, bandeirolas), a bandeirinha e a turma
seguem a chapa: CHAPA=V verde e amarelo (camisa amarela, capacete verde), CHAPA=R vermelho com estrela branca (camiseta
vermelha com estrela, capacete vermelho). Oleo preto, barris (faixa amarela) e listras de advertencia nao mudam.

  Blender -b -P tools/blender/torre_artilharia.py -- render arte/render/artilharia [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_artilharia.py -- render arte/render_r/artilharia [conjuntos...]
  Blender -b -P tools/blender/torre_artilharia.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_artilharia.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, hazard_mat, hard_hat, work_lamp, concrete, grupo, hide_tree, prism_xz, G   # noqa: F811 - lote de Brasilia
from chapa import CHAPA, cor, emblema, bandeirinha, estrela_peito   # cores da chapa (CHAPA=V ou R no ambiente)

FRONT = -math.pi / 2
FAM = 'artilharia'

import lib as _lib
_orig_palette2 = palette2


def palette2():   # noqa: F811 - aco preto e amarelo de assinatura
    P = _orig_palette2()
    P['steel_k'] = mat('aco_preto', '#383537', rough=0.5, metal=0.25, var=0.05, bump=0.05)
    P['steel_k2'] = mat('aco_grafite', '#57525a', rough=0.55, metal=0.2, var=0.05, bump=0.05)
    P['grating'] = mat('grade_deck', '#4a4649', rough=0.7, metal=0.15, var=0.03, bump=0.1, stripes=(34.0, '#545054', '#3a3739'))
    P['yellow'] = mat('amarelo_petro', '#f2b52e', rough=0.5, var=0.03, bump=0.04)
    P['yellow_d'] = mat('amarelo_petro_escuro', '#d6951f', rough=0.55, var=0.03, bump=0.04)
    P['hazard'] = hazard_mat('listra_petro', freq=12.0)
    P['barrel'] = mat('barril_preto', '#2b282a', rough=0.32, metal=0.35, var=0.05, bump=0.03)
    P['oil'] = mat('oleo_cru', '#151214', rough=0.06, var=0.0, bump=0.0)
    P['conc'] = concrete()
    P['pipe'] = mat('cano_aco', '#aab1b6', rough=0.35, metal=0.55, var=0.03, bump=0.02)
    P['tank'] = mat('tanque_branco', '#f1efe9', rough=0.55, var=0.03, bump=0.04)
    P['smoke'] = mat('fumaca_refinaria', '#cfc9c3', rough=0.95, var=0.06, bump=0.25)
    P['coverall'] = mat('macacao_petro', '#3d4250', rough=0.82, var=0.03, bump=0.08, sheen=0.3)
    P['hivis'] = mat('colete_refletivo', '#f5c040', rough=0.7, var=0.02, bump=0.06, sheen=0.3)
    P['suit'] = mat('terno_diretor', '#2e2f38', rough=0.75, var=0.03, bump=0.06, sheen=0.4)
    P['shirt'] = mat('camisa_diretor', '#f3f1ea', rough=0.8, var=0.02, bump=0.05, sheen=0.3)
    P['rubber'] = mat('borracha', '#262427', rough=0.8, var=0.02, bump=0.05)
    # cores da chapa (CHAPA=V verde e amarelo / CHAPA=R vermelho e branco). O amarelo_petro fica so no que e funcional:
    # a faixa e o bocal do barril; as listras de advertencia (hazard) e o oleo preto nao mudam.
    P['cA'] = cor('pri')                                   # pintura principal: pernas, coroas, caixas, porta
    P['cB'] = cor('sec')                                   # detalhe: borda do deck, flanges, cintas, volantes
    P['cC'] = cor('sec') if CHAPA == 'V' else cor('pri')   # guarda-corpo, escadas e listras sobre o branco
    P['flag'] = cor('pri', rough=0.8, sheen=0.4)           # bandeirolas que balancam
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
GUN_FACE = math.radians(-35)     # o cavalete arremessa para a direita e um pouco para a camera (o jogo espelha)


# ---------------------------------------------------------------- utilidades
def oil_barrel(root, P, name, loc, r=0.075, h=None, lying=False, rot=0.0, parent=None, band=None):
    """Barril de petroleo preto: corpo levemente bojudo, dois frisos, a faixa amarela no meio e o bocal na tampa."""
    h = h or r * 2.25
    with grupo(root, name + '_piv', loc=loc, rot=((math.pi / 2, 0, rot) if lying else (0, 0, rot)), parent=parent) as e:
        prof = [(-h / 2, r * 0.9, r * 0.9), (-h / 2 + h * 0.06, r * 0.99, r * 0.99), (0, r * 1.035, r * 1.035),
                (h / 2 - h * 0.06, r * 0.99, r * 0.99), (h / 2, r * 0.9, r * 0.9)]
        lathe(root, name, prof, P['barrel'], segs=20, lv=1, caps=True)
        for k, zz in enumerate((-0.3, 0.3)):
            torus(root, f'{name}_friso{k}', (0, 0, h * zz), r * 1.03, max(0.004, r * 0.07), P['barrel'], n=22, segs=5)
        cyl(root, name + '_faixa', r * 1.05, h * 0.2, (0, 0, 0), m=band or P['yellow'], v=22, bev=0.003)
        torus(root, name + '_borda', (0, 0, h / 2 - 0.003), r * 0.86, max(0.004, r * 0.08), P['barrel'], n=20, segs=5)
        cyl(root, name + '_bocal', r * 0.17, r * 0.12, (r * 0.45, r * 0.2, h / 2 + 0.002), m=P['yellow'], v=10, bev=0.002)
    return e


def barrels(root, P, tag, spots, r=0.07):
    """Barris em pe (x, y, z) ou deitados (x, y, z, giro) espalhados pelo chao."""
    for k, sp in enumerate(spots):
        if len(sp) == 4:
            oil_barrel(root, P, f'{tag}_barril{k}', (sp[0], sp[1], sp[2] + r), r=r, lying=True, rot=sp[3])
        else:
            oil_barrel(root, P, f'{tag}_barril{k}', (sp[0], sp[1], sp[2] + r * 1.125), r=r, rot=0.4 * k)


def oil_puddle(root, P, tag, x, y, rx, ry, z=G, rot=0.0):
    sphere(root, tag, 1.0, (x, y, z + 0.002), scale=(rx, ry, 0.012), m=P['oil'], seg=20, rot=(0, 0, rot))


def rail(root, P, tag, pts, z, h=0.13, m=None, front=False, every=0.24, r=0.012):
    """Guarda-corpo na cor da chapa: postes, corrimao e travessa do meio passando pelos pontos (x, y)."""
    m = m or P['cC']
    top = [(x, y, z + h) for x, y in pts]
    mid = [(x, y, z + h * 0.5) for x, y in pts]
    tube(root, tag + '_corrimao', top, r, m, segs=8, front=front)
    tube(root, tag + '_meio', mid, r * 0.75, m, segs=6, front=front)
    k = 0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(L / every))
        for i in range(n + (1 if (x1, y1) == pts[-1] else 0)):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            tube(root, f'{tag}_poste{k}', [(x, y, z), (x, y, z + h)], r * 0.9, m, segs=6, front=front)
            k += 1


def deck(root, P, tag, cx, cy, w, d, ztop, th=0.06, leg_r=0.065, inset=0.09, braces=False, z0=G):
    """Deck de aco (grade escura) com borda amarela, faixa listrada na frente e quatro pernas amarelas."""
    box(root, tag + '_deck', (w, d, th), (cx, cy, ztop - th / 2), m=P['grating'], bev=0.018)
    box(root, tag + '_deckBorda', (w + 0.025, d + 0.025, th * 0.5), (cx, cy, ztop - th * 0.72), m=P['cB'], bev=0.01)
    box(root, tag + '_deckListra', (w - 0.06, 0.014, th * 0.42), (cx, cy - d / 2 - 0.012, ztop - th * 0.7), m=P['hazard'], bev=0.0)
    legs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * (w / 2 - inset), cy + sy * (d / 2 - inset)
            cyl(root, f'{tag}_perna{sx}{sy}', leg_r, ztop - th - z0, (x, y, (ztop - th + z0) / 2), m=P['cA'], v=18, bev=0.012)
            cyl(root, f'{tag}_pe{sx}{sy}', leg_r * 1.5, 0.03, (x, y, z0 + 0.015), m=P['steel_k'], v=18, bev=0.008)
            torus(root, f'{tag}_anelPerna{sx}{sy}', (x, y, ztop - th - 0.03), leg_r * 1.05, 0.012, P['steel_k'], n=16, segs=5)
            legs.append((x, y))
    if braces:
        za, zb = z0 + 0.06, ztop - th - 0.05
        for k, (a, b) in enumerate(((0, 1), (1, 3), (2, 3), (0, 2))):
            if k == 3:
                continue    # a frente fica aberta (barris e canos aparecem por baixo)
            pa, pb = legs[a], legs[b]
            tube(root, f'{tag}_xA{k}', [(pa[0], pa[1], za), (pb[0], pb[1], zb)], 0.016, P['steel_k'], segs=6)
            tube(root, f'{tag}_xB{k}', [(pb[0], pb[1], za), (pa[0], pa[1], zb)], 0.016, P['steel_k'], segs=6)
    return legs


def truss(root, P, tag, c, bot, top, z0, z1, levels=4, r_leg=0.03, r_br=0.014, faces=('back', 'left', 'right'),
          front_legs=False, band_every=2):
    """Torre de trelica de 4 pernas afunilando (sonda): pernas pretas com cintas amarelas, cintas horizontais e
    X nas faces pedidas. bot/top: meias larguras (x, y) embaixo e em cima."""
    cx, cy = c

    def corner(sx, sy, t):
        hx = bot[0] + (top[0] - bot[0]) * t
        hy = bot[1] + (top[1] - bot[1]) * t
        return Vector((cx + sx * hx, cy + sy * hy, z0 + (z1 - z0) * t))
    for sx in (-1, 1):
        for sy in (-1, 1):
            fr = front_legs and sy < 0
            tube(root, f'{tag}_perna{sx}{sy}', [corner(sx, sy, 0), corner(sx, sy, 1)], r_leg, P['steel_k'], segs=8, front=fr)
            for k in range(1, levels + 1, band_every):
                p = corner(sx, sy, (k - 0.5) / levels)
                sphere(root, f'{tag}_cinta{sx}{sy}_{k}', r_leg * 1.5, tuple(p), scale=(1, 1, 0.7), m=P['cB'], seg=10, front=fr)
    face_pts = {'back': ((-1, 1), (1, 1)), 'front': ((-1, -1), (1, -1)), 'left': ((-1, -1), (-1, 1)), 'right': ((1, -1), (1, 1))}
    for k in range(levels + 1):
        t = k / levels
        for f, (a, b) in face_pts.items():
            if f not in faces and not (f == 'front' and k == levels):
                continue
            fr = front_legs and f == 'front'
            tube(root, f'{tag}_cintaH{f}{k}', [corner(*a, t), corner(*b, t)], r_br, P['steel_k'], segs=6, front=fr)
        if k == levels:
            break
        t2 = (k + 1) / levels
        for f in faces:
            a, b = face_pts[f]
            tube(root, f'{tag}_x{f}{k}a', [corner(*a, t), corner(*b, t2)], r_br * 0.85, P['steel_k2'], segs=5)
            tube(root, f'{tag}_x{f}{k}b', [corner(*b, t), corner(*a, t2)], r_br * 0.85, P['steel_k2'], segs=5)
    return corner


def stairs(root, P, tag, p0, p1, w=0.16, steps=6, front=False):
    """Escada reta na cor da chapa de p0 (chao) ate p1 (deck), com degraus pretos e corrimao."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    side = Vector((-d.y, d.x, 0)).normalized() * (w / 2)
    for s, sg in enumerate((-1, 1)):
        tube(root, f'{tag}_banzo{s}', [a + side * sg, b + side * sg], 0.014, P['cC'], segs=6, front=front)
        tube(root, f'{tag}_corrimao{s}', [a + side * sg + Vector((0, 0, 0.13)), b + side * sg + Vector((0, 0, 0.13))], 0.01, P['cC'], segs=6, front=front)
        for t in (0.0, 1.0):
            p = a.lerp(b, t) + side * sg
            tube(root, f'{tag}_balaustre{s}{int(t)}', [p, p + Vector((0, 0, 0.13))], 0.009, P['cC'], segs=5, front=front)
    ang = math.atan2(d.y, d.x)
    for k in range(steps):
        p = a.lerp(b, (k + 0.5) / steps)
        box(root, f'{tag}_degrau{k}', (0.05, w, 0.016), tuple(p), rot=(0, 0, ang), m=P['steel_k'], bev=0.004, front=front)


def tank_v(root, P, tag, x, y, z0, h, r, m=None, band=None, cap=None):
    """Tanque vertical: corpo, tampa abaulada, faixa e escadinha."""
    m = m or P['tank']
    cyl(root, tag, r, h, (x, y, z0 + h / 2), m=m, v=28, bev=0.02)
    lathe(root, tag + '_tampa', [(0, r, r), (r * 0.18, r * 0.8, r * 0.8), (r * 0.3, r * 0.35, r * 0.35), (r * 0.34, 0.0, 0.0)],
          cap or m, segs=28, lv=1).location = (x, y, z0 + h - 0.005)
    if band:
        cyl(root, tag + '_faixa', r * 1.02, min(0.06, h * 0.16), (x, y, z0 + h * 0.62), m=band, v=28, bev=0.004)


def flame(root, P, tag, loc, s=1.0):
    """Chama de queima no alto do flare: tres gotas de fogo que tremulam (pecas animadas)."""
    x, y, z = loc
    piv = empty(root, tag + '_chamaPivo', loc=loc)
    for k, (dx, hh, rr_) in enumerate(((0.0, 0.16, 0.05), (-0.03, 0.11, 0.035), (0.03, 0.1, 0.032))):
        o = sphere(root, f'{tag}_chama{k}', rr_ * s, (dx * s, 0, hh * s * 0.45), scale=(1, 1, hh / rr_ * 0.55), m=P['fire'], seg=12)
        kids(piv, o)
    register_anim(piv, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Diagonal((1 + 0.08 * math.sin(TAU * ph * 3),
                                                                                         1 + 0.08 * math.sin(TAU * ph * 3),
                                                                                         1 + 0.18 * math.sin(TAU * ph * 2), 1))))
    return piv


def smoke(root, P, tag, loc, n=4, s=1.0, rise=0.5, drift=(0.12, 0.05)):
    """Fumaca subindo da chamine: bolotas que crescem, sobem e somem (loop perfeito, cada uma com sua fase)."""
    for k in range(n):
        piv = empty(root, f'{tag}_fumacaPivo{k}', loc=loc)
        o = sphere(root, f'{tag}_fumaca{k}', 0.06 * s, (0, 0, 0), scale=(1.1, 1.0, 0.9), m=P['smoke'], seg=14)
        kids(piv, o)

        def fn(ob, mb, ph, k=k):
            t = (ph + k / n) % 1.0
            sc = math.sin(math.pi * t) * (0.6 + 0.9 * t)
            off = Vector((drift[0] * t, drift[1] * t, rise * t))
            ob.matrix_basis = Matrix.Translation(off) @ mb @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(piv, fn)


def pennant(root, P, tag, x, y, z, pole=0.32, length=0.22, height=0.1):
    """Bandeirola na cor da chapa num mastro fino, balancando no loop."""
    tube(root, tag + '_mastro', [(x, y, z), (x, y, z + pole)], 0.011, P['steel_k'], segs=6)
    sphere(root, tag + '_pomo', 0.018, (x, y, z + pole + 0.01), m=P['cB'], seg=8)
    pen = cloth_grid(root, tag, length, height, 10, 3, [P['flag']], thick=0.008,
                     shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * height * (1 - u * 0.85))))
    pen.location = (x + 0.01, y, z + pole - height * 0.5)
    register_cloth(pen, flag_wave(length, amp=0.04, cycles=1, waves=1.1))
    return pen


def wellhead(root, P, tag, x, y, z=G, s=1.0):
    """Arvore de natal do poco: carretel preto, flanges e valvulas com volante na cor da chapa."""
    cyl(root, tag, 0.05 * s, 0.1 * s, (x, y, z + 0.05 * s), m=P['steel_k'], v=16, bev=0.01)
    for k, zz in enumerate((0.1, 0.2)):
        cyl(root, f'{tag}_flange{k}', 0.065 * s, 0.02 * s, (x, y, z + zz * s), m=P['cA'], v=18, bev=0.004)
    cyl(root, tag + '_corpo', 0.04 * s, 0.12 * s, (x, y, z + 0.27 * s), m=P['steel_k'], v=14, bev=0.008)
    for sx in (-1, 1):
        tube(root, f'{tag}_braco{sx}', [(x, y, z + 0.24 * s), (x + sx * 0.09 * s, y, z + 0.24 * s)], 0.02 * s, P['steel_k'], segs=8)
        torus(root, f'{tag}_volante{sx}', (x + sx * 0.1 * s, y, z + 0.24 * s), 0.035 * s, 0.008 * s, P['cB'], axis='X', n=14, segs=5)
    torus(root, tag + '_volanteTopo', (x, y, z + 0.35 * s), 0.04 * s, 0.009 * s, P['cB'], n=14, segs=5)


# ---------------------------------------------------------------- cavalete-catapulta (conjuntos separados: espelham e arremessam)
ARM_REST = math.radians(20)      # balancim com a cabeca de cavalo baixa e o barril na concha
ARM_FIRE = math.radians(-48)     # cabeca de cavalo no alto: o barril acabou de sair
HEAD_PTS = [(0.25, 0.03), (0.31, 0.03), (0.355, 0.0), (0.378, -0.06), (0.365, -0.13), (0.325, -0.185), (0.27, -0.205), (0.245, -0.16)]


def gun_dims(size, royal):
    s = size * (1.12 if royal else 1.0)
    cup_r = (0.072 if not royal else 0.095) * s
    br = cup_r * 0.86
    return s, cup_r, br, br * 2.25


def build_gun(P, root, size=1.0, ornate=0, royal=False):
    """Cavalete de bombeio que virou catapulta: base (skid) preta, cavalete em A, balancim com a cabeca de cavalo
    e a concha do barril na ponta, redutor amarelo com a manivela e as bielas; aponta para +X local."""
    tag = root['set']
    piv = empty(root, tag + '_giro', rot=(0, 0, GUN_FACE))
    s, cup_r, br, bh = gun_dims(size, royal)
    K, Y = P['steel_k'], P['cA']               # aco preto e a pintura da chapa
    trim = P['gold'] if royal else P['cB']     # a da Refinaria Superfaturada e folheada a ouro
    with grupo(root, tag + '_base', parent=piv):
        for sy in (-1, 1):
            box(root, f'{tag}_longarina{sy}', (0.72 * s, 0.05 * s, 0.05 * s), (-0.02 * s, sy * 0.1 * s, 0.025 * s), m=K, bev=0.01)
        for k, x in enumerate((-0.32, -0.04, 0.24)):
            box(root, f'{tag}_travessa{k}', (0.05 * s, 0.27 * s, 0.035 * s), (x * s, 0, 0.035 * s), m=Y, bev=0.008)
        box(root, tag + '_chapa', (0.22 * s, 0.2 * s, 0.018 * s), (0.0, 0, 0.058 * s), m=P['hazard'], bev=0.004)
        # cavalete (dois As) e o mancal no alto
        for sy in (-1, 1):
            for sx in (-1, 1):
                tube(root, f'{tag}_perna{sx}{sy}', [(sx * 0.15 * s, sy * 0.1 * s, 0.05 * s), (0.0, sy * 0.06 * s, 0.44 * s)], 0.022 * s, K, segs=8)
            tube(root, f'{tag}_travessaA{sy}', [(-0.1 * s, sy * 0.088 * s, 0.18 * s), (0.1 * s, sy * 0.088 * s, 0.18 * s)], 0.015 * s, Y, segs=6)
            tube(root, f'{tag}_diagA{sy}', [(-0.1 * s, sy * 0.088 * s, 0.18 * s), (0.04 * s, sy * 0.07 * s, 0.34 * s)], 0.012 * s, K, segs=6)
        cyl(root, tag + '_mancal', 0.045 * s, 0.17 * s, (0, 0, 0.46 * s), rot=(math.pi / 2, 0, 0), m=trim, v=16, bev=0.008)
        # redutor amarelo e motor atras
        box(root, tag + '_redutor', (0.15 * s, 0.12 * s, 0.13 * s), (-0.27 * s, 0, 0.11 * s), m=Y, bev=0.025)
        cyl(root, tag + '_motor', 0.045 * s, 0.1 * s, (-0.4 * s, 0, 0.08 * s), rot=(0, math.pi / 2, 0), m=K, v=14, bev=0.008)
        # cabeca do poco na frente (onde desce a haste polida)
        cyl(root, tag + '_poco', 0.035 * s, 0.07 * s, (0.33 * s, 0, 0.035 * s), m=K, v=14, bev=0.006)
        cyl(root, tag + '_pocoFlange', 0.05 * s, 0.016 * s, (0.33 * s, 0, 0.075 * s), m=P['cB'], v=16, bev=0.004)
        torus(root, tag + '_pocoVolante', (0.33 * s, -0.06 * s, 0.045 * s), 0.024 * s, 0.006 * s, P['cB'], axis='Y', n=12, segs=5)
        tube(root, tag + '_pocoBraco', [(0.33 * s, 0, 0.045 * s), (0.33 * s, -0.06 * s, 0.045 * s)], 0.01 * s, K, segs=6)
        if ornate >= 1 or royal:
            # guarda (cor de detalhe da chapa, ou ouro) em volta da manivela
            g = [(-0.17 * s, -0.16 * s), (-0.44 * s, -0.16 * s), (-0.44 * s, 0.16 * s), (-0.17 * s, 0.16 * s)]
            tube(root, tag + '_guarda', [(x, y, 0.2 * s) for x, y in g], 0.01 * s, trim, segs=6)
            for k, (x, y) in enumerate(g):
                tube(root, f'{tag}_guardaPoste{k}', [(x, y, 0.03 * s), (x, y, 0.2 * s)], 0.009 * s, trim, segs=5)
    PC = Vector((-0.27 * s, 0, 0.14 * s))
    RC = 0.1 * s
    crank = empty(root, tag + '_manivela', loc=tuple(PC), parent=piv)
    for sy in (-1, 1):
        kids(crank, box(root, f'{tag}_manivelaBraco{sy}', (RC + 0.05 * s, 0.025 * s, 0.045 * s), (RC * 0.5 - 0.02 * s, sy * 0.085 * s, 0), m=K, bev=0.008))
        cw = prism_xz(root, f'{tag}_contrapeso{sy}', [(-0.02 * s, 0.05 * s), (-0.1 * s, 0.035 * s), (-0.125 * s, 0.0), (-0.1 * s, -0.035 * s), (-0.02 * s, -0.05 * s)],
                      0.032 * s, P['hazard'], bev=0.008)
        cw.location = (0, sy * 0.085 * s, 0)
        kids(crank, cw)
        kids(crank, cyl(root, f'{tag}_pino{sy}', 0.016 * s, 0.05 * s, (RC, sy * 0.1 * s, 0), rot=(math.pi / 2, 0, 0), m=trim, v=10, bev=0.003))
    # balancim (gira em Y no mancal) com a cabeca de cavalo, a concha e o barril
    AX = Vector((0, 0, 0.46 * s))
    arm = empty(root, tag + '_braco', loc=tuple(AX), parent=piv, rot=(0, ARM_REST, 0))
    with grupo(root, tag + '_balancimG', parent=arm):
        box(root, tag + '_balancim', (0.54 * s, 0.06 * s, 0.055 * s), (0.03 * s, 0, 0), m=K, bev=0.012)
        box(root, tag + '_balancimFaixa', (0.46 * s, 0.064 * s, 0.014 * s), (0.03 * s, 0, 0.022 * s), m=P['gold'] if royal else P['cB'], bev=0.004)
        cyl(root, tag + '_equalizador', 0.022 * s, 0.22 * s, (-0.22 * s, 0, -0.025 * s), rot=(math.pi / 2, 0, 0), m=trim, v=12, bev=0.004)
        prism_xz(root, tag + '_cabeca', [(x * s, z * s) for x, z in HEAD_PTS], 0.075 * s, K, bev=0.012)
        cxh = sum(p[0] for p in HEAD_PTS) / len(HEAD_PTS)
        czh = sum(p[1] for p in HEAD_PTS) / len(HEAD_PTS)
        prism_xz(root, tag + '_cabecaJanela', [((cxh + (x - cxh) * 0.6) * s, (czh + (z - czh) * 0.6) * s) for x, z in HEAD_PTS], 0.085 * s,
                 Y, bev=0.008)
        cup = lathe(root, tag + '_concha', [(0, 0.0, 0.0), (0.012 * s, cup_r * 0.85, cup_r * 0.85), (0.04 * s, cup_r, cup_r), (0.055 * s, cup_r * 1.06, cup_r * 1.06)],
                    trim, segs=20, lv=1, caps=False, solid=0.01)
        cup.location = (0.29 * s, 0, 0.026 * s)
    load = empty(root, tag + '_carga', parent=arm, loc=(0.29 * s, 0, 0.034 * s))
    oil_barrel(root, P, tag + '_barril', (0, 0, bh / 2), r=br, h=bh, parent=load, band=P['gold'] if royal else None)
    if ornate >= 2 or royal:
        # bandeirola da chapa no cavalete, com o emblema dos dois lados perto do mastro
        with grupo(root, tag + '_bandeiraG', parent=piv):
            tube(root, tag + '_mastro', [(-0.15 * s, 0.1 * s, 0.05 * s), (-0.15 * s, 0.13 * s, 0.7 * s)], 0.01 * s, K, segs=6)
            pen = cloth_grid(root, tag + '_flamula', 0.2 * s, 0.1 * s, 10, 3, [P['flag']], thick=0.008,
                             shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.1 * s * (1 - u * 0.85))))
            pen.location = (-0.14 * s, 0.13 * s, 0.66 * s)
        for sd, sg in (('a', -1), ('b', 1)):
            for o in emblema(root, f'{tag}_flamulaEmblema{sd}', 0.085 * s, 0.075 * s, loc=(0.06 * s, sg * 0.007, 0.0),
                             rot=(0, 0, 0 if sg < 0 else math.pi), depth=0.004):
                if o.parent == root:
                    o.parent = pen
    rods = {}
    for sy in (-1, 1):
        rods[sy] = ensure_mesh(root, f'{tag}_biela{sy}', K)
        rods[sy].parent = piv
    rod = ensure_mesh(root, tag + '_hastePolida', P['pipe'])
    rod.parent = piv
    bridle = ensure_mesh(root, tag + '_cabresto', P['steel_k'])
    bridle.parent = piv
    d_rest = (AX + Matrix.Rotation(ARM_REST, 3, 'Y') @ Vector((-0.22 * s, 0, -0.025 * s)) - PC).length
    d_fire = (AX + Matrix.Rotation(ARM_FIRE, 3, 'Y') @ Vector((-0.22 * s, 0, -0.025 * s)) - PC).length
    return {'piv': piv, 'arm': arm, 'load': load, 'crank': crank, 'rods': rods, 'rod': rod, 'bridle': bridle,
            's': s, 'AX': AX, 'PC': PC, 'RC': RC, 'LR': (d_rest + d_fire) / 2, 'bh': bh}


def gun_tip(size=1.0, royal=False):
    """Boca da torreta (centro do barril no instante do disparo), em BU relativas ao posto, ja com o CREW_BOOST."""
    s, cup_r, br, bh = gun_dims(size, royal)
    p = Vector((0, 0, 0.46 * s)) + Matrix.Rotation(ARM_FIRE, 3, 'Y') @ Vector((0.29 * s, 0, 0.034 * s + bh / 2))
    return Matrix.Rotation(GUN_FACE, 3, 'Z') @ p * CREW_BOOST


def gun_points(parts, tl):
    """Ponto de saida do barril: o centro do barril com o balancim no alto (instante do disparo)."""
    arm = parts['arm']
    old = arm.rotation_euler.copy()
    arm.rotation_euler = (0, ARM_FIRE, 0)
    bpy.context.view_layer.update()
    m = parts['load'].matrix_world @ Vector((0, 0, parts['bh'] / 2))
    arm.rotation_euler = old
    bpy.context.view_layer.update()
    return {'points': {'muzzle': project(m, tl)}}


ARM_SEQ = [0.0, 0.06, 0.2, 0.42, 0.66, 0.86, 0.97, 1.0]   # 0 = disparo (cabeca no alto), 1 = repouso (cabeca baixa com o barril)


def pose_gun(parts, f):
    """fire: quadro 0 = o balancim no alto (o barril ja saiu), depois desce devagar e recarrega (5..7).
    A manivela acompanha: gira ate a biela (comprimento fixo) alcancar a ponta de tras do balancim."""
    k = ARM_SEQ[f] if f is not None else 1.0
    th = ARM_FIRE + (ARM_REST - ARM_FIRE) * k
    parts['arm'].rotation_euler = (0, th, 0)
    hide_tree(parts['load'], f is not None and f < 5)
    s, AX, PC, RC, LR = parts['s'], parts['AX'], parts['PC'], parts['RC'], parts['LR']
    Ry = Matrix.Rotation(th, 3, 'Y')
    B = AX + Ry @ Vector((-0.22 * s, 0, -0.025 * s))
    H = AX + Ry @ Vector((0.372 * s, 0, -0.1 * s))
    dx, dz = B.x - PC.x, B.z - PC.z
    dl = math.hypot(dx, dz)
    ca = max(-1.0, min(1.0, (RC * RC + dl * dl - LR * LR) / (2 * RC * dl)))
    ang = math.atan2(dz, dx) + math.acos(ca)
    parts['crank'].rotation_euler = (0, -ang, 0)
    pin = Vector((PC.x + RC * math.cos(ang), 0, PC.z + RC * math.sin(ang)))
    for sy, o in parts['rods'].items():
        set_mesh_tube(o, [(pin.x, sy * 0.1 * s, pin.z), (B.x, sy * 0.1 * s, B.z)], 0.014 * s, segs=8)
    # cabresto (dois cabos) da frente da cabeca ate a barra, e a haste polida descendo ate o poco
    bar_z = max(0.14 * s, H.z - 0.08 * s)
    set_mesh_tube(parts['bridle'], [(H.x, -0.03 * s, H.z), (0.33 * s, -0.03 * s, bar_z), (0.33 * s, 0.03 * s, bar_z), (H.x, 0.03 * s, H.z)], 0.006 * s, segs=6)
    set_mesh_tube(parts['rod'], [(0.33 * s, 0, 0.08 * s), (0.33 * s, 0, bar_z + 0.01 * s)], 0.011 * s, segs=8)


GUN_N = 8


def gun_spec(key, label, **kw):
    def build(P, root):
        return build_gun(P, root, **kw)
    return {'key': key, 'label': label, 'build': build, 'boost': CREW_BOOST, 'shadow': True, 'extra': gun_points,
            'pose0': lambda parts, P, root: pose_gun(parts, None),
            'modes': [('fire', GUN_N, lambda parts, P, root, f: pose_gun(parts, f))]}


def top_of(slot, **kw):
    """Ponto 'top' (origem do barril no jogo, DATA.TOWER_TOP): o posto da torreta mais a boca do cavalete."""
    t = gun_tip(**kw)
    return (slot[0] + t.x * 0.5, slot[1], slot[2] + t.z)


# ---------------------------------------------------------------- nivel 1: plataformazinha de bombeio
def build_ar1(P, root):
    plot(root, P, 'ar1')
    lights = []
    dz = G + 0.2
    deck(root, P, 'ar1', 0.0, 0.06, 1.0, 0.74, dz, leg_r=0.06)
    rail(root, P, 'ar1_guarda', [(-0.48, -0.2), (-0.48, 0.41), (0.48, 0.41), (0.48, 0.05)], dz)
    # barris na frente, com a pocinha de oleo
    oil_puddle(root, P, 'ar1_poca', 0.46, -0.46, 0.22, 0.14, rot=0.3)
    barrels(root, P, 'ar1', [(0.36, -0.5, G), (0.56, -0.34, G), (0.52, -0.56, G, 0.5)], r=0.07)
    # arvore de natal do poco a esquerda, com o cano entrando no deck
    wellhead(root, P, 'ar1_poco', -0.62, -0.42, s=0.85)
    tube(root, 'ar1_cano', [(-0.62, -0.42, G + 0.2), (-0.62, -0.2, G + 0.2), (-0.46, -0.1, G + 0.12)], 0.022, P['pipe'], segs=8)
    # poste com refletor atras
    tube(root, 'ar1_poste', [(-0.66, 0.42, G), (-0.66, 0.42, G + 0.62)], 0.02, P['steel_k'], segs=8)
    work_lamp(root, P, 'ar1_refletor', (-0.62, 0.4, G + 0.6), face=-0.9)
    pennant(root, P, 'ar1_flamula', -0.66, 0.42, G + 0.62, pole=0.18, length=0.18, height=0.08)
    bandeirinha(root, 'ar1_bandeira', (0.42, 0.38, dz), h=0.36, w=0.2, fh=0.13)
    lights.append(((-0.6, 0.36, G + 0.58), '#ffcf7a', 14.0, 1))
    slot = (0.04, 0.0, dz)
    return {'slots': [slot, (-0.38, 0.24, dz)], 'lights': lights, 'points': {'top': top_of(slot, size=0.95)}}


# ---------------------------------------------------------------- nivel 2: deck alto com a sonda pequena e a escada
def build_ar2(P, root):
    plot(root, P, 'ar2')
    lights = []
    dz = G + 0.44
    deck(root, P, 'ar2', 0.0, 0.08, 1.18, 0.96, dz, th=0.07, leg_r=0.06, braces=True)
    rail(root, P, 'ar2_guarda', [(-0.57, -0.1), (-0.57, 0.54), (0.57, 0.54), (0.57, 0.2)], dz)
    rail(root, P, 'ar2_guardaFrente', [(-0.57, -0.38), (-0.3, -0.38)], dz, front=True)
    # sonda de trelica atras, a esquerda, com a roldana e o refletor
    sx_, sy_ = -0.42, 0.42
    truss(root, P, 'ar2_sonda', (sx_, sy_), (0.12, 0.1), (0.045, 0.04), dz, dz + 1.0, levels=5, r_leg=0.022, r_br=0.01,
          faces=('front', 'back', 'left', 'right'))
    box(root, 'ar2_sondaTopo', (0.15, 0.13, 0.05), (sx_, sy_, dz + 1.02), m=P['cA'], bev=0.012)
    torus(root, 'ar2_roldana', (sx_, sy_, dz + 1.08), 0.045, 0.012, P['cB'], axis='X', n=16, segs=5)
    pennant(root, P, 'ar2_flamula', sx_ + 0.04, sy_, dz + 1.04, pole=0.22, length=0.2, height=0.09)
    work_lamp(root, P, 'ar2_refletor', (sx_, sy_ - 0.08, dz + 0.78), face=-math.pi / 2)
    lights.append(((sx_, sy_ - 0.13, dz + 0.76), '#ffcf7a', 14.0, 1))
    # escada pela direita
    stairs(root, P, 'ar2_escada', (0.7, -0.4, G), (0.68, 0.16, dz), w=0.16, steps=7)
    # por baixo e em volta: barris, tanque e o poco
    barrels(root, P, 'ar2', [(-0.2, 0.2, G), (0.04, 0.24, G), (-0.1, 0.02, G), (-0.62, -0.5, G), (-0.46, -0.62, G, 0.2), (-0.8, -0.3, G)], r=0.07)
    oil_puddle(root, P, 'ar2_poca', -0.55, -0.6, 0.2, 0.12, rot=-0.3)
    tank_v(root, P, 'ar2_tanque', 0.3, 0.26, G, 0.3, 0.14, band=P['cA'])
    wellhead(root, P, 'ar2_poco', 0.36, -0.26, s=0.8)
    bandeirinha(root, 'ar2_bandeira', (0.52, 0.5, dz), h=0.36, w=0.2, fh=0.13)
    slot = (0.02, -0.06, dz)
    return {'slots': [slot, (-0.36, 0.1, dz), (0.38, 0.26, dz)], 'lights': lights, 'points': {'top': top_of(slot, size=1.05)}}


# ---------------------------------------------------------------- nivel 3: plataforma alta com a torre de sonda e o flare
def build_ar3(P, root):
    plot(root, P, 'ar3')
    lights = []
    fz = 0.8
    # pernas grossas de plataforma (jaqueta) com contraventamento
    deck(root, P, 'ar3', 0.0, 0.04, 1.36, 1.12, fz, th=0.08, leg_r=0.085, inset=0.12, braces=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (0.68 - 0.12), 0.04 + sy * (0.56 - 0.12)
            for k, zz in enumerate((0.3, 0.55)):
                torus(root, f'ar3_cintaPerna{sx}{sy}{k}', (x, y, zz), 0.09, 0.014, P['steel_k'], n=18, segs=5)
    rail(root, P, 'ar3_guarda', [(-0.66, -0.2), (-0.66, 0.58), (0.66, 0.58), (0.66, -0.2)], fz)
    rail(root, P, 'ar3_guardaFrenteE', [(-0.66, -0.5), (-0.36, -0.5)], fz, front=True)
    rail(root, P, 'ar3_guardaFrenteD', [(0.36, -0.5), (0.66, -0.5)], fz, front=True)
    # torre de sonda no fundo, no meio, com a catarina e o barril pendurado (balanca)
    truss(root, P, 'ar3_sonda', (0.0, 0.36), (0.2, 0.17), (0.07, 0.06), fz, fz + 1.08, levels=5, r_leg=0.026, r_br=0.011,
          faces=('front', 'back', 'left', 'right'))
    box(root, 'ar3_coroa', (0.24, 0.2, 0.07), (0.0, 0.36, fz + 1.11), m=P['cA'], bev=0.016)
    torus(root, 'ar3_coroaRoldana', (0.0, 0.26, fz + 1.1), 0.05, 0.014, P['steel_k'], axis='X', n=16, segs=5)
    tube(root, 'ar3_lanca', [(0.0, 0.3, fz + 1.08), (0.36, 0.2, fz + 1.2)], 0.022, P['steel_k'], segs=8)
    hook = empty(root, 'ar3_ganchoPivo', loc=(0.36, 0.2, fz + 1.18))
    kids(hook, tube(root, 'ar3_cabo', [(0, 0, 0), (0, 0, -0.36)], 0.008, P['steel_k'], segs=5))
    kids(hook, box(root, 'ar3_moitao', (0.05, 0.04, 0.07), (0, 0, -0.38), m=P['cA'], bev=0.01))
    oil_barrel(root, P, 'ar3_barrilPend', (0, 0, -0.5), r=0.055, parent=hook)
    register_anim(hook, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.09 * math.sin(TAU * ph), 4, 'X')))
    for k, zz in enumerate((0.45, 0.85)):
        work_lamp(root, P, f'ar3_refletor{k}', (0.0 + (0.09 if k else -0.1), 0.26, fz + zz), face=-math.pi / 2)
    lights.append(((0.0, 0.22, fz + 0.65), '#ffcf7a', 16.0, 1))
    # flare na esquerda (braco inclinado) com a chama
    tube(root, 'ar3_flare', [(-0.6, 0.4, fz), (-0.78, 0.46, fz + 0.5), (-0.86, 0.5, fz + 0.86)], 0.032, P['steel_k'], segs=10)
    for k, t in enumerate((0.3, 0.65)):
        torus(root, f'ar3_flareCinta{k}', (-0.6 - 0.24 * t, 0.4 + 0.09 * t, fz + 0.84 * t), 0.04, 0.012, P['cB'], n=14, segs=5)
    cyl(root, 'ar3_flareBico', 0.045, 0.05, (-0.86, 0.5, fz + 0.88), m=P['cA'], v=14, bev=0.008)
    flame(root, P, 'ar3_flare', (-0.86, 0.5, fz + 0.9), s=1.0)
    lights.append(((-0.86, 0.5, fz + 1.0), '#ff9a3a', 18.0, 1))
    # escada pela esquerda e, por baixo, barris e canos
    # escada de marinheiro com gaiola na perna da frente, a esquerda
    lx, ly = -0.36, -0.55
    for sx in (-1, 1):
        tube(root, f'ar3_escadaBanzo{sx}', [(lx + sx * 0.06, ly, G), (lx + sx * 0.06, ly, fz + 0.12)], 0.011, P['cC'], segs=6)
    for k in range(9):
        zz = G + 0.07 + k * (fz - G - 0.08) / 8
        tube(root, f'ar3_escadaDegrau{k}', [(lx - 0.06, ly, zz), (lx + 0.06, ly, zz)], 0.008, P['steel_k'], segs=5)
    for k, zz in enumerate((0.45, 0.62, 0.79)):
        tube(root, f'ar3_gaiola{k}', [(lx - 0.06, ly, zz)] + [(lx - 0.06 * math.cos(a), ly - 0.09 * math.sin(a), zz) for a in (0.6, 1.2, 1.9, 2.5)] + [(lx + 0.06, ly, zz)],
             0.007, P['cC'], segs=5)
    barrels(root, P, 'ar3',[(-0.26, 0.22, G), (0.0, 0.26, G), (0.26, 0.22, G), (-0.12, 0.04, G), (0.14, 0.06, G),
                             (0.56, -0.62, G), (0.72, -0.46, G), (0.66, -0.68, G, 1.0)], r=0.07)
    oil_puddle(root, P, 'ar3_poca', 0.6, -0.6, 0.22, 0.13, rot=0.2)
    tube(root, 'ar3_cano', [(-0.5, -0.36, G + 0.1), (-0.5, -0.36, fz - 0.1), (-0.4, -0.3, fz - 0.1)], 0.026, P['pipe'], segs=8)
    for k, zz in enumerate((G + 0.24, fz - 0.24)):
        torus(root, f'ar3_canoFlange{k}', (-0.5, -0.36, zz), 0.036, 0.01, P['cB'], n=14, segs=5)
    wellhead(root, P, 'ar3_poco', -0.5, -0.36, s=0.7)
    bandeirinha(root, 'ar3_bandeira', (0.6, 0.54, fz), h=0.38, w=0.2, fh=0.13)
    slot = (0.0, -0.08, fz)
    return {'slots': [slot, (-0.4, 0.1, fz), (0.4, 0.14, fz)], 'lights': lights, 'points': {'top': top_of(slot, size=1.12)}}


# ---------------------------------------------------------------- Refinaria Superfaturada: chamines, coluna e canos de ouro
def gold_bars(root, P, tag, x, y, z=G, rows=3):
    """Pilha de barras de ouro num palete (o superfaturamento a vista)."""
    box(root, tag + '_palete', (0.3, 0.22, 0.05), (x, y, z + 0.025), m=P['wood_l'], bev=0.008)
    k = 0
    for lv in range(rows):
        n = rows - lv
        for i in range(n):
            for j in range(2):
                bx = x + (i - (n - 1) / 2) * 0.085
                by = y + (j - 0.5) * 0.09
                cyl(root, f'{tag}_barra{k}', 0.05, 0.04, (bx, by, z + 0.07 + lv * 0.04), r2=0.036, m=P['gold'], v=4, bev=0.004,
                    rot=(0, 0, math.pi / 4)).scale = (1.0, 0.62, 1.0)
                k += 1


def build_arM(P, root):
    plot(root, P, 'arM')
    lights = []
    fz = 0.76
    conc = P['conc']
    # tambor de concreto curvo (Brasilia) com a faixa listrada no alto e frisos de ouro
    lathe(root, 'arM_tambor', [(G, 0.8, 0.8), (G + 0.06, 0.74, 0.74), (G + 0.18, 0.7, 0.7), (fz - 0.1, 0.7, 0.7), (fz - 0.03, 0.72, 0.72), (fz, 0.72, 0.72)],
          conc, segs=56, lv=1, caps=False, solid=0.03)
    cyl(root, 'arM_tampo', 0.71, 0.05, (0, 0, fz - 0.02), m=P['grating'], v=56, bev=0.012)
    cyl(root, 'arM_faixa', 0.728, 0.06, (0, 0, fz - 0.08), m=P['hazard'], v=56, bev=0.004)
    torus(root, 'arM_frisoOuro', (0, 0, fz - 0.115), 0.725, 0.016, P['gold'], n=56, segs=6)
    torus(root, 'arM_frisoOuro2', (0, 0, G + 0.2), 0.715, 0.014, P['gold'], n=56, segs=6)
    # porta na cor da chapa, a placa da chapa em cima dela e janelas acesas na frente
    box(root, 'arM_porta', (0.2, 0.05, 0.3), (0.0, -0.7, G + 0.17), m=P['cA'], bev=0.02, front=True)
    sphere(root, 'arM_portaMacaneta', 0.018, (0.06, -0.73, G + 0.17), m=P['gold'], seg=8, front=True)
    placa_chapa(root, 'arM_placa', 0.24, 0.15, (0.0, -0.712, G + 0.465), th=0.03)
    for k, a in enumerate((math.radians(-125), math.radians(-55))):
        x, y = 0.705 * math.cos(a), 0.705 * math.sin(a)
        box(root, f'arM_janela{k}', (0.07, 0.03, 0.22), (x, y, G + 0.4), rot=(0, 0, a + math.pi / 2), m=P['window'], bev=0.01)
    rail(root, P, 'arM_guarda', [(0.7 * math.cos(math.radians(a)), 0.7 * math.sin(math.radians(a))) for a in range(-20, 201, 20)], fz)
    # duas chamines (a mais alta e o flare com a chama, a outra solta fumaca) e a coluna de destilacao
    for k, (x, y, r, h) in enumerate(((-0.42, 0.38, 0.095, 1.45), (-0.14, 0.55, 0.08, 1.18), (0.08, 0.6, 0.06, 0.9))):
        cyl(root, f'arM_chamine{k}', r, h, (x, y, fz + h / 2), r2=r * 0.86, m=P['tank'], v=24, bev=0.01)
        for j, t in enumerate((0.72, 0.86)):   # listras da chapa (V verde e amarela, R vermelhas sobre o branco)
            cyl(root, f'arM_chamineListra{k}{j}', r * (1 - 0.14 * t) + 0.006, 0.07, (x, y, fz + h * t), m=P['cA'] if j == 0 else P['cC'], v=24, bev=0.003)
        torus(root, f'arM_chamineBoca{k}', (x, y, fz + h), r * 0.86, 0.016, P['gold'], n=24, segs=6)
        torus(root, f'arM_chaminePe{k}', (x, y, fz + 0.04), r * 1.02, 0.018, P['gold'], n=24, segs=6)
    flame(root, P, 'arM_flare', (-0.42, 0.38, fz + 1.46), s=1.25)
    lights.append(((-0.42, 0.38, fz + 1.6), '#ff9a3a', 22.0, 1))
    smoke(root, P, 'arM_ch1', (-0.14, 0.55, fz + 1.2), n=4, s=1.0, rise=0.5, drift=(0.14, 0.04))
    smoke(root, P, 'arM_ch2', (0.08, 0.6, fz + 0.92), n=3, s=0.8, rise=0.4, drift=(0.12, 0.03))
    cx_, cy_ = 0.36, 0.44
    cyl(root, 'arM_coluna', 0.12, 1.1, (cx_, cy_, fz + 0.55), m=P['tank'], v=28, bev=0.012)
    lathe(root, 'arM_colunaTopo', [(0, 0.12, 0.12), (0.05, 0.1, 0.1), (0.09, 0.05, 0.05), (0.1, 0.0, 0.0)], P['gold'], segs=24, lv=1).location = (cx_, cy_, fz + 1.1)
    for j, zz in enumerate((0.3, 0.62, 0.94)):
        torus(root, f'arM_colunaAnel{j}', (cx_, cy_, fz + zz), 0.15, 0.012, P['cA'], n=24, segs=5)
    for sx in (-1, 1):
        tube(root, f'arM_escadaColuna{sx}', [(cx_ + sx * 0.04, cy_ - 0.135, fz), (cx_ + sx * 0.04, cy_ - 0.135, fz + 1.04)], 0.007, P['cC'], segs=5)
    for j in range(10):
        tube(root, f'arM_degrauColuna{j}', [(cx_ - 0.04, cy_ - 0.135, fz + 0.08 + j * 0.1), (cx_ + 0.04, cy_ - 0.135, fz + 0.08 + j * 0.1)], 0.006, P['cC'], segs=4)
    # canos de ouro ligando tudo (superfaturados)
    tube(root, 'arM_canoOuro1', [(-0.42, 0.29, fz + 0.3), (-0.42, 0.2, fz + 0.42), (0.0, 0.26, fz + 0.48), (0.22, 0.4, fz + 0.48)], 0.026, P['gold'], segs=10)
    tube(root, 'arM_canoOuro2', [(-0.12, 0.46, fz + 0.2), (0.0, 0.42, fz + 0.12), (0.22, 0.44, fz + 0.2)], 0.022, P['gold'], segs=10)
    for k, (x, y, z) in enumerate(((-0.42, 0.24, fz + 0.38), (0.22, 0.4, fz + 0.48), (0.0, 0.42, fz + 0.12))):
        sphere(root, f'arM_valvulaOuro{k}', 0.04, (x, y, z), m=P['gold'], seg=12)
    # no chao: esfera de gas, barris e as barras de ouro
    tank_s = (-0.74, -0.34, G + 0.24)
    sphere(root, 'arM_esfera', 0.17, tank_s, m=P['tank'], seg=24)
    torus(root, 'arM_esferaFaixa', tank_s, 0.172, 0.018, P['cA'], n=28, segs=5)
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        tube(root, f'arM_esferaPe{k}', [(tank_s[0] + 0.12 * math.cos(a), tank_s[1] + 0.12 * math.sin(a), G),
                                        (tank_s[0] + 0.1 * math.cos(a), tank_s[1] + 0.1 * math.sin(a), tank_s[2] - 0.05)], 0.014, P['steel_k'], segs=6)
    barrels(root, P, 'arM', [(0.74, -0.2, G), (0.82, 0.02, G), (-0.42, -0.74, G, 0.3)], r=0.075)
    gold_bars(root, P, 'arM_ouro', 0.52, -0.62)
    lights.append(((0.0, -0.72, G + 0.4), '#ffcf7a', 10.0, 0))
    slot = (0.0, -0.08, fz)
    return {'slots': [slot, (0.44, 0.16, fz)], 'lights': lights, 'points': {'top': top_of(slot, size=1.12, royal=True)}}


# ---------------------------------------------------------------- Sonda do Pre-Sal: torre de perfuracao e a broca que bate no poco
BEAM_Z = 2.06
BIT_Z = G + 0.03      # topo do oleo no poco: onde a broca bate (posto do conjunto arH)


def build_arS(P, root):
    plot(root, P, 'arS')
    lights = []
    conc = P['conc']
    # poco: anel de concreto com o oleo brilhando dentro e a mesa rotativa amarela
    lathe(root, 'arS_poco', [(G, 0.36, 0.36), (G + 0.05, 0.35, 0.35), (G + 0.1, 0.33, 0.33)], conc, segs=40, lv=1, caps=False, solid=0.06)
    torus(root, 'arS_pocoBorda', (0, 0, G + 0.1), 0.33, 0.03, P['cA'], n=40, segs=6)
    cyl(root, 'arS_oleo', 0.31, 0.02, (0, 0, BIT_Z - 0.01), m=P['oil'], v=40, bev=0.0)
    for k in range(10):
        a = TAU * k / 10
        if math.sin(a) < -0.2:
            box(root, f'arS_pocoFrente{k}', (0.2, 0.07, 0.1), (0.35 * math.cos(a), 0.35 * math.sin(a), G + 0.05), rot=(0, 0, a + math.pi / 2),
                m=conc, bev=0.025, front=True)
    torus(root, 'arS_pocoBordaFrente', (0, 0, G + 0.105), 0.335, 0.026, P['cA'], n=40, segs=6, front=True)
    # torre de perfuracao (trelica de 4 pernas): as pernas da frente passam na frente da broca
    corner = truss(root, P, 'arS_torre', (0.0, 0.0), (0.6, 0.46), (0.15, 0.12), G, BEAM_Z, levels=6, r_leg=0.042, r_br=0.016,
                   faces=('back', 'left', 'right'), front_legs=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = corner(sx, sy, 0)
            cyl(root, f'arS_sapata{sx}{sy}', 0.07, 0.05, (p.x, p.y, G + 0.025), m=P['cA'], v=16, bev=0.01, front=sy < 0)
    # bloco de coroamento (com o emblema da chapa na frente), roldanas e a bandeirola da chapa no alto
    box(root, 'arS_coroa', (0.44, 0.36, 0.1), (0, 0, BEAM_Z + 0.06), m=P['cA'], bev=0.02)
    placa_chapa(root, 'arS_coroaEmblema', 0.2, 0.095, (0.0, -0.18, BEAM_Z + 0.06), plate=False)
    box(root, 'arS_coroaBase', (0.4, 0.32, 0.03), (0, 0, BEAM_Z + 0.0), m=P['steel_k'], bev=0.006)
    for sx in (-1, 1):
        torus(root, f'arS_roldana{sx}', (sx * 0.12, -0.12, BEAM_Z + 0.06), 0.07, 0.018, P['steel_k'], axis='X', n=20, segs=6, front=True)
    tube(root, 'arS_mastro', [(0.16, 0.1, BEAM_Z + 0.1), (0.16, 0.1, BEAM_Z + 0.46)], 0.014, P['steel_k'], segs=6)
    pen = cloth_grid(root, 'arS_flamula', 0.28, 0.13, 10, 3, [P['flag']], thick=0.01,
                     shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.13 * (1 - u * 0.85))))
    pen.location = (0.17, 0.1, BEAM_Z + 0.4)
    register_cloth(pen, flag_wave(0.28, amp=0.05, cycles=1, waves=1.1))
    # plataforma do torrista (meio da torre, atras) e refletores
    zb = 1.3
    box(root, 'arS_plataforma', (0.36, 0.14, 0.03), (0, 0.27, zb), m=P['grating'], bev=0.006)
    rail(root, P, 'arS_plataformaGuarda', [(-0.18, 0.2), (-0.18, 0.34), (0.18, 0.34), (0.18, 0.2)], zb + 0.015, h=0.1, r=0.008)
    for k, (x, z) in enumerate(((-0.3, 0.9), (0.3, 0.9))):
        work_lamp(root, P, f'arS_refletor{k}', (x, 0.0, z), face=-math.pi / 2 + (0.5 if x < 0 else -0.5))
    lights.append(((-0.3, -0.05, 0.88), '#ffcf7a', 14.0, 1))
    lights.append(((0.3, -0.05, 0.88), '#ffcf7a', 14.0, 1))
    # guincho (drawworks) a direita: tambor que gira e a engrenagem amarela; o cabo sobe ate a coroa
    box(root, 'arS_guincho', (0.26, 0.3, 0.2), (0.62, 0.36, G + 0.1), m=P['cA'], bev=0.03)
    bandeirinha(root, 'arS_bandeira', (0.68, 0.44, G + 0.23), h=0.32, w=0.2, fh=0.13)
    box(root, 'arS_guinchoTampa', (0.27, 0.31, 0.03), (0.62, 0.36, G + 0.215), m=P['steel_k'], bev=0.01)
    gp = empty(root, 'arS_engrenagemPivo', loc=(0.62, 0.19, G + 0.18), rot=(math.pi / 2, 0, 0))
    kids(gp, torus(root, 'arS_engrenagemAro', (0, 0, 0), 0.12, 0.02, P['steel_k'], n=28, segs=6))
    for k in range(12):
        a = TAU * k / 12
        kids(gp, box(root, f'arS_dente{k}', (0.04, 0.03, 0.03), (0.14 * math.cos(a), 0.14 * math.sin(a), 0), rot=(0, 0, a), m=P['steel_k'], bev=0.006))
    for k in range(4):
        a = TAU * k / 4
        kids(gp, tube(root, f'arS_raio{k}', [(0, 0, 0), (0.11 * math.cos(a), 0.11 * math.sin(a), 0)], 0.014, P['cB'], segs=6))
    kids(gp, cyl(root, 'arS_engrenagemCubo', 0.04, 0.06, (0, 0, 0), m=P['cB'], v=12, bev=0.006))
    register_anim(gp, spin('Z', sym=12, turns=1))
    tube(root, 'arS_caboGuincho', [(0.56, 0.3, G + 0.24), (0.1, 0.0, BEAM_Z - 0.02)], 0.008, P['steel_k'], segs=5)
    # barril pendurado no braco da esquerda (balanca)
    tube(root, 'arS_bracoBarril', [(-0.15, 0.0, BEAM_Z - 0.04), (-0.48, 0.0, BEAM_Z + 0.04)], 0.022, P['steel_k'], segs=8)
    cw = empty(root, 'arS_pendPivo', loc=(-0.46, 0.0, BEAM_Z + 0.02))
    kids(cw, tube(root, 'arS_corrente', [(0, 0, 0), (0, 0, -0.5)], 0.009, P['steel_k'], segs=5))
    oil_barrel(root, P, 'arS_barrilPend', (0, 0, -0.6), r=0.07, parent=cw)
    register_anim(cw, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.06 * math.sin(TAU * ph), 4, 'X')))
    # tubos de perfuracao no cavalete, atras, e o painel de comando na frente do sondador
    for sx in (-1, 1):
        box(root, f'arS_cavalete{sx}', (0.05, 0.22, 0.12), (sx * 0.34 - 0.2, 0.66, G + 0.06), m=P['steel_k'], bev=0.01)
    for k in range(5):
        x0, z0 = -0.62, G + 0.15 + (0.045 if k in (1, 3) else 0)
        y0 = 0.58 + 0.04 * k if k not in (1, 3) else 0.6 + 0.04 * (k - 0.5)
        tube(root, f'arS_tuboPerf{k}', [(x0, y0, z0), (0.22, y0, z0)], 0.024, P['pipe'], segs=10)
    box(root, 'arS_painel', (0.12, 0.08, 0.2), (-0.5, -0.5, G + 0.1), rot=(0, 0, 0.5), m=P['cA'], bev=0.015)
    box(root, 'arS_painelTela', (0.09, 0.01, 0.07), (-0.48, -0.54, G + 0.15), rot=(0, 0, 0.5), m=P['steel_k2'], bev=0.004)
    tube(root, 'arS_alavanca', [(-0.46, -0.48, G + 0.2), (-0.42, -0.46, G + 0.3)], 0.008, P['steel_k'], segs=5)
    sphere(root, 'arS_alavancaPomo', 0.02, (-0.42, -0.46, G + 0.3), m=P['red'], seg=8)
    barrels(root, P, 'arS', [(0.6, -0.5, G), (0.74, -0.34, G)], r=0.065)
    oil_puddle(root, P, 'arS_poca', 0.66, -0.56, 0.16, 0.1)
    return {'slots': [(0.0, 0.0, BIT_Z), (-0.24, -0.64, G)], 'lights': lights, 'points': {'top': (0.0, 0.0, 1.1)}}


def build_hammer(P, root):
    """Coluna de perfuracao (broca tricone de ouro, comando listrado, tubo de aco e o moitao amarelo) pendurada no cabo."""
    tag = root['set']
    piv = empty(root, tag + '_piv', loc=(0, 0, 0))
    with grupo(root, tag + '_coluna', parent=piv):
        for k in range(3):
            a = TAU * k / 3 + 0.3
            cyl(root, f'{tag}_cone{k}', 0.045, 0.08, (0.04 * math.cos(a), 0.04 * math.sin(a), 0.045), r2=0.012, m=P['gold'],
                v=12, bev=0.006, rot=(math.pi + 0.35 * math.sin(a), 0.35 * -math.cos(a), 0))
        cyl(root, tag + '_corpoBroca', 0.085, 0.07, (0, 0, 0.1), r2=0.07, m=P['steel_k'], v=18, bev=0.012)
        cyl(root, tag + '_comando', 0.065, 0.28, (0, 0, 0.28), m=P['hazard'], v=18, bev=0.01)
        cyl(root, tag + '_tubo', 0.04, 0.22, (0, 0, 0.52), m=P['pipe'], v=14, bev=0.006)
        torus(root, tag + '_luva', (0, 0, 0.43), 0.05, 0.012, P['steel_k'], n=16, segs=5)
        box(root, tag + '_moitao', (0.16, 0.12, 0.14), (0, 0, 0.7), m=P['cA'], bev=0.03)
        cyl(root, tag + '_gancho', 0.025, 0.06, (0, 0, 0.61), m=P['steel_k'], v=10, bev=0.004)
        torus(root, tag + '_argola', (0, 0, 0.8), 0.045, 0.014, P['steel_k'], axis='X', n=14, segs=5)
    ch = ensure_mesh(root, tag + '_cabo', P['steel_k'])
    ch['set'] = root['set']
    return {'piv': piv, 'chain': ch, 'top': BEAM_Z - BIT_Z}


HAMMER_N = 8


def pose_hammer(parts, f):
    """slam: sobe (0..4), cai (5) e bate (6), quica (7). idle = alto, balancando."""
    hz = [0.78, 0.86, 0.94, 1.0, 1.02, 0.5, 0.0, 0.04][f] if f is not None else 0.9
    parts['piv'].location = (0, 0, hz)
    set_mesh_tube(parts['chain'], [(0, 0, hz + 0.82), (0, 0, max(hz + 0.86, parts['top']))], 0.012, segs=6)


# ---------------------------------------------------------------- petroleiros (tripulacao)
def wrench(root, tag, P, gold=False):
    """Chave de grifo: cabo na cor da chapa e a boca (empunhadura em z = 0)."""
    m = P['gold'] if gold else P['pipe']
    return [tube(root, tag + '_cabo', [(0, 0, -0.16), (0, 0, 0.16)], 0.014, P['cA'] if not gold else m, segs=6),
            box(root, tag + '_boca', (0.05, 0.03, 0.075), (0.012, 0, 0.2), m=m, bev=0.008),
            box(root, tag + '_mandibula', (0.06, 0.028, 0.02), (0.03, 0, 0.245), m=m, bev=0.005)]


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


def petroleiro(P, root, tag, scarf=None):
    """Petroleiro da chapa: camisa da chapa de manga curta (V amarela da selecao com gola verde, R vermelha com a
    estrela branca), calca/bermuda da chapa (V azul, R jeans), luva de borracha e botina."""
    pr = build_person(P, root, tag, dict(tunic=P['camisa'], skirt_m=P['calca'], head='bald', belt=P['steel_k'], pants=P['calca'],
                                         bracer=P['skin'], boot_m=P['rubber'], glove=P['rubber'], scarf=scarf))
    peito_chapa(root, pr, tag, P)
    return pr


def build_gunner(P, root):
    tag = root['set']
    pr = petroleiro(P, root, tag)
    hard_hat(root, pr, tag, P['bone'], ridge=P['cB'])
    hold(pr, 'R', *wrench(root, tag + '_chave', P))
    return pr


def build_loader(P, root):
    tag = root['set']
    pr = petroleiro(P, root, tag)
    hard_hat(root, pr, tag, P['bone'], ridge=P['cB'])
    b = oil_barrel(root, P, tag + '_barril', (0, 0, 0.0), r=0.05)
    hold(pr, 'L', b)
    return pr


def build_master(P, root):
    """Diretor da refinaria: terno escuro, camisa clara, gravata da chapa e capacete de ouro (superfaturado), chave de
    grifo dourada; na lapela, a estrela (R) ou o broche amarelo (V)."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(tunic=P['suit'], vest=P['shirt'], head='bald', belt=P['steel_k'], buckle=P['gold'],
                                         pants=P['suit'], boot_m=P['rubber'], glove=P['skin'], bare_hands=True, sleeve=P['suit']))
    # gravata na cor da chapa sobre a camisa
    tie = tube(root, tag + '_gravata', [(0.095, 0, 0.45), (0.103, 0, 0.38), (0.1, 0, 0.32)], 0.012, P['cA'], segs=6,
               rfun=lambda t: 0.01 + 0.012 * t)
    tie.parent = pr['body']
    if CHAPA == 'R':
        estrela_peito(root, tag, pr['body'], (0.09, -0.05, 0.43), r=0.017, rot=(0, 0, math.pi / 2))
    else:
        kids(pr['body'], sphere(root, tag + '_broche', 0.013, (0.093, -0.05, 0.43), m=P['cB'], seg=10))
    hard_hat(root, pr, tag, P['gold'])
    hold(pr, 'R', *wrench(root, tag + '_chave', P, gold=True))
    return pr


def build_engineer(P, root):
    """Sondador: a turma da chapa com lenco (V verde, R branco) e o capacete branco de chefe com a crista da chapa."""
    tag = root['set']
    pr = petroleiro(P, root, tag, scarf=P['gola'])
    hard_hat(root, pr, tag, P['tank'], ridge=P['cA'])
    return pr


IDLE_N, FIRE_N = 12, 8


def gunner_state(mode, f):
    """fire: ergue a chave (0..2), bate na alavanca (3) e descansa (4..7)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.06, -0.13, 0.32 + 0.008 * s), grip_R=(0.3, 0.0, 1.0), hand_L=(0.04, 0.13, 0.27),
                    breathe=s, head_yaw=0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.1, ph=ph)
    k = [0.3, 0.7, 1.0, 0.9, 0.5, 0.3, 0.15, 0.05][f]
    back = [0, 0, 0, 0.6, 1.0, 0.7, 0.3, 0.1][f]
    return dict(hand_R=(0.08 + 0.14 * k, -0.1 + 0.04 * k, 0.32 + 0.06 * k), grip_R=(0.3 + 0.9 * k, 0, 1.0 - 0.6 * k),
                hand_L=(0.02 - 0.06 * back, 0.14, 0.3 + 0.12 * back), lean=0.18 * k - 0.16 * back, head_pitch=-0.1 + 0.1 * back,
                head_yaw=0.2 - 0.3 * back, ph=f / FIRE_N)


def loader_state(mode, f):
    """fire: depois do disparo, pega um barril (0..3) e poe na concha (4..7)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.1, 0.06, 0.3 + 0.006 * s), hand_R=(0.08, -0.1, 0.28), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph), head_pitch=-0.1, ph=ph)
    t = f / (FIRE_N - 1)
    up = math.sin(math.pi * t)
    return dict(hand_L=(0.08 + 0.12 * t, 0.06 - 0.06 * t, 0.26 + 0.28 * up), hand_R=(0.08 + 0.12 * t, -0.06, 0.26 + 0.26 * up),
                lean=0.15 * up, head_pitch=-0.2 * up, head_yaw=0.1, ph=t)


def engineer_state(mode, f):
    """fire: puxa a alavanca do guincho (0..3) e solta (4..7)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.18, -0.06, 0.36 + 0.01 * s), hand_L=(0.16, 0.06, 0.34 + 0.01 * s), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph), head_pitch=-0.15, ph=ph)
    k = math.sin(math.pi * min(1.0, f / 4))
    return dict(hand_R=(0.18 - 0.1 * k, -0.06, 0.36 - 0.14 * k), hand_L=(0.16 - 0.1 * k, 0.06, 0.34 - 0.14 * k), lean=-0.15 * k,
                head_pitch=-0.15 + 0.1 * k, head_yaw=0.1, ph=f / FIRE_N)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 3, 'fire'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('fire', FIRE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'fire'))]}


SPEC = {
    'show_crew': {'ar1': ['arT1', 'arG'], 'ar2': ['arT2', 'arG', 'arC'], 'ar3': ['arT3', 'arG', 'arC'], 'arM': ['arTM', 'arR'], 'arS': ['arH', 'arE']},
    'towers': [('ar1', 'Petrolao N1', build_ar1), ('ar2', 'Petrolao N2', build_ar2), ('ar3', 'Petrolao N3', build_ar3),
               ('arM', 'Refinaria Superfaturada', build_arM), ('arS', 'Sonda do Pre-Sal', build_arS)],
    'crews': [crew('arG', 'Petroleiro', build_gunner, gunner_state), crew('arC', 'Carregador de barril', build_loader, loader_state),
              crew('arR', 'Diretor da refinaria', build_master, gunner_state), crew('arE', 'Sondador', build_engineer, engineer_state)],
    'turrets': [gun_spec('arT1', 'Cavalete 1', size=0.95), gun_spec('arT2', 'Cavalete 2', size=1.05, ornate=1),
                gun_spec('arT3', 'Cavalete 3', size=1.12, ornate=2), gun_spec('arTM', 'Cavalete da refinaria', size=1.12, royal=True),
                {'key': 'arH', 'label': 'Coluna de perfuracao', 'build': build_hammer, 'boost': 1.0,
                 'pose0': lambda parts, P, root: pose_hammer(parts, None),
                 'modes': [('slam', HAMMER_N, lambda parts, P, root, f: pose_hammer(parts, f))]}],
}


if __name__ == '__main__':
    main(FAM, SPEC)
