"""Personagens de "Ninguem Sobe a Rampa" a partir dos GLB do Tripo (arte/modelos/rampa/<glb>.glb).

Reusa o pipeline do Guardioes (tools/blender/inimigos_glb.py: importa, enxuga, poe de pe, esqueleto por tipo de corpo,
poses por codigo, render nas 5 direcoes) e acrescenta o que a satira pede:
- sem a brasa da mata: ninguem esta possuido, a cor do GLB fica (so clareia um pouco e vira argila, como as torres);
- plan 'rigid': veiculo inteiro (moto, bicicleta, onibus): quica, balanca e empina; sem esqueleto;
- plan 'float': quem voa parado (balao, jatinho, estatua voadora, Fundao): sobe, desce e balanca;
- 'combo': dois GLB juntos, cada um com o proprio plan (o homem atras do boi ou do leao; o Capitao sentado na moto
  gigante; a Janjinha dancando em cima do trio eletrico).

Familias: 'inimigos' (adversarios e chefes, arte/render/inimigos), 'unidades' (herois e aliados com as chaves do motor:
hero, caipora, benzedeira, boitata, soldier, lancers, monks, rider, merc) e 'vitrine' (herois grandes).

uso: Blender -b -P tools/blender/rampa_glb.py -- render inimigos arte/render/inimigos [chaves]
     Blender -b -P tools/blender/rampa_glb.py -- render unidades arte/render/unidades [chaves]
     Blender -b -P tools/blender/rampa_glb.py -- vitrine arte/render/vitrine [chaves]
     Blender -b -P tools/blender/rampa_glb.py -- prova inimigos pasta [chaves]
     Blender -b -P tools/blender/rampa_glb.py -- cru pasta glbs        (modelo cru em 4 giros, para achar a frente)
"""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib
import inimigos_glb as G
import unidades_glb as UG
import esqueleto


# travas do esqueleto humano: braco com a mao grudada no corpo nao gira; com mao na coxa, a perna anda mais pelo joelho
# e o tronco quase nao torce; com mao na cabeca, a cabeca quase nao vira (sem movimento relativo no ponto fundido)
_turn0 = G.turn


def _turn_travado(arm, n, *rots):
    if n.startswith(('braco', 'antebraco')) and arm.get('preso_' + n[-1]):
        return
    k = 1.0
    if arm.get('preso_coxa') and n.startswith('coxa'):
        k = 0.45
    elif arm.get('preso_coxa') and n == 'peito':
        k = 0.5
    elif arm.get('preso_cabeca') and n == 'cabeca':
        k = 0.4
    if k != 1.0:
        rots = tuple((ax, ang * k) for ax, ang in rots)
    return _turn0(arm, n, *rots)


G.turn = _turn_travado

# densidade dos sprites da satira: 2.0 (o motor herdado usa 1.5); pessoas reais pedem rosto nitido em tela cheia/Retina
G.RES = 2.0

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
G.MODELOS = os.path.join(RAIZ, 'arte', 'modelos', 'rampa')
X, Y, Z = G.X, G.Y, G.Z
WALK_N, ATK_N, DIE_N = G.WALK_N, G.ATK_N, G.DIE_N


