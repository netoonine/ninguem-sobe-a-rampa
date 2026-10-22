"""Pecas comuns das torres de vila da mata (Guardioes da Mata): palafitas (estacas, paredes de tabua, telhado de
palha), portas de esteira, escadinhas, escudos trancados, chapeu de palha dos guardioes, a samauma (sumauma) com
sementes douradas que brilham, barcos de feira, cestos de frutas e fogueira de pedra.

Usado por torre_quartel.py, torre_estandarte.py e torre_mercado.py. Tudo no padrao das familias (lib.py):
objetos filhos da raiz do conjunto, Z para cima, frente da torre para -Y.
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise
from lib import (TAU, mat, glow_mat, box, cyl, sphere, tube, torus, lathe, bm_to_obj, empty, kids, register_anim, cloth_grid,
                 register_cloth, flag_wave, hang_wave, bob, spin, GLOW_MATS)


def vmats():
    """Materiais da vila (chaves curtas)."""
    return {
        'thatch': mat('palha_telhado', '#c4954e', rough=0.95, var=0.1, bump=0.9),
        'thatch_d': mat('palha_telhado_esc', '#9e7438', rough=0.95, var=0.1, bump=0.9),
        'thatch_l': mat('palha_telhado_cl', '#dcb46a', rough=0.95, var=0.1, bump=0.9),
        'plank': mat('tabua_vila', '#b27a48', rough=0.78, var=0.16, bump=0.3),
        'plank_l': mat('tabua_vila_cl', '#c99a62', rough=0.78, var=0.14, bump=0.3),
        'plank_d': mat('tabua_vila_esc', '#8a5a36', rough=0.8, var=0.12, bump=0.3),
        'stilt': mat('estaca_vila', '#6e4a30', rough=0.85, var=0.1, bump=0.4),
        'mat': mat('esteira', '#c9a06a', rough=0.9, var=0.0, bump=0.35, stripes=(14.0, '#d8b47a', '#a87a48')),
        'rope': mat('corda_vila', '#dcc290', rough=0.9, var=0.05, bump=0.4),
        'leaf': mat('folha_vila', '#5e9e3e', rough=0.7, var=0.12, bump=0.05, sheen=0.3),
        'leaf_d': mat('folha_vila_esc', '#3f7a34', rough=0.7, var=0.12, bump=0.05, sheen=0.3),
        'leaf_l': mat('folha_vila_cl', '#8cc152', rough=0.7, var=0.1, bump=0.05, sheen=0.3),
        'moss': mat('musgo_vila', '#7fae46', rough=0.9, var=0.15, bump=0.4),
        'bark': mat('casca_samauma', '#9a8a76', rough=0.88, var=0.1, bump=0.55),
        'bark_l': mat('casca_samauma_cl', '#b3a48e', rough=0.88, var=0.1, bump=0.5),
        'stone': mat('pedra_rio_vila', '#a7a397', rough=0.8, var=0.16, bump=0.25),
        'water': mat('agua_igarape', '#3f9a90', rough=0.06, var=0.02, bump=0.05),
        'water_l': mat('agua_igarape_cl', '#8fd0c0', rough=0.05, var=0.0, bump=0.02),
        'acai': mat('acai', '#4a2a5a', rough=0.45, var=0.08, bump=0.05),
        'banana': mat('banana', '#f2c84a', rough=0.55, var=0.06, bump=0.05),
        'cupuacu': mat('cupuacu', '#8a5a36', rough=0.8, var=0.08, bump=0.4),
        'orange': mat('fruta_laranja', '#f08a2c', rough=0.6, var=0.05, bump=0.1),
        'red': mat('fruta_vermelha', '#d8443a', rough=0.55, var=0.05, bump=0.05),
        'nut': mat('castanha_ourico', '#7a4a2a', rough=0.85, var=0.08, bump=0.5),
        'seed': glow_mat('semente_dourada', '#ffd25a', 1.6, 10.0, rough=0.4, var=0.03, bump=0.0),
        'fly': glow_mat('vaga_lume', '#e8ff8a', 3.5, 12.0, rough=0.5, var=0.0, bump=0.0),
        'jar': mat('vidro_pote', '#cfe8c8', rough=0.1, var=0.0, bump=0.0),
    }


# ---------------------------------------------------------------- palafita
def stilts(root, tag, V, pts, z0, z1, r=0.035, braces=True):
    for k, (x, y) in enumerate(pts):
        tube(root, f'{tag}_estaca{k}', [(x, y, z0 - 0.02), (x, y, z1)], r, V['stilt'], segs=8, rfun=lambda t: r * (1.08 - 0.12 * t))
        torus(root, f'{tag}_amarra{k}', (x, y, z1 - 0.05), r + 0.012, 0.01, V['rope'], n=12, segs=5)
    if braces and len(pts) >= 2:
        for k in range(len(pts)):
            (x0, y0), (x1, y1) = pts[k], pts[(k + 1) % len(pts)]
            if math.hypot(x1 - x0, y1 - y0) > 0.9:
                continue
            tube(root, f'{tag}_mao{k}', [(x0, y0, z0 + 0.03), (x1, y1, z1 - 0.06)], r * 0.55, V['stilt'], segs=6)


def deck_rect(root, tag, V, cx, cy, w, d, z, ang=0.0, rr=None):
    """Assoalho de tabuas (topo em z)."""
    rr = rr or random.Random(3)
    n = max(3, int(w / 0.12))
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(n):
        x = -w / 2 + w * (k + 0.5) / n
        box(root, f'{tag}_tabua{k}', (w / n * 0.92, d, 0.045), (cx + x * ca, cy + x * sa, z - 0.022 + rr.uniform(-0.003, 0.003)),
            rot=(0, 0, ang + rr.uniform(-0.01, 0.01)), m=V['plank'] if k % 2 else V['plank_l'], bev=0.01)
    box(root, f'{tag}_viga', (w, d * 0.9, 0.05), (cx, cy, z - 0.07), rot=(0, 0, ang), m=V['plank_d'], bev=0.01)


def deck_round(root, tag, V, cx, cy, R, z, rr=None):
    rr = rr or random.Random(4)
    n = max(5, int(R * 12))
    w = 2 * R / n
    for k in range(n):
        y = -R + w * (k + 0.5)
        half = math.sqrt(max(0.0, R * R - y * y)) * 0.98
        box(root, f'{tag}_tabua{k}', (half * 2, w * 0.9, 0.05), (cx + rr.uniform(-0.01, 0.01), cy + y, z - 0.025), rot=(0, 0, rr.uniform(-0.012, 0.012)),
            m=V['plank'] if k % 2 else V['plank_l'], bev=0.012)
    torus(root, f'{tag}_viga', (cx, cy, z - 0.065), R * 0.97, 0.04, V['plank_d'], n=40, segs=8)


def plank_box(root, tag, V, cx, cy, w, d, z0, h, faces=('front', 'left', 'right', 'back'), ripa=0.11, skip=None):
    """Parede de tabuas verticais em volta de um miolo (frente = -Y)."""
    box(root, tag + '_miolo', (w - 0.02, d - 0.02, h), (cx, cy, z0 + h / 2), m=V['plank_d'], bev=0.01)
    for f in faces:
        L = w if f in ('front', 'back') else d
        n = max(2, int(L / ripa))
        for k in range(n):
            u = -L / 2 + L * (k + 0.5) / n
            if skip and skip(f, u):
                continue
            if f == 'front':
                loc, rot = (cx + u, cy - d / 2, z0 + h / 2), 0
            elif f == 'back':
                loc, rot = (cx + u, cy + d / 2, z0 + h / 2), 0
            elif f == 'left':
                loc, rot = (cx - w / 2, cy + u, z0 + h / 2), math.pi / 2
            else:
                loc, rot = (cx + w / 2, cy + u, z0 + h / 2), math.pi / 2
            box(root, f'{tag}_ripa{f}{k}', (L / n * 0.94, 0.035, h * (1 - 0.03 * (k % 2))), loc, rot=(0, 0, rot), m=V['plank'] if k % 2 else V['plank_l'], bev=0.008)


def round_wall(root, tag, V, cx, cy, r, z0, h, n=22, door_ang=-math.pi / 2, door_w=0.3):
    """Parede redonda de tabuas verticais com um vao de porta."""
    cyl(root, tag + '_miolo', r - 0.02, h, (cx, cy, z0 + h / 2), m=V['plank_d'], v=32, bev=0.0)
    for k in range(n):
        a = TAU * k / n
        if abs(math.atan2(math.sin(a - door_ang), math.cos(a - door_ang))) < door_w / r / 2:
            continue
        box(root, f'{tag}_ripa{k}', (TAU * r / n * 0.92, 0.04, h * (1 - 0.04 * (k % 2))), (cx + r * math.cos(a), cy + r * math.sin(a), z0 + h / 2),
            rot=(0, 0, a + math.pi / 2), m=V['plank'] if k % 2 else V['plank_l'], bev=0.01)
    for z in (z0 + h * 0.15, z0 + h * 0.85):
        torus(root, f'{tag}_cinta{z:.2f}', (cx, cy, z), r + 0.025, 0.014, V['rope'], n=40, segs=5)


def leaf_band(root, tag, V, cx, cy, r, z, n=14, colors=None, front_only=True):
    """Faixa decorativa de folhinhas pintadas em volta da parede (motivo de folha, sem grafismo)."""
    cols = colors or [V['leaf'], V['leaf_l']]
    for k in range(n):
        a = TAU * k / n
        if front_only and math.sin(a) > 0.25:
            continue
        lf = sphere(root, f'{tag}_folhinha{k}', 0.045, (cx + (r + 0.03) * math.cos(a), cy + (r + 0.03) * math.sin(a), z), scale=(1.5, 0.35, 0.7),
                    m=cols[k % len(cols)], seg=10, rot=(0, 0.6 if k % 2 else -0.6, a + math.pi / 2))


def leaf_band_flat(root, tag, V, x0, x1, y, z, n=7, colors=None):
    cols = colors or [V['leaf'], V['leaf_l']]
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n
        sphere(root, f'{tag}_folhinha{k}', 0.045, (x, y - 0.012, z), scale=(1.5, 0.35, 0.7), m=cols[k % len(cols)], seg=10, rot=(0, 0.6 if k % 2 else -0.6, 0))


def thatch_cone(root, tag, V, cx, cy, r_bot, z_bot, h, r_top=0.0, fringe=True, m=None):
    """Telhado de palha conico (r_top > 0: anel aberto no alto, a 'saia' de palha do conceito)."""
    def wob(a, z):
        return 0.03 * math.sin(a * 23) + 0.02 * noise.noise(Vector((math.cos(a) * 3, math.sin(a) * 3, z * 5)))
    prof = [(0.0, r_bot, r_bot), (h * 0.5, (r_bot + r_top) / 2 + 0.03, (r_bot + r_top) / 2 + 0.03), (h, max(r_top, 0.0), max(r_top, 0.0))]
    if r_top <= 0:
        prof[-1] = (h, 0.0, 0.0)
    o = lathe(root, tag, prof, m or V['thatch'], segs=40, wobble=wob, lv=1, caps=False, solid=0.04)
    o.location = (cx, cy, z_bot)
    if fringe:
        for k in range(30):
            a = TAU * k / 30
            sphere(root, f'{tag}_franja{k}', 0.06, (cx + (r_bot - 0.01) * math.cos(a), cy + (r_bot - 0.01) * math.sin(a), z_bot - 0.025),
                   scale=(1.3, 0.5, 0.9), m=V['thatch_d'] if k % 2 else V['thatch'], seg=8, rot=(0, 0, a + math.pi / 2))
    rows = 3
    for j in range(rows):
        t = (j + 0.6) / (rows + 0.4)
        rz = z_bot + h * t
        rr_ = r_bot + (max(r_top, 0.0) - r_bot) * t + 0.035
        if rr_ > 0.03:
            torus(root, f'{tag}_fileira{j}', (cx, cy, rz), rr_, 0.028, V['thatch_d'] if j % 2 else V['thatch_l'], n=48, segs=6)
    if r_top > 0:
        torus(root, tag + '_aroTopo', (cx, cy, z_bot + h), r_top + 0.01, 0.03, V['rope'], n=36, segs=6)
    return o


def thatch_gable(root, tag, V, cx, cy, w, d, z_eave, h, ang=0.0):
    """Telhado de palha em duas aguas (cumeeira ao longo de X), com espessura e uma tora na cumeeira."""
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda x, y, z: (cx + x * ca - y * sa, cy + x * sa + y * ca, z)
    bm = bmesh.new()
    ridge = [bm.verts.new(P(x, 0, z_eave + h)) for x in (-w / 2, w / 2)]
    for sy in (-1, 1):
        eave = [bm.verts.new(P(x, sy * d / 2, z_eave)) for x in (-w / 2 - 0.04, w / 2 + 0.04)]
        bm.faces.new((ridge[0], ridge[1], eave[1], eave[0]) if sy < 0 else (ridge[1], ridge[0], eave[0], eave[1]))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True)
    for v in bm.verts:
        v.co.z += 0.012 * noise.noise(v.co * 6)
    roof = bm_to_obj(bm, tag, root, [V['thatch']], angle=89)
    sm = roof.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.07
    tube(root, tag + '_cumeeira', [P(-w / 2 - 0.06, 0, z_eave + h + 0.03), P(w / 2 + 0.06, 0, z_eave + h + 0.03)], 0.035, V['stilt'], segs=8)
    for sy in (-1, 1):
        for j in range(3):
            t = (j + 0.6) / 3.4
            y_ = sy * d / 2 * (1 - t)
            z_ = z_eave + h * t + 0.09
            tube(root, f'{tag}_fileira{sy}{j}', [P(-w / 2 - 0.03, y_, z_), P(w / 2 + 0.03, y_, z_)], 0.026, V['thatch_d'] if j % 2 else V['thatch_l'], segs=6)
    for sy in (-1, 1):
        for k in range(9):
            x = -w / 2 + w * (k + 0.5) / 9
            sphere(root, f'{tag}_franja{sy}{k}', 0.055, P(x, sy * (d / 2 + 0.01), z_eave - 0.02), scale=(1.4, 0.6, 0.8),
                   m=V['thatch_d'] if k % 2 else V['thatch'], seg=8, rot=(0, 0, ang))
    return roof


def mat_door(root, tag, V, x, y, z0, w=0.26, h=0.36, ang=0.0, frame=True):
    """Porta de esteira trancada (voltada para -Y)."""
    d = box(root, tag, (w, 0.03, h), (x, y - 0.015, z0 + h / 2), rot=(0, 0, ang), m=V['mat'], bev=0.008)
    if frame:
        ca, sa = math.cos(ang), math.sin(ang)
        for sx in (-1, 1):
            tube(root, f'{tag}_batente{sx}', [(x + sx * (w / 2 + 0.02) * ca, y - 0.03 + sx * (w / 2 + 0.02) * sa, z0),
                                              (x + sx * (w / 2 + 0.02) * ca, y - 0.03 + sx * (w / 2 + 0.02) * sa, z0 + h + 0.04)], 0.022, V['stilt'], segs=6)
        tube(root, f'{tag}_verga', [(x - (w / 2 + 0.05) * ca, y - 0.03 - (w / 2 + 0.05) * sa, z0 + h + 0.04),
                                    (x + (w / 2 + 0.05) * ca, y - 0.03 + (w / 2 + 0.05) * sa, z0 + h + 0.04)], 0.022, V['stilt'], segs=6)
    return d


def steps(root, tag, V, x, y, z_top, z_bot=0.13, n=3, w=0.3, dy=-0.1, ang=0.0):
    """Escadinha de tabuas descendo para a frente (-Y)."""
    for k in range(n):
        t = (k + 1) / (n + 1)
        z = z_top + (z_bot - z_top) * t
        box(root, f'{tag}_degrau{k}', (w, 0.08, 0.03), (x, y + dy * (k + 1), z), rot=(0, 0, ang), m=V['plank_l'], bev=0.006)
    for sx in (-1, 1):
        tube(root, f'{tag}_banzo{sx}', [(x + sx * w / 2, y, z_top), (x + sx * w / 2, y + dy * (n + 1), z_bot)], 0.016, V['stilt'], segs=6)


def woven_shield(root, tag, V, P, loc, rot=(math.pi / 2, 0, 0), r=0.1, m_mark=None):
    """Escudo redondo de fibra trancada com borda de madeira e folha pintada."""
    s = cyl(root, tag, r, 0.022, loc, rot=rot, m=V['mat'], v=24, bev=0.006)
    t = torus(root, tag + '_aro', (0, 0, 0), r, 0.012, V['stilt'], n=24, segs=5)
    t.parent = s
    t.location = (0, 0, 0.012)
    lf = sphere(root, tag + '_folha', r * 0.42, (0, 0, 0.014), scale=(0.55, 1.0, 0.18), m=m_mark or P['teal'], seg=12)
    lf.parent = s
    return s


def spear_leaf(root, P, V, tag, base, top, head_m=None, pennon=None):
    base, top = Vector(base), Vector(top)
    tube(root, tag, [base, top], 0.011, V['stilt'], segs=6)
    d = (top - base).normalized()
    hd = sphere(root, tag + '_ponta', 0.03, top + d * 0.04, scale=(0.5, 0.25, 1.6), m=head_m or P['steel'], seg=10)
    hd.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    torus(root, tag + '_amarra', tuple(top - d * 0.01), 0.016, 0.006, V['rope'], n=10, segs=4)
    if pennon:
        pn = cloth_grid(root, tag + '_flamula', 0.16, 0.07, 6, 2, [pennon], thick=0.008,
                        shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.07 * (1 - u * 0.9))))
        pn.location = top - d * 0.06
        register_cloth(pn, flag_wave(0.16, amp=0.03, cycles=1, waves=1.0))


def leaning_spears(root, P, V, tag, x, y, n=3, lean=(0.06, 0.06), pennon=None, head_m=None, h=0.72):
    for k in range(n):
        bx = x + (k - (n - 1) / 2) * 0.05
        spear_leaf(root, P, V, f'{tag}{k}', (bx, y, 0.13), (bx + lean[0], y + lean[1], 0.13 + h), head_m=head_m, pennon=pennon if k % 2 == 0 else None)


def firefly_jar(root, tag, V, P, loc, lights, s=1.0, hang=0.0):
    """Pote de vidro com vaga-lumes (luz amarela-esverdeada); o 'lampiao' da mata."""
    x, y, z = loc
    if hang:
        tube(root, tag + '_fio', [(x, y, z + hang + 0.16 * s), (x, y, z + 0.16 * s)], 0.005, V['rope'], segs=4)
    lathe(root, tag + '_vidro', [(0, 0.0, 0.0), (0.01, 0.06 * s, 0.06 * s), (0.11 * s, 0.065 * s, 0.065 * s), (0.14 * s, 0.04 * s, 0.04 * s)],
          V['jar'], segs=16, lv=1, caps=False).location = (x, y, z)
    sphere(root, tag + '_brilho', 0.045 * s, (x, y, z + 0.07 * s), m=V['fly'], seg=12)
    cyl(root, tag + '_tampa', 0.045 * s, 0.03 * s, (x, y, z + 0.15 * s), m=V['plank_d'], v=12, bev=0.006)
    rr = random.Random(hash(tag) & 255)
    for k in range(5):
        a = rr.uniform(0, TAU)
        sphere(root, f'{tag}_luz{k}', 0.014 * s, (x + 0.03 * s * math.cos(a), y + 0.03 * s * math.sin(a), z + rr.uniform(0.03, 0.11) * s), m=V['fly'], seg=8)
    lights.append(((x, y, z + 0.08 * s), '#d8ff7a', 12.0 * s, 1))


def fire_pit(root, tag, V, P, loc, lights, s=1.0):
    """Fogueira num anel de pedras de rio (chamas tremulam no loop)."""
    x, y, z = loc
    for k in range(9):
        a = TAU * k / 9
        sphere(root, f'{tag}_pedra{k}', 0.05 * s, (x + 0.12 * s * math.cos(a), y + 0.12 * s * math.sin(a), z + 0.02 * s), scale=(1.2, 1, 0.7), m=V['stone'], seg=10)
    for k in range(3):
        a = TAU * k / 3 + 0.4
        tube(root, f'{tag}_lenha{k}', [(x + 0.1 * s * math.cos(a), y + 0.1 * s * math.sin(a), z + 0.02 * s), (x - 0.02 * s * math.cos(a), y - 0.02 * s * math.sin(a), z + 0.09 * s)],
             0.018 * s, V['stilt'], segs=6)
    cyl(root, tag + '_brasa', 0.07 * s, 0.03 * s, (x, y, z + 0.03 * s), m=P['ember'], v=12, bev=0.01)
    fl = []
    for k in range(4):
        a = TAU * k / 4 + 0.4
        fl.append(cyl(root, f'{tag}_chama{k}', 0.03 * s, 0.12 * s, (x + 0.03 * s * math.cos(a), y + 0.03 * s * math.sin(a), z + 0.1 * s), r2=0.0, m=P['fire'], v=10, bev=0.0))
    fl.append(cyl(root, tag + '_chamaC', 0.045 * s, 0.18 * s, (x, y, z + 0.12 * s), r2=0.0, m=P['fire'], v=12, bev=0.0))
    for k, c in enumerate(fl):
        def flick(o, mb, ph, k=k):
            s_ = 1 + 0.18 * math.sin(TAU * (ph * 3 + k * 0.27)) + 0.08 * math.sin(TAU * (ph * 5 + k * 0.6))
            o.matrix_basis = mb @ Matrix.Diagonal((1 - 0.08 * (s_ - 1), 1 - 0.08 * (s_ - 1), s_, 1))
        register_anim(c, flick)
    lights.append(((x, y, z + 0.18 * s), '#ff9a40', 18.0 * s, 1))
    return fl


def straw_hat(root, parts, tag, V, band=None, brim=0.105):
    """Chapeu de palha do guardiao ribeirinho (preso ao pivo da cabeca)."""
    hc = Vector((0.006, 0, 0.055))
    hd = parts['head']
    b = cyl(root, tag + '_aba', brim, 0.012, (0, 0, 0), m=V['thatch'], v=24, bev=0.004)
    c = lathe(root, tag + '_copa', [(0.0, 0.066, 0.066), (0.03, 0.062, 0.062), (0.055, 0.045, 0.045), (0.065, 0.0, 0.0)], V['thatch'], segs=18, lv=1)
    objs = [b, c]
    if band:
        objs.append(torus(root, tag + '_fita', (0, 0, 0.012), 0.066, 0.01, band, n=18, segs=5))
    for o in objs:
        o.parent = hd
    b.location = hc + Vector((0.0, 0, 0.052))
    c.location = hc + Vector((0.0, 0, 0.052))
    if band:
        objs[2].location = hc + Vector((0.0, 0, 0.064))
    parts.setdefault('props', [])
    return objs


# ---------------------------------------------------------------- samauma (sumauma)
def samauma(root, tag, V, base, H, r0, crown=0.8, seeds=6, lights=None, crown_z=None, crown_back=0.0, seed=1, buttress=5, vines=2):
    """Samauma: tronco cinza claro com sapopemas enormes, copa em guarda-chuva de nuvens de folhas
    e sementes douradas que brilham (luz no passe de brilho)."""
    rr = random.Random(seed)
    bx, by, bz = base

    def ridges(a, z):
        return 0.05 * math.sin(a * 9 + seed) + 0.025 * noise.noise(Vector((math.cos(a) * 2, math.sin(a) * 2, z * 3 + seed)))
    prof = []
    for k in range(9):
        t = k / 8
        r = r0 * (1.25 - 0.45 * t) * (1 + 0.6 * max(0, 0.18 - t))
        prof.append((bz + H * t, r, r))
    tr = lathe(root, tag + '_tronco', prof, V['bark'], segs=40, wobble=ridges, lv=1)
    tr.location = (bx, by, 0)
    for k in range(buttress):
        a = TAU * k / buttress + rr.uniform(-0.25, 0.25) + 0.4
        L = r0 * rr.uniform(2.0, 2.6)
        Hb = H * rr.uniform(0.32, 0.45)
        bm = bmesh.new()
        prof2 = [(0, 0.0), (0.18, 1.0), (0.5, 0.45), (1.0, 0.04)]
        rings = []
        for (t, hz) in prof2:
            wd = r0 * 0.28 * (1 - 0.6 * t)
            rings.append([bm.verts.new((t * L, -wd, hz * Hb)), bm.verts.new((t * L, wd, hz * Hb)), bm.verts.new((t * L, wd, 0)), bm.verts.new((t * L, -wd, 0))])
        for i in range(len(rings) - 1):
            A_, B_ = rings[i], rings[i + 1]
            for j in range(4):
                bm.faces.new((A_[j], A_[(j + 1) % 4], B_[(j + 1) % 4], B_[j]))
        fin = bm_to_obj(bm, f'{tag}_sapopema{k}', root, [V['bark_l']], angle=60)
        sb = fin.modifiers.new('Suave', 'SUBSURF')
        sb.levels = sb.render_levels = 2
        fin.location = (bx + r0 * 0.7 * math.cos(a), by + r0 * 0.7 * math.sin(a), bz - 0.01)
        fin.rotation_euler = (0, 0, a)
    sphere(root, tag + '_musgoPe', r0 * 1.3, (bx, by, bz + 0.01), scale=(1.2, 1.2, 0.25), m=V['moss'], seg=18)
    for k in range(vines):
        a = rr.uniform(-2.6, -0.5)
        pts = [(bx + (r0 * 1.02) * math.cos(a + 0.15 * math.sin(t * 6)), by + (r0 * 1.02) * math.sin(a + 0.15 * math.sin(t * 6)), bz + 0.1 + (H - 0.2) * t)
               for t in [j / 10 for j in range(11)]]
        tube(root, f'{tag}_cipo{k}', pts, 0.012, V['leaf_d'], segs=5)
        for j in range(8):
            p = pts[1 + j]
            sphere(root, f'{tag}_cipo{k}_folha{j}', 0.03, p, scale=(1.4, 0.5, 0.8), m=V['leaf'], seg=8, rot=(0, 0.4 * math.sin(j), a + math.pi / 2))
    # galhos e copa em guarda-chuva
    cz = crown_z if crown_z is not None else bz + H
    top = Vector((bx, by + crown_back, cz))
    for k in range(4):
        a = TAU * k / 4 + 0.6 + rr.uniform(-0.2, 0.2)
        tube(root, f'{tag}_galho{k}', [(bx, by, bz + H * 0.85), (bx + crown * 0.45 * math.cos(a), by + crown_back + crown * 0.4 * math.sin(a), cz + 0.05)],
             r0 * 0.28, V['bark'], segs=8, rfun=lambda t: r0 * (0.3 - 0.18 * t))
    clumps = []
    n = 11
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.25, 0.25)
        d = crown * rr.uniform(0.35, 0.95) if k else 0.0
        r = crown * rr.uniform(0.32, 0.46)
        p = (top.x + d * math.cos(a), top.y + d * math.sin(a) * 0.85, top.z + rr.uniform(0.0, 0.22) * crown + (0.12 * crown if k == 0 else 0))
        clumps.append((p, r))
        sphere(root, f'{tag}_copa{k}', r, p, scale=(1, 1, 0.72), m=V['leaf'] if k % 3 else V['leaf_d'], seg=20)
    # sementes douradas (as de cima balancam devagar)
    piv = empty(root, tag + '_sementesPiv', loc=(top.x, top.y, top.z))
    for k in range(seeds):
        p, r = clumps[1 + k % (n - 1)]
        a = rr.uniform(-2.9, -0.25)
        u = rr.uniform(-0.1, 0.55)
        rad = r * math.sqrt(max(0.0, 1 - u * u)) * 1.02
        q = (p[0] + rad * math.cos(a) - top.x, p[1] + rad * math.sin(a) - top.y, p[2] + r * 0.72 * u - top.z)
        s_ = sphere(root, f'{tag}_semente{k}', rr.uniform(0.05, 0.07), (0, 0, 0), scale=(1, 1, 1.3), m=V['seed'], seg=12)
        s_.parent = piv
        s_.location = q
        if lights is not None and k % 2 == 0:
            lights.append(((top.x + q[0], top.y + q[1], top.z + q[2]), '#ffd25a', 6.0, 1))
    register_anim(piv, lambda o, mb, ph: setattr(o, 'matrix_basis', Matrix.Translation((0, 0, 0.012 * math.sin(TAU * ph))) @ mb))
    return clumps


def ribbon(root, tag, P, x, y, z, w=0.12, h=0.5, m=None):
    """Fita verde pendurada de um galho (o tecido balanca)."""
    rb = cloth_grid(root, tag, w, h, 3, 10, [m or P['teal']], thick=0.008)
    rb.location = (x - w / 2, y, z)
    register_cloth(rb, hang_wave(h, amp=0.04, axis='Y', cycles=1, waves=0.8, top=0.0))
    tube(root, tag + '_no', [(x - w / 2 - 0.01, y, z + 0.01), (x + w / 2 + 0.01, y, z + 0.01)], 0.012, P['gold'], segs=5)
    return rb


# ---------------------------------------------------------------- feira do rio
def water_patch(root, tag, V, cx, cy, rx, ry, z=0.158):
    """Lamina d'agua de igarape sobre parte do lote (com pedras na margem)."""
    w = cyl(root, tag, 1.0, 0.012, (cx, cy, z), m=V['water'], v=40, bev=0.004)
    w.scale = (rx, ry, 1)
    for k in range(18):
        a = TAU * k / 18
        sphere(root, f'{tag}_pedra{k}', 0.05, (cx + rx * 1.02 * math.cos(a), cy + ry * 1.02 * math.sin(a), z), scale=(1.3, 1, 0.6), m=V['stone'], seg=10)
    return w


