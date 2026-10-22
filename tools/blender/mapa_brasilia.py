"""Mapa de Brasilia (Ninguem Sobe a Rampa) em diorama 3D, com a mesma camera ortografica e escala das fases.

O Plano Piloto em forma de aviao: o Eixo Monumental (gramado largo com as duas pistas) de oeste para leste, as asas do
Eixo Rodoviario cruzando na Rodoviaria e arqueando para o lago, as superquadras dos dois lados, o Lago Paranoa a leste
(com os bracos norte e sul e a Ponte JK), cerrado dourado e ipes em volta. Os marcos das 5 fases ficam ao lado dos nos
(DATA.WORLD em js/data.js), nunca embaixo deles: 1 Rodoviaria, 2 Esplanada dos Ministerios (com a Catedral),
3 Congresso Nacional, 4 Praca dos Tres Poderes (mastro e STF), 5 Palacio do Planalto com a rampa.
O jogo desenha por cima as trilhas entre os nos, as bandeiras, os paineis e os botoes (WorldMap em js/ui.js): a faixa de
baixo (y > 600) e o alto (y < 60) ficam sem nada importante.

  Blender -b -P tools/blender/mapa_brasilia.py -- mapa arte/render/cenario [amostras] [px_por_unidade]
  python3 tools/sprites/empacotar.py cenario      (pack_mapa grava sprites/cenario_mapa.jpg e SPRITE_META.mapa)
"""
import os, sys, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cenario as C
from cenario import *   # noqa: F401,F403
from cenario_props import Lote, rock
from mapa import inside_poly, quad
from brasilia_props import (br_mats, ipe, arvore_cerrado, capim, predio_faixas, congresso, catedral, rodoviaria, planalto, stf,
                            mastro, rampa, pombal, onibus)

# nos das fases (DATA.WORLD) e as trilhas do jogo (a mesma curva do ui.js: controle no meio + (40, 30))
NODES = [(300, 468), (604, 484), (806, 484), (1016, 470), (930, 190)]
HUD = [(30, 0, 820, 62), (30, 600, 330, 720), (480, 606, 1260, 720)]

EIXO_Y = 345              # Eixo Monumental (y na tela)
EIXO_X = (30, 1012)
ASA_X0, ASA_Y = 362, (66, 628)   # asas: cruzam o eixo em x 362 e arqueiam para o leste nas pontas


def asa_pts(n=80):
    """Eixo Rodoviario: arco de norte a sul cruzando o Eixo Monumental, com as pontas viradas para o lago."""
    out = []
    for i in range(n + 1):
        t = -1 + 2 * i / n
        y = EIXO_Y + t * ((EIXO_Y - ASA_Y[0]) if t < 0 else (ASA_Y[1] - EIXO_Y))
        out.append((ASA_X0 + 118 * t * t, y))
    return out


def lake_poly():
    """Lago Paranoa: a baia a leste do Plano Piloto e os bracos norte e sul (fecha por fora da tela)."""
    pts = [(1380, -80), (600, -80), (600, 18)]
    pts += [(640, 46), (720, 60), (800, 52), (880, 70), (950, 98), (1010, 132), (1058, 180), (1080, 240), (1076, 300),
            (1086, 360), (1080, 420), (1066, 480), (1040, 540), (990, 586), (920, 612), (840, 628), (760, 640), (680, 672),
            (640, 720), (600, 800), (1380, 800)]
    return pts


def trails():
    out = []
    for a, b in zip(NODES[:-1], NODES[1:]):
        out.append(quad(a, ((a[0] + b[0]) / 2 + 40, (a[1] + b[1]) / 2 + 30), b))
    return out


