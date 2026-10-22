"""Mapa-mundi (Fronteira de Sahrim) em diorama 3D, no mesmo estilo e camera das fases.

O jogo desenha por cima os nos das fases, a estrada tracejada, os paineis e os botoes (WorldMap em js/ui.js);
aqui ficam o chao, o mar, o rio, as montanhas e um marco de cada regiao ao lado do no (nunca embaixo dele).

  Blender -b -P tools/blender/mapa.py -- mapa arte/render/cenario [amostras] [px_por_unidade]
"""
import os, sys, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cenario as C
from cenario import *   # noqa: F401,F403

# posicoes dos nos (DATA.WORLD) e das curvas da estrada (o mesmo controle do ui.js)
NODES = [(1010, 520), (790, 380), (560, 470), (380, 290), (610, 170), (870, 250), (1150, 400), (1120, 200)]
RIVER_CTRL = [((210, 120), (330, 260), (500, 300), (610, 400)), ((610, 400), (700, 480), (860, 520), (1000, 640)),
              ((1000, 640), (1040, 674), (1050, 720), (1060, 790))]
HUD = [(30, 20, 260, 92), (460, 20, 820, 92), (30, 600, 320, 700), (690, 610, 1250, 700), (1090, 26, 1260, 90)]

TH_MAP = dict(sand='#6c9a42', sand_l='#86b050', sand_d='#4a7432', road='#b0683f', road_d='#8a4b2c', relief=0.2, wl=(1.6, 4.5),
              ripples=0.0, water=('#24706e', '#58a898', '#cfe8d6'))


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def quad(a, c, b, n=30):
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1])
            for t in (i / n for i in range(n + 1))]


def sea_poly():
    """Litoral do mapa 2D (as mesmas curvas), fechado por fora da tela."""
    pts = [(-80, -80), (330, -80), (330, 0)]
    pts += bezier((330, 0), (300, 60), (220, 70), (200, 140), 24)[1:]
    pts += bezier((200, 140), (170, 230), (80, 220), (0, 300), 24)[1:]
    pts += [(-80, 330)]
    return pts


SEA = None


def roads():
    out = []
    for i in range(len(NODES) - 1):
        a, b = NODES[i], NODES[i + 1]
        out.append(quad(a, ((a[0] + b[0]) / 2 + 40, (a[1] + b[1]) / 2 + 30), b))
    return out


def inside_poly(x, y, poly):
    """Ponto(s) dentro do poligono (raio par-impar), vetorizado."""
    inside = np.zeros(np.shape(x), bool)
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        cond = ((y0 > y) != (y1 > y)) & (x < (x1 - x0) * (y - y0) / ((y1 - y0) or 1e-9) + x0)
        inside ^= cond
    return inside


