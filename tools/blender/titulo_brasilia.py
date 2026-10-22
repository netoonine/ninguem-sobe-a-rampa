"""Tela de inicio de "Ninguem Sobe a Rampa": a Praca dos Tres Poderes ao entardecer dourado da seca.

Mesma camera e mesmo layout do titulo da mata (tools/blender/titulo.py, de onde vem a camera, a grade do chao, a bruma
e as camadas): perspectiva 40 mm a 2,2 m de altura, 1,5 grau para baixo; tela logica de 1280x720.
  - logo no alto ao centro (y 40-300) sobre o ceu calmo; o horizonte fica em y ~323
  - botao JOGAR em y 470-546; atras dele, ao fundo no meio, a RAMPA sobe ate o Palacio do Planalto (colunas em arco)
  - os pes dos 4 herois em (190, 650), (330, 650), (950, 650), (1090, 650): praca de pedra portuguesa plana e limpa
  - espelhos d'agua dos dois lados da rampa refletindo o palacio; cupula, tigela e torres gemeas do Congresso no
    horizonte a direita; o mastro com a bandeira grande (sem texto) a esquerda; ipes amarelos nos cantos
Unidades em metros. Tres camadas (o jogo anima o resto por cima, js/ui.js -> Title):
  titulo_fundo.png   ceu, palacio, rampa, espelhos d'agua, Congresso, mastro, ipes e a praca
  titulo_frente.png  so os cantos: galhos de ipe florido no alto e capim seco embaixo, com alfa
  titulo_luz.png     passe de brilho: janelas do palacio e das torres, postes acesos (fundo preto)
titulo.json guarda a camera (chave cam) e as luzes na tela (chave luzes: [x, y, tipo]) para as particulas do jogo.

  Blender -b -P tools/blender/titulo_brasilia.py -- titulo arte/render/titulo [amostras] [k]     (k=3 -> 3840x2160)
  python3 tools/sprites/empacotar.py cenario      (pack_titulo grava sprites/titulo_* e SPRITE_META.titulo)
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bpy, bmesh
from mathutils import Vector
from lib import (TAU, ST, GLOW_MATS, lin, mat, sphere, tube, cyl, box, make_root, coll_for, setup_scene, clear_scene, render_to)
from cenario_props import Lote
import titulo as T
from titulo import W, H, FEET, ground_at, to_screen, at_depth, grid_mesh, frustum_grid, sstep, hexc
from brasilia_props import (br_mats, ipe, arvore_cerrado, capim, curb_loop, planalto, rampa, congresso, mastro, poste)

SUN_DIR = Vector((-0.72, -0.6, 0.25)).normalized()   # da cena para o sol: baixo a esquerda, um pouco atras da camera

# ---------------------------------------------------------------- planta da cena (metros; y = distancia a frente)
PRACA_Y = 17.2                                  # fim da praca de pedra portuguesa (onde estao os herois)
RAMPA = dict(y0=16.6, w=3.6)                    # pe da rampa e largura
PAL = dict(front=60.0, W=31.0, D=7.0, s=2.0, zf=1.5, Hc=3.5, n_col=11)
POOLS = [(-10.6, -3.7, 19.6, 52.0), (3.7, 10.6, 19.6, 52.0)]   # espelhos d'agua (x0, x1, y0, y1)
CONGRESSO = (116.0, 380.0)
MASTRO = (-38.0, 120.0)
FEET_W = []


def in_pool(X, Y, m=0.0):
    k = np.zeros_like(X, dtype=bool)
    for (x0, x1, y0, y1) in POOLS:
        k |= (X > x0 - m) & (X < x1 + m) & (Y > y0 - m) & (Y < y1 + m)
    return k


def terrain_br(X, Y):
    """Altura e cor do chao: praca de pedra portuguesa (ondas cinza), gramado seco em volta dos espelhos, cerrado dourado
    ao longe. Tudo plano (Brasilia e um planalto); so o fundo dos espelhos afunda."""
    n1, n2 = T.nz(X, Y, 0.3, 1.3), T.nz(X, Y, 1.6, 7.1)
    Z = np.zeros_like(X)
    Z = np.where(in_pool(X, Y, -0.3), -0.45, Z)
    # cores
    ped, ped_d = hexc('#ece4d3'), hexc('#e1d9c9')
    lawn, lawn_d = hexc('#a7a85a'), hexc('#8e9448')
    cer, cer_d, cer_l = hexc('#c6a45a'), hexc('#a98a46'), hexc('#d6b86c')
    a = (0.5 + 0.5 * n1)[..., None]
    col = cer_d * (1 - a) + cer * a
    pm = sstep(0.1, 0.6, n2 * 0.6 + n1 * 0.5)[..., None]
    col = col * (1 - pm * 0.5) + cer_l * pm * 0.5
    lk = ((np.abs(X) < 26) & (Y < 72)).astype(np.float32)[..., None] * (1 - sstep(60, 72, Y))[..., None]
    lc = lawn_d * (1 - a) + lawn * a
    col = col * (1 - lk) + lc * lk
    # praca: pedra portuguesa clara com as ondas do calcadao
    wave = 0.5 + 0.5 * np.sin(X / 1.05 + 1.7 * np.sin(Y / 1.6) + Y / 3.0)
    st = sstep(0.86, 0.92, wave)[..., None]
    pc = ped * (1 - st) + ped_d * st
    pk = (1 - sstep(PRACA_Y - 0.2, PRACA_Y + 0.2, Y))[..., None]
    col = col * (1 - pk) + pc * pk
    # faixa de concreto no fim da praca e em volta do pe da rampa
    fk = ((Y > PRACA_Y - 0.2) & (Y < PRACA_Y + 1.4)).astype(np.float32)[..., None]
    col = col * (1 - fk) + hexc('#d9d2c2') * fk
    # embasamento do palacio
    bk = ((np.abs(X) < PAL['W'] / 2 + 1.6) & (Y > PAL['front'] - 2.2) & (Y < PAL['front'] + 12)).astype(np.float32)[..., None]
    col = col * (1 - bk) + hexc('#d4cdbd') * bk
    # fundo dos espelhos
    col = np.where(in_pool(X, Y, -0.3)[..., None], hexc('#3c5b62'), col)
    far = sstep(120, 400, Y)[..., None]
    col = col * (1 - far * 0.35) + cer_d * far * 0.35
    return Z.astype(np.float32), col.astype(np.float32)


def build_ground(root):
    X, Y = frustum_grid(5.0, 1300.0, 900, 420, k=4.5)
    Z, col = terrain_br(X, Y)
    grid_mesh('Chao', root, X, Y, Z, col, T.ground_material(), bands=8)


def rounded_rect(x0, x1, y0, y1, r, n=8):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        for i in range(n + 1):
            a = a0 + (math.pi / 2) * i / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def build_pools(root, M):
    """Espelhos d'agua: lamina escura e espelhada (reflete o palacio e o ceu) e a borda de concreto."""
    deep, shal = hexc('#24414b'), hexc('#3f6873')
    for k, (x0, x1, y0, y1) in enumerate(POOLS):
        xs = np.linspace(x0 - 0.1, x1 + 0.1, 40, dtype=np.float32)
        ys = np.linspace(y0 - 0.1, y1 + 0.1, 80, dtype=np.float32)
        Y_, X_ = np.meshgrid(ys, xs, indexing='ij')
        t = sstep(0.0, 1.0, np.minimum.reduce([X_ - x0, x1 - X_, Y_ - y0, y1 - Y_]))[..., None]
        cw = shal * (1 - t) + deep * t
        grid_mesh(f'Espelho{k}', root, X_, Y_, np.full_like(X_, -0.14), cw, T.water_material(), bands=1)
        pts = [(x, y, 0.0) for (x, y) in rounded_rect(x0 - 0.22, x1 + 0.22, y0 - 0.22, y1 + 0.22, 0.6)]
        curb_loop(root, f'Espelho{k}_borda', pts, 0.45, 0.16, -0.5, M['conc_l'])


