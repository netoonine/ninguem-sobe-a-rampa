"""Mapa-mundi da segunda regiao (Rio das Duas Aguas), no mesmo estilo e camera do mapa.py.

O Negro desce do noroeste e o Solimoes vem do oeste; juntos correm lado a lado, sem misturar, ate o mar no sudeste, onde
o estuario vira manguezal. Um afluente de agua clara nasce numa cachoeira do tepui (nordeste) e atravessa a varzea alagada.
O jogo desenha por cima os nos 9 a 12, a trilha tracejada, os paineis e as setas (WorldMap em js/ui.js, reg 1).

  Blender -b -P tools/blender/mapa2.py -- mapa2 arte/render/cenario [amostras] [px_por_unidade]
"""
import os, sys, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cenario as C
from cenario import *   # noqa: F401,F403
from mapa import HUD, mountain, quad

# posicoes dos nos 9 a 12 (DATA.WORLD com reg: 1) e a seta de voltar para a regiao 1 (ui.js, x 48 y 340)
NODES2 = [(420, 320), (660, 565), (1000, 430), (1080, 210)]
HUD2 = HUD + [(10, 300, 92, 384)]

C.RIO_COR['clara'] = ('#2a7a78', '#5aa89c', '#d8eee6')
C.TH['mapa2'] = dict(sand='#6c9a42', sand_l='#86b050', sand_d='#4a7432', road='#b0683f', road_d='#8a4b2c', pad='#6a4e34', rim='#a7a397',
                     relief=0.18, wl=(1.6, 4.5), ripples=0.0, pebble='#a39e92', mata=True, bed='#4f5a32', grass='#7fa846',
                     water=('#24706e', '#58a898', '#cfe8d6'))

RIVERS2 = [
    {'pts': [(-60, 80), (90, 150), (220, 250), (300, 340), (352, 398)], 'w': 40, 'cor': 'negro'},
    {'pts': [(-60, 610), (100, 560), (230, 490), (320, 438), (352, 414)], 'w': 40, 'cor': 'barro'},
    {'pts': [(350, 406), (470, 422), (600, 440), (720, 472), (820, 522), (900, 592), (960, 662), (1010, 770)], 'w': 64, 'cor': ['negro', 'barro']},
    {'pts': [(1168, 178), (1110, 240), (1030, 300), (960, 360), (905, 430), (872, 500), (862, 556)], 'w': 26, 'cor': 'clara'},
]
SEA2 = [(1330, 900, 560, 380)]


def trail():
    out = []
    for i in range(len(NODES2) - 1):
        a, b = NODES2[i], NODES2[i + 1]
        out.append(quad(a, ((a[0] + b[0]) / 2 + 40, (a[1] + b[1]) / 2 + 30), b))
    return out


def free_of_ui(x, y, r=0):
    for (x0, y0, x1, y1) in HUD2:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return False
    for (nx, ny) in NODES2:
        if abs(x - nx) < 48 + r and ny - 70 - r < y < ny + 40 + r:
            return False
    return True