def boat(root, tag, V, P, loc, L=1.0, Wd=0.34, ang=0.0, colors=None, seats=True):
    """Barco de madeira pintado: casco em gamela (meia secao eliptica) com faixas coloridas na lateral, borda e assoalho.
    loc = centro do barco na linha d'agua; a borda fica em z + 0.42 * Wd."""
    x, y, z = loc
    cols = colors or [mat('casco_roxo', '#7a4a9a', rough=0.6, var=0.04, bump=0.15), mat('casco_verde', '#3f9a6a', rough=0.6, var=0.04, bump=0.15),
                      mat('casco_vermelho', '#d0503a', rough=0.6, var=0.04, bump=0.15)]
    D = Wd * 0.5
    zr = z + Wd * 0.42
    prof = [(0, 0.0, 0.0), (0.04, D * 0.55, Wd * 0.3), (0.2, D * 0.92, Wd * 0.47), (0.5, D, Wd * 0.5), (0.8, D * 0.92, Wd * 0.47), (0.96, D * 0.55, Wd * 0.3), (1.0, 0.0, 0.0)]
    hull = lathe(root, tag + '_casco', prof, cols[0], segs=28, lv=2, caps=False, solid=0.025, cut=lambda c: c.x < -0.002)
    hull.rotation_euler = (0, math.pi / 2, ang)
    hull.scale = (1.0, 1.0, L)
    ca, sa = math.cos(ang), math.sin(ang)
    hull.location = (x - ca * L / 2, y - sa * L / 2, zr)
    for k, m in enumerate(cols[1:]):
        band = torus(root, f'{tag}_faixa{k}', (x, y, zr - D * (0.25 + 0.22 * k)), 1.0, 0.022, m, n=48, segs=6)
        band.scale = (L * 0.47 * (1 - 0.05 * k), Wd * (0.49 - 0.04 * k), 1)
        band.rotation_euler = (0, 0, ang)
    rim = torus(root, tag + '_borda', (x, y, zr), 1.0, 0.024, V['plank_d'], n=48, segs=6)
    rim.scale = (L * 0.5, Wd * 0.51, 1)
    rim.rotation_euler = (0, 0, ang)
    inner = cyl(root, tag + '_assoalho', 1.0, 0.02, (x, y, zr - D * 0.45), m=V['plank'], v=32, bev=0.002)
    inner.scale = (L * 0.4, Wd * 0.4, 1)
    inner.rotation_euler = (0, 0, ang)
    if seats:
        for k in (-0.22, 0.18):
            box(root, f'{tag}_banco{k}', (0.06, Wd * 0.92, 0.03), (x + ca * k * L, y + sa * k * L, zr - 0.02), rot=(0, 0, ang), m=V['plank_l'], bev=0.006)
    return hull


