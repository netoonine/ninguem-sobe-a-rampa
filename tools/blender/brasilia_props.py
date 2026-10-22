"""Enfeites 3D de Brasilia (Ninguem Sobe a Rampa), no mesmo estilo de massinha macia do cenario da mata
(arte/conceitos/v1/fase): ipes amarelos, arvores retorcidas do cerrado, capim seco, concreto branco curvo (Niemeyer),
blocos dos ministerios, Congresso (torres gemeas, cupula e tigela), Catedral, Rodoviaria com onibus, Palacio do
Planalto com as colunas curvas e a rampa, STF, mastro da bandeira (sem texto), pombal, pombos, postes, bordas dos
espelhos d'agua e o terraco dos lotes altos (o lote em si e o das torres: tools/blender/lote_brasilia.py).

Mesmas convencoes do cenario_props.py: cada peca nasce no chao (z do ponto passado); pecas pequenas e numerosas vao num
Lote (uma malha por material). Predios sao montados num vazio (empty) proprio, em coordenadas locais, com x ao longo da
fachada e a frente virada para -y (para a camera).
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise
from lib import (TAU, GLOW_MATS, mat, lin, box, cyl, sphere, tube, tube_into, torus, lathe, bm_to_obj, empty, subsurf)


# ---------------------------------------------------------------- materiais
def M_(key, hexcol, **kw):
    kw.setdefault('var', 0.05)
    kw.setdefault('bump', 0.08)
    return mat('br_' + key, hexcol, **kw)


def glow_glass(key, base, light, night, day=0.0, rough=0.2):
    """Vidro/luminaria: cor de dia `base`; no passe de luz acende com a cor `light` (forca `night`)."""
    m = mat('br_' + key, base, rough=rough, var=0.03, bump=0.0)
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Emission Color'].default_value = lin(light)
    b.inputs['Emission Strength'].default_value = day
    GLOW_MATS[m.name] = night
    return m


def br_mats():
    return {
        # concreto branco (um pouco abaixo do branco puro, senao estoura no sol)
        'conc': M_('concreto', '#e9e5db', rough=0.84, var=0.03, bump=0.06),
        'conc_l': M_('concreto_claro', '#f1eee6', rough=0.84, var=0.02, bump=0.05),
        'conc_d': M_('concreto_junta', '#cfc8ba', rough=0.88, var=0.04, bump=0.06),
        'conc_s': M_('concreto_sombra', '#b9b1a2', rough=0.9, var=0.04, bump=0.08),
        'granito': M_('granito', '#8f8a84', rough=0.7, var=0.08, bump=0.1),
        'vidro': M_('vidro', '#7b9fb4', rough=0.16, var=0.03, bump=0.0),
        'vidro_esc': M_('vidro_escuro', '#4f6a7c', rough=0.18, var=0.03, bump=0.0),
        # no passe de luz so os emissores aparecem (a poca de luz no chao vem da luz do jogo, js/vfx.js)
        'janela': glow_glass('janela_noite', '#7b9fb4', '#ffd07a', 2.2),
        'janela_esc': glow_glass('janela_noite_esc', '#56717f', '#ffc86a', 1.8),
        'luminaria': glow_glass('luminaria', '#fff4dc', '#ffd890', 3.5, day=0.35, rough=0.4),
        'metal': M_('metal', '#9aa1a3', rough=0.4, metal=0.5, var=0.03, bump=0.02),
        'metal_d': M_('metal_escuro', '#5d6366', rough=0.45, metal=0.4, var=0.03, bump=0.02),
        # ipe amarelo
        'ipe': M_('ipe', '#f7c81c', rough=0.62, var=0.08, bump=0.15, sheen=0.35),
        'ipe_l': M_('ipe_claro', '#ffdb4d', rough=0.62, var=0.08, bump=0.15, sheen=0.35),
        'ipe_d': M_('ipe_escuro', '#e19d12', rough=0.65, var=0.08, bump=0.15, sheen=0.3),
        'ipe_casca': M_('ipe_casca', '#6e4a34', rough=0.85, var=0.08, bump=0.4),
        # cerrado
        'casca': M_('casca_cerrado', '#5e4231', rough=0.9, var=0.1, bump=0.6),
        'casca_l': M_('casca_cerrado_cl', '#7a573e', rough=0.9, var=0.1, bump=0.6),
        'folha': M_('folha_cerrado', '#7f8b3e', rough=0.75, var=0.14, bump=0.12, sheen=0.25),
        'folha_l': M_('folha_cerrado_cl', '#9da44c', rough=0.75, var=0.12, bump=0.12, sheen=0.25),
        'capim': M_('capim_seco', '#d1a650', rough=0.85, var=0.14, bump=0.05),
        'capim_d': M_('capim_seco_esc', '#b28637', rough=0.85, var=0.14, bump=0.05),
        'capim_v': M_('capim_verde', '#98a447', rough=0.85, var=0.14, bump=0.05),
        'arbusto': M_('arbusto', '#7c8f3e', rough=0.8, var=0.12, bump=0.1, sheen=0.3),
        'arbusto_l': M_('arbusto_cl', '#98ab4c', rough=0.8, var=0.12, bump=0.1, sheen=0.3),
        'pedra': M_('pedra', '#c9c0b0', rough=0.85, var=0.14, bump=0.25),
        'seixo': M_('seixo', '#ddd3c2', rough=0.85, var=0.16, bump=0.2),
        'terra': M_('terra_vermelha', '#b2603e', rough=0.95, var=0.06, bump=0.3),
        # onibus e bandeira
        'branco': M_('pintura_branca', '#f3f0e8', rough=0.5, var=0.02, bump=0.02),
        'pneu': M_('pneu', '#2d2b2c', rough=0.8, var=0.03, bump=0.05),
        'azul': M_('azul', '#2f74b0', rough=0.55, var=0.03, bump=0.02),
        'verde': M_('verde', '#3a9a52', rough=0.55, var=0.03, bump=0.02),
        'amarelo': M_('amarelo', '#efb52a', rough=0.55, var=0.03, bump=0.02),
        'vermelho': M_('vermelho', '#c64a36', rough=0.55, var=0.03, bump=0.02),
        # pombos
        'pombo': M_('pombo', '#8f929b', rough=0.75, var=0.1, bump=0.05),
        'pombo_d': M_('pombo_esc', '#6c6f79', rough=0.75, var=0.1, bump=0.05),
        'pombo_pesc': M_('pombo_pescoco', '#5f7f78', rough=0.6, var=0.08, bump=0.03),
    }


# ---------------------------------------------------------------- vegetacao do cerrado
def ipe(root, lote, name, loc, s, rr, M, ground=None, petals=True):
    """Ipe amarelo florido: tronco escuro que se abre em galhos e uma copa de pompons amarelos; flores caidas no chao."""
    x, y, z = loc
    H = 1.0 * s
    lx, ly = rr.uniform(-0.12, 0.12) * s, rr.uniform(-0.05, 0.08) * s
    pts = []
    for k in range(6):
        t = k / 5
        pts.append((x + lx * t * t + 0.03 * s * math.sin(t * 5 + x), y + ly * t * t, z - 0.04 + H * t))
    tube(root, name + '_tronco', pts, 0.1 * s, M['ipe_casca'], segs=10, rfun=lambda t: s * (0.11 - 0.05 * t))
    top = Vector(pts[-1])
    centers = []
    nb = rr.choice((3, 4, 4, 5))
    a0 = rr.uniform(0, TAU)
    for k in range(nb):
        a = a0 + TAU * k / nb + rr.uniform(-0.3, 0.3)
        r = s * rr.uniform(0.38, 0.55)
        z0 = H * rr.uniform(0.62, 0.9)
        b0 = Vector((x + lx * 0.6, y + ly * 0.6, z + z0))
        tip = Vector((x + lx + r * math.cos(a), y + ly + r * math.sin(a) * 0.85, z + H + s * rr.uniform(0.2, 0.4)))
        mid = b0.lerp(tip, 0.5) + Vector((0, 0, 0.08 * s))
        tube(root, f'{name}_galho{k}', [b0, mid, tip], 0.05 * s, M['ipe_casca'], segs=7, rfun=lambda t: s * (0.055 - 0.03 * t))
        centers.append(tip)
    centers.append(top + Vector((0, 0, 0.42 * s)))
    # copa: pompons amarelos em volta de cada ponta de galho (mais claros em cima, mais escuros por baixo)
    for c in centers:
        for j in range(rr.randrange(9, 13)):
            u = rr.uniform(0, TAU)
            v = rr.uniform(-0.35, 1.0)
            rad = s * rr.uniform(0.12, 0.3)
            p = (c.x + rad * math.cos(u) * math.sqrt(1 - v * v * 0.6), c.y + rad * math.sin(u) * 0.85, c.z + rad * 0.7 * v)
            mk = M['ipe_l'] if v > 0.45 else (M['ipe_d'] if v < -0.05 else M['ipe'])
            lote.pebble(mk, p, s * rr.uniform(0.1, 0.16), squash=0.85, rot=rr.uniform(0, TAU), rr=rr, sub=2, rough=0.32)
    if petals and ground:
        # flores caidas: tapete amarelo ralo em volta do pe
        for k in range(int(26 * s)):
            a = rr.uniform(0, TAU)
            d = s * 0.75 * math.sqrt(rr.random())
            px, py = x + d * math.cos(a) + lx * 0.5, y + d * math.sin(a) * 0.8
            lote.disc(M['ipe'] if k % 3 else M['ipe_d'], (px, py, ground(px, py) + 0.004), s * rr.uniform(0.025, 0.045), h=0.008, n=8)
    return centers


def arvore_cerrado(root, lote, name, loc, s, rr, M, leaves=True):
    """Arvore retorcida do cerrado: tronco torto de casca grossa, galhos em zigue-zague e poucas folhas."""
    x, y, z = loc
    hd = rr.uniform(0, TAU)
    p = Vector((x, y, z - 0.05))
    pts = [p.copy()]
    H = 0.95 * s
    for k in range(6):
        hd += rr.uniform(-1.0, 1.0)
        p = p + Vector((math.cos(hd) * 0.09 * s, math.sin(hd) * 0.07 * s, H / 6))
        pts.append(p.copy())
    tube(root, name + '_tronco', pts, 0.12 * s, M['casca'], segs=10, rfun=lambda t: s * (0.13 - 0.06 * t) * (1 + 0.12 * math.sin(t * 17)))
    tips = []
    for k in range(rr.choice((3, 3, 4))):
        q = Vector(pts[rr.randrange(3, 6)])
        a = rr.uniform(0, TAU)
        bp = [q.copy()]
        for j in range(4):
            a += rr.uniform(-0.9, 0.9)
            q = q + Vector((math.cos(a) * 0.16 * s, math.sin(a) * 0.12 * s, rr.uniform(0.05, 0.16) * s))
            bp.append(q.copy())
        tube(root, f'{name}_galho{k}', bp, 0.06 * s, M['casca_l'] if k % 2 else M['casca'], segs=7, rfun=lambda t: s * (0.065 - 0.045 * t))
        tips.append(q)
        if rr.random() < 0.6:
            sq = bp[2]
            b2 = [sq, sq + Vector((rr.uniform(-0.18, 0.18) * s, rr.uniform(-0.12, 0.12) * s, 0.14 * s))]
            tube(root, f'{name}_ramo{k}', b2, 0.03 * s, M['casca'], segs=6, rfun=lambda t: s * (0.032 - 0.02 * t))
    if leaves:
        for k, t_ in enumerate(tips):
            if rr.random() < 0.3:
                continue
            for j in range(rr.randrange(2, 4)):
                c = t_ + Vector((rr.uniform(-0.1, 0.1) * s, rr.uniform(-0.08, 0.08) * s, rr.uniform(0.0, 0.1) * s))
                lote.pebble(M['folha'] if (j + k) % 2 else M['folha_l'], tuple(c), s * rr.uniform(0.1, 0.16), squash=0.6, rot=rr.uniform(0, TAU), rr=rr, rough=0.35)
    return tips


def capim(lote, M, loc, size, rr, verde=False):
    """Touceira de capim seco do cerrado: laminas longas, finas e arqueadas."""
    n = rr.randrange(9, 14)
    m1, m2 = (M['capim_v'], M['capim']) if verde else (M['capim'], M['capim_d'])
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.4, 0.4)
        lean = rr.uniform(0.2, 0.55)
        hgt = size * rr.uniform(0.65, 1.15)
        b = (loc[0] + 0.03 * math.cos(a) * rr.random(), loc[1] + 0.03 * math.sin(a) * rr.random(), loc[2] - 0.01)
        t = (b[0] + math.cos(a) * hgt * lean, b[1] + math.sin(a) * hgt * lean, loc[2] + hgt)
        lote.blade(m2 if k % 3 == 0 else m1, b, t, size * 0.06)


# ---------------------------------------------------------------- pecas de concreto
def curb_loop(root, name, pts, w, ht, zb, m, sub=1, closed=True):
    """Meio-fio/borda de concreto ao longo de uma curva no chao (pontos do mundo): secao retangular de largura w,
    topo em ht (relativo ao z de cada ponto) e base em zb, arredondada pelo subsurf."""
    bm = bmesh.new()
    P = [Vector(p) for p in pts]
    n = len(P)
    prof = [(-0.5, zb), (-0.5, ht - 0.25 * w), (-0.3, ht), (0.3, ht), (0.5, ht - 0.25 * w), (0.5, zb)]
    rings = []
    for i in range(n):
        a = P[(i - 1) % n] if closed else P[max(0, i - 1)]
        b = P[(i + 1) % n] if closed else P[min(n - 1, i + 1)]
        t = Vector((b.x - a.x, b.y - a.y, 0))
        t = t.normalized() if t.length > 1e-9 else Vector((1, 0, 0))
        nrm = Vector((t.y, -t.x, 0))
        rings.append([bm.verts.new((P[i].x + nrm.x * o * w, P[i].y + nrm.y * o * w, P[i].z + zz)) for (o, zz) in prof])
    last = n if closed else n - 1
    k = len(prof)
    for i in range(last):
        A, B = rings[i], rings[(i + 1) % n]
        for j in range(k - 1):
            bm.faces.new((A[j], A[j + 1], B[j + 1], B[j]))
        bm.faces.new((A[k - 1], A[0], B[0], B[k - 1]))
    if not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    o = bm_to_obj(bm, name, root, [m], angle=89)
    if sub:
        subsurf(o, sub)
    return o


def terraco(root, name, c, top_z, M, rr):
    """Lote alto: terraco de concreto branco num pe em calice (o "pe" curvo de Niemeyer), topo plano em top_z."""
    prof = [(-0.05, 0.98, 0.92), (0.04, 0.95, 0.89), (0.14, 0.7, 0.66), (0.26, 0.56, 0.53), (0.38, 0.6, 0.57),
            (top_z - 0.16, 1.02, 0.95), (top_z - 0.07, 1.17, 1.09), (top_z, 1.17, 1.09)]
    o = lathe(root, name, prof, M['conc'], segs=48, lv=2)
    o.location = (c[0], c[1], 0)
    # junta escura sob a borda (le como a sombra da marquise) e a borda clara do topo
    band = lathe(root, name + '_faixa', [(top_z - 0.1, 1.12, 1.045), (top_z - 0.085, 1.135, 1.06)], M['conc_d'], segs=48, lv=1, caps=False)
    band.location = (c[0], c[1], 0)
    return o


def blade_xz(root, name, outline, t, m, loc=(0, 0, 0), bev=0.02):
    """Peca plana em XZ (contorno fechado, de baixo para cima pela esquerda e voltando pela direita) com espessura t em Y."""
    bm = bmesh.new()
    F = [bm.verts.new((px, -t / 2, pz)) for (px, pz) in outline]
    B = [bm.verts.new((px, t / 2, pz)) for (px, pz) in outline]
    bm.faces.new(list(reversed(F)))
    bm.faces.new(B)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((F[i], F[j], B[j], B[i]))
    o = bm_to_obj(bm, name, root, [m], angle=30, bev=bev, seg=2)
    o.location = loc
    return o


def coluna_planalto(root, name, x, y, z0, h, wt, wb, t, m, p=2.6):
    """Coluna curva do Planalto/STF vista de frente: ponta fina no chao, abrindo em curva ate encostar na laje; entre
    duas colunas o vao fica um arco."""
    left, right = [], []
    n = 14
    for i in range(n + 1):
        zz = h * i / n
        hw = wb / 2 + (wt / 2 - wb / 2) * (zz / h) ** p
        left.append((-hw, zz))
        right.append((hw, zz))
    outline = left + list(reversed(right))
    return blade_xz(root, name, outline, t, m, loc=(x, y, z0), bev=0.012)


def predio_faixas(root, name, loc, w, d, h, M, ang=0.0, floors=None, glass=None, pilotis=True, ends=True, roof=True):
    """Bloco modernista (ministerio, anexo): lajes brancas em faixas com vidro entre elas, empenas cegas nas pontas,
    terreo em pilotis e a casa de maquinas no teto."""
    sub = empty(root, name, loc, rot=(0, 0, ang))
    g = glass or M['vidro']
    z0 = 0.3 if pilotis else 0.0
    floors = floors or max(3, int((h - z0) / 0.24))
    box(sub, name + '_vidro', (w - 0.12, d - 0.14, h - z0 - 0.04), (0, 0, z0 + (h - z0) / 2), m=g, bev=0.02)
    for k in range(floors + 1):
        zk = z0 + (h - z0 - 0.07) * k / floors
        box(sub, f'{name}_laje{k}', (w - 0.04, d, 0.075), (0, 0, zk + 0.035), m=M['conc'], bev=0.028)
    if ends:
        for sx in (-1, 1):
            box(sub, f'{name}_empena{sx}', (0.14, d + 0.05, h - z0 + 0.04), (sx * (w / 2 - 0.05), 0, z0 + (h - z0) / 2), m=M['conc'], bev=0.05)
    if pilotis:
        nx = max(2, int(w / 0.75))
        for i in range(nx + 1):
            px = -w / 2 + 0.22 + (w - 0.44) * i / nx
            for py in (-d / 2 + 0.17, d / 2 - 0.17):
                cyl(sub, f'{name}_pilar{i}_{"f" if py < 0 else "t"}', 0.06, z0 + 0.02, (px, py, z0 / 2), m=M['conc'], v=12, bev=0.01)
        box(sub, name + '_terreo', (w * 0.55, d * 0.45, z0), (0, 0.04, z0 / 2), m=M['vidro_esc'], bev=0.02)
    if roof:
        box(sub, name + '_casa', (w * 0.28, d * 0.45, 0.17), (w * 0.12, 0.05, h + 0.08), m=M['conc'], bev=0.05)
    return sub


def colunata(sub, name, W, D, z0, Hc, n, M, t=0.09, wb=0.05, back=True, y_off=0.36, wt=None):
    """Colunas curvas na frente (e atras) de um palacio: n vaos ao longo de W."""
    sp = W / n
    wt = wt or sp * 0.92
    for side in ((-1, 1) if back else (-1,)):
        y = side * (D / 2 + y_off)
        for i in range(n + 1):
            x = -W / 2 + sp * i
            coluna_planalto(sub, f'{name}_col{"f" if side < 0 else "t"}{i}', x, y, z0, Hc, wt if 0 < i < n else wt * 0.5, wb, t, M['conc_l'])


def planalto(root, name, loc, s, M, glass=None, n_col=8, W=6.6, D=1.5, zf=None, Hc=None):
    """Palacio do Planalto: caixa de vidro sobre o piso elevado, laje de cobertura fina e as colunas curvas na frente e
    atras. W e D (planta) em unidades; s escala as alturas (zf e Hc, se dados, fixam o piso nobre e a laje).
    A rampa e uma peca a parte (rampa())."""
    g = glass or M['vidro']
    sub = empty(root, name, loc)
    zf = zf if zf is not None else 0.42 * s    # piso do salao nobre (onde a rampa chega)
    Hc = Hc if Hc is not None else 1.8 * s     # face de baixo da laje de cobertura
    yc = D / 2 + 0.32 * s  # linha das colunas
    # embasamento de concreto em volta e o terreo recuado de vidro escuro sobre pilotis
    box(sub, name + '_base', (W + 1.0, 2 * yc + 0.7, 0.08), (0, 0, 0.02), m=M['conc_d'], bev=0.03)
    box(sub, name + '_terreo', (W - 1.0, D - 0.4, zf), (0, 0, zf / 2), m=M['vidro_esc'], bev=0.02)
    for i in range(7):
        px = -W / 2 + 0.5 + (W - 1.0) * i / 6
        for py in (-D / 2 + 0.22, D / 2 - 0.22):
            cyl(sub, f'{name}_pilotis{i}{"f" if py < 0 else "t"}', 0.05 * s, zf, (px, py, zf / 2), m=M['conc'], v=12, bev=0.01)
    # piso nobre (laje ate a linha das colunas) e a caixa de vidro com os andares
    box(sub, name + '_piso', (W + 0.2, 2 * yc + 0.16, 0.1 * s), (0, 0, zf), m=M['conc'], bev=0.03)
    hb = Hc - zf - 0.05 * s
    box(sub, name + '_vidro', (W - 0.3, D, hb), (0, 0, zf + 0.05 * s + hb / 2), m=g, bev=0.02)
    for k in range(1, 3):
        zk = zf + hb * k / 3
        box(sub, f'{name}_andar{k}', (W - 0.26, D + 0.04, 0.05 * s), (0, 0, zk + 0.05 * s), m=M['conc'], bev=0.015)
    nm = 16
    for i in range(nm + 1):
        px = -(W - 0.3) / 2 + (W - 0.3) * i / nm
        box(sub, f'{name}_montante{i}', (0.025, D + 0.03, hb), (px, 0, zf + 0.05 * s + hb / 2), m=M['metal'], bev=0.0)
    # cobertura fina, so um pouco alem das colunas; em cima, o miolo em concreto mais escuro (a laje nao vira um
    # retangulo branco chapado vista do alto) e as casas de maquinas
    box(sub, name + '_laje', (W + 0.3, 2 * yc + 0.22, 0.12 * s), (0, 0, Hc + 0.06 * s), m=M['conc_l'], bev=0.04)
    box(sub, name + '_lajeMiolo', (W - 0.2, 2 * yc - 0.3, 0.02), (0, 0, Hc + 0.12 * s + 0.005), m=M['conc_d'], bev=0.01)
    for k, px in enumerate((-W * 0.22, W * 0.22)):
        box(sub, f'{name}_casaMaq{k}', (0.6, 0.35, 0.14), (px, 0.1, Hc + 0.12 * s + 0.07), m=M['conc'], bev=0.04)
    colunata(sub, name, W, D, 0.0, Hc, n_col, M, t=0.1 * s, wb=0.05 * s, y_off=0.32 * s)
    return sub, {'zf': zf, 'yc': yc, 'Hc': Hc}


def rampa(root, name, p0, p1, w, M, th=0.12, k=1.0):
    """Rampa de concreto do chao (p0, no z dele) ate p1 (no z dele): laje grossa com muretas brancas dos dois lados e
    a cunha por baixo (de lado ela le como uma rampa subindo). k escala a espessura e as muretas (tela de inicio)."""
    th = th * k
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    Lxy = math.hypot(d.x, d.y)
    yaw = math.atan2(d.y, d.x)
    pitch = math.atan2(d.z, Lxy)
    L3 = math.hypot(Lxy, d.z)
    mid = (p0 + p1) / 2
    rot = (0, -pitch, yaw)
    o = box(root, name, (L3 + 0.04, w, th), (mid.x, mid.y, mid.z - th / 2), rot=rot, m=M['conc_l'], bev=0.03)
    nrm = Vector((-math.sin(yaw), math.cos(yaw), 0))
    for sx in (-1, 1):
        q = mid + nrm * sx * (w / 2 - 0.035 * k)
        box(root, f'{name}_mureta{sx}', (L3 + 0.04, 0.07 * k, 0.17 * k), (q.x, q.y, q.z + 0.07 * k), rot=rot, m=M['conc'], bev=0.025 * k)
    # cunha por baixo: perfil triangular (sombra embaixo da rampa)
    bm = bmesh.new()
    ux, uy = math.cos(yaw), math.sin(yaw)
    hw = w / 2 - 0.08 * k
    pts = []
    for side in (-1, 1):
        ox, oy = -uy * hw * side, ux * hw * side
        pts.append((bm.verts.new((p0.x + ox + ux * 0.3, p0.y + oy + uy * 0.3, p0.z - 0.05)),
                    bm.verts.new((p1.x + ox, p1.y + oy, p0.z - 0.05)),
                    bm.verts.new((p1.x + ox, p1.y + oy, p1.z - th - 0.01))))
    A, B = pts
    bm.faces.new((A[0], A[1], A[2]))
    bm.faces.new((B[2], B[1], B[0]))
    bm.faces.new((A[0], B[0], B[1], A[1]))
    bm.faces.new((A[1], B[1], B[2], A[2]))
    bm.faces.new((A[2], B[2], B[0], A[0]))
    bm_to_obj(bm, name + '_cunha', root, [M['conc_d']], angle=30)
    return o


def stf(root, name, loc, s, M, glass=None):
    """Supremo: um palacio baixo com as mesmas colunas curvas, so na frente e nas laterais."""
    W, D = 3.6 * s, 1.6 * s
    sub = empty(root, name, loc)
    zf = 0.12 * s
    Hc = 1.05 * s
    box(sub, name + '_base', (W + 0.8 * s, D + 1.1 * s, 0.08), (0, 0, 0.02), m=M['conc_d'], bev=0.03)
    box(sub, name + '_vidro', (W - 0.3 * s, D, Hc - zf), (0, 0, zf + (Hc - zf) / 2), m=glass or M['vidro'], bev=0.02)
    box(sub, name + '_andar', (W - 0.26 * s, D + 0.04, 0.05 * s), (0, 0, zf + (Hc - zf) * 0.5), m=M['conc'], bev=0.015)
    yc = D / 2 + 0.36 * s
    box(sub, name + '_laje', (W + 0.3 * s, 2 * yc + 0.35 * s, 0.12 * s), (0, 0, Hc + 0.06 * s), m=M['conc_l'], bev=0.04)
    colunata(sub, name, W, D, 0.0, Hc, 5, M, t=0.09 * s, wb=0.045 * s, y_off=0.36 * s)
    return sub


def congresso(root, name, loc, s, M, glass=None, glass2=None, W=7.0, D=1.7, sd=1.15, Ht=3.9):
    """Congresso Nacional: o predio baixo e largo, a cupula do Senado (virada para baixo) a esquerda, a tigela da Camara
    (virada para cima) a direita e as duas torres gemeas atras, ligadas no meio. W e D (planta) em unidades; s escala as
    alturas, sd a cupula e a tigela."""
    g = glass or M['vidro']
    g2 = glass2 or g
    sub = empty(root, name, loc)
    Hp = 0.6 * s
    box(sub, name + '_base', (W, D, Hp * 0.25), (0, 0, Hp * 0.125), m=M['conc_d'], bev=0.04)
    box(sub, name + '_vidro', (W - 0.16, D - 0.16, Hp * 0.6), (0, 0, Hp * 0.25 + Hp * 0.3), m=g, bev=0.02)
    for k in range(14):
        px = -W / 2 + 0.2 + (W - 0.4) * k / 13
        box(sub, f'{name}_brise{k}', (0.05, D - 0.1, Hp * 0.6), (px, 0, Hp * 0.55), m=M['conc'], bev=0.01)
    box(sub, name + '_cobertura', (W + 0.12, D + 0.12, 0.14 * s), (0, 0, Hp + 0.02 * s), m=M['conc_l'], bev=0.05)
    zt = Hp + 0.09 * s
    k_ = sd * s
    # Senado: cupula macia
    dome = lathe(sub, name + '_cupula', [(0.0, 0.95 * k_, 0.95 * k_), (0.08 * k_, 0.94 * k_, 0.94 * k_), (0.25 * k_, 0.82 * k_, 0.82 * k_),
                                         (0.4 * k_, 0.6 * k_, 0.6 * k_), (0.5 * k_, 0.32 * k_, 0.32 * k_), (0.54 * k_, 0.0, 0.0)],
                 M['conc_l'], segs=48, lv=2)
    dome.location = (-W * 0.31, -0.02, zt)
    # Camara: tigela aberta para cima, num pe curto
    bowl = lathe(sub, name + '_tigela', [(0.0, 0.32 * k_, 0.32 * k_), (0.1 * k_, 0.42 * k_, 0.42 * k_), (0.3 * k_, 0.85 * k_, 0.85 * k_),
                                         (0.48 * k_, 1.22 * k_, 1.22 * k_), (0.56 * k_, 1.36 * k_, 1.36 * k_)],
                 M['conc_l'], segs=56, lv=2, caps=False, solid=0.07 * k_)
    bowl.location = (W * 0.31, -0.02, zt)
    cyl(sub, name + '_tigelaFundo', 0.33 * k_, 0.03, (W * 0.31, -0.02, zt + 0.02), m=M['conc_d'], v=32, bev=0.0)
    # torres gemeas (logo atras do predio baixo) e as passarelas entre elas
    ty = D / 2 + 0.42
    Ht = Ht * s
    for sx in (-1, 1):
        tx = sx * 0.6 * s
        box(sub, f'{name}_torre{sx}', (0.82 * s, 0.56 * s, Ht), (tx, ty, Ht / 2), m=g2, bev=0.03)
        n = 17
        for k in range(n + 1):
            box(sub, f'{name}_torre{sx}_laje{k}', (0.86 * s, 0.6 * s, 0.05 * s), (tx, ty, 0.05 + (Ht - 0.1) * k / n), m=M['conc'], bev=0.015)
        for ex in (-1, 1):
            box(sub, f'{name}_torre{sx}_empena{ex}', (0.07 * s, 0.6 * s, Ht + 0.04), (tx + ex * 0.43 * s, ty, Ht / 2), m=M['conc'], bev=0.03)
    for k, zz in enumerate((0.47, 0.6)):
        box(sub, f'{name}_ponte{k}', (0.36 * s, 0.5 * s, 0.4 * s), (0, ty, zz * Ht), m=M['conc'], bev=0.03)
    # rampa de acesso a cobertura (na frente, no eixo)
    rl = 1.5 * s
    tilt = math.atan2(Hp, rl)
    box(sub, name + '_rampa', (0.55 * s, math.hypot(rl, Hp), 0.06 * s), (0.0, -D / 2 - rl / 2, Hp / 2 + 0.02), rot=(tilt, 0, 0), m=M['conc_l'], bev=0.02)
    return sub, {'Ht': Ht, 'ty': ty, 'W': W, 'D': D, 'Hp': Hp, 'rl': rl}


def catedral(root, name, loc, s, M, n=16):
    """Catedral: 16 colunas curvas de concreto formando a coroa (hiperboloide), com o vidro azul claro entre elas."""
    sub = empty(root, name, loc)
    R0, Rw, Rt = 1.0 * s, 0.5 * s, 0.82 * s
    H = 1.9 * s
    for k in range(n):
        a = TAU * k / n
        pts = []
        for i in range(8):
            t = i / 7
            r = R0 * (1 - t) ** 2 + Rw * 2 * t * (1 - t) * 0.9 + Rt * t * t
            r = r if t < 0.92 else r + (t - 0.92) * 1.5 * s
            z = H * t
            pts.append((r * math.cos(a), r * math.sin(a), z))
        tube(sub, f'{name}_coluna{k}', pts, 0.07 * s, M['conc_l'], segs=8, rfun=lambda t: s * (0.085 - 0.05 * t))
    glass = M_('vidro_catedral', '#a9cde0', rough=0.12, var=0.02, bump=0.0)
    prof = []
    for i in range(9):
        t = i / 8
        r = (R0 * (1 - t) ** 2 + Rw * 2 * t * (1 - t) * 0.9 + Rt * t * t) * 0.93
        prof.append((H * 0.9 * t, r, r))
    lathe(sub, name + '_vidro', prof, glass, segs=48, lv=1, caps=False)
    cyl(sub, name + '_base', R0 * 1.25, 0.08, (0, 0, 0.0), m=M['conc_d'], v=48, bev=0.03)
    return sub


def rodoviaria(root, name, loc, s, M, W=6.0, D=1.5):
    """Plataforma da Rodoviaria: laje comprida bem alta sobre duas filas de pilares (o embarque e as lojas ficam
    embaixo, na sombra), mureta, quiosques de vidro, floreiras e uma marquise curva em cima."""
    W, D = W * s, D * s
    sub = empty(root, name, loc)
    Hd = 0.9 * s
    box(sub, name + '_embarque', (W + 0.3 * s, D + 0.5 * s, 0.07), (0, 0, 0.02), m=M['conc_d'], bev=0.02)
    for i in range(9):
        px = -W / 2 + 0.3 * s + (W - 0.6 * s) * i / 8
        for py in (-D / 2 + 0.25 * s, D / 2 - 0.25 * s):
            box(sub, f'{name}_pilar{i}{"f" if py < 0 else "t"}', (0.16 * s, 0.16 * s, Hd), (px, py, Hd / 2), m=M['conc'], bev=0.04)
    box(sub, name + '_lojas', (W * 0.8, D * 0.32, Hd * 0.62), (0, 0.15 * s, Hd * 0.31), m=M['vidro_esc'], bev=0.02)
    for k in range(5):
        box(sub, f'{name}_toldo{k}', (W * 0.12, 0.08 * s, 0.05 * s), (-W * 0.32 + k * W * 0.16, 0.15 * s - D * 0.16 - 0.04 * s, Hd * 0.6),
            m=(M['azul'], M['amarelo'], M['verde'], M['vermelho'], M['azul'])[k], bev=0.015)
    box(sub, name + '_laje', (W, D, 0.2 * s), (0, 0, Hd + 0.1 * s), m=M['conc'], bev=0.07)
    zt = Hd + 0.2 * s
    for sy in (-1, 1):
        box(sub, f'{name}_mureta{sy}', (W - 0.12 * s, 0.06 * s, 0.13 * s), (0, sy * (D / 2 - 0.05 * s), zt + 0.065 * s), m=M['conc_l'], bev=0.02)
    for k, px in enumerate((-W * 0.33, W * 0.0, W * 0.33)):
        w_ = W * 0.13
        box(sub, f'{name}_quiosque{k}', (w_, D * 0.36, 0.3 * s), (px, 0.12 * s, zt + 0.15 * s), m=M['vidro'], bev=0.02)
        box(sub, f'{name}_quiosqueTeto{k}', (w_ + 0.12 * s, D * 0.36 + 0.12 * s, 0.06 * s), (px, 0.12 * s, zt + 0.33 * s), m=M['conc_l'], bev=0.02)
    for k, px in enumerate((-W * 0.165, W * 0.165)):
        box(sub, f'{name}_floreira{k}', (W * 0.12, D * 0.25, 0.12 * s), (px, -0.2 * s, zt + 0.06 * s), m=M['conc_l'], bev=0.03)
        for j in range(3):
            sphere(sub, f'{name}_moita{k}_{j}', 0.13 * s, (px + (j - 1) * 0.22 * s, -0.2 * s, zt + 0.18 * s), scale=(1, 1, 0.8),
                   m=M['arbusto'] if j % 2 else M['arbusto_l'], seg=12)
    # marquise curva (laje fina de bordas redondas) sobre pilares finos, na ponta direita
    mq = cyl(sub, name + '_marquise', 0.62 * s, 0.06 * s, (W * 0.3, 0.05 * s, zt + 0.62 * s), m=M['conc_l'], v=40, bev=0.02)
    mq.scale = (1.9, 0.85, 1)
    for k in range(3):
        cyl(sub, f'{name}_marqPilar{k}', 0.035 * s, 0.6 * s, (W * 0.3 + (k - 1) * 0.6 * s, 0.05 * s, zt + 0.3 * s), m=M['conc'], v=10, bev=0.0)
    return sub


def onibus(root, name, loc, ang, M, cor, s=1.0):
    """Onibus estacionado (enfeite): carroceria branca de cantos redondos, faixa colorida, janelas escuras, rodas."""
    sub = empty(root, name, loc, rot=(0, 0, ang))
    L, Wb = 1.4 * s, 0.48 * s
    box(sub, name + '_carroceria', (L, Wb, 0.42 * s), (0, 0, 0.31 * s), m=M['branco'], bev=0.08 * s)
    box(sub, name + '_janelas', (L - 0.16 * s, Wb + 0.012, 0.15 * s), (-0.02 * s, 0, 0.4 * s), m=M['vidro_esc'], bev=0.03 * s)
    box(sub, name + '_parabrisa', (0.04, Wb - 0.08 * s, 0.2 * s), (L / 2 - 0.005, 0, 0.38 * s), m=M['vidro_esc'], bev=0.02 * s)
    box(sub, name + '_faixa', (L + 0.006, Wb + 0.014, 0.07 * s), (0, 0, 0.24 * s), m=cor, bev=0.02 * s)
    box(sub, name + '_teto', (L - 0.3 * s, Wb - 0.14 * s, 0.05 * s), (-0.05 * s, 0, 0.53 * s), m=M['conc_d'], bev=0.02 * s)
    for wx in (-0.42 * s, 0.4 * s):
        for wy in (-1, 1):
            cyl(sub, f'{name}_roda{wx:.2f}{wy}', 0.1 * s, 0.07 * s, (wx, wy * (Wb / 2 - 0.02 * s), 0.1 * s), rot=(math.pi / 2, 0, 0), m=M['pneu'], v=16, bev=0.02 * s)
    return sub


def poste(root, name, loc, M, s=1.0, ang=0.0):
    """Poste de luz (concreto claro, braco curvo e luminaria que acende no passe de luz). Devolve a ponta acesa."""
    x, y, z = loc
    h = 1.3 * s
    tube(root, name + '_haste', [(x, y, z - 0.02), (x, y, z + h)], 0.035 * s, M['metal_d'], segs=8, rfun=lambda t: s * (0.045 - 0.018 * t))
    dx, dy = math.cos(ang) * 0.22 * s, math.sin(ang) * 0.22 * s
    tube(root, name + '_braco', [(x, y, z + h - 0.02), (x + dx * 0.5, y + dy * 0.5, z + h + 0.07 * s), (x + dx, y + dy, z + h + 0.03 * s)],
         0.022 * s, M['metal_d'], segs=7)
    tip = (x + dx * 1.05, y + dy * 1.05, z + h)
    sphere(root, name + '_luminaria', 0.075 * s, tip, scale=(1.4, 1.4, 0.55), m=M['luminaria'], seg=14)
    cyl(root, name + '_pe', 0.07 * s, 0.06, (x, y, z + 0.02), m=M['conc_d'], v=12, bev=0.01)
    return tip


def pilar_saida(root, name, loc, M, s=1.0, lamp=True):
    """Pilar da saida: lamina curva de concreto branco (o perfil das colunas do Alvorada) com uma luz no topo."""
    x, y, z = loc
    h = 1.25 * s
    out = []
    n = 12
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        hw = s * (0.05 + 0.2 * (1 - t) ** 3 + 0.12 * t ** 3)
        left.append((-hw, h * t))
        right.append((hw, h * t))
    o = blade_xz(root, name, left + list(reversed(right)), 0.16 * s, M['conc_l'], loc=(x, y, z - 0.02), bev=0.03)
    out.append(o)
    cyl(root, name + '_base', 0.3 * s, 0.08, (x, y, z + 0.02), m=M['conc_d'], v=20, bev=0.02)
    tip = None
    if lamp:
        tip = (x, y, z + h + 0.06 * s)
        sphere(root, name + '_luz', 0.08 * s, tip, scale=(1, 1, 0.8), m=M['luminaria'], seg=14)
    return tip


def mastro(root, name, loc, s, M, rr, flag=True):
    """Mastro da Bandeira da Praca dos Tres Poderes: feixe de hastes de metal sobre a base redonda, e a bandeira
    (verde, losango amarelo e circulo azul, sem a faixa com o lema)."""
    x, y, z = loc
    H = 4.2 * s
    lathe(root, name + '_base', [(-0.05, 0.62 * s, 0.62 * s), (0.08 * s, 0.6 * s, 0.6 * s), (0.1 * s, 0.44 * s, 0.44 * s),
                                 (0.2 * s, 0.42 * s, 0.42 * s), (0.22 * s, 0.24 * s, 0.24 * s), (0.3 * s, 0.22 * s, 0.22 * s), (0.3 * s, 0, 0)],
          M['conc_l'], segs=40, lv=1).location = (x, y, z)
    for k in range(6):
        a = TAU * k / 6
        r0, r1 = 0.1 * s, 0.035 * s
        tube(root, f'{name}_haste{k}', [(x + r0 * math.cos(a), y + r0 * math.sin(a), z + 0.28 * s),
                                        (x + r1 * math.cos(a), y + r1 * math.sin(a), z + H)], 0.025 * s, M['metal'], segs=6)
    sphere(root, name + '_topo', 0.06 * s, (x, y, z + H + 0.03), m=M['metal'], seg=12)
    if not flag:
        return None
    fw, fh = 1.5 * s, 1.05 * s
    o = flag_mesh(root, name + '_bandeira', fw, fh, rr)
    o.location = (x + 0.05 * s, y, z + H - 0.06 * s)
    o.rotation_euler = (0, 0, -0.35)
    return o


def flag_mesh(root, name, w, h, rr, nx=24, ny=12):
    """Bandeira ondulada (malha em XZ, presa em x = 0, de z = 0 para baixo) com o desenho no proprio material."""
    bm = bmesh.new()
    V = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            a = TAU * (1.1 * u) + 0.6
            row.append(bm.verts.new((u * w - u * 0.05 * w, 0.12 * h * u ** 1.2 * math.sin(a), -v * h - 0.08 * h * u * u)))
        V.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    uv = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            lp[uv].uv = (co.x / (w * 0.95), 1 + co.z / h)
    o = bm_to_obj(bm, name, root, [flag_material()], angle=89)
    sm = o.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.02
    return o


def flag_material():
    """Verde com o losango amarelo e o circulo azul (sem estrelas nem texto), desenhados por UV."""
    key = 'br_bandeira'
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = mat(key, '#2f9a48', rough=0.75, var=0.0, bump=0.02, sheen=0.3)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    hsv = next(n for n in N if n.type == 'HUE_SAT')
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['UV'], sep.inputs[0])

    def node_math(op, a, b=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    du = node_math('ABSOLUTE', node_math('SUBTRACT', sep.outputs['X'], 0.5))
    dv = node_math('ABSOLUTE', node_math('SUBTRACT', sep.outputs['Y'], 0.5))
    rh = node_math('ADD', node_math('DIVIDE', du, 0.42), node_math('DIVIDE', dv, 0.4))
    rhombus = node_math('LESS_THAN', rh, 1.0)
    du2 = node_math('MULTIPLY', node_math('SUBTRACT', sep.outputs['X'], 0.5), 1.43)
    circ = node_math('LESS_THAN', node_math('ADD', node_math('MULTIPLY', du2, du2), node_math('MULTIPLY', dv, dv)), 0.045)
    green, yellow, blue = N.new('ShaderNodeRGB'), N.new('ShaderNodeRGB'), N.new('ShaderNodeRGB')
    green.outputs[0].default_value = lin('#2f9a48')
    yellow.outputs[0].default_value = lin('#f3c51e')
    blue.outputs[0].default_value = lin('#25479a')
    def mix(fac, a, b):
        n = N.new('ShaderNodeMix')
        n.data_type = 'RGBA'
        sock = lambda socks, nm: next(x for x in socks if x.name == nm and x.type in ('RGBA', 'VALUE') and (x.type == 'RGBA' or nm == 'Factor'))
        L.new(fac, sock(n.inputs, 'Factor'))
        L.new(a, sock(n.inputs, 'A'))
        L.new(b, sock(n.inputs, 'B'))
        return next(x for x in n.outputs if x.type == 'RGBA')
    c1 = mix(rhombus, green.outputs[0], yellow.outputs[0])
    c2 = mix(circ, c1, blue.outputs[0])
    L.new(c2, hsv.inputs['Color'])
    return m


def pombal(root, name, loc, s, M):
    """Pombal da Praca dos Tres Poderes: duas laminas curvas de concreto segurando a caixa dos pombos no alto."""
    x, y, z = loc
    sub = empty(root, name, loc)
    h = 1.9 * s
    for sx in (-1, 1):
        n = 10
        left, right = [], []
        for i in range(n + 1):
            t = i / n
            cx = sx * (0.12 * s + 0.1 * s * math.sin(t * math.pi))
            hw = 0.05 * s + 0.04 * s * t
            left.append((cx - hw, h * t))
            right.append((cx + hw, h * t))
        blade_xz(sub, f'{name}_perna{sx}', left + list(reversed(right)), 0.3 * s, M['conc_l'], bev=0.02)
    box(sub, name + '_caixa', (0.75 * s, 0.34 * s, 0.32 * s), (0, 0, h + 0.12 * s), m=M['conc_l'], bev=0.06)
    for k in range(4):
        box(sub, f'{name}_furo{k}', (0.09 * s, 0.02, 0.09 * s), (-0.24 * s + k * 0.16 * s, -0.17 * s, h + 0.12 * s), m=M['conc_s'], bev=0.015)
    cyl(sub, name + '_base', 0.42 * s, 0.06, (0, 0, 0.02), m=M['conc_d'], v=24, bev=0.02)
    return sub


def pombos(lote, M, loc, n, rr, ground, spread=0.6):
    """Bando de pombos ciscando (corpo, cabeca, rabo e pescoco brilhante), virados para todo lado."""
    x0, y0 = loc[0], loc[1]
    for k in range(n):
        x = x0 + rr.uniform(-spread, spread)
        y = y0 + rr.uniform(-spread, spread) * 0.7
        z = ground(x, y)
        a = rr.uniform(0, TAU)
        ca, sa = math.cos(a), math.sin(a)
        peck = rr.random() < 0.4
        lote.pebble(M['pombo'] if k % 3 else M['pombo_d'], (x, y, z + 0.055), 0.07, squash=0.75, rot=a, rr=rr, rough=0.05)
        hz = z + (0.07 if peck else 0.12)
        hx, hy = x + ca * 0.08, y + sa * 0.08
        lote.pebble(M['pombo_pesc'], (x + ca * 0.05, y + sa * 0.05, z + 0.09), 0.035, squash=1.0, rot=a, rr=rr, rough=0.05)
        lote.pebble(M['pombo_d'], (hx, hy, hz), 0.032, squash=0.95, rot=a, rr=rr, rough=0.05)
        lote.pebble(M['pombo_d'], (x - ca * 0.09, y - sa * 0.09, z + 0.06), 0.035, squash=0.35, rot=a, rr=rr, rough=0.05)


def jardineira(root, lote, name, loc, w, d, M, rr, ang=0.0):
    """Floreira de concreto com arbustos redondos."""
    x, y, z = loc
    o = box(root, name, (w, d, 0.2), (x, y, z + 0.1), rot=(0, 0, ang), m=M['conc'], bev=0.05)
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(max(2, int(w / 0.3))):
        t = (k + 0.5) / max(2, int(w / 0.3)) - 0.5
        px, py = x + ca * t * w * 0.9, y + sa * t * w * 0.9
        lote.pebble(M['arbusto'] if k % 2 else M['arbusto_l'], (px, py, z + 0.24), rr.uniform(0.13, 0.17), squash=0.8, rot=rr.uniform(0, TAU), rr=rr, rough=0.3)
    return o


def banco(root, name, loc, M, ang=0.0):
    """Banco de concreto curvo."""
    x, y, z = loc
    o = box(root, name, (0.6, 0.18, 0.1), (x, y, z + 0.14), rot=(0, 0, ang), m=M['conc_l'], bev=0.04)
    for sx in (-1, 1):
        box(root, f'{name}_pe{sx}', (0.08, 0.16, 0.12), (x + math.cos(ang) * sx * 0.22, y + math.sin(ang) * sx * 0.22, z + 0.05), rot=(0, 0, ang), m=M['conc_d'], bev=0.02)
    return o
