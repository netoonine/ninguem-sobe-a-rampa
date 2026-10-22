"""Leite Condensado (Artilharia da chapa V, Ninguem Sobe a Rampa): niveis 1 a 3, Compra de 15 Milhoes e Batedeira
Industrial. Piada com a compra gigante de leite condensado do governo: latas gigantes genericas (rotulo azul com faixa
branca e filete amarelo, sem nada escrito), paletes e caixotes de latas, a catapulta de colher que arremessa a lata e a
turma da chapa V (camisa amarela da selecao com gola verde, calcao azul, bone verde) carregando latas.
Troca so a arte da chapa V do Petrolao: nomes de conjuntos, postos, pontos, luzes e modos sao os mesmos do
tools/blender/torre_artilharia.py (js/sprites.js depende deles). A chapa R continua com o Petrolao (arte/render_r).

  ar1..ar3  deck de paletes sobre pernas de latas empilhadas, a catapulta de colher e montes de latas
  arM       Compra de 15 Milhoes: a torre e uma lata gigante, com a montanha de paletes de latas, a caixa registradora
            com a nota fiscal enorme (sem texto) e a catapulta de colher de ouro
  arS       Batedeira Industrial: batedeira de pe gigante; o batedor de arame (conjunto arH, modo 'slam') bate na
            tigela de leite condensado no mesmo ritmo da broca antiga
  arT*      catapulta de colher (o braco sobe e a lata sai da concha da colher)
  arG/arC/arR/arE  torcedor da colher, carregador de lata, comprador de terno, confeiteiro da batedeira

  CHAPA=V Blender -b -P tools/blender/torre_leite.py -- render arte/render/artilharia [conjuntos...]
  Blender -b -P tools/blender/torre_leite.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_leite.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lib import _M
from lote_brasilia import plot, work_lamp, concrete, grupo, hide_tree, prism_xz, G   # noqa: F811 - lote de Brasilia
from chapa import CHAPA, cor, emblema, bandeirinha, estrela_peito   # cores da chapa (esta torre e da chapa V)

FRONT = -math.pi / 2
FAM = 'artilharia'
HC = Vector((0.006, 0, 0.055))   # centro da cabeca no pivo da cabeca

import lib as _lib
_orig_palette2 = palette2


def band_mat(key, stops, rough=0.45, metal=0.0, sheen=0.0, axis='Z'):
    """Material em faixas ao longo do eixo local do objeto (coordenada Generated de 0 a 1, nao depende do tamanho):
    stops = [(posicao, '#cor'), ...] de baixo para cima. Serve para o rotulo das latas (pequenas e gigantes)."""
    if key in _M:
        return _M[key]
    m = mat(key, stops[0][1], rough=rough, metal=metal, var=0.02, bump=0.02, sheen=sheen)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = lin(stops[0][1])
    els[1].position = stops[1][0]
    els[1].color = lin(stops[1][1])
    for pos, col in stops[2:]:
        e = els.new(pos)
        e.color = lin(col)
    L.new(tc.outputs['Generated'], sep.inputs[0])
    L.new(sep.outputs[axis], ramp.inputs['Fac'])
    hsv = next(n for n in N if n.type == 'HUE_SAT')
    L.new(ramp.outputs['Color'], hsv.inputs['Color'])
    return m


AZUL, BRANCO, AMARELO = '#2a5cc2', '#f8f6ef', '#ffd21f'


def palette2():   # noqa: F811 - latas, paletes, leite condensado e as cores da chapa V
    P = _orig_palette2()
    P['tin'] = mat('lata_folha', '#cfd5da', rough=0.24, metal=0.85, var=0.02, bump=0.01)
    P['tin_d'] = mat('lata_tampa', '#b7bec4', rough=0.3, metal=0.8, var=0.02, bump=0.01)
    # rotulo generico: azul embaixo, filete amarelo, faixa branca larga, azul em cima (sem texto)
    P['label'] = band_mat('rotulo_leite', [(0.0, AZUL), (0.5, AMARELO), (0.57, BRANCO), (0.88, AZUL)], rough=0.42, sheen=0.2)
    P['label_gold'] = band_mat('rotulo_ouro', [(0.0, '#e0ad38'), (0.5, '#fff2bf'), (0.57, BRANCO), (0.88, '#e0ad38')], rough=0.3, metal=0.45)
    P['milk'] = mat('leite_condensado', '#f6e6bd', rough=0.1, var=0.0, bump=0.0, sheen=0.2)
    P['milk_d'] = mat('leite_condensado_doce', '#ecc98a', rough=0.12, var=0.0, bump=0.0)
    P['pallet'] = mat('palete_pinho', '#d9ab70', rough=0.8, var=0.08, bump=0.2)
    P['pallet_d'] = mat('palete_pinho_escuro', '#b98552', rough=0.8, var=0.08, bump=0.2)
    P['deck_wood'] = mat('deck_tabuas', '#b58d63', rough=0.75, var=0.04, bump=0.12, stripes=(9.0, '#bd966b', '#a98058'))
    P['awning'] = mat('listra_leite', BRANCO, rough=0.6, var=0.0, bump=0.04, stripes=(14.0, BRANCO, AZUL))
    P['inox'] = mat('colher_inox', '#e2e6ea', rough=0.16, metal=0.9, var=0.02, bump=0.0)
    P['pipe'] = mat('cano_aco', '#aab1b6', rough=0.35, metal=0.55, var=0.03, bump=0.02)
    P['steel_k'] = mat('aco_preto', '#383537', rough=0.5, metal=0.25, var=0.05, bump=0.05)
    P['rubber'] = mat('borracha', '#262427', rough=0.8, var=0.02, bump=0.05)
    P['suit'] = mat('terno_comprador', '#2e2f38', rough=0.75, var=0.03, bump=0.06, sheen=0.4)
    P['shirt'] = mat('camisa_comprador', '#f3f1ea', rough=0.8, var=0.02, bump=0.05, sheen=0.3)
    P['sneaker'] = mat('tenis_branco', '#f4f4f0', rough=0.5, var=0.0, bump=0.02)
    P['chef'] = mat('chapeu_confeiteiro', '#fbfaf6', rough=0.85, var=0.0, bump=0.08, sheen=0.4)
    P['paper'] = mat('nota_fiscal', '#fbf8ef', rough=0.85, var=0.02, bump=0.02)
    P['ink'] = mat('linha_nota', '#b9b4a8', rough=0.85, var=0.0, bump=0.0)
    P['beacon'] = glow_mat('giroflex', '#ff9a3a', 3.0, 18.0, rough=0.3, var=0.0, bump=0.0)
    P['conc'] = concrete()
    # cores da chapa: verde (pernas, caixas, a batedeira), amarelo (bordas, guarda-corpo, frisos), azul de detalhe
    P['cA'] = cor('pri')
    P['cB'] = cor('sec')
    P['cC'] = cor('sec') if CHAPA == 'V' else cor('pri')
    P['cT'] = cor('ter')
    P['flag'] = cor('pri', rough=0.8, sheen=0.4)
    P['camisa'], P['calca'], P['bone'], P['gola'] = cor('camisa'), cor('calca'), cor('bone'), cor('gola')
    P['teal'] = P['cA']
    P['_emblem'] = 'drop'
    return P


_lib.palette2 = palette2


def placa_chapa(root, name, w, h, loc, rot=(0, 0, 0), plate=True, th=0.014, parent=None, front=False):
    """Placa da chapa olhando para -Y: bandeira verde com o losango amarelo e o circulo azul."""
    e = empty(root, name + '_piv', loc=loc, rot=rot, parent=parent)
    if plate:
        kids(e, box(root, name + '_placa', (w, th, h), (0, 0, 0), m=cor('pri', rough=0.6), bev=min(0.006, th * 0.4), front=front))
    for o in emblema(root, name, w * 0.92, h * 0.92, loc=(0, -th / 2 - 0.002 if plate else -0.002, 0)):
        if o.parent == root:
            o.parent = e
        if front:
            o['front'] = 1
    return e


def basis_euler(xdir, zhint):
    """Giro que leva o X local para xdir e o Z local o mais perto possivel de zhint."""
    X = Vector(xdir).normalized()
    Z = Vector(zhint)
    Z = (Z - X * Z.dot(X)).normalized()
    Y = Z.cross(X)
    return Matrix((X, Y, Z)).transposed().to_euler()


GUN_FACE = math.radians(-35)     # a catapulta arremessa para a direita e um pouco para a camera (o jogo espelha)


# ---------------------------------------------------------------- latas, paletes, caixotes
def lata(root, P, name, loc, r=0.075, h=None, lying=False, rot=0.0, parent=None, label=None, aberta=False, tilt=None):
    """Lata de leite condensado: corpo de folha de flandres com os frisos da borda, rotulo em faixas (azul, filete
    amarelo, branco) e a tampa; aberta = o leite cremoso aparecendo. Centro em loc, eixo Z local."""
    h = h or r * 2.25
    rr = tilt if tilt is not None else ((math.pi / 2, 0, rot) if lying else (0, 0, rot))
    seg = 20 if r > 0.05 else 14
    with grupo(root, name + '_piv', loc=loc, rot=rr, parent=parent) as e:
        lathe(root, name, [(-h / 2, r * 0.88, r * 0.88), (-h / 2 + h * 0.035, r, r), (-h / 2 + h * 0.08, r * 0.95, r * 0.95),
                           (h / 2 - h * 0.08, r * 0.95, r * 0.95), (h / 2 - h * 0.035, r, r), (h / 2, r * 0.88, r * 0.88)],
              P['tin'], segs=seg, lv=1, caps=True)
        cyl(root, name + '_rotulo', r * 0.972, h * 0.8, (0, 0, 0), m=label or P['label'], v=seg, bev=0.0, caps=False)
        if aberta:
            cyl(root, name + '_leite', r * 0.86, 0.012, (0, 0, h / 2 - 0.012), m=P['milk'], v=seg, bev=0.004)
        else:
            cyl(root, name + '_tampa', r * 0.84, 0.008, (0, 0, h / 2 - 0.003), m=P['tin_d'], v=seg, bev=0.002)
    return e


def pilha(root, P, tag, x, y, z, r, rows, rot=0.0, gold=(), parent=None, jitter=0.0):
    """Piramide de latas em parede (rows na base, uma a menos por fileira), voltada para a camera depois do giro."""
    h = r * 2.25
    rr = random.Random(len(tag) * 7 + rows)
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot), parent=parent) as e:
        k = 0
        for row in range(rows):
            n = rows - row
            for i in range(n):
                cx = (i - (n - 1) / 2) * r * 2.04 + rr.uniform(-jitter, jitter)
                lata(root, P, f'{tag}_lata{k}', (cx, rr.uniform(-jitter, jitter), row * h + h / 2 + 0.001), r=r, rot=rr.uniform(0, TAU),
                     label=P['label_gold'] if k in gold else None)
                k += 1
    return e


def monte(root, P, tag, x, y, z, r, layers, rot=0.0, gold_top=False, parent=None):
    """Piramide de latas de base quadrada (layers x layers embaixo)."""
    h = r * 2.25
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot), parent=parent) as e:
        k = 0
        for L_ in range(layers):
            n = layers - L_
            for i in range(n):
                for j in range(n):
                    lata(root, P, f'{tag}_lata{k}', ((i - (n - 1) / 2) * r * 2.04, (j - (n - 1) / 2) * r * 2.04, L_ * h + h / 2 + 0.001),
                         r=r, rot=0.7 * k, label=P['label_gold'] if (gold_top and L_ == layers - 1) else None)
                    k += 1
    return e


PAL_H = 0.059


def palete(root, P, tag, x, y, z, w=0.36, d=0.3, rot=0.0, parent=None):
    """Palete de pinho: tres barrotes e cinco tabuas por cima. Topo em z + PAL_H."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot), parent=parent) as e:
        for k in range(3):
            box(root, f'{tag}_barrote{k}', (w, 0.045, 0.045), (0, (k - 1) * (d / 2 - 0.03), 0.0225), m=P['pallet_d'], bev=0.006)
        n = 5
        for k in range(n):
            box(root, f'{tag}_tabua{k}', (w / n * 0.8, d, 0.014), (-w / 2 + w / n * (k + 0.5), 0, 0.052), m=P['pallet'], bev=0.003)
    return e


