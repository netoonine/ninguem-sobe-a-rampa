"""Central do Zap (Catavento, Ninguem Sobe a Rampa): niveis 1 a 3, Disparo em Massa e Corrente do Zap.
Celulares gigantes empilhados numa doca de concreto branco sobre o lote de Brasilia, antenas com luz que pisca e
baloes de mensagem na cor da chapa (sem texto) flutuando; o ventilador grande na frente da pilha e a torreta: mira o
alvo, as pas giram e sopram um balao (conceito: arte/conceitos/torres/zap.png).
Nomes de conjuntos, postos, pontos e modos sao os mesmos do Leque de Palha (js/sprites.js depende deles).
Cores da chapa (chapa.py): CHAPA=V (padrao) capinha amarela, tela verde, pas amarelas com selo azul, baloes verdes e
amarelos, turma de camisa amarela da selecao; CHAPA=R capinha branca, tela vermelha, pas vermelhas com estrela branca,
baloes vermelhos e brancos, turma de camiseta vermelha com estrela branca. Bandeirinha da chapa no lote. A geometria que
o jogo usa (tamanho, ancora, postos, pontos, quadros) e a mesma nas duas.

  Blender -b -P tools/blender/torre_catavento.py -- render arte/render/catavento [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_catavento.py -- render arte/render_r/catavento [conjuntos...]
  Blender -b -P tools/blender/torre_catavento.py -- still <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, hide_tree, G   # noqa: F811 - lote de concreto de Brasilia
from pecas_zcv import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, estrela, bandeirinha   # cores da chapa: CHAPA=V (padrao) ou CHAPA=R

FRONT = -math.pi / 2
FAM = 'catavento'

import lib as _lib
_orig_palette2 = palette2


# cores da chapa nesta torre (o resto sai de chapa.cor): capinha dos celulares, tela acesa, conversa na tela, pas do
# ventilador, borrao das pas, led e a luz que as telas jogam no lote (tambem vai como cor da lanterna no meta.json)
ZAP = {'V': dict(case='#f2c21b', screen='#2fbf62', screen_b='#3f78d8', ui_g='#ffe066', blade='#ffd21f', blur='#fff6c8', led='#ffe45a',
                 luz='#86eaa2', luz2='#fff09a', wind='#f4fbe8'),
       'R': dict(case='#f6f3f0', screen='#e5443f', screen_b='#ff7a66', ui_g='#ffd0c8', blade='#d6282b', blur='#ffe2dc', led='#fff2ee',
                 luz='#ff8f80', luz2='#ffd0c4', wind='#fff0ec')}[CHAPA]


def palette2():   # noqa: F811 - cores da chapa (V verde e amarelo, R vermelho e branco), celulares e concreto branco
    P = _orig_palette2()
    P['teal'] = cor('pri', rough=0.7, sheen=0.4)                     # faixas, ondas da antena, aros das cornetas
    P['stripes'] = mat('listra_zap_' + CHAPA, PAL['pri'], rough=0.8, var=0.0, bump=0.05, stripes=(3.6, PAL['claro'], PAL['pri']), sheen=0.4)
    P['phone'] = mat('celular_capinha_' + CHAPA, ZAP['case'], rough=0.34, metal=0.1, var=0.03, bump=0.02)   # capinha da chapa
    P['phone_l'] = mat('celular_prata', '#b4bbc3', rough=0.28, metal=0.5, var=0.03, bump=0.02)
    P['phone_k'] = mat('celular_preto', '#33373e', rough=0.35, metal=0.3, var=0.03, bump=0.02)
    P['phone_d'] = mat('celular_detalhe', '#1d2024', rough=0.3, var=0.0, bump=0.0)
    P['screen'] = glow_mat('tela_zap_' + CHAPA, ZAP['screen'], 0.45, 2.4, rough=0.18, var=0.0, bump=0.0)
    P['screen_b'] = glow_mat('tela_lado_' + CHAPA, ZAP['screen_b'], 0.3, 1.8, rough=0.18, var=0.0, bump=0.0)
    P['ui_w'] = mat('tela_balao_branco', '#f4fbf8', rough=0.4, var=0.0, bump=0.0)
    P['ui_g'] = mat('tela_balao_chapa_' + CHAPA, ZAP['ui_g'], rough=0.4, var=0.0, bump=0.0)
    P['plastic'] = mat('plastico_branco', '#f2f1ec', rough=0.42, var=0.02, bump=0.02)
    P['plastic_t'] = mat('plastico_chapa_' + CHAPA, PAL['pri'], rough=0.4, var=0.02, bump=0.02)
    P['blade'] = mat('pa_ventilador_' + CHAPA, ZAP['blade'], rough=0.35, var=0.03, bump=0.02)
    P['seal'] = mat('selo_ventilador_' + CHAPA, PAL['ter'] if CHAPA == 'V' else PAL['pri'], rough=0.35, var=0.02, bump=0.02)
    P['cage'] = mat('grade_ventilador', '#c3cad0', rough=0.3, metal=0.7, var=0.02, bump=0.01)
    P['cage_d'] = mat('aro_ventilador', '#5d6670', rough=0.3, metal=0.55, var=0.02, bump=0.01)
    P['blur'] = mat('borrao_pas_' + CHAPA, ZAP['blur'], rough=0.5, var=0.0, bump=0.0)
    P['led'] = glow_mat('led_zap_' + CHAPA, ZAP['led'], 2.2, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['led_r'] = glow_mat('led_vermelho', '#ff6a5a', 2.0, 10.0, rough=0.3, var=0.0, bump=0.0)
    P['chain'] = mat('corrente_aco', '#c7cdd2', rough=0.25, metal=0.85, var=0.03, bump=0.01)
    P['conc'] = concrete()
    P['_emblem'] = 'swirl'
    # borrao das pas girando: meio transparente (so aparece no disparo)
    bm_ = P['blur']
    bs = next(n for n in bm_.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bs.inputs['Alpha'].default_value = 0.45
    return P


_lib.palette2 = palette2
FAN_FACE = math.radians(-60)   # o ventilador sopra para a direita e para a camera: a grade e as pas aparecem (o jogo espelha)


# ---------------------------------------------------------------- celular, doca, antena
def phone(root, P, name, loc, w, h, d=0.075, yaw=0.0, tilt=0.0, frame=None, screen=None, ui=0, home=True, front=False):
    """Celular gigante em pe: loc = centro da base; largura em X, espessura em Y, tela para -Y (girado por yaw).
    ui = quantos baloes de conversa na tela (brancos e verdes alternados, sem texto)."""
    frame = frame or P['phone']
    screen = screen or P['screen']
    with grupo(root, name, loc=loc, rot=(tilt, 0, yaw)) as e:
        slab(root, name + '_corpo', w, h, d, frame, r=w * 0.17, loc=(0, 0, h / 2), bev=d * 0.32, front=front)
        mw, mt, mb = w * 0.075, h * 0.1, h * (0.13 if home else 0.06)
        sw, sh = w - 2 * mw, h - mt - mb
        yf = -d / 2
        slab(root, name + '_tela', sw, sh, 0.008, screen, r=w * 0.05, loc=(0, yf - 0.002, mb + sh / 2), bev=0.003, front=front)
        slab(root, name + '_falante', w * 0.22, h * 0.02, 0.006, P['phone_d'], r=h * 0.01, loc=(0, yf - 0.002, h - mt * 0.5), bev=0.001, front=front)
        sphere(root, name + '_camera', w * 0.032, (-w * 0.24, yf - 0.001, h - mt * 0.5), scale=(1, 0.4, 1), m=P['phone_d'], seg=10, front=front)
        if home:
            cyl(root, name + '_botao', w * 0.075, 0.008, (0, yf - 0.002, mb * 0.5), rot=(math.pi / 2, 0, 0), m=P['phone_d'], v=20, bev=0.002, front=front)
        for k, zz in enumerate((0.74, 0.64)):
            box(root, f'{name}_volume{k}', (0.014, d * 0.42, h * 0.07), (-w / 2 - 0.004, 0, h * zz), m=frame, bev=0.005, front=front)
        box(root, name + '_liga', (0.014, d * 0.42, h * 0.1), (w / 2 + 0.004, 0, h * 0.72), m=frame, bev=0.005, front=front)
        for k in range(ui):
            right = k % 2 == 1
            bw = sw * (0.56 if not right else 0.5) * (1.0 - 0.12 * (k % 3 == 2))
            bh = sh * 0.105
            zc = mb + sh - sh * 0.12 - k * sh * 0.17
            if zc < mb + bh:
                break
            xc = (sw / 2 - bw / 2 - sw * 0.07) * (1 if right else -1)
            slab(root, f'{name}_conversa{k}', bw, bh, 0.006, P['ui_g'] if right else P['ui_w'], r=bh * 0.45, loc=(xc, yf - 0.008, zc), bev=0.002, front=front)
    return e


def dock(root, P, tag, cx, cy, w, d, h=0.08, z0=G):
    """Doca de carregar de concreto branco com faixa verde e luzinha (a base da pilha de celulares)."""
    slab(root, tag, w, d, h, P['conc'], r=min(w, d) * 0.3, loc=(cx, cy, z0 + h / 2), rot=(math.pi / 2, 0, 0), bev=0.025)
    slab(root, tag + '_faixa', w * 0.96, d * 0.96, 0.018, P['teal'], r=min(w, d) * 0.3, loc=(cx, cy, z0 + h * 0.62), rot=(math.pi / 2, 0, 0), bev=0.006)
    return z0 + h


def antenna(root, P, tag, base, h, ph0=0.0, arcs=True, red=False):
    """Antena de celular: haste de aco, bolinha que pisca (anim) e as ondinhas de sinal que pulsam (anim)."""
    x, y, z = base
    cyl(root, tag + '_pe', 0.03, 0.03, (x, y, z + 0.015), m=P['phone_k'], v=14, bev=0.006)
    tube(root, tag + '_haste', [(x, y, z), (x, y, z + h)], 0.011, P['cage'], segs=8)
    cyl(root, tag + '_bocal', 0.018, 0.02, (x, y, z + h), m=P['phone_k'], v=12, bev=0.004)
    led = empty(root, tag + '_led', loc=(x, y, z + h + 0.03))
    kids(led, sphere(root, tag + '_luz', 0.032, (0, 0, 0), m=P['led_r'] if red else P['led'], seg=14))
    pulse_anim(led, lo=0.68, hi=1.3, on=(0.0, 0.32), ph0=ph0)
    if arcs:
        wv = empty(root, tag + '_sinal', loc=(x, y, z + h + 0.02))
        for side in (-1, 1):
            for k, r in enumerate((0.075, 0.125)):
                a0 = -0.85 if side > 0 else math.pi - 0.85
                pts = [(r * math.cos(a0 + 1.7 * t / 10), 0, r * math.sin(a0 + 1.7 * t / 10)) for t in range(11)]
                kids(wv, tube(root, f'{tag}_onda{side}{k}', pts, 0.011 - 0.002 * k, P['teal'], segs=6))
        def breathe(o, mb, ph, p0=ph0):
            k = 0.86 + 0.2 * (0.5 + 0.5 * math.sin(TAU * (ph + p0)))
            o.matrix_basis = mb @ Matrix.Diagonal((k, k, k, 1))
        register_anim(wv, breathe)
    return led


def power_strip(root, P, tag, x, y, rz=0.0, z0=G):
    """Filtro de linha com os carregadores ligados (a 'central' de verdade)."""
    with grupo(root, tag, loc=(x, y, z0), rot=(0, 0, rz)):
        slab(root, tag + '_caixa', 0.3, 0.1, 0.04, P['plastic'], r=0.03, loc=(0, 0, 0.02), rot=(math.pi / 2, 0, 0), bev=0.012)
        sphere(root, tag + '_led', 0.01, (0.12, -0.04, 0.04), m=P['led_r'], seg=8)
        for k in range(3):
            box(root, f'{tag}_plugue{k}', (0.05, 0.05, 0.04), (-0.09 + 0.08 * k, 0, 0.055), m=P['phone_k'] if k % 2 else P['plastic'], bev=0.01)
    return (x, y, z0 + 0.06)


def cable(root, P, tag, pts, m=None):
    tube(root, tag, pts, 0.01, m or P['plastic'], segs=6)


def router(root, P, tag, x, y, rz=0.0, z0=G):
    """Roteador de wifi branco com duas antenas e luzinhas verdes."""
    with grupo(root, tag, loc=(x, y, z0), rot=(0, 0, rz)):
        slab(root, tag + '_caixa', 0.26, 0.16, 0.06, P['plastic'], r=0.05, loc=(0, 0, 0.03), rot=(math.pi / 2, 0, 0), bev=0.02)
        for k in range(4):
            sphere(root, f'{tag}_luz{k}', 0.008, (-0.07 + 0.04 * k, -0.081, 0.035), m=P['led'], seg=8)
        for sx in (-1, 1):
            tube(root, f'{tag}_antena{sx}', [(sx * 0.1, 0.05, 0.05), (sx * 0.13, 0.06, 0.24)], 0.012, P['phone_k'], segs=8)


def bubbles(root, tag, spots, s=1.15):
    """Baloes soltos flutuando em volta da pilha (cada um no seu ritmo)."""
    for k, (x, y, z, tl, light) in enumerate(spots):
        e = chat_bubble(root, f'{tag}_balao{k}', (x, y, z), s=s, rot=(0, -0.12 * tl, 0), light=light, tail=tl)
        float_anim(e, amp=0.028, ph0=0.27 * k, sway=0.1)


def dish(root, P, tag, loc, r=0.13):
    """Antena parabolica que gira devagar (anim) em cima do celular mais alto."""
    x, y, z = loc
    cyl(root, tag + '_pe', 0.035, 0.08, (x, y, z + 0.04), m=P['phone_k'], v=14, bev=0.008)
    piv = empty(root, tag + '_giro', loc=(x, y, z + 0.08))
    kids(piv, tube(root, tag + '_braco', [(0, 0, 0), (0, 0, 0.08)], 0.016, P['phone_k'], segs=8))
    with grupo(root, tag + '_prato', loc=(0, 0, 0.13), rot=(0, math.radians(-60), 0), parent=piv):
        lathe(root, tag + '_concha', [(0.0, 0.0, 0.0), (0.012, r * 0.5, r * 0.5), (0.04, r * 0.85, r * 0.85), (0.06, r, r)], P['plastic'], segs=24, lv=1,
              caps=False, solid=0.012)
        torus(root, tag + '_borda', (0, 0, 0.06), r, 0.01, P['teal'], n=28, segs=5)
        for k in range(3):
            a = TAU * k / 3
            tube(root, f'{tag}_vareta{k}', [(r * 0.8 * math.cos(a), r * 0.8 * math.sin(a), 0.05), (0, 0, 0.16)], 0.005, P['cage'], segs=4)
        sphere(root, tag + '_receptor', 0.022, (0, 0, 0.16), m=P['led'], seg=10)
    register_anim(piv, spin('Z', sym=1, turns=1))
    return piv


def flag_lot(root, tag, x, y, h=0.34):
    """Bandeirinha da chapa espetada no lote, atras e a esquerda (nada da frente cobre; nao mexe no enquadramento)."""
    m = bandeirinha(root, tag + '_bandeirinha', (x, y, G), h=h)
    m.scale = (-1, 1, 1)   # espelhada: o pano vai para a esquerda e a face com o emblema inteiro continua virada para a camera
    return m


# ---------------------------------------------------------------- ventilador (torreta: espelha, gira e sopra)
def build_fan(P, root, size=1.0, chain=False):
    """Ventilador de pe: base redonda, haste, motor atras e a grade de aco com as pas verde-agua. O eixo das pas e o
    X local do grupo 'incl' (aponta para o alvo). chain: o grande, com a corrente no pescoco e o funil de baloes."""
    tag = root['set']
    s = size
    R = 0.3 * s
    H = 0.34 * s
    piv = empty(root, tag + '_giro', rot=(0, 0, FAN_FACE))
    kids(piv, cyl(root, tag + '_base', 0.15 * s, 0.04 * s, (0, 0, 0.02 * s), r2=0.13 * s, m=P['plastic_t'], v=28, bev=0.012),
         torus(root, tag + '_baseAro', (0, 0, 0.03 * s), 0.13 * s, 0.012 * s, P['cage_d'], n=28, segs=5),
         tube(root, tag + '_haste', [(0, 0, 0.04 * s), (0, 0, H - 0.08 * s)], 0.022 * s, P['cage'], segs=10),
         cyl(root, tag + '_anel', 0.034 * s, 0.05 * s, (0, 0, H * 0.45), m=P['plastic'], v=16, bev=0.008))
    rec = empty(root, tag + '_recuo', loc=(0, 0, H), parent=piv)
    tilt = empty(root, tag + '_incl', parent=rec, rot=(0, math.radians(-6), 0))
    # garfo e motor (atras da grade)
    kids(rec, cyl(root, tag + '_junta', 0.036 * s, 0.06 * s, (-0.05 * s, 0, -0.05 * s), m=P['plastic'], v=16, bev=0.01))
    mot = lathe(root, tag + '_motor', [(-0.17 * s, 0.0, 0.0), (-0.165 * s, 0.05 * s, 0.05 * s), (-0.12 * s, 0.085 * s, 0.085 * s), (-0.05 * s, 0.08 * s, 0.08 * s),
                                       (-0.035 * s, 0.05 * s, 0.05 * s)], P['plastic'], segs=24, lv=1, caps=True)
    mot.rotation_euler = (0, math.pi / 2, 0)
    mot.location = (0, 0, 0)
    kids(tilt, mot)
    kids(tilt, torus(root, tag + '_motorFaixa', (0, 0, 0), 0.086 * s, 0.01 * s, P['teal'], axis='X', n=24, segs=5))
    bpy.data.objects[tag + '_motorFaixa'].location = (-0.1 * s, 0, 0)
    # grade: aro, aneis da frente e de tras e raios curvos
    kids(tilt, torus(root, tag + '_aro', (0, 0, 0), R, 0.028 * s, P['cage_d'], axis='X', n=40, segs=8))
    for k, (x, rr) in enumerate(((0.05 * s, 0.33), (0.035 * s, 0.66), (-0.035 * s, 0.6))):
        kids(tilt, torus(root, f'{tag}_anelGrade{k}', (x, 0, 0), R * rr, 0.006 * s, P['cage'], axis='X', n=28, segs=4))
    for k in range(14):
        a = TAU * k / 14
        c, sn = math.cos(a), math.sin(a)
        kids(tilt, tube(root, f'{tag}_raio{k}', [(0.06 * s, 0.05 * R * c, 0.05 * R * sn), (0.045 * s, 0.5 * R * c, 0.5 * R * sn), (0.0, R * c, R * sn)],
                        0.005 * s, P['cage'], segs=4))
        kids(tilt, tube(root, f'{tag}_raioT{k}', [(-0.045 * s, 0.4 * R * c, 0.4 * R * sn), (0.0, R * c, R * sn)], 0.005 * s, P['cage'], segs=4))
    kids(tilt, sphere(root, tag + '_selo', 0.05 * s, (0.066 * s, 0, 0), scale=(0.45, 1, 1), m=P['seal'], seg=18))
    if CHAPA == 'R':
        # estrela branca no selo da grade (V: o selo azul no meio das pas amarelas ja faz a bandeira)
        kids(tilt, estrela(root, tag + '_seloEstrela', 0.036 * s, 0.008 * s, loc=(0.086 * s, 0, 0), rot=(0, 0, math.pi / 2)))
    # pas (giram em torno do X local)
    spin_e = empty(root, tag + '_pas', parent=tilt, rot=(0, math.pi / 2, 0))
    spin_mb = spin_e.matrix_basis.copy()
    kids(spin_e, sphere(root, tag + '_cubo', 0.045 * s, (0, 0, 0), scale=(1, 1, 0.8), m=P['plastic'], seg=16))
    for k in range(5):
        a = TAU * k / 5
        bl = sphere(root, f'{tag}_pa{k}', 0.5 * R, (0.5 * R * math.cos(a), 0.5 * R * math.sin(a), 0), scale=(0.84, 0.46, 0.06), m=P['blade'], seg=16)
        bl.rotation_euler = (0.42, 0, a)
        bl.parent = spin_e
    blur = cyl(root, tag + '_borrao', R * 0.92, 0.004, (0, 0, 0.01 * s), m=P['blur'], v=36, bev=0.0)
    blur.parent = spin_e
    # balao soprado (aparece no disparo)
    puff = chat_bubble(root, tag + '_sopro', (0, 0, 0), s=s * 1.25, tail=-1, parent=tilt)
    parts = {'piv': piv, 'rec': rec, 'tilt': tilt, 'spin': spin_e, 'spin_mb': spin_mb, 'blur': blur, 'puff': puff, 'R': R, 's': s}
    if chain:
        # corrente enrolada no pescoco e o funil de baloes em cima do motor
        for k in range(9):
            t = k / 8
            a = TAU * 1.4 * t
            lk = torus(root, f'{tag}_elo{k}', (0, 0, 0), 0.024 * s, 0.007 * s, P['chain'], axis='Y' if k % 2 else 'X', n=14, segs=5)
            lk.location = (0.04 * s * math.cos(a), 0.04 * s * math.sin(a), 0.08 * s + (H - 0.18 * s) * t)
            lk.scale = (1.0, 1.0, 1.5)
            lk.parent = piv
        fun = lathe(root, tag + '_funil', [(0.0, 0.04 * s, 0.04 * s), (0.08 * s, 0.07 * s, 0.07 * s), (0.16 * s, 0.13 * s, 0.13 * s)], P['plastic_t'], segs=24, lv=1,
                    caps=False, solid=0.01)
        fun.location = (-0.11 * s, 0, 0.07 * s)
        fun.parent = rec
        for k in range(3):
            a = TAU * k / 3 + 0.4
            b = chat_bubble(root, f'{tag}_funilBalao{k}', (-0.11 * s + 0.05 * s * math.cos(a), 0.05 * s * math.sin(a), 0.25 * s + 0.03 * k), s=s * 0.55,
                            rot=(0, 0.3 * (k - 1), 0.6 * k), light=k == 1, tail=0, parent=rec)
        parts['chain'] = True
    return parts


def fan_points(parts, tl):
    bpy.context.view_layer.update()
    m = parts['tilt'].matrix_world @ Vector((0.09 * parts['s'], 0, 0))
    return {'points': {'muzzle': project(m, tl)}}


FAN_N = 8


def pose_fan(parts, f):
    """Disparo em 8 quadros: o motor da o tranco, as pas giram (borrao) e o balao sai da grade e some."""
    s, R = parts['s'], parts['R']
    rec = [-0.035, -0.02, -0.01, -0.004, 0.0, 0.0, 0.0, 0.0][f] if f is not None else 0.0
    parts['rec'].location = (rec * s, 0, 0.34 * s)
    turn = [0.0, 0.9, 1.7, 2.4, 2.95, 3.35, 3.6, 3.7][f] if f is not None else 3.7
    parts['spin'].matrix_basis = parts['spin_mb'] @ Matrix.Rotation(TAU / 5 * turn, 4, 'Z')
    blur_on = f is not None and f <= 4
    hide_tree(parts['blur'], not blur_on)
    # balao: nasce pequeno na grade, cresce e se afasta; some nos dois ultimos quadros
    k = [0.25, 0.5, 0.72, 0.88, 1.0, 1.0, 0.0, 0.0][f] if f is not None else 0.0
    x = [0.12, 0.3, 0.5, 0.68, 0.84, 0.98, 1.0, 1.0][f] if f is not None else 0.0
    parts['puff'].location = (R * (0.45 + 1.9 * x), 0, R * 0.3 * x)
    parts['puff'].rotation_euler = (0, 0, -FAN_FACE * 0.6)
    parts['puff'].scale = (k, k, k) if k > 0 else (1e-4, 1e-4, 1e-4)
    hide_tree(parts['puff'], k <= 0)


FAN_IDLE_N = 10


def pose_fan_idle(parts, f):
    """Espera (laco de 10 quadros a 12 qps): as pas giram sem parar, sem borrao nem balao. Comeca onde o disparo termina
    (0,7 de passo) e anda 3 passos de pa (5 pas: um passo = 1/5 de volta), entao o ultimo quadro emenda no primeiro."""
    pose_fan(parts, None)
    turn = 0.7 + 3.0 * f / FAN_IDLE_N
    parts['spin'].matrix_basis = parts['spin_mb'] @ Matrix.Rotation(TAU / 5 * turn, 4, 'Z')


def fan_spec(key, label, **kw):
    return {'key': key, 'label': label, 'build': lambda P, root: build_fan(P, root, **kw), 'boost': CREW_BOOST, 'extra': fan_points,
            'pose0': lambda parts, P, root: pose_fan(parts, None),
            'modes': [('fire', FAN_N, lambda parts, P, root, f: pose_fan(parts, f)),
                      ('idle', FAN_IDLE_N, lambda parts, P, root, f: pose_fan_idle(parts, f))]}


def fan_top(slot, size):
    """Centro da grade do ventilador no posto (origem do sopro): para o ponto 'top' da torre."""
    return (slot[0], slot[1], slot[2] + (0.34 + 0.02) * size * CREW_BOOST)


# ---------------------------------------------------------------- nivel 1: dois celulares na doca
def build_cv1(P, root):
    plot(root, P, 'cv1')
    lights = []
    zd = dock(root, P, 'cv1_doca', 0.02, 0.0, 0.66, 0.34)
    phone(root, P, 'cv1_celTras', (0.1, 0.07, zd), 0.42, 0.86, frame=P['phone_l'], home=False)
    phone(root, P, 'cv1_celFrente', (-0.03, -0.05, zd), 0.44, 0.78, frame=P['phone'], ui=4)
    antenna(root, P, 'cv1_antena', (0.22, 0.07, zd + 0.86), 0.24)
    bubbles(root, 'cv1', [(-0.44, -0.12, 0.86, 1, False), (0.42, -0.2, 0.72, -1, True)])
    p = power_strip(root, P, 'cv1_filtro', 0.5, 0.3, rz=0.5)
    flag_lot(root, 'cv1', -0.48, 0.36)
    cable(root, P, 'cv1_cabo', [(0.3, 0.12, zd - 0.03), (0.42, 0.2, G + 0.02), (0.46, 0.27, G + 0.03)])
    lights.append(((-0.03, -0.2, zd + 0.42), ZAP['luz'], 10.0, 1))
    lights.append(((0.22, 0.04, zd + 1.12), ZAP['luz2'], 6.0, 1))
    slot = (-0.1, -0.44, G)
    return {'slots': [slot], 'lights': lights, 'anim_shadow': True, 'points': {'top': fan_top(slot, 0.62)}}


# ---------------------------------------------------------------- nivel 2: tres celulares, o do lado e o roteador
def build_cv2(P, root):
    plot(root, P, 'cv2')
    lights = []
    zd = dock(root, P, 'cv2_doca', 0.04, 0.02, 0.78, 0.4)
    phone(root, P, 'cv2_celTras2', (0.18, 0.15, zd), 0.42, 1.12, frame=P['phone_k'], home=False)
    phone(root, P, 'cv2_celTras', (0.08, 0.06, zd), 0.43, 1.04, frame=P['phone_l'], home=False)
    phone(root, P, 'cv2_celFrente', (-0.04, -0.06, zd), 0.45, 0.94, frame=P['phone'], ui=5)
    phone(root, P, 'cv2_celLado', (0.5, -0.06, G), 0.34, 0.72, yaw=math.radians(52), frame=P['phone'], screen=P['screen_b'], ui=3)
    antenna(root, P, 'cv2_antena1', (0.3, 0.15, zd + 1.12), 0.26)
    antenna(root, P, 'cv2_antena2', (-0.04, 0.06, zd + 1.04), 0.2, ph0=0.5, red=True)
    router(root, P, 'cv2_roteador', -0.56, 0.24, rz=-0.4)
    flag_lot(root, 'cv2', -0.44, 0.42)
    bubbles(root, 'cv2', [(-0.48, -0.14, 1.04, 1, False), (0.3, -0.3, 1.18, -1, True), (-0.56, -0.3, 0.58, 1, True)])
    lights.append(((-0.04, -0.22, zd + 0.5), ZAP['luz'], 12.0, 1))
    lights.append(((0.3, 0.12, zd + 1.4), ZAP['luz2'], 6.0, 1))
    slot = (-0.14, -0.46, G)
    return {'slots': [slot], 'lights': lights, 'anim_shadow': True, 'points': {'top': fan_top(slot, 0.74)}}


# ---------------------------------------------------------------- nivel 3: a central completa com a parabolica
def build_cv3(P, root):
    plot(root, P, 'cv3')
    lights = []
    zd = dock(root, P, 'cv3_doca', 0.04, 0.04, 0.86, 0.46, h=0.1)
    phone(root, P, 'cv3_celTras3', (0.24, 0.22, zd), 0.42, 1.36, frame=P['phone_k'], home=False)
    phone(root, P, 'cv3_celTras2', (0.15, 0.14, zd), 0.43, 1.28, frame=P['phone'], home=False)
    phone(root, P, 'cv3_celTras', (0.06, 0.05, zd), 0.44, 1.18, frame=P['phone_l'], home=False)
    phone(root, P, 'cv3_celFrente', (-0.05, -0.07, zd), 0.46, 1.06, frame=P['phone'], ui=6)
    phone(root, P, 'cv3_celLado', (0.52, -0.02, G), 0.36, 0.8, yaw=math.radians(52), frame=P['phone_l'], screen=P['screen_b'], ui=3)
    dish(root, P, 'cv3_parabolica', (0.24, 0.22, zd + 1.36))
    antenna(root, P, 'cv3_antena1', (0.06, 0.05, zd + 1.18), 0.26)
    antenna(root, P, 'cv3_antena2', (-0.15, -0.07, zd + 1.06), 0.2, ph0=0.5, red=True)
    router(root, P, 'cv3_roteador', -0.58, 0.26, rz=-0.4)
    flag_lot(root, 'cv3', -0.44, 0.42)
    bubbles(root, 'cv3', [(-0.5, -0.1, 1.2, 1, False), (0.46, -0.32, 1.12, -1, True), (-0.58, -0.32, 0.66, 1, True),
                          (0.02, -0.3, 1.56, -1, False)])
    p = power_strip(root, P, 'cv3_filtro', 0.56, 0.42, rz=0.6)
    lights.append(((-0.05, -0.24, zd + 0.55), ZAP['luz'], 14.0, 1))
    lights.append(((0.06, 0.02, zd + 1.46), ZAP['luz2'], 6.0, 1))
    slot = (-0.2, -0.48, G)
    return {'slots': [slot, (0.5, -0.58, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': fan_top(slot, 0.84)}}


# ---------------------------------------------------------------- Disparo em Massa: pilar de celulares, cornetas,
# ventiladores girando e o redemoinho de baloes no topo
def horn_speaker(root, P, tag, loc, yaw, pitch=0.25, s=1.0):
    """Corneta de carro de som (alto-falante de boca larga) apontando para fora."""
    with grupo(root, tag, loc=loc, rot=(0, -pitch, yaw)):
        h = lathe(root, tag + '_boca', [(0.0, 0.03 * s, 0.03 * s), (0.08 * s, 0.045 * s, 0.045 * s), (0.17 * s, 0.09 * s, 0.09 * s), (0.22 * s, 0.14 * s, 0.14 * s)],
                  P['plastic'], segs=24, lv=1, caps=False, solid=0.012)
        h.rotation_euler = (0, math.pi / 2, 0)
        torus(root, tag + '_aro', (0.22 * s, 0, 0), 0.14 * s, 0.014 * s, P['teal'], axis='X', n=28, segs=6)
        cyl(root, tag + '_fundo', 0.045 * s, 0.01, (0.05 * s, 0, 0), rot=(0, math.pi / 2, 0), m=P['teal'], v=14, bev=0.0)
        cyl(root, tag + '_driver', 0.05 * s, 0.07 * s, (-0.03 * s, 0, 0), rot=(0, math.pi / 2, 0), m=P['phone_k'], v=16, bev=0.01)


def wall_fan(root, P, tag, loc, yaw, R=0.15, ph0=0.0):
    """Ventilador de parede preso no pilar: grade e pas que giram sem parar (anim)."""
    with grupo(root, tag, loc=loc, rot=(0, 0, yaw)) as g:
        torus(root, tag + '_aro', (0.04, 0, 0), R, 0.014, P['cage'], axis='X', n=32, segs=6)
        for k in range(10):
            a = TAU * k / 10
            tube(root, f'{tag}_raio{k}', [(0.08, 0.0, 0.0), (0.06, 0.5 * R * math.cos(a), 0.5 * R * math.sin(a)), (0.04, R * math.cos(a), R * math.sin(a))],
                 0.004, P['cage'], segs=4)
        cyl(root, tag + '_motor', 0.06, 0.08, (-0.02, 0, 0), rot=(0, math.pi / 2, 0), m=P['plastic'], v=18, bev=0.012)
        tube(root, tag + '_suporte', [(-0.16, 0, -0.05), (-0.04, 0, -0.03)], 0.016, P['phone_k'], segs=8)
        sp = empty(root, tag + '_pas', loc=(0.05, 0, 0), rot=(0, math.pi / 2, 0))
        for k in range(4):
            a = TAU * k / 4
            bl = sphere(root, f'{tag}_pa{k}', 0.5 * R, (0.5 * R * math.cos(a), 0.5 * R * math.sin(a), 0), scale=(0.84, 0.44, 0.07), m=P['blade'], seg=14)
            bl.rotation_euler = (0.4, 0, a)
            bl.parent = sp
        kids(sp, sphere(root, tag + '_cubo', 0.03, (0, 0, 0), m=P['teal'], seg=12))
    register_anim(sp, spin('Z', sym=4, turns=-3))
    return g


def build_cvT(P, root):
    plot(root, P, 'cvT')
    lights = []
    # palanque redondo de concreto com faixa verde
    cyl(root, 'cvT_podio', 0.5, 0.1, (0, 0.06, G + 0.05), m=P['conc'], v=48, bev=0.03)
    torus(root, 'cvT_podioFaixa', (0, 0.06, G + 0.07), 0.5, 0.018, P['teal'], n=48, segs=5)
    zp = G + 0.1
    # pilar: quatro celulares de costas um para o outro, telas para fora (dois de frente para a camera)
    box(root, 'cvT_miolo', (0.3, 0.3, 1.16), (0, 0.06, zp + 0.58), rot=(0, 0, math.pi / 4), m=P['phone_k'], bev=0.03)
    for k, yaw in enumerate((-45, 45, 135, 225)):
        a = math.radians(yaw) - math.pi / 2
        c = (0.19 * math.cos(a), 0.06 + 0.19 * math.sin(a), zp)
        phone(root, P, f'cvT_cel{k}', c, 0.34, 1.16, d=0.07, yaw=math.radians(yaw), frame=P['phone'] if k % 2 else P['phone_l'], ui=4 if k < 2 else 0,
              home=k < 2)
    ztop = zp + 1.16
    # laje do topo com guarda-corpo verde
    cyl(root, 'cvT_laje', 0.42, 0.07, (0, 0.06, ztop + 0.035), m=P['conc'], v=40, bev=0.02)
    torus(root, 'cvT_lajeFaixa', (0, 0.06, ztop + 0.02), 0.42, 0.014, cor('sec' if CHAPA == 'V' else 'pri', rough=0.7, sheen=0.4), n=40, segs=5)   # filete da laje (R: vermelho, o branco some no concreto)
    torus(root, 'cvT_corrimao', (0, 0.06, ztop + 0.2), 0.4, 0.014, P['cage'], n=40, segs=5)
    for k in range(12):
        a = TAU * k / 12
        tube(root, f'cvT_balaustre{k}', [(0.4 * math.cos(a), 0.06 + 0.4 * math.sin(a), ztop + 0.07), (0.4 * math.cos(a), 0.06 + 0.4 * math.sin(a), ztop + 0.2)],
             0.009, P['cage'], segs=4, front=math.sin(a) < -0.4)
    # cornetas nas quatro direcoes (as da frente apontam para os lados da camera)
    for k, yaw in enumerate((-30, -150, 60, 120)):
        a = math.radians(yaw)
        horn_speaker(root, P, f'cvT_corneta{k}', (0.24 * math.cos(a), 0.06 + 0.24 * math.sin(a), ztop + 0.3), a, pitch=0.35, s=0.72)
    tube(root, 'cvT_mastro', [(0, 0.06, ztop + 0.07), (0, 0.06, ztop + 0.36)], 0.03, P['phone_k'], segs=10)
    flag_lot(root, 'cvT', -0.55, 0.38)
    # ventiladores de parede nos dois lados do pilar
    for k, sx in enumerate((-1, 1)):
        wall_fan(root, P, f'cvT_ventilador{k}', (sx * 0.34, -0.04, zp + 0.62), math.radians(-90 + sx * 62), R=0.15)
    # redemoinho de baloes (tres bracos de espiral, gira)
    zc = ztop + 0.4
    tw = empty(root, 'cvT_redemoinho', loc=(0, 0.06, zc))
    wind = mat('vento_zap_' + CHAPA, ZAP['wind'], rough=0.6, var=0.0, bump=0.0, emit=0.3)
    for j in range(3):
        pts = []
        for k in range(30):
            t = k / 29
            a = TAU * 1.6 * t + j * TAU / 3
            r = 0.06 + 0.26 * t
            pts.append((r * math.cos(a), r * math.sin(a), 0.72 * t))
        kids(tw, tube(root, f'cvT_vento{j}', pts, 0.012, wind, segs=5, rfun=lambda t: 0.004 + 0.011 * t))
        for i, t in enumerate((0.3, 0.62, 0.92)):
            a = TAU * 1.6 * t + j * TAU / 3
            r = 0.06 + 0.26 * t
            b = chat_bubble(root, f'cvT_balao{j}{i}', (r * math.cos(a), r * math.sin(a), 0.72 * t + 0.05), s=0.8 + 0.3 * t,
                            rot=(0, 0.25 * (i - 1), a + math.pi / 2), light=(i + j) % 2 == 1, tail=1 if i % 2 else -1, both=True, d=0.09)
            b.parent = tw
            b.location = (r * math.cos(a), r * math.sin(a), 0.72 * t + 0.05)
    register_anim(tw, spin('Z', sym=3, turns=-1))
    lights.append(((0.0, -0.2, zp + 0.6), ZAP['luz'], 12.0, 1))
    lights.append(((0.0, 0.06, zc + 0.3), ZAP['luz2'], 8.0, 1))
    return {'slots': [(0.56, -0.6, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (0.0, 0.06, zc + 0.34)}}


# ---------------------------------------------------------------- Corrente do Zap: o celular gigante acorrentado e a
# fila de baloes presos um no outro por elos
def chain_link(root, P, name, p, d, k, s=1.0):
    """Elo de corrente no ponto p, ao longo da direcao d; elos alternam o plano (k par/impar)."""
    lk = torus(root, name, (0, 0, 0), 0.045 * s, 0.013 * s, P['chain'], axis='Z', n=16, segs=6)
    q = Vector(d).to_track_quat('X', 'Z')
    lk.matrix_basis = Matrix.Translation(Vector(p)) @ q.to_matrix().to_4x4() @ Matrix.Rotation((math.pi / 2) * (k % 2) + 0.3, 4, 'X') \
        @ Matrix.Diagonal((1.55, 1.0, 1.0, 1.0))
    return lk


def chain_path(root, P, tag, pts, step=0.1, s=1.0, front=False):
    pts = [Vector(p) for p in pts]
    L = [0.0]
    for a, b in zip(pts[:-1], pts[1:]):
        L.append(L[-1] + (b - a).length)
    n = max(2, int(L[-1] / step))
    out = []
    for k in range(n + 1):
        t = L[-1] * k / n
        i = max(0, min(len(pts) - 2, next((j for j in range(len(L) - 1) if L[j + 1] >= t), len(pts) - 2)))
        u = (t - L[i]) / max(1e-6, L[i + 1] - L[i])
        p = pts[i].lerp(pts[i + 1], u)
        o = chain_link(root, P, f'{tag}{k}', p, pts[i + 1] - pts[i], k, s)
        if front:
            o['front'] = 1
        out.append(o)
    return out


def build_cvS(P, root):
    plot(root, P, 'cvS')
    lights = []
    zd = dock(root, P, 'cvS_doca', 0.06, 0.16, 0.86, 0.36, h=0.1)
    tilt = -0.12
    phone(root, P, 'cvS_celular', (0.06, 0.18, zd), 0.66, 1.36, d=0.1, tilt=tilt, frame=P['phone'], ui=6)
    # corrente: desce do canto de cima, cruza a frente do celular e cai no chao, onde se amontoa
    ct = math.cos(tilt)
    zf = lambda z: zd + z * ct
    yf = lambda z: 0.18 - 0.07 - math.sin(tilt) * z
    chain_path(root, P, 'cvS_elo', [(-0.3, yf(1.2), zf(1.2)), (-0.05, yf(0.95) - 0.02, zf(0.95)), (0.2, yf(0.62) - 0.03, zf(0.62)),
                                    (0.36, yf(0.3) - 0.04, zf(0.3)), (0.44, -0.08, zd + 0.02), (0.52, -0.2, G + 0.04)], step=0.085)
    for k in range(5):
        a = TAU * k / 5
        chain_link(root, P, f'cvS_montinho{k}', (0.58 + 0.07 * math.cos(a), -0.26 + 0.05 * math.sin(a), G + 0.03 + 0.02 * (k % 2)), (math.cos(a + 1.6), math.sin(a + 1.6), 0), k)
    # cadeado aberto pendurado na ponta de cima
    flag_lot(root, 'cvS', -0.55, 0.3)
    cad = mat('cadeado_ouro', '#e2b13f', rough=0.3, metal=0.6, var=0.03, bump=0.02)
    slab(root, 'cvS_cadeado', 0.12, 0.11, 0.05, cad, r=0.03, loc=(-0.34, yf(1.12) - 0.04, zf(1.12) - 0.12), bev=0.012)
    tube(root, 'cvS_cadeadoAlca', [(-0.38, yf(1.12) - 0.04, zf(1.12) - 0.07), (-0.38, yf(1.12) - 0.04, zf(1.12) - 0.0), (-0.34, yf(1.12) - 0.04, zf(1.12) + 0.04),
                                   (-0.3, yf(1.12) - 0.04, zf(1.12) + 0.0)], 0.012, P['chain'], segs=6)
    # fila de baloes, um preso no outro, saindo do topo do celular e subindo em arco (cada um no seu tempo: onda)
    prev = None
    for k in range(5):
        t = k / 4
        x = 0.26 + 0.34 * math.sin(t * 1.4)
        z = zf(1.36) + 0.06 + 0.36 * t
        y = yf(1.36) - 0.1 - 0.1 * t
        e = chat_bubble(root, f'cvS_fila{k}', (x, y, z), s=1.05 - 0.07 * k, light=k % 2 == 1, tail=-1 if k % 2 else 1, rot=(0, 0.15 * (k - 2), 0))
        float_anim(e, amp=0.022, ph0=-0.16 * k, sway=0.06)
        if prev:
            mid = (Vector(prev) + Vector((x, y, z))) / 2
            lk = chain_link(root, P, f'cvS_filaElo{k}', mid, Vector((x, y, z)) - Vector(prev), k, s=0.7)
            float_anim(lk, amp=0.022, ph0=-0.16 * (k - 0.5), sway=0.0)
        prev = (x, y, z)
    lights.append(((0.06, -0.06, zd + 0.7), ZAP['luz'], 14.0, 1))
    slot = (-0.26, -0.46, G)
    return {'slots': [slot, (0.36, -0.62, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': fan_top(slot, 1.0)}}


# ---------------------------------------------------------------- tripulacao do zap
def hand_phone(root, P, tag, screen=None):
    """Celular na mao (ao longo do Z local, empunhadura embaixo), tela dos dois lados."""
    scr = screen or P['screen']
    return [box(root, tag + '_celMao', (0.014, 0.062, 0.12), (0, 0, 0.05), m=P['phone_k'], bev=0.006),
            box(root, tag + '_celMaoTela', (0.018, 0.05, 0.096), (0, 0, 0.052), m=scr, bev=0.003)]


def cap_bill(root, pr, tag, m):
    """Aba do bone (no pivo da cabeca, para a frente)."""
    o = cyl(root, tag + '_aba', 0.06, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.18, 0)
    return o


def build_militante(P, root):
    """Militante do zap: camisa da chapa (V amarela da selecao com gola verde, R vermelha com estrela branca), calca da
    chapa, tenis branco, bone da chapa e fone de telemarketing, celular na mao."""
    tag = root['set']
    shirt = cor('camisa')
    pants = cor('calca')
    pr = build_person(P, root, tag, dict(tunic=shirt, head='cap', head_m=cor('bone'),
                                         belt=mat('cinto_zap', '#3a2a22', rough=0.6, var=0, bump=0.04), skirt_m=pants, pants=pants,
                                         boot_m=mat('tenis_branco', '#f4f4f0', rough=0.5, var=0, bump=0.02), boot_cuff=pants, sleeve=shirt, bare_hands=True))
    cap_bill(root, pr, tag, cor('bone'))
    marca_peito(root, pr, tag)
    headset(root, pr, tag, P['phone_k'])
    badge_lanyard(root, pr, tag, cor('gola'))
    hold(pr, 'R', *hand_phone(root, P, tag))
    return pr


def build_disparador(P, root):
    """Disparador: moletom da chapa (V verde, R vermelho com estrela branca), gorro (V amarelo, R branco), oculos escuros
    e um celular em cada mao."""
    tag = root['set']
    hood = cor('pri', rough=0.85, sheen=0.3)
    black = cloth_mat('calca_preta_zap', '#2c2f36', sheen=0.1)
    pr = build_person(P, root, tag, dict(tunic=hood, head='cap', head_m=cor('sec', rough=0.85, sheen=0.3), belt=None, skirt_m=black, pants=black,
                                         boot_m=mat('tenis_verde', '#f4f4f0', rough=0.5, var=0, bump=0.02), boot_cuff=black, sleeve=hood, bare_hands=True,
                                         hair_m=mat('cabelo_zap', '#2a1a10', rough=0.7, var=0.03, bump=0.25)))
    if CHAPA == 'R':
        marca_peito(root, pr, tag, collar=False)
    else:
        # cordao amarelo do capuz no peito do moletom verde
        for k, sy in enumerate((-1, 1)):
            o = tube(root, f'{tag}_cordaoCapuz{k}', [(0.06, sy * 0.022, 0.462), (0.082, sy * 0.02, 0.41), (0.086, sy * 0.022, 0.385)], 0.006, cor('sec'), segs=5)
            o.parent = pr['body']
    # capuz caido nas costas
    o = blob(root, tag + '_capuzCaido', 0.06, (-0.07, 0.0, 0.46), (0.7, 1.2, 0.7), cor('escuro', rough=0.85, sheen=0.3))
    o.parent = pr['body']
    glasses(root, pr, tag, mat('lente_escura_zap', '#141418', rough=0.15, var=0, bump=0), dark=True)
    hold(pr, 'R', *hand_phone(root, P, tag + 'R'))
    hold(pr, 'L', *hand_phone(root, P, tag + 'L', P['screen_b']))
    return pr


IDLE_N, ACT_N = 12, 8


def militante_state(mode, f):
    """idle: olha o celular na frente do peito; act: ergue o celular e 'encaminha' (aponta para a frente) e volta."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.16, -0.05, 0.38 + 0.008 * s), grip_R=(0.35, 0.3, 1.0), hand_L=(0.12, 0.06, 0.34), breathe=s,
                    head_yaw=-0.15 + 0.12 * math.sin(TAU * ph), head_pitch=0.3 + 0.04 * math.sin(TAU * ph * 2), ph=ph)
    k = math.sin(math.pi * min(1.0, f / 4))
    return dict(hand_R=(0.16 + 0.08 * k, -0.08, 0.38 + 0.2 * k), grip_R=(0.35 + 0.5 * k, 0.2, 1.0), hand_L=(0.16 + 0.12 * k, 0.1, 0.34 + 0.12 * k),
                lean=-0.08 * k, head_pitch=0.3 - 0.45 * k, head_yaw=0.05, ph=f / ACT_N)


