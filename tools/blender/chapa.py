"""Cores da chapa nas torres (Ninguem Sobe a Rampa): a mesma torre sai em duas versoes, uma para cada chapa do jogador.

  CHAPA=V (padrao): Chapa Verde-Amarela -> verde e amarelo, azul de detalhe; turma de camisa amarela da selecao com gola
                    verde; bandeirinha verde com losango amarelo e circulo azul (sem faixa nem letras)
  CHAPA=R:          Chapa Vermelha -> vermelho com estrela branca; turma de camiseta vermelha com estrela branca no peito
                    e bone vermelho; bandeirinha vermelha com estrela branca

Render: a versao V vai para arte/render/<familia>, a R para arte/render_r/<familia> (pasta passada na linha de comando):
  Blender -b -P tools/blender/torre_x.py -- render arte/render/x
  CHAPA=R Blender -b -P tools/blender/torre_x.py -- render arte/render_r/x

Uso nos scripts das torres:
    from chapa import CHAPA, PAL, cor, estrela, bandeirinha, estrela_peito
    m = cor('pri')   # material da cor principal da chapa (pri, sec, ter, claro, escuro, camisa, gola, calca, bone)
"""
import math
from lib import mat, cyl, box, tube, sphere, _M
from lote_brasilia import prism_xz
import os

CHAPA = os.environ.get('CHAPA', 'V').strip().upper()[:1] or 'V'
if CHAPA not in ('V', 'R'):
    CHAPA = 'V'

PALS = {
    'V': dict(
        pri='#1f9a4c',      # verde bandeira
        sec='#ffd21f',      # amarelo ouro
        ter='#2453c4',      # azul do circulo
        claro='#fff4c2',    # creme amarelado
        escuro='#0f5a2b',   # verde escuro
        camisa='#ffd21f',   # camisa amarela da selecao
        gola='#1f9a4c',     # gola e punho verdes
        calca='#2453c4',    # calcao/calca azul
        bone='#1f9a4c',     # bone verde
        emblema='losango',
    ),
    'R': dict(
        pri='#d6282b',      # vermelho
        sec='#ffffff',      # branco da estrela
        ter='#8f1a1d',      # vinho
        claro='#ffe6df',    # rosado claro
        escuro='#7a1417',   # vermelho escuro
        camisa='#d6282b',   # camiseta vermelha
        gola='#ffffff',     # estrela/gola branca
        calca='#3a3a46',    # calca jeans escura
        bone='#d6282b',     # bone vermelho
        emblema='estrela',
    ),
}
PAL = PALS[CHAPA]

_ROUGH = dict(pri=0.55, sec=0.5, ter=0.55, claro=0.6, escuro=0.6, camisa=0.85, gola=0.8, calca=0.85, bone=0.75)


def cor(papel, rough=None, **kw):
    """Material da cor `papel` da chapa (uma chave por chapa e papel: nada se mistura entre renders)."""
    key = f'chapa_{CHAPA}_{papel}' + ('' if rough is None and not kw else '_' + '_'.join(f'{k}{v}' for k, v in sorted(dict(r=rough, **kw).items())))
    if key in _M:
        return _M[key]
    extra = dict(var=0.03, bump=0.05)
    if papel in ('camisa', 'gola', 'calca', 'bone'):
        extra['sheen'] = 0.3
    extra.update(kw)
    return mat(key, PAL[papel], rough=_ROUGH.get(papel, 0.6) if rough is None else rough, **extra)


def star_pts(r, ri=None, cx=0.0, cz=0.0, rot=0.0):
    """Contorno de estrela de 5 pontas no plano XZ (ponta para cima)."""
    ri = ri if ri is not None else r * 0.42
    pts = []
    for i in range(10):
        a = math.pi / 2 + rot + i * math.pi / 5
        rr = r if i % 2 == 0 else ri
        pts.append((cx + rr * math.cos(a), cz + rr * math.sin(a)))
    return pts[::-1]


