"""Sindicato (Ninguem Sobe a Rampa, so a CHAPA=R): a sede do sindicato no lugar da Rachadinha, na familia 'quartel'
(motor 'barracks'). Predinho de paredes creme com platibanda vermelha, faixas (estandartes) vermelhas com a estrela
branca penduradas na fachada (pano liso, sem letra nenhuma), a corneta de som (megafone de poste) no telhado e a porta
de onde saem os militantes (o ponto 'door' continua no mesmo lugar). Niveis 1 a 3 crescem em andares, faixas,
cornetas e bandeira; a Diretoria do Sindicato (lancers) ganha um palanque com caixas de som e a tenda listrada do
sindicato; os Pelegos (monks) sao a sala de descanso: rede com um pelego dormindo, garrafa termica, cadeiras de
plastico e guarda-sol na laje.

Os nomes de conjuntos, postos, pontos e modos sao os mesmos do torre_quartel.py (js/sprites.js depende deles):
qt1, qt2, qt3, qtL (lancers), qtM (monks) e a tripulacao qtG, qtS, qtL_c, qtM_c (modos idle 12 e act 8).
Tripulacao de militantes: camiseta vermelha com a estrela branca no peito, bone vermelho e calca jeans escura.
  qtG   Militante (apito na boca e bandeirinha da chapa; act: agita a bandeirinha)
  qtS   Coordenador (megafone de mao e panfletos; act: grita no megafone de punho erguido)
  qtL_c Presidente do sindicato (barba grisalha, lenco vermelho e microfone; act: discursa acenando)
  qtM_c Pelego (colete de pelego de carneiro, chinelo e cafezinho; act: espreguica e boceja)

So existe a versao R (a V continua a Rachadinha do torre_quartel.py):
  CHAPA=R Blender -b -P tools/blender/torre_sindicato.py -- render arte/render_r/quartel [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_sindicato.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_sindicato.py -- crew <arquivo.png> [amostras]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto branco de Brasilia (padrao de todas as torres)
from chapa import CHAPA, PAL, cor, estrela   # cores da chapa (este script e da CHAPA=R)
from pecas_zcv import marca_peito, HC

FAM = 'quartel'
ROT = math.radians(12)      # o predio gira um pouco para mostrar a lateral esquerda (a que pega sol)
Z0 = 0.07                   # chao do lote de Brasilia no codigo (topo 0.15 menos o LIFT que o build_family soma)

import lib as _lib
_orig_palette2 = palette2


def palette2():   # noqa: F811 - sede do sindicato: creme, vermelho e branco da chapa
    P = _orig_palette2()
    P['teal'] = cor('pri', rough=0.8, sheen=0.4)
    P['stripes'] = mat('toldo_chapa_' + CHAPA, PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(3.6, '#fff6f0', PAL['pri']), sheen=0.4)
    P['plume'] = mat('pluma_chapa_' + CHAPA, PAL['pri'], rough=0.9, var=0.0, bump=0.1, sheen=0.6)
    P['concrete'] = mat('concreto', '#efebe2', rough=0.88, var=0.03, bump=0.18)
    P['concrete_d'] = mat('concreto_junta', '#c9c2b4', rough=0.9, var=0.02, bump=0.1)
    P['wall'] = mat('parede_sindicato', '#f3e2c4', rough=0.86, var=0.03, bump=0.12)
    P['wall_m'] = mat('parede_pelego', '#ecdcc2', rough=0.9, var=0.04, bump=0.14)
    P['roof'] = mat('laje_sindicato', '#d7d0c4', rough=0.9, var=0.03, bump=0.12)
    P['trim_w'] = mat('friso_branco', '#fbf7f0', rough=0.6, var=0.02, bump=0.04)
    P['red'] = cor('pri', rough=0.55)
    P['red_d'] = cor('escuro', rough=0.6)
    P['red_cloth'] = cor('pri', rough=0.8, sheen=0.4)
    P['white_cloth'] = mat('pano_branco_estrela', '#ffffff', rough=0.7, var=0.0, bump=0.02, sheen=0.3)
    P['faded'] = mat('pano_desbotado', '#e58c84', rough=0.85, var=0.03, bump=0.06, sheen=0.4)
    P['glass_d'] = mat('vidro_escuro', '#35566e', rough=0.12, var=0.02, bump=0.0)
    P['door_red'] = mat('porta_vermelha', '#b3201f', rough=0.4, var=0.03, bump=0.04)
    P['horn'] = mat('corneta_branca', '#eeebe4', rough=0.35, metal=0.15, var=0.02, bump=0.02)
    P['horn_d'] = mat('corneta_escura', '#45484f', rough=0.5, metal=0.3, var=0.02, bump=0.02)
    P['plastic'] = mat('plastico_branco', '#f6f5f0', rough=0.32, var=0.02, bump=0.02)
    P['wool'] = mat('la_pelego', '#f3ecdc', rough=0.95, var=0.06, bump=0.7, sheen=0.7)
    P['hammock'] = mat('rede_listrada', PAL['pri'], rough=0.9, var=0.0, bump=0.2, stripes=(14.0, '#fff4ec', PAL['pri']), sheen=0.4)
    P['speaker'] = mat('caixa_som', '#24242a', rough=0.6, var=0.02, bump=0.04)
    P['ipe'] = mat('ipe_' + CHAPA, '#e8649a', rough=0.8, var=0.12, bump=0.1, sheen=0.4)
    P['ipe_l'] = mat('ipe_claro_' + CHAPA, '#f59cc0', rough=0.8, var=0.1, bump=0.1, sheen=0.4)
    P['flag_g'] = cor('pri', rough=0.8, sheen=0.4)
    P['flag_y'] = P['white_cloth']
    P['coffee'] = mat('cafe', '#3a2014', rough=0.2, var=0.0, bump=0.0)
    P['_emblem'] = 'spears'
    return P


_lib.palette2 = palette2


# ---------------------------------------------------------------- tecido com a estrela da chapa
def star_shape(R, cx, cz, y):
    """Leque de 10 colunas (as 10 quinas da estrela) no plano XZ do pano: a malha fecha a estrela exata."""
    def fn(u, v, co):
        k = int(round(u * 10))
        a = math.pi / 2 + TAU * k / 10
        r = R * (1.0 if k % 2 == 0 else 0.42) * v
        return Vector((cx + r * math.cos(a), y, cz + r * math.sin(a)))
    return fn


def pano(root, P, tag, par, loc, w, h, wave, m=None, star=0.3, star_z=0.5, rot=(0, 0, 0), nx=8, ny=10, crew=None, both=False):
    """Pano liso (x de 0 a w, z de 0 a -h, de frente para -Y) com a estrela branca; o mesmo `wave` move os dois.
    star = raio da estrela em fracao de min(w, h); star_z = altura do centro (fracao de h, a partir do topo).
    crew: lista de pecas de tecido do boneco (o pose_person anima)."""
    objs = [cloth_grid(root, tag, w, h, nx, ny, [m or P['red_cloth']], thick=0.008)]
    if star:
        R = min(w, h) * star
        objs.append(cloth_grid(root, tag + '_estrela', w, h, 10, 2, [P['white_cloth']], shape=star_shape(R, w / 2, -h * star_z, -0.008),
                               thick=0.004))
        if both:
            objs.append(cloth_grid(root, tag + '_estrelaVerso', w, h, 10, 2, [P['white_cloth']], shape=star_shape(R, w / 2, -h * star_z, 0.008),
                                   thick=0.004))
    for o in objs:
        o.parent = par
        o.location = loc
        o.rotation_euler = rot
        register_cloth(o, wave)
        if crew is not None:
            crew.append(o)
    return objs


# ---------------------------------------------------------------- pecas da sede
def lamp(root, P, tag, par, c, lights):
    """Arandela com globo de luz quente na fachada."""
    x, y, z = c
    objs = [tube(root, tag + '_braco', [(x, y + 0.03, z - 0.03), (x, y - 0.03, z - 0.03), (x, y - 0.05, z)], 0.008, P['iron_d'], segs=6),
            sphere(root, tag + '_globo', 0.036, (x, y - 0.05, z + 0.03), m=P['glow'], seg=14),
            cyl(root, tag + '_chapeu', 0.03, 0.018, (x, y - 0.05, z + 0.068), r2=0.012, m=P['red'], v=12, bev=0.004)]
    for o in objs:
        o.parent = par
    lights.append(('obj', objs[1], '#ffb25a', 14.0, 1))
    return objs


def flag(root, P, tag, par, base, h=0.5, w=0.3):
    """Bandeira da chapa (vermelha com a estrela branca) num mastro, balancando ao vento."""
    x, y, z = base
    objs = [tube(root, tag + '_mastro', [(x, y, z), (x, y, z + h)], 0.012, P['steel'], segs=8),
            sphere(root, tag + '_topo', 0.022, (x, y, z + h + 0.012), m=P['gold'], seg=10)]
    for o in objs:
        o.parent = par
    fh = w * 0.68
    objs += pano(root, P, tag + '_bandeira', par, (x + 0.01, y, z + h - 0.02), w, fh, flag_wave(w, amp=0.05, cycles=1, waves=1.1),
                 m=P['flag_g'], star=0.36, star_z=0.5, nx=14, ny=4, both=True)
    return objs


def corneta(root, P, tag, par, loc, yaw, pitch=-0.18, s=1.0):
    """Corneta de som (alto-falante de poste): trompete branco com aro vermelho e o motor escuro atras;
    aponta (yaw, pitch) no espaco do pai."""
    piv = empty(root, tag + '_piv', loc=loc, parent=par)
    d = Vector((math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), math.sin(pitch)))
    piv.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    prof = [(0.0, 0.022), (0.04, 0.026), (0.08, 0.036), (0.115, 0.056), (0.145, 0.082), (0.16, 0.094)]
    kids(piv, lathe(root, tag + '_cone', [(z * s, r * s, r * s) for z, r in prof], P['horn'], segs=20, lv=1, caps=False, solid=0.008 * s))
    kids(piv, torus(root, tag + '_aro', (0, 0, 0.16 * s), 0.094 * s, 0.011 * s, P['red'], n=24, segs=6))
    kids(piv, cyl(root, tag + '_garganta', 0.07 * s, 0.004, (0, 0, 0.11 * s), m=P['horn_d'], v=20, bev=0.0))
    kids(piv, cyl(root, tag + '_motor', 0.036 * s, 0.07 * s, (0, 0, -0.025 * s), m=P['horn_d'], v=16, bev=0.01 * s))
    return piv


def horn_mast(root, P, tag, par, x, y, z, h, yaws, s=1.0, flag_h=0.0):
    """Poste de ferro no telhado com as cornetas em cima (e a bandeirinha da chapa, se flag_h)."""
    o = tube(root, tag + '_poste', [(x, y, z), (x, y, z + h)], 0.014, P['steel'], segs=8)
    o.parent = par
    o = cyl(root, tag + '_pe', 0.04, 0.02, (x, y, z + 0.01), m=P['steel'], v=12, bev=0.004)
    o.parent = par
    o = box(root, tag + '_suporte', (0.05, 0.05, 0.04), (x, y, z + h - 0.02), m=P['horn_d'], bev=0.008)
    o.parent = par
    for k, yw in enumerate(yaws):
        dx, dy = 0.03 * math.cos(yw), 0.03 * math.sin(yw)
        corneta(root, P, f'{tag}_corneta{k}', par, (x + dx, y + dy, z + h - 0.02), yw, s=s)
    if flag_h:
        flag(root, P, tag + '_bandeira', par, (x, y, z + h), h=flag_h, w=0.2)


def window(root, P, tag, par, x, y, z, w, h, lit=False, side=False, blind=False):
    """Janela na fachada (side=False, plano XZ em y) ou na lateral esquerda (side=True, plano YZ em x)."""
    if side:
        objs = [box(root, tag + '_moldura', (0.03, w + 0.035, h + 0.035), (x - 0.006, y, z), m=P['trim_w'], bev=0.008),
                box(root, tag + '_vidro', (0.03, w, h), (x - 0.012, y, z), m=P['window'] if lit else P['glass_d'], bev=0.006),
                box(root, tag + '_peitoril', (0.05, w + 0.05, 0.02), (x - 0.02, y, z - h / 2 - 0.01), m=P['trim_w'], bev=0.005)]
    else:
        objs = [box(root, tag + '_moldura', (w + 0.035, 0.03, h + 0.035), (x, y - 0.006, z), m=P['trim_w'], bev=0.008),
                box(root, tag + '_vidro', (w, 0.03, h), (x, y - 0.012, z), m=P['window'] if lit else P['glass_d'], bev=0.006),
                box(root, tag + '_peitoril', (w + 0.05, 0.05, 0.02), (x, y - 0.02, z - h / 2 - 0.01), m=P['trim_w'], bev=0.005),
                box(root, tag + '_travessa', (0.012, 0.034, h), (x, y - 0.014, z), m=P['trim_w'], bev=0.003)]
        if blind:   # persiana vermelha meio baixada
            objs.append(box(root, tag + '_persiana', (w - 0.01, 0.034, h * 0.42), (x, y - 0.016, z + h * 0.29), m=P['red'], bev=0.004))
    for o in objs:
        o.parent = par
    return objs


def emblem_disc(root, P, tag, par, x, y, z, r):
    """Circulo vermelho com a estrela branca no muro (o 'brasao' do sindicato, sem letra nenhuma)."""
    d = cyl(root, tag + '_disco', r, 0.02, (x, y - 0.01, z), rot=(math.pi / 2, 0, 0), m=P['red'], v=32, bev=0.006)
    a = torus(root, tag + '_aro', (x, y - 0.012, z), r, 0.008, P['trim_w'], axis='Y', n=32, segs=5)
    e = estrela(root, tag + '_estrela', r * 0.7, 0.012, loc=(x, y - 0.022, z))
    for o in (d, a, e):
        o.parent = par
    return d


def sede(root, P, tag, W, D, floors, fh, cx=0.0, cy=0.14, door='single', lights=None, banners=(), horns=(), horn_h=0.2, horn_s=1.0,
         horn_flag=0.0, flag_on=False, ac=False, emblem=True, faixa=False, wall_m=None, lit=(), blinds=(), banner_m=None, wins=None):
    """Sede do sindicato: predio creme com frisos, platibanda vermelha, janelas, porta com marquise (metade direita),
    faixas penduradas com a estrela e o poste de cornetas no telhado. Devolve o predio, a altura e o at()."""
    lights = lights if lights is not None else []
    bld = empty(root, tag + '_predio', loc=(0, cy, 0), rot=(0, 0, ROT))

    def B(o):
        o.parent = bld
        return o
    bh = 0.04
    H = floors * fh
    zb = Z0 + bh
    zt = zb + H
    yf = -D / 2
    B(box(root, tag + '_base', (W + 0.08, D + 0.08, bh), (cx, 0, Z0 + bh / 2), m=P['concrete'], bev=0.012))
    B(box(root, tag + '_paredes', (W, D, H), (cx, 0, zb + H / 2), m=wall_m or P['wall'], bev=0.03))
    B(box(root, tag + '_rodape', (W + 0.012, D + 0.012, 0.06), (cx, 0, zb + 0.03), m=P['red_d'], bev=0.01))
    for k in range(1, floors):
        B(box(root, f'{tag}_friso{k}', (W + 0.03, D + 0.03, 0.026), (cx, 0, zb + k * fh), m=P['trim_w'], bev=0.008))
    # platibanda vermelha (quatro muretas) com o filete branco, e a laje cinza dentro
    ph_, pt = 0.09, 0.05
    Wp, Dp = W + 0.04, D + 0.04
    for nm, sz, lc in (('F', (Wp, pt, ph_), (cx, -Dp / 2 + pt / 2, zt + ph_ / 2)), ('T', (Wp, pt, ph_), (cx, Dp / 2 - pt / 2, zt + ph_ / 2)),
                       ('E', (pt, Dp, ph_), (cx - Wp / 2 + pt / 2, 0, zt + ph_ / 2)), ('D', (pt, Dp, ph_), (cx + Wp / 2 - pt / 2, 0, zt + ph_ / 2))):
        B(box(root, f'{tag}_platibanda{nm}', sz, lc, m=P['red'], bev=0.012))
    B(box(root, tag + '_filete', (Wp + 0.006, 0.012, 0.018), (cx, -Dp / 2 - 0.004, zt + 0.004), m=P['trim_w'], bev=0.004))
    B(box(root, tag + '_fileteE', (0.012, Dp + 0.006, 0.018), (cx - Wp / 2 - 0.004, 0, zt + 0.004), m=P['trim_w'], bev=0.004))
    B(box(root, tag + '_laje', (W - 0.04, D - 0.04, 0.03), (cx, 0, zt + 0.02), m=P['roof'], bev=0.006))
    # porta na metade direita
    dx = cx + W * 0.25
    door_h = min(fh * 0.8, 0.34)
    dw = 0.24 if door == 'double' else 0.17
    for sx in (-1, 1):
        B(box(root, f'{tag}_batente{sx}', (0.03, 0.05, door_h + 0.02), (dx + sx * (dw / 2 + 0.015), yf - 0.01, zb + (door_h + 0.02) / 2), m=P['trim_w'], bev=0.008))
    B(box(root, tag + '_verga', (dw + 0.06, 0.05, 0.03), (dx, yf - 0.01, zb + door_h + 0.025), m=P['trim_w'], bev=0.008))
    if door == 'double':
        for i, sx in enumerate((-1, 1)):
            lx = dx + sx * dw / 4
            B(box(root, f'{tag}_folha{i}', (dw / 2 - 0.008, 0.03, door_h), (lx, yf + 0.004, zb + door_h / 2), m=P['door_red'], bev=0.008))
            B(box(root, f'{tag}_vidroPorta{i}', (dw / 2 - 0.05, 0.012, door_h * 0.55), (lx, yf - 0.014, zb + door_h * 0.6), m=P['window'], bev=0.004))
            B(tube(root, f'{tag}_macaneta{i}', [(dx - sx * 0.022, yf - 0.02, zb + door_h * 0.36), (dx - sx * 0.022, yf - 0.02, zb + door_h * 0.52)], 0.008, P['gold'], segs=6))
    else:
        B(box(root, tag + '_folha', (dw, 0.03, door_h), (dx, yf + 0.004, zb + door_h / 2), m=P['door_red'], bev=0.008))
        B(box(root, tag + '_vidroPorta', (dw * 0.56, 0.012, door_h * 0.34), (dx, yf - 0.014, zb + door_h * 0.68), m=P['window'], bev=0.004))
        B(sphere(root, tag + '_macaneta', 0.013, (dx + dw * 0.32, yf - 0.02, zb + door_h * 0.45), m=P['gold'], seg=8))
    # marquise branca com a borda vermelha
    B(box(root, tag + '_marquise', (dw + 0.18, 0.2, 0.03), (dx, yf - 0.085, zb + door_h + 0.06), m=P['trim_w'], bev=0.012))
    B(box(root, tag + '_marquiseBorda', (dw + 0.186, 0.012, 0.034), (dx, yf - 0.186, zb + door_h + 0.06), m=P['red'], bev=0.005))
    lamp(root, P, tag + '_luz', bld, (dx + dw / 2 + 0.07, yf, zb + door_h - 0.05), lights)
    # janelas da frente: terreo a esquerda da porta, andares de cima em fila
    ww = 0.15
    xs_up = [cx - W / 2 + 0.14 + k * (W - 0.28) / max(1, int((W - 0.28) / 0.24)) for k in range(int((W - 0.28) / 0.24) + 1)]
    for f in range(floors):
        zc = zb + fh * f + fh * 0.55
        hh = min(0.17, fh * 0.48)
        xs = [x for x in xs_up if (f > 0 or x < dx - dw / 2 - 0.13)] if wins is None else [cx + x for x in wins[f]]
        if emblem and floors > 1 and f == 1:
            xs = [x for x in xs if abs(x - dx) > 0.17]
        for j, x in enumerate(xs):
            window(root, P, f'{tag}_janela{f}_{j}', bld, x, yf, zc, ww, hh, lit=(f, j) in lit, blind=(f, j) in blinds)
        window(root, P, f'{tag}_janelaLado{f}', bld, cx - W / 2, 0.02, zc, 0.16, hh, lit=False, side=True)
    # faixas (estandartes) vermelhas com a estrela, penduradas da platibanda
    for k, (bx, bw, bhh) in enumerate(banners):
        z_top = zt - 0.005
        rod = tube(root, f'{tag}_faixaVara{k}', [(bx - bw / 2 - 0.02, yf - 0.056, z_top), (bx + bw / 2 + 0.02, yf - 0.056, z_top)], 0.009, P['horn_d'], segs=6)
        rod.parent = bld
        for sx in (-1, 1):
            o = box(root, f'{tag}_faixaMao{k}{sx}', (0.012, 0.06, 0.012), (bx + sx * (bw / 2 + 0.01), yf - 0.028, z_top), m=P['horn_d'], bev=0.003)
            o.parent = bld
        pano(root, P, f'{tag}_faixa{k}', bld, (bx - bw / 2, yf - 0.058, z_top - 0.01), bw, bhh, hang_wave(bhh, amp=0.012, axis='Y', cycles=1, waves=0.5),
             m=banner_m, star=0.36, star_z=0.3)
    if emblem and floors > 1:
        emblem_disc(root, P, tag + '_brasao', bld, dx, yf, zb + fh * 1.5, min(0.075, fh * 0.26))
    elif emblem:
        o = estrela(root, tag + '_estrelaPlatibanda', 0.038, 0.012, loc=(dx, yf - 0.042, zt + 0.045))
        o.parent = bld
    if faixa:
        # faixa horizontal amarrada de ponta a ponta no friso do primeiro andar (pano liso com tres estrelas)
        fw, fhh = W * 0.62, 0.1
        x0 = cx - W / 2 + 0.06
        zf = zb + fh - 0.02
        wave = lambda co, ph, fw=fw: Vector((co.x, co.y - 0.012 * math.sin(math.pi * co.x / fw) * (1 + 0.5 * math.sin(TAU * ph)), co.z))
        cl = cloth_grid(root, tag + '_faixaH', fw, fhh, 16, 3, [P['red_cloth']], thick=0.008)
        cl.parent = bld
        cl.location = (x0, yf - 0.056, zf)
        register_cloth(cl, wave)
        for k in range(3):
            st = cloth_grid(root, f'{tag}_faixaHestrela{k}', fw, fhh, 10, 2, [P['white_cloth']],
                            shape=star_shape(fhh * 0.36, fw * (k + 1) / 4, -fhh / 2, -0.008), thick=0.004)
            st.parent = bld
            st.location = (x0, yf - 0.056, zf)
            register_cloth(st, wave)
        for sx, xx in ((-1, x0), (1, x0 + fw)):
            o = tube(root, f'{tag}_faixaCorda{sx}', [(xx, yf - 0.056, zf), (xx - sx * 0.02, yf - 0.005, zf + 0.01)], 0.005, P['rope'], segs=4)
            o.parent = bld
    if horns:
        horn_mast(root, P, tag + '_som', bld, cx - W / 2 + 0.2, 0.06, zt + 0.03, horn_h, horns, s=horn_s, flag_h=horn_flag)
    if flag_on:
        flag(root, P, tag + '_bandeira', bld, (cx + W / 2 - 0.14, 0.08, zt + 0.03), h=0.5, w=0.3)
    if ac:
        zc = zb + fh * (floors - 1) + fh * 0.3
        o = box(root, tag + '_arCond', (0.1, 0.24, 0.14), (cx - W / 2 - 0.05, -D / 2 + 0.17, zc), m=mat('ar_cond', '#ece4d2', rough=0.6, var=0.02, bump=0.04), bev=0.016)
        o.parent = bld
        for k in range(4):
            o = box(root, f'{tag}_arGrade{k}', (0.004, 0.18, 0.01), (cx - W / 2 - 0.101, -D / 2 + 0.17, zc - 0.042 + 0.027 * k), m=P['iron'], bev=0.0)
            o.parent = bld
    bpy.context.view_layer.update()

    def at(x, y, z=Z0):
        """Ponto do predio (antes do giro) -> coordenada da raiz."""
        c, sn = math.cos(ROT), math.sin(ROT)
        return (x * c - y * sn, cy + x * sn + y * c, z)
    return {'bld': bld, 'H': H, 'zt': zt, 'zb': zb, 'W': W, 'D': D, 'at': at, 'door': at(dx, yf - 0.12), 'dx': dx, 'lights': lights}


def ipe(root, P, tag, loc, s=1.0, seed=5):
    """Ipe rosa florido de Brasilia num vaso de concreto (a mancha de cor do lote)."""
    rr = random.Random(seed)
    x, y, z = loc
    box(root, tag + '_vaso', (0.2 * s, 0.2 * s, 0.13 * s), (x, y, z + 0.065 * s), m=P['concrete'], bev=0.02)
    box(root, tag + '_terra', (0.17 * s, 0.17 * s, 0.02), (x, y, z + 0.125 * s), m=mat('terra_vaso', '#8a4a2a', rough=0.95, var=0.05, bump=0.3), bev=0.005)
    z += 0.13 * s
    tube(root, tag + '_tronco', [(x, y, z), (x + 0.03 * s, y, z + 0.22 * s), (x - 0.02 * s, y, z + 0.4 * s)], 0.026 * s, P['wood'], segs=8,
         rfun=lambda t: s * (0.028 - 0.012 * t))
    for k in range(3):
        a = TAU * k / 3 + 0.4
        tube(root, f'{tag}_galho{k}', [(x - 0.02 * s, y, z + 0.38 * s), (x + 0.14 * s * math.cos(a), y + 0.1 * s * math.sin(a), z + 0.5 * s)], 0.01 * s, P['wood'], segs=6)
    for k in range(9):
        a = TAU * k / 9 + rr.uniform(-0.3, 0.3)
        rad = rr.uniform(0.06, 0.15) * s
        sphere(root, f'{tag}_flor{k}', rr.uniform(0.07, 0.1) * s, (x + rad * math.cos(a), y + rad * math.sin(a) * 0.8, z + (0.5 + rr.uniform(-0.05, 0.08)) * s),
               scale=(1, 1, 0.8), m=P['ipe'] if k % 3 else P['ipe_l'], seg=14)
    sphere(root, tag + '_florTopo', 0.1 * s, (x, y, z + 0.6 * s), scale=(1, 1, 0.8), m=P['ipe_l'], seg=14)


def resolve_lights(lights):
    """Luzes registradas como ('obj', objeto, cor, watts, halo) viram (posicao na raiz, cor, watts, halo)."""
    bpy.context.view_layer.update()
    out = []
    for L_ in lights:
        if L_[0] == 'obj':
            out.append((tuple(L_[1].matrix_world.translation),) + tuple(L_[2:]))
        else:
            out.append(L_)
    return out


# ---------------------------------------------------------------- nivel 1: a sede de um andar com a corneta no telhado
def build_qt1(P, root):
    plot(root, P, 'qt1')
    lights = []
    g = sede(root, P, 'qt1', W=0.92, D=0.54, floors=1, fh=0.5, lights=lights, banners=[(-0.06, 0.2, 0.36)],
             horns=[math.radians(-60)], horn_h=0.24, horn_flag=0.14, lit=[(0, 0)], wins=[[-0.3]])
    at = g['at']
    return {'slots': [at(0.6, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- nivel 2: dois andares, duas faixas e duas cornetas
def build_qt2(P, root):
    plot(root, P, 'qt2')
    lights = []
    g = sede(root, P, 'qt2', W=1.0, D=0.56, floors=2, fh=0.34, lights=lights, banners=[(-0.12, 0.2, 0.46)],
             horns=[math.radians(-60), math.radians(150)], horn_h=0.22, horn_flag=0.0, lit=[(0, 0), (1, 2)], blinds=[(1, 0)])
    at = g['at']
    ipe(root, P, 'qt2_ipe', (-0.68, 0.18, 0.07), s=0.72, seed=3)
    return {'slots': [at(-0.64, -0.46), at(0.64, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- nivel 3: tres andares, faixa horizontal, bandeira e o ipe
def build_qt3(P, root):
    plot(root, P, 'qt3')
    lights = []
    g = sede(root, P, 'qt3', W=1.08, D=0.58, floors=3, fh=0.3, lights=lights, banners=[(-0.34, 0.19, 0.46), (0.0, 0.19, 0.46)],
             horns=[math.radians(-60), math.radians(150), math.radians(60)], horn_h=0.24, flag_on=True, ac=True, faixa=True,
             lit=[(0, 0), (1, 1), (2, 3)], blinds=[(2, 0)])
    at = g['at']
    ipe(root, P, 'qt3_ipe', (-0.7, 0.2, 0.07), s=0.9, seed=8)
    return {'slots': [at(-0.67, -0.46), at(0.67, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- Diretoria do Sindicato: palanque, caixas de som e a tenda listrada
def tenda(root, P, tag, par, c, s=0.34, h_post=0.46, h_roof=0.17, z0=Z0, lights=None):
    """Tenda do sindicato (gazebo): quatro pes de aco, teto em piramide de gomos vermelhos e brancos e a sanefa
    de abas alternadas."""
    x, y = c
    for sx in (-1, 1):
        for sy in (-1, 1):
            o = tube(root, f'{tag}_pe{sx}{sy}', [(x + sx * s / 2, y + sy * s / 2, z0), (x + sx * s / 2, y + sy * s / 2, z0 + h_post + 0.01)], 0.012, P['steel'], segs=8)
            o.parent = par
            o = cyl(root, f'{tag}_sapata{sx}{sy}', 0.026, 0.014, (x + sx * s / 2, y + sy * s / 2, z0 + 0.007), m=P['steel'], v=10, bev=0.003)
            o.parent = par
    ze = z0 + h_post
    e = s / 2 + 0.035
    n = 3
    bm = bmesh.new()
    apex = bm.verts.new((x, y, ze + h_roof))
    corners = [(x + e, y - e), (x + e, y + e), (x - e, y + e), (x - e, y - e)]
    ring = []
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        for j in range(n):
            t = j / n
            ring.append(bm.verts.new((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, ze)))
    for i in range(len(ring)):
        f = bm.faces.new((ring[i], ring[(i + 1) % len(ring)], apex))
        f.material_index = i % 2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    roof = bm_to_obj(bm, tag + '_teto', root, [P['red_cloth'], P['white_cloth']], angle=20)
    sm = roof.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.012
    roof.parent = par
    o = sphere(root, tag + '_ponta', 0.022, (x, y, ze + h_roof + 0.01), m=P['red'], seg=10)
    o.parent = par
    # sanefa: abas penduradas na beira do teto, alternando as cores
    k = 0
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        m_ = int(L / 0.06)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for j in range(m_):
            t = (j + 0.5) / m_
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            o = box(root, f'{tag}_aba{k}', (L / m_ - 0.004, 0.008, 0.05), (px, py, ze - 0.022), rot=(0, 0, ang), m=P['white_cloth'] if k % 2 else P['red_cloth'], bev=0.003)
            o.parent = par
            k += 1
    if lights is not None:
        o = tube(root, tag + '_fioLampada', [(x, y - 0.05, ze + 0.02), (x, y - 0.05, ze - 0.06)], 0.003, P['iron_d'], segs=4)
        o.parent = par
        gl = sphere(root, tag + '_lampada', 0.026, (x, y - 0.05, ze - 0.085), m=P['glow'], seg=12)
        gl.parent = par
        lights.append(('obj', gl, '#ffb25a', 10.0, 1))
    return roof


def speaker(root, P, tag, par, loc, s=1.0, rot=0.0):
    """Caixa de som preta com dois alto-falantes (de frente para -Y antes do giro)."""
    x, y, z = loc
    e = empty(root, tag + '_piv', loc=(x, y, z), parent=par, rot=(0, 0, rot))
    kids(e, box(root, tag + '_caixa', (0.11 * s, 0.09 * s, 0.17 * s), (0, 0, 0.085 * s), m=P['speaker'], bev=0.012 * s))
    for k, (zz, r) in enumerate(((0.12, 0.03), (0.055, 0.038))):
        kids(e, cyl(root, f'{tag}_cone{k}', r * s, 0.012, (0, -0.046 * s, zz * s), rot=(math.pi / 2, 0, 0), m=P['horn_d'], v=18, bev=0.003))
        kids(e, cyl(root, f'{tag}_miolo{k}', r * 0.35 * s, 0.014, (0, -0.05 * s, zz * s), rot=(math.pi / 2, 0, 0), m=P['steel'], v=12, bev=0.002))
    return e


def build_qtL(P, root):
    plot(root, P, 'qtL')
    lights = []
    g = sede(root, P, 'qtL', W=0.86, D=0.58, floors=3, fh=0.31, cx=0.13, door='double', lights=lights,
             banners=[(-0.1, 0.18, 0.46), (0.14, 0.18, 0.46)], horns=[math.radians(-60), math.radians(150), math.radians(60)], horn_h=0.2,
             flag_on=True, lit=[(0, 0), (1, 0), (1, 2), (2, 1)], emblem=True)
    at = g['at']
    bld = g['bld']
    # tenda listrada do sindicato do lado esquerdo e o palanque na frente dela
    tenda(root, P, 'qtL_tenda', bld, (-0.54, -0.02), s=0.34, h_post=0.46, h_roof=0.17, lights=lights)
    sx0, sy0, sw, sd, sh = -0.5, -0.5, 0.42, 0.28, 0.08
    o = box(root, 'qtL_palanque', (sw, sd, sh), (sx0, sy0, Z0 + sh / 2), m=P['red_d'], bev=0.01)
    o.parent = bld
    o = box(root, 'qtL_palanqueTampo', (sw + 0.02, sd + 0.02, 0.022), (sx0, sy0, Z0 + sh + 0.006), m=P['wood_l'], bev=0.006)
    o.parent = bld
    for k in range(3):
        o = estrela(root, f'qtL_palanqueEstrela{k}', 0.022, 0.008, loc=(sx0 - sw / 2 + sw * (k + 0.5) / 3, sy0 - sd / 2 - 0.005, Z0 + sh * 0.5))
        o.parent = bld
    o = box(root, 'qtL_degrau', (0.12, 0.07, sh * 0.5), (sx0 + sw / 2 - 0.08, sy0 - sd / 2 - 0.035, Z0 + sh * 0.25), m=P['wood_l'], bev=0.006)
    o.parent = bld
    speaker(root, P, 'qtL_somE', bld, (sx0 - sw / 2 + 0.02, sy0 + sd / 2 - 0.01, Z0 + sh + 0.017), s=1.0, rot=math.radians(-20))
    speaker(root, P, 'qtL_somD', bld, (sx0 + sw / 2 + 0.07, sy0 + 0.02, Z0), s=1.15, rot=math.radians(15))
    # pedestal do microfone na beira do palanque
    o = tube(root, 'qtL_pedestal', [(sx0 + 0.1, sy0 - 0.06, Z0 + sh + 0.017), (sx0 + 0.1, sy0 - 0.06, Z0 + sh + 0.24), (sx0 + 0.07, sy0 - 0.08, Z0 + sh + 0.29)], 0.007,
             P['iron_d'], segs=6)
    o.parent = bld
    o = sphere(root, 'qtL_micro', 0.018, (sx0 + 0.065, sy0 - 0.083, Z0 + sh + 0.3), m=P['horn_d'], seg=10)
    o.parent = bld
    o = cyl(root, 'qtL_pedestalPe', 0.035, 0.01, (sx0 + 0.1, sy0 - 0.06, Z0 + sh + 0.022), m=P['iron_d'], v=12, bev=0.003)
    o.parent = bld
    return {'slots': [at(sx0 - 0.08, sy0 + 0.02, Z0 + sh + 0.017), at(0.68, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- Pelegos: rede com o dorminhoco, garrafa termica e a laje de descanso
def plastic_chair(root, P, tag, par, loc, rot=0.0, s=1.0, m=None):
    """Cadeira de plastico branca (monobloco), de frente para -Y antes do giro."""
    m = m or P['plastic']
    x, y, z = loc
    e = empty(root, tag + '_piv', loc=(x, y, z), parent=par, rot=(0, 0, rot))
    kids(e, box(root, tag + '_assento', (0.11 * s, 0.1 * s, 0.016 * s), (0, 0, 0.075 * s), m=m, bev=0.006 * s))
    kids(e, box(root, tag + '_encosto', (0.11 * s, 0.014 * s, 0.09 * s), (0, 0.05 * s, 0.13 * s), rot=(-0.18, 0, 0), m=m, bev=0.006 * s))
    for sx in (-1, 1):
        kids(e, box(root, f'{tag}_braco{sx}', (0.012 * s, 0.09 * s, 0.012 * s), (sx * 0.054 * s, 0.0, 0.11 * s), m=m, bev=0.004 * s))
        for sy in (-1, 1):
            kids(e, tube(root, f'{tag}_perna{sx}{sy}', [(sx * 0.048 * s, sy * 0.042 * s, 0.072 * s), (sx * 0.06 * s, sy * 0.055 * s, 0.0)], 0.008 * s, m, segs=6))
    return e


def thermos(root, P, tag, par, loc, s=1.0):
    """Garrafa termica de cafe (vermelha com o tampo branco de bomba e a alca)."""
    x, y, z = loc
    objs = [cyl(root, tag + '_corpo', 0.032 * s, 0.11 * s, (x, y, z + 0.055 * s), m=P['red'], v=18, bev=0.008 * s),
            cyl(root, tag + '_tampo', 0.03 * s, 0.03 * s, (x, y, z + 0.125 * s), r2=0.024 * s, m=P['plastic'], v=18, bev=0.006 * s),
            cyl(root, tag + '_bomba', 0.014 * s, 0.014 * s, (x, y, z + 0.146 * s), m=P['plastic'], v=12, bev=0.003),
            box(root, tag + '_bico', (0.03 * s, 0.012 * s, 0.01 * s), (x - 0.028 * s, y, z + 0.13 * s), m=P['plastic'], bev=0.003),
            tube(root, tag + '_alca', [(x + 0.03 * s, y, z + 0.1 * s), (x + 0.05 * s, y, z + 0.09 * s), (x + 0.05 * s, y, z + 0.04 * s), (x + 0.03 * s, y, z + 0.03 * s)],
                 0.007 * s, P['plastic'], segs=6)]
    for o in objs:
        o.parent = par
    return objs


def cups(root, P, tag, par, loc, n=3, seed=2):
    rr = random.Random(seed)
    x, y, z = loc
    for k in range(n):
        a = TAU * k / n + rr.uniform(-0.3, 0.3)
        px, py = x + 0.04 * math.cos(a), y + 0.04 * math.sin(a)
        o = cyl(root, f'{tag}_copo{k}', 0.011, 0.024, (px, py, z + 0.012), r2=0.014, m=P['plastic'], v=12, bev=0.002)
        o.parent = par
        o = cyl(root, f'{tag}_cafe{k}', 0.012, 0.003, (px, py, z + 0.021), m=P['coffee'], v=12, bev=0.0)
        o.parent = par


def wool_tuft(root, P, tag, par, c, rx, ry, rz, n=12, seed=4, r=0.03):
    """Pelego de carneiro: tufos de la (bolotas brancas fofas)."""
    rr = random.Random(seed)
    x, y, z = c
    out = []
    for k in range(n):
        a = rr.uniform(0, TAU)
        d = rr.uniform(0, 1) ** 0.5
        o = sphere(root, f'{tag}_tufo{k}', r * rr.uniform(0.8, 1.2), (x + rx * d * math.cos(a), y + ry * d * math.sin(a), z + rz * rr.uniform(-1, 1)),
                   scale=(1, 1, 0.7), m=P['wool'], seg=10)
        o.parent = par
        out.append(o)
    return out


def hammock(root, P, tag, x0, x1, y, z_hook, sag=0.22, w=0.2, posts=True, sleeper=True):
    """Rede listrada entre dois postes (balanca no loop), com um pelego dormindo dentro: bone na cara e o pelego de
    carneiro na barriga. Coordenadas da raiz (o predio e outra coisa)."""
    L = x1 - x0
    if posts:
        for k, xx in enumerate((x0, x1)):
            tube(root, f'{tag}_poste{k}', [(xx, y, Z0), (xx, y, z_hook + 0.08)], 0.02, P['wood'], segs=8)
            sphere(root, f'{tag}_posteTopo{k}', 0.024, (xx, y, z_hook + 0.085), m=P['wood'], seg=8)
            cyl(root, f'{tag}_posteBase{k}', 0.04, 0.03, (xx, y, Z0 + 0.015), m=P['concrete'], v=12, bev=0.006)
    piv = empty(root, tag + '_balanco', loc=((x0 + x1) / 2, y, z_hook))
    bm = bmesh.new()
    nu, nv = 16, 6
    inner = 0.1   # o pano so comeca depois das cordas
    rows = []
    for j in range(nv + 1):
        v = j / nv
        row = []
        for i in range(nu + 1):
            u = i / nu
            xx = -L / 2 + L * (inner + (1 - 2 * inner) * u)
            uu = (xx + L / 2) / L
            zz = -sag * math.sin(math.pi * uu) ** 0.9 - 0.035 * math.sin(math.pi * v) * math.sin(math.pi * u) * 1.2
            yy = (v - 0.5) * w * (0.35 + 0.65 * math.sin(math.pi * u) ** 0.5)
            row.append(bm.verts.new((xx, yy, zz + 0.03 * (1 - math.sin(math.pi * v)) * math.sin(math.pi * u))))
        rows.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    cloth = bm_to_obj(bm, tag + '_pano', root, [P['hammock']], angle=80)
    sm = cloth.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.01
    cloth.parent = piv
    # cordas das pontas ate o gancho
    for sx in (-1, 1):
        xe = sx * L / 2
        xi = sx * L * (0.5 - inner)
        zi = -sag * math.sin(math.pi * inner) ** 0.9
        for k, yy in enumerate((-w * 0.17, 0.0, w * 0.17)):
            o = tube(root, f'{tag}_corda{sx}{k}', [(xe, 0, 0), (xi, yy, zi)], 0.004, P['rope'], segs=4)
            o.parent = piv
    if sleeper:
        nap = empty(root, tag + '_dorminhocoRaiz', parent=piv)
        nap['set'] = root['set']
        pr = build_person(P, nap, tag + '_dorminhoco', militant_sp(P, big=0.86))
        pose_person(pr, P, nap, dict(lean=-math.pi / 2 + 0.22, face=0.0, offset=(0.3, 0.0, -sag + 0.065),
                                    hand_L=(0.11, 0.05, 0.31), hand_R=(0.11, -0.05, 0.33), head_pitch=-0.2))
        body = pr['body']
        cap_brim(root, pr, tag + '_dorminhoco', star=False)
        for s_, yy in enumerate((-0.024, 0.024)):
            o = blob(root, f'{tag}_palpebra{s_}', 0.0125, HC + Vector((0.061, yy, 0.014)), (0.7, 1.1, 0.9), P['skin'])
            o.parent = pr['head']
        # o pelego de carneiro (cobertor de la) em cima da barriga
        wool_tuft(root, P, tag + '_pelego', body, (0.1, 0.0, 0.3), 0.03, 0.09, 0.07, n=16, seed=7, r=0.036)
    register_anim(piv, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.16 * math.sin(TAU * ph), 4, 'X')))
    return piv


def umbrella(root, P, tag, par, loc, r=0.2, h=0.3):
    """Guarda-sol de gomos vermelhos e brancos num pe de aluminio."""
    x, y, z = loc
    o = tube(root, tag + '_haste', [(x, y, z), (x, y, z + h + 0.03)], 0.008, P['steel'], segs=6)
    o.parent = par
    bm = bmesh.new()
    n = 10
    apex = bm.verts.new((x, y, z + h + 0.05))
    ring = [bm.verts.new((x + r * math.cos(TAU * i / n), y + r * math.sin(TAU * i / n), z + h - 0.03)) for i in range(n)]
    for i in range(n):
        f = bm.faces.new((ring[i], ring[(i + 1) % n], apex))
        f.material_index = i % 2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = bm_to_obj(bm, tag + '_lona', root, [P['red_cloth'], P['white_cloth']], angle=20)
    sm = o.modifiers.new('Espessura', 'SOLIDIFY')
    sm.thickness = 0.01
    o.parent = par
    o = sphere(root, tag + '_ponta', 0.014, (x, y, z + h + 0.06), m=P['red'], seg=8)
    o.parent = par
    o = cyl(root, tag + '_base', 0.05, 0.02, (x, y, z + 0.01), m=P['horn_d'], v=14, bev=0.004)
    o.parent = par


def build_qtM(P, root):
    plot(root, P, 'qtM')
    lights = []
    g = sede(root, P, 'qtM', W=0.86, D=0.56, floors=2, fh=0.34, cx=0.12, lights=lights, banners=[(0.0, 0.14, 0.26)],
             horns=(), wall_m=P['wall_m'], lit=[(0, 0)], blinds=[(1, 0), (1, 1), (1, 2)], banner_m=P['faded'], emblem=True)
    at = g['at']
    bld = g['bld']
    zt = g['zt']
    # laje de descanso: guarda-sol, mesinha com a garrafa termica e os copinhos, cadeiras de plastico
    zr = zt + 0.035
    umbrella(root, P, 'qtM_guardaSol', bld, (-0.08, 0.06, zr), r=0.22, h=0.3)
    o = cyl(root, 'qtM_mesaTampo', 0.08, 0.014, (0.16, 0.04, zr + 0.11), m=P['plastic'], v=20, bev=0.005)
    o.parent = bld
    for k in range(3):
        a = TAU * k / 3 + 0.4
        o = tube(root, f'qtM_mesaPe{k}', [(0.16 + 0.05 * math.cos(a), 0.04 + 0.05 * math.sin(a), zr + 0.105), (0.16 + 0.07 * math.cos(a), 0.04 + 0.07 * math.sin(a), zr)],
                 0.008, P['plastic'], segs=6)
        o.parent = bld
    thermos(root, P, 'qtM_garrafa', bld, (0.14, 0.06, zr + 0.117), s=0.85)
    cups(root, P, 'qtM_copos', bld, (0.2, 0.02, zr + 0.117), n=2)
    plastic_chair(root, P, 'qtM_cadeira0', bld, (0.36, 0.0, zr), rot=math.radians(-110), s=1.15)
    plastic_chair(root, P, 'qtM_cadeira1', bld, (0.2, 0.2, zr), rot=math.radians(170), s=1.15)
    # a rede listrada com o pelego dormindo, na frente do lado esquerdo, e a garrafa termica no banquinho
    hammock(root, P, 'qtM_rede', -0.72, -0.18, -0.5, Z0 + 0.42, sag=0.22, w=0.2)
    # mesinha de plastico do lado da rede: a garrafa termica e os copinhos de cafe
    mx, my, mz = -0.44, -0.7, Z0 + 0.1
    cyl(root, 'qtM_mesinha', 0.07, 0.012, (mx, my, mz), m=P['plastic'], v=20, bev=0.004)
    for k in range(3):
        a = TAU * k / 3 + 0.3
        tube(root, f'qtM_mesinhaPe{k}', [(mx + 0.045 * math.cos(a), my + 0.045 * math.sin(a), mz - 0.004), (mx + 0.06 * math.cos(a), my + 0.06 * math.sin(a), Z0)],
             0.007, P['plastic'], segs=6)
    thermos(root, P, 'qtM_garrafa2', root, (mx - 0.015, my + 0.01, mz + 0.006), s=0.95)
    cups(root, P, 'qtM_copos2', root, (mx + 0.03, my - 0.01, mz + 0.006), n=2, seed=5)
    return {'slots': [at(0.06, -0.5), at(0.64, -0.46)], 'lights': resolve_lights(lights), 'points': {'door': g['door']}}


# ---------------------------------------------------------------- a tripulacao: militantes do sindicato
def militant_sp(P, cap=True, hair_m=None, beard=None, vest=None, scarf=None, boots=None, big=1.0):
    """Figurino do militante: camiseta vermelha, calca jeans escura, tenis e bone vermelho."""
    sp = dict(tunic=cor('camisa'), skirt_m=cor('calca'), pants=cor('calca'), sleeve=cor('camisa'), bracer=P['skin'], bare_hands=True,
              glove=P['skin'], boot_m=boots or mat('tenis_branco', '#f1efe8', rough=0.6, var=0.02, bump=0.04), boot_cuff=cor('calca'), belt=None,
              head='cap' if cap else 'hair', head_m=cor('bone'), hair_m=hair_m or mat('cabelo_escuro', '#2e1d12', rough=0.7, var=0.03, bump=0.25))
    if beard:
        sp['beard'] = beard
        sp['brow_m'] = beard
    if vest:
        sp['vest'] = vest
    if scarf:
        sp['scarf'] = scarf
    if big != 1.0:
        sp['big'] = big
    return sp


def cap_brim(root, pr, tag, star=True):
    """Aba do bone (o 'cap' do lib e so a copa) e a estrelinha branca na frente da copa."""
    m = cor('bone')
    aba = cyl(root, tag + '_boneAba', 0.05, 0.008, (0, 0, 0), m=m, v=18, bev=0.003)
    aba.parent = pr['head']
    aba.location = HC + Vector((0.062, 0, 0.036))
    aba.scale = (1.3, 0.95, 1.0)
    aba.rotation_euler = (0, -0.14, 0)
    out = [aba]
    if star:
        e = estrela(root, tag + '_boneEstrela', 0.016, 0.006, rot=(0, -0.55, math.pi / 2))
        e.parent = pr['head']
        e.location = HC + Vector((0.066, 0, 0.068))
        out.append(e)
    return out


def whistle(root, pr, tag):
    """Apito amarelo na boca, com o cordao branco caindo ate o peito."""
    ym = mat('apito', '#f5c518', rough=0.3, var=0.0, bump=0.0)
    h = pr['head']
    o1 = cyl(root, tag + '_apitoBocal', 0.009, 0.04, (0, 0, 0), rot=(0, math.pi / 2, 0), m=ym, v=10, bev=0.002)
    o1.parent = h
    o1.location = HC + Vector((0.08, -0.004, -0.03))
    o2 = sphere(root, tag + '_apitoBola', 0.017, HC + Vector((0.104, -0.004, -0.032)), scale=(1, 0.9, 0.9), m=ym, seg=10)
    o2.parent = h
    o3 = tube(root, tag + '_apitoCordao', [(0.05, -0.05, 0.47), (0.098, -0.03, 0.42), (0.11, -0.004, 0.47), (0.098, 0.03, 0.42), (0.05, 0.05, 0.47)],
              0.0035, mat('cordao_branco', '#f4f2ec', rough=0.8, var=0, bump=0), segs=4)
    o3.parent = pr['body']
    return [o1, o2, o3]


def hand_flag(root, P, pr, tag):
    """Bandeirinha da chapa num cabo de madeira (na mao; o pano entra nos tecidos do boneco)."""
    stick = tube(root, tag + '_bandeiraCabo', [(0, 0, -0.04), (0, 0, 0.26)], 0.007, P['wood_l'], segs=6)
    tip = sphere(root, tag + '_bandeiraPonta', 0.011, (0, 0, 0.265), m=P['gold'], seg=8)
    piv = empty(root, tag + '_bandeiraPiv', loc=(0, 0, 0.255))
    w, h = 0.15, 0.1
    pano(root, P, tag + '_bandeiraPano', piv, (0.006, 0, 0), w, h, flag_wave(w, amp=0.03, cycles=1, waves=1.0), m=P['flag_g'], star=0.36, star_z=0.5,
         nx=10, ny=3, crew=pr['cloth'], both=True)
    piv.rotation_euler = (0, 0, math.pi / 2)
    hold(pr, 'R', stick, tip, piv)


def megaphone(root, P, tag):
    """Megafone de mao: corneta branca com aro vermelho ao longo do Z local, cabo com gatilho embaixo (empunhadura
    em z = 0; o X local do punho fica para cima, entao a corneta vai acima da mao)."""
    up = 0.045
    objs = [lathe(root, tag + '_megaCone', [(-0.03, 0.02, 0.02), (0.02, 0.026, 0.026), (0.07, 0.042, 0.042), (0.11, 0.064, 0.064), (0.125, 0.07, 0.07)],
                  P['horn'], segs=18, lv=1, caps=False, solid=0.006),
            torus(root, tag + '_megaAro', (0, 0, 0.125), 0.07, 0.009, P['red'], n=20, segs=5),
            cyl(root, tag + '_megaFundo', 0.05, 0.004, (0, 0, 0.08), m=P['horn_d'], v=16, bev=0.0),
            cyl(root, tag + '_megaBocal', 0.024, 0.03, (0, 0, -0.035), m=P['horn_d'], v=12, bev=0.006)]
    for o in objs:
        o.location.x += up
    objs.append(box(root, tag + '_megaCabo', (0.05, 0.022, 0.026), (0.018, 0, 0.0), m=P['horn_d'], bev=0.008))
    objs.append(estrela(root, tag + '_megaEstrela', 0.014, 0.004, loc=(up, -0.034, 0.07), rot=(0, 0, 0), m=P['red']))
    return objs


def leaflets(root, P, tag):
    """Maco de panfletos (papeis em branco, sem nada escrito), empunhado pela borda de baixo."""
    pm = mat('panfleto', '#fbf6ea', rough=0.85, var=0.0, bump=0.0)
    pr_ = mat('panfleto_vermelho', '#f29a92', rough=0.85, var=0.0, bump=0.0)
    return [box(root, tag + '_panfleto0', (0.008, 0.07, 0.1), (0, 0, 0.045), m=pm, bev=0.002),
            box(root, tag + '_panfleto1', (0.008, 0.07, 0.1), (0.006, 0.008, 0.05), rot=(0.12, 0, 0), m=pr_, bev=0.002),
            box(root, tag + '_panfleto2', (0.008, 0.07, 0.1), (0.012, -0.006, 0.048), rot=(-0.1, 0, 0), m=pm, bev=0.002)]


def microphone(root, P, tag):
    """Microfone de mao (cabo preto, globo de grade) ao longo do Z local, com o fio caindo."""
    return [cyl(root, tag + '_microCabo', 0.012, 0.09, (0, 0, 0.02), r2=0.015, m=P['horn_d'], v=12, bev=0.003),
            sphere(root, tag + '_microGlobo', 0.024, (0, 0, 0.078), m=mat('grade_micro', '#9a9ca2', rough=0.45, metal=0.5, var=0, bump=0.4), seg=12),
            torus(root, tag + '_microAnel', (0, 0, 0.064), 0.017, 0.004, P['red'], n=12, segs=4),
            tube(root, tag + '_microFio', [(0, 0, -0.025), (0.02, 0.0, -0.08), (0.0, 0.02, -0.16), (-0.02, 0.03, -0.24)], 0.004, P['horn_d'], segs=4)]


def coffee_cup(root, P, tag):
    """Copinho de cafe de plastico (em pe na mao)."""
    return [cyl(root, tag + '_copinho', 0.017, 0.04, (0, 0, 0.012), r2=0.021, m=P['plastic'], v=14, bev=0.002),
            cyl(root, tag + '_cafezinho', 0.019, 0.004, (0, 0, 0.029), m=P['coffee'], v=14, bev=0.0)]


def build_guard(P, root):
    """Militante: camiseta vermelha com a estrela, bone vermelho, apito na boca e a bandeirinha da chapa."""
    tag = root['set']
    pr = build_person(P, root, tag, militant_sp(P))
    marca_peito(root, pr, tag)
    cap_brim(root, pr, tag)
    whistle(root, pr, tag)
    hand_flag(root, P, pr, tag)
    return pr


def build_sergeant(P, root):
    """Coordenador: bigode, bone vermelho, megafone de mao e o maco de panfletos."""
    tag = root['set']
    hair = mat('bigode_castanho', '#4a2c18', rough=0.8, var=0.02, bump=0.2)
    pr = build_person(P, root, tag, militant_sp(P))
    marca_peito(root, pr, tag)
    cap_brim(root, pr, tag)
    for s, yy in enumerate((-0.022, 0.022)):
        o = blob(root, f'{tag}_bigode{s}', 0.017, HC + Vector((0.064, yy, -0.024)), (0.7, 1.45, 0.65), hair)
        o.parent = pr['head']
    hold(pr, 'R', *megaphone(root, P, tag))
    hold(pr, 'L', *leaflets(root, P, tag))
    return pr


def build_lancer(P, root):
    """Presidente do sindicato: cabelo e barba grisalhos, lenco vermelho no pescoco, camiseta com a estrela e o
    microfone."""
    tag = root['set']
    grey = mat('barba_grisalha', '#c9c3b8', rough=0.85, var=0.02, bump=0.25)
    sp = militant_sp(P, cap=False, hair_m=grey, beard=grey)
    sp['head'] = 'bald'
    pr = build_person(P, root, tag, sp)
    marca_peito(root, pr, tag)
    # cabelo grisalho so dos lados e atras (careca no alto)
    fr = lathe(root, tag + '_franja', [(-0.03, 0.068, 0.07), (0.0, 0.072, 0.074), (0.03, 0.066, 0.068), (0.045, 0.05, 0.052)], grey, segs=16, lv=2,
               caps=False, solid=0.012, cut=lambda c: c.x > 0.02 and abs(math.atan2(c.y, c.x)) < math.radians(62))
    fr.parent = pr['head']
    fr.location = HC
    # cracha de diretor no cordao vermelho (cartao branco liso)
    o = tube(root, tag + '_crachaCordao', [(0.05, -0.05, 0.47), (0.096, -0.03, 0.39), (0.104, -0.012, 0.35), (0.098, 0.03, 0.39), (0.05, 0.05, 0.47)], 0.0045,
             cor('pri', rough=0.7), segs=4)
    o.parent = pr['body']
    o = box(root, tag + '_cracha', (0.006, 0.042, 0.054), (0.108, -0.012, 0.322), m=P['plastic'], bev=0.003)
    o.parent = pr['body']
    hold(pr, 'R', *microphone(root, P, tag))
    return pr


def build_monk(P, root):
    """Pelego: colete de pelego de carneiro por cima da camiseta, bone vermelho, olhos de sono, chinelo e o cafezinho."""
    tag = root['set']
    sp = militant_sp(P, vest=P['wool'], boots=P['skin'])
    pr = build_person(P, root, tag, sp)
    marca_peito(root, pr, tag)
    cap_brim(root, pr, tag)
    # la fofa na gola e nos ombros do colete
    rr = random.Random(5)
    for k in range(14):
        a = TAU * k / 14
        o = sphere(root, f'{tag}_la{k}', rr.uniform(0.022, 0.03), (0.075 * math.cos(a) * 0.95, 0.098 * math.sin(a), 0.44 + rr.uniform(-0.01, 0.015)),
                   scale=(1, 1, 0.75), m=P['wool'], seg=10)
        o.parent = pr['body']
    # palpebras caidas (sono)
    for s, yy in enumerate((-0.024, 0.024)):
        o = blob(root, f'{tag}_palpebra{s}', 0.0125, HC + Vector((0.061, yy, 0.019)), (0.7, 1.1, 0.62), P['skin'])
        o.parent = pr['head']
    # sola do chinelo
    for s, yy in enumerate((-0.046, 0.046)):
        o = box(root, f'{tag}_chinelo{s}', (0.11, 0.06, 0.012), (0.024, yy * 1.05, 0.006), m=mat('chinelo', '#2f62c9', rough=0.6, var=0, bump=0), bev=0.005)
        o.parent = pr['body']
    hold(pr, 'R', *coffee_cup(root, P, tag))
    boca = blob(root, tag + '_bocejo', 0.02, HC + Vector((0.058, 0.0, -0.03)), (0.5, 0.8, 1.15), mat('boca', '#3a1a14', rough=0.6, var=0, bump=0))
    boca.parent = pr['head']
    pr.setdefault('props', []).append(boca)
    return pr


IDLE_N, ACT_N = 12, 8


def guard_state(mode, f):
    """Militante. idle: bandeirinha no ombro, apito na boca; act: agita a bandeirinha bem alto (quando o companheiro sai)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.09, -0.15, 0.4 + 0.008 * s), grip_R=(0.12, -0.25, 1.0), hand_L=(0.05, 0.13, 0.28),
                    breathe=s, head_yaw=0.25 * math.sin(TAU * ph + 0.6), head_pitch=-0.1, ph=ph)
    t = f / ACT_N
    k = math.sin(math.pi * f / (ACT_N - 1))
    sw = math.sin(TAU * t * 2)
    return dict(hand_R=(0.09 + 0.02 * k, -0.15 - 0.02 * k, 0.4 + 0.12 * k), grip_R=(0.12 + 0.5 * sw * k, -0.3, 1.0),
                hand_L=(0.06 + 0.04 * k, 0.14, 0.29 + 0.05 * k), lean=0.04 * k, head_pitch=-0.18 * k - 0.05, head_yaw=0.1, ph=t)


