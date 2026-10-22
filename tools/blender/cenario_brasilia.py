"""Cenarios de Brasilia (Ninguem Sobe a Rampa): um fundo pre-renderizado por fase, com a mesma camera, sol e escala do
cenario da mata (tools/blender/cenario.py, de onde vem o Campo, o Lugar, a camera e o passe de luz).

Chao do cerrado (capim seco dourado, gramados do Eixo, pracas de concreto e de pedra portuguesa), estrada de terra
vermelha afundada (lida dos caminhos do jogo), espelhos d'agua com borda de concreto, o mesmo lote de concreto branco das
torres (tools/blender/lote_brasilia.py), lotes altos em terracos de concreto (pe em calice) e os marcos de cada fase:
  1 Eixo Monumental: gramados, a plataforma da Rodoviaria e onibus estacionados
  2 Esplanada dos Ministerios: os blocos iguais em fila, o gramado central e a Catedral
  3 Congresso Nacional (noite): cupula, tigela, torres gemeas e espelho d'agua; janelas e postes acendem
  4 Praca dos Tres Poderes (tempestade): pedra portuguesa, mastro da bandeira, pombal, pombos e o STF
  5 Rampa do Planalto: o palacio com as colunas curvas e a rampa no fim da estrada (a saida dos inimigos)
Nada de texto, de pessoas ou de bandeira com escrita. Os ipes ficam no fundo (sem sprite: a lista palms sai vazia).

  node tools/fases_json.js > arte/render/cenario/fases.json
  Blender -b -P tools/blender/cenario_brasilia.py -- fundo arte/render/cenario <fase 1-5> [amostras] [px_por_unidade]

Sai f<N>.png (e f<N>_glow.png quando a fase tem luzes) e f<N>.json (luzes do cenario); o empacotador
(tools/sprites/empacotar.py cenario) grava sprites/cenario_f<N>.jpg e a chave cenario do js/sprites_meta.js.
Final: 3 px por unidade do jogo (3840x2160); previa: 0.5 (640x360).
"""
import os, sys, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from lib import *   # noqa: F401,F403
import cenario as C
from cenario import to_world, to_game, sstep, hex3, mesa_center, MESA_H, GW, GH, GB, SIN, COS, MX0, MY0, MW, MH
from cenario_props import Lote, rock, rock_cluster
from brasilia_props import *   # noqa: F401,F403
from lote_brasilia import plot as lote_concreto   # o mesmo lote das torres novas (a torre construida casa com o fundo)

# ---------------------------------------------------------------- paleta do cerrado
BASE = dict(
    sand='#b3a05a', sand_l='#c4b06a', sand_d='#9a8a4a',     # capim seco (dourado)
    olive='#9c9a52',                                         # manchas de capim mais verde
    lawn='#9aa44c', lawn_l='#adb65a',                        # gramado (seca: verde amarelado)
    road='#b85f3d', road_d='#94462d',                        # terra vermelha
    pedra='#e4ddce', pedra_d='#c4bcac',                      # pedra portuguesa (clara, ondas cinza)
    laje='#d9d2c3',                                          # placas de concreto
    asfalto='#7f7a73',                                       # patio dos onibus
    pad='#c9c0ae', bed='#56717a',
    water=('#3a7f98', '#68aec2', '#bfe0e4'),
    relief=0.07, wl=(2.5, 6.0), exposure=-0.55,
)


def sel(F, key):
    return F.get(key, BASE[key])


# ---------------------------------------------------------------- formas (coordenadas de tela do jogo)
def superellipse_e(gx, gy, x, y, rx, ry, n):
    """1 na borda; superelipse de expoente n (2 = elipse, 4 = retangulo de cantos redondos)."""
    return (np.abs((gx - x) / rx) ** n + np.abs((gy - y) / ry) ** n) ** (1.0 / n)


def superellipse_pts(x, y, rx, ry, n, e=1.0, k=160):
    out = []
    for i in range(k):
        t = TAU * i / k
        c, s = math.cos(t), math.sin(t)
        out.append((x + rx * e * math.copysign(abs(c) ** (2 / n), c), y + ry * e * math.copysign(abs(s) ** (2 / n), s)))
    return out