def carga(root, P, tag, x, y, z, nx=2, ny=2, r=0.055, rot=0.0, units=1, gold_top=False, parent=None, layers=1):
    """Paletes empilhados, cada um com `layers` camadas de latas (nx por ny). Devolve o topo."""
    h = r * 2.25
    w, d = nx * r * 2.04 + 0.03, ny * r * 2.04 + 0.03
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot), parent=parent):
        zz = 0.0
        for u in range(units):
            palete(root, P, f'{tag}_palete{u}', 0, 0, zz, w=w, d=d, rot=0.0)
            zz += PAL_H
            for c_ in range(layers):
                for i in range(nx):
                    for j in range(ny):
                        gold = gold_top and u == units - 1 and c_ == layers - 1
                        lata(root, P, f'{tag}_u{u}{c_}_{i}{j}', ((i - (nx - 1) / 2) * r * 2.04, (j - (ny - 1) / 2) * r * 2.04, zz + h / 2 + 0.001), r=r,
                             rot=1.3 * (i + 2 * j + u + c_), label=P['label_gold'] if gold else None)
                zz += h + 0.002
    return z + zz


def caixote(root, P, tag, x, y, z, w=0.26, d=0.2, hh=0.11, r=0.045, rot=0.0, parent=None):
    """Caixote de madeira (ripas com fresta) cheio de latas em pe, as tampas aparecendo por cima."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot), parent=parent) as e:
        box(root, tag + '_fundo', (w, d, 0.02), (0, 0, 0.01), m=P['pallet_d'], bev=0.004)
        for k, zz in enumerate((hh * 0.28, hh * 0.76)):
            for sy in (-1, 1):
                box(root, f'{tag}_ripaF{k}{sy}', (w, 0.016, hh * 0.4), (0, sy * (d / 2 - 0.008), zz), m=P['pallet'], bev=0.004)
            for sx in (-1, 1):
                box(root, f'{tag}_ripaL{k}{sx}', (0.016, d, hh * 0.4), (sx * (w / 2 - 0.008), 0, zz), m=P['pallet'], bev=0.004)
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(root, f'{tag}_canto{sx}{sy}', (0.024, 0.024, hh), (sx * (w / 2 - 0.012), sy * (d / 2 - 0.012), hh / 2), m=P['pallet_d'], bev=0.004)
        nx, ny = max(1, int((w - 0.03) // (r * 2.06))), max(1, int((d - 0.03) // (r * 2.06)))
        k = 0
        for i in range(nx):
            for j in range(ny):
                lata(root, P, f'{tag}_lata{k}', ((i - (nx - 1) / 2) * r * 2.06, (j - (ny - 1) / 2) * r * 2.06, 0.02 + r * 1.125), r=r, rot=0.9 * k)
                k += 1
    return e


def poca(root, P, tag, x, y, rx, ry, z=G, rot=0.0):
    """Poca de leite condensado derramado (cremosa e brilhante) com duas gotinhas."""
    sphere(root, tag, 1.0, (x, y, z + 0.002), scale=(rx, ry, 0.014), m=P['milk'], seg=24, rot=(0, 0, rot))
    for k, (dx, dy, s) in enumerate(((rx * 1.1, -ry * 0.5, 0.35), (-rx * 0.9, ry * 0.7, 0.25))):
        c, sn = math.cos(rot), math.sin(rot)
        sphere(root, f'{tag}_gota{k}', 1.0, (x + dx * c - dy * sn, y + dx * sn + dy * c, z + 0.002), scale=(rx * s, ry * s, 0.012), m=P['milk'], seg=16)


def lata_derramando(root, P, tag, x, y, z=G, r=0.07, rot=0.0, flow=0.24):
    """Lata deitada e aberta com o leite condensado escorrendo numa lingua cremosa ate a poca."""
    h = r * 2.25
    lata(root, P, tag, (x, y, z + r * 0.97), r=r, lying=True, rot=rot, aberta=True)
    d = Vector((math.cos(rot - math.pi / 2), math.sin(rot - math.pi / 2), 0))   # para onde aponta a boca da lata
    p0 = Vector((x, y, z + r * 0.5)) + d * (h / 2 - 0.01)
    tube(root, tag + '_escorre', [p0, p0 + d * 0.05 + Vector((0, 0, -r * 0.35)), p0 + d * 0.1 + Vector((0, 0, -r * 0.5))], r * 0.32, P['milk'], segs=10,
         rfun=lambda t: r * (0.34 + 0.12 * t))
    c = p0 + d * (flow * 0.55)
    sphere(root, tag + '_poca', 1.0, (c.x, c.y, z + 0.002), scale=(flow * 0.6, flow * 0.42, 0.014), m=P['milk'], seg=24, rot=(0, 0, rot))


def rail(root, P, tag, pts, z, h=0.13, m=None, front=False, every=0.24, r=0.012):
    """Guarda-corpo amarelo: postes, corrimao e travessa do meio passando pelos pontos (x, y)."""
    m = m or P['cC']
    top = [(x, y, z + h) for x, y in pts]
    mid = [(x, y, z + h * 0.5) for x, y in pts]
    tube(root, tag + '_corrimao', top, r, m, segs=8, front=front)
    tube(root, tag + '_meio', mid, r * 0.75, m, segs=6, front=front)
    k = 0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(L / every))
        for i in range(n + (1 if (x1, y1) == pts[-1] else 0)):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            tube(root, f'{tag}_poste{k}', [(x, y, z), (x, y, z + h)], r * 0.9, m, segs=6, front=front)
            k += 1


def deck(root, P, tag, cx, cy, w, d, ztop, th=0.06, leg_r=0.065, inset=0.09, braces=False, z0=G):
    """Deck de tabuas de pinho com a borda amarela e o friso listrado azul e branco na frente, sobre quatro pernas
    de latas gigantes empilhadas."""
    box(root, tag + '_deck', (w, d, th), (cx, cy, ztop - th / 2), m=P['deck_wood'], bev=0.018)
    box(root, tag + '_deckBorda', (w + 0.025, d + 0.025, th * 0.5), (cx, cy, ztop - th * 0.72), m=P['cB'], bev=0.01)
    box(root, tag + '_deckListra', (w - 0.06, 0.014, th * 0.42), (cx, cy - d / 2 - 0.012, ztop - th * 0.7), m=P['awning'], bev=0.0)
    legs = []
    L = ztop - th - z0
    n = max(1, round(L / (2.25 * leg_r)))
    r = L / (2.25 * n)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * (w / 2 - inset), cy + sy * (d / 2 - inset)
            for k in range(n):
                lata(root, P, f'{tag}_perna{sx}{sy}_{k}', (x, y, z0 + r * 2.25 * (k + 0.5)), r=r * 0.995, rot=0.8 * k + sx + 2 * sy)
            legs.append((x, y))
    if braces:
        za, zb = z0 + 0.06, ztop - th - 0.05
        for k, (a, b) in enumerate(((0, 1), (1, 3), (2, 3), (0, 2))):
            if k == 3:
                continue    # a frente fica aberta (latas e caixotes aparecem por baixo)
            pa, pb = legs[a], legs[b]
            tube(root, f'{tag}_xA{k}', [(pa[0], pa[1], za), (pb[0], pb[1], zb)], 0.016, P['pallet_d'], segs=6)
            tube(root, f'{tag}_xB{k}', [(pb[0], pb[1], za), (pa[0], pa[1], zb)], 0.016, P['pallet_d'], segs=6)
    return legs


def stairs(root, P, tag, p0, p1, w=0.16, steps=6, front=False):
    """Escada reta amarela de p0 (chao) ate p1 (deck), com degraus de pinho e corrimao."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    side = Vector((-d.y, d.x, 0)).normalized() * (w / 2)
    for s, sg in enumerate((-1, 1)):
        tube(root, f'{tag}_banzo{s}', [a + side * sg, b + side * sg], 0.014, P['cC'], segs=6, front=front)
        tube(root, f'{tag}_corrimao{s}', [a + side * sg + Vector((0, 0, 0.13)), b + side * sg + Vector((0, 0, 0.13))], 0.01, P['cC'], segs=6, front=front)
        for t in (0.0, 1.0):
            p = a.lerp(b, t) + side * sg
            tube(root, f'{tag}_balaustre{s}{int(t)}', [p, p + Vector((0, 0, 0.13))], 0.009, P['cC'], segs=5, front=front)
    ang = math.atan2(d.y, d.x)
    for k in range(steps):
        p = a.lerp(b, (k + 0.5) / steps)
        box(root, f'{tag}_degrau{k}', (0.05, w, 0.016), tuple(p), rot=(0, 0, ang), m=P['pallet'], bev=0.004, front=front)


