"""Cenario 3D das fases: um fundo pre-renderizado por fase, com a mesma camera, sol e escala das torres.

Chao com relevo macio, estrada afundada (lida dos caminhos do jogo, ja suavizados), lagoas, mesas dos lotes altos,
lotes preparados (terra batida com anel de seixos) e os enfeites de cada tema. As palmeiras ficam fora do fundo
(so a sombra entra): elas balancam como sprites (tools/blender/ambiente.py).

  node tools/fases_json.js > arte/render/cenario/fases.json
  Blender -b -P tools/blender/cenario.py -- fundo arte/render/cenario <fase 1-8> [amostras] [px_por_unidade]

Sai f<N>.png (e f<N>_glow.png quando ha lava ou braseiros) e f<N>.json (palmeiras e luzes do cenario).
"""
import os, sys, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from lib import *   # noqa: F401,F403
import lib as _lib
from cenario_props import *   # noqa: F401,F403
from mata_props import *   # noqa: F401,F403
from rio_props import *   # noqa: F401,F403
MT = {}
RT = {}

SIN, COS = math.sin(ELEV), math.cos(ELEV)
GW, GH = 1280, 720
GB = GAME_PER_BU
# mascaras em coordenadas de tela do jogo (1 px por unidade), com folga para fora da tela
MX0, MY0, MW, MH = -110, -160, 1500, 1060



def to_world(gx, gy, z=0.0):
    return Vector(((gx - 640) / GB, ((360 - gy) / GB - z * COS) / SIN, z))


def to_game(p):
    return (640 + p[0] * GB, 360 - (p[1] * SIN + p[2] * COS) * GB)


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def hex3(h):
    return np.array(lin(h)[:3], np.float32)


# ---------------------------------------------------------------- temas
TH = {
    'oasis': dict(sand='#6f9a42', sand_l='#86ad4f', sand_d='#4c7631', road='#ad6442', road_d='#86462b', pad='#6a4e34',
                  rim='#a7a397', relief=0.16, wl=(1.8, 5.0), ripples=0.0, grass='#6f9f40', pebble='#a39e92', mata=True,
                  water=('#24706e', '#58a898', '#cfe8d6'), bed='#4f5a32', exposure=-0.4),
    'canyon': dict(sand='#6c9440', sand_l='#86ab4e', sand_d='#4f7432', road='#b0603e', road_d='#86452a', pad='#6a4e34', rim='#a7a397',
                   relief=0.16, wl=(2.2, 5.5), ripples=0.0, pebble='#a39e92', rock='#b8643e', rock2='#934a2e', mata=True, clay=True, exposure=-0.42),
    'ruins': dict(sand='#6f9846', sand_l='#88ae55', sand_d='#517535', road='#a99f86', road_d='#857c66', pad='#6a4e34', rim='#a7a397',
                  relief=0.12, wl=(2.0, 5.5), ripples=0.0, pebble='#9e9a8c', paved='#a7a391', mata=True, exposure=-0.42),
    'dunes': dict(sand='#6a9a46', sand_l='#84b055', sand_d='#4a7434', road='#a8693f', road_d='#83492b', pad='#6a4e34', rim='#a7a397',
                  relief=0.3, wl=(2.0, 5.0), ripples=0.0, pebble='#a39e92', mata=True, varzea=True,
                  water=('#2d6e66', '#5fa392', '#cfe8d6'), bed='#4f5a32', exposure=-0.42),
    'citadel': dict(sand='#4f6e3a', sand_l='#62844a', sand_d='#38522c', road='#8c7a62', road_d='#6c5c48', pad='#5a4430', rim='#8f8b80',
                    relief=0.1, wl=(2.0, 5.0), ripples=0.0, pebble='#8f8b80', paved='#8f8a78', mata=True, gruta=True, exposure=-0.35),
    'storm': dict(sand='#587e3c', sand_l='#6d9248', sand_d='#3f5e2c', road='#8e5a3c', road_d='#6c4029', pad='#5a4430', rim='#8f8b80',
                  relief=0.22, wl=(2.0, 5.0), ripples=0.0, pebble='#8f8b80', mata=True, varzea=True, rock='#7d7466', rock2='#5f584e',
                  water=('#1f2e2c', '#3d5a52', '#a8c0b4'), bed='#2f3a26', exposure=-0.4),
    'qanat': dict(sand='#6f9a42', sand_l='#88b050', sand_d='#4f7631', road='#ad6442', road_d='#86462b', pad='#6a4e34', rim='#a7a397',
                  relief=0.1, wl=(2.2, 6.0), ripples=0.0, pebble='#a39e92', mata=True, water=('#24706e', '#58a898', '#cfe8d6'), bed='#4f5a32',
                  exposure=-0.4),
    'ember': dict(sand='#5a4a40', sand_l='#6f5a4c', sand_d='#3e322c', road='#7a5a44', road_d='#5a4232', pad='#4a3a30', rim='#5a524c',
                  relief=0.14, wl=(2.2, 6.0), ripples=0.0, pebble='#5a524c', rock='#3a3230', rock2='#2a2422', lava=True, mata=True, cinza=True,
                  exposure=-0.15),
    # Rio das Duas Aguas (fases 9 a 12)
    'encontro': dict(sand='#6c9a44', sand_l='#86b052', sand_d='#4c7632', road='#b0683f', road_d='#8a4b2c', pad='#6a4e34', rim='#a7a397',
                     relief=0.14, wl=(2.0, 5.0), ripples=0.0, pebble='#a39e92', mata=True, bed='#5a5034', grass='#7fa846', exposure=-0.42),
    'mangue': dict(sand='#6b7650', sand_l='#84895c', sand_d='#4f5a3c', road='#cdb98c', road_d='#a8946a', pad='#5a4430', rim='#8f8b80',
                   relief=0.1, wl=(1.8, 4.5), ripples=0.0, pebble='#b9b2a2', mata=True, bed='#3e3a2e', mud='#4c4438', wet_all=0.55, exposure=-0.4),
    'cheia': dict(sand='#6a9a46', sand_l='#84b055', sand_d='#4a7434', road='#b0683f', road_d='#8a4b2c', pad='#6a4e34', rim='#a7a397',
                  relief=0.14, wl=(2.2, 5.5), ripples=0.0, pebble='#a39e92', mata=True, mud='#76603e', grass='#7fa846',
                  water=('#3f6a5a', '#6f9a7a', '#d8e8d0'), bed='#5a5034', exposure=-0.42),
    'tepui': dict(sand='#b8917e', sand_l='#caa491', sand_d='#9a7666', road='#dcc6a6', road_d='#bfa684', pad='#6a4e34', rim='#8f8b80',
                  relief=0.07, wl=(2.6, 6.5), ripples=0.0, pebble='#c9b8a6', mata=True, rock='#b78a7a', rock2='#93685c',
                  lichen='#4a4240', moss='#7a9a4a', borda=True, water=('#3e5a5c', '#7a9a92', '#e2ecdf'), bed='#6a5a4e', exposure=-0.45),
}

def fenda_pos(L):
    """Fenda da Fumaca (tepui): L.fenda, ou onde o caminho 0 entra na tela, um pouco abaixo da borda."""
    if L.get('fenda'):
        return tuple(L['fenda'])
    for q in L['paths'][0]:
        if 30 < q[0] < GW - 30 and q[1] >= 66:
            return (q[0], q[1])
    return (640, 120)


# cores da agua dos rios (fundo, raso, espuma)
RIO_COR = {
    'negro': ('#1a110b', '#3d2a1a', '#d6c29c'),
    'barro': ('#a3804f', '#c6a272', '#f2e8d0'),
    'salobra': ('#34504a', '#5f806c', '#d6e0cc'),
}
Z_CHEIA, Z_VAZANTE = -0.065, -0.2