def sergeant_state(mode, f):
    """Coordenador. idle: megafone baixo, panfletos no peito; act: megafone na boca e o punho dos panfletos erguido."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.06, -0.14, 0.29 + 0.006 * s), grip_R=(1.0, -0.2, -0.35), hand_L=(0.14, 0.07, 0.35 + 0.006 * s), grip_L=(0.35, 0.1, 1.0),
                    breathe=s, head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    k = math.sin(math.pi * min(1.0, f / (ACT_N - 2)))
    return dict(hand_R=(0.06 + 0.08 * k, -0.14 + 0.1 * k, 0.29 + 0.17 * k), grip_R=(1.0, -0.2 + 0.15 * k, -0.35 + 0.45 * k),
                hand_L=(0.1 + 0.02 * k, 0.1 + 0.05 * k, 0.35 + 0.2 * k), grip_L=(0.2, 0.1, 1.0),
                lean=0.08 * k, head_pitch=-0.12 - 0.12 * k, head_yaw=0.05, ph=f / ACT_N)


def chief_state(mode, f):
    """Presidente. idle: microfone no peito, a outra mao gesticulando; act: discursa de microfone na boca, acenando."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.12, -0.08, 0.38 + 0.006 * s), grip_R=(0.3, 0.25, 1.0), hand_L=(0.1, 0.14, 0.3 + 0.03 * max(0, s)), grip_L=(1, 0, 0.2),
                    breathe=s, head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.08, ph=ph)
    t = f / ACT_N
    k = math.sin(math.pi * f / (ACT_N - 1))
    wv = math.sin(TAU * t * 2)
    return dict(hand_R=(0.12 + 0.02 * k, -0.08 + 0.05 * k, 0.38 + 0.07 * k), grip_R=(0.3 - 0.4 * k, 0.25 + 0.2 * k, 1.0),
                hand_L=(0.06, 0.17 + 0.03 * wv * k, 0.32 + 0.24 * k), grip_L=(0.2, 0.1 * wv, 1.0),
                lean=0.05 * k, head_pitch=-0.08 - 0.15 * k, head_yaw=0.15 * k, ph=t)