def giroflex(root, P, tag, loc, s=1.0):
    """Giroflex laranja (luz de galpao): base verde, cupula acesa e o refletor girando dentro (anim)."""
    x, y, z = loc
    cyl(root, tag + '_base', 0.055 * s, 0.035 * s, (x, y, z + 0.0175 * s), m=P['cA'], v=18, bev=0.008)
    sphere(root, tag + '_cupula', 0.05 * s, (x, y, z + 0.06 * s), scale=(1, 1, 1.15), m=P['beacon'], seg=18)
    piv = empty(root, tag + '_giro', loc=(x, y, z + 0.06 * s))
    kids(piv, box(root, tag + '_refletor', (0.012 * s, 0.07 * s, 0.05 * s), (0.02 * s, 0, 0), m=P['inox'], bev=0.003))
    register_anim(piv, spin('Z', sym=1, turns=1))
    return piv


def pennant(root, P, tag, x, y, z, pole=0.32, length=0.22, height=0.1):
    """Bandeirola verde da chapa num mastro fino, balancando no loop."""
    tube(root, tag + '_mastro', [(x, y, z), (x, y, z + pole)], 0.011, P['pipe'], segs=6)
    sphere(root, tag + '_pomo', 0.018, (x, y, z + pole + 0.01), m=P['cB'], seg=8)
    pen = cloth_grid(root, tag, length, height, 10, 3, [P['flag']], thick=0.008,
                     shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * height * (1 - u * 0.85))))
    pen.location = (x + 0.01, y, z + pole - height * 0.5)
    register_cloth(pen, flag_wave(length, amp=0.04, cycles=1, waves=1.1))
    return pen


