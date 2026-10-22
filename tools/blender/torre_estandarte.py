"""CPI (Estandarte, Ninguem Sobe a Rampa): niveis 1 a 3, Palanque da CPI e Quebra de Sigilo. Mesa de comissao
parlamentar de madeira num tablado com carpete da chapa e galao claro, microfones de mesa, cadeira de veludo,
holofotes e a lupa gigante que balanca (a lupa e o 'revela invisiveis'), bandeira da chapa sem texto, tudo sobre
o lote de concreto branco de Brasilia (conceito: arte/conceitos/torres/cpi.png).
Nomes de conjuntos, postos, pontos e modos sao os mesmos da Samauma Sagrada (js/sprites.js depende deles).

Cores da chapa (tools/blender/chapa.py): carpete, passadeira, cadeiras, cordao, surdos, painel e bandeirolas na cor da
chapa, galao e frisos no tom claro dela; a bandeira do mastro vira a da chapa; a turma leva gravata, broche de lapela,
camiseta e bone da chapa. Madeira, lupa, martelo, cofre, pastas e o lacre de cera ficam iguais.
  CHAPA=V (padrao): carpete verde com galao amarelo, bandeira do Brasil (losango amarelo e circulo azul)
  CHAPA=R:          carpete vermelho com galao branco, bandeira vermelha com estrela branca, estrela na lapela

  Blender -b -P tools/blender/torre_estandarte.py -- render arte/render/estandarte [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_estandarte.py -- render arte/render_r/estandarte [conjuntos...]
  Blender -b -P tools/blender/torre_estandarte.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_estandarte.py -- crew <arquivo.png> [amostras] [show|pose0]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, G   # noqa: F811 - lote de concreto de Brasilia
from pecas_zcv import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, star_pts, emblema, bandeirinha, estrela_peito   # cores da chapa (CHAPA=V ou R)

FRONT = -math.pi / 2
FAM = 'estandarte'

import lib as _lib
_orig_palette2 = palette2


V_ = CHAPA == 'V'
VELUDO = dict(rough=0.88, var=0.03, bump=0.1, sheen=0.9)
BANDEIRA = dict(rough=0.8, var=0.0, bump=0.04, sheen=0.4)


def palette2():   # noqa: F811 - veludo da chapa, madeira de mesa de comissao, ouro e concreto branco
    P = _orig_palette2()
    P['velvet'] = cor('pri', **VELUDO)        # carpete, passadeira, cadeiras, cordao, surdos: V verde / R vermelho
    P['velvet_d'] = cor('escuro', **VELUDO)   # painel do palanque
    P['teal'] = P['velvet']   # o pano de assinatura do lib (estandartes, faixas) vira o veludo da chapa
    P['stripes'] = mat(f'listra_chapa_{CHAPA}', PAL['pri'], rough=0.85, var=0.0, bump=0.06, stripes=(3.6, PAL['claro'], PAL['pri']), sheen=0.4)
    P['trim'] = cor('sec', rough=0.45, var=0.02, bump=0.03, sheen=0.3)   # galao, frisos e franjas: V amarelo / R branco
    P['braid'] = mat('galao_ouro', '#e2b23f', rough=0.42, metal=0.35, var=0.02, bump=0.03)   # ouro dos objetos (botoes, aneis)
    P['folder'] = cor('sec', rough=0.6, var=0.02, bump=0.04)   # capa do relatorio: V amarela / R branca
    # lacre de cera e fita do cofre: vermelho de lacre nas duas chapas (e o objeto da piada, nao a cor da chapa)
    P['seal'] = mat('lacre_cpi', '#b3262f', rough=0.88, var=0.03, bump=0.1, sheen=0.9)
    P['seal_d'] = mat('lacre_cpi_escuro', '#86191f', rough=0.88, var=0.03, bump=0.1, sheen=0.9)
    P['desk'] = mat('mesa_cpi', '#a8683a', rough=0.5, var=0.05, bump=0.06)
    P['desk_l'] = mat('mesa_cpi_tampo', '#c58652', rough=0.42, var=0.04, bump=0.04)
    P['desk_d'] = mat('mesa_cpi_painel', '#86502a', rough=0.55, var=0.05, bump=0.06)
    P['stage'] = mat('tablado_cpi', '#9a5e34', rough=0.6, var=0.08, bump=0.12)
    P['stage_d'] = mat('tablado_cpi_escuro', '#7b4825', rough=0.65, var=0.08, bump=0.12)
    P['mic'] = mat('microfone_preto', '#2a2a2f', rough=0.55, var=0.0, bump=0.08)
    P['chrome'] = mat('cromado_cpi', '#d7dce0', rough=0.18, metal=0.9, var=0.02, bump=0.0)
    P['spot'] = mat('holofote_grafite', '#4a4e57', rough=0.4, metal=0.4, var=0.03, bump=0.02)
    P['lens'] = mat('lente_lupa', '#cfe9f2', rough=0.03, metal=0.15, var=0.0, bump=0.0)
    P['shine'] = mat('brilho_lupa', '#ffffff', rough=0.2, var=0.0, bump=0.0, emit=0.6)
    P['paper'] = mat('papel_cpi', '#fbf6ea', rough=0.8, var=0.02, bump=0.02)
    P['handle'] = mat('cabo_lupa', '#8a3f22', rough=0.45, var=0.03, bump=0.04)
    P['onair'] = glow_mat('luz_microfone', '#ff4a3a', 1.5, 8.0, rough=0.3, var=0.0, bump=0.0)
    # bandeira da chapa: campo, losango (V) ou estrela (R) e circulo azul (so V)
    P['flag_g'] = cor('pri', **BANDEIRA)
    P['flag_y'] = cor('sec', **BANDEIRA)
    P['flag_b'] = cor('ter', **BANDEIRA)
    P['conc'] = concrete()
    P['_emblem'] = 'sun'
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


# ---------------------------------------------------------------- tablado, carpete, escada
def stage(root, P, tag, cx, cy, w, d, h, z0=G, carpet=True, r=0.08):
    """Tablado de madeira com tabuas marcadas na frente, carpete da chapa por cima com galao claro. Devolve o topo."""
    slab(root, tag, w, d, h, P['stage'], r=r, loc=(cx, cy, z0 + h / 2), rot=(math.pi / 2, 0, 0), bev=0.02)
    n = max(3, int(w / 0.16))
    for k in range(1, n):
        x = cx - w / 2 + w * k / n
        box(root, f'{tag}_junta{k}', (0.008, 0.01, h * 0.8), (x, cy - d / 2 - 0.002, z0 + h / 2), m=P['stage_d'], bev=0.0)
    zt = z0 + h
    if carpet:
        slab(root, tag + '_galao', w - 0.03, d - 0.03, 0.012, P['trim'], r=r * 0.8, loc=(cx, cy, zt + 0.006), rot=(math.pi / 2, 0, 0), bev=0.004)
        slab(root, tag + '_carpete', w - 0.08, d - 0.08, 0.016, P['velvet'], r=r * 0.6, loc=(cx, cy, zt + 0.01), rot=(math.pi / 2, 0, 0), bev=0.005)
    return zt + 0.012


def stairs(root, P, tag, x, y0, z_top, w=0.34, n=2, run=0.1, z0=G):
    """Degraus de madeira descendo para a frente (-Y) a partir da borda y0, com a passadeira da chapa e o galao."""
    dz = (z_top - z0) / (n + 1)
    for k in range(n):
        zt = z_top - dz * (k + 1)
        yc = y0 - run * (k + 0.5)
        box(root, f'{tag}{k}', (w, run + 0.01, zt - z0), (x, yc, (zt + z0) / 2), m=P['stage'], bev=0.012)
        box(root, f'{tag}{k}_passadeira', (w * 0.7, run + 0.012, 0.014), (x, yc, zt + 0.005), m=P['velvet'], bev=0.004)
        for sx in (-1, 1):
            box(root, f'{tag}{k}_galao{sx}', (0.018, run + 0.014, 0.016), (x + sx * w * 0.36, yc, zt + 0.006), m=P['trim'], bev=0.003)
    # passadeira descendo pelo espelho dos degraus
    for k in range(n + 1):
        zt = z_top - dz * k
        yc = y0 - run * k
        box(root, f'{tag}{k}_espelho', (w * 0.7, 0.012, dz), (x, yc - 0.004, zt - dz / 2), m=P['velvet'], bev=0.003)


# ---------------------------------------------------------------- mesa, cadeira, microfone, papeis
def desk(root, P, tag, cx, cy, z0, w=0.78, d=0.28, h=0.3, panels=3):
    """Mesa de comissao: tampo claro, frente com paineis rebaixados e um friso na cor clara da chapa."""
    box(root, tag + '_tampo', (w + 0.04, d + 0.04, 0.04), (cx, cy, z0 + h - 0.02), m=P['desk_l'], bev=0.012)
    box(root, tag + '_corpo', (w, d, h - 0.04), (cx, cy, z0 + (h - 0.04) / 2), m=P['desk'], bev=0.014)
    pw = (w - 0.06) / panels
    for k in range(panels):
        x = cx - w / 2 + 0.03 + pw * (k + 0.5)
        box(root, f'{tag}_painel{k}', (pw - 0.04, 0.012, h - 0.12), (x, cy - d / 2 - 0.004, z0 + (h - 0.04) / 2 - 0.01), m=P['desk_d'], bev=0.006)
    box(root, tag + '_friso', (w - 0.02, 0.01, 0.014), (cx, cy - d / 2 - 0.006, z0 + h - 0.065), m=P['trim'], bev=0.003)
    box(root, tag + '_rodape', (w + 0.02, d + 0.02, 0.03), (cx, cy, z0 + 0.015), m=P['desk_d'], bev=0.008)
    return z0 + h


def chair(root, P, tag, x, y, z0, s=1.0, rz=0.0):
    """Cadeira de presidente de comissao: estofado de veludo da chapa, encosto alto com moldura de madeira."""
    with grupo(root, tag, loc=(x, y, z0), rot=(0, 0, rz)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                tube(root, f'{tag}_pe{sx}{sy}', [(sx * 0.1 * s, sy * 0.09 * s, 0), (sx * 0.1 * s, sy * 0.09 * s, 0.2 * s)], 0.014 * s, P['desk_d'], segs=6)
        box(root, tag + '_assento', (0.26 * s, 0.24 * s, 0.06 * s), (0, 0, 0.22 * s), m=P['velvet'], bev=0.025 * s)
        slab(root, tag + '_moldura', 0.28 * s, 0.46 * s, 0.05 * s, P['desk'], r=0.1 * s, loc=(0, 0.11 * s, 0.46 * s), bev=0.015 * s)
        slab(root, tag + '_encosto', 0.22 * s, 0.38 * s, 0.05 * s, P['velvet'], r=0.08 * s, loc=(0, 0.095 * s, 0.46 * s), bev=0.02 * s)
        for k in range(3):
            sphere(root, f'{tag}_botao{k}', 0.01 * s, ((k - 1) * 0.06 * s, 0.065 * s, 0.56 * s), m=P['braid'], seg=8)
        for sx in (-1, 1):
            box(root, f'{tag}_braco{sx}', (0.04 * s, 0.2 * s, 0.03 * s), (sx * 0.14 * s, 0.0, 0.32 * s), m=P['desk'], bev=0.01 * s)
            tube(root, f'{tag}_bracoPe{sx}', [(sx * 0.14 * s, -0.07 * s, 0.24 * s), (sx * 0.14 * s, -0.07 * s, 0.31 * s)], 0.01 * s, P['desk'], segs=6)


def desk_mic(root, P, tag, x, y, z, yaw=0.0, s=1.0):
    """Microfone de mesa: base redonda, haste flexivel (pescoco de ganso), cabeca de espuma e a luz vermelha."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, yaw)):
        cyl(root, tag + '_base', 0.045 * s, 0.022 * s, (0, 0, 0.011 * s), r2=0.038 * s, m=P['mic'], v=18, bev=0.006)
        sphere(root, tag + '_luz', 0.008 * s, (0.0, -0.04 * s, 0.018 * s), m=P['onair'], seg=8)
        tube(root, tag + '_pescoco', [(0, 0, 0.02 * s), (0, -0.01 * s, 0.1 * s), (0, -0.04 * s, 0.16 * s), (0, -0.08 * s, 0.18 * s)], 0.008 * s, P['chrome'], segs=6)
        sphere(root, tag + '_cabeca', 0.024 * s, (0, -0.1 * s, 0.18 * s), scale=(1, 1.35, 1), m=P['mic'], seg=12, rot=(0.5, 0, 0))