class CampoBR(C.Campo):
    """Campo da mata com o chao de Brasilia: zonas de praca (pedra/laje), gramados e espelhos d'agua retos."""

    def __init__(self, L, F):
        super().__init__(L)
        self.F = F
        self.th = dict(BASE, **F.get('th', {}))
        wn = F.get('water_n', 2.6)
        self.pools = [(x, y, rx, ry, wn) for (x, y, rx, ry) in L['water']] + list(F.get('pools', []))
        self.plazas = F.get('plazas', [])   # (tipo 'pedra'|'laje'|'asfalto', x, y, rx, ry, n)
        self.lawns = F.get('lawns', [])     # (x, y, rx, ry, n)

    def water_e(self, gx, gy):
        e = np.full(np.shape(gx), 9.0, np.float32)
        for (x, y, rx, ry, n) in self.pools:
            e = np.minimum(e, superellipse_e(gx, gy, x, y, rx, ry, n))
        return e

    def zone(self, gx, gy, shapes, soft=0.06):
        k = np.zeros(np.shape(gx), np.float32)
        for (x, y, rx, ry, n) in shapes:
            e = superellipse_e(gx, gy, x, y, rx, ry, n)
            k = np.maximum(k, 1 - sstep(1.0 - soft, 1.0, e))
        return k

    def plaza_k(self, gx, gy, kind=None):
        if kind:
            return self.zone(gx, gy, [p[1:] for p in self.plazas if p[0] == kind], soft=0.02)
        ped = self.zone(gx, gy, [p[1:] for p in self.plazas if p[0] == 'pedra'], soft=0.02)
        laj = self.zone(gx, gy, [p[1:] for p in self.plazas if p[0] in ('laje', 'asfalto')], soft=0.02)
        return ped, laj

    def evaluate_br(self, X, Y):
        th = self.th
        gx = 640 + X * GB
        gy = 360 - Y * SIN * GB
        d = self.road_at(gx, gy)
        ds = self.spot_dist(X, Y)
        e = self.water_e(gx, gy)
        rel = self.relief(X, Y)
        ped, laj = self.plaza_k(gx, gy)
        pk = np.maximum(ped, laj)
        lk = self.zone(gx, gy, self.lawns, soft=0.12) * (1 - pk)
        flat = sstep(30, 95, d) * sstep(0.85, 1.9, ds) * sstep(1.05, 1.6, e)
        h = rel * flat * (1 - pk) + 0.02 * pk
        paved = bool(th.get('road_paved'))
        # estrada: calha rasa, borda levantada e (na terra) os sulcos das rodas
        h += -0.055 * (1 - sstep(17, 30, d)) + 0.035 * np.exp(-((d - 31.5) / 5.0) ** 2) - (0.0 if paved else 0.014) * np.exp(-((d - 11.0) / 3.2) ** 2)
        # espelho d'agua: o fundo afunda por dentro da borda de concreto (a borda e uma peca 3D)
        h = np.where(e < 1.15, h * sstep(1.0, 1.15, e) - 0.3 * (1 - sstep(0.9, 1.0, e)), h)
        # cores: capim seco com manchas mais verdes e mais claras
        relk = np.tanh(rel / max(th['relief'], 0.03) * 1.1) * 0.5 + 0.5
        col = hex3(th['sand_d'])[None] * (1 - relk[:, None]) + hex3(th['sand_l'])[None] * relk[:, None]
        col = col * 0.55 + hex3(th['sand'])[None] * 0.45
        rr = random.Random(self.L['seed'] * 3 + 5)
        patch = np.zeros(np.shape(X), np.float32)
        for i in range(6):
            a = rr.uniform(0, TAU)
            k = TAU / rr.uniform(1.8, 4.5)
            patch += np.sin((X * math.cos(a) + Y * math.sin(a)) * k + rr.uniform(0, TAU)).astype(np.float32)
        ok = (sstep(0.6, 2.0, patch) * 0.55)[:, None]
        col = col * (1 - ok) + hex3(th['olive'])[None] * ok
        col *= (1 + 0.04 * patch / 3)[:, None]
        # gramado
        lawn = hex3(th['lawn'])[None] * (1 - relk[:, None]) * 0.5 + hex3(th['lawn_l'])[None] * (0.5 + 0.5 * relk[:, None])
        lawn *= (1 + 0.05 * patch / 3)[:, None]
        col = col * (1 - lk[:, None]) + lawn * lk[:, None]
        # pracas: pedra portuguesa clara com ondas cinza (calcadao) e placas de concreto
        wave = 0.5 + 0.5 * np.sin(gx / 23.0 + 2.2 * np.sin(gy / 31.0) + gy / 57.0)
        stripe = sstep(0.82, 0.9, wave).astype(np.float32) * float(th.get('waves', 0.0))
        pedra = hex3(th['pedra'])[None] * (1 - stripe[:, None]) + hex3(th['pedra_d'])[None] * stripe[:, None]
        col = col * (1 - ped[:, None]) + pedra * ped[:, None]
        asf = self.plaza_k(gx, gy, 'asfalto')
        lj = np.maximum(laj - asf, 0)
        col = col * (1 - lj[:, None]) + hex3(th['laje'])[None] * lj[:, None]
        col = col * (1 - asf[:, None]) + hex3(th['asfalto'])[None] * asf[:, None]
        # estrada de terra vermelha (ou de pedra vermelha, na praca)
        roadk = 1 - sstep(24, 33, d)
        road = hex3(th['road'])[None] * (1 - 0.1 * np.exp(-((d - 11.0) / 3.5) ** 2))[:, None]
        road = road * (1 - sstep(15, 27, d))[:, None] + hex3(th['road_d'])[None] * sstep(15, 27, d)[:, None]
        col = col * (1 - roadk[:, None]) + road * roadk[:, None]
        padk = 1 - sstep(0.62, 0.8, self.spot_dist(X, Y, high=False))
        col = col * (1 - padk[:, None]) + hex3(th['pad'])[None] * padk[:, None]
        bed = 1 - sstep(0.85, 1.0, e)
        col = col * (1 - bed[:, None]) + hex3(th['bed'])[None] * bed[:, None]
        rim = (1 - sstep(1.06, 1.14, e)) * sstep(0.9, 1.0, e)
        col = col * (1 - rim[:, None]) + hex3('#d8d2c4')[None] * rim[:, None]
        wet = (1 - sstep(0.95, 1.02, e)).astype(np.float32)
        Rm = (lj * (1 - roadk)).astype(np.float32)
        Bm = (ped * (1 - roadk) + (roadk * pk if paved else 0)).astype(np.float32)
        return dict(h=h.astype(np.float32), col=col.astype(np.float32), R=Rm, G=wet, B=Bm, d=d, ds=ds, e=e, pk=pk, lk=lk)

    def evaluate(self, X, Y):
        r = self.evaluate_br(X, Y)
        return r['h'], r['col'], r['R'], r['G'], r['d'], r['ds'], r['e']

    def height_at(self, x, y):
        return float(self.evaluate_br(np.array([x], np.float32), np.array([y], np.float32))['h'][0])

    def plaza_at(self, gx, gy):
        ped, laj = self.plaza_k(np.float32(gx), np.float32(gy))
        return float(max(ped, laj))

    def lawn_at(self, gx, gy):
        return float(self.zone(np.float32(gx), np.float32(gy), self.lawns))


