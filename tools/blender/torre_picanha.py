"""Churrascao da Picanha (Ninguem Sobe a Rampa, so a Chapa Vermelha): a arte da familia magos (engine 'mage') do lado R.
Meme: a promessa de campanha da "picanha e cervejinha". Churrasqueira de tijolinho com coifa vermelha (estrela branca),
chamine soltando fumaca, brasa acesa, grelha com espetos de picanha girando, a bancada lateral onde o churrasqueiro
trabalha (de avental por cima da camiseta vermelha com estrela, bone vermelho e jeans) e, no alto, a picanha
flutuando sobre a chama (o antigo orbe: e dela que sai o disparo). Isopor com latinhas e saco de carvao no pe.
Nada de marca, letra ou numero.

  niveis 1 a 3 (mg1, mg2, mg3): a churrasqueira cresce; no N2 um caneco de chope orbita, no N3 ela fica sobre as
                               colunas da Alvorada e orbitam o caneco e um espetinho
  Rodizio (mgL, 'lightning'):  carrossel de espetos girando sobre o braseiro, linguica enrolada no pedestal e
                               espetinhos voando em volta da picanha do alto (os espetos que saltam entre inimigos)
  Macarico do Churrasqueiro (mgS, 'sun'): macarico culinario gigante (cartucho vermelho com a estrela) soltando o
                               jato de chama azul pelo bico (o ponto 'top' e a ponta do bico, de onde sai o raio)

Mesmos conjuntos, postos, modos, quadros e pontos da Lanterna/Joias (js/sprites.js depende deles): mg1, mg2, mg3, mgL,
mgS e a tripulacao mgA, mgB, mgC, mgE, mgP (idle 12 e cast 8; ponto 'top'). A turma 'lanca' girando o espeto.
So existe na chapa R (o lado V continua com as Joias da Arabia de torre_magos.py):

  CHAPA=R Blender -b -P tools/blender/torre_picanha.py -- render arte/render_r/magos [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_picanha.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_picanha.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('CHAPA', 'R')   # torre so da Chapa Vermelha
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete   # noqa: F811 - lote de concreto branco de Brasilia
from pecas_zcv import slab, HC
from chapa import CHAPA, PAL, cor, estrela, bandeirinha, estrela_peito

G = 0.07   # chao do lote no codigo (topo 0.15 menos o LIFT que o build_family soma)
FRONT = -math.pi / 2
FAM = 'magos'

import lib as _lib
_orig_palette2 = palette2


def palette2():   # noqa: F811 - tijolinho, brasa, picanha e as cores da chapa
    P = _orig_palette2()
    P['concrete'] = mat('concreto', '#efebe2', rough=0.88, var=0.03, bump=0.18)
    P['conc_l'] = concrete()
    P['brick'] = [mat('tijolo_a', '#c4663f', rough=0.86, var=0.05, bump=0.3), mat('tijolo_b', '#b0543a', rough=0.86, var=0.05, bump=0.3),
                  mat('tijolo_c', '#d27d50', rough=0.86, var=0.05, bump=0.3)]
    P['mortar_l'] = mat('rejunte', '#ebe0cf', rough=0.92, var=0.02, bump=0.15)
    P['coifa'] = cor('pri', rough=0.42, var=0.02, bump=0.02)
    P['coifa_d'] = cor('escuro', rough=0.5)
    P['branco'] = cor('sec', rough=0.45)
    P['soot'] = mat('fuligem', '#2a2220', rough=0.95, var=0.02, bump=0.2)
    P['coal'] = mat('carvao', '#302826', rough=0.9, var=0.12, bump=0.4)
    P['ember'] = glow_mat('brasa_churrasco', '#ff5a1e', 1.4, 10.0, rough=0.7, var=0.15, bump=0.2)
    P['fire'] = glow_mat('fogo_churrasco', '#ff8f2a', 3.0, 16.0, rough=0.5, var=0.0, bump=0.0)
    P['fire_y'] = glow_mat('fogo_miolo', '#ffd75a', 3.5, 18.0, rough=0.5, var=0.0, bump=0.0)
    P['spark'] = glow_mat('fagulha', '#ffb347', 2.4, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['blue'] = glow_mat('chama_azul', '#3d9bff', 2.6, 14.0, rough=0.3, var=0.0, bump=0.0)
    P['blue_w'] = glow_mat('chama_azul_miolo', '#d9f3ff', 4.0, 20.0, rough=0.3, var=0.0, bump=0.0)
    P['grill'] = mat('grelha', '#3a3432', rough=0.45, metal=0.6, var=0.02, bump=0.02)
    P['steel'] = mat('aco_espeto', '#d5dade', rough=0.25, metal=0.85, var=0.02, bump=0.0)
    P['crust'] = mat('picanha_crosta', '#8c3420', rough=0.6, var=0.06, bump=0.25)
    P['meat_in'] = mat('picanha_miolo', '#d0473f', rough=0.55, var=0.04, bump=0.1)
    P['fat'] = mat('picanha_gordura', '#f2d9a8', rough=0.45, var=0.03, bump=0.1, sheen=0.3)
    P['sausage'] = mat('linguica', '#a9432c', rough=0.38, var=0.08, bump=0.08)
    P['heart'] = mat('coracaozinho', '#7c2a26', rough=0.4, var=0.08, bump=0.08)
    P['smoke'] = mat('fumaca', '#f1ede8', rough=1.0, var=0.05, bump=0.05)
    P['beer'] = glow_mat('chope', '#f6b425', 0.25, 2.0, rough=0.12, var=0.0, bump=0.0)
    P['foam_b'] = mat('colarinho', '#fffaf0', rough=0.6, var=0.02, bump=0.2)
    P['glass_l'] = mat('vidro_caneco', '#e6f3f5', rough=0.08, var=0.0, bump=0.0)
    P['styro'] = mat('isopor', '#f6f4ee', rough=0.95, var=0.02, bump=0.35)
    P['can'] = mat('lata', '#d3d8dc', rough=0.25, metal=0.85, var=0.04, bump=0.0)
    P['can_top'] = mat('lata_tampa', '#e9c55c', rough=0.3, metal=0.8, var=0.0, bump=0.0)
    P['ice'] = mat('gelo', '#d6f1ff', rough=0.08, var=0.03, bump=0.02)
    P['kraft'] = mat('saco_carvao', '#c99b5c', rough=0.85, var=0.04, bump=0.12)
    P['bark'] = mat('casca_lenha', '#6e4328', rough=0.9, var=0.08, bump=0.4)
    P['log_end'] = mat('miolo_lenha', '#dcb27a', rough=0.85, var=0.05, bump=0.2)
    P['board'] = mat('tabua', '#c88d4c', rough=0.7, var=0.05, bump=0.15)
    P['knife_h'] = mat('cabo_faca', '#2b2422', rough=0.5, var=0.0, bump=0.0)
    P['torch_k'] = mat('macarico_cabeca', '#2c2b30', rough=0.35, metal=0.3, var=0.0, bump=0.02)
    P['torch_o'] = mat('macarico_gatilho', '#ff8a1f', rough=0.4, var=0.0, bump=0.0)
    P['_emblem'] = 'star'
    return P


_lib.palette2 = palette2


# ---------------------------------------------------------------- formas basicas
def frustum(root, name, size, top, h, loc, m, toff=(0.0, 0.0), bev=0.012, front=False):
    """Tronco de piramide retangular: base size=(w, d), topo top=(wt, dt) deslocado de toff, altura h."""
    bm = bmesh.new()
    (w, d), (wt, dt) = size, top
    a = [bm.verts.new((sx * w / 2, sy * d / 2, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    b = [bm.verts.new((toff[0] + sx * wt / 2, toff[1] + sy * dt / 2, h)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], a[j], b[j], b[i]))
    o = bm_to_obj(bm, name, root, [m], bev=bev, angle=30, front=front)
    o.location = loc
    return o


def brick_face_into(bm, x0, x1, z0, z1, y, bw=0.09, bh=0.04, gap=0.008, dep=0.014, seed=1):
    """Tijolinhos aparentes numa face voltada para -Y (plano y), em fiadas desencontradas; 3 tons (indice de material)."""
    rr = random.Random(seed)
    rows = max(1, int(round((z1 - z0) / (bh + gap))))
    hh = (z1 - z0) / rows - gap
    for r in range(rows):
        zc = z0 + gap / 2 + hh / 2 + r * (hh + gap)
        x = x0 - ((bw + gap) / 2 if r % 2 else 0.0)
        while x < x1 - 1e-4:
            a, b = max(x, x0) + gap / 2, min(x + bw + gap, x1) - gap / 2
            if b - a > 0.012:
                res = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(((a + b) / 2, y - dep / 2, zc)) @ Matrix.Diagonal((b - a, dep, hh, 1)))
                mi = rr.choice((0, 0, 1, 2))
                for f in {f for v in res['verts'] for f in v.link_faces}:
                    f.material_index = mi
            x += bw + gap


def brick_block(root, P, tag, cx, cy, w, d, z0, h, front=False, seed=1):
    """Bloco de alvenaria: miolo de rejunte claro com os tijolinhos aparentes na frente (a face que a camera ve)."""
    box(root, tag + '_miolo', (w - 0.004, d - 0.004, h), (cx, cy, z0 + h / 2), m=P['mortar_l'], bev=0.008, front=front)
    bm = bmesh.new()
    brick_face_into(bm, cx - w / 2, cx + w / 2, z0, z0 + h, cy - d / 2, seed=seed)
    return bm_to_obj(bm, tag + '_tijolos', root, P['brick'], bev=0.004, angle=35, front=front)


def arc_box_into(bm, c, ri, ro, w, a0, a1, n=10, mi=(0, 0, 0), flip=1):
    """Fatia em arco no plano XZ (centro c): raio de ri a ro, largura w em Y, angulos a0..a1. mi = (dentro, fora, lados)."""
    cx, cy, cz = c
    secs = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        ca, sa = math.cos(a), math.sin(a) * flip
        secs.append([bm.verts.new((cx + r * ca, cy + yy, cz + r * sa)) for r in (ri, ro) for yy in (-w / 2, w / 2)])

    def f(vs, m):
        bm.faces.new(vs).material_index = m
    for i in range(n):
        A, B = secs[i], secs[i + 1]
        f((A[0], B[0], B[1], A[1]), mi[0])
        f((A[2], A[3], B[3], B[2]), mi[1])
        f((A[0], A[2], B[2], B[0]), mi[2])
        f((A[1], B[1], B[3], A[3]), mi[2])
    f((secs[0][0], secs[0][1], secs[0][3], secs[0][2]), mi[2])
    f((secs[-1][0], secs[-1][2], secs[-1][3], secs[-1][1]), mi[2])


def picanha_obj(root, P, name, pieces, R=0.045, t=0.036, fat=0.011, w=0.068, front=False):
    """Fatias de picanha dobradas em C no espeto (o espeto fura as duas pontas): crosta tostada, miolo rosado nos
    lados e a capa de gordura por fora. pieces = [(x, y, z, flip)] no plano XZ (espeto ao longo de X em z)."""
    bm = bmesh.new()
    for x, y, z, fl in pieces:
        c = (x, y, z + 0.12 * R * fl)
        arc_box_into(bm, c, R - t / 2, R + t / 2, w, -0.38, math.pi + 0.38, 12, (0, 0, 2), fl)
        arc_box_into(bm, c, R + t / 2 - 0.003, R + t / 2 + fat, w * 1.02, 0.2, math.pi - 0.2, 10, (1, 1, 1), fl)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm_to_obj(bm, name, root, [P['crust'], P['fat'], P['meat_in']], bev=0.005, angle=40, front=front)


def espeto(root, P, tag, x0, x1, pieces, R=0.045, w=0.065, parent=None, handle=True, front=False, kind='picanha'):
    """Espeto ao longo de X local (lamina de x0 a x1, cabo de madeira antes de x0) com a carne: kind 'picanha'
    (pieces = lista de x, ou (x, flip)), 'linguica' (gomos) ou 'coracao' (coracaozinhos)."""
    objs = [box(root, tag + '_lamina', (x1 - x0, 0.008, 0.016), ((x0 + x1) / 2, 0, 0), m=P['steel'], bev=0.003, front=front),
            cyl(root, tag + '_ponta', 0.011, 0.04, (x1 + 0.018, 0, 0), r2=0.0, rot=(0, math.pi / 2, 0), m=P['steel'], v=4, bev=0.0, front=front)]
    if handle:
        objs += [cyl(root, tag + '_cabo', 0.018, 0.14, (x0 - 0.07, 0, 0), rot=(0, math.pi / 2, 0), m=P['wood'], v=12, bev=0.006, front=front),
                 cyl(root, tag + '_guarda', 0.024, 0.012, (x0 - 0.002, 0, 0), rot=(0, math.pi / 2, 0), m=P['steel'], v=14, bev=0.003, front=front)]
    if pieces:
        if kind == 'picanha':
            pcs = [(p, 0, 0, 1) if not isinstance(p, tuple) else (p[0], 0, 0, p[1]) for p in pieces]
            objs.append(picanha_obj(root, P, tag + '_picanha', pcs, R=R, w=w, front=front))
        elif kind == 'linguica':
            bm = bmesh.new()
            for x in pieces:
                tube_into(bm, [(x - R * 0.95 + 1.9 * R * j / 8, 0, 0.006 * math.sin(math.pi * j / 8)) for j in range(9)], R * 0.55, segs=10,
                          rfun=lambda t, r=R: r * 0.55 * (0.35 + 0.65 * math.sqrt(max(0.0, math.sin(math.pi * t)))))
            objs.append(bm_to_obj(bm, tag + '_linguica', root, [P['sausage']], front=front))
        else:
            for k, x in enumerate(pieces):
                objs.append(sphere(root, f'{tag}_coracao{k}', R * 0.5, (x, 0, 0), scale=(1.0, 0.9, 1.15), m=P['heart'], seg=12, front=front))
    if parent:
        for o in objs:
            o.parent = parent
    return objs


def chama(root, P, tag, loc, h=0.09, r=0.026, ph0=0.0, parent=None, m=None, core=True, turns=2, lean=0.0):
    """Linguinha de fogo (gota com a ponta curva) que tremula; o miolo amarelo aparece na base, para a camera."""
    e = empty(root, tag, loc=loc, parent=parent, rot=(0, lean, 0))
    prof = [(0.0, 0.0, 0.0), (0.12 * h, r * 0.85, r * 0.85), (0.32 * h, r, r, 0.0), (0.58 * h, r * 0.72, r * 0.72, 0.006),
            (0.82 * h, r * 0.32, r * 0.32, 0.012), (h, 0.0, 0.0, 0.016)]
    kids(e, lathe(root, tag + '_fogo', prof, m or P['fire'], segs=10, lv=1))
    if core:
        kids(e, sphere(root, tag + '_miolo', r * 0.62, (0, -r * 0.45, 0.2 * h), scale=(1, 1, 1.3), m=P['fire_y'], seg=10))

    def fn(o, mb, ph, p0=ph0):
        a = TAU * (turns * ph + p0)
        k = 1 + 0.2 * math.sin(a)
        s = 1 - 0.08 * math.sin(a + 1.3)
        o.matrix_basis = mb @ Matrix.Rotation(0.12 * math.sin(TAU * ph + p0 * 3), 4, 'Y') @ Matrix.Diagonal((s, s, k, 1))
    register_anim(e, fn)
    return e


def fumaca(root, P, tag, loc, n=4, rise=0.34, r=0.055, drift=0.1):
    """Baforadas de fumaca subindo da chamine (cada uma cresce e some; o loop fecha)."""
    rr = random.Random(len(tag))
    for k in range(n):
        e = empty(root, f'{tag}{k}', loc=loc)
        for j, (dx, dz, s) in enumerate(((0, 0, 1.0), (-0.6, -0.25, 0.7), (0.65, -0.2, 0.75))):
            kids(e, sphere(root, f'{tag}{k}_bola{j}', r * s, (dx * r, rr.uniform(-0.2, 0.2) * r, dz * r), m=P['smoke'], seg=14))

        def fn(o, mb, ph, k=k):
            p = (ph + k / n) % 1.0
            s = max(0.001, math.sin(math.pi * min(1.0, p * 1.15)) ** 0.7) * (0.55 + 0.75 * p)
            o.matrix_basis = Matrix.Translation((drift * p + 0.012 * math.sin(TAU * 2 * p), 0.03 * p, rise * p)) @ mb @ Matrix.Diagonal((s, s, s, 1))
        register_anim(e, fn)


def fagulha(root, P, tag, loc, s=1.0, parent=None, blink=None):
    """Fagulha (estrela de 4 pontas cor de brasa) que pisca na fase blink."""
    piv = empty(root, tag + '_fagPivo', loc=loc, parent=parent, rot=(math.radians(-35), 0, 0))
    for k, (sx, sz) in enumerate(((1.0, 0.2), (0.2, 1.0))):
        kids(piv, sphere(root, f'{tag}_fag{k}', 0.04 * s, (0, 0, 0), scale=(sx, 0.06, sz), m=P['spark'], seg=10))
    if blink is not None:
        def fn(o, mb, ph, b=blink):
            k = max(0.0, math.cos(TAU * (ph - b))) ** 6
            sc = 0.05 + 0.95 * k
            o.matrix_basis = mb @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(piv, fn)
    return piv


# ---------------------------------------------------------------- churrasqueira
def coal_bed(root, P, tag, cx, cy, w, d, z, seed=1, flames=4, fl_h=0.09, front=False):
    """Cinza, carvao e brasa acesa num retangulo w x d (topo em z) e as linguinhas de fogo."""
    box(root, tag + '_cinza', (w, d, 0.03), (cx, cy, z + 0.015), m=P['soot'], bev=0.01, front=front)
    rr = random.Random(seed)
    n = max(8, int(w * d * 300))
    for k in range(n):
        x, y = cx + rr.uniform(-w / 2 + 0.02, w / 2 - 0.02), cy + rr.uniform(-d / 2 + 0.02, d / 2 - 0.02)
        hot = rr.random() < 0.5
        sphere(root, f'{tag}_carvao{k}', rr.uniform(0.016, 0.026), (x, y, z + 0.032 + rr.uniform(0, 0.012)), scale=(1.25, 1.0, 0.72),
               m=P['ember'] if hot else P['coal'], seg=8, rot=(0, 0, rr.uniform(0, TAU)), front=front)
    for k in range(flames):
        u = (k + 0.5) / flames - 0.5
        chama(root, P, f'{tag}_chama{k}', (cx + u * w * 0.85, cy - d * 0.15 + rr.uniform(-0.03, 0.03), z + 0.035),
              h=fl_h * rr.uniform(0.8, 1.15), r=fl_h * 0.3, ph0=rr.random(), lean=rr.uniform(-0.15, 0.15))


def lenha(root, P, tag, x, y, z, n=3, L=0.16, r=0.03, axis='Y', front=False):
    """Tocos de lenha empilhados (2 + 1), com a ponta clara para a camera."""
    pos = [(-r * 1.05, 0), (r * 1.05, 0), (0, r * 1.75)][:n]
    rot = (math.pi / 2, 0, 0) if axis == 'Y' else (0, math.pi / 2, 0)
    for k, (u, v) in enumerate(pos):
        p = (x + u, y, z + r + v) if axis == 'Y' else (x, y + u, z + r + v)
        cyl(root, f'{tag}{k}', r, L, p, rot=rot, m=P['bark'], v=12, bev=0.006, front=front)
        e = (p[0], p[1] - L / 2 - 0.002, p[2]) if axis == 'Y' else (p[0] - L / 2 - 0.002, p[1], p[2])
        cyl(root, f'{tag}{k}_ponta', r * 0.82, 0.006, e, rot=rot, m=P['log_end'], v=12, bev=0.002, front=front)


def churrasqueira(root, P, tag, cx, cy, W, D, z0, hb=0.28, hf=0.2, hh=0.26, hc=0.2, n_esp=2, lights=None, seed=1, star_r=0.08):
    """Churrasqueira de tijolinho: armario da lenha, bancada de concreto, fornalha com brasa, grelha, espetos de
    picanha girando, coifa vermelha com a estrela branca e chamine com fumaca. Devolve as alturas uteis."""
    yf = cy - D / 2
    zc = z0 + hb
    brick_block(root, P, tag + '_base', cx, cy, W, D, z0, hb, seed=seed)
    # boca da lenha com os tocos
    box(root, tag + '_bocaLenha', (W * 0.58, 0.03, hb * 0.56), (cx, yf - 0.006, z0 + hb * 0.44), m=P['soot'], bev=0.012)
    box(root, tag + '_bocaVerga', (W * 0.66, 0.035, 0.035), (cx, yf - 0.012, z0 + hb * 0.74), m=P['conc_l'], bev=0.008)
    lenha(root, P, tag + '_lenha', cx, yf + 0.06, z0 + hb * 0.16, n=3, L=0.13, r=min(0.034, hb * 0.11))
    # bancada
    box(root, tag + '_bancada', (W + 0.07, D + 0.06, 0.045), (cx, cy - 0.01, zc + 0.0225), m=P['conc_l'], bev=0.014)
    zf = zc + 0.045
    wt = 0.06
    brick_block(root, P, tag + '_fundo', cx, cy + D / 2 - wt / 2, W, wt, zf, hf, seed=seed + 1)
    for sx in (-1, 1):
        brick_block(root, P, f'{tag}_lado{sx}', cx + sx * (W / 2 - wt / 2), cy, wt, D, zf, hf, seed=seed + 2 + sx)
    iw, idp = W - 2 * wt, D - wt
    coal_bed(root, P, tag + '_brasa', cx, cy - wt / 2, iw - 0.01, idp - 0.02, zf, seed=seed, flames=3 + n_esp // 2, fl_h=0.11)
    # grelha baixa e os espetos de picanha atravessados de um lado a outro (o da frente bem a vista)
    zg = zf + 0.072
    for k in range(5):
        yy = cy - wt / 2 - idp / 2 + 0.03 + k * (idp - 0.06) / 4
        tube(root, f'{tag}_grelha{k}', [(cx - iw / 2, yy, zg), (cx + iw / 2, yy, zg)], 0.006, P['grill'], segs=6)
    tube(root, tag + '_grelhaAro', [(cx - iw / 2 + 0.01, yf + 0.03, zg), (cx + iw / 2 - 0.01, yf + 0.03, zg)], 0.009, P['grill'], segs=6)
    for k in range(n_esp):
        yy = yf + 0.075 + k * min(0.1, (idp - 0.12) / max(1, n_esp - 1))
        zz = zg + 0.045 + 0.006 * k
        e = empty(root, f'{tag}_espeto{k}', loc=(cx - 0.015, yy, zz))
        npc = max(2, int((iw - 0.08) / 0.105))
        xs = [(-(npc - 1) / 2 + j) * 0.1 + 0.03 for j in range(npc)]
        espeto(root, P, f'{tag}_espeto{k}', -W / 2 + 0.01, W / 2 - 0.03, xs, R=0.04, w=0.058, parent=e, handle=True)
    # coifa vermelha com a estrela branca e o friso
    zh0 = zf + hf
    box(root, tag + '_coifaBarra', (W + 0.05, D + 0.05, 0.055), (cx, cy, zh0 + 0.0275), m=P['coifa_d'], bev=0.014)
    box(root, tag + '_coifaFilete', (W + 0.056, 0.01, 0.014), (cx, cy - (D + 0.05) / 2 - 0.003, zh0 + 0.028), m=P['branco'], bev=0.004)
    zb = zh0 + 0.055
    tw, td = W * 0.4, D * 0.42
    toff = (0.0, (D - td) / 2 * 0.55)
    frustum(root, tag + '_coifa', (W + 0.02, D + 0.02), (tw, td), hh, (cx, cy, zb), P['coifa'], toff=toff, bev=0.014)
    yb, yt = cy - (D + 0.02) / 2, cy + toff[1] - td / 2
    th = math.atan2(yt - yb, hh)
    ts = 0.44
    estrela(root, tag + '_coifaEstrela', star_r, 0.012, loc=(cx, yb + (yt - yb) * ts - 0.004, zb + hh * ts), rot=(-th, 0, 0))
    zh1 = zb + hh
    # chamine de tijolinho com chapeu
    chx, chy = cx, cy + toff[1]
    cw, cd = tw * 0.82, td * 0.82
    brick_block(root, P, tag + '_chamine', chx, chy, cw, cd, zh1 - 0.02, hc + 0.02, seed=seed + 5)
    zt = zh1 + hc
    box(root, tag + '_chamineBorda', (cw + 0.035, cd + 0.035, 0.035), (chx, chy, zt + 0.0175), m=P['brick'][1], bev=0.01)
    box(root, tag + '_chamineBoca', (cw - 0.045, cd - 0.045, 0.01), (chx, chy, zt + 0.031), m=P['ember'], bev=0.003)
    for k, u in enumerate((-0.03, 0.03)):
        chama(root, P, f'{tag}_chamineFogo{k}', (chx + u, chy - 0.01, zt + 0.03), h=0.08, r=0.024, ph0=0.4 * k, lean=-0.2 + 0.4 * k)
    fumaca(root, P, tag + '_fumaca', (chx + 0.05, chy + 0.03, zt + 0.08), n=4, rise=0.28, r=0.05 + 0.05 * cw, drift=0.16)
    if lights is not None:
        lights.append(((cx, cy - D / 2, zg + 0.04), '#ff7a30', 9.0, 0))
    return {'zc': zc, 'zf': zf, 'zh1': zh1, 'zt': zt, 'chim': (chx, chy), 'yf': yf}


def bancada_lateral(root, P, tag, x0, x1, y0, y1, z0, zc, seed=4, board=True):
    """Bancada de tijolinho ao lado da churrasqueira (camada da frente: o churrasqueiro fica atras dela), tampo de
    concreto, tabua com a picanha inteira e a faca."""
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    brick_block(root, P, tag + '_bancadaLat', cx, cy, w, d, z0, zc - z0, front=True, seed=seed)
    box(root, tag + '_bancadaLatTampo', (w + 0.04, d + 0.05, 0.045), (cx + 0.01, cy - 0.005, zc + 0.0225), m=P['conc_l'], bev=0.014, front=True)
    zt = zc + 0.045
    if board:
        bx = cx - w * 0.12
        slab(root, tag + '_tabua', 0.26, d * 0.62, 0.025, P['board'], r=0.03, loc=(bx, cy - 0.01, zt + 0.0125), rot=(math.pi / 2, 0, 0.08), bev=0.008,
             front=True)
        z1 = zt + 0.025
        sphere(root, tag + '_picanhaInteira', 1.0, (bx - 0.02, cy - 0.01, z1 + 0.022), scale=(0.1, 0.055, 0.03), m=P['crust'], seg=18, front=True)
        sphere(root, tag + '_picanhaCapa', 1.0, (bx - 0.02, cy + 0.008, z1 + 0.036), scale=(0.104, 0.05, 0.022), m=P['fat'], seg=18, front=True)
        for k in range(3):
            sphere(root, f'{tag}_fatiaCorte{k}', 1.0, (bx + 0.075 + 0.02 * k, cy - 0.012, z1 + 0.018), scale=(0.008, 0.042, 0.02), rot=(0, 0.35, 0),
                   m=P['meat_in'], seg=10, front=True)
        box(root, tag + '_facaLamina', (0.13, 0.026, 0.006), (bx + 0.05, cy - d * 0.25, z1 + 0.006), rot=(0, 0, -0.3), m=P['steel'], bev=0.002, front=True)
        box(root, tag + '_facaCabo', (0.06, 0.02, 0.014), (bx - 0.04, cy - d * 0.25 + 0.03, z1 + 0.008), rot=(0, 0, -0.3), m=P['knife_h'], bev=0.004, front=True)
        # tigelinha de sal grosso
        cyl(root, tag + '_sal', 0.035, 0.03, (x1 - 0.06, cy + 0.01, zt + 0.015), r2=0.045, m=P['styro'], v=16, bev=0.006, front=True)
        for k in range(5):
            a = TAU * k / 5
            box(root, f'{tag}_salGrao{k}', (0.012, 0.012, 0.01), (x1 - 0.06 + 0.02 * math.cos(a), cy + 0.01 + 0.02 * math.sin(a), zt + 0.032), rot=(0.3, 0.4, a),
                m=P['ice'], bev=0.002, front=True)


def deck(root, P, tag, cx, cy, W, D, z0, step=False):
    """Deck de concreto branco (o terraco do churrasco) com a faixa vermelha e o filete branco da chapa."""
    if step:
        slab(root, tag + '_degrau', W + 0.12, D + 0.12, 0.08, P['concrete'], r=0.08, loc=(cx, cy, 0.11), rot=(math.pi / 2, 0, 0), bev=0.02)
    zb = 0.15 if step else 0.07
    h = z0 - zb
    slab(root, tag + '_deck', W, D, h, P['concrete'], r=0.06, loc=(cx, cy, zb + h / 2), rot=(math.pi / 2, 0, 0), bev=0.018)
    slab(root, tag + '_deckFaixa', W + 0.01, D + 0.01, 0.035, cor('pri'), r=0.064, loc=(cx, cy, z0 - 0.04), rot=(math.pi / 2, 0, 0), bev=0.006)
    slab(root, tag + '_deckFilete', W + 0.012, D + 0.012, 0.01, P['branco'], r=0.065, loc=(cx, cy, z0 - 0.067), rot=(math.pi / 2, 0, 0), bev=0.003)


# ---------------------------------------------------------------- adereços: isopor, carvao, caneco, picanha do alto
def isopor(root, P, tag, loc, rz=0.0, s=1.0, front=False):
    """Caixa de isopor aberta com latinhas (sem rotulo) e gelo."""
    e = empty(root, tag, loc=loc, rot=(0, 0, rz))
    w, d, h = 0.26 * s, 0.18 * s, 0.13 * s
    objs = [box(root, tag + '_caixa', (w, d, h), (0, 0, h / 2), m=P['styro'], bev=0.02 * s, front=front),
            box(root, tag + '_borda', (w + 0.012, d + 0.012, 0.02 * s), (0, 0, h - 0.008), m=P['styro'], bev=0.006, front=front),
            box(root, tag + '_tampa', (w + 0.01, 0.03 * s, d * 0.9), (0, d / 2 + 0.01, h + d * 0.4), rot=(-0.25, 0, 0), m=P['styro'], bev=0.012 * s, front=front)]
    for k, (u, v, t) in enumerate(((-0.07, -0.02, 0.1), (0.0, 0.03, -0.15), (0.07, -0.025, 0.2))):
        objs.append(cyl(root, f'{tag}_lata{k}', 0.028 * s, 0.085 * s, (u * s, v * s, h + 0.012 * s), rot=(t, 0.1 * k, 0), m=P['can'], v=16, bev=0.004, front=front))
        objs.append(cyl(root, f'{tag}_lataTopo{k}', 0.024 * s, 0.006, (u * s - 0.0, v * s, h + 0.012 * s + 0.044 * s), rot=(t, 0.1 * k, 0), m=P['can_top'], v=14,
                        bev=0.002, front=front))
    for k, (u, v) in enumerate(((-0.1, 0.05), (0.04, -0.05), (0.1, 0.04), (-0.03, 0.06))):
        objs.append(box(root, f'{tag}_gelo{k}', (0.03 * s, 0.03 * s, 0.026 * s), (u * s, v * s, h - 0.002), rot=(0.3 * k, 0.2, 0.5 * k), m=P['ice'], bev=0.006,
                        front=front))
    kids(e, *objs)
    return e


def saco_carvao(root, P, tag, loc, rz=0.0, s=1.0, front=False):
    """Saco de carvao de papel aberto, com os pedacos aparecendo e uma faixa escura (sem marca)."""
    e = empty(root, tag, loc=loc, rot=(0, 0, rz))
    objs = [box(root, tag + '_saco', (0.16 * s, 0.1 * s, 0.2 * s), (0, 0, 0.1 * s), m=P['kraft'], bev=0.025 * s, front=front),
            box(root, tag + '_dobra', (0.165 * s, 0.105 * s, 0.03 * s), (0, 0, 0.19 * s), rot=(0.08, 0, 0), m=P['kraft'], bev=0.01, front=front),
            box(root, tag + '_faixa', (0.162 * s, 0.102 * s, 0.045 * s), (0, 0, 0.09 * s), m=P['soot'], bev=0.006, front=front)]
    rr = random.Random(len(tag))
    for k in range(6):
        objs.append(sphere(root, f'{tag}_pedra{k}', 0.024 * s, (rr.uniform(-0.05, 0.05) * s, rr.uniform(-0.03, 0.03) * s, 0.205 * s + rr.uniform(0, 0.02) * s),
                           scale=(1.2, 1.0, 0.8), m=P['coal'], seg=8, front=front))
    kids(e, *objs)
    return e


def caneco(root, P, tag, s=1.0, parent=None):
    """Caneco de chope gelado: chope dourado, colarinho de espuma escorrendo e a alca de vidro (plano XZ)."""
    piv = empty(root, tag + '_canecoPivo', parent=parent)
    kids(piv, cyl(root, tag + '_chope', 0.05 * s, 0.11 * s, (0, 0, 0), m=P['beer'], v=20, bev=0.01 * s),
         cyl(root, tag + '_fundo', 0.054 * s, 0.022 * s, (0, 0, -0.062 * s), m=P['glass_l'], v=20, bev=0.007 * s),
         torus(root, tag + '_asa', (0.064 * s, 0, 0.002 * s), 0.032 * s, 0.01 * s, P['glass_l'], axis='Y', n=14, segs=6),
         sphere(root, tag + '_espuma', 0.056 * s, (0, 0, 0.058 * s), scale=(1, 1, 0.55), m=P['foam_b'], seg=16),
         sphere(root, tag + '_espuma2', 0.032 * s, (-0.014 * s, 0.006 * s, 0.084 * s), m=P['foam_b'], seg=12),
         sphere(root, tag + '_escorrido', 0.016 * s, (-0.044 * s, -0.028 * s, 0.03 * s), scale=(0.8, 0.8, 1.7), m=P['foam_b'], seg=10))
    for k in range(3):
        a = math.radians(-120 + 30 * k)
        kids(piv, box(root, f'{tag}_gomo{k}', (0.008 * s, 0.006 * s, 0.09 * s), (0.052 * s * math.cos(a), 0.052 * s * math.sin(a), -0.002), rot=(0, 0, a),
                      m=P['glass_l'], bev=0.002))
    return piv


def orbit(piv, rx, ry, z, tilt=0.1, turns=1, phase=0.0, bob_=0.05):
    """Faz o objeto (filho da raiz, em z) dar a volta na torre numa elipse, sempre de frente para a camera."""
    def fn(o, mb, ph):
        a = TAU * (turns * ph + phase)
        pos = Vector((rx * math.cos(a), ry * math.sin(a), z + bob_ * math.sin(2 * a)))
        o.matrix_basis = mb @ Matrix.Translation(pos) @ Matrix.Rotation(tilt * math.cos(a), 4, 'Y') @ Matrix.Rotation(0.25 * math.sin(a), 4, 'Z')
    register_anim(piv, fn)


def picanha_alto(root, P, tag, loc, lights, s=1.0, watts=24.0, col='#ffb36b', embers=True):
    """A picanha do alto (o antigo orbe): espeto sem cabo com tres fatias grandes flutuando sobre linguinhas de fogo,
    balancando, com fagulhas girando em volta. E dela que sai o disparo."""
    piv = empty(root, tag + '_picanhaPivo', loc=loc)
    sw = empty(root, tag + '_picanhaBalanco', parent=piv, rot=(math.radians(-38), 0, 0))   # o C da fatia de frente para a camera
    espeto(root, P, tag + '_picanhaAlto', -0.17 * s, 0.15 * s, [-0.085 * s, 0.0, 0.085 * s], R=0.054 * s, w=0.078 * s, parent=sw, handle=False)
    register_anim(sw, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.28 * math.sin(TAU * ph), 4, 'Z')
                                                     @ Matrix.Rotation(0.12 * math.sin(TAU * ph + 1.0), 4, 'X')))
    register_anim(piv, bob(amp=0.022, turns=1, axis='Z'))
    if embers:
        for ring_i in range(2):
            ep = empty(root, f'{tag}_fagulhaPivo{ring_i}', loc=loc)
            for k in range(3):
                a = TAU * k / 3 + ring_i
                kids(ep, sphere(root, f'{tag}_brasinha{ring_i}{k}', 0.016 * s, (0.26 * s * math.cos(a), 0.22 * s * math.sin(a), 0.07 * s * math.sin(2 * a + ring_i)),
                                m=P['spark'], seg=8))
            register_anim(ep, spin('Z', sym=3, turns=1 if ring_i == 0 else -1))
    fagulha(root, P, tag + '_fag0', (loc[0] - 0.13 * s, loc[1] - 0.08, loc[2] + 0.1 * s), s=0.7 * s, blink=0.1)
    fagulha(root, P, tag + '_fag1', (loc[0] + 0.15 * s, loc[1] - 0.08, loc[2] + 0.04 * s), s=0.55 * s, blink=0.6)
    lights.append((loc, col, watts, 1))
    return piv


def pedestal_drum(root, P, tag, r, z1, band=True):
    """Pedestal de concreto branco: base, tambor e tampo com quinas suaves e a faixa vermelha da chapa."""
    cyl(root, tag + '_pedestalBase', r * 1.08, 0.06, (0, 0, 0.1), m=P['concrete'], v=44, bev=0.02)
    cyl(root, tag + '_pedestal', r * 0.9, z1 - 0.18, (0, 0, (z1 + 0.13 - 0.05) / 2), m=P['concrete'], v=44, bev=0.015)
    cyl(root, tag + '_pedestalTampo', r, 0.06, (0, 0, z1 - 0.03), m=P['concrete'], v=44, bev=0.02)
    if band:
        torus(root, tag + '_pedestalFaixa', (0, 0, z1 - 0.1), r * 0.9 + 0.004, 0.016, cor('pri'), n=44, segs=6)


def alvorada_column(root, P, tag, x, y, zb, zt, w, t=0.05, axis='X'):
    """Coluna da Alvorada vista de frente: lamina branca larga no alto que afina em curva ate uma ponta no chao."""
    bm = bmesh.new()
    n = 16
    right = [(w / 2 * (1 - math.sqrt(max(0.0, 1 - (k / n) ** 2))), zb + (zt - zb) * k / n) for k in range(n + 1)]
    outline = [(0.0, zb)] + right[1:] + [(-u, z) for u, z in reversed(right[1:])]
    vs = []
    for side in (-1, 1):
        if axis == 'X':
            vs.append([bm.verts.new((x + u, y + side * t / 2, z)) for u, z in outline])
        else:
            vs.append([bm.verts.new((x + side * t / 2, y + u, z)) for u, z in outline])
    A, B = vs
    m_ = len(outline)
    caps = [bm.faces.new(A), bm.faces.new(list(reversed(B)))]
    for i in range(m_):
        j = (i + 1) % m_
        bm.faces.new((A[j], A[i], B[i], B[j]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=caps)
    return bm_to_obj(bm, tag, root, [P['concrete']], bev=0.01, angle=35)


def pedestal_alvorada(root, P, tag, Wp, Dp, z1, ncol=4):
    """O Palacio da Alvorada em miniatura sob o churrasco: piso, vidro fume recuado, colunata e a laje de cima
    (onde fica o terraco) com a faixa vermelha da chapa."""
    glass = mat('vidro_fume', '#a7b8c6', rough=0.1, metal=0.15, var=0.0, bump=0.0)
    box(root, tag + '_piso', (Wp + 0.18, Dp + 0.18, 0.06), (0, 0, 0.1), m=P['concrete'], bev=0.025)
    box(root, tag + '_vidro', (Wp - 0.14, Dp - 0.14, z1 - 0.2), (0, 0, (z1 + 0.06) / 2), m=glass, bev=0.01)
    for k in range(3):
        box(root, f'{tag}_caixilho{k}', (0.018, 0.02, z1 - 0.2), ((k - 1) * (Wp - 0.14) / 3, -(Dp - 0.14) / 2 - 0.004, (z1 + 0.06) / 2), m=P['concrete'], bev=0.004)
    zb, zt = 0.13, z1 - 0.07
    cw = Wp / ncol
    for k in range(ncol + 1):
        alvorada_column(root, P, f'{tag}_colunaF{k}', -Wp / 2 + cw * k, -Dp / 2 - 0.02, zb, zt, cw * 0.98)
    for sx in (-1, 1):
        for k in range(1, 3):
            alvorada_column(root, P, f'{tag}_colunaL{sx}{k}', sx * (Wp / 2 + 0.02), -Dp / 2 + Dp * k / 3, zb, zt, Dp / 3 * 0.98, axis='Y')
    box(root, tag + '_laje', (Wp + 0.14, Dp + 0.14, 0.07), (0, 0, z1 - 0.035), m=P['concrete'], bev=0.02)
    box(root, tag + '_lajeFaixa', (Wp + 0.15, Dp + 0.15, 0.026), (0, 0, z1 - 0.04), m=cor('pri'), bev=0.006)


def bandeira_chapa(root, name, loc, **kw):
    """chapa.bandeirinha com o emblema nos dois lados do pano (la ele nasce filho da raiz)."""
    mast = bandeirinha(root, name, loc, **kw)
    cloth = next(c for c in mast.children if c.name.startswith(name + '_pano'))
    for s, sgn in (('a', -1), ('b', 1)):
        for o in list(root.children):
            if o.name.startswith(f'{name}_em{s}_'):
                o.parent = cloth
                o.location = (0, sgn * 0.005, 0)
    return mast


# ---------------------------------------------------------------- niveis 1 a 3
def nivel(P, root, tag, z0, cx, W, D, hb, hf, hh, hc, n_esp, deck_wd, wing, slot, step=False, star_r=0.08, top_dz=0.2, top_s=1.1, alvorada=None):
    plot(root, P, tag)
    lights = []
    if alvorada:
        pedestal_alvorada(root, P, tag, alvorada[0], alvorada[1], z0)
    else:
        deck(root, P, tag, 0.02, 0.02, deck_wd[0], deck_wd[1], z0, step=step)
    cy = 0.1
    C = churrasqueira(root, P, tag + '_churras', cx, cy, W, D, z0, hb=hb, hf=hf, hh=hh, hc=hc, n_esp=n_esp, lights=lights, seed=len(tag) * 3, star_r=star_r)
    yf = cy - D / 2
    bancada_lateral(root, P, tag, cx + W / 2, wing, yf, yf + 0.19, z0, C['zc'])
    top = (cx, cy + 0.02, C['zt'] + top_dz)
    picanha_alto(root, P, tag, top, lights, s=top_s, col='#ffb36b')
    C['top'] = top
    return C, lights, top


def build_mg1(P, root):
    C, lights, top = nivel(P, root, 'mg1', 0.24, -0.22, 0.5, 0.4, 0.24, 0.26, 0.26, 0.2, 2, (1.12, 0.76), 0.5, None)
    isopor(root, P, 'mg1_isopor', (0.5, -0.5, G), rz=0.25)
    saco_carvao(root, P, 'mg1_carvao', (-0.54, -0.44, G), rz=-0.35)
    return {'slots': [(0.28, 0.22, 0.24)], 'lights': lights, 'points': {'top': top}}


def build_mg2(P, root):
    z0 = 0.34
    C, lights, top = nivel(P, root, 'mg2', z0, -0.24, 0.56, 0.42, 0.26, 0.27, 0.28, 0.22, 3, (1.2, 0.8), 0.54, None, step=True, star_r=0.088, top_s=1.18)
    ck = caneco(root, P, 'mg2_orbita', s=1.15)
    orbit(ck, 0.84, 0.56, C['zc'] + 0.2)
    isopor(root, P, 'mg2_isopor', (0.54, -0.5, G), rz=0.25)
    saco_carvao(root, P, 'mg2_carvao', (-0.56, -0.46, G), rz=-0.35)
    lenha(root, P, 'mg2_lenhaChao', -0.3, -0.56, G, n=3, L=0.14, r=0.032, axis='Y')
    return {'slots': [(0.3, 0.23, z0)], 'lights': lights, 'points': {'top': top}}


def build_mg3(P, root):
    z0 = 0.52
    C, lights, top = nivel(P, root, 'mg3', z0, -0.26, 0.6, 0.44, 0.26, 0.28, 0.3, 0.26, 3, None, 0.56, None, star_r=0.096, top_s=1.25,
                           alvorada=(1.06, 0.7))
    ck = caneco(root, P, 'mg3_orbita', s=1.2)
    orbit(ck, 0.9, 0.62, C['zc'] + 0.2)
    ep = empty(root, 'mg3_orbitaEspeto')
    sp = empty(root, 'mg3_orbitaEspetoGiro', parent=ep, rot=(0, -0.5, 0))
    espeto(root, P, 'mg3_orbitaEspeto', -0.1, 0.12, [-0.04, 0.05], R=0.04, w=0.055, parent=sp, handle=True)
    orbit(ep, 0.9, 0.62, C['zc'] + 0.24, phase=0.5)
    isopor(root, P, 'mg3_isopor', (0.5, -0.5, 0.13), rz=0.25)
    saco_carvao(root, P, 'mg3_carvao', (-0.5, -0.5, 0.13), rz=-0.35)
    saco_carvao(root, P, 'mg3_carvao2', (-0.66, -0.36, 0.13), rz=0.3, s=0.85)
    bandeira_chapa(root, 'mg3_bandeira', (0.5, 0.36, z0), h=0.4, w=0.2, fh=0.13)
    lights.append(((0.0, -0.3, z0 + 0.2), '#ffb070', 6.0, 0))
    return {'slots': [(0.3, 0.2, z0)], 'lights': lights, 'points': {'top': top}}


# ---------------------------------------------------------------- Rodizio: carrossel de espetos sobre o braseiro
def linguica_helice(root, P, tag, pts_fn, n, link=0.1, r=0.026):
    """Linguica em gomos ao longo de uma curva (pts_fn(t) -> ponto, t em 0..1), numa malha so, com os nozinhos."""
    pts = [Vector(pts_fn(k / 400)) for k in range(401)]
    acc = [0.0]
    for i in range(400):
        acc.append(acc[-1] + (pts[i + 1] - pts[i]).length)
    total = acc[-1]
    m = max(2, int(total / link))

    def at(d):
        i = min(399, max(0, next((j for j in range(400) if acc[j + 1] >= d), 399)))
        t = (d - acc[i]) / max(1e-6, acc[i + 1] - acc[i])
        return pts[i].lerp(pts[i + 1], t)
    bm = bmesh.new()
    knots = []
    for k in range(m):
        d0, d1 = total * k / m, total * (k + 1) / m
        seg = [at(d0 + (d1 - d0) * j / 6) for j in range(7)]
        tube_into(bm, seg, r, segs=10, rfun=lambda t: r * (0.3 + 0.7 * math.sqrt(max(0.0, math.sin(math.pi * t)))))
        knots.append(at(d1))
    o = bm_to_obj(bm, tag, root, [P['sausage']])
    for k, p in enumerate(knots[:-1]):
        sphere(root, f'{tag}_no{k}', r * 0.35, p, m=P['heart'], seg=8)
    return o


def build_mgL(P, root):
    plot(root, P, 'mgL')
    lights = []
    z0 = 0.56
    cyl(root, 'mgL_degrau', 0.6, 0.08, (0, 0, 0.11), m=P['concrete'], v=44, bev=0.025)
    pedestal_drum(root, P, 'mgL', 0.42, z0)
    # braseiro redondo de tijolinho com a brasa
    rr = random.Random(5)
    for row in range(2):
        nb = 16
        for k in range(nb):
            a = TAU * (k + 0.5 * row) / nb
            box(root, f'mgL_braseiro{row}_{k}', (0.12, 0.07, 0.05), (0.31 * math.cos(a), 0.31 * math.sin(a), z0 + 0.027 + row * 0.054), rot=(0, 0, a + math.pi / 2),
                m=P['brick'][rr.choice((0, 0, 1, 2))], bev=0.008)
    cyl(root, 'mgL_braseiroFundo', 0.3, 0.05, (0, 0, z0 + 0.03), m=P['soot'], v=32, bev=0.01)
    for k in range(34):
        a, d = rr.uniform(0, TAU), 0.26 * math.sqrt(rr.random())
        sphere(root, f'mgL_carvao{k}', rr.uniform(0.018, 0.028), (d * math.cos(a), d * math.sin(a), z0 + 0.075 + rr.uniform(0, 0.02)), scale=(1.25, 1.0, 0.72),
               m=P['ember'] if rr.random() < 0.55 else P['coal'], seg=8, rot=(0, 0, rr.uniform(0, TAU)))
    for k in range(5):
        a = TAU * k / 5 + 0.3
        chama(root, P, f'mgL_chama{k}', (0.17 * math.cos(a), 0.14 * math.sin(a), z0 + 0.09), h=0.11, r=0.032, ph0=0.27 * k, lean=0.1 * math.cos(a))
    # mastro e o carrossel girando (seis espetos pendurados: picanha e linguica alternando)
    zt = z0 + 0.84
    tube(root, 'mgL_mastro', [(0, 0, z0 + 0.05), (0, 0, zt)], 0.022, P['grill'], segs=12)
    cyl(root, 'mgL_mastroPe', 0.06, 0.04, (0, 0, z0 + 0.07), r2=0.04, m=P['grill'], v=16, bev=0.006)
    cr = empty(root, 'mgL_carrossel', loc=(0, 0, zt - 0.05))
    kids(cr, torus(root, 'mgL_coroa', (0, 0, 0), 0.26, 0.02, P['coifa'], n=40, segs=8),
         cyl(root, 'mgL_cubo', 0.07, 0.07, (0, 0, 0.0), m=P['coifa'], v=20, bev=0.012),
         torus(root, 'mgL_cuboFilete', (0, 0, 0.0), 0.071, 0.008, P['branco'], n=20, segs=5))
    for k in range(6):
        a = TAU * k / 6 + math.pi / 6
        kids(cr, tube(root, f'mgL_raio{k}', [(0.06 * math.cos(a), 0.06 * math.sin(a), 0), (0.26 * math.cos(a), 0.26 * math.sin(a), 0)], 0.01, P['grill'], segs=6),
             sphere(root, f'mgL_gancho{k}', 0.018, (0.26 * math.cos(a), 0.26 * math.sin(a), -0.01), m=P['steel'], seg=10))
        he = empty(root, f'mgL_espetoPend{k}', loc=(0.26 * math.cos(a), 0.26 * math.sin(a), -0.03), parent=cr, rot=(0, math.pi / 2, a + math.pi / 2))
        if k % 2 == 0:
            espeto(root, P, f'mgL_espPend{k}', 0.06, 0.38, [0.13, 0.22, 0.31], R=0.042, w=0.062, parent=he, handle=False)
        else:
            espeto(root, P, f'mgL_espPend{k}', 0.06, 0.38, [0.12, 0.22, 0.32], R=0.05, parent=he, handle=False, kind='linguica')
        kids(he, torus(root, f'mgL_argola{k}', (0.03, 0, 0), 0.02, 0.006, P['steel'], axis='Z', n=12, segs=4))
    register_anim(cr, spin('Z', sym=3, turns=1))
    # no alto: a picanha flamejante e os espetinhos voando em volta (os espetos que saltam entre os inimigos)
    top = (0.0, 0.02, zt + 0.2)
    cyl(root, 'mgL_topoHaste', 0.012, 0.1, (0, 0, zt + 0.06), m=P['steel'], v=10, bev=0.003)
    chama(root, P, 'mgL_topoFogo', (0, -0.01, zt + 0.1), h=0.07, r=0.022, ph0=0.2)
    picanha_alto(root, P, 'mgL', top, lights, s=1.15, watts=18.0, col='#ffb36b', embers=False)
    for k in range(3):
        ep = empty(root, f'mgL_espetinhoVoa{k}')
        sp = empty(root, f'mgL_espetinhoGiro{k}', parent=ep, rot=(0.0, -0.35, 0.0))
        espeto(root, P, f'mgL_espetinho{k}', -0.09, 0.09, [-0.03, 0.04], R=0.034, w=0.05, parent=sp, handle=False,
               kind='picanha' if k != 1 else 'coracao')
        orbit(ep, 0.36, 0.26, top[2] - 0.06, tilt=0.35, turns=1, phase=k / 3, bob_=0.06)
    # faiscas de brasa que pulam entre o carrossel e a picanha (o raio que salta)
    for k in range(4):
        a0 = TAU * k / 4 + 0.4
        pts = []
        for j in range(7):
            t = j / 6
            a = a0 + 0.7 * t
            rr_ = 0.24 + 0.05 * math.sin(j * 2.3 + k)
            pts.append((rr_ * math.cos(a), top[1] + 0.12 * math.sin(a), top[2] - 0.08 - 0.3 * t + 0.03 * math.sin(j * 3.1)))
        arc = tube(root, f'mgL_arco{k}', pts, 0.008, P['spark'], segs=5)

        def blink(o, mb, ph, k=k):
            on = (int(ph * 16) + k * 5) % 7 < 2
            o.matrix_basis = mb @ Matrix.Diagonal((1, 1, 1, 1) if on else (0.001, 0.001, 0.001, 1))
        register_anim(arc, blink)
    # linguica enrolada no pedestal
    linguica_helice(root, P, 'mgL_linguicaEnrolada',
                    lambda t: ((0.47 - 0.05 * t) * math.cos(-math.pi / 2 - 1.0 + TAU * 1.3 * t), (0.47 - 0.05 * t) * math.sin(-math.pi / 2 - 1.0 + TAU * 1.3 * t),
                               0.19 + 0.21 * t), 0, link=0.1, r=0.028)
    saco_carvao(root, P, 'mgL_carvao', (-0.56, -0.42, G), rz=-0.35)
    isopor(root, P, 'mgL_isopor', (0.6, -0.3, G), rz=0.5, s=0.9)
    lights.append(((0, -0.1, z0 + 0.15), '#ff7a30', 10.0, 0))
    return {'slots': [(0.3, -0.62, G)], 'lights': lights, 'points': {'top': top}, 'margin': (0.2, 0.95, 0.2, 0.3)}


# ---------------------------------------------------------------- Macarico do Churrasqueiro: macarico culinario gigante
def build_mgS(P, root):
    plot(root, P, 'mgS')
    lights = []
    z0 = 0.42
    cyl(root, 'mgS_degrau', 0.62, 0.08, (0, 0, 0.11), m=P['concrete'], v=44, bev=0.025)
    pedestal_drum(root, P, 'mgS', 0.46, z0)
    brick_block(root, P, 'mgS_base', 0.0, 0.06, 0.56, 0.44, z0, 0.12, seed=9)
    box(root, 'mgS_baseTampo', (0.6, 0.48, 0.03), (0.0, 0.06, z0 + 0.135), m=P['conc_l'], bev=0.01)
    # cartucho de gas vermelho com a estrela e a faixa branca
    cx, cy, r = 0.04, 0.1, 0.17
    zb = z0 + 0.15
    hcan = 0.56
    cyl(root, 'mgS_cartuchoPe', r * 0.97, 0.04, (cx, cy, zb + 0.02), m=P['coifa_d'], v=40, bev=0.012)
    cyl(root, 'mgS_cartucho', r, hcan, (cx, cy, zb + 0.04 + hcan / 2), m=P['coifa'], v=48, bev=0.02)
    torus(root, 'mgS_cartuchoFaixa', (cx, cy, zb + 0.1), r + 0.002, 0.014, P['branco'], n=48, segs=6)
    estrela(root, 'mgS_cartuchoEstrela', 0.1, 0.014, loc=(cx, cy - r - 0.002, zb + 0.34))
    zd = zb + 0.04 + hcan
    sphere(root, 'mgS_cartuchoDomo', r, (cx, cy, zd - 0.01), scale=(1, 1, 0.42), m=P['coifa'], seg=32)
    cyl(root, 'mgS_pescoco', 0.05, 0.08, (cx, cy, zd + 0.08), m=P['steel'], v=20, bev=0.008)
    # cabeca do macarico, gatilho e regulador laranja
    hz = zd + 0.16
    box(root, 'mgS_cabeca', (0.2, 0.14, 0.13), (cx, cy, hz), m=P['torch_k'], bev=0.035)
    box(root, 'mgS_gatilho', (0.05, 0.05, 0.09), (cx + 0.06, cy - 0.08, hz - 0.08), rot=(0.3, 0, 0), m=P['torch_o'], bev=0.015)
    cyl(root, 'mgS_regulador', 0.045, 0.05, (cx + 0.12, cy, hz + 0.01), rot=(0, math.pi / 2, 0), m=P['torch_o'], v=16, bev=0.008)
    for k in range(6):
        a = TAU * k / 6
        box(root, f'mgS_reguladorDente{k}', (0.05, 0.012, 0.012), (cx + 0.12, cy + 0.046 * math.cos(a), hz + 0.01 + 0.046 * math.sin(a)), rot=(a, 0, 0),
            m=P['torch_o'], bev=0.003)
    # bico de aco apontando para a frente e a esquerda (o jato sai da ponta: o ponto 'top')
    d = Vector((-0.78, -0.58, -0.12)).normalized()
    p0 = Vector((cx - 0.07, cy - 0.03, hz + 0.01))
    p1 = p0 + d * 0.3
    tube(root, 'mgS_bico', [tuple(p0), tuple(p0 + d * 0.15), tuple(p1)], 0.026, P['steel'], segs=12)
    q = d.to_track_quat('Z', 'Y').to_euler()
    cyl(root, 'mgS_bicoBoca', 0.03, 0.06, tuple(p1 + d * 0.02), r2=0.042, rot=q, m=P['steel'], v=16, bev=0.006)
    torus(root, 'mgS_bicoAnel', (0, 0, 0), 0.03, 0.008, P['grill'], n=16, segs=5).matrix_basis = Matrix.Translation(p0 + d * 0.12) @ q.to_matrix().to_4x4()
    tip = p1 + d * 0.05
    top = tuple(tip)
    # o jato: chama azul com miolo claro e a ponta laranja, tremulando
    fl = empty(root, 'mgS_jato', loc=top, rot=q)
    kids(fl, lathe(root, 'mgS_jatoFora', [(0.0, 0.03, 0.03), (0.06, 0.05, 0.05), (0.16, 0.045, 0.045), (0.26, 0.026, 0.026), (0.32, 0.0, 0.0)], P['blue'], segs=14, lv=1),
         lathe(root, 'mgS_jatoMiolo', [(0.0, 0.018, 0.018), (0.05, 0.03, 0.03), (0.12, 0.022, 0.022), (0.18, 0.0, 0.0)], P['blue_w'], segs=12, lv=1))
    for k, (zz, rr_) in enumerate(((0.3, 0.03), (0.36, 0.022))):
        kids(fl, sphere(root, f'mgS_jatoPonta{k}', rr_, (0, 0, zz), scale=(1, 1, 1.6), m=P['fire'], seg=12))

    def flick(o, mb, ph):
        a = TAU * 3 * ph
        k = 1 + 0.1 * math.sin(a) + 0.05 * math.sin(2 * a + 1)
        s = 1 - 0.06 * math.sin(a + 0.8)
        o.matrix_basis = mb @ Matrix.Diagonal((s, s, k, 1))
    register_anim(fl, flick)
    lights.append((top, '#ffd59a', 22.0, 1))
    fagulha(root, P, 'mgS_fag0', (tip.x - 0.16, tip.y - 0.12, tip.z + 0.12), s=0.9, blink=0.0)
    fagulha(root, P, 'mgS_fag1', (tip.x - 0.3, tip.y - 0.1, tip.z - 0.06), s=0.6, blink=0.5)
    # churrasqueira de chao com a picanha, isopor e a bandeirinha
    gx, gy = -0.56, -0.34
    for sx in (-1, 1):
        for sy in (-1, 1):
            tube(root, f'mgS_grelhaPe{sx}{sy}', [(gx + sx * 0.08, gy + sy * 0.05, G), (gx + sx * 0.1, gy + sy * 0.065, G + 0.13)], 0.008, P['grill'], segs=5)
    box(root, 'mgS_grelhaCaixa', (0.24, 0.16, 0.06), (gx, gy, G + 0.15), m=P['grill'], bev=0.012)
    cyl(root, 'mgS_grelhaBrasa', 0.07, 0.01, (gx, gy, G + 0.182), m=P['ember'], v=16, bev=0.004)
    for k in range(4):
        tube(root, f'mgS_grelhaBarra{k}', [(gx - 0.11, gy - 0.06 + 0.04 * k, G + 0.19), (gx + 0.11, gy - 0.06 + 0.04 * k, G + 0.19)], 0.005, P['steel'], segs=5)
    sphere(root, 'mgS_grelhaPicanha', 1.0, (gx, gy, G + 0.215), scale=(0.08, 0.05, 0.022), m=P['crust'], seg=16)
    sphere(root, 'mgS_grelhaPicanhaCapa', 1.0, (gx, gy + 0.012, G + 0.226), scale=(0.082, 0.042, 0.016), m=P['fat'], seg=16)
    isopor(root, P, 'mgS_isopor', (-0.5, 0.42, G), rz=-0.2, s=0.9)
    bandeira_chapa(root, 'mgS_bandeira', (0.5, 0.3, G), h=0.42, w=0.22, fh=0.14)
    return {'slots': [(0.38, -0.52, G)], 'lights': lights, 'points': {'top': top}}


# ---------------------------------------------------------------- turma do churrasco (tripulacao)
def cap_bill(root, pr, tag, m):
    """Aba do bone (no pivo da cabeca, para a frente)."""
    o = cyl(root, tag + '_aba', 0.06, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.18, 0)
    return o


def avental(root, P, pr, tag, m, long_=False):
    """Avental do churrasqueiro por cima da camiseta: peitilho com a estrela branca, alca no pescoco e a saia do
    avental ate o joelho (ou mais comprida)."""
    z0 = 0.06 if long_ else 0.11
    prof = [(z0, 0.134, 0.142), (0.15, 0.122, 0.13), (0.21, 0.108, 0.118), (0.27, 0.094, 0.106), (0.31, 0.088, 0.101), (0.34, 0.088, 0.102),
            (0.39, 0.092, 0.111), (0.43, 0.091, 0.115), (0.45, 0.082, 0.11)]
    cut = lambda c: abs(math.atan2(c.y, c.x)) > math.radians(68 if c.z < 0.335 else 44)
    o = lathe(root, tag + '_avental', prof, m, segs=24, lv=2, caps=False, solid=0.006, cut=cut)
    o.parent = pr['body']
    st = cor('gola', rough=0.6)
    s = tube(root, tag + '_avAlca', [(0.075, -0.045, 0.445), (0.03, -0.065, 0.49), (-0.035, 0.0, 0.5), (0.03, 0.065, 0.49), (0.075, 0.045, 0.445)], 0.006, st, segs=5)
    s.parent = pr['body']
    estrela_peito(root, tag, pr['body'], (0.096, -0.028, 0.398), r=0.027, rot=(0, 0, math.pi / 2 - 0.3))


def turma(P, root, tag, hair=None, big=1.0, beard=None, scarf=None, ponytail=None, apron_long=False, face=None):
    sp = dict(tunic=cor('camisa'), sleeve=cor('camisa'), bracer=P['skin'], skirt_m=cor('calca'), pants=cor('calca'), belt=None, head='cap', head_m=cor('bone'),
              bare_hands=True, boot_m=mat('tenis_escuro', '#2a2626', rough=0.5, var=0, bump=0.02), boot_cuff=cor('calca'), big=big)
    if beard:
        sp.update(beard=beard, brow_m=beard)
    if scarf:
        sp['scarf'] = scarf
    pr = build_person(P, root, tag, sp)
    cap_bill(root, pr, tag, cor('bone'))
    if ponytail:
        for k, (dx, dz, r) in enumerate(((-0.07, 0.03, 0.03), (-0.095, -0.01, 0.026), (-0.105, -0.05, 0.02))):
            o = blob(root, f'{tag}_rabo{k}', r, HC + Vector((dx, 0, dz)), (1, 0.9, 1.15), ponytail)
            o.parent = pr['head']
        o = blob(root, tag + '_cabeloLado', 0.03, HC + Vector((0.0, 0, -0.02)), (1.0, 2.35, 0.9), ponytail)
        o.parent = pr['head']
    elif hair:
        o = blob(root, tag + '_cabeloNuca', 0.05, HC + Vector((-0.03, 0, -0.005)), (1.0, 1.35, 0.9), hair)
        o.parent = pr['head']
    avental(root, P, pr, tag, cor('escuro', rough=0.75, sheen=0.3), long_=apron_long)
    return pr


def espeto_mao(root, P, tag, L=0.6, n=3, R=0.042, kind='picanha'):
    """Espeto na mao (eixo Z local, empunhadura em z = 0): cabo de madeira para baixo, lamina e a carne no alto."""
    e = empty(root, tag + '_espetoMao', rot=(0, -math.pi / 2, 0))   # X local do espeto -> Z da mao
    x1 = L - 0.26
    xs = [x1 - 0.035 - k * (2.25 * R) for k in range(n)]
    espeto(root, P, tag + '_esp', 0.05, x1, xs, R=R, w=R * 1.45, parent=e, handle=True, kind=kind)
    for o in e.children:
        if o.name.endswith('_cabo'):
            o.location.x = -0.03
            o.scale = (1, 1, 1.5)
    return [e]


def macarico_mao(root, P, tag):
    """Macarico culinario de mao: cartucho vermelho, cabeca preta, gatilho laranja e a chaminha azul no bico."""
    objs = [cyl(root, tag + '_cart', 0.03, 0.16, (0, 0, 0.0), m=P['coifa'], v=16, bev=0.008),
            sphere(root, tag + '_cartDomo', 0.03, (0, 0, 0.08), scale=(1, 1, 0.5), m=P['coifa'], seg=14),
            torus(root, tag + '_cartFaixa', (0, 0, -0.05), 0.031, 0.005, P['branco'], n=16, segs=4),
            box(root, tag + '_cab', (0.06, 0.045, 0.055), (0.006, 0, 0.11), m=P['torch_k'], bev=0.014),
            box(root, tag + '_gat', (0.016, 0.018, 0.034), (-0.024, 0, 0.075), m=P['torch_o'], bev=0.005),
            tube(root, tag + '_bico', [(0.025, 0, 0.12), (0.065, 0, 0.14), (0.1, 0, 0.14)], 0.009, P['steel'], segs=8),
            lathe(root, tag + '_chama', [(0.0, 0.01, 0.01), (0.03, 0.016, 0.016), (0.06, 0.009, 0.009), (0.085, 0.0, 0.0)], P['blue'], segs=10, lv=1)]
    objs[-1].location = (0.105, 0, 0.14)
    objs[-1].rotation_euler = (0, math.pi / 2, 0)
    return objs


def build_apprentice(P, root):
    """Ajudante do churrasco: camiseta vermelha com estrela, avental, bone, jeans e o espeto de picanha."""
    tag = root['set']
    pr = turma(P, root, tag, hair=mat('cabelo_escuro', '#3a2416', rough=0.7, var=0.03, bump=0.25))
    hold(pr, 'R', *espeto_mao(root, P, tag, L=0.68, n=2, R=0.042))
    return pr


def build_mage(P, root):
    """Churrasqueira da turma: rabo de cavalo saindo do bone, avental comprido e o espeto cheio."""
    tag = root['set']
    pr = turma(P, root, tag, ponytail=mat('cabelo_preto', '#2a1a12', rough=0.7, var=0.03, bump=0.25), apron_long=True)
    hold(pr, 'R', *espeto_mao(root, P, tag, L=0.72, n=3, R=0.042))
    return pr


def build_archmage(P, root):
    """Churrasqueiro-chefe: barba e bigode brancos, barriga de quem prova tudo e o espetao com tres picanhas."""
    tag = root['set']
    pr = turma(P, root, tag, big=1.06, beard=P['white'])
    hold(pr, 'R', *espeto_mao(root, P, tag, L=0.78, n=3, R=0.047))
    return pr


def build_engineer(P, root):
    """Passador do rodizio: lenco branco no pescoco, avental e o espetinho curto que ele serve."""
    tag = root['set']
    pr = turma(P, root, tag, scarf=cor('gola', rough=0.7, sheen=0.4), hair=mat('cabelo_castanho_esc', '#3b2618', rough=0.7, var=0.03, bump=0.25))
    hold(pr, 'R', *espeto_mao(root, P, tag, L=0.42, n=1, R=0.042))
    return pr


def build_priestess(P, root):
    """Macariqueira: rabo de cavalo, avental e o macarico de mao com a chaminha azul."""
    tag = root['set']
    pr = turma(P, root, tag, ponytail=mat('cabelo_castanho', '#4a2a18', rough=0.7, var=0.03, bump=0.25))
    hold(pr, 'R', *macarico_mao(root, P, tag))
    return pr


IDLE_N, CAST_N = 12, 8


def mage_state(mode, f, big_staff=False):
    """idle: respira e olha em volta, espeto de pe; cast: ergue o espeto, gira e aponta para a frente (quadro 3 = disparo)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.14, 0.3 + 0.006 * s), grip_R=(0.12, -0.42, 1.0), hand_L=(0.1, 0.08, 0.3 + 0.01 * s),
                    pole_L=(-0.4, 1.0, -0.4), breathe=s, head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.22, ph=ph)
    # o espeto fica inclinado para fora (a picanha nao tampa o rosto); no lancamento ele gira por cima e aponta
    seq = [
        dict(hand_R=(0.08, -0.13, 0.36), grip_R=(0.12, -0.3, 1.0), hand_L=(0.12, 0.06, 0.34)),
        dict(hand_R=(0.02, -0.1, 0.52), grip_R=(-0.25, 0, 1.0), hand_L=(0.16, 0.1, 0.42), lean=-0.05),
        dict(hand_R=(0.0, -0.08, 0.6), grip_R=(-0.35, 0, 1.0), hand_L=(0.2, 0.12, 0.48), lean=-0.08),
        dict(hand_R=(0.2, -0.06, 0.46), grip_R=(1.0, 0, 0.55), hand_L=(0.2, 0.14, 0.4), lean=0.1),
        dict(hand_R=(0.22, -0.06, 0.44), grip_R=(1.0, 0, 0.45), hand_L=(0.16, 0.14, 0.36), lean=0.12),
        dict(hand_R=(0.18, -0.08, 0.4), grip_R=(0.8, 0, 0.7), hand_L=(0.13, 0.12, 0.32), lean=0.07),
        dict(hand_R=(0.12, -0.12, 0.35), grip_R=(0.4, -0.25, 1.0), hand_L=(0.11, 0.1, 0.31), lean=0.03),
        dict(hand_R=(0.1, -0.14, 0.31), grip_R=(0.14, -0.4, 1.0), hand_L=(0.1, 0.08, 0.3), lean=0.0),
    ][f]
    st = dict(breathe=0.0, head_yaw=0.15, head_pitch=-0.2, ph=f / CAST_N, pole_L=(-0.4, 1.0, -0.4), pole_R=(-0.6, -1.0, -0.2))
    st.update(seq)
    return st