def papers(root, P, tag, x, y, z, n=3, rz=0.0, seed=1):
    rr = random.Random(seed)
    for k in range(n):
        box(root, f'{tag}{k}', (0.11, 0.15, 0.005), (x + rr.uniform(-0.02, 0.02), y + rr.uniform(-0.02, 0.02), z + 0.003 + 0.004 * k),
            rot=(0, 0, rz + rr.uniform(-0.25, 0.25)), m=P['paper'], bev=0.001)


def water(root, P, tag, x, y, z):
    """Copo d'agua e jarra na mesa."""
    cyl(root, tag + '_copo', 0.02, 0.06, (x, y, z + 0.03), r2=0.024, m=P['glass'], v=14, bev=0.003)
    cyl(root, tag + '_agua', 0.019, 0.035, (x, y, z + 0.02), r2=0.021, m=P['water_l'], v=14, bev=0.0)


# ---------------------------------------------------------------- holofote, lupa, bandeira
def spotlight(root, P, lights, tag, base, h, yaw, pitch=0.5, s=1.0, sweep=0.0, ph0=0.0, tripod=True, ground=True):
    """Holofote de palco num tripe: lata grafite com abas, lente acesa. sweep > 0: a cabeca varre (anim)."""
    x, y, z = base
    if tripod:
        for k in range(3):
            a = TAU * k / 3 + 0.4
            tube(root, f'{tag}_perna{k}', [(x + 0.16 * s * math.cos(a), y + 0.16 * s * math.sin(a), z), (x, y, z + 0.22 * s)], 0.012 * s, P['spot'], segs=6)
    elif ground:
        cyl(root, tag + '_base', 0.08 * s, 0.03 * s, (x, y, z + 0.015 * s), m=P['spot'], v=16, bev=0.008)
    tube(root, tag + '_haste', [(x, y, z + (0.2 * s if tripod else 0)), (x, y, z + h)], 0.016 * s, P['chrome'], segs=8)
    torus(root, tag + '_trava', (x, y, z + h * 0.6), 0.02 * s, 0.008 * s, P['spot'], n=12, segs=4)
    piv = empty(root, tag + '_giro', loc=(x, y, z + h), rot=(0, 0, yaw))
    kids(piv, tube(root, tag + '_garfo', [(0, -0.085 * s, 0.1 * s), (0, -0.085 * s, 0.0), (0, 0.085 * s, 0.0), (0, 0.085 * s, 0.1 * s)], 0.01 * s, P['spot'], segs=6))
    tilt = empty(root, tag + '_incl', parent=piv, loc=(0, 0, 0.1 * s), rot=(0, pitch, 0))
    can = lathe(root, tag + '_lata', [(-0.12 * s, 0.0, 0.0), (-0.11 * s, 0.05 * s, 0.05 * s), (-0.06 * s, 0.07 * s, 0.07 * s), (0.08 * s, 0.075 * s, 0.075 * s)],
                P['spot'], segs=20, lv=1, caps=True)
    can.rotation_euler = (0, math.pi / 2, 0)
    kids(tilt, can)
    kids(tilt, cyl(root, tag + '_lente', 0.064 * s, 0.012, (0.085 * s, 0, 0), rot=(0, math.pi / 2, 0), m=P['glow'], v=20, bev=0.0),
         torus(root, tag + '_aro', (0.085 * s, 0, 0), 0.072 * s, 0.009 * s, P['chrome'], axis='X', n=20, segs=4))
    for k, (dy, dz, rx) in enumerate(((0.0, 0.085, -0.6), (0.0, -0.085, 0.6), (0.085, 0.0, 0.0), (-0.085, 0.0, 0.0))):
        if dz:
            fl = box(root, f'{tag}_aba{k}', (0.07 * s, 0.13 * s, 0.006), (0.11 * s, 0, (dz + 0.02 * (1 if dz > 0 else -1)) * s), rot=(0, rx, 0), m=P['spot'], bev=0.002)
        else:
            fl = box(root, f'{tag}_aba{k}', (0.07 * s, 0.006, 0.13 * s), (0.11 * s, (dy + 0.02 * (1 if dy > 0 else -1)) * s, 0.0), rot=(0, 0, -0.6 if dy > 0 else 0.6),
                     m=P['spot'], bev=0.002)
        fl.parent = tilt
    if sweep:
        def fn(o, mb, ph, a=sweep, p0=ph0):
            o.matrix_basis = mb @ Matrix.Rotation(a * math.sin(TAU * (ph + p0)), 4, 'Z')
        register_anim(piv, fn)
    bpy.context.view_layer.update()
    lp = tilt.matrix_world @ Vector((0.12 * s, 0, 0))
    lights.append(((lp.x, lp.y, lp.z), '#ffe2a6', 12.0 * s, 1))
    return piv


