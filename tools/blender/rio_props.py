"""Enfeites do Rio das Duas Aguas (fases 9 a 12): mangue-vermelho com raizes em arco, guaras, garcas, caranguejos,
curral de pesca, tochas e vaga-lumes (mangue ao luar), arenito e quartzo do tepui, a fenda da Fumaca, flutuante,
barco de recreio, ponte, estiva e aninga (encontro das aguas e cheia).

Mesmas convencoes do mata_props.py: tudo nasce no chao (z do ponto passado), pecas numerosas vao num Lote e as que
brilham usam glow_mat (entram no passe de luz do jogo).
"""
import math
import bpy, bmesh
from mathutils import Vector, noise
from lib import (TAU, mat, glow_mat, box, cyl, sphere, tube, lathe, bm_to_obj)
from cenario_props import rock


def M(key, hexcol, **kw):
    kw.setdefault('var', 0.1)
    kw.setdefault('bump', 0.15)
    return mat('rio_' + key, hexcol, **kw)


def rio_mats():
    return {
        'mangue_casca': M('mangue_casca', '#7d6656', rough=0.85, bump=0.4), 'mangue_raiz': M('mangue_raiz', '#8e7462', rough=0.85, bump=0.35),
        'mangue_folha': M('mangue_folha', '#3f7f45', rough=0.45, var=0.12, sheen=0.2), 'mangue_folha_cl': M('mangue_folha_cl', '#5e9c4c', rough=0.5, var=0.12),
        'lama': M('lama', '#4f463e', rough=0.35, var=0.08, bump=0.2), 'guara': M('guara', '#ea4a3a', rough=0.6, var=0.06, bump=0.05, sheen=0.3),
        'guara_bico': M('guara_bico', '#3a2a26', rough=0.5, var=0.04, bump=0.0), 'garca': M('garca', '#f6f2ea', rough=0.6, var=0.03, bump=0.05, sheen=0.3),
        'garca_bico': M('garca_bico', '#f0b43a', rough=0.5, var=0.04, bump=0.0), 'perna': M('perna', '#4a3a30', rough=0.6, var=0.04, bump=0.0),
        'caranguejo': M('caranguejo', '#e0602e', rough=0.45, var=0.1, bump=0.05), 'caranguejo2': M('caranguejo2', '#5f7fa8', rough=0.45, var=0.1, bump=0.05),
        'estaca': M('estaca', '#6e5a48', rough=0.85, bump=0.35), 'rede': M('rede', '#c9b896', rough=0.9, var=0.05, bump=0.1),
        'chama': glow_mat('rio_chama', '#ffb04a', 6.0, 18.0, rough=0.5, var=0.05, bump=0.0),
        'vagalume': glow_mat('rio_vagalume', '#e8ff7a', 8.0, 22.0, rough=0.5, var=0.05, bump=0.0),
        'lua': glow_mat('rio_lua', '#e6eeff', 1.6, 6.0, rough=0.3, var=0.02, bump=0.0),
        'arenito': M('arenito', '#c39282', rough=0.88, bump=0.35), 'arenito2': M('arenito2', '#a5776a', rough=0.9, bump=0.35),
        'arenito_esc': M('arenito_esc', '#5a4642', rough=0.9, bump=0.35), 'liquen': M('liquen', '#3c3634', rough=0.95, bump=0.3),
        'quartzo': M('quartzo', '#f4d6e6', rough=0.15, var=0.08, bump=0.0),
        'quartzo2': M('quartzo2', '#e8f2ff', rough=0.15, var=0.08, bump=0.0),
        'jarro': M('jarro', '#7fa84a', rough=0.55, var=0.12, bump=0.1), 'jarro_boca': M('jarro_boca', '#c8443a', rough=0.55, var=0.1, bump=0.05),
        'brasa': glow_mat('rio_brasa', '#ff6a1a', 5.0, 16.0, rough=0.6, var=0.1, bump=0.1), 'fenda': M('fenda', '#241c1c', rough=0.9, bump=0.4),
        'brasa_miolo': glow_mat('rio_brasa_miolo', '#ffd27a', 8.0, 22.0, rough=0.5, var=0.05, bump=0.0),
        'nuvem': M('nuvem', '#f4f2f0', rough=0.95, var=0.03, bump=0.05, sheen=0.4),
        'casco': M('casco', '#f2efe6', rough=0.6, var=0.03, bump=0.05), 'faixa_azul': M('faixa_azul', '#3e7fb8', rough=0.6, var=0.03, bump=0.0),
        'faixa_verm': M('faixa_verm', '#c8463a', rough=0.6, var=0.03, bump=0.0), 'teto': M('teto', '#3f8a8a', rough=0.7, var=0.04, bump=0.05),
        'rede1': M('rede1', '#e8a63a', rough=0.9, var=0.05, bump=0.1), 'rede2': M('rede2', '#d9446a', rough=0.9, var=0.05, bump=0.1),
        'rede3': M('rede3', '#4fa0c8', rough=0.9, var=0.05, bump=0.1),
        'parede_az': M('parede_az', '#6aa6c8', rough=0.75, bump=0.2), 'parede_am': M('parede_am', '#e8c25a', rough=0.75, bump=0.2),
        'parede_vd': M('parede_vd', '#7fb86a', rough=0.75, bump=0.2), 'tora': M('tora', '#7a5636', rough=0.85, bump=0.4),
        'aninga': M('aninga', '#5f9e45', rough=0.6, var=0.12, sheen=0.2), 'canarana': M('canarana', '#8fbf4f', rough=0.8, var=0.15, bump=0.1),
        'marca': M('marca_cheia', '#6a5a46', rough=0.9, bump=0.2),
    }


