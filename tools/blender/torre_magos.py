"""Joias da Arabia (Ninguem Sobe a Rampa): niveis 1 a 3, Corrente de Ouro (lightning) e Relogio de Ouro (sun), com os
assessores das joias animados. Um estojo de joias de veludo (na cor da chapa), aberto, sobre pedestal de concreto
branco de Brasilia (no nivel 3, com as colunas da Alvorada); dentro, almofadas com aneis e gemas, e no alto a joia
principal que brilha e gira (o antigo orbe: e dela que sai o disparo). Colar de ouro e perolas orbitando. Veludo da
chapa e dourado de assinatura, nada de marca, letra ou numero (conceito: arte/conceitos/torres/joias.png).

Os nomes de conjuntos, postos e pontos sao os mesmos da Lanterna dos Vaga-lumes (js/sprites.js depende deles):
mg1, mg2, mg3, mgL (lightning), mgS (sun) e a tripulacao mgA, mgB, mgC, mgE, mgP (modos idle e cast; ponto 'top').

Cores da chapa (tools/blender/chapa.py): o veludo do estojo, o forro da tampa (com o emblema da chapa), as almofadas,
os mantos e a roupa da turma e a gema de assinatura seguem a chapa; ouro, perolas e as outras gemas ficam iguais.
  CHAPA=V (padrao): estojo verde, forro com a bandeira (losango amarelo e circulo azul), almofadas amarelas, turma de
                    amarelo da selecao com verde, gema verde
  CHAPA=R:          estojo vermelho, forro vermelho com estrela branca, almofadas brancas, turma de vermelho com a
                    estrela branca no peito, gema vermelha

  Blender -b -P tools/blender/torre_magos.py -- render arte/render/magos [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_magos.py -- render arte/render_r/magos [conjuntos...]
  Blender -b -P tools/blender/torre_magos.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_magos.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto branco de Brasilia (padrao de todas as torres)
from chapa import CHAPA, PAL, cor, emblema, bandeirinha, estrela_peito   # cores da chapa (CHAPA=V ou R)

G = 0.07   # chao do lote no codigo (topo 0.15 menos o LIFT que o build_family soma)

FRONT = -math.pi / 2
FAM = 'magos'

import lib as _lib
_orig_palette2 = palette2


VELUDO = dict(rough=0.9, var=0.03, bump=0.1, sheen=1.0)     # veludo do estojo
MANTO = dict(rough=0.82, var=0.03, bump=0.08, sheen=0.6)     # mantos e roupa da turma
V_ = CHAPA == 'V'


def palette2():   # noqa: F811 - veludo e roupa na cor da chapa, ouro de assinatura, sobre concreto branco
    P = _orig_palette2()
    P['teal'] = cor('pri', rough=0.8, var=0.04, bump=0.08, sheen=0.4)
    P['robe'] = cor('camisa', **MANTO)                         # V amarelo da selecao / R vermelho
    P['robe_d'] = cor('pri' if V_ else 'escuro', **MANTO)      # V verde / R vermelho escuro
    P['robe_l'] = cor('claro', **MANTO)                        # V creme amarelado / R branco rosado
    P['trim_c'] = cor('gola', rough=0.7, sheen=0.4)            # barra e faixa da turma: V verde / R branco
    P['stripes'] = mat(f'toldo_chapa_{CHAPA}', PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(3.6, PAL['claro'], PAL['pri']), sheen=0.4)
    P['velvet'] = cor('pri', **VELUDO)                         # estojo: V verde / R vermelho
    P['velvet_d'] = cor('escuro', **VELUDO)                    # tampa por fora
    P['velvet_l'] = cor('sec' if V_ else 'claro', **VELUDO)    # almofadas: V amarelo / R branco
    P['lining'] = cor('pri', **VELUDO)                         # forro da tampa = campo da bandeira (emblema por cima)
    P['gold'] = mat('ouro_joia', '#f0c04e', rough=0.28, metal=0.8, var=0.03, bump=0.03)
    P['gold_d'] = mat('ouro_velho', '#d29a32', rough=0.35, metal=0.8, var=0.03, bump=0.04)
    P['concrete'] = mat('concreto', '#efebe2', rough=0.88, var=0.03, bump=0.18)
    P['pearl'] = mat('perola', '#f8f1e6', rough=0.22, var=0.03, bump=0.0, sheen=0.6)
    P['keyhole'] = mat('fechadura', '#251b1d', rough=0.6, var=0.0, bump=0.0)
    # gemas: brilham um pouco de dia e forte no passe de luz (somado no jogo conforme o clima)
    P['diamond'] = glow_mat('gema_diamante', '#8fe4ff', 0.3, 10.0, rough=0.04, var=0.0, bump=0.0)
    P['emerald'] = glow_mat('gema_esmeralda', '#3ed67e', 0.35, 7.0, rough=0.05, var=0.0, bump=0.0)
    P['ruby'] = glow_mat('gema_rubi', '#ff4f8f', 0.35, 7.0, rough=0.05, var=0.0, bump=0.0)
    P['sapphire'] = glow_mat('gema_safira', '#4f86ff', 0.35, 7.0, rough=0.05, var=0.0, bump=0.0)
    # a antiga ametista de assinatura vira a gema da chapa (verde / vermelha)
    P['amethyst'] = glow_mat(f'gema_chapa_{CHAPA}', '#2fe07a' if V_ else '#ff3346', 0.4, 8.0, rough=0.05, var=0.0, bump=0.0)
    P['_luz_gema'] = '#a6ffcb' if V_ else '#ff9c9c'
    P['topaz'] = glow_mat('gema_topazio', '#ffc84a', 0.4, 8.0, rough=0.05, var=0.0, bump=0.0)
    P['glint'] = glow_mat('brilho_joia', '#fffbea', 3.0, 14.0, rough=0.3, var=0.0, bump=0.0)
    P['spark'] = glow_mat('faisca_ouro', '#ffe27a', 2.4, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['_emblem'] = 'star'
    return P


_lib.palette2 = palette2


def bandeira_chapa(root, name, loc, **kw):
    """chapa.bandeirinha com o emblema no pano: la o emblema nasce filho da raiz (o `parent is None` nunca vale) e
    ficaria escondido no centro do lote; aqui ele vai para os dois lados do pano."""
    mast = bandeirinha(root, name, loc, **kw)
    cloth = next(c for c in mast.children if c.name.startswith(name + '_pano'))
    for s, sgn in (('a', -1), ('b', 1)):
        for o in list(root.children):
            if o.name.startswith(f'{name}_em{s}_'):
                o.parent = cloth
                o.location = (0, sgn * 0.005, 0)
    return mast


# ---------------------------------------------------------------- pecas de joalheria
def gem(root, name, r, loc, m, rot=(0, 0, 0), n=8, crown=0.36, pav=0.82, table=0.56, front=False, parent=None):
    """Pedra lapidada (brilhante): mesa, coroa em estrela, cintura e pavilhao pontudo, em facetas chapadas."""
    bm = bmesh.new()
    top = [bm.verts.new((table * r * math.cos(TAU * k / n), table * r * math.sin(TAU * k / n), crown * r)) for k in range(n)]
    gir = [bm.verts.new((r * math.cos(TAU * (k + 0.5) / n), r * math.sin(TAU * (k + 0.5) / n), 0.0)) for k in range(n)]
    gir2 = [bm.verts.new((r * math.cos(TAU * (k + 0.5) / n), r * math.sin(TAU * (k + 0.5) / n), -0.07 * r)) for k in range(n)]
    apex = bm.verts.new((0, 0, -pav * r))
    bm.faces.new(top)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((top[k], gir[k], top[j]))
        bm.faces.new((gir[k - 1], gir[k], top[k]))
        bm.faces.new((gir[k], gir[j], gir2[j], gir2[k]))
        bm.faces.new((gir2[k], gir2[j], apex))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    o = bm_to_obj(bm, name, root, [m], front=front, angle=8)
    o.location = loc
    o.rotation_euler = rot
    if parent:
        o.parent = parent
    return o


def glint(root, P, tag, loc, s=1.0, parent=None, blink=None):
    """Estrela de brilho de 4 pontas (duas agulhas cruzadas voltadas para a camera); blink = fase em que pisca."""
    piv = empty(root, tag + '_brilhoPivo', loc=loc, parent=parent, rot=(math.radians(-35), 0, 0))
    for k, (sx, sz) in enumerate(((1.0, 0.16), (0.16, 1.0))):
        o = sphere(root, f'{tag}_brilho{k}', 0.05 * s, (0, 0, 0), scale=(sx, 0.05, sz), m=P['glint'], seg=10)
        o.parent = piv
    if blink is not None:
        def fn(o, mb, ph, b=blink):
            k = max(0.0, math.cos(TAU * (ph - b))) ** 6
            sc = 0.05 + 0.95 * k
            o.matrix_basis = mb @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(piv, fn)
    return piv


def ring(root, P, tag, loc, r=0.1, stone=None, gr=None, front=False):
    """Anel de ouro em pe (plano XZ, de frente para a camera) com a pedra cravada em garras no alto."""
    x, y, z = loc
    torus(root, tag + '_aro', (x, y, z), r, r * 0.16, P['gold'], axis='Y', n=28, segs=8, front=front)
    gr = gr or r * 0.55
    cyl(root, tag + '_engaste', gr * 0.62, gr * 0.5, (x, y, z + r + gr * 0.18), r2=gr * 0.85, m=P['gold'], v=12, bev=0.004, front=front)
    for k in range(4):
        a = TAU * k / 4 + math.pi / 4
        tube(root, f'{tag}_garra{k}', [(x + gr * 0.6 * math.cos(a), y + gr * 0.6 * math.sin(a), z + r + gr * 0.3),
                                       (x + gr * 0.78 * math.cos(a), y + gr * 0.78 * math.sin(a), z + r + gr * 0.9)], gr * 0.12, P['gold'], segs=5, front=front)
    return gem(root, tag + '_pedra', gr, (x, y, z + r + gr * 0.95), stone or P['ruby'], front=front)


def jewel_box(root, P, tag, W, D, Hb, z0, rim=0.1, wall=0.065, lid_open=102, lid_h=None, seed=1, front=True):
    """Estojo de veludo aberto (cor da chapa): corpo arredondado, paredes com friso de ouro, pes e fechadura de ouro,
    almofadas com fendas e a tampa aberta (forro capitone com o emblema da chapa no meio e borda de ouro). O que fica
    na frente da tripulacao vai na camada 'front'."""
    cz = z0 + Hb                 # topo das almofadas (onde o assessor pisa)
    zt = cz + rim                # topo das paredes
    box(root, tag + '_corpo', (W, D, Hb), (0, 0, z0 + Hb / 2), m=P['velvet'], bev=0.05, seg=4)
    # paredes acima das almofadas (a da frente cobre os pes do assessor)
    box(root, tag + '_paredeF', (W, wall, rim + 0.03), (0, -D / 2 + wall / 2, cz + (rim - 0.03) / 2), m=P['velvet'], bev=0.025, seg=3, front=front)
    box(root, tag + '_paredeT', (W, wall, rim + 0.03), (0, D / 2 - wall / 2, cz + (rim - 0.03) / 2), m=P['velvet'], bev=0.025, seg=3)
    for sx in (-1, 1):
        box(root, f'{tag}_paredeL{sx}', (wall, D - 0.02, rim + 0.03), (sx * (W / 2 - wall / 2), 0, cz + (rim - 0.03) / 2), m=P['velvet'], bev=0.025, seg=3)
    # friso de ouro no topo das paredes e na base
    xi, yi = W / 2 - wall / 2, D / 2 - wall / 2
    tube(root, tag + '_frisoF', [(-xi, -yi, zt), (xi, -yi, zt)], 0.02, P['gold'], segs=8, front=front)
    tube(root, tag + '_frisoT', [(-xi, yi, zt), (-xi, -yi + 0.02, zt)], 0.02, P['gold'], segs=8)
    tube(root, tag + '_frisoT2', [(xi, yi, zt), (xi, -yi + 0.02, zt)], 0.02, P['gold'], segs=8)
    tube(root, tag + '_frisoT3', [(-xi, yi, zt), (xi, yi, zt)], 0.02, P['gold'], segs=8)
    for sx in (-1, 1):
        sphere(root, f'{tag}_frisoCanto{sx}', 0.026, (sx * xi, -yi, zt), m=P['gold'], seg=12, front=front)
    xb, yb = W / 2 + 0.004, D / 2 + 0.004
    tube(root, tag + '_barraF', [(-xb, -yb, z0 + 0.035), (xb, -yb, z0 + 0.035)], 0.018, P['gold'], segs=8, front=front)
    for sx in (-1, 1):
        tube(root, f'{tag}_barraL{sx}', [(sx * xb, -yb, z0 + 0.035), (sx * xb, yb, z0 + 0.035)], 0.018, P['gold'], segs=8)
        # cantoneiras de ouro (pes) nos quatro cantos
        for sy in (-1, 1):
            sphere(root, f'{tag}_pe{sx}{sy}', 0.06, (sx * (W / 2 - 0.02), sy * (D / 2 - 0.02), z0 + 0.02), scale=(1.0, 1.0, 0.55), m=P['gold'], seg=14, front=front and sy < 0)
            sphere(root, f'{tag}_cantoneira{sx}{sy}', 0.05, (sx * (W / 2 - 0.005), sy * (D / 2 - 0.005), cz - 0.05), scale=(0.7, 0.7, 1.3), m=P['gold_d'], seg=12, front=front and sy < 0)
    # fechadura de ouro com o buraco da chave
    box(root, tag + '_fechadura', (0.12, 0.024, 0.13), (0, -D / 2 - 0.006, cz - 0.04), m=P['gold'], bev=0.012, front=front)
    cyl(root, tag + '_chaveBuraco', 0.016, 0.02, (0, -D / 2 - 0.016, cz - 0.025), m=P['keyhole'], v=12, bev=0.0, rot=(math.pi / 2, 0, 0), front=front)
    box(root, tag + '_chaveFenda', (0.014, 0.02, 0.04), (0, -D / 2 - 0.016, cz - 0.055), m=P['keyhole'], bev=0.0, front=front)
    # almofadas (rolos de veludo claro da chapa com fendas para os aneis)
    nroll = 3
    rr_ = (D - 2 * wall) / (2 * nroll)
    rolls = []
    for k in range(nroll):
        yy = -D / 2 + wall + rr_ * (2 * k + 1)
        cyl(root, f'{tag}_rolo{k}', rr_ * 1.02, W - 2 * wall - 0.01, (0, yy, cz - rr_ * 0.45), m=P['velvet_l'], v=20, bev=0.02, rot=(0, math.pi / 2, 0))
        rolls.append(yy)
    slits = [(rolls[k] + rolls[k + 1]) / 2 for k in range(nroll - 1)]
    # tampa aberta presa na dobradica do fundo
    lid_h = lid_h or 0.12
    lp = empty(root, tag + '_tampaPivo', loc=(0, D / 2 - 0.01, zt), rot=(math.radians(-lid_open), 0, 0))
    objs = [box(root, tag + '_tampa', (W, D, lid_h), (0, -D / 2, lid_h / 2), m=P['velvet_d'], bev=min(0.06, lid_h * 0.45), seg=4),
            box(root, tag + '_forro', (W - 0.1, D - 0.1, 0.03), (0, -D / 2, -0.004), m=P['lining'], bev=0.012)]
    for k, (a, b) in enumerate((((-W / 2, 0), (W / 2, 0)), ((-W / 2, -D), (W / 2, -D)), ((-W / 2, 0), (-W / 2, -D)), ((W / 2, 0), (W / 2, -D)))):
        objs.append(tube(root, f'{tag}_tampaFriso{k}', [(a[0] * 0.985, a[1] - 0.01 * (a[1] < 0) + 0.01 * (a[1] == 0), 0.004),
                                                        (b[0] * 0.985, b[1] - 0.01 * (b[1] < 0) + 0.01 * (b[1] == 0), 0.004)], 0.018, P['gold'], segs=8))
    # capitone: botoes de ouro no forro (os dois do meio dao lugar ao emblema)
    for i in range(4):
        for j in range(3):
            if i in (1, 2) and j == 1:
                continue
            objs.append(sphere(root, f'{tag}_botao{i}{j}', 0.014, ((i - 1.5) * (W - 0.2) / 3.5, -D / 2 + (j - 1) * (D - 0.2) / 3, -0.022), m=P['gold'], seg=8))
    # emblema da chapa no forro (a face de dentro da tampa aberta fica de frente para a camera): V = losango amarelo e
    # circulo azul sobre o forro verde (a bandeira), R = estrela branca sobre o forro vermelho
    objs += [o for o in emblema(root, tag + '_tampaEmblema', (W - 0.1) * 0.62, (D - 0.1) * 0.78, loc=(0, -D / 2, -0.025),
                                rot=(math.pi / 2, 0, 0), depth=0.008) if o.parent == root]
    objs.append(box(root, tag + '_presilha', (0.14, 0.05, 0.06), (0, -D - 0.005, lid_h * 0.5), m=P['gold'], bev=0.014))
    for o in objs:
        o.parent = lp
    return {'cz': cz, 'zt': zt, 'slits': slits, 'rolls': rolls, 'lid': lp, 'lid_top': zt + D * math.sin(math.radians(lid_open)) + 0.02}


def necklace(root, P, tag, rn=0.17, n=22, pend=None, parent=None):
    """Colar de ouro e perolas (aro no plano XZ) com pingente de ouro e a gema da chapa embaixo."""
    piv = empty(root, tag + '_colarPivo', parent=parent)
    for k in range(n):
        a = TAU * k / n + math.pi / 2
        if abs(math.sin(a) + 1) < 0.02:
            continue
        pearl = k % 2 == 0
        o = sphere(root, f'{tag}_conta{k}', 0.026 if pearl else 0.02, (rn * math.cos(a), 0, rn * math.sin(a)), m=P['pearl'] if pearl else P['gold'], seg=10)
        o.parent = piv
    o = box(root, tag + '_pingente', (0.09, 0.03, 0.09), (0, 0, -rn - 0.05), rot=(0, math.pi / 4, 0), m=P['gold'], bev=0.012)
    o.parent = piv
    gem(root, tag + '_pingenteGema', 0.05, (0, -0.02, -rn - 0.05), pend or P['amethyst'], rot=(math.pi / 2, 0, 0), parent=piv)
    return piv


def orbit(piv, rx, ry, z, tilt=0.1, turns=1, phase=0.0, bob_=0.05):
    """Faz o objeto (filho da raiz, em z) dar a volta na torre numa elipse, sempre de frente para a camera."""
    def fn(o, mb, ph):
        a = TAU * (turns * ph + phase)
        pos = Vector((rx * math.cos(a), ry * math.sin(a), z + bob_ * math.sin(2 * a)))
        o.matrix_basis = mb @ Matrix.Translation(pos) @ Matrix.Rotation(tilt * math.cos(a), 4, 'Y') @ Matrix.Rotation(0.25 * math.sin(a), 4, 'Z')
    register_anim(piv, fn)


def main_gem(root, P, tag, loc, r, lights, m=None, col='#c8f0ff', watts=24.0):
    """A joia principal: grande brilhante que flutua e gira devagar no alto (de onde sai o disparo)."""
    piv = empty(root, tag + '_joiaPivo', loc=loc, rot=(math.radians(-30), 0, 0))
    g = gem(root, tag + '_joia', r, (0, 0, 0), m or P['diamond'], rot=(0, 0, 0), crown=0.42, pav=0.95, table=0.52)
    g.parent = piv
    register_anim(piv, bob(amp=0.025, turns=1, axis='Z', spin_axis='Z', sym=8, spin_turns=1))
    for k, (dx, dz, s, b) in enumerate(((-0.6, 0.5, 0.9, 0.0), (0.7, -0.3, 0.7, 0.45), (0.2, 0.9, 0.6, 0.7))):
        glint(root, P, f'{tag}_joiaBrilho{k}', (loc[0] + dx * r, loc[1] - r * 0.8, loc[2] + dz * r), s=s * r / 0.16, blink=b)
    lights.append((loc, col, watts, 1))
    return piv


def pedestal_drum(root, P, tag, r, z1, band=True):
    """Pedestal de concreto branco: base, tambor e tampo com quinas suaves e um friso de ouro."""
    cyl(root, tag + '_pedestalBase', r * 1.08, 0.06, (0, 0, 0.1), m=P['concrete'], v=44, bev=0.02)
    cyl(root, tag + '_pedestal', r * 0.9, z1 - 0.18, (0, 0, (z1 + 0.13 - 0.05) / 2), m=P['concrete'], v=44, bev=0.015)
    cyl(root, tag + '_pedestalTampo', r, 0.06, (0, 0, z1 - 0.03), m=P['concrete'], v=44, bev=0.02)
    if band:
        torus(root, tag + '_pedestalOuro', (0, 0, z1 - 0.1), r * 0.9 + 0.004, 0.014, P['gold'], n=44, segs=6)


def alvorada_column(root, P, tag, x, y, zb, zt, w, t=0.05, axis='X'):
    """Coluna da Alvorada vista de frente: lamina branca larga no alto que afina em curva ate uma ponta no chao."""
    bm = bmesh.new()
    n = 16
    # borda em quarto de circulo: haste fina e vertical no chao, abrindo em arco ate a laje (o vao entre duas colunas
    # vira um arco redondo, como na Alvorada, e nao um dente)
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
    """Pedestal do nivel 3: o Palacio da Alvorada em miniatura. Laje de piso, caixa de vidro escuro recuada, colunata
    de colunas curvas na frente e nas laterais e a laje de cobertura com friso de ouro."""
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
    tube(root, tag + '_lajeOuro', [(-(Wp + 0.14) / 2, -(Dp + 0.14) / 2 - 0.004, z1 - 0.035), ((Wp + 0.14) / 2, -(Dp + 0.14) / 2 - 0.004, z1 - 0.035)],
         0.012, P['gold'], segs=6)


def coins(root, P, tag, loc, n=6, seed=2):
    """Pilha de moedas de ouro (lisas, sem cunho) e algumas soltas."""
    rr = random.Random(seed)
    x, y, z = loc
    for k in range(n):
        cyl(root, f'{tag}_moeda{k}', 0.045, 0.014, (x + rr.uniform(-0.006, 0.006), y + rr.uniform(-0.006, 0.006), z + 0.008 + 0.015 * k), m=P['gold'], v=16, bev=0.003)
    for k in range(3):
        a = rr.uniform(0, TAU)
        cyl(root, f'{tag}_moedaSolta{k}', 0.045, 0.014, (x + 0.1 * math.cos(a), y + 0.08 * math.sin(a), z + 0.012), m=P['gold_d'], v=16, bev=0.003,
            rot=(rr.uniform(-0.3, 0.3), rr.uniform(-0.3, 0.3), 0))


def gold_bars(root, P, tag, loc, rot=0.3):
    """Tres barras de ouro (troncos de piramide lisos) empilhadas."""
    x, y, z = loc
    c, s = math.cos(rot), math.sin(rot)
    for k, (dx, dz) in enumerate(((-0.07, 0.0), (0.07, 0.0), (0.0, 0.05))):
        cyl(root, f'{tag}_barra{k}', 0.08, 0.05, (x + dx * c, y + dx * s, z + 0.025 + dz), r2=0.06, m=P['gold'], v=4, bev=0.008, rot=(0, 0, rot + math.pi / 4))


def cushion_gems(root, P, tag, B, W, seed=3, rings=(), loose=()):
    """Aneis nas fendas e gemas soltas sobre as almofadas. rings: [(x, fenda, raio, pedra)], loose: [(x, rolo, raio, pedra)]."""
    cz = B['cz']
    for k, (x, si, r, st) in enumerate(rings):
        ring(root, P, f'{tag}_anel{k}', (x, B['slits'][si], cz - 0.02 + r * 0.3), r=r, stone=st)
    rr = random.Random(seed)
    for k, (x, ri, r, st) in enumerate(loose):
        gem(root, f'{tag}_gema{k}', r, (x, B['rolls'][ri], cz + r * 0.35), st, rot=(rr.uniform(0.4, 0.9), rr.uniform(-0.4, 0.4), rr.uniform(0, TAU)))


# ---------------------------------------------------------------- nivel 1: estojo pequeno sobre tambor de concreto
def build_mg1(P, root):
    plot(root, P, 'mg1')
    lights = []
    z0 = 0.4
    pedestal_drum(root, P, 'mg1', 0.5, z0)
    W, D = 0.86, 0.6
    B = jewel_box(root, P, 'mg1', W, D, 0.24, z0, rim=0.1)
    cushion_gems(root, P, 'mg1', B, W, rings=[(-0.24, 1, 0.075, P['ruby'])], loose=[(-0.05, 0, 0.05, P['emerald']), (-0.26, 0, 0.042, P['sapphire'])])
    top = (-0.06, 0.06, B['lid_top'] + 0.1)
    main_gem(root, P, 'mg1', top, 0.15, lights)
    # lascas de gema girando em volta (os antigos vaga-lumes)
    for ring_i in range(2):
        piv = empty(root, f'mg1_lascaPivo{ring_i}', loc=top)
        for k in range(3):
            a = TAU * k / 3 + ring_i
            g = gem(root, f'mg1_lasca{ring_i}{k}', 0.035, (0.34 * math.cos(a), 0.3 * math.sin(a), 0.1 * math.sin(2 * a + ring_i)),
                    (P['amethyst'], P['topaz'], P['emerald'], P['ruby'])[(k + ring_i) % 4], rot=(0.5, 0.3, a))
            g.parent = piv
        register_anim(piv, spin('Z', sym=3, turns=1 if ring_i == 0 else -1))
    coins(root, P, 'mg1_moedas', (0.5, -0.5, G))
    glint(root, P, 'mg1_brilhoAnel', (-0.2, -0.2, B['cz'] + 0.22), s=0.6, blink=0.3)
    return {'slots': [(0.22, -0.08, B['cz'] + 0.0)], 'lights': lights, 'points': {'top': top}}


# ---------------------------------------------------------------- nivel 2: pedestal alto, estojo maior e o colar orbitando
def build_mg2(P, root):
    plot(root, P, 'mg2')
    lights = []
    z0 = 0.58
    cyl(root, 'mg2_degrau', 0.64, 0.08, (0, 0, 0.11), m=P['concrete'], v=44, bev=0.025)
    pedestal_drum(root, P, 'mg2', 0.48, z0)
    W, D = 0.98, 0.68
    B = jewel_box(root, P, 'mg2', W, D, 0.26, z0, rim=0.11)
    cushion_gems(root, P, 'mg2', B, W, rings=[(-0.3, 1, 0.08, P['ruby']), (-0.05, 0, 0.065, P['emerald'])],
                 loose=[(-0.18, 0, 0.05, P['sapphire']), (0.02, 2, 0.045, P['topaz']), (-0.36, 2, 0.04, P['amethyst'])])
    top = (-0.08, 0.08, B['lid_top'] + 0.12)
    main_gem(root, P, 'mg2', top, 0.17, lights)
    nk = necklace(root, P, 'mg2', rn=0.15)
    orbit(nk, 0.82, 0.55, B['cz'] + 0.2)
    coins(root, P, 'mg2_moedas', (0.54, -0.48, G), n=7)
    glint(root, P, 'mg2_brilhoAnel', (-0.26, -0.22, B['cz'] + 0.24), s=0.6, blink=0.3)
    lights.append(((-0.3, -0.1, B['cz'] + 0.15), '#ff6fa8', 8.0, 0))
    return {'slots': [(0.26, -0.1, B['cz'])], 'lights': lights, 'points': {'top': top}}


# ---------------------------------------------------------------- nivel 3: colunas da Alvorada, estojo grande, colar e tesouro
def build_mg3(P, root):
    plot(root, P, 'mg3')
    lights = []
    z0 = 0.74
    pedestal_alvorada(root, P, 'mg3', 1.02, 0.72, z0)
    W, D = 1.14, 0.78
    B = jewel_box(root, P, 'mg3', W, D, 0.28, z0, rim=0.12, lid_h=0.14)
    cushion_gems(root, P, 'mg3', B, W, rings=[(-0.36, 1, 0.09, P['ruby']), (-0.1, 0, 0.07, P['emerald']), (0.42, 1, 0.07, P['sapphire'])],
                 loose=[(-0.24, 0, 0.055, P['sapphire']), (0.04, 2, 0.05, P['topaz']), (-0.42, 2, 0.045, P['amethyst']), (-0.16, 2, 0.05, P['diamond'])])
    top = (-0.1, 0.1, B['lid_top'] + 0.14)
    main_gem(root, P, 'mg3', top, 0.2, lights)
    nk = necklace(root, P, 'mg3', rn=0.17)
    orbit(nk, 0.9, 0.62, B['cz'] + 0.25)
    coins(root, P, 'mg3_moedas', (0.46, -0.42, 0.13), n=8)
    gold_bars(root, P, 'mg3_ouro', (-0.47, -0.42, 0.13))
    gem(root, 'mg3_gemaChao', 0.06, (-0.3, -0.6, G + 0.05), P['amethyst'], rot=(0.6, 0.2, 0.5))
    glint(root, P, 'mg3_brilhoAnel', (-0.32, -0.26, B['cz'] + 0.27), s=0.7, blink=0.3)
    glint(root, P, 'mg3_brilhoOuro', (-0.47, -0.48, 0.3), s=0.6, blink=0.75)
    lights.append(((-0.3, -0.1, B['cz'] + 0.15), '#ff6fa8', 9.0, 0))
    return {'slots': [(0.3, -0.12, B['cz'])], 'lights': lights, 'points': {'top': top}}


# ---------------------------------------------------------------- Corrente de Ouro: corrente grossa enrolada e o medalhao
def chain(root, P, tag, pts, m, link=0.11, wire=0.017, front=False):
    """Corrente de elos ovais (um em pe, outro deitado) ao longo da polilinha pts, numa malha so."""
    pts = [Vector(p) for p in pts]
    # reamostra a polilinha em passos iguais
    segl = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(segl)
    step = link * 0.72
    n = max(2, int(total / step))
    samples = []
    for k in range(n + 1):
        d = total * k / n
        i = 0
        while i < len(segl) - 1 and d > segl[i]:
            d -= segl[i]
            i += 1
        t = min(1.0, d / max(1e-6, segl[i]))
        samples.append(pts[i].lerp(pts[i + 1], t))
    bm = bmesh.new()
    prev = None
    for k in range(n):
        c = (samples[k] + samples[k + 1]) / 2
        tdir = (samples[k + 1] - samples[k]).normalized()
        ref = Vector((0, 0, 1)) if abs(tdir.z) < 0.9 else Vector((1, 0, 0))
        nn = tdir.cross(ref).normalized()
        if prev is not None and nn.dot(prev) < 0:
            nn = -nn
        prev = nn
        side = nn if k % 2 == 0 else tdir.cross(nn).normalized()
        L2, Wl = link / 2, link * 0.3
        ring_ = []
        for j in range(16):
            a = TAU * j / 16
            ring_.append(c + tdir * (L2 - Wl) * (1 if math.cos(a) > 0 else -1) + tdir * Wl * math.cos(a) + side * Wl * math.sin(a))
        tube_into(bm, ring_, wire, segs=6, closed=True)
    return bm_to_obj(bm, tag, root, [m], front=front, angle=75)


def medallion(root, P, tag, r, stone):
    """Medalhao redondo de ouro (plano XZ) com aro torcido, raios gravados e a gema no centro."""
    objs = [cyl(root, tag + '_disco', r, 0.05, (0, 0, 0), m=P['gold'], v=36, bev=0.012, rot=(math.pi / 2, 0, 0)),
            torus(root, tag + '_aro', (0, 0, 0), r, 0.022, P['gold_d'], axis='Y', n=40, segs=8),
            torus(root, tag + '_aroInterno', (0, -0.02, 0), r * 0.62, 0.01, P['gold_d'], axis='Y', n=32, segs=6),
            torus(root, tag + '_argola', (0, 0, r + 0.04), 0.036, 0.011, P['gold'], axis='X', n=16, segs=6)]
    for k in range(12):
        a = TAU * k / 12
        objs.append(sphere(root, f'{tag}_perola{k}', 0.016, (r * 0.8 * math.cos(a), -0.028, r * 0.8 * math.sin(a)), m=P['pearl'], seg=8))
    objs.append(gem(root, tag + '_gema', r * 0.42, (0, -0.04, 0), stone, rot=(math.pi / 2, 0, 0)))
    return objs


def build_mgL(P, root):
    plot(root, P, 'mgL')
    lights = []
    z0 = 0.56
    cyl(root, 'mgL_degrau', 0.6, 0.08, (0, 0, 0.11), m=P['concrete'], v=44, bev=0.025)
    pedestal_drum(root, P, 'mgL', 0.42, z0)
    W, D = 0.86, 0.6
    B = jewel_box(root, P, 'mgL', W, D, 0.24, z0, rim=0.1, front=False)   # aqui o ourives fica no chao, na frente de tudo
    cushion_gems(root, P, 'mgL', B, W, rings=[(-0.24, 1, 0.07, P['ruby'])], loose=[(0.22, 0, 0.045, P['emerald']), (-0.1, 2, 0.04, P['topaz'])])
    # corrente grossa enrolada no pedestal, subindo para dentro do estojo
    hel = []
    for k in range(49):
        t = k / 48
        a = -math.pi / 2 - 1.0 + TAU * 1.35 * t
        rad = 0.5 - 0.06 * t
        hel.append((rad * math.cos(a), rad * math.sin(a), 0.2 + 0.36 * t))
    hel.append((0.12, -0.1, B['cz'] + 0.04))
    chain(root, P, 'mgL_correnteEnrolada', hel, P['gold'], link=0.12, wire=0.02)
    # medalhao flutuando no alto, preso por uma corrente que desce para o estojo
    top = (0.0, 0.04, B['lid_top'] + 0.12)
    mp = empty(root, 'mgL_medalhaoPivo', loc=top)
    for o in medallion(root, P, 'mgL_medalhao', 0.2, P['amethyst']):
        o.parent = mp
    hang = chain(root, P, 'mgL_correntePendente', [(0, 0.01, -0.21), (0.03, -0.02, -0.42), (0.1, -0.08, -(top[2] - B['cz']) + 0.02)], P['gold'], link=0.09, wire=0.014)
    hang.parent = mp
    register_anim(mp, lambda o, mb, ph: setattr(o, 'matrix_basis', Matrix.Translation((0, 0, 0.02 * math.sin(TAU * ph))) @ mb @ Matrix.Rotation(0.18 * math.sin(TAU * ph), 4, 'Z')))
    lights.append((top, P['_luz_gema'], 18.0, 1))
    glint(root, P, 'mgL_brilho', (top[0] - 0.12, top[1] - 0.1, top[2] + 0.12), s=0.8, blink=0.2)
    # faiscas douradas que piscam entre o medalhao e a corrente (o raio que salta)
    for k in range(4):
        a0 = TAU * k / 4 + 0.4
        pts = []
        for j in range(7):
            t = j / 6
            a = a0 + 0.7 * t
            rr_ = 0.26 + 0.05 * math.sin(j * 2.3 + k)
            pts.append((rr_ * math.cos(a), top[1] + 0.12 * math.sin(a), top[2] - 0.05 - 0.38 * t + 0.03 * math.sin(j * 3.1)))
        arc = tube(root, f'mgL_arco{k}', pts, 0.009, P['spark'], segs=5)

        def blink(o, mb, ph, k=k):
            on = (int(ph * 16) + k * 5) % 7 < 2
            o.matrix_basis = mb @ Matrix.Diagonal((1, 1, 1, 1) if on else (0.001, 0.001, 0.001, 1))
        register_anim(arc, blink)
    gold_bars(root, P, 'mgL_ouro', (-0.54, -0.44, G))
    coins(root, P, 'mgL_moedas', (0.58, -0.36, G), n=5)
    return {'slots': [(0.3, -0.62, G)], 'lights': lights, 'points': {'top': top}, 'margin': (0.2, 0.95, 0.2, 0.3)}


# ---------------------------------------------------------------- Relogio de Ouro: relogio de pulso gigante em pe que reflete o sol
def build_mgS(P, root):
    plot(root, P, 'mgS')
    lights = []
    z0 = 0.42
    cyl(root, 'mgS_degrau', 0.62, 0.08, (0, 0, 0.11), m=P['concrete'], v=44, bev=0.025)
    pedestal_drum(root, P, 'mgS', 0.46, z0)
    # almofada de veludo onde o relogio fica em pe
    box(root, 'mgS_almofada', (0.6, 0.5, 0.14), (0, 0.06, z0 + 0.06), m=P['velvet'], bev=0.06, seg=4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sphere(root, f'mgS_borla{sx}{sy}', 0.03, (sx * 0.29, 0.06 + sy * 0.24, z0 + 0.06), m=P['gold'], seg=10)
    # pulseira de elos em volta de uma elipse (de lado, plano YZ) e a caixa na frente
    Rz, Ry = 0.46, 0.26
    cz = z0 + 0.12 + Rz
    cy = 0.1
    case_y = cy - Ry
    nseg = 26
    for k in range(nseg):
        a0 = TAU * k / nseg
        a1 = TAU * (k + 0.8) / nseg
        p0 = Vector((0, cy + Ry * math.cos(a0 + math.pi), cz + Rz * math.sin(a0 + math.pi)))
        p1 = Vector((0, cy + Ry * math.cos(a1 + math.pi), cz + Rz * math.sin(a1 + math.pi)))
        mid = (p0 + p1) / 2
        if (mid - Vector((0, case_y, cz))).length < 0.36:
            continue   # a caixa fica aqui
        d = (p1 - p0)
        ang = math.atan2(d.z, d.y)
        box(root, f'mgS_elo{k}', (0.12, d.length, 0.04), mid, rot=(ang, 0, 0), m=P['gold'], bev=0.012)
        for sx in (-1, 1):
            box(root, f'mgS_eloLado{k}{sx}', (0.07, d.length * 1.05, 0.036), (sx * 0.1, mid.y, mid.z), rot=(ang, 0, 0), m=P['gold_d'], bev=0.012)
    # caixa redonda, luneta, mostrador creme com indices de ouro (sem numeros), coroa e o vidro que reflete
    R = 0.34
    cyl(root, 'mgS_caixa', R, 0.13, (0, case_y, cz), m=P['gold'], v=48, bev=0.03, rot=(math.pi / 2, 0, 0))
    torus(root, 'mgS_luneta', (0, case_y - 0.07, cz), R - 0.02, 0.035, P['gold'], axis='Y', n=48, segs=8)
    cyl(root, 'mgS_mostrador', R - 0.05, 0.02, (0, case_y - 0.062, cz), m=mat('mostrador_creme', '#fbf2dc', rough=0.4, var=0.0, bump=0.0), v=40, bev=0.002, rot=(math.pi / 2, 0, 0))
    for k in range(12):
        a = TAU * k / 12
        big = k % 3 == 0
        box(root, f'mgS_indice{k}', (0.02 if big else 0.014, 0.012, 0.06 if big else 0.04), ((R - 0.1) * math.cos(a), case_y - 0.075, cz + (R - 0.1) * math.sin(a)),
            rot=(0, math.pi / 2 - a, 0), m=P['gold_d'], bev=0.003)
    for sx in (-1, 1):
        for sz in (-1, 1):
            box(root, f'mgS_alca{sx}{sz}', (0.06, 0.1, 0.12), (sx * 0.13, case_y + 0.02, cz + sz * (R + 0.02)), m=P['gold'], bev=0.02)
    cyl(root, 'mgS_coroa', 0.05, 0.07, (R + 0.04, case_y, cz), m=P['gold'], v=16, bev=0.01, rot=(0, math.pi / 2, 0))
    hand = mat('ponteiro', '#3a2a4a', rough=0.4, var=0.0, bump=0.0)
    # dez e dez, como na vitrine: ponteiro das horas no 10 e o dos minutos no 2 (angulo a partir do 12, sentido horario)
    for name, th, ln, wd, dy in (('Hora', -math.radians(60), 0.15, 0.026, 0.082), ('Min', math.radians(60), 0.22, 0.02, 0.086)):
        box(root, 'mgS_ponteiro' + name, (wd, 0.01, ln), (math.sin(th) * ln / 2, case_y - dy, cz + math.cos(th) * ln / 2), rot=(0, th, 0), m=hand, bev=0.004)
    sp = empty(root, 'mgS_segundoPivo', loc=(0, case_y - 0.092, cz))
    kids(sp, box(root, 'mgS_ponteiroSeg', (0.008, 0.006, 0.26), (0, 0, 0.09), m=mat('ponteiro_rubi', '#d23a5a', rough=0.4, var=0, bump=0), bev=0.002))
    register_anim(sp, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(TAU * ph, 4, 'Y')))
    sphere(root, 'mgS_centro', 0.024, (0, case_y - 0.094, cz), m=P['gold'], seg=10)
    vidro = mat('vidro_relogio', '#eaf6ff', rough=0.03, var=0.0, bump=0.0)
    o = sphere(root, 'mgS_vidro', R - 0.05, (0, case_y - 0.07, cz), scale=(1, 0.12, 1), m=vidro, seg=32)
    bsdf = next(nd for nd in vidro.node_tree.nodes if nd.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Alpha'].default_value = 0.18
    # reflexo do sol no vidro (duas faixas de luz em diagonal) e as estrelas de brilho
    for k, (off, w) in enumerate(((-0.08, 0.05), (0.04, 0.025))):
        box(root, f'mgS_reflexo{k}', (w, 0.006, 0.36 - 0.1 * k), (off, case_y - 0.112, cz + 0.04), rot=(0, -0.7, 0), m=P['glint'], bev=0.003)
    top = (0, case_y - 0.1, cz)
    lights.append((top, '#ffe9a8', 22.0, 1))
    glint(root, P, 'mgS_brilho0', (-0.2, case_y - 0.16, cz + 0.22), s=1.1, blink=0.0)
    glint(root, P, 'mgS_brilho1', (0.26, case_y - 0.14, cz - 0.16), s=0.7, blink=0.5)
    # estojinho fechado e moedas no pe
    box(root, 'mgS_estojinho', (0.2, 0.16, 0.12), (-0.6, -0.36, G + 0.06), rot=(0, 0, 0.3), m=P['velvet'], bev=0.04, seg=3)
    box(root, 'mgS_estojinhoTampa', (0.21, 0.17, 0.045), (-0.6, -0.36, G + 0.13), rot=(0, 0, 0.3), m=P['velvet_d'], bev=0.02, seg=3)
    box(root, 'mgS_estojinhoFecho', (0.03, 0.02, 0.03), (-0.57, -0.445, G + 0.11), rot=(0, 0, 0.3), m=P['gold'], bev=0.006)
    coins(root, P, 'mgS_moedas', (-0.5, 0.4, G), n=6)
    # bandeirinha da chapa espetada no lote, atras e a direita do relogio
    bandeira_chapa(root, 'mgS_bandeira', (0.5, 0.3, G), h=0.42, w=0.22, fh=0.14)
    return {'slots': [(0.38, -0.52, G)], 'lights': lights, 'points': {'top': top}}


# ---------------------------------------------------------------- assessores das joias (tripulacao)
def scepter(root, P, tag, length=0.62, stone=None, gr=0.04):
    """Cetro de ouro ao longo do Z local (empunhadura em z = 0) com uma gema lapidada no alto."""
    zt = length - 0.26
    objs = [tube(root, tag + '_cetro', [(0, 0, -0.26), (0, 0, zt)], 0.012, P['gold'], segs=8, rfun=lambda t: 0.011 + 0.004 * t),
            sphere(root, tag + '_cetroPomo', 0.02, (0, 0, -0.27), m=P['gold'], seg=10),
            torus(root, tag + '_cetroAnel', (0, 0, zt - 0.02), 0.02, 0.008, P['gold_d'], n=12, segs=5),
            cyl(root, tag + '_cetroGarra', gr * 0.55, gr * 0.6, (0, 0, zt + gr * 0.2), r2=gr * 0.9, m=P['gold'], v=10, bev=0.003)]
    objs.append(gem(root, tag + '_cetroGema', gr, (0, 0, zt + gr * 1.0), stone or P['diamond'], rot=(0, 0, 0)))
    return objs


def tie(root, pr, tag, m):
    """Gravata no peito (filha do corpo; o corpo olha para +X local) e a gola branca."""
    body = pr['body']
    shirt = mat('camisa_branca', '#f6f2ea', rough=0.8, var=0.0, bump=0.02)
    objs = [box(root, tag + '_gola', (0.012, 0.05, 0.035), (0.068, 0.0, 0.466), rot=(0, -0.5, 0), m=shirt, bev=0.006),
            blob(root, tag + '_gravataNo', 0.014, (0.08, 0.0, 0.452), (0.7, 1.0, 1.0), m),
            box(root, tag + '_gravata', (0.01, 0.026, 0.12), (0.087, 0.0, 0.385), rot=(0, 0.08, 0), m=m, bev=0.005)]
    for o in objs:
        o.parent = body
    return objs


def pearl_collar(root, P, pr, tag, n=14):
    """Colar de perolas no pescoco."""
    for k in range(n):
        a = TAU * k / n
        o = sphere(root, f'{tag}_perola{k}', 0.011, (0.074 * math.cos(a), 0.074 * math.sin(a), 0.462 - 0.012 * math.cos(a)), m=P['pearl'], seg=8)
        o.parent = pr['body']


def tiara(root, P, pr, tag, stone):
    """Tiara de ouro com uma gema na frente."""
    hc = Vector((0.006, 0, 0.055))
    t = torus(root, tag + '_tiara', (0, 0, 0), 0.07, 0.007, P['gold'], n=24, segs=5)
    t.parent = pr['head']
    t.location = hc + Vector((-0.004, 0, 0.045))
    t.rotation_euler = (0, math.radians(-14), 0)
    g = gem(root, tag + '_tiaraGema', 0.016, (0, 0, 0), stone, rot=(0, math.pi / 2, 0))
    g.parent = pr['head']
    g.location = hc + Vector((0.068, 0, 0.07))


def loupe(root, P, pr, tag):
    """Lupa de joalheiro presa no olho direito."""
    hc = Vector((0.006, 0, 0.055))
    o = cyl(root, tag + '_lupa', 0.013, 0.022, (0, 0, 0), r2=0.011, m=P['gold'], v=12, bev=0.002, rot=(0, math.pi / 2, 0))
    o.parent = pr['head']
    o.location = hc + Vector((0.074, -0.026, 0.016))
    o = cyl(root, tag + '_lupaLente', 0.01, 0.004, (0, 0, 0), m=P['glint'], v=12, bev=0.0, rot=(0, math.pi / 2, 0))
    o.parent = pr['head']
    o.location = hc + Vector((0.086, -0.026, 0.016))


def marca_peito(root, pr, tag, x, y=0.0, z=0.405, r=0.026, rz=math.pi / 2):
    """Chapa R: estrela branca no peito (filha do corpo, que olha para +X local; rz gira a estrela para a normal da roupa).
    A chapa V nao leva nada aqui: o amarelo e o verde da roupa ja fazem a camisa da selecao."""
    if CHAPA == 'R':
        return estrela_peito(root, tag, pr['body'], (x, y, z), r=r, rot=(0, 0, rz))
    return []


def build_apprentice(P, root):
    """Ajudante das joias: camisa da chapa, colete de veludo, gravata dourada, cetro com diamante."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(tunic=cor('camisa'), vest=P['velvet'] if V_ else P['velvet_d'], head='hair',
                                         hair_m=mat('cabelo_escuro', '#3a2416', rough=0.7, var=0.03, bump=0.25),
                                         belt=None, bare_hands=True, sleeve=cor('camisa'), bracer=cor('gola'), pants=cor('calca'),
                                         boot_m=mat('sapato_preto', '#1e1a18', rough=0.35, var=0.0, bump=0.02)))
    tie(root, pr, tag, P['gold'])
    marca_peito(root, pr, tag, 0.087, y=-0.042, z=0.4, r=0.026, rz=1.26)   # do lado da camera (a gravata fica no meio)
    hold(pr, 'R', *scepter(root, P, tag, length=0.6, gr=0.034))
    return pr


