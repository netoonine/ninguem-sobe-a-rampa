"""Carro de Som do Comicio (Catavento, Ninguem Sobe a Rampa) - arte da familia catavento SO da chapa R (Chapa Vermelha).
Troca a Central do Zap vermelha (a chapa V continua com torre_catavento.py). Meme: carro de som de comicio e discurso
que nao acaba nunca. Uma picapinha de som (cabine vermelha com faixa branca e estrela branca na porta) no lote de
Brasilia, com o paredao de caixas de som na cacamba, o mastro de cornetas com o giroflex e a sacadinha no teto com o
pedestal de microfone; notas musicais e baloes de "..." (sem texto) flutuando.
  niveis 1 a 3: o paredao cresce (2, 3 e 4 fileiras) e o mastro ganha cornetas
  cvT  Comicio na Praca: palanque com duas torres de som, painel vermelho com a estrela branca, o pulpito cheio de
       microfones e o redemoinho de notas e baloes subindo (gira)
  cvS  Jingle Chiclete: a picape com o buque de cornetas douradas (formato de trompete) tocando e a fila de notas saindo
  cvH* a caixa de som no pedestal (torreta): mira o alvo, o cone bate e solta os aneis de som; cvHS = cornetas douradas
  cvM  militante de camiseta vermelha com o microfone; cvO puxador do jingle com o megafone e a bandeirinha
Nomes de conjuntos, modos, quadros, postos e pontos sao os mesmos da Central do Zap (js/sprites.js depende deles), e o
quadro de cada conjunto (largura, altura e ancora) e travado no que o meta.json ja tinha (QUADRO, abaixo): o jogo nao
percebe a troca, so a arte muda. O script avisa (FOLGA) se alguma peca sair do quadro.

  CHAPA=R Blender -b -P tools/blender/torre_carro_som.py -- render arte/render_r/catavento [conjuntos...]
  CHAPA=R Blender -b -P tools/blender/torre_carro_som.py -- still <arquivo.png> [amostras]
  CHAPA=R Blender -b -P tools/blender/torre_carro_som.py -- crew <arquivo.png> [amostras] [show|...]
  (AMOSTRAS=16 no ambiente baixa as amostras do Cycles para testes rapidos)
"""
import os, sys
os.environ.setdefault('CHAPA', 'R')   # esta arte e so da chapa vermelha
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
from lote_brasilia import plot, concrete, grupo, hide_tree, G   # noqa: F811 - lote de concreto de Brasilia
from pecas_zcv import *   # noqa: F401,F403
from chapa import CHAPA, PAL, cor, estrela, bandeirinha   # cores da chapa

FAM = 'catavento'

import lib as _lib
_orig_palette2 = palette2

# luzes do passe de noite (cores das lanternas no meta.json): refletor vermelho no paredao e a luz quente do giroflex
SOM = dict(luz='#ff8f80', luz2='#ffd0c4', farol='#fff1c4', led='#fff2ee', giro='#ff5a4a')


def palette2():   # noqa: F811
    P = _orig_palette2()
    P['teal'] = cor('pri', rough=0.7, sheen=0.4)                     # aros das cornetas, ondas de som
    P['paint'] = mat('lataria_' + CHAPA, PAL['pri'], rough=0.3, var=0.02, bump=0.02)        # picape vermelha
    P['paint_w'] = mat('lataria_branca', '#f7f4ef', rough=0.3, var=0.02, bump=0.02)          # faixa e teto brancos
    P['glass'] = mat('vidro_carro', '#9fcde3', rough=0.08, metal=0.1, var=0.0, bump=0.0)
    P['tire'] = mat('pneu', '#2a2a30', rough=0.75, var=0.02, bump=0.08)
    P['hub'] = mat('calota_roda', '#e6e8ea', rough=0.3, metal=0.35, var=0.0, bump=0.0)
    P['chrome'] = mat('cromado_som', '#c9d0d6', rough=0.25, metal=0.8, var=0.02, bump=0.01)
    P['grille'] = mat('grade_carro', '#34363d', rough=0.5, var=0.0, bump=0.02)
    P['spk'] = mat('caixa_som_preta', '#2b2c33', rough=0.55, var=0.04, bump=0.04)
    P['spk_r'] = mat('caixa_som_chapa_' + CHAPA, PAL['pri'], rough=0.42, var=0.02, bump=0.03)
    P['baffle'] = mat('frente_caixa', '#3b3d46', rough=0.8, var=0.02, bump=0.06)
    P['spk_rim'] = mat('aro_falante', '#1f2025', rough=0.45, var=0.0, bump=0.0)
    P['cone'] = mat('cone_falante', '#62666e', rough=0.7, var=0.02, bump=0.05)
    P['surround'] = mat('borda_falante', '#9a9ea5', rough=0.6, var=0.0, bump=0.02)
    P['dust'] = mat('calota_falante_' + CHAPA, PAL['pri'], rough=0.35, var=0.0, bump=0.0)
    P['dust_w'] = mat('calota_falante_branca', '#f4f2ee', rough=0.35, var=0.0, bump=0.0)
    P['horn'] = mat('corneta_branca', '#f4f2ee', rough=0.4, var=0.02, bump=0.02)
    P['horn_k'] = mat('corneta_motor', '#33373e', rough=0.35, metal=0.3, var=0.03, bump=0.02)
    P['brass'] = mat('corneta_dourada', '#e6b24a', rough=0.26, metal=0.75, var=0.03, bump=0.02)
    P['brass_d'] = mat('corneta_dourada_escura', '#b98330', rough=0.3, metal=0.7, var=0.02, bump=0.02)
    P['deck'] = mat('chapa_xadrez', '#8d949b', rough=0.45, metal=0.5, var=0.02, bump=0.12)
    P['wood_s'] = mat('palco_tabuas', '#d6a66c', rough=0.75, var=0.05, bump=0.1, stripes=(16.0, '#d9ab72', '#c99660'))
    P['skirt'] = cor('pri', rough=0.85, sheen=0.4)
    P['cloth_w'] = mat('pano_branco', '#fbf8f4', rough=0.85, var=0.0, bump=0.04, sheen=0.4)
    P['truss'] = mat('trelica_aluminio', '#b9c0c6', rough=0.3, metal=0.75, var=0.02, bump=0.01)
    P['mic_k'] = mat('microfone_preto', '#26272c', rough=0.4, var=0.0, bump=0.0)
    P['mic_h'] = mat('microfone_grade', '#c2c8ce', rough=0.35, metal=0.7, var=0.0, bump=0.35)
    P['note'] = mat('nota_musical_' + CHAPA, PAL['pri'], rough=0.35, var=0.0, bump=0.0, sheen=0.3)
    P['note_d'] = mat('nota_musical_escura', '#2b2c33', rough=0.35, var=0.0, bump=0.0, sheen=0.3)
    P['wave'] = mat('onda_som_' + CHAPA, PAL['pri'], rough=0.5, var=0.0, bump=0.0, emit=0.15)
    P['wave_w'] = mat('onda_som_branca', '#fff4f0', rough=0.5, var=0.0, bump=0.0, emit=0.25)
    P['plastic'] = mat('plastico_branco', '#f2f1ec', rough=0.42, var=0.02, bump=0.02)
    P['plastic_t'] = mat('plastico_chapa_' + CHAPA, PAL['pri'], rough=0.4, var=0.02, bump=0.02)
    P['cage_d'] = mat('aro_ventilador', '#5d6670', rough=0.3, metal=0.55, var=0.02, bump=0.01)
    P['phone_k'] = mat('celular_preto', '#33373e', rough=0.35, metal=0.3, var=0.03, bump=0.02)
    P['head'] = glow_mat('farol_carro', SOM['farol'], 1.2, 9.0, rough=0.2, var=0.0, bump=0.0)
    P['led'] = glow_mat('led_som_' + CHAPA, SOM['led'], 2.2, 12.0, rough=0.3, var=0.0, bump=0.0)
    P['led_r'] = glow_mat('led_vermelho', '#ff6a5a', 2.0, 10.0, rough=0.3, var=0.0, bump=0.0)
    P['spot'] = glow_mat('refletor_palco', '#fff0d0', 1.6, 10.0, rough=0.3, var=0.0, bump=0.0)
    P['giro'] = glow_mat('giroflex_vermelho', '#ff2a20', 0.7, 10.0, rough=0.22, var=0.0, bump=0.0)
    P['conc'] = concrete()
    return P


_lib.palette2 = palette2
FAN_FACE = math.radians(-60)   # a torreta mira para a direita e para a camera (o jogo espelha)


# ---------------------------------------------------------------- quadro travado (o jogo le w, h e ancora do meta.json)
QUADRO = {
    'cv1': (374, 283, 137.61506963968276, 190.04972060918809),
    'cv2': (374, 316, 137.61506963968276, 223.0497206091881),
    'cv3': (374, 355, 137.61506963968276, 262.0497206091881),
    'cvT': (374, 424, 137.61506963968276, 331.04972060918806),
    'cvS': (374, 350, 137.61506963968276, 257.04972060918806),
    'cvM': (92, 130, 39.69361993843317, 105.67458988017587),
    'cvO': (97, 129, 39.12374346578121, 104.6745898801759),
    'cvH1': (100, 100, 42.901426446676254, 76.0957995453775),
    'cvH2': (115, 116, 49.317244374990466, 89.84067339691521),
    'cvH3': (128, 129, 54.66376090371609, 100.96139962095023),
    'cvHS': (149, 149, 63.21818639659882, 117.95456277075408),
}
_CUR = {'key': None}
_orig_frame_camera = _lib.frame_camera
_orig_render_tower = _lib.render_tower
_orig_render_frames = _lib.render_frames
_orig_setup_scene = _lib.setup_scene


