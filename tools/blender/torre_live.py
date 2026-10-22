"""Live do Cercadinho (Estandarte da chapa V, Ninguem Sobe a Rampa): niveis 1 a 3, Live de Quinta e Camera da Live.
Piada com o cercadinho do Alvorada (a grade baixa onde a turma se juntava) e as lives semanais: grade de contencao
galvanizada com torcedores da chapa V atras (camisa amarela da selecao, bone verde, bandeirinha na mao, pulando), o
celular no tripe com o ring light gigante, o pulpito com o emblema da chapa e os paineis de LED. Tudo sem texto.
Troca so a arte da chapa V da CPI: nomes de conjuntos, postos, pontos, luzes e modos sao os mesmos do
tools/blender/torre_estandarte.py (js/sprites.js depende deles). A chapa R continua com a CPI (arte/render_r).

  es1..es3  o cercadinho cresce: grade, torcedores, pulpito, ring light com o celular (o ponto 'top' e o centro do anel)
  esD       Live de Quinta: palco-estudio com a bancada (camada da frente), o ring light com o celular apontado para o
            apresentador, o painel-bandeira da chapa no fundo, o interprete de Libras e as curtidas subindo
  esW       Camera da Live: grua alta com o ring light e a camera na ponta varrendo (no lugar da lupa), o monitor da
            live aceso e a turma acenando atras da grade
  esP/esC/esA/esT/esV  torcedora da bandeirinha, torcedor da selfie, veterano do bandeirao, apresentador da live,
            cinegrafista do gimbal

  CHAPA=V Blender -b -P tools/blender/torre_live.py -- render arte/render/estandarte [conjuntos...]
  Blender -b -P tools/blender/torre_live.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_live.py -- crew <arquivo.png> [amostras] [show|pose0]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, G   # noqa: F811 - lote de concreto de Brasilia
from pecas_zcv import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, star_pts, emblema, bandeirinha, estrela_peito   # cores da chapa

FRONT = -math.pi / 2
FAM = 'estandarte'

import lib as _lib
_orig_palette2 = palette2

V_ = CHAPA == 'V'
VELUDO = dict(rough=0.88, var=0.03, bump=0.1, sheen=0.9)
BANDEIRA = dict(rough=0.8, var=0.0, bump=0.04, sheen=0.4)


def palette2():   # noqa: F811 - grade galvanizada, ring light, celulares, madeira do pulpito e as cores da chapa
    P = _orig_palette2()
    P['velvet'] = cor('pri', **VELUDO)        # carpete, passadeira, saia do palco
    P['velvet_d'] = cor('escuro', **VELUDO)
    P['teal'] = P['velvet']
    P['trim'] = cor('sec', rough=0.45, var=0.02, bump=0.03, sheen=0.3)   # galao e frisos amarelos
    P['braid'] = mat('galao_ouro', '#e2b23f', rough=0.42, metal=0.35, var=0.02, bump=0.03)
    P['desk'] = mat('mesa_live', '#a8683a', rough=0.5, var=0.05, bump=0.06)
    P['desk_l'] = mat('mesa_live_tampo', '#c58652', rough=0.42, var=0.04, bump=0.04)
    P['desk_d'] = mat('mesa_live_painel', '#86502a', rough=0.55, var=0.05, bump=0.06)
    P['stage'] = mat('tablado_live', '#9a5e34', rough=0.6, var=0.08, bump=0.12)
    P['stage_d'] = mat('tablado_live_escuro', '#7b4825', rough=0.65, var=0.08, bump=0.12)
    P['mic'] = mat('microfone_preto', '#2a2a2f', rough=0.55, var=0.0, bump=0.08)
    P['chrome'] = mat('cromado_live', '#d7dce0', rough=0.18, metal=0.9, var=0.02, bump=0.0)
    P['spot'] = mat('tripe_grafite', '#3f434b', rough=0.4, metal=0.4, var=0.03, bump=0.02)
    P['fence'] = mat('grade_galvanizada', '#bfc6cc', rough=0.32, metal=0.75, var=0.03, bump=0.01)
    P['ring'] = glow_mat('ring_light', '#fffbf0', 2.4, 11.0, rough=0.3, var=0.0, bump=0.0)
    P['screen'] = glow_mat('tela_live', '#e9f4ff', 1.1, 7.0, rough=0.25, var=0.0, bump=0.0)
    P['onair'] = glow_mat('luz_ao_vivo', '#ff3b3b', 2.0, 9.0, rough=0.3, var=0.0, bump=0.0)
    P['phone'] = mat('celular_preto', '#1f2126', rough=0.3, metal=0.3, var=0.0, bump=0.0)
    P['case'] = cor('pri', rough=0.5)          # capinha verde da chapa
    P['paper'] = mat('papel_live', '#fbf6ea', rough=0.8, var=0.02, bump=0.02)
    P['heart_a'] = mat('curtida_amarela', '#ffcf24', rough=0.35, var=0.0, bump=0.0, emit=0.25)
    P['heart_b'] = mat('curtida_verde', '#2bb35c', rough=0.35, var=0.0, bump=0.0, emit=0.2)
    P['heart_c'] = mat('curtida_vermelha', '#ff4d5e', rough=0.35, var=0.0, bump=0.0, emit=0.25)
    P['heart_w'] = mat('curtida_branca', '#fff6f0', rough=0.35, var=0.0, bump=0.0, emit=0.2)
    P['flag_g'] = cor('pri', **BANDEIRA)
    P['flag_y'] = cor('sec', **BANDEIRA)
    P['flag_b'] = cor('ter', **BANDEIRA)
    P['camisa'], P['calca'], P['bone'], P['gola'] = cor('camisa'), cor('calca'), cor('bone'), cor('gola')
    P['sneaker'] = mat('tenis_branco_live', '#f4f4f0', rough=0.5, var=0.0, bump=0.02)
    P['conc'] = concrete()
    P['_emblem'] = 'sun'
    return P


_lib.palette2 = palette2


# ---------------------------------------------------------------- bandeiras
def flag_mesh(root, P, tag, w, fh, front=False):
    """Pano da bandeira da chapa (x de 0 a w, z de 0 a -fh), com o losango amarelo e o circulo azul dos dois lados
    (R: estrela branca), tremulando (cloth)."""
    o = cloth_grid(root, tag, w, fh, 12, 6, [P['flag_g'], P['flag_y'], P['flag_b']], thick=0.008, front=front)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for yy in (-0.008, 0.008):
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
    return o


def br_flag(root, P, tag, x, y, z0, h, w=0.36, front=False):
    """Mastro com a bandeira da chapa, tremulando."""
    tube(root, tag + '_mastro', [(x, y, z0), (x, y, z0 + h)], 0.014, P['chrome'], segs=8, front=front)
    sphere(root, tag + '_ponta', 0.026, (x, y, z0 + h + 0.02), m=P['braid'], seg=12, front=front)
    cyl(root, tag + '_base', 0.06, 0.04, (x, y, z0 + 0.02), r2=0.045, m=P['spot'], v=16, bev=0.01, front=front)
    o = flag_mesh(root, P, tag, w, w * 0.7, front=front)
    o.location = (x + 0.012, y, z0 + h - 0.02)
    register_cloth(o, flag_wave(w, amp=0.05, cycles=1, waves=1.1))
    return o


def hand_flag(root, P, tag, stick=0.3, w=0.16, fh=0.11):
    """Bandeirinha de mao: palito e o pano da chapa no alto (empunhadura em z = 0, ao longo de Z). Devolve
    (objetos, pano) - o pano vai para parts['cloth'] para tremular na pose."""
    st = tube(root, tag + '_palito', [(0, 0, -0.05), (0, 0, stick)], 0.006, P['desk_l'], segs=6)
    o = flag_mesh(root, P, tag + '_pano', w, fh)
    o.location = (0.004, 0, stick - 0.005)
    register_cloth(o, flag_wave(w, amp=0.035, cycles=1, waves=1.0))
    return [st, o], o


# ---------------------------------------------------------------- tablado, escada, pulpito, microfone
def stage(root, P, tag, cx, cy, w, d, h, z0=G, carpet=True, r=0.08):
    """Tablado de madeira com tabuas marcadas na frente, carpete verde por cima com galao amarelo. Devolve o topo."""
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
    """Degraus de madeira descendo para a frente (-Y) a partir da borda y0, com a passadeira verde."""
    dz = (z_top - z0) / (n + 1)
    for k in range(n):
        zt = z_top - dz * (k + 1)
        yc = y0 - run * (k + 0.5)
        box(root, f'{tag}{k}', (w, run + 0.01, zt - z0), (x, yc, (zt + z0) / 2), m=P['stage'], bev=0.012)
        box(root, f'{tag}{k}_passadeira', (w * 0.7, run + 0.012, 0.014), (x, yc, zt + 0.005), m=P['velvet'], bev=0.004)
    for k in range(n + 1):
        zt = z_top - dz * k
        yc = y0 - run * k
        box(root, f'{tag}{k}_espelho', (w * 0.7, 0.012, dz), (x, yc - 0.004, zt - dz / 2), m=P['velvet'], bev=0.003)


def desk_mic(root, P, tag, x, y, z, yaw=0.0, s=1.0, front=False):
    """Microfone de mesa (pescoco de ganso) com a luzinha vermelha de 'no ar'."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, yaw)) as e:
        cyl(root, tag + '_base', 0.045 * s, 0.022 * s, (0, 0, 0.011 * s), r2=0.038 * s, m=P['mic'], v=18, bev=0.006, front=front)
        sphere(root, tag + '_luz', 0.008 * s, (0.0, -0.04 * s, 0.018 * s), m=P['onair'], seg=8, front=front)
        tube(root, tag + '_pescoco', [(0, 0, 0.02 * s), (0, -0.01 * s, 0.1 * s), (0, -0.04 * s, 0.16 * s), (0, -0.08 * s, 0.18 * s)], 0.008 * s, P['chrome'], segs=6, front=front)
        sphere(root, tag + '_cabeca', 0.024 * s, (0, -0.1 * s, 0.18 * s), scale=(1, 1.35, 1), m=P['mic'], seg=12, rot=(0.5, 0, 0), front=front)
    return e