# ---------------------------------------------------------------- ceu de fim de tarde da seca
def setup_sky_br():
    """Ceu pintado (camera e reflexos): dourado no horizonte, rosado no meio, lilas-azulado no alto; brilho do sol baixo
    a esquerda e umas faixas finas de nuvem perto do horizonte. O resto da cena recebe uma luz ambiente fria."""
    w = bpy.context.scene.world
    N, L = w.node_tree.nodes, w.node_tree.links
    N.clear()
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Generated'], sep.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.01; mr.inputs['From Max'].default_value = 0.5
    L.new(sep.outputs['Z'], mr.inputs['Value'])
    ramp = N.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.interpolation = 'B_SPLINE'
    stops = [(0.0, '#ffd394'), (0.05, '#ffc08a'), (0.12, '#f9a98d'), (0.22, '#eea3a1'), (0.34, '#cfa8b8'), (0.5, '#a3acce'), (1.0, '#7d9ac9')]
    cr.elements[0].position, cr.elements[0].color = stops[0][0], lin(stops[0][1])
    cr.elements[1].position, cr.elements[1].color = stops[-1][0], lin(stops[-1][1])
    for p, c in stops[1:-1]:
        e = cr.elements.new(p)
        e.color = lin(c)
    L.new(mr.outputs['Result'], ramp.inputs['Fac'])
    col = ramp.outputs['Color']
    a = math.radians(-50)
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    L.new(tc.outputs['Generated'], dot.inputs[0])
    dot.inputs[1].default_value = tuple(Vector((math.sin(a), math.cos(a), 0.05)).normalized())
    m2 = N.new('ShaderNodeMapRange'); m2.inputs['From Min'].default_value = 0.45; m2.inputs['From Max'].default_value = 1.0
    L.new(dot.outputs['Value'], m2.inputs['Value'])
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0
    L.new(m2.outputs['Result'], pw.inputs[0])
    mg = N.new('ShaderNodeMath'); mg.operation = 'MULTIPLY'; mg.inputs[1].default_value = 0.85
    L.new(pw.outputs[0], mg.inputs[0])
    col = T._mixc(N, L, mg.outputs[0], col, lin('#fff0c0'), 'SCREEN')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.4, 2.4, 18.0)
    L.new(tc.outputs['Generated'], mp.inputs['Vector'])
    cn = N.new('ShaderNodeTexNoise'); cn.inputs['Scale'].default_value = 1.7; cn.inputs['Detail'].default_value = 4; cn.inputs['Roughness'].default_value = 0.55
    L.new(mp.outputs['Vector'], cn.inputs['Vector'])
    cm = N.new('ShaderNodeMapRange'); cm.inputs['From Min'].default_value = 0.52; cm.inputs['From Max'].default_value = 0.72
    L.new(cn.outputs['Fac'], cm.inputs['Value'])
    b1 = N.new('ShaderNodeMapRange'); b1.inputs['From Min'].default_value = 0.012; b1.inputs['From Max'].default_value = 0.05
    L.new(sep.outputs['Z'], b1.inputs['Value'])
    b2 = N.new('ShaderNodeMapRange'); b2.inputs['From Min'].default_value = 0.14; b2.inputs['From Max'].default_value = 0.07
    L.new(sep.outputs['Z'], b2.inputs['Value'])
    bm_ = N.new('ShaderNodeMath'); bm_.operation = 'MULTIPLY'
    L.new(b1.outputs['Result'], bm_.inputs[0]); L.new(b2.outputs['Result'], bm_.inputs[1])
    cf = N.new('ShaderNodeMath'); cf.operation = 'MULTIPLY'
    L.new(cm.outputs['Result'], cf.inputs[0]); L.new(bm_.outputs[0], cf.inputs[1])
    cf2 = N.new('ShaderNodeMath'); cf2.operation = 'MULTIPLY'; cf2.inputs[1].default_value = 0.55
    L.new(cf.outputs[0], cf2.inputs[0])
    col = T._mixc(N, L, cf2.outputs[0], col, lin('#ffe2c8'), 'MIX')
    paint = N.new('ShaderNodeBackground'); paint.inputs['Strength'].default_value = 1.0
    L.new(col, paint.inputs['Color'])
    amb = N.new('ShaderNodeBackground'); amb.name = 'Ambiente'
    amb.inputs['Color'].default_value = lin('#c0bed0')
    amb.inputs['Strength'].default_value = 0.55
    lp = N.new('ShaderNodeLightPath')
    mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    L.new(lp.outputs['Is Camera Ray'], mx.inputs[0]); L.new(lp.outputs['Is Glossy Ray'], mx.inputs[1])
    ms = N.new('ShaderNodeMixShader'); ms.name = 'CeuMix'
    L.new(mx.outputs[0], ms.inputs[0]); L.new(amb.outputs[0], ms.inputs[1]); L.new(paint.outputs[0], ms.inputs[2])
    wo = N.new('ShaderNodeOutputWorld'); wo.name = 'SaidaMundo'
    L.new(ms.outputs[0], wo.inputs['Surface'])


