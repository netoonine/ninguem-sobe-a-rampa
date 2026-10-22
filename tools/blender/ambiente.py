"""Sprites vivos do cenario: as tamareiras que balancam na brisa (o fundo de cada fase guarda so a sombra delas),
a alavanca da comporta e a palicada que fecha o ramo inativo (Comportas de Qanat).

  Blender -b -P tools/blender/ambiente.py -- render arte/render/ambiente
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from cenario_props import palm, PALM_VARIANTS

FAM = 'ambiente'
LEVER_N = 9                    # quadros da alavanca, de -0.6 a +0.6 rad (o jogo escolhe pelo angulo)
GATE_DIRS = 8                  # palicada girada em passos de 22,5 graus (simetrica a cada meia volta)


def build_palm(v):
    def fn(P, root):
        pv = PALM_VARIANTS[v]
        palm(root, root['set'], P, s=1.0, seed=pv['seed'], lean=pv['lean'])
        return {}
    return fn


def sway(parts, P, root, f):
    apply_anim(f / ANIM_N)


def build_lever(P, root):
    tag = root['set']
    stone = mat('pedestal_comporta', '#b7a88e', rough=0.85, var=0.08, bump=0.3)
    box(root, tag + '_base', (0.62, 0.42, 0.12), (0, 0, 0.06), m=stone, bev=0.04)
    box(root, tag + '_bloco', (0.44, 0.3, 0.26), (0, 0, 0.25), m=stone, bev=0.05)
    gear = cyl(root, tag + '_roda', 0.15, 0.05, (0, -0.17, 0.27), m=P['bronze'], v=18, bev=0.01, rot=(math.pi / 2, 0, 0))
    for k in range(9):
        a = TAU * k / 9
        box(root, f'{tag}_dente{k}', (0.05, 0.05, 0.05), (0.17 * math.cos(a), -0.17, 0.27 + 0.17 * math.sin(a)), rot=(0, -a, 0), m=P['bronze'], bev=0.008)
    cyl(root, tag + '_eixo', 0.04, 0.06, (0, -0.2, 0.27), m=P['iron_d'], v=12, bev=0.008, rot=(math.pi / 2, 0, 0))
    piv = empty(root, tag + '_piv', (0, 0, 0.4))
    cyl(root, tag + '_mancal', 0.07, 0.3, (0, 0, 0.4), m=P['iron_d'], v=14, bev=0.01, rot=(math.pi / 2, 0, 0))
    h = tube(root, tag + '_cabo', [(0, 0, 0.0), (0, 0, 0.62)], 0.035, P['wood'], segs=8, rfun=lambda t: 0.038 - 0.01 * t)
    k = sphere(root, tag + '_pomo', 0.085, (0, 0, 0.66), m=P['red'], seg=16)
    kids(piv, h, k)
    h.location = (0, 0, 0)
    k.location = (0, 0, 0.66)
    return {'piv': piv}


def lever_pose(parts, P, root, f):
    ang = -0.6 + 1.2 * f / (LEVER_N - 1)
    parts['piv'].rotation_euler = (0, ang, 0)


def build_gate(P, root):
    tag = root['set']
    piv = empty(root, tag + '_giro', (0, 0, 0))
    wood = mat('estaca_palicada', '#a8743e', rough=0.8, var=0.12, bump=0.3)
    rope = P['rope']
    objs = []
    for k in range(-3, 4):
        x = k * 0.22
        hgt = 0.58 + 0.05 * math.cos(k * 1.7)
        objs.append(tube(root, f'{tag}_estaca{k}', [(x, 0, -0.04), (x, 0, hgt)], 0.055, wood, segs=8, rfun=lambda t: 0.058 - 0.008 * t))
        objs.append(cyl(root, f'{tag}_ponta{k}', 0.056, 0.12, (x, 0, hgt + 0.06), r2=0.0, m=wood, v=8, bev=0.0))
    for z in (0.2, 0.42):
        objs.append(tube(root, f'{tag}_trave{z}', [(-0.72, 0.06, z), (0.72, 0.06, z)], 0.03, P['wood'], segs=6))
        for k in range(-3, 4):
            objs.append(torus(root, f'{tag}_amarra{z}_{k}', (k * 0.22, 0.03, z), 0.06, 0.014, rope, axis='X', n=12, segs=5))
    kids(piv, *objs)
    return {'piv': piv}


def gate_pose(parts, P, root, f):
    parts['piv'].rotation_euler = (0, 0, math.pi * f / GATE_DIRS)


SPEC = {
    'crews': [
        {'key': 'palmA', 'label': 'Tamareira A', 'build': build_palm(0), 'boost': 0.8, 'shadow': False, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('balanca', ANIM_N, sway)]},
        {'key': 'palmB', 'label': 'Tamareira B', 'build': build_palm(1), 'boost': 0.8, 'shadow': False, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('balanca', ANIM_N, sway)]},
        {'key': 'palmC', 'label': 'Tamareira C', 'build': build_palm(2), 'boost': 0.8, 'shadow': False, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('balanca', ANIM_N, sway)]},
        {'key': 'alavanca', 'label': 'Alavanca da comporta', 'build': build_lever, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('ang', LEVER_N, lever_pose)]},
        {'key': 'palicada', 'label': 'Palicada', 'build': build_gate, 'margin': (0.1, 0.1, 0.1, 0.1),
         'modes': [('dir', GATE_DIRS, gate_pose)]},
    ],
}


if __name__ == '__main__':
    main(FAM, SPEC)
