"""Enfeites 3D do cenario (estilo "soft relaxante" das torres): rochas, arbustos, capim, juncos, palmeiras, colunas,
muros, obeliscos, tendas, ossos, rochedos, lavouras e fendas de lava.

Tudo fica no chao em z = 0 do proprio objeto (o cenario posiciona e gira). Pecas pequenas e numerosas (seixos, capim)
vao para um Lote: uma malha so por material, para a cena nao ter dezenas de milhares de objetos.
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, Euler, noise
from lib import (TAU, mat, lin, box, cyl, sphere, tube, tube_into, torus, lathe, lathe_into, bm_to_obj, mtx,
                 cloth_grid, register_cloth, flag_wave, register_anim, clay_pot, crate, sack, brazier)


# as tres tamareiras do cenario (o fundo guarda so a sombra; a imagem vem dos sprites que balancam, ambiente.py)
PALM_VARIANTS = [dict(seed=3, lean=(0.22, 0.08)), dict(seed=8, lean=(-0.2, 0.12)), dict(seed=13, lean=(0.08, -0.16))]


# ---------------------------------------------------------------- lote de pecas pequenas (uma malha por material)
class Lote:
    def __init__(self, name):
        self.name = name
        self.bms = {}

    def _bm(self, m):
        if m.name not in self.bms:
            self.bms[m.name] = (bmesh.new(), m)
        return self.bms[m.name][0]

    def pebble(self, m, loc, r, squash=0.6, rot=0.0, rr=None, sub=2, rough=0.18):
        """Seixo arredondado: icosfera achatada com leve deformacao."""
        bm = self._bm(m)
        res = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
        vs = res['verts']
        seed = (rr.random() if rr else 0.3) * 50
        for v in vs:
            n = noise.noise(v.co * 1.3 + Vector((seed, seed * 0.7, 0)))
            v.co *= 1 + rough * n
        bmesh.ops.transform(bm, matrix=mtx(loc, (0, 0, rot), (r * 1.15, r, r * squash)), verts=vs)

    def blade(self, m, base, tip, r, segs=4):
        tube_into(self._bm(m), [base, ((base[0] + tip[0]) / 2 + (tip[0] - base[0]) * 0.1, (base[1] + tip[1]) / 2, (base[2] + tip[2]) * 0.55), tip],
                  r, segs=segs, rfun=lambda t: r * (1 - t) + 0.002)

    def tube(self, m, pts, r, segs=6, rfun=None):
        tube_into(self._bm(m), pts, r, segs=segs, rfun=rfun)

    def box(self, m, size, loc, rot=(0, 0, 0)):
        bm = self._bm(m)
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.transform(bm, matrix=mtx(loc, rot, size), verts=res['verts'])

    def disc(self, m, loc, r, sy=1.0, h=0.01, rot=0.0, notch=0.0, n=18):
        """Disco fino (vitoria-regia, lajota redonda); notch abre uma fatia."""
        bm = self._bm(m)
        top, bot = [], []
        a0 = notch / 2
        for k in range(n + 1 if notch else n):
            a = a0 + (TAU - notch) * k / n
            x, y = r * math.cos(a + rot), r * sy * math.sin(a + rot)
            top.append(bm.verts.new((loc[0] + x, loc[1] + y, loc[2] + h)))
            bot.append(bm.verts.new((loc[0] + x, loc[1] + y, loc[2])))
        if notch:
            ct, cb = bm.verts.new((loc[0], loc[1], loc[2] + h)), bm.verts.new((loc[0], loc[1], loc[2]))
            top.insert(0, ct)
            bot.insert(0, cb)
        bm.faces.new(top)
        bm.faces.new(list(reversed(bot)))
        for i in range(len(top)):
            j = (i + 1) % len(top)
            bm.faces.new((bot[i], bot[j], top[j], top[i]))

    def done(self, root, smooth=True):
        out = []
        for key, (bm, m) in self.bms.items():
            if not bm.verts:
                bm.free()
                continue
            o = bm_to_obj(bm, f'{self.name}_{key}', root, [m], angle=80 if smooth else 30)
            out.append(o)
        self.bms = {}
        return out


# ---------------------------------------------------------------- rochas
def rock(root, name, m, loc, size, rr, squash=0.62, sub=3, lumpy=0.22, rot=None, sink=0.25):
    """Rocha macia: icosfera com ruido de baixa frequencia, achatada e meio enterrada."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    s = rr.random() * 40
    for v in bm.verts:
        n = noise.noise(v.co * 0.9 + Vector((s, s * 1.3, s * 0.4)))
        n2 = noise.noise(v.co * 2.2 + Vector((s * 0.5, s, 3)))
        v.co *= 1 + lumpy * n + lumpy * 0.35 * n2
        if v.co.z > 0.35:   # topo um pouco aplainado (rocha de deserto gasta pelo vento)
            v.co.z = 0.35 + (v.co.z - 0.35) * 0.55
    o = bm_to_obj(bm, name, root, [m], angle=80)
    o.scale = (size * (1 + rr.uniform(-0.15, 0.25)), size * (1 + rr.uniform(-0.15, 0.15)), size * squash)
    o.location = (loc[0], loc[1], loc[2] - size * squash * sink)
    o.rotation_euler = (0, 0, rot if rot is not None else rr.uniform(0, TAU))
    return o


