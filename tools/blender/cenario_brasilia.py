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
(python3 tools/sprites/empacotar.py --cenario) grava sprites/cenario_f<N>.jpg (+ _luz) e so a chave cenario do
js/sprites_meta.js.
Final: 6 px por unidade do jogo (7680x4320, o padrao: aguenta o zoom 2x da camera numa tela Retina); previa: 0.5.
A camera e o enquadramento nao dependem disso: px_por_unidade so muda a resolucao.
Detalhe de perto (ver ground_material_br e Det): borda nitida da estrada, marcas de pneu, pedrisco, meio-fio na
estrada calcada, capim baixo, flores de ipe, base dos postes, lixeiras, bancos, placas sem texto, gradis, sobras de
manifestacao em cores neutras e pocas na tempestade.
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
        self.DV, self.SD, self.S = self.via_field(L['paths'])

    def via_field(self, paths, M=70):
        """Por pixel de tela: distancia COM SINAL ao eixo da estrada mais proxima (lado esquerdo +) e o comprimento ao
        longo dela. O shader do chao usa os dois (interpolados por vertice) para a borda nitida da estrada, as marcas de
        pneu e as faixas pintadas, que assim ficam finas em qualquer resolucao."""
        D = np.full((MH, MW), 999.0, np.float32)
        SD = np.full((MH, MW), 999.0, np.float32)
        S = np.zeros((MH, MW), np.float32)
        for pts in paths:
            P = np.asarray(pts, np.float32)
            cum = 0.0
            for i in range(len(P) - 1):
                ax, ay = P[i]
                bx, by = P[i + 1]
                dx, dy = bx - ax, by - ay
                ln = math.hypot(dx, dy) or 1e-6
                x0 = int(max(min(ax, bx) - M - MX0, 0))
                x1 = int(min(max(ax, bx) + M - MX0, MW - 1)) + 1
                y0 = int(max(min(ay, by) - M - MY0, 0))
                y1 = int(min(max(ay, by) + M - MY0, MH - 1)) + 1
                if x0 < x1 and y0 < y1:
                    xs, ys = self.XX[y0:y1, x0:x1], self.YY[y0:y1, x0:x1]
                    t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / (ln * ln), 0, 1)
                    d = np.hypot(xs - (ax + t * dx), ys - (ay + t * dy))
                    sg = np.where(dx * (ys - ay) - dy * (xs - ax) >= 0, 1.0, -1.0).astype(np.float32)
                    upd = d < D[y0:y1, x0:x1]
                    D[y0:y1, x0:x1] = np.where(upd, d, D[y0:y1, x0:x1])
                    SD[y0:y1, x0:x1] = np.where(upd, sg * d, SD[y0:y1, x0:x1])
                    S[y0:y1, x0:x1] = np.where(upd, cum + t * ln, S[y0:y1, x0:x1])
                cum += ln
        return D, SD, S

    @staticmethod
    def bilin(F, gx, gy):
        fx = np.clip(np.asarray(gx, np.float32) - MX0, 0, MW - 1.001)
        fy = np.clip(np.asarray(gy, np.float32) - MY0, 0, MH - 1.001)
        x0, y0 = fx.astype(np.int64), fy.astype(np.int64)
        tx, ty = fx - x0, fy - y0
        return (F[y0, x0] * (1 - tx) * (1 - ty) + F[y0, x0 + 1] * tx * (1 - ty)
                + F[y0 + 1, x0] * (1 - tx) * ty + F[y0 + 1, x0 + 1] * tx * ty)

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
        lk0 = self.zone(gx, gy, self.lawns, soft=0.12)
        lk = lk0 * (1 - pk)
        # campo das pracas para o shader (borda nitida de perto): menor 'e' de superelipse por tipo de praca
        def emin(kinds):
            out = np.full(np.shape(gx), 9.0, np.float32)
            for (kd, x, y, rx, ry, n) in self.plazas:
                if kd in kinds:
                    out = np.minimum(out, superellipse_e(gx, gy, x, y, rx, ry, n))
            return out
        e_ped, e_laj, e_asf = emin(('pedra',)), emin(('laje',)), emin(('asfalto',))
        e_pr = np.minimum(np.minimum(e_ped, e_laj), e_asf)
        pk_h = 1 - sstep(0.94, 1.0, e_pr)   # altura: transicao um pouco mais larga (sem degrau serrilhado na borda)
        flat = sstep(30, 95, d) * sstep(0.85, 1.9, ds) * sstep(1.05, 1.6, e)
        h = rel * flat * (1 - pk_h) + 0.02 * pk_h
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
        col = col * (1 - lk0[:, None]) + lawn * lk0[:, None]
        # pracas: pedra portuguesa clara com ondas cinza (calcadao) e placas de concreto. A cor da praca vai a parte
        # ('cor_praca', sem a borda) e o shader corta a borda por pixel com o campo 'praca' interpolado
        wave = 0.5 + 0.5 * np.sin(gx / 23.0 + 2.2 * np.sin(gy / 31.0) + gy / 57.0)
        stripe = sstep(0.82, 0.9, wave).astype(np.float32) * float(th.get('waves', 0.0))
        pedra = hex3(th['pedra'])[None] * (1 - stripe[:, None]) + hex3(th['pedra_d'])[None] * stripe[:, None]
        is_ped = (e_ped <= e_laj).astype(np.float32)
        asf = 1 - sstep(0.98, 1.0, e_asf)
        pcol = pedra * is_ped[:, None] + hex3(th['laje'])[None] * (1 - is_ped[:, None])
        pcol = pcol * (1 - asf[:, None]) + hex3(th['asfalto'])[None] * asf[:, None]
        lj = (1 - is_ped) * (1 - asf) * (e_pr < 1.3)
        # estrada de terra vermelha (ou de pedra vermelha, na praca): a cor da estrada vai a parte ('cor_via') e o
        # shader mistura as duas com a distancia interpolada por vertice ('via'): borda nitida em qualquer resolucao
        roadk = 1 - sstep(24, 33, d)
        road = hex3(th['road'])[None] * (1 - 0.1 * np.exp(-((d - 11.0) / 3.5) ** 2))[:, None]
        road = road * (1 - sstep(15, 27, d))[:, None] + hex3(th['road_d'])[None] * sstep(15, 27, d)[:, None]
        padk = 1 - sstep(0.62, 0.8, self.spot_dist(X, Y, high=False))
        bed = 1 - sstep(0.85, 1.0, e)
        rim = (1 - sstep(1.07, 1.1, e)) * sstep(0.9, 1.0, e)   # termina sob a borda 3D (sem halo claro de perto)
        cols = []
        for c_ in (col, pcol):   # lotes e espelhos d'agua por cima, no chao e na praca
            c_ = c_ * (1 - padk[:, None]) + hex3(th['pad'])[None] * padk[:, None]
            c_ = c_ * (1 - bed[:, None]) + hex3(th['bed'])[None] * bed[:, None]
            cols.append(c_ * (1 - rim[:, None]) + hex3('#d8d2c4')[None] * rim[:, None])
        col, pcol = cols
        wet = (1 - sstep(0.95, 1.02, e)).astype(np.float32)
        # mascaras de juntas e pedrinhas: so o tipo da praca (a borda o shader corta) e, calcada, a estrada da praca
        Rm = (lj * (1 - roadk)).astype(np.float32)
        Bm = (is_ped * (e_pr < 1.3) * (1 - roadk) + (roadk * pk if paved else 0)).astype(np.float32)
        # campos do shader: distancia e lado da estrada, comprimento ao longo dela; zonas (gramado, cerrado, praca)
        dv = self.bilin(self.DV, gx, gy)
        sdv = np.clip(self.bilin(self.SD, gx, gy), -150, 150)
        sv = self.bilin(self.S, gx, gy)
        free = (1 - padk) * sstep(1.08, 1.25, e)
        lawn_k = (lk0 * free).astype(np.float32)          # o shader tira a praca (por pixel)
        sand_k = ((1 - lk0) * free).astype(np.float32)
        # (normalizados para 0..1: o atributo de cor nao precisa guardar valores fora da faixa)
        via = np.stack([np.minimum(dv, 99.0) / 100.0, (sdv + 200.0) / 400.0, sv / 4000.0, np.full_like(dv, 1.0 if paved else 0.0)], 1).astype(np.float32)
        zona = np.stack([lawn_k, sand_k, np.minimum(e_pr, 2.0) / 2.0, np.ones_like(lawn_k)], 1).astype(np.float32)
        return dict(h=h.astype(np.float32), col=col.astype(np.float32), pcol=pcol.astype(np.float32), road=road.astype(np.float32), via=via, zona=zona,
                    R=Rm, G=wet, B=Bm, d=d, ds=ds, e=e, pk=pk, lk=lk)

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
def ground_material_br(th=None):
    """Chao: cor do vertice ('cor', sem a estrada) com variacao macia; mascara R = placas de concreto (juntas),
    G = molhado, B = pedra portuguesa (pedrinhas em voronoi).
    Detalhe de perto (zoom 2x da camera do jogo), calculado por pixel a partir dos campos interpolados por vertice:
    'via' = (distancia ao eixo da estrada, lado + 200, comprimento ao longo dela, estrada calcada) e 'cor_via' (a cor
    da estrada): a borda da estrada sai nitida e um pouco irregular, a terra ganha marcas de pneu e pedrisco, o cerrado
    e o gramado ganham grao fino e a estrada calcada ganha as faixas pintadas da beira. 'zona' = (gramado, cerrado,
    praca)."""
    th = th or {}
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
    av = N.new('ShaderNodeAttribute'); av.attribute_name = 'via'
    ac = N.new('ShaderNodeAttribute'); ac.attribute_name = 'cor_via'
    ap = N.new('ShaderNodeAttribute'); ap.attribute_name = 'cor_praca'
    az = N.new('ShaderNodeAttribute'); az.attribute_name = 'zona'
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateColor')
    L.new(k.outputs['Color'], sep.inputs['Color'])
    sv = N.new('ShaderNodeSeparateColor')
    L.new(av.outputs['Color'], sv.inputs['Color'])
    sz = N.new('ShaderNodeSeparateColor')
    L.new(az.outputs['Color'], sz.inputs['Color'])
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

    def smooth(x, e0, e1):
        n = N.new('ShaderNodeMapRange')
        n.interpolation_type = 'SMOOTHSTEP'
        n.inputs['From Min'].default_value = e0
        n.inputs['From Max'].default_value = e1
        L.new(x, n.inputs['Value'])
        return n.outputs['Result']

    def mix(fac, c0, c1):
        n = N.new('ShaderNodeMix')
        n.data_type = 'RGBA'
        n.clamp_factor = True
        sock = lambda socks, nm: next(x for x in socks if x.name == nm and x.type in ('RGBA', 'VALUE') and (x.type == 'RGBA' or nm == 'Factor'))
        L.new(fac, sock(n.inputs, 'Factor'))
        for nm, c in (('A', c0), ('B', c1)):
            if isinstance(c, tuple):
                sock(n.inputs, nm).default_value = c
            else:
                L.new(c, sock(n.inputs, nm))
        return next(x for x in n.outputs if x.type == 'RGBA')

    def noise(scale, detail=2.0, vec=None, w=None):
        n = N.new('ShaderNodeTexNoise')
        if w is not None:
            n.noise_dimensions = '1D'
            L.new(w, n.inputs['W'])
        else:
            L.new(vec or tc.outputs['Object'], n.inputs['Vector'])
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        return n.outputs['Fac']

    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 26; nz.inputs['Detail'].default_value = 4
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    # praca: mascara por pixel a partir do 'e' da superelipse interpolado (borda nitida, sem degraus de vertice)
    pk_s = mth('SUBTRACT', 1.0, smooth(mth('MULTIPLY', sz.outputs['Blue'], 2.0), 0.98, 1.0))
    # juntas das placas (0,62 de lado) e pedrinhas da pedra portuguesa
    def joint(axis):
        f = mth('ABSOLUTE', mth('SUBTRACT', mth('FRACT', mth('MULTIPLY', xyz.outputs[axis], 1 / 0.62)), 0.5))
        return mth('SMOOTH_MIN', mth('MULTIPLY', mth('MAXIMUM', mth('SUBTRACT', f, 0.465), 0.0), 40.0), 1.0, 0.1)
    jl = mth('MULTIPLY', mth('MULTIPLY', mth('MAXIMUM', joint('X'), joint('Y')), sep.outputs['Red']), pk_s)
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 13.0
    L.new(tc.outputs['Object'], vo.inputs['Vector'])
    groove = mth('MULTIPLY', mth('MULTIPLY', mth('SUBTRACT', 1.0, mth('MINIMUM', mth('DIVIDE', vo.outputs['Distance'], 0.07), 1.0)), sep.outputs['Blue']), pk_s)
    # cor: escurece um pouco nas juntas e entre as pedrinhas
    dark = mth('SUBTRACT', 1.0, mth('ADD', mth('MULTIPLY', jl, 0.22), mth('MULTIPLY', groove, 0.16)))
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.95; mr.inputs['To Max'].default_value = 1.05
    L.new(nz.outputs['Fac'], mr.inputs['Value'])
    val = mth('MULTIPLY', mr.outputs['Result'], dark)

    # ---- estrada: mascara por pixel (borda nitida, levemente irregular), em px de tela do jogo
    d, S, paved = mth('MULTIPLY', sv.outputs['Red'], 100.0), mth('MULTIPLY', sv.outputs['Blue'], 4000.0), av.outputs['Alpha']
    sd = mth('SUBTRACT', mth('MULTIPLY', sv.outputs['Green'], 400.0), 200.0)
    e0, e1 = th.get('edge', (26.9, 30.1))
    # borda irregular na terra; reta na estrada calcada (la ela encosta no meio-fio)
    wob = mth('MULTIPLY', mth('MULTIPLY', mth('SUBTRACT', noise(4.0, 0.0), 0.5), 2.6), mth('SUBTRACT', 1.0, paved))
    rm = mth('SUBTRACT', 1.0, smooth(mth('ADD', d, wob), e0, e1))
    dirt = mth('MULTIPLY', rm, mth('SUBTRACT', 1.0, paved))
    # marcas de pneu na terra: dois carros (trilhas de 3 px com cravos em V), somem e voltam ao longo da estrada
    tracks = None
    for (c, w, seed) in ((11.0, 1.45, 0.0), (-11.0, 1.45, 0.0), (16.0, 1.25, 7.3), (-6.0, 1.25, 7.3)):
        dist = mth('ABSOLUTE', mth('SUBTRACT', sd, c))
        line = mth('SUBTRACT', 1.0, smooth(dist, w - 0.45, w + 0.45))
        tread = mth('ADD', 0.8, mth('MULTIPLY', mth('SINE', mth('MULTIPLY', mth('ADD', S, mth('MULTIPLY', dist, 0.9)), TAU / 2.8)), 0.2))
        vis = smooth(noise(1.0, 1.0, w=mth('ADD', mth('DIVIDE', S, 120.0), seed)), 0.47, 0.6)
        t = mth('MULTIPLY', mth('MULTIPLY', line, tread), vis)
        tracks = t if tracks is None else mth('MAXIMUM', tracks, t)
    tracks = mth('MULTIPLY', tracks, dirt)
    val = mth('MULTIPLY', val, mth('SUBTRACT', 1.0, mth('MULTIPLY', tracks, th.get('tracks', 0.17))))
    # pedrisco: pedrinhas de ~1 px do jogo (claras e escuras) na terra da estrada e, mais raras, no cerrado
    vg = N.new('ShaderNodeTexVoronoi'); vg.inputs['Scale'].default_value = 15.0
    L.new(tc.outputs['Object'], vg.inputs['Vector'])
    rnd = N.new('ShaderNodeSeparateColor')
    L.new(vg.outputs['Color'], rnd.inputs['Color'])
    dot = mth('SUBTRACT', 1.0, smooth(vg.outputs['Distance'], 0.16, 0.24))
    off = mth('MULTIPLY', mth('SUBTRACT', 1.0, rm), mth('SUBTRACT', 1.0, pk_s))
    sand = mth('MULTIPLY', sz.outputs['Green'], off)
    lawn = mth('MULTIPLY', sz.outputs['Red'], off)
    gsel = mth('LESS_THAN', rnd.outputs['Red'], mth('ADD', mth('MULTIPLY', dirt, 0.3), mth('MULTIPLY', sand, 0.14)))
    grav = mth('MULTIPLY', mth('MULTIPLY', dot, gsel), mth('MINIMUM', mth('ADD', dirt, sand), 1.0))
    val = mth('MULTIPLY', val, mth('ADD', 1.0, mth('MULTIPLY', grav, mth('SUBTRACT', mth('MULTIPLY', rnd.outputs['Green'], 0.34), 0.15))))
    # cerrado: grao fino e pintinhas escuras (folhinha seca, terra); gramado: textura miuda de touceira
    val = mth('MULTIPLY', val, mth('ADD', 1.0, mth('MULTIPLY', mth('SUBTRACT', noise(48.0, 2.0), 0.5), mth('ADD', mth('MULTIPLY', sand, 0.1), mth('MULTIPLY', lawn, 0.16)))))
    # terra: estrias de poeira ao longo da estrada (ruido esticado no sentido do caminho)
    cxyz = N.new('ShaderNodeCombineXYZ')
    L.new(mth('MULTIPLY', S, 0.035), cxyz.inputs['X'])
    L.new(mth('MULTIPLY', sd, 0.3), cxyz.inputs['Y'])
    streak = mth('SUBTRACT', noise(1.0, 2.0, vec=cxyz.outputs['Vector']), 0.5)
    val = mth('MULTIPLY', val, mth('ADD', 1.0, mth('MULTIPLY', streak, mth('MULTIPLY', dirt, 0.16))))
    # gramado: touceirinhas (celulas miudas com brilho sorteado)
    vt = N.new('ShaderNodeTexVoronoi'); vt.inputs['Scale'].default_value = 21.0
    L.new(tc.outputs['Object'], vt.inputs['Vector'])
    rt_ = N.new('ShaderNodeSeparateColor')
    L.new(vt.outputs['Color'], rt_.inputs['Color'])
    val = mth('MULTIPLY', val, mth('ADD', 1.0, mth('MULTIPLY', mth('SUBTRACT', rt_.outputs['Green'], 0.5), mth('MULTIPLY', lawn, 0.12))))
    vs = N.new('ShaderNodeTexVoronoi'); vs.inputs['Scale'].default_value = 9.0
    L.new(tc.outputs['Object'], vs.inputs['Vector'])
    rs = N.new('ShaderNodeSeparateColor')
    L.new(vs.outputs['Color'], rs.inputs['Color'])
    spk = mth('MULTIPLY', mth('SUBTRACT', 1.0, smooth(vs.outputs['Distance'], 0.1, 0.17)), mth('LESS_THAN', rs.outputs['Red'], 0.22))
    val = mth('MULTIPLY', val, mth('SUBTRACT', 1.0, mth('MULTIPLY', spk, mth('ADD', mth('MULTIPLY', sand, 0.1), mth('MULTIPLY', lawn, 0.08)))))

    base = mix(rm, mix(pk_s, a.outputs['Color'], ap.outputs['Color']), ac.outputs['Color'])
    hsv = N.new('ShaderNodeHueSaturation')
    L.new(base, hsv.inputs['Color'])
    L.new(val, hsv.inputs['Value'])
    col = hsv.outputs['Color']
    # estrada calcada: meio-fio de concreto (blocos de ~9 px com junta) entre a pista e a praca
    c0, c1 = th.get('curb', (27.4, 30.6))
    curb = mth('MULTIPLY', mth('MULTIPLY', smooth(d, c0 - 0.35, c0 + 0.35), mth('SUBTRACT', 1.0, smooth(d, c1 - 0.35, c1 + 0.35))), paved)
    jd = mth('MULTIPLY', mth('ABSOLUTE', mth('SUBTRACT', mth('FRACT', mth('ADD', mth('DIVIDE', S, 9.0), 0.5)), 0.5)), 9.0)
    joint_c = mth('SUBTRACT', 1.0, smooth(jd, 0.25, 0.5))
    curb_col = mix(joint_c, tuple(lin('#ddd7ca')), tuple(lin('#a9a294')))
    shade = mth('ADD', 0.86, mth('MULTIPLY', smooth(d, c0, c1), 0.14))   # face de dentro do meio-fio um pouco mais escura
    col = mix(curb, col, mix(mth('SUBTRACT', 1.0, shade), curb_col, tuple(lin('#9c9586'))))
    # estrada calcada: faixas pintadas (creme, gastas) na beira (desligadas por padrao: liam como pista de atletismo)
    if th.get('paint', False):
        pl = mth('SUBTRACT', 1.0, smooth(mth('ABSOLUTE', mth('SUBTRACT', d, th.get('paint_d', 22.5))), 0.55, 0.95))
        worn = smooth(noise(16.0, 3.0), 0.36, 0.52)
        pf = mth('MULTIPLY', mth('MULTIPLY', mth('MULTIPLY', pl, worn), mth('MULTIPLY', paved, rm)), 0.85)
        col = mix(pf, col, tuple(lin('#efe8d8')))
    L.new(col, bsdf.inputs['Base Color'])
    hgt = mth('SUBTRACT', mth('SUBTRACT', mth('MULTIPLY', nz.outputs['Fac'], 0.25), mth('MULTIPLY', jl, 0.5)), mth('MULTIPLY', groove, 0.35))
    hgt = mth('ADD', mth('SUBTRACT', hgt, mth('MULTIPLY', tracks, 0.45)), mth('MULTIPLY', grav, 0.5))
    hgt = mth('ADD', hgt, mth('MULTIPLY', mth('SUBTRACT', curb, mth('MULTIPLY', joint_c, curb)), 1.2))
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; bp.inputs['Distance'].default_value = 0.03
    L.new(hgt, bp.inputs['Height'])
    L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.92; rg.inputs['To Max'].default_value = 0.4
    L.new(sep.outputs['Green'], rg.inputs['Value'])
    rough = rg.outputs['Result']
    if th.get('wet_road'):
        # tempestade: a estrada calcada fica com o brilho de chao molhado
        rough = mth('SUBTRACT', rough, mth('MULTIPLY', rm, th['wet_road']))
    L.new(rough, bsdf.inputs['Roughness'])
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
    mat_ = ground_material_br(cp.th)
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
        for nm, key in (('cor_via', 'road'), ('cor_praca', 'pcol')):
            cv = me.color_attributes.new(nm, 'FLOAT_COLOR', 'POINT')
            cv.data.foreach_set('color', np.concatenate([r[key][sl], np.ones((len(verts), 1), np.float32)], 1).ravel())
        for nm in ('via', 'zona'):
            at = me.color_attributes.new(nm, 'FLOAT_COLOR', 'POINT')
            at.data.foreach_set('color', np.ascontiguousarray(r[nm][sl]).ravel())
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
        made = lote_concreto(empty(root, f'lote{k}', tuple(base)), P, f'lote{k}')
        # o lote vazio do fundo e neutro: a faixa pintada da chapa (verde ou vermelha) so vem com a torre construida
        for o in made or []:
            if 'Chapa' in o.name:
                bpy.data.objects.remove(o, do_unlink=True)
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