def pelego_state(mode, f):
    """Pelego. idle: toma o cafezinho devagar, de olho fechado; act: espreguica de bracos para cima e boceja."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        sip = max(0.0, math.sin(TAU * ph)) ** 2
        return dict(hand_R=(0.11 + 0.0 * sip, -0.1 + 0.07 * sip, 0.34 + 0.12 * sip), grip_R=(0.1 - 0.5 * sip, 0.0, 1.0), hand_L=(0.03, 0.14, 0.27),
                    breathe=0.7 * s, head_yaw=0.1 * s, head_pitch=0.05 - 0.2 * sip, head_roll=0.06, ph=ph, hide=(root_tag_bocejo(),))
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_R=(0.02 + 0.02 * k, -0.13 - 0.03 * k, 0.32 + 0.3 * k), grip_R=(0.0, 0.0, 1.0), hand_L=(0.02 + 0.02 * k, 0.13 + 0.03 * k, 0.28 + 0.34 * k),
                pole_R=(-0.3, -1.0, -0.2), pole_L=(-0.3, 1.0, -0.2), lean=-0.1 * k, head_pitch=-0.25 * k, head_roll=0.05,
                breathe=1.5 * k, hide=() if k > 0.35 else (root_tag_bocejo(),), ph=f / ACT_N)


def root_tag_bocejo():
    return 'qtM_c_bocejo'


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'qt1': 'qtG', 'qt2': 'qtG', 'qt3': ['qtS', 'qtG'], 'qtL': 'qtL_c', 'qtM': 'qtM_c'},
    'towers': [('qt1', 'Sindicato N1', build_qt1), ('qt2', 'Sindicato N2', build_qt2), ('qt3', 'Sindicato N3', build_qt3),
               ('qtL', 'Diretoria do Sindicato', build_qtL), ('qtM', 'Pelegos', build_qtM)],
    'crews': [crew('qtG', 'Militante', build_guard, guard_state), crew('qtS', 'Coordenador', build_sergeant, sergeant_state),
              crew('qtL_c', 'Presidente do sindicato', build_lancer, chief_state), crew('qtM_c', 'Pelego', build_monk, pelego_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