def _quad(a, c, b, n=8):
    return [tuple((1 - t) ** 2 * a[i] + 2 * (1 - t) * t * c[i] + t * t * b[i] for i in range(3)) for t in (k / n for k in range(n + 1))]


# ---------------------------------------------------------------- mangue
def mangrove(root, name, R, loc, s, rr, lote=None):
    """Mangue-vermelho: tronco que nasce acima da lama sobre um leque de raizes em arco, e copa larga e lustrosa."""
    out = []
    x0, y0, z0 = loc
    hb = s * rr.uniform(0.45, 0.6)          # onde as raizes se juntam
    H = s * rr.uniform(1.5, 1.9)
    lean = rr.uniform(-0.12, 0.12) * s
    out.append(tube(root, name + '_tronco', [(x0, y0, z0 + hb * 0.7), (x0 + lean * 0.5, y0, z0 + H * 0.6), (x0 + lean, y0, z0 + H)], 0.12 * s,
                    R['mangue_casca'], segs=10, rfun=lambda t: s * (0.13 - 0.05 * t)))
    n = rr.randrange(7, 10)
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.25, 0.25)
        d = s * rr.uniform(0.5, 0.85)
        zt = z0 + hb * rr.uniform(0.75, 1.05)
        top = (x0 + math.cos(a) * 0.08 * s, y0 + math.sin(a) * 0.08 * s, zt)
        foot = (x0 + math.cos(a) * d, y0 + math.sin(a) * d, z0 - 0.06)
        ctrl = (x0 + math.cos(a) * d * 0.62, y0 + math.sin(a) * d * 0.62, zt + hb * 0.35)
        pts = _quad(top, ctrl, foot, 7)
        if lote:
            lote.tube(R['mangue_raiz'], pts, 0.035 * s, segs=6, rfun=lambda t: s * (0.045 - 0.018 * t))
        else:
            out.append(tube(root, f'{name}_raiz{k}', pts, 0.035 * s, R['mangue_raiz'], segs=6, rfun=lambda t: s * (0.045 - 0.018 * t)))
    # galhos e copa: nuvens achatadas de folha brilhante
    top = Vector((x0 + lean, y0, z0 + H))
    for k in range(rr.randrange(6, 9)):
        a = TAU * k / 7 + rr.uniform(-0.4, 0.4)
        d = s * rr.uniform(0.25, 0.75) if k else 0
        r = s * rr.uniform(0.38, 0.55)
        out.append(sphere(root, f'{name}_copa{k}', r, (top.x + d * math.cos(a), top.y + d * math.sin(a) * 0.85, top.z + rr.uniform(-0.2, 0.2) * s),
                          scale=(1.15, 1.15, 0.62), m=R['mangue_folha'] if k % 3 else R['mangue_folha_cl'], seg=16))
    return out


def pneumatophores(lote, R, loc, r, rr, n=14):
    """Respiradouros do mangue-preto: palitinhos saindo da lama em volta da arvore."""
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = r * math.sqrt(rr.random())
        x, y = loc[0] + d * math.cos(a), loc[1] + d * math.sin(a)
        h = rr.uniform(0.06, 0.14)
        lote.blade(R['mangue_raiz'], (x, y, loc[2] - 0.02), (x + rr.uniform(-0.01, 0.01), y, loc[2] + h), 0.012)