def pulpito(root, P, tag, x, y, z, s=1.0, rz=0.0, mic=True, front=False):
    """Pulpito de madeira com o painel verde do emblema da chapa na frente e o microfone de ganso em cima."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rz)) as e:
        cyl(root, tag + '_pe', 0.15 * s, 0.03 * s, (0, 0.02 * s, 0.015 * s), m=P['desk_d'], v=4, bev=0.008, rot=(0, 0, math.pi / 4), front=front).scale = (1.25, 0.8, 1)
        box(root, tag + '_corpo', (0.24 * s, 0.16 * s, 0.4 * s), (0, 0.02 * s, 0.2 * s + 0.02 * s), m=P['desk'], bev=0.016 * s, front=front)
        box(root, tag + '_tampo', (0.28 * s, 0.2 * s, 0.03 * s), (0, 0.0, 0.45 * s), rot=(0.28, 0, 0), m=P['desk_l'], bev=0.008 * s, front=front)
        box(root, tag + '_painel', (0.19 * s, 0.012 * s, 0.24 * s), (0, -0.064 * s, 0.24 * s), m=P['velvet'], bev=0.006 * s, front=front)
        box(root, tag + '_painelGalao', (0.21 * s, 0.008 * s, 0.26 * s), (0, -0.059 * s, 0.24 * s), m=P['trim'], bev=0.004 * s, front=front)
        for o in emblema(root, tag + '_emblema', 0.17 * s, 0.15 * s, loc=(0, -0.073 * s, 0.25 * s), depth=0.008 * s):
            if front:
                o['front'] = 1
    if mic:
        desk_mic(root, P, tag + '_micro', x, y + 0.03 * s, z + 0.46 * s, yaw=rz, s=0.85 * s, front=front)
    return e


# ---------------------------------------------------------------- grade do cercadinho e a turma atras dela
def grade(root, P, tag, p0, p1, h=0.27, z0=G, front=False, faixa=False):
    """Grade de contencao (cercadinho): quadro de tubo galvanizado, barras verticais e os pes chatos; faixa=True
    amarra uma faixinha verde com o emblema da chapa (sem texto)."""
    a, b = Vector((p0[0], p0[1], z0)), Vector((p1[0], p1[1], z0))
    d = b - a
    L = d.length
    ang = math.atan2(d.y, d.x)
    with grupo(root, tag, loc=a, rot=(0, 0, ang)) as e:
        zb, zt = 0.05, h
        tube(root, tag + '_quadro', [(0.02, 0, zb), (0.02, 0, zt), (L - 0.02, 0, zt), (L - 0.02, 0, zb), (0.02, 0, zb)], 0.012, P['fence'], segs=8, front=front)
        n = max(2, int(L / 0.055))
        for i in range(1, n):
            x = 0.02 + (L - 0.04) * i / n
            tube(root, f'{tag}_barra{i}', [(x, 0, zb), (x, 0, zt)], 0.0055, P['fence'], segs=5, front=front)
        for k, x in enumerate((0.06, L - 0.06)):
            box(root, f'{tag}_pe{k}', (0.03, 0.17, 0.012), (x, 0, 0.006), m=P['fence'], bev=0.004, front=front)
            tube(root, f'{tag}_perna{k}', [(x, 0, 0.012), (x, 0, zb)], 0.01, P['fence'], segs=6, front=front)
        if faixa:
            fw, fhh = min(0.3, L * 0.6), 0.12
            slab(root, tag + '_faixa', fw, fhh, 0.008, P['velvet'], r=0.01, loc=(L / 2, -0.016, zt - fhh / 2 - 0.015), bev=0.003, front=front)
            for o in emblema(root, tag + '_faixaEmb', fw * 0.55, fhh * 0.9, loc=(L / 2, -0.022, zt - fhh / 2 - 0.015), depth=0.005):
                if front:
                    o['front'] = 1
            for sx in (-1, 1):
                torus(root, f'{tag}_amarra{sx}', (L / 2 + sx * fw * 0.45, -0.012, zt - 0.012), 0.014, 0.004, P['paper'], axis='X', n=10, segs=4, front=front)
    return e


SKINS = [('pele', '#c98d5e'), ('pele_clara', '#e2b08a'), ('pele_escura', '#8a5634')]


def torcedor_sp(P, kind=0):
    """Figurino da turma da chapa V: camisa amarela da selecao, calcao azul, perna de fora, meiao e tenis brancos;
    kind 0 = bone verde, 1 = cabelo preso (coque), 2 = grisalho."""
    sk = mat(*SKINS[kind % 3], rough=0.7, var=0.05, bump=0.02)
    sp = dict(tunic=P['camisa'], skirt_m=P['calca'], belt=None, pants=sk, skin=sk, boot_m=P['sneaker'], boot_cuff=P['sneaker'],
              bare_hands=True, bracer=sk)
    if kind == 0:
        sp.update(head='cap', head_m=P['bone'])
    elif kind == 1:
        sp.update(head='hair', hair_m=mat('cabelo_torcedora', '#3a2414', rough=0.7, var=0.03, bump=0.25), topknot=True)
    else:
        grey = mat('cabelo_grisalho_live', '#c9c2b6', rough=0.7, var=0.02, bump=0.25)
        sp.update(head='hair', hair_m=grey, brow_m=grey)
    return sp


def vestir_torcedor(root, P, pr, tag, kind):
    """Gola verde da camisa e a aba do bone."""
    marca_peito(root, pr, tag)
    if kind == 0:
        o = cyl(root, tag + '_boneAba', 0.06, 0.01, (0, 0, 0), m=P['bone'], v=18, bev=0.003)
        o.parent = pr['head']
        o.location = HC + Vector((0.07, 0, 0.045))
        o.scale = (1.15, 0.95, 1)
        o.rotation_euler = (0, -0.18, 0)


def apoiador(P, root, tag, loc, face=-0.5, s=1.0, ph0=0.0, kind=0, pose=0, jump=0.03):
    """Torcedor parado da torre (nao e tripulacao): veste, faz a pose (bandeirinha erguida, braco no ar), vira um
    grupo so e pula no loop, com a bandeirinha tremulando. face = para onde olha (radianos, mundo)."""
    pr = build_person(P, root, tag, torcedor_sp(P, kind))
    vestir_torcedor(root, P, pr, tag, kind)
    objs, cl = hand_flag(root, P, tag + '_bandeirinha')
    hold(pr, 'L' if pose != 2 else 'R', *objs)
    poses = [dict(hand_L=(0.1, 0.14, 0.64), grip_L=(0.1, 0.1, 1.0), hand_R=(0.16, -0.12, 0.5), pole_R=(-0.3, -1.0, -0.2)),
             dict(hand_L=(0.16, 0.12, 0.5), grip_L=(0.4, 0.2, 1.0), hand_R=(0.08, -0.15, 0.62), pole_R=(-0.3, -1.0, -0.2)),
             dict(hand_R=(0.12, -0.14, 0.64), grip_R=(0.1, -0.1, 1.0), hand_L=(0.14, 0.13, 0.36))]
    st = dict(poses[pose % 3])
    st.update(breathe=0.4, head_pitch=-0.12, head_yaw=0.15, ph=ph0)
    pose_person(pr, P, root, st)
    g = empty(root, tag + '_grupo')
    for o in list(root.children):
        if o is not g and o.name.startswith(tag + '_'):
            o.parent = g
    g.location = (loc[0], loc[1], loc[2] if len(loc) > 2 else G)
    g.rotation_euler = (0, 0, face - PERSON_FACE)
    g.scale = (s, s, s)

    def fn(o, mb, ph, p0=ph0):
        a = TAU * (2 * ph + p0)
        o.matrix_basis = Matrix.Translation((0, 0, jump * abs(math.sin(a / 2)))) @ mb @ Matrix.Rotation(0.05 * math.sin(a / 2), 4, 'Y')
    register_anim(g, fn)
    return g


# ---------------------------------------------------------------- ring light, celular, painel de LED
def celular(root, P, tag, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, parent=None, front=False, screen=True):
    """Celular em pe (retrato) voltado para -Y local: capinha verde da chapa atras, tela acesa na frente com a
    bolinha vermelha de 'ao vivo' e o coracaozinho; as lentes na capinha."""
    with grupo(root, tag, loc=loc, rot=rot, parent=parent) as e:
        slab(root, tag + '_capa', 0.085 * s, 0.16 * s, 0.018 * s, P['case'], r=0.016 * s, bev=0.005 * s, front=front)
        if screen:
            slab(root, tag + '_tela', 0.072 * s, 0.144 * s, 0.006 * s, P['screen'], r=0.011 * s, loc=(0, -0.01 * s, 0), bev=0.002 * s, front=front)
            sphere(root, tag + '_aoVivo', 0.008 * s, (-0.022 * s, -0.014 * s, 0.056 * s), scale=(1, 0.4, 1), m=P['onair'], seg=8, front=front)
            for k, (dx, dz) in enumerate(((0.016, -0.05), (0.024, -0.03))):
                sphere(root, f'{tag}_coracaoTela{k}', 0.006 * s, (dx * s, -0.014 * s, dz * s), scale=(1, 0.4, 1), m=P['heart_c'], seg=8, front=front)
        for k, dz in enumerate((0.05, 0.028)):
            cyl(root, f'{tag}_lente{k}', 0.009 * s, 0.006 * s, (-0.02 * s, 0.011 * s, dz * s), rot=(math.pi / 2, 0, 0), m=P['phone'], v=12, bev=0.002, front=front)
    return e


def ring_light(root, P, tag, base, h, R=0.2, yaw=-0.6, rock=0.2, ph0=0.0, stand=True, front=False):
    """Ring light gigante num tripe, com o celular preso no meio do anel (voltado para -Y local, girado por yaw).
    A cabeca balanca devagar (anim). Devolve (pivo, centro do anel)."""
    x, y, z = base
    if stand:
        for k in range(3):
            a = TAU * k / 3 + 0.5
            tube(root, f'{tag}_perna{k}', [(x + 0.17 * math.cos(a), y + 0.17 * math.sin(a), z), (x, y, z + 0.26)], 0.011, P['spot'], segs=6, front=front)
        tube(root, tag + '_haste', [(x, y, z + 0.2), (x, y, z + h)], 0.014, P['spot'], segs=8, front=front)
        torus(root, tag + '_trava', (x, y, z + h * 0.62), 0.02, 0.008, P['chrome'], n=12, segs=4, front=front)
    piv = empty(root, tag + '_giro', loc=(x, y, z + h), rot=(0, 0, yaw))
    kids(piv, sphere(root, tag + '_junta', 0.028, (0, 0, 0), m=P['spot'], seg=12, front=front))
    with grupo(root, tag + '_cabeca', loc=(0, 0, R * 1.05), parent=piv):
        torus(root, tag + '_anel', (0, 0, 0), R, R * 0.13, P['ring'], axis='Y', n=44, segs=10, front=front)
        torus(root, tag + '_carcaca', (0, R * 0.09, 0), R, R * 0.1, P['spot'], axis='Y', n=44, segs=8, front=front)
        tube(root, tag + '_suporte', [(0, R * 0.05, -R * 0.95), (0, R * 0.05, -0.06)], 0.008, P['chrome'], segs=6, front=front)
        celular(root, P, tag + '_celular', loc=(0, -0.004, 0.0), s=R / 0.2 * 0.95, front=front)
    kids(piv, tube(root, tag + '_garfo', [(0, 0, 0.0), (0, 0, R * 0.1)], 0.012, P['spot'], segs=6, front=front))
    if rock:
        def fn(o, mb, ph, a=rock, p0=ph0):
            o.matrix_basis = mb @ Matrix.Rotation(a * math.sin(TAU * (ph + p0)), 4, 'Z')
        register_anim(piv, fn)
    return piv, (x, y, z + h + R * 1.05)


def painel_led(root, P, lights, tag, base, h, yaw, pitch=0.5, s=1.0, sweep=0.0, ph0=0.0, tripod=True, ground=True):
    """Painel de LED de live num tripe (no lugar do holofote): placa grafite com a face acesa, quatro abas e o
    garfo; sweep > 0: a cabeca varre (anim). A luz vai para `lights`."""
    x, y, z = base
    if tripod:
        for k in range(3):
            a = TAU * k / 3 + 0.4
            tube(root, f'{tag}_perna{k}', [(x + 0.16 * s * math.cos(a), y + 0.16 * s * math.sin(a), z), (x, y, z + 0.22 * s)], 0.011 * s, P['spot'], segs=6)
    elif ground:
        cyl(root, tag + '_base', 0.08 * s, 0.03 * s, (x, y, z + 0.015 * s), m=P['spot'], v=16, bev=0.008)
    tube(root, tag + '_haste', [(x, y, z + (0.2 * s if tripod else 0)), (x, y, z + h)], 0.015 * s, P['chrome'], segs=8)
    piv = empty(root, tag + '_giro', loc=(x, y, z + h), rot=(0, 0, yaw))
    kids(piv, tube(root, tag + '_garfo', [(0, -0.1 * s, 0.09 * s), (0, -0.1 * s, 0.0), (0, 0.1 * s, 0.0), (0, 0.1 * s, 0.09 * s)], 0.009 * s, P['spot'], segs=6))
    tilt = empty(root, tag + '_incl', parent=piv, loc=(0, 0, 0.09 * s), rot=(0, pitch, 0))
    kids(tilt, box(root, tag + '_placa', (0.04 * s, 0.19 * s, 0.13 * s), (0, 0, 0), m=P['spot'], bev=0.01 * s),
         box(root, tag + '_face', (0.006, 0.165 * s, 0.108 * s), (0.021 * s, 0, 0), m=P['glow'], bev=0.003),
         box(root, tag + '_trava', (0.03 * s, 0.04 * s, 0.03 * s), (-0.03 * s, 0, 0), m=P['chrome'], bev=0.005))
    for k, (dy, dz, rot) in enumerate(((0.0, 0.07, (0, -0.55, 0)), (0.0, -0.07, (0, 0.55, 0)))):
        fl = box(root, f'{tag}_aba{k}', (0.06 * s, 0.19 * s, 0.005), (0.045 * s, 0, dz * s + (0.012 if dz > 0 else -0.012) * s), rot=rot, m=P['spot'], bev=0.002)
        fl.parent = tilt
    for k, sy in enumerate((-1, 1)):
        fl = box(root, f'{tag}_abaL{k}', (0.05 * s, 0.005, 0.13 * s), (0.04 * s, sy * 0.105 * s, 0), rot=(0, 0, sy * 0.5), m=P['spot'], bev=0.002)
        fl.parent = tilt
    if sweep:
        def fn(o, mb, ph, a=sweep, p0=ph0):
            o.matrix_basis = mb @ Matrix.Rotation(a * math.sin(TAU * (ph + p0)), 4, 'Z')
        register_anim(piv, fn)
    bpy.context.view_layer.update()
    lp = tilt.matrix_world @ Vector((0.06 * s, 0, 0))
    lights.append(((lp.x, lp.y, lp.z), '#ffe2a6', 12.0 * s, 1))
    return piv


def coracao(root, tag, s, m, front=False):
    """Coracaozinho de curtida voltado para -Y (duas bolas e a ponta para baixo)."""
    out = []
    for k, sx in enumerate((-1, 1)):
        out.append(sphere(root, f'{tag}_lobo{k}', 0.03 * s, (sx * 0.022 * s, 0, 0.012 * s), scale=(1, 0.55, 1), m=m, seg=12, front=front))
    o = cyl(root, tag + '_ponta', 0.046 * s, 0.06 * s, (0, 0, -0.024 * s), r2=0.0, rot=(0, 0, 0), m=m, v=4, bev=0.006, front=front)
    o.rotation_euler = (math.pi, 0, math.pi / 4)
    o.scale = (1.0, 0.45, 1.0)
    out.append(o)
    return out


def curtidas(root, P, tag, loc, n=4, rise=0.5, s=1.0, spread=0.12):
    """Curtidas da live subindo e sumindo (coracoes e baloezinhos da chapa), cada um no seu tempo (loop perfeito)."""
    mats = [P['heart_c'], P['heart_w'], P['heart_c'], P['heart_a']]
    for k in range(n):
        piv = empty(root, f'{tag}_curtida{k}', loc=loc)
        if k % 3 == 2:
            b = chat_bubble(root, f'{tag}_balao{k}', (0, 0, 0), s=0.5 * s, tail=(1 if k % 2 else -1), light=k % 2 == 0)
            b.parent = piv
        else:
            for o in coracao(root, f'{tag}_coracao{k}', s, mats[k % 4]):
                o.parent = piv
        sx = spread * math.sin(k * 2.4)

        def fn(ob, mb, ph, k=k, sx=sx):
            t = (ph + k / n) % 1.0
            sc = min(1.0, t * 5) * min(1.0, (1 - t) * 4)
            off = Vector((sx + 0.04 * math.sin(TAU * t + k), 0, rise * t))
            ob.matrix_basis = Matrix.Translation(off) @ mb @ Matrix.Diagonal((sc, sc, sc, 1))
        register_anim(piv, fn)


# ---------------------------------------------------------------- nivel 1: cercadinho pequeno, pulpito e o ring light
def build_es1(P, root):
    plot(root, P, 'es1')
    lights = []
    # grade em L no fundo, a esquerda, com dois torcedores atras
    grade(root, P, 'es1_gradeA', (-0.72, -0.12), (-0.5, 0.3), faixa=False)
    grade(root, P, 'es1_gradeB', (-0.5, 0.3), (0.0, 0.5), faixa=True)
    apoiador(P, root, 'es1_torA', (-0.66, 0.36), face=-0.55, ph0=0.0, kind=0, pose=0)
    apoiador(P, root, 'es1_torB', (-0.28, 0.58), face=-0.9, ph0=0.45, kind=1, pose=1)
    # pulpito no meio, um pouco atras
    pulpito(root, P, 'es1_pulpito', -0.04, 0.12, G, s=0.95, rz=0.15)
    # painel de LED no tripe (na frente, a esquerda) e o ring light com o celular a direita (o 'top' e o anel)
    painel_led(root, P, lights, 'es1_led', (-0.6, -0.16, G), 0.5, math.radians(25), pitch=0.35, s=0.85)
    _, lc = ring_light(root, P, 'es1_ring', (0.5, 0.16, G), 0.62, R=0.2, yaw=-0.75, rock=0.18)
    br_flag(root, P, 'es1_bandeira', 0.28, 0.5, G, 0.88, w=0.3)
    return {'slots': [(0.34, -0.42, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- nivel 2: palanquinho, o cercadinho do lado e mais gente
def build_es2(P, root):
    plot(root, P, 'es2')
    lights = []
    zt = stage(root, P, 'es2_tablado', 0.06, 0.08, 0.76, 0.78, 0.12)
    stairs(root, P, 'es2_degrau', -0.14, 0.08 - 0.39, zt, w=0.26, n=1, run=0.1)
    pulpito(root, P, 'es2_pulpito', 0.24, 0.27, zt, s=1.0, rz=0.1)
    br_flag(root, P, 'es2_bandeira', 0.34, 0.4, zt, 1.0, w=0.34)
    painel_led(root, P, lights, 'es2_led', (-0.18, 0.4, zt), 0.98, math.radians(-70), pitch=0.6, s=0.95, tripod=False, sweep=0.18)
    _, lc = ring_light(root, P, 'es2_ring', (0.6, 0.1, G), 0.78, R=0.23, yaw=-0.95, rock=0.2)
    # cercadinho a esquerda: grade em diagonal (de frente para a camera) e tres torcedores atras dela
    grade(root, P, 'es2_gradeA', (-0.79, -0.04), (-0.5, -0.44), faixa=True)
    grade(root, P, 'es2_gradeB', (-0.5, -0.44), (-0.18, -0.6))
    apoiador(P, root, 'es2_torA', (-0.56, -0.2), face=-0.45, ph0=0.0, kind=0, pose=0)
    apoiador(P, root, 'es2_torB', (-0.66, 0.1), face=-0.35, ph0=0.35, kind=1, pose=1)
    apoiador(P, root, 'es2_torC', (-0.5, 0.38), face=-0.4, ph0=0.7, kind=2, pose=2, s=0.95)
    return {'slots': [(0.06, -0.16, zt)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- nivel 3: palanque de dois andares e o cercadinho cheio
def build_es3(P, root):
    plot(root, P, 'es3')
    lights = []
    z1 = stage(root, P, 'es3_tablado1', 0.04, 0.04, 0.92, 0.92, 0.08, r=0.1)
    z2 = stage(root, P, 'es3_tablado2', 0.1, 0.25, 0.7, 0.48, 0.08, z0=z1, r=0.08)
    stairs(root, P, 'es3_degrau', 0.1, 0.25 - 0.24, z2, w=0.3, n=1, run=0.09, z0=z1)
    stairs(root, P, 'es3_degrauBaixo', 0.12, 0.04 - 0.46, z1, w=0.34, n=1, run=0.1)
    pulpito(root, P, 'es3_pulpito', 0.1, 0.3, z2, s=1.05, rz=0.1)
    # painel de fundo verde com o emblema (o fundo da live) atras do pulpito
    slab(root, 'es3_fundo', 0.6, 0.42, 0.03, P['velvet_d'], r=0.04, loc=(0.1, 0.47, z2 + 0.42), bev=0.01)
    slab(root, 'es3_fundoGalao', 0.64, 0.46, 0.02, P['trim'], r=0.05, loc=(0.1, 0.48, z2 + 0.42), bev=0.006)
    emblema(root, 'es3_fundoEmblema', 0.34, 0.3, loc=(0.1, 0.452, z2 + 0.44), depth=0.008)
    br_flag(root, P, 'es3_bandeira', 0.42, 0.44, z2, 1.12, w=0.36)
    painel_led(root, P, lights, 'es3_led1', (0.36, -0.6, G), 0.6, math.radians(125), pitch=0.45, s=0.95)
    painel_led(root, P, lights, 'es3_led2', (-0.24, 0.42, z1), 1.08, math.radians(-60), pitch=0.6, s=1.0, tripod=False, sweep=0.2)
    _, lc = ring_light(root, P, 'es3_ring', (0.62, 0.06, G), 0.92, R=0.28, yaw=-0.95, rock=0.22)
    # cercadinho cheio a esquerda: grade em diagonal e quatro torcedores atras dela
    grade(root, P, 'es3_gradeA', (-0.8, 0.02), (-0.58, -0.4), faixa=True)
    grade(root, P, 'es3_gradeB', (-0.58, -0.4), (-0.24, -0.62), faixa=True)
    apoiador(P, root, 'es3_torA', (-0.58, -0.16), face=-0.45, ph0=0.0, kind=0, pose=0)
    apoiador(P, root, 'es3_torB', (-0.68, 0.14), face=-0.35, ph0=0.3, kind=1, pose=1)
    apoiador(P, root, 'es3_torC', (-0.58, 0.42), face=-0.45, ph0=0.6, kind=2, pose=2)
    apoiador(P, root, 'es3_torD', (-0.32, 0.64), face=-0.7, ph0=0.85, kind=0, pose=1, s=0.95)
    return {'slots': [(-0.32, -0.26, z1)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- Live de Quinta: o estudio da live semanal
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


def bunting(root, P, tag, p0, p1, n=9, sag=0.08):
    """Varal de bandeirolas verde, amarelo e azul."""
    p0, p1 = Vector(p0), Vector(p1)
    pts = [p0.lerp(p1, t) - Vector((0, 0, sag * math.sin(math.pi * t))) for t in [j / 16 for j in range(17)]]
    tube(root, tag + '_fio', pts, 0.004, P['mic'], segs=4)
    cols = [P['velvet'], P['trim'], P['flag_b'] if V_ else P['velvet_d']]
    for k in range(n):
        t = (k + 0.5) / n
        c = p0.lerp(p1, t) - Vector((0, 0, sag * math.sin(math.pi * t)))
        o = cyl(root, f'{tag}_bandeirola{k}', 0.035, 0.07, (c.x, c.y - 0.003, c.z - 0.035), r2=0.0, rot=(math.pi, 0, 0), m=cols[k % 3], v=3, bev=0.0)
        o.scale = (1.0, 0.18, 1.0)
        o.rotation_euler = (math.pi, 0, math.pi / 2)


def interprete(P, root, tag, loc, face=-0.4):
    """Interprete de Libras (roupa preta, as maos no ar sinalizando), que mexe as maos no loop (o grupo balanca)."""
    blk = mat('roupa_interprete', '#26262b', rough=0.8, var=0.02, bump=0.06, sheen=0.3)
    sk = mat('pele_clara', '#e2b08a', rough=0.7, var=0.05, bump=0.02)
    pr = build_person(P, root, tag, dict(tunic=blk, skirt_m=blk, pants=blk, belt=None, head='hair', topknot=True, skin=sk,
                                         hair_m=mat('cabelo_interprete', '#4a2c18', rough=0.7, var=0.03, bump=0.25), boot_m=shoes(), boot_cuff=blk,
                                         sleeve=blk, bracer=blk, bare_hands=True))
    pose_person(pr, P, root, dict(hand_R=(0.16, -0.1, 0.52), grip_R=(0.3, -0.2, 1.0), hand_L=(0.15, 0.08, 0.46), grip_L=(0.4, 0.3, 1.0),
                                  head_pitch=-0.05, breathe=0.3, pole_R=(-0.3, -1.0, -0.2), pole_L=(-0.3, 1.0, -0.2)))
    g = empty(root, tag + '_grupo')
    for o in list(root.children):
        if o is not g and o.name.startswith(tag + '_'):
            o.parent = g
    g.location = (loc[0], loc[1], loc[2] if len(loc) > 2 else G)
    g.rotation_euler = (0, 0, face - PERSON_FACE)
    g.scale = (0.92, 0.92, 0.92)
    register_anim(g, lambda o, mb, ph: setattr(o, 'matrix_basis', mb @ Matrix.Rotation(0.06 * math.sin(TAU * 2 * ph), 4, 'Z')
                                               @ Matrix.Translation((0, 0, 0.008 * math.sin(TAU * 2 * ph)))))
    return g


def build_esD(P, root):
    plot(root, P, 'esD')
    lights = []
    cx, cy = 0.0, 0.06
    W, D = 1.24, 0.74
    zt = stage(root, P, 'esD_palco', cx, cy, W, D, 0.2, r=0.06)
    # saia de veludo com franja amarela na frente do palco (camada da frente)
    box(root, 'esD_saia', (W - 0.04, 0.02, 0.15), (cx, cy - D / 2 - 0.008, G + 0.11), m=P['velvet'], bev=0.006, front=True)
    box(root, 'esD_franja', (W - 0.04, 0.024, 0.025), (cx, cy - D / 2 - 0.01, G + 0.185), m=P['trim'], bev=0.005, front=True)
    stairs(root, P, 'esD_degrau', 0.44, cy - D / 2, zt, w=0.24, n=2, run=0.08)
    # trelica: duas torres atras e a viga com os paineis de LED que varrem e o varal de bandeirolas
    zb = 1.36
    for sx in (-1, 1):
        truss(root, P, f'esD_torre{sx}', (sx * 0.56, cy + 0.26, zt), (sx * 0.56, cy + 0.26, zb + 0.04))
        cyl(root, f'esD_sapata{sx}', 0.07, 0.02, (sx * 0.56, cy + 0.26, zt + 0.01), m=P['spot'], v=4, bev=0.004, rot=(0, 0, math.pi / 4))
    truss(root, P, 'esD_viga', (-0.62, cy + 0.26, zb), (0.62, cy + 0.26, zb))
    for k, (x, yaw, p0) in enumerate(((-0.32, math.radians(-70), 0.0), (0.0, math.radians(-90), 0.33), (0.32, math.radians(-110), 0.66))):
        painel_led(root, P, lights, f'esD_led{k}', (x, cy + 0.26, zb + 0.04), 0.06, yaw, pitch=0.75, s=0.8, tripod=False, ground=False, sweep=0.3, ph0=p0)
    bunting(root, P, 'esD_varal', (-0.56, cy + 0.2, zb - 0.06), (0.56, cy + 0.2, zb - 0.06), n=11, sag=0.12)
    # o fundo da live: o painel-bandeira da chapa (verde com o losango amarelo e o circulo azul, sem a faixa)
    slab(root, 'esD_painelGalao', 1.04, 0.76, 0.02, P['trim'], r=0.05, loc=(cx, cy + 0.31, zt + 0.44), bev=0.006)
    slab(root, 'esD_painel', 1.0, 0.72, 0.03, P['flag_g'], r=0.04, loc=(cx, cy + 0.3, zt + 0.44), bev=0.01)
    los = prism_xz(root, 'esD_painelLosango', [(0.42, 0.0), (0.0, 0.3), (-0.42, 0.0), (0.0, -0.3)], 0.01, P['flag_y'], bev=0.004)
    los.location = (cx, cy + 0.282, zt + 0.44)
    cyl(root, 'esD_painelCirculo', 0.15, 0.012, (cx, cy + 0.274, zt + 0.44), rot=(math.pi / 2, 0, 0), m=P['flag_b'], v=32, bev=0.004)
    # estante baixa atras, de um lado, com livros (o escritorio da live)
    ex = 0.42
    box(root, 'esD_estante', (0.26, 0.12, 0.34), (ex, cy + 0.2, zt + 0.17), m=P['desk_d'], bev=0.012)
    for k in range(5):
        box(root, f'esD_livro{k}', (0.035, 0.08, 0.12 + 0.02 * (k % 2)), (ex - 0.09 + 0.045 * k, cy + 0.16, zt + 0.25), rot=(0, 0.08 * (k == 4), 0),
            m=(P['velvet'], P['trim'], P['flag_b'], P['paper'], P['velvet'])[k], bev=0.004)
    box(root, 'esD_prateleira', (0.24, 0.1, 0.012), (ex, cy + 0.16, zt + 0.185), m=P['desk_l'], bev=0.003)
    # interprete de Libras no canto esquerdo do palco, olhando para a frente
    interprete(P, root, 'esD_libras', (-0.44, cy + 0.02, zt), face=-0.75)
    # a bancada da live na frente do apresentador (camada da frente): o celular no suporte, o microfone e os papeis
    by = cy - 0.27
    box(root, 'esD_bancada', (0.62, 0.2, 0.33), (cx - 0.04, by, zt + 0.165), m=P['desk'], bev=0.016, front=True)
    box(root, 'esD_bancadaTampo', (0.68, 0.24, 0.035), (cx - 0.04, by, zt + 0.345), m=P['desk_l'], bev=0.01, front=True)
    for k, x in enumerate((-0.22, 0.14)):
        box(root, f'esD_bancadaPainel{k}', (0.24, 0.012, 0.22), (cx - 0.04 + x * 1.0 + 0.04, by - 0.104, zt + 0.165), m=P['desk_d'], bev=0.006, front=True)
    box(root, 'esD_bancadaFriso', (0.6, 0.01, 0.016), (cx - 0.04, by - 0.106, zt + 0.3), m=P['trim'], bev=0.003, front=True)
    for o in emblema(root, 'esD_bancadaEmblema', 0.14, 0.12, loc=(cx - 0.04, by - 0.112, zt + 0.17), depth=0.008):
        o['front'] = 1
    zd = zt + 0.363
    # suporte de mesa com o celular virado para o apresentador (a camera ve a capinha verde)
    tube(root, 'esD_suporte', [(-0.2, by + 0.02, zd), (-0.2, by + 0.02, zd + 0.12)], 0.008, P['spot'], segs=6, front=True)
    cyl(root, 'esD_suporteBase', 0.04, 0.012, (-0.2, by + 0.02, zd + 0.006), m=P['spot'], v=14, bev=0.004, front=True)
    celular(root, P, 'esD_celularMesa', loc=(-0.2, by + 0.02, zd + 0.19), rot=(0, 0, math.pi + 0.35), s=0.85, front=True)
    for k in range(2):
        box(root, f'esD_papel{k}', (0.1, 0.14, 0.004), (0.1 + 0.02 * k, by + 0.02, zd + 0.003 + 0.004 * k), rot=(0, 0, 0.2 - 0.3 * k), m=P['paper'], bev=0.001, front=True)
    cyl(root, 'esD_copo', 0.02, 0.06, (0.2, by + 0.05, zd + 0.03), r2=0.024, m=P['glass'], v=14, bev=0.003, front=True)
    # o ring light grande de pe, no canto da bancada, apontado para o apresentador (camada da frente)
    rp, rc = ring_light(root, P, 'esD_ring', (0.4, cy - 0.2, zt), 0.46, R=0.15, yaw=math.pi - 0.75, rock=0.0, front=True)
    # curtidas subindo do celular da mesa
    curtidas(root, P, 'esD_curtidas', (-0.22, by - 0.04, zd + 0.32), n=4, rise=0.42, s=0.9, spread=0.08)
    return {'slots': [(0.0, cy - 0.12, zt)], 'lights': lights, 'anim_shadow': True, 'points': {'top': (0.0, cy + 0.2, zb - 0.2)}}


# ---------------------------------------------------------------- Camera da Live: a grua com o ring light varrendo
def monitor(root, P, tag, x, y, z=G, w=0.6, h=0.4, rz=0.0):
    """Monitor grande da live num pedestal: moldura preta, tela acesa com o fundo verde, o emblema da chapa, a
    bolinha vermelha de 'ao vivo' e coracoes (sem texto)."""
    with grupo(root, tag, loc=(x, y, z), rot=(0, 0, rz)) as e:
        cyl(root, tag + '_pe', 0.16, 0.04, (0, 0.02, 0.02), r2=0.13, m=P['spot'], v=24, bev=0.012)
        tube(root, tag + '_coluna', [(0, 0.04, 0.04), (0, 0.04, 0.5)], 0.03, P['spot'], segs=10)
        zc = 0.5 + h / 2
        slab(root, tag + '_moldura', w + 0.05, h + 0.05, 0.05, P['phone'], r=0.03, loc=(0, 0.02, zc), bev=0.012)
        slab(root, tag + '_tela', w, h, 0.01, P['screen'], r=0.02, loc=(0, -0.008, zc), bev=0.003)
        slab(root, tag + '_telaFundo', w * 0.94, h * 0.62, 0.006, mat('tela_verde', '#3cc46a', rough=0.3, var=0, bump=0, emit=0.8), r=0.015,
             loc=(0, -0.015, zc + h * 0.1), bev=0.002)
        for o in emblema(root, tag + '_telaEmb', w * 0.42, h * 0.5, loc=(0, -0.019, zc + h * 0.1), depth=0.004):
            pass
        box(root, tag + '_barra', (w * 0.94, 0.006, h * 0.16), (0, -0.015, zc - h * 0.33), m=P['trim'], bev=0.002)
        sphere(root, tag + '_aoVivo', 0.022, (-w * 0.4, -0.02, zc + h * 0.36), scale=(1, 0.4, 1), m=P['onair'], seg=10)
        for k in range(3):
            for o in coracao(root, f'{tag}_coracao{k}', 0.45, (P['heart_c'], P['heart_a'], P['heart_b'])[k]):
                o.location = o.location + Vector((w * 0.3 + 0.05 * k, -0.02, zc - h * 0.33))
    return e


def build_esW(P, root):
    plot(root, P, 'esW')
    lights = []
    # o monitor da live no fundo, a esquerda, com a bandeirinha e os cabos
    mx, my = -0.36, 0.34
    monitor(root, P, 'esW_monitor', mx, my, rz=0.25)
    lights.append(((mx + 0.02, my - 0.12, G + 0.7), '#ffd88a', 14.0, 1))
    bandeirinha(root, 'esW_bandeira', (mx - 0.36, my + 0.08, G), h=0.62, w=0.24, fh=0.16)
    tube(root, 'esW_cabo', [(mx + 0.08, my + 0.05, G + 0.01), (0.0, 0.3, G + 0.01), (0.2, 0.16, G + 0.01), (0.4, 0.2, G + 0.01)], 0.012, P['mic'], segs=6)
    # curtidas subindo do monitor
    curtidas(root, P, 'esW_curtidas', (mx + 0.05, my - 0.05, G + 1.02), n=4, rise=0.42, s=1.0, spread=0.14)
    # o cercadinho na frente, a esquerda, e a turma acenando para a camera
    grade(root, P, 'esW_gradeA', (-0.74, -0.2), (-0.42, -0.5), faixa=True)
    grade(root, P, 'esW_gradeB', (-0.42, -0.5), (-0.06, -0.62))
    apoiador(P, root, 'esW_torA', (-0.56, -0.12), face=-0.9, ph0=0.0, kind=0, pose=1)
    apoiador(P, root, 'esW_torB', (-0.24, -0.34), face=-1.1, ph0=0.5, kind=1, pose=0)
    # painel de LED no tripe
    painel_led(root, P, lights, 'esW_led', (-0.66, 0.08, G), 0.62, math.radians(10), pitch=0.45, s=0.9)
    # a grua: tripe com rodinhas, coluna verde, o braco de trelica com os contrapesos atras e o ring light na ponta
    x0, y0 = 0.5, 0.2
    for k in range(3):
        a = TAU * k / 3 + 0.3
        tube(root, f'esW_gruaPerna{k}', [(x0 + 0.24 * math.cos(a), y0 + 0.24 * math.sin(a), G + 0.06), (x0, y0, G + 0.34)], 0.022, P['spot'], segs=8)
        sphere(root, f'esW_gruaRoda{k}', 0.045, (x0 + 0.24 * math.cos(a), y0 + 0.24 * math.sin(a), G + 0.045), scale=(1, 0.6, 1), m=P['mic'], seg=14,
               rot=(0, 0, a + math.pi / 2))
    tube(root, 'esW_gruaColuna', [(x0, y0, G + 0.3), (x0, y0, G + 0.84)], 0.045, P['velvet'], segs=12)
    for k, zz in enumerate((0.42, 0.7)):
        torus(root, f'esW_gruaTrava{k}', (x0, y0, G + zz), 0.05, 0.014, P['trim'], n=16, segs=5)
    cyl(root, 'esW_gruaCabecote', 0.07, 0.08, (x0, y0, G + 0.87), m=P['spot'], v=18, bev=0.012)
    hx, hy, hzz = x0 - 0.3, y0 - 0.16, G + 1.1
    p_back = Vector((x0 + 0.26, y0 + 0.14, G + 0.73))
    p_head = Vector((hx, hy, hzz))
    truss(root, P, 'esW_gruaBraco', p_back, p_head, w=0.06, m=P['chrome'])
    tube(root, 'esW_gruaBracoFaixa', [p_back.lerp(p_head, 0.55), p_back.lerp(p_head, 0.8)], 0.038, P['velvet'], segs=10)
    for k in range(3):
        cyl(root, f'esW_contrapeso{k}', 0.075 - 0.01 * k, 0.035, tuple(p_back.lerp(p_head, 0.02 + 0.06 * k)),
            rot=Vector(p_head - p_back).to_track_quat('Z', 'Y').to_euler(), m=P['spot'] if k != 1 else P['trim'], v=20, bev=0.008)
    sphere(root, 'esW_gruaPonta', 0.045, (hx, hy, hzz), m=P['spot'], seg=12)
    piv, lc = ring_light(root, P, 'esW_ring', (hx, hy, hzz), 0.0, R=0.3, yaw=-0.55, rock=0.28, stand=False)
    # camera de verdade presa na frente do anel (alem do celular), olhando junto
    return {'slots': [(0.42, -0.5, G)], 'lights': lights, 'anim_shadow': True, 'points': {'top': lc}}


# ---------------------------------------------------------------- tripulacao
def suit_mat(key, hexcol):
    return mat('terno_' + key, hexcol, rough=0.7, var=0.03, bump=0.06, sheen=0.3)


def build_torcedora(P, root):
    """Torcedora da bandeirinha: camisa amarela da selecao, coque, calcao azul e a bandeira da chapa na mao esquerda."""
    tag = root['set']
    pr = build_person(P, root, tag, torcedor_sp(P, 1))
    vestir_torcedor(root, P, pr, tag, 1)
    objs, cl = hand_flag(root, P, tag + '_bandeira', stick=0.26, w=0.18, fh=0.125)
    hold(pr, 'L', *objs)
    pr['cloth'].append(cl)
    return pr


def build_selfie(P, root):
    """Torcedor da selfie: bone verde, camisa da selecao e o celular de capinha verde na mao direita (fazendo live)."""
    tag = root['set']
    pr = build_person(P, root, tag, torcedor_sp(P, 0))
    vestir_torcedor(root, P, pr, tag, 0)
    e = celular(root, P, tag + '_celular', loc=(0, 0, 0.07), rot=(0, 0, -math.pi / 2), s=0.9)
    hold(pr, 'R', e)
    return pr


def build_veterano(P, root):
    """Veterano do bandeirao: grisalho, oculos escuros, camisa da selecao e o bandeirao da chapa num mastro."""
    tag = root['set']
    pr = build_person(P, root, tag, torcedor_sp(P, 2))
    vestir_torcedor(root, P, pr, tag, 2)
    glasses(root, pr, tag, dark=True)
    st = tube(root, tag + '_mastro', [(0, 0, -0.08), (0, 0, 0.27)], 0.008, P['chrome'], segs=6)
    o = flag_mesh(root, P, tag + '_bandeirao', 0.22, 0.15)
    o.location = (0.006, 0, 0.265)
    register_cloth(o, flag_wave(0.22, amp=0.045, cycles=1, waves=1.0))
    hold(pr, 'L', st, o)
    pr['cloth'].append(o)
    return pr


def cabelo_curto(root, pr, tag, m):
    """Cabelo curto penteado (so o alto e a nuca, a testa e as orelhas de fora), no pivo da cabeca."""
    def cut(c):
        return abs(math.atan2(c.y, c.x)) < math.radians(62) and c.z < 0.032
    o = lathe(root, tag + '_cabeloCurto', [(-0.012, 0.069, 0.071), (0.02, 0.073, 0.075), (0.05, 0.06, 0.062), (0.07, 0.034, 0.034), (0.08, 0.0, 0.0)],
              m, segs=18, lv=2, caps=False, solid=0.01, cut=cut)
    o.parent = pr['head']
    o.location = HC
    return o


def build_apresentador(P, root):
    """Apresentador da live (pessoa generica): terno azul-marinho, camisa branca, gravata verde com o no amarelo e o
    broche da chapa; gesticula com as duas maos (o ritmo da batucada antiga)."""
    tag = root['set']
    s_ = suit_mat('marinho_live', '#25335a')
    hair = mat('cabelo_apresentador', '#3a2a20', rough=0.7, var=0.03, bump=0.25)
    pr = build_person(P, root, tag, dict(tunic=s_, head='bald', belt=None, skirt_m=s_, pants=s_, boot_m=shoes(), boot_cuff=s_,
                                         sleeve=s_, bracer=s_, bare_hands=True, big=1.06, brow_m=hair))
    cabelo_curto(root, pr, tag, hair)
    tie(root, pr, tag, cor('pri', rough=0.6, sheen=0.3), knot=cor('sec', rough=0.6, sheen=0.3))
    broche(root, pr, tag)
    return pr


def build_cinegrafista(P, root):
    """Cinegrafista da live: bone verde virado para tras, camisa da selecao e o celular deitado no gimbal (bastao)."""
    tag = root['set']
    pr = build_person(P, root, tag, torcedor_sp(P, 0))
    marca_peito(root, pr, tag)
    o = cyl(root, tag + '_boneAba', 0.06, 0.01, (0, 0, 0), m=P['bone'], v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((-0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, 0.18, 0)
    gim = [tube(root, tag + '_gimbalCabo', [(0, 0, -0.04), (0, 0, 0.09)], 0.016, P['mic'], segs=8),
           tube(root, tag + '_gimbalBraco', [(0, 0, 0.09), (0.0, 0.03, 0.12), (0.0, 0.0, 0.15)], 0.008, P['spot'], segs=6),
           sphere(root, tag + '_gimbalBotao', 0.008, (0.014, 0, 0.06), m=P['velvet'], seg=8)]
    e = celular(root, P, tag + '_celular', loc=(0.0, 0, 0.17), s=0.85)
    e.rotation_euler = Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0))).to_euler()
    hold(pr, 'R', *gim, e)
    return pr


IDLE_N, ACT_N = 12, 8


def relatora_state(mode, f):
    """idle: segura a bandeirinha junto ao peito; act: ergue a bandeirinha bem alto e sacode."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.12, 0.08, 0.36 + 0.01 * s), grip_L=(0.2, 0.0, 1.0), hand_R=(0.06, -0.13, 0.28), breathe=s,
                    head_yaw=0.3 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    k = math.sin(math.pi * f / (ACT_N - 1))
    return dict(hand_L=(0.12 + 0.04 * k, 0.1, 0.36 + 0.17 * k), grip_L=(0.2, 0.25 * math.sin(TAU * f / ACT_N * 2), 1.0), hand_R=(0.1, -0.12, 0.3 + 0.08 * k),
                head_pitch=-0.25 * k, ph=f / ACT_N)