def _frame_camera(cam, lo, hi, margin=(0.12, 0.12, 0.12, 0.12)):
    q = QUADRO.get(_CUR['key'])
    if not q:
        return _orig_frame_camera(cam, lo, hi, margin)
    w, h, ax, ay = q
    px = ST['px']
    x0, y1 = -ax / px, ay / px
    x1, y0 = x0 + w / px, y1 - h / px
    print('FOLGA %s esq %.3f dir %.3f baixo %.3f cima %.3f%s' % (_CUR['key'], lo[0] - x0, x1 - hi[0], lo[1] - y0, y1 - hi[1],
          '  <<< SAI DO QUADRO' if min(lo[0] - x0, x1 - hi[0], lo[1] - y0, y1 - hi[1]) < 0 else ''), flush=True)
    Rv, Uv, Fv = cam_axes()
    sc = bpy.context.scene
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    cam.data.ortho_scale = w / px
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cam.location = Rv * cx + Uv * cy - Fv * 20
    return w, h, (x0, y1)


def _render_tower(key, out):
    _CUR['key'] = key
    try:
        return _orig_render_tower(key, out)
    finally:
        _CUR['key'] = None


def _render_frames(key, out, frames, **kw):
    _CUR['key'] = key
    try:
        return _orig_render_frames(key, out, frames, **kw)
    finally:
        _CUR['key'] = None


def _setup_scene():
    cam = _orig_setup_scene()
    if os.environ.get('AMOSTRAS'):
        bpy.context.scene.cycles.samples = int(os.environ['AMOSTRAS'])
    return cam


_lib.frame_camera = _frame_camera
_lib.render_tower = _render_tower
_lib.render_frames = _render_frames
_lib.setup_scene = _setup_scene


# ---------------------------------------------------------------- utilidades
def thump(ph, n=2):
    """Batida do grave: 1 no tempo, cai rapido (n batidas por volta do laco)."""
    u = (ph * n) % 1.0
    return max(0.0, 1.0 - 3.2 * u) ** 2


def wpos(o, local=(0, 0, 0)):
    bpy.context.view_layer.update()
    return tuple(o.matrix_world @ Vector(local))


def front_tree(o):
    for c in [o] + list(o.children_recursive):
        if c.type == 'MESH':
            c['front'] = 1


# ---------------------------------------------------------------- alto-falante, caixa de som, corneta
def woofer(root, P, tag, loc, R, parent=None, cap=None, beat=True, n=2, ph0=0.0):
    """Alto-falante redondo virado para -Y do pai: aro, cone, borda de borracha e calota. beat: o cone bate no grave
    (anim do laco). Devolve (grupo, cone que mexe)."""
    # loc = ponto na face da caixa; o falante fica todo na frente dela (senao o cone some dentro da frente da caixa)
    z0 = 0.15 * R
    e = empty(root, tag, loc=loc, rot=(math.pi / 2, 0, 0), parent=parent)
    kids(e, cyl(root, tag + '_cesto', R, z0, (0, 0, z0 / 2), m=P['spk_rim'], v=28, bev=0.0, caps=False),
         torus(root, tag + '_aro', (0, 0, z0 + 0.004), R, 0.075 * R, P['spk_rim'], n=28, segs=5))
    mov = empty(root, tag + '_cone', parent=e)
    kids(mov, lathe(root, tag + '_conico', [(z0 - 0.13 * R, 0.16 * R, 0.16 * R), (z0 - 0.09 * R, 0.46 * R, 0.46 * R), (z0 - 0.035 * R, 0.72 * R, 0.72 * R),
                                          (z0, 0.88 * R, 0.88 * R)], P['cone'], segs=24, lv=1, caps=True, solid=0.004),
         torus(root, tag + '_borda', (0, 0, z0), 0.9 * R, 0.08 * R, P['surround'], n=28, segs=6),
         sphere(root, tag + '_calota', 0.3 * R, (0, 0, z0 - 0.07 * R), scale=(1, 1, 0.6), m=cap or P['dust'], seg=16))
    if beat:
        def fn(o, mb, ph, R=R, p0=ph0):
            k = thump(ph + p0, n)
            o.matrix_basis = mb @ Matrix.Translation((0, 0, 0.16 * R * k)) @ Matrix.Diagonal((1 + 0.1 * k, 1 + 0.1 * k, 1 + 0.6 * k, 1))
        register_anim(mov, fn)
    return e, mov


def cabinet(root, P, tag, loc, w, h, d, yaw=0.0, parent=None, shell=None, cones=None, tweet=True, beat=True, cap=None, star=0.0):
    """Caixa de som de canto arredondado, frente para -Y do grupo; loc = centro da base.
    cones: [(x, z, R)] em fracoes (x da largura, z da altura, R da menor medida). Devolve (grupo, cones que mexem)."""
    m = min(w, h)
    if cones is None:
        cones = [(0.0, 0.4, 0.36)] if w < 1.3 * h else [(-0.24, 0.44, 0.34), (0.24, 0.44, 0.34)]
    movs = []
    with grupo(root, tag, loc=loc, rot=(0, 0, yaw), parent=parent) as g:
        slab(root, tag + '_caixa', w, h, d, shell or P['spk'], r=m * 0.14, loc=(0, 0, h / 2), bev=min(0.014, d * 0.08))
        slab(root, tag + '_frente', w * 0.86, h * 0.88, 0.012, P['baffle'], r=m * 0.1, loc=(0, -d / 2 - 0.001, h / 2), bev=0.004)
        for k, (xf, zf, rf) in enumerate(cones):
            e, mv = woofer(root, P, f'{tag}_falante{k}', (xf * w, -d / 2 - 0.006, zf * h), rf * m, beat=beat, cap=cap)
            movs.append(mv)
        if star:
            estrela(root, tag + '_estrela', star, 0.012, loc=(0, -d / 2 - 0.008, h * 0.845))
        elif tweet:
            zt = h * 0.84
            slab(root, tag + '_tweeter', w * 0.36, h * 0.09, 0.016, P['spk_rim'], r=h * 0.04, loc=(0, -d / 2 - 0.008, zt), bev=0.004)
            slab(root, tag + '_tweeterBoca', w * 0.26, h * 0.045, 0.01, P['surround'], r=h * 0.02, loc=(0, -d / 2 - 0.016, zt), bev=0.002)
    return g, movs


def horn_speaker(root, P, tag, loc, yaw, pitch=0.25, s=1.0, parent=None, arcs=True, n=2, ph0=0.0):
    """Corneta de carro de som (boca larga branca, aro vermelho) apontando para o X local; arcs: as ondinhas de som na
    boca que pulsam com o grave (anim)."""
    with grupo(root, tag, loc=loc, rot=(0, -pitch, yaw), parent=parent) as g:
        h = lathe(root, tag + '_boca', [(0.0, 0.03 * s, 0.03 * s), (0.08 * s, 0.045 * s, 0.045 * s), (0.17 * s, 0.09 * s, 0.09 * s), (0.22 * s, 0.14 * s, 0.14 * s)],
                  P['horn'], segs=24, lv=1, caps=False, solid=0.012)
        h.rotation_euler = (0, math.pi / 2, 0)
        torus(root, tag + '_aro', (0.22 * s, 0, 0), 0.14 * s, 0.016 * s, P['teal'], axis='X', n=28, segs=6)
        cyl(root, tag + '_fundo', 0.045 * s, 0.01, (0.05 * s, 0, 0), rot=(0, math.pi / 2, 0), m=P['horn_k'], v=14, bev=0.0)
        cyl(root, tag + '_driver', 0.055 * s, 0.08 * s, (-0.03 * s, 0, 0), rot=(0, math.pi / 2, 0), m=P['horn_k'], v=16, bev=0.01)
    if arcs:
        wv = empty(root, tag + '_ondas', loc=(0.24 * s, 0, 0), parent=g)
        for k, r in enumerate((0.13 * s, 0.2 * s)):
            pts = [(r * math.cos(a), 0, r * math.sin(a)) for a in [-0.75 + 1.5 * t / 10 for t in range(11)]]
            kids(wv, tube(root, f'{tag}_onda{k}', pts, 0.016 * s, P['wave'], segs=6))

        def breathe(o, mb, ph, p0=ph0):
            k = 0.82 + 0.4 * thump(ph + p0, n)
            o.matrix_basis = mb @ Matrix.Diagonal((k, k, k, 1))
        register_anim(wv, breathe)
    return g