def crab(lote, R, loc, s, ang, rr, blue=False):
    m = R['caranguejo2'] if blue else R['caranguejo']
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (loc[0] + x * ca - y * sa, loc[1] + x * sa + y * ca, loc[2] + z)
    lote.pebble(m, P(0, 0, 0.03 * s), 0.07 * s, squash=0.45, rot=ang, rr=rr, sub=2, rough=0.05)
    big = rr.random() < 0.5
    for sy in (-1, 1):
        cr = 0.045 * s if (big and sy > 0) else 0.028 * s
        lote.pebble(m, P(0.08 * s, sy * 0.06 * s, 0.045 * s), cr, squash=0.6, rot=ang, rr=rr, sub=1, rough=0.05)
        for j in range(3):
            lx = -0.03 * s + j * 0.03 * s
            lote.blade(m, P(lx, sy * 0.05 * s, 0.03 * s), P(lx - 0.02 * s, sy * 0.11 * s, 0.0), 0.008 * s, segs=3)


def wader(root, name, R, loc, s, ang, rr, kind='guara'):
    """Guara (vermelho, bico curvo) ou garca (branca, bico reto amarelo) parada na lama ou na agua rasa."""
    body = R['guara'] if kind == 'guara' else R['garca']
    beak = R['guara_bico'] if kind == 'guara' else R['garca_bico']
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (loc[0] + x * ca - y * sa, loc[1] + x * sa + y * ca, loc[2] + z)
    out = []
    leg = 0.22 * s
    for sy in (-1, 1):
        out.append(tube(root, f'{name}_perna{sy}', [P(0, sy * 0.03 * s, -0.02), P(0.01 * s, sy * 0.025 * s, leg)], 0.008 * s, R['perna'], segs=5))
    out.append(sphere(root, name + '_corpo', 0.1 * s, P(0, 0, leg + 0.07 * s), scale=(1.5, 0.85, 0.85), m=body, seg=14, rot=(0, -0.3, ang)))
    up = rr.uniform(0.6, 1.0)
    neck = [P(0.1 * s, 0, leg + 0.1 * s), P(0.16 * s, 0, leg + 0.2 * s * up), P(0.14 * s, 0, leg + 0.3 * s * up)]
    out.append(tube(root, name + '_pescoco', neck, 0.025 * s, body, segs=6, rfun=lambda t: s * (0.03 - 0.01 * t)))
    hx, hz = 0.14 * s, leg + 0.31 * s * up
    out.append(sphere(root, name + '_cabeca', 0.035 * s, P(hx, 0, hz), scale=(1.3, 1, 1), m=body, seg=10, rot=(0, 0, ang)))
    if kind == 'guara':
        bk = _quad(P(hx + 0.03 * s, 0, hz), P(hx + 0.12 * s, 0, hz + 0.01 * s), P(hx + 0.16 * s, 0, hz - 0.07 * s), 5)
    else:
        bk = [P(hx + 0.03 * s, 0, hz), P(hx + 0.15 * s, 0, hz - 0.02 * s)]
    out.append(tube(root, name + '_bico', bk, 0.012 * s, beak, segs=5, rfun=lambda t: s * (0.014 - 0.011 * t)))
    return out


def fish_weir(lote, R, pts, rr, h=0.4):
    """Curral de pesca: fileira de estacas finas na agua rasa com a rede presa entre elas."""
    for i, p in enumerate(pts):
        hh = h * rr.uniform(0.85, 1.1)
        lote.tube(R['estaca'], [(p[0], p[1], p[2] - 0.15), (p[0] + rr.uniform(-0.01, 0.01), p[1], p[2] + hh)], 0.018, segs=5)
        if i:
            q = pts[i - 1]
            for z in (0.08, 0.2):
                lote.tube(R['rede'], [(q[0], q[1], q[2] + z), (p[0], p[1], p[2] + z)], 0.006, segs=4)