# ---------------------------------------------------------------- chao
def ground_material_br():
    """Chao: cor do vertice ('cor') com variacao macia; mascara R = placas de concreto (juntas), G = molhado,
    B = pedra portuguesa (pedrinhas em voronoi)."""
    m = bpy.data.materials.new('chao_brasilia')
    try:
        m.use_nodes = True
    except Exception:
        pass
    N, L = m.node_tree.nodes, m.node_tree.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.92
    a = N.new('ShaderNodeAttribute'); a.attribute_name = 'cor'
    k = N.new('ShaderNodeAttribute'); k.attribute_name = 'mask'
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateColor')
    L.new(k.outputs['Color'], sep.inputs['Color'])
    xyz = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Object'], xyz.inputs[0])

    def mth(op, x, y=None, z=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((x, y, z)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 26; nz.inputs['Detail'].default_value = 4
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    # juntas das placas (0,62 de lado) e pedrinhas da pedra portuguesa
    def joint(axis):
        f = mth('ABSOLUTE', mth('SUBTRACT', mth('FRACT', mth('MULTIPLY', xyz.outputs[axis], 1 / 0.62)), 0.5))
        return mth('SMOOTH_MIN', mth('MULTIPLY', mth('MAXIMUM', mth('SUBTRACT', f, 0.465), 0.0), 40.0), 1.0, 0.1)
    jl = mth('MULTIPLY', mth('MAXIMUM', joint('X'), joint('Y')), sep.outputs['Red'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 13.0
    L.new(tc.outputs['Object'], vo.inputs['Vector'])
    groove = mth('MULTIPLY', mth('SUBTRACT', 1.0, mth('MINIMUM', mth('DIVIDE', vo.outputs['Distance'], 0.07), 1.0)), sep.outputs['Blue'])
    # cor: escurece um pouco nas juntas e entre as pedrinhas
    dark = mth('SUBTRACT', 1.0, mth('ADD', mth('MULTIPLY', jl, 0.22), mth('MULTIPLY', groove, 0.16)))
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.95; mr.inputs['To Max'].default_value = 1.05
    L.new(nz.outputs['Fac'], mr.inputs['Value'])
    val = mth('MULTIPLY', mr.outputs['Result'], dark)
    hsv = N.new('ShaderNodeHueSaturation')
    L.new(a.outputs['Color'], hsv.inputs['Color'])
    L.new(val, hsv.inputs['Value'])
    L.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    hgt = mth('SUBTRACT', mth('SUBTRACT', mth('MULTIPLY', nz.outputs['Fac'], 0.25), mth('MULTIPLY', jl, 0.5)), mth('MULTIPLY', groove, 0.35))
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; bp.inputs['Distance'].default_value = 0.03
    L.new(hgt, bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.92; rg.inputs['To Max'].default_value = 0.4
    L.new(sep.outputs['Green'], rg.inputs['Value'])
    L.new(rg.outputs['Result'], bsdf.inputs['Roughness'])
    return m


def build_ground_br(cp, root, bands=10):
    """Malha do chao em faixas (como no cenario.py), com a mascara de tres canais do chao de Brasilia."""
    xs = np.arange(-16.8, 16.8 + 1e-6, 0.06, dtype=np.float32)
    ys = np.arange(-17.6, 19.0 + 1e-6, 0.072, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    r = cp.evaluate_br(XX.ravel(), YY.ravel())
    h, col = r['h'], r['col']
    nx, ny = len(xs), len(ys)
    Hg = h.reshape(ny, nx)
    gy_, gx_ = np.gradient(Hg, 0.072, 0.06)
    nrm = np.stack([-gx_, -gy_, np.ones_like(Hg)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    mat_ = ground_material_br()
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
        ma.data.foreach_set('color', np.stack([r['R'][sl], r['G'][sl], r['B'][sl], np.ones(len(verts), np.float32)], 1).ravel())
        me.polygons.foreach_set('use_smooth', np.ones(len(q), bool))
        me.normals_split_custom_set_from_vertices(nrm[r0:r1 + 1].reshape(-1, 3).tolist())
        o = bpy.data.objects.new(f'Chao{b}', me)
        root.users_collection[0].objects.link(o)
        o.parent = root
        o['set'] = root['set']
        me.materials.append(mat_)


def build_pools(cp, root, M):
    """Espelhos d'agua: lamina d'agua (funda no meio, clara na borda) e a borda de concreto em volta."""
    wc = cp.th['water']
    deep, shallow, foam = hex3(wc[0]), hex3(wc[1]), hex3(wc[2])
    z = -0.06
    for k, (x, y, rx, ry, n) in enumerate(cp.pools):
        bm = bmesh.new()
        es = [0.0, 0.3, 0.55, 0.75, 0.88, 0.95, 1.0, 1.06]
        kk = 96
        rings = []
        for e in es:
            if e == 0:
                rings.append([bm.verts.new(tuple(to_world(x, y, z)))])
            else:
                rings.append([bm.verts.new(tuple(to_world(px, py, z))) for (px, py) in superellipse_pts(x, y, rx, ry, n, e, kk)])
        for i in range(len(rings) - 1):
            A, B = rings[i], rings[i + 1]
            for j in range(kk):
                if len(A) == 1:
                    bm.faces.new((A[0], B[j], B[(j + 1) % kk]))
                else:
                    bm.faces.new((A[j], A[(j + 1) % kk], B[(j + 1) % kk], B[j]))
        o = bm_to_obj(bm, f'Espelho{k}', root, [C.water_material()], angle=89)
        ca = o.data.color_attributes.new('cor', 'FLOAT_COLOR', 'POINT')
        vals = []
        for v in o.data.vertices:
            gx, gy = to_game(v.co)
            e = float(superellipse_e(gx, gy, x, y, rx, ry, n))
            t = min(1.0, max(0.0, (e - 0.25) / 0.65))
            c = deep * (1 - t) + shallow * t
            f = min(1.0, max(0.0, (e - 0.93) / 0.07))
            c = c * (1 - f * 0.7) + foam * f * 0.7
            vals += [c[0], c[1], c[2], 1.0]
        ca.data.foreach_set('color', vals)
        # borda: largura constante de ~7 px de tela
        e_c = 1.0 + 4.0 / max(min(rx, ry * 1.6), 10)
        pts = [to_world(px, py, 0.0) for (px, py) in superellipse_pts(x, y, rx, ry, n, e_c, 128)]
        curb_loop(root, f'Espelho{k}_borda', [(p.x, p.y, 0.0) for p in pts], 0.17, 0.07, -0.16, M['conc_l'])


# ---------------------------------------------------------------- posicionamento
class LugarBR(C.Lugar):
    """Lugar da mata com areas reservadas (predios, pracas cheias): nada de enfeite sorteado dentro delas."""

    def __init__(self, cp, L, rr):
        super().__init__(cp, L, rr)
        self.blocks = []

    def block(self, x0, y0, x1, y1):
        self.blocks.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))

    def free(self, x, y, d):
        m = d * 0.6
        for (x0, y0, x1, y1) in self.blocks:
            if x0 - m < x < x1 + m and y0 - m < y < y1 + m:
                return False
        return super().free(x, y, d)

    def ground(self, x, y):
        w = to_world(x, y)
        w.z = self.cp.height_at(w.x, w.y)
        return w

    def clear_above(self, x, y, h, w):
        """Nada importante na tela logo acima de uma peca alta: lotes, estrada, predios e espelhos d'agua."""
        if not super().clear_above(x, y, h, w):
            return False
        for (x0, y0, x1, y1) in self.blocks:
            if x1 > x - w and x0 < x + w and y1 > y - h and y0 < y:
                return False
        for (px, py, rx, ry, n) in self.cp.pools:
            if px + rx > x - w and px - rx < x + w and py + ry > y - h and py - ry < y:
                return False
        return True


def gz(cp):
    """Altura do chao num ponto do mundo (para pecas soltas: flores caidas, pombos)."""
    return lambda wx, wy: cp.height_at(wx, wy)


def block_world(place, loc, half_w, half_d, up=0.0, front=26):
    """Reserva na tela a area de um predio: retangulo no chao (meia largura e meia profundidade em unidades), a altura e
    uma folga na frente (px), para nenhuma arvore nascer colada na fachada."""
    x0, y0 = to_game((loc[0] - half_w, loc[1] - half_d, 0))
    x1, y1 = to_game((loc[0] + half_w, loc[1] + half_d, up))
    place.block(x0, y0 + front, x1, y1)


def at(gx, gy, cp=None):
    w = to_world(gx, gy)
    if cp is not None:
        w.z = cp.height_at(w.x, w.y)
    return w


# ---------------------------------------------------------------- pecas comuns de todas as fases
def build_common(L, F, root, P, cp, place, lote, M, rr, out):
    """Seixos na beira da estrada, lotes (e terracos dos lotes altos) e os pilares da saida."""
    # seixos nas bordas da estrada (fora das pracas)
    for p in L['paths']:
        P_ = np.asarray(p, np.float32)
        seg = np.hypot(np.diff(P_[:, 0]), np.diff(P_[:, 1]))
        cum = np.concatenate([[0], np.cumsum(seg)])
        dist = 0.0
        while dist < cum[-1]:
            i = max(1, min(int(np.searchsorted(cum, dist)), len(P_) - 1))
            a, b = P_[i - 1], P_[i]
            t = (dist - cum[i - 1]) / max(seg[i - 1], 1e-6)
            qx, qy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            dx, dy = (b[0] - a[0]) / max(seg[i - 1], 1e-6), (b[1] - a[1]) / max(seg[i - 1], 1e-6)
            for side in (-1, 1):
                if rr.random() < F.get('road_stones', 0.5):
                    off = side * rr.uniform(29, 34)
                    x, y = qx - dy * off, qy + dx * off
                    if float(cp.road_at(x, y)) < 27 or not (-40 < x < GW + 40 and -40 < y < GH + 60):
                        continue
                    if cp.plaza_at(x, y) > 0.3:
                        continue
                    w = to_world(x, y)
                    if float(cp.spot_dist(np.float32(w.x), np.float32(w.y))) < 0.85:
                        continue
                    w.z = cp.height_at(w.x, w.y)
                    lote.pebble(M['seixo'], (w.x, w.y, w.z + 0.01), rr.uniform(0.05, 0.085), squash=0.6, rot=rr.uniform(0, TAU), rr=rr)
            dist += rr.uniform(6.0, 9.0)
    # lotes: o lote de concreto branco das torres (tools/blender/lote_brasilia.py, topo em z = 0.15), no chao ou em cima
    # do terraco de concreto dos lotes altos
    for k, s in enumerate(L['spots']):
        if s['high']:
            c = mesa_center(s)
            terraco(root, f'terraco{k}', (c.x, c.y), MESA_H, M, rr)
            base = Vector((c.x, c.y, MESA_H))
        else:
            base = to_world(s['x'], s['y'])
            base.z = cp.height_at(base.x, base.y)
        lote_concreto(empty(root, f'lote{k}', tuple(base)), P, f'lote{k}')
    for s in L['spots']:
        place.placed.append((s['x'], s['y']))
    # saida: dois pilares curvos com luz (a Rampa do Planalto e a propria saida)
    if F.get('exit_pylons', True):
        for p in L['paths']:
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
                x, y = q[0] + nx_ * side * 46, q[1] + ny_ * side * 46
                w = place.ground(x, y)
                tip = pilar_saida(root, f'saida{side}_{k}', tuple(w), M, s=1.15)
                place.placed.append((x, y))
                if tip and F.get('lamps_glow'):
                    gx, gy = to_game(tip)
                    out['env'].append([round(gx, 1), round(gy, 1), '#ffd890', 60])


def lamps_along(L, F, root, cp, place, M, rr, out, every=170, side0=1, skip=None):
    """Postes na beira da estrada, alternando os lados (a noite viram luzes do cenario)."""
    for pi, p in enumerate(L['paths']):
        acc, side = every * 0.55, side0
        for a, b in zip(p[:-1], p[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            acc += ln
            if acc < every:
                continue
            acc = 0.0
            side = -side
            x, y = b[0] - dy / ln * 43 * side, b[1] + dx / ln * 43 * side
            if not (24 < x < GW - 24 and 70 < y < GH - 12) or not place.far_spot(x, y, 50) or not place.hud_free(x, y):
                continue
            if float(cp.road_at(x, y)) < 36 or float(cp.water_e(np.float32(x), np.float32(y))) < 1.3 or not place.free(x, y, 18):
                continue
            if skip and skip(x, y):
                continue
            # o braco aponta para a estrada (direcao de tela -> chao: y da tela desce, y do chao sobe e encolhe por SIN)
            ang = math.atan2(dx / ln * side / SIN, dy / ln * side)
            tip = poste(root, f'poste{pi}_{len(place.placed)}', tuple(place.ground(x, y)), M, s=1.0, ang=ang)
            place.placed.append((x, y))
            if F.get('lamps_glow'):
                gx, gy = to_game(tip)
                out['env'].append([round(gx, 1), round(gy + 6, 1), '#ffd890', 70])


def cerrado(L, F, root, cp, place, lote, M, rr, out, ipes=10, trees=8, tufts=160, rocks=6, bushes=10, lawn_tufts=40, ipe_s=(1.1, 1.4)):
    """Enchimento do cerrado: ipes, arvores retorcidas, capim seco, pedras e moitas (fora das pracas e da agua)."""
    no_plaza = lambda x, y: cp.plaza_at(x, y) < 0.2
    dry = lambda x, y: no_plaza(x, y) and cp.lawn_at(x, y) < 0.5
    grd = gz(cp)
    for k, (x, y) in enumerate(place.take(ipes, 28, tall=(78, 34), path_d=46, test=no_plaza)):
        ipe(root, lote, f'ipe{k}', tuple(place.ground(x, y)), rr.uniform(*ipe_s), rr, M, ground=grd)
    for k, (x, y) in enumerate(place.take(trees, 26, tall=(64, 30), path_d=46, test=dry)):
        arvore_cerrado(root, lote, f'retorcida{k}', tuple(place.ground(x, y)), rr.uniform(1.2, 1.6), rr, M)
    for k, (x, y) in enumerate(place.take(bushes, 12, path_d=40, test=no_plaza)):
        w = place.ground(x, y)
        for j in range(rr.randrange(2, 4)):
            a = rr.uniform(0, TAU)
            lote.pebble(M['arbusto'] if j % 2 else M['arbusto_l'], (w.x + 0.14 * math.cos(a) * j, w.y + 0.1 * math.sin(a) * j, w.z + 0.1),
                        rr.uniform(0.14, 0.22), squash=0.8, rot=rr.uniform(0, TAU), rr=rr, rough=0.3)
    for k, (x, y) in enumerate(place.take(rocks, 12, test=no_plaza)):
        w = place.ground(x, y)
        if rr.random() < 0.4:
            rock_cluster(root, f'pedra{k}', M['pedra'], tuple(w), rr.uniform(0.2, 0.3), rr, n=3)
        else:
            rock(root, f'pedra{k}', M['pedra'], tuple(w), rr.uniform(0.2, 0.36), rr)
    for k, (x, y) in enumerate(place.take(tufts, 5, path_d=36, test=dry)):
        capim(lote, M, tuple(place.ground(x, y)), rr.uniform(0.34, 0.6), rr)
    for k, (x, y) in enumerate(place.take(lawn_tufts, 5, path_d=36, test=lambda x, y: no_plaza(x, y) and cp.lawn_at(x, y) >= 0.5)):
        capim(lote, M, tuple(place.ground(x, y)), rr.uniform(0.18, 0.26), rr, verde=True)


def pool_ipes(L, cp, place, root, lote, M, rr, n_per=3):
    """Ipes na margem de tras dos espelhos d'agua (na frente cobririam a agua)."""
    grd = gz(cp)
    for (x, y, rx, ry, n) in cp.pools:
        got = 0
        for k in range(n_per * 8):
            if got >= n_per:
                break
            a = rr.uniform(math.pi * 1.1, math.pi * 1.9)
            e = rr.uniform(1.35, 1.75)
            gx, gy = x + rx * e * math.cos(a), y + ry * e * math.sin(a)
            if place.far_path(gx, gy, 52) and place.far_spot(gx, gy, 50) and place.hud_free(gx, gy) and place.clear_above(gx, gy, 78, 34) and place.free(gx, gy, 30):
                place.placed.append((gx, gy))
                ipe(root, lote, f'ipeEspelho{x}_{k}', tuple(place.ground(gx, gy)), rr.uniform(1.0, 1.25), rr, M, ground=grd)
                got += 1


# ---------------------------------------------------------------- fases
def fase1(L, F, root, cp, place, lote, M, rr, out):
    """Eixo Monumental: gramados largos, a plataforma da Rodoviaria com o patio dos onibus e os dois espelhos d'agua."""
    s = 1.0
    c = at(1140, 548)
    rodoviaria(root, 'rodoviaria', (c.x, c.y, 0.0), s, M)
    block_world(place, (c.x, c.y), 3.4, 1.2, up=1.5)
    # patio: onibus em vagas diagonais, com as faixas brancas
    cores = [M['azul'], M['verde'], M['amarelo'], M['vermelho'], M['azul']]
    ang = 0.55
    for k, gx in enumerate((1010, 1074, 1138, 1202)):
        w = at(gx, 652, cp)
        onibus(root, f'onibus{k}', (w.x, w.y, w.z + 0.01), ang, M, cores[k], s=1.2)
    for k, gx in enumerate((978, 1042, 1106, 1170, 1234)):
        w = at(gx, 652, cp)
        lote.box(M['conc_l'], (2.0, 0.06, 0.012), (w.x, w.y, w.z + 0.006), rot=(0, 0, ang))
    place.block(940, 600, 1280, 720)
    lamps_along(L, F, root, cp, place, M, rr, out, every=190)
    pool_ipes(L, cp, place, root, lote, M, rr, n_per=3)
    for k, (x, y) in enumerate(place.take(6, 16, path_d=44, test=lambda x, y: cp.lawn_at(x, y) > 0.6)):
        banco(root, f'banco{k}', tuple(place.ground(x, y)), M, ang=rr.choice((0.0, 0.0, math.pi / 2)))
    cerrado(L, F, root, cp, place, lote, M, rr, out, ipes=14, trees=10, tufts=300, rocks=6, bushes=12, lawn_tufts=90)


def fase2(L, F, root, cp, place, lote, M, rr, out):
    """Esplanada dos Ministerios: blocos iguais em fila nas duas margens, gramado central e a Catedral."""
    # os blocos iguais: largos e baixos, como os ministerios de verdade
    for k, gx in enumerate((806, 930, 1054, 1178)):
        w = at(gx, 150)
        predio_faixas(root, f'ministerio{k}', (w.x, w.y, 0.0), 2.65, 0.95, 1.95, M)
        block_world(place, (w.x, w.y), 1.4, 0.6, up=2.2)
    for k, gx in enumerate((420, 574, 962, 1116, 1270)):
        w = at(gx, 742)
        predio_faixas(root, f'ministerioB{k}', (w.x, w.y, 0.0), 2.65, 0.95, 1.95, M)
        block_world(place, (w.x, w.y), 1.4, 0.6, up=2.2)
    w = at(112, 512, cp)
    catedral(root, 'catedral', (w.x, w.y, w.z), 1.0, M)
    block_world(place, (w.x, w.y), 1.3, 1.3, up=2.0)
    lamps_along(L, F, root, cp, place, M, rr, out, every=200)
    cerrado(L, F, root, cp, place, lote, M, rr, out, ipes=16, trees=8, tufts=240, rocks=4, bushes=10, lawn_tufts=120)


def fase3(L, F, root, cp, place, lote, M, rr, out):
    """Congresso Nacional (noite): cupula, tigela e torres gemeas; espelho d'agua; postes e janelas acendem."""
    s = 1.0
    w = at(566, 174)
    sub, info = congresso(root, 'congresso', (w.x, w.y, 0.0), s, M, glass=M['janela'], glass2=M['janela'], Ht=3.55)
    block_world(place, (w.x, w.y), info['W'] / 2 + 0.3, info['D'] / 2 + info['rl'], up=1.4)
    block_world(place, (w.x, w.y + info['ty']), 1.1, 0.4, up=info['Ht'])
    # luz das janelas das torres (pequena: o predio continua escuro, so as janelas acendem)
    for sx in (-1, 1):
        gx, gy = to_game((w.x + sx * 0.6 * s, w.y + info['ty'], info['Ht'] * 0.5))
        out['env'].append([round(gx, 1), round(gy, 1), '#ffd07a', 55])
    # anexo (bloco de ministerio) na direita
    w2 = at(1226, 336)
    predio_faixas(root, 'anexo', (w2.x, w2.y, 0.0), 1.9, 0.9, 2.0, M, glass=M['janela'])
    block_world(place, (w2.x, w2.y), 1.05, 0.55, up=2.3)
    gx, gy = to_game((w2.x, w2.y - 0.45, 1.1))
    out['env'].append([round(gx, 1), round(gy, 1), '#ffd07a', 70])
    lamps_along(L, F, root, cp, place, M, rr, out, every=150)
    cerrado(L, F, root, cp, place, lote, M, rr, out, ipes=12, trees=10, tufts=300, rocks=6, bushes=10, lawn_tufts=80)


def fase4(L, F, root, cp, place, lote, M, rr, out):
    """Praca dos Tres Poderes (tempestade): pedra portuguesa, mastro, pombal, pombos e o STF de colunas curvas."""
    w = at(1188, 322)
    stf(root, 'stf', (w.x, w.y, 0.0), 1.0, M)
    block_world(place, (w.x, w.y), 2.3, 1.5, up=1.3)
    w = at(470, 152, cp)
    mastro(root, 'mastro', (w.x, w.y, w.z), 1.0, M, rr)
    place.block(430, 20, 560, 175)
    pts = place.take(1, 30, tall=(80, 30), path_d=60, test=lambda x, y: cp.plaza_at(x, y) > 0.8)
    for (x, y) in pts:
        pombal(root, 'pombal', tuple(place.ground(x, y)), 1.0, M)
    grd = gz(cp)
    for k, (x, y) in enumerate(place.take(9, 26, path_d=46, test=lambda x, y: cp.plaza_at(x, y) > 0.8)):
        w = place.ground(x, y)
        pombos(lote, M, (w.x, w.y), rr.randrange(5, 10), rr, grd, spread=0.5)
    for k, (x, y) in enumerate(place.take(8, 16, path_d=44, test=lambda x, y: cp.plaza_at(x, y) > 0.8)):
        banco(root, f'banco{k}', tuple(place.ground(x, y)), M, ang=rr.choice((0.0, 0.0, math.pi / 2)))
    for k, (x, y) in enumerate(place.take(5, 30, path_d=50, test=lambda x, y: cp.plaza_at(x, y) > 0.8)):
        jardineira(root, lote, f'floreira{k}', tuple(place.ground(x, y)), 1.0, 0.36, M, rr, ang=rr.uniform(-0.2, 0.2))
    lamps_along(L, F, root, cp, place, M, rr, out, every=180)
    cerrado(L, F, root, cp, place, lote, M, rr, out, ipes=10, trees=8, tufts=220, rocks=4, bushes=8, lawn_tufts=20)


def path_y(L, pi, x):
    """y do caminho pi na tela em x (primeiro trecho que cruza x)."""
    p = L['paths'][pi]
    for (ax, ay), (bx, by) in zip(p[:-1], p[1:]):
        if min(ax, bx) <= x <= max(ax, bx) and ax != bx:
            return ay + (by - ay) * (x - ax) / (bx - ax)
    return p[-1][1]


def fase5(L, F, root, cp, place, lote, M, rr, out):
    """Rampa do Planalto: o palacio com as colunas curvas e a RAMPA no fim da estrada (a saida dos inimigos): ela sobe
    pelo ultimo trecho do caminho ate o piso nobre e um patamar leva ao palacio, logo atras."""
    s = 1.4
    W, D = 6.2, 1.1
    yc = D / 2 + 0.32 * s
    front = 546                               # linha das colunas da frente, na tela
    cy = (360 - front) / (GB * SIN) + yc
    cx = (1128 - 640) / GB
    sub, info = planalto(root, 'planalto', (cx, cy, 0.0), s, M, glass=M['janela'], W=W, D=D, n_col=7)
    block_world(place, (cx, cy), W / 2 + 0.5, yc + 0.35, up=info['Hc'] + 0.3, front=14)
    x0, x1 = 1100, 1232
    w0 = to_world(x0, path_y(L, 0, x0))
    w0.z = cp.height_at(w0.x, w0.y) - 0.02
    w1 = to_world(x1, path_y(L, 0, x1))
    w1.z = info['zf'] + 0.05
    rampa(root, 'rampa', tuple(w0), tuple(w1), 1.35, M)
    # patamar: do alto da rampa ate a frente do palacio (sai pela direita da tela), com muretas e pilares finos
    yf = cy - yc
    y_lo = w1.y - 0.62
    px = w1.x + 0.5
    ln = yf - y_lo + 0.1
    box(root, 'patamar', (1.1, ln, 0.12), (px, (yf + y_lo) / 2, w1.z - 0.06), m=M['conc_l'], bev=0.03)
    for sx in (-1, 1):
        box(root, f'patamar_mureta{sx}', (0.07, ln - 0.1 if sx > 0 else ln - 1.3, 0.17),
            (px + sx * 0.52, (yf + y_lo) / 2 + (0 if sx > 0 else 0.6), w1.z + 0.07), m=M['conc'], bev=0.025)
    for k, yy in enumerate((y_lo + 0.35, (yf + y_lo) / 2, yf - 0.25)):
        cyl(root, f'patamar_pilar{k}', 0.06, w1.z - 0.14, (px - 0.35, yy, (w1.z - 0.14) / 2), m=M['conc'], v=12, bev=0.01)
    lo, hi = to_game((w0.x - 0.2, w0.y - 0.8, 0)), to_game((px + 0.8, yf, 1.0))
    place.block(lo[0], hi[1], hi[0], lo[1] + 10)
    gx, gy = to_game((cx, cy - yc, 0.9))
    out['env'].append([round(gx, 1), round(gy, 1), '#ffd07a', 130])
    gx, gy = to_game((cx - W * 0.3, cy - yc, 0.9))
    out['env'].append([round(gx, 1), round(gy, 1), '#ffd07a', 110])
    out['rampa'] = [x0, round(path_y(L, 0, x0), 1), x1, round(path_y(L, 0, x1), 1)]
    lamps_along(L, F, root, cp, place, M, rr, out, every=170, skip=lambda x, y: x > 1040 and y > 540)
    pool_ipes(L, cp, place, root, lote, M, rr, n_per=4)
    cerrado(L, F, root, cp, place, lote, M, rr, out, ipes=16, trees=10, tufts=280, rocks=5, bushes=10, lawn_tufts=90)


FASES = {
    1: dict(build=fase1,
            lawns=[(700, 330, 560, 200, 4), (690, 118, 200, 70, 3), (790, 600, 200, 90, 3)],
            plazas=[('laje', 1140, 556, 170, 46, 5), ('asfalto', 1118, 656, 190, 52, 4)]),
    2: dict(build=fase2,
            lawns=[(690, 360, 640, 150, 4)],
            plazas=[('laje', 1020, 150, 290, 42, 6), ('laje', 830, 742, 520, 40, 6), ('pedra', 112, 520, 80, 42, 2.4)]),
    3: dict(build=fase3, lamps_glow=True, janela=0.45,
            lawns=[(566, 250, 260, 70, 3), (700, 470, 520, 160, 3)],
            plazas=[('laje', 566, 182, 186, 44, 5), ('laje', 1226, 340, 64, 30, 4)],
            pools=[(472, 218, 48, 11, 5), (660, 218, 48, 11, 5)]),
    4: dict(build=fase4, th=dict(road_paved=True, waves=1.0, road='#b4573a', road_d='#8f4630', exposure=-0.6),
            road_stones=0.0,
            lawns=[],
            plazas=[('pedra', 690, 380, 470, 250, 3.5), ('pedra', 1188, 326, 112, 66, 4), ('pedra', 470, 150, 90, 50, 3)]),
    5: dict(build=fase5, lamps_glow=True, exit_pylons=False, janela=0.8,
            lawns=[(950, 220, 330, 150, 3), (300, 380, 220, 120, 3)],
            plazas=[('laje', 1128, 522, 168, 36, 6)]),
}


# ---------------------------------------------------------------- montagem e render
def build_level_br(L, idx, root, P):
    F = FASES[idx + 1]
    cp = CampoBR(L, F)
    rr = random.Random(L['seed'] * 101 + 7)
    out = {'palms': [], 'env': []}
    M = br_mats()
    if 'janela' in F:
        GLOW_MATS[M['janela'].name] = F['janela']
    build_ground_br(cp, root)
    build_pools(cp, root, M)
    lote = Lote('miudos')
    place = LugarBR(cp, L, rr)
    build_common(L, F, root, P, cp, place, lote, M, rr, out)
    F['build'](L, F, root, cp, place, lote, M, rr, out)
    lote.done(root)
    out['_cp'] = cp
    return out


def render_level_br(idx, out_dir, samples=96, k=3.0):
    with open(os.path.join(out_dir, 'fases.json')) as fh:
        LV = json.load(fh)
    L = LV[idx]
    F = FASES[idx + 1]
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
    th = dict(BASE, **F.get('th', {}))
    sc.view_settings.exposure = th['exposure']
    bpy.data.objects['ChaoSombra'].hide_render = True
    sc.cycles.samples = samples
    P = palette2()
    root = make_root('raiz_cenario', 'cenario', coll_for('Cenario'))
    meta = build_level_br(L, idx, root, P)
    meta.pop('_cp')
    C.setup_camera(k)
    sc.render.image_settings.color_mode = 'RGB'
    path = os.path.join(out_dir, f'f{idx + 1}.png')
    render_to(path)
    glow = bool(meta.get('env'))
    if glow:
        # so as janelas e os postes acesos: a poca de luz no chao vem da propria luminaria
        BUILT['cenario'] = {'lights': []}
        render_glow_pass('cenario', os.path.join(out_dir, f'f{idx + 1}_glow.png'))
    meta['glow'] = glow
    meta['k'] = k
    with open(os.path.join(out_dir, f'f{idx + 1}.json'), 'w') as fh:
        json.dump(meta, fh)
    print('FUNDO_OK', path, len(meta['env']), 'luzes')


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'fundo':
        out = args[1]
        idxs = [int(a) - 1 for a in args[2].split(',')]
        samples = int(args[3]) if len(args) > 3 else 96
        k = float(args[4]) if len(args) > 4 else 3.0
        for i in idxs:
            render_level_br(i, out, samples, k)