def colher(root, tag, m, L=0.5, r=0.06, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    """Colher gigante: cabo achatado ao longo de +X e a concha na ponta (aberta para +Z). Ponta do cabo em x = 0."""
    with grupo(root, tag, loc=loc, rot=rot, parent=parent) as e:
        cb = tube(root, tag + '_cabo', [(0, 0, 0.0), (L * 0.45, 0, 0.0), (L - r * 1.3, 0, r * 0.25)], r * 0.3, m, segs=10,
                  rfun=lambda t: r * (0.36 - 0.12 * t))
        cb.scale = (1.0, 1.45, 0.7)
        sphere(root, tag + '_ponta', r * 0.42, (0, 0, 0), scale=(1.0, 1.4, 0.7), m=m, seg=12)
        cup = lathe(root, tag + '_concha', [(0, 0.0, 0.0), (r * 0.15, r * 0.82, r * 0.82), (r * 0.42, r, r), (r * 0.55, r * 1.04, r * 1.04)],
                    m, segs=22, lv=1, caps=False, solid=0.01)
        cup.location = (L, 0, r * 0.05)
        cup.scale = (1.35, 1.0, 1.0)
    return e


# ---------------------------------------------------------------- catapulta de colher (conjuntos separados: espelham e arremessam)
ARM_REST = math.radians(20)      # colher baixa, com a lata na concha
ARM_FIRE = math.radians(-48)     # colher no alto: a lata acabou de sair


def gun_dims(size, royal):
    s = size * (1.12 if royal else 1.0)
    cup_r = (0.072 if not royal else 0.095) * s
    br = cup_r * 0.86
    return s, cup_r, br, br * 2.25


def build_gun(P, root, size=1.0, ornate=0, royal=False):
    """Catapulta de colher: base de palete, dois cavaletes em A verdes, eixo amarelo; o braco e uma colher gigante de
    inox (de ouro na Compra de 15 Milhoes) com a lata na concha e o contrapeso (caixote de latas) atras; o sarilho
    de tras puxa a corda. Aponta para +X local."""
    tag = root['set']
    piv = empty(root, tag + '_giro', rot=(0, 0, GUN_FACE))
    s, cup_r, br, bh = gun_dims(size, royal)
    Y, B = P['cA'], P['cB']
    spoon_m = P['gold'] if royal else P['inox']
    trim = P['gold'] if royal else P['cB']
    with grupo(root, tag + '_base', parent=piv):
        for sy in (-1, 1):
            box(root, f'{tag}_longarina{sy}', (0.72 * s, 0.055 * s, 0.05 * s), (-0.02 * s, sy * 0.1 * s, 0.025 * s), m=P['pallet_d'], bev=0.01)
        for k in range(6):
            x = -0.34 + k * 0.12
            box(root, f'{tag}_tabua{k}', (0.085 * s, 0.29 * s, 0.022 * s), (x * s, 0, 0.061 * s), m=P['pallet'], bev=0.005)
        # cavaletes em A e o eixo no alto
        for sy in (-1, 1):
            for sx in (-1, 1):
                tube(root, f'{tag}_perna{sx}{sy}', [(sx * 0.15 * s, sy * 0.1 * s, 0.07 * s), (0.0, sy * 0.065 * s, 0.44 * s)], 0.023 * s, Y, segs=8)
            tube(root, f'{tag}_travessaA{sy}', [(-0.1 * s, sy * 0.088 * s, 0.19 * s), (0.1 * s, sy * 0.088 * s, 0.19 * s)], 0.015 * s, trim, segs=6)
        cyl(root, tag + '_mancal', 0.04 * s, 0.19 * s, (0, 0, 0.46 * s), rot=(math.pi / 2, 0, 0), m=trim, v=16, bev=0.008)
        for sy in (-1, 1):
            sphere(root, f'{tag}_porca{sy}', 0.03 * s, (0, sy * 0.1 * s, 0.46 * s), scale=(1, 0.6, 1), m=Y, seg=12)
        # sarilho (tambor da corda) atras, com dois postes
        for sy in (-1, 1):
            box(root, f'{tag}_posteSarilho{sy}', (0.04 * s, 0.025 * s, 0.13 * s), (-0.36 * s, sy * 0.085 * s, 0.13 * s), m=Y, bev=0.006)
        cyl(root, tag + '_sarilho', 0.042 * s, 0.14 * s, (-0.36 * s, 0, 0.16 * s), rot=(math.pi / 2, 0, 0), m=P['pallet_d'], v=16, bev=0.006)
        for sy in (-1, 1):
            cyl(root, f'{tag}_sarilhoAba{sy}', 0.06 * s, 0.012 * s, (-0.36 * s, sy * 0.066 * s, 0.16 * s), rot=(math.pi / 2, 0, 0), m=trim, v=18, bev=0.003)
        # batente: duas latas em pe debaixo da concha (a municao de reserva)
        for k in range(2):
            lata(root, P, f'{tag}_batente{k}', (0.31 * s, 0.0, 0.072 * s + br * 0.62 * 2.25 * (k + 0.5)), r=br * 0.62, rot=1.1 * k,
                 label=P['label_gold'] if royal else None)
        if ornate >= 1 or royal:
            g = [(-0.2 * s, -0.16 * s), (-0.46 * s, -0.16 * s), (-0.46 * s, 0.16 * s), (-0.2 * s, 0.16 * s)]
            tube(root, tag + '_guarda', [(x, y, 0.22 * s) for x, y in g], 0.01 * s, trim, segs=6)
            for k, (x, y) in enumerate(g):
                tube(root, f'{tag}_guardaPoste{k}', [(x, y, 0.07 * s), (x, y, 0.22 * s)], 0.009 * s, trim, segs=5)
    # manivela do sarilho (gira enquanto a corda puxa)
    crank = empty(root, tag + '_manivela', loc=(-0.36 * s, -0.09 * s, 0.16 * s), parent=piv)
    kids(crank, box(root, tag + '_manivelaBraco', (0.075 * s, 0.014 * s, 0.018 * s), (0.03 * s, 0, 0), m=Y, bev=0.004),
         cyl(root, tag + '_manivelaPunho', 0.011 * s, 0.05 * s, (0.062 * s, -0.025 * s, 0), rot=(math.pi / 2, 0, 0), m=trim, v=10, bev=0.003))
    # braco: a colher gigante que gira em Y no eixo, com a concha na ponta e o contrapeso atras
    AX = Vector((0, 0, 0.46 * s))
    arm = empty(root, tag + '_braco', loc=tuple(AX), parent=piv, rot=(0, ARM_REST, 0))
    L = 0.29 * s + 0.25 * s
    colher(root, tag + '_colher', spoon_m, L=L, r=cup_r, loc=(-0.25 * s, 0, -0.002 * s), parent=arm)
    with grupo(root, tag + '_bracoG', parent=arm):
        box(root, tag + '_abracadeira', (0.07 * s, 0.075 * s, 0.05 * s), (0, 0, 0), m=Y, bev=0.01)
        box(root, tag + '_faixa', (0.05 * s, 0.08 * s, 0.012 * s), (0.12 * s, 0, 0.005 * s), m=trim, bev=0.003)
        # contrapeso: caixote de latas pendurado atras
        caixote(root, P, tag + '_contrapeso', -0.235 * s, 0, -0.13 * s, w=0.12 * s, d=0.1 * s, hh=0.09 * s, r=0.022 * s)
        tube(root, tag + '_alca', [(-0.235 * s, -0.045 * s, -0.05 * s), (-0.235 * s, 0, 0.0), (-0.235 * s, 0.045 * s, -0.05 * s)], 0.008 * s, P['steel_k'], segs=6)
    load = empty(root, tag + '_carga', parent=arm, loc=(0.29 * s, 0, 0.034 * s))
    lata(root, P, tag + '_lata', (0, 0, bh / 2), r=br, h=bh, parent=load, label=P['label_gold'] if royal else None)
    if ornate >= 2 or royal:
        # bandeirola da chapa no cavalete, com o emblema dos dois lados perto do mastro
        with grupo(root, tag + '_bandeiraG', parent=piv):
            tube(root, tag + '_mastro', [(-0.15 * s, 0.1 * s, 0.05 * s), (-0.15 * s, 0.13 * s, 0.7 * s)], 0.01 * s, P['pipe'], segs=6)
            pen = cloth_grid(root, tag + '_flamula', 0.2 * s, 0.1 * s, 10, 3, [P['flag']], thick=0.008,
                             shape=lambda u, v, co: Vector((co.x, co.y, -(v - 0.5) * 0.1 * s * (1 - u * 0.85))))
            pen.location = (-0.14 * s, 0.13 * s, 0.66 * s)
        for sd, sg in (('a', -1), ('b', 1)):
            for o in emblema(root, f'{tag}_flamulaEmblema{sd}', 0.085 * s, 0.075 * s, loc=(0.06 * s, sg * 0.007, 0.0),
                             rot=(0, 0, 0 if sg < 0 else math.pi), depth=0.004):
                if o.parent == root:
                    o.parent = pen
    rope = ensure_mesh(root, tag + '_corda', mat('corda_catapulta', '#e8dcc0', rough=0.9, var=0.02, bump=0.2))
    rope.parent = piv
    return {'piv': piv, 'arm': arm, 'load': load, 'crank': crank, 'rope': rope, 's': s, 'AX': AX, 'bh': bh}


def gun_tip(size=1.0, royal=False):
    """Boca da torreta (centro da lata no instante do disparo), em BU relativas ao posto, ja com o CREW_BOOST."""
    s, cup_r, br, bh = gun_dims(size, royal)
    p = Vector((0, 0, 0.46 * s)) + Matrix.Rotation(ARM_FIRE, 3, 'Y') @ Vector((0.29 * s, 0, 0.034 * s + bh / 2))
    return Matrix.Rotation(GUN_FACE, 3, 'Z') @ p * CREW_BOOST


def gun_points(parts, tl):
    """Ponto de saida da lata: o centro da lata com a colher no alto (instante do disparo)."""
    arm = parts['arm']
    old = arm.rotation_euler.copy()
    arm.rotation_euler = (0, ARM_FIRE, 0)
    bpy.context.view_layer.update()
    m = parts['load'].matrix_world @ Vector((0, 0, parts['bh'] / 2))
    arm.rotation_euler = old
    bpy.context.view_layer.update()
    return {'points': {'muzzle': project(m, tl)}}


ARM_SEQ = [0.0, 0.06, 0.2, 0.42, 0.66, 0.86, 0.97, 1.0]   # 0 = disparo (colher no alto), 1 = repouso (colher baixa com a lata)


def pose_gun(parts, f):
    """fire: quadro 0 = a colher no alto (a lata ja saiu), depois desce devagar e recarrega (5..7). A corda vai do
    sarilho ate o contrapeso e a manivela gira junto."""
    k = ARM_SEQ[f] if f is not None else 1.0
    th = ARM_FIRE + (ARM_REST - ARM_FIRE) * k
    parts['arm'].rotation_euler = (0, th, 0)
    hide_tree(parts['load'], f is not None and f < 5)
    s, AX = parts['s'], parts['AX']
    Ry = Matrix.Rotation(th, 3, 'Y')
    Bk = AX + Ry @ Vector((-0.235 * s, 0, -0.13 * s))
    parts['crank'].rotation_euler = (0, -TAU * 0.75 * k, 0)
    d0 = Vector((-0.36 * s, 0, 0.16 * s + 0.042 * s))
    set_mesh_tube(parts['rope'], [d0, d0.lerp(Bk, 0.5) + Vector((0, 0, -0.01 * s)), Bk], 0.007 * s, segs=6)


GUN_N = 8


def gun_spec(key, label, **kw):
    def build(P, root):
        return build_gun(P, root, **kw)
    return {'key': key, 'label': label, 'build': build, 'boost': CREW_BOOST, 'shadow': True, 'extra': gun_points,
            'pose0': lambda parts, P, root: pose_gun(parts, None),
            'modes': [('fire', GUN_N, lambda parts, P, root, f: pose_gun(parts, f))]}


def top_of(slot, **kw):
    """Ponto 'top' (origem da lata no jogo, DATA.TOWER_TOP): o posto da torreta mais a boca da catapulta."""
    t = gun_tip(**kw)
    return (slot[0] + t.x * 0.5, slot[1], slot[2] + t.z)


# ---------------------------------------------------------------- nivel 1: deck baixo de paletes sobre latas
def build_ar1(P, root):
    plot(root, P, 'ar1')
    lights = []
    dz = G + 0.2
    deck(root, P, 'ar1', 0.0, 0.06, 1.0, 0.74, dz, leg_r=0.06)
    rail(root, P, 'ar1_guarda', [(-0.48, -0.2), (-0.48, 0.41), (0.48, 0.41), (0.48, 0.05)], dz)
    # piramide de latas na frente, a direita, e a lata derramando
    pilha(root, P, 'ar1_pilha', 0.46, -0.44, G, 0.058, 3, rot=-0.45, gold=(5,))
    lata_derramando(root, P, 'ar1_derrama', 0.22, -0.6, r=0.055, rot=0.35, flow=0.22)
    # caixote de latas a esquerda, na frente
    caixote(root, P, 'ar1_caixote', -0.58, -0.4, G, w=0.26, d=0.2, hh=0.11, r=0.045, rot=0.35)
    lata(root, P, 'ar1_lataSolta', (-0.36, -0.58, G + 0.05 * 1.125), r=0.05, rot=0.6)
    # poste com refletor atras
    tube(root, 'ar1_poste', [(-0.66, 0.42, G), (-0.66, 0.42, G + 0.62)], 0.02, P['cA'], segs=8)
    work_lamp(root, P, 'ar1_refletor', (-0.62, 0.4, G + 0.6), face=-0.9)
    pennant(root, P, 'ar1_flamula', -0.66, 0.42, G + 0.62, pole=0.18, length=0.18, height=0.08)
    bandeirinha(root, 'ar1_bandeira', (0.42, 0.38, dz), h=0.36, w=0.2, fh=0.13)
    lights.append(((-0.6, 0.36, G + 0.58), '#ffcf7a', 14.0, 1))
    slot = (0.04, 0.0, dz)
    return {'slots': [slot, (-0.38, 0.24, dz)], 'lights': lights, 'points': {'top': top_of(slot, size=0.95)}}


# ---------------------------------------------------------------- nivel 2: deck alto, a torre de latas e a escada
def build_ar2(P, root):
    plot(root, P, 'ar2')
    lights = []
    dz = G + 0.44
    deck(root, P, 'ar2', 0.0, 0.08, 1.18, 0.96, dz, th=0.07, leg_r=0.075, braces=True)
    rail(root, P, 'ar2_guarda', [(-0.57, -0.1), (-0.57, 0.54), (0.57, 0.54), (0.57, 0.2)], dz)
    rail(root, P, 'ar2_guardaFrente', [(-0.57, -0.38), (-0.3, -0.38)], dz, front=True)
    # torre de latas gigantes empilhadas atras, a esquerda (meio torta), com o refletor e a bandeirola no alto
    sx_, sy_ = -0.4, 0.4
    rr_, n = 0.1, 4
    hh = rr_ * 2.25
    for k in range(n):
        off = (0.012 * math.sin(k * 2.1), 0.01 * math.cos(k * 1.7))
        lata(root, P, f'ar2_torre{k}', (sx_ + off[0], sy_ + off[1], dz + hh * (k + 0.5) + 0.001), r=rr_ * (1 - 0.03 * k), h=hh, rot=0.9 * k,
             label=P['label_gold'] if k == n - 1 else None)
    ztop = dz + hh * n
    pennant(root, P, 'ar2_flamula', sx_ + 0.03, sy_ + 0.02, ztop, pole=0.22, length=0.2, height=0.09)
    tube(root, 'ar2_bracoRefletor', [(sx_, sy_ - 0.06, ztop - 0.02), (sx_, sy_ - 0.12, ztop + 0.03)], 0.012, P['cA'], segs=6)
    work_lamp(root, P, 'ar2_refletor', (sx_, sy_ - 0.14, ztop + 0.04), face=-math.pi / 2)
    lights.append(((sx_, sy_ - 0.19, ztop + 0.02), '#ffcf7a', 14.0, 1))
    # escada pela direita
    stairs(root, P, 'ar2_escada', (0.7, -0.4, G), (0.68, 0.16, dz), w=0.16, steps=7)
    # por baixo e em volta: latas, caixotes, a lata gigante aberta e a poca de leite
    pilha(root, P, 'ar2_pilhaBaixo', -0.08, 0.2, G, 0.06, 3, rot=0.0)
    caixote(root, P, 'ar2_caixote', -0.62, -0.5, G, w=0.26, d=0.2, hh=0.11, r=0.045, rot=0.5)
    lata(root, P, 'ar2_lataSolta', (-0.8, -0.28, G + 0.06 * 1.125), r=0.06, rot=0.3)
    lata_derramando(root, P, 'ar2_derrama', -0.42, -0.66, r=0.055, rot=-0.4, flow=0.2)
    lata(root, P, 'ar2_latona', (0.3, 0.26, G + 0.15), r=0.135, h=0.3, rot=0.4, aberta=True)
    caixote(root, P, 'ar2_caixote2', 0.36, -0.24, G, w=0.22, d=0.18, hh=0.1, r=0.04, rot=-0.2)
    bandeirinha(root, 'ar2_bandeira', (0.52, 0.5, dz), h=0.36, w=0.2, fh=0.13)
    slot = (0.02, -0.06, dz)
    return {'slots': [slot, (-0.36, 0.1, dz), (0.38, 0.26, dz)], 'lights': lights, 'points': {'top': top_of(slot, size=1.05)}}


# ---------------------------------------------------------------- nivel 3: plataforma alta, a piramide de latas e o guindaste
def build_ar3(P, root):
    plot(root, P, 'ar3')
    lights = []
    fz = 0.8
    deck(root, P, 'ar3', 0.0, 0.04, 1.36, 1.12, fz, th=0.08, leg_r=0.085, inset=0.12, braces=True)
    rail(root, P, 'ar3_guarda', [(-0.66, -0.2), (-0.66, 0.58), (0.66, 0.58), (0.66, -0.2)], fz)
    rail(root, P, 'ar3_guardaFrenteE', [(-0.66, -0.5), (-0.36, -0.5)], fz, front=True)
    rail(root, P, 'ar3_guardaFrenteD', [(0.36, -0.5), (0.66, -0.5)], fz, front=True)
    # piramide de latas no fundo (4-3-2-1), a lata de ouro no topo e o giroflex laranja em cima
    r = 0.098
    pilha(root, P, 'ar3_piramide', -0.04, 0.4, fz, r, 4, rot=0.0, gold=(9,))
    zap = fz + 4 * r * 2.25
    giroflex(root, P, 'ar3_giroflex', (-0.04, 0.4, zap), s=1.0)
    # guindaste de mastro a direita: lanca e a lata pendurada que balanca; refletores no mastro
    mx, my = 0.52, 0.44
    tube(root, 'ar3_mastro', [(mx, my, fz), (mx, my, fz + 1.2)], 0.03, P['cA'], segs=10)
    for k, zz in enumerate((0.3, 0.62, 0.94)):
        torus(root, f'ar3_mastroCinta{k}', (mx, my, fz + zz), 0.036, 0.012, P['cB'], n=14, segs=5)
    box(root, 'ar3_mastroTopo', (0.1, 0.1, 0.06), (mx, my, fz + 1.22), m=P['cB'], bev=0.012)
    tube(root, 'ar3_lanca', [(mx, my, fz + 1.2), (0.3, 0.16, fz + 1.22)], 0.02, P['cA'], segs=8)
    tube(root, 'ar3_tirante', [(mx, my, fz + 1.25), (0.3, 0.16, fz + 1.23)], 0.007, P['steel_k'], segs=5)
    hook = empty(root, 'ar3_ganchoPivo', loc=(0.3, 0.16, fz + 1.2))
    kids(hook, tube(root, 'ar3_cabo', [(0, 0, 0), (0, 0, -0.3)], 0.008, P['steel_k'], segs=5))
    kids(hook, box(root, 'ar3_moitao', (0.05, 0.04, 0.06), (0, 0, -0.32), m=P['cB'], bev=0.01))
    lata(root, P, 'ar3_lataPend', (0, 0, -0.43), r=0.058, parent=hook)
    register_anim(hook, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.09 * math.sin(TAU * ph), 4, 'X')))
    for k, zz in enumerate((0.45, 0.85)):
        work_lamp(root, P, f'ar3_refletor{k}', (mx - 0.05, my - 0.04, fz + zz), face=math.radians(-150), tilt=0.3)
    lights.append(((mx - 0.1, my - 0.08, fz + 0.65), '#ffcf7a', 16.0, 1))
    lights.append(((-0.04, 0.36, zap + 0.08), '#ff9a3a', 18.0, 1))   # o giroflex (mesma ordem de luzes do Petrolao)
    # lata gigante aberta na esquerda com a colher gigante enfiada (como se come leite condensado)
    lata(root, P, 'ar3_latona', (-0.5, 0.38, fz + 0.17), r=0.15, h=0.34, rot=0.5, aberta=True)
    colher(root, 'ar3_colherona', P['inox'], L=0.62, r=0.09, loc=(-0.5, 0.38, fz + 0.2),
           rot=basis_euler((-0.45, 0.12, 0.88), (0.0, -1.0, 0.25)))
    # escada de marinheiro na perna da frente, a esquerda
    lx, ly = -0.36, -0.55
    for sx in (-1, 1):
        tube(root, f'ar3_escadaBanzo{sx}', [(lx + sx * 0.06, ly, G), (lx + sx * 0.06, ly, fz + 0.12)], 0.011, P['cC'], segs=6)
    for k in range(9):
        zz = G + 0.07 + k * (fz - G - 0.08) / 8
        tube(root, f'ar3_escadaDegrau{k}', [(lx - 0.06, ly, zz), (lx + 0.06, ly, zz)], 0.008, P['pallet_d'], segs=5)
    for k, zz in enumerate((0.45, 0.62, 0.79)):
        tube(root, f'ar3_gaiola{k}', [(lx - 0.06, ly, zz)] + [(lx - 0.06 * math.cos(a), ly - 0.09 * math.sin(a), zz) for a in (0.6, 1.2, 1.9, 2.5)] + [(lx + 0.06, ly, zz)],
             0.007, P['cC'], segs=5)
    # por baixo: o estoque (monte de latas e caixotes) e, na frente, latas e a poca de leite
    monte(root, P, 'ar3_estoque', -0.02, 0.18, G, 0.068, 3, gold_top=True)
    caixote(root, P, 'ar3_caixoteA', 0.34, 0.2, G, w=0.26, d=0.2, hh=0.11, r=0.045, rot=0.2)
    caixote(root, P, 'ar3_caixoteB', -0.34, 0.24, G, w=0.26, d=0.2, hh=0.11, r=0.045, rot=-0.15)
    pilha(root, P, 'ar3_pilhaFrente', 0.6, -0.56, G, 0.058, 3, rot=-0.5)
    lata_derramando(root, P, 'ar3_derrama', 0.3, -0.7, r=0.055, rot=0.3, flow=0.2)
    bandeirinha(root, 'ar3_bandeira', (0.6, 0.54, fz), h=0.38, w=0.2, fh=0.13)
    slot = (0.0, -0.08, fz)
    return {'slots': [slot, (-0.4, 0.1, fz), (0.4, 0.14, fz)], 'lights': lights, 'points': {'top': top_of(slot, size=1.12)}}