# ---------------------------------------------------------------- detalhes de perto (zoom 2x da camera do jogo)
# Pecas miudas que so aparecem de perto: pedrisco e capim baixo na beira da estrada, flores de ipe caidas, tufos e
# seixos em volta dos lotes, base dos postes, lixeiras, bancos, placas sem texto, gradis e sobras de manifestacao
# (bandeirinhas lisas de cores neutras, confete, cartaz de papelao em branco, copinho), e pocas na tempestade.
# Tudo fora da estrada e dos lotes, com um sorteio proprio (os enfeites grandes de cada fase nao mudam de lugar).
def det_mats(M):
    def alpha_mat(key, hexcol, a, rough):
        m = M_(key, hexcol, rough=rough, var=0.0, bump=0.0)
        b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs['Alpha'].default_value = a
        return m
    return dict(
        pedrisco=[M['seixo'], M['pedra'], M_('pedrisco_esc', '#a99c88', rough=0.85, var=0.12, bump=0.2)],
        lixeira=M_('lixeira', '#5d6c66', rough=0.45, metal=0.35, var=0.03, bump=0.02),
        placa=M_('placa_verde', '#2f6b55', rough=0.45, var=0.02, bump=0.0),
        placa_borda=M_('placa_borda', '#eceee8', rough=0.45, var=0.02, bump=0.0),
        papelao=M_('papelao', '#bb9a6c', rough=0.92, var=0.06, bump=0.12),
        papel=M_('papel', '#f2efe6', rough=0.7, var=0.03, bump=0.02),
        vareta=M_('vareta', '#cdb68e', rough=0.8, var=0.05, bump=0.05),
        panos=[M_('pano_branco', '#f3f0ea', rough=0.8, sheen=0.3), M_('pano_creme', '#e9ddc2', rough=0.8, sheen=0.3),
               M_('pano_cinza', '#c0c3c5', rough=0.8, sheen=0.3), M_('pano_azulado', '#b6c5d1', rough=0.8, sheen=0.3)],
        confete=[M_('confete_branco', '#f7f4ee', rough=0.5), M_('confete_rosa', '#f2bccb', rough=0.5),
                 M_('confete_lilas', '#cdbbe6', rough=0.5), M_('confete_celeste', '#abd5ee', rough=0.5),
                 M_('confete_pessego', '#f6cba2', rough=0.5)],
        folha=[M['folha'], M['folha_l'], M_('folha_seca', '#a8874a', rough=0.8, var=0.1, bump=0.05)],
        poca=alpha_mat('poca', '#647f8c', 0.86, 0.04),
        poca_brilho=alpha_mat('poca_brilho', '#c4d7dd', 0.55, 0.04),
        molhado=alpha_mat('chao_molhado', '#2e2620', 0.2, 0.3),
    )