# ---------------------------------------------------------------- campos (estrada, lotes, agua)
class Campo:
    def __init__(self, L):
        self.L = L
        self.th = TH[L['theme']]
        ys, xs = np.mgrid[0:MH, 0:MW].astype(np.float32)
        self.XX, self.YY = xs + MX0, ys + MY0
        self.D = self.road_field(L['paths'])
        self.spots = []
        for s in L['spots']:
            if s['high']:
                c = mesa_center(s)
                self.spots.append((c.x, c.y, 1.45, s))
            else:
                w = to_world(s['x'], s['y'])
                self.spots.append((w.x, w.y, 0.0, s))
        self.water = L['water']
        self.rng = np.random.default_rng(L['seed'])
        # rios: campo normalizado (1 = margem) e o lado do eixo. Um rio que nasce dentro de outro (juncao) comeca com a
        # largura de um afluente e alarga em 140 px: a ponta de terra entre os dois afluentes fica em cunha, sem paredao
        fields = [self.river_field(rv['pts']) for rv in L.get('rivers', [])]
        self.rivers = []
        for i, rv in enumerate(L.get('rivers', [])):
            D, S, A = fields[i]
            hw = rv['w'] / 2.0
            x0, y0 = rv['pts'][0]
            others = [fields[j][0] for j in range(len(fields)) if j != i]
            if any(float(self._grid(Dj, x0, y0)) < L['rivers'][j if j < i else j + 1]['w'] / 2.0 for j, Dj in enumerate(others)):
                hw = hw * (0.58 + 0.42 * sstep(0, 140, A))
            self.rivers.append(((D / hw).astype(np.float32), S, A, rv.get('cor', 'barro')))
        self.flood = bool(L.get('flood'))
        self.lows = [to_world(s['x'], s['y']) for s in L['spots'] if s.get('low')]
        self.fenda = fenda_pos(L) if L['theme'] == 'tepui' else None
        self.estiva = []   # trechos da estrada em estiva (preenchido por mark_estiva)
        self.E = None
        if self.flood:
            self.mark_estiva()

    def river_field(self, pts):
        """Distancia ao eixo do rio, o lado (positivo a esquerda de quem desce o rio) e quanto ja desceu (px)."""
        D = np.full((MH, MW), 999.0, np.float32)
        S = np.zeros((MH, MW), np.float32)
        A = np.zeros((MH, MW), np.float32)
        P = np.asarray(pts, np.float32)
        acc = 0.0
        for i in range(len(P) - 1):
            ax, ay = P[i]
            bx, by = P[i + 1]
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy or 1e-6
            ln = math.sqrt(L2)
            t = np.clip(((self.XX - ax) * dx + (self.YY - ay) * dy) / L2, 0, 1)
            d = np.hypot(self.XX - (ax + t * dx), self.YY - (ay + t * dy))
            sd = ((self.XX - ax) * dy - (self.YY - ay) * dx) / ln
            m = d < D
            D[m] = d[m]
            S[m] = sd[m]
            A[m] = acc + t[m] * ln
            acc += ln
        return D, S, A

    def _grid(self, F, gx, gy):
        ix = np.clip(np.rint(np.asarray(gx) - MX0).astype(np.int64), 0, MW - 1)
        iy = np.clip(np.rint(np.asarray(gy) - MY0).astype(np.int64), 0, MH - 1)
        return F[iy, ix]

    def river_e(self, gx, gy):
        """Distancia normalizada ao rio mais proximo (1 = margem) e o indice dele."""
        e = np.full(np.shape(gx), 9.0, np.float32)
        k = np.zeros(np.shape(gx), np.int32)
        for i, (En, S, A, cor) in enumerate(self.rivers):
            ei = self._grid(En, gx, gy)
            m = ei < e
            e = np.where(m, ei, e)
            k = np.where(m, i, k)
        return e, k

    def basin(self, X, Y, er):
        """Cheia: quanto um ponto e baixada (0 a 1): em volta dos lotes baixos e na varzea da beira do rio."""
        B = np.zeros(np.shape(X), np.float32)
        for w in self.lows:
            B = np.maximum(B, np.exp(-((X - w.x) ** 2 + (Y - w.y) ** 2) / 1.75 ** 2))
        if self.rivers:
            B = np.maximum(B, 0.85 * (1 - sstep(1.0, 2.1, er)))
        return B

    def mark_estiva(self):
        """Cheia: onde a estrada cruza a baixada ela vira estiva (passarela de tabuas); no resto fica no aterro."""
        segs = []
        for p in self.L['paths']:
            P_ = np.asarray(p, np.float32)
            X = (P_[:, 0] - 640) / GB
            Y = (360 - P_[:, 1]) / GB / SIN
            er = self.river_e(P_[:, 0], P_[:, 1])[0]
            low = (self.basin(X, Y, er) > 0.5) & (er > 1.2)
            idx = np.where(low)[0]
            if not len(idx):
                continue
            runs, a, b = [], idx[0], idx[0]
            for j in idx[1:]:
                if j - b <= 3:
                    b = j
                else:
                    runs.append((a, b)); a = b = j
            runs.append((a, b))
            for a, b in runs:
                if b - a >= 4:
                    a, b = max(0, a - 1), min(len(P_) - 1, b + 1)
                    segs.append([(float(x), float(y)) for x, y in P_[a:b + 1]])
        self.estiva = segs
        if segs:
            self.E = self.road_field([np.asarray(s_, np.float32) for s_ in segs])

    def road_field(self, paths):
        D = np.full((MH, MW), 999.0, np.float32)
        M = 100
        for pts in paths:
            P = np.asarray(pts, np.float32)
            for i in range(len(P) - 1):
                ax, ay = P[i]
                bx, by = P[i + 1]
                x0 = int(max(min(ax, bx) - M - MX0, 0))
                x1 = int(min(max(ax, bx) + M - MX0, MW - 1)) + 1
                y0 = int(max(min(ay, by) - M - MY0, 0))
                y1 = int(min(max(ay, by) + M - MY0, MH - 1)) + 1
                if x0 >= x1 or y0 >= y1:
                    continue
                xs, ys = self.XX[y0:y1, x0:x1], self.YY[y0:y1, x0:x1]
                dx, dy = bx - ax, by - ay
                L2 = dx * dx + dy * dy or 1e-6
                t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
                d = np.hypot(xs - (ax + t * dx), ys - (ay + t * dy))
                np.minimum(D[y0:y1, x0:x1], d, out=D[y0:y1, x0:x1])
        return D

    def road_at(self, gx, gy):
        ix = np.clip(np.rint(np.asarray(gx) - MX0).astype(np.int64), 0, MW - 1)
        iy = np.clip(np.rint(np.asarray(gy) - MY0).astype(np.int64), 0, MH - 1)
        return self.D[iy, ix]

    def spot_dist(self, X, Y, low=None, high=None):
        """Distancia (no chao) ao lote mais proximo; as mesas contam com o raio da base. low/high filtram o tipo de lote."""
        d = np.full(np.shape(X), 99.0, np.float32)
        for (sx, sy, extra, s) in self.spots:
            if low is not None and bool(s.get('low')) != low:
                continue
            if high is not None and bool(s.get('high')) != high:
                continue
            d = np.minimum(d, np.hypot(X - sx, Y - sy) - extra)
        return d

    def water_e(self, gx, gy):
        e = np.full(np.shape(gx), 9.0, np.float32)
        for (x, y, rx, ry) in self.water:
            e = np.minimum(e, np.sqrt(((gx - x) / rx) ** 2 + ((gy - y) / ry) ** 2))
        return e

    def relief(self, X, Y):
        th = self.th
        rr = random.Random(self.L['seed'] * 7 + 1)
        h = np.zeros(np.shape(X), np.float32)
        n = 10
        for i in range(n):
            a = rr.uniform(0, TAU)
            k = TAU / rr.uniform(*th['wl'])
            ph = rr.uniform(0, TAU)
            h += np.sin((X * math.cos(a) + Y * math.sin(a)) * k + ph).astype(np.float32) * rr.uniform(0.5, 1.0)
        h *= th['relief'] * 2.0 / n
        if th.get('dunes'):
            # cristas de duna: ondas largas e assimetricas, deformadas por outra onda
            for i in range(3):
                a = 0.5 + rr.uniform(-0.35, 0.35)
                k = TAU / rr.uniform(6.5, 9.5)
                warp = 0.9 * np.sin((X * math.cos(a + 1.4) + Y * math.sin(a + 1.4)) * TAU / 7.0 + i)
                th_ = (X * math.cos(a) + Y * math.sin(a)) * k + warp + rr.uniform(0, TAU)
                h += (0.5 + 0.5 * np.sin(th_ + 0.45 * np.sin(th_))) ** 2.2 * 0.42
        return h

    def evaluate(self, X, Y):
        """Altura, cor e mascara (R ondulacao, G molhado) para pontos do chao (arrays)."""
        th = self.th
        gx = 640 + X * GB
        gy = 360 - Y * SIN * GB
        d = self.road_at(gx, gy)
        ds = self.spot_dist(X, Y)
        e = self.water_e(gx, gy)
        er, rk = self.river_e(gx, gy)
        rel = self.relief(X, Y)
        flat = sstep(30, 95, d) * sstep(0.85, 1.9, ds) * sstep(1.05, 1.6, e) * sstep(1.05, 1.5, er)
        if th.get('varzea'):
            rel = rel - th['relief'] * 0.55
        dE = self._grid(self.E, gx, gy) if self.E is not None else np.full(np.shape(X), 999.0, np.float32)
        h = rel * flat
        est = (1 - sstep(28, 60, dE)) if self.flood else np.zeros(np.shape(X), np.float32)
        if self.flood:
            # baixada: lotes baixos e varzea do rio afundam; a agua da cheia passa por baixo da estiva
            B = self.basin(X, Y, er)
            h = h - 0.17 * B
            # os lotes que nao alagam ficam num tablado seco
            nl = 1 - sstep(0.8, 1.25, self.spot_dist(X, Y, low=False))
            h = h * (1 - nl) + np.maximum(h, 0.0) * nl
            # aterro: onde a estrada passa pela baixada ela fica acima da cheia (menos onde vira estiva)
            h += 0.11 * (1 - sstep(30, 58, d)) * (1 - est) * sstep(0.05, 0.3, B)
        # estrada: calha rasa, sulcos das rodas e a borda levantada onde ficam os seixos
        h += (-0.055 * (1 - sstep(17, 30, d)) + 0.035 * np.exp(-((d - 31.5) / 5.0) ** 2) - 0.014 * np.exp(-((d - 11.0) / 3.2) ** 2)) * (1 - est)
        # lote: terra batida um pouco abaixo
        h += -0.018 * (1 - sstep(0.66, 0.8, ds))
        # lagoa: fundo e margem
        bank = 0.03 * np.exp(-((e - 1.12) / 0.1) ** 2)
        h = np.where(e < 1.3, h * sstep(0.95, 1.3, e) - 0.32 * (1 - sstep(0.72, 1.06, e)) + bank, h)
        # rio: leito mais fundo e margem macia
        if self.rivers:
            bank = 0.03 * np.exp(-((er - 1.1) / 0.1) ** 2)
            hr = h * sstep(0.95, 1.3, er) - 0.36 * (1 - sstep(0.62, 1.04, er)) + bank
            # onde ja e agua (mar, lagoa) o rio so pode aprofundar, nunca levantar margem
            h = np.where(er < 1.3, np.where(h < -0.05, np.minimum(h, hr), hr), h)
        # borda do tepui: o plato acaba numa queda (longe da estrada); alem dela, mar de nuvens
        if th.get('borda'):
            ye = 62 + 14 * np.sin(gx / 97.0) + 9 * np.sin(gx / 41.0 + 1.0)
            cliff = (1 - sstep(ye - 14, ye, gy)) * sstep(44, 74, d)
            if self.fenda is not None:
                cliff = cliff * sstep(120, 170, np.hypot(gx - self.fenda[0], (gy - self.fenda[1]) * 1.6))
            h = h - 3.2 * cliff
        # cores
        relk = np.tanh(rel / max(th['relief'], 0.05) * 1.1) * 0.5 + 0.5
        sand = hex3(th['sand_d'])[None] * (1 - relk[:, None]) + hex3(th['sand_l'])[None] * relk[:, None]
        sand = sand * 0.55 + hex3(th['sand'])[None] * 0.45
        rr = random.Random(self.L['seed'] * 3 + 5)
        patch = np.zeros(np.shape(X), np.float32)
        for i in range(6):
            a = rr.uniform(0, TAU)
            k = TAU / rr.uniform(1.5, 4.0)
            patch += np.sin((X * math.cos(a) + Y * math.sin(a)) * k + rr.uniform(0, TAU)).astype(np.float32)
        sand *= (1 + 0.035 * patch / 3)[:, None]
        roadk = (1 - sstep(24, 33, d)) * (1 - est)
        road = hex3(th['road'])[None] * (1 - 0.12 * np.exp(-((d - 11.0) / 3.5) ** 2))[:, None]
        road = road * (1 - sstep(15, 27, d))[:, None] + hex3(th['road_d'])[None] * sstep(15, 27, d)[:, None]
        col = sand * (1 - roadk[:, None]) + road * roadk[:, None]
        padk = 1 - sstep(0.62, 0.8, self.spot_dist(X, Y, high=False))
        col = col * (1 - padk[:, None]) + hex3(th['pad'])[None] * padk[:, None]
        wet = np.zeros(np.shape(X), np.float32)
        if len(self.water):
            if th.get('grass'):
                gk = (1 - sstep(1.25, 1.55, e)) * sstep(1.02, 1.12, e) * (0.75 + 0.25 * np.clip(patch / 3 + 0.5, 0, 1))
                col = col * (1 - gk[:, None]) + hex3(th['grass'])[None] * gk[:, None]
            wet = (1 - sstep(0.98, 1.1, e)).astype(np.float32)
            col = col * (1 - 0.3 * wet[:, None])
            bed = 1 - sstep(0.85, 1.0, e)
            col = col * (1 - bed[:, None]) + hex3(th.get('bed', '#b9b07c'))[None] * bed[:, None]
        if self.rivers:
            wr = (1 - sstep(0.98, 1.12, er)).astype(np.float32)
            wet = np.maximum(wet, wr)
            col = col * (1 - 0.3 * wr[:, None])
            bed = 1 - sstep(0.85, 1.0, er)
            col = col * (1 - bed[:, None]) + hex3(th.get('bed', '#b9b07c'))[None] * bed[:, None]
            if th.get('grass'):
                gk = (1 - sstep(1.2, 1.5, er)) * sstep(1.02, 1.12, er) * (0.75 + 0.25 * np.clip(patch / 3 + 0.5, 0, 1))
                col = col * (1 - gk[:, None]) + hex3(th['grass'])[None] * gk[:, None]
        if th.get('mud'):
            # lama: nas baixadas (cheia) ou em manchas largas (mangue), sempre fora da estrada
            low = (1 - sstep(-0.12, -0.04, h)) if self.flood else sstep(0.5, 2.2, patch) * 0.6
            mk = (low * (1 - roadk)).astype(np.float32)
            col = col * (1 - mk[:, None]) + hex3(th['mud'])[None] * mk[:, None]
            wet = np.maximum(wet, mk * 0.7)
        if th.get('wet_all'):
            wet = np.maximum(wet, (th['wet_all'] * (1 - roadk)).astype(np.float32))
        if th.get('lichen'):
            lk = sstep(1.7, 2.5, patch) * sstep(36, 60, d) * sstep(0.9, 1.3, ds)
            col = col * (1 - 0.35 * lk[:, None]) + hex3(th['lichen'])[None] * 0.35 * lk[:, None]
            mk2 = sstep(1.5, 2.4, -patch) * sstep(36, 60, d) * sstep(0.9, 1.3, ds)
            col = col * (1 - 0.45 * mk2[:, None]) + hex3(th['moss'])[None] * 0.45 * mk2[:, None]
        if self.fenda is not None:
            # chao chamuscado em volta da fenda da Fumaca
            fx, fy = self.fenda
            sc = np.clip(1.25 * np.exp(-(((gx - fx) / 150.0) ** 2 + ((gy - fy) / 64.0) ** 2)), 0, 1) * (1 - roadk * 0.3)
            col = col * (1 - 0.8 * sc[:, None]) + hex3('#2c201e')[None] * 0.8 * sc[:, None]
        if th.get('meadow'):
            mk = sstep(0.6, 1.6, patch) * sstep(40, 70, d) * sstep(0.9, 1.4, ds)
            col = col * (1 - 0.75 * mk[:, None]) + hex3('#9db457')[None] * 0.75 * mk[:, None]
        rip = (sstep(36, 60, d) * sstep(0.9, 1.3, ds) * sstep(1.2, 1.5, e) * th['ripples']).astype(np.float32)
        return h.astype(np.float32), col.astype(np.float32), rip, wet, d, ds, e

    def height_at(self, x, y):
        h, *_ = self.evaluate(np.array([x], np.float32), np.array([y], np.float32))
        return float(h[0])


def mesa_center(s):
    """Centro no chao da mesa de um lote alto: o topo (z = MESA_H) projeta no lote."""
    w = to_world(s['x'], s['y'], MESA_H)
    return w


MESA_H = 0.72
EXPOSURE = {'ember': -0.2, 'citadel': -0.45}