def disparador_state(mode, f):
    """idle: digita nos dois celulares; act: ergue os dois de uma vez (disparo em massa)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        t = math.sin(TAU * 2 * ph)
        return dict(hand_R=(0.16, -0.08, 0.36 + 0.012 * t), grip_R=(0.3, 0.2, 1.0), hand_L=(0.16, 0.08, 0.36 - 0.012 * t), grip_L=(0.3, -0.2, 1.0),
                    breathe=s, head_pitch=0.3, head_yaw=0.1 * math.sin(TAU * ph), ph=ph)
    k = math.sin(math.pi * min(1.0, f / 4))
    return dict(hand_R=(0.14 + 0.06 * k, -0.14 - 0.04 * k, 0.36 + 0.24 * k), grip_R=(0.3, -0.3 * k, 1.0), hand_L=(0.14 + 0.06 * k, 0.14 + 0.04 * k, 0.36 + 0.24 * k),
                grip_L=(0.3, 0.3 * k, 1.0), lean=-0.06 * k, head_pitch=0.3 - 0.4 * k, ph=f / ACT_N)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'cv1': ['cvH1'], 'cv2': ['cvH2'], 'cv3': ['cvH3', 'cvM'], 'cvT': ['cvM'], 'cvS': ['cvHS', 'cvO']},
    'towers': [('cv1', 'Central do Zap N1', build_cv1), ('cv2', 'Central do Zap N2', build_cv2), ('cv3', 'Central do Zap N3', build_cv3),
               ('cvT', 'Disparo em Massa', build_cvT), ('cvS', 'Corrente do Zap', build_cvS)],
    'crews': [crew('cvM', 'Militante do zap', build_militante, militante_state), crew('cvO', 'Disparador', build_disparador, disparador_state)],
    'turrets': [fan_spec('cvH1', 'Ventilador N1', size=0.62), fan_spec('cvH2', 'Ventilador N2', size=0.74),
                fan_spec('cvH3', 'Ventilador N3', size=0.84), fan_spec('cvHS', 'Ventilador da Corrente', size=1.0, chain=True)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
