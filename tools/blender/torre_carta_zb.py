"""Panfletagem (especializacao da Carta ao Povo Brasileiro, Ninguem Sobe a Rampa, chapa R; motor 'archer' spec 'blowgun',
familia 'zarabatana'): o guiche menor de concreto branco com terraco aberto e o arco de Niemeyer atras vira uma banca de
panfletagem de campanha: varal de santinhos (panfletos vermelhos com estrela branca e creme com estrela vermelha,
sem texto) no arco, pilhas de santinhos no balcao, no terraco e no chao, cesto cheio de santinhos e um megafone.
Dois militantes de camiseta vermelha com estrela branca e bone vermelho sopram santinhos dobrados por um canudo de
panfleto enrolado. Nada de dinheiro.
Mesmos conjuntos, postos, luzes e pontos da Zarabatana/Dolar na Cueca (js/sprites.js depende deles). So a chapa R:

  CHAPA=R Blender -b -P tools/blender/torre_carta_zb.py -- render arte/render_r/zarabatana [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_carta_zb.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_carta_zb.py -- crew <arquivo.png> [amostras] [show|pose0]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib as _lib
from carta_pecas import *   # noqa: F401,F403
from mensalinho_pecas import _poly_into
from lote_brasilia import plot   # noqa: F811 - lote de concreto de Brasilia (o mesmo das outras torres)

FAM = 'zarabatana'
LUZ = '#ffd896'

_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811
    P = mats_carta(_orig_palette2())
    P['estrela_v'] = cor('pri', rough=0.45)          # estrela vermelha dos santinhos creme
    P['megafone'] = mat('megafone_branco', '#f3efe6', rough=0.4, var=0.02, bump=0.02)
    return P


_lib.palette2 = palette2


def santinho_varal(root, P, tag, x, y, z, m, m_star, w=0.11, h=0.15):
    """Santinho pendurado no varal (pano animado, dobra no meio) com a estrela dos dois lados e um prendedor."""
    def shape(u, v, co):
        co.y += 0.008 * (1 - abs(2 * u - 1))          # vinco da dobra
        return co
    o = cloth_grid(root, tag, w, h, 6, 8, [m, m_star], shape=shape, thick=0.008)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    cx, cz = w / 2, -h * 0.5
    r, ri = min(w, h) * 0.34, min(w, h) * 0.34 * 0.42
    for sy in (-1, 1):
        _poly_into(bm, [(cx + (r if i % 2 == 0 else ri) * math.cos(math.pi / 2 + i * math.pi / 5),
                         cz + (r if i % 2 == 0 else ri) * math.sin(math.pi / 2 + i * math.pi / 5)) for i in range(10)], 0.004 + sy * 0.011, 1)
    # tarja de baixo (faixa da cor da estrela, sem letras)
    for sy in (-1, 1):
        _poly_into(bm, [(0.012, -h + 0.035), (w - 0.012, -h + 0.035), (w - 0.012, -h + 0.018), (0.012, -h + 0.018)], 0.004 + sy * 0.009, 1)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o.location = (x - w / 2, y, z)
    register_cloth(o, hang_wave(h, amp=0.03, axis='Y', cycles=1, waves=0.6, top=0.0))
    box(root, f'{tag}_prendedor', (0.014, 0.022, 0.04), (x, y, z + 0.008), m=P['wood_l'], bev=0.004)
    return o


def megafone(root, P, tag, loc, rz=0.0, s=1.0):
    """Megafone branco de boca vermelha deitado (campanha)."""
    x, y, z = loc
    piv = empty(root, tag, loc=(x, y, z), rot=(0, 0, rz))
    kids(piv, cyl(root, tag + '_cone', 0.022 * s, 0.13 * s, (0.0, 0, 0.05 * s), r2=0.05 * s, rot=(0, math.pi / 2, 0), m=P['megafone'], v=18, bev=0.006 * s),
         torus(root, tag + '_boca', (0.066 * s, 0, 0.05 * s), 0.05 * s, 0.009 * s, P['chapa'], axis='X', n=18, segs=6),
         cyl(root, tag + '_bocal', 0.02 * s, 0.04 * s, (-0.08 * s, 0, 0.05 * s), rot=(0, math.pi / 2, 0), m=P['chapa'], v=12, bev=0.005 * s),
         box(root, tag + '_cabo', (0.022 * s, 0.024 * s, 0.05 * s), (-0.03 * s, 0, 0.02 * s), m=P['chapa3'], bev=0.006 * s))
    return piv


def build_zb(P, root):
    plot(root, P, 'zb')
    fz = 1.06
    zf = fz + 0.035                     # piso do terraco (os postos ficam aqui)
    box(root, 'zb_rodape', (0.98, 0.76, 0.06), (0, 0.04, 0.18), m=P['concreto_s'], bev=0.025)
    sq = lambda a, z: (abs(math.cos(a)) ** 4 + abs(math.sin(a)) ** 4) ** -0.25 - 1.0
    prof = [(0.2 + (fz - 0.24) * t, 0.36 + 0.08 * t ** 1.6, 0.28 + 0.06 * t ** 1.6, 0.0) for t in [j / 8 for j in range(9)]]
    o = lathe(root, 'zb_bloco', prof, P['concreto'], segs=48, wobble=sq, lv=1)
    o.location.y = 0.04
    t0, t1 = (fz - 0.34 - 0.2) / (fz - 0.24), (fz - 0.26 - 0.2) / (fz - 0.24)
    fr = [(0.2 + (fz - 0.24) * t, 0.366 + 0.08 * t ** 1.6, 0.286 + 0.06 * t ** 1.6, 0.0) for t in (t0, (t0 + t1) / 2, t1)]
    o = lathe(root, 'zb_friso', fr, P['chapa'], segs=48, wobble=sq, lv=1)
    o.location.y = 0.04
    box(root, 'zb_laje', (1.1, 0.88, 0.07), (0, 0.04, fz), m=P['concreto'], bev=0.03)
    box(root, 'zb_piso', (1.0, 0.78, 0.02), (0, 0.04, zf - 0.01), m=P['tapete'], bev=0.006)
    for k, (sx, sy, lx, ly, fr) in enumerate(((0, 0.45, 1.06, 0.06, False), (-0.52, 0.04, 0.06, 0.84, False), (0.52, 0.04, 0.06, 0.84, False),
                                              (0, -0.37, 1.06, 0.06, True))):
        box(root, f'zb_mureta{k}', (lx, ly, 0.13 if fr else 0.16), (sx, sy, zf + (0.065 if fr else 0.08)), m=P['concreto'], bev=0.025, front=fr)
    # santinhos colados na mureta da frente (faixa de campanha sem letras)
    for k, x in enumerate((-0.36, -0.12, 0.12, 0.36)):
        b = box(root, f'zb_cartaz{k}', (0.12, 0.006, 0.075), (x, -0.403, zf + 0.065), m=P['panfleto'] if k % 2 == 0 else P['panfleto_cl'], bev=0.002, front=True)
        e = estrela(root, f'zb_cartazEstrela{k}', 0.024, 0.004, m=P['estrela'] if k % 2 == 0 else P['estrela_v'], bev=0.001)
        e.location = (x, -0.408, zf + 0.065)
        e['front'] = 1
    bandeira_chapa(root, P, 'zb_bandeiraChapa', (0.52, 0.06, zf + 0.156), h=0.48)
    lamp = guiche_correio(root, P, 'zb', -0.27, z0=0.21, w=0.4, d=0.18, h=0.4, balcao='santinhos')
    for k, a in enumerate((math.radians(-38), math.radians(-142))):
        aleta(root, P, f'zb_aleta{k}', a, 0.63, 0.17, fz - 0.04, wmax=0.14)
    for sx in (-1, 1):
        box(root, f'zb_janela{sx}', (0.03, 0.34, 0.14), (sx * 0.43, 0.06, fz - 0.22), m=P['vidro_v'], bev=0.006)
    # arco parabolico de Niemeyer atras da dupla (Pampulha), com o varal de santinhos
    AH, AW = 1.02, 0.5
    pts = [(-AW + 2 * AW * t, 0.4, zf + AH * (1 - (2 * t - 1) ** 2)) for t in [j / 24 for j in range(25)]]
    tube(root, 'zb_arco', pts, 0.045, P['concreto'], segs=10, rfun=lambda t: 0.052 - 0.018 * math.sin(math.pi * t))
    zv = zf + 0.74
    xs = AW * math.sqrt(1 - 0.74 / AH)
    tube(root, 'zb_varal', [(-xs, 0.4, zv), (0.0, 0.4, zv - 0.035), (xs, 0.4, zv)], 0.005, P['rope'], segs=5)
    santinho_varal(root, P, 'zb_santinhoA', -0.15, 0.4, zv - 0.024, P['panfleto'], P['estrela'])
    santinho_varal(root, P, 'zb_santinhoB', 0.13, 0.4, zv - 0.026, P['panfleto'], P['estrela'])
    santinho_varal(root, P, 'zb_santinho0', -0.01, 0.4, zv - 0.034, P['panfleto_cl'], P['estrela_v'], w=0.09, h=0.12)
    santinho_varal(root, P, 'zb_santinho1', 0.25, 0.4, zv - 0.012, P['panfleto_cl'], P['estrela_v'], w=0.08, h=0.11)
    santinho_varal(root, P, 'zb_santinho2', -0.27, 0.4, zv - 0.01, P['panfleto_cl'], P['estrela_v'], w=0.08, h=0.11)
    # no terraco: luminaria de globo (luz quente), pilha de santinhos e megafone
    glob = globo(root, P, 'zb_poste', 0.362, 0.286, zf, h=0.105)
    pilha_panfletos(root, 'zb_santinhosT', P, (-0.36, 0.3, zf), n=5, rz=0.3)
    megafone(root, P, 'zb_megafone', (0.16, 0.3, zf), rz=2.5, s=1.0)
    # no chao: cesto cheio de santinhos e pilhas de santinhos
    cyl(root, 'zb_cesto', 0.13, 0.16, (0.6, -0.5, 0.15 + 0.08), r2=0.15, m=P['vime'], v=24, bev=0.02)
    torus(root, 'zb_cestoBorda', (0.6, -0.5, 0.15 + 0.16), 0.15, 0.014, P['vime'], n=24, segs=6)
    sphere(root, 'zb_cestoMonte', 0.13, (0.6, -0.5, 0.15 + 0.17), scale=(1, 1, 0.45), m=P['panfleto'], seg=14)
    rr = random.Random(3)
    for k in range(6):
        a = TAU * k / 6
        pf = panfleto(root, f'zb_cestoSantinho{k}', P, w=0.085, h=0.1, m=P['panfleto'] if k % 2 else P['panfleto_cl'],
                      star_m=None if k % 2 else P['estrela_v'])
        pf.location = (0.6 + 0.065 * math.cos(a), -0.5 + 0.065 * math.sin(a), 0.15 + 0.17)
        pf.rotation_euler = (rr.uniform(-0.5, 0.5) - 0.3 * math.sin(a), rr.uniform(-0.3, 0.3) + 0.35 * math.cos(a), a + math.pi / 2 + rr.uniform(-0.3, 0.3))
    pilha_panfletos(root, 'zb_santinhosChao', P, (-0.6, -0.46, 0.15), n=6, rz=-0.4, s=1.1, seed=4)
    pilha_panfletos(root, 'zb_santinhosChao2', P, (-0.47, -0.6, 0.15), n=4, rz=0.9, seed=5)
    lights = [(glob, LUZ, 10.0, 1), (lamp, LUZ, 8.0, 1)]
    return {'slots': [(-0.24, -0.2, fz + 0.04), (0.24, -0.22, fz + 0.04)], 'lights': lights, 'points': {'top': (0.0, -0.22, fz + 0.62)}}


def build_militante(P, root, variant):
    """Militante da panfletagem: camiseta vermelha com estrela branca, jeans, bone vermelho e o canudo de panfleto
    enrolado (creme com faixas vermelhas) que sopra santinhos. a: oculos escuros; b: bigode e costeletas grisalhas."""
    tag = root['set']
    skin = mat('pele_zb' + variant, '#d7a27a' if variant == 'a' else '#b37a52', rough=0.7, var=0.05, bump=0.02)
    pr = build_person(P, root, tag, dict(skin=skin, tunic=P['camisa'], sleeve=P['camisa'], bracer=skin, skirt_m=P['calca'], pants=P['calca'],
                                         boot_m=P['sapato'], boot_cuff=P['calca'], belt=P['cinto'], buckle=P['gold'], head='bald',
                                         hair_m=P['cabelo_p'], bare_hands=True))
    pr['head'].scale = (HEAD_K, HEAD_K, HEAD_K)
    sa = bpy.data.objects[f'{tag}_saia']
    sa.scale = (0.86, 0.86, 1.0)                     # calca, nao tunica
    peito_chapa(root, P, pr, tag)                    # estrela branca no peito
    bone(root, pr, tag, P['bone'])
    hd = pr['head']
    if variant == 'a':
        cabelo_curto(root, pr, tag, P['cabelo_p'])
        for s, yy in enumerate((-0.026, 0.026)):
            o = blob(root, f'{tag}_lente{s}', 0.021, HC + Vector((0.064, yy, 0.012)), (0.45, 1.0, 0.8), P['oculos_esc'])
            o.parent = hd
        o = tube(root, f'{tag}_oculosPonte', [HC + Vector((0.07, -0.008, 0.016)), HC + Vector((0.072, 0, 0.018)), HC + Vector((0.07, 0.008, 0.016))], 0.004,
                 P['oculos_esc'], segs=5)
        o.parent = hd
    else:
        cabelo_curto(root, pr, tag, P['cabelo_g'])
        bigode(root, P, pr, tag, P['cabelo_p'])
    # canudo de cartaz enrolado (eixo Z local da mao direita): papel creme (contrasta com a camiseta), bordas e faixas
    # vermelhas e a costura do rolo em espiral
    hold(pr, 'R', tube(root, tag + '_canudo', [(0, 0, -0.32), (0, 0, 0.36)], 0.017, P['panfleto_cl'], segs=10),
         torus(root, tag + '_canudoBorda1', (0, 0, -0.32), 0.0165, 0.005, P['panfleto'], n=12, segs=4),
         torus(root, tag + '_canudoBorda2', (0, 0, 0.36), 0.0165, 0.005, P['panfleto'], n=12, segs=4),
         tube(root, tag + '_canudoCostura', [(0.0175 * math.cos(2.2 * t), 0.0175 * math.sin(2.2 * t), -0.31 + 0.66 * t) for t in [j / 14 for j in range(15)]],
              0.0028, P['panfleto'], segs=4),
         torus(root, tag + '_canudoFaixa', (0, 0, 0.12), 0.0175, 0.006, P['panfleto'], n=12, segs=4),
         torus(root, tag + '_canudoFaixa2', (0, 0, 0.2), 0.0175, 0.006, P['panfleto'], n=12, segs=4))
    return pr


IDLE_N, AIM_N, SHOOT_N = 12, 4, 8


def hunter_state(mode, f):
    """idle: canudo de pe, olhando em volta; aim: na boca, mirando; shoot: sopra (0), baixa, carrega um santinho e volta."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        return dict(hand_R=(0.1, -0.13, 0.3 + 0.006 * s), grip_R=(0.1, 0.0, 1.0), hand_L=(0.08, 0.12, 0.3), breathe=s,
                    head_yaw=-0.1 + 0.35 * math.sin(TAU * ph + 0.6), head_pitch=-0.12, ph=ph)
    aim = dict(hand_R=(0.13, -0.03, 0.5), grip_R=(-1.0, 0.0, -0.08), hand_L=(0.28, 0.02, 0.49), pole_L=(-0.2, 1.0, -0.6),
               head_pitch=-0.02, head_yaw=0.05)
    if mode == 'aim':
        ph = f / AIM_N
        st = dict(aim)
        st.update(breathe=0.4 * math.sin(TAU * ph), ph=ph)
        return st
    seq = [
        dict(lean=-0.06, breathe=1.0),
        dict(lean=-0.03, breathe=0.6),
        dict(hand_R=(0.1, -0.08, 0.38), grip_R=(-0.5, 0.0, 0.8), hand_L=(0.06, 0.12, 0.34)),
        dict(hand_R=(0.08, -0.12, 0.34), grip_R=(0.0, 0.0, 1.0), hand_L=(-0.02, 0.1, 0.3)),
        dict(hand_R=(0.08, -0.12, 0.34), grip_R=(0.0, 0.0, 1.0), hand_L=(0.06, 0.02, 0.5)),
        dict(hand_R=(0.1, -0.08, 0.4), grip_R=(-0.6, 0.0, 0.6), hand_L=(0.16, 0.02, 0.45)),
        dict(hand_R=(0.12, -0.05, 0.46), grip_R=(-0.9, 0.0, 0.2), hand_L=(0.24, 0.02, 0.48)),
        dict(),
    ][f]
    st = dict(aim)
    st.update(ph=f / SHOOT_N)
    st.update(seq)
    return st


def crew(key, label, variant):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, hunter_state(mode, f))
    return {'key': key, 'label': label, 'build': lambda P, root: build_militante(P, root, variant), 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'aim'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('aim', AIM_N, lambda parts, P, root, f: pose(parts, P, root, f, 'aim')),
                      ('shoot', SHOOT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'shoot'))]}


SPEC = {
    'show_crew': {'zb': ['zbA', 'zbB']},
    'towers': [('zb', 'Panfletagem', build_zb)],
    'crews': [crew('zbA', 'Militante A', 'a'), crew('zbB', 'Militante B', 'b')],
}


if __name__ == '__main__':
    main(FAM, SPEC)
