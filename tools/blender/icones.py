"""Icones da interface em 3D (mesmo estilo e luz das torres) no tema do Ninguem Sobe a Rampa: as 32 habilidades das
especializacoes, as 2 operacoes (feiticos) e os botoes do anel (evoluir, vender, encontro, obra parada, obra, alvos).
Cada icone e um objeto pequeno e de silhueta forte, sem texto, letras, numeros ou logos, renderizado sozinho num quadro
quadrado; os nomes internos sao os do motor (js/data.js). Os retratos das torres saem dos proprios sprites
(tools/sprites/retratos.js).

  Blender -b -P tools/blender/icones.py -- render arte/render/icones [nomes...]
  Blender -b -P tools/blender/icones.py -- still <png> [nomes...]      (prancha com todos, ou so os nomes dados)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403

ICON_PX = 168          # lado do quadro de cada icone (pixels)
ICONS = {}


def icon(name):
    def deco(fn):
        ICONS[name] = fn
        return fn
    return deco


def M(key, hexcol, **kw):
    kw.setdefault('var', 0.0)
    kw.setdefault('bump', 0.05)
    return mat('ic_' + key, hexcol, **kw)


def G(key, hexcol, strength, **kw):
    """Material que brilha (fogo, giroflex, clarao): a mesma forca de dia e no passe de luz."""
    kw.setdefault('var', 0.0)
    kw.setdefault('bump', 0.0)
    return glow_mat('ic_' + key, hexcol, strength, strength, **kw)


def C():
    return {
        'red': M('vermelho', '#e0573f', rough=0.5), 'red_d': M('vermelho_esc', '#a8302a', rough=0.45), 'orange': M('laranja', '#f08a2c', rough=0.5),
        'yellow': M('amarelo', '#ffd04a', rough=0.45), 'gold': M('ouro', '#f2bd48', rough=0.3, metal=0.6), 'gold_d': M('ouro_velho', '#d29a32', rough=0.35, metal=0.6),
        'green': M('verde', '#5fbf4a', rough=0.45), 'green_d': M('verde_esc', '#3f8f3a', rough=0.5), 'urna': M('verde_confirma', '#2fae4e', rough=0.42),
        'zap': M('verde_zap', '#3fbf6a', rough=0.45), 'zap_l': M('verde_zap_claro', '#c9f2b8', rough=0.5), 'zap_d': M('verde_zap_escuro', '#2c6e4a', rough=0.5),
        'teal': M('teal', '#26a69a', rough=0.5), 'blue': M('azul', '#4a9be0', rough=0.4), 'navy': M('marinho', '#2a3f73', rough=0.45),
        'sky': M('ceu', '#9fd8f2', rough=0.35), 'ice': M('gelo', '#b9ecfb', rough=0.08), 'purple': M('roxo', '#9a62d8', rough=0.4),
        'violet': M('violeta', '#c79af2', rough=0.4), 'pink': M('rosa', '#f28aa8', rough=0.5), 'white': M('branco', '#f6f1e6', rough=0.6),
        'paper': M('papel', '#fbf8f0', rough=0.75), 'line': M('linha_cinza', '#a9a7a2', rough=0.7), 'news': M('jornal', '#e9e3d2', rough=0.8),
        'cream': M('creme', '#f4e2bc', rough=0.7), 'wood': M('madeira', '#9a6236', rough=0.7, bump=0.2), 'wood_l': M('madeira_cl', '#c88a52', rough=0.7, bump=0.2),
        'iron': M('ferro', '#6a6e78', rough=0.4, metal=0.6), 'steel': M('aco', '#c9d2dc', rough=0.25, metal=0.8), 'dark': M('escuro', '#3a3440', rough=0.6),
        'black': M('preto', '#2c2830', rough=0.5), 'grey': M('cinza', '#8d8f98', rough=0.55), 'stone': M('pedra', '#b9a688', rough=0.8, bump=0.25),
        'earth': M('terra_cerrado', '#b0603e', rough=0.9, bump=0.3), 'grass': M('capim_seco', '#a8a446', rough=0.9),
        'concrete': M('concreto', '#ecebe5', rough=0.85, bump=0.15), 'concrete_d': M('concreto_sombra', '#cfcbc1', rough=0.9, bump=0.1),
        'rust': M('ferrugem', '#a5532c', rough=0.75, bump=0.2), 'obra': M('laranja_obra', '#f07a22', rough=0.55),
        'mud': M('lama', '#6e4a30', rough=0.32, bump=0.15), 'mud_l': M('lama_clara', '#8a6040', rough=0.3, bump=0.1),
        'cloud': M('nuvem', '#dfe6ee', rough=0.7), 'cloud_d': M('nuvem_esc', '#66607e', rough=0.7),
        'skin': M('pele', '#e0a074', rough=0.6), 'skin2': M('pele_morena', '#b97a52', rough=0.6), 'leather': M('couro', '#8b5a35', rough=0.6),
        'mala': M('mala_couro', '#7b4a2b', rough=0.5, bump=0.1), 'mala_d': M('mala_couro_esc', '#4f2f1c', rough=0.55, bump=0.1),
        'case': M('pasta_preta', '#25222a', rough=0.28), 'kraft': M('papel_pardo', '#c99a5c', rough=0.85, bump=0.08), 'kraft_d': M('papel_pardo_esc', '#a87a42', rough=0.85),
        'envelope': M('envelope', '#f4ead2', rough=0.85), 'envelope_d': M('envelope_aba', '#dccaa0', rough=0.85),
        'note': M('cedula', '#8cc678', rough=0.75, bump=0.03), 'note_d': M('cedula_esc', '#3f8a4c', rough=0.75),
        'suit': M('terno_azul', '#2e3a5c', rough=0.75, sheen=0.3), 'suit_g': M('terno_cinza', '#6b6f78', rough=0.75, sheen=0.3),
        'brief': M('cueca_azul', '#3f6fd0', rough=0.8, sheen=0.4), 'brief_d': M('cueca_costura', '#2b4f9a', rough=0.8),
        'barrel': M('barril_preto', '#2b282a', rough=0.32, metal=0.35), 'petro': M('amarelo_petro', '#f2b52e', rough=0.5), 'oil': M('oleo', '#151214', rough=0.06),
        'phone': M('telefone_vermelho', '#c93a32', rough=0.3), 'safe': M('cofre_verde', '#4f6b62', rough=0.45, metal=0.3), 'safe_l': M('cofre_porta', '#62827a', rough=0.4, metal=0.3),
        'car': M('viatura_preta', '#1d1b21', rough=0.22, metal=0.3), 'glass': M('vidro', '#9fc6d8', rough=0.05), 'hat': M('capacete_amarelo', '#ffc531', rough=0.35),
        'tire': M('pneu', '#1a181b', rough=0.8), 'water': M('agua', '#4aa8e8', rough=0.1), 'water_l': M('agua_clara', '#a8e2fa', rough=0.08),
        'diamond': G('diamante', '#8fe4ff', 0.35, rough=0.04), 'diamond_w': G('diamante_branco', '#e8fbff', 0.5, rough=0.04),
        'fire': G('fogo', '#ff7424', 2.2, rough=0.5), 'glow_y': G('brilho', '#fff1a0', 3.5, rough=0.5), 'bolt': G('raio', '#ffe45a', 1.8, rough=0.4),
        'spark': G('faisca', '#fffbea', 3.0, rough=0.3), 'siren_r': G('giroflex_vermelho', '#ff3b3b', 3.2, rough=0.3), 'siren_b': G('giroflex_azul', '#3b8bff', 3.2, rough=0.3),
        'beam': G('feixe', '#fff3b0', 1.1, rough=0.6), 'gold_hot': G('ouro_quente', '#ffb347', 0.6, rough=0.3, metal=0.5),
    }


# ---------------------------------------------------------------- utilidades de modelagem
class grp:
    """Grupo com coordenadas locais: tudo o que nasce filho da raiz dentro do `with` vira filho de um empty
    (posicao, giro e escala do grupo)."""
    def __init__(self, r, name, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
        self.r = r
        self.e = empty(r, name, loc=loc, rot=rot)
        self.e.scale = (s, s, s)

    def __enter__(self):
        self.before = set(bpy.data.objects.keys())
        return self.e

    def __exit__(self, *a):
        for o in list(bpy.data.objects):
            if o.name not in self.before and o.parent == self.r and o != self.e:
                o.parent = self.e


def prism(r, name, pts, depth, m, loc=(0, 0, 0), rot=(0, 0, 0), bev=0.02, seg=3):
    """Placa grossa: poligono no plano XZ extrudado em Y (centrada em y = 0, a face -Y olha para a camera)."""
    bm = bmesh.new()
    a = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]
    b = [bm.verts.new((x, depth / 2, z)) for x, z in pts]
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, name, r, [m], bev=bev, seg=seg, angle=30)
    o.location = loc
    o.rotation_euler = rot
    return o


def rrect(w, h, rad, n=4, cx=0.0, cz=0.0):
    """Retangulo de cantos redondos (pontos no plano XZ, sentido anti-horario)."""
    pts = []
    for k, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        ccx, ccz = cx + sx * (w / 2 - rad), cz + sz * (h / 2 - rad)
        for j in range(n + 1):
            a = k * math.pi / 2 + (math.pi / 2) * j / n
            pts.append((ccx + rad * math.cos(a), ccz + rad * math.sin(a)))
    return pts


def star_pts(n, R_, r_, a0=math.pi / 2, cx=0.0, cz=0.0):
    return [(cx + (R_ if k % 2 == 0 else r_) * math.cos(a0 + math.pi * k / n),
             cz + (R_ if k % 2 == 0 else r_) * math.sin(a0 + math.pi * k / n)) for k in range(2 * n)]


def axis_rot(d):
    """Giro (em Y) que leva o eixo Z de um cilindro para a direcao d do plano XZ."""
    return (0, math.atan2(d[0], d[2]), 0)


def bolt_shape(root, name, m, loc, s=1.0, rot=0.0, depth=0.08):
    bm = bmesh.new()
    pts = [(0.12, 0.62), (-0.26, 0.02), (-0.02, 0.02), (-0.14, -0.62), (0.28, 0.08), (0.04, 0.08), (0.22, 0.62)]
    top = [bm.verts.new((x * s, depth / 2, z * s)) for x, z in pts]
    bot = [bm.verts.new((x * s, -depth / 2, z * s)) for x, z in pts]
    bm.faces.new(list(reversed(top)))
    bm.faces.new(bot)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top[i], top[j], bot[j], bot[i]))
    o = bm_to_obj(bm, name, root, [m], bev=0.015, angle=30)
    o.location = loc
    o.rotation_euler = (0, rot, 0)
    return o


def arrow3d(root, name, m, loc, s=1.0, rot=(0, 0, 0), up=True):
    """Seta gorda (evoluir/descer): prisma com bisel."""
    bm = bmesh.new()
    pts = [(0, 0.62), (0.5, 0.08), (0.2, 0.08), (0.2, -0.55), (-0.2, -0.55), (-0.2, 0.08), (-0.5, 0.08)]
    if not up:
        pts = [(x, -z) for x, z in pts]
    d = 0.22
    top = [bm.verts.new((x * s, d / 2 * s, z * s)) for x, z in pts]
    bot = [bm.verts.new((x * s, -d / 2 * s, z * s)) for x, z in pts]
    bm.faces.new(list(reversed(top)))
    bm.faces.new(bot)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((top[i], top[j], bot[j], bot[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, name, root, [m], bev=0.05 * s, seg=4, angle=30)
    o.location = loc
    o.rotation_euler = rot
    return o


def cloud(root, name, m, loc, s=1.0):
    out = []
    for k, (x, z, r) in enumerate(((-0.32, 0.0, 0.26), (0.0, 0.1, 0.34), (0.3, 0.0, 0.25), (-0.12, -0.12, 0.24), (0.15, -0.12, 0.24))):
        out.append(sphere(root, f'{name}{k}', r * s, (loc[0] + x * s, loc[1], loc[2] + z * s), scale=(1, 0.8, 1), m=m, seg=20))
    return out


def coin(r, name, P, loc, s=1.0, rot=(math.pi / 2, 0, 0)):
    """Moeda de ouro com aro (a face +Z olha para a camera com o giro padrao)."""
    with grp(r, name, loc, rot, s):
        cyl(r, name + '_disco', 0.22, 0.06, (0, 0, 0), m=P['gold'], v=32, bev=0.02)
        for z in (-0.031, 0.031):
            torus(r, f'{name}_aro{z}', (0, 0, z), 0.165, 0.014, P['gold_d'], n=28, segs=6)


def note(r, name, P, loc, rot=(0, 0, 0), s=1.0):
    """Cedula verde (no plano XZ) com o oval escuro no meio e um canto marcado."""
    with grp(r, name, loc, rot, s):
        box(r, name + '_papel', (0.36, 0.014, 0.17), (0, 0, 0), m=P['note'], bev=0.006)
        o = cyl(r, name + '_oval', 0.05, 0.02, (0.04, 0, 0), m=P['note_d'], v=20, bev=0.0, rot=(math.pi / 2, 0, 0))
        o.scale = (1.3, 1, 1)
        box(r, name + '_canto', (0.05, 0.02, 0.05), (-0.12, 0, 0.042), m=P['note_d'], bev=0.004)


def gem(r, name, m, loc, s=1.0, rot=(0, 0, 0), n=8):
    """Brilhante lapidado de faces chapadas: pavilhao em ponta para baixo, cinta, coroa e mesa."""
    bm = bmesh.new()
    tip = bm.verts.new((0, 0, -0.5 * s))
    g0 = [bm.verts.new((0.5 * s * math.cos(TAU * k / n), 0.5 * s * math.sin(TAU * k / n), 0.0)) for k in range(n)]
    g1 = [bm.verts.new((0.5 * s * math.cos(TAU * k / n), 0.5 * s * math.sin(TAU * k / n), 0.05 * s)) for k in range(n)]
    tb = [bm.verts.new((0.3 * s * math.cos(TAU * (k + 0.5) / n), 0.3 * s * math.sin(TAU * (k + 0.5) / n), 0.24 * s)) for k in range(n)]
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((tip, g0[j], g0[k]))
        bm.faces.new((g0[k], g0[j], g1[j], g1[k]))
        bm.faces.new((g1[k], g1[j], tb[k]))
        bm.faces.new((tb[k], g1[j], tb[j]))
    bm.faces.new(tb)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, name, r, [m], smooth=False)
    o.location = loc
    o.rotation_euler = rot
    return o


def sparkle(r, name, m, loc, s=0.12, rot=0.0):
    """Brilhinho de 4 pontas (placa fina virada para a camera)."""
    return prism(r, name, star_pts(4, s, s * 0.28, a0=math.pi / 2 + rot), 0.03, m, loc=loc, bev=0.006)


def flame(r, name, m, loc, h=0.4, w=0.13, rot=(0, 0, 0)):
    fl = lathe(r, name, [(0, 0.0, 0.0), (0.15 * h, w, w), (0.5 * h, w * 0.78, w * 0.78), (h, 0.0, 0.0)], m, segs=14, lv=1)
    fl.location = loc
    fl.rotation_euler = rot
    return fl


def oil_barrel(r, name, P, loc, s=1.0, rot=(0, 0, 0), open_top=False):
    """Barril de petroleo preto com a faixa amarela e os aros."""
    with grp(r, name, loc, rot, s):
        cyl(r, name + '_corpo', 0.2, 0.5, (0, 0, 0), m=P['barrel'], v=28, bev=0.02)
        cyl(r, name + '_faixa', 0.206, 0.12, (0, 0, 0), m=P['petro'], v=28, bev=0.008)
        for k, z in enumerate((-0.17, 0.17)):
            torus(r, f'{name}_aro{k}', (0, 0, z), 0.204, 0.016, P['barrel'], n=28, segs=6)
        torus(r, name + '_borda', (0, 0, 0.245), 0.19, 0.02, P['iron'], n=28, segs=6)
        if open_top:
            cyl(r, name + '_oleo', 0.18, 0.02, (0, 0, 0.235), m=P['oil'], v=28, bev=0.0)
        else:
            cyl(r, name + '_tampao', 0.035, 0.03, (0.09, 0, 0.255), m=P['iron'], v=12, bev=0.005)


def capsule(r, name, m1, m2, loc, rot=(0, 0, 0), s=1.0):
    with grp(r, name, loc, rot, s):
        for k, (m, sz) in enumerate(((m1, 1), (m2, -1))):
            cyl(r, f'{name}_meia{k}', 0.1, 0.16, (0, 0, sz * 0.08), m=m, v=20, bev=0.0)
            sphere(r, f'{name}_ponta{k}', 0.1, (0, 0, sz * 0.16), m=m, seg=20)


def chat_bubble(r, name, m, loc, s=1.0, rot=(0, 0, 0), dot_m=None, w=0.36, h=0.25, tail=1):
    """Balao de conversa (cantos redondos, rabinho embaixo) com os tres pontinhos de digitando."""
    with grp(r, name, loc, rot, s):
        prism(r, name + '_balao', rrect(w, h, 0.09), 0.08, m, bev=0.02)
        prism(r, name + '_rabo', [(tail * 0.02, -h / 2 + 0.03), (tail * 0.13, -h / 2 + 0.03), (tail * 0.18, -h / 2 - 0.08)], 0.08, m, bev=0.01)
        if dot_m:
            for k in range(3):
                sphere(r, f'{name}_ponto{k}', 0.03, ((k - 1) * 0.085, -0.045, 0), m=dot_m, seg=10)


def raised_hand(r, name, P, loc, skin, sleeve, s=1.0, rot=(0, 0, 0)):
    """Mao levantada (votando): palma, quatro dedos, polegar, punho da camisa e a manga do paleto."""
    with grp(r, name, loc, rot, s):
        sphere(r, name + '_palma', 0.16, (0, 0, 0), scale=(1.0, 0.5, 1.08), m=skin, seg=20)
        for k, (x, top) in enumerate(((-0.105, 0.31), (-0.036, 0.4), (0.034, 0.38), (0.1, 0.29))):
            tube(r, f'{name}_dedo{k}', [(x * 0.95, 0, 0.08), (x, 0, top)], 0.043, skin, segs=10)
            sphere(r, f'{name}_ponta{k}', 0.043, (x, 0, top), m=skin, seg=12)
        tube(r, name + '_polegar', [(-0.11, -0.01, -0.06), (-0.2, -0.02, 0.04), (-0.25, -0.02, 0.12)], 0.046, skin, segs=10)
        sphere(r, name + '_polegarPonta', 0.046, (-0.25, -0.02, 0.12), m=skin, seg=12)
        cyl(r, name + '_punho', 0.135, 0.08, (0, 0, -0.2), m=P['white'], v=24, bev=0.02)
        cyl(r, name + '_manga', 0.155, 0.36, (0, 0, -0.42), m=sleeve, v=24, bev=0.03)


def pawn(r, name, P, body_m, loc, s=1.0):
    """Boneco cabecudo de fila (andando para a direita): corpo em cone, cabeca grande e nariz para a frente."""
    with grp(r, name, loc, (0, 0, 0), s):
        lathe(r, name + '_corpo', [(0, 0.17, 0.15), (0.05, 0.17, 0.15), (0.2, 0.11, 0.1), (0.33, 0.07, 0.07)], body_m, segs=20, lv=2)
        sphere(r, name + '_cabeca', 0.15, (0, 0, 0.45), m=P['skin'], seg=20)
        sphere(r, name + '_nariz', 0.035, (0.15, -0.02, 0.44), m=P['skin'], seg=10)
        sphere(r, name + '_olho', 0.02, (0.12, -0.08, 0.48), m=P['black'], seg=8)


def hard_hat(r, name, m, loc, s=1.0, rot=(0, 0, 0)):
    """Capacete de obra: casco, aba e a crista do meio."""
    with grp(r, name, loc, rot, s):
        lathe(r, name + '_casco', [(0.0, 0.34, 0.31), (0.12, 0.33, 0.3), (0.24, 0.27, 0.25), (0.33, 0.16, 0.15), (0.37, 0.0, 0.0)], m, segs=28, lv=2)
        o = cyl(r, name + '_aba', 0.36, 0.045, (0, -0.06, 0.01), m=m, v=36, bev=0.02)
        o.scale = (1.12, 1.08, 1)
        tube(r, name + '_crista', [(0, 0.27, 0.22), (0, 0.12, 0.34), (0, -0.05, 0.37), (0, -0.2, 0.3), (0, -0.3, 0.17)], 0.045, m, segs=10)
        torus(r, name + '_faixa', (0, 0, 0.05), 0.335, 0.016, M('capacete_faixa', '#e0a218', rough=0.4), n=36, segs=6)


def jet(r, name, P, loc, rot=(0, 0, 0), s=1.0):
    """Jatinho executivo (nariz em +X): fuselagem branca com faixa azul, asas enflechadas, deriva e janelinhas."""
    with grp(r, name, loc, rot, s):
        fu = lathe(r, name + '_fuselagem', [(-0.5, 0.0, 0.0), (-0.48, 0.05, 0.05), (-0.3, 0.1, 0.1), (0.15, 0.12, 0.12), (0.34, 0.1, 0.1),
                                            (0.46, 0.05, 0.05), (0.52, 0.0, 0.0)], P['white'], segs=20, lv=2)
        fu.rotation_euler = (0, math.pi / 2, 0)
        fx = lathe(r, name + '_faixa', [(-0.36, 0.105, 0.105), (0.3, 0.123, 0.123)], P['navy'], segs=20, lv=1, caps=False)
        fx.rotation_euler = (0, math.pi / 2, 0)
        fx.scale = (0.32, 1.0, 1.0)
        fx.location = (0, 0, -0.035)
        wing = [(0.12, 0.0), (0.02, 0.0), (-0.18, -0.52), (-0.08, -0.52)]
        for sz in (-1, 1):
            prism(r, f'{name}_asa{sz}', [(x, z * sz) for x, z in (wing if sz > 0 else wing[::-1])], 0.03, P['white'], loc=(0, 0, -0.03), rot=(math.pi / 2, 0, 0), bev=0.01)
            prism(r, f'{name}_estab{sz}', [(-0.38, 0.0), (-0.44, 0.0), (-0.52, -0.18 * sz), (-0.46, -0.18 * sz)][::sz], 0.02, P['white'],
                  loc=(0, 0, 0.17), rot=(math.pi / 2, 0, 0), bev=0.006)
        prism(r, name + '_deriva', [(-0.3, 0.06), (-0.48, 0.04), (-0.54, 0.2), (-0.44, 0.2)], 0.03, P['navy'], bev=0.01)
        for k in range(4):
            sphere(r, f'{name}_janela{k}', 0.022, (0.16 - 0.1 * k, -0.11, 0.03), scale=(1.1, 0.5, 1.0), m=P['black'], seg=10)
        sphere(r, name + '_cabine', 0.05, (0.38, -0.06, 0.04), scale=(1.4, 0.8, 0.6), m=P['black'], seg=12)
        for sz in (-1, 1):
            cyl(r, f'{name}_motor{sz}', 0.045, 0.16, (-0.3, 0.12 * sz, 0.06), m=P['grey'], v=14, bev=0.01, rot=(0, math.pi / 2, 0))


# ---------------------------------------------------------------- habilidades: Mensalao (Mensalinho)
@icon('explosive')
def _(r, P):
    # Mala Estourada: mala de couro escancarada, notas voando e o estouro amarelo atras
    prism(r, 'estouro', star_pts(9, 0.66, 0.4), 0.05, P['yellow'], loc=(0.0, 0.34, 0.16), bev=0.012)
    prism(r, 'estouroMiolo', star_pts(9, 0.45, 0.28, a0=1.9), 0.06, P['orange'], loc=(0.0, 0.29, 0.18), bev=0.012)
    box(r, 'mala', (0.86, 0.34, 0.44), (0, 0, -0.32), m=P['mala'], bev=0.07, seg=4)
    for s_ in (-1, 1):
        box(r, f'correia{s_}', (0.08, 0.36, 0.46), (s_ * 0.24, 0, -0.32), m=P['mala_d'], bev=0.02)
        box(r, f'fecho{s_}', (0.1, 0.03, 0.08), (s_ * 0.24, -0.19, -0.14), m=P['gold'], bev=0.012)
    box(r, 'monte', (0.74, 0.26, 0.1), (0, 0.0, -0.08), m=P['note'], bev=0.03)
    # tampa aberta para tras (dobradica na quina de tras) com a alca
    with grp(r, 'tampa', (0, 0.17, -0.1), (math.radians(-112), 0, 0)):
        box(r, 'tampaCouro', (0.86, 0.34, 0.08), (0, -0.17, 0.04), m=P['mala'], bev=0.03)
        tube(r, 'alca', [(-0.13, -0.36, 0.04), (-0.1, -0.43, 0.04), (0.1, -0.43, 0.04), (0.13, -0.36, 0.04)], 0.03, P['mala_d'], segs=8)
    for k, (x, z, a, b) in enumerate(((-0.45, 0.2, 0.55, 0.3), (-0.18, 0.44, -0.3, -0.2), (0.16, 0.52, 0.25, 0.4),
                                      (0.46, 0.24, -0.6, 0.2), (0.02, 0.18, 0.08, -0.3), (-0.34, 0.5, -0.9, 0.1))):
        note(r, f'nota{k}', P, (x, -0.14, z), rot=(b, a, 0), s=0.95)


@icon('eagle')
def _(r, P):
    # Olho no Plenario: lupa de aro dourado com um olho arregalado vigiando
    cx, cz = -0.08, 0.12
    tube(r, 'cabo', [(cx + 0.29, 0.02, cz - 0.29), (0.52, 0.02, -0.52)], 0.075, P['black'], segs=12)
    sphere(r, 'caboPonta', 0.076, (0.52, 0.02, -0.52), m=P['black'], seg=14)
    cyl(r, 'virola', 0.088, 0.12, (cx + 0.31, 0.02, cz - 0.31), m=P['gold'], v=16, bev=0.015, rot=axis_rot((1, 0, -1)))
    torus(r, 'aro', (cx, 0, cz), 0.37, 0.065, P['gold'], axis='Y', n=40, segs=10)
    cyl(r, 'lente', 0.35, 0.03, (cx, 0.02, cz), m=P['glass'], v=40, bev=0.01, rot=(math.pi / 2, 0, 0))
    sphere(r, 'branco', 0.22, (cx, -0.04, cz), scale=(1.28, 0.42, 0.82), m=P['white'], seg=28)
    sphere(r, 'iris', 0.12, (cx + 0.02, -0.12, cz - 0.01), scale=(1, 0.45, 1), m=P['blue'], seg=20)
    sphere(r, 'pupila', 0.058, (cx + 0.02, -0.16, cz - 0.01), scale=(1, 0.5, 1), m=P['black'], seg=14)
    sphere(r, 'reflexo', 0.025, (cx - 0.02, -0.19, cz + 0.04), m=P['white'], seg=8)
    # palpebras (contorno de amendoa)
    for k, sz in enumerate((1, -1)):
        tube(r, f'palpebra{k}', [(cx - 0.29, -0.06, cz), (cx - 0.15, -0.1, cz + sz * 0.15), (cx + 0.15, -0.1, cz + sz * 0.15), (cx + 0.29, -0.06, cz)],
             0.022 if sz > 0 else 0.014, P['black'], segs=6)


@icon('cloud')
def _(r, P):
    # Chuva de Notas: nuvem despejando cedulas
    cloud(r, 'nuvem', P['cloud'], (0, 0, 0.24), 1.0)
    for k, (x, z, a, b) in enumerate(((-0.36, -0.22, 0.45, 0.3), (0.0, -0.36, -0.3, -0.35), (0.36, -0.2, 0.6, 0.15),
                                      (-0.18, -0.6, -0.5, 0.2), (0.22, -0.58, 0.35, -0.25))):
        note(r, f'nota{k}', P, (x, -0.1, z), rot=(b, a, 0.15 * (k - 2)), s=0.9)


@icon('corrosive')
def _(r, P):
    # Elastico Apertado: cueca azul com o elastico branco esticado e os dolares enfiados no cos
    pts = [(-0.46, 0.1), (0.46, 0.1), (0.44, -0.1), (0.32, -0.22), (0.2, -0.36), (0.13, -0.5), (-0.13, -0.5), (-0.2, -0.36),
           (-0.32, -0.22), (-0.44, -0.1)]
    prism(r, 'cueca', pts, 0.26, P['brief'], bev=0.07, seg=4)
    for k, sx in enumerate((-1, 1)):
        tube(r, f'perna{k}', [(sx * 0.42, -0.135, -0.1), (sx * 0.31, -0.135, -0.22), (sx * 0.2, -0.135, -0.35), (sx * 0.13, -0.135, -0.47)],
             0.022, P['brief_d'], segs=6)
    for k, (x, a) in enumerate(((-0.26, 0.32), (0.0, -0.05), (0.26, -0.38))):
        note(r, f'nota{k}', P, (x, 0.03, 0.3), rot=(0, math.pi / 2 + a, 0), s=1.15)
    box(r, 'cos', (0.96, 0.29, 0.13), (0, 0, 0.14), m=P['white'], bev=0.05)
    box(r, 'cosFriso', (0.97, 0.3, 0.025), (0, 0, 0.14), m=P['red'], bev=0.005)
    # a frente do elastico puxada para cima, esticada como estilingue
    arc = [(-0.4, -0.13, 0.17), (-0.26, -0.22, 0.38), (0.0, -0.3, 0.58), (0.26, -0.22, 0.38), (0.4, -0.13, 0.17)]
    tube(r, 'elastico', arc, 0.06, P['white'], segs=10)
    tube(r, 'elasticoFriso', [(x, y - 0.045, z) for x, y, z in arc], 0.012, P['red'], segs=6)
    for k, sx in enumerate((-1, 1)):
        for j in range(2):
            box(r, f'tensao{k}{j}', (0.13, 0.03, 0.04), (sx * (0.24 + 0.1 * j), -0.3, 0.6 - 0.12 * j), rot=(0, sx * (0.5 + 0.35 * j), 0), m=P['yellow'], bev=0.012)


# ---------------------------------------------------------------- Joias da Arabia
@icon('overload')
def _(r, P):
    # Choque de Quilates: diamante grande atravessado por uma faisca eletrica
    gem(r, 'diamante', P['diamond'], (0, 0.05, 0.06), s=1.0, rot=(0.0, 0, 0.2))
    bolt_shape(r, 'raio', P['bolt'], (0.3, -0.42, -0.16), s=0.72, rot=0.25)
    sparkle(r, 'brilho0', P['spark'], (-0.42, -0.3, 0.36), 0.13)
    sparkle(r, 'brilho1', P['spark'], (0.46, -0.3, 0.38), 0.09)


@icon('storm')
def _(r, P):
    # Chuva de Brilhantes: nuvem escura despejando diamantes
    cloud(r, 'nuvem', P['cloud_d'], (0, 0, 0.28), 1.0)
    for k, (x, z, s_) in enumerate(((-0.36, -0.2, 0.3), (0.02, -0.38, 0.34), (0.38, -0.18, 0.28), (-0.16, -0.62, 0.26), (0.24, -0.62, 0.24))):
        gem(r, f'brilhante{k}', P['diamond'] if k % 2 == 0 else P['diamond_w'], (x, -0.15, z), s=s_, rot=(0.35, 0.2 * (k - 2), 0.3 * k))
    sparkle(r, 'brilho0', P['spark'], (-0.5, -0.25, -0.45), 0.08)
    sparkle(r, 'brilho1', P['spark'], (0.5, -0.25, -0.42), 0.07)


@icon('flash')
def _(r, P):
    # Clarao de Diamante: diamante no meio de um estouro de luz
    prism(r, 'clarao', star_pts(12, 0.66, 0.3), 0.04, P['glow_y'], loc=(0, 0.22, 0), bev=0.008)
    prism(r, 'clarao2', star_pts(12, 0.5, 0.26, a0=math.pi / 2 + math.pi / 12), 0.05, P['yellow'], loc=(0, 0.16, 0), bev=0.008)
    gem(r, 'diamante', P['diamond_w'], (0, -0.1, 0.06), s=0.62, rot=(0.15, 0, 0.3))
    sparkle(r, 'brilho0', P['spark'], (-0.22, -0.3, 0.28), 0.1)


@icon('burn')
def _(r, P):
    # Ouro Quente: tres lingotes empilhados em brasa, com fogo saindo de cima
    def ingot(name, m, loc):
        bm = bmesh.new()
        lo = [(-0.23, -0.13), (0.23, -0.13), (0.23, 0.13), (-0.23, 0.13)]
        hi = [(-0.17, -0.08), (0.17, -0.08), (0.17, 0.08), (-0.17, 0.08)]
        a = [bm.verts.new((x, y, 0.0)) for x, y in lo]
        b = [bm.verts.new((x, y, 0.2)) for x, y in hi]
        bm.faces.new(a[::-1])
        bm.faces.new(b)
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        o = bm_to_obj(bm, name, r, [m], bev=0.02, seg=3, angle=30)
        o.location = loc
        return o
    ingot('lingote0', P['gold_hot'], (-0.25, 0, -0.5))
    ingot('lingote1', P['gold_hot'], (0.25, 0, -0.5))
    ingot('lingote2', P['gold'], (0, 0.02, -0.3))
    for k, (x, h, w) in enumerate(((-0.12, 0.42, 0.11), (0.04, 0.6, 0.13), (0.17, 0.36, 0.1))):
        flame(r, f'chama{k}', P['fire'], (x, 0.0, -0.12), h=h, w=w)
    flame(r, 'chamaMiolo', P['glow_y'], (0.04, -0.1, -0.12), h=0.24, w=0.06)


# ---------------------------------------------------------------- Petrolao
@icon('cluster')
def _(r, P):
    # Chuva de Barris: tres barris de petroleo despencando, com rastro e gotas de oleo
    for k, (x, z, a, s_) in enumerate(((-0.32, 0.2, 0.45, 0.85), (0.32, 0.26, -0.35, 0.8), (0.0, -0.3, 0.12, 1.0))):
        oil_barrel(r, f'barril{k}', P, (x, 0, z), s=s_, rot=(0.25, a, 0))
        for j in range(3):
            box(r, f'rastro{k}_{j}', (0.035, 0.03, 0.2 - 0.05 * abs(j - 1)), (x + (j - 1) * 0.1 - a * 0.2, 0.1, z + 0.4 * s_ + 0.06), rot=(0, a, 0), m=P['white'], bev=0.012)
    for k, (x, z) in enumerate(((-0.5, -0.2), (0.48, -0.3), (-0.3, -0.55))):
        sphere(r, f'gota{k}', 0.05, (x, -0.1, z), scale=(1, 1, 1.4), m=P['oil'], seg=12)


@icon('barrel')
def _(r, P):
    # Oleo em Chamas: barril aberto pegando fogo sobre uma poca de oleo
    sphere(r, 'poca', 0.5, (0.04, 0.05, -0.56), scale=(1.15, 0.8, 0.1), m=P['oil'], seg=28)
    oil_barrel(r, 'barril', P, (0, 0, -0.22), s=1.3, open_top=True)
    for k, (x, z, s_) in enumerate(((-0.27, -0.06, 1.0), (-0.27, -0.3, 0.7), (0.2, -0.36, 0.8))):
        sphere(r, f'escorrido{k}', 0.035 * s_, (x * 0.95, -0.17, z), scale=(1, 0.6, 2.0), m=P['oil'], seg=10)
    for k in range(5):
        a = TAU * k / 5 + 0.4
        flame(r, f'chama{k}', P['fire'], (0.13 * math.cos(a), 0.13 * math.sin(a) * 0.6, 0.1), h=0.34 + 0.08 * (k % 2), w=0.1)
    flame(r, 'chamaC', P['fire'], (0, 0.0, 0.1), h=0.56, w=0.14)
    flame(r, 'chamaMiolo', P['glow_y'], (0, -0.1, 0.1), h=0.28, w=0.07)


@icon('tremor')
def _(r, P):
    # Tremor de Sonda: broca de perfuracao cravando no chao de terra vermelha, que racha em ondas de choque
    box(r, 'laje', (1.1, 0.6, 0.2), (0, 0.06, -0.5), m=P['earth'], bev=0.05)
    for k, (x, a, L) in enumerate(((-0.28, 0.5, 0.3), (0.26, -0.45, 0.3), (-0.08, 0.1, 0.18), (0.42, 0.2, 0.15))):
        box(r, f'racha{k}', (L, 0.04, 0.05), (x, -0.25, -0.46), rot=(0, a, 0), m=P['dark'], bev=0.008)
    for k, (x, z, s_) in enumerate(((-0.42, -0.22, 1.0), (0.4, -0.18, 0.8), (-0.24, -0.08, 0.6), (0.24, -0.05, 0.7))):
        box(r, f'lasca{k}', (0.09 * s_, 0.08 * s_, 0.07 * s_), (x, -0.15, z), rot=(0.5 * k, 0.4, 0.3 * k), m=P['earth'], bev=0.015)
    for k, R_ in enumerate((0.3, 0.46)):
        o = torus(r, f'onda{k}', (0, 0, 0), R_, 0.022, P['yellow'], axis='Y', n=32, segs=6)
        o.location = (0, -0.22, -0.38)
        o.scale = (1, 1, 0.42)
    # broca: motor amarelo, haste de aco, rosca e ponta
    box(r, 'motor', (0.34, 0.26, 0.22), (0, 0.0, 0.62), m=P['petro'], bev=0.04)
    cyl(r, 'mandril', 0.1, 0.12, (0, 0, 0.47), m=P['dark'], v=16, bev=0.02)
    tube(r, 'haste', [(0, 0, 0.44), (0, 0, -0.18)], 0.055, P['steel'], segs=12)
    hel = [(0.1 * math.cos(t * 3.5 * TAU), 0.1 * math.sin(t * 3.5 * TAU), 0.38 - 0.56 * t) for t in [j / 60 for j in range(61)]]
    tube(r, 'rosca', hel, 0.035, P['iron'], segs=8)
    cyl(r, 'ponta', 0.001, 0.2, (0, 0, -0.27), r2=0.11, m=P['iron'], v=14, bev=0.0)


@icon('chasm')
def _(r, P):
    # Poco sem Fundo: boca de poco com aro de concreto no chao de terra vermelha, escura ate perder de vista
    with grp(r, 'chao', (0, 0, 0), (math.radians(40), 0, 0)):
        cyl(r, 'terra', 0.66, 0.2, (0, 0, -0.1), m=P['earth'], v=44, bev=0.05)
        cyl(r, 'boca', 0.31, 0.02, (0, 0, 0.0), m=P['black'], v=40, bev=0.0)
        for k, (R_, c) in enumerate(((0.25, '#463c43'), (0.18, '#2f282d'), (0.11, '#1d181b'))):
            torus(r, f'fundo{k}', (0, 0, 0.012), R_, 0.02, M(f'poco{k}', c, rough=0.8), n=32, segs=6)
        torus(r, 'aro', (0, 0, 0.03), 0.33, 0.06, P['concrete'], n=40, segs=10)
        for k, ang in enumerate((150, 210, 35, 325, 100, 70)):
            a = math.radians(ang)
            cx, cy = 0.56 * math.cos(a), 0.56 * math.sin(a)
            for j in range(4):
                b = TAU * j / 4 + k
                tube(r, f'capim{k}_{j}', [(cx, cy, 0.0), (cx + 0.06 * math.cos(b), cy + 0.06 * math.sin(b), 0.12 + 0.03 * (j % 2))], 0.016, P['grass'],
                     segs=5, rfun=lambda t: 0.018 * (1 - t) + 0.003)
    coin(r, 'moeda', P, (0.05, -0.32, 0.36), s=0.6, rot=(math.pi / 2 - 0.5, 0.6, 0))
    for k, (x, z) in enumerate(((-0.12, 0.2), (0.18, 0.12))):
        sphere(r, f'pedrinha{k}', 0.04, (x, -0.35, z), m=P['stone'], seg=10)


# ---------------------------------------------------------------- Rachadinha
@icon('charge')
def _(r, P):
    # Carteirada: carteira funcional aberta, distintivo dourado de um lado e cracha do outro, mostrada com tudo
    for k in range(3):
        box(r, f'rastro{k}', (0.3 - 0.06 * k, 0.03, 0.045), (-0.66 + 0.03 * k, 0.05, 0.16 - 0.16 * k), m=P['white'], bev=0.015)
    with grp(r, 'carteira', (0.08, 0, 0), (0, 0, 0)):
        for k, s_ in enumerate((-1, 1)):
            with grp(r, f'banda{k}', (0, 0, 0), (0, 0, s_ * 0.32)):
                box(r, f'couro{k}', (0.46, 0.05, 0.64), (s_ * 0.24, 0, 0), m=P['black'], bev=0.04)
                if s_ < 0:
                    prism(r, 'distintivo', star_pts(7, 0.17, 0.11), 0.05, P['gold'], loc=(-0.24, -0.04, 0.06), bev=0.012)
                    cyl(r, 'distintivoMiolo', 0.07, 0.06, (-0.24, -0.05, 0.06), m=P['navy'], v=20, bev=0.01, rot=(math.pi / 2, 0, 0))
                    box(r, 'distintivoFita', (0.22, 0.04, 0.06), (-0.24, -0.04, -0.18), m=P['gold_d'], bev=0.01)
                else:
                    box(r, 'cracha', (0.36, 0.02, 0.48), (0.24, -0.035, 0), m=P['white'], bev=0.012)
                    box(r, 'crachaFoto', (0.12, 0.02, 0.15), (0.15, -0.045, 0.1), m=P['sky'], bev=0.006)
                    sphere(r, 'crachaRosto', 0.035, (0.15, -0.055, 0.12), m=P['skin'], seg=10)
                    for j in range(3):
                        box(r, f'crachaLinha{j}', (0.12, 0.02, 0.022), (0.31, -0.045, 0.15 - 0.05 * j), m=P['line'], bev=0.004)
                    box(r, 'crachaFaixa', (0.36, 0.022, 0.07), (0.24, -0.045, -0.17), m=P['green'], bev=0.006)
        box(r, 'lombada', (0.07, 0.07, 0.64), (0, 0.02, 0), m=P['black'], bev=0.03)
    sparkle(r, 'brilho0', P['spark'], (-0.12, -0.25, 0.4), 0.11)


@icon('shield')
def _(r, P):
    # Foro Privilegiado: escudo azul de borda dourada protegido pelo martelo de juiz
    pts = [(-0.42, 0.42), (-0.2, 0.47), (0, 0.42), (0.2, 0.47), (0.42, 0.42), (0.42, 0.05), (0.36, -0.2), (0.22, -0.4), (0, -0.56),
           (-0.22, -0.4), (-0.36, -0.2), (-0.42, 0.05)]
    prism(r, 'borda', [(x * 1.12, z * 1.1) for x, z in pts], 0.1, P['gold'], loc=(0, 0.04, 0), bev=0.03)
    prism(r, 'escudo', pts, 0.16, P['navy'], bev=0.04, seg=4)
    prism(r, 'faixa', [(-0.42, 0.12), (0.42, 0.12), (0.42, -0.02), (-0.42, -0.02)], 0.17, P['white'], bev=0.01)
    with grp(r, 'martelo', (0.12, -0.2, -0.02), (0, math.radians(-38), 0)):
        cyl(r, 'cabeca', 0.11, 0.44, (0, 0, 0.2), m=P['wood'], v=24, bev=0.02, rot=(0, math.pi / 2, 0))
        for k, x in enumerate((-0.13, 0.13)):
            cyl(r, f'cinta{k}', 0.116, 0.035, (x, 0, 0.2), m=P['gold'], v=24, bev=0.008, rot=(0, math.pi / 2, 0))
        for k, x in enumerate((-0.23, 0.23)):
            cyl(r, f'face{k}', 0.12, 0.04, (x, 0, 0.2), m=P['wood_l'], v=24, bev=0.012, rot=(0, math.pi / 2, 0))
        tube(r, 'cabo', [(0, 0, 0.1), (0, 0, -0.48)], 0.04, P['wood_l'], segs=10)
        sphere(r, 'caboPonta', 0.055, (0, 0, -0.5), m=P['wood'], seg=12)


@icon('heal')
def _(r, P):
    # Atestado Medico: folha com a cruz vermelha, linhas e a assinatura, e uma capsula na frente
    with grp(r, 'atestado', (-0.08, 0.05, 0.04), (0, math.radians(-6), 0)):
        box(r, 'folha', (0.6, 0.03, 0.8), (0, 0, 0), m=P['paper'], bev=0.015)
        box(r, 'cruzV', (0.08, 0.045, 0.26), (0, -0.02, 0.2), m=P['red'], bev=0.012)
        box(r, 'cruzH', (0.26, 0.045, 0.08), (0, -0.02, 0.2), m=P['red'], bev=0.012)
        for k in range(3):
            box(r, f'linha{k}', (0.42 if k < 2 else 0.28, 0.035, 0.03), (0 if k < 2 else -0.07, -0.018, -0.04 - 0.09 * k), m=P['line'], bev=0.006)
        sig = [(x, -0.03, -0.3 + 0.03 * math.sin(x * 34)) for x in [0.0 + j * 0.02 for j in range(12)]]
        tube(r, 'assinatura', sig, 0.012, P['blue'], segs=6)
    capsule(r, 'capsula', P['red'], P['white'], (0.3, -0.2, -0.32), rot=(0.2, math.radians(55), 0.2), s=1.0)


@icon('palm')
def _(r, P):
    # Pancada de Pasta: pasta 007 preta no meio do golpe, com arcos de movimento e o impacto
    for k in range(3):
        R_ = 0.62 + 0.1 * k
        arc = [(-0.12 + R_ * math.cos(a), -0.1, -0.5 + R_ * math.sin(a)) for a in [math.radians(108 + 6 * k + 9 * j) for j in range(6)]]
        tube(r, f'arco{k}', arc, 0.02, P['white'], segs=6)
    with grp(r, 'pasta', (0.04, 0, -0.04), (0, math.radians(-20), 0)):
        box(r, 'corpo', (0.86, 0.22, 0.58), (0, 0, 0), m=P['case'], bev=0.05, seg=4)
        box(r, 'friso', (0.875, 0.235, 0.035), (0, 0, 0.1), m=P['steel'], bev=0.01)
        for s_ in (-1, 1):
            box(r, f'trava{s_}', (0.1, 0.04, 0.09), (s_ * 0.26, -0.12, 0.1), m=P['gold'], bev=0.012)
            for z in (-0.25, 0.25):
                box(r, f'canto{s_}{z}', (0.07, 0.235, 0.07), (s_ * 0.405, 0, z), m=P['steel'], bev=0.015)
        tube(r, 'alca', [(-0.15, 0, 0.29), (-0.14, 0, 0.42), (0.14, 0, 0.42), (0.15, 0, 0.29)], 0.035, P['case'], segs=10)
    prism(r, 'impacto', star_pts(8, 0.24, 0.1), 0.05, P['yellow'], loc=(0.5, -0.2, -0.4), bev=0.012)
    prism(r, 'impactoMiolo', star_pts(8, 0.14, 0.06, a0=1.8), 0.06, P['orange'], loc=(0.5, -0.23, -0.4), bev=0.01)


# ---------------------------------------------------------------- Lava a Jato
@icon('spring')
def _(r, P):
    # Banho de Loja: sacolas de compras de grife (cura os aliados)
    def bag(name, m, loc, s, rot, handle):
        with grp(r, name, loc, (0, 0, rot), s):
            box(r, name + '_corpo', (0.34, 0.16, 0.42), (0, 0, 0), m=m, bev=0.02)
            box(r, name + '_dobra', (0.345, 0.165, 0.05), (0, 0, 0.17), m=P['white'], bev=0.008)
            for y in (-0.06, 0.06):
                tube(r, f'{name}_alca{y}', [(-0.08, y, 0.2), (-0.07, y, 0.33), (0.07, y, 0.33), (0.08, y, 0.2)], 0.016, handle, segs=6)
    bag('sacolaOuro', P['gold'], (0.02, 0.14, 0.04), 1.15, 0.05, P['black'])
    for k, (x, z) in enumerate(((-0.06, 0.34), (0.06, 0.36), (0.0, 0.42))):
        sphere(r, f'papelSeda{k}', 0.08, (x, 0.12, z), scale=(1, 0.6, 0.8), m=P['pink'] if k % 2 else P['white'], seg=12)
    bag('sacolaRosa', P['pink'], (-0.3, -0.06, -0.14), 1.0, 0.22, P['gold'])
    bag('sacolaTeal', P['teal'], (0.32, -0.1, -0.17), 0.95, -0.25, P['white'])
    box(r, 'cruzV', (0.07, 0.06, 0.24), (0.44, -0.2, 0.34), m=P['green'], bev=0.025)
    box(r, 'cruzH', (0.24, 0.06, 0.07), (0.44, -0.2, 0.34), m=P['green'], bev=0.025)
    sparkle(r, 'brilho0', P['spark'], (-0.42, -0.25, 0.3), 0.09)


@icon('mire')
def _(r, P):
    # Lama do Esquema: poca de lama borbulhando com uma nota e uma moeda afundando
    with grp(r, 'lama', (0, 0, 0), (math.radians(32), 0, 0)):
        sphere(r, 'poca', 0.62, (0, 0, -0.04), scale=(1, 0.85, 0.2), m=P['mud'], seg=32)
        for k, (x, y, s_) in enumerate(((-0.34, -0.2, 0.09), (0.15, -0.3, 0.07), (0.36, 0.12, 0.06), (-0.1, 0.3, 0.07), (0.3, -0.12, 0.05))):
            sphere(r, f'bolha{k}', s_, (x, y, 0.07), m=P['mud_l'], seg=12)
        sphere(r, 'bolhona', 0.15, (0.08, 0.06, 0.08), scale=(1, 1, 0.75), m=P['mud_l'], seg=20)
        sphere(r, 'reflexo', 0.04, (0.04, 0.0, 0.18), m=P['cream'], seg=10)
    note(r, 'nota', P, (-0.26, -0.12, 0.12), rot=(0.2, math.radians(58), 0.3), s=1.25)
    coin(r, 'moeda', P, (0.36, -0.12, 0.08), s=0.75, rot=(math.pi / 2 - 0.25, 0.5, 0.2))
    for k, (x, z) in enumerate(((-0.5, 0.25), (0.12, 0.36), (0.52, 0.3))):
        sphere(r, f'respingo{k}', 0.04, (x, -0.2, z), m=P['mud'], seg=10)


@icon('chill')
def _(r, P):
    # Agua Gelada: dois cubos de gelo, gotas e um floquinho
    box(r, 'gelo0', (0.5, 0.5, 0.5), (-0.16, 0.08, -0.2), rot=(0.25, 0.2, 0.55), m=P['ice'], bev=0.09, seg=4)
    box(r, 'gelo1', (0.4, 0.4, 0.4), (0.26, -0.1, 0.18), rot=(-0.3, 0.45, -0.3), m=P['ice'], bev=0.08, seg=4)
    for k, (x, z, s_) in enumerate(((-0.28, -0.12, 1.0), (0.16, 0.24, 0.8))):
        box(r, f'reflexo{k}', (0.16 * s_, 0.02, 0.04 * s_), (x, -0.28, z), rot=(0, 0.6, 0), m=P['white'], bev=0.01)
    for k, (x, z, s_) in enumerate(((0.42, -0.36, 1.0), (0.22, -0.52, 0.7), (-0.5, 0.3, 0.8))):
        d = lathe(r, f'gota{k}', [(0, 0.0, 0.0), (0.03, 0.07, 0.07), (0.09, 0.08, 0.08), (0.17, 0.035, 0.035), (0.22, 0.0, 0.0)], P['water'], segs=16, lv=2)
        d.location = (x, -0.2, z)
        d.scale = (s_, s_, s_)
    with grp(r, 'floco', (-0.36, -0.22, 0.4), (0, 0, 0), 0.42):
        for k in range(3):
            a = k * math.pi / 3 + math.pi / 2
            tube(r, f'flocoBraco{k}', [(-0.5 * math.cos(a), 0, -0.5 * math.sin(a)), (0.5 * math.cos(a), 0, 0.5 * math.sin(a))], 0.07, P['white'], segs=8)
            for s_ in (-1, 1):
                cx, cz = 0.3 * s_ * math.cos(a), 0.3 * s_ * math.sin(a)
                for t in (-1, 1):
                    b = a + t * 0.8
                    tube(r, f'flocoRamo{k}{s_}{t}', [(cx, 0, cz), (cx + 0.18 * s_ * math.cos(b), 0, cz + 0.18 * s_ * math.sin(b))], 0.05, P['white'], segs=6)
        sphere(r, 'flocoCentro', 0.12, (0, -0.02, 0), m=P['sky'], seg=12)


# ---------------------------------------------------------------- Vaza Jato
@icon('burst')
def _(r, P):
    # Grampo Estourado: monofone vermelho deitado, o fio enrolado com o grampo e o vazamento estourando dele
    with grp(r, 'fone', (-0.08, 0, 0.26), (0, math.radians(-8), 0), 1.2):
        tube(r, 'cabo', [(-0.38, 0, -0.02), (-0.27, 0, 0.13), (0, 0, 0.19), (0.27, 0, 0.13), (0.38, 0, -0.02)], 0.095, P['phone'], segs=14)
        for k, s_ in enumerate((-1, 1)):
            cyl(r, f'concha{k}', 0.17, 0.16, (s_ * 0.4, 0, -0.1), r2=0.12, m=P['phone'], v=28, bev=0.04, rot=(0, s_ * 0.4, 0))
    # fio enrolado descendo da ponta do bocal ate o grampo
    a0, b0 = Vector((0.36, 0.0, 0.02)), Vector((0.22, 0.0, -0.4))
    hel = []
    for j in range(73):
        t = j / 72
        c = a0.lerp(b0, t)
        hel.append((c.x + 0.05 * math.cos(t * 6 * TAU), c.y + 0.05 * math.sin(t * 6 * TAU), c.z))
    tube(r, 'fio', hel, 0.017, P['phone'], segs=6)
    box(r, 'grampo', (0.13, 0.09, 0.08), (0.21, -0.05, -0.45), rot=(0, 0.3, 0), m=P['steel'], bev=0.015)
    box(r, 'grampoMola', (0.05, 0.1, 0.045), (0.13, -0.05, -0.49), rot=(0, 0.3, 0), m=P['iron'], bev=0.01)
    # jato d'agua estourando do grampo para cima e para a esquerda, por baixo do fone
    jt = lathe(r, 'jato', [(0, 0.04, 0.04), (0.2, 0.08, 0.08), (0.42, 0.13, 0.13), (0.5, 0.0, 0.0)], P['water_l'], segs=18, lv=1)
    jt.location = (0.16, -0.1, -0.44)
    jt.rotation_euler = (0, math.radians(-52), 0)
    for k, (x, z, s_) in enumerate(((-0.24, -0.12, 1.0), (-0.36, -0.26, 0.8), (-0.12, -0.02, 0.7), (-0.4, -0.06, 0.6), (-0.2, -0.36, 0.7), (-0.02, -0.2, 0.6))):
        sphere(r, f'gota{k}', 0.06 * s_, (x, -0.14, z), m=P['water'], seg=12)
    sphere(r, 'espuma', 0.1, (-0.18, -0.12, -0.16), m=P['white'], seg=14)


# ---------------------------------------------------------------- Central do Zap
@icon('twister')
def _(r, P):
    # Viralizou: redemoinho verde e branco de mensagens, com baloes de conversa girando em volta
    for k in range(7):
        t = k / 6
        torus(r, f'giro{k}', (0.12 * math.sin(t * 5), 0, -0.5 + t * 1.0), 0.08 + 0.36 * t, 0.06 + 0.02 * t, P['zap'] if k % 2 else P['white'], n=32, segs=8)
    for k, (x, z, s_, tl) in enumerate(((-0.46, 0.34, 0.9, 1), (0.48, 0.02, 0.85, -1), (-0.36, -0.34, 0.75, 1))):
        chat_bubble(r, f'balao{k}', P['white'] if k != 1 else P['zap_l'], (x, -0.3, z), s=s_, dot_m=P['dark'], tail=tl)


@icon('skyward')
def _(r, P):
    # Derruba Aviao: jatinho embicando para baixo com rastro de fumaca e a seta vermelha
    for k, (x, z, s_) in enumerate(((-0.6, 0.55, 0.13), (-0.46, 0.44, 0.11), (-0.34, 0.33, 0.09))):
        sphere(r, f'fumaca{k}', s_, (x, 0.06, z), m=P['grey'], seg=14)
    jet(r, 'jato', P, (-0.02, 0, 0.0), rot=(0.55, 0.75, -0.35), s=1.0)
    arrow3d(r, 'seta', P['red'], (0.5, -0.18, -0.32), s=0.42, up=False)


@icon('shred')
def _(r, P):
    # Audio de 8 Minutos: balao verde de mensagem de voz, botao de play e a onda sonora comprida
    prism(r, 'balao', rrect(1.08, 0.5, 0.2), 0.12, P['zap_l'], bev=0.03)
    prism(r, 'rabo', [(-0.42, -0.2), (-0.28, -0.2), (-0.5, -0.36)], 0.12, P['zap_l'], bev=0.015)
    prism(r, 'play', [(-0.42, -0.11), (-0.42, 0.11), (-0.25, 0.0)], 0.04, P['zap_d'], loc=(0, -0.07, 0), bev=0.012)
    hs = [0.1, 0.22, 0.3, 0.16, 0.34, 0.24, 0.12, 0.28, 0.18, 0.32, 0.14, 0.22]
    for k, h in enumerate(hs):
        x = -0.15 + 0.056 * k
        box(r, f'onda{k}', (0.032, 0.04, h), (x, -0.07, 0), m=P['zap_d'] if k < 5 else P['grey'], bev=0.012)
    sphere(r, 'cursor', 0.05, (-0.15 + 0.056 * 4.5, -0.1, 0), m=P['blue'], seg=12)
    sphere(r, 'avatar', 0.09, (0.62, -0.02, -0.16), m=P['skin'], seg=14)


@icon('blind')
def _(r, P):
    # Fake News nos Olhos: jornal tapando o olho, marcado com o X vermelho
    sphere(r, 'olho', 0.42, (0, 0, 0), scale=(1.18, 0.55, 0.85), m=P['white'], seg=28)
    sphere(r, 'iris', 0.18, (-0.12, -0.17, 0.12), scale=(1, 0.5, 1), m=P['teal'], seg=18)
    sphere(r, 'pupila', 0.08, (-0.12, -0.24, 0.12), scale=(1, 0.5, 1), m=P['black'], seg=12)
    with grp(r, 'jornal', (0.04, -0.3, -0.06), (0, math.radians(-16), 0)):
        box(r, 'folha', (1.08, 0.03, 0.34), (0, 0, 0), m=P['news'], bev=0.012)
        box(r, 'manchete', (0.96, 0.035, 0.06), (0, -0.005, 0.11), m=P['dark'], bev=0.005)
        box(r, 'foto', (0.22, 0.035, 0.14), (-0.33, -0.005, -0.05), m=P['grey'], bev=0.005)
        for k in range(3):
            box(r, f'linha{k}', (0.5, 0.035, 0.022), (0.12, -0.005, 0.03 - 0.055 * k), m=P['line'], bev=0.004)
        for k, a in enumerate((0.75, -0.75)):
            box(r, f'xis{k}', (0.42, 0.05, 0.08), (0.14, -0.03, -0.02), rot=(0, a, 0), m=P['red'], bev=0.02)
    for k, (x, z) in enumerate(((-0.52, 0.42), (0.5, 0.4))):
        sparkle(r, f'tontura{k}', P['yellow'], (x, -0.2, z), 0.09)


# ---------------------------------------------------------------- CPI
@icon('warcry')
def _(r, P):
    # Holofote: refletor de palco apontado para cima, com o feixe de luz
    with grp(r, 'refletor', (-0.18, 0, -0.14), (0, math.radians(42), 0)):
        cyl(r, 'corpo', 0.2, 0.42, (0, 0, 0), m=P['black'], v=28, bev=0.03)
        for k, z in enumerate((-0.06, -0.12, -0.18)):
            torus(r, f'aleta{k}', (0, 0, z), 0.205, 0.016, P['dark'], n=28, segs=6)
        torus(r, 'aro', (0, 0, 0.21), 0.2, 0.035, P['black'], n=28, segs=8)
        cyl(r, 'lente', 0.18, 0.03, (0, 0, 0.215), m=P['glow_y'], v=28, bev=0.0)
        cyl(r, 'feixe', 0.17, 0.72, (0, 0, 0.6), r2=0.42, m=P['beam'], v=32, bev=0.0)
        for k, s_ in enumerate((-1, 1)):
            cyl(r, f'pino{k}', 0.05, 0.06, (0, s_ * 0.22, 0), m=P['iron'], v=12, bev=0.01, rot=(math.pi / 2, 0, 0))
    tube(r, 'garfo', [(-0.18, -0.24, -0.14), (-0.26, -0.24, -0.3), (-0.3, 0, -0.38), (-0.26, 0.24, -0.3), (-0.18, 0.24, -0.14)], 0.03, P['iron'], segs=8)
    tube(r, 'pe', [(-0.3, 0, -0.38), (-0.32, 0, -0.56)], 0.045, P['iron'], segs=10)
    cyl(r, 'base', 0.22, 0.07, (-0.32, 0, -0.58), m=P['dark'], v=28, bev=0.02)
    sparkle(r, 'brilho', P['spark'], (0.5, -0.3, 0.5), 0.1)


@icon('march')
def _(r, P):
    # Discurso Inflamado: microfone pegando fogo
    with grp(r, 'microfone', (-0.06, 0, -0.08), (0, math.radians(28), 0)):
        lathe(r, 'cabo', [(-0.6, 0.05, 0.05), (-0.58, 0.06, 0.06), (-0.2, 0.08, 0.08), (0.0, 0.095, 0.095)], P['black'], segs=20, lv=1)
        cyl(r, 'anel', 0.11, 0.08, (0, 0, 0.04), m=P['gold'], v=24, bev=0.015)
        sphere(r, 'globo', 0.2, (0, 0, 0.25), m=M('grade_microfone', '#b8c0c8', rough=0.35, metal=0.7, stripes=(40.0, '#c9d2dc', '#7d858e')), seg=28)
        torus(r, 'globoAro', (0, 0, 0.25), 0.2, 0.016, P['steel'], axis='Y', n=28, segs=6)
        box(r, 'botao', (0.04, 0.05, 0.08), (0, -0.085, -0.22), m=P['red'], bev=0.01)
    for k, (x, h, w) in enumerate(((0.0, 0.36, 0.1), (0.14, 0.52, 0.13), (0.28, 0.34, 0.1))):
        flame(r, f'chama{k}', P['fire'], (x, 0.0, 0.26), h=h, w=w)
    flame(r, 'chamaMiolo', P['glow_y'], (0.14, -0.1, 0.26), h=0.22, w=0.06)


@icon('mark')
def _(r, P):
    # Convocacao: envelope oficial lacrado com o selo de cera vermelha
    box(r, 'envelope', (0.92, 0.06, 0.6), (0, 0, 0), m=P['envelope'], bev=0.02)
    prism(r, 'aba', [(-0.45, 0.29), (0.45, 0.29), (0, -0.06)], 0.02, P['envelope_d'], loc=(0, -0.04, 0), bev=0.008)
    for k, s_ in enumerate((-1, 1)):
        tube(r, f'dobra{k}', [(s_ * 0.45, -0.035, -0.29), (s_ * 0.06, -0.035, -0.02)], 0.008, P['envelope_d'], segs=5)
    cyl(r, 'selo', 0.15, 0.05, (0, -0.07, -0.06), m=P['red_d'], v=28, bev=0.02, rot=(math.pi / 2, 0, 0))
    for k in range(5):
        a = TAU * k / 5 + 0.3
        sphere(r, f'pingo{k}', 0.045, (0.15 * math.cos(a), -0.07, -0.06 + 0.15 * math.sin(a)), scale=(1, 0.5, 1), m=P['red_d'], seg=10)
    prism(r, 'seloEstrela', star_pts(5, 0.08, 0.035), 0.02, P['red'], loc=(0, -0.1, -0.06), bev=0.005)
    for k, a in enumerate((0.35, -0.35)):
        box(r, f'fita{k}', (0.07, 0.02, 0.24), (0.07 * (1 if k else -1), -0.05, -0.3), rot=(0, a, 0), m=P['gold'], bev=0.008)


@icon('bounty')
def _(r, P):
    # Acordo de Leniencia: aperto de maos entre dois paletos e a moeda brilhando em cima
    for k, (sx, sleeve, skin) in enumerate(((-1, P['suit'], P['skin']), (1, P['suit_g'], P['skin2']))):
        tube(r, f'manga{k}', [(sx * 0.72, 0.02, -0.46), (sx * 0.46, 0.0, -0.26), (sx * 0.26, 0.0, -0.11)], 0.12, sleeve, segs=14)
        tube(r, f'punho{k}', [(sx * 0.27, 0.0, -0.115), (sx * 0.19, 0.0, -0.055)], 0.1, P['white'], segs=14)
        sphere(r, f'mao{k}', 0.13, (sx * 0.07, -0.01 * k, 0.0), scale=(1.45, 0.95, 0.88), m=skin, seg=20)
    for k in range(4):
        z = 0.08 - 0.05 * k
        pts = [(0.06, -0.08, z), (-0.03, -0.13, z), (-0.13, -0.11, z - 0.02)]
        tube(r, f'dedo{k}', pts, 0.033, P['skin2'], segs=8)
        sphere(r, f'dedoPonta{k}', 0.033, pts[-1], m=P['skin2'], seg=10)
    tube(r, 'polegar', [(-0.12, -0.04, 0.08), (-0.02, -0.07, 0.13), (0.07, -0.08, 0.12)], 0.04, P['skin'], segs=8)
    coin(r, 'moeda', P, (0, -0.06, 0.44), s=0.85)
    sparkle(r, 'brilho0', P['spark'], (0.24, -0.15, 0.6), 0.09)
    sparkle(r, 'brilho1', P['spark'], (-0.26, -0.15, 0.36), 0.07)


# ---------------------------------------------------------------- Banco Vorcash
@icon('mercs')
def _(r, P):
    # Centrao de Aluguel: etiqueta de preco vermelha pendurada no barbante, com uma moeda
    tube(r, 'barbante', [(-0.4, -0.02, 0.12), (-0.5, -0.02, 0.3), (-0.42, -0.02, 0.48), (-0.24, -0.02, 0.52), (-0.08, -0.02, 0.42)], 0.016, P['cream'], segs=6)
    with grp(r, 'etiqueta', (0.05, 0, -0.06), (0, math.radians(-28), 0)):
        pts = [(-0.58, 0.0), (-0.32, 0.27), (0.5, 0.27), (0.5, -0.27), (-0.32, -0.27)]
        prism(r, 'placa', pts, 0.07, P['red'], bev=0.04, seg=4)
        torus(r, 'ilhos', (-0.36, 0, 0), 0.06, 0.022, P['gold'], axis='Y', n=20, segs=6)
        cyl(r, 'furo', 0.045, 0.08, (-0.36, 0, 0), m=P['black'], v=16, bev=0.0, rot=(math.pi / 2, 0, 0))
    coin(r, 'moeda', P, (0.16, -0.08, -0.13), s=0.75, rot=(math.pi / 2, 0, 0))


@icon('caravan')
def _(r, P):
    # Emenda de Relator: envelope pardo estufado de notas, com moedas escapando
    with grp(r, 'envelopePardo', (-0.04, 0, 0), (0, math.radians(-10), math.radians(-12))):
        prism(r, 'aba', [(-0.4, 0.0), (0.4, 0.0), (0.0, 0.32)], 0.025, P['kraft_d'], loc=(0, 0.05, 0.1), rot=(-0.25, 0, 0), bev=0.01)
        for k, a in enumerate((0.45, 0.15, -0.15, -0.45)):
            note(r, f'nota{k}', P, (-0.2 + 0.13 * k, 0.0, 0.2 + 0.05 * (1 - abs(a) * 2)), rot=(0, math.pi / 2 + a, 0), s=1.1)
        box(r, 'envelope', (0.8, 0.07, 0.6), (0, 0.0, -0.2), m=P['kraft'], bev=0.025)
        for k, s_ in enumerate((-1, 1)):
            tube(r, f'dobra{k}', [(s_ * 0.4, -0.038, -0.5), (s_ * 0.05, -0.038, -0.24)], 0.008, P['kraft_d'], segs=5)
        for k, z in enumerate((0.02, -0.2)):
            cyl(r, f'botao{k}', 0.05, 0.02, (0.0, -0.045, z), m=P['kraft_d'], v=16, bev=0.005, rot=(math.pi / 2, 0, 0))
        tube(r, 'cordao', [(0.0, -0.06, 0.02), (0.06, -0.06, -0.06), (-0.06, -0.06, -0.13), (0.0, -0.06, -0.2)], 0.012, P['red_d'], segs=5)
    for k, (x, z, rot) in enumerate(((0.44, -0.4, (math.pi / 2, 0.4, 0)), (0.56, -0.24, (math.pi / 2 - 0.3, -0.3, 0.2)), (0.3, -0.52, (0.3, 0, 0.2)))):
        coin(r, f'moeda{k}', P, (x, -0.16, z), s=0.65, rot=rot)


@icon('compound')
def _(r, P):
    # Juros Magicos: pilhas de moedas crescendo, a seta verde subindo e brilhos de magica
    for k in range(3):
        for j in range(2 + 2 * k):
            cyl(r, f'moeda{k}_{j}', 0.15, 0.07, (-0.38 + 0.32 * k, 0.05, -0.5 + j * 0.08), m=P['gold'], v=24, bev=0.015)
    pts = [(-0.52, -0.2, -0.2), (-0.2, -0.2, 0.02), (0.0, -0.2, -0.04), (0.36, -0.2, 0.32)]
    tube(r, 'seta', pts, 0.045, P['urna'], segs=10)
    d = Vector(pts[-1]) - Vector(pts[-2])
    d.normalize()
    cyl(r, 'setaPonta', 0.12, 0.22, Vector(pts[-1]) + d * 0.1, r2=0.0, m=P['urna'], v=16, bev=0.01, rot=axis_rot(d))
    for k, (x, z, s_) in enumerate(((-0.38, 0.32, 0.11), (0.08, 0.5, 0.09), (0.52, 0.0, 0.08))):
        sparkle(r, f'magica{k}', P['spark'] if k != 1 else P['violet'], (x, -0.25, z), s_)


@icon('vault')
def _(r, P):
    # O FGC Garante: cofre verde de aco com o segredo e o volante
    box(r, 'cofre', (0.82, 0.62, 0.8), (0, 0.05, -0.04), m=P['safe'], bev=0.06, seg=4)
    box(r, 'porta', (0.66, 0.06, 0.64), (0, -0.27, -0.04), m=P['safe_l'], bev=0.03)
    for k, z in enumerate((0.16, -0.24)):
        cyl(r, f'dobradica{k}', 0.04, 0.12, (-0.35, -0.28, z), m=P['steel'], v=12, bev=0.01)
    cyl(r, 'segredo', 0.15, 0.05, (-0.05, -0.31, 0.08), m=P['steel'], v=32, bev=0.015, rot=(math.pi / 2, 0, 0))
    cyl(r, 'segredoMiolo', 0.06, 0.06, (-0.05, -0.33, 0.08), m=P['black'], v=16, bev=0.01, rot=(math.pi / 2, 0, 0))
    for k in range(12):
        a = TAU * k / 12
        box(r, f'marca{k}', (0.012, 0.02, 0.03), (-0.05 + 0.12 * math.cos(a), -0.34, 0.08 + 0.12 * math.sin(a)), rot=(0, -a + math.pi / 2, 0), m=P['black'], bev=0.0)
    cx, cz = 0.14, -0.2
    sphere(r, 'volanteCubo', 0.05, (cx, -0.33, cz), m=P['gold'], seg=12)
    for k in range(3):
        a = TAU * k / 3 + 0.4
        tube(r, f'volanteRaio{k}', [(cx, -0.33, cz), (cx + 0.14 * math.cos(a), -0.36, cz + 0.14 * math.sin(a))], 0.018, P['gold'], segs=6)
        sphere(r, f'volantePonta{k}', 0.032, (cx + 0.14 * math.cos(a), -0.36, cz + 0.14 * math.sin(a)), m=P['gold'], seg=10)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(r, f'pe{sx}{sy}', (0.1, 0.1, 0.06), (sx * 0.32, 0.05 + sy * 0.22, -0.47), m=P['black'], bev=0.015)
    prism(r, 'selo', star_pts(8, 0.12, 0.09), 0.03, P['gold'], loc=(0.28, -0.32, 0.26), bev=0.008)


# ---------------------------------------------------------------- operacoes (feiticos)
@icon('fury')
def _(r, P):
    # Operacao da PF: viatura preta de 3/4 com o giroflex azul e vermelho aceso no teto
    with grp(r, 'viatura', (0, 0, 0), (0, 0, math.radians(-30))):
        box(r, 'carroceria', (1.15, 0.52, 0.26), (0, 0, -0.18), m=P['car'], bev=0.07, seg=4)
        prism(r, 'cabine', [(-0.44, -0.06), (0.24, -0.06), (0.1, 0.2), (-0.38, 0.2)], 0.46, P['car'], bev=0.04)
        prism(r, 'vidro', [(-0.4, -0.04), (0.19, -0.04), (0.07, 0.17), (-0.35, 0.17)], 0.48, P['glass'], bev=0.01)
        box(r, 'coluna', (0.05, 0.49, 0.21), (-0.1, 0, 0.07), m=P['car'], bev=0.01)
        box(r, 'faixa', (1.16, 0.53, 0.035), (0, 0, -0.13), m=P['white'], bev=0.005)
        for x in (-0.36, 0.36):
            for y in (-0.25, 0.25):
                cyl(r, f'pneu{x}{y}', 0.14, 0.11, (x, y, -0.31), m=P['tire'], v=24, bev=0.02, rot=(math.pi / 2, 0, 0))
                cyl(r, f'calota{x}{y}', 0.07, 0.115, (x, y, -0.31), m=P['steel'], v=16, bev=0.01, rot=(math.pi / 2, 0, 0))
        for y in (-0.17, 0.17):
            box(r, f'farol{y}', (0.03, 0.1, 0.05), (0.575, y, -0.13), m=P['glow_y'], bev=0.008)
        box(r, 'grade', (0.03, 0.2, 0.06), (0.575, 0, -0.21), m=P['dark'], bev=0.008)
        box(r, 'barraLuz', (0.12, 0.38, 0.04), (-0.12, 0, 0.215), m=P['dark'], bev=0.01)
        for k, (y, m) in enumerate(((0.1, P['siren_r']), (-0.1, P['siren_b']))):
            sphere(r, f'giroflex{k}', 0.08, (-0.12, y, 0.25), scale=(1.0, 1.15, 0.8), m=m, seg=16)
    for k, (x, z, m) in enumerate(((-0.26, 0.42, P['siren_r']), (0.0, 0.48, P['siren_b']), (-0.42, 0.32, P['siren_r']), (0.18, 0.38, P['siren_b']))):
        box(r, f'clarao{k}', (0.03, 0.03, 0.12), (x, -0.2, z), rot=(0, (x + 0.12) * 1.6, 0), m=m, bev=0.01)


@icon('riders')
def _(r, P):
    # Bancada de Apoio: duas maos levantadas votando (dois deputados aliados)
    raised_hand(r, 'maoE', P, (-0.22, 0.08, -0.02), P['skin2'], P['suit_g'], s=0.92, rot=(0, math.radians(14), 0))
    raised_hand(r, 'maoD', P, (0.2, -0.06, 0.06), P['skin'], P['suit'], s=1.0, rot=(0, math.radians(-10), 0))


# ---------------------------------------------------------------- botoes do anel
@icon('upgrade')
def _(r, P):
    # Evoluir: a seta verde do CONFIRMA da urna
    arrow3d(r, 'seta', P['urna'], (0, 0, 0), s=1.15)
    sparkle(r, 'brilho', P['spark'], (0.42, -0.2, 0.5), 0.1)


@icon('sell')
def _(r, P):
    # Vender: maco de notas com cinta de papel e moedas na frente (a verba volta)
    with grp(r, 'maco', (-0.08, 0.06, 0.08), (0, math.radians(-8), math.radians(-24))):
        for k in range(6):
            note(r, f'nota{k}', P, (0.004 * (k % 2), 0.02 * k - 0.05, 0.004 * (k % 3)), s=2.2)
        box(r, 'cinta', (0.16, 0.16, 0.39), (0.0, 0.0, 0.0), m=P['white'], bev=0.01)
    coin(r, 'moeda0', P, (0.32, -0.2, -0.3), s=0.85)
    coin(r, 'moeda1', P, (-0.02, -0.26, -0.38), s=0.7, rot=(math.pi / 2 - 0.2, 0.3, 0))


@icon('rally')
def _(r, P):
    # Encontro: bandeira laranja de obra num bloco de concreto (ponto de encontro da tropa)
    box(r, 'base', (0.44, 0.34, 0.16), (-0.2, 0, -0.56), m=P['concrete'], bev=0.04)
    tube(r, 'mastro', [(-0.2, 0, -0.5), (-0.2, 0, 0.58)], 0.035, P['steel'], segs=10)
    sphere(r, 'pomo', 0.065, (-0.2, 0, 0.62), m=P['gold'], seg=12)
    fl = cloth_grid(r, 'bandeira', 0.62, 0.4, 12, 4, [M('bandeira_obra', '#f07a22', rough=0.6, stripes=(2.4, '#f07a22', '#f6f1e6'))], thick=0.03,
                    shape=lambda u, v, co: Vector((co.x, co.y + 0.05 * math.sin(u * 5), co.z)))
    fl.location = (-0.18, 0, 0.56)


@icon('ruin')
def _(r, P):
    # Obra parada: pilar de concreto pela metade, ferragem enferrujada para fora, entulho e o cone tombado
    sphere(r, 'monte', 0.5, (0, 0.05, -0.54), scale=(1.15, 0.8, 0.2), m=P['earth'], seg=24)
    for k, (x, z, s_, a) in enumerate(((-0.4, -0.46, 1.0, 0.4), (0.12, -0.5, 0.8, -0.3), (-0.2, -0.5, 0.7, 0.9), (0.42, -0.48, 0.65, 0.2))):
        box(r, f'entulho{k}', (0.18 * s_, 0.16 * s_, 0.12 * s_), (x, -0.08, z), rot=(0.3, a * 0.4, a), m=P['concrete_d'] if k % 2 else P['concrete'], bev=0.025)
    pil = [(-0.27, -0.45), (0.27, -0.45), (0.27, 0.04), (0.17, 0.14), (0.08, 0.0), (-0.04, 0.2), (-0.15, 0.06), (-0.27, 0.12)]
    prism(r, 'pilar', pil, 0.42, P['concrete'], loc=(-0.08, 0.04, 0.0), bev=0.035)
    for k, (x, y, bend) in enumerate(((-0.26, -0.1, -0.1), (0.04, -0.1, 0.12), (-0.22, 0.14, -0.14), (0.08, 0.14, 0.16))):
        tube(r, f'ferro{k}', [(x, y, 0.0), (x, y, 0.42), (x + bend * 0.5, y, 0.54), (x + bend, y, 0.58)], 0.026, P['rust'], segs=6)
    with grp(r, 'cone', (0.36, -0.2, -0.38), (0, math.radians(76), math.radians(28)), 1.2):
        box(r, 'coneBase', (0.34, 0.34, 0.04), (0, 0, 0.02), m=P['obra'], bev=0.015)
        lathe(r, 'coneCorpo', [(0.0, 0.14, 0.14), (0.04, 0.13, 0.13), (0.46, 0.035, 0.035), (0.48, 0.0, 0.0)], P['obra'], segs=24, lv=1)
        lathe(r, 'coneFaixa', [(0.18, 0.106, 0.106), (0.28, 0.08, 0.08)], P['white'], segs=24, lv=1, caps=False).scale = (1.04, 1.04, 1)


@icon('work')
def _(r, P):
    # Obra: capacete amarelo com o martelo atras
    with grp(r, 'martelo', (0.14, 0.18, 0.0), (0, math.radians(-38), 0)):
        tube(r, 'cabo', [(0, 0, -0.55), (0, 0, 0.36)], 0.05, P['wood_l'], segs=10)
        box(r, 'cabeca', (0.44, 0.15, 0.15), (0.04, 0, 0.42), m=P['iron'], bev=0.03)
        cyl(r, 'face', 0.085, 0.05, (0.27, 0, 0.42), m=P['steel'], v=16, bev=0.01, rot=(0, math.pi / 2, 0))
    hard_hat(r, 'capacete', P['hat'], (-0.06, -0.12, -0.32), s=1.05)


def queue(r, P, hi):
    """Fila de tres bonecos andando para a direita; o alvo fica maior, colorido e com a seta dourada em cima."""
    xs = (-0.44, 0.0, 0.44)
    for k, x in enumerate(xs):
        on = k == hi
        body = (P['red'] if hi == 2 else P['teal']) if on else P['grey']
        pawn(r, f'boneco{k}', P, body, (x, 0, -0.5), s=1.3 if on else 0.92)
    arrow3d(r, 'seta', P['gold'], (xs[hi], -0.05, 0.5), s=0.36, up=False)


@icon('prio_first')
def _(r, P):
    # Alvo: o primeiro da fila
    queue(r, P, 2)


@icon('prio_last')
def _(r, P):
    # Alvo: o ultimo da fila
    queue(r, P, 0)


@icon('prio_strong')
def _(r, P):
    # Alvo: o mais forte (coroa dourada)
    sphere(r, 'veludo', 0.36, (0, 0.04, -0.06), scale=(1.0, 1.0, 0.75), m=P['red_d'], seg=24)
    cyl(r, 'aro', 0.42, 0.24, (0, 0, -0.22), m=P['gold'], v=40, bev=0.02)
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.62
        x, y = 0.4 * math.cos(a), 0.4 * math.sin(a)
        cyl(r, f'ponta{k}', 0.1, 0.32, (x, y, 0.06), r2=0.0, m=P['gold'], v=12, bev=0.0)
        sphere(r, f'perola{k}', 0.055, (x, y, 0.24), m=P['white'], seg=12)
    for k in range(3):
        a = -math.pi / 2 + (k - 1) * 0.55
        sphere(r, f'joia{k}', 0.075, (0.43 * math.cos(a), 0.43 * math.sin(a), -0.22), m=(P['red'], P['green'], P['blue'])[k], seg=14)


@icon('prio_flying')
def _(r, P):
    # Alvo: os voadores (jatinho subindo com o rastro branco)
    for k in range(5):
        sphere(r, f'rastro{k}', 0.07 + 0.015 * k, (-0.6 + 0.1 * k, 0.1, -0.52 + 0.09 * k), m=P['white'], seg=12)
    jet(r, 'jato', P, (0.08, 0, 0.04), rot=(0.55, -0.62, -0.25), s=1.25)


# ---------------------------------------------------------------- render
def build_all(only=None):
    clear_scene()
    sc = bpy.context.scene
    ST['coll'] = sc.collection
    setup_scene()
    try:
        bpy.context.preferences.addons['cycles'].preferences.metalrt = 'OFF'
    except Exception:
        pass
    palette2()
    P = C()
    bpy.data.objects['ChaoSombra'].hide_render = True
    roots = {}
    for i, (name, fn) in enumerate(ICONS.items()):
        if only and name not in only:
            continue
        root = make_root('raiz_' + name, name, coll_for('ic_' + name))
        fn(root, P)
        # vira o icone um pouco para a camera (de frente e levemente de cima)
        root.rotation_euler = (math.radians(-25), 0, 0)
        roots[name] = root
    bpy.context.view_layer.update()
    return roots


def render_icons(out, only=None):
    roots = build_all(only)
    sc = bpy.context.scene
    sc.cycles.samples = 48
    os.makedirs(out, exist_ok=True)
    cam = bpy.data.objects['CamJogo']
    meta = {'family': 'icones', 'px_per_game': PX_PER_GAME, 'game_per_bu': GAME_PER_BU, 'sets': {}}
    mp = os.path.join(out, 'meta.json')
    if os.path.exists(mp):
        meta = json.load(open(mp))
    for name, root in roots.items():
        set_visible({name})
        bpy.data.objects['ChaoSombra'].hide_render = True   # o pegador de sombra cortava tudo abaixo de z = 0
        objs = meshes_of({name})
        lo, hi = bounds_of(objs)
        side = max(hi[0] - lo[0], hi[1] - lo[1]) * 1.12
        cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
        ST['px'] = ICON_PX / side
        frame_camera(cam, (cx - side / 2, cy - side / 2), (cx + side / 2, cy + side / 2), margin=(0, 0, 0, 0))
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        render_to(os.path.join(d, 'still_00.png'))
        w, h = sc.render.resolution_x, sc.render.resolution_y
        meta['sets'][name] = {'w': w, 'h': h, 'anchor': [w / 2, h / 2], 'modes': {'still': 1}, 'icon': 1}
        print('OK', name, flush=True)
    with open(mp, 'w') as fh:
        json.dump(meta, fh, indent=1)


def still_sheet(path, only=None):
    roots = build_all(only)
    names = list(roots)
    cols = 8 if len(names) > 8 else len(names)
    for i, name in enumerate(names):
        roots[name].location = ((i % cols) * 1.6, 0, -(i // cols) * 1.6 * 1.0)
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name != 'ChaoSombra':
            o.hide_render = False
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'ChaoSombra' and not o.hide_render]
    lo, hi = bounds_of(objs)
    ST['px'] = 100 if not only else 150
    frame_camera(bpy.data.objects['CamJogo'], lo, hi, margin=(0.3, 0.3, 0.3, 0.3))
    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.cycles.samples = 24
    render_to(path)


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'render':
        render_icons(args[1], set(args[2:]) or None)
        print('RENDER_OK', args[1])
    elif args and args[0] == 'still':
        still_sheet(args[1], set(args[2:]) or None)
        print('STILL_OK', args[1])