def trumpet(root, P, tag, loc, yaw, pitch=0.0, L=0.4, Rm=0.13, parent=None, beat=True, n=2, ph0=0.0):
    """Corneta dourada em forma de trompete (tubo fino que abre numa campana larga), apontando para o X local.
    beat: a campana pulsa no grave (anim). Devolve (grupo, campana que mexe)."""
    r0 = Rm * 0.2
    with grupo(root, tag, loc=loc, rot=(0, -pitch, yaw), parent=parent) as g:
        cyl(root, tag + '_motor', r0 * 2.1, L * 0.16, (L * 0.04, 0, 0), rot=(0, math.pi / 2, 0), m=P['spk_r'], v=18, bev=0.008)
        tb = lathe(root, tag + '_tubo', [(0.0, r0, r0), (0.45 * L, r0 * 1.05, r0 * 1.05), (0.62 * L, r0 * 1.5, r0 * 1.5)], P['brass'], segs=18, lv=1, caps=False)
        tb.rotation_euler = (0, math.pi / 2, 0)
        for k, x in enumerate((0.24 * L, 0.4 * L)):
            torus(root, f'{tag}_anel{k}', (x, 0, 0), r0 * 1.25, r0 * 0.35, P['brass_d'], axis='X', n=16, segs=5)
    bell = empty(root, tag + '_campana', loc=(0.62 * L, 0, 0), parent=g)
    b = lathe(root, tag + '_campanaBoca', [(0.0, r0 * 1.5, r0 * 1.5), (0.18 * L, Rm * 0.36, Rm * 0.36), (0.3 * L, Rm * 0.68, Rm * 0.68), (0.38 * L, Rm, Rm)],
              P['brass'], segs=28, lv=1, caps=False, solid=0.01)
    b.rotation_euler = (0, math.pi / 2, 0)
    kids(bell, b, torus(root, tag + '_borda', (0.38 * L, 0, 0), Rm, Rm * 0.09, P['brass_d'], axis='X', n=32, segs=6))
    if beat:
        def fn(o, mb, ph, p0=ph0):
            k = thump(ph + p0, n)
            o.matrix_basis = mb @ Matrix.Diagonal((1 + 0.18 * k, 1 + 0.12 * k, 1 + 0.12 * k, 1))
        register_anim(bell, fn)
    return g, bell


# ---------------------------------------------------------------- notas, baloes, ondas, microfone
def note(root, P, tag, loc, s=1.0, rot=(0, 0, 0), double=False, m=None, parent=None):
    """Nota musical (colcheia; double: duas ligadas) de argila no plano XZ, de frente para -Y."""
    m = m or P['note']
    with grupo(root, tag, loc=loc, rot=rot, parent=parent) as e:
        heads = [(0.0, 0.0)] + ([(0.12 * s, 0.025 * s)] if double else [])
        for k, (x, z) in enumerate(heads):
            sphere(root, f'{tag}_cabeca{k}', 0.04 * s, (x, 0, z), scale=(1.3, 0.62, 0.95), rot=(0, 0.42, 0), m=m, seg=16)
            box(root, f'{tag}_haste{k}', (0.018 * s, 0.018 * s, 0.17 * s), (x + 0.042 * s, 0, z + 0.085 * s), m=m, bev=0.006 * s)
        if double:
            p0, p1 = Vector((0.042 * s, 0, 0.165 * s)), Vector((0.162 * s, 0, 0.19 * s))
            bb = box(root, tag + '_barra', ((p1 - p0).length + 0.018 * s, 0.022 * s, 0.035 * s), tuple((p0 + p1) / 2), m=m, bev=0.008 * s)
            bb.rotation_euler = (0, -math.atan2(p1.z - p0.z, p1.x - p0.x), 0)
        else:
            tube(root, tag + '_bandeira', [(0.042 * s, 0, 0.17 * s), (0.085 * s, 0, 0.13 * s), (0.092 * s, 0, 0.075 * s)], 0.014 * s, m, segs=6,
                 rfun=lambda t: 0.016 * s * (1 - 0.5 * t))
    return e


def sound_rings(root, P, tag, loc, R, rot=(0, 0, 0), parent=None, n=2, s_th=1.0):
    """Aneis de onda de som (um vermelho e um branco por dentro) no plano XZ; crescem no grave (anim)."""
    e = empty(root, tag, loc=loc, rot=rot, parent=parent)
    kids(e, torus(root, tag + '_anel', (0, 0, 0), R, 0.016 * s_th, P['wave'], axis='Y', n=36, segs=6),
         torus(root, tag + '_anelB', (0, 0, 0), R * 0.7, 0.012 * s_th, P['wave_w'], axis='Y', n=30, segs=6))

    def fn(o, mb, ph):
        k = 0.8 + 0.35 * thump(ph, n)
        o.matrix_basis = mb @ Matrix.Diagonal((k, k, k, 1))
    register_anim(e, fn)
    return e


def hand_mic(root, P, tag):
    """Microfone de mao (ao longo do Z local, empunhadura em z = 0)."""
    return [cyl(root, tag + '_micCabo', 0.011, 0.085, (0, 0, 0.025), r2=0.015, m=P['mic_k'], v=12, bev=0.004),
            torus(root, tag + '_micAnel', (0, 0, 0.07), 0.017, 0.005, cor('pri'), n=14, segs=5),
            sphere(root, tag + '_micCabeca', 0.025, (0, 0, 0.09), m=P['mic_h'], seg=14)]


def mic_stand(root, P, tag, base, h=0.3, yaw=0.0, parent=None, s=1.0):
    """Pedestal de microfone: tripe, haste cromada, girafa inclinada para o X local e o microfone na ponta."""
    with grupo(root, tag, loc=base, rot=(0, 0, yaw), parent=parent) as g:
        for k in range(3):
            a = TAU * k / 3 + 0.5
            tube(root, f'{tag}_pe{k}', [(0, 0, 0.05 * s), (0.075 * s * math.cos(a), 0.075 * s * math.sin(a), 0.004)], 0.007 * s, P['mic_k'], segs=6)
        tube(root, tag + '_haste', [(0, 0, 0.0), (0, 0, h)], 0.009 * s, P['chrome'], segs=8)
        cyl(root, tag + '_trava', 0.016 * s, 0.03 * s, (0, 0, h), m=P['mic_k'], v=12, bev=0.004)
        tip = Vector((0.1 * s, 0, h + 0.06 * s))
        tube(root, tag + '_girafa', [(-0.05 * s, 0, h - 0.03 * s), tuple(tip)], 0.008 * s, P['chrome'], segs=8)
        d = (tip - Vector((-0.05 * s, 0, h - 0.03 * s))).normalized()
        mc = cyl(root, tag + '_micCabo', 0.013 * s, 0.07 * s, tuple(tip + d * 0.02 * s), r2=0.017 * s, m=P['mic_k'], v=12, bev=0.004)
        mc.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        head = sphere(root, tag + '_micCabeca', 0.034 * s, tuple(tip + d * 0.075 * s), m=P['mic_h'], seg=14)
        torus(root, tag + '_micAnel', tuple(tip + d * 0.05 * s), 0.02 * s, 0.007 * s, cor('pri'), n=14, segs=5)
    return g, head


def rail_loop(root, P, tag, w, d, z, r=0.04, th=0.008, m=None):
    """Corrimao fechado (retangulo de canto arredondado no plano XY) na altura z."""
    pts = [(x, y, z) for x, y in rrect(w, d, r, n=4)]
    return tube(root, tag, pts, th, m or P['chrome'], segs=6, closed=True)