def fruit_crate(root, tag, V, P, loc, fruitm, s=1.0, rot=0.0, n=7):
    x, y, z = loc
    box(root, tag, (0.22 * s, 0.17 * s, 0.11 * s), (x, y, z + 0.055 * s), rot=(0, 0, rot), m=V['plank_l'], bev=0.01)
    for k, zz in enumerate((0.025, 0.085)):
        box(root, f'{tag}_ripa{k}', (0.226 * s, 0.176 * s, 0.02 * s), (x, y, z + zz * s), rot=(0, 0, rot), m=V['plank_d'], bev=0.004)
    rr = random.Random(hash(tag) & 255)
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0, 0.06 * s)
        sphere(root, f'{tag}_fruta{k}', 0.035 * s, (x + d * math.cos(a), y + d * math.sin(a) * 0.7, z + 0.12 * s + 0.01 * (k % 2)), m=fruitm, seg=10)


def acai_basket(root, tag, V, P, loc, s=1.0):
    x, y, z = loc
    lathe(root, tag, [(0, 0.06 * s, 0.06 * s), (0.08 * s, 0.09 * s, 0.09 * s), (0.12 * s, 0.1 * s, 0.1 * s)], V['thatch'], segs=16, lv=1, caps=False, solid=0.01).location = (x, y, z)
    cyl(root, tag + '_base', 0.06 * s, 0.01, (x, y, z + 0.005), m=V['thatch_d'], v=12, bev=0.002)
    for k in range(9):
        a = TAU * k / 9
        sphere(root, f'{tag}_acai{k}', 0.022 * s, (x + 0.05 * s * math.cos(a), y + 0.05 * s * math.sin(a), z + 0.115 * s), m=V['acai'], seg=8)
    sphere(root, tag + '_monte', 0.06 * s, (x, y, z + 0.12 * s), scale=(1, 1, 0.55), m=V['acai'], seg=12)