def build_mage(P, root):
    """Assessora das joias: vestido da chapa com barra e faixa (V amarelo com verde, R vermelho com branco), coque,
    colar de perolas e cetro com a gema da chapa."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(robe=True, robe_m=P['robe'], trim=P['trim_c'], tunic=P['robe'], sleeve=P['robe'], sash=P['trim_c'],
                                         head='hair', topknot=True, hair_m=mat('cabelo_preto', '#2a1a12', rough=0.7, var=0.03, bump=0.25),
                                         scarf=None, belt=None, bare_hands=True))
    pearl_collar(root, P, pr, tag)
    marca_peito(root, pr, tag, 0.086, z=0.392, r=0.03)
    tiara(root, P, pr, tag, P['ruby'])
    hold(pr, 'R', *scepter(root, P, tag, length=0.66, stone=P['amethyst'], gr=0.04))
    return pr


def build_archmage(P, root):
    """Joalheiro-chefe: barba branca, manto da chapa (V verde, R vermelho escuro) com mantelete de veludo (V amarelo,
    R vermelho), gola de ouro, lupa e cetro de diamante."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(robe=True, robe_m=P['robe_d'], trim=P['gold'], tunic=P['robe_d'], sleeve=P['robe'], sash=P['gold'],
                                         head='hair', hair_m=P['white'], beard=P['white'], brow_m=P['white'], belt=None, bare_hands=True,
                                         mantle=P['velvet_l'] if V_ else P['velvet'], mantle_trim=P['trim_c'], gold_collar=True))
    loupe(root, P, pr, tag)
    marca_peito(root, pr, tag, 0.088, y=-0.068, z=0.41, r=0.028, rz=1.07)   # de lado, fora da barba
    hold(pr, 'R', *scepter(root, P, tag, length=0.72, gr=0.05))
    return pr