def build_map2(root, P):
    L = {'seed': 5151, 'theme': 'mapa2', 'paths': [], 'water': SEA2, 'rivers': RIVERS2, 'pontes': [],
         'spots': [{'x': x, 'y': y + 4, 'high': False, 'ruin': 0, 'low': False} for (x, y) in NODES2]}
    cp = C.Campo(L)
    Dt = cp.road_field(trail())
    rr = random.Random(23)
    out = {'palms': [], 'env': []}
    C.build_ground(cp, root)
    C.build_water(cp, root)
    C.build_river(cp, root)
    lote = Lote('miudos_mapa2')
    C.MT = mats()
    C.RT = rio_mats()
    Mt, R = C.MT, C.RT
    place = C.Lugar(cp, L, rr)
    g = lambda x, y: place.ground(x, y)
    er = lambda x, y: float(cp.river_e(np.float32(x), np.float32(y))[0])
    ew = lambda x, y: float(cp.water_e(np.float32(x), np.float32(y)))

    def ok(x, y, r=0, trail_d=12):
        return (free_of_ui(x, y, r) and float(cp._grid(Dt, x, y)) > trail_d + r * 0.5 and ew(x, y) > 1.12 + r / 200
                and er(x, y) > 1.25 + r / 40)

    # 12 tepuis no nordeste: o maior solta a cachoeira que vira o afluente; fumaca negra sobe do topo
    lights = []
    for k, (x, y, rx, h) in enumerate(((1196, 148, 1.85, 2.4), (962, 122, 1.15, 1.5), (1252, 312, 0.85, 1.1))):
        w = g(x, y)
        objs, top = strata_rock(root, f'tepui_mapa{k}', R['arenito'], R['arenito2'], tuple(w), rx, rx * 0.7, h, rr, layers=4)
        grass_cap(root, f'tepui_mapa{k}_mata', Mt, tuple(w), rx * 0.6, rx * 0.42, top - 0.02)
        for j in range(5):
            a = rr.uniform(0, TAU)
            sphere(root, f'tepui_mapa{k}_copa{j}', 0.2 * rx, (w.x + 0.35 * rx * math.cos(a), w.y + 0.25 * rx * math.sin(a), w.z + top + 0.08),
                   scale=(1, 1, 0.7), m=Mt['leaf'] if j % 2 else Mt['leaf_d'], seg=12)
        if k == 0:
            # cachoeira na face da frente, caindo ate a nascente do afluente
            fall = mat('cachoeira_mapa', '#eef8fa', rough=0.3, var=0.02, bump=0.05, emit=0.4)
            box(root, 'cachoeira_mapa', (0.22, 0.05, top), (w.x - 0.2, w.y - rx * 0.62, w.z + top / 2), rot=(0.12, 0, 0), m=fall, bev=0.03)
            for j in range(6):
                sphere(root, f'espuma_mapa{j}', rr.uniform(0.1, 0.16), (w.x - 0.2 + rr.uniform(-0.25, 0.25), w.y - rx * 0.75 + rr.uniform(-0.1, 0.1), w.z + 0.04),
                       scale=(1.2, 1, 0.6), m=R['nuvem'], seg=12)
            smoke = mat('fumaca_mapa', '#3c3536', rough=0.9, var=0.08, bump=0.1)
            for j in range(8):
                t = j / 7
                sphere(root, f'fumaca_mapa{j}', 0.18 + 0.22 * t, (w.x + 0.25 + 0.5 * t + 0.1 * math.sin(j * 1.7), w.y + 0.2 * t, w.z + top + 0.2 + 1.3 * t),
                       scale=(1.2, 1, 0.8), m=smoke, seg=14)
            ember = glow_mat('brasa_mapa2', '#ff6a1a', 5.0, 16.0, rough=0.6, var=0.1, bump=0.1)
            sphere(root, 'coracao_mapa', 0.16, (w.x + 0.2, w.y, w.z + top + 0.06), scale=(1.4, 1.2, 0.5), m=ember, seg=14)
            out['env'].append([x + 6, y - 64, '#ff6a1a'])
    # 9 encontro das aguas: barco de recreio e flutuantes na juncao
    for k, (x, y, a) in enumerate(((470, 428, 0.05), (560, 446, -0.1))):
        w = to_world(x, y, -0.05)
        if k == 0:
            river_boat(root, 'recreio_mapa', Mt, R, (w.x, w.y, -0.05), 0.55, a, rr)
        else:
            floating_house(root, 'flutuante_mapa', Mt, R, (w.x, w.y, -0.07), 0.5, a, rr)
    for k, (x, y, a) in enumerate(((150, 165, 0.6), (130, 555, -0.4), (760, 492, 0.4), (980, 336, -0.8))):
        w = to_world(x, y, -0.05)
        canoe(root, f'canoa_mapa2_{k}', Mt, (w.x, w.y, -0.08), 0.5, a, rr)
    # 10 manguezal no estuario e no litoral
    for k in range(70):
        x, y = rr.uniform(720, 1280), rr.uniform(500, 720)
        d_ = min(er(x, y), ew(x, y))
        if not (1.0 < d_ < 1.9) or not free_of_ui(x, y, 4) or float(cp._grid(Dt, x, y)) < 14:
            continue
        mangrove(root, f'mangue_mapa{k}', R, tuple(g(x, y)), rr.uniform(0.5, 0.65), rr, lote=lote)
    for j in range(6):
        w = g(770 + rr.uniform(-20, 20), 640 + rr.uniform(-8, 8))
        wader(root, f'guara_mapa{j}', R, tuple(w), 0.7, rr.uniform(0, TAU), rr)
    # 11 varzea alagada: arvores com o pe na agua na beira do afluente e uma palafita
    for k in range(40):
        x, y = rr.uniform(860, 1100), rr.uniform(300, 560)
        if not (0.75 < er(x, y) < 1.3) or not free_of_ui(x, y, 4):
            continue
        w = g(x, y)
        jungle_tree(root, f'arvore_varzea_mapa{k}', Mt, (w.x, w.y, max(w.z, -0.06)), rr.uniform(0.42, 0.52), rr)
    w = g(1050, 488)
    if free_of_ui(1050, 488, 4):
        palafita(root, 'palafita_mapa2', Mt, tuple(w), 0.7, rr, ang=-0.2)
    # mata densa no resto
    for k in range(1800):
        x, y = rr.random() * 1280, rr.random() * 720
        if not ok(x, y, 6, trail_d=14):
            continue
        r_ = rr.random()
        w = g(x, y)
        if r_ < 0.58:
            for j in range(3):
                a = rr.uniform(0, TAU)
                sphere(root, f'copa_mapa2_{k}_{j}', rr.uniform(0.22, 0.32), (w.x + 0.18 * math.cos(a), w.y + 0.15 * math.sin(a), w.z + 0.35 + 0.08 * j),
                       scale=(1, 1, 0.8), m=Mt['leaf'] if (k + j) % 3 else Mt['leaf_d'], seg=14)
            tube(root, f'tronco_mapa2_{k}', [(w.x, w.y, w.z), (w.x, w.y, w.z + 0.35)], 0.05, Mt['bark'], segs=6)
        elif r_ < 0.66:
            out['palms'].append([rr.randrange(3), *[round(v_, 1) for v_ in to_game(w)], round(rr.uniform(0.42, 0.55), 3), rr.random()])
        elif r_ < 0.82:
            fern(root, f'samambaia_mapa2_{k}', Mt, tuple(w), rr.uniform(0.35, 0.5), rr)
        elif r_ < 0.9:
            bromeliad(root, f'bromelia_mapa2_{k}', Mt, tuple(w), rr.uniform(0.7, 1.0), rr, center=rr.choice((Mt['pink'], Mt['red'])))
        else:
            grass_tuft(lote, Mt, tuple(w), rr.uniform(0.2, 0.3), rr)
    # beira dos rios: aninga e canarana
    for k in range(60):
        x, y = rr.random() * 1280, rr.random() * 720
        if 0.85 < er(x, y) < 1.05 and free_of_ui(x, y, 2):
            w = to_world(x, y)
            aninga(lote, R, (w.x, w.y, max(-0.05, cp.height_at(w.x, w.y))), 0.55, rr)
    # pracas dos nos: deck de madeira pequeno
    for (nx, ny) in NODES2:
        c0 = to_world(nx, ny + 4)
        c0.z = cp.height_at(c0.x, c0.y)
        deck_pad(lote, Mt, (c0.x, c0.y, c0.z), 0.5, rr)
    lote.done(root)
    out['glow_lights'] = lights
    return out