# ---------------------------------------------------------------- picape do carro de som
def truck(root, P, tag, loc, yaw, s=1.0):
    """Picapinha de cabine avancada (frente para o X local): lataria vermelha com faixa e teto brancos, farois que
    acendem, estrela branca na porta e no bico, rodas gordas de brinquedo. Devolve (grupo, medidas locais)."""
    def S(*v):
        return tuple(a * s for a in v)
    with grupo(root, tag, loc=loc, rot=(0, 0, yaw)) as g:
        slab(root, tag + '_chassi', 0.86 * s, 0.15 * s, 0.4 * s, P['paint'], r=0.06 * s, loc=S(0, 0, 0.185), bev=0.02 * s)
        slab(root, tag + '_cabine', 0.32 * s, 0.3 * s, 0.39 * s, P['paint'], r=0.08 * s, loc=S(0.27, 0, 0.38), bev=0.02 * s)
        slab(root, tag + '_faixaBranca', 0.326 * s, 0.15 * s, 0.396 * s, P['paint_w'], r=0.07 * s, loc=S(0.27, 0, 0.46), bev=0.015 * s)
        slab(root, tag + '_teto', 0.34 * s, 0.05 * s, 0.41 * s, P['paint_w'], r=0.022 * s, loc=S(0.27, 0, 0.55), bev=0.01 * s)
        for k, sy in enumerate((-1, 1)):
            slab(root, f'{tag}_janela{k}', 0.2 * s, 0.1 * s, 0.012, P['glass'], r=0.025 * s, loc=S(0.255, sy * 0.199, 0.462), bev=0.003)
        slab(root, tag + '_parabrisa', 0.31 * s, 0.11 * s, 0.012, P['glass'], r=0.03 * s, loc=S(0.433, 0, 0.462), rot=(0, 0, math.pi / 2), bev=0.003)
        box(root, tag + '_parabrisaMeio', (0.014 * s, 0.016 * s, 0.11 * s), S(0.438, 0, 0.462), m=P['paint_w'], bev=0.004)
        for k, sy in enumerate((-1, 1)):
            cyl(root, f'{tag}_farol{k}', 0.038 * s, 0.02 * s, S(0.432, sy * 0.125, 0.315), rot=(0, math.pi / 2, 0), m=P['head'], v=20, bev=0.004)
            torus(root, f'{tag}_farolAro{k}', S(0.437, sy * 0.125, 0.315), 0.039 * s, 0.008 * s, P['chrome'], axis='X', n=20, segs=5)
        estrela(root, tag + '_estrelaBico', 0.045 * s, 0.014 * s, loc=S(0.437, 0, 0.31), rot=(0, 0, math.pi / 2))
        slab(root, tag + '_grade', 0.2 * s, 0.045 * s, 0.012, P['grille'], r=0.02 * s, loc=S(0.433, 0, 0.235), rot=(0, 0, math.pi / 2), bev=0.003)
        for k, sx in enumerate((-1, 1)):
            box(root, f'{tag}_parachoque{k}', S(0.05, 0.43, 0.05), S(sx * 0.44, 0, 0.135), m=P['chrome'], bev=0.018 * s)
        # rodas gordas de brinquedo (saem para fora da lataria) e o paralama escuro em arco
        for k, (xw, sy) in enumerate(((0.27, -1), (0.27, 1), (-0.27, -1), (-0.27, 1))):
            cyl(root, f'{tag}_pneu{k}', 0.1 * s, 0.085 * s, S(xw, sy * 0.2, 0.1), rot=(math.pi / 2, 0, 0), m=P['tire'], v=28, bev=0.028 * s)
            cyl(root, f'{tag}_calota{k}', 0.05 * s, 0.09 * s, S(xw, sy * 0.2, 0.1), rot=(math.pi / 2, 0, 0), m=P['hub'], v=20, bev=0.012 * s)
            sphere(root, f'{tag}_calotaMiolo{k}', 0.018 * s, S(xw, sy * 0.246, 0.1), scale=(1, 0.5, 1), m=P['grille'], seg=10)
            tube(root, f'{tag}_paralama{k}', [S(xw + 0.125 * math.cos(a), sy * 0.203, 0.1 + 0.125 * math.sin(a)) for a in [math.pi * t / 12 for t in range(13)]],
                 0.022 * s, P['grille'], segs=6)
        estrela(root, tag + '_estrelaPorta', 0.055 * s, 0.012 * s, loc=S(0.27, -0.201, 0.312))
        tube(root, tag + '_retrovisorHaste', [S(0.415, -0.19, 0.43), S(0.44, -0.235, 0.44)], 0.007 * s, P['grille'], segs=6)
        sphere(root, tag + '_retrovisor', 0.026 * s, S(0.44, -0.24, 0.455), scale=(0.6, 0.9, 1.1), m=P['paint_w'], seg=12)
        for k, sy in enumerate((-1, 1)):
            box(root, f'{tag}_lanterna{k}', S(0.014, 0.06, 0.045), S(-0.432, sy * 0.15, 0.215), m=P['led_r'], bev=0.006 * s)
        # cacamba: grade de tras e tampa (o paredao de som ocupa o resto)
        slab(root, tag + '_cacambaTras', 0.54 * s, 0.07 * s, 0.022 * s, P['paint'], r=0.02 * s, loc=S(-0.16, 0.189, 0.29), bev=0.006 * s)
        slab(root, tag + '_cacambaFrente', 0.54 * s, 0.045 * s, 0.022 * s, P['paint'], r=0.016 * s, loc=S(-0.16, -0.189, 0.28), bev=0.006 * s)
        slab(root, tag + '_tampa', 0.4 * s, 0.07 * s, 0.022 * s, P['paint'], r=0.02 * s, loc=S(-0.425, 0, 0.29), rot=(0, 0, math.pi / 2), bev=0.006 * s)
    return g, dict(s=s, bed_z=0.26 * s, bed_x=(-0.42 * s, 0.1 * s), roof_z=0.575 * s, cab_x=0.27 * s)


def paredao(root, P, tag, g, T, rows, d=0.3, x_c=None, front_y=-0.19):
    """Paredao de caixas de som na cacamba (coordenadas da picape): rows = [[(w, h), ...], ...] de baixo para cima
    (medidas em s). Frente das caixas para o lado da camera (-Y local). Devolve (topo z, centro x, cones)."""
    s = T['s']
    xc = x_c if x_c is not None else (T['bed_x'][0] + T['bed_x'][1]) / 2
    z = T['bed_z']
    dd = d * s
    yc = front_y * s + dd / 2
    movs = []
    for j, row in enumerate(rows):
        tot = sum(w for w, h in row) * s
        x = xc - tot / 2
        hh = max(h for w, h in row) * s
        for k, (w, h) in enumerate(row):
            ww = w * s
            _, mv = cabinet(root, P, f'{tag}{j}{k}', (x + ww / 2, yc + 0.006 * j, z), ww, h * s, dd - 0.012 * j, parent=g)
            movs += mv
            x += ww
        z += hh
    return z, xc, movs


def roof_deck(root, P, tag, g, T, rail=True, flag=False, banner=False):
    """Sacadinha no teto da cabine: chapa xadrez, corrimao cromado e o pedestal de microfone. Devolve (grupo, ponta do microfone local)."""
    s = T['s']
    with grupo(root, tag, loc=(T['cab_x'], 0, T['roof_z']), parent=g) as e:
        slab(root, tag + '_piso', 0.31 * s, 0.37 * s, 0.024 * s, P['deck'], r=0.04 * s, loc=(0, 0, 0.012 * s), rot=(math.pi / 2, 0, 0), bev=0.006 * s)
        if rail:
            hr = 0.13 * s
            for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1), (0, -1), (0, 1))):
                tube(root, f'{tag}_poste{k}', [(sx * 0.135 * s, sy * 0.165 * s, 0.02 * s), (sx * 0.135 * s, sy * 0.165 * s, hr)], 0.008 * s, P['chrome'], segs=6)
            rail_loop(root, P, tag + '_corrimao', 0.27 * s, 0.33 * s, hr, r=0.04 * s, th=0.009 * s)
            rail_loop(root, P, tag + '_corrimaoMeio', 0.27 * s, 0.33 * s, hr * 0.55, r=0.04 * s, th=0.006 * s)
        ms, head = mic_stand(root, P, tag + '_pedestal', (0.03 * s, -0.04 * s, 0.024 * s), h=0.26 * s, yaw=math.radians(-70), s=s)
        if banner:
            # faixa vermelha com estrela branca presa no corrimao do lado da camera (sem letras)
            slab(root, tag + '_faixa', 0.25 * s, 0.085 * s, 0.01, P['skirt'], r=0.012 * s, loc=(0, -0.172 * s, 0.085 * s), bev=0.003)
            estrela(root, tag + '_faixaEstrela', 0.032 * s, 0.008, loc=(0, -0.18 * s, 0.085 * s))
        if flag:
            with grupo(root, tag + '_bandeira', loc=(-0.135 * s, 0.165 * s, 0.02 * s)):
                bandeirinha(root, tag + '_bandeirinha', (0, 0, 0), h=0.36 * s, w=0.2 * s, fh=0.13 * s)
    return e, head


def horn_mast(root, P, tag, base, h, horns, g, s=1.0, hs=0.6, beacon=True):
    """Mastro cromado em cima do paredao com as cornetas (yaw, pitch) e o giroflex vermelho que pisca. Devolve o led."""
    led = None
    with grupo(root, tag, loc=base, parent=g) as e:
        tube(root, tag + '_haste', [(0, 0, 0), (0, 0, h)], 0.016 * s, P['chrome'], segs=10)
        cyl(root, tag + '_suporte', 0.04 * s, 0.05 * s, (0, 0, h - 0.04 * s), m=P['horn_k'], v=16, bev=0.008)
        for k, (yaw, pitch) in enumerate(horns):
            horn_speaker(root, P, f'{tag}_corneta{k}', (0.035 * s * math.cos(yaw), 0.035 * s * math.sin(yaw), h - 0.04 * s), yaw, pitch=pitch, s=hs * s,
                         arcs=abs(math.sin(yaw)) < 0.5)   # ondinhas so nas cornetas de lado (as de frente viram risco)
        if beacon:
            cyl(root, tag + '_giroBase', 0.03 * s, 0.025 * s, (0, 0, h + 0.012 * s), m=P['horn_k'], v=16, bev=0.006)
            led = empty(root, tag + '_giro', loc=(0, 0, h + 0.024 * s))
            kids(led, lathe(root, tag + '_giroLuz', [(0.0, 0.034 * s, 0.034 * s), (0.035 * s, 0.033 * s, 0.033 * s), (0.055 * s, 0.024 * s, 0.024 * s),
                                                    (0.066 * s, 0.0, 0.0)], P['giro'], segs=20, lv=1, caps=True),
                 torus(root, tag + '_giroFaixa', (0, 0, 0.004 * s), 0.035 * s, 0.006 * s, P['horn_k'], n=20, segs=5))
    if led is not None:
        pulse_anim(led, lo=0.8, hi=1.25, on=(0.0, 0.25), ph0=0.0)
    return e, led


def float_notes(root, P, tag, spots, s=1.0):
    """Notas e baloes soltos flutuando (cada um no seu ritmo): spots = (x, y, z, tipo, inclinacao),
    tipo 'n' nota, 'nn' duas notas, 'b' balao vermelho, 'bw' balao branco."""
    out = []
    for k, (x, y, z, kind, tl) in enumerate(spots):
        if kind in ('n', 'nn'):
            e = note(root, P, f'{tag}_nota{k}', (x, y, z), s=s, rot=(0, tl, 0), double=kind == 'nn', m=P['note'] if k % 3 != 2 else P['note_d'])
        else:
            e = chat_bubble(root, f'{tag}_balao{k}', (x, y, z), s=s * 1.05, rot=(0, -0.12 * tl, 0), light=kind == 'bw', tail=1 if tl >= 0 else -1)
        float_anim(e, amp=0.026, ph0=0.27 * k, sway=0.1)
        out.append(e)
    return out


def flag_lot(root, tag, x, y, h=0.34):
    m = bandeirinha(root, tag + '_bandeirinha', (x, y, G), h=h)
    m.scale = (-1, 1, 1)
    return m


