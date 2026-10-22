"""Dolar na Cueca (especializacao do Mensalinho, Ninguem Sobe a Rampa; motor 'archer' spec 'blowgun', familia
'zarabatana'): um guiche menor de concreto branco com terraco aberto, arco de Niemeyer atras, varal de cuecas listradas
e dolares secando (a lavanderia) e dois assessores de cueca samba-cancao listrada por cima da calca, com dolares
escapando pelo elastico, que sopram notas de dolar enroladas pela zarabatana. Humor leve, sem nudez.
Mesmos conjuntos, postos, luzes e pontos da Zarabatana do Guardioes da Mata (js/sprites.js depende deles).
Duas versoes, uma por chapa (tools/blender/chapa.py): friso, guiche, tapete, bandeirinha na mureta, cuecas e a roupa
dos assessores (camisa da selecao com gola em V ou camiseta vermelha com estrela) mudam de cor; o resto e igual.

  Blender -b -P tools/blender/torre_zarabatana.py -- render arte/render/zarabatana [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_zarabatana.py -- render arte/render_r/zarabatana [conjuntos...]
  Blender -b -P tools/blender/torre_zarabatana.py -- still <arquivo.png> [amostras]
  Blender -b -P tools/blender/torre_zarabatana.py -- crew <arquivo.png> [amostras] [show|pose0]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib as _lib
from mensalinho_pecas import *   # noqa: F401,F403
from lote_brasilia import plot   # noqa: F811 - lote de concreto de Brasilia (o mesmo das outras torres)

FAM = 'zarabatana'

_orig_palette2 = _lib.palette2


def palette2():   # noqa: F811
    P = mats_mensalinho(_orig_palette2())
    # cuecas listradas nas cores da chapa (V: amarelo e verde, branco e azul; R: branco e vermelho, branco e vinho)
    (a1, a2), (b1, b2) = CUECAS[CHAPA]
    P['cueca_a'] = mat('cueca_a_' + CHAPA, a2, rough=0.85, var=0.0, bump=0.05, stripes=(30.0, a1, a2), sheen=0.4)
    P['cueca_b'] = mat('cueca_b_' + CHAPA, b2, rough=0.85, var=0.0, bump=0.05, stripes=(30.0, b1, b2), sheen=0.4)
    P['elastico'] = mat('elastico', '#f7f4ec', rough=0.8, var=0.0, bump=0.05)
    P['zara'] = mat('zarabatana_dolar', '#8fa77e', rough=0.75, var=0.04, bump=0.06)
    P['oculos_esc'] = mat('oculos_escuros', '#1d1d22', rough=0.15, var=0.0, bump=0.0)
    P['vime'] = mat('cesto_vime', '#d4ae6a', rough=0.9, var=0.08, bump=0.4)
    return P


_lib.palette2 = palette2


def cueca_varal(root, P, tag, x, y, z, m, w=0.16, h=0.13):
    """Cueca samba-cancao pendurada no varal (pano animado) com dois prendedores."""
    def shape(u, v, co):
        # pernas: um recorte em V embaixo, no meio
        if v > 0.6 and abs(u - 0.5) < 0.12:
            co.z += (v - 0.6) / 0.4 * h * 0.45
        return co
    o = cloth_grid(root, tag, w, h, 8, 6, [m], shape=shape, thick=0.012)
    o.location = (x - w / 2, y, z)
    register_cloth(o, hang_wave(h, amp=0.03, axis='Y', cycles=1, waves=0.6, top=0.0))
    for k, dx in enumerate((-w * 0.32, w * 0.32)):
        box(root, f'{tag}_prendedor{k}', (0.014, 0.022, 0.04), (x + dx, y, z + 0.008), m=P['wood_l'], bev=0.004)
    return o


def dolar_varal(root, P, tag, x, y, z, w=0.12, h=0.06):
    o = cloth_grid(root, tag, w, h, 6, 3, [P['dolar']], thick=0.008)
    o.location = (x - w / 2, y, z)
    register_cloth(o, hang_wave(h, amp=0.02, axis='Y', cycles=1, waves=0.5, top=0.0))
    box(root, tag + '_prendedor', (0.014, 0.022, 0.04), (x, y, z + 0.008), m=P['wood_l'], bev=0.004)
    return o


def build_zb(P, root):
    plot(root, P, 'zb')
    fz = 1.06
    zf = fz + 0.035                     # piso do terraco (os postos ficam aqui)
    # guiche menor: bloco de concreto arredondado sobre um rodape, laje fina com beiral e tapete verde no terraco
    box(root, 'zb_rodape', (0.98, 0.76, 0.06), (0, 0.04, 0.18), m=P['concreto_s'], bev=0.025)
    # bloco em quadrado arredondado que abre para cima (como o guiche do conceito), sem quina viva
    sq = lambda a, z: (abs(math.cos(a)) ** 4 + abs(math.sin(a)) ** 4) ** -0.25 - 1.0
    prof = [(0.2 + (fz - 0.24) * t, 0.36 + 0.08 * t ** 1.6, 0.28 + 0.06 * t ** 1.6, 0.0) for t in [j / 8 for j in range(9)]]
    o = lathe(root, 'zb_bloco', prof, P['concreto'], segs=48, wobble=sq, lv=1)
    o.location.y = 0.04
    # friso na cor da chapa logo abaixo da laje
    t0, t1 = (fz - 0.34 - 0.2) / (fz - 0.24), (fz - 0.26 - 0.2) / (fz - 0.24)
    fr = [(0.2 + (fz - 0.24) * t, 0.366 + 0.08 * t ** 1.6, 0.286 + 0.06 * t ** 1.6, 0.0) for t in (t0, (t0 + t1) / 2, t1)]
    o = lathe(root, 'zb_friso', fr, P['chapa'], segs=48, wobble=sq, lv=1)
    o.location.y = 0.04
    box(root, 'zb_laje', (1.1, 0.88, 0.07), (0, 0.04, fz), m=P['concreto'], bev=0.03)
    box(root, 'zb_piso', (1.0, 0.78, 0.02), (0, 0.04, zf - 0.01), m=P['tapete'], bev=0.006)
    # mureta: fundo e lados na base; a da frente na camada da frente
    for k, (sx, sy, lx, ly, fr) in enumerate(((0, 0.45, 1.06, 0.06, False), (-0.52, 0.04, 0.06, 0.84, False), (0.52, 0.04, 0.06, 0.84, False),
                                              (0, -0.37, 1.06, 0.06, True))):
        box(root, f'zb_mureta{k}', (lx, ly, 0.13 if fr else 0.16), (sx, sy, zf + (0.065 if fr else 0.08)), m=P['concreto'], bev=0.025, front=fr)
    # bandeirinha da chapa em pe na mureta da direita (pano para fora, abaixo do arco: o enquadramento nao muda)
    bandeira_chapa(root, P, 'zb_bandeiraChapa', (0.52, 0.06, zf + 0.156), h=0.48)
    lamp = guiche(root, P, 'zb', -0.27, z0=0.21, w=0.4, d=0.18, h=0.4)
    for k, a in enumerate((math.radians(-38), math.radians(-142))):
        aleta(root, P, f'zb_aleta{k}', a, 0.63, 0.17, fz - 0.04, wmax=0.14)
    # faixa de vidro esverdeado dos lados do bloco
    for sx in (-1, 1):
        box(root, f'zb_janela{sx}', (0.03, 0.34, 0.14), (sx * 0.43, 0.06, fz - 0.22), m=P['vidro_v'], bev=0.006)
    # arco parabolico de Niemeyer atras da dupla (Pampulha), com o varal da lavanderia
    AH, AW = 1.02, 0.5
    pts = [(-AW + 2 * AW * t, 0.4, zf + AH * (1 - (2 * t - 1) ** 2)) for t in [j / 24 for j in range(25)]]
    tube(root, 'zb_arco', pts, 0.045, P['concreto'], segs=10, rfun=lambda t: 0.052 - 0.018 * math.sin(math.pi * t))
    zv = zf + 0.74
    xs = AW * math.sqrt(1 - 0.74 / AH)
    tube(root, 'zb_varal', [(-xs, 0.4, zv), (0.0, 0.4, zv - 0.035), (xs, 0.4, zv)], 0.005, P['rope'], segs=5)
    cueca_varal(root, P, 'zb_cuecaA', -0.17, 0.4, zv - 0.02, P['cueca_a'])
    cueca_varal(root, P, 'zb_cuecaB', 0.15, 0.4, zv - 0.022, P['cueca_b'])
    dolar_varal(root, P, 'zb_dolar0', -0.02, 0.4, zv - 0.034)
    dolar_varal(root, P, 'zb_dolar1', 0.29, 0.4, zv - 0.012)
    dolar_varal(root, P, 'zb_dolar2', -0.31, 0.4, zv - 0.01)
    # abajur de banqueiro no fundo do terraco e macos de dolar
    lampada_banqueiro(root, P, 'zb_abajur', (0.36, 0.3, zf), rz=-2.2)
    pilha(root, 'zb_dolarT', P, (-0.36, 0.3, zf), n=2, rz=0.3, m=P['dolar'])
    # no chao: cesto de roupa cheio de dolares e uma pilha de macos
    cyl(root, 'zb_cesto', 0.13, 0.16, (0.6, -0.5, 0.15 + 0.08), r2=0.15, m=P['vime'], v=24, bev=0.02)
    torus(root, 'zb_cestoBorda', (0.6, -0.5, 0.15 + 0.16), 0.15, 0.014, P['vime'], n=24, segs=6)
    sphere(root, 'zb_cestoMonte', 0.13, (0.6, -0.5, 0.15 + 0.17), scale=(1, 1, 0.45), m=P['dolar_esc'], seg=14)
    rr = random.Random(3)
    for k in range(6):
        a = TAU * k / 6
        nota(root, f'zb_cestoNota{k}', P, (0.6 + 0.07 * math.cos(a), -0.5 + 0.07 * math.sin(a), 0.15 + 0.22), rot=(rr.uniform(-0.6, 0.6), rr.uniform(-0.6, 0.6), a),
             m=P['dolar'])
    pilha(root, 'zb_dolarChao', P, (-0.6, -0.46, 0.15), n=3, rz=-0.4, m=P['dolar'])
    maco(root, 'zb_dolarChao2', P, (-0.48, -0.6, 0.15), rz=0.9, m=P['dolar'])
    lights = [((0.38, 0.3, zf + 0.15), '#8affa6', 10.0, 1), (lamp, '#8affa6', 8.0, 1)]
    return {'slots': [(-0.24, -0.2, fz + 0.04), (0.24, -0.22, fz + 0.04)], 'lights': lights, 'points': {'top': (0.0, -0.22, fz + 0.62)}}


def build_assessor(P, root, variant):
    """Assessor com a camisa da chapa (manga curta) e cueca samba-cancao listrada por cima da calca, com dolares
    escapando pelo elastico. a: cabelo preto penteado e oculos escuros, cueca A; b: careca de bigode, cueca B."""
    tag = root['set']
    skin = mat('pele_zb' + variant, '#d7a27a' if variant == 'a' else '#b37a52', rough=0.7, var=0.05, bump=0.02)
    cueca = P['cueca_a'] if variant == 'a' else P['cueca_b']
    pr = build_person(P, root, tag, dict(skin=skin, tunic=P['camisa'], sleeve=P['camisa'], bracer=skin, skirt_m=cueca, pants=P['calca'],
                                         boot_m=P['sapato'], boot_cuff=P['calca'], belt=None, head='hair' if variant == 'a' else 'bald',
                                         hair_m=P['cabelo_p'], bare_hands=True))
    pr['head'].scale = (HEAD_K, HEAD_K, HEAD_K)
    body = pr['body']
    sa = bpy.data.objects[f'{tag}_saia']
    sa.rotation_euler = (0, 0, math.pi / 2)          # listras na vertical
    sa.scale = (1.06, 1.06, 0.74)
    sa.location = (0, 0, 0.32 * (1 - 0.74))          # samba-cancao curta: aparece a calca embaixo
    el = torus(root, f'{tag}_elastico', (0, 0, 0), 0.084, 0.013, P['elastico'], n=22, segs=6)
    el.parent = body
    el.location = (0, 0, 0.318)
    el.scale = (0.92, 1.1, 1.0)
    for k, a in enumerate((-55, -18, 22, 60)):
        r = math.radians(a)
        o = box(root, f'{tag}_dolarCueca{k}', (0.006, 0.042, 0.04), (0.088 * math.cos(r), 0.104 * math.sin(r), 0.335), rot=(0, -0.45, r),
                m=P['dolar'] if k % 2 == 0 else P['dolar_esc'], bev=0.003)
        o.parent = body
    peito_chapa(root, P, pr, tag)                    # estrela branca (R) ou decote em V com debrum verde (V)
    hd = pr['head']
    hc = Vector((0.006, 0, 0.055))
    if variant == 'a':
        for s, yy in enumerate((-0.026, 0.026)):
            o = blob(root, f'{tag}_lente{s}', 0.021, hc + Vector((0.064, yy, 0.012)), (0.45, 1.0, 0.8), P['oculos_esc'])
            o.parent = hd
        o = tube(root, f'{tag}_oculosPonte', [hc + Vector((0.07, -0.008, 0.016)), hc + Vector((0.072, 0, 0.018)), hc + Vector((0.07, 0.008, 0.016))], 0.004,
                 P['oculos_esc'], segs=5)
        o.parent = hd
        o = blob(root, f'{tag}_topete', 0.04, hc + Vector((0.03, 0, 0.064)), (1.3, 0.9, 0.55), P['cabelo_p'], rot=(0, -0.3, 0))
        o.parent = hd
    else:
        bigode(root, P, pr, tag, P['cabelo_p'])
        for s, yy in enumerate((-0.06, 0.06)):
            o = blob(root, f'{tag}_costeleta{s}', 0.026, hc + Vector((-0.02, yy, -0.005)), (1.0, 0.5, 1.0), P['cabelo_g'])
            o.parent = hd
    # zarabatana de nota de dolar enrolada (eixo Z local da mao direita)
    hold(pr, 'R', tube(root, tag + '_zarabatana', [(0, 0, -0.32), (0, 0, 0.36)], 0.014, P['zara'], segs=8),
         torus(root, tag + '_zaraAnel1', (0, 0, 0.0), 0.016, 0.005, P['dolar_esc'], n=10, segs=4),
         torus(root, tag + '_zaraAnel2', (0, 0, 0.24), 0.016, 0.005, P['dolar_esc'], n=10, segs=4),
         cyl(root, tag + '_zaraBocal', 0.02, 0.03, (0, 0, -0.33), m=P['gold'], v=10, bev=0.003))
    return pr


IDLE_N, AIM_N, SHOOT_N = 12, 4, 8


def hunter_state(mode, f):
    """idle: zarabatana de pe, olhando em volta; aim: na boca, mirando; shoot: sopra (0), baixa, carrega uma nota e volta a mirar."""
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
    return {'key': key, 'label': label, 'build': lambda P, root: build_assessor(P, root, variant), 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'aim'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('aim', AIM_N, lambda parts, P, root, f: pose(parts, P, root, f, 'aim')),
                      ('shoot', SHOOT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'shoot'))]}


SPEC = {
    'show_crew': {'zb': ['zbA', 'zbB']},
    'towers': [('zb', 'Dolar na Cueca', build_zb)],
    'crews': [crew('zbA', 'Assessor A', 'a'), crew('zbB', 'Assessor B', 'b')],
}


if __name__ == '__main__':
    main(FAM, SPEC)