def banana_bunch(root, tag, V, loc, s=1.0):
    x, y, z = loc
    tube(root, tag + '_cacho', [(x, y, z + 0.02), (x, y, z + 0.22 * s)], 0.015 * s, V['leaf_d'], segs=5)
    for k in range(10):
        a = TAU * k / 5
        zz = z + 0.06 * s + 0.06 * s * (k // 5)
        tube(root, f'{tag}_b{k}', [(x + 0.02 * s * math.cos(a), y + 0.02 * s * math.sin(a), zz), (x + 0.07 * s * math.cos(a), y + 0.07 * s * math.sin(a), zz + 0.06 * s)],
             0.016 * s, V['banana'], segs=6, rfun=lambda t: s * (0.017 - 0.01 * t * t))


def nut_sacks(root, tag, V, P, loc, n=3, s=1.0):
    x, y, z = loc
    for k in range(n):
        a = TAU * k / n
        sx, sy = x + 0.1 * s * math.cos(a), y + 0.08 * s * math.sin(a)
        sphere(root, f'{tag}{k}', 0.09 * s, (sx, sy, z + 0.08 * s), scale=(1, 0.9, 1.0), m=P['rope'], seg=14)
        torus(root, f'{tag}{k}_no', (sx, sy, z + 0.16 * s), 0.03 * s, 0.01 * s, V['plank_d'], n=10, segs=4)
    for k in range(3):
        sphere(root, f'{tag}_ourico{k}', 0.05 * s, (x + 0.2 * s, y - 0.08 * s + 0.07 * k * s, z + 0.045 * s), m=V['nut'], seg=12)