# ---------------------------------------------------------------- torreta: caixa de som no pedestal (mira, bate e solta o som)
def build_pa(P, root, size=1.0, brass=False):
    """Caixa de som vermelha num pedestal (ou, brass, o buque de cornetas douradas): o eixo de mira e o X local do
    grupo 'incl' (aponta para o alvo); o cone bate e os aneis de som saem da frente no disparo."""
    tag = root['set']
    s = size
    R = 0.3 * s
    H = 0.34 * s
    piv = empty(root, tag + '_giro', rot=(0, 0, FAN_FACE))
    kids(piv, cyl(root, tag + '_base', 0.15 * s, 0.04 * s, (0, 0, 0.02 * s), r2=0.13 * s, m=P['plastic_t'], v=28, bev=0.012),
         torus(root, tag + '_baseAro', (0, 0, 0.03 * s), 0.13 * s, 0.012 * s, P['cage_d'], n=28, segs=5),
         tube(root, tag + '_haste', [(0, 0, 0.04 * s), (0, 0, 0.11 * s)], 0.026 * s, P['chrome'], segs=10))
    rec = empty(root, tag + '_recuo', loc=(0, 0, H), parent=piv)
    tilt = empty(root, tag + '_incl', parent=rec, rot=(0, math.radians(-6), 0))
    movs, bells = [], []
    if not brass:
        W, Hc, D = 0.4 * s, 0.42 * s, 0.24 * s
        xc = 0.09 * s - D / 2
        # garfo cromado: segura a caixa pelos lados (no recuo, nao inclina)
        yk = W / 2 + 0.02 * s
        zb = -H + 0.11 * s
        kids(rec, tube(root, tag + '_garfo', [(xc, -yk, 0.0), (xc, -yk, zb + 0.03 * s), (xc, -yk + 0.03 * s, zb), (xc, yk - 0.03 * s, zb), (xc, yk, zb + 0.03 * s),
                                              (xc, yk, 0.0)], 0.014 * s, P['chrome'], segs=8))
        for k, sy in enumerate((-1, 1)):
            kids(rec, cyl(root, f'{tag}_garfoTrava{k}', 0.026 * s, 0.02 * s, (xc, sy * (yk + 0.006 * s), 0.0), rot=(math.pi / 2, 0, 0), m=P['horn_k'], v=16, bev=0.004))
        cg, movs = cabinet(root, P, tag + '_caixa', (xc, 0, -Hc / 2), W, Hc, D, yaw=math.pi / 2, parent=tilt, shell=P['spk_r'],
                           cones=[(0.0, 0.36, 0.34)], beat=False, cap=P['dust_w'], star=0.058 * s)
        # alca em cima e estrela branca no lado que a camera ve
        kids(tilt, tube(root, tag + '_alca', [(xc - 0.05 * s, 0, Hc / 2), (xc - 0.04 * s, 0, Hc / 2 + 0.035 * s), (xc + 0.04 * s, 0, Hc / 2 + 0.035 * s),
                                              (xc + 0.05 * s, 0, Hc / 2)], 0.012 * s, P['horn_k'], segs=6))
        kids(tilt, estrela(root, tag + '_estrela', 0.085 * s, 0.012 * s, loc=(xc, -W / 2 - 0.006 * s, 0.01 * s)))
        for k, sz in enumerate((-1, 1)):
            for j, sx in enumerate((-1, 1)):
                kids(tilt, sphere(root, f'{tag}_quina{k}{j}', 0.022 * s, (xc + D / 2 - 0.006 * s, sx * (W / 2 - 0.02 * s), sz * (Hc / 2 - 0.02 * s)), m=P['horn_k'], seg=10))
        puff = empty(root, tag + '_sopro', parent=tilt)
        sound_arcs(root, P, tag + '_soproArcos', puff, s, (0.08, 0.15, 0.22))
    else:
        # buque de cornetas douradas num tambor vermelho
        kids(rec, tube(root, tag + '_garfo', [(-0.12 * s, 0, -H + 0.11 * s), (-0.12 * s, 0, -0.06 * s)], 0.02 * s, P['chrome'], segs=8))
        drum = cyl(root, tag + '_tambor', 0.12 * s, 0.16 * s, (-0.16 * s, 0, -0.02 * s), rot=(0, math.pi / 2, 0), m=P['spk_r'], v=28, bev=0.02 * s)
        kids(tilt, drum,
             torus(root, tag + '_tamborAro', (-0.08 * s, 0, -0.02 * s), 0.12 * s, 0.014 * s, P['brass_d'], axis='X', n=28, segs=5),
             torus(root, tag + '_tamborAroT', (-0.24 * s, 0, -0.02 * s), 0.12 * s, 0.014 * s, P['brass_d'], axis='X', n=28, segs=5))
        e = estrela(root, tag + '_estrela', 0.06 * s, 0.01 * s, loc=(-0.16 * s, -0.124 * s, -0.02 * s), rot=(0, 0, 0))
        kids(tilt, e)
        for k, (yaw, pitch, L, Rm, z) in enumerate(((0.0, 0.0, 0.36 * s, 0.15 * s, -0.02 * s), (0.42, 0.32, 0.3 * s, 0.1 * s, 0.05 * s),
                                                    (-0.42, 0.32, 0.3 * s, 0.1 * s, 0.05 * s))):
            g, b = trumpet(root, P, f'{tag}_corneta{k}', (-0.12 * s, 0, z), yaw, pitch, L=L, Rm=Rm, parent=tilt, beat=False)
            bells.append(b)
        puff = empty(root, tag + '_sopro', parent=tilt)
        sound_arcs(root, P, tag + '_soproArcos', puff, s, (0.08, 0.15))
        ne = note(root, P, tag + '_soproNota', (0, 0, 0), s=1.05 * s, double=True)
        ne.parent = puff
        ne.location = (0.0, -0.02 * s, -0.11 * s)
        ne.rotation_euler = (0, 0, -FAN_FACE)
    return {'piv': piv, 'rec': rec, 'tilt': tilt, 'movs': movs, 'bells': bells, 'puff': puff, 'R': R, 's': s, 'brass': brass}


def sound_arcs(root, P, tag, parent, s, radii):
    """Ondas de som ')))' de frente para a camera (o grupo desfaz o giro da torreta), abrindo para o lado da mira."""
    pa = empty(root, tag, parent=parent, rot=(0, 0, -FAN_FACE))
    for q, r in enumerate(radii):
        a0 = 0.95 - 0.1 * q
        pts = [(r * s * math.cos(-a0 + 2 * a0 * t / 12) - radii[0] * s, 0, r * s * math.sin(-a0 + 2 * a0 * t / 12)) for t in range(13)]
        kids(pa, tube(root, f'{tag}{q}', pts, 0.02 * s, P['wave'] if q % 2 == 0 else P['wave_w'], segs=7, rfun=lambda t: 0.014 * s + 0.016 * s * math.sin(math.pi * t)))
    return pa


def fan_points(parts, tl):
    bpy.context.view_layer.update()
    m = parts['tilt'].matrix_world @ Vector((0.09 * parts['s'], 0, 0))
    return {'points': {'muzzle': project(m, tl)}}


FAN_N = 8


def set_pump(parts, p):
    """p de 0 a 1: o cone (ou a campana) estufa no grave."""
    s = parts['s']
    for mv in parts['movs']:
        mv.matrix_basis = Matrix.Translation((0, 0, 0.03 * s * p)) @ Matrix.Diagonal((1 + 0.14 * p, 1 + 0.14 * p, 1 + 0.9 * p, 1))
    for b in parts['bells']:
        loc = b.location.copy()
        b.matrix_basis = Matrix.Translation(loc) @ Matrix.Diagonal((1 + 0.22 * p, 1 + 0.14 * p, 1 + 0.14 * p, 1))


def pose_fan(parts, f):
    """Disparo em 8 quadros: a caixa da o tranco, o cone estufa e o anel de som sai da frente, cresce e some."""
    s, R = parts['s'], parts['R']
    rec = [-0.035, -0.02, -0.01, -0.004, 0.0, 0.0, 0.0, 0.0][f] if f is not None else 0.0
    parts['rec'].location = (rec * s, 0, 0.34 * s)
    set_pump(parts, [1.0, 0.7, 0.45, 0.25, 0.12, 0.05, 0.0, 0.0][f] if f is not None else 0.0)
    k = [0.25, 0.5, 0.72, 0.88, 1.0, 1.0, 0.0, 0.0][f] if f is not None else 0.0
    x = [0.12, 0.3, 0.5, 0.68, 0.84, 0.98, 1.0, 1.0][f] if f is not None else 0.0
    parts['puff'].location = (R * (0.45 + 1.6 * x), 0, R * 0.3 * x)
    parts['puff'].scale = (k, k, k) if k > 0 else (1e-4, 1e-4, 1e-4)
    hide_tree(parts['puff'], k <= 0)


FAN_IDLE_N = 10


def pose_fan_idle(parts, f):
    """Espera (laco de 10 quadros): o grave bate duas vezes por volta, sem anel."""
    pose_fan(parts, None)
    set_pump(parts, 0.55 * thump(f / FAN_IDLE_N, 2))


def fan_spec(key, label, **kw):
    return {'key': key, 'label': label, 'build': lambda P, root: build_pa(P, root, **kw), 'boost': CREW_BOOST, 'extra': fan_points,
            'pose0': lambda parts, P, root: pose_fan(parts, None),
            'modes': [('fire', FAN_N, lambda parts, P, root, f: pose_fan(parts, f)),
                      ('idle', FAN_IDLE_N, lambda parts, P, root, f: pose_fan_idle(parts, f))]}