def setup_sun_br():
    sun = bpy.data.objects['Sol']
    sun.data.energy = 3.6
    sun.data.color = lin('#ffc58a')[:3]
    sun.data.angle = math.radians(5)
    sun.rotation_euler = SUN_DIR.to_track_quat('Z', 'Y').to_euler()
    bpy.data.lights['Preenchimento'].energy = 0.0


def warm_haze():
    """Bruma do titulo da mata com as cores do entardecer da seca (laranja do lado do sol, rosada do outro)."""
    g = T.haze_group()
    ramp = next(n for n in g.nodes if n.type == 'VALTORGB')
    ramp.color_ramp.elements[0].color = lin('#f6c69a')
    ramp.color_ramp.elements[1].color = lin('#e2b4ac')


# ---------------------------------------------------------------- moldura da frente (so os cantos)
def build_frente(root, M):
    """Cantos: galho de ipe florido entrando pelo alto (esquerda e direita) e capim seco com flores caidas embaixo.
    Longe dos herois (x 130-390 e 890-1150), do logo (x 330-950, y < 300) e do botao."""
    rr = random.Random(41)
    lote = Lote('frente')
    for side, pts_s in ((-1, [(-90, 30), (60, 18), (200, -10)]), (1, [(1370, 34), (1215, 16), (1080, -12)])):
        br = [at_depth(x, y, 3.0 + 0.04 * i) for i, (x, y) in enumerate(pts_s)]
        tube(root, f'galhoIpe{side}', br, 0.05, M['ipe_casca'], segs=10, rfun=lambda t: 0.065 - 0.035 * t)
        for k in range(26):
            t = rr.random()
            p = br[0].lerp(br[1], t * 2) if t < 0.5 else br[1].lerp(br[2], (t - 0.5) * 2)
            q = p + Vector((rr.uniform(-0.12, 0.12), rr.uniform(-0.1, 0.1), rr.uniform(-0.2, 0.03)))
            sx, sy = to_screen(q)
            if (side < 0 and sx > 290) or (side > 0 and sx < 990) or sy > 190:
                continue
            mk = M['ipe_l'] if q.z > p.z - 0.05 else M['ipe']
            lote.pebble(mk, tuple(q), rr.uniform(0.045, 0.075), squash=0.85, rot=rr.uniform(0, TAU), rr=rr, sub=2, rough=0.3)
        # florzinhas soltas penduradas
        for k in range(8):
            t = rr.uniform(0.1, 0.9)
            p = br[0].lerp(br[1], t * 2) if t < 0.5 else br[1].lerp(br[2], (t - 0.5) * 2)
            q = p + Vector((rr.uniform(-0.1, 0.1), 0, -rr.uniform(0.18, 0.32)))
            if to_screen(q)[1] > 200:
                continue
            lote.pebble(M['ipe_d'], tuple(q), 0.03, squash=1.0, rot=0, rr=rr, sub=1, rough=0.2)
    # cantos de baixo: touceiras de capim seco e flores de ipe caidas
    for side, sx_ in ((-1, 30), (1, 1250)):
        base = ground_at(sx_, 700)
        for k in range(7):
            p = (base.x + rr.uniform(-0.45, 0.45), base.y + rr.uniform(-0.3, 0.5), 0.0)
            if (side < 0 and to_screen(p)[0] > 105) or (side > 0 and to_screen(p)[0] < 1175):
                continue
            capim(lote, M, p, rr.uniform(0.5, 0.75), rr)
        for k in range(14):
            p = (base.x + rr.uniform(-0.6, 0.6), base.y + rr.uniform(-0.4, 0.6), 0.004)
            if (side < 0 and to_screen(p)[0] > 110) or (side > 0 and to_screen(p)[0] < 1170):
                continue
            lote.disc(M['ipe'] if k % 3 else M['ipe_d'], p, rr.uniform(0.02, 0.035), h=0.008, n=8)
    lote.done(root)