def presidente_state(mode, f):
    """idle: celular na mao, gesticulando de leve; act: ergue o celular na frente do rosto e fala com a live."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.12, 0.32), grip_R=(0.3, -0.2, 1.0), hand_L=(0.1, 0.13, 0.3 + 0.03 * s), breathe=s,
                    head_yaw=0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.1, ph=ph)
    k = math.sin(math.pi * min(1.0, f / 3))
    return dict(hand_R=(0.1 + 0.03 * k, -0.04, 0.4 + 0.1 * k), grip_R=(0.8, 0.0, 0.6 + 0.4 * k), hand_L=(0.16 + 0.04 * k, 0.16, 0.42 + 0.12 * k),
                head_pitch=-0.15 * k, breathe=0.6 * k, ph=f / ACT_N)


def senador_state(mode, f):
    """idle: bandeirao na mao esquerda, encostado atras do ombro (nao cobre o rosto); act: ergue o bandeirao bem alto
    e baixa com tudo (o ritmo da martelada antiga)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_L=(0.06, 0.16, 0.34 + 0.01 * s), grip_L=(-0.25, 0.45, 1.0), hand_R=(0.08, -0.12, 0.3), breathe=s,
                    head_yaw=0.2 * math.sin(TAU * ph), head_pitch=-0.1, ph=ph)
    up = [0.3, 0.7, 1.0, 1.0, 0.2, 0.0, 0.0, 0.1][f]
    return dict(hand_L=(0.06 + 0.06 * up, 0.16 + 0.02 * up, 0.34 + 0.22 * up), grip_L=(-0.25 + 0.15 * up, 0.45 - 0.2 * up, 1.0), hand_R=(0.12, -0.12, 0.34 + 0.06 * up),
                head_pitch=-0.25 * up + 0.1 * (1 - up), lean=0.06 * (1 - up), ph=f / ACT_N)