def torch(root, name, R, loc, s, rr, lights=None):
    """Tocha de margem (fase da noite): vara com cesto e chama que brilha."""
    out = [tube(root, name + '_vara', [(loc[0], loc[1], loc[2] - 0.05), (loc[0] + rr.uniform(-0.03, 0.03), loc[1], loc[2] + 0.62 * s)], 0.022 * s, R['estaca'], segs=6)]
    z = loc[2] + 0.62 * s
    out.append(cyl(root, name + '_cesto', 0.05 * s, 0.07 * s, (loc[0], loc[1], z + 0.02 * s), r2=0.07 * s, m=R['tora'], v=10, bev=0.005))
    out.append(sphere(root, name + '_chama', 0.055 * s, (loc[0], loc[1], z + 0.11 * s), scale=(1, 1, 1.7), m=R['chama'], seg=12))
    if lights is not None:
        lights.append(((loc[0], loc[1], z + 0.2 * s), '#ffb04a', 14.0 * s, 1))
    return out


def fireflies(root, name, R, loc, rr, n=7, spread=0.5):
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = spread * math.sqrt(rr.random())
        sphere(root, f'{name}_{k}', rr.uniform(0.012, 0.02), (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a), loc[2] + rr.uniform(0.15, 0.7)), m=R['vagalume'], seg=6)


def moon_glint(lote, R, loc, rx, rr):
    """Reflexo da lua na agua: tracos claros horizontais que afinam para as pontas."""
    for k in range(9):
        y = (k - 4) * rx * 0.11
        w = rx * (1 - abs(k - 4) / 5.0) * rr.uniform(0.7, 1.0)
        lote.disc(R['lua'], (loc[0] + rr.uniform(-0.05, 0.05) * rx, loc[1] + y, loc[2]), w, sy=0.07, h=0.004, rot=rr.uniform(-0.04, 0.04), n=16)


# ---------------------------------------------------------------- tepui
def sandstone_tower(root, name, R, loc, h, r, rr):
    """Escultura de arenito do topo do tepui: pilha de blocos gastos que alargam e estreitam, com liquen escuro."""
    out = []
    z = 0.0
    s0 = rr.random() * 30
    k = 0
    while z < h:
        hk = r * rr.uniform(0.45, 0.8)
        rk = r * (0.75 + 0.35 * math.sin(z / max(h, 1e-3) * 4 + s0)) * rr.uniform(0.85, 1.1)
        prof = [(0, rk * 0.82, rk * 0.74), (hk * 0.35, rk * 1.0, rk * 0.9), (hk * 0.8, rk * 0.95, rk * 0.86), (hk, rk * 0.8, rk * 0.72)]

        def wob(a, zz, k=k):
            return 0.12 * noise.noise(Vector((math.cos(a) * 1.4 + s0, math.sin(a) * 1.4, k * 0.9))) + 0.05 * math.sin(a * 3 + k)
        o = lathe(root, f'{name}_b{k}', prof, (R['arenito'], R['arenito2'], R['arenito_esc'])[k % 3] if k % 3 != 2 else R['arenito2'], segs=24, wobble=wob, lv=1)
        o.location = (loc[0], loc[1], loc[2] + z - 0.03)
        o.rotation_euler = (0, 0, rr.uniform(0, TAU))
        out.append(o)
        z += hk * 0.92
        k += 1
    return out, z


def quartz(root, name, R, loc, s, rr, pink=True):
    """Drusa de quartzo: prismas de seis faces com ponta, saindo do chao em leque."""
    m = R['quartzo'] if pink else R['quartzo2']
    out = []
    for k in range(rr.randrange(4, 8)):
        a = rr.uniform(0, TAU)
        tilt = rr.uniform(0.1, 0.55)
        L = s * rr.uniform(0.12, 0.28)
        r = s * rr.uniform(0.025, 0.045)
        o = lathe(root, f'{name}_{k}', [(0, r, r), (L, r, r), (L + r * 2.2, 0.001, 0.001)], m, segs=6, lv=0)
        o.location = (loc[0] + math.cos(a) * 0.04 * s, loc[1] + math.sin(a) * 0.04 * s, loc[2] - 0.02)
        o.rotation_euler = (math.sin(a) * tilt, -math.cos(a) * tilt, rr.uniform(0, TAU))
        out.append(o)
    return out