class MapaCampo(C.Campo):
    def __init__(self):
        self.L = {'seed': 4242, 'theme': 'mapa', 'paths': roads(), 'spots': [], 'water': []}
        self.th = TH_MAP
        ys, xs = np.mgrid[0:C.MH, 0:C.MW].astype(np.float32)
        self.XX, self.YY = xs + C.MX0, ys + C.MY0
        self.D = self.road_field(self.L['paths'])
        global SEA
        SEA = sea_poly()
        coast = [p for p in SEA]
        self.Dsea = self.road_field([coast + [coast[0]]])
        self.Dr = self.road_field([sum((bezier(*seg) for seg in RIVER_CTRL), [])])
        canals = [[(1090, 360), (1210, 380)], [(1100, 430), (1230, 440)], [(1150, 340), (1150, 470)]]
        self.Dc = self.road_field(canals)
        self.spots = []
        self.water = [(1090, 604, 40, 18)]

    def field_at(self, F, gx, gy):
        ix = np.clip(np.rint(np.asarray(gx) - C.MX0).astype(np.int64), 0, C.MW - 1)
        iy = np.clip(np.rint(np.asarray(gy) - C.MY0).astype(np.int64), 0, C.MH - 1)
        return F[iy, ix]

    def spot_dist(self, X, Y):
        d = np.full(np.shape(X), 99.0, np.float32)
        for (nx, ny) in NODES:
            w = to_world(nx, ny + 4)
            d = np.minimum(d, np.hypot(X - w.x, Y - w.y))
        return d

    def evaluate(self, X, Y):
        th = self.th
        gx = 640 + X * GB
        gy = 360 - Y * C.SIN * GB
        d = self.road_at(gx, gy)
        ds = self.spot_dist(X, Y)
        e = self.water_e(gx, gy)
        dsea = self.field_at(self.Dsea, gx, gy)
        sea_in = inside_poly(gx, gy, SEA)
        sd = np.where(sea_in, -dsea, dsea)            # distancia com sinal ao litoral (negativo = mar)
        dr = self.field_at(self.Dr, gx, gy)
        dc = self.field_at(self.Dc, gx, gy)
        rel = self.relief(X, Y) + th['relief'] * 1.2   # o relevo nunca desce ate a agua (senao vira poca)
        flat = sstep(6, 30, d) * sstep(0.7, 1.4, ds) * sstep(10, 40, sd) * sstep(14, 40, dr) * sstep(1.05, 1.6, e) * sstep(8, 40, dc)
        h = rel * flat
        h += -0.02 * (1 - sstep(2, 6, d))                                  # trilha entre as fases
        h += -0.012 * (1 - sstep(0.55, 0.75, ds))                          # praca do no
        h = np.where(sd < 14, np.minimum(h, -0.45 * (1 - sstep(-30, 12, sd)) + 0.0), h)   # mar
        h = np.minimum(h, np.where(dr < 22, -0.26 * (1 - sstep(7, 21, dr)), 9))          # rio
        h = np.minimum(h, np.where(dc < 6, -0.12 * (1 - sstep(2, 5, dc)), 9))            # canais
        h = np.where(e < 1.3, h * sstep(0.95, 1.3, e) - 0.3 * (1 - sstep(0.72, 1.06, e)), h)
        relk = np.tanh((rel - th['relief'] * 1.2) / th['relief'] * 1.1) * 0.5 + 0.5
        col = hex3(th['sand_d'])[None] * (1 - relk[:, None]) + hex3(th['sand_l'])[None] * relk[:, None]
        col = col * 0.55 + hex3(th['sand'])[None] * 0.45
        rr = random.Random(77)
        patch = np.zeros(np.shape(X), np.float32)
        for i in range(6):
            a = rr.uniform(0, TAU)
            k = TAU / rr.uniform(1.5, 4.0)
            patch += np.sin((X * math.cos(a) + Y * math.sin(a)) * k + rr.uniform(0, TAU)).astype(np.float32)
        col *= (1 + 0.035 * patch / 3)[:, None]
        # verde nas margens do rio, no oasis e nas lavouras do qanat
        green = (1 - sstep(12, 34, dr)) * (0.7 + 0.3 * np.clip(patch / 3 + 0.5, 0, 1))
        green = np.maximum(green, (1 - sstep(1.2, 1.7, e)) * sstep(1.0, 1.1, e))
        green = np.maximum(green, (1 - sstep(10, 26, dc)) * 0.8)
        green = np.maximum(green, sstep(0, 20, sd) * (1 - sstep(20, 46, sd)) * 0.35)
        col = col * (1 - green[:, None]) + hex3('#7fae46')[None] * green[:, None]
        trail = 1 - sstep(3, 6, d)
        col = col * (1 - trail[:, None] * 0.8) + hex3(th['road'])[None] * trail[:, None] * 0.8
        plaza = 1 - sstep(0.6, 0.72, ds)
        col = col * (1 - plaza[:, None]) + hex3('#9a6a42')[None] * plaza[:, None]
        wet = np.maximum(np.maximum(1 - sstep(-2, 8, sd), 1 - sstep(8, 13, dr)), 1 - sstep(0.98, 1.1, e)).astype(np.float32)
        wet = np.maximum(wet, (1 - sstep(4, 7, dc)).astype(np.float32))
        col = col * (1 - 0.3 * wet[:, None])
        bed = np.maximum(1 - sstep(-14, 0, sd), 1 - sstep(4, 9, dr))
        col = col * (1 - bed[:, None]) + hex3('#4f5a32')[None] * bed[:, None]
        rip = (sstep(8, 30, d) * sstep(0.9, 1.3, ds) * sstep(20, 50, sd) * sstep(20, 40, dr) * (1 - green)).astype(np.float32)
        self._extra = (sd, dr, dc)
        return h.astype(np.float32), col.astype(np.float32), rip, wet, d, ds, e