def rock_cluster(root, name, m, loc, size, rr, n=3, m2=None):
    out = [rock(root, name + '_0', m, loc, size, rr)]
    for k in range(1, n):
        a = rr.uniform(0, TAU)
        d = size * rr.uniform(0.9, 1.4)
        out.append(rock(root, f'{name}_{k}', m2 if (m2 and k % 2) else m, (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a) * 0.8, loc[2]),
                        size * rr.uniform(0.35, 0.6), rr))
    return out


def strata_rock(root, name, m, m2, loc, rx, ry, h, rr, layers=4, top_flat=True):
    """Rochedo em camadas (desfiladeiro): degraus arredondados que estreitam para cima, com faixas de cor."""
    s = rr.random() * 30
    out = []
    z = 0.0
    for k in range(layers):
        hk = h / layers * rr.uniform(0.85, 1.15)
        k0 = 1 - 0.13 * k
        k1 = 1 - 0.13 * k - 0.08
        prof = [(0.0, rx * k0, ry * k0), (hk * 0.45, rx * (k0 - 0.015), ry * (k0 - 0.015)), (hk * 0.9, rx * k1, ry * k1), (hk, rx * (k1 - 0.04), ry * (k1 - 0.04))]

        def wob(a, zz, k=k):
            return 0.09 * noise.noise(Vector((math.cos(a) * 1.6 + s, math.sin(a) * 1.6, k * 0.7))) + 0.04 * math.sin(a * 5 + k)
        o = lathe(root, f'{name}_c{k}', prof, m if k % 2 == 0 else (m2 or m), segs=28, wobble=wob, lv=1)
        o.location = (loc[0], loc[1], loc[2] + z - (0.05 if k == 0 else 0.02))
        out.append(o)
        z += hk * 0.96
    return out, z


# ---------------------------------------------------------------- vegetacao
def bush(root, name, m, loc, size, rr, m2=None, flowers=None):
    """Arbusto redondo: cachos de esferas macias."""
    out = []
    n = 5 + rr.randrange(4)
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.3, 0.3)
        d = size * rr.uniform(0.25, 0.55) if k else 0.0
        r = size * rr.uniform(0.38, 0.55) * (1.25 if k == 0 else 1)
        z = r * 0.75 + (size * 0.25 if k == 0 else 0)
        o = sphere(root, f'{name}_{k}', r, (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a), loc[2] + z),
                   scale=(1, 1, 0.85), m=m2 if (m2 and k % 3 == 1) else m, seg=14)
        out.append(o)
    if flowers:
        for k in range(4):
            a = rr.uniform(0, TAU)
            out.append(sphere(root, f'{name}_flor{k}', size * 0.07, (loc[0] + size * 0.45 * math.cos(a), loc[1] + size * 0.45 * math.sin(a), loc[2] + size * rr.uniform(0.5, 0.85)),
                              m=flowers, seg=8))
    return out