def render_map2(out_dir, samples=96, k=2.0):
    clear_scene()
    ANIMS.clear()
    sc = bpy.context.scene
    ST['coll'] = sc.collection
    setup_scene()
    try:
        bpy.context.preferences.addons['cycles'].preferences.metalrt = 'OFF'
    except Exception:
        pass
    sc.render.film_transparent = False
    sc.view_settings.exposure = -0.52
    bpy.data.objects['ChaoSombra'].hide_render = True
    sc.cycles.samples = samples
    P = palette2()
    root = make_root('raiz_mapa2', 'mapa2', coll_for('Mapa2'))
    meta = build_map2(root, P)
    meta.pop('glow_lights', None)
    for i, (v, gx, gy, s_, ph) in enumerate(meta['palms']):
        sub = make_root(f'palm_mapa2_{i}', root['set'], root.users_collection[0])
        pv = PALM_VARIANTS[v]
        palm(sub, f'pmapa2_{i}', P, s=s_, seed=pv['seed'], lean=pv['lean'], animate=False)
        sub.location = to_world(gx, gy)
    C.setup_camera(k)
    sc.render.image_settings.color_mode = 'RGB'
    path = os.path.join(out_dir, 'mapa2.png')
    render_to(path)
    BUILT['mapa2'] = {'lights': []}
    render_glow_pass('mapa2', os.path.join(out_dir, 'mapa2_glow.png'))
    meta['glow'] = True
    meta['nodes'] = NODES2
    with open(os.path.join(out_dir, 'mapa2.json'), 'w') as fh:
        json.dump(meta, fh)
    print('MAPA2_OK', path, len(meta['palms']), 'palmeiras')


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'mapa2':
        render_map2(args[1], int(args[2]) if len(args) > 2 else 96, float(args[3]) if len(args) > 3 else 2.0)