def build_engineer(P, root):
    """Ourives da corrente: camisa da chapa, lenco (V verde, R branco), avental de couro, oculos de protecao e o gancho
    de ouro que puxa a corrente."""
    tag = root['set']
    apron = mat('avental', '#7b5233', rough=0.7, var=0.04, bump=0.15)
    pr = build_person(P, root, tag, dict(tunic=cor('camisa'), sleeve=cor('camisa'), vest=apron, head='bald', scarf=P['trim_c'], belt=P['leather'],
                                         bare_hands=False, goggles=True, pants=cor('calca')))
    marca_peito(root, pr, tag, 0.095, z=0.392, r=0.03)
    w = [tube(root, tag + '_vara', [(0, 0, -0.06), (0, 0, 0.2)], 0.012, P['gold_d'], segs=6),
         torus(root, tag + '_gancho', (0.0, 0, 0.22), 0.022, 0.008, P['gold'], axis='Y', n=12, segs=5)]
    hold(pr, 'R', *w)
    return pr


def build_priestess(P, root):
    """Polidora do relogio: vestido claro com mangas e mantelete da chapa, faixa (V verde, R branco) e o espelho de mao
    que devolve o brilho do sol."""
    tag = root['set']
    pr = build_person(P, root, tag, dict(robe=True, robe_m=P['robe_l'], trim=P['gold'], tunic=P['robe_l'], sleeve=P['robe'], sash=P['trim_c'],
                                         head='hair', hair_m=mat('cabelo_castanho', '#4a2a18', rough=0.7, var=0.03, bump=0.25),
                                         belt=None, bare_hands=True, mantle=P['velvet'], mantle_trim=P['gold']))
    marca_peito(root, pr, tag, 0.105, z=0.405, r=0.03)
    tiara(root, P, pr, tag, P['topaz'])
    mirror = [tube(root, tag + '_espelhoCabo', [(0, 0, -0.08), (0, 0, 0.12)], 0.011, P['gold'], segs=8),
              torus(root, tag + '_espelhoAro', (0, 0, 0.19), 0.06, 0.012, P['gold'], axis='X', n=20, segs=6),
              cyl(root, tag + '_espelho', 0.055, 0.008, (0, 0, 0.19), m=P['glint'], v=20, bev=0.002, rot=(0, math.pi / 2, 0))]
    hold(pr, 'R', *mirror)
    return pr