class MapaBR(C.Campo):
    """Chao do mapa: cerrado, gramado do eixo, pistas, superquadras, a praca e o lago (sem a montagem de fase do Campo)."""

    def __init__(self):
        self.L = {'seed': 61, 'theme': 'mapa', 'paths': trails(), 'spots': [], 'water': []}
        self.th = dict(relief=0.08, wl=(2.0, 5.0))
        ys, xs = np.mgrid[0:C.MH, 0:C.MW].astype(np.float32)
        self.XX, self.YY = xs + C.MX0, ys + C.MY0
        self.D = self.road_field(self.L['paths'])
        self.LAKE = lake_poly()
        self.Dlake = self.road_field([self.LAKE + [self.LAKE[0]]])
        self.ASA = asa_pts()
        self.Dasa = self.road_field([self.ASA])
        self.spots = []
        self.water = []

    def field_at(self, F, gx, gy):
        ix = np.clip(np.rint(np.asarray(gx) - C.MX0).astype(np.int64), 0, C.MW - 1)
        iy = np.clip(np.rint(np.asarray(gy) - C.MY0).astype(np.int64), 0, C.MH - 1)
        return F[iy, ix]

    def lake_sd(self, gx, gy):
        d = self.field_at(self.Dlake, gx, gy)
        return np.where(inside_poly(gx, gy, self.LAKE), -d, d)   # negativo = agua

    def spot_dist(self, X, Y):
        d = np.full(np.shape(X), 99.0, np.float32)
        for (nx, ny) in NODES:
            w = to_world(nx, ny + 4)
            d = np.minimum(d, np.hypot(X - w.x, Y - w.y))
        return d

    def urban(self, gx, gy):
        """0..1: dentro do Plano Piloto (asas e eixo), onde nao ha cerrado alto."""
        da = self.field_at(self.Dasa, gx, gy)
        ax = 1 - sstep(72, 98, da)   # o campo de distancia das asas so vai ate 100 px delas (cenario.road_field)
        ex = (1 - sstep(70, 95, np.abs(gy - EIXO_Y))) * sstep(EIXO_X[0] - 20, EIXO_X[0] + 20, gx) * (1 - sstep(EIXO_X[1], EIXO_X[1] + 30, gx))
        return np.maximum(ax, ex)

    def evaluate(self, X, Y):
        gx = 640 + X * GB
        gy = 360 - Y * C.SIN * GB
        sd = self.lake_sd(gx, gy)
        da = self.field_at(self.Dasa, gx, gy)
        ds = self.spot_dist(X, Y)
        rel = self.relief(X, Y) + 0.1
        h = rel * sstep(8, 40, sd) * (1 - 0.8 * self.urban(gx, gy))
        h = np.where(sd < 10, np.minimum(h, -0.4 * (1 - sstep(-30, 10, sd))), h)
        # cores: cerrado dourado com manchas verdes
        rr = random.Random(77)
        patch = np.zeros(np.shape(X), np.float32)
        for i in range(6):
            a = rr.uniform(0, TAU)
            k = TAU / rr.uniform(1.4, 3.6)
            patch += np.sin((X * math.cos(a) + Y * math.sin(a)) * k + rr.uniform(0, TAU)).astype(np.float32)
        relk = np.clip(rel * 4, 0, 1)
        col = hex3('#a68a46')[None] * (1 - relk[:, None]) + hex3('#c8aa5e')[None] * relk[:, None]
        ok = (sstep(0.5, 2.0, patch) * 0.55)[:, None]
        col = col * (1 - ok) + hex3('#99984d')[None] * ok
        col *= (1 + 0.04 * patch / 3)[:, None]
        # Plano Piloto: chao mais claro e verde das superquadras
        ub = self.urban(gx, gy)[:, None]
        col = col * (1 - ub * 0.7) + hex3('#b7b06a')[None] * ub * 0.7
        # superquadras: blocos verdes dos dois lados das asas, separados pelas entrequadras
        t_ = np.clip((gy - ASA_Y[0]) / (ASA_Y[1] - ASA_Y[0]), 0, 1)
        blk = (np.modf(gy / 46.0)[0] > 0.18) & (np.abs(gy - EIXO_Y) > 44)
        sq = (((da > 14) & (da < 52)) | ((da > 60) & (da < 98))) & blk
        sqk = (sq.astype(np.float32) * (1 - sstep(0.0, 0.04, np.abs(t_ - 0.5) - 0.46)))[:, None]
        col = col * (1 - sqk) + hex3('#8ea251')[None] * sqk
        # pistas: Eixo Rodoviario e as duas do Eixo Monumental (asfalto claro)
        road = 1 - sstep(3.5, 5.5, da)
        ey = np.abs(gy - EIXO_Y)
        inx = sstep(EIXO_X[0], EIXO_X[0] + 10, gx) * (1 - sstep(EIXO_X[1] - 10, EIXO_X[1], gx))
        road = np.maximum(road, (1 - sstep(2.5, 4.0, np.abs(ey - 22))) * inx)
        lawn = (1 - sstep(17, 19.5, ey)) * inx
        col = col * (1 - lawn[:, None]) + hex3('#9fae55')[None] * lawn[:, None]
        col = col * (1 - road[:, None]) + hex3('#8c877e')[None] * road[:, None]
        # Praca dos Tres Poderes: triangulo de pedra portuguesa no fim do eixo
        tri = inside_poly(gx, gy, [(888, 292), (1000, 345), (888, 402)]).astype(np.float32)
        col = col * (1 - tri[:, None]) + hex3('#e3dccd')[None] * tri[:, None]
        # pracinhas dos nos (o jogo poe a bandeira em cima)
        pad = 1 - sstep(0.5, 0.62, ds)
        col = col * (1 - pad[:, None]) + hex3('#d9d1c1')[None] * pad[:, None]
        h = h * (1 - pad) + 0.01 * pad
        # beira do lago: areia clara e fundo
        sand = (1 - sstep(4, 14, sd)) * sstep(-6, 2, sd)
        col = col * (1 - sand[:, None]) + hex3('#d8c79c')[None] * sand[:, None]
        bed = 1 - sstep(-16, 0, sd)
        col = col * (1 - bed[:, None]) + hex3('#4f6a5e')[None] * bed[:, None]
        wet = (1 - sstep(-2, 6, sd)).astype(np.float32)
        self._sd = sd
        d = self.road_at(gx, gy)
        e = np.full(np.shape(X), 9.0, np.float32)
        return h.astype(np.float32), col.astype(np.float32), np.zeros(np.shape(X), np.float32), wet, d, ds, e