def magnifier(root, P, tag, base, h, R=0.22, yaw=0.3, rock=0.22, ph0=0.0, stand=True):
    """Lupa gigante num pedestal: aro cromado grosso, lente azulada com reflexo e o cabo de madeira para baixo e para
    o lado. A cabeca balanca devagar, varrendo (anim). Devolve (pivo, centro da lente)."""
    x, y, z = base
    if stand:
        cyl(root, tag + '_base', 0.12, 0.04, (x, y, z + 0.02), r2=0.1, m=P['spot'], v=24, bev=0.012)
        tube(root, tag + '_haste', [(x, y, z + 0.04), (x, y, z + h)], 0.02, P['chrome'], segs=10)
        torus(root, tag + '_trava', (x, y, z + h * 0.55), 0.028, 0.01, P['spot'], n=14, segs=5)
    piv = empty(root, tag + '_giro', loc=(x, y, z + h), rot=(0, 0, yaw))
    kids(piv, sphere(root, tag + '_junta', 0.035, (0, 0, 0), m=P['spot'], seg=14))
    with grupo(root, tag + '_cabeca', loc=(0, 0, R * 1.05), rot=(0, 0, 0), parent=piv) as hd:
        torus(root, tag + '_aro', (0, 0, 0), R, R * 0.12, P['chrome'], axis='Y', n=40, segs=10)
        cyl(root, tag + '_lente', R * 0.94, R * 0.06, (0, 0, 0), rot=(math.pi / 2, 0, 0), m=P['lens'], v=40, bev=R * 0.02)
        tube(root, tag + '_reflexo', [(R * 0.55 * math.cos(a), -R * 0.05, R * 0.55 * math.sin(a)) for a in [math.radians(v) for v in range(110, 171, 10)]],
             R * 0.06, P['shine'], segs=6)
        sphere(root, tag + '_reflexo2', R * 0.06, (R * 0.2, -R * 0.05, R * 0.62), scale=(1, 0.4, 1), m=P['shine'], seg=10)
        # cabo para baixo e para a direita
        a = math.radians(-50)
        c0 = Vector((R * 1.08 * math.cos(a), 0, R * 1.08 * math.sin(a)))
        c1 = Vector((R * 2.0 * math.cos(a), 0, R * 2.0 * math.sin(a)))
        tube(root, tag + '_pescoco', [c0, c0.lerp(c1, 0.25)], R * 0.1, P['chrome'], segs=10)
        tube(root, tag + '_cabo', [c0.lerp(c1, 0.22), c1], R * 0.13, P['handle'], segs=12, rfun=lambda t: R * (0.12 + 0.03 * math.sin(math.pi * t)))
        sphere(root, tag + '_caboPonta', R * 0.13, (c1.x, 0, c1.z), m=P['handle'], seg=12)
    if rock:
        def fn(o, mb, ph, a=rock, p0=ph0):
            o.matrix_basis = mb @ Matrix.Rotation(a * math.sin(TAU * (ph + p0)), 4, 'Z') @ Matrix.Rotation(0.06 * math.sin(TAU * (ph + p0) * 2), 4, 'X')
        register_anim(piv, fn)
    return piv, (x, y, z + h + R * 1.05)


def br_flag(root, P, tag, x, y, z0, h, w=0.36, front=False):
    """Mastro com a bandeira da chapa, tremulando: V = bandeira do Brasil (campo verde, losango amarelo, circulo azul;
    sem a faixa de texto), R = campo vermelho com a estrela branca de 5 pontas no meio."""
    tube(root, tag + '_mastro', [(x, y, z0), (x, y, z0 + h)], 0.014, P['chrome'], segs=8)
    sphere(root, tag + '_ponta', 0.026, (x, y, z0 + h + 0.02), m=P['braid'], seg=12)
    cyl(root, tag + '_base', 0.06, 0.04, (x, y, z0 + 0.02), r2=0.045, m=P['spot'], v=16, bev=0.01)
    fh = w * 0.7
    o = cloth_grid(root, tag, w, fh, 14, 6, [P['flag_g'], P['flag_y'], P['flag_b']], thick=0.01, front=front)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for yy in (-0.009, 0.009):
        if not V_:
            st = [bm.verts.new((w / 2 + px, yy, -fh / 2 + pz)) for px, pz in star_pts(fh * 0.4)]
            f = bm.faces.new(st if yy < 0 else st[::-1])
            f.material_index = 1
            continue
        lz = [bm.verts.new(p) for p in ((w * 0.1, yy, -fh / 2), (w / 2, yy, -fh * 0.1), (w * 0.9, yy, -fh / 2), (w / 2, yy, -fh * 0.9))]
        f = bm.faces.new(lz if yy < 0 else lz[::-1])
        f.material_index = 1
        yb = yy * 1.4
        circ = [bm.verts.new((w / 2 + fh * 0.2 * math.cos(a), yb, -fh / 2 + fh * 0.2 * math.sin(a))) for a in [TAU * k / 20 for k in range(20)]]
        f = bm.faces.new(circ if yy < 0 else circ[::-1])
        f.material_index = 2
    bm.to_mesh(me)
    bm.free()
    o.location = (x + 0.012, y, z0 + h - 0.02)
    register_cloth(o, flag_wave(w, amp=0.05, cycles=1, waves=1.1))
    return o


def velvet_rope(root, P, tag, pts, z0=G, h=0.24):
    """Pedestais cromados com cordao de veludo (a area reservada da comissao)."""
    for k, (x, y) in enumerate(pts):
        cyl(root, f'{tag}_base{k}', 0.04, 0.02, (x, y, z0 + 0.01), r2=0.032, m=P['chrome'], v=14, bev=0.005)
        tube(root, f'{tag}_poste{k}', [(x, y, z0), (x, y, z0 + h)], 0.011, P['chrome'], segs=6)
        sphere(root, f'{tag}_bola{k}', 0.018, (x, y, z0 + h + 0.01), m=P['braid'], seg=10)
    for k in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        line = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + h - 0.02 - 0.07 * math.sin(math.pi * t)) for t in [j / 8 for j in range(9)]]
        tube(root, f'{tag}_cordao{k}', line, 0.012, P['velvet'], segs=6)