def pitcher_plants(root, name, R, loc, s, rr):
    """Heliamphora (planta-jarro do tepui): tubos verdes com a boca avermelhada."""
    out = []
    for k in range(rr.randrange(4, 7)):
        a = rr.uniform(0, TAU)
        d = s * rr.uniform(0.02, 0.1)
        h = s * rr.uniform(0.18, 0.32)
        x, y = loc[0] + d * math.cos(a), loc[1] + d * math.sin(a)
        lean = 0.04 * s
        pts = [(x, y, loc[2] - 0.02), (x + math.cos(a) * lean * 0.4, y + math.sin(a) * lean * 0.4, loc[2] + h * 0.5), (x + math.cos(a) * lean, y + math.sin(a) * lean, loc[2] + h)]
        out.append(tube(root, f'{name}_{k}', pts, 0.03 * s, R['jarro'], segs=8, rfun=lambda t: s * (0.018 + 0.022 * t)))
        out.append(cyl(root, f'{name}_boca{k}', 0.042 * s, 0.02 * s, (pts[-1][0], pts[-1][1], pts[-1][2]), m=R['jarro_boca'], v=10, bev=0.004))
    return out


def smoke_fissure(lote, root, name, R, pts_ground, w, rr, lights=None):
    """Fenda da Fumaca Negra: rasgo escuro no chao, bordas de rocha queimada e brasa no fundo (a fumaca e do jogo)."""
    # faixa chamuscada larga e rasa embaixo; a brasa por cima dela, com um miolo mais quente
    lote.tube(R['fenda'], [(p[0], p[1], p[2] - w * 2.2) for p in pts_ground], w * 2.4, segs=8, rfun=lambda t: w * 2.4 * (0.35 + 0.65 * math.sin(math.pi * t)))
    lote.tube(R['brasa'], [(p[0], p[1], p[2] - w * 0.6) for p in pts_ground], w, segs=8, rfun=lambda t: w * (0.25 + 0.75 * math.sin(math.pi * t)))
    if len(pts_ground) >= 7:
        lote.tube(R['brasa_miolo'], [(p[0], p[1], p[2] - w * 0.2) for p in pts_ground[2:-2]], w * 0.45, segs=6, rfun=lambda t: w * 0.45 * (0.3 + 0.7 * math.sin(math.pi * t)))
    for i, p in enumerate(pts_ground[1:-1]):
        for sy in (-1, 1):
            q = pts_ground[i + 2] if i + 2 < len(pts_ground) else p
            dx, dy = q[0] - p[0], q[1] - p[1]
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            rock(root, f'{name}_borda{i}{sy}', R['arenito_esc'], (p[0] + nx * sy * w * 2.6, p[1] + ny * sy * w * 2.6, p[2]), w * rr.uniform(1.0, 1.6), rr, squash=0.5)
    if lights is not None:
        mid = pts_ground[len(pts_ground) // 2]
        lights.append(((mid[0], mid[1], mid[2] + 0.2), '#ff6a1a', 30.0, 1))


def cloud(root, name, R, loc, s, rr):
    for k in range(rr.randrange(4, 7)):
        a = rr.uniform(0, TAU)
        d = s * rr.uniform(0, 0.8)
        sphere(root, f'{name}_{k}', s * rr.uniform(0.4, 0.7), (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a) * 0.6, loc[2] + rr.uniform(-0.1, 0.15) * s),
               scale=(1.3, 1.0, 0.55), m=R['nuvem'], seg=14)


# ---------------------------------------------------------------- rio
def bridge(root, name, Mt, R, a, b, width, rr):
    """Ponte de tabuas entre a e b (pontos no chao): pranchas atravessadas, vigas, estacas e corrimao de vara."""
    out = []
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    ang = math.atan2(dy, dx)
    zt = max(a[2], b[2]) + 0.06
    n = max(4, int(L / 0.17))
    lote_m = Mt['plank'], Mt['wood_l']
    for k in range(n):
        t = (k + 0.5) / n
        arch = 0.06 * math.sin(math.pi * t)
        cx, cy = a[0] + dx * t, a[1] + dy * t
        out.append(box(root, f'{name}_tabua{k}', (L / n * 0.9, width * rr.uniform(0.96, 1.04), 0.045), (cx, cy, zt + arch), rot=(0, 0, ang + rr.uniform(-0.03, 0.03)),
                       m=lote_m[k % 2], bev=0.008))
    for sy in (-1, 1):
        ox, oy = nx * sy * width * 0.46, ny * sy * width * 0.46
        rail = [(a[0] + ox + dx * t, a[1] + oy + dy * t, zt + 0.3 + 0.06 * math.sin(math.pi * t)) for t in (0, 0.25, 0.5, 0.75, 1)]
        out.append(tube(root, f'{name}_corrimao{sy}', rail, 0.022, Mt['wood'], segs=6))
        for k in range(5):
            t = k / 4
            px, py = a[0] + ox + dx * t, a[1] + oy + dy * t
            out.append(tube(root, f'{name}_estaca{sy}{k}', [(px, py, -0.3), (px, py, zt + 0.32 + 0.06 * math.sin(math.pi * t))], 0.035, Mt['bark_d'], segs=6))
    return out