def estrela(root, name, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), m=None, bev=0.004):
    """Estrela de 5 pontas em relevo (placa fina no plano XZ, espessura em Y). Padrao: branca."""
    o = prism_xz(root, name, star_pts(r), depth, m or cor('sec', rough=0.45), bev=min(bev, depth * 0.3))
    o.location = loc
    o.rotation_euler = rot
    return o


def emblema(root, name, w, h, loc=(0, 0, 0), rot=(0, 0, 0), depth=0.006):
    """Emblema da chapa sobre um fundo w x h no plano XZ (centro em loc): V = losango amarelo com circulo azul,
    R = estrela branca. Devolve a lista de objetos (o chamador cuida do pai)."""
    out = []
    if CHAPA == 'V':
        los = prism_xz(root, name + '_losango', [(w * 0.42, 0), (0, h * 0.40), (-w * 0.42, 0), (0, -h * 0.40)], depth, cor('sec', rough=0.45), bev=depth * 0.25)
        los.location = loc
        los.rotation_euler = rot
        out.append(los)
        d = cyl(root, name + '_circulo', min(w, h) * 0.2, depth * 1.6, (0, 0, 0), m=cor('ter', rough=0.45), v=24, bev=depth * 0.3)
        d.rotation_euler = (math.pi / 2, 0, 0)
        d.parent = los
        d.location = (0, -depth * 0.6, 0)
        out.append(d)
    else:
        out.append(estrela(root, name + '_estrela', min(w, h) * 0.36, depth, loc=loc, rot=rot))
    return out


def bandeirinha(root, name, loc, h=0.34, w=0.2, fh=0.13, face=0.0, pole=None):
    """Mastro fininho com a bandeira da chapa (pano levemente ondulado, emblema dos dois lados)."""
    x, y, z = loc
    pm = pole or mat('mastro_aluminio', '#c9ced2', rough=0.3, metal=0.7, var=0.02, bump=0.02)
    mast = cyl(root, name + '_mastro', 0.008, h, (x, y, z + h / 2), m=pm, v=8, bev=0.002)
    tip = sphere(root, name + '_ponta', 0.014, (x, y, z + h + 0.008), m=pm)
    fundo = 'pri'
    cloth = box(root, name + '_pano', (w, 0.008, fh), (0, 0, 0), m=cor(fundo, rough=0.8, sheen=0.4), bev=0.002)
    cloth.parent = mast
    cloth.location = (w / 2 + 0.006, 0, h / 2 - fh / 2 - 0.004)
    cloth.rotation_euler = (0, 0, 0)
    cloth.scale = (1, 1, 1)
    for s, sgn in (('a', -1), ('b', 1)):
        for o in emblema(root, f'{name}_em{s}', w * 0.9, fh * 0.9, depth=0.004):
            if o.parent is None or o.parent == root:   # o lib pendura tudo na raiz: o emblema vai para o pano
                o.parent = cloth
                o.location = (0, sgn * 0.005, 0)
    mast.rotation_euler = (0, 0, face)
    return mast


def estrela_peito(root, name, parent, loc, r=0.022, rot=(0, 0, 0)):
    """Detalhe da camisa da turma presa no peito (pivo `parent`): R = estrela branca; V = gola verde em V
    (duas tirinhas). Devolve os objetos criados."""
    out = []
    if CHAPA == 'R':
        e = estrela(root, name + '_estrelaPeito', r, 0.006, rot=rot)
        e.parent = parent
        e.location = loc
        out.append(e)
    else:
        gm = cor('gola')
        for k, sg in enumerate((-1, 1)):
            t = box(root, f'{name}_golaV{k}', (0.008, 0.006, r * 1.4), (0, 0, 0), m=gm, bev=0.002)
            t.parent = parent
            t.location = (loc[0], loc[1] + sg * r * 0.35, loc[2] + r * 0.2)
            t.rotation_euler = (-sg * 0.5, 0, 0)   # pontas de cima abrindo para fora: V, nao Λ
            out.append(t)
    return out