def fan_top(slot, size):
    """Centro da frente da caixa no posto (origem do som): o ponto 'top' da torre (o mesmo da Central do Zap)."""
    return (slot[0], slot[1], slot[2] + (0.34 + 0.02) * size * CREW_BOOST)


# ---------------------------------------------------------------- niveis 1 a 3: a picape e o paredao que cresce
CARRO_LOC = (0.1, 0.14, G)
CARRO_YAW = math.radians(-27)


def build_cv1(P, root):
    plot(root, P, 'cv1')
    g, T = truck(root, P, 'cv1_carro', CARRO_LOC, CARRO_YAW, s=0.96)
    zt, xc, _ = paredao(root, P, 'cv1_caixa', g, T, [[(0.27, 0.27), (0.27, 0.27)], [(0.36, 0.22)]])
    mast, led = horn_mast(root, P, 'cv1_mastro', (xc, 0.0, zt), 0.2 * T['s'], [(0.0, 0.25), (math.pi, 0.25)], g, s=T['s'])
    deck, tip = roof_deck(root, P, 'cv1_sacada', g, T, rail=False)
    flag_lot(root, 'cv1', -0.6, 0.3)
    float_notes(root, P, 'cv1', [(-0.5, -0.05, 0.98, 'n', 0.15), (0.52, 0.0, 0.96, 'bw', -1)])
    bpy.context.view_layer.update()
    lights = [((-0.1, -0.3, 0.42), SOM['luz'], 10.0, 1), (wpos(led), SOM['luz2'], 6.0, 1)]
    slot = (-0.1, -0.44, G)
    return {'slots': [slot], 'lights': lights, 'anim_shadow': False, 'points': {'top': fan_top(slot, 0.62)}}


def build_cv2(P, root):
    plot(root, P, 'cv2')
    g, T = truck(root, P, 'cv2_carro', CARRO_LOC, CARRO_YAW, s=1.03)
    zt, xc, _ = paredao(root, P, 'cv2_caixa', g, T, [[(0.27, 0.27), (0.27, 0.27)], [(0.25, 0.25), (0.25, 0.25)], [(0.36, 0.2)]])
    mast, led = horn_mast(root, P, 'cv2_mastro', (xc, 0.0, zt), 0.24 * T['s'], [(0.0, 0.25), (math.pi, 0.25)], g, s=T['s'])
    deck, tip = roof_deck(root, P, 'cv2_sacada', g, T, rail=True)
    flag_lot(root, 'cv2', -0.6, 0.3)
    bpy.context.view_layer.update()
    mt = wpos(tip)
    float_notes(root, P, 'cv2', [(-0.52, -0.08, 1.18, 'nn', 0.15), (mt[0] + 0.12, mt[1] - 0.12, mt[2] + 0.16, 'bw', 1), (0.58, -0.1, 1.2, 'n', -0.2)])
    lights = [((-0.1, -0.32, 0.5), SOM['luz'], 12.0, 1), (wpos(led), SOM['luz2'], 6.0, 1)]
    slot = (-0.14, -0.46, G)
    return {'slots': [slot], 'lights': lights, 'anim_shadow': False, 'points': {'top': fan_top(slot, 0.74)}}


def build_cv3(P, root):
    plot(root, P, 'cv3')
    g, T = truck(root, P, 'cv3_carro', CARRO_LOC, CARRO_YAW, s=1.1)
    zt, xc, _ = paredao(root, P, 'cv3_caixa', g, T, [[(0.27, 0.28), (0.27, 0.28)], [(0.26, 0.26), (0.26, 0.26)], [(0.24, 0.24), (0.24, 0.24)],
                                                    [(0.36, 0.2)]])
    mast, led = horn_mast(root, P, 'cv3_mastro', (xc, 0.0, zt), 0.26 * T['s'], [(0.0, 0.25), (math.pi, 0.25), (-math.pi / 2, 0.3), (math.pi / 2, 0.3)], g,
                          s=T['s'])
    deck, tip = roof_deck(root, P, 'cv3_sacada', g, T, rail=True, banner=True, flag=True)
    bpy.context.view_layer.update()
    mt = wpos(tip)
    float_notes(root, P, 'cv3', [(-0.56, -0.1, 1.3, 'nn', 0.15), (mt[0] + 0.14, mt[1] - 0.12, mt[2] + 0.18, 'bw', 1), (0.6, -0.12, 1.32, 'n', -0.2),
                                 (-0.36, -0.2, 1.62, 'b', -1)])
    lights = [((-0.1, -0.34, 0.6), SOM['luz'], 14.0, 1), (wpos(led), SOM['luz2'], 6.0, 1)]
    slot = (-0.2, -0.48, G)
    return {'slots': [slot, (0.5, -0.58, G)], 'lights': lights, 'anim_shadow': False, 'points': {'top': fan_top(slot, 0.84)}}


# ---------------------------------------------------------------- Comicio na Praca: palanque, torres de som, painel com a
# estrela, pulpito cheio de microfones e o redemoinho do discurso que nao acaba
def speaker_tower(root, P, tag, x, y, yaw, flip=1):
    """Torre de som: tres caixas empilhadas no chao, a trelica e o 'line array' pendurado que curva para baixo."""
    with grupo(root, tag, loc=(x, y, G), rot=(0, 0, yaw)) as g:
        z = 0.0
        for k, (w, h) in enumerate(((0.3, 0.3), (0.27, 0.27), (0.25, 0.25))):
            cabinet(root, P, f'{tag}_caixa{k}', (0, 0.006 * k, z), w, h, 0.26 - 0.01 * k, beat=True)
            z += h
        # trelica (dois tubos com zigue-zague) subindo atras das caixas
        top = 1.42
        for k, sx in enumerate((-1, 1)):
            tube(root, f'{tag}_trelica{k}', [(sx * 0.07, 0.11, z - 0.05), (sx * 0.07, 0.11, top)], 0.014, P['truss'], segs=6)
        zz = [z - 0.05 + (top - z + 0.05) * t / 8 for t in range(9)]
        pts = [((-0.07 if i % 2 == 0 else 0.07), 0.11, zz[i]) for i in range(9)]
        tube(root, tag + '_trelicaZ', pts, 0.008, P['truss'], segs=5)
        box(root, tag + '_trelicaTopo', (0.22, 0.05, 0.05), (0, 0.06, top + 0.02), m=P['truss'], bev=0.01)
        # line array: quatro caixas finas penduradas, cada uma um pouco mais inclinada
        zc = top - 0.04
        for k in range(4):
            tilt = 0.08 + 0.12 * k
            h = 0.09
            zc -= h * 0.98
            with grupo(root, f'{tag}_array{k}', loc=(0, -0.005 * k, zc), rot=(-tilt, 0, 0)):
                slab(root, f'{tag}_array{k}_caixa', 0.3, h, 0.17, P['spk'], r=0.02, loc=(0, 0, 0), bev=0.006)
                slab(root, f'{tag}_array{k}_grade', 0.27, h * 0.66, 0.008, P['baffle'], r=0.012, loc=(0, -0.088, 0), bev=0.002)
                for j, sx in enumerate((-1, 1)):
                    sphere(root, f'{tag}_array{k}_cone{j}', 0.026, (sx * 0.08, -0.092, 0), scale=(1, 0.35, 1), m=P['dust'], seg=12)
        tube(root, tag + '_cabos', [(0.0, 0.0, top), (0.0, 0.0, zc + 0.36)], 0.006, P['grille'], segs=5)
    return g


def lectern(root, P, tag, loc):
    """Pulpito vermelho com a estrela branca e o buque de microfones nas hastes (o lugar do discurso)."""
    with grupo(root, tag, loc=loc) as g:
        prism = prism_xz(root, tag + '_corpo', rrect(0.2, 0.3, 0.03, n=3, cz=0.15), 0.14, P['spk_r'], bev=0.012)
        box(root, tag + '_tampo', (0.25, 0.18, 0.03), (0, 0.01, 0.31), rot=(0.25, 0, 0), m=P['spk'], bev=0.01)
        estrela(root, tag + '_estrela', 0.07, 0.012, loc=(0, -0.076, 0.16))
        mics = [(-0.07, -0.25, 0.1), (-0.03, -0.1, 0.13), (0.01, 0.06, 0.14), (0.05, 0.2, 0.12), (0.08, 0.34, 0.09)]
        for k, (x, a, h) in enumerate(mics):
            p0 = Vector((x, -0.05, 0.32))
            p1 = p0 + Vector((math.sin(a) * 0.05, -0.06, h))
            p2 = p1 + Vector((math.sin(a) * 0.02, -0.05, 0.0))
            tube(root, f'{tag}_haste{k}', [tuple(p0), tuple(p1), tuple(p2)], 0.006, P['mic_k'], segs=5)
            sphere(root, f'{tag}_mic{k}', 0.022, tuple(p2 + Vector((0, -0.012, 0))), m=P['mic_h'] if k % 2 == 0 else cor('pri'), seg=12)
    front_tree(g)
    return g