def boardwalk(lote, Mt, pts, width, z, rr, posts=True):
    """Estiva: passarela de tabuas sobre estacas ao longo da estrada (baixadas da varzea)."""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ang = math.atan2(dy, dx)
        lote.box(Mt['plank'] if i % 2 else Mt['wood_l'], (L * 0.94, width * rr.uniform(0.97, 1.03), 0.04), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z), rot=(0, 0, ang + rr.uniform(-0.04, 0.04)))
        if posts and i % 3 == 0:
            nx, ny = -dy / L, dx / L
            for sy in (-1, 1):
                px, py = a[0] + nx * sy * width * 0.45, a[1] + ny * sy * width * 0.45
                lote.tube(Mt['bark_d'], [(px, py, -0.35), (px, py, z + 0.01)], 0.03, segs=6)
    # longarinas embaixo das tabuas
    for sy in (-1, 1):
        rail = []
        for p, q in zip(pts[:-1], pts[1:]):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dy) or 1
            rail.append((p[0] - dy / L * sy * width * 0.35, p[1] + dx / L * sy * width * 0.35, z - 0.04))
        if len(rail) > 1:
            lote.tube(Mt['wood'], rail, 0.025, segs=5)


def floating_house(root, name, Mt, R, loc, s, ang, rr):
    """Flutuante: casa colorida de madeira sobre um estrado de toras."""
    out = []
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (loc[0] + x * ca - y * sa, loc[1] + x * sa + y * ca, loc[2] + z)
    for k in range(5):
        y = (k - 2) * 0.17 * s
        out.append(cyl(root, f'{name}_tora{k}', 0.08 * s, 1.35 * s, P(0, y, 0.02), m=R['tora'], v=12, bev=0.01, rot=(math.pi / 2, 0, ang + math.pi / 2)))
    out.append(box(root, name + '_deck', (1.4 * s, 0.9 * s, 0.05 * s), P(0, 0, 0.12 * s), rot=(0, 0, ang), m=Mt['plank'], bev=0.01))
    wall = rr.choice((R['parede_az'], R['parede_am'], R['parede_vd']))
    wh = 0.42 * s
    out.append(box(root, name + '_casa', (0.85 * s, 0.62 * s, wh), P(0.12 * s, 0.03 * s, 0.15 * s + wh / 2), rot=(0, 0, ang), m=wall, bev=0.02))
    out.append(box(root, name + '_porta', (0.18 * s, 0.03 * s, 0.28 * s), P(0.0, -0.29 * s, 0.15 * s + 0.14 * s), rot=(0, 0, ang), m=Mt['bark_d'], bev=0.01))
    out.append(box(root, name + '_janela', (0.16 * s, 0.03 * s, 0.12 * s), P(0.32 * s, -0.29 * s, 0.15 * s + 0.26 * s), rot=(0, 0, ang), m=Mt['white'], bev=0.01))
    bm = bmesh.new()
    rz = 0.15 * s + wh
    ridge = [bm.verts.new(P(x, 0.03 * s, rz + 0.3 * s)) for x in (-0.38 * s, 0.62 * s)]
    for sy in (-1, 1):
        eave = [bm.verts.new(P(x, 0.03 * s + sy * 0.46 * s, rz - 0.03 * s)) for x in (-0.4 * s, 0.64 * s)]
        bm.faces.new((ridge[0], ridge[1], eave[1], eave[0]) if sy < 0 else (ridge[1], ridge[0], eave[0], eave[1]))
    roof = bm_to_obj(bm, name + '_telhado', root, [R['faixa_verm'] if wall is R['parede_am'] else Mt['straw']], angle=89)
    roof.modifiers.new('Espessura', 'SOLIDIFY').thickness = 0.05 * s
    out.append(roof)
    return out