def tuft(lote, m, loc, size, rr, n=7, spread=0.04, m2=None):
    """Tufo de capim (laminas finas e curvas)."""
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.4, 0.4)
        lean = rr.uniform(0.25, 0.6)
        hgt = size * rr.uniform(0.7, 1.1)
        b = (loc[0] + spread * math.cos(a) * rr.random(), loc[1] + spread * math.sin(a) * rr.random(), loc[2])
        t = (b[0] + math.cos(a) * hgt * lean, b[1] + math.sin(a) * hgt * lean, loc[2] + hgt)
        lote.blade(m2 if (m2 and k % 2) else m, b, t, size * 0.07)


def drybush(lote, m, loc, size, rr):
    """Arbusto seco: galhos finos que se abrem."""
    for k in range(9):
        a = TAU * k / 9 + rr.uniform(-0.3, 0.3)
        up = rr.uniform(0.5, 1.0)
        L = size * rr.uniform(0.6, 1.0)
        p0 = (loc[0], loc[1], loc[2])
        p1 = (loc[0] + math.cos(a) * L * 0.35, loc[1] + math.sin(a) * L * 0.35, loc[2] + L * up * 0.45)
        p2 = (loc[0] + math.cos(a) * L * 0.8, loc[1] + math.sin(a) * L * 0.8, loc[2] + L * up * 0.75)
        lote.tube(m, [p0, p1, p2], size * 0.035, segs=4, rfun=lambda t: size * (0.035 - 0.025 * t))


def reeds(lote, m, m_head, loc, size, rr, n=6):
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0, size * 0.18)
        b = (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a), loc[2])
        hgt = size * rr.uniform(0.7, 1.15)
        lean = rr.uniform(-0.12, 0.12)
        t = (b[0] + lean * hgt, b[1] + lean * 0.5 * hgt, b[2] + hgt)
        lote.blade(m, b, t, size * 0.03)
        if k % 2 == 0:
            c = (b[0] + lean * hgt * 0.8, b[1] + lean * 0.4 * hgt, b[2] + hgt * 0.8)
            lote.tube(m_head, [c, (c[0] + lean * 0.05, c[1], c[2] + size * 0.14)], size * 0.035, segs=6)


def cactus(root, name, m, loc, size, rr):
    out = [tube(root, name, [(loc[0], loc[1], loc[2] - 0.02), (loc[0], loc[1], loc[2] + size)], size * 0.16, m, segs=12,
                rfun=lambda t: size * (0.16 - 0.04 * t * t * t))]
    for k, s in enumerate((-1, 1)):
        if rr.random() < 0.3 and k:
            continue
        z0 = size * rr.uniform(0.35, 0.55)
        ox = s * size * 0.32
        out.append(tube(root, f'{name}_b{k}', [(loc[0] + s * size * 0.1, loc[1], loc[2] + z0), (loc[0] + ox, loc[1], loc[2] + z0 + size * 0.03),
                                              (loc[0] + ox, loc[1], loc[2] + z0 + size * rr.uniform(0.3, 0.45))], size * 0.09, m, segs=10,
                        rfun=lambda t: size * (0.09 - 0.02 * t * t)))
    return out


