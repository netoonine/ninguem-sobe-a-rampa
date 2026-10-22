"""Inimigos de "Guardioes da Mata": bichos e folclore da Amazonia possuidos pela Fumaca Negra das queimadas.
Possessao: olhos e rachaduras em brasa laranja e fiapos de fumaca escura (nada de roxo). Estilo argila suave.
Mesma familia e modos dos inimigos anteriores (arte/render/inimigos; r/u/d andando, a ataque, x morte), com as
mesmas chaves de tipo do jogo (raider, jackal...), para o motor e o balanceamento continuarem iguais.

uso: /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/inimigos_mata.py -- render arte/render/inimigos [tipos]
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib
import inimigos as K
import inimigos_bichos as B

FAM = K.FAM
WALK_N, ATK_N, DIE_N = K.WALK_N, K.ATK_N, K.DIE_N
VIEWS = K.VIEWS
creature, set_body, limb, smooth01, alpha_mat = B.creature, B.set_body, B.limb, B.smooth01, B.alpha_mat


def pal():
    P = B.pal()
    for k, hx, kw in [
        ('m_ant', '#b8603e', {}), ('m_ant_d', '#5e4036', {}), ('m_ant_q', '#8e5444', {}), ('m_leaf', '#7cbc5c', {}),
        ('m_pig', '#6f5a50', {'bump': 0.35}), ('m_pig_l', '#efe4d2', {}), ('m_snout', '#d99e8a', {}),
        ('m_jag', '#e2a24e', {}), ('m_jag_spot', '#5e3e2a', {}), ('m_belly', '#f1e2c2', {}),
        ('m_antler', '#e8dcc6', {}), ('m_tatu', '#bda084', {}), ('m_tatu_d', '#987a60', {}), ('m_tatu_skin', '#d8aa8e', {}),
        ('m_croc', '#8b9a5c', {}), ('m_croc_d', '#6d7a44', {}), ('m_stone', '#a8a398', {'bump': 0.4}), ('m_croc_belly', '#e7d9ae', {}),
        ('m_shell', '#6f6a48', {}), ('m_shell_l', '#a8a06c', {}), ('m_turtle', '#8a8d58', {}), ('m_yellow', '#f2c84a', {}),
        ('m_teeth', '#f6f0e2', {}), ('m_dark', '#3b2c28', {}),
    ]:
        P[k] = mat('mata_' + k, hx, rough=kw.get('rough', 0.72), var=0.04, bump=kw.get('bump', 0.1), sheen=0.15)
    P['m_ember'] = mat('mata_brasa', '#ff8a3a', rough=0.5, var=0.0, bump=0.0, emit=4.0)
    P['m_ember_d'] = mat('mata_brasa_funda', '#ff7a2a', rough=0.5, var=0.0, bump=0.0, emit=3.5)
    P['m_smoke'] = alpha_mat('mata_fumaca', '#3a3433', 0.62, emit=0.0)
    P['m_ghost'] = alpha_mat('mata_fantasma', '#eef1f2', 0.82, emit=0.25)
    return P


# ---------------------------------------------------------------- possessao: olhos em brasa, rachaduras e fumaca
def ember_eyes(root, P, parent, tag, c, r, sep, squint=0.75):
    out = []
    for k, s in enumerate((-1, 1)):
        e = blob(root, f'{tag}_olhoBrasa{k}', r, (c[0], c[1] + s * sep, c[2]), (0.55, 0.9, squint), P['m_ember'])
        e.parent = parent
        out.append(e)
    return out


def cracks(root, P, parent, tag, paths, r=0.008):
    for i, pts in enumerate(paths):
        t = tube(root, f'{tag}_racha{i}', pts, r, P['m_ember_d'], segs=5, rfun=lambda u: r * (1 - 0.6 * abs(u - 0.5) * 2) + 0.0015)
        t.parent = parent


def smoke_wisps(root, P, parent, tag, n, base, spread=0.05, size=0.035):
    # a fumaca agora e desenhada no jogo (js/vfx.js, particulas macias); o modelo so leva brasas
    return []
    ws = []
    for i in range(n):
        o = blob(root, f'{tag}_fumaca{i}', size, base, (1.0, 1.0, 1.25), P['m_smoke'])
        o.parent = parent
        ws.append((o, Vector(base), i, spread, size))
    return ws


def pose_smoke(ws, ph):
    n = max(1, len(ws))
    for o, base, i, spread, size in ws:
        t = (ph + i / n) % 1.0
        a = TAU * (i / n) + t * 2.0
        o.location = base + Vector((math.cos(a) * spread * (0.4 + t), math.sin(a) * spread * (0.4 + t), 0.16 * t))
        k = math.sin(math.pi * t) * (0.7 + 0.6 * t)
        o.scale = (k, k, k * 1.25)


# ---------------------------------------------------------------- QUADRUPEDES (queixada, onca, anhanga, tatu)
def build_quad(P, root, cfg):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'legs': {}, 'cfg': cfg}

    def p(o):
        o.parent = body
        return o
    bz = cfg['bz']
    fur, belly = cfg['fur'], cfg['belly']
    p(blob(root, tag + '_tronco', cfg['br'], (0, 0, bz), cfg['bs'], fur))
    p(blob(root, tag + '_barriga', cfg['br'] * 0.8, (0.0, 0, bz - cfg['br'] * 0.35), (cfg['bs'][0] * 0.85, cfg['bs'][1] * 0.8, 0.5), belly))
    if cfg.get('mane'):
        p(blob(root, tag + '_crina', cfg['br'] * 0.62, (0.02, 0, bz + cfg['br'] * 0.62), (cfg['bs'][0] * 0.9, 0.42, 0.42), cfg['mane']))
    if cfg.get('collar'):
        p(torus(root, tag + '_colar', (cfg['br'] * 1.05, 0, bz + 0.01), cfg['br'] * 0.62, cfg['br'] * 0.2, cfg['collar'], n=18, segs=6)).rotation_euler = (0, 1.2, 0)
    if cfg.get('bands'):
        for j in range(cfg['bands']):
            x = -cfg['br'] * cfg['bs'][0] * 0.65 + j * cfg['br'] * cfg['bs'][0] * 1.3 / max(1, cfg['bands'] - 1)
            rr = cfg['br'] * cfg['bs'][1] * (1.0 - 0.25 * abs(x) / (cfg['br'] * cfg['bs'][0]))
            ring = p(torus(root, f'{tag}_banda{j}', (x, 0, bz + 0.005), rr, 0.016, cfg['band_m'], n=22, segs=6))
            ring.rotation_euler = (0, math.pi / 2, 0)
            ring.scale = (1.0, 1.0, cfg['bs'][2] / cfg['bs'][1] * 1.02)
    if cfg.get('spots'):
        rng = __import__('random').Random(7)
        for j in range(cfg['spots']):
            a = rng.uniform(0.3, math.pi - 0.3) * (1 if j % 2 else -1)
            x = rng.uniform(-0.8, 0.8) * cfg['br'] * cfg['bs'][0]
            y = math.cos(a) * cfg['br'] * cfg['bs'][1] * 0.98
            z = bz + abs(math.sin(a)) * cfg['br'] * cfg['bs'][2] * 0.98
            sp = p(torus(root, f'{tag}_roseta{j}', (x, y, z), 0.014, 0.0055, cfg['spot_m'], n=12, segs=4))
            sp.rotation_euler = (math.atan2(y, z - bz), 0, 0)
            sp.scale = (1.0, 1.0, 0.35)
            dot = p(blob(root, f'{tag}_pinta{j}', 0.006, (x, y * 1.01, z), (1.0, 0.4, 1.0), cfg['spot_m']))
            dot.rotation_euler = (math.atan2(y, z - bz), 0, 0)
    head = empty(root, tag + '_cabecaPivo', loc=cfg['head'], parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    hr = cfg['hr']
    ph(blob(root, tag + '_cabeca', hr, (0, 0, 0), cfg.get('hs', (1.1, 0.95, 0.9)), fur))
    sn = cfg['snout']
    ph(tube(root, tag + '_focinho', [(hr * 0.5, 0, -hr * 0.2), (hr * 0.5 + sn, 0, -hr * 0.35)], hr * 0.55, cfg.get('snout_m', belly), segs=10,
            rfun=lambda t: hr * 0.58 * (1 - 0.45 * t)))
    ph(blob(root, tag + '_nariz', hr * 0.22, (hr * 0.5 + sn + 0.004, 0, -hr * 0.36), (0.6, 1.0, 0.8), cfg.get('nose_m', P['m_dark'])))
    ember_eyes(root, P, head, tag, (hr * 0.72, 0, hr * 0.22), hr * 0.2, hr * 0.42)
    et = cfg['ears']
    for k, s in enumerate((-1, 1)):
        if et == 'round':
            ph(blob(root, f'{tag}_orelha{k}', hr * 0.32, (-hr * 0.15, s * hr * 0.6, hr * 0.7), (0.5, 1.0, 1.0), fur))
        elif et == 'small':
            ear = lathe(root, f'{tag}_orelha{k}', [(0.0, hr * 0.3, hr * 0.16), (hr * 0.4, hr * 0.18, hr * 0.1), (hr * 0.62, 0.0, 0.0)], fur, segs=8, lv=1)
            ph(ear).location = (-hr * 0.2, s * hr * 0.55, hr * 0.55)
            ear.rotation_euler = (s * 0.6, -0.4, 0)
        elif et in ('deer', 'tube'):
            ear = lathe(root, f'{tag}_orelha{k}', [(0.0, hr * 0.26, hr * 0.12), (hr * 0.6, hr * 0.2, hr * 0.1), (hr * 0.95, 0.0, 0.0)], fur, segs=8, lv=1)
            ph(ear).location = (-hr * 0.2, s * hr * 0.55, hr * 0.5)
            ear.rotation_euler = (s * 1.0, -0.5 if et == 'deer' else -0.9, 0)
    if cfg.get('antlers'):
        for k, s in enumerate((-1, 1)):
            base = Vector((-hr * 0.05, s * hr * 0.35, hr * 0.8))
            main = [base, base + Vector((-0.02, s * 0.04, 0.08)), base + Vector((-0.05, s * 0.09, 0.15)), base + Vector((-0.07, s * 0.1, 0.22))]
            ph(tube(root, f'{tag}_galho{k}', main, 0.012, cfg['antlers'], segs=6, rfun=lambda t: 0.013 * (1 - 0.6 * t)))
            for j, u in enumerate((0.35, 0.65)):
                q = main[0].lerp(main[-1], u)
                ph(tube(root, f'{tag}_galho{k}{j}', [q, q + Vector((0.035, s * 0.02, 0.05))], 0.009, cfg['antlers'], segs=5, rfun=lambda t: 0.009 * (1 - 0.6 * t)))
    if cfg.get('tusks'):
        for k, s in enumerate((-1, 1)):
            ph(tube(root, f'{tag}_presa{k}', [(hr * 0.5 + sn * 0.6, s * hr * 0.3, -hr * 0.5), (hr * 0.5 + sn * 0.7, s * hr * 0.36, -hr * 0.25)], hr * 0.07, P['m_teeth'], segs=5,
                    rfun=lambda t: hr * 0.08 * (1 - 0.7 * t)))
    # rachaduras em brasa no corpo
    br, bs = cfg['br'], cfg['bs']
    cracks(root, P, body, tag, [
        [(-br * bs[0] * 0.3, br * bs[1] * 0.75, bz + br * bs[2] * 0.4), (-br * bs[0] * 0.1, br * bs[1] * 0.85, bz + br * bs[2] * 0.2),
         (br * bs[0] * 0.05, br * bs[1] * 0.8, bz + br * bs[2] * 0.42), (br * bs[0] * 0.25, br * bs[1] * 0.72, bz + br * bs[2] * 0.3)],
        [(-br * bs[0] * 0.45, -br * bs[1] * 0.7, bz + br * bs[2] * 0.35), (-br * bs[0] * 0.2, -br * bs[1] * 0.82, bz + br * bs[2] * 0.15),
         (0.0, -br * bs[1] * 0.78, bz + br * bs[2] * 0.4)]])
    parts['smoke'] = smoke_wisps(root, P, body, tag, 3, (-br * bs[0] * 0.2, 0, bz + br * bs[2] * 0.9), spread=0.04, size=br * 0.38)
    # cauda
    parts['tail'] = limb(root, body, tag + '_cauda', cfg.get('tail_m', fur))
    if cfg.get('tail_tip'):
        parts['tailtip'] = p(blob(root, tag + '_caudaPonta', cfg['tail_r'] * 1.3, (0, 0, 0), (1.3, 1.0, 1.0), cfg['tail_tip']))
    for k in cfg['legs']:
        parts['legs'][k] = (limb(root, body, f'{tag}_perna{k}a', fur), limb(root, body, f'{tag}_perna{k}b', cfg.get('leg_low', fur)),
                            p(blob(root, f'{tag}_pata{k}', cfg['leg_r'] * 0.9, (0, 0, 0), (1.4, 1.0, 0.7), cfg.get('paw', P['m_dark']))))
    return parts


def pose_quad(parts, mode, f, view):
    cfg = parts['cfg']
    face = VIEWS[view]
    ph = f / WALK_N
    a = TAU * ph
    roll = pitch = 0.0
    off = (0, 0, cfg.get('bob', 0.012) * math.cos(2 * a) + cfg.get('float', 0.0))
    stride, lift = cfg.get('stride', 0.07), cfg.get('lift', 0.05)
    feet = {}
    for k, (x, y, z, o) in cfg['legs'].items():
        b = a + o
        feet[k] = Vector((x + stride * math.cos(b), y, 0.02 + lift * max(0.0, -math.sin(b))))
    head_p = cfg.get('head_bob', 0.06) * math.sin(2 * a)
    tail_s = 0.05 * math.sin(a)
    if mode == 'atk':
        t = f / (ATK_N - 1)
        lunge = math.sin(math.pi * t)
        off = (0.04 * lunge, 0, off[2])
        pitch = 0.18 * lunge
        head_p = 0.35 * lunge
        for k, (x, y, z, o) in cfg['legs'].items():
            feet[k] = Vector((x + (0.05 if k[0] == 'F' else -0.03) * lunge, y, 0.02))
    elif mode == 'die':
        t = f / (DIE_N - 1)
        e = smooth01(t)
        if cfg.get('ghost'):
            set_body(parts, face, (0, 0, 0.05 + 0.12 * t), scale=1.0 - 0.75 * e)
        roll = 1.45 * e if not cfg.get('ghost') else 0.0
        off = (0, -0.05 * e, off[2] if cfg.get('ghost') else 0.0)
        for k, (x, y, z, o) in cfg['legs'].items():
            feet[k] = Vector((x + 0.03 * e, y + (0.05 if y > 0 else 0.0) * e, 0.02 + 0.05 * e))
        head_p = -0.2 * e
    if not (mode == 'die' and cfg.get('ghost')):
        set_body(parts, face, off, roll=roll, pitch=pitch)
    parts['head'].rotation_euler = (0, head_p, 0)
    l1, l2 = cfg['l1'], cfg['l2']
    for k, (x, y, z, o) in cfg['legs'].items():
        A0 = Vector((x, y, z))
        Kn, F2 = two_bone(A0, feet[k], l1, l2, (-1.0, 0.0, 0.25))
        up, lo, paw = parts['legs'][k]
        set_mesh_tube(up, [A0, A0.lerp(Kn, 0.5), Kn], cfg['leg_r'] * 1.25, segs=8, rfun=lambda t: cfg['leg_r'] * (1.35 - 0.35 * t))
        set_mesh_tube(lo, [Kn, Kn.lerp(F2, 0.5), F2], cfg['leg_r'], segs=8)
        paw.location = F2 + Vector((0.01, 0, -0.006))
    tb = Vector(cfg['tail'][0])
    tp = [tb] + [Vector(q) + Vector((0, tail_s * j / len(cfg['tail']), 0)) for j, q in enumerate(cfg['tail'][1:], 1)]
    set_mesh_tube(parts['tail'], tp, cfg['tail_r'], segs=8, rfun=lambda t: cfg['tail_r'] * cfg.get('tail_taper', 1.0) ** t)
    if parts.get('tailtip'):
        parts['tailtip'].location = tp[-1]
    pose_smoke(parts['smoke'], ph)


QUAD = {
    # Queixada: porco-do-mato atarracado, pelo escuro eriçado, faixa clara no pescoco, presas
    'jackal': dict(bz=0.15, br=0.088, bs=(1.5, 1.0, 0.95), head=(0.16, 0, 0.165), hr=0.068, hs=(1.25, 0.95, 1.0), snout=0.055, ears='small',
                   l1=0.065, l2=0.06, leg_r=0.016, stride=0.065, lift=0.045, tusks=True,
                   legs={'FL': (0.08, 0.04, 0.12, 0.0), 'FR': (0.08, -0.04, 0.12, math.pi), 'BL': (-0.08, 0.045, 0.12, math.pi), 'BR': (-0.08, -0.045, 0.12, 0.0)},
                   tail=[(-0.13, 0, 0.18), (-0.16, 0, 0.17), (-0.18, 0, 0.14)], tail_r=0.01),
    # Onca-pintada: dourada com rosetas, cauda longa, passos amplos
    'brute': dict(bz=0.2, br=0.095, bs=(1.8, 1.0, 0.9), head=(0.21, 0, 0.26), hr=0.078, hs=(1.05, 1.08, 0.95), snout=0.032, ears='round',
                  l1=0.085, l2=0.08, leg_r=0.027, stride=0.085, lift=0.055, spots=26,
                  legs={'FL': (0.11, 0.045, 0.16, 0.0), 'FR': (0.11, -0.045, 0.16, math.pi), 'BL': (-0.11, 0.05, 0.17, math.pi), 'BR': (-0.11, -0.05, 0.17, 0.0)},
                  tail=[(-0.16, 0, 0.24), (-0.25, 0, 0.27), (-0.33, 0, 0.22), (-0.37, 0, 0.15)], tail_r=0.014, tail_taper=0.7),
    # Anhanga: veado-fantasma branco translucido, galhada, flutua um pouco
    'specter': dict(bz=0.22, br=0.07, bs=(1.6, 0.85, 0.85), head=(0.15, 0, 0.36), hr=0.05, hs=(1.2, 0.85, 0.9), snout=0.045, ears='deer',
                    l1=0.1, l2=0.1, leg_r=0.013, stride=0.08, lift=0.06, float=0.03, ghost=True,
                    legs={'FL': (0.09, 0.035, 0.19, 0.0), 'FR': (0.09, -0.035, 0.19, math.pi), 'BL': (-0.09, 0.04, 0.2, math.pi), 'BR': (-0.09, -0.04, 0.2, 0.0)},
                    tail=[(-0.11, 0, 0.27), (-0.14, 0, 0.29), (-0.15, 0, 0.27)], tail_r=0.014),
    # Tatu: carapaca em faixas, focinho comprido, orelhas tubulares
    'beetle': dict(bz=0.1, br=0.08, bs=(1.45, 1.0, 0.85), head=(0.13, 0, 0.09), hr=0.042, hs=(1.2, 0.9, 0.9), snout=0.06, ears='tube',
                   l1=0.045, l2=0.045, leg_r=0.016, stride=0.05, lift=0.03, bands=6, bob=0.006,
                   legs={'FL': (0.07, 0.055, 0.07, 0.0), 'FR': (0.07, -0.055, 0.07, math.pi), 'BL': (-0.07, 0.06, 0.07, math.pi), 'BR': (-0.07, -0.06, 0.07, 0.0)},
                   tail=[(-0.12, 0, 0.09), (-0.17, 0, 0.06), (-0.2, 0, 0.03)], tail_r=0.016, tail_taper=0.4),
}


def quad_builder(key):
    def build(P, root):
        cfg = dict(QUAD[key])
        if key == 'jackal':
            cfg.update(fur=P['m_pig'], belly=P['m_pig'], mane=P['m_pig'], collar=P['m_pig_l'], snout_m=P['m_snout'], paw=P['m_dark'])
        elif key == 'brute':
            cfg.update(fur=P['m_jag'], belly=P['m_belly'], spot_m=P['m_jag_spot'], snout_m=P['m_belly'], paw=P['m_belly'], tail_tip=P['m_jag_spot'])
        elif key == 'specter':
            cfg.update(fur=P['m_ghost'], belly=P['m_ghost'], antlers=P['m_antler'], snout_m=P['m_ghost'], nose_m=P['m_ghost'], paw=P['m_ghost'])
        elif key == 'beetle':
            cfg.update(fur=P['m_tatu'], belly=P['m_tatu_skin'], band_m=P['m_tatu_d'], snout_m=P['m_tatu_skin'], nose_m=P['m_tatu_skin'],
                       leg_low=P['m_tatu_skin'], paw=P['m_tatu_skin'], tail_m=P['m_tatu_d'])
        return build_quad(P, root, cfg)
    return build


# ---------------------------------------------------------------- FORMIGAS (sauva, tucandeira, tucandeira-mae)
ANT_LEGS = [(0.03, 0.0), (0.0, math.pi), (-0.03, 0.0)]


def build_ant(P, root, cfg):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'legs': [], 'k': cfg['k'], 'cfg': cfg}

    def p(o):
        o.parent = body
        return o
    m = cfg['m']
    p(blob(root, tag + '_torax', 0.045, (0.02, 0, 0.1), (1.3, 0.85, 0.8), m))
    p(blob(root, tag + '_peciolo', 0.02, (-0.04, 0, 0.1), (1, 1, 1), m))
    gr = cfg.get('gaster', 0.065)
    p(blob(root, tag + '_gaster', gr, (-0.1 - (gr - 0.065), 0, 0.105), (1.35, 1.0, 0.9), m))
    head = empty(root, tag + '_cabecaPivo', loc=(0.1, 0, 0.12), parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    ph(blob(root, tag + '_cabeca', 0.05, (0, 0, 0), (1.0, 1.15, 0.9), m))
    ember_eyes(root, P, head, tag, (0.035, 0, 0.018), 0.012, 0.035)
    for k, s in enumerate((-1, 1)):
        ph(tube(root, f'{tag}_mandibula{k}', [(0.04, s * 0.025, -0.02), (0.075, s * 0.02, -0.025), (0.085, s * 0.005, -0.02)], 0.009, P['m_dark'], segs=5,
                rfun=lambda t: 0.01 * (1 - 0.6 * t)))
        ph(tube(root, f'{tag}_antena{k}', [(0.01, s * 0.025, 0.035), (0.03, s * 0.05, 0.09), (0.08, s * 0.07, 0.11), (0.11, s * 0.065, 0.09)], 0.005, m, segs=5))
    if cfg.get('leaf'):
        lf = cloth_grid(root, tag + '_folha', 1.0, 1.0, 4, 4, [P['m_leaf']], thick=0.006,
                        shape=lambda u, v, co: Vector((0.03 + 0.11 * v - 0.05, (u - 0.5) * 0.13 * math.sin(math.pi * max(0.05, v)) * 1.6, 0.05 + 0.1 * v + 0.02 * math.sin(math.pi * u))))
        lf.parent = head
        parts['leaf'] = lf
    if cfg.get('eggs'):
        for j in range(6):
            a = j * TAU / 6
            p(blob(root, f'{tag}_ovo{j}', 0.022, (-0.12 + 0.04 * math.cos(a), 0.04 * math.sin(a), 0.17 + 0.01 * (j % 2)), (1.3, 0.9, 0.9), P['m_belly']))
    cracks(root, P, body, tag, [[(-0.16, 0.05, 0.13), (-0.12, 0.06, 0.15), (-0.08, 0.055, 0.13)], [(-0.15, -0.05, 0.14), (-0.1, -0.06, 0.12)]], r=0.004)
    parts['smoke'] = smoke_wisps(root, P, body, tag, 2, (-0.1, 0, 0.18), spread=0.03, size=0.025)
    for i, (x, o) in enumerate(ANT_LEGS):
        for k, s in enumerate((-1, 1)):
            up = limb(root, body, f'{tag}_perna{i}{k}a', m)
            lo = limb(root, body, f'{tag}_perna{i}{k}b', P['m_dark'])
            parts['legs'].append((x, s, o + (math.pi if s > 0 else 0.0), up, lo))
    body.scale = (cfg['k'],) * 3
    return parts


def pose_ant(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    roll = 0.0
    off = (0, 0, 0.005 * math.cos(2 * a))
    hp = 0.05 * math.sin(2 * a)
    curl = 0.0
    if mode == 'atk':
        t = f / (ATK_N - 1)
        hp = -0.35 * math.sin(math.pi * t)
        off = (0.03 * math.sin(math.pi * t), 0, 0)
    elif mode == 'die':
        t = f / (DIE_N - 1)
        curl = smooth01(t)
        roll = 0.4 * curl
        off = (0, 0, -0.015 * curl)
    set_body(parts, face, off, roll=roll, scale=parts['k'])
    parts['head'].rotation_euler = (0, hp, 0)
    for x, s, o, up, lo in parts['legs']:
        b = a + o
        A0 = Vector((x, s * 0.03, 0.095))
        F = Vector((x + 0.035 * math.cos(b) + x * 1.5, s * (0.13 - 0.05 * curl), 0.008 + 0.025 * max(0.0, -math.sin(b)) + 0.04 * curl))
        Kn, F2 = two_bone(A0, F, 0.07, 0.08, (0.0, s * 0.4, 1.0))
        set_mesh_tube(up, [A0, A0.lerp(Kn, 0.5), Kn], 0.01, segs=6)
        set_mesh_tube(lo, [Kn, Kn.lerp(F2, 0.5), F2], 0.008, segs=6, rfun=lambda t: 0.009 - 0.005 * t)
    pose_smoke(parts['smoke'], f / WALK_N)


def ant_builder(cfg_fn):
    def build(P, root):
        return build_ant(P, root, cfg_fn(P))
    return build


# ---------------------------------------------------------------- JACARE-DE-PEDRA (corpo comprido, placas de pedra)
def build_croc(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'segs': [], 'legs': []}

    def p(o):
        o.parent = body
        return o
    for j in range(9):
        u = j / 8
        r = 0.07 * (1 - abs(u - 0.35) * 0.9) + 0.02
        sg = p(blob(root, f'{tag}_gomo{j}', r, (0, 0, 0), (1.3, 1.25, 0.7), P['m_croc'] if j % 2 else P['m_croc_d']))
        if 1 <= j <= 6:
            for k, s in enumerate((-1, 1)):
                pl = blob(root, f'{tag}_placa{j}{k}', r * 0.42, (0.0, s * r * 0.45, r * 0.6), (1.2, 0.9, 0.55), P['m_stone'])
                pl.parent = sg
        parts['segs'].append((sg, u, r))
    p(blob(root, tag + '_ventre', 0.07, (0.02, 0, 0.04), (2.6, 1.0, 0.35), P['m_croc_belly']))
    head = empty(root, tag + '_cabecaPivo', loc=(0.2, 0, 0.07), parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    ph(blob(root, tag + '_cranio', 0.05, (0, 0, 0.01), (1.2, 1.1, 0.75), P['m_croc']))
    ph(blob(root, tag + '_focinho', 0.045, (0.075, 0, -0.008), (1.9, 0.85, 0.42), P['m_croc']))
    ph(blob(root, tag + '_mandibula', 0.04, (0.07, 0, -0.03), (1.9, 0.8, 0.3), P['m_croc_belly']))
    for i in range(5):
        for k, s in enumerate((-1, 1)):
            th = blob(root, f'{tag}_dente{i}{k}', 0.008, (0.04 + i * 0.022, s * 0.034, -0.022), (0.7, 0.7, 1.3), P['m_teeth'])
            th.parent = head
    for k, s in enumerate((-1, 1)):
        ph(blob(root, f'{tag}_olhoBolsa{k}', 0.02, (0.01, s * 0.035, 0.045), (1, 1, 0.8), P['m_croc']))
    ember_eyes(root, P, head, tag, (0.02, 0, 0.055), 0.012, 0.035, squint=0.6)
    for k, (x, s) in enumerate(((0.12, 1), (0.12, -1), (-0.06, 1), (-0.06, -1))):
        up = limb(root, body, f'{tag}_perna{k}a', P['m_croc_d'])
        lo = limb(root, body, f'{tag}_perna{k}b', P['m_croc_d'])
        paw = p(blob(root, f'{tag}_pata{k}', 0.02, (0, 0, 0), (1.3, 1.3, 0.5), P['m_croc_d']))
        parts['legs'].append((x, s, (0.0 if (k in (0, 3)) else math.pi), up, lo, paw))
    cracks(root, P, body, tag, [[(0.0, 0.07, 0.07), (0.05, 0.075, 0.05), (0.1, 0.07, 0.07)], [(-0.05, -0.07, 0.06), (0.0, -0.075, 0.045)]], r=0.005)
    parts['smoke'] = smoke_wisps(root, P, body, tag, 3, (0.05, 0, 0.12), spread=0.05, size=0.03)
    return parts


def pose_croc(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    roll = 0.0
    snap = 0.0
    if mode == 'atk':
        snap = math.sin(math.pi * f / (ATK_N - 1))
    if mode == 'die':
        t = f / (DIE_N - 1)
        roll = 2.6 * smooth01(t)
    set_body(parts, face, (0, 0, 0.004 * math.cos(2 * a) + (0.06 * smooth01(f / (DIE_N - 1)) if mode == 'die' else 0)), roll=roll)
    # ondulacao lateral do corpo
    n = len(parts['segs'])
    for sg, u, r in parts['segs']:
        x = 0.16 - 0.5 * u
        y = 0.03 * math.sin(a - u * 5) * (0.4 + u)
        sg.location = (x, y, 0.06 + 0.01 * (1 - u))
        sg.rotation_euler = (0, 0, 0.3 * math.cos(a - u * 5) * u)
    parts['head'].rotation_euler = (0, -0.35 * snap, 0.08 * math.sin(a))
    for x, s, o, up, lo, paw in parts['legs']:
        b = a + o
        A0 = Vector((x, s * 0.06, 0.06))
        F = Vector((x + 0.05 * math.cos(b), s * 0.13, 0.008 + 0.03 * max(0.0, -math.sin(b))))
        if mode == 'die':
            F = Vector((x, s * 0.12, 0.08))
        Kn, F2 = two_bone(A0, F, 0.05, 0.05, (0.0, s * 1.0, 0.6))
        set_mesh_tube(up, [A0, A0.lerp(Kn, 0.5), Kn], 0.018, segs=8)
        set_mesh_tube(lo, [Kn, Kn.lerp(F2, 0.5), F2], 0.015, segs=8)
        paw.location = F2
    pose_smoke(parts['smoke'], f / WALK_N)


# ---------------------------------------------------------------- TRACAJA (casco virado para a frente)
def build_turtle(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'legs': []}

    def p(o):
        o.parent = body
        return o
    shell = lathe(root, tag + '_casco', [(0.0, 0.14, 0.12), (0.035, 0.145, 0.125), (0.08, 0.125, 0.108), (0.12, 0.08, 0.07), (0.14, 0.0, 0.0)], P['m_shell'], segs=24, lv=2)
    p(shell).location = (0, 0, 0.06)
    shell.scale = (1.2, 1.0, 1.0)
    # escudos do casco (linhas claras)
    for k, (ra, za) in enumerate(((0.105, 0.115), (0.135, 0.075))):
        p(torus(root, f'{tag}_escudoLinha{k}', (0, 0, 0.06 + za), ra, 0.006, P['m_shell_l'], n=28, segs=4)).scale = (1.2, 1.0, 0.3)
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        p(tube(root, f'{tag}_escudoRaio{i}', [(0.0, 0.0, 0.2), (math.cos(a) * 0.14, math.sin(a) * 0.12, 0.16)], 0.005, P['m_shell_l'], segs=4))
    p(blob(root, tag + '_plastrao', 0.13, (0, 0, 0.06), (1.25, 1.0, 0.18), P['m_croc_belly']))
    head = empty(root, tag + '_cabecaPivo', loc=(0.17, 0, 0.1), parent=body)
    parts['head'] = head
    hb = blob(root, tag + '_cabeca', 0.042, (0.02, 0, 0), (1.25, 1.0, 0.9), P['m_turtle'])
    hb.parent = head
    for k, (x, y, z) in enumerate(((0.02, 0.03, 0.025), (0.03, -0.03, 0.025), (0.0, 0.0, 0.04))):
        sp = blob(root, f'{tag}_pinta{k}', 0.012, (x, y, z), (1.2, 1.0, 0.4), P['m_yellow'])
        sp.parent = head
    ember_eyes(root, P, head, tag, (0.05, 0, 0.012), 0.009, 0.026)
    neck = limb(root, body, tag + '_pescoco', P['m_turtle'])
    parts['neck'] = neck
    for k, (x, s) in enumerate(((0.1, 1), (0.1, -1), (-0.09, 1), (-0.09, -1))):
        leg = p(blob(root, f'{tag}_nadadeira{k}', 0.035, (0, 0, 0), (1.5, 0.8, 0.5), P['m_turtle']))
        parts['legs'].append((x, s, (0.0 if k in (0, 3) else math.pi), leg))
    cracks(root, P, body, tag, [[(-0.05, 0.1, 0.12), (0.0, 0.11, 0.1), (0.04, 0.105, 0.12)], [(-0.02, -0.11, 0.11), (0.03, -0.1, 0.13)]], r=0.006)
    parts['smoke'] = smoke_wisps(root, P, body, tag, 3, (-0.02, 0, 0.22), spread=0.05, size=0.032)
    return parts


def pose_turtle(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    roll = 0.0
    sink = 0.0
    hide = 0.0
    if mode == 'atk':
        hide = -math.sin(math.pi * f / (ATK_N - 1))   # bote para a frente
    if mode == 'die':
        t = f / (DIE_N - 1)
        sink = smooth01(t)
        roll = 0.5 * sink
    set_body(parts, face, (0, 0, 0.006 * abs(math.sin(a)) - 0.03 * sink), roll=roll, yaw=0.05 * math.sin(a))
    hp = Vector((0.17 - 0.04 * hide + 0.01 * math.sin(2 * a), 0, 0.1 - 0.04 * sink))
    parts['head'].location = hp
    set_mesh_tube(parts['neck'], [Vector((0.11, 0, 0.09)), hp.lerp(Vector((0.11, 0, 0.09)), 0.5), hp], 0.026, segs=8)
    for x, s, o, leg in parts['legs']:
        b = a + o
        leg.location = (x + 0.035 * math.cos(b), s * 0.12, 0.035 + 0.02 * max(0.0, -math.sin(b)) - 0.02 * sink)
        leg.rotation_euler = (0, 0, s * 0.4 + 0.3 * math.sin(b))
    pose_smoke(parts['smoke'], f / WALK_N)


# ---------------------------------------------------------------- MORCEGO-VAMPIRO (voa)
def bat_wing(side):
    def fn(u, v, co):
        # membrana com borda de fuga recortada (dedos)
        x = 0.04 - v * (0.13 - 0.05 * u) - 0.02 * u + 0.025 * v * math.sin(u * math.pi * 3) * u
        return Vector((x, side * u * 0.26, 0.02 * math.sin(math.pi * u) * (1 - v)))
    return fn


def build_bat(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'wings': []}

    def p(o):
        o.parent = body
        return o
    fur, mem = P['m_dark'], mat('mata_membrana', '#6e5650', rough=0.6, var=0.03, bump=0.08, sheen=0.2)
    p(blob(root, tag + '_tronco', 0.06, (0, 0, 0), (1.15, 0.9, 1.0), mat('mata_morcego', '#5e4a44', rough=0.8, var=0.04, bump=0.3)))
    p(blob(root, tag + '_peito', 0.045, (0.03, 0, -0.01), (0.9, 0.8, 0.9), mat('mata_morcego_peito', '#8a6e62', rough=0.85, var=0.03, bump=0.3)))
    head = empty(root, tag + '_cabecaPivo', loc=(0.06, 0, 0.045), parent=body)
    parts['head'] = head
    hb = blob(root, tag + '_cabeca', 0.045, (0, 0, 0), (1.0, 1.05, 0.95), mat('mata_morcego', '#5e4a44'))
    hb.parent = head
    for k, s in enumerate((-1, 1)):
        ear = lathe(root, f'{tag}_orelha{k}', [(0.0, 0.02, 0.012), (0.04, 0.016, 0.009), (0.07, 0.0, 0.0)], mem, segs=8, lv=1)
        ear.parent = head
        ear.location = (-0.005, s * 0.025, 0.03)
        ear.rotation_euler = (s * 0.45, -0.2, 0)
        fang = blob(root, f'{tag}_presa{k}', 0.006, (0.042, s * 0.01, -0.026), (0.7, 0.7, 1.6), P['m_teeth'])
        fang.parent = head
    sn = blob(root, tag + '_focinho', 0.016, (0.042, 0, -0.008), (0.8, 1.0, 0.8), mem)
    sn.parent = head
    ember_eyes(root, P, head, tag, (0.038, 0, 0.012), 0.01, 0.019)
    for k, s in enumerate((-1, 1)):
        piv = empty(root, f'{tag}_asaPivo{k}', loc=(0.0, s * 0.045, 0.02), parent=body)
        w = cloth_grid(root, f'{tag}_asa{k}', 1.0, 1.0, 6, 4, [mem], thick=0.01, shape=bat_wing(s))
        w.parent = piv
        for j in range(3):
            fx = 0.03 - 0.045 * j
            bone = tube(root, f'{tag}_dedo{k}{j}', [(0.035, s * 0.02, 0.0), (fx, s * (0.26 - 0.03 * j), 0.0)], 0.0045, fur, segs=4)
            bone.parent = piv
        parts['wings'].append((s, piv))
    cracks(root, P, body, tag, [[(-0.03, 0.04, 0.03), (0.0, 0.05, 0.01), (0.03, 0.04, 0.03)]], r=0.006)
    return parts


def pose_bat(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    flap = 0.95 * math.sin(a * 2)
    off = (0, 0, -0.02 * math.sin(a * 2))
    pitch = 0.1 * math.cos(a * 2)
    roll = 0.0
    if mode == 'die':
        t = f / (DIE_N - 1)
        flap = 1.2 * smooth01(t)
        pitch = 1.4 * smooth01(t)
        roll = 0.7 * smooth01(t)
        off = (0, 0, 0)
    set_body(parts, face, off, roll=roll, pitch=pitch, scale=1.2)
    for s, piv in parts['wings']:
        piv.rotation_euler = (s * flap, 0, 0)


# ---------------------------------------------------------------- BOIUNA, A COBRA GRANDE (chefe; sai de um poco de agua barrenta)
def build_boiuna(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'dashes': []}

    def p(o):
        o.parent = body
        return o
    water = mat('mata_agua_barrenta', '#5f8a7a', rough=0.15, var=0.02, bump=0.05)
    p(lathe(root, tag + '_poco', [(0.0, 0.3, 0.26), (0.012, 0.28, 0.24), (0.02, 0.2, 0.17), (0.022, 0.0, 0.0)], water, segs=28, lv=2))
    p(lathe(root, tag + '_margem', [(0.0, 0.33, 0.29), (0.03, 0.3, 0.26), (0.05, 0.26, 0.22)], P['m_croc_d'], segs=28,
            wobble=lambda a, z: 0.015 * math.sin(7 * a), lv=2, caps=False, solid=0.02))
    skin, belly = mat('mata_boiuna', '#46523e', rough=0.4, var=0.04, bump=0.1, sheen=0.2), mat('mata_boiuna_ventre', '#c9bf92', rough=0.5, var=0.03, bump=0.06)
    # corpo continuo (tubo refeito a cada pose) e ventre claro na frente
    parts['tube'] = limb(root, body, tag + '_tronco', skin)
    parts['belly'] = limb(root, body, tag + '_ventre', belly)
    for k in range(7):
        d = blob(root, f'{tag}_risco{k}', 0.02, (0, 0, 0), (0.7, 0.45, 1.6), P['m_ember_d'])
        d.parent = body
        parts['dashes'].append((d, 0.12 + 0.12 * k, -1 if k % 2 else 1))
    head = empty(root, tag + '_cabeca', parent=body)
    parts['head'] = head
    hb = blob(root, tag + '_cranio', 0.1, (0.04, 0, 0), (1.5, 1.05, 0.7), skin)
    hb.parent = head
    jaw = blob(root, tag + '_queixo', 0.085, (0.05, 0, -0.04), (1.4, 0.95, 0.4), belly)
    jaw.parent = head
    ember_eyes(root, P, head, tag, (0.07, 0, 0.045), 0.024, 0.06, squint=0.7)
    tongue = tube(root, tag + '_lingua', [(0.18, 0, -0.03), (0.24, 0, -0.035), (0.27, 0.015, -0.03)], 0.007, P['m_snout'], segs=4)
    tongue.parent = head
    parts['tongue'] = tongue
    return parts


def pose_boiuna(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    arch = math.sin(math.pi * f / (ATK_N - 1)) if mode == 'atk' else 0.0
    sink = smooth01(f / (DIE_N - 1)) if mode == 'die' else 0.0
    set_body(parts, face)
    n = 16
    pts = []
    for j in range(n + 1):
        u = j / n
        h = 0.66 * math.sin(math.pi * 0.5 * u) * (1 - 0.55 * arch * u) * (1 - sink)
        x = 0.14 * u + 0.05 * math.sin(a - u * 4) * u + 0.3 * arch * u * u
        y = 0.045 * math.sin(a - u * 3) * u
        pts.append(Vector((x, y, h - 0.05 + 0.02 * (1 - sink) - 0.12 * sink * u)))
    rad = lambda t: 0.108 - 0.03 * t
    set_mesh_tube(parts['tube'], pts, 0.1, segs=14, rfun=rad)
    set_mesh_tube(parts['belly'], [q + Vector((0.035, 0, 0)) for q in pts[:-1]], 0.08, segs=12, rfun=lambda t: 0.08 - 0.025 * t)
    for d, u, side in parts['dashes']:
        k = u * n
        j0 = min(n - 1, int(k))
        q = pts[j0].lerp(pts[j0 + 1], k - j0)
        r = rad(u) * 0.97
        d.location = q + Vector((-0.25 * r, side * 0.0 - 0.95 * r, 0.0))
        d.hide_render = q.z < -0.01
    d = (pts[-1] - pts[-2]).normalized()
    hd = (d + Vector((0.8 + 0.5 * arch, 0, -0.5 - 0.7 * arch))).normalized()
    parts['head'].location = pts[-1] + hd * 0.03
    parts['head'].rotation_euler = hd.to_track_quat('X', 'Z').to_euler()
    parts['tongue'].hide_render = (f % 3) != 0 and mode == 'walk'


# ---------------------------------------------------------------- BOITATA, A COBRA DE FOGO (chefe final, voa)
def build_boitata(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'flames': []}

    def p(o):
        o.parent = body
        return o
    coal = mat('mata_carvao', '#3a2a28', rough=0.6, var=0.05, bump=0.2)
    glowb = mat('mata_ventre_brasa', '#ff8a3a', rough=0.5, var=0.0, bump=0.0, emit=1.4)
    flame = mat('mata_chama', '#ff6a1e', rough=0.5, var=0.0, bump=0.0, emit=1.6)
    parts['tube'] = limb(root, body, tag + '_tronco', coal)
    parts['belly'] = limb(root, body, tag + '_ventre', glowb)
    for j in range(7):
        fl = limb(root, body, f'{tag}_chama{j}', flame)
        parts['flames'].append((fl, j))
    head = empty(root, tag + '_cabeca', parent=body)
    parts['head'] = head
    hb = blob(root, tag + '_cranio', 0.085, (0.04, 0, 0), (1.45, 1.0, 0.8), coal)
    hb.parent = head
    jaw = blob(root, tag + '_queixo', 0.07, (0.05, 0, -0.035), (1.35, 0.9, 0.4), glowb)
    jaw.parent = head
    # olhos enormes de fogo (traco da lenda)
    for k, s in enumerate((-1, 1)):
        e = blob(root, f'{tag}_olho{k}', 0.032, (0.07, s * 0.05, 0.04), (0.8, 1.0, 1.0), P['m_ember'])
        e.parent = head
    for i in range(5):
        cr = limb(root, head, f'{tag}_crista{i}', flame)
        parts['flames'].append((cr, 100 + i))
    return parts


def pose_boitata(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    throw = math.sin(math.pi * min(1.0, f / (ATK_N - 1) * 1.3)) if mode == 'atk' else 0.0
    sc = 1.0 - 0.85 * smooth01(f / (DIE_N - 1)) if mode == 'die' else 1.0
    set_body(parts, face, (0, 0, 0.03 * math.sin(a)), scale=sc)
    n = 18
    pts = []
    for j in range(n + 1):
        u = j / n
        x = -0.3 + 0.62 * u
        y = 0.07 * math.sin(a - (1 - u) * 6)
        z = 0.06 * math.sin(a + (1 - u) * 5) - 0.05 * (1 - u) + 0.1 * throw * u
        pts.append(Vector((x, y, z)))
    rad = lambda t: 0.026 + 0.05 * t
    set_mesh_tube(parts['tube'], pts, 0.07, segs=14, rfun=rad)
    set_mesh_tube(parts['belly'], [q + Vector((0, 0, -0.022)) for q in pts[2:]], 0.05, segs=12, rfun=lambda t: 0.02 + 0.035 * t)
    parts['head'].location = pts[-1] + Vector((0.03, 0, 0.02))
    parts['head'].rotation_euler = (0, -0.25 * throw, 0.1 * math.sin(a))
    for fl, j in parts['flames']:
        h = 0.06 + 0.04 * math.sin(a * 3 + j)
        if j >= 100:
            k = j - 100
            base = Vector((0.0 - 0.025 * k, (k - 2) * 0.012, 0.055))
            w = 0.022
        else:
            u = 0.15 + 0.12 * j
            q = pts[int(u * n)]
            base = q + Vector((0, 0, rad(u) * 0.8))
            w = 0.012 + 0.02 * u
        tip = base + Vector((-0.04 + 0.015 * math.sin(a * 2 + j), 0.01 * math.sin(a * 3 + j), h))
        set_mesh_tube(fl, [base, base.lerp(tip, 0.5) + Vector((0.008 * math.sin(a * 2 + j), 0, 0)), tip], w, segs=6, rfun=lambda t, w=w: w * (1 - t) + 0.002)


# ---------------------------------------------------------------- HUMANOIDES DO FOLCLORE (kit de personagem do inimigos.py)
def possess_eyes(pr, P):
    # os olhos do kit chibi viram brasa (mesmo formato, sem o brilho branco)
    tag = pr['tag']
    for k in range(2):
        o = bpy.data.objects.get(f'{tag}_olho{k}')
        if o:
            o.data.materials.clear()
            o.data.materials.append(P['m_ember'])
        b = bpy.data.objects.get(f'{tag}_brilho{k}')
        if b:
            pr.setdefault('_hidden', []).append(b)


def hide_legs(pr):
    hid = pr.setdefault('_hidden', [])
    hid.extend(pr['limbs'][k] for k in ('coxaL', 'coxaR', 'canelaL', 'canelaR'))
    hid.extend(pr[k] for k in ('peL', 'peR'))


def apply_hidden(parts):
    for o in parts.get('_hidden', ()):
        o.hide_render = o.hide_viewport = True


def with_post(states, post):
    def fn(mode, f, view):
        st = states(mode, f, view)
        st['_post'] = post
        return st
    return fn


def humanoid2(key, label, builder, states, boost=K.EN_BOOST, post=None):
    """Igual ao K.humanoid, com um gancho depois da pose (pes virados, cauda, chapeu...)."""
    def mk(mode, view):
        def fn(parts, P, root, f):
            st = states(mode, f, view)
            st.setdefault('face', VIEWS[view])
            K.pose_chibi(parts, st)
            if post:
                post(parts, mode, f, st)
            apply_hidden(parts)
        return fn
    modes = [('r', WALK_N, mk('walk', 'r')), ('u', WALK_N, mk('walk', 'u')), ('d', WALK_N, mk('walk', 'd')),
             ('a', ATK_N, mk('atk', 'r')), ('x', DIE_N, mk('die', 'r'))]
    return {'key': key, 'label': label, 'build': builder, 'boost': boost, 'margin': (0.08, 0.08, 0.1, 0.06),
            'pose0': lambda parts, P, root: K.pose_chibi(parts, dict(states('walk', 0, 'r'), face=VIEWS['r'])), 'modes': modes}


# Curupira: menino da mata de cabelo em chamas e pes virados para tras (chefe)
def build_curupira(P, root):
    tag = root['set']
    skin = mat('mata_pele_curupira', '#b97a52', rough=0.6, var=0.03, bump=0.05)
    pr = K.build_chibi(P, root, dict(top=skin, pants=skin, sleeve=skin, glove=skin, skin=skin, shoe=skin, skirt=0.16,
                                     skirt_m=P['m_leaf'], head='bald', big=1.85, head_r=0.125, blush=False))
    hc = Vector((0, 0, 0.125 * 0.92))
    for i in range(9):
        an = -1.4 + i * 0.35
        base = hc + Vector((-0.02 + 0.06 * math.cos(an) * 0.4, 0.1 * math.sin(an) * 0.6, 0.09))
        tip = base + Vector((-0.08 - 0.03 * math.cos(an), 0.05 * math.sin(an), 0.09 + 0.03 * math.cos(an * 2)))
        fl = tube(root, f'{tag}_cabelo{i}', [base, base.lerp(tip, 0.5) + Vector((0.02, 0, 0.02)), tip], 0.035, mat('mata_cabelo_fogo', '#ef6a2a', rough=0.5, var=0.0, bump=0.0, emit=0.6),
                  segs=8, rfun=lambda t: 0.04 * (1 - t) + 0.004)
        fl.parent = pr['head']
    possess_eyes(pr, P)
    cracks(root, P, pr['body'], tag, [[(0.06, 0.1, 0.3), (0.08, 0.06, 0.26), (0.09, 0.08, 0.22)], [(0.06, -0.1, 0.3), (0.085, -0.07, 0.25)]], r=0.007)
    br = tube(root, f'{tag}_galho', [(0, 0, -0.05), (0.01, 0, 0.12), (0.03, 0.01, 0.26)], 0.018, P['p_wood'], segs=6, rfun=lambda t: 0.02 * (1 - 0.4 * t))
    lf = blob(root, f'{tag}_galhoFolha', 0.03, (0.04, 0.01, 0.27), (1.4, 0.5, 0.8), P['m_leaf'])
    lf.parent = br
    K.hold2(pr, 'R', br)
    return pr


def curupira_states(mode, f, view):
    if mode == 'walk':
        st = K.gait(f / WALK_N, stride=0.08, lift=0.05, lean=0.08)
        st['grip_R'] = (0.2, 0.0, 1.0)
        return st
    if mode == 'atk':
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.6))
        hit = max(0.0, (t - 0.5) / 0.5)
        return {'lean': 0.25 * hit - 0.1 * up, 'ph': t, 'offset': (0, 0, 0.04 * up), 'hand_R': (0.06 + 0.15 * hit, -0.13, 0.26 + 0.28 * up - 0.18 * hit),
                'grip_R': (-0.2 + 1.2 * hit, 0, 1.0 - 1.0 * hit), 'foot_L': (0.07, 0.06, 0.045 + 0.04 * up), 'foot_R': (-0.05, -0.06, 0.045)}
    return K.death(f / (DIE_N - 1), VIEWS['r'])


def curupira_post(parts, mode, f, st):
    # pes virados para tras
    for side in 'LR':
        pe = parts['pe' + side]
        pe.location = pe.location + Vector((-0.052, 0, 0))
        pe.rotation_euler = (0, -pe.rotation_euler[1], math.pi)


# Iara: mae-d'agua com cauda de peixe e top de conchas
def build_iara(P, root):
    tag = root['set']
    skin = mat('mata_pele_iara', '#e6b896', rough=0.6, var=0.03, bump=0.04)
    scale_m = mat('mata_escama', '#6aa8a0', rough=0.35, var=0.05, bump=0.1, sheen=0.3)
    pr = K.build_chibi(P, root, dict(top=skin, pants=scale_m, sleeve=skin, glove=skin, skin=skin, head='bald', brows='calm', head_r=0.12))
    hide_legs(pr)
    hair = mat('mata_cabelo_iara', '#2f4a40', rough=0.6, var=0.04, bump=0.15, sheen=0.3)
    for i in range(7):
        y = (i - 3) * 0.03
        h = tube(root, f'{tag}_cabelo{i}', [(-0.02, y, 0.2), (-0.1, y * 1.4, 0.14), (-0.16, y * 1.6, 0.04), (-0.18, y * 1.8, -0.06)], 0.026, hair, segs=6,
                 rfun=lambda t: 0.03 * (1 - 0.6 * t))
        h.parent = pr['head']
    cap = blob(root, f'{tag}_franja', 0.13, (-0.015, 0, 0.18), (1.0, 1.05, 0.5), hair)
    cap.parent = pr['head']
    shell = mat('mata_concha', '#f4a99a', rough=0.35, var=0.02, bump=0.08, sheen=0.4)
    for k, s in enumerate((-1, 1)):
        sh = blob(root, f'{tag}_concha{k}', 0.038, (0.08, s * 0.045, 0.31), (0.45, 1.0, 0.9), shell)
        sh.parent = pr['body']
    possess_eyes(pr, P)
    parts_tail = []
    for j in range(7):
        sg = blob(root, f'{tag}_cauda{j}', 0.075 - 0.007 * j, (0, 0, 0), (1.0, 1.0, 0.9), scale_m)
        sg.parent = pr['body']
        parts_tail.append(sg)
    fin = cloth_grid(root, f'{tag}_barbatana', 1.0, 1.0, 3, 3, [mat('mata_barbatana', '#8fc8be', rough=0.4, var=0.03, bump=0.05)], thick=0.01,
                     shape=lambda u, v, co: Vector((-v * 0.12, (u - 0.5) * 0.16 * (0.4 + v), 0.0)))
    fin.parent = pr['body']
    pr['tail'] = parts_tail
    pr['fin'] = fin
    cracks(root, P, pr['body'], tag, [[(0.08, 0.06, 0.22), (0.09, 0.0, 0.2), (0.08, -0.06, 0.22)]], r=0.006)
    return pr


def iara_states(mode, f, view):
    ph = f / WALK_N
    a = TAU * ph
    if mode == 'walk':
        return {'lean': 0.05, 'ph': ph, 'offset': (0, 0, 0.03 + 0.015 * math.sin(a)), 'head_pitch': -0.05,
                'hand_L': (0.05, 0.16, 0.24 + 0.02 * math.sin(a)), 'hand_R': (0.05, -0.16, 0.24 - 0.02 * math.sin(a))}
    if mode == 'atk':
        t = f / (ATK_N - 1)
        k = math.sin(math.pi * t)
        return {'lean': -0.08 * k, 'ph': t, 'offset': (0, 0, 0.03 + 0.03 * k), 'head_pitch': -0.3 * k,
                'hand_L': (0.08 + 0.06 * k, 0.15, 0.26 + 0.2 * k), 'hand_R': (0.08 + 0.06 * k, -0.15, 0.26 + 0.2 * k)}
    st = K.death(f / (DIE_N - 1), VIEWS['r'])
    st['offset'] = (st['offset'][0], 0, st['offset'][2] + 0.03)
    return st


def iara_post(parts, mode, f, st):
    ph = st.get('ph', 0.0)
    a = TAU * ph
    pts = []
    for j in range(8):
        u = j / 7
        pts.append(Vector((-0.02 - 0.24 * u, 0.04 * math.sin(a - u * 4) * u, 0.18 - 0.17 * math.sin(math.pi * 0.5 * u) - (st['offset'][2] if 'offset' in st else 0) * u)))
    for j, sg in enumerate(parts['tail']):
        sg.location = pts[j].lerp(pts[j + 1], 0.5)
    parts['fin'].location = pts[-1]
    parts['fin'].rotation_euler = (0.3 * math.sin(a * 2), 0, 0.3 * math.sin(a - 2))


# Boto encantado: golfinho cor-de-rosa de roupa branca e chapeu de palha
def build_boto(P, root):
    tag = root['set']
    pink = mat('mata_boto', '#e8a2a8', rough=0.35, var=0.03, bump=0.04, sheen=0.3)
    white = mat('mata_linho', '#f4efe6', rough=0.85, var=0.02, bump=0.08)
    pr = K.build_chibi(P, root, dict(top=white, pants=white, sleeve=white, glove=pink, skin=pink, shoe=P['p_leather'], belt=P['p_tan'],
                                     head='bald', brows='calm', blush=False, mask=None, head_r=0.12))
    for nm in ('_nariz', '_boca'):
        o = bpy.data.objects.get(tag + nm)
        if o:
            pr.setdefault('_hidden', []).append(o)
    hc = Vector((0, 0, 0.12 * 0.92))
    ro = tube(root, f'{tag}_rostro', [hc + Vector((0.1, 0, -0.02)), hc + Vector((0.17, 0, -0.03)), hc + Vector((0.22, 0, -0.025))], 0.035, pink, segs=10,
              rfun=lambda t: 0.04 * (1 - 0.55 * t))
    ro.parent = pr['head']
    straw = mat('mata_palha', '#e2c27a', rough=0.9, var=0.05, bump=0.35)
    brim = torus(root, f'{tag}_aba', hc + Vector((0, 0, 0.1)), 0.14, 0.018, straw, n=28, segs=6)
    brim.parent = pr['head']
    brim.scale = (1.0, 1.0, 0.45)
    crown = lathe(root, f'{tag}_copa', [(0.0, 0.085, 0.085), (0.05, 0.08, 0.08), (0.075, 0.06, 0.06), (0.08, 0.0, 0.0)], straw, segs=20, lv=2)
    crown.parent = pr['head']
    crown.location = hc + Vector((0, 0, 0.095))
    band = torus(root, f'{tag}_fita', hc + Vector((0, 0, 0.11)), 0.083, 0.008, P['p_coral'], n=24, segs=5)
    band.parent = pr['head']
    possess_eyes(pr, P)
    bubble = blob(root, f'{tag}_bolha', 0.045, (0, 0, 0.05), (1, 1, 1), alpha_mat('mata_bolha', '#cfeef0', 0.55, emit=0.4))
    K.hold2(pr, 'R', bubble)
    cracks(root, P, pr['body'], tag, [[(0.09, 0.07, 0.3), (0.1, 0.03, 0.27)], [(0.09, -0.06, 0.24), (0.1, -0.02, 0.21)]], r=0.006)
    return pr


def boto_states(mode, f, view):
    if mode == 'walk':
        st = K.gait(f / WALK_N, stride=0.085, lean=0.06, bob=0.018)
        st['hand_R'] = (0.08, -0.15, 0.24)
        st['grip_R'] = (0.0, 0.0, 1.0)
        return st
    if mode == 'atk':
        t = f / (ATK_N - 1)
        back = math.sin(math.pi * min(1.0, t / 0.6))
        fwd = max(0.0, (t - 0.55) / 0.45)
        return {'lean': 0.05 - 0.12 * back + 0.25 * fwd, 'ph': t, 'hand_R': (-0.06 * back + 0.2 * fwd, -0.12, 0.3 + 0.18 * back),
                'grip_R': (0.0, 0.0, 1.0), 'hand_L': (0.14, 0.12, 0.28), 'hide': (root_tag_bubble,) if fwd > 0.3 else (),
                'foot_L': (0.07, 0.06, 0.045), 'foot_R': (-0.05, -0.06, 0.045)}
    return K.death(f / (DIE_N - 1), VIEWS['r'])


root_tag_bubble = 'saboteur_bolha'


# Macaco-prego: atira carocos; boné de pelo escuro, cara clara e cauda enrolada
def build_macaco(P, root):
    tag = root['set']
    fur = mat('mata_macaco', '#8a6448', rough=0.85, var=0.04, bump=0.3)
    face = mat('mata_macaco_cara', '#e8c9a2', rough=0.6, var=0.03, bump=0.05)
    pr = K.build_chibi(P, root, dict(top=fur, pants=fur, sleeve=fur, glove=face, skin=face, shoe=fur, head='bald', head_r=0.115, blush=False))
    hc = Vector((0, 0, 0.115 * 0.92))
    cap = blob(root, f'{tag}_bone', 0.105, hc + Vector((-0.015, 0, 0.05)), (1.0, 1.05, 0.7), mat('mata_macaco_bone', '#4e3424', rough=0.85, var=0.04, bump=0.3))
    cap.parent = pr['head']
    for k, s in enumerate((-1, 1)):
        ear = blob(root, f'{tag}_orelhaM{k}', 0.032, hc + Vector((-0.01, s * 0.11, 0.0)), (0.5, 0.9, 1.0), face)
        ear.parent = pr['head']
    muz = blob(root, f'{tag}_focinhoM', 0.05, hc + Vector((0.09, 0, -0.04)), (0.8, 1.1, 0.8), face)
    muz.parent = pr['head']
    possess_eyes(pr, P)
    tail = tube(root, f'{tag}_cauda', [(-0.1, 0, 0.2), (-0.2, 0, 0.22), (-0.26, 0, 0.32), (-0.22, 0, 0.4), (-0.17, 0, 0.36)], 0.018, fur, segs=6, rfun=lambda t: 0.02 * (1 - 0.5 * t))
    tail.parent = pr['body']
    seed = blob(root, f'{tag}_caroco', 0.022, (0, 0, 0.03), (1, 1, 1), P['p_wood'])
    K.hold2(pr, 'R', seed)
    cracks(root, P, pr['body'], tag, [[(0.09, 0.06, 0.3), (0.1, 0.02, 0.26), (0.09, -0.03, 0.24)]], r=0.006)
    return pr


def macaco_states(mode, f, view):
    if mode == 'walk':
        st = K.gait(f / WALK_N, stride=0.09, lift=0.06, bob=0.026, lean=0.18)
        st['grip_R'] = (0.0, 0.0, 1.0)
        return st
    if mode == 'atk':
        t = f / (ATK_N - 1)
        back = math.sin(math.pi * min(1.0, t / 0.6))
        fwd = max(0.0, (t - 0.55) / 0.45)
        return {'lean': 0.08 - 0.1 * back + 0.2 * fwd, 'ph': t, 'hand_R': (-0.05 * back + 0.2 * fwd, -0.12, 0.3 + 0.2 * back),
                'grip_R': (0.0, 0.0, 1.0), 'hand_L': (0.12, 0.13, 0.26), 'hide': ('nomad_caroco',) if fwd > 0.3 else (),
                'foot_L': (0.07, 0.06, 0.045), 'foot_R': (-0.05, -0.06, 0.045)}
    return K.death(f / (DIE_N - 1), VIEWS['r'])


# Matinta Pereira: velha-passaro (rasga-mortalha) de capa de penas escuras, flutua (sem chapeu de bruxa)
def owl_wing(side):
    def fn(u, v, co):
        # asa arredondada com a borda de fuga em penas (recortes)
        x = 0.03 - v * (0.15 - 0.07 * u * u) - 0.012 * v * (1 + math.cos(u * math.pi * 5)) * u
        return Vector((x, side * u * 0.24, 0.025 * math.sin(math.pi * u) * (1 - v)))
    return fn


def build_matinta(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'wings': []}

    def p(o):
        o.parent = body
        return o
    feather = mat('mata_penas', '#4a3f3c', rough=0.85, var=0.05, bump=0.3)
    feather_l = mat('mata_penas_claras', '#7a6a62', rough=0.85, var=0.05, bump=0.3)
    skin = mat('mata_pele_matinta', '#e8c8ac', rough=0.65, var=0.03, bump=0.08)
    hair = mat('mata_cabelo_branco', '#ece6dc', rough=0.8, var=0.03, bump=0.2)
    rag = lambda a, z: 0.018 * math.sin(11 * a) * max(0.0, (-0.05 - z) / 0.12)
    # capa de penas em sino com barra rasgada
    p(lathe(root, tag + '_capa', [(-0.17, 0.0, 0.0, -0.14), (-0.12, 0.045, 0.04, -0.1), (-0.06, 0.08, 0.072, -0.06), (0.0, 0.095, 0.088, -0.03),
                                  (0.06, 0.098, 0.09, -0.01), (0.12, 0.07, 0.068, 0.0)], feather, segs=22, wobble=rag, lv=2))
    p(blob(root, tag + '_peito', 0.07, (0.03, 0, 0.04), (0.8, 1.0, 1.1), feather_l))
    p(torus(root, tag + '_gola', (0.0, 0, 0.12), 0.06, 0.028, feather_l, n=20, segs=8)).scale = (1.0, 1.1, 0.8)
    head = empty(root, tag + '_cabecaPivo', loc=(0.02, 0, 0.17), parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    ph(blob(root, tag + '_cabeca', 0.075, (0.0, 0, 0.0), (0.95, 1.0, 1.0), skin))
    # cabelo branco preso atras e mechas soltas
    ph(blob(root, tag + '_coque', 0.05, (-0.07, 0, 0.05), (1.0, 1.1, 1.0), hair))
    ph(blob(root, tag + '_cabeloTopo', 0.07, (-0.035, 0, 0.02), (0.9, 1.05, 0.8), hair))
    for k, sd in enumerate((-1, 1)):
        ph(tube(root, f'{tag}_mecha{k}', [(-0.01, sd * 0.06, 0.02), (0.0, sd * 0.078, -0.03), (-0.01, sd * 0.07, -0.08)], 0.014, hair, segs=6,
                rfun=lambda t: 0.016 * (1 - 0.6 * t)))
    ph(tube(root, tag + '_nariz', [(0.068, 0, 0.0), (0.095, 0, -0.012), (0.098, 0, -0.03)], 0.014, skin, segs=6, rfun=lambda t: 0.015 * (1 - 0.55 * t)))
    for k, sd in enumerate((-1, 1)):
        ph(blob(root, f'{tag}_olhoBrasa{k}', 0.013, (0.062, sd * 0.028, 0.015), (0.55, 0.9, 0.7), P['m_ember']))
        ph(box(root, f'{tag}_sobrancelha{k}', (0.008, 0.026, 0.007), (0.066, sd * 0.03, 0.034), rot=(math.radians(-20 * sd), 0, 0), m=hair, bev=0.003))
    for k, sd in enumerate((-1, 1)):
        piv = empty(root, f'{tag}_asaPivo{k}', loc=(-0.01, sd * 0.07, 0.1), parent=body)
        w = cloth_grid(root, f'{tag}_asa{k}', 1.0, 1.0, 6, 4, [feather], thick=0.014, shape=owl_wing(sd))
        w.parent = piv
        tip = cloth_grid(root, f'{tag}_asaPonta{k}', 1.0, 1.0, 4, 2, [feather_l], thick=0.016,
                         shape=lambda u, v, co, sd=sd: Vector((0.03 - v * 0.05, sd * (0.02 + u * 0.2), 0.012)))
        tip.parent = piv
        parts['wings'].append((sd, piv))
    cracks(root, P, body, tag, [[(0.07, 0.07, 0.0), (0.085, 0.03, -0.03), (0.085, -0.02, -0.01)]], r=0.006)
    return parts


def pose_matinta(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    flap = 0.55 * math.sin(a) + 0.25
    sc = 1.3
    off = (0, 0, 0.03 * math.sin(a))
    if mode == 'atk':
        flap = 0.9 * math.sin(math.pi * f / (ATK_N - 1)) + 0.25
    if mode == 'die':
        t = f / (DIE_N - 1)
        sc = 1.3 * (1.0 - 0.8 * smooth01(t))
        off = (0, 0, 0.06 * t)
    set_body(parts, face, off, pitch=0.1, scale=sc)
    parts['head'].rotation_euler = (0, 0.05 * math.sin(a * 2), 0.08 * math.sin(a))
    for sd, piv in parts['wings']:
        piv.rotation_euler = (sd * flap, 0, 0)


# Mapinguari: gigante peludo de um olho e boca na barriga
def build_mapinguari(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'limbs': {}}

    def p(o):
        o.parent = body
        return o
    fur = mat('mata_pelo_mapi', '#7a5a40', rough=0.95, var=0.06, bump=0.5)
    fur_d = mat('mata_pelo_mapi_d', '#5e442e', rough=0.95, var=0.06, bump=0.5)
    p(blob(root, tag + '_tronco', 0.3, (0, 0, 0.62), (0.9, 1.05, 1.05), fur))
    import random as _r
    rr = _r.Random(5)
    for j in range(26):
        a = rr.uniform(-math.pi, math.pi)
        z = rr.uniform(0.42, 0.9)
        rad = 0.3 * math.sqrt(max(0.0, 1 - ((z - 0.62) / 0.33) ** 2))
        p(blob(root, f'{tag}_tufo{j}', rr.uniform(0.05, 0.08), (math.cos(a) * rad * 0.88, math.sin(a) * rad, z), (1.0, 1.0, 0.8), fur if j % 3 else fur_d))
    # olho unico na testa
    eye = p(blob(root, tag + '_olhoUnico', 0.06, (0.24, 0, 0.85), (0.6, 1.0, 1.0), P['m_ember']))
    p(blob(root, tag + '_sobrancelha', 0.07, (0.24, 0, 0.92), (0.6, 1.4, 0.4), fur_d))
    # boca na barriga
    p(blob(root, tag + '_boca', 0.09, (0.27, 0, 0.56), (0.35, 1.0, 0.7), P['m_dark']))
    for i in range(6):
        y = (i - 2.5) * 0.028
        p(blob(root, f'{tag}_dente{i}', 0.014, (0.29, y, 0.6 if i % 2 else 0.52), (0.6, 0.7, 1.2), P['m_teeth']))
    for side in 'LR':
        for nm in ('braco', 'antebraco', 'coxa', 'canela'):
            parts['limbs'][nm + side] = limb(root, body, f'{tag}_{nm}{side}', fur)
        parts['mao' + side] = p(blob(root, f'{tag}_mao{side}', 0.08, (0, 0, 0), (1.0, 1.0, 1.1), fur_d))
        parts['pe' + side] = p(blob(root, f'{tag}_pe{side}', 0.09, (0, 0, 0), (1.4, 1.0, 0.6), fur_d))
    cracks(root, P, body, tag, [[(0.2, 0.18, 0.75), (0.24, 0.1, 0.7), (0.26, 0.14, 0.64)], [(0.18, -0.2, 0.7), (0.23, -0.12, 0.66)]], r=0.012)
    return parts


def pose_mapinguari(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    L = parts['limbs']
    roll = 0.06 * math.sin(a)
    pitch = 0.05
    off = Vector((0, 0, 0.035 * abs(math.sin(a)) - 0.02))
    feet, hands = {}, {}
    for side, s, yy in (('L', 0, 0.14), ('R', 1, -0.14)):
        b = a + s * math.pi
        feet[side] = Vector((0.1 * math.cos(b), yy, 0.06 + 0.06 * max(0.0, -math.sin(b)) - off.z))
        hands[side] = Vector((0.06 - 0.12 * math.cos(b), yy * 2.3, 0.32 + 0.04 * max(0.0, -math.cos(b))))
    if mode == 'atk':
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.6))
        hit = max(0.0, (t - 0.5) / 0.5)
        pitch = 0.05 + 0.3 * hit - 0.1 * up
        roll = 0.0
        for side, yy in (('L', 0.16), ('R', -0.16)):
            hands[side] = Vector((0.12 + 0.2 * hit, yy * 1.6, 0.6 + 0.4 * up - 0.3 * hit))
            feet[side] = Vector((0.05, yy * 0.9, 0.06))
    elif mode == 'die':
        t = f / (DIE_N - 1)
        e = smooth01(t)
        pitch = 1.3 * e
        off = Vector((0.12 * e, 0, -0.06 * e))
        for side, yy in (('L', 0.14), ('R', -0.14)):
            feet[side] = Vector((-0.02, yy, 0.06 + 0.06 * e))
            hands[side] = Vector((0.2 + 0.15 * e, yy * 2.2, 0.4 - 0.1 * e))
    set_body(parts, face, off, roll=roll, pitch=pitch)
    for side, yy in (('L', 0.14), ('R', -0.14)):
        hip = Vector((0, yy, 0.38))
        Kn, F = two_bone(hip, feet[side], 0.18, 0.17, (1.0, 0, 0.2))
        set_mesh_tube(L['coxa' + side], [hip, hip.lerp(Kn, 0.5), Kn], 0.085, segs=8)
        set_mesh_tube(L['canela' + side], [Kn, Kn.lerp(F, 0.5), F], 0.075, segs=8)
        parts['pe' + side].location = F + Vector((0.04, 0, -0.03))
        sh = Vector((0.02, yy * 2.0, 0.78))
        E, Hh = two_bone(sh, hands[side], 0.22, 0.22, (-0.5, yy * 3, -0.5))
        set_mesh_tube(L['braco' + side], [sh, sh.lerp(E, 0.5), E], 0.075, segs=8)
        set_mesh_tube(L['antebraco' + side], [E, E.lerp(Hh, 0.5), Hh], 0.065, segs=8)
        parts['mao' + side].location = Hh + (Hh - E).normalized() * 0.05


SPEC = {
    'crews': [
        creature('raider', 'Sauva', ant_builder(lambda P: {'m': P['m_ant'], 'k': 1.25, 'leaf': True}), pose_ant, atk=True),
        creature('scorpling', 'Tucandeira', ant_builder(lambda P: {'m': P['m_ant_d'], 'k': 0.85}), pose_ant, atk=True),
        creature('brood', 'Tucandeira-Mae', ant_builder(lambda P: {'m': P['m_ant_q'], 'k': 1.7, 'gaster': 0.085, 'eggs': True}), pose_ant, atk=True),
        creature('jackal', 'Queixada', quad_builder('jackal'), pose_quad, atk=True),
        creature('brute', 'Onca-Pintada', quad_builder('brute'), pose_quad, atk=True, boost=K.EN_BOOST * 1.15),
        creature('specter', 'Anhanga', quad_builder('specter'), pose_quad, shadow=False),
        creature('beetle', 'Tatu', quad_builder('beetle'), pose_quad),
        creature('scorpion', 'Jacare-de-Pedra', build_croc, pose_croc, atk=True, boost=K.EN_BOOST * 1.1),
        creature('bulwark', 'Tracaja', build_turtle, pose_turtle, atk=True),
        creature('vulture', 'Morcego-Vampiro', build_bat, pose_bat, shadow=False),
        creature('worm', 'Boiuna', build_boiuna, pose_boiuna, atk=True, views=('r',)),
        creature('ifrit', 'Boitata', build_boitata, pose_boitata, atk=True, shadow=False, boost=K.EN_BOOST * 1.25),
        creature('djinn', 'Matinta Pereira', build_matinta, pose_matinta, atk=True, shadow=False),
        creature('golem', 'Mapinguari', build_mapinguari, pose_mapinguari, atk=True),
        humanoid2('warlord', 'Curupira', build_curupira, curupira_states, post=curupira_post),
        humanoid2('shaman', 'Iara', build_iara, iara_states, post=iara_post),
        humanoid2('saboteur', 'Boto', build_boto, boto_states),
        humanoid2('nomad', 'Macaco-prego', build_macaco, macaco_states),
    ],
}


if __name__ == '__main__':
    lib.palette2 = pal
    main(FAM, SPEC)
