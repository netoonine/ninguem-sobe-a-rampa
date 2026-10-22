"""Pecas comuns da torre Mensalinho (Ninguem Sobe a Rampa): concreto branco de Brasilia com curvas de Niemeyer
(fuste hiperbolico, cuia como a da Camara, colunas do Alvorada), guiche de caixa, dinheiro (notas, macos, envelopes,
malas) e os funcionarios do caixa (viseira de caixa de banco). Usado por torre_arqueiros.py (Mensalinho N1-N3 e
Mensalao) e torre_zarabatana.py (Dolar na Cueca). Nada de texto, numero ou logo na arte.

Cores da chapa (tools/blender/chapa.py, variavel CHAPA): o que identifica o lado sai de la (faixa da cuia, toldo,
moldura e placa do guiche com o emblema, caixa de envelopes, estandartes, bandeirinha, tapete, viseira e a roupa da
turma); o que carrega a piada fica igual nos dois lados (cedula verde, envelope, mala de couro, ouro, luz verde).
  CHAPA=V: camisa amarela da selecao com gola verde em V, calca azul, viseira verde
  CHAPA=R: camiseta vermelha com estrela branca no peito, calca jeans escura, viseira vermelha
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, emblema, estrela_peito   # noqa: F401

TAPETE = {'V': '#3a9a52', 'R': '#b3282d'}                         # piso da cuia e prato do Mensalao
VISEIRA = {'V': ('#3fb06a', '#2f8f52'), 'R': ('#ec4a3e', '#a81c22')}   # acetato translucido e faixa
CUECAS = {'V': ((PAL['sec'], PAL['pri']), ('#f4eedc', PAL['ter'])),  # varal e assessores do Dolar na Cueca
          'R': (('#f4eedc', PAL['pri']), ('#f4eedc', PAL['ter']))}


# ---------------------------------------------------------------- materiais (concreto branco, dinheiro e a chapa)
def mats_mensalinho(P):
    P['concreto'] = mat('concreto_bsb', '#efebe2', rough=0.86, var=0.03, bump=0.1)
    P['concreto_s'] = mat('concreto_bsb_sombra', '#d6cfc0', rough=0.9, var=0.03, bump=0.12)
    P['vidro_v'] = mat('vidro_bsb', '#6d9f97', rough=0.12, var=0.02, bump=0.0)
    P['vidro_esc'] = mat('vidro_guiche', '#3f6a6c', rough=0.1, var=0.0, bump=0.0)
    P['tapete'] = mat('tapete_chapa_' + CHAPA, TAPETE[CHAPA], rough=0.95, var=0.03, bump=0.25, sheen=0.5)
    P['teal'] = mat('verde_dinheiro', '#4f9a5a', rough=0.8, var=0.04, bump=0.08, sheen=0.4)
    P['verde_cl'] = mat('verde_dinheiro_cl', '#86c472', rough=0.8, var=0.04, bump=0.06, sheen=0.3)
    P['stripes'] = mat('toldo_chapa_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(14.0, PAL['sec'], PAL['pri']), sheen=0.4)
    P['chapa'] = cor('pri')        # cor principal da chapa: moldura, placa, caixa de envelopes, faixa, lacre
    P['chapa2'] = cor('sec')       # amarelo / branco
    P['chapa3'] = cor('ter')       # azul / vinho
    P['nota'] = mat('cedula', '#8cc678', rough=0.8, var=0.08, bump=0.04, sheen=0.2)
    P['nota_esc'] = mat('cedula_esc', '#3f8a4c', rough=0.8, var=0.06, bump=0.04)
    P['cinta'] = mat('cinta_papel', '#f3ecd6', rough=0.85, var=0.02, bump=0.02)
    P['envelope'] = mat('envelope', '#f4ead2', rough=0.85, var=0.03, bump=0.03, sheen=0.2)
    P['envelope_d'] = mat('envelope_aba', '#dccaa0', rough=0.85, var=0.02, bump=0.03)
    P['mala'] = mat('mala_couro', '#7b4a2b', rough=0.55, var=0.05, bump=0.12)
    P['mala_cl'] = mat('mala_couro_cl', '#a0663a', rough=0.55, var=0.05, bump=0.1)
    P['mala_esc'] = mat('mala_couro_esc', '#4f2f1c', rough=0.6, var=0.04, bump=0.1)
    P['forro'] = mat('forro_mala', '#2f5e3c', rough=0.7, var=0.02, bump=0.05, sheen=0.6)
    P['dolar'] = mat('dolar', '#b9c8a0', rough=0.8, var=0.06, bump=0.04)
    P['dolar_esc'] = mat('dolar_esc', '#6f8c63', rough=0.8, var=0.05, bump=0.04)
    P['camisa'] = cor('camisa')                                  # camisa da selecao / camiseta vermelha
    P['gola'] = cor('gola')                                      # debrum verde do decote em V (so na chapa V)
    P['calca'] = cor('calca')
    P['saia_v'] = cor('calca')
    P['sapato'] = mat('sapato_social', '#2b2320', rough=0.4, var=0.02, bump=0.02)
    P['cinto'] = mat('cinto_social', '#2e2522', rough=0.5, var=0.02, bump=0.02)
    P['gravata'] = mat('gravata_verde', '#3c8a4c', rough=0.6, var=0.02, bump=0.03, sheen=0.3)
    P['gravata_esc'] = mat('gravata_verde_esc', '#2c6a3a', rough=0.6, var=0.02, bump=0.03, sheen=0.3)
    P['colete'] = mat('colete_verde', '#4a8f55', rough=0.85, var=0.02, bump=0.06, sheen=0.4)
    P['viseira'] = mat('viseira_' + CHAPA, VISEIRA[CHAPA][0], rough=0.3, var=0.0, bump=0.0)
    vb = next(n for n in P['viseira'].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    vb.inputs['Alpha'].default_value = 0.62     # acetato translucido na cor da chapa: os olhos aparecem por baixo
    P['viseira_faixa'] = mat('viseira_faixa_' + CHAPA, VISEIRA[CHAPA][1], rough=0.4, var=0.0, bump=0.0)
    P['lente'] = mat('oculos_aro', '#2a2a2e', rough=0.4, var=0.0, bump=0.0)
    P['cabelo_c'] = mat('cabelo_castanho', '#5a3a22', rough=0.7, var=0.03, bump=0.25)
    P['cabelo_p'] = mat('cabelo_preto', '#2b2220', rough=0.7, var=0.03, bump=0.25)
    P['cabelo_g'] = mat('cabelo_grisalho', '#8f8a84', rough=0.7, var=0.03, bump=0.25)
    P['ipe'] = mat('ipe_amarelo', '#f2c230', rough=0.85, var=0.1, bump=0.15, sheen=0.4)
    P['ipe_cl'] = mat('ipe_amarelo_cl', '#ffd95a', rough=0.85, var=0.08, bump=0.15, sheen=0.4)
    P['casca'] = mat('casca_ipe', '#6a4a36', rough=0.85, var=0.1, bump=0.4)
    P['lamp_v'] = glow_mat('lampada_caixa', '#9dffb4', 1.0, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['globo'] = glow_mat('globo_bsb', '#fff0cc', 0.8, 14.0, rough=0.3, var=0.0, bump=0.0)
    P['sandstone'] = P['concreto']
    P['sandstone_l'] = P['concreto']
    P['mortar'] = P['concreto_s']
    P['_emblem'] = 'coin'
    return P


# ---------------------------------------------------------------- geometria de concreto
def lathe_arc(root, name, sec, a0, a1, m, n=24, front=False, bev=0.03):
    """Secao fechada sec [(r, z), ...] varrida em volta do eixo Z entre os angulos a0 e a1, com tampas.
    Serve para o parapeito da cuia (dividido em fundo e frente)."""
    bm = bmesh.new()
    rows = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        rows.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in sec])
    s = len(sec)
    for k in range(n):
        A, B = rows[k], rows[k + 1]
        for j in range(s):
            bm.faces.new((A[j], A[(j + 1) % s], B[(j + 1) % s], B[j]))
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm_to_obj(bm, name, root, [m], front=front, bev=bev, seg=3, angle=50)


def fuste(root, P, tag, z0, z1, r0, rw, r1, segs=48):
    """Fuste de concreto em hiperboloide (cintura em 55% da altura), como a torre de TV e a Catedral."""
    prof = []
    for k in range(13):
        t = k / 12
        base = r0 + (r1 - r0) * t
        dip = (base - rw) * math.sin(math.pi * min(1.0, t / 1.1)) ** 1.3 if rw < base else 0.0
        r = base - dip * 0.95
        prof.append((z0 + (z1 - z0) * t, r, r))
    return lathe(root, tag + '_fuste', prof, P['concreto'], segs=segs, lv=1)


def cuia(root, P, tag, zb, fz, r1, R, rail=0.2, trim=None):
    """Cuia de concreto no alto (a da Camara dos Deputados): barriga curva por baixo, piso de tapete verde e parapeito
    baixo e aberto em cima (a tripulacao aparece inteira). A frente do parapeito vai na camada da frente."""
    prof = []
    zt = fz - 0.012
    for k in range(11):
        t = k / 10
        prof.append((zb + (zt - zb) * t, r1 + (R - r1) * math.sin(t * math.pi / 2), r1 + (R - r1) * math.sin(t * math.pi / 2)))
    lathe(root, tag + '_cuia', prof, P['concreto'], segs=56, lv=1)
    cyl(root, tag + '_piso', R - 0.05, 0.05, (0, 0, fz - 0.025), m=P['tapete'], v=56, bev=0.01)
    ri = R - 0.075
    sec = [(ri, fz - 0.04), (R, fz - 0.04), (R + 0.004, fz + rail * 0.6), (R - 0.01, fz + rail), (ri + 0.01, fz + rail), (ri, fz + rail * 0.6)]
    fa0, fa1 = -math.pi + 0.32, -0.32       # trecho da frente (sin < -0.3)
    lathe_arc(root, tag + '_parapeito', sec, fa1, fa0 + TAU, P['concreto'], n=40)
    lathe_arc(root, tag + '_parapeitoF', sec, fa0, fa1, P['concreto'], n=24, front=True)
    # faixa pintada da chapa na face de fora do parapeito (a mesma do lote: cor principal com filete por cima);
    # o trecho da frente vai na camada da frente junto com o parapeito
    za, zm, zc = fz + rail * 0.08, fz + rail * 0.38, fz + rail * 0.5
    rof = lambda z: R + 0.004 * (z - (fz - 0.04)) / (rail * 0.6 + 0.04)     # raio da face de fora do parapeito em z
    faixa = [(rof(za) - 0.002, za), (rof(za) + 0.006, za), (rof(zm) + 0.006, zm), (rof(zm) - 0.002, zm)]
    filete = [(rof(zm) - 0.002, zm + 0.012), (rof(zm) + 0.006, zm + 0.012), (rof(zc) + 0.006, zc), (rof(zc) - 0.002, zc)]
    for nm, s_, m_ in (('_faixaChapa', faixa, P['chapa']), ('_fileteChapa', filete, P['chapa2'])):
        lathe_arc(root, tag + nm, s_, fa1, fa0 + TAU, m_, n=40, bev=0.002)
        lathe_arc(root, tag + nm + 'F', s_, fa0, fa1, m_, n=24, front=True, bev=0.002)
    if trim:
        tube(root, tag + '_frisoT', ring_pts((0, 0, fz - 0.06), R + 0.012, n=40, a0=fa1, a1=fa0 + TAU, closed=False), 0.014, trim, segs=6)
        tube(root, tag + '_frisoF', ring_pts((0, 0, fz - 0.06), R + 0.012, n=24, a0=fa0, a1=fa1, closed=False), 0.014, trim, segs=6)


def faixa_vidro(root, P, tag, z0, z1, r, n=12):
    """Faixa de vidro esverdeado com montantes de concreto (o 'aquario' dos ministerios)."""
    cyl(root, tag + '_laje', r + 0.05, 0.04, (0, 0, z0 - 0.02), m=P['concreto'], v=48, bev=0.012)
    cyl(root, tag + '_vidro', r - 0.012, z1 - z0, (0, 0, (z0 + z1) / 2), m=P['vidro_v'], v=48, bev=0.0)
    for k in range(n):
        a = TAU * k / n + math.pi / n
        box(root, f'{tag}_montante{k}', (0.03, 0.035, z1 - z0), (r * math.cos(a), r * math.sin(a), (z0 + z1) / 2), rot=(0, 0, a + math.pi / 2),
            m=P['concreto'], bev=0.01)


def aleta(root, P, name, ang, s_c, z0, z1, wmax=0.22, th=0.055):
    """Coluna do Palacio da Alvorada: toca o chao numa ponta e abre em curva ate a cuia (plano radial em ang)."""
    bm = bmesh.new()
    rows = []
    N = 14
    for k in range(N + 1):
        t = k / N
        w = 0.014 + wmax * t ** 1.7
        z = z0 + (z1 - z0) * t
        s0, s1 = s_c - w * 0.5, s_c + w * 0.5
        rows.append([bm.verts.new((s0, -th / 2, z)), bm.verts.new((s1, -th / 2, z)), bm.verts.new((s1, th / 2, z)), bm.verts.new((s0, th / 2, z))])
    for k in range(N):
        A, B = rows[k], rows[k + 1]
        for j in range(4):
            bm.faces.new((A[j], A[(j + 1) % 4], B[(j + 1) % 4], B[j]))
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, name, root, [P['concreto']], bev=0.018, seg=3, angle=40)
    o.rotation_euler = (0, 0, ang)
    return o


# ---------------------------------------------------------------- dinheiro
def nota(root, name, P, loc, rot=(0, 0, 0), s=1.0, m=None):
    """Cedula solta (verde), uma placa fina."""
    return box(root, name, (0.13 * s, 0.065 * s, 0.006 * s), loc, rot=rot, m=m or P['nota'], bev=0.002 * s)


def maco(root, name, P, loc, rz=0.0, s=1.0, m=None):
    """Maco de dinheiro com cinta de papel."""
    x, y, z = loc
    box(root, name, (0.13 * s, 0.066 * s, 0.04 * s), (x, y, z + 0.02 * s), rot=(0, 0, rz), m=m or P['nota'], bev=0.006 * s)
    box(root, name + '_cinta', (0.03 * s, 0.07 * s, 0.044 * s), (x, y, z + 0.02 * s), rot=(0, 0, rz), m=P['cinta'], bev=0.004 * s)


def pilha(root, tag, P, loc, n=3, s=1.0, rz=0.0, m=None, seed=1):
    rr = random.Random(seed)
    x, y, z = loc
    for k in range(n):
        maco(root, f'{tag}{k}', P, (x + rr.uniform(-0.01, 0.01) * s, y + rr.uniform(-0.01, 0.01) * s, z + 0.042 * s * k), rz=rz + rr.uniform(-0.15, 0.15), s=s, m=m)


def envelope(root, name, P, w=0.13, h=0.09, th=0.012, cash=True, aba=True):
    """Envelope de dinheiro no plano YZ (espessura em X, face para +X), base em z=0, centrado em Y.
    Devolve o pivo (empty) com tudo pendurado; quem chama posiciona/gira o pivo."""
    piv = empty(root, name)
    kids(piv, box(root, name + '_papel', (th, w, h), (0, 0, h / 2), m=P['envelope'], bev=min(0.006, th * 0.45)))
    if aba:
        bm = bmesh.new()
        tri = [(th / 2 + 0.0015, -w / 2 + 0.008, h - 0.006), (th / 2 + 0.0015, w / 2 - 0.008, h - 0.006), (th / 2 + 0.0015, 0.0, h * 0.42)]
        a = [bm.verts.new(p) for p in tri]
        b = [bm.verts.new((p[0] + 0.004, p[1], p[2])) for p in tri]
        bm.faces.new(a[::-1])
        bm.faces.new(b)
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        kids(piv, bm_to_obj(bm, name + '_aba', root, [P['envelope_d']], bev=0.0015, angle=30))
        kids(piv, cyl(root, name + '_selo', 0.012, 0.006, (th / 2 + 0.006, 0, h * 0.44), rot=(0, math.pi / 2, 0), m=P['chapa'], v=12, bev=0.002))
    if cash:
        for k, (dy, rx, hz) in enumerate(((-0.025, -0.12, 0.034), (0.012, 0.06, 0.04), (0.03, 0.22, 0.028))):
            kids(piv, box(root, f'{name}_nota{k}', (th * 0.5, w * 0.62, 0.05), (0, dy * w / 0.13, h - 0.02 + hz * 0.5), rot=(rx, 0, 0),
                          m=P['nota'] if k != 1 else P['nota_esc'], bev=0.002))
    return piv


def mala(root, name, P, w=0.5, h=0.36, d=0.14, alca=True, notas=True, s=1.0, notas_em='x'):
    """Mala de couro marrom (face no plano XZ, espessura em Y), centrada na origem do pivo, alca em +Z,
    cantoneiras e fechos de ouro, cintas mais escuras e notas escapando pela costura do lado -X (ou de baixo, -Z)."""
    w, h, d = w * s, h * s, d * s
    piv = empty(root, name)
    kids(piv, box(root, name + '_corpo', (w, d, h), (0, 0, 0), m=P['mala'], bev=0.035 * s, seg=4))
    # costura em volta (no meio da espessura)
    q = 0.004 * s
    rect = [(-w / 2 - q, 0, -h / 2 + 0.03 * s), (-w / 2 - q, 0, h / 2 - 0.03 * s), (-w / 2 + 0.03 * s, 0, h / 2 + q), (w / 2 - 0.03 * s, 0, h / 2 + q),
            (w / 2 + q, 0, h / 2 - 0.03 * s), (w / 2 + q, 0, -h / 2 + 0.03 * s), (w / 2 - 0.03 * s, 0, -h / 2 - q), (-w / 2 + 0.03 * s, 0, -h / 2 - q)]
    kids(piv, tube(root, name + '_costura', rect, 0.008 * s, P['mala_esc'], segs=6, closed=True))
    for k, x in enumerate((-w * 0.27, w * 0.27)):
        kids(piv, box(root, f'{name}_cinta{k}', (0.045 * s, d + 0.012 * s, h + 0.012 * s), (x, 0, 0), m=P['mala_esc'], bev=0.008 * s))
        kids(piv, box(root, f'{name}_fivela{k}', (0.05 * s, d + 0.02 * s, 0.035 * s), (x, 0, -h * 0.18), m=P['gold'], bev=0.006 * s))
    for sx in (-1, 1):
        for sz in (-1, 1):
            kids(piv, sphere(root, f'{name}_canto{sx}{sz}', 0.03 * s, (sx * (w / 2 - 0.012 * s), 0, sz * (h / 2 - 0.012 * s)), scale=(1, d / (0.06 * s) * 0.55, 1),
                             m=P['gold'], seg=10))
    if alca:
        kids(piv, tube(root, name + '_alca', [(-0.07 * s, 0, h / 2), (-0.06 * s, 0, h / 2 + 0.055 * s), (0.06 * s, 0, h / 2 + 0.055 * s), (0.07 * s, 0, h / 2)],
                       0.016 * s, P['mala_esc'], segs=8))
        for sx in (-1, 1):
            kids(piv, box(root, f'{name}_fecho{sx}', (0.045 * s, d * 0.6, 0.025 * s), (sx * 0.14 * s, 0, h / 2 + 0.006 * s), m=P['gold'], bev=0.005 * s))
    if notas:
        for k, (dz, ry, ln) in enumerate(((-0.1, -0.5, 0.11), (-0.02, 0.15, 0.13), (0.07, 0.55, 0.1), (0.13, -0.15, 0.08))):
            if notas_em == 'x':
                o = box(root, f'{name}_notaFora{k}', (ln * s, 0.005 * s, 0.055 * s), (-w / 2 - ln * s * 0.35, 0, dz * h / 0.36), rot=(0, ry, 0),
                        m=P['nota'] if k % 2 == 0 else P['nota_esc'], bev=0.002 * s)
            else:
                o = box(root, f'{name}_notaFora{k}', (0.055 * s, 0.005 * s, ln * s), (dz * w / 0.36, 0, -h / 2 - ln * s * 0.35), rot=(0, ry, 0),
                        m=P['nota'] if k % 2 == 0 else P['nota_esc'], bev=0.002 * s)
            kids(piv, o)
    return piv


def canteiro_dinheiro(root, P, tag, loc, s=1.0, seed=3):
    """Floreira de concreto em que o dinheiro 'da em arvore': notas espetadas como folhas."""
    rr = random.Random(seed)
    x, y, z = loc
    box(root, tag, (0.3 * s, 0.2 * s, 0.14 * s), (x, y, z + 0.07 * s), m=P['concreto'], bev=0.04 * s, seg=4)
    sphere(root, tag + '_monte', 0.12 * s, (x, y, z + 0.13 * s), scale=(1.15, 0.75, 0.4), m=P['nota_esc'], seg=14)
    for k in range(8):
        a = TAU * k / 8 + rr.uniform(-0.3, 0.3)
        px, py = x + 0.08 * s * math.cos(a), y + 0.05 * s * math.sin(a)
        nota(root, f'{tag}_folha{k}', P, (px, py, z + 0.2 * s), rot=(rr.uniform(-0.5, 0.5), rr.uniform(0.5, 1.1) * (1 if math.cos(a) > 0 else -1), a + math.pi / 2),
             s=s * 0.9, m=P['nota'] if k % 3 else P['verde_cl'])


def bandeja_envelopes(root, P, tag, loc, rz=0.0, n=6, s=1.0, seed=5):
    """Caixa verde de correspondencia cheia de envelopes de pe (a municao)."""
    rr = random.Random(seed)
    x, y, z = loc
    piv = empty(root, tag, loc=(x, y, z), rot=(0, 0, rz))
    kids(piv, box(root, tag + '_caixa', (0.2 * s, 0.16 * s, 0.1 * s), (0, 0, 0.05 * s), m=P['chapa'], bev=0.012 * s))
    for k in range(n):
        e = envelope(root, f'{tag}_env{k}', P, w=0.12 * s, h=0.11 * s, th=0.012 * s, aba=False)
        e.parent = piv
        e.location = (-0.075 * s + 0.15 * s * k / max(1, n - 1), rr.uniform(-0.02, 0.02) * s, 0.05 * s)
        e.rotation_euler = (rr.uniform(-0.12, 0.12), rr.uniform(-0.25, 0.25), math.pi / 2 + rr.uniform(-0.1, 0.1))
    return piv


def ipe(root, P, tag, loc, s=1.0, seed=7):
    """Ipe amarelo de Brasilia num vaso redondo de concreto."""
    rr = random.Random(seed)
    x, y, z = loc
    cyl(root, tag + '_vaso', 0.12 * s, 0.12 * s, (x, y, z + 0.06 * s), r2=0.1 * s, m=P['concreto'], v=24, bev=0.02 * s)
    sphere(root, tag + '_terra', 0.1 * s, (x, y, z + 0.12 * s), scale=(1, 1, 0.25), m=mat('terra_cerrado', '#a5532f', rough=0.95, var=0.08, bump=0.3), seg=12)
    top = (x + 0.03 * s, y, z + 0.5 * s)
    tube(root, tag + '_tronco', [(x, y, z + 0.1 * s), (x - 0.02 * s, y, z + 0.28 * s), top], 0.026 * s, P['casca'], segs=8, rfun=lambda t: (0.03 - 0.012 * t) * s)
    for k in range(3):
        a = TAU * k / 3 + 0.4
        tube(root, f'{tag}_galho{k}', [top, (top[0] + 0.12 * s * math.cos(a), top[1] + 0.12 * s * math.sin(a), top[2] + 0.1 * s)], 0.012 * s, P['casca'], segs=6)
    for k in range(9):
        a = rr.uniform(0, TAU)
        r = rr.uniform(0.04, 0.15) * s
        c = (top[0] + r * math.cos(a), top[1] + r * math.sin(a) * 0.9, top[2] + 0.1 * s + rr.uniform(-0.05, 0.08) * s)
        sphere(root, f'{tag}_flor{k}', rr.uniform(0.07, 0.1) * s, c, scale=(1, 1, 0.82), m=P['ipe'] if k % 3 else P['ipe_cl'], seg=14)


def nota_bandeira(root, P, tag, x, y, z, size=0.42, h_pole=0.9):
    """Mastro com uma cedula gigante tremulando (pano animado): verde com barra clara e medalhao (sem rosto nem numero)."""
    tube(root, tag + '_mastro', [(x, y, z), (x, y, z + h_pole)], 0.02, P['concreto_s'], segs=8)
    sphere(root, tag + '_topo', 0.035, (x, y, z + h_pole + 0.02), m=P['gold'], seg=12)
    hh = size * 0.5
    o = cloth_grid(root, tag + '_cedula', size, hh, 16, 6, [P['nota'], P['cinta'], P['nota_esc']], thick=0.012,
                   shape=lambda u, v, co: Vector((co.x, co.y, co.z)))
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    q = 0.035
    edge = [(q, -q), (size - q, -q), (size - q, -hh + q), (q, -hh + q)]
    tube_into(bm, [(ex, -0.009, ez) for ex, ez in edge] + [(edge[0][0], -0.009, edge[0][1])], 0.008, segs=5, caps=True, mat_index=1)
    tube_into(bm, [(ex, 0.009, ez) for ex, ez in edge] + [(edge[0][0], 0.009, edge[0][1])], 0.008, segs=5, caps=True, mat_index=1)
    for sy in (-0.011, 0.011):
        tube_into(bm, [(size * 0.66 + 0.06 * math.cos(a), sy, -hh / 2 + 0.07 * math.sin(a)) for a in [TAU * j / 18 for j in range(19)]], 0.012, segs=5,
                  caps=True, mat_index=2)
        tube_into(bm, [(size * 0.25 + 0.03 * math.cos(a), sy, -hh / 2 + 0.03 * math.sin(a)) for a in [TAU * j / 14 for j in range(15)]], 0.009, segs=5,
                  caps=True, mat_index=1)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o.location = (x + 0.02, y, z + h_pole - 0.04)
    register_cloth(o, flag_wave(size, amp=0.06, cycles=1, waves=1.1))
    return o


# ---------------------------------------------------------------- marcas da chapa (bandeirinha, estandarte, peito)
def _poly_into(bm, pts, y, mat_index):
    """Poligono plano no plano XZ (em y), face unica: o Solidify do pano da a espessura e o balanco acompanha."""
    f = bm.faces.new([bm.verts.new((x, y, z)) for x, z in pts])
    f.material_index = mat_index
    return f


def emblema_into(bm, cx, cz, w, h, y=-0.012):
    """Emblema da chapa costurado na malha do pano (centro cx, cz; caixa w x h). V: losango amarelo (material 1)
    com circulo azul (material 2); R: estrela branca de 5 pontas (material 1)."""
    if CHAPA == 'V':
        _poly_into(bm, [(cx + w * 0.42, cz), (cx, cz + h * 0.4), (cx - w * 0.42, cz), (cx, cz - h * 0.4)], y, 1)
        r = min(w, h) * 0.2
        _poly_into(bm, [(cx + r * math.cos(a), cz + r * math.sin(a)) for a in [TAU * j / 20 for j in range(20)]], y - 0.004, 2)
    else:
        r, ri = min(w, h) * 0.36, min(w, h) * 0.36 * 0.42
        _poly_into(bm, [(cx + (r if i % 2 == 0 else ri) * math.cos(math.pi / 2 + i * math.pi / 5),
                         cz + (r if i % 2 == 0 else ri) * math.sin(math.pi / 2 + i * math.pi / 5)) for i in range(10)], y, 1)


def estandarte_chapa(root, name, P, x, y, z_top, w=0.26, h=0.5):
    """Estandarte da chapa (mesmo pano, haste e balanco do lib.banner): cor principal com borda e emblema da chapa.
    Plano XZ, voltado para -Y."""
    def shape(u, v, co):
        if v > 0.82:                    # ponta em V na base
            co.z += abs(u - 0.5) * 2 * (v - 0.82) / 0.18 * h * 0.16
        return co
    o = cloth_grid(root, name, w, h, 6, 14, [P['chapa'], P['chapa2'], P['chapa3']], shape=shape, thick=0.016)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    edge = [(0.03, -0.02), (0.03, -h * 0.84), (w / 2, -h * 0.99), (w - 0.03, -h * 0.84), (w - 0.03, -0.02)]
    tube_into(bm, [(ex, -0.012, ez) for ex, ez in edge], 0.009, segs=5, caps=True, mat_index=1)
    emblema_into(bm, w / 2, -h * 0.38, w * 0.8, w * (0.8 if CHAPA == 'R' else 0.62), y=-0.012)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o.location = (x - w / 2, y, z_top)
    register_cloth(o, hang_wave(h, amp=0.045, axis='Y', cycles=1, waves=0.7, top=0.0))
    tube(root, name + '_haste', [(x - w / 2 - 0.05, y, z_top + 0.01), (x + w / 2 + 0.05, y, z_top + 0.01)], 0.014, P['gold'], segs=8)
    for sx in (-1, 1):
        sphere(root, f'{name}_ponta{sx}', 0.022, (x + sx * (w / 2 + 0.06), y, z_top + 0.01), m=P['gold'], seg=10)
    return o


def bandeira_chapa(root, P, name, loc, h=0.42, w=0.26, fh=0.17, face=0.0):
    """Bandeirinha da chapa num mastro fino de aluminio com ponta de ouro (pano na cor principal e o emblema dos dois
    lados). O pano fica parado: nao cria quadros de animacao. Quem chama garante que cabe no enquadramento atual."""
    x, y, z = loc
    piv = empty(root, name, loc=(x, y, z), rot=(0, 0, face))
    pm = mat('mastro_aluminio', '#c9ced2', rough=0.3, metal=0.7, var=0.02, bump=0.02)
    kids(piv, cyl(root, name + '_mastro', 0.01, h, (0, 0, h / 2), m=pm, v=8, bev=0.002),
         cyl(root, name + '_pe', 0.022, 0.014, (0, 0, 0.007), m=pm, v=10, bev=0.003),
         sphere(root, name + '_ponta', 0.016, (0, 0, h + 0.01), m=P['gold'], seg=10))
    pano = box(root, name + '_pano', (w, 0.008, fh), (0.01 + w / 2, 0, h - fh / 2 - 0.012), m=cor('pri', rough=0.8, sheen=0.4), bev=0.002)
    pano.parent = piv
    for s_, sg in (('a', -1), ('b', 1)):
        for o in emblema(root, f'{name}_em{s_}', w * 0.9, fh * 0.9, depth=0.004):
            if o.parent == root:       # (o circulo do losango ja vem preso no losango)
                o.parent = pano
                o.location = (0, sg * 0.005, 0)
                o.rotation_euler = (0, 0, math.pi if sg > 0 else 0.0)
    return piv


TRONCO = [(0.29, 0.072, 0.088), (0.34, 0.077, 0.094), (0.39, 0.081, 0.103), (0.43, 0.08, 0.108), (0.455, 0.066, 0.102),
          (0.475, 0.045, 0.064), (0.495, 0.03, 0.032)]     # perfil (z, rx, ry) do tronco do lib.build_person


def _tronco_x(z, y):
    """Frente do tronco (x local do corpo) na altura z e no lado y."""
    for (z0, a0, b0), (z1, a1, b1) in zip(TRONCO, TRONCO[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            rx, ry = a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
            return rx * math.sqrt(max(0.0, 1 - (y / ry) ** 2))
    return 0.0


def peito_chapa(root, P, parts, tag, z=0.414):
    """Marca da chapa no peito da turma: R = estrela branca (chapa.estrela_peito); V = decote em V da camisa da
    selecao (pele por dentro e debrum verde), rente ao tronco. Fica dentro do volume do corpo: nao mexe no quadro."""
    body = parts['body']
    if CHAPA == 'R':
        return estrela_peito(root, tag, body, (_tronco_x(z, 0.0) + 0.004, 0.0, z), r=0.03, rot=(-0.25, 0, math.pi / 2))
    zb, zt, hw = 0.43, 0.474, 0.06          # ponta do V, alto do decote e meia largura no alto
    bm = bmesh.new()
    rows = [[bm.verts.new((_tronco_x(zb, 0.0) + 0.0015, 0.0, zb))]]
    for j in range(1, 6):
        t = j / 5
        zz = zb + (zt - zb) * t
        half = hw * t
        rows.append([bm.verts.new((_tronco_x(zz, yy) + 0.0015, yy, zz)) for yy in [-half + 2 * half * i / 4 for i in range(5)]])
    for i in range(4):
        bm.faces.new((rows[0][0], rows[1][i + 1], rows[1][i]))
    for j in range(1, 5):
        for i in range(4):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    pele = bm_to_obj(bm, tag + '_decote', root, [parts['sp'].get('skin', P['skin'])], angle=80)
    pele.parent = body
    pts = [(_tronco_x(zz, yy) + 0.0025, yy, zz) for yy, zz in ((-hw, zt), (-hw * 0.5, (zb + zt) / 2), (0.0, zb), (hw * 0.5, (zb + zt) / 2), (hw, zt))]
    t = tube(root, tag + '_golaV', pts, 0.0075, P['gola'], segs=6)
    t.parent = body
    return [pele, t]


def lampada_banqueiro(root, P, tag, loc, rz=0.0, s=1.0):
    """Luminaria de banqueiro: pe de latao e cupula de vidro verde (brilha)."""
    x, y, z = loc
    piv = empty(root, tag, loc=(x, y, z), rot=(0, 0, rz))
    kids(piv, cyl(root, tag + '_pe', 0.05 * s, 0.02 * s, (0, 0, 0.01 * s), m=P['gold'], v=16, bev=0.005 * s),
         tube(root, tag + '_haste', [(0, 0, 0.0), (0, 0, 0.12 * s), (0.02 * s, 0, 0.14 * s)], 0.009 * s, P['gold'], segs=6),
         cyl(root, tag + '_cupula', 0.045 * s, 0.16 * s, (0.02 * s, 0, 0.15 * s), rot=(0, math.pi / 2, 0), m=P['lamp_v'], v=16, bev=0.01 * s))
    o = bpy.data.objects[tag + '_cupula']
    o.scale = (0.75, 1.0, 1.0)
    return piv


def globo(root, P, tag, x, y, z, h=0.2, front=False):
    """Poste curvo de concreto com globo de luz branca (iluminacao modernista)."""
    tube(root, tag + '_poste', [(x, y, z), (x, y, z + h * 0.6), (x * 1.05, y * 1.05, z + h)], 0.016, P['concreto'], segs=8, front=front)
    sphere(root, tag + '_globo', 0.05, (x * 1.05, y * 1.05, z + h + 0.045), m=P['globo'], seg=16, front=front)
    return (x * 1.05, y * 1.05, z + h + 0.045)


def guiche(root, P, tag, y_body, z0=0.15, w=0.42, d=0.22, h=0.44, lamp=True):
    """Guiche de caixa na frente da torre: janela de vidro com grade de ouro, boquinha do passa-dinheiro, balcao com um
    maco de notas, toldo listrado verde e placa verde com uma cedula em relevo. Devolve a posicao da lampada verde."""
    cy = y_body - d / 2 + 0.04
    yf = cy - d / 2
    box(root, tag + '_guiche', (w, d, h), (0, cy, z0 + h / 2), m=P['concreto'], bev=0.05, seg=4)
    box(root, tag + '_rodape', (w + 0.03, d + 0.03, 0.05), (0, cy, z0 + 0.025), m=P['concreto_s'], bev=0.015)
    zc = z0 + h * 0.62
    box(root, tag + '_janela', (w - 0.13, 0.03, h * 0.38), (0, yf + 0.006, zc), m=P['vidro_esc'], bev=0.006)
    pts = [(-(w - 0.13) / 2 - 0.012, yf - 0.006, zc - h * 0.19 - 0.012), (-(w - 0.13) / 2 - 0.012, yf - 0.006, zc + h * 0.19 + 0.012),
           ((w - 0.13) / 2 + 0.012, yf - 0.006, zc + h * 0.19 + 0.012), ((w - 0.13) / 2 + 0.012, yf - 0.006, zc - h * 0.19 - 0.012)]
    tube(root, tag + '_moldura', pts, 0.014, P['chapa'], segs=6, closed=True)
    for k in range(3):
        xx = -(w - 0.13) / 2 + (w - 0.13) * (k + 1) / 4
        tube(root, f'{tag}_grade{k}', [(xx, yf - 0.012, zc - h * 0.19), (xx, yf - 0.012, zc + h * 0.19)], 0.006, P['gold'], segs=6)
    cyl(root, tag + '_boquinha', 0.04, 0.03, (0, yf - 0.004, zc - h * 0.19), rot=(math.pi / 2, 0, 0), m=P['dark'], v=16, bev=0.0)
    zb = zc - h * 0.19 - 0.02
    box(root, tag + '_balcao', (w - 0.04, 0.11, 0.028), (0, yf - 0.045, zb), m=P['concreto'], bev=0.01)
    maco(root, tag + '_maco', P, (0.09, yf - 0.05, zb + 0.014), rz=0.2, s=0.8)
    maco(root, tag + '_maco2', P, (0.085, yf - 0.048, zb + 0.048), rz=-0.1, s=0.8)
    # toldo listrado inclinado com babado (listras e babado nas cores da chapa)
    zt = z0 + h + 0.01
    box(root, tag + '_toldo', (w + 0.06, 0.15, 0.02), (0, yf - 0.05, zt), rot=(math.radians(24), 0, 0), m=P['stripes'], bev=0.006)
    for k in range(7):
        xx = -(w + 0.06) / 2 + (w + 0.06) * (k + 0.5) / 7
        cyl(root, f'{tag}_babado{k}', (w + 0.06) / 14, 0.012, (xx, yf - 0.118, zt - 0.035), rot=(math.pi / 2, 0, 0),
            m=P['chapa'] if k % 2 == 0 else P['chapa2'], v=12, bev=0.002)
    # placa na cor da chapa com o emblema em relevo (V: losango amarelo e circulo azul; R: estrela branca), sem letras
    zp = zt + 0.075
    box(root, tag + '_placa', (w * 0.7, 0.03, 0.1), (0, yf + 0.04, zp), m=P['chapa'], bev=0.012)
    emblema(root, tag + '_placaEmblema', w * 0.62, 0.1, loc=(0, yf + 0.0225, zp), depth=0.006)
    lp = None
    if lamp:
        lx, lz = w / 2 - 0.02, zp + 0.01
        tube(root, tag + '_bracoLamp', [(lx - 0.04, yf + 0.03, lz - 0.05), (lx + 0.03, yf - 0.03, lz - 0.05), (lx + 0.03, yf - 0.03, lz - 0.02)], 0.008, P['gold'], segs=6)
        sphere(root, tag + '_lampada', 0.032, (lx + 0.03, yf - 0.03, lz + 0.01), m=P['lamp_v'], seg=14)
        lp = (lx + 0.03, yf - 0.03, lz + 0.01)
    return lp


# ---------------------------------------------------------------- funcionarios do caixa
def viseira(root, P, parts, tag, m=None, band_m=None):
    """Viseira verde de caixa de banco: faixa em volta da cabeca e aba curta (deixa os olhos a vista)."""
    hd = parts['head']
    hc = Vector((0.006, 0, 0.055))
    b = torus(root, f'{tag}_viseiraFaixa', (0, 0, 0), 0.072, 0.009, band_m or P['viseira_faixa'], n=22, segs=6)
    b.parent = hd
    b.location = hc + Vector((0, 0, 0.036))

    def cut(c):
        return abs(math.atan2(c.y, c.x)) > math.radians(58)
    aba = lathe(root, f'{tag}_viseiraAba', [(-0.016, 0.112, 0.104), (-0.006, 0.09, 0.086), (0.0, 0.068, 0.068)], m or P['viseira'], segs=32, lv=1,
                caps=False, solid=0.007, cut=cut)
    aba.parent = hd
    aba.location = hc + Vector((0, 0, 0.04))


def gravata(root, P, parts, tag, m, dx=0.0, clip=False):
    body = parts['body']
    pts = [(0.083 + dx, 0, 0.447), (0.088 + dx, 0, 0.41), (0.091 + dx, 0, 0.37), (0.087 + dx, 0, 0.33)]
    knot = blob(root, f'{tag}_gravataNo', 0.016, (0.08 + dx, 0, 0.455), (0.7, 1.0, 0.85), m)
    knot.parent = body
    t = tube(root, f'{tag}_gravata', pts, 0.02, m, segs=8, rfun=lambda u: 0.011 + 0.012 * min(1.0, u * 1.8) - 0.018 * max(0.0, u - 0.86) / 0.14)
    t.parent = body
    t.scale = (0.4, 1, 1)
    t.location = (0.088 + dx - 0.4 * (0.088 + dx), 0, 0)    # achata em X sem tirar do peito
    if clip:
        c = box(root, f'{tag}_prendedor', (0.008, 0.04, 0.008), (0.094 + dx, 0, 0.385), m=P['gold'], bev=0.002)
        c.parent = body


def gola(root, P, parts, tag, m=None):
    for s, yy in enumerate((-0.026, 0.026)):
        o = blob(root, f'{tag}_gola{s}', 0.022, (0.052, yy, 0.47), (0.55, 1.0, 0.6), m or P['camisa'], rot=(0.5 if yy > 0 else -0.5, 0, 0))
        o.parent = parts['body']


def oculos(root, P, parts, tag):
    hd = parts['head']
    hc = Vector((0.006, 0, 0.055))
    for s, yy in enumerate((-0.025, 0.025)):
        o = torus(root, f'{tag}_oculos{s}', (0, 0, 0), 0.019, 0.004, P['lente'], axis='X', n=14, segs=5)
        o.parent = hd
        o.location = hc + Vector((0.068, yy, 0.012))
    o = tube(root, f'{tag}_oculosPonte', [hc + Vector((0.07, -0.007, 0.016)), hc + Vector((0.073, 0, 0.019)), hc + Vector((0.07, 0.007, 0.016))], 0.003, P['lente'], segs=5)
    o.parent = hd


def bigode(root, P, parts, tag, m):
    hd = parts['head']
    hc = Vector((0.006, 0, 0.055))
    for s, yy in enumerate((-0.017, 0.017)):
        o = blob(root, f'{tag}_bigode{s}', 0.016, hc + Vector((0.064, yy, -0.024)), (0.6, 1.3, 0.6), m, rot=(0.35 if yy > 0 else -0.35, 0, 0))
        o.parent = hd


def env_mao(root, P, parts, tag, side='R', s=1.0):
    """Envelope na mao (eixo Z local da mao): o que vai ser arremessado."""
    e = envelope(root, f'{tag}_env{side}', P, w=0.14 * s, h=0.1 * s, th=0.012 * s)
    e.location = (0, 0, -0.014)
    e.rotation_euler = (0, 0, math.pi / 2)    # face para o lado da mao (aparece para a camera)
    hold(parts, side, e)
    return e


def leque(root, P, parts, tag, side='L', s=1.0):
    """Leque de tres envelopes na outra mao (o estoque do arremessador)."""
    piv = empty(root, f'{tag}_leque')
    for k, ang in enumerate((-0.38, 0.0, 0.38)):
        e = envelope(root, f'{tag}_leque{k}', P, w=0.13 * s, h=0.095 * s, th=0.01 * s, cash=(k == 1))
        e.parent = piv
        e.location = (0.004 * (k - 1), 0, -0.012)
        e.rotation_euler = (ang, 0, 0)
    piv.rotation_euler = (0, 0, math.pi / 2)
    hold(parts, side, piv)
    return piv


HEAD_K = 1.4    # cabecao de boneco (caricatura)


def build_funcionario(P, root, variant, tag=None):
    """Funcionario do caixa (~0.6 BU, cabecao) com a roupa da chapa (camisa da selecao amarela de gola verde em V e
    calca azul, ou camiseta vermelha com estrela branca no peito e jeans escuro), manga curta, viseira de caixa de
    banco na cor da chapa, envelope na mao direita e um leque de envelopes na esquerda.
    a1: cabelo castanho; a2: cabelo preto e oculos; a3: grisalho de bigode, viseira com faixa de ouro; a3b: funcionaria
    de coque, saia e brincos de ouro; op: suspensorio (opera a mala do Mensalao)."""
    tag = tag or root['set']
    hair = {'a1': P['cabelo_c'], 'a2': P['cabelo_p'], 'a3': P['cabelo_g'], 'a3b': P['cabelo_p'], 'op': P['cabelo_c']}[variant]
    skin = mat('pele_' + variant, {'a1': '#d9a578', 'a2': '#a8714a', 'a3': '#e3b48c', 'a3b': '#8c5a3c', 'op': '#c98d5e'}[variant], rough=0.7, var=0.05, bump=0.02)
    sp = dict(skin=skin, tunic=P['camisa'], sleeve=P['camisa'], bracer=skin, skirt_m=P['saia_v'] if variant == 'a3b' else P['calca'],
              pants=P['calca'] if variant != 'a3b' else skin, boot_m=P['sapato'], boot_cuff=P['calca'] if variant != 'a3b' else P['sapato'],
              belt=P['cinto'] if variant != 'a3b' else None, buckle=P['gold'], head='hair', hair_m=hair, bare_hands=True,
              topknot=(variant == 'a3b'))
    pr = build_person(P, root, tag, sp)
    pr['head'].scale = (HEAD_K, HEAD_K, HEAD_K)
    sa = bpy.data.objects.get(f'{tag}_saia')
    if sa and variant != 'a3b':
        sa.scale = (0.86, 0.86, 1.0)    # calca, nao tunica
    peito_chapa(root, P, pr, tag)       # decote em V (V) ou estrela no peito (R); a gola de camisa social saiu
    if variant == 'a3b':
        hd = pr['head']
        for s, yy in enumerate((-0.066, 0.066)):
            b = sphere(root, f'{tag}_brinco{s}', 0.009, Vector((0.006, yy, 0.03)), m=P['gold'], seg=8)
            b.parent = hd
    if variant == 'op':
        for s, yy in enumerate((-0.05, 0.05)):
            o = tube(root, f'{tag}_suspensorio{s}', [(0.085, yy, 0.3), (0.09, yy * 1.1, 0.4), (0.05, yy * 1.3, 0.462), (-0.04, yy * 1.2, 0.46), (-0.085, yy * 0.8, 0.38),
                                                    (-0.085, yy * 0.6, 0.3)], 0.009, P['calca'], segs=6)
            o.parent = pr['body']
    if variant == 'a2':
        oculos(root, P, pr, tag)
    if variant == 'a3':
        bigode(root, P, pr, tag, P['cabelo_g'])
    viseira(root, P, pr, tag, band_m=P['gold'] if variant == 'a3' else None)
    if variant != 'op':
        env_mao(root, P, pr, tag, 'R')
        leque(root, P, pr, tag, 'L')
    pr['variant'] = variant
    return pr


# arremesso do envelope (por cima do ombro); o corpo olha para +X local (3/4 para a direita e para a camera)
IDLE, AIM, SHOOT = 12, 4, 8
MIRA = dict(hand_R=(-0.06, -0.135, 0.63), grip_R=(0.45, 0.1, 1.0), pole_R=(-0.4, -1.0, 0.4),
            hand_L=(0.22, 0.08, 0.45), grip_L=(0.7, -0.2, 1.0), pole_L=(-0.2, 1.0, -0.7), lean=-0.05, head_pitch=-0.14, head_yaw=-0.3)


def caixa_state(mode, f, tag):
    envR = f'{tag}_envR'
    if mode == 'idle':
        # conta as notas do leque: a mao direita belisca o maco duas vezes por ciclo; ora olha o dinheiro, ora olha em volta
        ph = f / IDLE
        s = math.sin(TAU * ph)
        c = max(0.0, math.sin(2 * TAU * ph))
        return dict(hand_L=(0.15, 0.07, 0.35 + 0.004 * s), grip_L=(0.6, -0.4, 1.0), pole_L=(-0.3, 1.0, -0.7),
                    hand_R=(0.17, -0.02, 0.37 + 0.025 * c), grip_R=(0.3, 0.3, 1.0), pole_R=(-0.3, -1.0, -0.7), hide=(envR,), breathe=s,
                    head_yaw=-0.15 + 0.3 * math.sin(TAU * ph + 0.6), head_pitch=0.12 * (0.5 + 0.5 * math.cos(TAU * ph)) - 0.1, ph=ph)
    if mode == 'aim':
        ph = f / AIM
        st = dict(MIRA)
        st.update(breathe=0.4 * math.sin(TAU * ph), ph=ph)
        return st
    seq = [
        dict(hand_R=(0.25, -0.03, 0.55), grip_R=(1.0, 0.0, 0.3), pole_R=(-0.6, -1.0, -0.2), hand_L=(0.1, 0.12, 0.36), lean=0.09, hide=(envR,), head_pitch=-0.08),
        dict(hand_R=(0.2, 0.02, 0.36), grip_R=(1.0, 0.0, -0.3), pole_R=(-0.4, -1.0, -0.5), hand_L=(0.11, 0.11, 0.35), lean=0.1, hide=(envR,), head_pitch=-0.04),
        dict(hand_R=(0.16, 0.02, 0.39), grip_R=(0.4, 0.3, 1.0), pole_R=(-0.3, -1.0, -0.6), hand_L=(0.15, 0.07, 0.38), lean=0.05, hide=(envR,), head_pitch=0.04, head_yaw=-0.15),
        dict(hand_R=(0.13, -0.04, 0.45), grip_R=(0.3, 0.2, 1.0), pole_R=(-0.3, -1.0, -0.4), hand_L=(0.16, 0.07, 0.39), lean=0.03, head_pitch=-0.02, head_yaw=-0.2),
        dict(hand_R=(0.05, -0.11, 0.54), grip_R=(0.4, 0.1, 1.0), pole_R=(-0.3, -1.0, 0.0), hand_L=(0.18, 0.07, 0.41), lean=0.0),
        dict(hand_R=(-0.02, -0.13, 0.6), grip_R=(0.45, 0.1, 1.0), pole_R=(-0.4, -1.0, 0.3), hand_L=(0.2, 0.08, 0.43), lean=-0.03),
        dict(hand_R=(-0.05, -0.135, 0.625), grip_R=(0.45, 0.1, 1.0), pole_R=(-0.4, -1.0, 0.4), hand_L=(0.215, 0.08, 0.445), lean=-0.045),
        dict(),
    ][f]
    st = dict(MIRA)
    st.update(ph=f / SHOOT)
    st.update(seq)
    return st


def pose_caixa(parts, P, root, mode, f):
    pose_person(parts, P, root, caixa_state(mode, f, parts['tag']))