# ---------------------------------------------------------------- Compra de 15 Milhoes: a lata gigante e a montanha de paletes
def caixa_registradora(root, P, tag, x, y, z=G, rot=0.0):
    """Caixa registradora verde com teclas, visor apagado e a nota fiscal enorme (sem texto, so linhas cinza)
    saindo por cima e caindo enrolada no chao (a nota tremula no loop)."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rot)) as e:
        box(root, tag + '_gaveta', (0.3, 0.24, 0.07), (0, 0, 0.035), m=P['cA'], bev=0.015)
        box(root, tag + '_gavetaFrente', (0.22, 0.01, 0.035), (0, -0.122, 0.035), m=P['cB'], bev=0.004)
        box(root, tag + '_corpo', (0.26, 0.18, 0.1), (0, 0.02, 0.12), rot=(-0.25, 0, 0), m=P['cA'], bev=0.02)
        for i in range(4):
            for j in range(3):
                box(root, f'{tag}_tecla{i}{j}', (0.035, 0.03, 0.014), (-0.075 + 0.05 * i, -0.05 + 0.04 * j, 0.15 + 0.012 * j), rot=(-0.25, 0, 0),
                    m=P['shirt'] if (i + j) % 3 else P['cB'], bev=0.004)
        box(root, tag + '_visorPe', (0.03, 0.03, 0.08), (0.04, 0.09, 0.2), m=P['cA'], bev=0.006)
        box(root, tag + '_visor', (0.14, 0.03, 0.07), (0.04, 0.09, 0.26), rot=(0.2, 0, 0), m=P['steel_k'], bev=0.01)
        box(root, tag + '_visorTela', (0.11, 0.006, 0.045), (0.04, 0.073, 0.262), rot=(0.2, 0, 0), m=mat('visor_verde', '#7fe08f', rough=0.4, var=0.0, bump=0.0, emit=0.6), bev=0.002)
        cyl(root, tag + '_rolo', 0.03, 0.08, (-0.08, 0.08, 0.2), rot=(0, math.pi / 2, 0), m=P['paper'], v=14, bev=0.004)
    # a nota fiscal: tira de papel que sai do rolo, faz a curva e desce ate o chao, onde fica enrolada
    c, sn = math.cos(rot), math.sin(rot)

    def W(px, py):
        return (x + px * c - py * sn, y + px * sn + py * c)
    strip = cloth_grid(root, tag + '_nota', 0.06, 0.6, 1, 14, [P['paper'], P['ink']], thick=0.004,
                       shape=lambda u, v, co: Vector((co.x, -0.06 * math.sin(math.pi * v * 0.8) - 0.15 * v * v, co.z * (1 - 0.35 * v))))
    # listrinhas cinza de "itens" na nota (sem texto): faces alternadas no segundo material
    for k, p in enumerate(strip.data.polygons):
        if k % 2 == 1:
            p.material_index = 1
    strip.location = (*W(-0.11, 0.08), z + 0.235)
    strip.rotation_euler = (0, 0, rot + math.pi / 2)
    register_cloth(strip, hang_wave(0.6, amp=0.025, axis='X', cycles=1, waves=0.7, top=0.0))
    gx, gy = W(-0.28, -0.08)
    for k in range(3):
        torus(root, f'{tag}_notaRolo{k}', (gx + 0.02 * k, gy - 0.015 * k, G + 0.02 + 0.012 * k), 0.05 - 0.008 * k, 0.012, P['paper'], axis='Y', n=18, segs=5)
    return e


def etiqueta(root, P, tag, loc, s=1.0):
    """Etiqueta de preco gigante (sem numero: furo e cordao) pendurada, balancando."""
    piv = empty(root, tag + '_pivo', loc=loc)
    kids(piv, tube(root, tag + '_cordao', [(0, 0, 0), (0.0, 0, -0.08 * s)], 0.005, P['steel_k'], segs=4))
    pts = [(-0.06, 0.0), (0.06, 0.0), (0.1, -0.05), (0.1, -0.2), (-0.1, -0.2), (-0.1, -0.05)]
    t = prism_xz(root, tag + '_etiqueta', [(px * s, pz * s - 0.08 * s) for px, pz in pts], 0.012, P['cB'], bev=0.004)
    kids(piv, t)
    kids(piv, torus(root, tag + '_furo', (0, 0, -0.105 * s), 0.016 * s, 0.006, P['cA'], axis='Y', n=12, segs=4))
    for k in range(2):
        kids(piv, box(root, f'{tag}_risco{k}', (0.12 * s, 0.016, 0.018 * s), (0, 0, (-0.16 - 0.04 * k) * s), m=P['cA'], bev=0.003))
    register_anim(piv, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.18 * math.sin(TAU * ph), 4, 'Y') @ Matrix.Rotation(0.1 * math.sin(TAU * ph + 1), 4, 'X')))
    return piv


def build_arM(P, root):
    plot(root, P, 'arM')
    lights = []
    fz = 0.76
    R = 0.72
    # a lata gigante: corpo de folha com os frisos, o rotulo em faixas e a tampa (o deck) com os aneis
    lathe(root, 'arM_lata', [(G, R * 0.96, R * 0.96), (G + 0.025, R + 0.012, R + 0.012), (G + 0.06, R * 0.985, R * 0.985),
                             (fz - 0.06, R * 0.985, R * 0.985), (fz - 0.025, R + 0.012, R + 0.012), (fz, R * 0.97, R * 0.97)],
          P['tin'], segs=56, lv=1, caps=False, solid=0.03)
    cyl(root, 'arM_rotulo', R + 0.01, fz - G - 0.13, (0, 0, (fz + G) / 2), m=P['label'], v=56, bev=0.0, caps=False)
    cyl(root, 'arM_tampa', R * 0.965, 0.04, (0, 0, fz - 0.02), m=P['tin_d'], v=56, bev=0.01)
    for k, rr in enumerate((0.56, 0.4)):
        torus(root, f'arM_tampaAnel{k}', (0, 0, fz), rr, 0.012, P['tin'], n=48, segs=5)
    torus(root, 'arM_frisoOuro', (0, 0, fz - 0.03), R + 0.016, 0.014, P['gold'], n=56, segs=6)
    rail(root, P, 'arM_guarda', [(0.69 * math.cos(math.radians(a)), 0.69 * math.sin(math.radians(a))) for a in range(-20, 201, 20)], fz)
    # porta verde de casinha na frente da lata, com a placa da chapa na faixa branca em cima
    box(root, 'arM_porta', (0.2, 0.05, 0.3), (0.0, -0.7, G + 0.17), m=P['cA'], bev=0.02, front=True)
    box(root, 'arM_portaMoldura', (0.24, 0.04, 0.33), (0.0, -0.69, G + 0.165), m=P['cB'], bev=0.012, front=True)
    sphere(root, 'arM_portaMacaneta', 0.018, (0.06, -0.73, G + 0.17), m=P['gold'], seg=8, front=True)
    placa_chapa(root, 'arM_placa', 0.24, 0.15, (0.0, -0.715, G + 0.48), th=0.03)
    # a montanha de paletes de latas no fundo do deck (a mais alta com o giroflex), latas de ouro no topo
    zA = carga(root, P, 'arM_cargaA', -0.3, 0.4, fz, nx=3, ny=2, r=0.06, units=4, layers=2, gold_top=True, rot=0.12)
    zB = carga(root, P, 'arM_cargaB', 0.08, 0.5, fz, nx=2, ny=2, r=0.06, units=3, layers=2, rot=-0.08)
    zC = carga(root, P, 'arM_cargaC', 0.36, 0.36, fz, nx=2, ny=2, r=0.06, units=2, layers=2, gold_top=True, rot=0.2)
    carga(root, P, 'arM_cargaD', -0.56, 0.08, fz, nx=2, ny=2, r=0.055, units=1, layers=2, rot=-0.3)
    giroflex(root, P, 'arM_giroflex', (-0.3, 0.4, zA), s=1.25)
    lights.append(((-0.3, 0.36, zA + 0.1), '#ff9a3a', 22.0, 1))
    etiqueta(root, P, 'arM_etiqueta', (0.08, 0.36, zB - 0.05), s=1.15)
    pennant(root, P, 'arM_flamula', 0.36, 0.36, zC, pole=0.22, length=0.2, height=0.09)
    # no chao: palete de latas, latas soltas e a caixa registradora com a nota fiscal enorme
    carga(root, P, 'arM_chaoA', -0.72, -0.34, G, nx=2, ny=2, r=0.05, units=2, rot=0.5, gold_top=True)
    for k, (x, y) in enumerate(((0.76, -0.16), (0.8, 0.06))):
        lata(root, P, f'arM_lataChao{k}', (x, y, G + 0.065 * 1.125), r=0.065, rot=k)
    lata(root, P, 'arM_lataDeitada', (-0.42, -0.74, G + 0.06), r=0.06, lying=True, rot=0.3, label=P['label_gold'])
    caixa_registradora(root, P, 'arM_caixa', 0.5, -0.6, rot=0.35)
    lights.append(((0.0, -0.72, G + 0.4), '#ffcf7a', 10.0, 0))
    slot = (0.0, -0.08, fz)
    return {'slots': [slot, (0.44, 0.16, fz)], 'lights': lights, 'points': {'top': top_of(slot, size=1.12, royal=True)}}


# ---------------------------------------------------------------- Batedeira Industrial: a batedeira gigante e o batedor que bate na tigela
BEAM_Z = 2.06
BIT_Z = G + 0.03      # onde o batedor bate (posto do conjunto arH)


def lamp_post(root, P, tag, base, head, lights, face=-math.pi / 2, arm=None):
    """Poste verde com o refletor na ponta (ou so o braco `arm` = (de, ate) preso em outra peca)."""
    if arm:
        p0, p1 = arm
        tube(root, tag + '_braco', [p0, p1], 0.018, P['cA'], segs=8)
        hx, hy, hz = p1[0], p1[1], p1[2] - 0.04
    else:
        bx, by = base
        hx, hy, hz = head
        tube(root, tag + '_poste', [(bx, by, G), (bx, by, hz + 0.06), (hx, hy, hz + 0.08)], 0.02, P['cA'], segs=8)
        cyl(root, tag + '_pe', 0.05, 0.03, (bx, by, G + 0.015), m=P['cB'], v=14, bev=0.006)
    work_lamp(root, P, tag + '_refletor', (hx, hy, hz), face=face, tilt=0.5)
    lights.append(((hx + 0.05 * math.cos(face), hy + 0.05 * math.sin(face), hz - 0.03), '#ffcf7a', 14.0, 1))


def build_arS(P, root):
    plot(root, P, 'arS')
    lights = []
    G_ = P['cA']
    # tigela de inox: metade de tras na base, o arco da frente (direita do posto do confeiteiro) na camada da frente
    prof = [(G - 0.01, 0.28, 0.28), (G + 0.04, 0.35, 0.35), (G + 0.1, 0.4, 0.4), (G + 0.14, 0.415, 0.415)]
    lathe(root, 'arS_tigela', prof, P['inox'], segs=48, lv=1, caps=False, solid=0.02,
          cut=lambda c: c.y < 0 and c.x > -0.14)
    lathe(root, 'arS_tigelaFrente', prof, P['inox'], segs=48, lv=1, caps=False, solid=0.02,
          cut=lambda c: not (c.y < 0 and c.x > -0.14))['front'] = 1
    torus(root, 'arS_borda', (0, 0, G + 0.14), 0.415, 0.022, P['inox'], n=48, segs=6)
    bf = torus(root, 'arS_bordaFrente', (0, 0, G + 0.142), 0.417, 0.022, P['inox'], n=48, segs=6, front=True)
    bm_ = bmesh.new()
    bm_.from_mesh(bf.data)
    dead = [v for v in bm_.verts if not (v.co.y < -0.05 and v.co.x > -0.16)]
    bmesh.ops.delete(bm_, geom=dead, context='VERTS')
    bm_.to_mesh(bf.data)
    bm_.free()
    # o leite condensado na tigela, com o redemoinho mais douradinho e um montinho no meio
    cyl(root, 'arS_leite', 0.39, 0.02, (0, 0, BIT_Z + 0.025), m=P['milk'], v=48, bev=0.008)
    tube(root, 'arS_redemoinho', [(0.28 * (1 - t) * math.cos(TAU * 1.6 * t), 0.28 * (1 - t) * math.sin(TAU * 1.6 * t), BIT_Z + 0.036 + 0.01 * t)
                                  for t in [j / 30 for j in range(31)]], 0.014, P['milk_d'], segs=6)
    # anel de pes da tigela no lote (verde com filete amarelo)
    cyl(root, 'arS_pedestal', 0.33, 0.03, (0, 0, G + 0.012), m=G_, v=40, bev=0.008)
    # a batedeira de pe vista de lado (a silhueta classica): pe verde a esquerda com a chapa que vai ate a tigela, o
    # pescoco grosso subindo e a cabeca grande deitada para a direita, por cima da tigela
    fx, fy = -0.52, 0.04
    cyl(root, 'arS_baseB', 0.3, 0.14, (fx, fy, G + 0.07), m=G_, v=40, bev=0.05).scale = (1.0, 0.82, 1.0)
    torus(root, 'arS_baseFriso', (fx, fy, G + 0.13), 0.288, 0.013, P['cB'], n=40, segs=5).scale = (1.0, 0.81, 1.0)
    box(root, 'arS_baseChapa', (0.3, 0.3, 0.05), (-0.3, 0.04, G + 0.025), m=G_, bev=0.02)
    hz = BEAM_Z + 0.2
    neck = [(fx, fy, G + 0.12), (fx - 0.02, fy, 0.8), (fx, fy, 1.5), (fx + 0.06, fy - 0.01, 1.95), (fx + 0.14, 0.0, hz)]
    tube(root, 'arS_pescoco', neck, 0.2, G_, segs=24, rfun=lambda t: 0.21 - 0.04 * math.sin(math.pi * min(1.0, t * 1.3)))
    for k, zz in enumerate((0.55, 1.35)):
        torus(root, f'arS_pescocoFriso{k}', (fx - 0.01, fy, zz), 0.178, 0.014, P['cB'], n=28, segs=5)
    # cabeca: capsula deitada ao longo de X, com a faixa cromada, o nariz cromado e o bocal do batedor embaixo
    head = lathe(root, 'arS_cabeca', [(-0.46, 0.0, 0.0), (-0.42, 0.14, 0.15), (-0.3, 0.23, 0.25), (-0.05, 0.25, 0.27), (0.22, 0.24, 0.26),
                                      (0.4, 0.19, 0.2), (0.5, 0.0, 0.0)], G_, segs=32, lv=2, caps=False)
    head.rotation_euler = (0, math.pi / 2, 0)
    head.location = (-0.18, 0, hz)
    faixa = torus(root, 'arS_cabecaFaixa', (0, 0, 0), 0.25, 0.02, P['inox'], axis='X', n=36, segs=6)
    faixa.location = (0.11, 0, hz)
    faixa.scale = (1.0, 1.06, 0.96)
    sphere(root, 'arS_nariz', 0.14, (0.27, 0, hz), scale=(0.42, 1.0, 0.9), m=P['inox'], seg=22)
    cyl(root, 'arS_bocal', 0.065, 0.1, (0, 0.0, BEAM_Z + 0.03), m=P['inox'], v=20, bev=0.012)
    torus(root, 'arS_bocalAnel', (0, 0.0, BEAM_Z - 0.01), 0.064, 0.015, P['cB'], n=20, segs=5)
    # o emblema da chapa na lateral da cabeca que a camera ve (onde fica a marca numa batedeira de verdade)
    placa_chapa(root, 'arS_emblema', 0.2, 0.14, (-0.24, -0.268, hz + 0.01), plate=False)
    pennant(root, P, 'arS_flamula', -0.44, 0.06, hz + 0.18, pole=0.2, length=0.24, height=0.11)
    # alavanca de velocidade atras da cabeca e o botao de giro (engrenagem que gira) na frente do pescoco
    tube(root, 'arS_alavanca', [(-0.52, -0.14, hz + 0.08), (-0.58, -0.24, hz + 0.18)], 0.016, P['inox'], segs=6)
    sphere(root, 'arS_alavancaPomo', 0.034, (-0.58, -0.24, hz + 0.18), m=P['cB'], seg=10)
    gp = empty(root, 'arS_engrenagemPivo', loc=(fx - 0.01, fy - 0.205, 1.02), rot=(math.pi / 2, 0, 0))
    kids(gp, torus(root, 'arS_engrenagemAro', (0, 0, 0), 0.075, 0.016, P['cB'], n=24, segs=6))
    for k in range(10):
        a = TAU * k / 10
        kids(gp, box(root, f'arS_dente{k}', (0.03, 0.025, 0.025), (0.092 * math.cos(a), 0.092 * math.sin(a), 0), rot=(0, 0, a), m=P['cB'], bev=0.005))
    for k in range(3):
        a = TAU * k / 3
        kids(gp, tube(root, f'arS_raio{k}', [(0, 0, 0), (0.07 * math.cos(a), 0.07 * math.sin(a), 0)], 0.012, P['inox'], segs=6))
    kids(gp, cyl(root, 'arS_engrenagemCubo', 0.03, 0.05, (0, 0, 0), m=P['inox'], v=12, bev=0.006))
    register_anim(gp, spin('Z', sym=10, turns=1))
    # luzes: poste a direita da tigela e o refletor num braco do pescoco, os dois olhando para o batedor
    lamp_post(root, P, 'arS_luz0', (-0.33, -0.1), (0.0, 0.0, 0.0), lights, arm=((fx + 0.12, fy - 0.1, 0.95), (-0.32, -0.1, 0.92)), face=-0.45)
    lamp_post(root, P, 'arS_luz1', (0.56, -0.02), (0.38, -0.06, 0.9), lights, face=math.radians(-140))
    # utensilios pendurados no lado do pescoco: a colher de pau balancando
    cw = empty(root, 'arS_pendPivo', loc=(fx - 0.22, fy - 0.02, 1.62))
    kids(cw, tube(root, 'arS_gancho', [(0.08, 0, 0.03), (0, 0, 0), (0, 0, -0.04)], 0.008, P['inox'], segs=5))
    kids(cw, tube(root, 'arS_colherPau', [(0, 0, -0.04), (0, 0, -0.32)], 0.014, P['pallet_d'], segs=8))
    kids(cw, sphere(root, 'arS_colherPauConcha', 0.045, (0, 0, -0.36), scale=(1.0, 0.45, 1.3), m=P['pallet_d'], seg=12))
    register_anim(cw, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.12 * math.sin(TAU * ph), 4, 'Y')))
    # a lata gigante tombada num cavalete, a direita, derramando leite condensado na tigela
    lx, ly = 0.6, 0.3
    for sx in (-1, 1):
        tube(root, f'arS_cavalete{sx}', [(lx + sx * 0.09, ly - 0.08, G), (lx + sx * 0.07, ly, G + 0.42), (lx + sx * 0.09, ly + 0.08, G)], 0.016, P['cA'], segs=6)
    lata(root, P, 'arS_lataDerrama', (lx - 0.02, ly, G + 0.5), r=0.12, h=0.27, tilt=(0, math.radians(-105), math.radians(20)), aberta=True)
    tube(root, 'arS_fio', [(0.45, 0.25, 0.53), (0.4, 0.22, 0.45), (0.34, 0.19, 0.3), (0.31, 0.17, BIT_Z + 0.04)],
         0.022, P['milk'], segs=10, rfun=lambda t: 0.026 - 0.008 * t)
    # caixotes e latas no fundo e o painel do confeiteiro na frente, a esquerda
    caixote(root, P, 'arS_caixote', -0.42, 0.52, G, w=0.26, d=0.2, hh=0.11, r=0.045, rot=-0.3)
    carga(root, P, 'arS_carga', 0.2, 0.6, G, nx=2, ny=2, r=0.05, units=2, rot=0.4)
    box(root, 'arS_painel', (0.12, 0.08, 0.2), (-0.5, -0.5, G + 0.1), rot=(0, 0, 0.5), m=P['cA'], bev=0.015)
    box(root, 'arS_painelTela', (0.09, 0.01, 0.07), (-0.48, -0.54, G + 0.15), rot=(0, 0, 0.5), m=P['steel_k'], bev=0.004)
    for k in range(3):
        sphere(root, f'arS_botao{k}', 0.012, (-0.505 + 0.03 * k * math.cos(0.5), -0.55 + 0.03 * k * math.sin(0.5), G + 0.08), m=(P['cB'], P['red'], P['cT'])[k], seg=8)
    tube(root, 'arS_alavancaPainel', [(-0.46, -0.48, G + 0.2), (-0.42, -0.46, G + 0.3)], 0.008, P['inox'], segs=5)
    sphere(root, 'arS_alavancaPomoP', 0.02, (-0.42, -0.46, G + 0.3), m=P['red'], seg=8)
    pilha(root, P, 'arS_pilha', 0.6, -0.48, G, 0.055, 2, rot=-0.5)
    poca(root, P, 'arS_poca', 0.66, -0.62, 0.12, 0.08)
    return {'slots': [(0.0, 0.0, BIT_Z), (-0.24, -0.64, G)], 'lights': lights, 'points': {'top': (0.0, 0.0, 1.1)}}


def build_hammer(P, root):
    """Batedor de arame (fouet) gigante: os arames do balao com leite condensado grudado, o cabo de inox com a luva
    verde e o engate em cima; a haste telescopica sobe ate a cabeca da batedeira."""
    tag = root['set']
    piv = empty(root, tag + '_piv', loc=(0, 0, 0))
    spin_e = empty(root, tag + '_giro', parent=piv)
    with grupo(root, tag + '_fouet', parent=spin_e):
        zb, zt, Rw = 0.02, 0.5, 0.13
        for k in range(6):
            a = math.pi * k / 6
            pts = []
            for j in range(24):
                ph = TAU * j / 24
                bulge = 0.72 + 0.28 * ((1 - math.cos(ph)) / 2)
                z = (zt + zb) / 2 + (zt - zb) / 2 * math.cos(ph)
                rr_ = Rw * math.sin(ph) * bulge * (1.0 - 0.5 * max(0.0, (z - 0.35) / (zt - 0.35)))
                pts.append((rr_ * math.cos(a), rr_ * math.sin(a), z))
            tube(root, f'{tag}_arame{k}', pts, 0.011, P['inox'], segs=6, closed=True)
        # leite condensado grudado nos arames
        sphere(root, tag + '_grude', 0.07, (0, 0, 0.12), scale=(1.15, 1.15, 0.8), m=P['milk'], seg=16)
        sphere(root, tag + '_pingo', 0.022, (0.03, 0.0, 0.03), scale=(1, 1, 1.4), m=P['milk'], seg=10)
        cyl(root, tag + '_cabo', 0.04, 0.28, (0, 0, 0.62), m=P['inox'], v=16, bev=0.01)
        cyl(root, tag + '_luva', 0.048, 0.1, (0, 0, 0.62), m=P['cA'], v=16, bev=0.012)
        torus(root, tag + '_anel', (0, 0, 0.5), 0.042, 0.012, P['cB'], n=16, segs=5)
        cyl(root, tag + '_engate', 0.055, 0.06, (0, 0, 0.79), m=P['cB'], v=16, bev=0.012)
    ch = ensure_mesh(root, tag + '_haste', P['inox'])
    ch['set'] = root['set']
    return {'piv': piv, 'spin': spin_e, 'chain': ch, 'top': BEAM_Z - BIT_Z}


HAMMER_N = 8


def pose_hammer(parts, f):
    """slam: sobe (0..4), cai (5) e bate (6), quica (7) girando o batedor; idle = alto."""
    hz = [0.78, 0.86, 0.94, 1.0, 1.02, 0.5, 0.0, 0.04][f] if f is not None else 0.9
    parts['piv'].location = (0, 0, hz)
    parts['spin'].rotation_euler = (0, 0, (f or 0) * math.pi / 6 / 2)
    set_mesh_tube(parts['chain'], [(0, 0, hz + 0.82), (0, 0, max(hz + 0.86, parts['top']))], 0.026, segs=10)


# ---------------------------------------------------------------- a turma da chapa V
def bone(root, pr, tag, m):
    """Aba do bone (o 'cap' do build_person e a copa)."""
    o = cyl(root, tag + '_boneAba', 0.06, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.18, 0)
    return o


def peito_chapa(root, pr, tag, P):
    """Gola verde redonda com o decote em V da camisa da selecao (R: estrela branca no peito)."""
    if CHAPA == 'R':
        return estrela_peito(root, tag, pr['body'], (0.084, 0, 0.395), r=0.03, rot=(0, 0, math.pi / 2))
    gm = P['gola']
    out = [tube(root, tag + '_golaV', [(0.05, -0.038, 0.468), (0.085, 0.0, 0.415), (0.05, 0.038, 0.468)], 0.009, gm, segs=6)]
    ring = torus(root, tag + '_golaAnel', (0, 0, 0.474), 0.06, 0.009, gm, n=20, segs=5)
    ring.scale = (0.8, 1.0, 1.0)
    out.append(ring)
    return kids(pr['body'], *out)


def torcedor(P, root, tag, head='cap', scarf=None):
    """Torcedor da chapa: camisa amarela da selecao com gola verde, calcao azul, perna de fora, meiao e tenis
    brancos; bone verde (head='cap') ou outro chapeu."""
    sp = dict(tunic=P['camisa'], skirt_m=P['calca'], head=head, head_m=P['bone'], belt=None, pants=P['skin'],
              boot_m=P['sneaker'], boot_cuff=P['sneaker'], bare_hands=True, bracer=P['skin'], scarf=scarf)
    pr = build_person(P, root, tag, sp)
    peito_chapa(root, pr, tag, P)
    if head == 'cap':
        bone(root, pr, tag, P['bone'])
    return pr


def chapeu_confeiteiro(root, pr, tag, P):
    """Chapeu de confeiteiro (toque branco fofo) no pivo da cabeca."""
    out = [cyl(root, tag + '_toqueFaixa', 0.074, 0.05, (0, 0, 0), m=P['chef'], v=20, bev=0.01)]
    out[0].location = HC + Vector((0, 0, 0.055))
    for k, (dx, dy) in enumerate(((0.03, 0.0), (-0.03, 0.03), (-0.03, -0.03), (0.0, 0.0))):
        o = sphere(root, f'{tag}_toqueBolo{k}', 0.05 if k < 3 else 0.06, (0, 0, 0), m=P['chef'], seg=14)
        o.location = HC + Vector((dx, dy, 0.12 if k < 3 else 0.14))
        out.append(o)
    for o in out:
        o.parent = pr['head']
    return out


def colher_mao(root, tag, P, gold=False):
    """Colher gigante na mao (empunhadura em z = 0, a concha para cima)."""
    m = P['gold'] if gold else P['inox']
    out = [tube(root, tag + '_cabo', [(0, 0, -0.08), (0, 0, 0.2)], 0.014, m, segs=8, rfun=lambda t: 0.013 + 0.006 * t)]
    c = lathe(root, tag + '_concha', [(0, 0.0, 0.0), (0.01, 0.04, 0.04), (0.028, 0.05, 0.05), (0.036, 0.053, 0.053)], m, segs=18, lv=1, caps=False, solid=0.007)
    c.location = (0.0, 0, 0.255)
    c.rotation_euler = (0, -math.pi / 2, 0)
    c.scale = (1.0, 1.0, 1.35)
    out.append(c)
    if not gold:
        out.append(cyl(root, tag + '_punho', 0.017, 0.07, (0, 0, -0.04), m=P['cA'], v=10, bev=0.004))
    return out


def cabelo_curto(root, pr, tag, m):
    """Cabelo curto penteado (so o alto e a nuca, a testa e as orelhas de fora), no pivo da cabeca."""
    def cut(c):
        return abs(math.atan2(c.y, c.x)) < math.radians(62) and c.z < 0.032
    o = lathe(root, tag + '_cabeloCurto', [(-0.012, 0.069, 0.071), (0.02, 0.073, 0.075), (0.05, 0.06, 0.062), (0.07, 0.034, 0.034), (0.08, 0.0, 0.0)],
              m, segs=18, lv=2, caps=False, solid=0.01, cut=cut)
    o.parent = pr['head']
    o.location = HC
    return o


def build_gunner(P, root):
    tag = root['set']
    pr = torcedor(P, root, tag)
    hold(pr, 'R', *colher_mao(root, tag + '_colher', P))
    return pr


def build_loader(P, root):
    tag = root['set']
    pr = torcedor(P, root, tag)
    b = lata(root, P, tag + '_lata', (0, 0, 0.0), r=0.05)
    hold(pr, 'L', b)
    return pr


def build_master(P, root):
    """Comprador da Compra de 15 Milhoes: terno escuro, camisa clara, gravata verde, broche amarelo, cabelo penteado
    e a colher de ouro na mao."""
    tag = root['set']
    hair = mat('cabelo_comprador', '#a99f93', rough=0.6, var=0.02, bump=0.2)
    pr = build_person(P, root, tag, dict(tunic=P['suit'], vest=P['shirt'], head='bald', brow_m=hair,
                                         belt=P['steel_k'], buckle=P['gold'], pants=P['suit'], boot_m=P['rubber'], glove=P['skin'], bare_hands=True,
                                         sleeve=P['suit']))
    cabelo_curto(root, pr, tag, hair)
    tie = tube(root, tag + '_gravata', [(0.095, 0, 0.45), (0.103, 0, 0.38), (0.1, 0, 0.32)], 0.012, P['cA'], segs=6,
               rfun=lambda t: 0.01 + 0.012 * t)
    tie.parent = pr['body']
    if CHAPA == 'R':
        estrela_peito(root, tag, pr['body'], (0.09, -0.05, 0.43), r=0.017, rot=(0, 0, math.pi / 2))
    else:
        kids(pr['body'], sphere(root, tag + '_broche', 0.013, (0.093, -0.05, 0.43), m=P['cB'], seg=10))
    hold(pr, 'R', *colher_mao(root, tag + '_colher', P, gold=True))
    return pr


def build_engineer(P, root):
    """Confeiteiro da batedeira: a turma da chapa com lenco verde no pescoco e o chapeu branco de confeiteiro."""
    tag = root['set']
    pr = torcedor(P, root, tag, head='bald', scarf=P['gola'])
    chapeu_confeiteiro(root, pr, tag, P)
    return pr


IDLE_N, FIRE_N = 12, 8


def gunner_state(mode, f):
    """fire: ergue a colher (0..2), bate na trava (3) e descansa (4..7)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.06, -0.13, 0.32 + 0.008 * s), grip_R=(0.3, 0.0, 1.0), hand_L=(0.04, 0.13, 0.27),
                    breathe=s, head_yaw=0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.1, ph=ph)
    k = [0.3, 0.7, 1.0, 0.9, 0.5, 0.3, 0.15, 0.05][f]
    back = [0, 0, 0, 0.6, 1.0, 0.7, 0.3, 0.1][f]
    return dict(hand_R=(0.08 + 0.14 * k, -0.1 + 0.04 * k, 0.32 + 0.06 * k), grip_R=(0.3 + 0.9 * k, 0, 1.0 - 0.6 * k),
                hand_L=(0.02 - 0.06 * back, 0.14, 0.3 + 0.12 * back), lean=0.18 * k - 0.16 * back, head_pitch=-0.1 + 0.1 * back,
                head_yaw=0.2 - 0.3 * back, ph=f / FIRE_N)


