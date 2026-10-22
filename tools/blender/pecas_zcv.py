"""Pecas comuns da Central do Zap, da CPI e do Banco Vorcash (Ninguem Sobe a Rampa): balao de mensagem, placas de
canto arredondado (celulares, mesas, portas), gravata, oculos, fone de ouvido e cracha da tripulacao.
Os baloes saem nas cores da chapa (CHAPA=V verde e amarelo, CHAPA=R vermelho e branco; ver chapa.py), e as marcas da
chapa na roupa (gola da camisa, estrela no peito, broche na lapela) tambem moram aqui.

Uso nos scripts das torres (so le o lib.py, o lote_brasilia.py e o chapa.py, nao mexe neles):
    from pecas_zcv import *
"""
import math
from mathutils import Vector, Matrix
from lib import TAU, mat, cyl, box, tube, torus, sphere, lathe, blob, empty, kids, register_anim, glow_mat
from lote_brasilia import grupo, prism_xz
from chapa import CHAPA, PAL, cor, estrela, emblema, estrela_peito


# ---------------------------------------------------------------- formas
def rrect(w, h, r, n=5, cx=0.0, cz=0.0):
    """Contorno de retangulo de canto arredondado no plano XZ (centro em cx, cz), sentido anti-horario."""
    r = min(r, w / 2 - 1e-4, h / 2 - 1e-4)
    pts = []
    for k, (sx, sz, a0) in enumerate(((1, -1, -math.pi / 2), (1, 1, 0.0), (-1, 1, math.pi / 2), (-1, -1, math.pi))):
        ox, oz = cx + sx * (w / 2 - r), cz + sz * (h / 2 - r)
        for i in range(n + 1):
            a = a0 + (math.pi / 2) * i / n
            pts.append((ox + r * math.cos(a), oz + r * math.sin(a)))
    return pts


def slab(root, name, w, h, d, m, r=None, loc=(0, 0, 0), rot=(0, 0, 0), bev=None, front=False, n=5):
    """Placa grossa de canto arredondado (celular, tampo, porta): largura em X, altura em Z, espessura em Y.
    loc e o centro da placa."""
    o = prism_xz(root, name, rrect(w, h, r if r is not None else min(w, h) * 0.18, n=n), d, m,
                 bev=bev if bev is not None else min(0.03, d * 0.32), front=front)
    o.location = loc
    o.rotation_euler = rot
    return o


# ---------------------------------------------------------------- balao de mensagem (sem texto: tres pontinhos)
# cores dos baloes por chapa: (corpo, corpo claro, pontinhos do corpo, pontinhos do claro)
BALAO = {'V': ('#2db35a', '#ffd84a', '#fbfdfb', '#1f9a4c'),     # verde com pontinhos brancos / amarelo com pontinhos verdes
         'R': ('#e0383b', '#fff6f2', '#fffaf8', '#d6282b')}     # vermelho com pontinhos brancos / branco com pontinhos vermelhos


def bubble_mats():
    """(corpo, corpo claro, pontinho) dos baloes na cor da chapa; o pontinho do balao claro sai de bubble_dot_light()."""
    c = BALAO[CHAPA]
    return (mat('balao_zap_' + CHAPA, c[0], rough=0.45, var=0.05, bump=0.03, sheen=0.3),
            mat('balao_zap_claro_' + CHAPA, c[1], rough=0.45, var=0.03, bump=0.03, sheen=0.3),
            mat('balao_ponto_' + CHAPA, c[2], rough=0.5, var=0.0, bump=0.0))


def bubble_dot_light():
    return mat('balao_ponto_claro_' + CHAPA, BALAO[CHAPA][3], rough=0.5, var=0.0, bump=0.0)