# ---------------------------------------------------------------- material: cor do GLB, sem brasa
def limpa(m):
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next((n for n in N if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        return
    if bsdf.inputs['Base Color'].links:
        # a textura do imagem->3D ja vem com sombra pintada: clareia um pouco para nao escurecer em dobro
        src = bsdf.inputs['Base Color'].links[0].from_socket
        hsv = N.new('ShaderNodeHueSaturation')
        hsv.inputs['Value'].default_value = 1.15
        hsv.inputs['Saturation'].default_value = 1.02
        L.new(src, hsv.inputs['Color'])
        L.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    for nm in ('Metallic', 'Roughness', 'Normal', 'Emission Color', 'Emission Strength'):
        for lk in list(bsdf.inputs[nm].links):
            L.remove(lk)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.72
    bsdf.inputs['Emission Strength'].default_value = 0.0


G.ember_remap_all = lambda ob, cfg: [limpa(s.material) for s in ob.material_slots if s.material and s.material.use_nodes]


# ---------------------------------------------------------------- partes de um combo: giro e posicao locais
_place = G.place


def place_local(parts, view, loc=(0, 0, 0), rx=0.0, ry=0.0):
    """Parte de um combo (filha do corpo do combo, que ja leva o giro da vista): posicao e inclinacao locais."""
    if 'off' not in parts:
        return _place(parts, view, loc, rx, ry)
    o = parts['off']
    parts['body'].rotation_euler = (rx, ry, math.radians(parts['cfg'].get('rot', 0.0)))
    parts['body'].location = (o[0] + loc[0], o[1] + loc[1], o[2] + loc[2])


G.place = place_local


# ---------------------------------------------------------------- personagens
# plan: biped | quad | flyer | rigid | float | combo. ph: altura na tela (BU, vista r); length: comprimento (veiculos).
# glb: arquivo (padrao = a chave). yaw: giro para a frente olhar +X (achar com o modo cru). espelho: vira o lado. arm: balanco dos bracos
# (baixo para quem segura coisa). show/show8: giro so no render (mostra mais o rosto).
BIP = dict(plan='biped', hip=0.36, shoulder=0.60, neck=0.64, show=-35.0, arm=0.35, ergue=1.6)


def bip(**kw):
    d = dict(BIP)
    d.update(kw)
    return d


INIMIGOS = {
    # turma verde-amarela
    'pneu':      bip(label='Patriota do Pneu', ph=0.62, arm=0.08, ergue=0.6, atk=True),
    'motociata': dict(label='Motociata', plan='rigid', length=0.78, atk=True, quique=0.018, balanco=0.04),
    'nicolau':   bip(label='Nicolau Selfie', ph=0.66, yaw=-40.0, atk=True),
    'general':   bip(label='General Logistica', ph=0.70, arm=0.06, ergue=0.5, yaw=-45.0, atk=True),
    'michele':   bip(label='Michele Uncao', ph=0.68, passo=0.2, joelho=0.3, atk=True),
    'dudu':      dict(label='Dudu Tarifaco', plan='float', ph=0.78, shadow=False, atk=True),
    'zambela':   bip(label='Zambela Fujona', ph=0.66, arm=0.15, yaw=-45.0),
    'boiada':    dict(label='Passador de Boiada', plan='combo', atk=True, combo=[
                     dict(glb='boiada_boi', plan='quad', length=0.80, off=(0.14, 0.0, 0.0), atk=True),
                     dict(glb='boiada_homem', **bip(ph=0.58, arm=0.2), off=(-0.36, 0.08, 0.0))]),
    'damaris':   bip(label='Damaris da Goiabeira', ph=0.66, arm=0.15, atk=True),
    'carluxo':   bip(label='Carluxo dos Robos', ph=0.82, arm=0.05, ergue=0.5, atk=True),
    'robo':      bip(label='Robo de Zap', ph=0.40, hip=0.30, shoulder=0.55, neck=0.62, atk=True),
    'valdomar':  bip(label='Valdomar do Partidao', ph=0.86, arm=0.2, ergue=1.2, atk=True),
    'veio':      dict(label='Veio da Estatua', plan='float', ph=0.80, yaw=0.0, shadow=False, atk=True),
    # turma vermelha
    'mortadela': bip(label='Militante da Mortadela', ph=0.62, arm=0.3, atk=True),
    'rouanet':   bip(label='Bonde da Rouanet', ph=0.62, arm=0.4, atk=True),
    'gleice':    bip(label='Gleice Megafone', ph=0.66, arm=0.15, atk=True),
    'ze':        bip(label='Ze Guerreiro', ph=0.70, arm=0.2, yaw=-40.0, atk=True),
    'chuchu':    bip(label='Doutor Chuchu', ph=0.68, arm=0.2, atk=True),
    'jatinho':   dict(label='Ministro do Jatinho', plan='float', length=0.70, yaw=90.0, shadow=False, atk=True),
    'dilmae':    dict(label='Dilmae Pedalada', plan='rigid', length=0.62, yaw=90.0, espelho='y', quique=0.012, balanco=0.05),
    'taxad':     dict(label='Taxad', plan='combo', atk=True, combo=[
                     dict(glb='taxad_leao', plan='quad', length=0.78, off=(0.14, 0.0, 0.0), atk=True),
                     dict(glb='taxad_homem', **bip(ph=0.58, arm=0.15), off=(-0.36, 0.08, 0.0))]),
    'pelego':    bip(label='Pelego da Greve', ph=0.74, arm=0.04, ergue=0.4, atk=True),
    'busao':     dict(label='Busao da Caravana', plan='rigid', length=1.05, atk=True, quique=0.01, balanco=0.025),
    'excursao':  bip(label='Militante de Excursao', ph=0.44, arm=0.3, atk=True),
    'lulinha':   bip(label='Lulinha Ronaldinho', ph=0.84, arm=0.35, atk=True),
    'pomba':     dict(label='Pomba do Foro', plan='flyer', ph=0.50, show=-30.0, show8=-25.0, shadow=False, atk=True, flap=0.45),
    # Centrao
    'lyra':      bip(label='Lyra Secreto', ph=0.68, arm=0.1, atk=True),
    'centrao':   bip(label='O Centrao', ph=1.45, hip=0.33, shoulder=0.70, neck=0.74, arm=0.2, ergue=0.7, hand_low=0.12, atk=True),
    'cacique':   bip(label='Cacique do Centrao', ph=1.40, arm=0.25, ergue=1.4, atk=True),
    'fundao':    dict(label='Fundao Eleitoral', plan='float', ph=1.25, shadow=False, atk=True),
    # chefes: os herois da chapa rival (vice no veiculo; candidato grande)
    'capitao_moto': dict(label='Capitao Mito na Motociata', plan='combo', atk=True, combo=[
                     dict(glb='moto_gigante', plan='rigid', length=1.05, yaw=90.0, off=(0.0, 0.0, 0.0), quique=0.012, balanco=0.03),
                     dict(glb='capitao', **bip(ph=0.74), off=(-0.24, 0.0, 0.30), sentado=True, maos=(1.0, 0.0))]),
    'janja_trio':   dict(label='Janjinha no Trio Eletrico', plan='combo', atk=True, combo=[
                     dict(glb='trio', plan='rigid', length=1.40, off=(0.0, 0.0, 0.0), quique=0.006, balanco=0.015),
                     dict(glb='janjinha', **bip(ph=0.74), off=(-0.30, 0.0, 0.66), danca=True)]),
    # Comitiva da Janjinha (lutam do nosso lado; o jogo usa os quadros do andar e do ataque)
    'comitiva':   bip(label='Seguranca da Comitiva', glb='chefe', ph=0.66, arm=0.15, ergue=1.4, atk=True),
    'comitiva_b': bip(label='Assessor de Viagem', glb='assessor', ph=0.62, arm=0.25, ergue=1.6, atk=True),
    'zeroum_chefe': bip(label='Zero-Um, o Candidato', glb='zeroum', ph=1.75, arm=0.3, ergue=1.4, atk=True),
    'lulala_chefe': bip(label='Lulala, o Candidato', glb='lulala', ph=1.75, arm=0.3, ergue=1.4, atk=True),
}

# pessoas reais (modelos v3, foto + prompt): o braco do ataque sobe pouco (o adereco fica perto do rosto e o resto do
# golpe vem do corpo indo para a frente)
PESSOAS = {'lulala', 'janjinha', 'zeroum', 'capitao', 'nicolau', 'general', 'michele', 'dudu', 'zambela', 'boiada_homem',
           'damaris', 'carluxo', 'valdomar', 'veio', 'gleice', 'ze', 'chuchu', 'dilmae', 'taxad_homem', 'lyra'}


def _limita_ergue(tab):
    for k, c in tab.items():
        for sc in (c.get('combo') or [c]):
            if sc.get('plan') == 'biped':
                sc.setdefault('esqueleto', 'humano')   # todos os bipedes: esqueleto de verdade (tools/blender/esqueleto.py)
                sc.setdefault('gingado', 0.07)          # boneco de vinil: o corpo gingando faz o papel do braco
                sc.setdefault('pulo', 0.024)
                sc.setdefault('joelho', 0.9)
            if sc.get('plan') == 'biped' and sc.get('glb', k) in PESSOAS:
                sc['ergue'] = min(sc.get('ergue', 1.6), 0.7)


_limita_ergue(INIMIGOS)

# aliados com as chaves que o motor ja usa (DATA.HEROES[].sprite e as tropas das torres)
UNIDADES = {
    'hero':       bip(label='Lulala', glb='lulala', ph=0.80, ergue=1.8, espera='lulala'),
    'caipora':    bip(label='Janjinha', glb='janjinha', ph=0.76, ergue=1.8, espera='janjinha'),
    'benzedeira': bip(label='Zero-Um', glb='zeroum', ph=0.78, ergue=1.6, espera='zeroum'),
    'boitata':    bip(label='Capitao Mito', glb='capitao', ph=0.80, ergue=1.6, espera='capitao'),
    'soldier':    bip(label='Assessor', glb='assessor', ph=0.62, arm=0.25, ergue=1.8),
    'lancers':    bip(label='Chefe de Gabinete', glb='chefe', ph=0.68, arm=0.15, ergue=1.4),
    'monks':      bip(label='Funcionario Fantasma', glb='fantasma', ph=0.64, arm=0.3, ergue=1.6),
    'rider':      bip(label='Bancada de Apoio', glb='bancada', ph=0.66, arm=0.3, ergue=1.6),
    'merc':       bip(label='Centrao de Aluguel', glb='aluguel', ph=0.70, arm=0.3, ergue=1.8),
    # tropa do Sindicato (Chapa Vermelha): militantes de camiseta vermelha no lugar dos assessores (js/unidades.js USPR.key)
    'soldier_r':  bip(label='Militante', glb='excursao', ph=0.62, arm=0.3, ergue=1.8),
    'lancers_r':  bip(label='Diretoria do Sindicato', glb='mortadela', ph=0.68, arm=0.3, ergue=1.6),
    'monks_r':    bip(label='Pelego', glb='pelego', ph=0.66, arm=0.04, ergue=0.4),
}


_limita_ergue(UNIDADES)


def glb_of(key, cfg):
    return cfg.get('glb', key)


def present(key, cfg):
    gl = [s['glb'] for s in cfg['combo']] if cfg['plan'] == 'combo' else [glb_of(key, cfg)]
    return all(os.path.exists(os.path.join(G.MODELOS, g + '.glb')) for g in gl)


# ---------------------------------------------------------------- montar
def importa(glb, key, cfg, root):
    """Importa o GLB e marca a malha como do conjunto `key` (combo e chefe reaproveitando o GLB de um heroi)."""
    G.CFG[glb] = cfg
    ob = G.import_glb(glb, cfg, root)
    ob.name = key + '_' + glb + '_malha'
    ob['set'] = key
    return ob


def amostra(ob):
    P = G.verts_np(ob)
    M = np.array(ob.matrix_world)
    P = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3]
    return P[np.random.default_rng(1).choice(len(P), min(3000, len(P)), replace=False)]


def parte(key, cfg, root, glb, nome):
    """Uma malha com o seu esqueleto (ou nenhum, nos veiculos) debaixo de um corpo vazio."""
    ob = importa(glb, key, cfg, root)
    if cfg.get('espelho'):
        # espelha a malha: 'y' troca o lado (quem monta de lado passa a olhar para a camera);
        # 'x' troca frente e costas (quem corre para a esquerda no conceito passa a correr para a direita)
        # direto na malha (o esqueleto le os vertices locais), com as normais viradas de volta
        import mathutils
        ob.data.transform(mathutils.Matrix.Diagonal((-1, 1, 1, 1) if cfg['espelho'] == 'x' else (1, -1, 1, 1)))
        ob.data.flip_normals()
        ob.data.update()
        bpy.context.view_layer.update()
    corpo = empty(root, nome + '_corpo')
    if cfg['plan'] in ('rigid', 'float'):
        ob.parent = corpo
        return {'tag': key, 'body': corpo, 'arm': None, 'mesh': ob, 'info': {}, 'cfg': cfg, 'pts': amostra(ob)}
    if cfg['plan'] == 'biped' and cfg.get('esqueleto') == 'humano':
        arm, info = esqueleto.rig_humano(nome, ob, root, cfg)   # esqueleto de verdade (tools/blender/esqueleto.py)
    else:
        arm, info = G.RIGS[cfg['plan']](nome, ob, root, cfg)
    arm.parent = corpo
    return {'tag': key, 'body': corpo, 'arm': arm, 'mesh': ob, 'info': info, 'cfg': cfg, 'pts': amostra(ob)}


def builder(key, cfg):
    def build(P, root):
        if cfg['plan'] != 'combo':
            return parte(key, cfg, root, glb_of(key, cfg), key)
        corpo = empty(root, key + '_corpo')
        subs = []
        for i, s in enumerate(cfg['combo']):
            sc = dict(s)
            sp = parte(key, sc, root, s['glb'], f'{key}_{i}')
            sp['body'].parent = corpo
            sp['off'] = s.get('off', (0, 0, 0))
            subs.append(sp)
        bpy.context.view_layer.update()
        pts = np.concatenate([amostra(s['mesh']) for s in subs])
        return {'tag': key, 'body': corpo, 'arm': None, 'subs': subs, 'cfg': cfg, 'pts': pts, 'info': {}}
    return build


# ---------------------------------------------------------------- poses novas
def pose_rigid(parts, mode, f, view):
    """Veiculo: quica e balanca andando; no ataque empina e avanca; na queda tomba de lado."""
    cfg = parts['cfg']
    a = TAU * f / WALK_N
    if mode == 'walk':
        G.place(parts, view, (0, 0, cfg.get('quique', 0.012) * abs(math.sin(2 * a))),
                rx=cfg.get('balanco', 0.03) * math.sin(a), ry=0.015 * math.sin(2 * a + 0.5))
    elif mode == 'atk':
        t = f / (ATK_N - 1)
        k = math.sin(math.pi * t)
        G.place(parts, view, (0.07 * k, 0, 0.02 * k), ry=-0.14 * k)
    else:
        t = f / (DIE_N - 1)
        e = G.smooth01(t)
        G.place(parts, view, (0, 0.04 * e, 0.02 * math.sin(math.pi * min(1.0, t * 1.6))), rx=1.3 * e)


def pose_float(parts, mode, f, view):
    """Voa parado: sobe e desce devagar e balanca; ataque e um mergulho curto; na queda tomba e desce."""
    a = TAU * f / WALK_N
    if mode == 'walk':
        G.place(parts, view, (0, 0, 0.025 * math.sin(a)), rx=0.05 * math.sin(a + 0.6), ry=0.04 * math.sin(2 * a))
    elif mode == 'atk':
        t = f / (ATK_N - 1)
        k = math.sin(math.pi * t)
        G.place(parts, view, (0.06 * k, 0, -0.05 * k), ry=0.3 * k)
    else:
        t = f / (DIE_N - 1)
        e = G.smooth01(t)
        G.place(parts, view, (0, 0, -0.1 * e), rx=0.9 * e, ry=0.5 * e)


def pose_sentado(parts, mode, f, view):
    """Piloto: coxas para a frente, canelas para baixo, maos no guidao; balanca junto com a moto."""
    arm = parts['arm']
    G.reset(arm)
    a = TAU * f / WALK_N
    k = math.sin(math.pi * f / (ATK_N - 1)) if mode == 'atk' else 0.0
    G.place(parts, view, (0, 0, 0.008 * math.sin(2 * a)), ry=-0.05 * k)
    # maos: quanto cada braco vai ao guidao (0 = fica na pose do modelo, ex. o joinha do Capitao)
    mL, mR = parts['cfg'].get('maos', (1.0, 1.0))
    for nm, s, m in (('L', 1, mL), ('R', -1, mR)):
        G.turn(arm, 'coxa' + nm, (Y, -1.45), (X, s * 0.25))
        G.turn(arm, 'canela' + nm, (Y, 1.35))
        G.turn(arm, 'braco' + nm, (Y, m * (-1.0 - 0.9 * k * (s < 0))), (X, m * s * 0.15))
        G.turn(arm, 'antebraco' + nm, (Y, m * -0.4))
    G.turn(arm, 'peito', (Y, 0.12 - 0.15 * k))
    G.turn(arm, 'cabeca', (Z, 0.12 * math.sin(a)))


def pose_danca(parts, mode, f, view):
    """Em cima do trio: quadril de um lado para o outro e os bracos acenando para a multidao."""
    arm = parts['arm']
    G.reset(arm)
    a = TAU * f / WALK_N
    k = math.sin(math.pi * f / (ATK_N - 1)) if mode == 'atk' else 0.0
    G.place(parts, view, (0, 0, 0.01 * abs(math.sin(2 * a))))
    G.turn(arm, 'quadril', (X, 0.12 * math.sin(a)))
    for nm, s in (('L', 1), ('R', -1)):
        G.turn(arm, 'coxa' + nm, (X, -0.1 * math.sin(a)))
        G.turn(arm, 'braco' + nm, (Y, -2.2 - 0.3 * math.sin(2 * a + (s > 0) * math.pi) - 0.4 * k), (X, s * 0.35))
        G.turn(arm, 'antebraco' + nm, (Y, -0.3), (X, s * 0.4 * math.sin(4 * a)))
    G.turn(arm, 'peito', (X, -0.1 * math.sin(a)))
    G.turn(arm, 'cabeca', (X, 0.08 * math.sin(a)))


def pose_parte(sp, mode, f, view):
    sc = sp['cfg']
    if sc.get('sentado'):
        return pose_sentado(sp, mode, f, view)
    if sc.get('danca'):
        return pose_danca(sp, mode, f, view)
    POSES[sc['plan']](sp, mode, f, view)


def pose_combo(parts, mode, f, view):
    """O combo gira com a vista; cada parte anima com a sua pose (homem andando atras do bicho, piloto na moto)."""
    _place(parts, view)
    for sp in parts['subs']:
        if mode == 'die' and (sp['cfg'].get('sentado') or sp['cfg'].get('danca')):
            # chefe no veiculo: o veiculo tomba e leva o heroi junto
            pose_parte(sp, 'walk', 0, view)
        else:
            pose_parte(sp, mode, f, view)
    if mode == 'die' and any(sp['cfg'].get('sentado') or sp['cfg'].get('danca') for sp in parts['subs']):
        t = f / (DIE_N - 1)
        e = G.smooth01(t)
        _place(parts, view, (0, 0.05 * e, 0), rx=1.2 * e)


POSES = dict(G.POSES, rigid=pose_rigid, float=pose_float, combo=pose_combo)


# ---------------------------------------------------------------- espera dos herois (jogo parado e vitrine)
def pose_espera(parts, f, n=UG.IDLE_N, chega=False):
    """Respira, troca o peso, olha em volta e faz o gesto do personagem; chega=True e a entrada da vitrine."""
    arm, cfg = parts['arm'], parts['cfg']
    G.reset(arm)
    est = cfg.get('espera', 'base')
    t = f / n
    a = math.tau * (0.0 if chega else t)
    k = math.sin(math.pi * t) if chega else 0.0
    R = {}
    add = lambda b, ax, ang: R.setdefault(b, []).append((ax, ang))
    sway, resp = math.sin(a), math.sin(2 * a)
    add('quadril', X, 0.035 * sway)
    for nm in ('L', 'R'):
        add('coxa' + nm, X, -0.035 * sway)
    add('peito', X, -0.02 * sway)
    add('peito', Y, 0.025 * resp)
    olhar = 0.0 if chega else 0.16 * (UG.janela(t, 0.1, 0.4) - UG.janela(t, 0.52, 0.82))
    add('cabeca', Z, olhar)
    add('cabeca', X, 0.03 * sway)
    for nm, s in (('L', 1), ('R', -1)):
        add('braco' + nm, Y, 0.03 * math.sin(2 * a + s))
        add('antebraco' + nm, Y, -0.04 - 0.02 * resp)
    # os modelos das pessoas reais ja vem no gesto (mao do "L", joinha, celular, pau de selfie): o braco so balanca
    # pouco em cima dele; erguer de novo jogava o braco atras da cabeca e rasgava o rosto
    g = 0.0 if chega else UG.janela(t, 0.35, 0.75, 0.12)
    w = math.sin(6 * math.pi * t) * g
    if est == 'lulala':
        add('antebracoL', X, 0.12 * w)        # o "L" balanca, falando com a plateia
        add('peito', Y, -0.05 * g)
        add('cabeca', X, 0.05 * w)
    elif est == 'janjinha':
        add('bracoR', Y, -0.12 * g)            # ergue um pouco o pau de selfie
        add('cabeca', Z, -0.08 * g)
        add('cabeca', X, -0.05 * g)
    elif est == 'zeroum':
        add('cabeca', X, 0.06 * math.sin(8 * math.pi * t) * g)   # concorda no telefone
        add('peito', Z, 0.04 * w)
    elif est == 'capitao':
        add('bracoR', Y, -0.12 * w)            # o joinha bombeia
        add('peito', Y, -0.07 * g)
        add('cabeca', Y, -0.05 * g)
    # chegada na vitrine: um pulinho, sem erguer braco
    G.place(parts, 'we', (0, 0, 0.025 * k))
    for b, rots in R.items():
        G.turn(arm, b, *rots)
    G.grow(arm, 'peito', 1.0 + 0.012 * resp)


# ---------------------------------------------------------------- itens das familias
def item(key, cfg, fam):
    G.CFG[key] = cfg
    pose = POSES[cfg['plan']]
    ms = G.walk_modes(pose)
    if cfg.get('atk') or fam == 'unidades':
        ms.append(('a', ATK_N, lambda parts, P, root, f: pose(parts, 'atk', f, 'wr')))
    ms.append(('x', DIE_N, lambda parts, P, root, f: pose(parts, 'die', f, 'r')))
    if fam == 'unidades':
        if key == 'hero':
            ms.append(('g', UG.GIRO_N, lambda parts, P, root, f: UG.pose_giro(parts, f)))
        ms.append(('i', UG.IDLE_N, lambda parts, P, root, f: pose_espera(parts, f)))
    boost = cfg.get('boost', 1.3) * G.RES
    return {'key': key, 'label': cfg['label'], 'build': builder(key, cfg), 'boost': boost, 'pxk': G.RES,
            'shadow': cfg.get('shadow', True), 'margin': (0.08, 0.08, 0.1, 0.06),
            'pose0': lambda parts, P, root: pose(parts, 'walk', 0, 'wr'), 'modes': ms}


def chaves(tab, pedidas):
    ks = [k for k in pedidas if k in tab] if pedidas else list(tab)
    falta = [k for k in ks if not present(k, tab[k])]
    if falta:
        print('SEM GLB (pulando):', ' '.join(falta), flush=True)
    return [k for k in ks if k not in falta]


def cru(out, glbs):
    """Um quadro por giro (0, 90, 180, 270) de cada GLB, sem esqueleto: para achar o yaw (frente para +X)."""
    clear_scene()
    ST['coll'] = bpy.context.scene.collection
    setup_scene()
    os.makedirs(out, exist_ok=True)
    cam = bpy.context.scene.camera
    for glb in glbs:
        root = make_root('raiz_' + glb, glb, coll_for(glb))
        ob = importa(glb, glb, {'height': 0.5, 'yaw': 0.0}, root)
        set_px(1.2)
        for yaw in (0, 90, 180, 270):
            ob.rotation_euler = (0, 0, math.radians(yaw) + G.VIEWS['r'])
            bpy.context.view_layer.update()
            reset_vis()
            set_visible({glb})
            lo, hi = bounds_of(meshes_of({glb}))
            frame_camera(cam, lo, hi, margin=(0.05, 0.05, 0.05, 0.05))
            bpy.context.scene.cycles.samples = 12
            render_to(os.path.join(out, f'{glb}_{yaw}.png'))
        ob.hide_render = True
    print('CRU_OK', out)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    cmd = args[0] if args else ''
    if cmd == 'cru':
        cru(args[1], args[2:])
        sys.exit(0)
    if cmd == 'vitrine':
        fam, out, pedidas = 'unidades', args[1], args[2:]
    else:
        fam, out, pedidas = args[1], args[2], args[3:]
    tab = INIMIGOS if fam == 'inimigos' else UNIDADES
    for k, c in tab.items():
        G.CFG[k] = c
    SPEC = {'crews': [item(k, tab[k], fam) for k in chaves(tab, pedidas)]}
    G.SPEC = SPEC
    build_family(SPEC)
    sc = bpy.context.scene
    sc.render.use_persistent_data = True
    if cmd == 'vitrine':
        UG.pose_espera = pose_espera
        UG.vitrine(out, [i['key'] for i in SPEC['crews']])
    elif cmd == 'prova':
        sc.cycles.samples = 24
        G.prova(out, [i['key'] for i in SPEC['crews']])
    else:
        sc.cycles.samples = 40
        render_family(fam, SPEC, out, None)
        print('RENDER_OK', out)