# ---------------------------------------------------------------- cena
def build():
    rr = random.Random(7)
    M = br_mats()
    GLOW_MATS[M['janela'].name] = 3.0
    GLOW_MATS[M['luminaria'].name] = 9.0
    FEET_W[:] = [tuple(ground_at(x, y)[:2]) for (x, y) in FEET]
    root = make_root('raiz_titulo', 'fundo', coll_for('Titulo'))
    root['camada'] = 'fundo'
    front = make_root('raiz_frente', 'frente', coll_for('TituloFrente'))
    front['camada'] = 'frente'
    build_ground(root)
    build_pools(root, M)
    lote = Lote('miudos')
    lights, luzes = [], []
    gz = lambda x, y: 0.0
    # palacio do Planalto e a rampa (do fim da praca ate o piso nobre)
    yc = PAL['D'] / 2 + 0.32 * PAL['s']
    sub, info = planalto(root, 'planalto', (0.0, PAL['front'] + yc, 0.0), PAL['s'], M, glass=M['janela'], n_col=PAL['n_col'],
                         W=PAL['W'], D=PAL['D'], zf=PAL['zf'], Hc=PAL['Hc'])
    rampa(root, 'rampa', (0.0, RAMPA['y0'], -0.02), (0.0, PAL['front'] - 0.3, PAL['zf'] + 0.08), RAMPA['w'], M, k=2.2)
    for fx in (-0.33, 0.0, 0.33):
        p = (fx * PAL['W'], PAL['front'], (PAL['zf'] + PAL['Hc']) / 2)
        luzes.append([round(v, 1) for v in to_screen(p)] + ['janela'])
    # Congresso no horizonte (a direita) e o mastro com a bandeira (a esquerda)
    cx, cy = CONGRESSO
    csub, cinfo = congresso(root, 'congresso', (cx, cy, 0.0), 8.0, M, glass=M['janela'], glass2=M['janela'], W=56.0, D=13.6, sd=1.15, Ht=3.9)
    for sx in (-1, 1):
        p = (cx + sx * 0.6 * 8.0, cy + cinfo['ty'], cinfo['Ht'] * 0.6)
        luzes.append([round(v, 1) for v in to_screen(p)] + ['torre'])
    mastro(root, 'mastro', (MASTRO[0], MASTRO[1], 0.0), 5.0, M, rr)
    T.HAZE_K.update({'br_bandeira': 3000.0})
    # postes: na frente do palacio e nas pontas de tras dos espelhos d'agua
    for k, (x, y) in enumerate(((-12.6, 50.5), (12.6, 50.5), (-21.0, 58.5), (21.0, 58.5))):
        tip = poste(root, f'poste{k}', (x, y, 0.0), M, s=3.4, ang=math.pi / 2 if x < 0 else math.pi / 2)
        lights.append((tuple(Vector(tip) + Vector((0, 0, -0.35))), '#ffc878', 90.0))
        luzes.append([round(v, 1) for v in to_screen(tip)] + ['poste'])
    # ipes nos cantos (fundo) e mais alguns ao longe, perto do palacio
    # (a direita os ipes ficam baixos e na beirada: o Congresso aparece no horizonte entre eles e o logo)
    for k, (x, y, s_) in enumerate(((-10.4, 25.0, 3.6), (-12.6, 33.5, 3.3), (-14.4, 45.0, 3.0), (11.3, 21.5, 2.7),
                                    (-27.0, 64.0, 3.2), (-40.0, 75.0, 3.4))):
        ipe(root, lote, f'ipe{k}', (x, y, 0.0), s_, rr, M, ground=gz)
    # cerrado ao longe: arvores retorcidas e ipes soltos, capim seco nos lados
    for k in range(70):
        y = 70 + rr.random() ** 1.4 * 260
        x = rr.uniform(-1, 1) * (0.9 * y + 20)
        sx, sy = to_screen((x, y, 0))
        if -60 < sx < W + 60 and (abs(x) > PAL['W'] / 2 + 4 or y > PAL['front'] + 20):
            if 950 < sx < 1215:
                continue   # nao tapar o Congresso
            if rr.random() < 0.22:
                ipe(root, lote, f'ipeLonge{k}', (x, y, 0.0), rr.uniform(3.0, 4.2), rr, M, ground=gz, petals=False)
            else:
                arvore_cerrado(root, lote, f'cerradoLonge{k}', (x, y, 0.0), rr.uniform(3.2, 4.8), rr, M)
    for k in range(260):
        y = 18 + rr.random() * 60
        x = rr.choice((-1, 1)) * rr.uniform(10.8, 0.9 * y + 6)
        if in_pool(np.array([x]), np.array([y]), 0.6)[0] or (abs(x) < PAL['W'] / 2 + 3 and y > PAL['front'] - 3):
            continue
        capim(lote, M, (x, y, 0.0), rr.uniform(0.5, 0.9), rr)
    for k in range(120):
        y = 72 + rr.random() * 120
        x = rr.uniform(-1, 1) * (0.8 * y)
        capim(lote, M, (x, y, 0.0), rr.uniform(0.8, 1.3), rr)
    lote.done(root)
    build_frente(front, M)
    return lights, luzes