# ---------------------------------------------------------------- nivel 1: mesinha de comissao num tablado baixo
def build_es1(P, root):
    plot(root, P, 'es1')
    lights = []
    zt = stage(root, P, 'es1_tablado', -0.04, 0.12, 0.92, 0.6, 0.09)
    zd = desk(root, P, 'es1_mesa', -0.06, 0.16, zt, w=0.5, d=0.24, h=0.27, panels=2)
    chair(root, P, 'es1_cadeira', -0.06, 0.36, zt, s=0.85)
    desk_mic(root, P, 'es1_micro', -0.14, 0.12, zd, yaw=0.2)
    papers(root, P, 'es1_papel', 0.06, 0.14, zd, n=2, rz=0.2)
    water(root, P, 'es1_agua', 0.14, 0.2, zd)
    br_flag(root, P, 'es1_bandeira', -0.42, 0.34, zt, 1.0, w=0.32)
    spotlight(root, P, lights, 'es1_holofote', (-0.6, -0.14, G), 0.52, math.radians(25), pitch=0.45, s=0.85)
    _, lc = magnifier(root, P, 'es1_lupa', (0.5, 0.16, G), 0.62, R=0.2, yaw=math.radians(-20), rock=0.2)
    return {'slots': [(0.34, -0.42, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- nivel 2: tablado com degraus, mesa com dois microfones
def build_es2(P, root):
    plot(root, P, 'es2')
    lights = []
    zt = stage(root, P, 'es2_tablado', 0.0, 0.08, 1.12, 0.78, 0.12)
    stairs(root, P, 'es2_degrau', -0.28, 0.08 - 0.39, zt, w=0.32, n=1, run=0.1)
    zd = desk(root, P, 'es2_mesa', 0.0, 0.2, zt, w=0.68, d=0.26, h=0.29, panels=3)
    chair(root, P, 'es2_cadeira', 0.0, 0.42, zt, s=0.95)
    desk_mic(root, P, 'es2_micro1', -0.18, 0.16, zd, yaw=0.25)
    desk_mic(root, P, 'es2_micro2', 0.16, 0.16, zd, yaw=-0.2)
    papers(root, P, 'es2_papel', -0.02, 0.18, zd, n=3)
    water(root, P, 'es2_agua', 0.27, 0.24, zd)
    br_flag(root, P, 'es2_bandeira', -0.46, 0.38, zt, 1.18, w=0.36)
    spotlight(root, P, lights, 'es2_holofote', (-0.24, 0.42, zt), 1.04, math.radians(-75), pitch=0.6, s=0.95, tripod=False, sweep=0.18)
    _, lc = magnifier(root, P, 'es2_lupa', (0.6, 0.1, G), 0.78, R=0.23, yaw=math.radians(-20), rock=0.22)
    velvet_rope(root, P, 'es2_cordao', [(0.24, -0.5), (0.52, -0.38)])
    return {'slots': [(0.06, -0.16, zt)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- nivel 3: a CPI completa (dois andares de tablado)
def build_es3(P, root):
    plot(root, P, 'es3')
    lights = []
    z1 = stage(root, P, 'es3_tablado1', 0.0, 0.04, 1.3, 0.92, 0.08, r=0.1)
    z2 = stage(root, P, 'es3_tablado2', 0.04, 0.2, 1.02, 0.58, 0.08, z0=z1, r=0.08)
    stairs(root, P, 'es3_degrau', -0.18, 0.2 - 0.29, z2, w=0.36, n=1, run=0.09, z0=z1)
    stairs(root, P, 'es3_degrauBaixo', -0.18, 0.04 - 0.46, z1, w=0.4, n=1, run=0.1)
    zd = desk(root, P, 'es3_mesa', 0.04, 0.22, z2, w=0.8, d=0.28, h=0.3, panels=3)
    chair(root, P, 'es3_cadeira', 0.06, 0.46, z2, s=1.05)
    desk_mic(root, P, 'es3_micro1', -0.22, 0.17, zd, yaw=0.25)
    desk_mic(root, P, 'es3_micro2', 0.2, 0.17, zd, yaw=-0.2)
    papers(root, P, 'es3_papel', 0.0, 0.2, zd, n=3)
    water(root, P, 'es3_agua', -0.33, 0.27, zd)
    br_flag(root, P, 'es3_bandeira', -0.4, 0.44, z2, 1.3, w=0.4)
    spotlight(root, P, lights, 'es3_holofote1', (-0.6, -0.08, G), 0.74, math.radians(30), pitch=0.5, s=1.0)
    spotlight(root, P, lights, 'es3_holofote2', (-0.12, 0.46, z2), 1.16, math.radians(-75), pitch=0.65, s=1.0, tripod=False, sweep=0.2)
    _, lc = magnifier(root, P, 'es3_lupa', (0.62, 0.06, G), 0.92, R=0.28, yaw=math.radians(-20), rock=0.24)
    velvet_rope(root, P, 'es3_cordao', [(0.24, -0.6), (0.56, -0.44)])
    return {'slots': [(-0.32, -0.26, z1)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- Palanque da CPI: palco com trelica, holofotes,
# caixas de som que pulsam e os surdos da batucada
def truss(root, P, tag, p0, p1, w=0.07, m=None):
    """Trelica quadrada de aluminio (quatro tubos e diagonais em zigue-zague) entre dois pontos."""
    m = m or P['chrome']
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0)
    L = d.length
    q = d.to_track_quat('Z', 'Y')
    with grupo(root, tag, loc=p0, rot=q.to_euler()):
        cs = [(-w / 2, -w / 2), (w / 2, -w / 2), (w / 2, w / 2), (-w / 2, w / 2)]
        for k, (a, b) in enumerate(cs):
            tube(root, f'{tag}_tubo{k}', [(a, b, 0), (a, b, L)], 0.009, m, segs=6)
        n = max(2, int(L / w))
        for k in range(4):
            (a0, b0), (a1, b1) = cs[k], cs[(k + 1) % 4]
            pts = [((a0, b0) if j % 2 == 0 else (a1, b1)) for j in range(n + 1)]
            tube(root, f'{tag}_diag{k}', [(px, py, L * j / n) for j, (px, py) in enumerate(pts)], 0.005, m, segs=4)


def speaker(root, P, tag, x, y, z, w=0.26, h=0.36, d=0.22, rz=0.0, ph0=0.0):
    """Caixa de som de palco: gabinete grafite, tela, woofer que pulsa (anim) e tweeter."""
    cab = mat('caixa_som', '#2f3136', rough=0.6, var=0.03, bump=0.08)
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rz)):
        box(root, tag + '_gabinete', (w, d, h), (0, 0, h / 2), m=cab, bev=0.02)
        box(root, tag + '_quina', (w + 0.012, d * 0.3, 0.02), (0, d * 0.35, h - 0.01), m=P['chrome'], bev=0.004)
        cyl(root, tag + '_tweeter', w * 0.11, 0.02, (0, -d / 2 - 0.006, h * 0.8), rot=(math.pi / 2, 0, 0), m=P['chrome'], v=16, bev=0.004)
        torus(root, tag + '_aroWoofer', (0, -d / 2 - 0.004, h * 0.38), w * 0.36, 0.012, P['chrome'], axis='Y', n=28, segs=5)
    wf = empty(root, tag + '_woofer', loc=(x + math.sin(rz) * (d / 2 + 0.004), y - math.cos(rz) * (d / 2 + 0.004), z + h * 0.38), rot=(math.pi / 2, 0, rz))
    kids(wf, lathe(root, tag + '_cone', [(0.0, w * 0.34, w * 0.34), (-0.025, w * 0.2, w * 0.2), (-0.035, w * 0.08, w * 0.08), (-0.03, 0.0, 0.0)],
                   mat('cone_som', '#5a5d64', rough=0.7, var=0.0, bump=0.1), segs=24, lv=1, caps=False, solid=0.006),
         sphere(root, tag + '_domo', w * 0.07, (0, 0, -0.03), scale=(1, 1, 0.6), m=cab, seg=12))

    def fn(o, mb, ph, p0=ph0):
        k = 1.0 + 0.08 * max(0.0, math.sin(TAU * 2 * (ph + p0)))
        o.matrix_basis = mb @ Matrix.Diagonal((k, k, 1.0 + 0.6 * (k - 1), 1))
    register_anim(wf, fn)


def surdo(root, P, tag, x, y, z, r=0.13, h=0.2):
    """Surdo da batucada num suporte: casco da chapa com aros dourados e pele clara."""
    for k in range(3):
        a = TAU * k / 3 + 0.5
        tube(root, f'{tag}_pe{k}', [(x + r * 0.9 * math.cos(a), y + r * 0.9 * math.sin(a), z), (x, y, z + 0.2)], 0.008, P['chrome'], segs=5)
    zb = z + 0.2
    cyl(root, tag, r, h, (x, y, zb + h / 2), m=P['velvet'], v=28, bev=0.01)
    for k, zz in enumerate((zb + 0.005, zb + h - 0.005)):
        torus(root, f'{tag}_aro{k}', (x, y, zz), r + 0.004, 0.012, P['braid'], n=28, segs=5)
    cyl(root, tag + '_pele', r * 0.97, 0.008, (x, y, zb + h + 0.002), m=P['paper'], v=28, bev=0.002)
    for k in range(8):
        a = TAU * k / 8
        tube(root, f'{tag}_tirante{k}', [(x + (r + 0.006) * math.cos(a), y + (r + 0.006) * math.sin(a), zb + 0.02),
                                        (x + (r + 0.006) * math.cos(a), y + (r + 0.006) * math.sin(a), zb + h - 0.02)], 0.004, P['chrome'], segs=4)
    return zb + h


def bunting(root, P, tag, p0, p1, n=9, sag=0.08):
    """Varal de bandeirolas da chapa (V verde, amarelo e azul; R vermelho, branco e vinho)."""
    p0, p1 = Vector(p0), Vector(p1)
    pts = [p0.lerp(p1, t) - Vector((0, 0, sag * math.sin(math.pi * t))) for t in [j / 16 for j in range(17)]]
    tube(root, tag + '_fio', pts, 0.004, P['mic'], segs=4)
    cols = [P['velvet'], P['trim'], P['flag_b'] if V_ else P['velvet_d']]
    for k in range(n):
        t = (k + 0.5) / n
        c = p0.lerp(p1, t) - Vector((0, 0, sag * math.sin(math.pi * t)))
        o = cyl(root, f'{tag}_bandeirola{k}', 0.035, 0.07, (c.x, c.y - 0.003, c.z - 0.035), r2=0.0, rot=(math.pi, 0, 0), m=cols[k % 3], v=3, bev=0.0)
        o.scale = (1.0, 0.18, 1.0)
        o.rotation_euler = (math.pi, 0, math.pi / 2 + 0.0)


def build_esD(P, root):
    plot(root, P, 'esD')
    lights = []
    cx, cy = 0.0, 0.06
    W, D = 1.24, 0.74
    zt = stage(root, P, 'esD_palco', cx, cy, W, D, 0.2, r=0.06)
    # saia de veludo com franja dourada na frente do palco
    box(root, 'esD_saia', (W - 0.04, 0.02, 0.15), (cx, cy - D / 2 - 0.008, G + 0.11), m=P['velvet'], bev=0.006, front=True)
    box(root, 'esD_franja', (W - 0.04, 0.024, 0.025), (cx, cy - D / 2 - 0.01, G + 0.185), m=P['trim'], bev=0.005, front=True)
    stairs(root, P, 'esD_degrau', 0.44, cy - D / 2, zt, w=0.24, n=2, run=0.08)
    # trelica: duas torres atras e a viga de cima com os holofotes que varrem e o varal de bandeirolas
    zb = 1.36
    for sx in (-1, 1):
        truss(root, P, f'esD_torre{sx}', (sx * 0.56, cy + 0.26, zt), (sx * 0.56, cy + 0.26, zb + 0.04))
        cyl(root, f'esD_sapata{sx}', 0.07, 0.02, (sx * 0.56, cy + 0.26, zt + 0.01), m=P['spot'], v=4, bev=0.004, rot=(0, 0, math.pi / 4))
    truss(root, P, 'esD_viga', (-0.62, cy + 0.26, zb), (0.62, cy + 0.26, zb))
    for k, (x, yaw, p0) in enumerate(((-0.32, math.radians(-70), 0.0), (0.0, math.radians(-90), 0.33), (0.32, math.radians(-110), 0.66))):
        spotlight(root, P, lights, f'esD_holofote{k}', (x, cy + 0.26, zb + 0.04), 0.06, yaw, pitch=0.75, s=0.8, tripod=False, ground=False, sweep=0.3, ph0=p0)
    bunting(root, P, 'esD_varal', (-0.56, cy + 0.2, zb - 0.06), (0.56, cy + 0.2, zb - 0.06), n=11, sag=0.12)
    # painel de veludo atras (o fundo do palanque) com o emblema da chapa dos dois lados do puxador
    slab(root, 'esD_painel', 1.0, 0.7, 0.03, P['velvet_d'], r=0.04, loc=(cx, cy + 0.3, zt + 0.42), bev=0.01)
    slab(root, 'esD_painelGalao', 1.04, 0.74, 0.02, P['trim'], r=0.05, loc=(cx, cy + 0.31, zt + 0.42), bev=0.006)
    for sx in (-1, 1):
        emblema(root, f'esD_painelEmblema{sx}', 0.22, 0.2, loc=(cx + sx * 0.27, cy + 0.3 - 0.019, zt + 0.56), depth=0.008)
    # caixas de som empilhadas nos cantos da frente
    for sx in (-1, 1):
        x = sx * 0.5
        speaker(root, P, f'esD_caixa{sx}a', x, cy - 0.18, zt, rz=-sx * 0.25, ph0=0.0)
        speaker(root, P, f'esD_caixa{sx}b', x, cy - 0.16, zt + 0.36, w=0.22, h=0.28, d=0.2, rz=-sx * 0.25, ph0=0.25)
    # pulpito com microfone atras, surdos dos lados do posto
    box(root, 'esD_pulpito', (0.22, 0.16, 0.36), (0.0, cy + 0.12, zt + 0.18), m=P['desk'], bev=0.014)
    box(root, 'esD_pulpitoTampo', (0.26, 0.2, 0.03), (0.0, cy + 0.1, zt + 0.37), rot=(0.25, 0, 0), m=P['desk_l'], bev=0.008)
    box(root, 'esD_pulpitoFaixa', (0.2, 0.012, 0.05), (0.0, cy + 0.035, zt + 0.26), m=P['trim'], bev=0.003)
    desk_mic(root, P, 'esD_micro', 0.0, cy + 0.06, zt + 0.38, s=0.9)
    surdo(root, P, 'esD_surdo1', -0.22, cy - 0.12, zt, r=0.11, h=0.18)
    surdo(root, P, 'esD_surdo2', 0.22, cy - 0.12, zt, r=0.1, h=0.17)
    return {'slots': [(0.0, cy - 0.12, zt)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (0.0, cy + 0.2, zb - 0.2)}}


# ---------------------------------------------------------------- Quebra de Sigilo: o cofre aberto, pastas saltando,
# o lacre rompido e a lupa enorme por cima
def folder(root, P, tag, loc, rot=(0, 0, 0), m=None, s=1.0, parent=None):
    """Pasta de processo (cartolina colorida) com papeis aparecendo por cima e o elastico."""
    m = m or mat('pasta_parda', '#e5be76', rough=0.75, var=0.04, bump=0.04)
    with grupo(root, tag, loc=loc, rot=rot, parent=parent) as e:
        slab(root, tag + '_capa', 0.17 * s, 0.22 * s, 0.03 * s, m, r=0.012 * s, bev=0.006 * s)
        slab(root, tag + '_papeis', 0.15 * s, 0.22 * s, 0.022 * s, P['paper'], r=0.008 * s, loc=(0.0, 0, 0.02 * s), bev=0.003 * s)
        slab(root, tag + '_aba', 0.06 * s, 0.04 * s, 0.03 * s, m, r=0.01 * s, loc=(-0.04 * s, 0, 0.12 * s), bev=0.004 * s)
        box(root, tag + '_elastico', (0.006 * s, 0.034 * s, 0.23 * s), (0.05 * s, 0, 0), m=mat('elastico_preto', '#2b2626', rough=0.6, var=0, bump=0), bev=0.002 * s)
    return e


def build_esW(P, root):
    plot(root, P, 'esW')
    lights = []
    safe = mat('cofre_verde', '#3f5c56', rough=0.32, metal=0.45, var=0.03, bump=0.02)
    safe_d = mat('cofre_verde_escuro', '#2c403c', rough=0.4, metal=0.35, var=0.03, bump=0.02)
    inner = cor('sec' if V_ else 'pri', rough=0.7, var=0.04, bump=0.05)   # forro do cofre na cor da chapa (V amarelo, R vermelho)
    cx, cy = -0.16, 0.18
    W, D, H = 0.62, 0.5, 0.86
    z0 = G + 0.06
    box(root, 'esW_pes', (W - 0.06, D - 0.06, 0.06), (cx, cy, G + 0.03), m=safe_d, bev=0.012)
    # tapete da chapa debaixo do cofre (veludo com galao claro), chato no chao: nao muda o contorno
    slab(root, 'esW_tapeteGalao', 0.9, 0.76, 0.008, P['trim'], r=0.05, loc=(cx - 0.02, cy - 0.03, G + 0.004), rot=(math.pi / 2, 0, 0), bev=0.002)
    slab(root, 'esW_tapete', 0.84, 0.7, 0.01, P['velvet'], r=0.04, loc=(cx - 0.02, cy - 0.03, G + 0.006), rot=(math.pi / 2, 0, 0), bev=0.003)
    # caixa do cofre aberta na frente: paredes, teto e fundo (dentro iluminado)
    t = 0.06
    box(root, 'esW_fundo', (W, t, H), (cx, cy + D / 2 - t / 2, z0 + H / 2), m=safe, bev=0.025)
    for sx in (-1, 1):
        box(root, f'esW_lado{sx}', (t, D, H), (cx + sx * (W / 2 - t / 2), cy, z0 + H / 2), m=safe, bev=0.025)
    box(root, 'esW_teto', (W, D, t), (cx, cy, z0 + H - t / 2), m=safe, bev=0.025)
    box(root, 'esW_chao', (W, D, t), (cx, cy, z0 + t / 2), m=safe, bev=0.02)
    box(root, 'esW_forro', (W - 2 * t, 0.01, H - 2 * t), (cx, cy + D / 2 - t - 0.006, z0 + H / 2), m=inner, bev=0.0)
    box(root, 'esW_moldura', (W + 0.02, 0.02, 0.03), (cx, cy - D / 2 - 0.005, z0 + H - 0.015), m=P['braid'], bev=0.005)
    # prateleira com pastas de pe e pilhas de dinheiro? nao: so pastas (e o sigilo)
    box(root, 'esW_prateleira', (W - 2 * t, D - 0.08, 0.02), (cx, cy + 0.02, z0 + H * 0.5), m=safe_d, bev=0.004)
    cols = [mat('pasta_parda', '#e5be76', rough=0.75, var=0.04, bump=0.04), mat('pasta_vermelha', '#c8463c', rough=0.75, var=0.04, bump=0.04),
            mat('pasta_azul', '#4a78b8', rough=0.75, var=0.04, bump=0.04)]
    for k in range(5):
        folder(root, P, f'esW_pastaPe{k}', (cx - 0.18 + 0.075 * k, cy + 0.04, z0 + H * 0.5 + 0.13), rot=(0, 0.12 * (k % 2) - 0.06, math.pi / 2 - 0.1),
               m=cols[k % 3], s=0.95)
    for k in range(3):
        folder(root, P, f'esW_pastaDeitada{k}', (cx + 0.02, cy + 0.04, z0 + t + 0.02 + 0.03 * k), rot=(math.pi / 2, 0, 0.2 * k), m=cols[(k + 1) % 3], s=1.05)
    # porta escancarada (dobradica na esquerda): a face de dentro fica para a camera, com os trincos, o volante e o
    # lacre vermelho rompido
    hinge = (cx - W / 2, cy - D / 2)
    with grupo(root, 'esW_porta', loc=(hinge[0], hinge[1], z0), rot=(0, 0, math.radians(-118))):
        box(root, 'esW_portaChapa', (W, 0.07, H - 0.02), (W / 2, -0.035, H / 2), m=safe, bev=0.025)
        box(root, 'esW_portaMiolo', (W - 0.12, 0.03, H - 0.14), (W / 2, 0.012, H / 2), m=safe_d, bev=0.01)
        for k in range(3):
            cyl(root, f'esW_trinco{k}', 0.02, 0.1, (W + 0.02, -0.03, 0.2 + 0.22 * k), rot=(0, math.pi / 2, 0), m=P['chrome'], v=12, bev=0.004)
        cyl(root, 'esW_volanteBase', 0.08, 0.02, (W / 2, 0.035, H * 0.55), rot=(math.pi / 2, 0, 0), m=P['chrome'], v=28, bev=0.006)
        for k in range(4):
            a = TAU * k / 4 + 0.3
            tube(root, f'esW_volanteRaio{k}', [(W / 2, 0.05, H * 0.55), (W / 2 + 0.13 * math.cos(a), 0.05, H * 0.55 + 0.13 * math.sin(a))], 0.012, P['braid'], segs=6)
            sphere(root, f'esW_volantePunho{k}', 0.022, (W / 2 + 0.13 * math.cos(a), 0.05, H * 0.55 + 0.13 * math.sin(a)), m=P['braid'], seg=10)
        cyl(root, 'esW_segredo', 0.05, 0.03, (W / 2, 0.04, H * 0.27), rot=(math.pi / 2, 0, 0), m=P['braid'], v=24, bev=0.006)
        sphere(root, 'esW_lacre', 0.042, (W * 0.86, 0.045, H * 0.76), scale=(1, 0.35, 1), m=P['seal_d'], seg=14)
        tube(root, 'esW_fitaLacre', [(W * 0.86, 0.04, H * 0.76), (W * 0.97, 0.04, H * 0.66), (W * 0.93, 0.04, H * 0.5)], 0.011, P['seal'], segs=5)
    # fita do lacre rompida pendurada na caixa
    tube(root, 'esW_fitaRompida', [(cx + W / 2 - 0.02, cy - D / 2 - 0.01, z0 + H * 0.72), (cx + W / 2 - 0.05, cy - D / 2 - 0.02, z0 + H * 0.6),
                                   (cx + W / 2 - 0.03, cy - D / 2 - 0.02, z0 + H * 0.5)], 0.01, P['seal'], segs=5)
    # bandeirinha da chapa espetada no teto do cofre (canto de tras, a esquerda)
    bandeira_chapa(root, 'esW_bandeira', (cx - W / 2 + 0.07, cy + D / 2 - 0.1, z0 + H), h=0.4, w=0.28, fh=0.18)
    # pastas saltando do cofre (cada uma no seu tempo, girando)
    for k, (dx, dz, rz) in enumerate(((-0.12, 0.62, 0.4), (0.05, 0.86, -0.3), (0.2, 0.7, 0.2))):
        f = folder(root, P, f'esW_pastaVoando{k}', (cx + dx, cy - 0.12, z0 + dz), rot=(0.3, 0.4 * (k - 1), rz), m=cols[k], s=1.0)

        def hop(o, mb, ph, p0=0.33 * k):
            a = TAU * (ph + p0)
            o.matrix_basis = Matrix.Translation((0, 0, 0.06 * math.sin(a))) @ mb @ Matrix.Rotation(0.25 * math.sin(a + 0.8), 4, 'Y')
        register_anim(f, hop)
    for k, (x, y, rz) in enumerate(((0.12, -0.38, 0.4), (0.3, -0.24, -0.5), (-0.5, -0.36, 1.2), (0.02, -0.56, -0.2))):
        box(root, f'esW_papelChao{k}', (0.12, 0.16, 0.005), (x, y, G + 0.003), rot=(0, 0, rz), m=P['paper'], bev=0.001)
    folder(root, P, 'esW_pastaChao', (-0.44, -0.18, G + 0.016), rot=(math.pi / 2, 0, 0.7), m=cols[1], s=1.05)
    # luz dourada saindo de dentro do cofre
    sphere(root, 'esW_brilho', 0.03, (cx, cy + 0.12, z0 + H - t - 0.035), m=P['glow'], seg=12)
    lights.append(((cx, cy - 0.05, z0 + H * 0.7), '#ffd88a', 14.0, 1))
    # holofote apontado para o cofre
    spotlight(root, P, lights, 'esW_holofote', (-0.6, -0.3, G), 0.66, math.radians(60), pitch=0.45, s=0.9)
    # lupa enorme num braco articulado, por cima e na frente do cofre
    x0, y0 = 0.5, 0.2
    cyl(root, 'esW_lupaBase', 0.14, 0.05, (x0, y0, G + 0.025), r2=0.11, m=P['spot'], v=24, bev=0.014)
    tube(root, 'esW_lupaBraco1', [(x0, y0, G + 0.05), (x0 - 0.02, y0, G + 0.86)], 0.024, P['chrome'], segs=10)
    sphere(root, 'esW_lupaJunta', 0.04, (x0 - 0.02, y0, G + 0.88), m=P['spot'], seg=14)
    tube(root, 'esW_lupaBraco2', [(x0 - 0.02, y0, G + 0.88), (x0 - 0.3, y0 - 0.16, G + 1.1)], 0.02, P['chrome'], segs=10)
    piv, lc = magnifier(root, P, 'esW_lupa', (x0 - 0.3, y0 - 0.16, G + 1.1), 0.0, R=0.3, yaw=math.radians(-10), rock=0.2, stand=False)
    return {'slots': [(0.42, -0.5, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- tripulacao da comissao
def suit_mat(key, hexcol):
    return mat('terno_' + key, hexcol, rough=0.7, var=0.03, bump=0.06, sheen=0.3)


def broche(root, pr, tag, loc=(0.078, -0.047, 0.43), rz=1.24, s=0.04):
    """Broche da chapa na lapela, do lado que a camera ve (filho do corpo, que olha para +X local; rz vira o broche
    para a normal do paleto): V = bandeirinha (placa verde com losango amarelo e circulo azul), R = estrela branca."""
    body = pr['body']
    if not V_:
        return estrela_peito(root, tag + '_broche', body, loc, r=s * 0.5, rot=(0, 0, rz))
    pl = box(root, tag + '_brochePlaca', (s, 0.006, s * 0.72), (0, 0, 0), m=cor('pri', rough=0.5), bev=0.002)
    pl.parent = body
    pl.location = loc
    pl.rotation_euler = (0, 0, rz)
    out = [pl]
    for o in emblema(root, tag + '_broche', s, s * 0.72, depth=0.004):
        if o.parent == root:
            o.parent = pl
            o.location = (0, -0.004, 0)
        out.append(o)
    return out


def estrela_camiseta(root, pr, tag, x=0.086, z=0.4, r=0.032):
    """Chapa R: estrela branca no peito da camiseta. A chapa V nao leva nada: a camisa amarela com gola verde ja e a
    da selecao."""
    if not V_:
        return estrela_peito(root, tag, pr['body'], (x, 0.0, z), r=r, rot=(0, 0, math.pi / 2))
    return []


def red_folder(root, P, tag):
    """Relatorio da CPI: pasta grossa (capa clara da chapa, ao longo do Z local, empunhadura embaixo)."""
    return [box(root, tag + '_relatorio', (0.03, 0.12, 0.16), (0, 0, 0.06), m=P['folder'], bev=0.006),
            box(root, tag + '_relatorioPapel', (0.024, 0.11, 0.15), (0.0, 0.006, 0.065), m=P['paper'], bev=0.003),
            box(root, tag + '_relatorioGalao', (0.034, 0.124, 0.014), (0, 0, 0.1), m=P['braid'], bev=0.002)]


def hand_mic(root, P, tag):
    """Microfone de mao (cabo preto, globo cromado em cima)."""
    return [tube(root, tag + '_micCabo', [(0, 0, -0.03), (0, 0, 0.08)], 0.013, P['mic'], segs=10, rfun=lambda t: 0.011 + 0.006 * t),
            sphere(root, tag + '_micGlobo', 0.025, (0, 0, 0.1), m=P['chrome'], seg=14),
            torus(root, tag + '_micAnel', (0, 0, 0.082), 0.018, 0.004, P['velvet'], n=12, segs=4)]


def gavel(root, P, tag):
    """Martelo de presidente de comissao: cabo de madeira, cabeca atravessada com aneis dourados."""
    return [tube(root, tag + '_martCabo', [(0, 0, -0.03), (0, 0, 0.12)], 0.009, P['desk'], segs=8),
            cyl(root, tag + '_martCabeca', 0.026, 0.11, (0, 0, 0.13), rot=(math.pi / 2, 0, 0), m=P['desk_d'], v=16, bev=0.006),
            torus(root, tag + '_martAnel1', (0, 0.03, 0.13), 0.027, 0.004, P['braid'], axis='Y', n=14, segs=4),
            torus(root, tag + '_martAnel2', (0, -0.03, 0.13), 0.027, 0.004, P['braid'], axis='Y', n=14, segs=4)]


def mallet(root, P, tag, side):
    return [tube(root, f'{tag}_baqueta{side}', [(0, 0, -0.04), (0, 0, 0.2)], 0.011, P['desk_d'], segs=6),
            sphere(root, f'{tag}_baquetaPonta{side}', 0.03, (0, 0, 0.22), m=P['paper'], seg=12)]


def hand_lens(root, P, tag):
    """Lupa de mao: cabo de madeira para baixo, aro cromado de frente (olha atraves dela)."""
    return [tube(root, tag + '_lupaCabo', [(0, 0, -0.03), (0, 0, 0.07)], 0.012, P['handle'], segs=8),
            torus(root, tag + '_lupaAro', (0, 0, 0.13), 0.05, 0.009, P['chrome'], axis='X', n=24, segs=6),
            cyl(root, tag + '_lupaLente', 0.046, 0.006, (0, 0, 0.13), rot=(0, math.pi / 2, 0), m=P['lens'], v=24, bev=0.0)]


def hair_bun(root, pr, tag, m):
    o = blob(root, tag + '_coque', 0.032, HC + Vector((-0.05, 0, 0.06)), (1, 1, 0.9), m)
    o.parent = pr['head']
    return o


def build_relatora(P, root):
    """Relatora: blazer da chapa (V verde, R vermelho), coque, colar de perolas, broche e o relatorio na mao esquerda."""
    tag = root['set']
    blazer = cor('pri', rough=0.7, var=0.03, bump=0.06, sheen=0.3)
    skirt = suit_mat('saia_grafite', '#3b3f48')
    hair = mat('cabelo_relatora', '#3a2414', rough=0.7, var=0.03, bump=0.25)
    pr = build_person(P, root, tag, dict(tunic=blazer, head='hair', hair_m=hair, belt=None, skirt_m=skirt, pants=mat('meia_cpi', '#c98d5e', rough=0.7, var=0, bump=0.02),
                                         boot_m=shoes(), boot_cuff=skirt, sleeve=blazer, bare_hands=True))
    hair_bun(root, pr, tag, hair)
    for k in range(7):
        a = math.radians(-60 + 20 * k)
        o = sphere(root, f'{tag}_perola{k}', 0.008, (0.055 * math.cos(a) + 0.01, 0.06 * math.sin(a), 0.468 - 0.01 * math.cos(a * 1.5)), m=P['paper'], seg=8)
        o.parent = pr['body']
    broche(root, pr, tag, loc=(0.08, -0.047, 0.415))
    hold(pr, 'L', *red_folder(root, P, tag))
    return pr


def build_presidente(P, root):
    """Presidente da CPI: terno azul-marinho, gravata da chapa (V amarela, R vermelha), broche, oculos e cabelo
    grisalho; o microfone de mao."""
    tag = root['set']
    s_ = suit_mat('marinho_cpi', '#243154')
    grey = mat('cabelo_grisalho_cpi', '#b9b2a6', rough=0.7, var=0.02, bump=0.25)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=grey, brow_m=grey, belt=None, skirt_m=s_, pants=s_, boot_m=shoes(), boot_cuff=s_,
                                         sleeve=s_, bracer=s_, bare_hands=True))
    tie(root, pr, tag, cor('sec' if V_ else 'pri', rough=0.6, sheen=0.3), knot=cor('sec' if V_ else 'escuro', rough=0.6, sheen=0.3))
    broche(root, pr, tag)
    glasses(root, pr, tag)
    hold(pr, 'R', *hand_mic(root, P, tag))
    return pr


def build_senador(P, root):
    """Senador veterano: terno grafite, barba branca, gravata da chapa (V verde, R vermelha), broche e o martelo da
    comissao."""
    tag = root['set']
    s_ = suit_mat('grafite_cpi', '#41454f')
    white = mat('cabelo_branco_cpi', '#e6e0d4', rough=0.7, var=0.02, bump=0.25)
    pr = build_person(P, root, tag, dict(tunic=s_, head='hair', hair_m=white, beard=white, brow_m=white, belt=None, skirt_m=s_, pants=s_, boot_m=shoes(),
                                         boot_cuff=s_, sleeve=s_, bracer=s_, bare_hands=True, sash=None))
    tie(root, pr, tag, cor('pri', rough=0.6, sheen=0.3))
    broche(root, pr, tag)
    hold(pr, 'R', *gavel(root, P, tag))
    return pr


def build_batuqueiro(P, root):
    """Puxador da batucada do palanque: camiseta e bone da chapa (V camisa amarela da selecao com lenco verde e bone
    verde; R camiseta vermelha com estrela branca, lenco branco e bone vermelho), duas baquetas de surdo."""
    tag = root['set']
    tee = cor('camisa')
    jeans = cor('calca')
    cap = cor('bone')
    pr = build_person(P, root, tag, dict(tunic=tee, head='cap', head_m=cap, belt=mat('cinto_cpi', '#3a2a22', rough=0.6, var=0, bump=0.04),
                                         skirt_m=jeans, pants=jeans, boot_m=mat('tenis_cpi', '#f4f4f0', rough=0.5, var=0, bump=0.02), boot_cuff=jeans,
                                         sleeve=tee, bracer=cor('gola'), bare_hands=True, scarf=cor('gola'), big=1.06))
    estrela_camiseta(root, pr, tag)
    o = cyl(root, tag + '_boneAba', 0.06, 0.01, (0, 0, 0), m=cap, v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.18, 0)
    for side in 'LR':
        hold(pr, side, *mallet(root, P, tag, side))
    return pr


def build_perito(P, root):
    """Perito: capa de chuva bege, chapeu de feltro marrom com a fita da chapa, broche e a lupa de mao."""
    tag = root['set']
    coat = mat('capa_perito', '#c9a96e', rough=0.8, var=0.03, bump=0.08, sheen=0.3)
    felt = mat('chapeu_feltro', '#5a3b26', rough=0.75, var=0.02, bump=0.08)
    pr = build_person(P, root, tag, dict(tunic=coat, head='hair', hair_m=mat('cabelo_perito', '#2e1d12', rough=0.7, var=0.03, bump=0.25),
                                         belt=mat('cinto_capa', '#a8884e', rough=0.8, var=0, bump=0.06), skirt_m=coat, pants=suit_mat('calca_perito', '#3b3f48'),
                                         boot_m=shoes(mat('sapato_marrom_cpi', '#4a2a18', rough=0.35, var=0, bump=0.02)), sleeve=coat, bare_hands=True,
                                         scarf=None))
    aba = cyl(root, tag + '_chapeuAba', 0.1, 0.012, (0, 0, 0), m=felt, v=24, bev=0.004)
    copa = lathe(root, tag + '_chapeuCopa', [(0.0, 0.066, 0.066), (0.04, 0.062, 0.062), (0.06, 0.05, 0.05), (0.065, 0.0, 0.0)], felt, segs=18, lv=1)
    fita = torus(root, tag + '_chapeuFita', (0, 0, 0.012), 0.066, 0.01, cor('pri', rough=0.6), n=18, segs=5)
    for o in (aba, copa, fita):
        o.parent = pr['head']
        o.location = HC + Vector((0.0, 0, 0.052))
    aba.rotation_euler = (0, -0.25, 0)
    broche(root, pr, tag)
    hold(pr, 'R', *hand_lens(root, P, tag))
    return pr


IDLE_N, ACT_N = 12, 8


def relatora_state(mode, f):
    """idle: segura o relatorio junto ao peito; act: ergue o relatorio (apresenta a conclusao)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.12, 0.08, 0.36 + 0.01 * s), grip_L=(0.2, 0.0, 1.0), hand_R=(0.06, -0.13, 0.28), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_L=(0.12 + 0.04 * k, 0.1, 0.36 + 0.24 * k), grip_L=(0.2, 0.0, 1.0), hand_R=(0.1, -0.12, 0.3 + 0.08 * k), head_pitch=-0.25 * k, ph=f / ACT_N)


def presidente_state(mode, f):
    """idle: microfone na mao, gesticulando de leve; act: leva o microfone a boca e discursa."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.12, 0.32), grip_R=(0.3, -0.2, 1.0), hand_L=(0.1, 0.13, 0.3 + 0.03 * s), breathe=s,
                    head_yaw=0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.1, ph=ph)
    k = math.sin(math.pi * min(1.0, f / 3))
    return dict(hand_R=(0.1 + 0.03 * k, -0.04, 0.4 + 0.1 * k), grip_R=(0.8, 0.0, 0.6 + 0.4 * k), hand_L=(0.16 + 0.04 * k, 0.16, 0.42 + 0.12 * k),
                head_pitch=-0.15 * k, breathe=0.6 * k, ph=f / ACT_N)


def senador_state(mode, f):
    """idle: martelo na mao, na altura do peito; act: ergue o martelo e bate (ordem na sessao!)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.14, -0.1, 0.36 + 0.01 * s), grip_R=(0.2, 0.0, 1.0), hand_L=(0.08, 0.1, 0.3), breathe=s,
                    head_yaw=0.2 * math.sin(TAU * ph), head_pitch=-0.1, ph=ph)
    up = [0.3, 0.7, 1.0, 1.0, 0.2, 0.0, 0.0, 0.1][f]
    return dict(hand_R=(0.12 + 0.06 * up, -0.14 - 0.05 * up, 0.32 + 0.32 * up), grip_R=(0.3 - 0.6 * up, -0.35 * up, 1.0), hand_L=(0.12, 0.12, 0.34),
                head_pitch=-0.25 * up + 0.1 * (1 - up), lean=0.06 * (1 - up), ph=f / ACT_N)


def batuqueiro_state(mode, f):
    """idle: batida lenta (alternando as maos); act: batida rapida."""
    n = IDLE_N if mode == 'idle' else ACT_N
    ph = f / n
    k = 2 if mode == 'act' else 1
    l = 0.5 + 0.5 * math.sin(TAU * k * ph)
    r = 0.5 + 0.5 * math.sin(TAU * k * ph + math.pi)
    return dict(hand_L=(0.2, 0.12, 0.32 + 0.22 * l), grip_L=(1.0, 0.0, 0.4 - 1.2 * (1 - l)), hand_R=(0.2, -0.12, 0.32 + 0.22 * r),
                grip_R=(1.0, 0.0, 0.4 - 1.2 * (1 - r)), lean=0.12, head_pitch=-0.1, breathe=0.5 * math.sin(TAU * ph), ph=ph,
                pole_L=(-0.3, 1.0, -0.2), pole_R=(-0.3, -1.0, -0.2))


def perito_state(mode, f):
    """Olha pela lupa de mao, varrendo devagar de um lado para o outro."""
    ph = f / (IDLE_N if mode == 'idle' else ACT_N)
    look = math.sin(TAU * ph)
    return dict(hand_R=(0.2, -0.04 + 0.03 * look, 0.52), grip_R=(0.15, 0.25 * look, 1.0), hand_L=(0.08, 0.12, 0.32 + 0.02 * look),
                head_yaw=0.25 * look, head_pitch=0.05, lean=0.1, breathe=0.5 * math.sin(TAU * ph), ph=ph)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 2, 'act'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'es1': 'esP', 'es2': 'esC', 'es3': 'esA', 'esD': 'esT', 'esW': 'esV'},
    'towers': [('es1', 'CPI N1', build_es1), ('es2', 'CPI N2', build_es2), ('es3', 'CPI N3', build_es3),
               ('esD', 'Palanque da CPI', build_esD), ('esW', 'Quebra de Sigilo', build_esW)],
    'crews': [crew('esP', 'Relatora', build_relatora, relatora_state), crew('esC', 'Presidente da CPI', build_presidente, presidente_state),
              crew('esA', 'Senador veterano', build_senador, senador_state), crew('esT', 'Puxador da batucada', build_batuqueiro, batuqueiro_state),
              crew('esV', 'Perito', build_perito, perito_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