def build_cvT(P, root):
    plot(root, P, 'cvT')
    lights = []
    # palanque: saia vermelha com estrelas, tablado de madeira
    slab(root, 'cvT_palcoSaia', 1.06, 0.52, 0.17, P['skirt'], r=0.08, loc=(0, 0.17, G + 0.085), rot=(math.pi / 2, 0, 0), bev=0.02)
    slab(root, 'cvT_palcoTablado', 1.1, 0.56, 0.04, P['wood_s'], r=0.08, loc=(0, 0.17, G + 0.19), rot=(math.pi / 2, 0, 0), bev=0.012)
    for k, x in enumerate((-0.32, 0.0, 0.32)):
        estrela(root, f'cvT_palcoEstrela{k}', 0.05, 0.01, loc=(x, 0.17 - 0.265, G + 0.085))
    zp = G + 0.21
    for k in range(2):
        box(root, f'cvT_degrau{k}', (0.18, 0.09, 0.07 + 0.07 * k), (0.34, -0.24 + 0.085 * k, G + (0.07 + 0.07 * k) / 2), m=P['wood_s'], bev=0.01)
    # painel do fundo: trelica, pano vermelho com borda branca e a estrela grande
    yb = 0.4
    for k, sx in enumerate((-1, 1)):
        tube(root, f'cvT_poste{k}', [(sx * 0.47, yb + 0.03, zp), (sx * 0.47, yb + 0.03, zp + 1.08)], 0.022, P['truss'], segs=8)
    tube(root, 'cvT_travessa', [(-0.5, yb + 0.03, zp + 1.06), (0.5, yb + 0.03, zp + 1.06)], 0.026, P['truss'], segs=8)
    slab(root, 'cvT_painelBorda', 0.9, 0.98, 0.02, P['cloth_w'], r=0.04, loc=(0, yb + 0.012, zp + 0.53), bev=0.006)
    slab(root, 'cvT_painel', 0.82, 0.9, 0.02, P['skirt'], r=0.03, loc=(0, yb, zp + 0.53), bev=0.006)
    estrela(root, 'cvT_painelEstrela', 0.3, 0.02, loc=(0, yb - 0.014, zp + 0.55))
    # refletores na travessa (acendem a noite)
    dl = Vector((0, -math.sin(math.radians(110)), math.cos(math.radians(110))))
    for k, x in enumerate((-0.3, 0.3)):
        c0 = Vector((x, yb - 0.03, zp + 1.03))
        cyl(root, f'cvT_refletor{k}', 0.045, 0.08, tuple(c0), rot=(math.radians(110), 0, 0), m=P['spk'], v=16, bev=0.008)
        cyl(root, f'cvT_refletorLuz{k}', 0.037, 0.01, tuple(c0 + dl * 0.042), rot=(math.radians(110), 0, 0), m=P['spot'], v=16, bev=0.0)
    for k, sx in enumerate((-1, 1)):
        with grupo(root, f'cvT_bandeira{k}', loc=(sx * 0.47, yb + 0.03, zp + 1.08)):
            bf = bandeirinha(root, f'cvT_bandeira{k}_b', (0, 0, 0), h=0.26, w=0.18, fh=0.12)
            if sx < 0:
                bf.scale = (-1, 1, 1)
    # torres de som dos dois lados, viradas para a plateia
    speaker_tower(root, P, 'cvT_torreE', -0.63, 0.12, math.radians(-14))
    speaker_tower(root, P, 'cvT_torreD', 0.63, 0.12, math.radians(14))
    lectern(root, P, 'cvT_pulpito', (0.0, 0.04, zp))
    # redemoinho do discurso: tres bracos em espiral (fita branca) com notas, baloes de '...' e aneis (gira)
    zc = G + 0.1 + 1.16 + 0.4
    tw = empty(root, 'cvT_redemoinho', loc=(0, 0.06, zc))
    for j in range(3):
        pts = []
        for k in range(30):
            t = k / 29
            a = TAU * 1.6 * t + j * TAU / 3
            r = 0.06 + 0.26 * t
            pts.append((r * math.cos(a), r * math.sin(a), -0.62 + 1.34 * t))
        kids(tw, tube(root, f'cvT_fita{j}', pts, 0.012, P['wave_w'], segs=5, rfun=lambda t: 0.004 + 0.012 * t))
        for i, t in enumerate((0.36, 0.64, 0.92)):
            a = TAU * 1.6 * t + j * TAU / 3
            r = 0.06 + 0.26 * t
            p = (r * math.cos(a), r * math.sin(a), -0.62 + 1.34 * t + 0.04)
            kind = (i + j) % 3
            if kind == 0:
                b = chat_bubble(root, f'cvT_balao{j}{i}', p, s=0.8 + 0.3 * t, rot=(0, 0.2 * (i - 1), a + math.pi / 2), light=j % 2 == 1, tail=1 if i % 2 else -1,
                                both=True, d=0.09)
            elif kind == 1:
                b = note(root, P, f'cvT_nota{j}{i}', p, s=0.9 + 0.4 * t, rot=(0, 0.2, a + math.pi / 2), double=j == 0)
                b2 = note(root, P, f'cvT_notaB{j}{i}', (0, 0, 0), s=0.9 + 0.4 * t, rot=(0, -0.2, math.pi), double=j == 0)
                b2.parent = b
            else:
                b = empty(root, f'cvT_onda{j}{i}', loc=p, rot=(0, 0, a + math.pi / 2))
                for q, rr in enumerate((0.07, 0.11)):
                    for sd in (-1, 1):
                        a0 = -0.8 if sd > 0 else math.pi - 0.8
                        kids(b, tube(root, f'cvT_onda{j}{i}_{q}{sd}', [(rr * math.cos(a0 + 1.6 * u / 8), 0, rr * math.sin(a0 + 1.6 * u / 8)) for u in range(9)],
                                     0.014, P['wave'], segs=5))
            b.parent = tw
            b.location = p
    register_anim(tw, spin('Z', sym=3, turns=-1))
    lights.append(((0.0, -0.2, zp + 0.5), SOM['luz'], 12.0, 1))
    lights.append(((0.0, 0.06, zc + 0.3), SOM['luz2'], 8.0, 1))
    return {'slots': [(0.56, -0.6, G)], 'lights': lights, 'anim_shadow': False, 'points': {'top': (0.0, 0.06, zc + 0.34)}}