def palm(root, tag, P, s=1.0, seed=0, lean=(0.22, 0.1), animate=True):
    """Tamareira: tronco em aneis, coroa de folhas pendentes (que balancam no loop) e cachos de tamaras."""
    rr = random.Random(seed)
    bark = mat('casca_palmeira', '#a07648', rough=0.85, var=0.08, bump=0.45)
    bark_d = mat('casca_palmeira_esc', '#7d5634', rough=0.9, var=0.06, bump=0.4)
    leaf = mat('folha_palmeira', '#5e9a3e', rough=0.75, var=0.1, bump=0.05, sheen=0.3)
    leaf_l = mat('folha_palmeira_clara', '#86b84c', rough=0.75, var=0.08, bump=0.05, sheen=0.3)
    date = mat('tamara', '#c0662c', rough=0.55, var=0.1, bump=0.05)
    Hh = 1.55 * s
    top = Vector((lean[0] * Hh, lean[1] * Hh, Hh))
    pts = []
    for k in range(9):
        t = k / 8
        pts.append(Vector((lean[0] * Hh * t * t, lean[1] * Hh * t * t, Hh * t)))
    out = [tube(root, tag + '_tronco', pts, 0.09 * s, bark, segs=12,
                rfun=lambda t: s * (0.1 - 0.035 * t) * (1 + 0.1 * abs(math.sin(t * math.pi * 11))))]
    # anel escuro no pe e no topo
    out.append(sphere(root, tag + '_pe', 0.13 * s, (0, 0, 0.02 * s), scale=(1, 1, 0.45), m=bark_d, seg=14))
    out.append(sphere(root, tag + '_copa', 0.1 * s, tuple(top + Vector((0, 0, 0.02 * s))), scale=(1, 1, 0.8), m=bark_d, seg=14))
    for k in range(3):
        a = TAU * k / 3 + 0.5
        out.append(sphere(root, f'{tag}_tamaras{k}', 0.065 * s, tuple(top + Vector((0.09 * s * math.cos(a), 0.09 * s * math.sin(a), -0.07 * s))),
                          scale=(1, 1, 1.25), m=date, seg=10))
    n = 9
    fronds = []
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.15, 0.15)
        L = s * rr.uniform(0.95, 1.2)
        rise = rr.uniform(0.15, 0.45)
        piv = _pivot(root, f'{tag}_folha{k}_piv', tuple(top), rot=(0, 0, a))
        fr = frond(root, f'{tag}_folha{k}', L, s, rise, leaf if k % 2 else leaf_l, rr)
        fr.parent = piv
        fronds.append((piv, k))
        out.append(fr)
    if animate:
        for piv, k in fronds:
            ph0 = k / n

            def sway(o, mb, ph, ph0=ph0, k=k):
                # brisa: as folhas sobem e descem defasadas, com um leve giro
                w = math.sin(TAU * (ph + ph0))
                w2 = math.sin(TAU * (2 * ph + ph0 * 1.7))
                o.matrix_basis = mb @ Matrix.Rotation(0.07 * w + 0.025 * w2, 4, 'Y') @ Matrix.Rotation(0.04 * math.sin(TAU * (ph + ph0 + 0.25)), 4, 'Z')
            register_anim(piv, sway)
    return out


def _pivot(root, name, loc, rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    root.users_collection[0].objects.link(e)
    e.parent = root
    e.location = loc
    e.rotation_euler = rot
    e['set'] = root['set']
    return e


def frond(root, name, L, s, rise, m, rr):
    """Folha de palmeira: tira em V ao longo de uma curva que sobe e cai, com folíolos serrilhados nas bordas."""
    bm = bmesh.new()
    nseg = 14
    rows = []
    for i in range(nseg + 1):
        t = i / nseg
        x = L * t
        z = s * (rise * math.sin(t * math.pi * 0.8) - 0.55 * t * t) * 1.0
        w = s * 0.2 * math.sin(math.pi * min(1.0, t * 1.15 + 0.06)) * (1 - 0.3 * t)
        serr = 0.35 * (i % 2)
        fold = w * 0.35
        rows.append([bm.verts.new((x, -w * (1 - serr), z - fold)), bm.verts.new((x, 0, z + 0.012 * s)), bm.verts.new((x, w * (1 - serr), z - fold))])
    for i in range(nseg):
        A, B = rows[i], rows[i + 1]
        bm.faces.new((A[0], B[0], B[1], A[1]))
        bm.faces.new((A[1], B[1], B[2], A[2]))
    o = bm_to_obj(bm, name, root, [m], angle=89)
    sm = o.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.012 * s
    return o


# ---------------------------------------------------------------- construcoes e ruinas
def column(root, name, m, m_cap, loc, h, r, rr, broken=False):
    out = [cyl(root, name + '_base', r * 1.35, r * 0.5, (loc[0], loc[1], loc[2] + r * 0.25), m=m_cap, v=20, bev=r * 0.12)]
    hh = h * (rr.uniform(0.45, 0.75) if broken else 1.0)

    def flute(a, z):
        return 0.05 * math.cos(a * 12)
    prof = [(0, r, r), (hh * 0.5, r * 0.96, r * 0.96), (hh, r * 0.9, r * 0.9)]
    o = lathe(root, name + '_fuste', prof, m, segs=36, wobble=flute, lv=1)
    o.location = (loc[0], loc[1], loc[2] + r * 0.45)
    out.append(o)
    if broken:
        # topo quebrado: tampa inclinada e um pedaco caido ao lado
        out.append(cyl(root, name + '_quebra', r * 0.9, r * 0.25, (loc[0], loc[1], loc[2] + r * 0.45 + hh), m=m, v=20, bev=r * 0.1,
                       rot=(rr.uniform(-0.25, 0.25), rr.uniform(-0.25, 0.25), 0)))
        a = rr.uniform(0, TAU)
        out.append(cyl(root, name + '_caco', r * 0.85, r * 1.1, (loc[0] + r * 2.4 * math.cos(a), loc[1] + r * 2.4 * math.sin(a), loc[2] + r * 0.6),
                       m=m, v=20, bev=r * 0.1, rot=(math.pi / 2, 0, a + 0.6)))
    else:
        out.append(cyl(root, name + '_capitel', r * 1.1, r * 0.35, (loc[0], loc[1], loc[2] + r * 0.45 + hh + r * 0.17), r2=r * 1.4, m=m_cap, v=20, bev=r * 0.08))
        out.append(box(root, name + '_abaco', (r * 3.0, r * 3.0, r * 0.35), (loc[0], loc[1], loc[2] + r * 0.45 + hh + r * 0.52), m=m_cap, bev=r * 0.1))
    return out


def fallen_column(root, name, m, loc, r, rr, ang=None):
    a = rr.uniform(0, TAU) if ang is None else ang
    out = []
    n = 3
    for k in range(n):
        d = (k - 1) * r * 2.3 + rr.uniform(-0.03, 0.03)
        out.append(cyl(root, f'{name}_{k}', r, r * 2.1, (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a), loc[2] + r * 0.85),
                       m=m, v=24, bev=r * 0.12, rot=(math.pi / 2, 0, a + math.pi / 2 + rr.uniform(-0.12, 0.12))))
    return out