def engineer_state(mode, f):
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.12, -0.12, 0.28 + 0.01 * s), grip_R=(0.4, 0, 1.0), hand_L=(0.03, 0.13, 0.27),
                    breathe=s, head_yaw=0.4 * math.sin(TAU * ph), head_pitch=-0.05 + 0.15 * max(0, math.sin(TAU * ph * 2)), ph=ph)
    # cast: estica o espetinho para a frente (serve o rodizio) e recolhe
    t = f / (CAST_N - 1)
    k = math.sin(math.pi * min(1, t * 1.6))
    return dict(hand_R=(0.2, -0.06 + 0.04 * k, 0.4 + 0.08 * k), grip_R=(1.0, 0.3 * k, 0.4), hand_L=(0.16, 0.1, 0.34 + 0.05 * k),
                lean=0.12 * k - 0.1 * max(0, t - 0.5), head_pitch=-0.12 * k, head_yaw=0.1, ph=t)


def priestess_state(mode, f):
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.13, 0.3 + 0.006 * s), grip_R=(0.0, 0.0, 1.0), hand_L=(0.12, 0.05, 0.36 + 0.01 * s),
                    pole_L=(-0.4, 1.0, -0.4), breathe=s, head_yaw=0.2 * math.sin(TAU * ph + 0.6), head_pitch=-0.15, ph=ph)
    t = f / (CAST_N - 1)
    k = math.sin(math.pi * t)
    return dict(hand_R=(0.08, -0.12 + 0.02 * k, 0.32 + 0.24 * k), grip_R=(0.1 * k, 0, 1.0), hand_L=(0.1 + 0.06 * k, 0.12, 0.36 + 0.2 * k),
                pole_L=(-0.4, 1.0, -0.2), head_pitch=-0.3 * k, head_yaw=0.1, lean=-0.06 * k, ph=t)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 3, 'cast'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('cast', CAST_N, lambda parts, P, root, f: pose(parts, P, root, f, 'cast'))]}


SPEC = {
    'show_crew': {'mg1': 'mgA', 'mg2': 'mgB', 'mg3': 'mgC', 'mgL': 'mgE', 'mgS': 'mgP'},
    'towers': [('mg1', 'Churrascao N1', build_mg1), ('mg2', 'Churrascao N2', build_mg2), ('mg3', 'Churrascao N3', build_mg3),
               ('mgL', 'Rodizio', build_mgL), ('mgS', 'Macarico do Churrasqueiro', build_mgS)],
    'crews': [crew('mgA', 'Ajudante do churrasco', build_apprentice, mage_state), crew('mgB', 'Churrasqueira da turma', build_mage, mage_state),
              crew('mgC', 'Churrasqueiro-chefe', build_archmage, mage_state), crew('mgE', 'Passador do rodizio', build_engineer, engineer_state),
              crew('mgP', 'Macariqueira', build_priestess, priestess_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