# ---------------------------------------------------------------- chao
def ground_material(th):
    m = bpy.data.materials.new('chao_cenario')
    try:
        m.use_nodes = True
    except Exception:
        pass
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.93
    a = N.new('ShaderNodeAttribute'); a.attribute_name = 'cor'
    k = N.new('ShaderNodeAttribute'); k.attribute_name = 'mask'
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 26; nz.inputs['Detail'].default_value = 4
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.94; mr.inputs['To Max'].default_value = 1.05
    L.new(nz.outputs['Fac'], mr.inputs['Value'])
    hsv = N.new('ShaderNodeHueSaturation')
    L.new(a.outputs['Color'], hsv.inputs['Color'])
    L.new(mr.outputs['Result'], hsv.inputs['Value'])
    L.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    sep = N.new('ShaderNodeSeparateColor')
    L.new(k.outputs['Color'], sep.inputs['Color'])
    # ondulacoes de vento na areia
    mp = N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, 0.55)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = N.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 2.1; wv.inputs['Distortion'].default_value = 3.5; wv.inputs['Detail'].default_value = 1.5
    L.new(mp.outputs['Vector'], wv.inputs['Vector'])
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    L.new(wv.outputs['Fac'], mul.inputs[0]); L.new(sep.outputs['Red'], mul.inputs[1])
    fine = N.new('ShaderNodeMath'); fine.operation = 'MULTIPLY_ADD'
    L.new(nz.outputs['Fac'], fine.inputs[0]); fine.inputs[1].default_value = 0.25
    L.new(mul.outputs[0], fine.inputs[2])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.22; bp.inputs['Distance'].default_value = 0.03
    L.new(fine.outputs[0], bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.93; rg.inputs['To Max'].default_value = 0.45
    L.new(sep.outputs['Green'], rg.inputs['Value'])
    L.new(rg.outputs['Result'], bsdf.inputs['Roughness'])
    return m


def build_ground(cp, root, bands=10):
    """Malha do chao em faixas (a GPU Metal fura uma malha unica muito grande); as normais vem da grade inteira,
    para nao aparecer costura entre as faixas."""
    xs = np.arange(-16.8, 16.8 + 1e-6, 0.06, dtype=np.float32)
    ys = np.arange(-17.6, 19.0 + 1e-6, 0.072, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    h, col, rip, wet, d, ds, e = cp.evaluate(XX.ravel(), YY.ravel())
    nx, ny = len(xs), len(ys)
    Hg = h.reshape(ny, nx)
    gy_, gx_ = np.gradient(Hg, 0.072, 0.06)
    nrm = np.stack([-gx_, -gy_, np.ones_like(Hg)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    mat_ = ground_material(cp.th)
    out = []
    cuts = np.linspace(0, ny - 1, bands + 1).astype(int)
    for b in range(bands):
        r0, r1 = cuts[b], cuts[b + 1]
        rows = r1 - r0 + 1
        sl = slice(r0 * nx, (r1 + 1) * nx)
        verts = np.stack([XX.ravel()[sl], YY.ravel()[sl], h[sl]], 1)
        idx = np.arange(rows * nx).reshape(rows, nx)
        q = np.stack([idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()], 1)
        me = bpy.data.meshes.new(f'Chao{b}')
        me.vertices.add(len(verts))
        me.vertices.foreach_set('co', verts.ravel())
        me.loops.add(q.size)
        me.loops.foreach_set('vertex_index', q.ravel().astype(np.int32))
        me.polygons.add(len(q))
        me.polygons.foreach_set('loop_start', (np.arange(len(q)) * 4).astype(np.int32))
        me.update(calc_edges=True)
        ca = me.color_attributes.new('cor', 'FLOAT_COLOR', 'POINT')
        ca.data.foreach_set('color', np.concatenate([col[sl], np.ones((len(verts), 1), np.float32)], 1).ravel())
        ma = me.color_attributes.new('mask', 'FLOAT_COLOR', 'POINT')
        ma.data.foreach_set('color', np.stack([rip[sl], wet[sl], np.zeros(len(verts), np.float32), np.ones(len(verts), np.float32)], 1).ravel())
        me.polygons.foreach_set('use_smooth', np.ones(len(q), bool))
        me.normals_split_custom_set_from_vertices(nrm[r0:r1 + 1].reshape(-1, 3).tolist())
        o = bpy.data.objects.new(f'Chao{b}', me)
        root.users_collection[0].objects.link(o)
        o.parent = root
        o['set'] = root['set']
        me.materials.append(mat_)
        out.append(o)
    return out


def water_material():
    m = bpy.data.materials.new('agua_lagoa')
    try:
        m.use_nodes = True
    except Exception:
        pass
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['Specular IOR Level'].default_value = 0.7
    a = N.new('ShaderNodeAttribute'); a.attribute_name = 'cor'
    L.new(a.outputs['Color'], bsdf.inputs['Base Color'])
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 5; nz.inputs['Detail'].default_value = 2
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.12
    L.new(nz.outputs['Fac'], bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def build_water(cp, root, z=-0.05):
    out = []
    wc = cp.th.get('water', ('#2f9fb3', '#6cd0cf', '#d8f4ef'))
    deep, shallow, foam = hex3(wc[0]), hex3(wc[1]), hex3(wc[2])
    for k, (x, y, rx, ry) in enumerate(cp.water):
        bm = bmesh.new()
        rings = []
        es = [0.0, 0.25, 0.5, 0.7, 0.82, 0.9, 0.96, 1.02, 1.1, 1.18]
        n = 64
        cols = []
        for e in es:
            if e == 0:
                rings.append([bm.verts.new(tuple(to_world(x, y, z)))])
            else:
                rings.append([bm.verts.new(tuple(to_world(x + rx * e * math.cos(TAU * i / n), y + ry * e * math.sin(TAU * i / n), z))) for i in range(n)])
        for i in range(len(rings) - 1):
            A, B = rings[i], rings[i + 1]
            for j in range(n):
                if len(A) == 1:
                    bm.faces.new((A[0], B[j], B[(j + 1) % n]))
                else:
                    bm.faces.new((A[j], A[(j + 1) % n], B[(j + 1) % n], B[j]))
        o = bm_to_obj(bm, f'Lagoa{k}', root, [water_material()], angle=89)
        ca = o.data.color_attributes.new('cor', 'FLOAT_COLOR', 'POINT')
        vals = []
        for v in o.data.vertices:
            gx, gy = to_game(v.co)
            e = math.sqrt(((gx - x) / rx) ** 2 + ((gy - y) / ry) ** 2)
            t = min(1.0, max(0.0, (e - 0.3) / 0.6))
            c = deep * (1 - t) + shallow * t
            f = min(1.0, max(0.0, (e - 0.93) / 0.07))
            c = c * (1 - f) + foam * f
            vals += [c[0], c[1], c[2], 1.0]
        ca.data.foreach_set('color', vals)
        out.append(o)
    return out


def build_flood(cp, root, z=-0.06, cheia=False, name='Varzea'):
    """Varzea: uma lamina d'agua que so aparece onde o relevo desce abaixo dela (longe da trilha e dos lotes).
    Na cheia ela cobre tambem os lotes baixos e passa por baixo da estiva; o aterro da estrada fica de fora sozinho."""
    st = 0.05 if cheia else 0.1
    xs = np.arange(-16.8, 16.8 + 1e-6, st, dtype=np.float32)
    ys = np.arange(-17.6, 19.0 + 1e-6, st, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    h, col0, rip0, wet0, d, ds, e = cp.evaluate(XX.ravel(), YY.ravel())
    if cheia:
        d = np.full_like(d, 999.0)
        ds = cp.spot_dist(XX.ravel(), YY.ravel(), low=False)
        gx_, gy_ = 640 + XX.ravel() * GB, 360 - YY.ravel() * SIN * GB
        er = cp.river_e(gx_, gy_)[0]
        dr = cp.road_at(gx_, gy_)
        dE = cp._grid(cp.E, gx_, gy_) if cp.E is not None else np.full_like(dr, 999.0)
        out_ = (er < 0.95) | (e < 0.95) | (cp.basin(XX.ravel(), YY.ravel(), er) < 0.22) | ((dr < 40) & (dE > 50))
        ds = np.where(out_, 0.0, ds)
    nx, ny = len(xs), len(ys)
    wc = cp.th.get('water', ('#2d6e66', '#5fa392', '#cfe8d6'))
    deep, shallow, foam = hex3(wc[0]), hex3(wc[1]), hex3(wc[2])
    depth = np.clip((z - h) / 0.25, 0, 1)
    col = shallow[None] * (1 - depth[:, None]) + deep[None] * depth[:, None]
    f = np.clip(1 - (z - h) / 0.025, 0, 1)
    col = col * (1 - f[:, None] * 0.6) + foam[None] * f[:, None] * 0.6
    verts = np.stack([XX.ravel(), YY.ravel(), np.full(nx * ny, z, np.float32)], 1)
    idx = np.arange(nx * ny).reshape(ny, nx)
    # nunca sobre a trilha nem sobre os lotes (a trilha e rebaixada e ficaria embaixo d'agua)
    keep = ((h < z + 0.03) & (d > 42) & (ds > 1.0)).reshape(ny, nx)
    k4 = keep[:-1, :-1] & keep[:-1, 1:] & keep[1:, 1:] & keep[1:, :-1]
    q = np.stack([idx[:-1, :-1][k4], idx[:-1, 1:][k4], idx[1:, 1:][k4], idx[1:, :-1][k4]], 1)
    if not len(q):
        return None
    me = bpy.data.meshes.new(name)
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
    o = bpy.data.objects.new(name, me)
    root.users_collection[0].objects.link(o)
    o.parent = root
    o['set'] = root['set']
    me.materials.append(water_material())
    return o


def build_river(cp, root, z=-0.05):
    """Rios (L.rivers): lamina d'agua sobre o leito, funda no meio e clara na margem. Um rio com duas cores
    (encontro das aguas) separa as cores pelo lado do eixo, com a costura ondulada e uns redemoinhos."""
    xs = np.arange(-16.8, 16.8 + 1e-6, 0.07, dtype=np.float32)
    ys = np.arange(-17.6, 19.0 + 1e-6, 0.07, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    X, Y = XX.ravel(), YY.ravel()
    gx = 640 + X * GB
    gy = 360 - Y * SIN * GB
    er, rk = cp.river_e(gx, gy)
    nx, ny = len(xs), len(ys)
    col = np.zeros((len(X), 3), np.float32)
    wsum = np.zeros(len(X), np.float32)
    sky = hex3('#a9cbe0')
    for i, (En, S, A, cor) in enumerate(cp.rivers):
        ei = cp._grid(En, gx, gy)
        m = ei < 1.3
        if not m.any():
            continue
        e_ = ei[m]
        sd = cp._grid(S, gx[m], gy[m])
        al = cp._grid(A, gx[m], gy[m])
        px, py = gx[m], gy[m]
        t = np.clip((e_ - 0.35) / 0.6, 0, 1)[:, None]
        f = np.clip((e_ - 0.9) / 0.12, 0, 1)[:, None]
        # tracinhos de correnteza (agua de desenho): poucos, finos, ao longo do rio
        ca, cc = np.floor(al / 26.0), np.floor((sd + 500.0) / 9.0)
        rnd = np.modf(np.abs(np.sin(ca * 12.9898 + cc * 78.233 + i * 4.1) * 43758.5453))[0]
        fa, fc = np.modf(al / 26.0)[0], np.modf((sd + 500.0) / 9.0)[0]
        dash = ((rnd < 0.13) & (np.abs(fa - 0.5) < 0.3) & (np.abs(fc - 0.5) < 0.13) & (e_ < 0.85)).astype(np.float32)[:, None]
        # reflexo do ceu: mais forte longe da margem de baixo, ondulado
        refl = (0.1 + 0.08 * np.sin(px / 53.0 + py / 37.0) * np.sin(px / 21.0))[:, None]

        def tone(key):
            deep, shallow, foam = (hex3(c) for c in RIO_COR[key])
            c = deep[None] * (1 - t) + shallow[None] * t
            r_ = refl * (0.55 if key == 'negro' else 1.0)
            c = c * (1 - r_) + sky[None] * r_
            c = c * (1 - dash * 0.5) + foam[None] * dash * 0.5
            return c * (1 - f * 0.55) + foam[None] * f * 0.55
        if isinstance(cor, (list, tuple)):
            # lado esquerdo de quem desce o rio (S > 0) fica com a primeira cor
            wob = 7 * np.sin(px / 23.0 + py / 31.0) + 4 * np.sin(px / 9.0 - py / 13.0) + 2.5 * np.sin((px + py) / 5.0)
            k = 0.5 + 0.5 * np.tanh((sd + wob) / 3.0)
            ci = tone(cor[0]) * k[:, None] + tone(cor[1]) * (1 - k[:, None])
        else:
            ci = tone(cor)
        # rios que se encontram misturam as cores pela distancia (sem degrau na juncao)
        w = np.exp(-e_ * 7.0)
        col[m] += ci * w[:, None]
        wsum[m] += w
    col = col / np.maximum(wsum, 1e-6)[:, None]
    # chegando no mar (ou numa lagoa) a cor do rio vira a da agua de la, e a lamina do rio fica um fio acima
    we = cp.water_e(gx, gy)
    sea = hex3(cp.th.get('water', ('#2f9fb3', '#6cd0cf', '#d8f4ef'))[1])
    sk = (1 - sstep(0.9, 1.3, we))[:, None]
    col = col * (1 - sk) + sea[None] * sk
    z = z + 0.002
    verts = np.stack([X, Y, np.full(len(X), z, np.float32)], 1)
    idx = np.arange(nx * ny).reshape(ny, nx)
    # onde o rio entra no mar ou numa lagoa, a lamina e a dela (duas laminas no mesmo z dao manchas pretas)
    keep = ((er < 1.12) & (we > 0.86)).reshape(ny, nx)
    k4 = keep[:-1, :-1] & keep[:-1, 1:] & keep[1:, 1:] & keep[1:, :-1]
    q = np.stack([idx[:-1, :-1][k4], idx[:-1, 1:][k4], idx[1:, 1:][k4], idx[1:, :-1][k4]], 1)
    if not len(q):
        return None
    me = bpy.data.meshes.new('Rio')
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
    o = bpy.data.objects.new('Rio', me)
    root.users_collection[0].objects.link(o)
    o.parent = root
    o['set'] = root['set']
    me.materials.append(water_material())
    return o


# ---------------------------------------------------------------- posicionamento (as mesmas regras do cenario 2D)
class Lugar:
    def __init__(self, cp, L, rr):
        self.cp, self.L, self.rr = cp, L, rr
        self.placed = []

    def far_path(self, x, y, d):
        return float(self.cp.road_at(x, y)) > d

    def far_spot(self, x, y, d):
        return all(math.hypot(s['x'] - x, (s['y'] - y) * 1.3) > d for s in self.L['spots'])

    def free(self, x, y, d):
        return all(math.hypot(p[0] - x, p[1] - y) > d for p in self.placed)

    @staticmethod
    def hud_free(x, y):
        return not ((x < 350 and y < 90) or (x > 1120 and y < 82) or (x < 310 and y > 600))

    def clear_above(self, x, y, h, w):
        for s in self.L['spots']:
            if abs(s['x'] - x) < w + 34 and -24 < y - s['y'] < h + 24:
                return False
        for p in self.L['paths']:
            for q in p[::3]:
                if abs(q[0] - x) < w + 28 and 0 < y - q[1] < h + 28:
                    return False
        return True

    def take(self, n, rad, tall=None, test=None, path_d=44, water_ok=False, area=None):
        out = []
        rr = self.rr
        for k in range(n * 30):
            if len(out) >= n:
                break
            if area:
                x, y = area()
            else:
                x, y = 12 + rr.random() * (GW - 24), 16 + rr.random() * (GH - 26)
            if not self.far_path(x, y, path_d + rad) or not self.far_spot(x, y, 46 + rad) or not self.free(x, y, rad * 1.4) or not self.hud_free(x, y):
                continue
            if not water_ok and float(self.cp.water_e(np.float32(x), np.float32(y))) < 1.25 + rad / 60:
                continue
            if not water_ok and self.cp.rivers and float(self.cp.river_e(np.float32(x), np.float32(y))[0]) < 1.2 + rad / 60:
                continue
            if tall and not self.clear_above(x, y, tall[0], tall[1]):
                continue
            if test and not test(x, y):
                continue
            self.placed.append((x, y))
            out.append((x, y))
        return out

    def ground(self, x, y):
        w = to_world(x, y)
        w.z = self.cp.height_at(w.x, w.y)
        return w


# ---------------------------------------------------------------- montagem de uma fase
def build_level(L, root, P):
    th = TH[L['theme']]
    cp = Campo(L)
    rr = random.Random(L['seed'] * 101 + 7)
    out = {'palms': [], 'env': []}
    build_ground(cp, root)
    if cp.water:
        build_water(cp, root)
    if cp.rivers:
        build_river(cp, root)
    if th.get('varzea'):
        build_flood(cp, root, z=Z_VAZANTE if cp.flood else -0.06)
    lote = Lote('miudos')
    global MT, RT
    MT = mats()
    RT = rio_mats()
    pebble_m = mat('seixo_' + L['theme'], th['pebble'], rough=0.85, var=0.18, bump=0.15)
    rim_m = mat('anel_' + L['theme'], th['rim'], rough=0.85, var=0.2, bump=0.15)
    grass_m = mat('capim_cen', '#9aa94e', rough=0.85, var=0.15, bump=0.05)
    grass2_m = mat('capim_cen2', '#7f9a3e', rough=0.85, var=0.15, bump=0.05)
    dry_m = mat('galho_seco', '#8a6844', rough=0.9, var=0.12, bump=0.1)
    # seixos nas bordas da estrada (nunca em cima de outra estrada nem de um lote)
    for p in L['paths']:
        P_ = np.asarray(p, np.float32)
        seg = np.hypot(np.diff(P_[:, 0]), np.diff(P_[:, 1]))
        cum = np.concatenate([[0], np.cumsum(seg)])
        dist = 0.0
        while dist < cum[-1]:
            i = min(int(np.searchsorted(cum, dist)) , len(P_) - 1)
            i = max(1, i)
            a, b = P_[i - 1], P_[i]
            t = (dist - cum[i - 1]) / max(seg[i - 1], 1e-6)
            qx, qy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            dx, dy = (b[0] - a[0]) / max(seg[i - 1], 1e-6), (b[1] - a[1]) / max(seg[i - 1], 1e-6)
            for side in (-1, 1):
                if rr.random() < 0.62:
                    off = side * rr.uniform(29, 35)
                    x, y = qx - dy * off, qy + dx * off
                    if float(cp.road_at(x, y)) < 27 or not (-40 < x < GW + 40 and -40 < y < GH + 60):
                        continue
                    w = to_world(x, y)
                    if float(cp.spot_dist(np.float32(w.x), np.float32(w.y))) < 0.85:
                        continue
                    if cp.rivers and float(cp.river_e(np.float32(x), np.float32(y))[0]) < 1.25:
                        continue
                    if cp.E is not None and float(cp._grid(cp.E, x, y)) < 62:
                        continue
                    w.z = cp.height_at(w.x, w.y)
                    lote.pebble(pebble_m, (w.x, w.y, w.z + 0.01), rr.uniform(0.055, 0.1), squash=0.62, rot=rr.uniform(0, TAU), rr=rr)
            dist += rr.uniform(5.5, 8.5)
        # calcamento (ruinas e cidadela): lajes antigas meio cobertas de areia
        if th.get('paved'):
            pav = mat('laje_estrada_' + L['theme'], th['paved'], rough=0.85, var=0.2, bump=0.25)
            dist = 0.0
            while dist < cum[-1]:
                i = max(1, min(int(np.searchsorted(cum, dist)), len(P_) - 1))
                a, b = P_[i - 1], P_[i]
                t = (dist - cum[i - 1]) / max(seg[i - 1], 1e-6)
                qx, qy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                dx, dy = (b[0] - a[0]) / max(seg[i - 1], 1e-6), (b[1] - a[1]) / max(seg[i - 1], 1e-6)
                for j in range(-2, 3):
                    if rr.random() < 0.45:
                        continue
                    off = j * 9.5 + rr.uniform(-1.5, 1.5)
                    x, y = qx - dy * off, qy + dx * off
                    w = to_world(x, y)
                    w.z = cp.height_at(w.x, w.y)
                    ang = math.atan2(-dy * SIN, dx) if abs(dx) > 1e-3 or abs(dy) > 1e-3 else 0
                    lote.pebble(pav, (w.x, w.y, w.z - 0.012), rr.uniform(0.11, 0.14), squash=0.18, rot=ang + rr.uniform(-0.2, 0.2), rr=rr, sub=2, rough=0.08)
                dist += 10.0
    # lotes: terra batida e um anel de seixos (a torre cobre tudo)
    for s in L['spots']:
        if s['high']:
            c = mesa_center(s)
            build_mesa(root, P, th, c, rr, L['theme'])
            base = Vector((c.x, c.y, MESA_H))
        else:
            base = to_world(s['x'], s['y'])
            base.z = cp.height_at(base.x, base.y)
        if th.get('mata'):
            deck_pad(lote, MT, (base.x, base.y, base.z), 0.66, rr, ang=rr.uniform(-0.2, 0.2))
            continue
        n = 24
        for k in range(n):
            a = TAU * k / n + rr.uniform(-0.04, 0.04)
            r = 0.78 + rr.uniform(-0.02, 0.02)
            lote.pebble(rim_m, (base.x + r * math.cos(a), base.y + r * math.sin(a), base.z + 0.005), rr.uniform(0.09, 0.12), squash=0.6,
                        rot=a + rr.uniform(-0.3, 0.3), rr=rr)
    # saida: pilares da muralha com a bandeira do reino
    teal_banner = mat('estandarte_saida', '#4f9a44' if th.get('mata') else '#23968f', rough=0.8, var=0.02, bump=0.06, sheen=0.4)
    stone_m = mat('pilar_saida', '#a87850' if th.get('mata') else '#e0bf8e', rough=0.82, var=0.08, bump=0.3)
    for p in L['paths']:
        # caminho que termina no meio da tela (junta noutro) nao tem portal
        if 40 < p[-1][0] < GW - 40 and 40 < p[-1][1] < GH - 40:
            continue
        k = len(p) - 1
        while k > 0 and (p[k][0] < 24 or p[k][0] > GW - 24 or p[k][1] < 30 or p[k][1] > GH - 24):
            k -= 1
        q, q0 = p[k], p[max(0, k - 3)]
        dx, dy = q[0] - q0[0], q[1] - q0[1]
        ln = math.hypot(dx, dy) or 1
        nx_, ny_ = -dy / ln, dx / ln
        for side in (-1, 1):
            x, y = q[0] + nx_ * side * 44, q[1] + ny_ * side * 44
            w = to_world(x, y)
            w.z = cp.height_at(w.x, w.y)
            gate_post(root, f'saida{side}_{k}', P, tuple(w), stone_m, teal_banner, rr, s=1.35)
    place = Lugar(cp, L, rr)
    for s in L['spots']:
        place.placed.append((s['x'], s['y']))
    # pontes onde a estrada cruza o rio, e estiva nas baixadas da cheia
    for k, pt in enumerate(L.get('pontes', [])):
        build_bridge(cp, L, root, k, pt, rr)
    for k, seg in enumerate(cp.estiva):
        build_estiva(cp, lote, seg, rr)
    THEME_FN[L['theme']](L, root, P, th, cp, place, lote, rr, out, dict(grass=grass_m, grass2=grass2_m, dry=dry_m, pebble=pebble_m))
    lote.done(root)
    out['_cp'] = cp
    return out


ROAD_W = 58   # largura da estrada na tela (px do jogo)


def road_dir(L, x, y):
    """Direcao (na tela) do trecho de estrada mais perto de (x, y)."""
    best, bd = (1.0, 0.0), 1e9
    for p in L['paths']:
        for a, b in zip(p[:-1], p[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy or 1e-6
            t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
            d = math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)
            if d < bd:
                ln = math.sqrt(L2)
                bd, best = d, (dx / ln, dy / ln)
    return best


def world_width(nx, ny, px):
    """Largura no chao (unidades do Blender) de px pixels da tela na direcao lateral (nx, ny)."""
    return math.hypot(nx * px / GB, ny * px / (GB * SIN))


def build_bridge(cp, L, root, k, pt, rr):
    x, y = pt[0], pt[1]
    ux, uy = road_dir(L, x, y)
    # anda pela estrada ate sair do rio dos dois lados
    ends = []
    for sg in (-1, 1):
        t = 0
        while t < 320 and float(cp.river_e(np.float32(x + ux * t * sg), np.float32(y + uy * t * sg))[0]) < 1.22:
            t += 4
        ends.append((x + ux * (t + 10) * sg, y + uy * (t + 10) * sg))
    a, b = (to_world(*ends[0]), to_world(*ends[1]))
    a.z = cp.height_at(a.x, a.y)
    b.z = cp.height_at(b.x, b.y)
    bridge(root, f'ponte{k}', MT, RT, tuple(a), tuple(b), world_width(-uy, ux, ROAD_W), rr)


def build_estiva(cp, lote, seg, rr):
    pts = [to_world(x, y) for x, y in seg]
    # tabuas a cada ~10 px de estrada
    dense = []
    for (x0, y0), (x1, y1) in zip(seg[:-1], seg[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 10))
        for i in range(n):
            dense.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    dense.append(seg[-1])
    if len(dense) < 2:
        return
    ux, uy = dense[-1][0] - dense[0][0], dense[-1][1] - dense[0][1]
    ln = math.hypot(ux, uy) or 1
    w = world_width(-uy / ln, ux / ln, ROAD_W * 0.92)
    boardwalk(lote, MT, [tuple(to_world(x, y)) for x, y in dense], w, 0.02, rr)


def build_mesa(root, P, th, c, rr, theme):
    """Mesa de pedra macia sob um lote alto (+15% de alcance): degraus arredondados e topo plano."""
    rock_c = th.get('rock', '#8f8b7e' if th.get('mata') else '#c9a06c')
    m1 = mat('mesa_' + theme, rock_c, rough=0.88, var=0.08, bump=0.3)
    m2 = mat('mesa2_' + theme, th.get('rock2', '#76736a' if th.get('mata') else '#b08756'), rough=0.9, var=0.08, bump=0.3)
    top = mat('mesa_topo_' + theme, th['sand'], rough=0.92, var=0.04, bump=0.15)
    s = rr.random() * 20

    def wob(a, z):
        return 0.06 * noise.noise(Vector((math.cos(a) * 1.5 + s, math.sin(a) * 1.5, z * 2))) + 0.025 * math.sin(a * 6 + s)
    H_ = MESA_H
    prof = [(-0.1, 1.42, 1.32), (0.12, 1.38, 1.28), (0.3, 1.3, 1.2), (0.36, 1.25, 1.16), (0.55, 1.2, 1.12), (H_ - 0.06, 1.16, 1.08), (H_, 1.12, 1.04)]
    o = lathe(root, f'mesa_{s:.2f}', prof, m1, segs=40, wobble=wob, lv=1)
    o.location = (c.x, c.y, 0)
    band = lathe(root, f'mesa_faixa_{s:.2f}', [(0.3, 1.31, 1.21), (0.4, 1.27, 1.18)], m2, segs=40, wobble=wob, lv=1, caps=False)
    band.location = (c.x, c.y, 0.005)
    cap = cyl(root, f'mesa_topo_{s:.2f}', 1.1, 0.03, (c.x, c.y, H_ - 0.005), m=top, v=40, bev=0.02)
    cap.scale = (1, 1.04 / 1.12 * 1.07, 1)
    return o


# ---------------------------------------------------------------- enfeites por tema
def deco_palms(place, cp, out, pts, rr, smin=0.85, smax=1.1):
    for (x, y) in pts:
        w = place.ground(x, y)
        v = rr.randrange(len(PALM_VARIANTS))
        s = rr.uniform(smin, smax)
        out['palms'].append([v, round(to_game(w)[0], 1), round(to_game(w)[1], 1), round(s, 3), rr.random()])


def add_palm_shadows(root, P, out):
    """Palmeiras so como sombra no fundo (a imagem delas vem dos sprites que balancam)."""
    for i, (v, gx, gy, s, ph) in enumerate(out['palms']):
        sub = make_root(f'palm_bg{i}', root['set'], root.users_collection[0])
        pv = PALM_VARIANTS[v]
        objs = palm(sub, f'pbg{i}', P, s=s, seed=pv['seed'], lean=pv['lean'], animate=False)
        for o in objs:
            o.visible_camera = False
            o.visible_glossy = False
        sub.location = to_world(gx, gy)


def deco_common(place, root, P, th, cp, lote, rr, m, rocks=10, bushes=0, tufts=0, dry=0, rock_m=None, bush_m=None):
    rock_m = rock_m or mat('rocha_cen', '#b9a084', rough=0.85, var=0.12, bump=0.3)
    for k, (x, y) in enumerate(place.take(rocks, 14)):
        w = place.ground(x, y)
        if rr.random() < 0.35:
            rock_cluster(root, f'rocha{k}', rock_m, tuple(w), rr.uniform(0.3, 0.46), rr, n=3)
        else:
            rock(root, f'rocha{k}', rock_m, tuple(w), rr.uniform(0.26, 0.5), rr)
    bm_ = bush_m or mat('arbusto_cen', '#6f9a45', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    bm2 = mat('arbusto_cen2', '#89b053', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    for k, (x, y) in enumerate(place.take(bushes, 12)):
        w = place.ground(x, y)
        bush(root, f'arbusto{k}', bm_, tuple(w), rr.uniform(0.34, 0.5), rr, m2=bm2)
    for k, (x, y) in enumerate(place.take(tufts, 6, path_d=36)):
        w = place.ground(x, y)
        tuft(lote, m['grass'], tuple(w), rr.uniform(0.24, 0.36), rr, m2=m['grass2'])
    for k, (x, y) in enumerate(place.take(dry, 8)):
        w = place.ground(x, y)
        drybush(lote, m['dry'], tuple(w), rr.uniform(0.3, 0.46), rr)


def pond_life(L, root, P, cp, place, lote, rr, out, m, palms_per=6):
    reed_m = mat('junco', '#7e9a46', rough=0.8, var=0.15, bump=0.05)
    head_m = mat('taboa', '#7a4b2a', rough=0.85, var=0.1, bump=0.1)
    lily_m = mat('vitoria_regia', '#5e9b46', rough=0.6, var=0.12, bump=0.05)
    flower_m = mat('flor_lagoa', '#f2a0b8', rough=0.6, var=0.1, bump=0.0)
    wrock = mat('rocha_lagoa', '#c4b8a6', rough=0.8, var=0.12, bump=0.25)
    for (x, y, rx, ry) in cp.water:
        # capim em volta, juncos na margem, vitorias-regias na agua
        for k in range(int(rx * 0.9)):
            a = rr.uniform(0, TAU)
            e = rr.uniform(1.06, 1.42)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            if float(cp.road_at(gx, gy)) < 40:
                continue
            w = place.ground(gx, gy)
            tuft(lote, m['grass'], tuple(w), rr.uniform(0.2, 0.3), rr, m2=m['grass2'])
        for k in range(7):
            a = rr.uniform(0, TAU)
            if math.sin(a) > 0.55:   # na margem da frente os juncos cobririam a agua
                continue
            e = rr.uniform(0.94, 1.04)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            w = to_world(gx, gy)
            w.z = max(-0.05, cp.height_at(w.x, w.y))
            reeds(lote, reed_m, head_m, tuple(w), rr.uniform(0.5, 0.75), rr)
        for k in range(int(3 + rx / 40)):
            a = rr.uniform(0, TAU)
            e = rr.uniform(0.25, 0.75)
            w = to_world(x + rx * e * math.cos(a), y + ry * e * math.sin(a), -0.045)
            lote.disc(lily_m, (w.x, w.y, -0.048), rr.uniform(0.14, 0.22), notch=0.6, rot=rr.uniform(0, TAU), h=0.008)
            if rr.random() < 0.5:
                sphere(root, f'flor_lagoa{k}_{x}', 0.055, (w.x + 0.03, w.y, -0.025), scale=(1, 1, 0.7), m=flower_m, seg=10)
        w = to_world(x + rx * 0.2, y - ry * 0.05, -0.05)
        rock(root, f'rocha_agua{x}', wrock, (w.x, w.y, -0.05), 0.24, rr, sink=0.4)
        # palmeiras em volta (nunca na frente da agua)
        pts = []
        for k in range(palms_per * 4):
            if len(pts) >= palms_per:
                break
            a = rr.uniform(math.pi * 1.05, math.pi * 1.95) if rr.random() < 0.75 else rr.uniform(-0.25, 0.25) + (0 if rr.random() < 0.5 else math.pi)
            e = rr.uniform(1.28, 1.7)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            if place.far_path(gx, gy, 50) and place.far_spot(gx, gy, 50) and place.hud_free(gx, gy) and place.clear_above(gx, gy, 80, 30) and place.free(gx, gy, 30):
                place.placed.append((gx, gy))
                pts.append((gx, gy))
        deco_palms(place, cp, out, pts, rr)


def theme_oasis(L, root, P, th, cp, place, lote, rr, out, m):
    return theme_igarape(L, root, P, th, cp, place, lote, rr, out, m)


def mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=12, ferns=34, bromel=22, helic=16, leaves=22, logs=4, rocks=10, tufts=130, flw=40, moita=60):
    """Chao de mata: arvores grandes nas bordas (copa para fora da tela), samambaias, bromelias, heliconias, folhagens,
    troncos com musgo, pedras de rio, capim e florzinhas."""
    Mt = MT
    edge = lambda x, y: x < 120 or x > W_EDGE - 120 or y < 70
    for k, (x, y) in enumerate(place.take(trees, 46, tall=(160, 70), path_d=60, test=edge)):
        jungle_tree(root, f'arvore{k}', Mt, tuple(place.ground(x, y)), rr.uniform(1.0, 1.35), rr)
    # moita densa onde a trilha e os lotes estao longe (bordas da tela e miolos vazios)
    far = lambda x, y: float(cp.road_at(x, y)) > 110 and place.far_spot(x, y, 105)
    for k, (x, y) in enumerate(place.take(moita, 18, test=far)):
        g = place.ground(x, y)
        kind = rr.random()
        if kind < 0.35:
            fern(root, f'moita_s{k}', Mt, tuple(g), rr.uniform(0.9, 1.25), rr)
        elif kind < 0.6:
            big_leaves(root, f'moita_f{k}', Mt, tuple(g), rr.uniform(1.3, 1.7), rr, n=6)
        elif kind < 0.78:
            bush(root, f'moita_a{k}', Mt['leaf_d'], tuple(g), rr.uniform(0.4, 0.6), rr, m2=Mt['leaf'])
        elif kind < 0.9:
            heliconia(root, f'moita_h{k}', Mt, tuple(g), rr.uniform(1.3, 1.6), rr)
        else:
            bromeliad(root, f'moita_b{k}', Mt, tuple(g), rr.uniform(1.4, 1.8), rr, center=Mt['red'])
    for k, (x, y) in enumerate(place.take(ferns, 16)):
        fern(root, f'samambaia{k}', Mt, tuple(place.ground(x, y)), rr.uniform(0.75, 1.05), rr)
    for k, (x, y) in enumerate(place.take(bromel, 10)):
        bromeliad(root, f'bromelia{k}', Mt, tuple(place.ground(x, y)), rr.uniform(1.2, 1.6), rr, center=rr.choice((Mt['pink'], Mt['red'], Mt['orange'])))
    for k, (x, y) in enumerate(place.take(helic, 14, tall=(50, 18))):
        heliconia(root, f'heliconia{k}', Mt, tuple(place.ground(x, y)), rr.uniform(1.2, 1.5), rr)
    for k, (x, y) in enumerate(place.take(leaves, 14)):
        big_leaves(root, f'folhagem{k}', Mt, tuple(place.ground(x, y)), rr.uniform(1.1, 1.5), rr)
    for k, (x, y) in enumerate(place.take(logs, 30)):
        log(root, f'tronco{k}', Mt, tuple(place.ground(x, y)), rr.uniform(1.2, 1.5), rr)
    for k, (x, y) in enumerate(place.take(rocks, 14)):
        mossy_rock(root, f'pedra{k}', Mt, tuple(place.ground(x, y)), rr.uniform(0.3, 0.5), rr)
    for k, (x, y) in enumerate(place.take(tufts, 6, path_d=34)):
        grass_tuft(lote, Mt, tuple(place.ground(x, y)), rr.uniform(0.28, 0.42), rr)
    for k, (x, y) in enumerate(place.take(flw, 6, path_d=34)):
        flowers(lote, Mt, tuple(place.ground(x, y)), rr.uniform(0.7, 1.0), rr)


W_EDGE = GW


def igarape_life(L, root, P, cp, place, lote, rr, out, palms_per=4):
    """Margem de igarape: vitorias-regias, juncos, palafita com canoa e palmeiras de acai em volta."""
    Mt = MT
    reed_m = mat('junco', '#7e9a46', rough=0.8, var=0.15, bump=0.05)
    head_m = mat('taboa', '#7a4b2a', rough=0.85, var=0.1, bump=0.1)
    for i, (x, y, rx, ry) in enumerate(cp.water):
        for k in range(int(4 + rx / 22)):
            a = rr.uniform(0, TAU)
            e = rr.uniform(0.2, 0.78)
            w = to_world(x + rx * e * math.cos(a), y + ry * e * math.sin(a), -0.045)
            vitoria_regia(lote, Mt, (w.x, w.y, -0.046), rr.uniform(0.16, 0.26), rr)
            if rr.random() < 0.35:
                sphere(root, f'flor_lagoa{i}_{k}', 0.06, (w.x + 0.05, w.y, -0.02), scale=(1, 1, 0.7), m=Mt['white'] if k % 2 else Mt['pink'], seg=10)
        for k in range(8):
            a = rr.uniform(0, TAU)
            if math.sin(a) > 0.55:
                continue
            e = rr.uniform(0.94, 1.04)
            w = to_world(x + rx * e * math.cos(a), y + ry * e * math.sin(a))
            w.z = max(-0.05, cp.height_at(w.x, w.y))
            reeds(lote, reed_m, head_m, tuple(w), rr.uniform(0.5, 0.75), rr)
        for k in range(int(rx * 0.9)):
            a = rr.uniform(0, TAU)
            e = rr.uniform(1.06, 1.45)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            if float(cp.road_at(gx, gy)) < 40 or not place.far_spot(gx, gy, 40):
                continue
            grass_tuft(lote, Mt, tuple(place.ground(gx, gy)), rr.uniform(0.22, 0.32), rr)
        # palafita na margem de tras e canoa na agua
        for k in range(10):
            a = rr.uniform(math.pi * 1.15, math.pi * 1.85)
            e = rr.uniform(0.95, 1.1)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            if place.far_path(gx, gy, 70) and place.far_spot(gx, gy, 70) and place.hud_free(gx, gy) and place.clear_above(gx, gy, 70, 44) and place.free(gx, gy, 50):
                place.placed.append((gx, gy))
                w = to_world(gx, gy)
                w.z = max(-0.05, cp.height_at(w.x, w.y))
                palafita(root, f'palafita{i}', Mt, tuple(w), rr.uniform(1.3, 1.5), rr, ang=rr.uniform(-0.25, 0.25))
                cw = to_world(gx + rr.uniform(-30, 30), gy + ry * 0.45, -0.05)
                canoe(root, f'canoa{i}', Mt, (cw.x, cw.y, -0.07), 0.8, rr.uniform(-0.4, 0.4), rr)
                break
        pts = []
        for k in range(palms_per * 4):
            if len(pts) >= palms_per:
                break
            a = rr.uniform(math.pi * 1.05, math.pi * 1.95) if rr.random() < 0.75 else rr.uniform(-0.25, 0.25) + (0 if rr.random() < 0.5 else math.pi)
            e = rr.uniform(1.3, 1.75)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            if place.far_path(gx, gy, 50) and place.far_spot(gx, gy, 50) and place.hud_free(gx, gy) and place.clear_above(gx, gy, 80, 30) and place.free(gx, gy, 30):
                place.placed.append((gx, gy))
                pts.append((gx, gy))
        deco_palms(place, cp, out, pts, rr)


def theme_igarape(L, root, P, th, cp, place, lote, rr, out, m):
    igarape_life(L, root, P, cp, place, lote, rr, out)
    deco_palms(place, cp, out, place.take(6, 26, tall=(80, 30)), rr, 0.85, 1.1)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m)


def theme_oasis_deserto(L, root, P, th, cp, place, lote, rr, out, m):
    pond_life(L, root, P, cp, place, lote, rr, out, m)
    deco_palms(place, cp, out, place.take(9, 26, tall=(80, 30)), rr, 0.8, 1.05)
    for k, (x, y) in enumerate(place.take(2, 30, tall=(36, 28))):
        tent(root, f'tenda{k}', P, tuple(place.ground(x, y)), rr, ang=rr.uniform(-0.5, 0.5) + math.pi * 0.5, s=1.35)
    for k, (x, y) in enumerate(place.take(3, 10)):
        jars(root, f'jarros{k}', P, tuple(place.ground(x, y)), rr, s=1.5)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=12, bushes=20, tufts=60)


def theme_canyon(L, root, P, th, cp, place, lote, rr, out, m, rock_n=22):
    rm = mat('rocha_' + L['theme'], th['rock'], rough=0.88, var=0.1, bump=0.3)
    rm2 = mat('rocha2_' + L['theme'], th['rock2'], rough=0.9, var=0.1, bump=0.3)
    for k, (x, y) in enumerate(place.take(10, 62, tall=(110, 66), path_d=50)):
        w = place.ground(x, y)
        rx = rr.uniform(1.0, 1.7)
        strata_rock(root, f'rochedo{k}', rm, rm2, tuple(w), rx, rx * rr.uniform(0.7, 0.9), rr.uniform(0.9, 1.7), rr, layers=rr.choice((3, 4, 5)))
    cm = mat('cacto_cen', '#6a9a50', rough=0.75, var=0.08, bump=0.2)
    if L['theme'] == 'canyon':
        for k, (x, y) in enumerate(place.take(6, 12, tall=(40, 14))):
            cactus(root, f'cacto{k}', cm, tuple(place.ground(x, y)), rr.uniform(0.4, 0.62), rr)
    bone_m = mat('osso', '#efe4c8', rough=0.6, var=0.04, bump=0.1)
    for k, (x, y) in enumerate(place.take(3, 16)):
        bones(root, f'ossada{k}', bone_m, tuple(place.ground(x, y)), rr, s=rr.uniform(0.8, 1.1))
    if L['theme'] == 'storm':
        for k, (x, y) in enumerate(place.take(3, 8)):
            skull_horns(root, f'cranio{k}', bone_m, tuple(place.ground(x, y)), rr)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=rock_n, dry=20, tufts=8, rock_m=rm)


def theme_ruins(L, root, P, th, cp, place, lote, rr, out, m):
    st = mat('coluna', '#e6d4b0', rough=0.8, var=0.06, bump=0.2)
    st2 = mat('coluna_capitel', '#d8c39c', rough=0.8, var=0.06, bump=0.2)
    wall_m = mat('muro_ruina', '#d9c195', rough=0.85, var=0.1, bump=0.25)
    wall2 = mat('muro_ruina2', '#c8ad80', rough=0.85, var=0.1, bump=0.25)
    tile_m = mat('lajota_ruina', '#d2bc94', rough=0.88, var=0.15, bump=0.25)
    # pisos antigos meio enterrados
    for k in range(14):
        pts = place.take(1, 30, path_d=40)
        if not pts:
            continue
        x, y = pts[0]
        w0 = place.ground(x, y)
        cols, rows = 3 + rr.randrange(4), 2 + rr.randrange(3)
        for a in range(cols):
            for b in range(rows):
                if rr.random() < 0.3:
                    continue
                px, py = w0.x + (a - cols / 2) * 0.5 + (b % 2) * 0.25, w0.y + (b - rows / 2) * 0.42
                gx, gy = to_game((px, py, 0))
                if not place.far_path(gx, gy, 34) or not place.far_spot(gx, gy, 46):
                    continue
                lote.pebble(tile_m, (px, py, cp.height_at(px, py) - 0.02), 0.21, squash=0.16, rot=rr.uniform(-0.06, 0.06), rr=rr, sub=2, rough=0.05)
    for k, (x, y) in enumerate(place.take(12, 16, tall=(56, 14))):
        column(root, f'coluna{k}', st, st2, tuple(place.ground(x, y)), rr.uniform(1.0, 1.35), 0.15, rr, broken=rr.random() < 0.6)
    for k, (x, y) in enumerate(place.take(6, 26)):
        fallen_column(root, f'caida{k}', st, tuple(place.ground(x, y)), 0.14, rr)
    for k, (x, y) in enumerate(place.take(6, 36, tall=(36, 34))):
        ruin_wall(root, f'muro{k}', wall_m, wall2, tuple(place.ground(x, y)), rr.uniform(1.0, 1.6), rr.uniform(0.4, 0.7), rr, ang=rr.uniform(-0.4, 0.4))
    deco_palms(place, cp, out, place.take(8, 26, tall=(80, 30)), rr, 0.8, 1.0)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=12, bushes=16, tufts=40, dry=4)


def theme_dunes(L, root, P, th, cp, place, lote, rr, out, m):
    bone_m = mat('osso', '#efe4c8', rough=0.6, var=0.04, bump=0.1)
    for k, (x, y) in enumerate(place.take(6, 16)):
        bones(root, f'ossada{k}', bone_m, tuple(place.ground(x, y)), rr, s=rr.uniform(0.9, 1.25))
    for k, (x, y) in enumerate(place.take(5, 8)):
        skull_horns(root, f'cranio{k}', bone_m, tuple(place.ground(x, y)), rr)
    deco_palms(place, cp, out, place.take(3, 26, tall=(80, 30)), rr, 0.8, 0.95)
    rm = mat('rocha_dunas', '#c9a77a', rough=0.85, var=0.1, bump=0.3)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=12, dry=26, tufts=10, rock_m=rm)


def theme_citadel(L, root, P, th, cp, place, lote, rr, out, m):
    wall_m = mat('muro_cidadela', '#b49c78', rough=0.85, var=0.1, bump=0.25)
    wall2 = mat('muro_cidadela2', '#9d8562', rough=0.85, var=0.1, bump=0.25)
    st = mat('coluna_cid', '#c9b58f', rough=0.8, var=0.06, bump=0.2)
    st2 = mat('capitel_cid', '#b7a27c', rough=0.8, var=0.06, bump=0.2)
    obm = mat('obelisco', '#b39a76', rough=0.75, var=0.05, bump=0.15)
    tile_m = mat('lajota_cid', '#a99272', rough=0.85, var=0.15, bump=0.2)
    for k in range(16):
        pts = place.take(1, 30, path_d=40)
        if not pts:
            continue
        x, y = pts[0]
        w0 = place.ground(x, y)
        cols, rows = 3 + rr.randrange(4), 2 + rr.randrange(3)
        for a in range(cols):
            for b in range(rows):
                if rr.random() < 0.25:
                    continue
                px, py = w0.x + (a - cols / 2) * 0.5 + (b % 2) * 0.25, w0.y + (b - rows / 2) * 0.42
                gx, gy = to_game((px, py, 0))
                if not place.far_path(gx, gy, 34) or not place.far_spot(gx, gy, 46):
                    continue
                lote.pebble(tile_m, (px, py, cp.height_at(px, py) - 0.02), 0.21, squash=0.16, rot=rr.uniform(-0.06, 0.06), rr=rr, sub=2, rough=0.05)
    for k, (x, y) in enumerate(place.take(10, 36, tall=(36, 34))):
        ruin_wall(root, f'muro{k}', wall_m, wall2, tuple(place.ground(x, y)), rr.uniform(1.0, 1.8), rr.uniform(0.45, 0.8), rr, ang=rr.uniform(-0.4, 0.4))
    for k, (x, y) in enumerate(place.take(5, 18, tall=(72, 12))):
        obelisk(root, f'obelisco{k}', obm, P['gold'], tuple(place.ground(x, y)), rr.uniform(1.4, 1.8), rr)
    for k, (x, y) in enumerate(place.take(8, 16, tall=(50, 12))):
        column(root, f'coluna{k}', st, st2, tuple(place.ground(x, y)), rr.uniform(0.9, 1.2), 0.15, rr, broken=True)
    for k, (x, y) in enumerate(place.take(5, 26)):
        fallen_column(root, f'caida{k}', st, tuple(place.ground(x, y)), 0.14, rr)
    # braseiros acesos (luz do cenario a noite)
    lights = []
    for k, (x, y) in enumerate(place.take(7, 14, tall=(30, 12))):
        w = place.ground(x, y)
        brazier(root, f'braseiro{k}', P, tuple(w), s=1.6, lights=lights)
        out['env'].append([round(x, 1), round(y - 14, 1), '#ff9a40'])
    bone_m = mat('osso', '#efe4c8', rough=0.6, var=0.04, bump=0.1)
    for k, (x, y) in enumerate(place.take(6, 14)):
        bones(root, f'ossada{k}', bone_m, tuple(place.ground(x, y)), rr, s=0.9)
    rm = mat('rocha_cid', '#9a8466', rough=0.85, var=0.1, bump=0.3)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=14, dry=8, rock_m=rm)
    out['glow_lights'] = lights


def theme_storm(L, root, P, th, cp, place, lote, rr, out, m):
    theme_canyon(L, root, P, th, cp, place, lote, rr, out, m, rock_n=20)


def theme_qanat(L, root, P, th, cp, place, lote, rr, out, m):
    pond_life(L, root, P, cp, place, lote, rr, out, m, palms_per=4)
    soil = mat('terra_lavoura', '#8c6a42', rough=0.95, var=0.06, bump=0.3)
    crop = mat('broto', '#79a845', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    crop2 = mat('broto2', '#a2c25a', rough=0.8, var=0.15, bump=0.1, sheen=0.3)
    for k, (x, y) in enumerate(place.take(8, 62, path_d=52)):
        w = place.ground(x, y)
        field(root, f'lavoura{k}', soil, crop if k % 2 else crop2, lote, tuple(w), rr.uniform(2.0, 2.8), rr.uniform(1.0, 1.4), rr,
              rows=rr.choice((5, 6)), ang=rr.uniform(-0.15, 0.15))
    deco_palms(place, cp, out, place.take(8, 26, tall=(80, 30)), rr, 0.8, 1.05)
    wall_m = mat('muro_adobe', '#d6b886', rough=0.85, var=0.1, bump=0.25)
    for k, (x, y) in enumerate(place.take(4, 36, tall=(36, 34))):
        ruin_wall(root, f'muro{k}', wall_m, None, tuple(place.ground(x, y)), rr.uniform(1.0, 1.5), rr.uniform(0.35, 0.5), rr, ang=rr.uniform(-0.3, 0.3))
    for k, (x, y) in enumerate(place.take(4, 10)):
        jars(root, f'jarros{k}', P, tuple(place.ground(x, y)), rr, s=1.5)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=8, bushes=20, tufts=50)


def theme_ember(L, root, P, th, cp, place, lote, rr, out, m):
    lava = glow_mat('lava', '#ff8a30', 7.0, 16.0, rough=0.5, var=0.1, bump=0.0)
    rim = mat('borda_lava', '#3a2a26', rough=0.9, var=0.1, bump=0.3)
    for i in range(24):
        x, y = rr.random() * GW, rr.random() * GH
        if not place.far_path(x, y, 44) or not place.far_spot(x, y, 50):
            continue
        # fenda organica: passeio com direcao que muda devagar, e um galho as vezes
        pts = [(x, y)]
        hd = rr.uniform(0, TAU)
        for k in range(10):
            hd += rr.uniform(-0.55, 0.55)
            x += math.cos(hd) * 9
            y += math.sin(hd) * 5.5
            pts.append((x, y))
        if not all(place.far_path(px, py, 40) and place.far_spot(px, py, 46) for px, py in pts):
            continue
        wp = [place.ground(px, py) for px, py in pts]
        lava_crack(lote, lava, rim, [tuple(w) for w in wp], rr.uniform(0.05, 0.075))
        if rr.random() < 0.6:
            j = rr.randrange(3, 7)
            hb = rr.uniform(-1.2, 1.2)
            bx, by = pts[j]
            br = [(bx, by)]
            for k in range(4):
                bx += math.cos(hb) * 8
                by += math.sin(hb) * 5
                br.append((bx, by))
                hb += rr.uniform(-0.4, 0.4)
            lava_crack(lote, lava, rim, [tuple(place.ground(px, py)) for px, py in br], 0.04)
        out['env'].append([round(pts[5][0], 1), round(pts[5][1], 1), '#ff6a1a'])
    obm = mat('obelisco_negro', '#4a3c3a', rough=0.6, var=0.05, bump=0.15)
    for k, (x, y) in enumerate(place.take(4, 18, tall=(72, 12))):
        obelisk(root, f'obelisco{k}', obm, P['gold'], tuple(place.ground(x, y)), rr.uniform(1.4, 1.7), rr)
    bone_m = mat('osso_cinza', '#d9cdb4', rough=0.6, var=0.04, bump=0.1)
    for k, (x, y) in enumerate(place.take(6, 14)):
        bones(root, f'ossada{k}', bone_m, tuple(place.ground(x, y)), rr, s=0.95)
    for k, (x, y) in enumerate(place.take(6, 8)):
        skull_horns(root, f'cranio{k}', bone_m, tuple(place.ground(x, y)), rr)
    rm = mat('obsidiana', th['rock'], rough=0.45, var=0.1, bump=0.25)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=22, dry=10, rock_m=rm)


# ---------------------------------------------------------------- fases da mata (2 a 8)
def grass_cap(root, name, Mt, loc, rx, ry, z):
    """Tampa de capim sobre um barranco ou pedra."""
    return sphere(root, name, 1.0, (loc[0], loc[1], loc[2] + z), scale=(rx, ry, 0.12), m=Mt['moss'], seg=24)


def theme_barranco(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    rm = mat('barro', th['rock'], rough=0.88, var=0.1, bump=0.35)
    rm2 = mat('barro2', th['rock2'], rough=0.9, var=0.1, bump=0.35)
    for k, (x, y) in enumerate(place.take(10, 62, tall=(110, 66), path_d=50)):
        w = place.ground(x, y)
        rx = rr.uniform(1.0, 1.6)
        ry = rx * rr.uniform(0.7, 0.9)
        objs, top = strata_rock(root, f'barranco{k}', rm, rm2, tuple(w), rx, ry, rr.uniform(0.8, 1.5), rr, layers=rr.choice((3, 4)))
        grass_cap(root, f'barranco{k}_capim', Mt, tuple(w), rx * 0.62, ry * 0.62, top - 0.02)
        for j in range(3):
            a = rr.uniform(0, TAU)
            fern(root, f'barranco{k}_sam{j}', Mt, (w.x + rx * 0.35 * math.cos(a), w.y + ry * 0.35 * math.sin(a), w.z + top), rr.uniform(0.5, 0.7), rr)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=10, ferns=24, bromel=14, helic=10, leaves=16, logs=3, rocks=8, tufts=100, flw=24)


def theme_cidade(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    st = mat('pedra_antiga', '#a9a58e', rough=0.85, var=0.1, bump=0.3)
    st2 = mat('pedra_antiga2', '#8f8b74', rough=0.85, var=0.1, bump=0.3)
    for k, (x, y) in enumerate(place.take(10, 16, tall=(56, 14))):
        w = place.ground(x, y)
        column(root, f'coluna{k}', st, st2, tuple(w), rr.uniform(1.0, 1.35), 0.15, rr, broken=rr.random() < 0.6)
        sphere(root, f'coluna{k}_musgo', 0.2, (w.x, w.y, w.z + 0.06), scale=(1.3, 1.3, 0.35), m=Mt['moss'], seg=14)
    for k, (x, y) in enumerate(place.take(5, 26)):
        fallen_column(root, f'caida{k}', st, tuple(place.ground(x, y)), 0.14, rr)
    for k, (x, y) in enumerate(place.take(6, 36, tall=(36, 34))):
        w = place.ground(x, y)
        a = rr.uniform(-0.4, 0.4)
        ruin_wall(root, f'muro{k}', st, st2, tuple(w), rr.uniform(1.0, 1.6), rr.uniform(0.4, 0.7), rr, ang=a)
        grass_cap(root, f'muro{k}_musgo', Mt, tuple(w), 0.45, 0.2, 0.45)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=12, ferns=30, bromel=16, helic=10, leaves=20, logs=3, rocks=6, tufts=110, flw=20)
    deco_palms(place, cp, out, place.take(5, 26, tall=(80, 30)), rr, 0.85, 1.05)


def theme_varzea(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    reed_m = mat('junco', '#7e9a46', rough=0.8, var=0.15, bump=0.05)
    head_m = mat('taboa', '#7a4b2a', rough=0.85, var=0.1, bump=0.1)
    wet = lambda x, y: (lambda w: cp.height_at(w.x, w.y) < -0.09)(to_world(x, y))
    dry = lambda x, y: not wet(x, y)
    # arvores da varzea com o pe dentro d'agua
    for k, (x, y) in enumerate(place.take(9, 46, tall=(160, 70), path_d=70, test=wet)):
        w = to_world(x, y, -0.06)
        jungle_tree(root, f'arvoreVarzea{k}', Mt, (w.x, w.y, -0.06), rr.uniform(0.9, 1.2), rr)
    for k, (x, y) in enumerate(place.take(40, 8, test=wet, path_d=40)):
        w = to_world(x, y, -0.06)
        vitoria_regia(lote, Mt, (w.x, w.y, -0.058), rr.uniform(0.14, 0.24), rr)
    for k, (x, y) in enumerate(place.take(18, 8, test=lambda x, y: wet(x, y) and not wet(x + 14, y), path_d=40)):
        w = to_world(x, y)
        reeds(lote, reed_m, head_m, (w.x, w.y, -0.06), rr.uniform(0.5, 0.75), rr)
    for k, (x, y) in enumerate(place.take(2, 30, test=wet, path_d=60)):
        w = to_world(x, y, -0.06)
        canoe(root, f'canoaVarzea{k}', Mt, (w.x, w.y, -0.08), 0.8, rr.uniform(-0.5, 0.5), rr)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=4, ferns=18, bromel=10, helic=8, leaves=12, logs=2, rocks=4, tufts=90, flw=14)
    deco_palms(place, cp, out, place.take(6, 26, tall=(80, 30), test=dry), rr, 0.85, 1.05)


def theme_gruta(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    st = mat('pedra_gruta', '#6f6c60', rough=0.85, var=0.12, bump=0.35)
    st2 = mat('pedra_gruta2', '#59574e', rough=0.85, var=0.12, bump=0.35)
    for k, (x, y) in enumerate(place.take(9, 40, tall=(90, 40), path_d=50)):
        w = place.ground(x, y)
        rx = rr.uniform(0.6, 1.0)
        objs, top = strata_rock(root, f'rochaGruta{k}', st, st2, tuple(w), rx, rx * 0.8, rr.uniform(0.9, 1.6), rr, layers=3)
        grass_cap(root, f'rochaGruta{k}_musgo', Mt, tuple(w), rx * 0.55, rx * 0.45, top - 0.02)
    for k, (x, y) in enumerate(place.take(6, 36, tall=(36, 34))):
        ruin_wall(root, f'muroGruta{k}', st, st2, tuple(place.ground(x, y)), rr.uniform(1.0, 1.5), rr.uniform(0.4, 0.7), rr, ang=rr.uniform(-0.4, 0.4))
    lights = []
    for k, (x, y) in enumerate(place.take(12, 14)):
        w = place.ground(x, y)
        glow_mushrooms(root, f'cogumelos{k}', Mt, tuple(w), rr.uniform(1.0, 1.5), rr, lights=lights)
        out['env'].append([round(x, 1), round(y - 10, 1), '#7ff0d0'])
    out['glow_lights'] = lights
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=10, ferns=30, bromel=8, helic=4, leaves=20, logs=4, rocks=10, tufts=80, flw=6)


def theme_temporal(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    rm = mat('pedra_negra', th['rock'], rough=0.7, var=0.1, bump=0.3)
    wet = lambda x, y: (lambda w: cp.height_at(w.x, w.y) < -0.09)(to_world(x, y))
    for k, (x, y) in enumerate(place.take(16, 16)):
        w = place.ground(x, y)
        rock_cluster(root, f'pedraNegra{k}', rm, tuple(w), rr.uniform(0.25, 0.4), rr, n=3)
    for k, (x, y) in enumerate(place.take(2, 30, test=wet, path_d=60)):
        w = to_world(x, y, -0.06)
        canoe(root, f'canoaTemporal{k}', Mt, (w.x, w.y, -0.08), 0.8, rr.uniform(-0.5, 0.5), rr)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=10, ferns=26, bromel=8, helic=6, leaves=18, logs=4, rocks=6, tufts=90, flw=6)
    deco_palms(place, cp, out, place.take(8, 26, tall=(80, 30), test=lambda x, y: not wet(x, y)), rr, 0.85, 1.1)


def theme_furos(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    igarape_life(L, root, P, cp, place, lote, rr, out, palms_per=4)
    soil = mat('terra_roca', '#6a4a30', rough=0.95, var=0.06, bump=0.35)
    for k, (x, y) in enumerate(place.take(7, 62, path_d=52)):
        w = place.ground(x, y)
        field(root, f'roca{k}', soil, Mt['leaf'] if k % 2 else Mt['leaf_l'], lote, tuple(w), rr.uniform(2.0, 2.8), rr.uniform(1.0, 1.4), rr,
              rows=rr.choice((4, 5)), ang=rr.uniform(-0.15, 0.15))
    for k, (x, y) in enumerate(place.take(2, 50, tall=(70, 44))):
        w = place.ground(x, y)
        palafita(root, f'palafitaFuro{k}', Mt, tuple(w), rr.uniform(1.2, 1.4), rr, ang=rr.uniform(-0.3, 0.3))
    deco_palms(place, cp, out, place.take(8, 26, tall=(80, 30)), rr, 0.85, 1.05)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=8, ferns=20, bromel=12, helic=10, leaves=14, logs=3, rocks=6, tufts=100, flw=20)


def theme_queimada(L, root, P, th, cp, place, lote, rr, out, m):
    Mt = MT
    rim = mat('borda_brasa', '#2a2220', rough=0.9, var=0.1, bump=0.3)
    for i in range(26):
        x, y = rr.random() * GW, rr.random() * GH
        if not place.far_path(x, y, 44) or not place.far_spot(x, y, 50):
            continue
        pts = [(x, y)]
        hd = rr.uniform(0, TAU)
        for k in range(10):
            hd += rr.uniform(-0.55, 0.55)
            x += math.cos(hd) * 9
            y += math.sin(hd) * 5.5
            pts.append((x, y))
        if not all(place.far_path(px, py, 40) and place.far_spot(px, py, 46) for px, py in pts):
            continue
        lava_crack(lote, Mt['ember'], rim, [tuple(place.ground(px, py)) for px, py in pts], rr.uniform(0.04, 0.06))
        out['env'].append([round(pts[5][0], 1), round(pts[5][1], 1), '#ff6a1a'])
    for k, (x, y) in enumerate(place.take(18, 22, tall=(60, 20))):
        charred_trunk(root, f'toco{k}', Mt, tuple(place.ground(x, y)), rr.uniform(0.9, 1.4), rr)
    char_log = mat('tora_queimada', '#2e2622', rough=0.9, var=0.1, bump=0.5)
    for k, (x, y) in enumerate(place.take(8, 30)):
        w = place.ground(x, y)
        cyl(root, f'toraQueimada{k}', 0.15, rr.uniform(0.9, 1.4), (w.x, w.y, w.z + 0.12), m=char_log, v=14, bev=0.03, rot=(math.pi / 2, 0, rr.uniform(0, TAU)))
    rm = mat('pedra_cinza', th['rock'], rough=0.6, var=0.1, bump=0.25)
    deco_common(place, root, P, th, cp, lote, rr, m, rocks=16, dry=10, rock_m=rm)


# ---------------------------------------------------------------- Rio das Duas Aguas (fases 9 a 12)
def _er(cp, x, y):
    return float(cp.river_e(np.float32(x), np.float32(y))[0]) if cp.rivers else 9.0


def _ew(cp, x, y):
    return float(cp.water_e(np.float32(x), np.float32(y)))


def river_angle(L, cp, x, y):
    """Angulo (no chao) do rio mais perto de (x, y)."""
    best, bd = 0.0, 1e9
    for rv in L.get('rivers', []):
        for a, b in zip(rv['pts'][:-1], rv['pts'][1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy or 1e-6
            t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
            d = math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)
            if d < bd:
                bd, best = d, math.atan2(-dy / SIN, dx)
    return best


def river_area(L, rr, lo, hi, cp=None):
    """Sorteia um ponto ao longo dos rios (e das lagoas), a uma distancia do eixo entre lo e hi meias-larguras."""
    rivers = L.get('rivers', [])
    ponds = cp.water if cp is not None else L.get('water', [])

    def pick():
        if ponds and (not rivers or rr.random() < 0.3):
            x, y, rx, ry = rr.choice(ponds)
            a = rr.uniform(0, TAU)
            e = rr.uniform(lo, hi)
            return x + rx * e * math.cos(a), y + ry * e * math.sin(a)
        rv = rr.choice(rivers)
        P_ = rv['pts']
        i = rr.randrange(len(P_) - 1)
        (ax, ay), (bx, by) = P_[i], P_[i + 1]
        t = rr.random()
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) or 1
        off = rv['w'] / 2.0 * rr.uniform(lo, hi) * rr.choice((-1, 1))
        return ax + dx * t - dy / ln * off, ay + dy * t + dx / ln * off
    return pick


def bank_trees(L, root, cp, place, rr, n, lo=1.3, hi=2.4, s=(0.9, 1.2)):
    for k, (x, y) in enumerate(place.take(n, 46, tall=(160, 70), path_d=60, area=river_area(L, rr, lo, hi, cp),
                                          test=lambda x, y: lo <= min(_er(cp, x, y), _ew(cp, x, y)) <= hi)):
        jungle_tree(root, f'arvoreMargem{k}', MT, tuple(place.ground(x, y)), rr.uniform(*s), rr)


def theme_encontro(L, root, P, th, cp, place, lote, rr, out, m):
    Mt, R = MT, RT
    mid = lambda lo, hi: (lambda x, y: lo <= _er(cp, x, y) <= hi)
    # barco de recreio no meio do rio, flutuantes perto da margem, canoas
    for k, (x, y) in enumerate(place.take(1, 60, test=mid(0, 0.4), water_ok=True, path_d=80, area=river_area(L, rr, 0, 0.3))):
        w = to_world(x, y, -0.05)
        river_boat(root, f'recreio{k}', Mt, R, (w.x, w.y, -0.05), 1.3, river_angle(L, cp, x, y) + rr.choice((0, math.pi)), rr)
    for k, (x, y) in enumerate(place.take(2, 44, test=mid(0.5, 0.78), water_ok=True, path_d=80, area=river_area(L, rr, 0.5, 0.75))):
        w = to_world(x, y, -0.05)
        floating_house(root, f'flutuante{k}', Mt, R, (w.x, w.y, -0.07), 1.1, river_angle(L, cp, x, y) + rr.uniform(-0.2, 0.2), rr)
    for k, (x, y) in enumerate(place.take(3, 24, test=mid(0.3, 0.8), water_ok=True, path_d=70, area=river_area(L, rr, 0.3, 0.8))):
        w = to_world(x, y, -0.05)
        canoe(root, f'canoaRio{k}', Mt, (w.x, w.y, -0.08), 0.8, river_angle(L, cp, x, y) + rr.uniform(-0.4, 0.4), rr)
    # beira: aninga e canarana na agua rasa, capim e arvores grandes na margem
    for k, (x, y) in enumerate(place.take(18, 9, test=mid(0.82, 1.02), water_ok=True, path_d=44, area=river_area(L, rr, 0.82, 1.02))):
        w = to_world(x, y)
        aninga(lote, R, (w.x, w.y, max(-0.05, cp.height_at(w.x, w.y))), rr.uniform(0.8, 1.1), rr)
    for k, (x, y) in enumerate(place.take(10, 14, test=mid(0.66, 0.92), water_ok=True, path_d=50, area=river_area(L, rr, 0.66, 0.92))):
        w = to_world(x, y, -0.045)
        floating_grass(lote, R, (w.x, w.y, -0.045), rr.uniform(0.25, 0.4), rr)
    bank_trees(L, root, cp, place, rr, 8)
    deco_palms(place, cp, out, place.take(8, 26, tall=(80, 30), test=lambda x, y: _er(cp, x, y) < 2.6), rr, 0.85, 1.1)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=8, ferns=24, bromel=12, helic=10, leaves=16, logs=3, rocks=6, tufts=110, flw=20)


def theme_mangue(L, root, P, th, cp, place, lote, rr, out, m):
    Mt, R = MT, RT
    lights = []
    shore = lambda x, y: 1.0 <= min(_er(cp, x, y), _ew(cp, x, y)) <= 2.1
    dry = lambda x, y: min(_er(cp, x, y), _ew(cp, x, y)) > 1.05
    # caranguejos, guaras em bando e garcas
    for k, (x, y) in enumerate(place.take(46, 4, path_d=36, test=dry)):
        crab(lote, R, tuple(place.ground(x, y)), rr.uniform(0.9, 1.3), rr.uniform(0, TAU), rr, blue=rr.random() < 0.35)
    for k, (x, y) in enumerate(place.take(4, 24, test=shore, path_d=40, area=river_area(L, rr, 1.1, 1.8, cp))):
        for j in range(rr.randrange(4, 7)):
            gx, gy = x + rr.uniform(-26, 26), y + rr.uniform(-12, 12)
            wader(root, f'guara{k}_{j}', R, tuple(place.ground(gx, gy)), rr.uniform(0.95, 1.15), rr.uniform(0, TAU), rr)
    for k, (x, y) in enumerate(place.take(5, 12, test=shore, path_d=44, area=river_area(L, rr, 1.0, 1.6, cp))):
        wader(root, f'garca{k}', R, tuple(place.ground(x, y)), rr.uniform(1.0, 1.2), rr.uniform(0, TAU), rr, kind='garca')
    # mangue-vermelho na lama da margem e um bosque mais para dentro
    for k, (x, y) in enumerate(place.take(22, 34, tall=(110, 50), test=shore, path_d=56, area=river_area(L, rr, 1.05, 2.0, cp))):
        w = place.ground(x, y)
        mangrove(root, f'mangue{k}', R, tuple(w), rr.uniform(0.95, 1.3), rr, lote=lote)
        pneumatophores(lote, R, tuple(w), 1.0, rr)
    for k, (x, y) in enumerate(place.take(12, 34, tall=(110, 50), path_d=64)):
        w = place.ground(x, y)
        mangrove(root, f'mangueB{k}', R, tuple(w), rr.uniform(0.85, 1.15), rr, lote=lote)
        pneumatophores(lote, R, tuple(w), 0.8, rr, n=10)
    # curral de pesca num canal (estacas em V)
    for k, (x, y) in enumerate(place.take(1, 50, test=lambda x, y: _er(cp, x, y) < 0.5, water_ok=True, path_d=90, area=river_area(L, rr, 0, 0.4))):
        a = river_angle(L, cp, x, y)
        w0 = to_world(x, y, -0.05)
        pts = []
        for i in range(-5, 6):
            t = abs(i) / 5
            pts.append((w0.x + math.cos(a) * t * 0.9 - math.sin(a) * i * 0.13, w0.y + math.sin(a) * t * 0.9 + math.cos(a) * i * 0.13, -0.05))
        fish_weir(lote, R, pts, rr)
    # palafita com canoa
    for k, (x, y) in enumerate(place.take(1, 50, tall=(70, 44), test=shore, path_d=70, area=river_area(L, rr, 1.2, 1.9, cp))):
        w = place.ground(x, y)
        palafita(root, f'palafitaMangue{k}', Mt, tuple(w), rr.uniform(1.25, 1.4), rr, ang=rr.uniform(-0.25, 0.25))
        out['env'].append([round(x - 6, 1), round(y - 40, 1), '#ffc070', 60])
    # tochas na beira da estrada (fase da noite), vaga-lumes e a lua na agua
    for p in L['paths']:
        acc, side = 0.0, 1
        for a, b in zip(p[:-1], p[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            acc += ln
            if acc < 190:
                continue
            acc = 0.0
            side = -side
            x, y = b[0] - dy / ln * 44 * side, b[1] + dx / ln * 44 * side
            if not (30 < x < GW - 30 and 60 < y < GH - 20) or not place.far_spot(x, y, 52) or not place.hud_free(x, y) or not dry(x, y):
                continue
            if float(cp.road_at(x, y)) < 34:
                continue
            torch(root, f'tocha{len(lights)}', R, tuple(place.ground(x, y)), 1.25, rr, lights=lights)
            place.placed.append((x, y))
            out['env'].append([round(x, 1), round(y - 30, 1), '#ffb04a'])
    for k, (x, y) in enumerate(place.take(9, 12, test=dry, path_d=40)):
        fireflies(root, f'vagalume{k}', R, tuple(place.ground(x, y)), rr)
        out['env'].append([round(x, 1), round(y - 16, 1), '#d8ff6a', 45])
    spot = None
    if cp.water:
        x, y, rx, ry = max(cp.water, key=lambda w_: w_[2] * w_[3])
        spot = (x, y, rx / GB * 0.7)
    elif cp.rivers:
        cand = place.take(1, 30, test=lambda x, y: _er(cp, x, y) < 0.35, water_ok=True, path_d=70, area=river_area(L, rr, 0, 0.3))
        if cand:
            spot = (cand[0][0], cand[0][1], 0.75)
    if spot:
        w = to_world(spot[0], spot[1], -0.045)
        moon_glint(lote, R, (w.x, w.y, -0.046), spot[2], rr)
        out['env'].append([round(spot[0], 1), round(spot[1], 1), '#cfe0ff', 120])
    deco_palms(place, cp, out, place.take(4, 26, tall=(80, 30), test=dry), rr, 0.85, 1.05)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=0, ferns=10, bromel=4, helic=0, leaves=8, logs=4, rocks=4, tufts=70, flw=0)
    out['glow_lights'] = lights


def theme_cheia(L, root, P, th, cp, place, lote, rr, out, m):
    Mt, R = MT, RT
    wet = lambda x, y: (lambda w: cp.height_at(w.x, w.y) < -0.1)(to_world(x, y))
    dry = lambda x, y: not wet(x, y)
    # arvores da varzea na baixada, com a marca escura da cheia no tronco
    for k, (x, y) in enumerate(place.take(10, 46, tall=(160, 70), path_d=70, test=wet)):
        w = place.ground(x, y)
        s_ = rr.uniform(0.9, 1.2)
        jungle_tree(root, f'arvoreCheia{k}', Mt, tuple(w), s_, rr)
        cyl(root, f'arvoreCheia{k}_marca', 0.33 * s_, Z_CHEIA - w.z + 0.04, (w.x, w.y, (w.z + Z_CHEIA + 0.04) / 2), m=R['marca'], v=18, bev=0.01)
    for k, (x, y) in enumerate(place.take(2, 50, tall=(70, 44), test=wet, path_d=70)):
        w = place.ground(x, y)
        palafita(root, f'palafitaCheia{k}', Mt, tuple(w), rr.uniform(1.25, 1.4), rr, ang=rr.uniform(-0.25, 0.25))
    for k, (x, y) in enumerate(place.take(20, 9, test=wet, path_d=40)):
        aninga(lote, R, tuple(place.ground(x, y)), rr.uniform(0.8, 1.1), rr)
    for k, (x, y) in enumerate(place.take(10, 14, test=wet, path_d=44)):
        floating_grass(lote, R, tuple(place.ground(x, y)), rr.uniform(0.25, 0.4), rr)
    # canoas: na vazante ficam no seco da baixada
    for k, (x, y) in enumerate(place.take(3, 26, test=wet, path_d=60)):
        canoe(root, f'canoaCheia{k}', Mt, tuple(place.ground(x, y)), 0.8, rr.uniform(-0.6, 0.6), rr)
    # pocas da vazante com vitoria-regia
    for k, (x, y) in enumerate(place.take(16, 8, test=lambda x, y: (lambda w: cp.height_at(w.x, w.y) < Z_VAZANTE - 0.03)(to_world(x, y)), path_d=40)):
        w = to_world(x, y)
        vitoria_regia(lote, Mt, (w.x, w.y, Z_VAZANTE + 0.002), rr.uniform(0.14, 0.22), rr)
    deco_palms(place, cp, out, place.take(7, 26, tall=(80, 30), test=dry), rr, 0.85, 1.05)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=4, ferns=16, bromel=8, helic=8, leaves=12, logs=2, rocks=4, tufts=90, flw=12)


def theme_tepui(L, root, P, th, cp, place, lote, rr, out, m):
    Mt, R = MT, RT
    lights = []
    # fenda da Fumaca Negra (L.fenda ou o comeco da primeira estrada que aparece na tela)
    fx, fy = cp.fenda
    ux, uy = road_dir(L, fx, fy)
    # rasgo principal atravessando a estrada e dois galhos menores
    nx_, ny_ = -uy, ux
    pts = []
    for i in range(-8, 9):
        t = i * 11
        pts.append(tuple(place.ground(fx + nx_ * t + rr.uniform(-3, 3), fy + ny_ * t * 0.55 + 5 * math.sin(i * 1.2) + rr.uniform(-2, 2))))
    smoke_fissure(lote, root, 'fenda', R, pts, 0.2, rr, lights=lights)
    for j, (i0, sg) in enumerate(((-5, -1), (4, 1))):
        bx, by = fx + nx_ * i0 * 11, fy + ny_ * i0 * 11 * 0.55
        br = []
        for i in range(5):
            br.append(tuple(place.ground(bx + ux * sg * i * 9 + nx_ * i * 4 * sg, by + uy * sg * i * 6 + rr.uniform(-2, 2))))
        smoke_fissure(lote, root, f'fenda_galho{j}', R, br, 0.1, rr)
    out['env'].append([round(fx, 1), round(fy, 1), '#ff6a1a', 130])
    out['fenda'] = [round(fx, 1), round(fy, 1)]
    place.placed.append((fx, fy))
    # esculturas de arenito com musgo no topo
    for k, (x, y) in enumerate(place.take(9, 48, tall=(120, 50), path_d=60)):
        w = place.ground(x, y)
        r_ = rr.uniform(0.5, 0.75)
        objs, top = sandstone_tower(root, f'arenito{k}', R, tuple(w), rr.uniform(1.0, 2.0), r_, rr)
        sphere(root, f'arenito{k}_musgo', r_ * 0.7, (w.x, w.y, w.z + top - 0.02), scale=(1.1, 1.0, 0.3), m=Mt['moss'], seg=14)
        if rr.random() < 0.6:
            bromeliad(root, f'arenito{k}_brom', Mt, (w.x, w.y, w.z + top + 0.02), rr.uniform(0.9, 1.2), rr, center=rr.choice((Mt['red'], Mt['orange'])))
    rm = mat('rocha_tepui', th['rock'], rough=0.88, var=0.12, bump=0.3)
    for k, (x, y) in enumerate(place.take(14, 14)):
        w = place.ground(x, y)
        rock_cluster(root, f'pedraTepui{k}', rm, tuple(w), rr.uniform(0.22, 0.38), rr, n=3, m2=R['arenito_esc'])
    for k, (x, y) in enumerate(place.take(12, 10)):
        quartz(root, f'quartzo{k}', R, tuple(place.ground(x, y)), rr.uniform(0.9, 1.4), rr, pink=k % 3 != 0)
    for k, (x, y) in enumerate(place.take(14, 10)):
        pitcher_plants(root, f'jarro{k}', R, tuple(place.ground(x, y)), rr.uniform(1.0, 1.4), rr)
    # alem da borda: mar de nuvens e outros tepuis ao longe
    for i, gx in enumerate(range(-60, GW + 80, 64)):
        ye = 62 + 14 * math.sin(gx / 97.0) + 9 * math.sin(gx / 41.0 + 1.0)
        if float(cp.road_at(gx, ye)) < 90:
            continue
        w = to_world(gx + rr.uniform(-20, 20), ye - rr.uniform(20, 46), -1.4)
        cloud(root, f'nuvem{i}', R, (w.x, w.y, -1.4), rr.uniform(0.9, 1.3), rr)
    for k, gx in enumerate((150, 560, 1010)):
        if float(cp.road_at(gx, 40)) < 140:
            continue
        w = to_world(gx + rr.uniform(-60, 60), 26, -0.9)
        rx_ = rr.uniform(1.6, 2.4)
        objs, top = strata_rock(root, f'tepuiLonge{k}', R['arenito'], R['arenito2'], (w.x, w.y, -3.4), rx_, rx_ * 0.65, 2.7, rr, layers=4)
        grass_cap(root, f'tepuiLonge{k}_mata', Mt, (w.x, w.y, -3.4), rx_ * 0.55, rx_ * 0.36, top - 0.02)
    mata_floor(L, root, P, th, cp, place, lote, rr, out, m, trees=0, ferns=6, bromel=16, helic=0, leaves=0, logs=0, rocks=0, tufts=90, flw=12, moita=20)
    out['glow_lights'] = lights


THEME_FN = {'oasis': theme_oasis, 'canyon': theme_barranco, 'ruins': theme_cidade, 'dunes': theme_varzea,
            'citadel': theme_gruta, 'storm': theme_temporal, 'qanat': theme_furos, 'ember': theme_queimada,
            'encontro': theme_encontro, 'mangue': theme_mangue, 'cheia': theme_cheia, 'tepui': theme_tepui}


# ---------------------------------------------------------------- render
def setup_camera(k):
    cam = bpy.data.objects['CamJogo']
    sc = bpy.context.scene
    sc.render.resolution_x = int(GW * k)
    sc.render.resolution_y = int(GH * k)
    cam.data.ortho_scale = GW / GB
    Rv, Uv, Fv = cam_axes()
    cam.location = -Fv * 40
    cam.data.clip_end = 200
    return cam


def render_level(idx, out_dir, samples=96, k=2.0):
    with open(os.path.join(out_dir, 'fases.json')) as fh:
        LV = json.load(fh)
    L = LV[idx]
    clear_scene()
    ANIMS.clear()
    sc = bpy.context.scene
    ST['coll'] = sc.collection
    setup_scene()
    try:   # o MetalRT fura o chao em retangulos; o BVH da propria Cycles nao
        bpy.context.preferences.addons['cycles'].preferences.metalrt = 'OFF'
    except Exception:
        pass
    sc.render.film_transparent = False
    # o chao e quase todo areia clara: sem isto o vermelho estoura e tudo fica laranja chapado (as torres seguem em 0)
    sc.view_settings.exposure = TH[L['theme']].get('exposure', EXPOSURE.get(L['theme'], -0.6))
    bpy.data.objects['ChaoSombra'].hide_render = True
    sc.cycles.samples = samples
    P = palette2()
    root = make_root('raiz_cenario', 'cenario', coll_for('Cenario'))
    meta = build_level(L, root, P)
    cp = meta.pop('_cp')
    add_palm_shadows(root, P, meta)
    setup_camera(k)
    sc.render.image_settings.color_mode = 'RGB'
    path = os.path.join(out_dir, f'f{idx + 1}.png')
    render_to(path)
    if cp.flood:
        # mesmo cenario com a agua da cheia: o jogo mistura os dois fundos (alpha = g.flood)
        o = build_flood(cp, root, z=Z_CHEIA, cheia=True, name='Cheia')
        render_to(os.path.join(out_dir, f'f{idx + 1}_cheia.png'))
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
        meta['cheia'] = True
    glow = bool(meta.get('env'))
    if glow:
        # so as chamas e a lava: a poca de luz no chao quem faz e a luz do jogo (js/vfx.js, A.envLights)
        BUILT['cenario'] = {'lights': []}
        # no passe de luz o chao vira preto e so a lava e as chamas aparecem
        render_glow_pass('cenario', os.path.join(out_dir, f'f{idx + 1}_glow.png'))
    meta.pop('glow_lights', None)
    meta['glow'] = glow
    meta['k'] = k
    with open(os.path.join(out_dir, f'f{idx + 1}.json'), 'w') as fh:
        json.dump(meta, fh)
    print('FUNDO_OK', path, len(meta['palms']), 'palmeiras', len(meta['env']), 'luzes')


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'fundo':
        out = args[1]
        idxs = [int(a) - 1 for a in args[2].split(',')]
        samples = int(args[3]) if len(args) > 3 else 96
        k = float(args[4]) if len(args) > 4 else 2.0
        for i in idxs:
            render_level(i, out, samples, k)