# ---------------------------------------------------------------- Jingle Chiclete: a picape com o buque de cornetas
# douradas tocando e a fila de notas que gruda (sai da corneta grande, sobe e faz a curva)
def smooth_path(pts, n=60):
    """Curva suave (Catmull-Rom) pelos pontos de controle: devolve n pontos."""
    P_ = [Vector(p) for p in pts]
    P_ = [P_[0] * 2 - P_[1]] + P_ + [P_[-1] * 2 - P_[-2]]
    out = []
    segs = len(P_) - 3
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(segs - 1, int(u))
        t = u - k
        p0, p1, p2, p3 = P_[k], P_[k + 1], P_[k + 2], P_[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out


def build_cvS(P, root):
    plot(root, P, 'cvS')
    lights = []
    g, T = truck(root, P, 'cvS_carro', (0.14, 0.15, G), math.radians(-25), s=1.05)
    s = T['s']
    bz = T['bed_z']
    xc = (T['bed_x'][0] + T['bed_x'][1]) / 2
    # caixa amplificadora vermelha na cacamba, com dois alto-falantes de frente, e a coluna que segura o buque
    cabinet(root, P, 'cvS_ampli', (xc, -0.045 * s, bz), 0.52 * s, 0.22 * s, 0.3 * s, parent=g, shell=P['spk_r'],
            cones=[(-0.26, 0.48, 0.38), (0.26, 0.48, 0.38)], tweet=False, cap=P['dust_w'])
    zb = bz + 0.22 * s
    hub = (xc, -0.02 * s, zb + 0.2 * s)
    with grupo(root, 'cvS_coluna', loc=(0, 0, 0), parent=g):
        cyl(root, 'cvS_colunaTubo', 0.05 * s, 0.2 * s, (hub[0], hub[1], zb + 0.1 * s), m=P['spk'], v=20, bev=0.01)
        sphere(root, 'cvS_cubo', 0.085 * s, hub, m=P['spk_r'], seg=20)
        estrela(root, 'cvS_cuboEstrela', 0.05 * s, 0.01, loc=(hub[0], hub[1] - 0.088 * s, hub[2]))
    # buque de cornetas douradas em forma de trompete (yaw e pitch na picape, comprimento, boca)
    horns = [(math.pi - 0.3, 0.55, 0.56, 0.19),   # a grande: para tras, para a esquerda e para cima (dela sai a fita)
             (2.0, 1.05, 0.44, 0.14),             # para tras e para cima
             (0.15, 0.75, 0.46, 0.15),            # para a frente e para cima
             (1.2, 1.2, 0.4, 0.13),               # quase em pe
             (-1.25, 0.55, 0.4, 0.14)]            # para o lado da camera
    big = None
    for k, (yaw, pitch, L, Rm) in enumerate(horns):
        hg, bell = trumpet(root, P, f'cvS_corneta{k}', hub, yaw, pitch, L=L * s, Rm=Rm * s, parent=g, ph0=0.0)
        if k == 0:
            big = bell
    deck, head = roof_deck(root, P, 'cvS_sacada', g, T, rail=True, flag=True)
    bpy.context.view_layer.update()
    # a fita do jingle (pauta de tres linhas) sai da boca da corneta grande, sobe e faz a curva por cima do carro;
    # as notas e um balao de '...' vao grudados nela (cada um no seu tempo: onda)
    mouth = Vector(wpos(big, (0.4 * 0.56 * s, 0, 0)))
    ctrl = [mouth + Vector((-0.04, -0.02, 0.06)), Vector((-0.64, 0.08, 1.36)), Vector((-0.42, -0.04, 1.7)), Vector((-0.04, -0.08, 1.76)),
            Vector((0.3, -0.1, 1.6)), Vector((0.58, -0.1, 1.7)), Vector((0.7, -0.1, 1.88))]
    path = smooth_path(ctrl, 70)
    for q, dz in enumerate((-0.04, 0.0, 0.04)):
        tube(root, f'cvS_pauta{q}', [tuple(p + Vector((0, 0, dz))) for p in path], 0.009, P['wave_w'], segs=6,
             rfun=lambda t: 0.004 + 0.008 * math.sin(math.pi * min(1.0, t * 1.15)))
    spots = [(0.18, 'nn'), (0.34, 'n'), (0.5, 'b'), (0.64, 'nn'), (0.8, 'n'), (0.94, 'bw')]
    for k, (t, kind) in enumerate(spots):
        p = path[int(t * (len(path) - 1))] + Vector((0, -0.03, 0.02))
        if kind in ('n', 'nn'):
            e = note(root, P, f'cvS_fila{k}', tuple(p + Vector((-0.04, 0, -0.06))), s=1.3, rot=(0, 0.15 * (k % 3 - 1), 0), double=kind == 'nn',
                     m=P['note'] if k != 4 else P['note_d'])
        else:
            e = chat_bubble(root, f'cvS_fila{k}', tuple(p), s=1.0, light=kind == 'bw', tail=-1 if k % 2 else 1, rot=(0, 0.1, 0))
        float_anim(e, amp=0.024, ph0=-0.16 * k, sway=0.08)
    lights.append(((0.06, -0.12, 0.8), SOM['luz'], 14.0, 1))
    slot = (-0.26, -0.46, G)
    return {'slots': [slot, (0.36, -0.62, G)], 'lights': lights, 'anim_shadow': False, 'points': {'top': fan_top(slot, 1.0)}}


# ---------------------------------------------------------------- tripulacao do comicio
def cap_bill(root, pr, tag, m):
    """Aba do bone (no pivo da cabeca, para a frente)."""
    o = cyl(root, tag + '_aba', 0.06, 0.01, (0, 0, 0), m=m, v=18, bev=0.003)
    o.parent = pr['head']
    o.location = HC + Vector((0.07, 0, 0.045))
    o.scale = (1.15, 0.95, 1)
    o.rotation_euler = (0, -0.18, 0)
    return o


def megaphone(root, P, tag):
    """Megafone: a mao segura o gargalo (z = 0) e o cone branco de aro vermelho abre para +Z local (grip = para onde fala)."""
    out = [lathe(root, tag + '_megaCone', [(-0.03, 0.022, 0.022), (0.02, 0.03, 0.03), (0.07, 0.05, 0.05), (0.12, 0.076, 0.076)], P['horn'], segs=22, lv=1,
                 caps=False, solid=0.008)]
    out.append(torus(root, tag + '_megaAro', (0, 0, 0.12), 0.076, 0.011, cor('pri'), n=24, segs=5))
    out.append(cyl(root, tag + '_megaFundo', 0.028, 0.04, (0, 0, -0.045), m=cor('pri'), v=16, bev=0.008))
    return out


def hand_flag(root, P, tag):
    """Bandeirinha de mao da chapa (mastro no Z local)."""
    with grupo(root, tag + '_bandeiraMao', loc=(0, 0, -0.03)) as e:
        bandeirinha(root, tag + '_bandeiraMao_b', (0, 0, 0), h=0.2, w=0.13, fh=0.085)
    return [e]


def build_militante(P, root):
    """Militante do comicio: camiseta vermelha com estrela branca, jeans, tenis branco, bone vermelho e o microfone."""
    tag = root['set']
    shirt = cor('camisa')
    pants = cor('calca')
    pr = build_person(P, root, tag, dict(tunic=shirt, head='cap', head_m=cor('bone'),
                                         belt=mat('cinto_zap', '#3a2a22', rough=0.6, var=0, bump=0.04), skirt_m=pants, pants=pants,
                                         boot_m=mat('tenis_branco', '#f4f4f0', rough=0.5, var=0, bump=0.02), boot_cuff=pants, sleeve=shirt, bare_hands=True))
    cap_bill(root, pr, tag, cor('bone'))
    marca_peito(root, pr, tag)
    badge_lanyard(root, pr, tag, cor('gola'))
    hold(pr, 'R', *hand_mic(root, P, tag))
    return pr


def build_puxador(P, root):
    """Puxador do jingle: camiseta vermelha com estrela, bone branco, oculos escuros, megafone e bandeirinha da chapa."""
    tag = root['set']
    shirt = cor('pri', rough=0.85, sheen=0.3)
    black = cloth_mat('calca_preta_zap', '#2c2f36', sheen=0.1)
    pr = build_person(P, root, tag, dict(tunic=shirt, head='cap', head_m=cor('sec', rough=0.85, sheen=0.3), belt=None, skirt_m=black, pants=black,
                                         boot_m=mat('tenis_verde', '#f4f4f0', rough=0.5, var=0, bump=0.02), boot_cuff=black, sleeve=shirt, bare_hands=True,
                                         hair_m=mat('cabelo_zap', '#2a1a10', rough=0.7, var=0.03, bump=0.25)))
    cap_bill(root, pr, tag, cor('sec', rough=0.85, sheen=0.3))
    marca_peito(root, pr, tag)
    glasses(root, pr, tag, mat('lente_escura_zap', '#141418', rough=0.15, var=0, bump=0), dark=True)
    hold(pr, 'R', *megaphone(root, P, tag))
    hold(pr, 'L', *hand_flag(root, P, tag))
    return pr


IDLE_N, ACT_N = 12, 8


def militante_state(mode, f):
    """idle: fala no microfone e gesticula com a outra mao; act: ergue o punho e solta o grito (e volta)."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        t = math.sin(TAU * 2 * ph)
        return dict(hand_R=(0.13, -0.05, 0.43 + 0.006 * t), grip_R=(-0.15, 0.45, 1.0), hand_L=(0.15, 0.12, 0.33 + 0.05 * max(0.0, s)),
                    grip_L=(0.6, 0.2, 1.0), breathe=s, head_yaw=-0.1 + 0.08 * s, head_pitch=0.02 + 0.06 * t, ph=ph)
    k = math.sin(math.pi * min(1.0, f / 4))
    return dict(hand_R=(0.13 + 0.02 * k, -0.05, 0.43 + 0.02 * k), grip_R=(-0.15 + 0.2 * k, 0.45, 1.0), hand_L=(0.1 + 0.02 * k, 0.13 + 0.02 * k, 0.33 + 0.26 * k),
                grip_L=(0.4, 0.2, 1.0), lean=-0.06 * k, head_pitch=0.02 - 0.3 * k, head_yaw=0.0, ph=f / ACT_N)


def puxador_state(mode, f):
    """idle: megafone no peito e a bandeirinha balancando no ritmo; act: megafone na boca e a bandeirinha la em cima."""
    if mode == 'idle':
        ph = f / IDLE_N
        s = math.sin(TAU * ph)
        t = math.sin(TAU * 2 * ph)
        return dict(hand_R=(0.13, -0.12, 0.31 + 0.01 * t), grip_R=(0.9, -0.3, -0.55), hand_L=(0.09, 0.15, 0.36 + 0.015 * t), grip_L=(0.35 * s, 0.25, 1.0),
                    breathe=s, head_pitch=0.08 + 0.05 * t, head_yaw=0.12 * s, ph=ph)
    k = math.sin(math.pi * min(1.0, f / 4))
    return dict(hand_R=(0.12 + 0.03 * k, -0.12 + 0.08 * k, 0.3 + 0.2 * k), grip_R=(0.9 + 0.1 * k, -0.3 + 0.2 * k, -0.55 + 0.8 * k), hand_L=(0.08, 0.15, 0.36 + 0.1 * k),
                grip_L=(0.25 * k, 0.3, 1.0), lean=-0.05 * k, head_pitch=0.08 - 0.2 * k, ph=f / ACT_N)


def crew(key, label, builder, statefn):
    def pose(parts, P, root, f, mode):
        pose_person(parts, P, root, statefn(mode, f))
    return {'key': key, 'label': label, 'build': builder, 'boost': CREW_BOOST,
            'pose0': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'show': lambda parts, P, root: pose(parts, P, root, 0, 'idle'),
            'modes': [('idle', IDLE_N, lambda parts, P, root, f: pose(parts, P, root, f, 'idle')),
                      ('act', ACT_N, lambda parts, P, root, f: pose(parts, P, root, f, 'act'))]}


SPEC = {
    'show_crew': {'cv1': ['cvH1'], 'cv2': ['cvH2'], 'cv3': ['cvH3', 'cvM'], 'cvT': ['cvM'], 'cvS': ['cvHS', 'cvO']},
    'towers': [('cv1', 'Carro de Som N1', build_cv1), ('cv2', 'Carro de Som N2', build_cv2), ('cv3', 'Carro de Som N3', build_cv3),
               ('cvT', 'Comicio na Praca', build_cvT), ('cvS', 'Jingle Chiclete', build_cvS)],
    'crews': [crew('cvM', 'Militante do microfone', build_militante, militante_state), crew('cvO', 'Puxador do jingle', build_puxador, puxador_state)],
    'turrets': [fan_spec('cvH1', 'Caixa de som N1', size=0.62), fan_spec('cvH2', 'Caixa de som N2', size=0.74),
                fan_spec('cvH3', 'Caixa de som N3', size=0.84), fan_spec('cvHS', 'Cornetas do jingle', size=1.0, brass=True)],
}


if __name__ == '__main__':
    main(FAM, SPEC)