def chat_bubble(root, name, loc, s=1.0, rot=(0, 0, 0), light=False, tail=1, both=False, parent=None, dots=True, w=0.2, h=0.14, d=0.055):
    """Balao de mensagem de canto bem arredondado, voltado para -Y, com o rabinho embaixo (tail = -1 esquerda,
    1 direita, 0 sem) e os tres pontinhos de 'digitando'. both: pontinhos dos dois lados (balao que gira).
    Devolve o empty do balao (centro), para animar."""
    mb, ml, md = bubble_mats()
    body_m = ml if light else mb
    dot_m = bubble_dot_light() if light else md
    w, h, d = w * s, h * s, d * s
    with grupo(root, name, loc=loc, rot=rot, parent=parent) as e:
        slab(root, name + '_corpo', w, h, d, body_m, r=h * 0.46, bev=d * 0.42)
        if tail:
            tx = tail * w * 0.3
            # cone com a ponta para baixo e para fora (a base larga fica dentro do balao)
            cyl(root, name + '_rabo', 0.0, h * 0.32, (tx + tail * h * 0.05, 0, -h * 0.52), r2=h * 0.17, rot=(0, -tail * 0.55, 0), m=body_m, v=12, bev=0.0)
        if dots:
            for side in ((-1, 1) if both else (-1,)):
                for k in (-1, 0, 1):
                    sphere(root, f'{name}_ponto{side}{k}', h * 0.1, (k * w * 0.22, side * d * 0.5, 0), scale=(1, 0.45, 1), m=dot_m, seg=10)
    return e


def float_anim(o, amp=0.03, ph0=0.0, sway=0.08, spin_z=0.0):
    """Balao flutuando: sobe e desce, balanca de leve (fase ph0 desencontra os baloes)."""
    def fn(ob, mb, ph):
        a = TAU * (ph + ph0)
        ob.matrix_basis = Matrix.Translation((0, 0, amp * math.sin(a))) @ mb @ Matrix.Rotation(sway * math.sin(a + 1.1), 4, 'Y') \
            @ Matrix.Rotation(spin_z * math.sin(a), 4, 'Z')
    register_anim(o, fn)
    return o


def pulse_anim(o, lo=0.6, hi=1.25, on=(0.0, 0.3), ph0=0.0):
    """Pisca: escala alta no trecho 'on' da fase, baixa no resto (luz de antena, LED)."""
    def fn(ob, mb, ph):
        p = (ph + ph0) % 1.0
        k = hi if on[0] <= p < on[1] else lo
        ob.matrix_basis = mb @ Matrix.Diagonal((k, k, k, 1))
    register_anim(o, fn)
    return o


# ---------------------------------------------------------------- tripulacao (terno, gravata, cracha)
HC = Vector((0.006, 0, 0.055))   # centro da cabeca no pivo da cabeca


def cloth_mat(key, hexcol, sheen=0.3):
    return mat(key, hexcol, rough=0.72, var=0.03, bump=0.06, sheen=sheen)


def tie(root, pr, tag, m, knot=None, collar=None):
    """Gravata no peito (filha do corpo; o corpo olha para +X local) e a gola branca da camisa."""
    shirt = collar or mat('camisa_branca_zcv', '#f6f2ea', rough=0.8, var=0.0, bump=0.02)
    objs = [box(root, tag + '_gola', (0.012, 0.05, 0.035), (0.068, 0.0, 0.466), rot=(0, -0.5, 0), m=shirt, bev=0.006),
            blob(root, tag + '_gravataNo', 0.014, (0.08, 0.0, 0.452), (0.7, 1.0, 1.0), knot or m),
            box(root, tag + '_gravata', (0.01, 0.026, 0.12), (0.087, 0.0, 0.385), rot=(0, 0.08, 0), m=m, bev=0.005)]
    for o in objs:
        o.parent = pr['body']
    return objs


def glasses(root, pr, tag, m=None, dark=False):
    """Oculos de aro (ou escuros) no pivo da cabeca."""
    fr = m or mat('aro_oculos', '#2a2626', rough=0.4, var=0.0, bump=0.0)
    objs = []
    for s, yy in enumerate((-0.026, 0.026)):
        if dark:
            objs.append(blob(root, f'{tag}_lente{s}', 0.017, HC + Vector((0.064, yy, 0.012)), (0.45, 1.1, 0.8), fr))
        else:
            o = torus(root, f'{tag}_aro{s}', (0, 0, 0), 0.015, 0.0035, fr, axis='X', n=14, segs=4)
            o.location = HC + Vector((0.066, yy, 0.012))
            objs.append(o)
    objs.append(box(root, tag + '_ponte', (0.006, 0.022, 0.005), HC + Vector((0.07, 0, 0.016)), m=fr, bev=0.001))
    for o in objs:
        o.parent = pr['head']
    return objs


