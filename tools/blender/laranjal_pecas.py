"""Pecas comuns do Laranjal (Ninguem Sobe a Rampa, so a chapa V; a chapa R continua com o Mensalinho).

Piada: as "candidaturas laranja" (candidato de fachada, so no papel). Tudo e laranja: o pomar de campanha com a
laranjeira cuja copa vira a plataforma de tiro, caixotes de feira cheios de laranja, a banquinha de campanha com a
bandeirinha da chapa, a turma de camisa amarela da selecao (gola verde em V, calcao azul, meiao branco e bone verde)
que arremessa laranjas, o Laranjao (caixote-catapulta de rodas de rodela de laranja) e a Candidatura Laranja (laranja
gigante sorridente de faixa no peito num palanque de caixotes). Nada de texto, numero, nome ou logo na arte.
Usado por tools/blender/torre_laranjal.py (familia 'arqueiros') e tools/blender/torre_laranjal_zb.py ('zarabatana').
As cores da chapa vem de tools/blender/chapa.py (CHAPA=V).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, emblema   # noqa: F401
from lote_brasilia import prism_xz, G   # noqa: F401
from mensalinho_pecas import (peito_chapa, emblema_into, bandeira_chapa, estandarte_chapa, oculos, bigode,   # noqa: F401
                              caixa_state, HEAD_K, IDLE, AIM, SHOOT)

HC = Vector((0.006, 0, 0.055))     # centro da cabeca no pivo do pescoco (lib.build_person)


# ---------------------------------------------------------------- materiais
def mat_casca(key, hexcol, rough=0.42, scale=95.0, bump=0.3, var=0.05, sheen=0.0):
    """Casca de laranja: o ruido do relevo bem fino (poros da casca) em vez do padrao do lib."""
    m = mat(key, hexcol, rough=rough, var=var, bump=bump, sheen=sheen)
    for n in m.node_tree.nodes:
        if n.type == 'TEX_NOISE':
            n.inputs['Scale'].default_value = scale
    return m


def mats_laranjal(P):
    P['laranja'] = mat_casca('casca_laranja', '#ff8a17')
    P['laranja_cl'] = mat_casca('casca_laranja_cl', '#ffa12e')
    P['laranja_esc'] = mat_casca('casca_laranja_esc', '#f2740c')
    P['polpa'] = mat('polpa_laranja', '#ffb02e', rough=0.28, var=0.03, bump=0.18)
    P['albedo'] = mat('albedo_laranja', '#fff1d4', rough=0.6, var=0.0, bump=0.02)
    P['suco'] = mat('suco_laranja', '#ffa01a', rough=0.08, var=0.0, bump=0.0)
    P['calice'] = mat('calice_laranja', '#4d7a28', rough=0.7, var=0.04, bump=0.1)
    P['folha'] = mat('folha_laranjeira', '#2f8a3c', rough=0.42, var=0.1, bump=0.06, sheen=0.2)
    P['folha_cl'] = mat('folha_laranjeira_cl', '#58b24a', rough=0.45, var=0.1, bump=0.06)
    P['copa'] = mat('copa_laranjeira', '#3b9442', rough=0.72, var=0.08, bump=0.35, sheen=0.3)
    P['copa_cl'] = mat('copa_laranjeira_cl', '#5cb04a', rough=0.72, var=0.08, bump=0.35, sheen=0.3)
    P['copa_esc'] = mat('copa_laranjeira_esc', '#2b7636', rough=0.78, var=0.06, bump=0.3)
    P['casca'] = mat('casca_arvore', '#80583a', rough=0.85, var=0.08, bump=0.45)
    P['casca_esc'] = mat('casca_arvore_esc', '#5f4029', rough=0.85, var=0.06, bump=0.4)
    P['terra'] = mat('terra_canteiro', '#6e4a32', rough=0.95, var=0.06, bump=0.4)
    P['meiofio'] = mat('meiofio_bsb', '#e9e5da', rough=0.86, var=0.03, bump=0.12)
    P['caixote'] = mat('caixote_pinus', '#e4b673', rough=0.75, var=0.1, bump=0.25)
    P['caixote_esc'] = mat('caixote_pinus_esc', '#c18f52', rough=0.75, var=0.08, bump=0.25)
    P['caixote_int'] = mat('caixote_dentro', '#6b4628', rough=0.9, var=0.0, bump=0.1)
    P['deck'] = mat('deck_laranjal', '#c9a77f', rough=0.75, var=0.05, bump=0.2, stripes=(11.0, '#d2b48c', '#bb9a72'))
    P['madeira'] = mat('madeira_banca', '#9a6337', rough=0.72, var=0.08, bump=0.25)
    P['madeira_cl'] = mat('madeira_banca_cl', '#c48c56', rough=0.72, var=0.08, bump=0.25)
    P['chapa'] = cor('pri')
    P['chapa2'] = cor('sec')
    P['chapa3'] = cor('ter')
    P['toldo'] = mat('toldo_laranjal_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(14.0, PAL['sec'], PAL['pri']), sheen=0.4)
    P['camisa'] = cor('camisa')
    P['gola'] = cor('gola')
    P['calca'] = cor('calca')
    P['bone'] = cor('bone')
    P['meia'] = mat('meiao_branco', '#f4f2ec', rough=0.85, var=0.0, bump=0.05, sheen=0.3)
    P['tenis'] = mat('tenis_branco', '#f4f4f0', rough=0.5, var=0.0, bump=0.02)
    P['rede'] = cor('pri', rough=0.7)
    P['lamp_q'] = glow_mat('lampada_laranjal', '#ffcf6a', 1.6, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['lente'] = mat('oculos_aro', '#2a2a2e', rough=0.4, var=0.0, bump=0.0)
    P['oculos_esc'] = mat('oculos_escuros', '#1d1d22', rough=0.15, var=0.0, bump=0.0)
    P['cabelo_c'] = mat('cabelo_castanho', '#5a3a22', rough=0.7, var=0.03, bump=0.25)
    P['cabelo_p'] = mat('cabelo_preto', '#2b2220', rough=0.7, var=0.03, bump=0.25)
    P['cabelo_g'] = mat('cabelo_grisalho', '#8f8a84', rough=0.7, var=0.03, bump=0.25)
    P['bochecha'] = mat('bochecha_laranja', '#ff5a4a', rough=0.6, var=0.0, bump=0.0)
    P['olho_br'] = mat('olho_brilho', '#ffffff', rough=0.2, var=0.0, bump=0.0)
    P['boca'] = mat('boca_escura', '#4a1610', rough=0.5, var=0.0, bump=0.0)
    P['lingua'] = mat('lingua_laranja', '#ff6f6a', rough=0.5, var=0.0, bump=0.0)
    P['dente'] = mat('dente', '#fffaf0', rough=0.35, var=0.0, bump=0.0)
    P['luva'] = mat('luva_branca', '#fbf8f0', rough=0.6, var=0.0, bump=0.03, sheen=0.3)
    P['semente'] = mat('semente_laranja', '#f3e3b4', rough=0.5, var=0.04, bump=0.02)
    P['canudo'] = mat('canudo_branco', '#f7f5ee', rough=0.25, var=0.0, bump=0.0)
    P['concreto'] = mat('concreto_bsb', '#efebe2', rough=0.86, var=0.03, bump=0.1)
    P['_emblem'] = 'coin'
    return P


# ---------------------------------------------------------------- laranja, folha, rodela
def folha(root, P, name, L, loc=(0, 0, 0), rot=(0, 0, 0), m=None):
    """Folha de laranjeira: amendoa achatada e brilhante."""
    return sphere(root, name, L / 2, loc, scale=(1.0, 0.44, 0.12), m=m or P['folha'], seg=10, rot=rot)


def laranja(root, P, name, r, loc=(0, 0, 0), m=None, folhas=0, seg=14, front=False, parent=None, rot=(0, 0, 0)):
    """Laranja levemente achatada com o calice verde no topo; `folhas` folhinhas presas no cabinho. Os detalhes vao
    pendurados na esfera (mexer na esfera leva tudo)."""
    o = sphere(root, name, r, loc, scale=(1, 1, 0.94), m=m or P['laranja'], seg=seg, front=front, rot=rot)
    if parent is not None:
        o.parent = parent
    c = sphere(root, name + '_calice', r * 0.2, (0, 0, r * 0.9), scale=(1, 1, 0.45), m=P['calice'], seg=8, front=front)
    c.parent = o
    for k in range(folhas):
        a = 0.6 + k * 2.4
        f = folha(root, P, f'{name}_folha{k}', r * 1.25, (r * 0.42 * math.cos(a), r * 0.42 * math.sin(a), r * 0.98),
                  rot=(0.0, -0.45, a), m=P['folha'] if k == 0 else P['folha_cl'])
        if front:
            f['front'] = 1
        f.parent = o
    return o


def fatia(root, P, name, r, th=0.03, gomos=8):
    """Rodela de laranja (corte transversal) com a face para +Z: casca, albedo branco, gomos de polpa e o miolo.
    Devolve o pivo (empty) no centro."""
    piv = empty(root, name)
    kids(piv, cyl(root, name + '_casca', r, th, (0, 0, 0), m=P['laranja'], v=28, bev=th * 0.3),
         cyl(root, name + '_albedo', r * 0.9, th * 1.08, (0, 0, 0), m=P['albedo'], v=28, bev=th * 0.2),
         cyl(root, name + '_miolo', r * 0.11, th * 1.3, (0, 0, 0), m=P['albedo'], v=12, bev=th * 0.15))
    bm = bmesh.new()
    gap = 0.11
    rin, rout = r * 0.16, r * 0.8
    z0, z1 = th * 0.5, th * 0.62
    for k in range(gomos):
        a0 = TAU * k / gomos + gap / 2
        a1 = TAU * (k + 1) / gomos - gap / 2
        ring = [(rin * math.cos((a0 + a1) / 2), rin * math.sin((a0 + a1) / 2))]
        for j in range(7):
            a = a0 + (a1 - a0) * j / 6
            ring.append((rout * math.cos(a), rout * math.sin(a)))
        lo = [bm.verts.new((x, y, z0)) for x, y in ring]
        hi = [bm.verts.new((x, y, z1)) for x, y in ring]
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        n = len(ring)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    kids(piv, bm_to_obj(bm, name + '_gomos', root, [P['polpa']], bev=0.004, angle=30))
    # o outro lado tambem (as rodas giram e aparecem dos dois lados)
    g2 = bpy.data.objects[name + '_gomos'].copy()
    g2.data = bpy.data.objects[name + '_gomos'].data
    root.users_collection[0].objects.link(g2)
    g2.parent = piv
    g2.rotation_euler = (math.pi, 0, 0)
    g2['set'] = root['set']
    return piv


# ---------------------------------------------------------------- caixote de feira
def caixote(root, P, name, s=1.0, cheio=True, seed=0, adesivo=False, monte=True):
    """Caixote de feira de pinus (ripas com fresta, cabeceiras com alca vazada) cheio de laranjas. Origem no centro
    do fundo, comprimento em X. Devolve o pivo."""
    W, D, H = 0.26 * s, 0.18 * s, 0.13 * s
    rr = random.Random(seed)
    piv = empty(root, name)
    kids(piv, box(root, name + '_fundo', (W, D, 0.014 * s), (0, 0, 0.007 * s), m=P['caixote_esc'], bev=0.003 * s),
         box(root, name + '_dentro', (W - 0.03 * s, D - 0.026 * s, H * 0.85), (0, 0, H * 0.45), m=P['caixote_int'], bev=0.0))
    for sx in (-1, 1):
        kids(piv, box(root, f'{name}_cab{sx}', (0.018 * s, D, H), (sx * (W / 2 - 0.009 * s), 0, H / 2), m=P['caixote'], bev=0.004 * s),
             box(root, f'{name}_alca{sx}', (0.022 * s, D * 0.42, 0.026 * s), (sx * (W / 2 - 0.007 * s), 0, H * 0.76), m=P['caixote_int'], bev=0.008 * s))
    for sy in (-1, 1):
        for j, zz in enumerate((H * 0.2, H * 0.7)):
            kids(piv, box(root, f'{name}_ripa{sy}{j}', (W + 0.004 * s, 0.013 * s, H * 0.34), (0, sy * (D / 2 - 0.0065 * s), zz),
                          m=P['caixote'] if j else P['caixote_esc'], bev=0.003 * s))
    if adesivo:
        b = box(root, name + '_adesivo', (W * 0.42, 0.004 * s, H * 0.3), (0, -D / 2 - 0.0015 * s, H * 0.7), m=P['chapa'], bev=0.0015 * s)
        b.parent = piv
        for o in emblema(root, name + '_adesivoEm', W * 0.4, H * 0.3, depth=0.003 * s):
            if o.parent == root:
                o.parent = b
                o.location = (0, -0.0035 * s, 0)
    if cheio:
        nx, ny = 3, 2
        ro = min((W - 0.03 * s) / (2 * nx), (D - 0.026 * s) / (2 * ny)) * 1.02
        mats = [P['laranja'], P['laranja_cl'], P['laranja_esc']]
        for i in range(nx):
            for j in range(ny):
                cx = -W / 2 + 0.015 * s + (i + 0.5) * (W - 0.03 * s) / nx + rr.uniform(-0.004, 0.004) * s
                cy = -D / 2 + 0.013 * s + (j + 0.5) * (D - 0.026 * s) / ny + rr.uniform(-0.004, 0.004) * s
                laranja(root, P, f'{name}_lar{i}{j}', ro, (cx, cy, H - ro * 0.45 + rr.uniform(0, ro * 0.25)), m=rr.choice(mats), seg=12,
                        parent=piv, rot=(0, 0, rr.uniform(0, TAU)))
        if monte:
            for i in range(2):
                cx = -W / 2 + 0.015 * s + (i + 1) * (W - 0.03 * s) / nx
                laranja(root, P, f'{name}_larM{i}', ro, (cx, rr.uniform(-0.01, 0.01) * s, H + ro * 0.5), m=rr.choice(mats), seg=12, parent=piv,
                        folhas=1 if i == 0 else 0, rot=(0, 0, rr.uniform(0, TAU)))
    return piv


def pilha_caixotes(root, P, tag, spec, seed=1):
    """Caixotes no chao: spec = [(x, y, z, rz, s, cheio, adesivo), ...]."""
    out = []
    for k, (x, y, z, rz, s, cheio, ad) in enumerate(spec):
        c = caixote(root, P, f'{tag}{k}', s=s, cheio=cheio, seed=seed + k, adesivo=ad)
        c.location = (x, y, z)
        c.rotation_euler = (0, 0, rz)
        out.append(c)
    return out


def laranjas_chao(root, P, tag, pts, seed=3):
    """Laranjas soltas no chao (caidas da arvore)."""
    rr = random.Random(seed)
    for k, (x, y, z, r) in enumerate(pts):
        laranja(root, P, f'{tag}{k}', r, (x, y, z + r * 0.9), m=rr.choice([P['laranja'], P['laranja_cl']]), seg=12, rot=(rr.uniform(-0.6, 0.6), 0.3, rr.uniform(0, TAU)))


# ---------------------------------------------------------------- laranjeira com a copa-plataforma
def laranjeira(root, P, tag, fz, R, seed=1, frutos=0.6, trunk_r=0.1, galhos_lat=0, z0=G):
    """Laranjeira robusta: canteiro redondo, tronco grosso com raizes, galhos abrindo para a copa; a copa e uma tigela de
    folhagem em tufos cheia de laranjas e, em cima, um deck redondo de tabuas (os postos ficam nele) cercado por uma sebe
    baixa de folhas. A sebe da frente vai na camada da frente."""
    rr = random.Random(seed)
    depth = 0.46 + 0.2 * (R - 0.6)
    zb = fz - depth
    # canteiro de concreto com terra e o pe do tronco
    cyl(root, tag + '_canteiro', 0.27, 0.055, (0, 0, z0 + 0.0275), m=P['meiofio'], v=36, bev=0.02)
    cyl(root, tag + '_terra', 0.235, 0.02, (0, 0, z0 + 0.05), m=P['terra'], v=36, bev=0.006)
    zt = zb + 0.1
    hgt = zt - z0
    pts = [(0, 0, z0 + 0.03), (0.025, 0.0, z0 + hgt * 0.3), (-0.02, 0.01, z0 + hgt * 0.65), (0.0, 0.0, zt)]
    tube(root, tag + '_tronco', pts, trunk_r, P['casca'], segs=14,
         rfun=lambda t: trunk_r * (1.0 - 0.18 * t) + trunk_r * 0.55 * max(0.0, 0.14 - t) / 0.14)
    for k in range(5):
        a = TAU * k / 5 + 0.4
        tube(root, f'{tag}_raiz{k}', [(0.05 * math.cos(a), 0.05 * math.sin(a), z0 + 0.1), (0.17 * math.cos(a), 0.17 * math.sin(a), z0 + 0.045)],
             trunk_r * 0.45, P['casca'], segs=8, rfun=lambda t: trunk_r * (0.5 - 0.3 * t))
    # galhos principais subindo para dentro da copa
    for k in range(4):
        a = TAU * k / 4 + 0.8
        r1 = R * 0.42
        tube(root, f'{tag}_galho{k}', [(0, 0, zb - 0.06), (r1 * 0.45 * math.cos(a), r1 * 0.45 * math.sin(a), zb + 0.06), (r1 * math.cos(a), r1 * math.sin(a), zb + 0.2)],
             trunk_r * 0.55, P['casca'], segs=8, rfun=lambda t: trunk_r * (0.62 - 0.3 * t))
    # galhos laterais com tufo e frutas (arvores grandes: enche o tronco comprido)
    for k in range(galhos_lat):
        sx = -1 if k % 2 == 0 else 1
        zz = z0 + hgt * (0.5 + 0.12 * (k // 2))
        tip = (0.3 * sx, -0.12, zz + 0.12)
        tube(root, f'{tag}_galhoLat{k}', [(0.0, 0.0, zz), (0.16 * sx, -0.05, zz + 0.07), tip], trunk_r * 0.4, P['casca'], segs=8,
             rfun=lambda t: trunk_r * (0.42 - 0.22 * t))
        tc = (tip[0] + 0.04 * sx, tip[1] - 0.02, tip[2] + 0.06)
        sphere(root, f'{tag}_tufoLat{k}', 0.12, tc, scale=(1.15, 1.0, 0.8), m=P['copa'], seg=16)
        sphere(root, f'{tag}_tufoLatB{k}', 0.08, (tc[0] - 0.08 * sx, tc[1] + 0.03, tc[2] + 0.04), scale=(1, 1, 0.85), m=P['copa_cl'], seg=14)
        laranja(root, P, f'{tag}_frutoLat{k}a', 0.048, (tc[0] + 0.05 * sx, tc[1] - 0.08, tc[2] - 0.04), seg=12)
        laranja(root, P, f'{tag}_frutoLat{k}b', 0.044, (tc[0] - 0.05 * sx, tc[1] - 0.08, tc[2] - 0.06), m=P['laranja_cl'], seg=12)
    # tigela de folhagem por baixo do deck
    prof = []
    for k in range(10):
        t = k / 9
        z = zb + (fz - 0.03 - zb) * t
        r = 0.16 + (R - 0.02 - 0.16) * math.sin(t * math.pi / 2) ** 0.75
        prof.append((z, r, r))
    lathe(root, tag + '_copa', prof, P['copa_esc'], segs=40, lv=1)

    def r_at(z):
        t = max(0.0, min(1.0, (z - zb) / (fz - 0.03 - zb)))
        return 0.16 + (R - 0.02 - 0.16) * math.sin(t * math.pi / 2) ** 0.75
    kc = 0.85 + 0.3 * R
    RMAX = 0.945          # nada passa da largura do lote (o enquadramento das torres e o mesmo do Mensalinho)
    rows = [(0.06, 0.145), (0.32, 0.13), (0.58, 0.115), (0.84, 0.095)]
    mats = [P['copa'], P['copa_cl'], P['copa'], P['copa_esc']]
    nfr = 0
    for ri, (td, rc) in enumerate(rows):
        rc *= kc
        z = fz - 0.03 - td * (fz - 0.03 - zb)
        rad = r_at(z) - rc * 0.3
        n = max(6, int(TAU * rad / (rc * 1.3)))
        off = rr.uniform(0, TAU)
        for k in range(n):
            a = off + TAU * k / n
            if ri > 0 and math.sin(a) > 0.55:      # atras e por baixo: a camera nao ve
                continue
            rk = rc * rr.uniform(0.88, 1.1)
            rd = min(rad, RMAX - rk)
            cx, cy = rd * math.cos(a), rd * math.sin(a)
            cz = z + rr.uniform(-0.02, 0.02)
            # a primeira fileira da frente e a borda da plataforma: vai na camada da frente (nada a encobre)
            fr = ri == 0 and math.sin(a) < -0.3
            mk = (P['copa'] if k % 2 else P['copa_cl']) if ri == 0 else mats[(k + ri) % 4]     # na borda nada de tufo escuro (parece buraco)
            sphere(root, f'{tag}_tufo{ri}_{k}', rk, (cx, cy, cz), scale=(1.0, 1.0, 0.82), m=mk, seg=16, rot=(0, 0, a), front=fr)
            if rr.random() < frutos + (0.12 if ri == 0 else 0.0) and math.sin(a) < 0.45:
                d = Vector((math.cos(a), math.sin(a), -0.35 - 0.25 * ri)).normalized()
                ro = rr.uniform(0.048, 0.06) * (0.9 + 0.2 * R)
                p = Vector((cx, cy, cz)) + d * (rk * 0.86)
                if p.xy.length + ro > RMAX + 0.01:
                    continue
                laranja(root, P, f'{tag}_fruto{nfr}', ro, tuple(p), m=rr.choice([P['laranja'], P['laranja_cl'], P['laranja_esc']]), seg=12,
                        folhas=1 if rr.random() < 0.3 else 0, rot=(rr.uniform(-0.4, 0.4), rr.uniform(-0.4, 0.4), rr.uniform(0, TAU)), front=fr)
                nfr += 1
    # deck de tabuas e a sebe em volta
    cyl(root, tag + '_deck', R - 0.06, 0.05, (0, 0, fz - 0.025), m=P['deck'], v=56, bev=0.01)
    torus(root, tag + '_deckAro', (0, 0, fz - 0.012), R - 0.07, 0.014, P['madeira'], n=56, segs=6)
    n = int(TAU * R / 0.11)
    off = rr.uniform(0, TAU)
    for k in range(n):
        a = off + TAU * k / n
        if math.sin(a) < 0.05:
            continue        # na metade da frente a borda e a propria fileira de tufos (a sebe encostaria na camada da frente)
        fr = False
        back = max(0.0, math.sin(a))
        rh = (0.074 + 0.014 * rr.random()) * (1.0 + 0.55 * back)      # atras a sebe cresce: copa de fundo para a turma
        x, y = (R - 0.035 - 0.03 * back) * math.cos(a), (R - 0.035 - 0.03 * back) * math.sin(a)
        sphere(root, f'{tag}_sebe{k}', rh, (x, y, fz + 0.004 + 0.05 * back), scale=(1.0, 1.0, 0.82), m=mats[k % 3], seg=14, front=fr, rot=(0, 0, a))
        if rr.random() < frutos * 0.55 and math.sin(a) < 0.7:
            ro = rr.uniform(0.04, 0.05)
            d = Vector((math.cos(a), math.sin(a), 0.55)).normalized()
            p = Vector((x, y, fz + 0.004 + 0.05 * back)) + d * rh * 0.82
            laranja(root, P, f'{tag}_frutoSebe{k}', ro, tuple(p), m=rr.choice([P['laranja'], P['laranja_cl']]), seg=12, front=fr,
                    folhas=1 if rr.random() < 0.4 else 0, rot=(0, 0, rr.uniform(0, TAU)))
    return zb


def lanterna_poste(root, P, tag, x, y, z, h=0.18):
    """Postinho de madeira com lampiao redondo de luz quente (fica na beira do deck). Devolve a posicao da luz."""
    tube(root, tag + '_poste', [(x, y, z), (x, y, z + h * 0.6), (x * 1.04, y * 1.04, z + h)], 0.014, P['madeira'], segs=8)
    c = (x * 1.04, y * 1.04, z + h + 0.042)
    sphere(root, tag + '_globo', 0.046, c, m=P['lamp_q'], seg=16)
    cyl(root, tag + '_chapeu', 0.036, 0.02, (c[0], c[1], c[2] + 0.044), r2=0.012, m=P['chapa'], v=14, bev=0.004)
    return c


def bandeira_pano(root, P, tag, x, y, z, size=0.42, h_pole=0.9):
    """Bandeira da chapa num mastro de madeira com uma laranjinha na ponta: pano animado (verde, losango amarelo e
    circulo azul na face da frente; sem faixa nem letras)."""
    tube(root, tag + '_mastro', [(x, y, z), (x, y, z + h_pole)], 0.018, P['madeira_cl'], segs=8)
    laranja(root, P, tag + '_topo', 0.036, (x, y, z + h_pole + 0.03), seg=12, folhas=1)
    hh = size * 0.62
    o = cloth_grid(root, tag + '_pano', size, hh, 16, 7, [P['chapa'], P['chapa2'], P['chapa3']], thick=0.012)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    emblema_into(bm, size * 0.52, -hh / 2, size * 0.84, hh * 0.86, y=-0.012)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o.location = (x + 0.02, y, z + h_pole - 0.04)
    register_cloth(o, flag_wave(size, amp=0.06, cycles=1, waves=1.1))
    return o


def mudinha(root, P, tag, loc, s=1.0, seed=9):
    """Mudinha de laranjeira num vaso redondo de concreto, com tres laranjinhas."""
    rr = random.Random(seed)
    x, y, z = loc
    cyl(root, tag + '_vaso', 0.12 * s, 0.13 * s, (x, y, z + 0.065 * s), r2=0.1 * s, m=P['meiofio'], v=24, bev=0.02 * s)
    cyl(root, tag + '_terra', 0.105 * s, 0.02 * s, (x, y, z + 0.125 * s), m=P['terra'], v=20, bev=0.005)
    top = (x, y, z + 0.36 * s)
    tube(root, tag + '_tronco', [(x, y, z + 0.12 * s), (x + 0.015 * s, y, z + 0.24 * s), top], 0.022 * s, P['casca'], segs=8,
         rfun=lambda t: (0.026 - 0.01 * t) * s)
    c = (x, y, top[2] + 0.1 * s)
    sphere(root, tag + '_copa', 0.15 * s, c, scale=(1, 1, 0.85), m=P['copa'], seg=18)
    sphere(root, tag + '_copaB', 0.1 * s, (c[0] - 0.08 * s, c[1] - 0.04 * s, c[2] + 0.05 * s), scale=(1, 1, 0.85), m=P['copa_cl'], seg=14)
    for k, a in enumerate((-2.0, -1.0, -0.2)):
        laranja(root, P, f'{tag}_fruto{k}', 0.036 * s, (c[0] + 0.14 * s * math.cos(a), c[1] + 0.12 * s * math.sin(a), c[2] - 0.03 * s + 0.03 * s * k),
                m=P['laranja'] if k != 1 else P['laranja_cl'], seg=12, rot=(0, 0, rr.uniform(0, TAU)))


# ---------------------------------------------------------------- banquinha de campanha
def banca(root, P, tag, loc, w=0.42, d=0.2, h=0.25, lamp=True, flag=True, flag_h=0.32):
    """Banquinha de campanha de madeira (frente verde com o emblema da chapa), piramide de laranjas no balcao, toldo
    listrado verde e amarelo com babado, lampada pendurada e a bandeirinha da chapa no canto. Frente para -Y; loc =
    (x, y do centro, z do chao). Devolve a posicao da lampada (ou None)."""
    x, y, z = loc
    yf = y - d / 2
    box(root, tag + '_banca', (w, d, h), (x, y, z + h / 2), m=P['madeira'], bev=0.012)
    box(root, tag + '_painel', (w - 0.05, 0.012, h - 0.07), (x, yf - 0.004, z + h / 2 - 0.012), m=P['chapa'], bev=0.004)
    emblema(root, tag + '_emblema', (w - 0.05) * 0.8, (h - 0.07) * 0.95, loc=(x, yf - 0.012, z + h / 2 - 0.012), depth=0.006)
    box(root, tag + '_tampo', (w + 0.05, d + 0.05, 0.03), (x, y, z + h + 0.015), m=P['madeira_cl'], bev=0.008)
    zt = z + h + 0.03
    ro = 0.036
    rr = random.Random(5)
    k = 0
    for layer, (nx, ny) in enumerate(((4, 2), (3, 1))):
        for i in range(nx):
            for j in range(ny):
                cx = x - (nx - 1) * ro + i * 2 * ro
                cy = y - 0.01 - (ny - 1) * ro + j * 2 * ro
                laranja(root, P, f'{tag}_lar{k}', ro, (cx, cy, zt + ro * 0.9 + layer * ro * 1.5), m=rr.choice([P['laranja'], P['laranja_cl'], P['laranja_esc']]),
                        seg=12, folhas=1 if k == 5 else 0, rot=(0, 0, rr.uniform(0, TAU)))
                k += 1
    # postes e toldo
    hp = 0.34
    for sx in (-1, 1):
        tube(root, f'{tag}_poste{sx}', [(x + sx * (w / 2 + 0.005), y + d / 2 - 0.015, zt - 0.02), (x + sx * (w / 2 + 0.005), y + d / 2 - 0.015, zt + hp)], 0.011,
             P['madeira_cl'], segs=8)
    zw = zt + hp
    box(root, tag + '_toldo', (w + 0.08, d + 0.03, 0.018), (x, y - 0.025, zw), rot=(math.radians(20), 0, 0), m=P['toldo'], bev=0.005)
    nb = 7
    yb = y - 0.025 - (d + 0.03) / 2 * math.cos(math.radians(20)) - 0.004
    zbb = zw - (d + 0.03) / 2 * math.sin(math.radians(20)) - 0.014
    for i in range(nb):
        xx = x - (w + 0.08) / 2 + (w + 0.08) * (i + 0.5) / nb
        cyl(root, f'{tag}_babado{i}', (w + 0.08) / (2 * nb), 0.012, (xx, yb, zbb), rot=(math.pi / 2, 0, 0), m=P['chapa'] if i % 2 == 0 else P['chapa2'], v=12, bev=0.002)
    lp = None
    if lamp:
        lx = x - w / 2 + 0.06
        tube(root, tag + '_fio', [(lx, y - 0.01, zw - 0.02), (lx, y - 0.02, zw - 0.09)], 0.004, P['dark'], segs=5)
        sphere(root, tag + '_lampada', 0.03, (lx, y - 0.02, zw - 0.12), m=P['lamp_q'], seg=14)
        lp = (lx, y - 0.02, zw - 0.12)
    if flag:
        bandeira_chapa(root, P, tag + '_bandeira', (x + w / 2 + 0.03, y - d / 2 + 0.03, zt - 0.03), h=flag_h, w=0.18, fh=0.12)
    return lp


# ---------------------------------------------------------------- a turma (camisa amarela, gola verde, calcao azul)
def bone(root, pr, tag, m):
    """Bone de torcedor: copa justa na cabeca inclinada para tras (a frente fica acima das sobrancelhas), aba curta
    para a frente e o botao amarelo do topo (tudo no pivo da cabeca)."""
    hd = pr['head']
    c = lathe(root, tag + '_bone', [(0.0, 0.072, 0.07), (0.022, 0.069, 0.067), (0.042, 0.058, 0.056), (0.058, 0.036, 0.035), (0.066, 0.0, 0.0)],
              m, segs=18, lv=2, caps=False, solid=0.008)
    c.parent = hd
    c.location = HC + Vector((-0.004, 0, 0.018))
    c.rotation_euler = (0, -0.28, 0)
    o = cyl(root, tag + '_aba', 0.058, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = hd
    o.location = HC + Vector((0.074, 0, 0.044))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.16, 0)
    b = sphere(root, tag + '_boneBotao', 0.01, HC + Vector((-0.026, 0, 0.088)), m=cor('sec', rough=0.45), seg=10)
    b.parent = hd
    return c


def cabelo_curto(root, pr, tag, m):
    """Cabelo curto aparecendo por baixo do bone: nuca e costeletas."""
    hd = pr['head']
    o = blob(root, f'{tag}_nuca', 0.042, HC + Vector((-0.034, 0, 0.006)), (0.85, 1.38, 0.95), m)
    o.parent = hd
    for s, yy in enumerate((-0.058, 0.058)):
        o = blob(root, f'{tag}_costeleta{s}', 0.019, HC + Vector((-0.002, yy, 0.014)), (1.1, 0.55, 1.25), m)
        o.parent = hd


def rabo_cavalo(root, pr, tag, m):
    """Rabo de cavalo saindo por tras do bone."""
    hd = pr['head']
    o = blob(root, f'{tag}_rabo', 0.026, HC + Vector((-0.078, 0, 0.026)), (1.0, 0.9, 1.0), m)
    o.parent = hd
    t = tube(root, f'{tag}_raboPonta', [HC + Vector((-0.083, 0, 0.028)), HC + Vector((-0.106, 0, -0.008)), HC + Vector((-0.1, 0, -0.055))], 0.02, m, segs=8,
             rfun=lambda t: 0.022 * (1 - t) + 0.006)
    t.parent = hd


def saco_laranjas(root, P, tag, side='L'):
    """Saquinho de rede verde com quatro laranjas na mao (o estoque do arremessador)."""
    piv = empty(root, f'{tag}_saco')
    rr = random.Random(2)
    for k, (dx, dy, dz) in enumerate(((0.022, 0.0, -0.06), (-0.022, 0.0, -0.06), (0.0, 0.022, -0.035), (0.0, -0.02, -0.098))):
        laranja(root, P, f'{tag}_sacoLar{k}', 0.03, (dx, dy, dz), m=rr.choice([P['laranja'], P['laranja_cl']]), seg=12, parent=piv, rot=(0, 0, rr.uniform(0, TAU)))
    for k, zz in enumerate((-0.04, -0.07, -0.1)):
        t = torus(root, f'{tag}_sacoRede{k}', (0, 0, zz), 0.05 - 0.008 * abs(k - 1), 0.0035, P['rede'], n=16, segs=4)
        t.parent = piv
    kids(piv, blob(root, f'{tag}_sacoNo', 0.014, (0, 0, -0.008), (1, 1, 1.3), P['rede']))
    for k in range(4):
        a = TAU * k / 4 + 0.4
        t = tube(root, f'{tag}_sacoFio{k}', [(0, 0, -0.01), (0.045 * math.cos(a), 0.045 * math.sin(a), -0.06), (0.012 * math.cos(a), 0.012 * math.sin(a), -0.13)],
                 0.003, P['rede'], segs=4)
        t.parent = piv
    return piv


SKINS = {'a1': '#d9a578', 'a2': '#a8714a', 'a3': '#e3b48c', 'a3b': '#8c5a3c', 'op': '#c98d5e', 'za': '#d7a27a', 'zb': '#b37a52'}


def build_apoiador(P, root, variant, tag=None, municao=True):
    """Apoiador da chapa V (~0.6 BU, cabecao): camisa amarela da selecao com gola verde em V, calcao azul, meiao e tenis
    brancos e bone verde; laranja na mao direita e saquinho de laranjas na esquerda.
    a1: castanho; a2: cabelo preto, oculos e calca comprida; a3: grisalho de bigode; a3b: rabo de cavalo e brincos de
    ouro; op: suspensorio verde (opera o Laranjao); za/zb: os do canudo (Candidatura Laranja)."""
    tag = tag or root['set']
    hair = {'a1': P['cabelo_c'], 'a2': P['cabelo_p'], 'a3': P['cabelo_g'], 'a3b': P['cabelo_p'], 'op': P['cabelo_c'], 'za': P['cabelo_p'],
            'zb': P['cabelo_g']}[variant]
    skin = mat('pele_lj_' + variant, SKINS[variant], rough=0.7, var=0.05, bump=0.02)
    shorts = variant != 'a2'
    sp = dict(skin=skin, tunic=P['camisa'], sleeve=P['camisa'], bracer=skin, skirt_m=P['calca'], pants=skin if shorts else P['calca'],
              boot_m=P['tenis'], boot_cuff=P['meia'] if shorts else P['calca'], belt=None, head='hair' if variant == 'a3b' else 'bald',
              hair_m=hair, bare_hands=True)
    pr = build_person(P, root, tag, sp)
    pr['head'].scale = (HEAD_K, HEAD_K, HEAD_K)
    sa = bpy.data.objects.get(f'{tag}_saia')
    if sa and shorts:
        sa.scale = (0.84, 0.84, 0.72)       # calcao curto: aparecem o joelho e o meiao
        sa.location = (0, 0, 0.32 * (1 - 0.72))
    elif sa:
        sa.scale = (0.88, 0.88, 1.0)        # calca, nao tunica
    # barra da camisa por cima do calcao
    o = lathe(root, f'{tag}_barraCamisa', [(0.27, 0.083, 0.099), (0.3, 0.081, 0.097)], P['camisa'], segs=12, lv=1)
    o.parent = pr['body']
    if shorts:
        for s, yy in enumerate((-0.046, 0.046)):        # meiao subindo pela canela
            o = tube(root, f'{tag}_meiao{s}', [(0.002, yy, 0.07), (0.002, yy * 0.95, 0.115)], 0.035, P['meia'], segs=10)
            o.parent = pr['body']
    peito_chapa(root, P, pr, tag)           # decote em V com debrum verde
    bone(root, pr, tag, P['bone'])
    if variant != 'a3b':
        cabelo_curto(root, pr, tag, hair)
    if variant == 'a3b':
        rabo_cavalo(root, pr, tag, hair)
        hd = pr['head']
        for s, yy in enumerate((-0.066, 0.066)):
            b = sphere(root, f'{tag}_brinco{s}', 0.009, Vector((0.006, yy, 0.03)), m=P['gold'], seg=8)
            b.parent = hd
    if variant == 'op':
        for s, yy in enumerate((-0.05, 0.05)):
            o = tube(root, f'{tag}_suspensorio{s}', [(0.085, yy, 0.3), (0.09, yy * 1.1, 0.4), (0.05, yy * 1.3, 0.462), (-0.04, yy * 1.2, 0.46), (-0.085, yy * 0.8, 0.38),
                                                    (-0.085, yy * 0.6, 0.3)], 0.009, P['chapa'], segs=6)
            o.parent = pr['body']
    if variant == 'a2':
        oculos(root, P, pr, tag)
    if variant in ('a3', 'zb'):
        bigode(root, P, pr, tag, hair)
    if variant == 'za':
        hd = pr['head']
        for s, yy in enumerate((-0.026, 0.026)):
            o = blob(root, f'{tag}_lente{s}', 0.021, HC + Vector((0.064, yy, 0.012)), (0.45, 1.0, 0.8), P['oculos_esc'])
            o.parent = hd
        o = tube(root, f'{tag}_oculosPonte', [HC + Vector((0.07, -0.008, 0.016)), HC + Vector((0.072, 0, 0.018)), HC + Vector((0.07, 0.008, 0.016))], 0.004,
                 P['oculos_esc'], segs=5)
        o.parent = hd
    if municao and variant not in ('op', 'za', 'zb'):
        lr = laranja(root, P, f'{tag}_laranjaR', 0.044, (0, 0, 0.03), seg=14, folhas=1)
        hold(pr, 'R', lr)
        hold(pr, 'L', saco_laranjas(root, P, tag))
    pr['variant'] = variant
    return pr


def apoiador_state(mode, f, tag):
    """Mesmo arremesso por cima do ombro do Mensalinho (mesmos quadros e tempos): so troca o envelope pela laranja."""
    st = caixa_state(mode, f, tag)
    if 'hide' in st:
        st['hide'] = (f'{tag}_laranjaR',)
    return st


def pose_apoiador(parts, P, root, mode, f):
    pose_person(parts, P, root, apoiador_state(mode, f, parts['tag']))