def build_lake(root, cp, z=-0.05):
    """Lamina d'agua do lago: onde o chao foi cavado; cor pela profundidade, espuma clara na beira."""
    xs = np.arange(-16.8, 16.8 + 1e-6, 0.12, dtype=np.float32)
    ys = np.arange(-17.6, 19.0 + 1e-6, 0.12, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    h, *_ = cp.evaluate(XX.ravel(), YY.ravel())
    sd = cp._sd
    nx, ny = len(xs), len(ys)
    depth = np.clip((z - h) / 0.35, 0, 1)
    deep, shallow, foam = hex3('#2f7d93'), hex3('#62aebf'), hex3('#d6eef0')
    col = shallow[None] * (1 - depth[:, None]) + deep[None] * depth[:, None]
    f = np.clip(1 - (z - h) / 0.03, 0, 1)
    col = col * (1 - f[:, None] * 0.75) + foam[None] * f[:, None] * 0.75
    verts = np.stack([XX.ravel(), YY.ravel(), np.full(nx * ny, z, np.float32)], 1)
    idx = np.arange(nx * ny).reshape(ny, nx)
    keep = ((h < z + 0.02) & (sd < 12)).reshape(ny, nx)
    k4 = keep[:-1, :-1] | keep[:-1, 1:] | keep[1:, 1:] | keep[1:, :-1]
    q = np.stack([idx[:-1, :-1][k4], idx[:-1, 1:][k4], idx[1:, 1:][k4], idx[1:, :-1][k4]], 1)
    me = bpy.data.meshes.new('Lago')
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
    o = bpy.data.objects.new('Lago', me)
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
        # o no ocupa da ponta da bandeira (y - 60) ate as estrelas (y + 32), e o heroi fica a esquerda
        if nx - 80 - r < x < nx + 48 + r and ny - 70 - r < y < ny + 40 + r:
            return False
    return True


def ponte_jk(root, name, a, b, M, s=1.0):
    """Ponte JK: tabuleiro reto sobre o lago com tres arcos brancos cruzados por cima."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L_ = d.length
    yaw = math.atan2(d.y, d.x)
    mid = (a + b) / 2
    box(root, name + '_tabuleiro', (L_, 0.28 * s, 0.05 * s), (mid.x, mid.y, 0.1 * s), rot=(0, 0, yaw), m=M['conc'], bev=0.015)
    for k in range(3):
        c0 = a + d * (k / 3)
        c1 = a + d * ((k + 1) / 3)
        pts = []
        for i in range(13):
            t = i / 12
            p = c0.lerp(c1, t)
            side = (-1 if k % 2 else 1) * 0.12 * s * math.sin(math.pi * t)
            pts.append((p.x - math.sin(yaw) * side, p.y + math.cos(yaw) * side, 0.1 * s + 0.55 * s * math.sin(math.pi * t)))
        tube(root, f'{name}_arco{k}', pts, 0.03 * s, M['conc_l'], segs=8)
    for k in range(7):
        p = a.lerp(b, (k + 0.5) / 7)
        cyl(root, f'{name}_pilar{k}', 0.03 * s, 0.2 * s, (p.x, p.y, -0.02), m=M['conc'], v=8, bev=0.0)


def torre_tv(root, name, loc, M, s=1.0):
    """Torre de TV: tripe de concreto, mastro de trelica fino e o mirante no meio."""
    x, y, z = loc
    for k in range(3):
        a = TAU * k / 3 + 0.3
        tube(root, f'{name}_pe{k}', [(x + 0.35 * s * math.cos(a), y + 0.35 * s * math.sin(a), z), (x, y, z + 0.9 * s)], 0.05 * s, M['conc'], segs=8)
    tube(root, name + '_mastro', [(x, y, z + 0.85 * s), (x, y, z + 3.0 * s)], 0.05 * s, M['metal'], segs=8, rfun=lambda t: s * (0.06 - 0.04 * t))
    cyl(root, name + '_mirante', 0.16 * s, 0.1 * s, (x, y, z + 1.55 * s), m=M['conc_l'], v=16, bev=0.02)
    cyl(root, name + '_mirante2', 0.12 * s, 0.07 * s, (x, y, z + 2.1 * s), m=M['metal'], v=12, bev=0.01)
    sphere(root, name + '_ponta', 0.035 * s, (x, y, z + 3.02 * s), m=M['vermelho'], seg=8)


def build_map_br(root, P):
    cp = MapaBR()
    rr = random.Random(9)
    C.build_ground(cp, root)
    build_lake(root, cp)
    M = br_mats()
    lote = Lote('miudos_mapa')
    g = lambda x, y: (lambda w: Vector((w.x, w.y, cp.height_at(w.x, w.y))))(to_world(x, y))
    placed = []

    def ok(x, y, r=0, trail_d=12):
        if not free_of_ui(x, y, r) or float(cp.road_at(x, y)) < trail_d + r * 0.5:
            return False
        if float(cp.lake_sd(np.float32(x), np.float32(y))) < 10 + r * 0.4:
            return False
        return all(math.hypot(px - x, py - y) > r + pr for (px, py, pr) in placed)

    def mark(x, y, r):
        placed.append((x, y, r))

    # ---- marcos das fases (ao lado dos nos)
    # 1 Rodoviaria: no cruzamento do eixo com as asas
    w = g(ASA_X0 + 4, EIXO_Y)
    rodoviaria(root, 'rodoviaria', (w.x, w.y, w.z), 0.36, M, W=6.0, D=2.0)
    mark(ASA_X0, EIXO_Y, 60)
    for k, (dx, a) in enumerate(((-30, 0.5), (-8, 0.5), (14, 0.5))):
        b = g(ASA_X0 + dx, EIXO_Y + 34)
        onibus(root, f'onibus{k}', (b.x, b.y, b.z), a, M, (M['azul'], M['verde'], M['amarelo'])[k], s=0.42)
    # 2 Esplanada: duas filas de ministerios iguais e a Catedral no comeco
    for row, yy in ((0, EIXO_Y - 52), (1, EIXO_Y + 54)):
        for k in range(6):
            x = 478 + k * 50
            w = g(x, yy)
            predio_faixas(root, f'ministerio{row}_{k}', (w.x, w.y, w.z), 1.0, 0.42, 0.85, M, floors=5, pilotis=False)
            mark(x, yy, 22)
    w = g(440, EIXO_Y + 58)
    catedral(root, 'catedral', (w.x, w.y, w.z), 0.42, M)
    mark(440, EIXO_Y + 58, 22)
    # 3 Congresso no fim da Esplanada
    w = g(822, EIXO_Y + 2)
    congresso(root, 'congresso', (w.x, w.y, w.z), 0.42, M, W=3.2, D=0.85, sd=1.25, Ht=4.2)
    mark(822, EIXO_Y - 20, 66)
    # 4 Praca dos Tres Poderes: mastro com a bandeira, pombal e o STF ao sul
    w = g(944, EIXO_Y - 4)
    mastro(root, 'mastro', (w.x, w.y, w.z), 0.36, M, rr)
    w = g(914, EIXO_Y + 26)
    pombal(root, 'pombal', (w.x, w.y, w.z), 0.32, M)
    w = g(918, 414)
    stf(root, 'stf', (w.x, w.y, w.z), 0.42, M)
    mark(930, 390, 40)
    # 5 Palacio do Planalto ao norte da praca, com a rampa descendo para o sul (para a praca)
    w = g(906, 278)
    sub, info = planalto(root, 'planalto', (w.x, w.y, w.z), 0.55, M, n_col=6, W=2.5, D=0.55)
    yf = w.y - info['yc']
    rampa(root, 'rampa', (w.x + 0.62, yf - 0.95, w.z), (w.x + 0.62, yf - 0.02, w.z + info['zf'] + 0.02), 0.3, M, k=0.5)
    mark(906, 270, 60)
    # Torre de TV no comeco do eixo e o Palacio da Alvorada na beira do lago
    w = g(116, EIXO_Y - 6)
    torre_tv(root, 'torreTV', (w.x, w.y, w.z), M, s=0.75)
    mark(116, EIXO_Y - 30, 30)
    # Ponte JK no braco sul do lago
    a, b = to_world(1082, 556), to_world(1176, 604)
    ponte_jk(root, 'ponteJK', (a.x, a.y, 0.0), (b.x, b.y, 0.0), M, s=1.0)
    # veleiros no lago (casco branco e vela triangular)
    for k, (x, y, a) in enumerate(((1150, 250, 0.4), (1210, 420, -0.3), (1120, 640, 0.9), (760, 30, 0.2))):
        w = to_world(x, y)
        box(root, f'veleiro{k}', (0.34, 0.12, 0.06), (w.x, w.y, -0.03), rot=(0, 0, a), m=M['branco'], bev=0.03)
        bm = bmesh.new()
        vs = [bm.verts.new((w.x - 0.12 * math.cos(a), w.y - 0.12 * math.sin(a), 0.02)), bm.verts.new((w.x + 0.1 * math.cos(a), w.y + 0.1 * math.sin(a), 0.02)),
              bm.verts.new((w.x - 0.04 * math.cos(a), w.y - 0.04 * math.sin(a), 0.42))]
        bm.faces.new(vs)
        o = bm_to_obj(bm, f'vela{k}', root, [M['conc_l'] if k % 2 else M['amarelo']], angle=89)
        o.modifiers.new('Espessura', 'SOLIDIFY').thickness = 0.015
    # ---- superquadras: predinhos brancos e arvores nos blocos verdes das asas
    for i, (ax_, ay_) in enumerate(cp.ASA[::2]):
        if abs(ay_ - EIXO_Y) < 50:
            continue
        for side in (-1, 1):
            for off in (33, 79):
                x = ax_ + side * off
                y = ay_ + rr.uniform(-6, 6)
                if not free_of_ui(x, y, 6) or float(cp.lake_sd(np.float32(x), np.float32(y))) < 14 or float(cp.road_at(x, y)) < 12:
                    continue
                w = g(x, y)
                for j in range(rr.randrange(2, 4)):
                    bx = w.x + rr.uniform(-0.35, 0.35)
                    by = w.y + rr.uniform(-0.25, 0.25)
                    ang = rr.choice((0.0, math.pi / 2))
                    lote.box(M['conc_l'], (0.5, 0.14, 0.24), (bx, by, w.z + 0.12), rot=(0, 0, ang))
                    lote.box(M['vidro'], (0.46, 0.15, 0.04), (bx, by, w.z + 0.16), rot=(0, 0, ang))
                for j in range(3):
                    lote.pebble(M['arbusto'] if j % 2 else M['arbusto_l'], (w.x + rr.uniform(-0.45, 0.45), w.y + rr.uniform(-0.3, 0.3), w.z + 0.1),
                                rr.uniform(0.09, 0.13), squash=0.85, rot=rr.uniform(0, TAU), rr=rr, rough=0.3)
    # ---- ipes e cerrado em volta; capim seco
    grd = lambda wx, wy: cp.height_at(wx, wy)
    for k in range(220):
        x, y = rr.random() * 1280, rr.random() * 720
        if not ok(x, y, 16):
            continue
        mark(x, y, 16)
        w = g(x, y)
        if float(cp.urban(np.float32(x), np.float32(y))) > 0.5 or rr.random() < 0.4:
            ipe(root, lote, f'ipeMapa{k}', tuple(w), rr.uniform(0.42, 0.55), rr, M, ground=grd, petals=False)
        else:
            arvore_cerrado(root, lote, f'cerradoMapa{k}', tuple(w), rr.uniform(0.5, 0.7), rr, M)
    for k in range(520):
        x, y = rr.random() * 1280, rr.random() * 720
        if not ok(x, y, 6, trail_d=10) or float(cp.urban(np.float32(x), np.float32(y))) > 0.3:
            continue
        w = g(x, y)
        capim(lote, M, tuple(w), rr.uniform(0.18, 0.26), rr)
    for k in range(10):
        x, y = rr.random() * 1280, rr.random() * 720
        if ok(x, y, 10) and float(cp.urban(np.float32(x), np.float32(y))) < 0.3:
            rock(root, f'pedraMapa{k}', M['pedra'], tuple(g(x, y)), rr.uniform(0.15, 0.25), rr)
    # pracinhas dos nos: laje redonda de concreto com o anel de terra vermelha
    for k, (nx, ny) in enumerate(NODES):
        c0 = g(nx, ny + 4)
        cyl(root, f'pracaNo{k}_terra', 0.66, 0.03, (c0.x, c0.y, c0.z + 0.0), m=M['terra'], v=36, bev=0.01)
        cyl(root, f'pracaNo{k}', 0.56, 0.05, (c0.x, c0.y, c0.z + 0.02), m=M['conc_l'], v=36, bev=0.02)
    lote.done(root)
    return {'nodes': NODES}


def render_map(out_dir, samples=96, k=3.0):
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
    sc.view_settings.exposure = -0.55
    bpy.data.objects['ChaoSombra'].hide_render = True
    sc.cycles.samples = samples
    P = palette2()
    root = make_root('raiz_mapa', 'mapa', coll_for('Mapa'))
    meta = build_map_br(root, P)
    C.setup_camera(k)
    sc.render.image_settings.color_mode = 'RGB'
    path = os.path.join(out_dir, 'mapa.png')
    render_to(path)
    # sem luz no mapa de Brasilia (o mapa da mata tinha o vulcao): tira a camada antiga para o empacotador nao usa-la
    old = os.path.join(out_dir, 'mapa_glow.png')
    if os.path.exists(old):
        os.remove(old)
    with open(os.path.join(out_dir, 'mapa.json'), 'w') as fh:
        json.dump(meta, fh)
    print('MAPA_OK', path)


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'mapa':
        render_map(args[1], int(args[2]) if len(args) > 2 else 96, float(args[3]) if len(args) > 3 else 3.0)
