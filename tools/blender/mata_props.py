"""Enfeites da floresta amazonica (Guardioes da Mata), no estilo de massinha macia dos conceitos
(arte/conceitos/amazonia/fase.png): arvores com sapopemas, samaumas, samambaias, bromelias, heliconias,
folhas grandes, troncos caidos com musgo, pedras de rio, palafitas, canoas, vitorias-regias, cogumelos
que brilham, troncos queimados e o deck de madeira dos lotes.

Mesmas convencoes do cenario_props.py: tudo nasce no chao (z do ponto passado) e pecas numerosas vao num Lote.
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise
from lib import (TAU, mat, glow_mat, box, cyl, sphere, tube, tube_into, torus, lathe, bm_to_obj, mtx)
from cenario_props import Lote, rock, frond


def M(key, hexcol, **kw):
    kw.setdefault('var', 0.1)
    kw.setdefault('bump', 0.15)
    return mat('mt_' + key, hexcol, **kw)


def mats():
    return {
        'leaf': M('folha', '#5e9e3e', rough=0.7, var=0.14, sheen=0.3), 'leaf_d': M('folha_esc', '#3f7a34', rough=0.7, var=0.14, sheen=0.3),
        'leaf_l': M('folha_cl', '#8cc152', rough=0.7, var=0.12, sheen=0.3), 'fern': M('samambaia', '#4f9a44', rough=0.75, var=0.15, sheen=0.3),
        'moss': M('musgo', '#7fae46', rough=0.9, var=0.15, bump=0.4), 'bark': M('casca', '#8a5a36', rough=0.85, var=0.1, bump=0.45),
        'bark_l': M('casca_cl', '#a87850', rough=0.85, var=0.1, bump=0.45), 'bark_d': M('casca_esc', '#5e3c26', rough=0.9, var=0.08, bump=0.4),
        'wood': M('madeira', '#9a6236', rough=0.75, var=0.12, bump=0.3), 'wood_l': M('madeira_cl', '#c08a54', rough=0.75, var=0.12, bump=0.3),
        'plank': M('tabua', '#b27a48', rough=0.78, var=0.16, bump=0.3), 'straw': M('palha', '#d9b26a', rough=0.95, var=0.08, bump=0.5),
        'stone': M('pedra_rio', '#a7a397', rough=0.8, var=0.16, bump=0.25), 'stone_d': M('pedra_rio_esc', '#7f7c72', rough=0.8, var=0.14, bump=0.25),
        'red': M('heliconia', '#e2552e', rough=0.55, var=0.06, bump=0.05), 'orange': M('heliconia_ponta', '#f49a2c', rough=0.55, var=0.06, bump=0.05),
        'pink': M('bromelia', '#d9446a', rough=0.55, var=0.08, bump=0.05), 'yellow': M('flor_amarela', '#f2c84a', rough=0.55, var=0.06, bump=0.05),
        'white': M('flor_branca', '#f6eee0', rough=0.6, var=0.04, bump=0.05), 'lily': M('vitoria_regia', '#6aa84a', rough=0.55, var=0.1, bump=0.1),
        'lily_rim': M('vitoria_borda', '#b0503a', rough=0.6, var=0.08, bump=0.1), 'mush': glow_mat('mt_cogumelo', '#7ff0d0', 1.2, 8.0, rough=0.4, var=0.05, bump=0.0),
        'mush_cap': M('chapeu', '#e8e0c8', rough=0.5, var=0.06, bump=0.05), 'char': M('carvao', '#2e2622', rough=0.9, var=0.1, bump=0.5),
        'ember': glow_mat('mt_brasa', '#ff7a2a', 3.0, 12.0, rough=0.6, var=0.1, bump=0.1),
    }


# ---------------------------------------------------------------- vegetacao baixa
def fern(root, name, Mt, loc, s, rr):
    """Samambaia: folhas longas que sobem e caem em leque."""
    out = []
    n = 8 + rr.randrange(3)
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.2, 0.2)
        piv = bpy.data.objects.new(f'{name}_p{k}', None)
        root.users_collection[0].objects.link(piv)
        piv.parent = root
        piv['set'] = root['set']
        piv.location = loc
        piv.rotation_euler = (0, 0, a)
        f = frond(root, f'{name}_{k}', s * rr.uniform(0.75, 1.0), s * 0.55, rr.uniform(0.7, 1.1), Mt['fern'] if k % 2 else Mt['leaf'], rr)
        f.parent = piv
        out.append(f)
    return out


def bromeliad(root, name, Mt, loc, s, rr, center=None):
    """Bromelia: roseta de folhas grossas abertas com o miolo colorido."""
    bm = bmesh.new()
    n = 11
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.1, 0.1)
        L = s * rr.uniform(0.32, 0.42)
        up = rr.uniform(0.5, 0.9)
        pts = [(0, 0, 0.02), (math.cos(a) * L * 0.45, math.sin(a) * L * 0.45, L * up * 0.6), (math.cos(a) * L, math.sin(a) * L, L * up * 0.75)]
        tube_into(bm, [Vector((loc[0] + p[0], loc[1] + p[1], loc[2] + p[2])) for p in pts], s * 0.05, segs=6, rfun=lambda t: s * (0.055 - 0.045 * t))
    o = bm_to_obj(bm, name, root, [Mt['leaf_d'] if rr.random() < 0.5 else Mt['leaf']], angle=89)
    o.scale = (1, 1, 1)
    c = sphere(root, name + '_miolo', s * 0.09, (loc[0], loc[1], loc[2] + s * 0.1), scale=(1, 1, 1.3), m=center or Mt['pink'], seg=12)
    for k in range(5):
        a = TAU * k / 5
        sphere(root, f'{name}_bractea{k}', s * 0.05, (loc[0] + s * 0.07 * math.cos(a), loc[1] + s * 0.07 * math.sin(a), loc[2] + s * 0.14),
               scale=(0.6, 0.6, 1.6), m=center or Mt['pink'], seg=10)
    return [o, c]


def heliconia(root, name, Mt, loc, s, rr):
    """Heliconia: haste com bracteas em zigue-zague (vermelho com ponta amarela) e duas folhas largas."""
    out = [tube(root, name + '_haste', [loc, (loc[0], loc[1], loc[2] + s * 0.9)], s * 0.03, Mt['leaf_d'], segs=6)]
    for k in range(5):
        z = loc[2] + s * (0.35 + 0.11 * k)
        side = 1 if k % 2 else -1
        b = cyl(root, f'{name}_bract{k}', s * 0.06, s * 0.22, (loc[0] + side * s * 0.09, loc[1], z), r2=0.0, m=Mt['red'], v=8, bev=0.0,
                rot=(0, side * math.radians(60), 0))
        b.scale = (1, 0.55, 1)
        sphere(root, f'{name}_ponta{k}', s * 0.03, (loc[0] + side * s * 0.19, loc[1], z + s * 0.06), m=Mt['yellow'], seg=8)
        out.append(b)
    for k, a in enumerate((rr.uniform(0, TAU), rr.uniform(0, TAU))):
        leaf = sphere(root, f'{name}_folha{k}', s * 0.3, (loc[0] + math.cos(a) * s * 0.22, loc[1] + math.sin(a) * s * 0.22, loc[2] + s * 0.45),
                      scale=(1.0, 0.3, 0.08), m=Mt['leaf'], seg=14, rot=(0.6, 0, a))
        out.append(leaf)
    return out


def big_leaves(root, name, Mt, loc, s, rr, n=5):
    """Touceira de folhas largas (taioba/costela-de-adao): folhas em gota sobre talos curvos."""
    out = []
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.3, 0.3)
        L = s * rr.uniform(0.35, 0.5)
        tip = (loc[0] + math.cos(a) * L, loc[1] + math.sin(a) * L, loc[2] + s * rr.uniform(0.25, 0.45))
        out.append(tube(root, f'{name}_talo{k}', [loc, (loc[0] + math.cos(a) * L * 0.4, loc[1] + math.sin(a) * L * 0.4, tip[2] + s * 0.1), tip], s * 0.02, Mt['leaf_d'], segs=5))
        lf = sphere(root, f'{name}_f{k}', s * 0.2, tip, scale=(1.4, 0.95, 0.07), m=Mt['leaf'] if k % 2 else Mt['leaf_l'], seg=16, rot=(0.35, 0, a))
        out.append(lf)
    return out


def grass_tuft(lote, Mt, loc, s, rr, n=8):
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.4, 0.4)
        lean = rr.uniform(0.2, 0.5)
        h = s * rr.uniform(0.7, 1.1)
        lote.blade(Mt['leaf_l'] if k % 3 else Mt['leaf'], (loc[0], loc[1], loc[2]), (loc[0] + math.cos(a) * h * lean, loc[1] + math.sin(a) * h * lean, loc[2] + h), s * 0.06)


def flowers(lote, Mt, loc, s, rr, n=5, col=None):
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0, s * 0.25)
        lote.pebble(col or rr.choice((Mt['pink'], Mt['yellow'], Mt['white'])), (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a), loc[2] + s * 0.06),
                    s * 0.035, squash=0.7, rr=rr, sub=1, rough=0.1)


# ---------------------------------------------------------------- arvores e troncos
def jungle_tree(root, name, Mt, loc, s, rr, canopy=True, crown_m=None):
    """Arvore da mata: tronco grosso com sapopemas (raizes em aleta) e copa de nuvens de folhas."""
    out = []
    H = s * rr.uniform(2.0, 2.6)
    out.append(tube(root, name + '_tronco', [(loc[0], loc[1], loc[2] - 0.05), (loc[0] + 0.05 * s, loc[1], loc[2] + H * 0.6), (loc[0] + 0.02 * s, loc[1], loc[2] + H)],
                    0.3 * s, Mt['bark'], segs=14, rfun=lambda t: s * (0.32 - 0.12 * t)))
    for k in range(5):
        a = TAU * k / 5 + rr.uniform(-0.2, 0.2)
        L = s * rr.uniform(0.55, 0.8)
        bm = bmesh.new()
        prof = [(0, 0.0), (0.25, 0.32), (0.6, 0.18), (1.0, 0.02)]
        vs = []
        for (t, hz) in prof:
            vs.append((bm.verts.new((t * L, -0.05 * s, hz * H * 0.55)), bm.verts.new((t * L, 0.05 * s, hz * H * 0.55)),
                       bm.verts.new((t * L, 0.05 * s, 0)), bm.verts.new((t * L, -0.05 * s, 0))))
        for i in range(len(vs) - 1):
            A_, B_ = vs[i], vs[i + 1]
            for j in range(4):
                bm.faces.new((A_[j], A_[(j + 1) % 4], B_[(j + 1) % 4], B_[j]))
        fin = bm_to_obj(bm, f'{name}_sapopema{k}', root, [Mt['bark_l']], angle=60)
        sub = fin.modifiers.new('Suave', 'SUBSURF')
        sub.levels = sub.render_levels = 2
        fin.location = (loc[0] + math.cos(a) * 0.12 * s, loc[1] + math.sin(a) * 0.12 * s, loc[2] - 0.02)
        fin.rotation_euler = (0, 0, a)
        out.append(fin)
    sphere(root, name + '_musgo', 0.33 * s, (loc[0], loc[1], loc[2] + 0.05), scale=(1.2, 1.2, 0.4), m=Mt['moss'], seg=16)
    if canopy:
        cm = crown_m or Mt['leaf']
        top = Vector((loc[0] + 0.02 * s, loc[1], loc[2] + H))
        for k in range(9):
            a = TAU * k / 9 + rr.uniform(-0.3, 0.3)
            d = s * rr.uniform(0.35, 0.9) if k else 0
            r = s * rr.uniform(0.45, 0.7)
            out.append(sphere(root, f'{name}_copa{k}', r, (top.x + d * math.cos(a), top.y + d * math.sin(a) * 0.8, top.z + rr.uniform(-0.15, 0.35) * s),
                              scale=(1, 1, 0.78), m=cm if k % 3 else Mt['leaf_d'], seg=18))
    return out


def log(root, name, Mt, loc, s, rr, ang=None):
    """Tronco caido com musgo e cogumelinhos."""
    a = rr.uniform(0, TAU) if ang is None else ang
    L = s * rr.uniform(0.9, 1.3)
    o = cyl(root, name, 0.16 * s, L, (loc[0], loc[1], loc[2] + 0.12 * s), m=Mt['bark'], v=18, bev=0.03, rot=(math.pi / 2, 0, a + math.pi / 2))
    for k, sgn in enumerate((-1, 1)):
        cyl(root, f'{name}_anel{k}', 0.15 * s, 0.01, (loc[0] + math.cos(a) * L / 2 * sgn, loc[1] + math.sin(a) * L / 2 * sgn, loc[2] + 0.12 * s),
            m=Mt['bark_l'], v=18, bev=0.0, rot=(math.pi / 2, 0, a + math.pi / 2))
    sphere(root, name + '_musgo', 0.17 * s, (loc[0], loc[1], loc[2] + 0.2 * s), scale=(L / (0.34 * s) * 0.45, 0.9, 0.35), m=Mt['moss'], seg=16, rot=(0, 0, a))
    for k in range(3):
        t = rr.uniform(-0.35, 0.35) * L
        sphere(root, f'{name}_cog{k}', 0.045 * s, (loc[0] + math.cos(a) * t, loc[1] + math.sin(a) * t - 0.12 * s, loc[2] + 0.12 * s), scale=(1.3, 1.3, 0.6), m=Mt['white'], seg=10)
    return o


def mossy_rock(root, name, Mt, loc, s, rr):
    out = [rock(root, name, Mt['stone'], loc, s, rr, squash=0.55)]
    out.append(sphere(root, name + '_musgo', s * 0.85, (loc[0], loc[1], loc[2] + s * 0.3), scale=(1.1, 1.0, 0.32), m=Mt['moss'], seg=16))
    return out


def charred_trunk(root, name, Mt, loc, s, rr):
    """Toco queimado (Coracao em Chamas): tronco preto partido, brasas nas rachaduras."""
    H = s * rr.uniform(0.6, 1.4)
    out = [tube(root, name, [(loc[0], loc[1], loc[2] - 0.03), (loc[0] + rr.uniform(-0.1, 0.1), loc[1], loc[2] + H)], 0.2 * s, Mt['char'], segs=10,
                rfun=lambda t: s * (0.22 - 0.08 * t))]
    for k in range(3):
        z = loc[2] + H * rr.uniform(0.2, 0.8)
        a = rr.uniform(0, TAU)
        box(root, f'{name}_brasa{k}', (0.05 * s, 0.03 * s, 0.14 * s), (loc[0] + math.cos(a) * 0.18 * s, loc[1] + math.sin(a) * 0.18 * s, z), rot=(0, 0, a), m=Mt['ember'], bev=0.01)
    return out


def glow_mushrooms(root, name, Mt, loc, s, rr, lights=None):
    """Cogumelos que brilham (Gruta dos Vaga-lumes): luz do cenario a noite."""
    out = []
    for k in range(rr.randrange(3, 6)):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0, 0.18) * s
        h = rr.uniform(0.12, 0.3) * s
        x, y = loc[0] + d * math.cos(a), loc[1] + d * math.sin(a)
        out.append(tube(root, f'{name}_pe{k}', [(x, y, loc[2]), (x, y, loc[2] + h)], 0.025 * s, Mt['mush_cap'], segs=6))
        out.append(sphere(root, f'{name}_chapeu{k}', rr.uniform(0.06, 0.1) * s, (x, y, loc[2] + h), scale=(1, 1, 0.55), m=Mt['mush'], seg=14))
    if lights is not None:
        lights.append(((loc[0], loc[1], loc[2] + 0.3 * s), '#7ff0d0', 10.0 * s, 1))
    return out


# ---------------------------------------------------------------- agua
def vitoria_regia(lote, Mt, loc, r, rr):
    """Vitoria-regia: disco grande com a borda virada para cima (avermelhada por fora)."""
    bm = lote._bm(Mt['lily'])
    n = 28
    rim = []
    base = []
    for k in range(n):
        a = TAU * k / n
        base.append(bm.verts.new((loc[0] + r * 0.96 * math.cos(a), loc[1] + r * 0.96 * math.sin(a), loc[2])))
    c0 = bm.verts.new(loc)
    for k in range(n):
        bm.faces.new((c0, base[k], base[(k + 1) % n]))
    bmr = lote._bm(Mt['lily_rim'])
    lo = [bmr.verts.new((loc[0] + r * math.cos(TAU * k / n), loc[1] + r * math.sin(TAU * k / n), loc[2] - 0.005)) for k in range(n)]
    hi = [bmr.verts.new((loc[0] + r * 1.03 * math.cos(TAU * k / n), loc[1] + r * 1.03 * math.sin(TAU * k / n), loc[2] + r * 0.13)) for k in range(n)]
    for k in range(n):
        j = (k + 1) % n
        bmr.faces.new((lo[k], lo[j], hi[j], hi[k]))


def canoe(root, name, Mt, loc, s, ang, rr):
    """Canoa de madeira (casco escavado) com um remo."""
    o = lathe(root, name, [(0, 0.0, 0.0), (0.05, 0.08, 0.04), (0.5, 0.2, 0.09), (0.95, 0.08, 0.04), (1.0, 0.0, 0.0)], Mt['wood'], segs=16, lv=1)
    o.rotation_euler = (0, math.pi / 2, ang)
    o.scale = (1, 1.0, 1)
    o.location = (loc[0] - math.cos(ang) * 0.5 * s, loc[1] - math.sin(ang) * 0.5 * s, loc[2] + 0.06)
    o.scale = (s * 0.9, s * 1.0, s)
    inner = cyl(root, name + '_dentro', 0.07 * s, 0.75 * s, (loc[0], loc[1], loc[2] + 0.12 * s), m=Mt['bark_d'], v=12, bev=0.01, rot=(math.pi / 2, 0, ang + math.pi / 2))
    inner.scale = (1.4, 0.35, 1)
    tube(root, name + '_remo', [(loc[0] - 0.2 * s, loc[1] - 0.15 * s, loc[2] + 0.15 * s), (loc[0] + 0.3 * s, loc[1] + 0.05 * s, loc[2] + 0.17 * s)], 0.015 * s, Mt['wood_l'], segs=6)
    return o


def palafita(root, name, Mt, loc, s, rr, ang=0.0):
    """Casa de palafita: deck sobre estacas, paredes de tabua, telhado de palha em duas aguas e escadinha."""
    out = []
    W_, D_, Hs = 1.0 * s, 0.8 * s, 0.45 * s
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (loc[0] + x * ca - y * sa, loc[1] + x * sa + y * ca, loc[2] + z)
    for ix in (-1, 0, 1):
        for iy in (-1, 1):
            x, y = ix * W_ * 0.45, iy * D_ * 0.42
            out.append(tube(root, f'{name}_estaca{ix}{iy}', [P(x, y, -0.25), P(x, y, Hs)], 0.04 * s, Mt['bark_d'], segs=6))
    out.append(box(root, name + '_deck', (W_ * 1.15, D_ * 1.1, 0.06 * s), P(0, 0, Hs + 0.03 * s), rot=(0, 0, ang), m=Mt['plank'], bev=0.012))
    wh = 0.42 * s
    out.append(box(root, name + '_parede', (W_ * 0.8, D_ * 0.72, wh), P(0, 0.04 * s, Hs + 0.06 * s + wh / 2), rot=(0, 0, ang), m=Mt['wood_l'], bev=0.02))
    for k in range(5):
        x = -W_ * 0.4 + W_ * 0.8 * (k + 0.5) / 5
        out.append(box(root, f'{name}_ripa{k}', (0.02 * s, D_ * 0.74, wh * 0.98), P(x, 0.04 * s, Hs + 0.06 * s + wh / 2), rot=(0, 0, ang), m=Mt['wood'], bev=0.004))
    out.append(box(root, name + '_porta', (0.2 * s, 0.03 * s, 0.3 * s), P(0.1 * s, -D_ * 0.33, Hs + 0.21 * s), rot=(0, 0, ang), m=Mt['bark_d'], bev=0.01))
    out.append(box(root, name + '_janela', (0.16 * s, 0.03 * s, 0.12 * s), P(-0.25 * s, -D_ * 0.33, Hs + 0.3 * s), rot=(0, 0, ang), m=Mt['bark_d'], bev=0.01))
    # telhado de palha
    bm = bmesh.new()
    rz = Hs + 0.06 * s + wh
    ridge = [bm.verts.new(P(x, 0.04 * s, rz + 0.42 * s)) for x in (-W_ * 0.55, W_ * 0.55)]
    for sy in (-1, 1):
        eave = [bm.verts.new(P(x, 0.04 * s + sy * D_ * 0.62, rz - 0.04 * s)) for x in (-W_ * 0.58, W_ * 0.58)]
        bm.faces.new((ridge[0], ridge[1], eave[1], eave[0]) if sy < 0 else (ridge[1], ridge[0], eave[0], eave[1]))
    roof = bm_to_obj(bm, name + '_telhado', root, [Mt['straw']], angle=89)
    sm = roof.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.07 * s
    out.append(roof)
    for k in range(4):
        z = 0.08 + k * 0.1
        out.append(box(root, f'{name}_degrau{k}', (0.22 * s, 0.05 * s, 0.025 * s), P(0.1 * s, -D_ * 0.62 - (3 - k) * 0.06 * s, (z) * s + 0.05), rot=(0, 0, ang), m=Mt['wood'], bev=0.005))
    return out


def deck_pad(lote, Mt, loc, r, rr, ang=0.0):
    """Lote de madeira: tabuas paralelas cortadas em circulo e um anel de pedras de rio (a torre cobre tudo)."""
    n = 7
    w = 2 * r / n
    for k in range(n):
        y = -r + w * (k + 0.5)
        half = math.sqrt(max(0.0, r * r - y * y))
        if half < 0.05:
            continue
        x0 = rr.uniform(-0.02, 0.02)
        ca, sa = math.cos(ang), math.sin(ang)
        cx, cy = loc[0] + x0 * ca - y * sa, loc[1] + x0 * sa + y * ca
        lote.box(Mt['plank'] if k % 2 else Mt['wood_l'], (half * 2 * 0.98, w * 0.92, 0.05), (cx, cy, loc[2] + 0.025), rot=(0, 0, ang))
    m = 22
    for k in range(m):
        a = TAU * k / m + rr.uniform(-0.04, 0.04)
        rr_ = r + 0.07
        lote.pebble(Mt['stone'] if k % 3 else Mt['stone_d'], (loc[0] + rr_ * math.cos(a), loc[1] + rr_ * math.sin(a), loc[2] + 0.01), rr.uniform(0.08, 0.11),
                    squash=0.6, rot=a, rr=rr)
