"""Criaturas do Bastiao das Areias (sprites pre-renderizados, cores pasteis). Complementa tools/blender/inimigos.py:
mesma familia (arte/render/inimigos), mesmos modos (r/u/d andando, a ataque, x morte). Referencias em arte/conceitos/inimigos/.

uso: /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/inimigos_bichos.py -- render arte/render/inimigos [conjuntos]
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib
import inimigos as K

FAM = K.FAM
WALK_N, ATK_N, DIE_N = K.WALK_N, K.ATK_N, K.DIE_N
VIEWS = K.VIEWS


def pal():
    P = K.pastel()
    P['c_jackal'] = mat('pastel_chacal', '#c4a8cc', rough=0.85, var=0.04, bump=0.25, sheen=0.3)
    P['c_jackal_d'] = mat('pastel_chacal_escuro', '#9f88b6', rough=0.85, var=0.04, bump=0.25, sheen=0.3)
    P['c_amber'] = mat('pastel_ambar', '#e8a24a', rough=0.2, var=0.0, bump=0.0)
    P['c_dark'] = mat('pastel_escuro', '#4a3a48', rough=0.3, var=0.0, bump=0.0)
    P['c_shell'] = mat('pastel_carapaca', '#ec877b', rough=0.35, var=0.03, bump=0.04)
    P['c_mauve'] = mat('pastel_carapaca_malva', '#bf8fb2', rough=0.35, var=0.03, bump=0.04)
    P['c_mint'] = mat('pastel_carapaca_menta', '#82cfa4', rough=0.35, var=0.03, bump=0.04)
    P['c_turq'] = mat('pastel_turquesa', '#6cc7c0', rough=0.25, metal=0.15, var=0.02, bump=0.03)
    P['c_navy'] = mat('pastel_lilas_escuro', '#7a7cbb', rough=0.5, var=0.03, bump=0.06)
    P['c_engrave'] = mat('pastel_gravura', '#f2dfa8', rough=0.3, metal=0.4, var=0.0, bump=0.0)
    P['c_stone'] = mat('pastel_arenito', '#efb27c', rough=0.9, var=0.07, bump=0.45)
    P['c_rune'] = mat('pastel_runa', '#a6f2cf', rough=0.4, var=0.0, bump=0.0, emit=3.0)
    P['c_moss'] = mat('pastel_musgo', '#97bd86', rough=0.95, var=0.08, bump=0.5)
    P['c_worm'] = mat('pastel_verme', '#ee8f84', rough=0.45, var=0.03, bump=0.08)
    P['c_worm_ring'] = mat('pastel_verme_anel', '#f3dcc4', rough=0.5, var=0.02, bump=0.06)
    P['c_mouth'] = mat('pastel_boca', '#a988c6', rough=0.4, var=0.0, bump=0.0)
    P['c_sand'] = mat('pastel_areia', '#e8cfa0', rough=0.95, var=0.05, bump=0.5)
    P['c_fire'] = mat('pastel_fogo', '#ec7f5c', rough=0.55, var=0.03, bump=0.03, emit=0.18)
    P['c_fire2'] = mat('pastel_fogo_claro', '#f4a46e', rough=0.55, var=0.03, bump=0.03, emit=0.25)
    P['c_flame'] = mat('pastel_chama', '#ffbe63', rough=0.5, var=0.0, bump=0.0, emit=1.1)
    P['c_ball'] = mat('pastel_bola_fogo', '#ffb85a', rough=0.5, var=0.0, bump=0.0, emit=1.6)
    P['c_eye_glow'] = mat('pastel_olho_luz', '#fff3c8', rough=0.5, var=0.0, bump=0.0, emit=4.0)
    P['c_wind'] = alpha_mat('pastel_vento', '#9ee0c4', 0.85, emit=0.25)
    P['c_wind2'] = alpha_mat('pastel_vento_lilas', '#c0a8e6', 0.85, emit=0.25)
    P['c_ghost'] = alpha_mat('pastel_espectro', '#d2ecf8', 0.7, emit=0.35)
    P['c_veil'] = alpha_mat('pastel_veu', '#c7b6ea', 0.65, emit=0.3)
    P['c_smoke'] = alpha_mat('pastel_fumaca', '#c9b3dc', 0.7, emit=0.1)
    return P


def alpha_mat(key, hexcol, alpha, emit=0.0):
    """Material translucido (vento, veu, espectro): o mat() do lib com alfa no Principled."""
    m = mat(key, hexcol, rough=0.5, var=0.0, bump=0.0, emit=emit)
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Alpha'].default_value = alpha
    try:
        m.blend_method = 'BLEND'
    except Exception:
        pass
    return m


def limb(root, body, name, m):
    o = ensure_mesh(root, name, m)
    o.parent = body
    o['set'] = root['set']
    return o


def eye_pair(root, P, parent, tag, c, r, sep, m=None, glow=False):
    out = []
    for k, s in enumerate((-1, 1)):
        e = blob(root, f'{tag}_olho{k}', r, (c[0], c[1] + s * sep, c[2]), (0.55, 0.85, 1.1), m or P['p_eye'])
        e.parent = parent
        out.append(e)
        if not glow:
            h = blob(root, f'{tag}_olhoBrilho{k}', r * 0.32, (c[0] + r * 0.45, c[1] + s * sep - r * 0.2, c[2] + r * 0.45), (0.5, 1, 1), P['p_white'])
            h.parent = parent
            out.append(h)
    return out


def creature(key, label, build, pose, atk=False, boost=K.EN_BOOST, shadow=True, views=('r', 'u', 'd'), margin=(0.08, 0.08, 0.1, 0.06)):
    ms = [(v, WALK_N, (lambda parts, P, root, f, v=v: pose(parts, 'walk', f, v))) for v in views]
    if atk:
        ms.append(('a', ATK_N, lambda parts, P, root, f: pose(parts, 'atk', f, 'r')))
    ms.append(('x', DIE_N, lambda parts, P, root, f: pose(parts, 'die', f, 'r')))
    return {'key': key, 'label': label, 'build': build, 'boost': boost, 'shadow': shadow, 'margin': margin,
            'pose0': lambda parts, P, root: pose(parts, 'walk', 0, 'r'), 'modes': ms}


def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def set_body(parts, face, offset=(0, 0, 0), roll=0.0, pitch=0.0, yaw=0.0, scale=1.0):
    b = parts['body']
    b.rotation_euler = (roll, pitch, face + yaw)
    b.location = Vector(offset)
    b.scale = (scale, scale, scale)


# ---------------------------------------------------------------- CHACAL
JACKAL_LEGS = {'FL': (0.09, 0.036, 0.17, 0.0), 'FR': (0.09, -0.036, 0.17, math.pi), 'BL': (-0.085, 0.04, 0.17, math.pi), 'BR': (-0.085, -0.04, 0.17, 0.0)}


def build_jackal(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'legs': {}}

    def p(o):
        o.parent = body
        return o
    fur, cream = P['c_jackal'], P['p_cream']
    p(blob(root, tag + '_tronco', 0.075, (0, 0, 0.2), (1.7, 0.82, 0.78), fur))
    p(blob(root, tag + '_barriga', 0.058, (0.0, 0, 0.172), (1.45, 0.72, 0.55), cream))
    p(blob(root, tag + '_listra', 0.05, (-0.02, 0, 0.245), (1.9, 0.42, 0.25), P['c_jackal_d']))
    p(blob(root, tag + '_peito', 0.058, (0.095, 0, 0.21), (1.0, 0.8, 1.0), cream))
    p(tube(root, tag + '_pescoco', [(0.09, 0, 0.23), (0.14, 0, 0.3)], 0.036, fur, segs=10))
    head = empty(root, tag + '_cabecaPivo', loc=(0.15, 0, 0.31), parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    ph(blob(root, tag + '_cabeca', 0.056, (0, 0, 0), (1.1, 0.95, 0.9), fur))
    ph(tube(root, tag + '_focinho', [(0.03, 0, -0.012), (0.115, 0, -0.03)], 0.03, cream, segs=10, rfun=lambda t: 0.032 * (1 - 0.55 * t)))
    ph(blob(root, tag + '_nariz', 0.013, (0.118, 0, -0.026), (1, 1, 0.8), P['c_dark']))
    eye_pair(root, P, head, tag, (0.04, 0, 0.012), 0.014, 0.03, m=P['c_amber'])
    for k, s in enumerate((-1, 1)):
        ear = lathe(root, f'{tag}_orelha{k}', [(0.0, 0.028, 0.012), (0.05, 0.024, 0.011), (0.1, 0.012, 0.006), (0.125, 0.0, 0.0)], fur, segs=10, lv=1)
        ph(ear).location = (-0.01, s * 0.03, 0.035)
        ear.rotation_euler = (s * 0.32, -0.12, 0)
        inner = blob(root, f'{tag}_orelhaDentro{k}', 0.018, (0.012, 0, 0.05), (0.35, 1.0, 2.1), P['p_pink'])
        inner.parent = ear
    p(torus(root, tag + '_coleira', (0.125, 0, 0.275), 0.034, 0.008, P['p_tan'], n=16, segs=5)).rotation_euler = (0, -0.6, 0)
    p(blob(root, tag + '_conta', 0.012, (0.155, 0, 0.255), (1, 1, 1), P['p_butter']))
    parts['tail'] = limb(root, body, tag + '_cauda', fur)
    parts['tailtip'] = p(blob(root, tag + '_caudaPonta', 0.034, (0, 0, 0), (1.3, 0.85, 0.85), cream))
    for k in JACKAL_LEGS:
        parts['legs'][k] = (limb(root, body, f'{tag}_perna{k}a', fur), limb(root, body, f'{tag}_perna{k}b', fur),
                            p(blob(root, f'{tag}_pata{k}', 0.02, (0, 0, 0), (1.4, 1.0, 0.7), cream)))
    return parts


def pose_jackal(parts, mode, f, view):
    face = VIEWS[view]
    ph = f / WALK_N
    a = TAU * ph
    roll = pitch = 0.0
    off = (0, 0, 0.012 * math.cos(2 * a))
    feet = {}
    stride, lift = 0.075, 0.055
    for k, (x, y, z, o) in JACKAL_LEGS.items():
        b = a + o
        feet[k] = Vector((x + stride * math.cos(b), y, 0.022 + lift * max(0.0, -math.sin(b))))
    head_p = 0.06 * math.sin(2 * a)
    tail_y = 0.05 * math.sin(a)
    if mode == 'atk':
        t = f / (ATK_N - 1)
        lunge = math.sin(math.pi * t)
        off = (0.04 * lunge, 0, 0)
        pitch = 0.2 * lunge
        head_p = 0.4 * lunge
        for k, (x, y, z, o) in JACKAL_LEGS.items():
            feet[k] = Vector((x + (0.05 if k[0] == 'F' else -0.03) * lunge, y, 0.022))
    elif mode == 'die':
        t = f / (DIE_N - 1)
        e = smooth01(t)
        roll = 1.45 * e
        off = (0, -0.06 * e, 0.0)
        for k, (x, y, z, o) in JACKAL_LEGS.items():
            feet[k] = Vector((x + 0.03 * e, y + (0.06 if y > 0 else 0.0) * e, 0.022 + 0.06 * e))
        head_p = -0.2 * e
        tail_y = 0.0
    set_body(parts, face, off, roll=roll, pitch=pitch)
    parts['head'].rotation_euler = (0, head_p, 0)
    for k, (x, y, z, o) in JACKAL_LEGS.items():
        A = Vector((x, y, z))
        F = feet[k]
        Kn, F2 = two_bone(A, F, 0.08, 0.08, (-1.0, 0.0, 0.25))
        up, lo, paw = parts['legs'][k]
        set_mesh_tube(up, [A, A.lerp(Kn, 0.5), Kn], 0.026, segs=8, rfun=lambda t: 0.03 - 0.01 * t)
        set_mesh_tube(lo, [Kn, Kn.lerp(F2, 0.5), F2], 0.017, segs=8)
        paw.location = F2 + Vector((0.012, 0, -0.008))
    tp = [Vector((-0.11, 0, 0.22)), Vector((-0.17, tail_y * 0.5, 0.215)), Vector((-0.22, tail_y, 0.19))]
    set_mesh_tube(parts['tail'], tp, 0.024, segs=8, rfun=lambda t: 0.022 + 0.012 * t)
    parts['tailtip'].location = tp[-1] + Vector((-0.025, tail_y * 0.3, -0.008))


# ---------------------------------------------------------------- ESCORPIOES (gigante, filhote e mae)
SC_LEGS = [(0.05, 0.0), (-0.01, math.pi), (-0.07, 0.0)]


def build_scorpion(P, root, shell, claw=None, scale=1.0, babies=False, eye_r=0.016):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'legs': [], 'k': scale}
    claw = claw or shell

    def p(o):
        o.parent = body
        return o
    p(blob(root, tag + '_cefalo', 0.075, (0.06, 0, 0.09), (1.15, 1.12, 0.62), shell))
    for j, (x, r) in enumerate(((-0.03, 0.074), (-0.095, 0.068), (-0.155, 0.056))):
        p(blob(root, f'{tag}_placa{j}', r, (x, 0, 0.088 - 0.006 * j), (0.72, 1.05, 0.56), shell))
    p(blob(root, tag + '_ventre', 0.07, (-0.03, 0, 0.065), (1.9, 0.9, 0.35), P['p_cream']))
    eye_pair(root, P, body, tag, (0.12, 0, 0.125), eye_r, 0.026)
    parts['tail'] = [p(blob(root, f'{tag}_cauda{j}', 0.046 - 0.004 * j, (0, 0, 0), (1.0, 0.95, 0.9), shell)) for j in range(6)]
    sting = lathe(root, tag + '_ferrao', [(0.0, 0.03, 0.03), (0.03, 0.026, 0.026), (0.065, 0.0, 0.0)], P['c_mint'], segs=12, lv=2)
    parts['sting'] = p(sting)
    parts['arms'] = []
    for k, s in enumerate((-1, 1)):
        arm = limb(root, body, f'{tag}_braco{k}', claw)
        big = p(blob(root, f'{tag}_pinca{k}', 0.045, (0, 0, 0), (1.35, 0.8, 0.62), claw))
        fin = p(blob(root, f'{tag}_dedo{k}', 0.026, (0, 0, 0), (1.5, 0.6, 0.5), claw))
        parts['arms'].append((s, arm, big, fin))
    for i, (x, o) in enumerate(SC_LEGS):
        for k, s in enumerate((-1, 1)):
            up = limb(root, body, f'{tag}_perna{i}{k}a', shell)
            lo = limb(root, body, f'{tag}_perna{i}{k}b', shell)
            parts['legs'].append((x, s, o + (math.pi if s > 0 else 0.0), up, lo))
    if babies:
        basket = lathe(root, tag + '_cesto', [(0.0, 0.055, 0.06), (0.03, 0.085, 0.09), (0.06, 0.1, 0.105), (0.068, 0.096, 0.1)],
                       mat('pastel_cesto', '#e9d3a6', rough=0.9, var=0.03, bump=0.4, stripes=(26.0, '#e9d3a6', '#cfae7c')), segs=20, lv=2, caps=False, solid=0.01)
        p(basket).location = (-0.07, 0, 0.13)
        parts['babies'] = []
        for j, (bx, by, col) in enumerate(((-0.03, 0.04, 'p_mint'), (0.02, -0.03, 'p_peach'), (-0.09, -0.04, 'p_mint'),
                                           (-0.12, 0.03, 'p_peach'), (-0.06, 0.0, 'p_mint'))):
            bb = p(blob(root, f'{tag}_filhote{j}', 0.03, (-0.07 + bx, by, 0.2), (1.1, 1.0, 0.8), P[col]))
            eye_pair(root, P, bb, f'{tag}_filhote{j}', (0.024, 0, 0.012), 0.009, 0.012)
            parts['babies'].append(bb)
    body.scale = (scale, scale, scale)
    return parts


def pose_scorpion(parts, mode, f, view, tail_hi=1.0):
    face = VIEWS[view]
    ph = f / WALK_N
    a = TAU * ph
    roll = pitch = 0.0
    off = (0, 0, 0.006 * math.cos(2 * a))
    strike = 0.0
    curl = 0.0
    if mode == 'atk':
        t = f / (ATK_N - 1)
        strike = math.sin(math.pi * min(1.0, t * 1.4))
    elif mode == 'die':
        # encolhe e afunda: patas recolhidas, cauda caindo, leve tombo de lado
        t = f / (DIE_N - 1)
        curl = smooth01(t)
        roll = 0.32 * curl
        pitch = -0.08 * curl
        off = (0, 0, 0.03 * math.sin(math.pi * min(1.0, t * 1.6)) - 0.02 * curl)
    set_body(parts, face, off, roll=roll, pitch=pitch, scale=parts['k'])
    # cauda em arco sobre as costas; no ataque o ferrao desce para a frente
    n = len(parts['tail'])
    pts = []
    sway = 0.02 * math.sin(a)
    for j in range(n + 1):
        u = j / n
        ang = math.pi * (0.1 + 0.85 * u * tail_hi) * (1 - 0.35 * curl)
        x = -0.18 + 0.12 * (1 - math.cos(ang))
        z = 0.1 + 0.2 * math.sin(ang) * tail_hi
        x += 0.16 * strike * u * u
        z -= 0.12 * strike * u * u
        pts.append(Vector((x, sway * u, z * (1 - 0.5 * curl))))
    for j, seg in enumerate(parts['tail']):
        seg.location = pts[j].lerp(pts[j + 1], 0.5)
    tip = pts[-1]
    d = (pts[-1] - pts[-2]).normalized()
    parts['sting'].location = tip
    parts['sting'].rotation_euler = d.to_track_quat('Z', 'X').to_euler()
    for s, arm, big, fin in parts['arms']:
        snap = 0.5 + 0.5 * math.sin(2 * a + (0 if s > 0 else 1.5))
        reach = 0.05 * strike
        A = Vector((0.11, s * 0.055, 0.09))
        Bv = Vector((0.17 + reach, s * 0.1, 0.085 + 0.02 * strike))
        C = Vector((0.23 + reach * 1.6, s * 0.09, 0.08))
        set_mesh_tube(arm, [A, Bv, C], 0.022, segs=8, rfun=lambda t: 0.022 + 0.004 * t)
        big.location = C + Vector((0.035, 0, 0.004))
        big.rotation_euler = (0, 0, s * 0.25)
        fin.location = C + Vector((0.04, -s * 0.012, -0.012 - 0.008 * snap))
        fin.rotation_euler = (0, 0, -s * (0.3 + 0.3 * snap))
    for x, s, o, up, lo in parts['legs']:
        b = a + o
        A = Vector((x, s * 0.06, 0.08))
        if mode == 'die':
            F = Vector((x + 0.01, s * (0.15 - 0.07 * curl), 0.012 + 0.05 * curl))
        else:
            F = Vector((x + 0.035 * math.cos(b), s * 0.15, 0.012 + 0.03 * max(0.0, -math.sin(b))))
        Kn, F2 = two_bone(A, F, 0.075, 0.08, (0.0, s * 0.5, 1.0))
        set_mesh_tube(up, [A, A.lerp(Kn, 0.5), Kn], 0.016, segs=8)
        set_mesh_tube(lo, [Kn, Kn.lerp(F2, 0.5), F2], 0.013, segs=8, rfun=lambda t: 0.014 - 0.007 * t)
    for j, bb in enumerate(parts.get('babies', [])):
        bb.location.z = 0.2 + 0.012 * math.sin(a * 2 + j * 1.3)


def build_scorp_giant(P, root):
    return build_scorpion(P, root, P['c_shell'], scale=1.15)


def build_scorpling(P, root):
    return build_scorpion(P, root, P['c_mint'], claw=P['p_peach'], scale=0.55, eye_r=0.026)


def build_brood(P, root):
    return build_scorpion(P, root, P['c_mauve'], scale=1.35, babies=True)


# ---------------------------------------------------------------- BESOURO ESCAVADOR
def build_beetle(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'legs': []}

    def p(o):
        o.parent = body
        return o
    sh = lathe(root, tag + '_casco', [(0.0, 0.112, 0.1), (0.035, 0.12, 0.106), (0.075, 0.106, 0.094), (0.11, 0.07, 0.062), (0.128, 0.0, 0.0)],
               P['c_turq'], segs=24, lv=2)
    p(sh).location = (-0.02, 0, 0.045)
    sh.scale = (1.25, 1.0, 1.0)
    # gravuras douradas: costura do meio e arcos nos elitros
    p(tube(root, tag + '_costura', [(-0.16 + 0.32 * t, 0, 0.045 + 0.128 * math.sqrt(max(0.0, 1 - ((t - 0.5) * 2) ** 2)) * 0.98 + 0.002) for t in [i / 12 for i in range(13)]],
           0.006, P['c_engrave'], segs=5))
    for k, s in enumerate((-1, 1)):
        arc = []
        for i in range(11):
            t = i / 10
            x = -0.12 + 0.2 * t
            yy = s * (0.055 + 0.02 * math.sin(math.pi * t))
            rr = math.sqrt(max(0.0, 1 - (x / 0.15) ** 2 - (yy / 0.106) ** 2))
            arc.append((x - 0.02, yy, 0.045 + 0.126 * rr + 0.003))
        p(tube(root, f'{tag}_gravura{k}', arc, 0.005, P['c_engrave'], segs=5))
    p(blob(root, tag + '_cabeca', 0.05, (0.13, 0, 0.07), (1.0, 1.1, 0.8), P['c_navy']))
    horn = [(0.15, 0, 0.09), (0.19, 0, 0.13), (0.22, 0, 0.16)]
    p(tube(root, tag + '_chifre', horn, 0.016, P['c_navy'], segs=8, rfun=lambda t: 0.018 - 0.006 * t))
    p(blob(root, tag + '_pa', 0.03, (0.225, 0, 0.165), (0.6, 1.3, 0.35), P['c_navy']))
    eye_pair(root, P, body, tag, (0.17, 0, 0.085), 0.012, 0.03, m=P['p_cream'], glow=True)
    for i, (x, o) in enumerate(SC_LEGS):
        for k, s in enumerate((-1, 1)):
            up = limb(root, body, f'{tag}_perna{i}{k}a', P['c_navy'])
            lo = limb(root, body, f'{tag}_perna{i}{k}b', P['c_navy'])
            parts['legs'].append((x * 1.2, s, o + (math.pi if s > 0 else 0.0), up, lo))
    return parts


def pose_beetle(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    roll = 0.0
    off = (0, 0, 0.006 * math.cos(2 * a))
    curl = 0.0
    if mode == 'die':
        t = f / (DIE_N - 1)
        roll = math.pi * smooth01(min(1.0, t * 1.3))
        off = (0, 0, 0.12 * math.sin(math.pi * min(1.0, t * 1.3)) + 0.17 * smooth01(min(1.0, t * 1.3)))
        curl = smooth01(t)
    set_body(parts, face, off, roll=roll)
    for x, s, o, up, lo in parts['legs']:
        b = a + o
        A = Vector((x, s * 0.08, 0.06))
        F = Vector((x + 0.04 * math.cos(b), s * 0.15, 0.012 + 0.028 * max(0.0, -math.sin(b)))) if not curl else Vector((x, s * (0.15 - 0.05 * curl), 0.012 + 0.05 * curl))
        Kn, F2 = two_bone(A, F, 0.06, 0.06, (0.0, s * 0.5, 1.0))
        set_mesh_tube(up, [A, A.lerp(Kn, 0.5), Kn], 0.016, segs=8)
        set_mesh_tube(lo, [Kn, Kn.lerp(F2, 0.5), F2], 0.013, segs=8)


# ---------------------------------------------------------------- ABUTRE (voa)
def wing_shape(side):
    # asa larga na raiz, borda de ataque curva e ponta mais estreita (onde saem as penas)
    def fn(u, v, co):
        lead = 0.075 - 0.05 * u * u
        chord = 0.21 - 0.09 * u
        x = lead - v * chord
        return Vector((x, side * u * 0.3, -0.025 * math.sin(math.pi * u) * (1 - 0.6 * v)))
    return fn


def build_vulture(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'wings': []}

    def p(o):
        o.parent = body
        return o
    p(blob(root, tag + '_tronco', 0.085, (0, 0, 0), (1.35, 0.95, 0.85), P['p_slate']))
    p(blob(root, tag + '_peito', 0.062, (0.05, 0, -0.025), (1.2, 0.8, 0.7), P['p_lilac']))
    p(torus(root, tag + '_gola', (0.11, 0, 0.045), 0.034, 0.016, P['p_fur'], n=18, segs=8)).rotation_euler = (0, -1.0, 0)
    head = empty(root, tag + '_cabecaPivo', loc=(0.15, 0, 0.07), parent=body)
    parts['head'] = head
    hb = blob(root, tag + '_cabeca', 0.042, (0.0, 0, 0), (1.15, 0.95, 0.95), P['p_pink'])
    hb.parent = head
    bk = lathe(root, tag + '_bico', [(0.0, 0.02, 0.016), (0.03, 0.016, 0.012), (0.05, 0.006, 0.005), (0.058, 0.0, 0.0, -0.012)], P['p_butter'], segs=10, lv=2)
    bk.parent = head
    bk.location = (0.03, 0, -0.004)
    bk.rotation_euler = (0, math.pi / 2 + 0.25, 0)
    eye_pair(root, P, head, tag, (0.022, 0, 0.012), 0.011, 0.025)
    tail = blob(root, tag + '_cauda', 0.06, (-0.13, 0, -0.005), (1.0, 1.25, 0.22), P['p_rose'])
    p(tail)
    for k, s in enumerate((-1, 1)):
        piv = empty(root, f'{tag}_asaPivo{k}', loc=(0.02, s * 0.06, 0.03), parent=body)
        w = cloth_grid(root, f'{tag}_asa{k}', 1.0, 1.0, 6, 4, [P['p_rose']], thick=0.016, shape=wing_shape(s))
        w.parent = piv
        for j in range(4):
            fx = -0.01 - 0.035 * j
            ft = tube(root, f'{tag}_pena{k}{j}', [(fx, s * 0.29, -0.0), (fx - 0.02, s * (0.36 + 0.015 * (2 - abs(j - 1.5))), -0.005)], 0.013, P['p_cream'], segs=6,
                      rfun=lambda t: 0.014 * (1 - 0.5 * t))
            ft.parent = piv
        parts['wings'].append((s, piv))
    for k, s in enumerate((-1, 1)):
        p(blob(root, f'{tag}_pe{k}', 0.016, (-0.03, s * 0.03, -0.075), (1.3, 0.8, 0.7), P['p_pink']))
    return parts


def pose_vulture(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    flap = 0.85 * math.sin(a)
    off = (0, 0, -0.025 * math.sin(a))
    pitch = 0.08 * math.cos(a)
    roll = 0.0
    if mode == 'die':
        t = f / (DIE_N - 1)
        flap = 0.9 * (1 - smooth01(t)) * math.sin(a * 3) + 1.1 * smooth01(t)
        pitch = 1.6 * smooth01(t)
        roll = 0.6 * smooth01(t)
        off = (0, 0, 0)
    set_body(parts, face, off, roll=roll, pitch=pitch)
    parts['head'].rotation_euler = (0, 0.1 * math.sin(a + 1), 0)
    for s, piv in parts['wings']:
        piv.rotation_euler = (s * flap, 0, 0)


# ---------------------------------------------------------------- GOLEM DE ARENITO
def build_golem(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body}

    def p(o):
        o.parent = body
        return o
    st, rune = P['c_stone'], P['c_rune']
    p(box(root, tag + '_quadril', (0.2, 0.3, 0.12), (0, 0, 0.42), m=st, bev=0.035))
    p(box(root, tag + '_tronco', (0.26, 0.36, 0.3), (0, 0, 0.62), m=st, bev=0.05))
    p(box(root, tag + '_peitoral', (0.1, 0.24, 0.12), (0.1, 0, 0.7), m=st, bev=0.03))
    # runa no peito e nos ombros
    for i, (y0, z0, y1, z1) in enumerate(((-0.07, 0.6, 0.0, 0.7), (0.0, 0.7, 0.07, 0.6), (-0.05, 0.62, 0.05, 0.62), (0.0, 0.7, 0.0, 0.54))):
        p(tube(root, f'{tag}_runa{i}', [(0.157, y0, z0), (0.157, y1, z1)], 0.01, rune, segs=5))
    for k, s in enumerate((-1, 1)):
        p(box(root, f'{tag}_ombro{k}', (0.16, 0.14, 0.13), (0.0, s * 0.24, 0.76), m=st, bev=0.04))
        p(tube(root, f'{tag}_runaOmbro{k}', [(0.081, s * 0.2, 0.74), (0.081, s * 0.28, 0.74)], 0.008, rune, segs=5))
        p(blob(root, f'{tag}_musgo{k}', 0.045, (-0.01, s * 0.23, 0.83), (1.3, 1.0, 0.45), P['c_moss']))
    # cactos pequenos no ombro esquerdo
    p(cyl(root, tag + '_cacto', 0.022, 0.08, (0.0, 0.22, 0.87), m=P['cactus'], v=10, bev=0.01))
    p(blob(root, tag + '_cactoTopo', 0.022, (0.0, 0.22, 0.91), (1, 1, 1), P['cactus']))
    p(blob(root, tag + '_flor', 0.01, (0.0, 0.22, 0.935), (1, 1, 0.6), P['p_pink']))
    head = empty(root, tag + '_cabecaPivo', loc=(0.02, 0, 0.8), parent=body)
    parts['head'] = head
    hb = box(root, tag + '_cabeca', (0.13, 0.14, 0.12), (0, 0, 0.05), m=st, bev=0.03)
    hb.parent = head
    for k, s in enumerate((-1, 1)):
        e = box(root, f'{tag}_olho{k}', (0.01, 0.03, 0.016), (0.066, s * 0.033, 0.055), m=rune, bev=0.004)
        e.parent = head
    parts['limbs'] = {}
    for side in 'LR':
        for nm in ('braco', 'antebraco', 'coxa', 'canela'):
            parts['limbs'][nm + side] = limb(root, body, f'{tag}_{nm}{side}', st)
        parts['punho' + side] = p(box(root, f'{tag}_punho{side}', (0.11, 0.1, 0.11), (0, 0, 0), m=st, bev=0.035))
        parts['pe' + side] = p(box(root, f'{tag}_pe{side}', (0.15, 0.1, 0.06), (0, 0, 0), m=st, bev=0.025))
    return parts


def pose_golem(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    L = parts['limbs']
    roll = 0.05 * math.sin(a)
    pitch = 0.05
    off = Vector((0, 0, 0.03 * abs(math.sin(a)) - 0.015))
    feet = {}
    hands = {}
    for side, s, yy in (('L', 0, 0.1), ('R', 1, -0.1)):
        b = a + s * math.pi
        feet[side] = Vector((0.1 * math.cos(b), yy, 0.05 + 0.05 * max(0.0, -math.sin(b)) - off.z))
        hands[side] = Vector((0.02 - 0.1 * math.cos(b), yy * 2.6, 0.4 + 0.03 * max(0.0, -math.cos(b))))
    if mode == 'atk':
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.6))
        hit = max(0.0, (t - 0.5) / 0.5)
        pitch = 0.05 + 0.35 * hit - 0.1 * up
        for side, yy in (('L', 0.12), ('R', -0.12)):
            hands[side] = Vector((0.08 + 0.2 * hit, yy, 0.55 + 0.4 * up - 0.3 * hit))
            feet[side] = Vector((0.06 if side == 'L' else -0.06, yy * 0.85, 0.05))
        roll = 0.0
    elif mode == 'die':
        t = f / (DIE_N - 1)
        e = smooth01(t)
        pitch = 1.35 * e
        roll = 0.15 * e
        off = Vector((0.1 * e, 0, -0.05 * e))
        for side, yy in (('L', 0.1), ('R', -0.1)):
            feet[side] = Vector((-0.02, yy, 0.05 + 0.05 * e))
            hands[side] = Vector((0.15 + 0.15 * e, yy * 2.4, 0.45 - 0.1 * e))
    set_body(parts, face, off, roll=roll, pitch=pitch)
    for side, yy in (('L', 0.1), ('R', -0.1)):
        hip = Vector((0, yy, 0.38))
        Kn, F = two_bone(hip, feet[side], 0.17, 0.17, (1.0, 0, 0.2))
        set_mesh_tube(L['coxa' + side], [hip, hip.lerp(Kn, 0.5), Kn], 0.07, segs=6)
        set_mesh_tube(L['canela' + side], [Kn, Kn.lerp(F, 0.5), F], 0.065, segs=6)
        parts['pe' + side].location = F + Vector((0.03, 0, -0.025))
        sh = Vector((0, yy * 2.5, 0.74))
        E, H = two_bone(sh, hands[side], 0.17, 0.17, (-0.5, yy * 3, -0.5))
        set_mesh_tube(L['braco' + side], [sh, sh.lerp(E, 0.5), E], 0.065, segs=6)
        set_mesh_tube(L['antebraco' + side], [E, E.lerp(H, 0.5), H], 0.06, segs=6)
        parts['punho' + side].location = H + (H - E).normalized() * 0.04
    parts['head'].rotation_euler = (0, 0.05 * math.sin(2 * a), 0.06 * math.sin(a))


# ---------------------------------------------------------------- ESPECTRO DA AREIA
def build_specter(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'cloth': []}

    def p(o):
        o.parent = body
        return o
    wob = lambda a, z: 0.012 * math.sin(6 * a + z * 30)
    # corpo de areia e veu: capuz arredondado em cima, afinando numa cauda de fumaca curvada para tras
    p(lathe(root, tag + '_corpo_veu', [(0.02, 0.0, 0.0, -0.11), (0.06, 0.018, 0.02, -0.085), (0.11, 0.042, 0.046, -0.05), (0.17, 0.066, 0.072, -0.022),
                                       (0.24, 0.082, 0.088), (0.31, 0.086, 0.092), (0.37, 0.078, 0.084), (0.42, 0.052, 0.056), (0.445, 0.0, 0.0)],
            P['c_ghost'], segs=20, wobble=wob, lv=2))
    parts['bands'] = []
    for j, (z, r) in enumerate(((0.2, 0.083), (0.29, 0.092))):
        bd = p(torus(root, f'{tag}_faixa{j}', (0, 0, 0), r, 0.012, P['c_veil'], n=24, segs=6))
        bd.location = (0.0, 0, z)
        parts['bands'].append((bd, j))
    for k, s in enumerate((-1, 1)):
        e = blob(root, f'{tag}_olho{k}', 0.024, (0.078, s * 0.036, 0.35), (0.5, 0.8, 1.35), P['c_dark'])
        p(e)
        p(blob(root, f'{tag}_olhoLuz{k}', 0.012, (0.09, s * 0.036, 0.352), (0.5, 0.8, 1.3), P['c_eye_glow']))
    for j, (y, z, w, h) in enumerate(((0.06, 0.3, 0.05, 0.22), (-0.06, 0.28, 0.05, 0.2), (0.0, 0.34, 0.06, 0.26))):
        r = cloth_grid(root, f'{tag}_fita{j}', w, h, 2, 6, [P['c_veil']], thick=0.008)
        p(r).location = (-0.07, y, z)
        r.rotation_euler = (0, 1.25, math.pi / 2)
        register_cloth(r, hang_wave(h, amp=0.04, axis='Y', cycles=1, waves=0.9, top=0.0))
        parts['cloth'].append(r)
    parts['arms'] = [limb(root, body, f'{tag}_braco{k}', P['c_veil']) for k in range(2)]
    return parts


def pose_specter(parts, mode, f, view):
    face = VIEWS[view]
    ph = f / WALK_N
    a = TAU * ph
    off = (0, 0, 0.03 + 0.02 * math.sin(a))
    sc = 1.0
    pitch = 0.12
    if mode == 'die':
        t = f / (DIE_N - 1)
        sc = 1.0 - 0.75 * smooth01(t)
        off = (0, 0, 0.03 + 0.12 * t)
    set_body(parts, face, off, pitch=pitch, scale=sc)
    for bd, j in parts.get('bands', []):
        bd.rotation_euler = (0.35 * math.sin(a + j * 2), 0.35 * math.cos(a + j * 2), a * (1 + j))
    for c in parts['cloth']:
        base, fn = CLOTH[c.name]
        for v, b in zip(c.data.vertices, base):
            v.co = fn(b, ph)
        c.data.update()
    for k, s in enumerate((-1, 1)):
        sw = 0.04 * math.sin(a + k * math.pi)
        set_mesh_tube(parts['arms'][k], [Vector((0.0, s * 0.085, 0.3)), Vector((0.04 + sw, s * 0.13, 0.24)), Vector((0.06 + sw, s * 0.14, 0.18))],
                      0.022, segs=8, rfun=lambda t: 0.022 * (1 - 0.7 * t))


# ---------------------------------------------------------------- DJINN MENOR (voa) - redemoinho com mascara de arenito
def build_djinn(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'rings': [], 'grains': []}

    def p(o):
        o.parent = body
        return o
    for j in range(9):
        t = j / 8
        r = 0.105 * (1 - t) ** 0.9 + 0.012
        ring = p(torus(root, f'{tag}_giro{j}', (0, 0, 0), r, 0.026 * (1 - 0.6 * t) + 0.008, P['c_wind'] if j % 2 == 0 else P['c_wind2'], n=22, segs=8))
        ring.location = (0, 0, 0.18 - 0.38 * t)
        parts['rings'].append((ring, t))
    p(blob(root, tag + '_peito', 0.09, (0, 0, 0.2), (0.95, 1.1, 0.8), P['c_wind']))
    head = empty(root, tag + '_cabecaPivo', loc=(0.0, 0, 0.29), parent=body)
    parts['head'] = head
    mk = blob(root, tag + '_mascara', 0.07, (0.0, 0, 0.0), (0.9, 1.0, 1.12), P['c_stone'])
    mk.parent = head
    for k, s in enumerate((-1, 1)):
        e = box(root, f'{tag}_fenda{k}', (0.01, 0.03, 0.011), (0.063, s * 0.027, 0.01), rot=(s * 0.35, 0, 0), m=P['c_eye_glow'], bev=0.004)
        e.parent = head
        horn = tube(root, f'{tag}_fita{k}', [(-0.02, s * 0.03, 0.06), (-0.06, s * 0.06, 0.12), (-0.13, s * 0.08, 0.14), (-0.17, s * 0.07, 0.1), (-0.15, s * 0.05, 0.08)],
                    0.016, P['p_lilac'], segs=8, rfun=lambda t: 0.017 * (1 - 0.5 * t))
        horn.parent = head
    parts['arms'] = []
    for k, s in enumerate((-1, 1)):
        arm = limb(root, body, f'{tag}_braco{k}', P['c_wind'])
        hand = p(blob(root, f'{tag}_mao{k}', 0.03, (0, 0, 0), (1.1, 0.9, 1.0), P['c_stone']))
        rings = [p(torus(root, f'{tag}_argola{k}{i}', (0, 0, 0), 0.03, 0.006, P['c_stone'], n=16, segs=5)) for i in range(2)]
        parts['arms'].append((s, arm, hand, rings))
    for i in range(7):
        parts['grains'].append(p(blob(root, f'{tag}_grao{i}', 0.008, (0, 0, 0), (1, 1, 1), P['c_stone'])))
    return parts


def pose_djinn(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    off = (0, 0, 0.02 * math.sin(a))
    sc = 1.0
    spin = a
    cast = 0.0
    if mode == 'atk':
        cast = math.sin(math.pi * f / (ATK_N - 1))
    if mode == 'die':
        t = f / (DIE_N - 1)
        sc = 1.0 - 0.8 * smooth01(t)
        spin = a * 3
        off = (0, 0, 0.05 * t)
    set_body(parts, face, off, pitch=0.08, scale=sc)
    for ring, t in parts['rings']:
        ring.rotation_euler = (0.15 * math.sin(spin + t * 6), 0.15 * math.cos(spin + t * 6), spin * 2 + t * 4)
        ring.location.x = 0.02 * math.sin(spin + t * 5) * t
    parts['head'].rotation_euler = (0, 0.05 * math.sin(a), 0)
    for s, arm, hand, rings in parts['arms']:
        sw = 0.04 * math.sin(a + (0 if s > 0 else math.pi))
        sh = Vector((0.0, s * 0.1, 0.24))
        H = Vector((0.06 + sw + 0.1 * cast, s * (0.17 + 0.05 * cast), 0.14 + 0.12 * cast))
        E = sh.lerp(H, 0.5) + Vector((-0.02, s * 0.03, -0.03))
        set_mesh_tube(arm, [sh, E, H], 0.024, segs=8, rfun=lambda t: 0.026 - 0.008 * t)
        hand.location = H + (H - E).normalized() * 0.025
        for i, rg in enumerate(rings):
            rg.location = H - (H - E).normalized() * (0.01 + 0.018 * i) + Vector((0, 0, 0.004 * math.sin(a * 2 + i)))
            rg.rotation_euler = (H - E).normalized().to_track_quat('Z', 'X').to_euler()
    for i, gr in enumerate(parts['grains']):
        an = spin * 1.5 + i * TAU / 7
        z = 0.12 - 0.3 * ((i * 0.37 + a / TAU) % 1)
        rr = 0.06 + 0.06 * (1 - (0.18 - z) / 0.38)
        gr.location = (rr * math.cos(an), rr * math.sin(an), z)


# ---------------------------------------------------------------- IFRIT, O REI DAS CHAMAS (chefe, voa)
def build_ifrit(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'flames': [], 'vortex': []}

    def p(o):
        o.parent = body
        return o
    fire = P['c_fire']
    p(lathe(root, tag + '_tronco', [(0.0, 0.06, 0.07), (0.06, 0.1, 0.12), (0.14, 0.13, 0.16), (0.22, 0.14, 0.175), (0.28, 0.12, 0.15), (0.32, 0.07, 0.08)],
            fire, segs=20, lv=2))
    p(blob(root, tag + '_ornamento', 0.035, (0.13, 0, 0.21), (0.4, 1.0, 1.0), P['p_gold']))
    p(blob(root, tag + '_gema', 0.018, (0.145, 0, 0.21), (0.5, 1, 1), P['c_ball']))
    for k, s in enumerate((-1, 1)):
        p(blob(root, f'{tag}_ombro{k}', 0.07, (0.0, s * 0.15, 0.27), (1.0, 0.9, 0.8), fire))
    head = empty(root, tag + '_cabecaPivo', loc=(0.02, 0, 0.33), parent=body)
    parts['head'] = head
    hb = blob(root, tag + '_cabeca', 0.08, (0.0, 0, 0.05), (0.95, 1.0, 1.0), fire)
    hb.parent = head
    for k, s in enumerate((-1, 1)):
        e = blob(root, f'{tag}_olho{k}', 0.014, (0.07, s * 0.03, 0.06), (0.5, 0.9, 1.2), P['c_eye_glow'])
        e.parent = head
        br = box(root, f'{tag}_sobrancelha{k}', (0.02, 0.04, 0.012), (0.066, s * 0.03, 0.085), rot=(s * -0.4, 0, 0), m=P['p_gold'], bev=0.004)
        br.parent = head
    for i in range(7):
        an = -1.2 + i * 0.4
        fl = limb(root, head, f'{tag}_chama{i}', P['c_flame'])
        parts['flames'].append((fl, an, i))
    for k in range(5):
        v = limb(root, body, f'{tag}_vortice{k}', P['c_fire'] if k % 2 == 0 else P['c_fire2'])
        parts['vortex'].append(v)
    parts['smoke'] = [p(blob(root, f'{tag}_fumaca{k}', 0.028, (0, 0, 0), (1.6, 1.0, 0.5), P['c_smoke'])) for k in range(3)]
    parts['arms'] = []
    for k, s in enumerate((-1, 1)):
        up = limb(root, body, f'{tag}_braco{k}', fire)
        lo = limb(root, body, f'{tag}_antebraco{k}', fire)
        cuff = p(torus(root, f'{tag}_bracelete{k}', (0, 0, 0), 0.045, 0.014, P['p_gold'], n=18, segs=6))
        ball = p(blob(root, f'{tag}_bola{k}', 0.05, (0, 0, 0), (1, 1, 1), P['c_ball']))
        parts['arms'].append((s, up, lo, cuff, ball))
    return parts


def pose_ifrit(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    off = (0, 0, 0.025 * math.sin(a))
    sc = 1.0
    throw = 0.0
    if mode == 'atk':
        throw = math.sin(math.pi * min(1.0, f / (ATK_N - 1) * 1.3))
    if mode == 'die':
        t = f / (DIE_N - 1)
        sc = 1.0 - 0.85 * smooth01(t)
        off = (0, 0, 0.1 * t)
    set_body(parts, face, off, pitch=0.06 - 0.1 * throw, scale=sc)
    for fl, an, i in parts['flames']:
        h = 0.09 + 0.05 * math.sin(a * 2 + i * 1.7) + 0.03 * (1 - abs(an) / 1.2)
        base = Vector((0.0 + 0.02 * math.cos(an), 0.065 * math.sin(an), 0.11))
        tip = base + Vector((-0.03 + 0.01 * math.sin(a + i), 0.03 * math.sin(an) + 0.012 * math.sin(a * 3 + i), h))
        mid = base.lerp(tip, 0.5) + Vector((0.01 * math.sin(a * 2 + i), 0, 0))
        set_mesh_tube(fl, [base, mid, tip], 0.026, segs=8, rfun=lambda t: 0.026 * (1 - t) + 0.002)
    for k, v in enumerate(parts['vortex']):
        pts = []
        for j in range(9):
            t = j / 8
            an = a * 2 + k * TAU / 5 + t * 5.0
            r = 0.13 * (1 - t) + 0.015
            pts.append(Vector((r * math.cos(an) * 0.9, r * math.sin(an), 0.02 - 0.42 * t)))
        set_mesh_tube(v, pts, 0.03, segs=8, rfun=lambda t: 0.034 * (1 - 0.8 * t))
    for k, sm in enumerate(parts['smoke']):
        an = a + k * TAU / 3
        sm.location = (0.05 * math.cos(an), 0.05 * math.sin(an), -0.3 - 0.04 * k)
        sm.rotation_euler = (0, 0, an)
    for s, up, lo, cuff, ball in parts['arms']:
        sh = Vector((0.0, s * 0.16, 0.27))
        H = Vector((0.12 + 0.18 * throw, s * (0.22 - 0.08 * throw), 0.14 + 0.06 * math.sin(a + s) + 0.12 * throw))
        E, H2 = two_bone(sh, H, 0.14, 0.13, (-0.5, s * 1.0, -0.4))
        set_mesh_tube(up, [sh, sh.lerp(E, 0.5), E], 0.048, segs=10, rfun=lambda t: 0.05 - 0.008 * t)
        set_mesh_tube(lo, [E, E.lerp(H2, 0.5), H2], 0.042, segs=10)
        d = (H2 - E).normalized()
        cuff.location = E.lerp(H2, 0.7)
        cuff.rotation_euler = d.to_track_quat('Z', 'X').to_euler()
        ball.location = H2 + d * 0.06
        ball.scale = (1.0 + 0.1 * math.sin(a * 3), 1.0, 1.0 + 0.1 * math.cos(a * 3))


# ---------------------------------------------------------------- GRANDE VERME DAS AREIAS (chefe)
def build_worm(P, root):
    tag = root['set']
    body = empty(root, tag + '_corpo')
    parts = {'tag': tag, 'body': body, 'segs': []}

    def p(o):
        o.parent = body
        return o
    mound = lathe(root, tag + '_monte', [(0.0, 0.3, 0.26), (0.03, 0.27, 0.23), (0.07, 0.19, 0.16), (0.09, 0.12, 0.1)], P['c_sand'], segs=24,
                  wobble=lambda a, z: 0.02 * math.sin(7 * a), lv=2, caps=False, solid=0.02)
    p(mound)
    for j in range(10):
        r = 0.115 - 0.003 * j
        sg = p(blob(root, f'{tag}_gomo{j}', r, (0, 0, 0), (0.75, 1.0, 1.0), P['c_worm']))
        ring = torus(root, f'{tag}_anel{j}', (0, 0, 0), r * 0.98, 0.018, P['c_worm_ring'], n=24, segs=6)
        ring.parent = sg
        ring.rotation_euler = (0, math.pi / 2, 0)
        ring.location = (r * 0.36, 0, 0)
        parts['segs'].append(sg)
    mouth = empty(root, tag + '_boca', parent=body)
    parts['mouth'] = mouth
    lip = torus(root, tag + '_labio', (0, 0, 0), 0.09, 0.03, P['c_worm'], n=24, segs=8)
    lip.parent = mouth
    lip.rotation_euler = (0, math.pi / 2, 0)
    inner = blob(root, tag + '_gula', 0.08, (-0.015, 0, 0), (0.3, 1, 1), P['c_mouth'])
    inner.parent = mouth
    for i in range(10):
        an = i * TAU / 10
        tooth = blob(root, f'{tag}_dente{i}', 0.016, (0.01, 0.075 * math.cos(an), 0.075 * math.sin(an)), (1.4, 0.8, 0.8), P['p_cream'])
        tooth.parent = mouth
    eye_pair(root, P, mouth, tag, (-0.02, 0, 0.1), 0.018, 0.06)
    return parts


def pose_worm(parts, mode, f, view):
    face = VIEWS[view]
    a = TAU * f / WALK_N
    arch = 0.0
    sink = 0.0
    if mode == 'atk':
        t = f / (ATK_N - 1)
        arch = math.sin(math.pi * min(1.0, t * 1.4))
    if mode == 'die':
        sink = smooth01(f / (DIE_N - 1))
    set_body(parts, face)
    n = len(parts['segs'])
    pts = []
    for j in range(n + 1):
        u = j / n
        h = 0.62 * math.sin(math.pi * 0.5 * u) * (1 - 0.6 * arch * u) * (1 - sink)
        x = 0.16 * u + 0.05 * math.sin(a - u * 4) * u + 0.3 * arch * u * u
        y = 0.04 * math.sin(a * 1 - u * 3) * u
        pts.append(Vector((x, y, h + 0.02 - 0.15 * sink * u)))
    for j, sg in enumerate(parts['segs']):
        c = pts[j].lerp(pts[j + 1], 0.5)
        d = (pts[j + 1] - pts[j]).normalized()
        sg.location = c
        sg.rotation_euler = d.to_track_quat('X', 'Z').to_euler()
    d = (pts[-1] - pts[-2]).normalized()
    head_dir = (d + Vector((0.6 + 0.6 * arch, 0, -0.35 - 0.8 * arch))).normalized()
    parts['mouth'].location = pts[-1] + head_dir * 0.05
    parts['mouth'].rotation_euler = head_dir.to_track_quat('X', 'Z').to_euler()
    open_ = 1.0 + 0.15 * math.sin(a * 2) + 0.3 * arch
    parts['mouth'].scale = (1.0, open_, open_)


SPEC = {
    'crews': [
        creature('jackal', 'Chacal', build_jackal, pose_jackal, atk=True),
        creature('scorpion', 'Escorpiao Gigante', build_scorp_giant, pose_scorpion, atk=True),
        creature('scorpling', 'Filhote de Escorpiao', build_scorpling, pose_scorpion, atk=True),
        creature('brood', 'Mae-Escorpiao', build_brood, lambda parts, mode, f, view: pose_scorpion(parts, mode, f, view, tail_hi=0.8), atk=True),
        creature('beetle', 'Besouro Escavador', build_beetle, pose_beetle),
        creature('vulture', 'Abutre', build_vulture, pose_vulture, shadow=False),
        creature('golem', 'Golem de Arenito', build_golem, pose_golem, atk=True),
        creature('specter', 'Espectro da Areia', build_specter, pose_specter, shadow=False),
        creature('djinn', 'Djinn Menor', build_djinn, pose_djinn, atk=True, shadow=False),
        creature('ifrit', 'Ifrit', build_ifrit, pose_ifrit, atk=True, shadow=False, boost=K.EN_BOOST * 1.25),
        creature('worm', 'Grande Verme', build_worm, pose_worm, atk=True, views=('r',)),
    ],
}


if __name__ == '__main__':
    lib.palette2 = pal
    main(FAM, SPEC)