# ---------------------------------------------------------------- passe de luz e render
def glow_pass_br(path, lights):
    """So o que acende: janelas e luminarias (sem sol, sem ceu, sem bruma), com uma luz pontual em cada poste."""
    sc = bpy.context.scene
    N = sc.world.node_tree.nodes
    ms, wo = N['CeuMix'], N['SaidaMundo']
    old_sun = bpy.data.lights['Sol'].energy
    bpy.data.lights['Sol'].energy = 0.0
    sc.world.node_tree.links.remove(wo.inputs['Surface'].links[0])
    em = bpy.data.node_groups['Bruma'].nodes['BrumaEmissao']
    old_em = em.inputs['Strength'].default_value
    em.inputs['Strength'].default_value = 0.0
    olds = {}
    for name, val in GLOW_MATS.items():
        gm = bpy.data.materials.get(name)
        if not gm:
            continue
        gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        olds[name] = gb.inputs['Emission Strength'].default_value
        gb.inputs['Emission Strength'].default_value = val
    temp = []
    for i, (pos, col, watts) in enumerate(lights):
        ld = bpy.data.lights.new(f'luzT{i}', 'POINT')
        ld.energy = watts
        ld.shadow_soft_size = 0.2
        ld.color = lin(col)[:3]
        lo = bpy.data.objects.new(f'luzT{i}', ld)
        sc.collection.objects.link(lo)
        lo.location = Vector(pos)
        temp.append(lo)
    render_to(path)
    for lo in temp:
        ld = lo.data
        bpy.data.objects.remove(lo, do_unlink=True)
        bpy.data.lights.remove(ld)
    for name, v in olds.items():
        gb = next(n for n in bpy.data.materials[name].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        gb.inputs['Emission Strength'].default_value = v
    em.inputs['Strength'].default_value = old_em
    sc.world.node_tree.links.new(ms.outputs[0], wo.inputs['Surface'])
    bpy.data.lights['Sol'].energy = old_sun


def render_titulo(out, samples=128, k=3.0, only=None):
    os.makedirs(out, exist_ok=True)
    clear_scene()
    sc = bpy.context.scene
    ST['coll'] = sc.collection
    setup_scene()
    try:
        bpy.context.preferences.addons['cycles'].preferences.metalrt = 'OFF'
    except Exception:
        pass
    bpy.data.objects['ChaoSombra'].hide_render = True
    sc.cycles.samples = samples
    sc.cycles.transparent_max_bounces = 48
    sc.view_settings.exposure = -0.15
    setup_sky_br()
    setup_sun_br()
    lights, luzes = build()
    T.apply_haze()
    warm_haze()
    T.make_camera(k)
    layers = only or ['fundo', 'frente', 'luz']
    if 'fundo' in layers:
        T.set_layer('fundo')
        sc.render.film_transparent = False
        sc.render.image_settings.color_mode = 'RGB'
        render_to(os.path.join(out, 'titulo_fundo.png'))
    if 'frente' in layers:
        T.set_layer('frente')
        sc.render.film_transparent = True
        sc.render.image_settings.color_mode = 'RGBA'
        render_to(os.path.join(out, 'titulo_frente.png'))
    if 'luz' in layers:
        T.set_layer('fundo')
        sc.render.film_transparent = False
        sc.render.image_settings.color_mode = 'RGB'
        glow_pass_br(os.path.join(out, 'titulo_luz.png'), lights)
    meta = {'lens_mm': T.LENS, 'sensor_mm': T.SENSOR, 'cam_h_m': T.CAM_H, 'pitch_deg': math.degrees(T.PITCH),
            'feet_world': FEET_W, 'sun_dir': list(SUN_DIR),
            'feet_view_deg': [math.degrees(math.atan2(T.CAM_H, math.hypot(*fw))) for fw in FEET_W],
            'px_per_m_at_feet': [T.FPX / (T.CAM_ROT.transposed() @ (Vector((fw[0], fw[1], 0)) - T.CAM_O)).z * -1 for fw in FEET_W],
            'luzes': luzes}
    with open(os.path.join(out, 'titulo.json'), 'w') as fh:
        json.dump(meta, fh, indent=1)
    print('TITULO_OK', json.dumps(meta))


if __name__ == '__main__' and '--' in sys.argv:
    args = sys.argv[sys.argv.index('--') + 1:]
    if args and args[0] == 'titulo':
        only = args[4].split(',') if len(args) > 4 else None
        render_titulo(args[1], int(args[2]) if len(args) > 2 else 128, float(args[3]) if len(args) > 3 else 3.0, only)
