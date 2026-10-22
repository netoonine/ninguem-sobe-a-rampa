"""Unidades aliadas de "Guardioes da Mata" (heroina Jaci, guardioes da Palafita, lanceiros, mateiros, guardioes do rio e
mercenarios do Barco-Feira) a partir de modelos 3D tirados de desenhos no estilo do conceito.

Mesmo caminho dos inimigos (tools/blender/inimigos_glb.py: importa o GLB, enxuga, esqueleto de bipede, anima por codigo),
com modos proprios: r q u e d andando (a unidade parada usa e_00), a ataque, x queda e, so na heroina, g o Giro do Facao.
GLB em arte/modelos/unidades/<tipo>.glb; quadros em arte/render/unidades/<tipo>/; empacotar com
python3 tools/sprites/empacotar_inimigos.py --unidades

Andar (r q u e d) em 5 direcoes, como os inimigos (inimigos_glb.DIRS).

uso: Blender -b -P tools/blender/unidades_glb.py -- render arte/render/unidades [tipos]
     Blender -b -P tools/blender/unidades_glb.py -- prova pasta [tipos]
     Blender -b -P tools/blender/unidades_glb.py -- vitrine arte/render/vitrine hero caipora benzedeira boitata
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib
import inimigos_glb as G

G.MODELOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'arte', 'modelos', 'unidades')
FAM = 'unidades'
ATK_N, DIE_N, GIRO_N = 6, 8, 8
IDLE_N, CHEGA_N = 32, 12   # espera (laco de ~2,7 s a 12 qps) e chegada na vitrine dos herois

# ph: altura na tela (BU, vista r); unidades do tamanho dos inimigos medios (guardiao ~25 do jogo, Jaci ~32)
CFG = {
    'hero':    dict(label='Jaci', plan='biped', ph=0.78, hip=0.40, shoulder=0.62, neck=0.66, show=-35.0, arm=0.4, ergue=1.8, espera='jaci'),
    'soldier': dict(label='Guardiao', plan='biped', ph=0.62, hip=0.38, shoulder=0.60, neck=0.64, show=-35.0, arm=0.35, ergue=1.8),
    'lancers': dict(label='Lanceiro', plan='biped', ph=0.68, hip=0.36, shoulder=0.58, neck=0.62, show=-35.0, arm=0.3, ergue=1.4),
    'monks':   dict(label='Mateiro', plan='biped', ph=0.62, hip=0.40, shoulder=0.62, neck=0.66, show=-35.0, arm=0.3, ergue=1.6),
    'rider':   dict(label='Guardiao do Rio', plan='biped', ph=0.66, hip=0.38, shoulder=0.60, neck=0.64, show=-35.0, arm=0.3, ergue=1.6),
    'merc':    dict(label='Mercenario', plan='biped', ph=0.70, hip=0.36, shoulder=0.60, neck=0.64, show=-35.0, arm=0.3, ergue=1.8),
    # herois novos: Caipora, Benzedeira (saia longa: passo curto) e o Boitata liberto (modelo do inimigo, cores naturais)
    'caipora':    dict(label='Caipora', plan='biped', ph=0.76, hip=0.40, shoulder=0.60, neck=0.64, show=-35.0, arm=0.35, ergue=1.8, espera='caipora'),
    'benzedeira': dict(label='Benzedeira', plan='biped', ph=0.68, hip=0.36, shoulder=0.60, neck=0.66, show=-35.0, arm=0.25, ergue=1.2, passo=0.2, joelho=0.3, espera='benz'),
    'boitata':    dict(label='Boitata', plan='serpent', ph=0.95, yaw=90.0, coil=0.30, show=-35.0, glow_hue='fogo', liberto=True, espera='boitata'),
}


def pose_giro(parts, f):
    """Giro do Facao: volta inteira com os bracos abertos e o corpo inclinado."""
    arm = parts['arm']
    G.reset(arm)
    t = f / GIRO_N
    G.place(parts, 'r', (0, 0, 0.01 * math.sin(math.pi * 2 * t)))
    parts['body'].rotation_euler.z += math.tau * t
    for nm, s in (('L', 1), ('R', -1)):
        G.turn(arm, 'braco' + nm, (G.X, s * 1.3), (G.Y, -0.2))
        G.turn(arm, 'antebraco' + nm, (G.X, s * 0.2))
    G.turn(arm, 'peito', (G.Y, 0.12))


def janela(t, a, b, r=0.1):
    """0 fora de [a, b], sobe e desce suave em r nas bordas."""
    return G.smooth01((t - a) / r) * G.smooth01((b - t) / r)


def torce(arm, n, ang):
    """Torce o osso em torno do proprio eixo (por cima do giro ja posto)."""
    b = G.pb(arm, n)
    if b:
        b.rotation_quaternion = b.rotation_quaternion @ G.Quaternion((0, 1, 0), ang)


def pose_espera(parts, f, n=IDLE_N, chega=False):
    """Espera parada (laco de n quadros) na vista sudeste: respira, troca o peso, olha em volta e faz o gesto do
    personagem. chega=True: a chegada da vitrine (gesto grande que volta ao quadro 0 da espera)."""
    arm, cfg = parts['arm'], parts['cfg']
    G.reset(arm)
    est = cfg.get('espera', 'base')
    t = f / n
    a = math.tau * (0.0 if chega else t)
    k = math.sin(math.pi * t) if chega else 0.0
    R = {}
    add = lambda b, ax, ang: R.setdefault(b, []).append((ax, ang))
    z = 0.0
    if cfg['plan'] == 'serpent':
        neck = parts['info']['neck']
        olhar = 0.0 if chega else 0.3 * (janela(t, 0.15, 0.45) - janela(t, 0.55, 0.85))
        # a base do pescoco mexe menos (dobrava junto do enrolado)
        for i, nm in enumerate(neck):
            add(nm, G.X, (0.07 + 0.04 * i) * math.sin(a - i * 0.7))
            add(nm, G.Y, 0.06 * math.sin(2 * a - i) - 0.1 * k)
        add('cabeca', G.Z, olhar)
        add('cabeca', G.Y, 0.08 * math.sin(2 * a) - 0.15 * k)
        add('enrolado', G.Z, 0.04 * math.sin(a))
        G.place(parts, 'we')
        for b, rots in R.items():
            G.turn(arm, b, *rots)
        G.grow(arm, 'enrolado', 1.0 + 0.04 * math.sin(2 * a))
        return
    sway, resp = math.sin(a), math.sin(2 * a)
    # peso de uma perna para a outra (quadril inclina, coxas compensam) e respiracao no peito
    add('quadril', G.X, 0.035 * sway)
    for nm in ('L', 'R'):
        add('coxa' + nm, G.X, -0.035 * sway)
    add('peito', G.X, -0.02 * sway)
    add('peito', G.Y, 0.025 * resp)
    olhar = 0.0 if chega else (0.18 if est == 'benz' else 0.28) * (janela(t, 0.1, 0.4) - janela(t, 0.52, 0.82))
    add('cabeca', G.Z, olhar)
    add('cabeca', G.X, 0.04 * sway)
    add('cabeca', G.Y, -0.03 * resp)
    for nm, s in (('L', 1), ('R', -1)):
        add('braco' + nm, G.Y, 0.04 * math.sin(2 * a + s))
        add('antebraco' + nm, G.Y, -0.08 - 0.03 * resp)
    if est == 'jaci':
        # ergue o facao, confere o fio virando o punho e baixa
        g = 0.0 if chega else janela(t, 0.3, 0.72, 0.12)
        add('bracoR', G.Y, -0.8 * g - 1.8 * k)
        add('antebracoR', G.Y, -1.2 * g - 0.4 * k)
        add('bracoL', G.X, 0.3 * k)
        add('peito', G.Y, -0.12 * k)
        add('cabeca', G.Z, -0.25 * g)
        add('cabeca', G.Y, -0.08 * k + 0.12 * g)
    elif est == 'caipora':
        # pulinhos nos calcanhares e o cajado batendo no chao
        z = 0.006 * max(0.0, math.sin(4 * a)) + 0.04 * k
        add('cabeca', G.X, 0.05 * math.sin(4 * a))
        g = 0.0 if chega else janela(t, 0.45, 0.8, 0.08)
        bate = abs(math.sin(math.pi * 3 * max(0.0, min(1.0, (t - 0.45) / 0.35))))
        add('bracoR', G.Y, -0.35 * g * bate - 1.4 * k)
        add('bracoL', G.X, 0.6 * k)
    elif est == 'benz':
        # balanco lento do corpo e o mao de ervas abanando
        add('peito', G.Z, 0.05 * sway)
        g = 0.0 if chega else janela(t, 0.25, 0.85)
        add('bracoR', G.Y, -0.2 * g - 0.55 * k)
        add('antebracoR', G.Z, 0.3 * g * math.sin(6 * math.pi * t))
        add('antebracoL', G.Y, -0.1 * sway)
        add('peito', G.Y, 0.08 * k)
        add('cabeca', G.Y, 0.12 * k)
    G.place(parts, 'we', (0, 0, z))
    for b, rots in R.items():
        G.turn(arm, b, *rots)
    G.grow(arm, 'peito', 1.0 + 0.012 * resp)
    if est == 'jaci' and not chega:
        torce(arm, 'antebracoR', 0.9 * janela(t, 0.38, 0.62, 0.08) * math.sin(4 * math.pi * (t - 0.38)))


def item(key):
    cfg = CFG[key]
    G.CFG[key] = cfg
    pose = G.POSES[cfg['plan']]
    # andar nas 5 direcoes (o jogo espelha as outras 3); ataque de lado, queda na vista antiga
    ms = G.walk_modes(pose) + [('a', ATK_N, lambda parts, P, root, f: pose(parts, 'atk', f, 'wr')),
                               ('x', DIE_N, lambda parts, P, root, f: pose(parts, 'die', f, 'r'))]
    if key == 'hero':
        ms.append(('g', GIRO_N, lambda parts, P, root, f: pose_giro(parts, f)))
    # parado no jogo: espera na vista sudeste (a mesma do quadro e_00 de antes)
    ms.append(('i', IDLE_N, lambda parts, P, root, f: pose_espera(parts, f)))
    build = G.builder(key)

    def build_lib(P, root):
        # Boitata heroi: mesmo material do bicho libertado (sem a brasa da possessao)
        G.LIBERTO = cfg.get('liberto', False)
        try:
            return build(P, root)
        finally:
            G.LIBERTO = False
    return {'key': key, 'label': cfg['label'], 'build': build_lib, 'boost': cfg.get('boost', 1.3) * G.RES, 'pxk': G.RES, 'shadow': True,
            'margin': (0.08, 0.08, 0.1, 0.06), 'pose0': lambda parts, P, root: pose(parts, 'walk', 0, 'wr'), 'modes': ms}


def keys():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ks = [k for k in args[2:] if k in CFG] if args and args[0] in ('render', 'prova', 'vitrine') and len(args) > 2 else list(CFG)
    return [k for k in ks if os.path.exists(os.path.join(G.MODELOS, k + '.glb'))]


SPEC = {'crews': [item(k) for k in keys()]}

# vitrine (tela de herois e inicio): camera baixa, a mesma elevacao do fundo do inicio, e o heroi grande
VITRINE_ELEV = 13.0
VITRINE_H = 760


def vitrine(out, keys):
    """Espera (i_NN) e chegada (c_NN) de cada heroi em out/<tipo>/, para tools/sprites/empacotar_inimigos.py --vitrine."""
    import json
    lib.ELEV = math.radians(VITRINE_ELEV)
    sc = bpy.context.scene
    cam = sc.camera
    cam.rotation_euler = (math.pi / 2 - lib.ELEV, 0, 0)
    sc.render.use_persistent_data = True
    sc.cycles.samples = 48
    sets = {}
    for key in keys:
        parts = BUILT[key]
        fr = [('i', f, (lambda f=f: pose_espera(parts, f))) for f in range(IDLE_N)]
        fr += [('c', f, (lambda f=f: pose_espera(parts, f, CHEGA_N, True))) for f in range(CHEGA_N)]
        reset_vis()
        set_visible({key})
        set_px(1.0)
        boxes = []
        for m, f, fn in fr:
            fn()
            boxes.append(bounds_of(meshes_of({key})))
        lo, hi = union(boxes)
        k = VITRINE_H / ((hi[1] - lo[1]) * ST['px'])
        set_px(k)
        wpx, hpx, tl = frame_camera(cam, lo, hi, margin=(0.06, 0.1, 0.06, 0.03))
        d = os.path.join(out, key)
        os.makedirs(d, exist_ok=True)
        for m, f, fn in fr:
            fn()
            render_to(os.path.join(d, f'{m}_{f:02d}.png'))
        sets[key] = {'w': wpx, 'h': hpx, 'anchor': project((0, 0, 0), tl), 'boost': k, 'modes': {'i': IDLE_N, 'c': CHEGA_N}}
        set_px(1.0)
        print('OK vitrine', key, flush=True)
    mp = os.path.join(out, 'meta.json')
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    meta.setdefault('sets', {}).update(sets)
    meta.update({'family': 'vitrine', 'px_per_game': PX_PER_GAME, 'game_per_bu': GAME_PER_BU})
    json.dump(meta, open(mp, 'w'), indent=1)
    print('VITRINE_OK', out)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    G.SPEC = SPEC
    if args and args[0] == 'vitrine':
        build_family(SPEC)
        vitrine(args[1], [i['key'] for i in SPEC['crews']])
    elif args and args[0] == 'prova':
        build_family(SPEC)
        bpy.context.scene.cycles.samples = 24
        G.prova(args[1], [i['key'] for i in SPEC['crews']])
    else:
        build_family(SPEC)
        # render mais leve: dados persistentes entre quadros e menos amostras (o denoiser segura)
        sc = bpy.context.scene
        sc.render.use_persistent_data = True
        sc.cycles.samples = 40
        out = args[1]
        only = set(args[2:]) or None
        render_family(FAM, SPEC, out, only)
        print('RENDER_OK', out)