def build_sea(root, cp, z=-0.05):
    """Uma lamina d'agua so: aparece onde o chao foi cavado (mar, rio, canais, lagoa). A cor vem da profundidade."""
    xs = np.arange(-16.8, 16.8 + 1e-6, 0.12, dtype=np.float32)
    ys = np.arange(-17.6, 19.0 + 1e-6, 0.12, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    h, *_ = cp.evaluate(XX.ravel(), YY.ravel())
    nx, ny = len(xs), len(ys)
    depth = np.clip((z - h) / 0.4, 0, 1)
    deep, shallow, foam = hex3('#24706e'), hex3('#58a898'), hex3('#cfe8d6')
    col = shallow[None] * (1 - depth[:, None]) + deep[None] * depth[:, None]
    f = np.clip(1 - (z - h) / 0.03, 0, 1)
    col = col * (1 - f[:, None] * 0.8) + foam[None] * f[:, None] * 0.8
    verts = np.stack([XX.ravel(), YY.ravel(), np.full(nx * ny, z, np.float32)], 1)
    idx = np.arange(nx * ny).reshape(ny, nx)
    sd, dr, dc = cp._extra
    e = cp.water_e(640 + XX.ravel() * GB, 360 - YY.ravel() * C.SIN * GB)
    wmask = (sd < 16) | (dr < 23) | (dc < 7) | (e < 1.2)
    keep = ((h < z + 0.02) & wmask).reshape(ny, nx)
    k4 = keep[:-1, :-1] | keep[:-1, 1:] | keep[1:, 1:] | keep[1:, :-1]
    q = np.stack([idx[:-1, :-1][k4], idx[:-1, 1:][k4], idx[1:, 1:][k4], idx[1:, :-1][k4]], 1)
    me = bpy.data.meshes.new('Agua')
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.ravel())
    me.loops.add(q.size)
    me.loops.foreach_set('vertex_index', q.ravel().astype(np.int32))
    me.polygons.add(len(q))
    me.polygons.foreach_set('loop_start', (np.arange(len(q)) * 4).astype(np.int32))
    me.update(calc_edges=True)
    ca = me.color_attributes.new('cor', 'FLOAT_COLOR', 'POINT')
    ca.data.foreach_set('color', np.concatenate([col, np.ones((len(col), 1), np.float32)], 1).ravel())
    me.polygons.foreach_set('use_smooth', np.ones(len(q), bool))
    o = bpy.data.objects.new('Agua', me)
    root.users_collection[0].objects.link(o)
    o.parent = root
    o['set'] = root['set']
    me.materials.append(C.water_material())
    return o


def free_of_ui(x, y, r=0):
    for (x0, y0, x1, y1) in HUD:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return False
    for (nx, ny) in NODES:
        # o no ocupa da ponta da bandeira (y - 60) ate as estrelas (y + 32)
        if abs(x - nx) < 48 + r and ny - 70 - r < y < ny + 40 + r:
            return False
    return True


def mountain(root, name, m, m2, loc, s, rr):
    """Montanha de arenito: cone macio com sulcos de erosao e uma faixa mais escura na base."""
    sd = rr.random() * 20

    def wob(a, z):
        return 0.07 * noise.noise(Vector((math.cos(a) * 1.4 + sd, math.sin(a) * 1.4, z * 1.5))) + 0.05 * math.sin(a * 7 + sd) * (0.4 + z)
    prof = [(0, 1.5 * s, 1.25 * s), (0.35 * s, 1.25 * s, 1.05 * s), (0.9 * s, 0.85 * s, 0.72 * s), (1.45 * s, 0.45 * s, 0.4 * s),
            (1.75 * s, 0.2 * s, 0.18 * s), (1.85 * s, 0.0, 0.0)]
    o = lathe(root, name, prof, m, segs=40, wobble=wob, lv=2, caps=False)
    o.location = (loc[0], loc[1], loc[2] - 0.05)
    o.rotation_euler = (0, 0, rr.uniform(0, TAU))
    b = lathe(root, name + '_base', [(0, 1.55 * s, 1.3 * s), (0.22 * s, 1.38 * s, 1.15 * s)], m2, segs=40, wobble=wob, lv=1, caps=False)
    b.location = (loc[0], loc[1], loc[2] - 0.06)
    b.rotation_euler = o.rotation_euler
    return o