def loader_state(mode, f):
    """fire: depois do disparo, pega uma lata (0..3) e poe na concha (4..7)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.1, 0.06, 0.3 + 0.006 * s), hand_R=(0.08, -0.1, 0.28), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph), head_pitch=-0.1, ph=ph)
    t = f / (FIRE_N - 1)
    up = math.sin(math.pi * t)
    return dict(hand_L=(0.08 + 0.12 * t, 0.06 - 0.06 * t, 0.26 + 0.28 * up), hand_R=(0.08 + 0.12 * t, -0.06, 0.26 + 0.26 * up),
                lean=0.15 * up, head_pitch=-0.2 * up, head_yaw=0.1, ph=t)


def engineer_state(mode, f):
    """fire: puxa a alavanca da batedeira (0..3) e solta (4..7)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.18, -0.06, 0.36 + 0.01 * s), hand_L=(0.16, 0.06, 0.34 + 0.01 * s), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph), head_pitch=-0.15, ph=ph)
    k = math.sin(math.pi * min(1.0, f / 4))
    return dict(hand_R=(0.18 - 0.1 * k, -0.06, 0.36 - 0.14 * k), hand_L=(0.16 - 0.1 * k, 0.06, 0.34 - 0.14 * k), lean=-0.15 * k,
                head_pitch=-0.15 + 0.1 * k, head_yaw=0.1, ph=f / FIRE_N)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 3, 'fire'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('fire', FIRE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'fire'))]}


