"""Inimigos do Bastiao das Areias em sprites pre-renderizados (estilo "soft relaxante", sempre em cores pasteis).

Usa o lib.py da familia das torres SO como biblioteca (nao edita nada nele). Referencias em arte/conceitos/inimigos/.
Os humanoides usam um kit proprio (cabeca grande, olhos expressivos, membros grossos com joelho e cotovelo),
mais proximo das referencias do que a tripulacao das torres.

Modos de cada conjunto (quadros <modo>_NN.png):
  r  andando de lado (3/4 de frente, olhando para a direita; o jogo espelha para a esquerda)
  u  andando para cima (3/4 de costas)        d  andando para baixo (quase de frente)
  a  ataque / especial de lado                x  morte de lado

uso: /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/inimigos.py -- render arte/render/inimigos [conjuntos]
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib

_ORIG_PAL = lib.palette2
FAM = 'inimigos'
WALK_N, ATK_N, DIE_N = 12, 6, 8
VIEWS = {'r': math.radians(-28), 'u': math.radians(42), 'd': math.radians(-74)}
EN_BOOST = 1.3


# ---------------------------------------------------------------- paleta pastel
def pastel():
    P = _ORIG_PAL()
    for k, hx in [
        ('peach', '#f0a684'), ('mint', '#82cfa4'), ('cream', '#ecdcbc'), ('lilac', '#ad94de'), ('sky', '#86b9ea'),
        ('butter', '#f0cf6e'), ('coral', '#ec877b'), ('rose', '#e290b0'), ('sage', '#97bd86'), ('plum', '#b07db4'),
        ('aqua', '#74cfcf'), ('apricot', '#f0b177'), ('tan', '#c99f76'), ('slate', '#8a86b6'), ('mauve', '#bf8fb2'),
        ('ice', '#b4dcf2'), ('teal', '#6dbdb3'), ('salmon', '#ee957e'), ('navy', '#7a7cbb'), ('pink', '#eea8bf'),
    ]:
        P['p_' + k] = mat('pastel_' + k, hx, rough=0.78, var=0.03, bump=0.08, sheen=0.12)
    P['p_skin'] = mat('pastel_pele', '#e6a985', rough=0.6, var=0.03, bump=0.04)
    P['p_skin2'] = mat('pastel_pele2', '#cf9470', rough=0.6, var=0.03, bump=0.04)
    P['p_eye'] = mat('pastel_olho', '#3a2b35', rough=0.18, var=0.0, bump=0.0)
    P['p_white'] = mat('pastel_brilho', '#ffffff', rough=0.3, var=0.0, bump=0.0, emit=1.5)
    P['p_blush'] = mat('pastel_bochecha', '#f2a9a2', rough=0.7, var=0.0, bump=0.0)
    P['p_brow'] = mat('pastel_sobrancelha', '#6a4a46', rough=0.8, var=0.0, bump=0.0)
    P['p_metal'] = mat('pastel_metal', '#dde2ea', rough=0.3, metal=0.6, var=0.02, bump=0.03)
    P['p_bronze'] = mat('pastel_bronze', '#ead0a4', rough=0.34, metal=0.55, var=0.03, bump=0.04)
    P['p_rosegold'] = mat('pastel_ouro_rosa', '#efc2ac', rough=0.34, metal=0.55, var=0.03, bump=0.04)
    P['p_gold'] = mat('pastel_ouro', '#f0d58e', rough=0.3, metal=0.6, var=0.02, bump=0.03)
    P['p_leather'] = mat('pastel_couro', '#c9a07e', rough=0.6, var=0.05, bump=0.12)
    P['p_wood'] = mat('pastel_madeira', '#c7a487', rough=0.7, var=0.05, bump=0.15)
    P['p_fur'] = mat('pastel_pelo', '#f6eedf', rough=0.95, var=0.04, bump=0.4)
    P['p_stripe'] = mat('pastel_listras', '#e290b0', rough=0.85, var=0.0, bump=0.05, stripes=(16.0, '#e290b0', '#86b9ea'))
    P['p_sand_glow'] = mat('pastel_areia_brilho', '#ffe7a6', rough=0.4, var=0.0, bump=0.0, emit=3.0)
    return P


# ---------------------------------------------------------------- kit de personagem
def scaled(prof, s, dz=0.0):
    return [tuple([p[0] * s + dz] + [v * s for v in p[1:]]) for p in prof]


def build_chibi(P, root, sp):
    """sp: top, pants, shoe, sleeve, glove, skin, vest, sash, belt, skirt (barra da tunica ate z), robe (manto cobrindo as pernas),
    head ('bald'|'wrap'|'hood'|'helmet'|'turban'), head_m, mask, agal, crest, plume, horns, cheek, goggles, scarf, fur, big,
    brows ('angry'|'calm'), blush."""
    tag = root['set']
    parts = {'tag': tag, 'sp': sp, 'cloth': [], 'props': [], 'limbs': {}}
    body = empty(root, tag + '_corpo')
    parts['body'] = body

    def p(o):
        o.parent = body
        return o
    skin = sp.get('skin', P['p_skin'])
    top = sp['top']
    pants = sp.get('pants', top)
    shoe = sp.get('shoe', P['p_leather'])
    parts['m'] = {'pants': pants, 'shoe': shoe, 'sleeve': sp.get('sleeve', top), 'glove': sp.get('glove', skin)}
    # quadril, tronco e barra da tunica
    p(blob(root, tag + '_quadril', 0.082, (0, 0, 0.205), (1.0, 1.2, 0.72), pants))
    p(lathe(root, tag + '_tronco', [(0.17, 0.088, 0.104), (0.22, 0.098, 0.116), (0.28, 0.103, 0.121), (0.33, 0.098, 0.116),
                                    (0.365, 0.082, 0.1), (0.39, 0.052, 0.062), (0.405, 0.03, 0.034)], top, segs=18, lv=2))
    hem = sp.get('skirt')
    if hem is not None:
        fold = lambda a, z: 0.012 * math.sin(9 * a)
        p(lathe(root, tag + '_barra', [(hem, 0.112, 0.128), (hem + 0.04, 0.104, 0.12), (0.2, 0.095, 0.112), (0.24, 0.094, 0.11)],
                sp.get('skirt_m', top), segs=18, wobble=fold, lv=2, caps=False, solid=0.006))
    if sp.get('robe'):
        fold = lambda a, z: 0.016 * math.sin(8 * a) * max(0.0, (0.2 - z) / 0.16)
        p(lathe(root, tag + '_manto', [(0.075, 0.125, 0.135), (0.11, 0.116, 0.128), (0.15, 0.104, 0.118), (0.2, 0.097, 0.113)],
                sp['robe'], segs=18, wobble=fold, lv=2, caps=False, solid=0.006))
    if sp.get('vest'):
        p(lathe(root, tag + '_colete', [(0.2, 0.1, 0.12), (0.26, 0.107, 0.126), (0.32, 0.103, 0.121), (0.36, 0.088, 0.106)],
                sp['vest'], segs=18, lv=2, caps=False, solid=0.006, cut=lambda c: c.x > 0.06 and abs(c.y) < 0.035))
    if sp.get('sash'):
        p(lathe(root, tag + '_faixa', [(0.185, 0.1, 0.12), (0.215, 0.104, 0.124), (0.24, 0.102, 0.122)], sp['sash'], segs=18, lv=1))
        tail = cloth_grid(root, tag + '_faixaPonta', 0.035, 0.09, 2, 4, [sp['sash']], thick=0.012)
        p(tail).location = (-0.03, 0.115, 0.215)
        register_cloth(tail, hang_wave(0.09, amp=0.02, axis='X', cycles=1, waves=0.5, top=0.0))
        parts['cloth'].append(tail)
    elif sp.get('belt'):
        p(lathe(root, tag + '_cinto', [(0.19, 0.1, 0.12), (0.215, 0.102, 0.122)], sp['belt'], segs=18, lv=1))
        p(blob(root, tag + '_fivela', 0.02, (0.1, 0, 0.202), (0.5, 1.0, 0.8), P['p_gold']))
    if sp.get('armor'):
        # escamas: aneis sobrepostos no tronco
        for j, z in enumerate((0.2, 0.245, 0.29, 0.335)):
            p(torus(root, f'{tag}_escama{j}', (0, 0, z), 0.107 - 0.005 * max(0, j - 2), 0.016, sp['armor'], n=22, segs=6)).scale = (1.0, 1.16, 1.0)
    if sp.get('pauldron'):
        for s, yy in enumerate((-0.112, 0.112)):
            p(blob(root, f'{tag}_ombreira{s}', 0.05, (0.0, yy, 0.37), (1.0, 0.9, 0.62), sp['pauldron']))
    if sp.get('fur'):
        p(torus(root, tag + '_golaPelo', (0, 0, 0.385), 0.075, 0.034, sp['fur'], n=20, segs=8)).scale = (1.0, 1.15, 0.8)
    if sp.get('scarf'):
        p(torus(root, tag + '_lenco', (0.0, 0, 0.392), 0.064, 0.026, sp['scarf'], n=20, segs=8)).scale = (1.0, 1.1, 0.9)
        tail = cloth_grid(root, tag + '_lencoPonta', 0.04, 0.13, 2, 6, [sp['scarf']], thick=0.014)
        p(tail).location = (-0.055, -0.03, 0.4)
        tail.rotation_euler = (0, 0, math.pi / 2)
        register_cloth(tail, hang_wave(0.13, amp=0.05, axis='Y', cycles=1, waves=0.6, top=0.0))
        parts['cloth'].append(tail)
    if sp.get('cape'):
        cp = cloth_grid(root, tag + '_capa', 0.2, 0.3, 4, 8, [sp['cape']], thick=0.014,
                        shape=lambda u, v, co: Vector((co.x, -0.025 * math.sin(math.pi * u), co.z)))
        p(cp).location = (-0.095, 0.1, 0.38)
        cp.rotation_euler = (0, 0, -math.pi / 2)
        register_cloth(cp, hang_wave(0.3, amp=0.05, axis='Y', cycles=1, waves=0.6, top=0.0))
        parts['cloth'].append(cp)
    # cabeca grande (pivo no pescoco)
    head = empty(root, tag + '_cabecaPivo', loc=(0, 0, 0.395), parent=body)
    parts['head'] = head

    def ph(o):
        o.parent = head
        return o
    R = sp.get('head_r', 0.13)
    s = R / 0.066
    hc = Vector((0.0, 0, R * 0.92))
    ph(blob(root, tag + '_cabeca', R, hc, (0.95, 1.0, 0.97), skin))
    eye_y = R * 0.36
    for k, yy in enumerate((-eye_y, eye_y)):
        ex = math.sqrt(max(0.0, R * R - yy * yy)) * 0.93
        ph(blob(root, f'{tag}_olho{k}', R * 0.17, hc + Vector((ex, yy, R * 0.02)), (0.45, 0.82, 1.2), P['p_eye']))
        ph(blob(root, f'{tag}_brilho{k}', R * 0.045, hc + Vector((ex + R * 0.06, yy - R * 0.03, R * 0.09)), (0.5, 1, 1), P['p_white']))
        if sp.get('brows', 'angry') == 'angry':
            ang = math.radians(-24 if yy > 0 else 24)
        else:
            ang = math.radians(8 if yy > 0 else -8)
        ph(box(root, f'{tag}_sobrancelha{k}', (R * 0.08, R * 0.3, R * 0.07), hc + Vector((ex - R * 0.02, yy * 1.05, R * 0.24)),
               rot=(ang, 0, 0), m=P['p_brow'], bev=0.004))
        if sp.get('blush', True) and not sp.get('mask'):
            ph(blob(root, f'{tag}_bochecha{k}', R * 0.17, hc + Vector((ex - R * 0.1, yy * 1.5, -R * 0.28)), (0.3, 1.0, 0.6), P['p_blush']))
    if not sp.get('mask'):
        ph(blob(root, tag + '_nariz', R * 0.14, hc + Vector((R * 0.97, 0, -R * 0.15)), (0.8, 0.9, 0.85), skin))
        ph(box(root, tag + '_boca', (R * 0.05, R * 0.3, R * 0.05), hc + Vector((R * 0.9, 0, -R * 0.43)), m=P['p_brow'], bev=0.003))
    hm = sp.get('head', 'bald')
    head_m = sp.get('head_m', top)
    if hm in ('wrap', 'hood'):
        def face_cut(c):
            ang = math.atan2(c.y, c.x)
            return abs(ang) < math.radians(74) and -0.62 * R < c.z < 0.48 * R and c.x > 0
        prof = [(-0.72 * R, 0.98 * R, 1.0 * R), (-0.38 * R, 1.08 * R, 1.1 * R), (0.0, 1.11 * R, 1.13 * R), (0.36 * R, 1.07 * R, 1.09 * R, -0.02 * R),
                (0.66 * R, 0.88 * R, 0.9 * R, -0.05 * R), (0.88 * R, 0.55 * R, 0.56 * R, -0.08 * R)]
        if hm == 'hood':
            prof += [(1.04 * R, 0.26 * R, 0.26 * R, -0.22 * R), (1.12 * R, 0.0, 0.0, -0.4 * R)]
        else:
            prof += [(0.99 * R, 0.0, 0.0, -0.08 * R)]
        hd = lathe(root, tag + '_capuz', prof, head_m, segs=20, lv=2, caps=False, solid=0.012, cut=face_cut)
        ph(hd).location = hc
        if sp.get('agal'):
            ph(torus(root, tag + '_agal', hc + Vector((-0.01 * R, 0, 0.5 * R)), 0.98 * R, 0.1 * R, sp['agal'], n=22, segs=6))
        if hm == 'wrap':
            # ponta do pano caindo atras da cabeca
            tl = cloth_grid(root, tag + '_panoPonta', 0.06, 0.14, 2, 6, [head_m], thick=0.014)
            ph(tl).location = hc + Vector((-0.95 * R, -0.03, 0.1 * R))
            tl.rotation_euler = (0, 0, math.pi / 2)
            register_cloth(tl, hang_wave(0.14, amp=0.04, axis='Y', cycles=1, waves=0.6, top=0.0))
            parts['cloth'].append(tl)
    elif hm == 'helmet':
        hl = lathe(root, tag + '_elmo', [(0.08 * R, 1.1 * R, 1.12 * R, -0.03 * R), (0.4 * R, 1.08 * R, 1.1 * R, -0.02 * R), (0.72 * R, 0.86 * R, 0.88 * R),
                                          (0.95 * R, 0.48 * R, 0.5 * R), (1.08 * R, 0.0, 0.0)], head_m, segs=20, lv=2, caps=False, solid=0.012)
        ph(hl).location = hc
        ph(torus(root, tag + '_elmoAba', hc + Vector((-0.02 * R, 0, 0.1 * R)), 1.1 * R, 0.07 * R, head_m, n=24, segs=6))
        if sp.get('cheek'):
            for k, yy in enumerate((-1, 1)):
                ph(blob(root, f'{tag}_jugular{k}', 0.035 * s, hc + Vector((0.02 * s, yy * 0.066 * s, -0.035 * s)), (0.8, 0.35, 1.2), head_m))
        if sp.get('crest'):
            crest = [hc + Vector(((-0.09 + 0.17 * t) * s, 0, (0.085 + 0.055 * math.sin(math.pi * t)) * s)) for t in [j / 10 for j in range(11)]]
            ph(tube(root, tag + '_crista', crest, 0.024 * s, sp['crest'], segs=8, rfun=lambda t: (0.03 - 0.016 * abs(t - 0.45)) * s))
        if sp.get('plume'):
            ph(tube(root, tag + '_pluma', [hc + Vector((-0.01 * s, 0, 0.1 * s)), hc + Vector((-0.04 * s, 0, 0.16 * s)), hc + Vector((-0.09 * s, 0, 0.17 * s))],
                    0.02 * s, sp['plume'], segs=8, rfun=lambda t: (0.024 * (1 - t) + 0.008) * s))
        if sp.get('horns'):
            for k, yy in enumerate((-1, 1)):
                pts = [hc + Vector((0.0, yy * 0.062 * s, 0.05 * s)), hc + Vector((0.01 * s, yy * 0.095 * s, 0.09 * s)),
                       hc + Vector((0.03 * s, yy * 0.1 * s, 0.135 * s))]
                ph(tube(root, f'{tag}_chifre{k}', pts, 0.018 * s, sp['horns'], segs=8, rfun=lambda t: (0.02 * (1 - t) + 0.004) * s))
    elif hm == 'turban':
        tm = head_m
        for j, (zz, rr_, tilt) in enumerate(((0.02, 0.078, 0.12), (0.05, 0.083, -0.1), (0.078, 0.07, 0.14))):
            t_ = torus(root, f'{tag}_turbante{j}', (0, 0, 0), rr_ * s, 0.017 * s, tm, n=22, segs=6)
            ph(t_).location = hc + Vector((-0.012 * s, 0, zz * s))
            t_.rotation_euler = (tilt, 0, 0)
        ph(blob(root, tag + '_turbanteTopo', 0.06 * s, hc + Vector((-0.01 * s, 0, 0.08 * s)), (1, 1, 0.7), tm))
    if sp.get('mask'):
        mk = lathe(root, tag + '_mascara', [(-0.8 * R, 0.96 * R, 0.98 * R), (-0.55 * R, 1.06 * R, 1.08 * R), (-0.34 * R, 1.08 * R, 1.1 * R), (-0.2 * R, 1.06 * R, 1.08 * R)],
                   sp['mask'], segs=20, lv=2, caps=False, solid=0.01)
        ph(mk).location = hc
    if sp.get('goggles'):
        for k, yy in enumerate((-eye_y, eye_y)):
            ph(torus(root, f'{tag}_oculos{k}', hc + Vector((0.02, yy, R * 0.72)), R * 0.2, R * 0.06, P['p_bronze'], axis='X', n=14, segs=6)).rotation_euler = (0, math.radians(-50), 0)
            ph(blob(root, f'{tag}_lente{k}', R * 0.17, hc + Vector((0.03, yy, R * 0.74)), (0.4, 1, 1), P['glass'])).rotation_euler = (0, math.radians(-50), 0)
    # membros (reconstruidos a cada pose) e maos
    for side in 'LR':
        for nm, m in (('coxa', pants), ('canela', pants), ('braco', parts['m']['sleeve']), ('antebraco', parts['m']['sleeve'])):
            o = ensure_mesh(root, f'{tag}_{nm}{side}', m)
            o.parent = body
            o['set'] = root['set']
            parts['limbs'][nm + side] = o
        parts['pe' + side] = p(blob(root, f'{tag}_pe{side}', 0.047, (0, 0, 0), (1.45, 0.95, 0.72), shoe))
        parts['luva' + side] = p(blob(root, f'{tag}_luva{side}', 0.038, (0, 0, 0), (1.1, 1.0, 1.05), parts['m']['glove']))
        parts['mao' + side] = empty(root, f'{tag}_mao{side}', parent=body)
    k = sp.get('big', 1.0)
    body.scale = (k, k, k)
    return parts


def hold2(parts, side, *objs):
    for o in objs:
        o.parent = parts['mao' + side]
    parts['props'].extend(objs)
    return objs


def attach(parts, objs, where='body'):
    for o in objs:
        o.parent = parts[where]
    return objs


def pose_chibi(parts, st):
    """st: face, lean, roll, yaw, offset, head_pitch/yaw/roll, ph (tecido), foot_L/R (tornozelo, local do corpo),
    hand_L/R, grip_L/R, pole_L/R, hide."""
    body = parts['body']
    k = parts['sp'].get('big', 1.0)
    body.scale = (k, k, k)
    body.rotation_euler = (st.get('roll', 0.0), st.get('lean', 0.0), st.get('face', VIEWS['r']) + st.get('yaw', 0.0))
    body.location = Vector(st.get('offset', (0, 0, 0)))
    parts['head'].rotation_euler = (st.get('head_roll', 0.0), st.get('head_pitch', 0.0), st.get('head_yaw', 0.0))
    ph = st.get('ph', 0.0)
    for c in parts['cloth']:
        base, fn = CLOTH[c.name]
        for v, b in zip(c.data.vertices, base):
            v.co = fn(b, ph)
        c.data.update()
    L = parts['limbs']
    m = parts['m']
    for side, yy in (('L', 0.052), ('R', -0.052)):
        hip = Vector((0.0, yy, 0.2))
        A = Vector(st.get('foot_' + side, (0.0, yy * 1.05, 0.045)))
        Kn, A2 = two_bone(hip, A, 0.09, 0.088, (1.0, 0.0, 0.2))
        set_mesh_tube(L['coxa' + side], [hip, hip.lerp(Kn, 0.5), Kn], 0.046, segs=10, rfun=lambda t: 0.048 - 0.006 * t)
        set_mesh_tube(L['canela' + side], [Kn, Kn.lerp(A2, 0.5), A2], 0.04, segs=10, rfun=lambda t: 0.041 - 0.004 * t)
        pe = parts['pe' + side]
        pe.location = A2 + Vector((0.026, 0, -0.02))
        pe.rotation_euler = (0, st.get('toe_' + side, 0.0), 0)
    sh = {'L': Vector((0.0, 0.112, 0.352)), 'R': Vector((0.0, -0.112, 0.352))}
    rest = {'L': (0.02, 0.15, 0.2), 'R': (0.02, -0.15, 0.2)}
    poles = {'L': (-0.4, 1.0, -0.5), 'R': (-0.4, -1.0, -0.5)}
    for side in 'LR':
        S = sh[side]
        H = Vector(st.get('hand_' + side, rest[side]))
        E, Hh = two_bone(S, H, 0.09, 0.088, st.get('pole_' + side, poles[side]))
        set_mesh_tube(L['braco' + side], [S, S.lerp(E, 0.5), E], 0.034, segs=10, rfun=lambda t: 0.036 - 0.006 * t)
        set_mesh_tube(L['antebraco' + side], [E, E.lerp(Hh, 0.5), Hh], 0.03, segs=10, rfun=lambda t: 0.03 + 0.004 * t)
        g = parts['luva' + side]
        hp = Hh + (Hh - E).normalized() * 0.022
        g.location = hp
        g.rotation_euler = (Hh - E).normalized().to_track_quat('X', 'Z').to_euler()
        hand = parts['mao' + side]
        hand.location = hp
        gd = Vector(st.get('grip_' + side, tuple(Hh - E)))
        hand.rotation_euler = gd.normalized().to_track_quat('Z', 'X').to_euler()
    hide = set(st.get('hide', ()))
    for o in parts['props']:
        hid = any(o.name.startswith(h) for h in hide)
        o.hide_render = o.hide_viewport = hid
        for ch in o.children_recursive:
            ch.hide_render = ch.hide_viewport = hid


def gait(ph, stride=0.1, lift=0.055, swing=0.1, bob=0.02, lean=0.12, arms=True):
    """Passada: pes vao e voltam (sobem no balanco), quadril sobe e desce, bracos balancam ao contrario das pernas."""
    a = TAU * ph
    st = {'lean': lean, 'ph': ph, 'yaw': 0.07 * math.cos(a), 'offset': (0, 0, bob * abs(math.sin(a)) - bob * 0.3),
          'head_pitch': -0.04 + 0.03 * math.sin(2 * a)}
    for side, s, yy in (('L', 0, 0.055), ('R', 1, -0.055)):
        b = a + s * math.pi
        x = stride * math.cos(b)
        z = 0.045 + lift * max(0.0, -math.sin(b)) - st['offset'][2]
        st['foot_' + side] = (x, yy, z)
        st['toe_' + side] = -0.35 * max(0.0, -math.sin(b)) + 0.15 * max(0.0, math.sin(b)) * (1 if x < 0 else 0)
        if arms:
            hy = 0.15 if side == 'L' else -0.15
            st['hand_' + side] = (0.02 - swing * math.cos(b), hy, 0.21 + 0.03 * max(0.0, -math.cos(b)))
    return st


def death(t, face):
    e = t * t * (3 - 2 * t)
    hop = 0.05 * math.sin(math.pi * min(1.0, t * 1.8))
    return {'face': face, 'lean': -1.45 * e, 'offset': (-0.1 * e, 0, hop), 'ph': t, 'head_pitch': 0.35 * e,
            'hand_L': (-0.02 - 0.12 * e, 0.17, 0.3 + 0.16 * e), 'hand_R': (-0.02 - 0.12 * e, -0.17, 0.3 + 0.16 * e),
            'foot_L': (0.03 + 0.08 * e, 0.06, 0.045 + 0.03 * e), 'foot_R': (-0.02 + 0.06 * e, -0.06, 0.045)}


def humanoid(key, label, builder, states, boost=EN_BOOST, margin=(0.08, 0.08, 0.1, 0.06)):
    """states(mode, f, view) -> st (sem 'face'); modos: walk (r/u/d), atk e die."""
    def mk(mode, view):
        def fn(parts, P, root, f):
            st = states(mode, f, view)
            st.setdefault('face', VIEWS[view])
            pose_chibi(parts, st)
        return fn
    modes = [('r', WALK_N, mk('walk', 'r')), ('u', WALK_N, mk('walk', 'u')), ('d', WALK_N, mk('walk', 'd')),
             ('a', ATK_N, mk('atk', 'r')), ('x', DIE_N, mk('die', 'r'))]
    return {'key': key, 'label': label, 'build': builder, 'boost': boost, 'margin': margin,
            'pose0': lambda parts, P, root: pose_chibi(parts, dict(states('walk', 0, 'r'), face=VIEWS['r'])),
            'modes': modes}


# ---------------------------------------------------------------- armas e objetos (construidos ao longo de +Z, empunhadura em z=0)
def sabre(root, P, tag, length=0.2, m=None):
    grip = tube(root, f'{tag}_cabo', [(0, 0, -0.03), (0, 0, 0.03)], 0.013, P['p_leather'], segs=6)
    guard = box(root, f'{tag}_guarda', (0.014, 0.055, 0.014), (0, 0, 0.036), m=P['p_gold'], bev=0.005)
    pts = [(0.0, 0, 0.04), (0.012, 0, 0.04 + length * 0.4), (0.032, 0, 0.04 + length * 0.75), (0.065, 0, 0.04 + length)]
    blade = tube(root, f'{tag}_lamina', pts, 0.02, m or P['p_metal'], segs=8, rfun=lambda t: 0.022 * (1 - 0.6 * t) + 0.005)
    blade.scale = (1.0, 0.32, 1.0)
    return grip, guard, blade


def mace(root, P, tag):
    h = tube(root, f'{tag}_cabo', [(0, 0, -0.04), (0, 0, 0.12)], 0.012, P['p_wood'], segs=6)
    hd = blob(root, f'{tag}_cabeca', 0.038, (0, 0, 0.14), (1, 1, 1), P['p_bronze'])
    spikes = [blob(root, f'{tag}_cravo{i}', 0.014, (0.035 * math.cos(i * 1.57), 0.035 * math.sin(i * 1.57), 0.14), (1, 1, 1), P['p_gold']) for i in range(4)]
    return (h, hd, *spikes)


def round_shield(root, P, tag, r=0.15, m=None, emblem=None, rim=None):
    """Escudo redondo no plano XY local (frente para +Z), preso pela empunhadura no centro."""
    d = lathe(root, f'{tag}_escudo', [(0.0, r, r), (0.02, r * 0.97, r * 0.97), (0.035, r * 0.75, r * 0.75), (0.045, 0.0, 0.0)],
              m or P['p_bronze'], segs=28, lv=2, caps=True)
    out = [d, torus(root, f'{tag}_escudoAro', (0, 0, 0.01), r, 0.014, rim or P['p_gold'], n=32, segs=6)]
    if emblem:
        out.append(blob(root, f'{tag}_escudoSol', r * 0.28, (0, 0, 0.046), (1, 1, 0.35), emblem))
        for i in range(8):
            a = i * TAU / 8
            out.append(blob(root, f'{tag}_escudoRaio{i}', r * 0.07, (math.cos(a) * r * 0.42, math.sin(a) * r * 0.42, 0.042), (1.6, 0.8, 0.35), emblem,
                            rot=(0, 0, a)))
    return out


def recurve_bow(root, P, tag):
    pts = [(0.0, 0.02 * math.sin(math.pi * t) - 0.0, -0.16 + 0.32 * t) for t in [i / 10 for i in range(11)]]
    pts = [(0.03 * math.sin(math.pi * (z + 0.16) / 0.32) - 0.012 * math.sin(2 * math.pi * (z + 0.16) / 0.32), 0, z) for (_, _, z) in pts]
    limb = tube(root, f'{tag}_arco', pts, 0.012, P['p_wood'], segs=6, rfun=lambda t: 0.013 - 0.005 * abs(t - 0.5))
    string = tube(root, f'{tag}_corda', [(-0.01, 0, -0.155), (-0.01, 0, 0.155)], 0.0025, P['p_cream'], segs=4)
    return limb, string


def quiver(root, P, tag, m):
    q = cyl(root, f'{tag}_aljava', 0.038, 0.17, (0, 0, 0), m=m, v=14, bev=0.006)
    tips = [tube(root, f'{tag}_pena{i}', [(0.012 * math.cos(i * 2.1), 0.012 * math.sin(i * 2.1), 0.085), (0.012 * math.cos(i * 2.1), 0.012 * math.sin(i * 2.1), 0.13)],
                 0.009, P['p_coral'], segs=5) for i in range(3)]
    return (q, *tips)


def clay_pot_p(root, P, tag, s=1.0):
    b = lathe(root, f'{tag}_pote', scaled([(0.0, 0.02, 0.02), (0.015, 0.034, 0.034), (0.035, 0.036, 0.036), (0.05, 0.022, 0.022), (0.058, 0.016, 0.016)], s),
              P['p_cream'], segs=14, lv=2)
    lid = blob(root, f'{tag}_tampa', 0.019 * s, (0, 0, 0.062 * s), (1, 1, 0.6), P['p_pink'])
    return b, lid


def staff_swirl(root, P, tag):
    pts = [(0.012 * math.sin(t * 9), 0.012 * math.cos(t * 9), -0.12 + 0.48 * t) for t in [i / 16 for i in range(17)]]
    shaft = tube(root, f'{tag}_cajado', pts, 0.013, P['p_lilac'], segs=6)
    sw = [(0.045 * (1 - t * 0.7) * math.cos(t * 11), 0.045 * (1 - t * 0.7) * math.sin(t * 11), 0.38 + 0.08 * t) for t in [i / 24 for i in range(25)]]
    swirl = tube(root, f'{tag}_espiral', sw, 0.011, P['p_sand_glow'], segs=6, rfun=lambda t: 0.012 * (1 - 0.5 * t))
    return shaft, swirl


def great_axe(root, P, tag):
    h = tube(root, f'{tag}_cabo', [(0, 0, -0.12), (0, 0, 0.3)], 0.016, P['p_wood'], segs=8)
    bl = lathe(root, f'{tag}_lamina', [(0.0, 0.0, 0.0), (0.02, 0.09, 0.01), (0.08, 0.11, 0.012), (0.14, 0.09, 0.01), (0.16, 0.0, 0.0)],
               P['p_metal'], segs=16, lv=1, caps=True)
    bl.location = (0.0, 0.0, 0.17)
    bl.scale = (1.0, 0.3, 1.0)
    bl.rotation_euler = (0, 0, 0)
    gem = blob(root, f'{tag}_gema', 0.02, (0.02, 0, 0.25), (1, 0.6, 1), P['p_mint'])
    return h, bl, gem


# ---------------------------------------------------------------- SAQUEADOR
def build_raider(P, root):
    pr = build_chibi(P, root, dict(top=P['p_coral'], pants=P['p_cream'], vest=P['p_tan'], sash=P['p_lilac'], skirt=0.17,
                                   head='wrap', head_m=P['p_mint'], mask=P['p_mint'], agal=P['p_lilac'], shoe=P['p_leather']))
    hold2(pr, 'R', *sabre(root, P, root['set']))
    return pr


def raider_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N)
        st['grip_R'] = (0.7, 0.0, 0.7)
        return st
    if mode == 'atk':
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.8))
        hit = max(0.0, (t - 0.45) / 0.55)
        return {'lean': 0.05 + 0.22 * hit - 0.08 * up, 'ph': t, 'hand_R': (0.06 + 0.16 * hit - 0.05 * up, -0.14, 0.24 + 0.24 * up - 0.12 * hit),
                'grip_R': (0.2 + 0.9 * hit, 0, 1.0 - 0.8 * hit), 'hand_L': (0.08, 0.15, 0.24),
                'foot_L': (0.06, 0.055, 0.045), 'foot_R': (-0.05, -0.055, 0.045)}
    return death(f / (DIE_N - 1), VIEWS['r'])


# ---------------------------------------------------------------- ATIRADOR NOMADE
def build_nomad(P, root):
    tag = root['set']
    pr = build_chibi(P, root, dict(top=P['p_sky'], pants=P['p_sky'], robe=P['p_sky'], head='hood', head_m=P['p_sky'], scarf=P['p_butter'],
                                   belt=P['p_tan'], glove=P['p_leather'], shoe=P['p_leather'], brows='angry'))
    hold2(pr, 'L', *recurve_bow(root, P, tag))
    q = quiver(root, P, tag, P['p_tan'])
    for o in q:
        o.parent = pr['body']
    q[0].location = (-0.1, 0.03, 0.3)
    q[0].rotation_euler = (math.radians(-20), math.radians(-25), 0)
    for o in q[1:]:
        o.parent = q[0]
    return pr


def nomad_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N, stride=0.07)
        st['hand_L'] = (0.06, 0.15, 0.24)
        st['grip_L'] = (0.2, 0.3, 1.0)
        return st
    if mode == 'atk':
        # puxa a corda e solta (quadro 4)
        t = f / (ATK_N - 1)
        draw = min(1.0, t / 0.6) if t < 0.65 else max(0.0, 1 - (t - 0.65) / 0.2)
        return {'lean': 0.02, 'ph': t, 'hand_L': (0.2, 0.08, 0.33), 'grip_L': (0.0, 0.0, 1.0), 'pole_L': (0.0, 1.0, -0.3),
                'hand_R': (0.17 - 0.12 * draw, -0.02, 0.33), 'pole_R': (-0.5, -1.0, 0.2),
                'foot_L': (0.07, 0.06, 0.045), 'foot_R': (-0.05, -0.06, 0.045), 'head_yaw': 0.1}
    return death(f / (DIE_N - 1), VIEWS['r'])


# ---------------------------------------------------------------- XAMA DAS DUNAS
def build_shaman(P, root):
    tag = root['set']
    pr = build_chibi(P, root, dict(top=P['p_teal'], robe=P['p_teal'], head='hood', head_m=P['p_teal'], scarf=None, sash=P['p_lilac'],
                                   skin=P['p_skin2'], brows='calm', head_r=0.11))
    hold2(pr, 'R', *staff_swirl(root, P, tag))
    for i in range(7):
        a = -0.8 + i * 0.27
        b = blob(root, f'{tag}_conta{i}', 0.015, (0.09 * math.cos(a), 0.09 * math.sin(a), 0.36 - 0.02 * math.cos(a * 2)), (1, 1, 1), P['p_lilac'])
        b.parent = pr['body']
    return pr


def shaman_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N, stride=0.055, lift=0.03, lean=0.22, swing=0.04)
        st['hand_R'] = (0.12, -0.13, 0.25)
        st['grip_R'] = (0.15, 0.0, 1.0)
        return st
    if mode == 'atk':
        # ergue o cajado e cura
        t = f / (ATK_N - 1)
        k = math.sin(math.pi * t)
        return {'lean': 0.18 - 0.2 * k, 'ph': t, 'hand_R': (0.12, -0.12, 0.25 + 0.16 * k), 'grip_R': (0.1, 0, 1.0),
                'hand_L': (0.1 + 0.06 * k, 0.15, 0.24 + 0.2 * k), 'head_pitch': -0.25 * k}
    return death(f / (DIE_N - 1), VIEWS['r'])


# ---------------------------------------------------------------- PORTA-ESCUDO
def build_bulwark(P, root):
    tag = root['set']
    pr = build_chibi(P, root, dict(top=P['p_sage'], pants=P['p_cream'], belt=P['p_tan'], skirt=0.14, head='helmet', head_m=P['p_bronze'],
                                   cheek=True, plume=P['p_coral'], shoe=P['p_leather'], big=1.08))
    sh = round_shield(root, P, tag, r=0.17, m=P['p_bronze'], emblem=P['p_butter'], rim=P['p_gold'])
    hold2(pr, 'L', *sh)
    hold2(pr, 'R', *mace(root, P, tag))
    return pr


def bulwark_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N, stride=0.06, lift=0.035, bob=0.012)
        st['hand_L'] = (0.15, 0.06, 0.26)
        st['grip_L'] = (1.0, 0.1, 0.1)
        st['pole_L'] = (-0.2, 1.0, -0.6)
        st['grip_R'] = (0.6, 0.0, 0.8)
        return st
    if mode == 'atk':
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.8))
        hit = max(0.0, (t - 0.45) / 0.55)
        return {'lean': 0.06 + 0.15 * hit, 'ph': t, 'hand_L': (0.16, 0.06, 0.26), 'grip_L': (1.0, 0.1, 0.1),
                'hand_R': (0.05 + 0.12 * hit, -0.14, 0.24 + 0.25 * up - 0.1 * hit), 'grip_R': (0.2 + 0.9 * hit, 0, 1.0 - 0.8 * hit)}
    st = death(f / (DIE_N - 1), VIEWS['r'])
    st['grip_L'] = (1.0, 0.1, 0.3)
    return st


# ---------------------------------------------------------------- SABOTADOR
def build_saboteur(P, root):
    tag = root['set']
    pr = build_chibi(P, root, dict(top=P['p_plum'], pants=P['p_mauve'], head='hood', head_m=P['p_plum'], goggles=True,
                                   scarf=P['p_stripe'], belt=P['p_tan'], shoe=P['p_leather'], head_r=0.122))
    bag = blob(root, f'{tag}_bolsa', 0.07, (-0.02, 0.12, 0.2), (0.7, 0.45, 0.8), P['p_mint'])
    bag.parent = pr['body']
    strap = tube(root, f'{tag}_alca', [(-0.06, 0.1, 0.25), (-0.02, 0.0, 0.37), (0.06, -0.09, 0.36)], 0.012, P['p_mint'], segs=6)
    strap.parent = pr['body']
    for i, (x, z) in enumerate(((-0.03, 0.26), (0.02, 0.27))):
        b, lid = clay_pot_p(root, P, f'{tag}_poteBolsa{i}', 0.8)
        for o in (b, lid):
            o.parent = bag
        b.location = (x / 0.7, 0.05, (z - 0.2) / 0.8)
        lid.location = b.location + Vector((0, 0, 0.05))
    pot = clay_pot_p(root, P, f'{tag}_poteMao')
    hold2(pr, 'R', *pot)
    return pr


def saboteur_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N, stride=0.075, lean=0.18, bob=0.02)
        st['hand_R'] = (0.08, -0.15, 0.22)
        st['grip_R'] = (0.0, 0.0, 1.0)
        return st
    if mode == 'atk':
        # arremesso por cima (solta no quadro 4)
        t = f / (ATK_N - 1)
        back = math.sin(math.pi * min(1.0, t / 0.6))
        fwd = max(0.0, (t - 0.55) / 0.45)
        return {'lean': 0.05 - 0.12 * back + 0.25 * fwd, 'ph': t, 'hand_R': (-0.06 * back + 0.2 * fwd, -0.12, 0.3 + 0.18 * back),
                'grip_R': (0.0, 0.0, 1.0), 'hand_L': (0.14, 0.12, 0.28), 'hide': ('poteMao',) if fwd > 0.3 else (),
                'foot_L': (0.07, 0.06, 0.045), 'foot_R': (-0.05, -0.06, 0.045)}
    return death(f / (DIE_N - 1), VIEWS['r'])


# ---------------------------------------------------------------- GUERREIRO DE BRONZE
def build_brute(P, root):
    tag = root['set']
    pr = build_chibi(P, root, dict(top=P['p_slate'], pants=P['p_slate'], armor=P['p_rosegold'], pauldron=P['p_rosegold'], fur=P['p_fur'],
                                   head='helmet', head_m=P['p_rosegold'], horns=P['p_cream'], belt=P['p_tan'], shoe=P['p_leather'],
                                   glove=P['p_cream'], big=1.35, head_r=0.112))
    hold2(pr, 'R', *great_axe(root, P, tag))
    return pr


def brute_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N, stride=0.07, lift=0.035, bob=0.02, lean=0.12, swing=0.04)
        st['hand_R'] = (0.12, -0.14, 0.24)
        st['grip_R'] = (0.35, 0.0, 0.9)
        st['hand_L'] = (0.1, 0.0, 0.24)
        return st
    if mode == 'atk':
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.6))
        hit = max(0.0, (t - 0.5) / 0.5)
        return {'lean': 0.05 + 0.3 * hit - 0.1 * up, 'ph': t, 'hand_R': (0.04 + 0.2 * hit, -0.06, 0.26 + 0.3 * up - 0.14 * hit),
                'grip_R': (-0.3 + 1.4 * hit, 0, 1.0 - 0.9 * hit), 'hand_L': (0.06 + 0.18 * hit, 0.0, 0.26 + 0.28 * up - 0.14 * hit),
                'foot_L': (0.08, 0.06, 0.045), 'foot_R': (-0.06, -0.06, 0.045)}
    return death(f / (DIE_N - 1), VIEWS['r'])


# ---------------------------------------------------------------- KADDAR, O SENHOR DA GUERRA (chefe)
def build_warlord(P, root):
    tag = root['set']
    pr = build_chibi(P, root, dict(top=P['p_teal'], pants=P['p_teal'], armor=P['p_gold'], pauldron=P['p_gold'], cape=P['p_rose'],
                                   head='helmet', head_m=P['p_gold'], crest=P['p_cream'], cheek=True, belt=P['p_rose'], skirt=0.13,
                                   skirt_m=P['p_rose'], shoe=P['p_leather'], glove=P['p_cream'], big=1.9, head_r=0.11))
    hold2(pr, 'R', *sabre(root, P, tag, length=0.26))
    hold2(pr, 'L', *round_shield(root, P, f'{tag}_e', r=0.12, m=P['p_teal'], emblem=P['p_gold'], rim=P['p_gold']))
    return pr


def warlord_states(mode, f, view):
    if mode == 'walk':
        st = gait(f / WALK_N, stride=0.07, lift=0.035, bob=0.014, lean=0.06, swing=0.05)
        st['hand_L'] = (0.12, 0.1, 0.25)
        st['grip_L'] = (1.0, 0.2, 0.1)
        st['grip_R'] = (0.5, 0.0, 0.9)
        return st
    if mode == 'atk':
        # golpe no chao (onda de choque no jogo)
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t * 1.6))
        hit = max(0.0, (t - 0.5) / 0.5)
        return {'lean': 0.3 * hit - 0.12 * up, 'ph': t, 'offset': (0, 0, 0.03 * up), 'hand_R': (0.05 + 0.18 * hit, -0.12, 0.26 + 0.3 * up - 0.2 * hit),
                'grip_R': (-0.2 + 1.3 * hit, 0, 1.0 - 1.1 * hit), 'hand_L': (0.12, 0.1, 0.25), 'grip_L': (1.0, 0.2, 0.1),
                'foot_L': (0.08, 0.06, 0.045 + 0.03 * up), 'foot_R': (-0.06, -0.06, 0.045)}
    return death(f / (DIE_N - 1), VIEWS['r'])


SPEC = {
    'crews': [
        humanoid('raider', 'Saqueador', build_raider, raider_states),
        humanoid('nomad', 'Atirador Nomade', build_nomad, nomad_states),
        humanoid('shaman', 'Xama das Dunas', build_shaman, shaman_states),
        humanoid('bulwark', 'Porta-Escudo', build_bulwark, bulwark_states),
        humanoid('saboteur', 'Sabotador', build_saboteur, saboteur_states),
        humanoid('brute', 'Guerreiro de Bronze', build_brute, brute_states),
        humanoid('warlord', 'Kaddar', build_warlord, warlord_states),
    ],
}


if __name__ == '__main__':
    # a paleta pastel entra por cima da do lib (so neste processo)
    lib.palette2 = pastel
    main(FAM, SPEC)