def batuqueiro_state(mode, f):
    """idle: gesticula devagar (alternando as maos, o ritmo da batucada antiga); act: gesticula rapido."""
    n = IDLE_N if mode == 'idle' else ACT_N
    ph = f / n
    k = 2 if mode == 'act' else 1
    l = 0.5 + 0.5 * math.sin(TAU * k * ph)
    r = 0.5 + 0.5 * math.sin(TAU * k * ph + math.pi)
    return dict(hand_L=(0.2, 0.12, 0.32 + 0.22 * l), grip_L=(1.0, 0.0, 0.4 - 1.2 * (1 - l)), hand_R=(0.2, -0.12, 0.32 + 0.22 * r),
                grip_R=(1.0, 0.0, 0.4 - 1.2 * (1 - r)), lean=0.12, head_pitch=-0.1, breathe=0.5 * math.sin(TAU * ph), ph=ph,
                pole_L=(-0.3, 1.0, -0.2), pole_R=(-0.3, -1.0, -0.2))


def perito_state(mode, f):
    """Filma com o gimbal na altura dos olhos, varrendo devagar de um lado para o outro."""
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
    'towers': [('es1', 'Live do Cercadinho N1', build_es1), ('es2', 'Live do Cercadinho N2', build_es2), ('es3', 'Live do Cercadinho N3', build_es3),
               ('esD', 'Live de Quinta', build_esD), ('esW', 'Camera da Live', build_esW)],
    'crews': [crew('esP', 'Torcedora da bandeirinha', build_torcedora, relatora_state), crew('esC', 'Torcedor da selfie', build_selfie, presidente_state),
              crew('esA', 'Veterano do bandeirao', build_veterano, senador_state), crew('esT', 'Apresentador da live', build_apresentador, batuqueiro_state),
              crew('esV', 'Cinegrafista', build_cinegrafista, perito_state)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