def ruin_wall(root, name, m, m2, loc, w, h, rr, ang=0.0, depth=0.26):
    """Muro arruinado: fiadas de blocos arredondados com topo irregular."""
    out = []
    bw, bh = 0.3, 0.17
    cols = max(2, int(w / bw))
    prof = [h * (0.45 + 0.55 * abs(math.sin(i * 1.3 + rr.random() * 2))) for i in range(cols)]
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(cols):
        rows = max(1, int(prof[i] / bh))
        for j in range(rows):
            off = (j % 2) * bw * 0.5
            x = -w / 2 + i * bw + off + bw / 2
            if x > w / 2:
                continue
            z = j * bh + bh / 2
            lx, ly = loc[0] + x * ca, loc[1] + x * sa
            out.append(box(root, f'{name}_{i}_{j}', (bw * 0.94, depth * rr.uniform(0.92, 1.0), bh * 0.92), (lx, ly, loc[2] + z),
                           rot=(0, 0, ang + rr.uniform(-0.04, 0.04)), m=m2 if (m2 and rr.random() < 0.3) else m, bev=0.035, seg=3))
    return out


def obelisk(root, name, m, m_tip, loc, h, rr):
    out = [box(root, name + '_base', (0.5, 0.5, 0.16), (loc[0], loc[1], loc[2] + 0.08), m=m, bev=0.03)]
    bm = bmesh.new()
    w0, w1 = 0.17, 0.11
    vs = []
    for z, w in ((0, w0), (h, w1)):
        vs.append([bm.verts.new((sx * w, sy * w, z)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for k in range(4):
        bm.faces.new((vs[0][k], vs[0][(k + 1) % 4], vs[1][(k + 1) % 4], vs[1][k]))
    tip = bm.verts.new((0, 0, h + w1 * 1.5))
    for k in range(4):
        bm.faces.new((vs[1][k], vs[1][(k + 1) % 4], tip))
    bm.faces.new(list(reversed(vs[0])))
    for f in bm.faces:
        if tip in f.verts:
            f.material_index = 1
    o = bm_to_obj(bm, name, root, [m, m_tip], bev=0.012, angle=30)
    o.location = (loc[0], loc[1], loc[2] + 0.16)
    o.rotation_euler = (0, 0, rr.uniform(-0.3, 0.3))
    out.append(o)
    return out


def tent(root, name, P, loc, rr, ang=0.0, m_cloth=None, s=1.0):
    """Tenda de nomade: lona listrada em duas aguas, estacas e cordas."""
    cl = m_cloth or mat('lona_listrada', '#c2563a', rough=0.85, var=0.0, bump=0.06, stripes=(4.0, '#c2563a', '#f1e2c2'), sheen=0.3)
    W_, D_, H_ = 0.9 * s, 0.75 * s, 0.6 * s
    bm = bmesh.new()
    ridge = [bm.verts.new((x, 0, H_)) for x in (-W_ / 2, W_ / 2)]
    for sy in (-1, 1):
        sag = [bm.verts.new((x, sy * D_ / 2, 0.02)) for x in (-W_ / 2 - 0.05 * s, W_ / 2 + 0.05 * s)]
        bm.faces.new((ridge[0], ridge[1], sag[1], sag[0]) if sy < 0 else (ridge[1], ridge[0], sag[0], sag[1]))
    back = [bm.verts.new((W_ / 2, sy * D_ / 2, 0.02)) for sy in (-1, 1)]
    bm.faces.new((ridge[1], back[0], back[1]))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
    for v in bm.verts:   # lona caida entre as estacas
        v.co.z -= 0.05 * s * math.sin(math.pi * (v.co.x / W_ + 0.5)) * (1 - v.co.z / H_)
    o = bm_to_obj(bm, name, root, [cl], angle=89)
    sm = o.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.02 * s
    o.location = loc
    o.rotation_euler = (0, 0, ang)
    out = [o]
    dark = mat('tenda_porta', '#4a2414', rough=0.95, var=0.0, bump=0.0)
    door = cyl(root, name + '_porta', 0.2 * s, 0.01, (0, 0, 0), m=dark, v=3, bev=0.0)
    door.parent = o
    door.location = (-W_ / 2 - 0.005, 0, 0.17 * s)
    door.rotation_euler = (0, math.pi / 2, 0)
    door.scale = (1.4, 1.0, 1.0)
    for sx in (-1, 1):
        p = tube(root, f'{name}_mastro{sx}', [(sx * W_ / 2, 0, 0), (sx * W_ / 2, 0, H_ + 0.08 * s)], 0.018 * s, P['wood'], segs=6)
        p.parent = o
    return out


def bones(root, name, m, loc, rr, s=1.0, skull=True):
    """Esqueleto de camelo meio enterrado: costelas em arco e cranio."""
    out = []
    a = rr.uniform(0, TAU)
    ca, sa = math.cos(a), math.sin(a)
    sp = []
    for k in range(7):
        d = (k - 3) * 0.12 * s
        sp.append((loc[0] + d * ca, loc[1] + d * sa, loc[2] + 0.04 * s))
    out.append(tube(root, name + '_coluna', sp, 0.025 * s, m, segs=8))
    for k in range(5):
        d = (k - 2) * 0.12 * s
        cx, cy = loc[0] + d * ca, loc[1] + d * sa
        for side in (-1, 1):
            pts = []
            for j in range(6):
                t = j / 5
                r = 0.22 * s * (1 - 0.12 * abs(k - 2))
                px = cx + side * (-sa) * r * math.sin(t * 1.9)
                py = cy + side * ca * r * math.sin(t * 1.9)
                pz = loc[2] + 0.04 * s + r * math.cos(t * 1.9) * 0.9 * (1 - t * 0.3)
                pts.append((px, py, pz))
            out.append(tube(root, f'{name}_costela{k}{side}', pts, 0.018 * s, m, segs=6, rfun=lambda t: 0.018 * s * (1 - 0.5 * t)))
    if skull:
        hx, hy = loc[0] + 0.5 * s * ca, loc[1] + 0.5 * s * sa
        out.append(sphere(root, name + '_cranio', 0.09 * s, (hx, hy, loc[2] + 0.06 * s), scale=(1.5, 0.9, 0.8), m=m, seg=14, rot=(0, 0, a)))
    return out


def skull_horns(root, name, m, loc, rr, s=1.0):
    a = rr.uniform(-0.6, 0.6)
    out = [sphere(root, name, 0.09 * s, (loc[0], loc[1], loc[2] + 0.05 * s), scale=(1, 1.3, 0.8), m=m, seg=14, rot=(0, 0, a))]
    for side in (-1, 1):
        out.append(tube(root, f'{name}_chifre{side}', [(loc[0] + side * 0.07 * s, loc[1], loc[2] + 0.08 * s), (loc[0] + side * 0.2 * s, loc[1] + 0.02 * s, loc[2] + 0.14 * s),
                                                      (loc[0] + side * 0.26 * s, loc[1] + 0.03 * s, loc[2] + 0.24 * s)], 0.03 * s, m, segs=8,
                        rfun=lambda t: s * (0.03 - 0.026 * t)))
    return out


def jars(root, name, P, loc, rr, n=3, s=1.0):
    out = []
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.3, 0.3)
        d = 0.14 * s if k else 0.0
        clay_pot(root, f'{name}_{k}', P, (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a), loc[2]), s=s * rr.uniform(0.9, 1.25))
    return out


def field(root, name, m_soil, m_crop, lote, loc, w, d, rr, rows=5, ang=0.0):
    """Lavoura: canteiro de terra escura com fileiras de plantinhas redondas."""
    out = [box(root, name + '_terra', (w, d, 0.06), (loc[0], loc[1], loc[2] + 0.0), rot=(0, 0, ang), m=m_soil, bev=0.03)]
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(rows):
        y = -d / 2 + d * (i + 0.5) / rows
        n = int(w / 0.12)
        for j in range(n):
            x = -w / 2 + w * (j + 0.5) / n + rr.uniform(-0.01, 0.01)
            px, py = loc[0] + x * ca - y * sa, loc[1] + x * sa + y * ca
            lote.pebble(m_crop, (px, py, loc[2] + 0.06), 0.05 * rr.uniform(0.8, 1.2), squash=0.9, rr=rr, sub=1, rough=0.25)
    return out


def lava_crack(lote, m_glow, m_rim, pts, w):
    """Fenda de lava: borda escura levantada e o miolo que brilha."""
    # a borda fica mais baixa que o miolo, senao esconde a lava
    lote.tube(m_rim, [(p[0], p[1], p[2] - 0.065) for p in pts], w * 1.7, segs=6, rfun=lambda t: w * 1.7 * (0.4 + 0.6 * math.sin(math.pi * t)))
    lote.tube(m_glow, [(p[0], p[1], p[2] - 0.01) for p in pts], w, segs=6, rfun=lambda t: w * (0.3 + 0.7 * math.sin(math.pi * t)))


def gate_post(root, name, P, loc, m_stone, m_banner, rr, emblem=None, s=1.0):
    """Pilar da saida (a muralha do reino): bloco de arenito, cornija, faixa com a bandeira e um pomo de ouro."""
    x, y, z = loc
    k = s
    out = [box(root, name + '_base', (0.42 * k, 0.42 * k, 0.14 * k), (x, y, z + 0.07 * k), m=m_stone, bev=0.04 * k),
           box(root, name + '_fuste', (0.32 * k, 0.32 * k, 0.86 * k), (x, y, z + 0.57 * k), m=m_stone, bev=0.05 * k),
           box(root, name + '_cornija', (0.44 * k, 0.44 * k, 0.1 * k), (x, y, z + 1.04 * k), m=m_stone, bev=0.035 * k),
           sphere(root, name + '_topo', 0.12 * k, (x, y, z + 1.16 * k), scale=(1, 1, 0.8), m=P['gold'], seg=14)]
    out.append(box(root, name + '_faixa', (0.33 * k, 0.04 * k, 0.6 * k), (x, y - 0.175 * k, z + 0.58 * k), m=m_banner, bev=0.01 * k))
    out.append(box(root, name + '_faixaOuro', (0.34 * k, 0.045 * k, 0.04 * k), (x, y - 0.18 * k, z + 0.87 * k), m=P['gold'], bev=0.008 * k))
    tri = cyl(root, name + '_ponta', 0.17 * k, 0.04 * k, (x, y - 0.175 * k, z + 0.26 * k), m=m_banner, v=3, bev=0.005, rot=(math.pi / 2, 0, math.pi / 2))
    tri.scale = (1, 0.55, 1)
    out.append(tri)
    return out