IDLE_N, CAST_N = 12, 8


def mage_state(mode, f, big_staff=False):
    """idle: respira e olha em volta, cetro de pe; cast: ergue o cetro, gira e aponta para a frente (quadro 3 = disparo)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.13, 0.3 + 0.006 * s), grip_R=(0.05, 0.0, 1.0), hand_L=(0.1, 0.08, 0.3 + 0.01 * s),
                    pole_L=(-0.4, 1.0, -0.4), breathe=s, head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.22, ph=ph)
    seq = [
        dict(hand_R=(0.08, -0.12, 0.36), grip_R=(0.1, 0, 1.0), hand_L=(0.12, 0.06, 0.34)),
        dict(hand_R=(0.02, -0.1, 0.52), grip_R=(-0.25, 0, 1.0), hand_L=(0.16, 0.1, 0.42), lean=-0.05),
        dict(hand_R=(0.0, -0.08, 0.6), grip_R=(-0.35, 0, 1.0), hand_L=(0.2, 0.12, 0.48), lean=-0.08),
        dict(hand_R=(0.2, -0.06, 0.46), grip_R=(1.0, 0, 0.55), hand_L=(0.2, 0.14, 0.4), lean=0.1),
        dict(hand_R=(0.22, -0.06, 0.44), grip_R=(1.0, 0, 0.45), hand_L=(0.16, 0.14, 0.36), lean=0.12),
        dict(hand_R=(0.18, -0.08, 0.4), grip_R=(0.8, 0, 0.7), hand_L=(0.13, 0.12, 0.32), lean=0.07),
        dict(hand_R=(0.12, -0.11, 0.35), grip_R=(0.4, 0, 1.0), hand_L=(0.11, 0.1, 0.31), lean=0.03),
        dict(hand_R=(0.1, -0.13, 0.31), grip_R=(0.1, 0, 1.0), hand_L=(0.1, 0.08, 0.3), lean=0.0),
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
    # cast: puxa a corrente com o gancho e se encolhe com a faisca
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
    'towers': [('mg1', 'Joias N1', build_mg1), ('mg2', 'Joias N2', build_mg2), ('mg3', 'Joias N3', build_mg3),
               ('mgL', 'Corrente de Ouro', build_mgL), ('mgS', 'Relogio de Ouro', build_mgS)],
    'crews': [crew('mgA', 'Ajudante das joias', build_apprentice, mage_state), crew('mgB', 'Assessora das joias', build_mage, mage_state),
              crew('mgC', 'Joalheiro-chefe', build_archmage, mage_state), crew('mgE', 'Ourives da corrente', build_engineer, engineer_state),
              crew('mgP', 'Polidora do relogio', build_priestess, priestess_state)],
}


def show():
    build_family(SPEC)
    for it in SPEC['crews']:
        it['show'](BUILT[it['key']], palette2(), SETS[it['key']])
    layout_show(SPEC)


if __name__ == '__main__':
    main(FAM, SPEC)