def headset(root, pr, tag, m, mic=True):
    """Fone de ouvido com microfone (de telemarketing), no pivo da cabeca."""
    pts = [HC + Vector((0.0, -0.07, 0.0)), HC + Vector((0.0, -0.06, 0.05)), HC + Vector((0.0, 0.0, 0.078)),
           HC + Vector((0.0, 0.06, 0.05)), HC + Vector((0.0, 0.07, 0.0))]
    objs = [tube(root, tag + '_arcoFone', pts, 0.007, m, segs=6)]
    for s, yy in enumerate((-0.07, 0.07)):
        o = cyl(root, f'{tag}_concha{s}', 0.024, 0.016, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=m, v=16, bev=0.004)
        o.location = HC + Vector((0.0, yy, -0.004))
        objs.append(o)
    if mic:
        objs.append(tube(root, tag + '_haste', [HC + Vector((0.0, -0.075, -0.01)), HC + Vector((0.04, -0.06, -0.05)), HC + Vector((0.07, -0.025, -0.055))],
                         0.004, m, segs=5))
        objs.append(sphere(root, tag + '_micro', 0.009, HC + Vector((0.072, -0.022, -0.055)), m=mat('espuma_micro', '#2b2b2e', rough=0.9, var=0, bump=0.2), seg=8))
    for o in objs:
        o.parent = pr['head']
    return objs


def badge_lanyard(root, pr, tag, m, card=None):
    """Cracha pendurado no pescoco (cordao colorido e cartao claro, sem nada escrito)."""
    o = tube(root, tag + '_crachaCordao', [(0.05, -0.05, 0.47), (0.098, -0.02, 0.4), (0.1, 0.0, 0.37), (0.098, 0.02, 0.4), (0.05, 0.05, 0.47)], 0.004, m, segs=4)
    c = box(root, tag + '_cracha', (0.006, 0.04, 0.05), (0.104, 0.0, 0.345), m=card or mat('cracha_zcv', '#f8f4ea', rough=0.6, var=0, bump=0), bev=0.003)
    for x in (o, c):
        x.parent = pr['body']
    return o, c


def shoes(m=None):
    return m or mat('sapato_preto_zcv', '#1e1a18', rough=0.35, var=0.0, bump=0.02)


# ---------------------------------------------------------------- marcas da chapa na roupa (todas presas no corpo)
def marca_peito(root, pr, tag, star_r=0.027, collar=True):
    """Camisa da turma: gola redonda na cor 'gola' da chapa (V verde, R branca); V ganha o decote em V verde da camisa
    da selecao, R a estrela branca no peito (do lado que a camera ve). Nao muda o contorno do boneco."""
    out = []
    gm = cor('gola')
    if collar:
        o = torus(root, tag + '_golaCamisa', (0, 0, 0.468), 0.06, 0.009, gm, n=20, segs=5)
        o.scale = (0.86, 1.18, 1.0)
        out.append(o)
    if CHAPA == 'V':
        for k, sy in enumerate((-1, 1)):
            out.append(tube(root, f'{tag}_golaV{k}', [(0.058, sy * 0.03, 0.466), (0.074, sy * 0.012, 0.44), (0.08, 0.0, 0.425)], 0.0075, gm, segs=5))
    else:
        out += estrela_peito(root, tag, pr['body'], (0.085, -0.032, 0.405), r=star_r, rot=(0, 0, math.pi / 2 - 0.3))
    for o in out:
        o.parent = pr['body']
    return out


def broche(root, pr, tag, r=0.024):
    """Broche da chapa na lapela do terno (lado que a camera ve): R estrela branca, V losango amarelo com o circulo azul."""
    loc = (0.079, -0.046, 0.425)
    rot = (0, 0, math.pi / 2 - 0.34)
    if CHAPA == 'R':
        out = [estrela(root, tag + '_broche', r, 0.006, loc=loc, rot=rot)]
    else:
        out = emblema(root, tag + '_broche', r * 2.3, r * 2.3, loc=loc, rot=rot, depth=0.006)
    for o in out:
        if o.parent is None or o.parent.name == root.name:
            o.parent = pr['body']
    return out