def river_boat(root, name, Mt, R, loc, s, ang, rr):
    """Barco de recreio: casco branco com faixa, dois conveses cheios de redes coloridas e teto verde-agua."""
    out = []
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (loc[0] + x * ca - y * sa, loc[1] + x * sa + y * ca, loc[2] + z)
    L, B = 2.2 * s, 0.62 * s
    hull = lathe(root, name + '_casco', [(0, 0.0, 0.0), (0.06, 0.6, 0.55), (0.25, 1.0, 1.0), (0.8, 1.0, 1.0), (1.0, 0.25, 0.4)], R['casco'], segs=16, lv=1)
    # perfil ao longo do Z local: girado em Y vira o comprimento; a escala e (altura, meia boca, comprimento)
    hull.rotation_euler = (0, math.pi / 2, ang)
    hull.scale = (0.14 * s, B * 0.5, L)
    hull.location = P(-L * 0.5, 0, 0.06 * s)
    out.append(hull)
    out.append(box(root, name + '_faixa', (L * 0.8, B * 1.01, 0.05 * s), P(0.02 * L, 0, 0.16 * s), rot=(0, 0, ang), m=R['faixa_azul'], bev=0.01))
    z = 0.2 * s
    for lvl in range(2):
        Lk = L * (0.72 if lvl == 0 else 0.55)
        x0 = -L * 0.08 - lvl * 0.06 * L
        out.append(box(root, f'{name}_piso{lvl}', (Lk, B * 0.94, 0.04 * s), P(x0, 0, z), rot=(0, 0, ang), m=R['casco'], bev=0.01))
        hgt = 0.34 * s
        for i in range(5):
            xx = x0 - Lk / 2 + Lk * i / 4
            for sy in (-1, 1):
                out.append(cyl(root, f'{name}_pilar{lvl}{i}{sy}', 0.018 * s, hgt, P(xx, sy * B * 0.44, z + hgt / 2), m=R['casco'], v=6, bev=0.0))
        for i in range(4):
            xx = x0 - Lk / 2 + Lk * (i + 0.5) / 4
            out.append(sphere(root, f'{name}_rede{lvl}{i}', 0.09 * s, P(xx, rr.uniform(-0.1, 0.1) * B, z + hgt * 0.55), scale=(1.4, 0.55, 0.45),
                              m=(R['rede1'], R['rede2'], R['rede3'])[(i + lvl) % 3], seg=10, rot=(0, 0, ang)))
        out.append(box(root, f'{name}_teto{lvl}', (Lk * 1.04, B * 1.02, 0.04 * s), P(x0, 0, z + hgt + 0.02 * s), rot=(0, 0, ang),
                       m=R['teto'] if lvl else R['casco'], bev=0.01))
        out.append(box(root, f'{name}_aba{lvl}', (Lk * 1.04, B * 1.03, 0.025 * s), P(x0, 0, z + hgt - 0.01 * s), rot=(0, 0, ang), m=R['faixa_verm'], bev=0.005))
        z += hgt + 0.04 * s
    return out


def aninga(lote, R, loc, s, rr):
    """Aninga: touceira de talos altos com folha em ponta de flecha (beira de rio e baixada alagada)."""
    for k in range(rr.randrange(5, 9)):
        a = rr.uniform(0, TAU)
        d = s * rr.uniform(0, 0.15)
        h = s * rr.uniform(0.45, 0.8)
        x, y = loc[0] + d * math.cos(a), loc[1] + d * math.sin(a)
        tip = (x + math.cos(a) * 0.05 * s, y + math.sin(a) * 0.05 * s, loc[2] + h)
        lote.blade(R['aninga'], (x, y, loc[2] - 0.05), tip, 0.014 * s, segs=4)
        lote.pebble(R['aninga'], (tip[0] + math.cos(a) * 0.05 * s, tip[1] + math.sin(a) * 0.05 * s, tip[2]), 0.075 * s, squash=0.12, rot=a, rr=rr, sub=1, rough=0.1)


def floating_grass(lote, R, loc, r, rr):
    """Canarana: tapete de capim boiando."""
    for k in range(rr.randrange(5, 9)):
        a = rr.uniform(0, TAU)
        d = r * math.sqrt(rr.random())
        lote.pebble(R['canarana'], (loc[0] + d * math.cos(a), loc[1] + d * math.sin(a) * 0.8, loc[2]), r * rr.uniform(0.3, 0.5), squash=0.18, rot=a, rr=rr, sub=2, rough=0.25)