def build_map(root, P):
    cp = MapaCampo()
    rr = random.Random(9)
    out = {'palms': [], 'env': []}
    C.build_ground(cp, root)
    build_sea(root, cp)
    lote = Lote('miudos_mapa')
    place = C.Lugar(cp, {'spots': [], 'paths': roads()}, rr)
    g = lambda x, y: place.ground(x, y)

    def ok(x, y, r=0, path_d=10):
        return free_of_ui(x, y, r) and float(cp.road_at(x, y)) > path_d + r * 0.5 and float(cp.field_at(cp.Dsea, x, y)) > 12 + r * 0.4 \
            and not inside_poly(np.float32(x), np.float32(y), SEA) and float(cp.field_at(cp.Dr, x, y)) > 14 + r * 0.4

    S = 0.6   # escala dos enfeites no mapa (uma regiao inteira cabe na tela)
    sand_rock = mat('rocha_mapa', '#c9a57a', rough=0.85, var=0.1, bump=0.3)
    red = mat('rocha_vermelha_mapa', '#bd7955', rough=0.88, var=0.1, bump=0.3)
    red2 = mat('rocha_vermelha2_mapa', '#a2633f', rough=0.9, var=0.1, bump=0.3)
    mount = mat('montanha_mapa', '#c99d6c', rough=0.9, var=0.08, bump=0.3)
    mount2 = mat('montanha2_mapa', '#b3865a', rough=0.9, var=0.08, bump=0.3)
    # montanhas (as mesmas do mapa 2D, deslocadas para longe dos nos)
    for k, (x, y, s) in enumerate([(790, 175, 1.15), (840, 150, 0.95), (940, 180, 1.2), (995, 215, 0.85), (735, 240, 0.85), (700, 330, 0.75),
                                   (965, 300, 0.9), (1000, 120, 0.8), (680, 90, 0.7)]):
        if not free_of_ui(x, y, 6):
            continue
        w = g(x, y)
        mountain(root, f'montanha{k}', mount, mount2, tuple(w), s, rr)
    # 1 oasis: lagoa com palmeiras
    for k in range(6):
        a = rr.uniform(math.pi * 1.0, math.pi * 2.0)
        x, y = 1090 + 60 * math.cos(a), 604 + 30 * math.sin(a)
        if ok(x, y, 6):
            out['palms'].append([rr.randrange(3), *[round(v, 1) for v in to_game(g(x, y))], round(rr.uniform(0.5, 0.62), 3), rr.random()])
    # 2 desfiladeiro: pilhas de rocha vermelha
    for k, (x, y) in enumerate([(725, 395), (858, 410), (862, 330), (718, 335), (700, 440)]):
        if ok(x, y, 10):
            strata_rock(root, f'desfiladeiro{k}', red, red2, tuple(g(x, y)), rr.uniform(0.55, 0.75), 0.5, rr.uniform(0.6, 0.9), rr, layers=3)
    # 3 ruinas: colunas
    st = mat('coluna_mapa', '#e6d4b0', rough=0.8, var=0.06, bump=0.2)
    st2 = mat('capitel_mapa', '#d8c39c', rough=0.8, var=0.06, bump=0.2)
    for k, (x, y) in enumerate([(492, 455), (496, 500), (628, 448), (630, 498), (470, 480)]):
        if ok(x, y, 4):
            column(root, f'ruina{k}', st, st2, tuple(g(x, y)), rr.uniform(0.9, 1.2), 0.12, rr, broken=k % 2 == 0)
    # 4 dunas: o relevo ja sobe; uma ossada e arbustos secos
    bone_m = mat('osso_mapa', '#efe4c8', rough=0.6, var=0.04, bump=0.1)
    bones(root, 'ossada_mapa', bone_m, tuple(g(330, 330)), rr, s=0.7)
    for k in range(8):
        x, y = 300 + rr.random() * 170, 240 + rr.random() * 120
        if ok(x, y, 4):
            drybush(lote, mat('galho_mapa', '#8a6844', rough=0.9, var=0.12, bump=0.1), tuple(g(x, y)), 0.25, rr)
    # 5 cidadela soterrada: muralha e torres atras do no
    wall = mat('muro_mapa', '#c7ab80', rough=0.85, var=0.1, bump=0.25)
    wall2 = mat('muro2_mapa', '#ad9268', rough=0.85, var=0.1, bump=0.25)
    for k, (x, y, a, w_) in enumerate([(560, 120, 0.1, 1.6), (665, 118, -0.1, 1.4)]):
        if free_of_ui(x, y):
            ruin_wall(root, f'cidadela{k}', wall, wall2, tuple(g(x, y)), w_, 0.55, rr, ang=a)
    for k, x in enumerate((540, 690)):
        w = g(x, 122)
        cyl(root, f'cidadela_torre{k}', 0.24, 0.9, (w.x, w.y, w.z + 0.45), m=wall, v=20, bev=0.04)
        cyl(root, f'cidadela_torreTopo{k}', 0.29, 0.12, (w.x, w.y, w.z + 0.95), m=wall2, v=20, bev=0.03)
    # 6 passo das tempestades: redemoinho de areia
    swirl = mat('redemoinho', '#c69c6a', rough=0.95, var=0.04, bump=0.2)
    w = g(905, 205)
    pts = [(w.x + 0.22 * (1 + t * 2.2) * math.cos(t * 16), w.y + 0.22 * (1 + t * 2.2) * math.sin(t * 16), w.z + t * 1.5) for t in (i / 90 for i in range(91))]
    tube(root, 'redemoinho', pts, 0.06, swirl, segs=6, rfun=lambda t: 0.07 + 0.05 * t)
    # 7 qanat: lavouras
    soil = mat('terra_mapa', '#8c6a42', rough=0.95, var=0.06, bump=0.3)
    crop = mat('broto_mapa', '#86b04c', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    for k, (x, y) in enumerate([(1092, 455), (1210, 458), (1098, 348), (1212, 342), (1240, 400), (1060, 400)]):
        if ok(x, y, 0, path_d=8):
            field(root, f'lavoura_mapa{k}', soil, crop, lote, tuple(g(x, y)), 1.45, 0.75, rr, rows=4, ang=0.05)
    # 8 trono do ifrit: vulcao atras do no
    v = g(1130, 118)
    rock_d = mat('vulcao', '#6a4e44', rough=0.85, var=0.08, bump=0.3)
    vo = lathe(root, 'vulcao', [(0, 1.35, 1.2), (0.5, 1.0, 0.9), (1.05, 0.55, 0.5), (1.2, 0.42, 0.38), (1.12, 0.3, 0.27)], rock_d, segs=36,
               wobble=lambda a, z: 0.06 * math.sin(a * 5) + 0.03 * math.sin(a * 11), lv=1, caps=False)
    vo.location = (v.x, v.y, v.z - 0.05)
    lava = glow_mat('lava_mapa', '#ff8a30', 7.0, 16.0, rough=0.5, var=0.05, bump=0.0)
    cyl(root, 'cratera', 0.3, 0.04, (v.x, v.y, v.z + 1.08), m=lava, v=24, bev=0.0)
    for k in range(3):
        a = 0.6 + k * 1.1
        tube(root, f'lava_escorre{k}', [(v.x + 0.32 * math.cos(a), v.y + 0.3 * math.sin(a), v.z + 1.1),
                                       (v.x + 0.75 * math.cos(a), v.y + 0.7 * math.sin(a), v.z + 0.55),
                                       (v.x + 1.05 * math.cos(a), v.y + 1.0 * math.sin(a), v.z + 0.1)], 0.05, lava, segs=6, rfun=lambda t: 0.05 - 0.03 * t)
    out['env'].append([1130, 70, '#ff6a1a'])
    # barquinho a vela no mar
    hull = mat('casco', '#8a5a32', rough=0.7, var=0.05, bump=0.2)
    sail = mat('vela', '#f4e7c9', rough=0.85, var=0.0, bump=0.05, sheen=0.3)
    b = to_world(95, 120, -0.05)
    lathe(root, 'barco', [(0, 0.0, 0.0), (0.06, 0.32, 0.11), (0.14, 0.4, 0.14)], hull, segs=20, lv=1).location = (b.x, b.y, -0.08)
    tube(root, 'barco_mastro', [(b.x, b.y, 0.0), (b.x, b.y, 0.7)], 0.018, P['wood'], segs=6)
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((b.x + 0.02, b.y, 0.12), (b.x + 0.02, b.y, 0.68), (b.x + 0.36, b.y, 0.14))]
    bm.faces.new(vs)
    so = bm_to_obj(bm, 'barco_vela', root, [sail], angle=89)
    so.modifiers.new('Espessura', 'SOLIDIFY').thickness = 0.01
    # vegetacao pelo mapa: arbustos verdes na beira do rio, rochas e capim no resto
    bush_m = mat('arbusto_mapa', '#6f9a45', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    bush2 = mat('arbusto_mapa2', '#89b053', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    grass = mat('capim_mapa', '#9aa94e', rough=0.85, var=0.15, bump=0.05)
    for k in range(260):
        x, y = rr.random() * 1280, rr.random() * 720
        dr = float(cp.field_at(cp.Dr, x, y))
        if not ok(x, y, 2, path_d=8):
            continue
        if dr < 40 and rr.random() < 0.6:
            if rr.random() < 0.25:
                out['palms'].append([rr.randrange(3), *[round(v_, 1) for v_ in to_game(g(x, y))], round(rr.uniform(0.45, 0.58), 3), rr.random()])
            else:
                bush(root, f'arb_mapa{k}', bush_m, tuple(g(x, y)), rr.uniform(0.16, 0.24), rr, m2=bush2)
        elif rr.random() < 0.18:
            rock(root, f'rocha_mapa{k}', sand_rock, tuple(g(x, y)), rr.uniform(0.1, 0.2), rr)
        elif rr.random() < 0.4:
            tuft(lote, grass, tuple(g(x, y)), rr.uniform(0.14, 0.2), rr)
    cm = mat('cacto_mapa', '#6a9a50', rough=0.75, var=0.08, bump=0.2)
    for k in range(40):
        x, y = rr.random() * 1280, rr.random() * 720
        if not ok(x, y, 14, path_d=16):
            continue
        r_ = rr.random()
        if r_ < 0.25:
            strata_rock(root, f'mesinha{k}', sand_rock, mount2, tuple(g(x, y)), rr.uniform(0.3, 0.45), 0.3, rr.uniform(0.25, 0.4), rr, layers=2)
        elif r_ < 0.5:
            cactus(root, f'cacto_mapa{k}', cm, tuple(g(x, y)), rr.uniform(0.22, 0.32), rr)
        elif r_ < 0.75:
            rock_cluster(root, f'pedras_mapa{k}', sand_rock, tuple(g(x, y)), rr.uniform(0.12, 0.18), rr, n=3)
        else:
            drybush(lote, mat('galho_mapa', '#8a6844', rough=0.9, var=0.12, bump=0.1), tuple(g(x, y)), 0.22, rr)
    for k, (x, y) in enumerate([(205, 400), (240, 418), (222, 380)]):
        if ok(x, y, 6):
            tent(root, f'tenda_mapa{k}', P, tuple(g(x, y)), rr, ang=rr.uniform(-0.6, 0.6) + 1.5, s=0.62)
    b2 = to_world(150, 60, -0.05)
    lathe(root, 'barco2', [(0, 0.0, 0.0), (0.05, 0.24, 0.08), (0.1, 0.3, 0.1)], hull, segs=20, lv=1).location = (b2.x, b2.y, -0.08)
    tube(root, 'barco2_mastro', [(b2.x, b2.y, 0.0), (b2.x, b2.y, 0.5)], 0.014, P['wood'], segs=6)
    bm = bmesh.new()
    vs = [bm.verts.new(p_) for p_ in ((b2.x - 0.02, b2.y, 0.1), (b2.x - 0.02, b2.y, 0.48), (b2.x - 0.26, b2.y, 0.11))]
    bm.faces.new(vs)
    so2 = bm_to_obj(bm, 'barco2_vela', root, [mat('vela_teal', '#23968f', rough=0.85, var=0.0, bump=0.05, sheen=0.3)], angle=89)
    so2.modifiers.new('Espessura', 'SOLIDIFY').thickness = 0.01
    # pracas dos nos: anel de pedrinhas
    rim = mat('anel_mapa', '#bfae98', rough=0.85, var=0.2, bump=0.15)
    for (nx, ny) in NODES:
        c0 = to_world(nx, ny + 4)
        c0.z = cp.height_at(c0.x, c0.y)
        for k in range(20):
            a = TAU * k / 20
            lote.pebble(rim, (c0.x + 0.68 * math.cos(a), c0.y + 0.68 * math.sin(a), c0.z), 0.06, squash=0.6, rr=rr)
    lote.done(root)
    return out


def build_map_mata(root, P):
    """Floresta do Rio Grande: mata densa em volta das trilhas, um marco de cada regiao ao lado do no."""
    cp = MapaCampo()
    rr = random.Random(9)
    out = {'palms': [], 'env': []}
    C.build_ground(cp, root)
    build_sea(root, cp)
    lote = Lote('miudos_mapa')
    C.MT = mats()
    Mt = C.MT
    place = C.Lugar(cp, {'spots': [], 'paths': roads()}, rr)
    g = lambda x, y: place.ground(x, y)

    def ok(x, y, r=0, path_d=10):
        return free_of_ui(x, y, r) and float(cp.road_at(x, y)) > path_d + r * 0.5 and float(cp.field_at(cp.Dsea, x, y)) > 12 + r * 0.4 \
            and not inside_poly(np.float32(x), np.float32(y), SEA) and float(cp.field_at(cp.Dr, x, y)) > 24 + r * 0.4

    S = 0.55
    # serras cobertas de mata (no lugar das montanhas do deserto)
    hill = mat('serra_mapa', '#5f8a3c', rough=0.9, var=0.1, bump=0.3)
    hill2 = mat('serra_mapa2', '#4a7030', rough=0.9, var=0.1, bump=0.3)
    for k, (x, y, sc) in enumerate([(790, 175, 1.1), (840, 150, 0.9), (940, 180, 1.15), (995, 215, 0.8), (735, 240, 0.8), (965, 300, 0.85), (1000, 120, 0.8)]):
        if not free_of_ui(x, y, 6):
            continue
        w = g(x, y)
        mountain(root, f'serra{k}', hill, hill2, tuple(w), sc * 0.85, rr)
        for j in range(4):
            a = rr.uniform(0, TAU)
            sphere(root, f'serra{k}_copa{j}', 0.32 * sc, (w.x + 0.75 * sc * math.cos(a), w.y + 0.6 * sc * math.sin(a), w.z + 0.25), scale=(1, 1, 0.75), m=Mt['leaf'], seg=14)
    # 1 igarape: lagoa com palafita
    w = g(1150, 590)
    if ok(1150, 590, 4):
        palafita(root, 'palafita_mapa1', Mt, tuple(w), 0.75, rr, ang=-0.2)
    # 2 barranco vermelho
    clay = mat('barro_mapa', '#b8643e', rough=0.88, var=0.1, bump=0.35)
    clay2 = mat('barro_mapa2', '#934a2e', rough=0.9, var=0.1, bump=0.35)
    for k, (x, y) in enumerate([(725, 395), (858, 410), (862, 330), (718, 335), (700, 440)]):
        if ok(x, y, 10):
            objs, top = strata_rock(root, f'barranco_mapa{k}', clay, clay2, tuple(g(x, y)), rr.uniform(0.55, 0.75), 0.5, rr.uniform(0.6, 0.9), rr, layers=3)
            sphere(root, f'barranco_mapa{k}_capim', 1.0, (g(x, y).x, g(x, y).y, g(x, y).z + top), scale=(0.35, 0.28, 0.08), m=Mt['moss'], seg=16)
    # 3 cidade perdida: colunas com musgo
    st = mat('coluna_mapa', '#a9a58e', rough=0.85, var=0.1, bump=0.3)
    st2 = mat('capitel_mapa', '#8f8b74', rough=0.85, var=0.1, bump=0.3)
    for k, (x, y) in enumerate([(492, 455), (496, 500), (628, 448), (630, 498), (470, 480)]):
        if ok(x, y, 4):
            column(root, f'ruina_mapa{k}', st, st2, tuple(g(x, y)), rr.uniform(0.9, 1.2), 0.12, rr, broken=k % 2 == 0)
    # 4 varzea: vitorias-regias no rio perto do no 4
    for k in range(10):
        t = rr.uniform(0.25, 0.42)
        bx, by = bezier(*RIVER_CTRL[0], 40)[int(t * 40)]
        w = to_world(bx + rr.uniform(-8, 8), by + rr.uniform(-5, 5), -0.05)
        vitoria_regia(lote, Mt, (w.x, w.y, -0.048), rr.uniform(0.1, 0.16), rr)
    # 5 gruta dos vaga-lumes: pedras com musgo e cogumelos que brilham atras do no
    gst = mat('pedra_gruta_mapa', '#6f6c60', rough=0.85, var=0.12, bump=0.35)
    for k, (x, y) in enumerate([(560, 118), (665, 118), (540, 150), (690, 150)]):
        if free_of_ui(x, y):
            w = g(x, y)
            objs, top = strata_rock(root, f'gruta_mapa{k}', gst, gst, tuple(w), 0.45, 0.38, rr.uniform(0.5, 0.8), rr, layers=3)
            glow_mushrooms(root, f'cogumelo_mapa{k}', Mt, (w.x + 0.3, w.y - 0.2, w.z), 0.8, rr)
            out['env'].append([x + 8, y + 4, '#7ff0d0'])
    # 6 temporal: nuvem de chuva sobre a serra
    for k, (x, z) in enumerate(((-0.35, 0.0), (0.0, 0.1), (0.32, 0.0), (0.1, -0.1))):
        w = g(905, 205)
        sphere(root, f'nuvem_mapa{k}', 0.32, (w.x + x, w.y + 0.1, w.z + 1.4 + z), scale=(1, 0.8, 0.7), m=mat('nuvem_mapa', '#6f7a84', rough=0.8, var=0.05), seg=18)
    for k in range(9):
        w = g(905, 205)
        tube(root, f'chuva_mapa{k}', [(w.x - 0.4 + 0.1 * k, w.y, w.z + 1.25), (w.x - 0.5 + 0.1 * k, w.y, w.z + 0.75)], 0.012, mat('chuva_mapa', '#a8c8d8', rough=0.3), segs=4)
    # 7 furos e comportas: rocas
    soil = mat('terra_mapa', '#6a4a30', rough=0.95, var=0.06, bump=0.3)
    for k, (x, y) in enumerate([(1092, 455), (1210, 458), (1098, 348), (1212, 342), (1240, 400), (1060, 400)]):
        if ok(x, y, 0, path_d=8):
            field(root, f'roca_mapa{k}', soil, Mt['leaf'], lote, tuple(g(x, y)), 1.45, 0.75, rr, rows=4, ang=0.05)
    # 8 coracao em chamas: morro queimado com brasas e tocos pretos
    v = g(1130, 118)
    burnt = mat('morro_queimado', '#3e322c', rough=0.9, var=0.08, bump=0.35)
    vo = lathe(root, 'morro_queimado', [(0, 1.35, 1.2), (0.45, 1.0, 0.9), (0.85, 0.55, 0.5), (1.0, 0.0, 0.0)], burnt, segs=36,
               wobble=lambda a, z: 0.06 * math.sin(a * 5) + 0.03 * math.sin(a * 11), lv=1, caps=False)
    vo.location = (v.x, v.y, v.z - 0.05)
    for k in range(7):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0.3, 0.9)
        charred_trunk(root, f'toco_mapa{k}', Mt, (v.x + d * math.cos(a), v.y + d * math.sin(a) * 0.8, v.z + 0.5 * (1 - d)), 0.7, rr)
    lava_crack(lote, Mt['ember'], mat('borda_brasa_mapa', '#2a2220'), [(v.x - 0.4 + 0.1 * t, v.y - 0.6 + 0.05 * math.sin(t), v.z + 0.2) for t in range(9)], 0.05)
    out['env'].append([1130, 80, '#ff6a1a'])
    # canoas no Rio Grande
    for k, (x, y, a) in enumerate(((95, 120, 0.3), (150, 60, -0.4), (470, 300, 0.6))):
        w = to_world(x, y, -0.05)
        canoe(root, f'canoa_mapa{k}', Mt, (w.x, w.y, -0.08), 0.6, a, rr)
    # mata densa: copas e folhagens onde nao ha no, trilha, rio nem HUD
    for k in range(900):
        x, y = rr.random() * 1280, rr.random() * 720
        if not ok(x, y, 6, path_d=14):
            continue
        r_ = rr.random()
        w = g(x, y)
        if r_ < 0.55:
            for j in range(3):
                a = rr.uniform(0, TAU)
                sphere(root, f'copa_mapa{k}_{j}', rr.uniform(0.22, 0.32), (w.x + 0.18 * math.cos(a), w.y + 0.15 * math.sin(a), w.z + 0.35 + 0.08 * j),
                       scale=(1, 1, 0.8), m=Mt['leaf'] if (k + j) % 3 else Mt['leaf_d'], seg=14)
            tube(root, f'tronco_mapa{k}', [(w.x, w.y, w.z), (w.x, w.y, w.z + 0.35)], 0.05, Mt['bark'], segs=6)
        elif r_ < 0.62:
            out['palms'].append([rr.randrange(3), *[round(v_, 1) for v_ in to_game(w)], round(rr.uniform(0.42, 0.55), 3), rr.random()])
        elif r_ < 0.8:
            fern(root, f'samambaia_mapa{k}', Mt, tuple(w), rr.uniform(0.35, 0.5), rr)
        elif r_ < 0.9:
            bromeliad(root, f'bromelia_mapa{k}', Mt, tuple(w), rr.uniform(0.7, 1.0), rr, center=rr.choice((Mt['pink'], Mt['red'])))
        else:
            grass_tuft(lote, Mt, tuple(w), rr.uniform(0.2, 0.3), rr)
    # pracas dos nos: deck de madeira pequeno
    for (nx, ny) in NODES:
        c0 = to_world(nx, ny + 4)
        c0.z = cp.height_at(c0.x, c0.y)
        deck_pad(lote, Mt, (c0.x, c0.y, c0.z), 0.5, rr)
    lote.done(root)
    return out


def render_map(out_dir, samples=96, k=2.0):
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
    root = make_root('raiz_mapa', 'mapa', coll_for('Mapa'))
    meta = build_map_mata(root, P)
    for i, (v, gx, gy, s_, ph) in enumerate(meta['palms']):
        sub = make_root(f'palm_mapa{i}', root['set'], root.users_collection[0])
        pv = PALM_VARIANTS[v]
        palm(sub, f'pmapa{i}', P, s=s_, seed=pv['seed'], lean=pv['lean'], animate=False)
        sub.location = to_world(gx, gy)
    C.setup_camera(k)
    sc.render.image_settings.color_mode = 'RGB'
    path = os.path.join(out_dir, 'mapa.png')
    render_to(path)
    BUILT['mapa'] = {'lights': []}
    render_glow_pass('mapa', os.path.join(out_dir, 'mapa_glow.png'))
    meta['glow'] = True
    with open(os.path.join(out_dir, 'mapa.json'), 'w') as fh:
        json.dump(meta, fh)
    print('MAPA_OK', path, len(meta['palms']), 'palmeiras')


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'mapa':
        render_map(args[1], int(args[2]) if len(args) > 2 else 96, float(args[3]) if len(args) > 3 else 2.0)