SPEC = {
    'show_crew': {'ar1': ['arT1', 'arG'], 'ar2': ['arT2', 'arG', 'arC'], 'ar3': ['arT3', 'arG', 'arC'], 'arM': ['arTM', 'arR'], 'arS': ['arH', 'arE']},
    'towers': [('ar1', 'Leite Condensado N1', build_ar1), ('ar2', 'Leite Condensado N2', build_ar2), ('ar3', 'Leite Condensado N3', build_ar3),
               ('arM', 'Compra de 15 Milhoes', build_arM), ('arS', 'Batedeira Industrial', build_arS)],
    'crews': [crew('arG', 'Torcedor da colher', build_gunner, gunner_state), crew('arC', 'Carregador de lata', build_loader, loader_state),
              crew('arR', 'Comprador', build_master, gunner_state), crew('arE', 'Confeiteiro', build_engineer, engineer_state)],
    'turrets': [gun_spec('arT1', 'Catapulta de colher 1', size=0.95), gun_spec('arT2', 'Catapulta de colher 2', size=1.05, ornate=1),
                gun_spec('arT3', 'Catapulta de colher 3', size=1.12, ornate=2), gun_spec('arTM', 'Catapulta de colher de ouro', size=1.12, royal=True),
                {'key': 'arH', 'label': 'Batedor da batedeira', 'build': build_hammer, 'boost': 1.0,
                 'pose0': lambda parts, P, root: pose_hammer(parts, None),
                 'modes': [('slam', HAMMER_N, lambda parts, P, root, f: pose_hammer(parts, f))]}],
}


if __name__ == '__main__':
    main(FAM, SPEC)