def spot_centers(L):
    out = []
    for s in L['spots']:
        c = mesa_center(s) if s['high'] else to_world(s['x'], s['y'])
        out.append((c.x, c.y, 1.0, s))
    return out


class Det:
    def __init__(self, L, F, root, cp, place, M, rr):
        self.L, self.F, self.root, self.cp, self.place, self.M, self.rr = L, F, root, cp, place, M, rr
        self.D = det_mats(M)
        self.SC = spot_centers(L)
        self.lote = Lote('detalhes')
        self.ipes = []
        for o in root.children_recursive:
            if o.name.startswith('ipe') and o.name.endswith('_tronco') and o.type == 'MESH' and len(o.data.vertices):
                v = o.data.vertices[0].co
                self.ipes.append((v.x, v.y))
        self.n = dict()

    def count(self, k, n=1):
        self.n[k] = self.n.get(k, 0) + n

    # ---- testes
    def road(self, x, y):
        return float(self.cp.bilin(self.cp.DV, x, y))

    def spot_gap(self, wx, wy):
        return min(math.hypot(wx - x, wy - y) - r for (x, y, r, s) in self.SC)

    def ok(self, x, y, road=31.0, gap=0.1, plaza=None, block=True, water=1.2):
        if not (-16 < x < GW + 16 and -16 < y < GH + 24):
            return False
        if self.road(x, y) < road:
            return False
        if float(self.cp.water_e(np.float32(x), np.float32(y))) < water:
            return False
        w = to_world(x, y)
        if self.spot_gap(w.x, w.y) < gap:
            return False
        if block:
            for (x0, y0, x1, y1) in self.place.blocks:
                if x0 < x < x1 and y0 < y < y1:
                    return False
        if plaza is not None:
            pz = self.cp.plaza_at(x, y)
            if (plaza is False and pz > 0.2) or (plaza is True and pz < 0.8):
                return False
        return True

    def gz(self, wx, wy):
        return self.cp.height_at(wx, wy)

    def along(self, step, fn, start=None):
        """Percorre os caminhos (px de tela) chamando fn(x, y, tx, ty) a cada ~step px (tx, ty = direcao)."""
        rr = self.rr
        for p in self.L['paths']:
            P = np.asarray(p, np.float32)
            seg = np.hypot(np.diff(P[:, 0]), np.diff(P[:, 1]))
            cum = np.concatenate([[0], np.cumsum(seg)])
            dist = rr.uniform(0, step) if start is None else start
            while dist < cum[-1]:
                i = max(1, min(int(np.searchsorted(cum, dist)), len(P) - 1))
                a, b = P[i - 1], P[i]
                ln = max(float(seg[i - 1]), 1e-6)
                t = (dist - cum[i - 1]) / ln
                fn(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, (b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
                dist += step * rr.uniform(0.6, 1.4)

    @staticmethod
    def side(x, y, tx, ty, s, o):
        return x - ty * s * o, y + tx * s * o

    @staticmethod
    def world_ang(tx, ty):
        """Angulo no chao de uma direcao de tela (y da tela desce, y do chao sobe e encolhe por SIN)."""
        return math.atan2(-ty / SIN, tx)

    # ---- pecas miudas (num Lote so por material)
    def pebble(self, x, y, r=None):
        rr = self.rr
        w = to_world(x, y)
        r = r or rr.uniform(0.016, 0.034)
        self.lote.pebble(rr.choice(self.D['pedrisco']), (w.x, w.y, self.gz(w.x, w.y) + r * 0.25), r, squash=0.55, rot=rr.uniform(0, TAU), rr=rr, sub=1)
        self.count('pedrisco')

    def tuft(self, x, y, size=None):
        rr = self.rr
        w = to_world(x, y)
        verde = self.cp.lawn_at(x, y) > 0.5
        size = size or (rr.uniform(0.1, 0.17) if verde else rr.uniform(0.12, 0.22))
        capim(self.lote, self.M, (w.x, w.y, self.gz(w.x, w.y)), size, rr, verde=verde)
        self.count('capim')

    def petal(self, x, y):
        rr = self.rr
        w = to_world(x, y)
        m = rr.choice((self.M['ipe'], self.M['ipe'], self.M['ipe_d'], self.M['ipe_l']))
        self.lote.disc(m, (w.x, w.y, self.gz(w.x, w.y) + 0.003), rr.uniform(0.018, 0.03), sy=rr.uniform(0.55, 1.0), h=0.006, rot=rr.uniform(0, TAU), n=7)
        self.count('petala')

    def leaf(self, x, y):
        rr = self.rr
        w = to_world(x, y)
        self.lote.disc(rr.choice(self.D['folha']), (w.x, w.y, self.gz(w.x, w.y) + 0.003), rr.uniform(0.025, 0.04), sy=rr.uniform(0.35, 0.5), h=0.005, rot=rr.uniform(0, TAU), n=8)
        self.count('folha')

    def confetti(self, wx, wy, n, spread):
        rr = self.rr
        for k in range(n):
            px, py = wx + rr.gauss(0, spread), wy + rr.gauss(0, spread * 0.8)
            gx, gy = to_game((px, py, 0))
            if self.road(gx, gy) < 26 or self.spot_gap(px, py) < 0.04:
                continue
            self.lote.disc(rr.choice(self.D['confete']), (px, py, self.gz(px, py) + 0.003), rr.uniform(0.011, 0.017), sy=rr.uniform(0.55, 1.0),
                           h=0.004, rot=rr.uniform(0, TAU), n=rr.choice((4, 4, 5, 6)))
            self.count('confete')

    def flag(self, wx, wy, a):
        """Bandeirinha lisa caida no chao: varinha e pano (sem desenho), em cor neutra."""
        rr = self.rr
        z = self.gz(wx, wy)
        ca, sa = math.cos(a), math.sin(a)
        Ls = rr.uniform(0.24, 0.32)
        p0 = (wx - ca * Ls / 2, wy - sa * Ls / 2, z + 0.008)
        p1 = (wx + ca * Ls / 2, wy + sa * Ls / 2, z + 0.008)
        self.lote.tube(self.D['vareta'], [p0, p1], 0.008, segs=5)
        fw, fh = rr.uniform(0.12, 0.16), rr.uniform(0.08, 0.1)
        cx, cy = p1[0] - ca * fw * 0.55 - sa * fh * 0.5, p1[1] - sa * fw * 0.55 + ca * fh * 0.5
        self.lote.box(rr.choice(self.D['panos']), (fw, fh, 0.005), (cx, cy, z + 0.007), rot=(rr.uniform(-0.12, 0.12), rr.uniform(-0.12, 0.12), a))
        self.count('bandeirinha')

    def sign_board(self, wx, wy, a):
        """Cartaz de papelao em branco caido (com o cabo)."""
        rr = self.rr
        z = self.gz(wx, wy)
        ca, sa = math.cos(a), math.sin(a)
        self.lote.tube(self.D['vareta'], [(wx - ca * 0.28, wy - sa * 0.28, z + 0.01), (wx + ca * 0.06, wy + sa * 0.06, z + 0.01)], 0.009, segs=5)
        self.lote.box(self.D['papelao'], (0.24, 0.17, 0.008), (wx + ca * 0.12, wy + sa * 0.12, z + 0.012), rot=(rr.uniform(-0.06, 0.06), rr.uniform(-0.06, 0.06), a + rr.uniform(-0.2, 0.2)))
        self.count('cartaz')

    def cup(self, wx, wy, a):
        z = self.gz(wx, wy)
        ca, sa = math.cos(a), math.sin(a)
        self.lote.tube(self.D['papel'], [(wx, wy, z + 0.017), (wx + ca * 0.045, wy + sa * 0.045, z + 0.017)], 0.017, segs=8,
                       rfun=lambda t: 0.014 + 0.005 * t)
        self.count('copinho')

    def bin_(self, wx, wy):
        """Lixeira redonda de metal (corpo, aro e tampa escura)."""
        z = self.gz(wx, wy)
        self.lote.tube(self.D['lixeira'], [(wx, wy, z - 0.01), (wx, wy, z + 0.15)], 0.055, segs=14)
        self.lote.tube(self.M['metal'], [(wx, wy, z + 0.14), (wx, wy, z + 0.165)], 0.06, segs=14)
        self.lote.disc(self.M['pneu'], (wx, wy, z + 0.163), 0.05, h=0.006, n=14)
        self.count('lixeira')

    def puddle(self, wx, wy, R):
        """Poca d'agua: mancha molhada em volta e a lamina brilhante, de contorno irregular, colada no chao."""
        rr = self.rr
        ph = [rr.uniform(0, TAU) for _ in range(3)]
        sy = rr.uniform(0.55, 0.85)
        rot = rr.uniform(0, TAU)
        # mancha molhada, lamina d'agua e um reflexo claro do ceu, deslocado para o fundo da poca
        for (m, k, dz, off) in ((self.D['molhado'], 1.35, 0.003, 0.0), (self.D['poca'], 1.0, 0.006, 0.0), (self.D['poca_brilho'], 0.38, 0.008, 0.45)):
            bm = self.lote._bm(m)
            vs = []
            n = 28
            cx, cy = wx - 0.1 * R * off, wy + 0.45 * R * off * sy
            ro = 0.0 if off else rot   # o reflexo fica deitado na horizontal da tela
            for i in range(n):
                t = TAU * i / n
                r = R * k * (1 + 0.22 * math.sin(2 * t + ph[0]) + 0.12 * math.sin(3 * t + ph[1]) + 0.06 * math.sin(5 * t + ph[2]))
                lx, ly = r * math.cos(t) * (1.3 if off else 1.0), r * math.sin(t) * sy * (0.32 if off else 1.0)
                px = cx + lx * math.cos(ro) - ly * math.sin(ro)
                py = cy + lx * math.sin(ro) + ly * math.cos(ro)
                vs.append(bm.verts.new((px, py, self.gz(px, py) + dz)))
            c = bm.verts.new((cx, cy, self.gz(cx, cy) + dz))
            for i in range(n):
                bm.faces.new((c, vs[i], vs[(i + 1) % n]))
        self.count('poca')

    # ---- pecas maiores (objeto proprio), sempre com folga da estrada, dos lotes e do que ja foi posto
    def bench(self, wx, wy, ang, name):
        banco(self.root, name, (wx, wy, self.gz(wx, wy)), self.M, ang=ang)
        self.count('banco')

    def placa(self, wx, wy, yaw, name):
        """Placa de transito sem texto: poste fino e placa verde lisa de borda branca, virada para a camera."""
        z = self.gz(wx, wy)
        sub = empty(self.root, name, (wx, wy, z), rot=(0, 0, yaw))
        tube(sub, name + '_haste', [(0, 0, -0.02), (0, 0, 0.98)], 0.02, self.M['metal_d'], segs=8)
        box(sub, name + '_borda', (0.4, 0.016, 0.26), (0, -0.024, 0.84), m=self.D['placa_borda'], bev=0.016)
        box(sub, name + '_placa', (0.36, 0.02, 0.22), (0, -0.03, 0.84), m=self.D['placa'], bev=0.012)
        cyl(sub, name + '_pe', 0.05, 0.04, (0, 0, 0.0), m=self.M['conc_d'], v=12, bev=0.01)
        self.count('placa')

    def gradil(self, wx, wy, ang, name):
        """Gradil de contencao (cerca baixa de metal com pes), alinhado com a estrada."""
        z = self.gz(wx, wy)
        sub = empty(self.root, name, (wx, wy, z), rot=(0, 0, ang))
        bm = bmesh.new()
        hw, H = 0.36, 0.3
        tube_into(bm, [(-hw, 0, 0.05), (-hw, 0, H), (hw, 0, H), (hw, 0, 0.05)], 0.012, segs=6)
        tube_into(bm, [(-hw, 0, 0.07), (hw, 0, 0.07)], 0.009, segs=6)
        nb = 9
        for i in range(1, nb):
            x = -hw + 2 * hw * i / nb
            tube_into(bm, [(x, 0, 0.07), (x, 0, H)], 0.0055, segs=5)
        bm_to_obj(bm, name + '_grade', sub, [self.M['metal']], angle=60)
        for sx in (-1, 1):
            box(sub, f'{name}_pe{sx}', (0.035, 0.2, 0.014), (sx * (hw - 0.04), 0, 0.007), m=self.M['metal_d'], bev=0.004)
            box(sub, f'{name}_suporte{sx}', (0.02, 0.012, 0.06), (sx * (hw - 0.04), 0, 0.04), m=self.M['metal_d'], bev=0.003)
        self.count('gradil')

    # ---- passadas
    def roadside(self):
        rr = self.rr

        def fn(x, y, tx, ty):
            for s in (-1, 1):
                if rr.random() < 0.55:
                    px, py = self.side(x, y, tx, ty, s, rr.uniform(27, 39))
                    if self.ok(px, py, road=26.5, gap=0.06, plaza=False):
                        self.pebble(px, py)
                        if rr.random() < 0.3:
                            self.pebble(px + rr.uniform(-3, 3), py + rr.uniform(-2, 2), rr.uniform(0.012, 0.022))
        self.along(5.0, fn)

        def fn2(x, y, tx, ty):
            for s in (-1, 1):
                if rr.random() < 0.42:
                    px, py = self.side(x, y, tx, ty, s, rr.uniform(34, 47))
                    if self.ok(px, py, road=33.5, gap=0.12, plaza=False):
                        self.tuft(px, py)
        self.along(10.0, fn2)

    def petals(self, base=0.04, near=0.55):
        if not self.ipes:
            return
        rr = self.rr

        def fn(x, y, tx, ty):
            for s in (-1, 1):
                px, py = self.side(x, y, tx, ty, s, rr.uniform(20, 72))
                w = to_world(px, py)
                dmin = min(math.hypot(w.x - a, w.y - b) for (a, b) in self.ipes)
                if rr.random() < base + near * math.exp(-dmin / 2.0) and self.ok(px, py, road=20, gap=0.04, water=1.1, block=False):
                    self.petal(px, py)
        self.along(6.0, fn)

    def spot_rings(self, protest=0.0):
        rr = self.rr
        for (sx, sy, R0, s) in self.SC:
            for j in range(rr.randrange(9, 15)):
                a = rr.uniform(0, TAU)
                rad = R0 + rr.uniform(0.06, 0.45)
                wx, wy = sx + rad * math.cos(a), sy + rad * math.sin(a)
                gx, gy = to_game((wx, wy, 0))
                if not self.ok(gx, gy, road=31, gap=0.04, water=1.15):
                    continue
                pz = self.cp.plaza_at(gx, gy) > 0.3
                u = rr.random()
                if u < 0.42:
                    for _ in range(rr.randrange(1, 4)):
                        self.pebble(gx + rr.uniform(-4, 4), gy + rr.uniform(-3, 3), rr.uniform(0.016, 0.04))
                elif u < 0.78 and not pz:
                    self.tuft(gx, gy, rr.uniform(0.11, 0.2))
                elif u < 0.9 and self.ipes:
                    for _ in range(rr.randrange(2, 5)):
                        self.petal(gx + rr.uniform(-6, 6), gy + rr.uniform(-4, 4))
                elif protest and rr.random() < protest:
                    self.confetti(wx, wy, rr.randrange(4, 10), 0.08)

    def lamp_bases(self):
        rr = self.rr
        bpy.context.view_layer.update()
        for o in list(self.root.children_recursive):
            if not (o.name.startswith('poste') and o.name.endswith('_pe')):
                continue
            p = o.matrix_world.translation
            wx, wy = p.x, p.y
            z = self.gz(wx, wy)
            self.lote.box(self.M['conc_d'], (0.21, 0.21, 0.045), (wx, wy, z + 0.008), rot=(0, 0, rr.uniform(-0.25, 0.25)))
            gx, gy = to_game((wx, wy, 0))
            lx, ly = wx + rr.choice((-1, 1)) * 0.2, wy - 0.07
            if self.ok(*to_game((lx, ly, 0)), road=30, gap=0.06, block=False):
                self.lote.box(self.M['metal_d'], (0.1, 0.1, 0.012), (lx, ly, self.gz(lx, ly) + 0.004), rot=(0, 0, rr.uniform(-0.2, 0.2)))
            for k in range(rr.randrange(2, 4)):
                a = rr.uniform(0, TAU)
                tx, ty = to_game((wx + 0.16 * math.cos(a), wy + 0.16 * math.sin(a), 0))
                if self.ok(tx, ty, road=31, gap=0.05, block=False):
                    if self.cp.plaza_at(tx, ty) < 0.3 and rr.random() < 0.6:
                        self.tuft(tx, ty, rr.uniform(0.09, 0.15))
                    else:
                        self.pebble(tx, ty)
            self.count('base_poste')

    def bins_by_benches(self):
        rr = self.rr
        bpy.context.view_layer.update()
        for o in list(self.root.children_recursive):
            if not (o.name.startswith('banco') and '_' not in o.name):
                continue
            if rr.random() < 0.3:
                continue
            p = o.matrix_world.translation
            ang = o.matrix_world.to_euler().z
            sgn = rr.choice((-1, 1))
            wx, wy = p.x + math.cos(ang) * 0.48 * sgn, p.y + math.sin(ang) * 0.48 * sgn
            if self.ok(*to_game((wx, wy, 0)), road=34, gap=0.12, block=False):
                self.bin_(wx, wy)

    def candidates(self, o0, o1, step, test):
        out = []
        rr = self.rr

        def fn(x, y, tx, ty):
            for s in (-1, 1):
                px, py = self.side(x, y, tx, ty, s, rr.uniform(o0, o1))
                if test(px, py):
                    out.append((px, py, tx, ty))
        self.along(step, fn)
        rr.shuffle(out)
        return out

    def street_furniture(self, benches=0, signs=0, gradis=0):
        rr = self.rr
        P = self.place
        for k, (x, y, tx, ty) in enumerate(self.candidates(46, 58, 23, lambda x, y: (self.cp.lawn_at(x, y) > 0.5 or self.cp.plaza_at(x, y) > 0.8)
                                                       and self.ok(x, y, road=44, gap=0.35) and P.free(x, y, 30) and P.far_spot(x, y, 54)
                                                       and P.hud_free(x, y) and P.clear_above(x, y, 12, 22))):
            if self.n.get('banco', 0) >= benches:
                break
            if not P.free(x, y, 30):
                continue
            w = to_world(x, y)
            ang = self.world_ang(tx, ty)
            self.bench(w.x, w.y, ang, f'bancoDet{k}')
            P.placed.append((x, y))
            if rr.random() < 0.75:
                sg = rr.choice((-1, 1))
                bx, by = w.x + math.cos(ang) * 0.5 * sg, w.y + math.sin(ang) * 0.5 * sg
                if self.ok(*to_game((bx, by, 0)), road=36, gap=0.15):
                    self.bin_(bx, by)
        got = 0
        for k, (x, y, tx, ty) in enumerate(self.candidates(40, 50, 31, lambda x, y: self.ok(x, y, road=38, gap=0.4) and P.free(x, y, 30)
                                                       and P.far_spot(x, y, 58) and P.hud_free(x, y) and P.clear_above(x, y, 46, 18))):
            if got >= signs:
                break
            # placas espalhadas pela fase
            if any(math.hypot(px - x, py - y) < 160 for (px, py) in self.signs_at) or not P.free(x, y, 30):
                continue
            w = to_world(x, y)
            self.placa(w.x, w.y, rr.uniform(-0.35, 0.35), f'placa{k}')
            self.signs_at.append((x, y))
            P.placed.append((x, y))
            got += 1
        got = 0
        for k, (x, y, tx, ty) in enumerate(self.candidates(42, 50, 19, lambda x, y: self.ok(x, y, road=40, gap=0.35) and P.free(x, y, 26)
                                                       and P.far_spot(x, y, 52) and P.hud_free(x, y) and P.clear_above(x, y, 16, 26))):
            if got >= gradis:
                break
            if not P.free(x, y, 26):
                continue
            w = to_world(x, y)
            ang = self.world_ang(tx, ty)
            self.gradil(w.x, w.y, ang, f'gradil{k}')
            P.placed.append((x, y))
            got += 1
            # as vezes um segundo gradil emendado
            if rr.random() < 0.5:
                x2, y2 = x + tx * 31, y + ty * 31
                if self.ok(x2, y2, road=40, gap=0.35) and P.free(x2, y2, 22) and P.clear_above(x2, y2, 16, 26):
                    w2 = to_world(x2, y2)
                    self.gradil(w2.x, w2.y, ang + rr.uniform(-0.15, 0.15), f'gradil{k}b')
                    P.placed.append((x2, y2))

    def protest(self, n):
        """Sobras de manifestacao: confete, bandeirinhas lisas, cartaz em branco e copinho, em montinhos."""
        rr = self.rr
        got = 0
        for (x, y, tx, ty) in self.candidates(36, 95, 17, lambda x, y: self.ok(x, y, road=34, gap=0.14)):
            if got >= n:
                break
            if any(math.hypot(px - x, py - y) < 90 for (px, py) in self.piles):
                continue
            self.piles.append((x, y))
            got += 1
            w = to_world(x, y)
            self.confetti(w.x, w.y, rr.randrange(14, 34), rr.uniform(0.18, 0.32))
            for j in range(rr.choice((0, 1, 1, 2))):
                fx, fy = w.x + rr.uniform(-0.3, 0.3), w.y + rr.uniform(-0.2, 0.2)
                if self.ok(*to_game((fx, fy, 0)), road=33, gap=0.14):
                    self.flag(fx, fy, rr.uniform(0, TAU))
            if rr.random() < 0.35:
                fx, fy = w.x + rr.uniform(-0.25, 0.25), w.y + rr.uniform(-0.2, 0.2)
                if self.ok(*to_game((fx, fy, 0)), road=36, gap=0.2):
                    self.sign_board(fx, fy, rr.uniform(0, TAU))
            if rr.random() < 0.45:
                fx, fy = w.x + rr.uniform(-0.3, 0.3), w.y + rr.uniform(-0.2, 0.2)
                if self.ok(*to_game((fx, fy, 0)), road=32, gap=0.1):
                    self.cup(fx, fy, rr.uniform(0, TAU))

    def puddles(self, n):
        rr = self.rr
        got = 0
        for (x, y, tx, ty) in self.candidates(28, 110, 13, lambda x, y: self.ok(x, y, road=28, gap=0.18, water=1.3)):
            if got >= n:
                break
            if any(math.hypot(px - x, py - y) < 55 for (px, py) in self.pocas):
                continue
            w = to_world(x, y)
            R = rr.uniform(0.12, 0.3)
            # a poca nao pode invadir a estrada nem os lotes
            if self.road(x, y) - R * GB * 1.6 < 26 or self.spot_gap(w.x, w.y) < R * 1.5:
                continue
            self.pocas.append((x, y))
            self.puddle(w.x, w.y, R)
            got += 1

    def leaves(self, n):
        rr = self.rr
        for k in range(n * 4):
            if self.n.get('folha', 0) >= n:
                break
            x, y = rr.uniform(0, GW), rr.uniform(0, GH)
            if self.ok(x, y, road=24, gap=0.05, block=False):
                for _ in range(rr.randrange(1, 4)):
                    self.leaf(x + rr.uniform(-5, 5), y + rr.uniform(-4, 4))


def detalhes(L, F, root, cp, place, M, out):
    """Detalhe de perto de cada fase (F['det']): ver o comentario acima de det_mats."""
    cfg = F.get('det', {})
    rr = random.Random(L['seed'] * 313 + 17)
    d = Det(L, F, root, cp, place, M, rr)
    d.signs_at, d.piles, d.pocas = [], [], []
    d.lamp_bases()
    d.bins_by_benches()
    d.street_furniture(benches=cfg.get('bancos', 0), signs=cfg.get('placas', 2), gradis=cfg.get('gradis', 0))
    d.roadside()
    d.petals(base=cfg.get('petalas', 0.04))
    d.spot_rings(protest=cfg.get('confete_lotes', 0.0))
    d.protest(cfg.get('protesto', 0))
    if cfg.get('pocas'):
        d.puddles(cfg['pocas'])
    if cfg.get('folhas'):
        d.leaves(cfg['folhas'])
    d.lote.done(root)
    out['detalhes'] = d.n
    return d.n


FASES = {
    1: dict(build=fase1,
            lawns=[(700, 330, 560, 200, 4), (690, 118, 200, 70, 3), (790, 600, 200, 90, 3)],
            plazas=[('laje', 1140, 556, 170, 46, 5), ('asfalto', 1118, 656, 190, 52, 4)],
            det=dict(placas=3, protesto=6, confete_lotes=0.25)),
    2: dict(build=fase2,
            lawns=[(690, 360, 640, 150, 4)],
            plazas=[('laje', 1020, 150, 290, 42, 6), ('laje', 830, 742, 520, 40, 6), ('pedra', 112, 520, 80, 42, 2.4)],
            det=dict(bancos=4, placas=2, gradis=5, protesto=11, confete_lotes=0.5)),
    3: dict(build=fase3, lamps_glow=True, janela=0.45,
            lawns=[(566, 250, 260, 70, 3), (700, 470, 520, 160, 3)],
            plazas=[('laje', 566, 182, 186, 44, 5), ('laje', 1226, 340, 64, 30, 4)],
            pools=[(472, 218, 48, 11, 5), (660, 218, 48, 11, 5)],
            det=dict(bancos=4, placas=2, gradis=2, protesto=4, confete_lotes=0.15)),
    4: dict(build=fase4, th=dict(road_paved=True, waves=1.0, road='#b4573a', road_d='#8f4630', exposure=-0.6, wet_road=0.3),
            road_stones=0.0,
            lawns=[],
            plazas=[('pedra', 690, 380, 470, 250, 3.5), ('pedra', 1188, 326, 112, 66, 4), ('pedra', 470, 150, 90, 50, 3)],
            det=dict(placas=2, protesto=7, pocas=16, folhas=70, confete_lotes=0.3)),
    5: dict(build=fase5, lamps_glow=True, exit_pylons=False, janela=0.8,
            lawns=[(950, 220, 330, 150, 3), (300, 380, 220, 120, 3)],
            plazas=[('laje', 1128, 522, 168, 36, 6)],
            det=dict(bancos=3, placas=2, gradis=6, protesto=8, confete_lotes=0.3)),
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
    detalhes(L, F, root, cp, place, M, out)
    out['_cp'] = cp
    return out


def render_level_br(idx, out_dir, samples=96, k=6.0):
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
        k = float(args[4]) if len(args) > 4 else 6.0
        for i in idxs:
            render_level_br(i, out, samples, k)
