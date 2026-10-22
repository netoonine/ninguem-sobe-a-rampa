"""Inimigos de "Guardioes da Mata" a partir de modelos 3D tirados dos conceitos aprovados (arte/conceitos/amazonia).

Cada conceito recortado vira um GLB (imagem->3D, arte/modelos/inimigos/<tipo>.glb). Aqui o GLB e importado, enxugado,
posto de pe (pes no chao, frente para +X, tamanho alvo), o brilho roxo do conceito vira brasa laranja (mascara de matiz
no material) e um esqueleto simples por tipo de corpo e montado e animado por codigo. Sai no mesmo formato dos outros
inimigos (arte/render/inimigos/<tipo>/r|u|d|a|x_NN.png), com a mesma camera, luz e escala.

Tipos de corpo (plan): quad (4 patas), hexa (formigas), biped (de pe), serpent (cobras: pescoco sobe do enrolado),
flyer (asas), mermaid (tronco + cauda de peixe).

uso: Blender -b -P tools/blender/inimigos_glb.py -- render arte/render/inimigos [tipos]
     Blender -b -P tools/blender/inimigos_glb.py -- prova pasta [tipos]     (quadros soltos para conferir)
     Blender -b -P tools/blender/inimigos_glb.py -- cru pasta tipos          (modelo cru, para achar a frente)
"""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import lib
import inimigos as K
import inimigos_bichos as B
from mathutils import Quaternion

FAM = K.FAM
ATK_N, DIE_N = K.ATK_N, K.DIE_N
WALK_N = 16   # quadros por passada (eram 12: o passo ficava picado)
# vistas antigas (r: lado meio virado, u: costas, d: frente) servem a escala (ph), ao ataque e a queda; o andar usa
# 5 direcoes de verdade no chao (graus a partir de +X, positivo = para longe da camera) e o jogo espelha as outras 3:
# r leste, q nordeste, u norte, e sudeste, d sul. TURN vira todas um pouco para a camera (aparece mais o rosto)
VIEWS = dict(K.VIEWS)
DIRS = {'r': 0.0, 'q': 45.0, 'u': 90.0, 'e': -45.0, 'd': -90.0}
VIEWS.update({'w' + k: math.radians(v) for k, v in DIRS.items()})
TURN = -18.0
smooth01 = B.smooth01
MODELOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'arte', 'modelos', 'inimigos')

# plan: tipo de corpo; ph: altura projetada na tela (BU, vista r) = mesmo tamanho dos sprites que ja estavam no jogo;
# yaw: giro (graus) para a frente do modelo olhar para +X (o esqueleto assume frente +X, lados +-Y). Nos bipedes a frente
# e a dos pes, nao a do rosto (o conceito costuma virar a cabeca para quem olha): pes tortos = passo torto;
# show: giro extra so na hora de renderizar (personagem de pe mostra mais o rosto); glow: forca da brasa
CFG = {
    'raider':    dict(label='Sauva', plan='hexa', ph=0.52, yaw=90.0, atk=True),
    'scorpling': dict(label='Tucandeira', plan='hexa', ph=0.34, atk=True),
    'brood':     dict(label='Tucandeira-Mae', plan='hexa', ph=0.56, yaw=90.0, atk=True),
    'jackal':    dict(label='Queixada', plan='quad', ph=0.44, atk=True),
    'brute':     dict(label='Onca-Pintada', plan='quad', length=0.81, boost=K.EN_BOOST * 1.15, atk=True),
    'specter':   dict(label='Anhanga', plan='quad', ph=0.60, shadow=False, glow_hue='fogo', loose=0.1),
    'beetle':    dict(label='Tatu', plan='quad', ph=0.36, low=0.06, ginga=0.1, passo=0.7, joelho=1.1, pulo=0.02, cauda=0.08),
    'scorpion':  dict(label='Jacare-de-Pedra', plan='quad', ph=0.44, yaw=90.0, sprawl=True, low=0.06, boost=K.EN_BOOST * 1.1, atk=True),
    'bulwark':   dict(label='Tracaja', plan='quad', ph=0.43, sprawl=True, low=0.06, atk=True),
    'vulture':   dict(label='Morcego-Vampiro', plan='flyer', ph=0.44, show=-60.0, show8=-35.0, shadow=False),
    'djinn':     dict(label='Matinta Pereira', plan='flyer', ph=0.55, show=-30.0, show8=-25.0, shadow=False, atk=True, flap=0.35),
    'worm':      dict(label='Boiuna', plan='serpent', ph=1.05, coil=0.42, atk=True),
    'ifrit':     dict(label='Boitata', plan='serpent', ph=1.15, yaw=90.0, coil=0.30, shadow=False, boost=K.EN_BOOST * 1.1, atk=True, glow_hue='fogo'),
    'golem':     dict(label='Mapinguari', plan='biped', ph=1.45, yaw=-15.0, show=-40.0, hip=0.33, shoulder=0.70, neck=0.74, atk=True, arm=0.2, ergue=0.7, hand_low=0.12),
    'warlord':   dict(label='Curupira', plan='biped', ph=1.45, yaw=0.0, show=-40.0, hip=0.36, shoulder=0.56, neck=0.60, atk=True, arm=0.3, ergue=1.6, pes_tras=True),
    'shaman':    dict(label='Iara', plan='mermaid', ph=0.62, yaw=-30.0, show=-40.0, hip=0.42, shoulder=0.60, neck=0.64, atk=True),
    'saboteur':  dict(label='Boto', plan='biped', ph=0.62, yaw=0.0, show=-40.0, hip=0.32, shoulder=0.55, neck=0.60, tail=True, atk=True),
    'nomad':     dict(label='Macaco-prego', plan='biped', ph=0.56, show=-40.0, hip=0.36, shoulder=0.56, neck=0.60, tail=True, atk=True),
    # chefe final (fase 12): gigante de fumaca e raiz queimada com o coracao aceso no peito; sem liberto (ele se desfaz)
    'heart':     dict(label='Coracao da Fumaca', plan='biped', ph=1.8, show=-40.0, hip=0.32, shoulder=0.70, neck=0.76, atk=True, arm=0.2, ergue=0.7, hand_low=0.12),
}


def present(key):
    return os.path.exists(os.path.join(MODELOS, key + '.glb'))


# ---------------------------------------------------------------- importar e normalizar
def verts_np(ob):
    n = len(ob.data.vertices)
    P = np.empty(n * 3, dtype=np.float64)
    ob.data.vertices.foreach_get('co', P)
    return P.reshape(n, 3)


def drop_loose(ob, frac=0.02):
    """Tira pedacinhos soltos (o imagem->3D as vezes deixa uma bolinha flutuando)."""
    import bmesh as bm_
    b = bm_.new()
    b.from_mesh(ob.data)
    b.verts.ensure_lookup_table()
    seen, parts = set(), []
    for v in b.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            u = stack.pop()
            comp.append(u)
            for e in u.link_edges:
                w = e.other_vert(u)
                if w.index not in seen:
                    seen.add(w.index)
                    stack.append(w)
        parts.append(comp)
    big = max(len(c) for c in parts)
    kill = [v for c in parts if len(c) < frac * big for v in c]
    if kill:
        bm_.ops.delete(b, geom=kill, context='VERTS')
        b.to_mesh(ob.data)
    b.free()
    return len(kill)


def import_glb(key, cfg, root):
    path = os.path.join(MODELOS, key + '.glb')
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for o in new:
        if o != ob and o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    root.users_collection[0].objects.link(ob)
    ob.name = key + '_malha'
    # enxugar (os GLB vem com 0,2 a 1,5 mi de triangulos)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    alvo = cfg.get('tris', 60000)
    if tris > alvo:
        d = ob.modifiers.new('Enxugar', 'DECIMATE')
        d.ratio = alvo / tris
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=d.name)
    drop_loose(ob, cfg.get('loose', 0.02))
    # frente para +X (o importador de glTF deixa o objeto em quaternio: sem isto o giro nao pega)
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0, 0, math.radians(cfg.get('yaw', 0.0)))
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    P = verts_np(ob)
    lo, hi = P.min(0), P.max(0)
    if 'length' in cfg:
        k = cfg['length'] / (hi[0] - lo[0])
    elif 'ph' in cfg:
        # altura na tela (vista r): o mesmo tamanho que o inimigo ja tinha no jogo
        Rv, Uv, Fv = cam_axes()
        a = VIEWS['r']
        Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        up = (P @ Rz.T) @ np.array(Uv)
        k = cfg['ph'] / (up.max() - up.min())
    else:
        k = cfg['height'] / (hi[2] - lo[2])
    c = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    P = (P - c) * k
    if cfg.get('pes_tras'):
        P = pes_para_tras(P)
    ob.data.vertices.foreach_set('co', P.ravel())
    ob.data.update()
    for p in ob.data.polygons:
        p.use_smooth = True
    ob['set'] = key
    ember_remap_all(ob, cfg)
    return ob


def pes_para_tras(P, abre=12.0):
    """Curupira (a lenda): pes virados para tras. Cada pe gira em torno do proprio tornozelo ate os dedos apontarem
    para tras (-X, abertos `abre` graus para fora). A parte longe do tornozelo (o pe) gira inteira; a canela logo acima
    torce aos poucos ate a barra da calca, para a malha nao rasgar."""
    def sstep(t):
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3 - 2 * t)
    P = P.copy()
    H = P[:, 2].max()
    z, xy = P[:, 2], P[:, :2]
    low = P[z < 0.04 * H, :2]
    cy, wy = np.median(low[:, 1]), np.ptp(low[:, 1])
    C = kmeans(low, [(np.median(low[:, 0]), cy + 0.25 * wy), (np.median(low[:, 0]), cy - 0.25 * wy)])
    # tornozelo: o anel de pele entre o pe e a barra da calca
    anel = (z > 0.05 * H) & (z < 0.08 * H)
    ja = ((xy[anel][:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
    piv = np.array([xy[anel][ja == k].mean(0) for k in range(2)])
    R = np.array([np.median(np.linalg.norm(xy[anel][ja == k] - piv[k], axis=1)) for k in range(2)])
    perto = ((xy[:, None, :] - piv[None]) ** 2).sum(-1).argmin(1)
    for k in range(2):
        m = (perto == k) & (z < 0.095 * H)
        d = xy[m] - piv[k]
        r = np.linalg.norm(d, axis=1)
        pe = (z[m] < 0.04 * H) & (r > 1.5 * R[k])
        ponta = d[pe].mean(0)
        agora = math.atan2(ponta[1], ponta[0])
        fora = 1.0 if piv[k][1] > piv[1 - k][1] else -1.0
        alvo = math.pi - fora * math.radians(abre)
        giro = (alvo - agora + math.pi) % (2 * math.pi) - math.pi
        wz = 1.0 - sstep((z[m] - 0.045 * H) / (0.04 * H))
        wr = sstep((r - 1.1 * R[k]) / (0.7 * R[k])) * (1.0 - sstep((z[m] - 0.065 * H) / (0.02 * H)))
        ang = giro * np.maximum(wz, wr)
        c, s_ = np.cos(ang), np.sin(ang)
        P[np.where(m)[0], 0] = piv[k][0] + c * d[:, 0] - s_ * d[:, 1]
        P[np.where(m)[0], 1] = piv[k][1] + s_ * d[:, 0] + c * d[:, 1]
        print('pe', k, 'apontava', round(math.degrees(agora)), 'gira', round(math.degrees(giro)), flush=True)
    return P


# ---------------------------------------------------------------- brilho do conceito -> brasa laranja
HUES = {'roxo': (0.68, 0.74, 0.92, 0.97), 'fogo': (0.0, 0.0, 0.11, 0.15)}
LIBERTO = False   # True: bicho libertado da Fumaca Negra (cores naturais, sem brasa)


def ember_remap(m, strength=1.4, hue='roxo'):
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = next((n for n in N if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None or not bsdf.inputs['Base Color'].links:
        return
    src = bsdf.inputs['Base Color'].links[0].from_socket
    # a textura do imagem->3D ja vem com sombra pintada: clareia um pouco para nao escurecer em dobro sob a nossa luz
    hsv = N.new('ShaderNodeHueSaturation')
    hsv.inputs['Value'].default_value = 1.18
    hsv.inputs['Saturation'].default_value = 0.95
    L.new(src, hsv.inputs['Color'])
    src = hsv.outputs['Color']
    sep = N.new('ShaderNodeSeparateColor')
    sep.mode = 'HSV'
    L.new(src, sep.inputs[0])

    def ramp(sock, a, b):
        n = N.new('ShaderNodeMapRange')
        n.interpolation_type = 'SMOOTHSTEP'
        n.inputs['From Min'].default_value = a
        n.inputs['From Max'].default_value = b
        L.new(sock, n.inputs['Value'])
        return n.outputs['Result']

    def op(kind, a, b):
        n = N.new('ShaderNodeMath')
        n.operation = kind
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def mix(fac, a, b):
        n = N.new('ShaderNodeMix')
        n.data_type = 'RGBA'
        ins = [x for x in n.inputs if x.type == 'RGBA']
        L.new(fac, n.inputs[0])
        L.new(a, ins[0])
        L.new(b, ins[1])
        return next(x for x in n.outputs if x.type == 'RGBA')
    H, S, V = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    h0, h1, h2, h3 = HUES[hue]
    if hue == 'fogo':
        # chama/olho de fogo ja e laranja: so acende o que e laranja vivo e claro
        faixa = op('SUBTRACT', 1.0, ramp(H, h2, h3))
        brilho = op('MULTIPLY', op('MULTIPLY', faixa, ramp(S, 0.45, 0.6)), ramp(V, 0.6, 0.78))
        L.new(src, bsdf.inputs['Emission Color'])
        L.new(op('MULTIPLY', brilho, strength * (0.35 if LIBERTO else 1.0)), bsdf.inputs['Emission Strength'])
    else:
        faixa = op('MULTIPLY', ramp(H, h0, h1), op('SUBTRACT', 1.0, ramp(H, h2, h3)))
        roxo = op('MULTIPLY', faixa, ramp(S, 0.22, 0.34))
        claro = ramp(V, 0.45, 0.6)
        brilho = op('MULTIPLY', roxo, claro)              # pintas e olhos acesos
        sombra = op('MULTIPLY', roxo, op('SUBTRACT', 1.0, claro))   # roxo escuro de sombra -> marrom
        brasa = N.new('ShaderNodeCombineColor')
        brasa.mode = 'HSV'
        brasa.inputs[0].default_value = 0.055
        brasa.inputs[1].default_value = 0.92
        L.new(op('MULTIPLY', V, 0.85), brasa.inputs[2])
        marrom = N.new('ShaderNodeCombineColor')
        marrom.mode = 'HSV'
        marrom.inputs[0].default_value = 0.03
        marrom.inputs[1].default_value = 0.45
        L.new(V, marrom.inputs[2])
        if LIBERTO:
            # libertado: pintas e olhos viram marrom escuro de bicho (as rosetas da onca viram rosetas de verdade)
            natural = N.new('ShaderNodeCombineColor')
            natural.mode = 'HSV'
            natural.inputs[0].default_value = 0.065
            natural.inputs[1].default_value = 0.6
            L.new(op('MULTIPLY', V, 0.26), natural.inputs[2])
            # mascara mais larga que a da brasa: pega tambem o halo rosado em volta das pintas
            largo = op('MULTIPLY', faixa, ramp(S, 0.1, 0.24))
            L.new(mix(largo, src, natural.outputs[0]), bsdf.inputs['Base Color'])
        else:
            cor = mix(brilho, mix(sombra, src, marrom.outputs[0]), brasa.outputs[0])
            L.new(cor, bsdf.inputs['Base Color'])
            L.new(brasa.outputs[0], bsdf.inputs['Emission Color'])
            L.new(op('MULTIPLY', brilho, strength), bsdf.inputs['Emission Strength'])
    if hue == 'fogo':
        L.new(src, bsdf.inputs['Base Color'])
    # argila como as torres: sem metal, rugosidade 0,75, sem mapa de normal (o GLB vem com metal=1, ORM e normal)
    for nm in ('Metallic', 'Roughness', 'Normal'):
        for lk in list(bsdf.inputs[nm].links):
            L.remove(lk)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.75


def ember_remap_all(ob, cfg):
    for slot in ob.material_slots:
        if slot.material and slot.material.use_nodes:
            ember_remap(slot.material, cfg.get('glow', 1.4), cfg.get('glow_hue', 'roxo'))


# ---------------------------------------------------------------- esqueleto: ferramentas
def kmeans(pts, seeds, it=12):
    C = np.array(seeds, dtype=np.float64)
    for _ in range(it):
        d = ((pts[:, None, :] - C[None, :, :]) ** 2).sum(-1)
        j = d.argmin(1)
        for i in range(len(C)):
            if (j == i).any():
                C[i] = pts[j == i].mean(0)
    return C


def new_armature(key, root):
    ad = bpy.data.armatures.new(key + '_ossos')
    arm = bpy.data.objects.new(key + '_esqueleto', ad)
    root.users_collection[0].objects.link(arm)
    arm['set'] = key
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    return arm


def bone(arm, name, h, t, parent=None, connect=False, deform=True):
    eb = arm.data.edit_bones.new(name)
    eb.head = Vector(tuple(h))
    eb.tail = Vector(tuple(t))
    if (eb.tail - eb.head).length < 1e-4:
        eb.tail = eb.head + Vector((0, 0, 0.02))
    eb.align_roll(Vector((0, 1, 0)) if abs((eb.tail - eb.head).normalized().y) < 0.9 else Vector((0, 0, 1)))
    if parent:
        eb.parent = arm.data.edit_bones[parent]
        eb.use_connect = connect
    eb.use_deform = deform
    return eb


def chain(arm, prefix, pts, parent, connect_first=False):
    names = []
    for i in range(len(pts) - 1):
        nm = f'{prefix}{i}'
        bone(arm, nm, pts[i], pts[i + 1], parent if i == 0 else names[-1], connect=(i > 0) or connect_first)
        names.append(nm)
    return names


def path_through(P, attach, n=3):
    """Centros de n fatias de uma regiao (cauda, pescoco...) ao longo do seu eixo principal, a partir do ponto de apoio."""
    if len(P) < 20:
        return []
    c = P.mean(0)
    u = np.linalg.svd(P - c, full_matrices=False)[2][0]
    t = (P - c) @ u
    if abs((np.asarray(attach) - c) @ u - t.min()) > abs((np.asarray(attach) - c) @ u - t.max()):
        u, t = -u, -t
    edges = np.linspace(t.min(), t.max(), n + 1)
    pts = []
    for i in range(n):
        m = (t >= edges[i]) & (t <= edges[i + 1])
        if m.any():
            pts.append(P[m].mean(0))
    return pts


def skin(arm, ob, allow=None, power=4.0, keep=3):
    """Pesos suaves por distancia aos ossos (o 'calor' do Blender falha nessas malhas pequenas e abertas).
    allow(nome_osso, P) -> mascara booleana de quais vertices podem seguir aquele osso."""
    bpy.ops.object.mode_set(mode='OBJECT')
    P = verts_np(ob)
    names, W = [], []
    for b in arm.data.bones:
        if not b.use_deform:
            continue
        a, c = np.array(b.head_local), np.array(b.tail_local)
        ab = c - a
        t = np.clip(((P - a) @ ab) / max(1e-12, ab @ ab), 0.0, 1.0)
        d = np.linalg.norm(a + t[:, None] * ab - P, axis=1)
        w = 1.0 / (d + 0.004) ** power
        if allow:
            w = np.where(allow(b.name, P), w, 0.0)
        names.append(b.name)
        W.append(w)
    W = np.stack(W, axis=1)
    orphan = W.sum(1) == 0
    if orphan.any():
        # vertice que nenhuma regra aceitou: vai so pela distancia
        W[orphan] = np.stack([1.0 / (np.linalg.norm(P[orphan] - (np.array(b.head_local) + np.array(b.tail_local)) / 2, axis=1) + 0.004) ** power
                              for b in arm.data.bones if b.use_deform], axis=1)
    if keep < W.shape[1]:
        cut = np.sort(W, axis=1)[:, -keep][:, None]
        W = np.where(W >= cut, W, 0.0)
    W = W / W.sum(axis=1, keepdims=True)
    for j, nm in enumerate(names):
        g = ob.vertex_groups.new(name=nm)
        col = np.round(W[:, j], 2)
        for lv in np.unique(col[col > 0.01]):
            g.add(np.nonzero(col == lv)[0].tolist(), float(lv), 'REPLACE')
    ob.parent = arm
    md = ob.modifiers.new('Esqueleto', 'ARMATURE')
    md.object = arm
    for pb_ in arm.pose.bones:
        pb_.rotation_mode = 'QUATERNION'
    print('pele:', len(P), 'vertices,', len(names), 'ossos,', int(orphan.sum()), 'orfaos')


def body_frame(P):
    H = P[:, 2].max()
    x0, x1 = P[:, 0].min(), P[:, 0].max()
    y0, y1 = P[:, 1].min(), P[:, 1].max()
    return H, x0, x1, y0, y1, x1 - x0, y1 - y0


# ---------------------------------------------------------------- esqueletos por tipo de corpo
def rig_quad(key, ob, root, cfg):
    P = verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = body_frame(P)
    cy = float(np.median(P[:, 1]))
    low = P[P[:, 2] < cfg.get('low', 0.1) * H]
    if cfg.get('sprawl'):
        low = low[np.abs(low[:, 1] - cy) > 0.22 * Wy]
    xm = low[:, 0].mean()
    s = 0.25 * Wy
    C = kmeans(low[:, :2], [(xm + 0.2 * Lx, cy + s), (xm + 0.2 * Lx, cy - s), (xm - 0.2 * Lx, cy + s), (xm - 0.2 * Lx, cy - s)])
    C = sorted([Vector((c[0], c[1], 0)) for c in C], key=lambda c: -c.x)
    front, back = sorted(C[:2], key=lambda c: -c.y), sorted(C[2:], key=lambda c: -c.y)
    feetd = {'FL': front[0], 'FR': front[1], 'BL': back[0], 'BR': back[1]}
    xf, xb = (front[0].x + front[1].x) / 2, (back[0].x + back[1].x) / 2

    def top_at(x, w=0.05):
        m = (np.abs(P[:, 0] - x) < w * Lx) & (np.abs(P[:, 1] - cy) < 0.15 * Wy)
        return P[m, 2].max() if m.any() else 0.6 * H
    hz = 0.62 * min(top_at(xf), top_at(xb))
    arm = new_armature(key, root)
    bone(arm, 'raiz', (0, cy, hz * 0.6), (0, cy, hz * 0.6 + 0.04), deform=False)
    bone(arm, 'quadril', (xb, cy, hz), ((xb + xf) / 2, cy, hz), 'raiz')
    bone(arm, 'peito', ((xb + xf) / 2, cy, hz), (xf, cy, hz), 'quadril', True)
    hm = P[:, 0] > xf + 0.08 * Lx
    if hm.sum() > 30:
        hc = P[hm].mean(0)
        bone(arm, 'pescoco', (xf, cy, hz), (hc[0] - 0.04 * Lx, cy, hc[2]), 'peito', True)
        bone(arm, 'cabeca', (hc[0] - 0.04 * Lx, cy, hc[2]), (x1, cy, hc[2]), 'pescoco', True)
    tm = P[:, 0] < xb - 0.1 * Lx
    if tm.sum() > 30:
        pts = path_through(P[tm], (xb, cy, hz), 3)
        chain(arm, 'cauda', [Vector((xb, cy, hz))] + [Vector(p) for p in pts], 'quadril')
    for nm, f in feetd.items():
        par = 'peito' if nm[0] == 'F' else 'quadril'
        top = Vector((f.x, cy + (f.y - cy) * (0.45 if cfg.get('sprawl') else 0.8), hz * 0.95))
        knee = Vector((f.x, cy + (f.y - cy) * (0.85 if cfg.get('sprawl') else 1.0), hz * 0.45))
        foot = Vector((f.x, f.y, 0.02 * H))
        bone(arm, 'coxa' + nm, top, knee, par)
        bone(arm, 'canela' + nm, knee, foot, 'coxa' + nm, True)

    def allow(nm, Pv):
        x, y, z = Pv[:, 0], Pv[:, 1], Pv[:, 2]
        if nm.startswith(('coxa', 'canela')):
            f = feetd[nm[-2:]]
            ok = (np.sign(y - cy) == np.sign(f.y - cy)) | (np.abs(y - cy) > 0.5 * abs(f.y - cy))
            ok &= np.abs(x - f.x) < 0.2 * Lx
            ok &= z < hz * (1.0 if nm.startswith('coxa') else 0.6)
            return ok
        if nm.startswith('cauda'):
            return x < xb - 0.02 * Lx
        if nm in ('pescoco', 'cabeca'):
            return x > xf - 0.06 * Lx
        return np.ones(len(x), dtype=bool)
    skin(arm, ob, allow)
    return arm, {'H': H, 'L': Lx, 'hz': hz, 'legs': {k: Vector(v) for k, v in feetd.items()}}


def rig_hexa(key, ob, root, cfg):
    P = verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = body_frame(P)
    cy = float(np.median(P[:, 1]))
    # corpo: o que esta perto da linha do meio
    core = P[np.abs(P[:, 1] - cy) < 0.12 * Wy]
    bhw = np.percentile(np.abs(P[P[:, 2] > 0.3 * H, 1] - cy), 40)
    low = P[(P[:, 2] < cfg.get('low', 0.08) * H) & (np.abs(P[:, 1] - cy) > bhw)]
    qx = np.percentile(low[:, 0], [15, 50, 85])
    seeds = [(qx[i], cy + s * 0.4 * Wy) for i in range(3) for s in (1, -1)]
    C = kmeans(low[:, :2], seeds)
    feet = {}
    for s, side in ((1, 'L'), (-1, 'R')):
        cs = sorted([c for c in C if s * (c[1] - cy) > 0], key=lambda c: -c[0])
        for i, c in enumerate(cs[:3]):
            feet[f'{side}{i}'] = Vector((c[0], c[1], 0.0))
    # eixo do corpo: cabeca na frente, torax no meio, abdomen atras
    zc = np.percentile(core[:, 2], 55)
    xt = np.mean([f.x for f in feet.values()])
    hz = float(np.percentile(core[np.abs(core[:, 0] - xt) < 0.08 * Lx, 2], 50)) if (np.abs(core[:, 0] - xt) < 0.08 * Lx).any() else zc
    arm = new_armature(key, root)
    bone(arm, 'raiz', (xt, cy, hz * 0.5), (xt, cy, hz * 0.5 + 0.03), deform=False)
    bone(arm, 'torax', (xt - 0.08 * Lx, cy, hz), (xt + 0.1 * Lx, cy, hz), 'raiz')
    hm = core[:, 0] > xt + 0.12 * Lx
    hc = core[hm].mean(0) if hm.sum() > 20 else np.array([x1 - 0.1 * Lx, cy, hz])
    bone(arm, 'cabeca', (xt + 0.1 * Lx, cy, hz), (core[:, 0].max(), cy, hc[2]), 'torax', True)
    am = core[:, 0] < xt - 0.12 * Lx
    ac = core[am].mean(0) if am.sum() > 20 else np.array([x0 + 0.2 * Lx, cy, hz])
    bone(arm, 'abdomen', (xt - 0.08 * Lx, cy, hz), (core[:, 0].min(), cy, ac[2]), 'torax', True)
    legs = {}
    for nm, f in feet.items():
        s = 1 if nm[0] == 'L' else -1
        hip = Vector((xt + (f.x - xt) * 0.25, cy + s * bhw * 0.7, hz * 0.85))
        mid = hip.lerp(f, 0.42)
        near = P[(np.linalg.norm(P[:, :2] - np.array([mid.x, mid.y]), axis=1) < 0.06 * Lx)]
        knee = Vector((mid.x, mid.y, float(near[:, 2].max()) if len(near) else hz * 1.1))
        bone(arm, 'coxa' + nm, hip, knee, 'torax')
        bone(arm, 'canela' + nm, knee, (f.x, f.y, 0.01 * H), 'coxa' + nm, True)
        legs[nm] = (hip, f)

    def allow(nm, Pv):
        y = Pv[:, 1]
        if nm.startswith(('coxa', 'canela')):
            s = 1 if nm[4 if nm.startswith('coxa') else 6] == 'L' else -1
            return s * (y - cy) > bhw * 0.6
        return np.abs(y - cy) < bhw * 1.6
    skin(arm, ob, allow, power=5.0)
    return arm, {'H': H, 'L': Lx, 'legs': legs}


def rig_biped(key, ob, root, cfg):
    P = verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = body_frame(P)
    hip, sh, nk = cfg.get('hip', 0.36) * H, cfg.get('shoulder', 0.6) * H, cfg.get('neck', 0.64) * H
    band = P[(P[:, 2] > hip) & (P[:, 2] < sh)]
    cx, cy = float(np.median(band[:, 0])), float(np.median(band[:, 1]))
    low = P[P[:, 2] < 0.07 * H]
    C = kmeans(low[:, :2], [(cx, cy + 0.15 * Wy), (cx, cy - 0.15 * Wy)])
    C = sorted([Vector((c[0], c[1], 0)) for c in C], key=lambda c: -c.y)
    feet = {'L': C[0], 'R': C[1]}
    ymid = (C[0].y + C[1].y) / 2
    torso = P[(P[:, 2] > sh - 0.06 * H) & (P[:, 2] < sh + 0.02 * H)]
    shw = float(np.percentile(np.abs(torso[:, 1] - cy), 80)) if len(torso) else 0.2 * Wy
    hands = {}
    hl = cfg.get('hand_low', 0.26) * H      # abaixo disso e barra de calca/pe, nao mao
    for s, nm in ((1, 'L'), (-1, 'R')):
        side = P[(s * (P[:, 1] - cy) > 0.3 * shw) & (P[:, 2] > hl) & (P[:, 2] < sh)]
        q = s * (side[:, 1] - cy)
        hands[nm] = Vector(side[q >= np.percentile(q, 96)].mean(0))
    arm = new_armature(key, root)
    bone(arm, 'raiz', (cx, cy, hip * 0.5), (cx, cy, hip * 0.5 + 0.03), deform=False)
    bone(arm, 'quadril', (cx, cy, hip), (cx, cy, (hip + sh) / 2), 'raiz')
    bone(arm, 'peito', (cx, cy, (hip + sh) / 2), (cx, cy, nk), 'quadril', True)
    bone(arm, 'cabeca', (cx, cy, nk), (cx, cy, H), 'peito', True)
    for nm, f in feet.items():
        knee = Vector((f.x + 0.02 * H, f.y, hip * 0.5))
        bone(arm, 'coxa' + nm, (f.x, f.y, hip), knee, 'quadril')
        bone(arm, 'canela' + nm, knee, (f.x, f.y, 0.02 * H), 'coxa' + nm, True)
    for s, nm in ((1, 'L'), (-1, 'R')):
        shp = Vector((cx, cy + s * shw * 0.85, sh))
        hd = hands[nm]
        el = shp.lerp(hd, 0.5) + Vector((-0.03 * H, 0, 0))
        bone(arm, 'braco' + nm, shp, el, 'peito')
        bone(arm, 'antebraco' + nm, el, hd, 'braco' + nm, True)
    tail_x = None
    if cfg.get('tail'):
        tm = (P[:, 0] < cx - 0.2 * Lx) & (P[:, 2] > 0.1 * H)
        if tm.sum() > 30:
            base = Vector((cx - 0.08 * Lx, cy, hip))
            pts = path_through(P[tm], base, 3)
            chain(arm, 'cauda', [base] + [Vector(p) for p in pts], 'quadril')
            tail_x = cx - 0.15 * Lx

    # largura da cabeca (acima do pescoco): bochecha, orelha e cabelo nunca seguem o braco, mesmo com a mao encostada
    # no rosto (joinha no queixo, celular na orelha, "L" na bochecha); sem isso o rosto esticava junto com o gesto
    headp = P[P[:, 2] > nk + 0.06 * H]
    head_hw = float(np.percentile(np.abs(headp[:, 1] - cy), 92)) if len(headp) > 50 else 0.0

    def arm_zone(side, Pv):
        x, y, z = Pv[:, 0], Pv[:, 1], Pv[:, 2]
        s = 1 if side == 'L' else -1
        hd = hands[side]
        far = s * (y - cy)
        ok = (far > 0.55 * shw) & (z < sh + 0.08 * H) & (z > hd.z - 0.1 * H)
        ok &= (z > hip) | (far > abs(feet[side].y - cy) + 0.06 * H)
        ok &= ~((z > sh - 0.03 * H) & (np.abs(y - cy) < head_hw * 1.04))
        return ok

    def allow(nm, Pv):
        x, y, z = Pv[:, 0], Pv[:, 1], Pv[:, 2]
        if nm.startswith(('coxa', 'canela')):
            me, other = feet[nm[-1]], feet['R' if nm[-1] == 'L' else 'L']
            ok = z < hip + 0.03 * H
            # cada vertice so segue a perna do pe mais perto (no plano), sem dividir entre as duas
            dm = (x - me.x) ** 2 + (y - me.y) ** 2
            do = (x - other.x) ** 2 + (y - other.y) ** 2
            ok &= dm < do
            # mao pendurada na altura do quadril nao e perna
            ok &= np.abs(y - me.y) < max(0.11 * H, 1.3 * abs(me.y - ymid))
            if tail_x is not None:
                ok &= x > tail_x
            return ok
        if nm.startswith(('braco', 'antebraco')):
            return arm_zone(nm[-1], Pv)
        if nm.startswith('cauda'):
            return x < cx - 0.1 * Lx
        if nm == 'cabeca':
            return z > nk - 0.05 * H
        # tronco nao segura os pes (o pe esticava no chao) nem o braco abaixo do ombro (o braco esticava)
        ombro = z > sh - 0.06 * H
        return (z > hip * 0.8) & (ombro | ~(arm_zone('L', Pv) | arm_zone('R', Pv)))
    skin(arm, ob, allow)
    return arm, {'H': H, 'L': Lx}


def rig_mermaid(key, ob, root, cfg):
    P = verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = body_frame(P)
    hip, sh, nk = cfg.get('hip', 0.42) * H, cfg.get('shoulder', 0.6) * H, cfg.get('neck', 0.64) * H
    band = P[(P[:, 2] > hip) & (P[:, 2] < sh)]
    cx, cy = float(np.median(band[:, 0])), float(np.median(band[:, 1]))
    torso = P[(P[:, 2] > sh - 0.06 * H) & (P[:, 2] < sh + 0.02 * H) & (np.abs(P[:, 0] - cx) < 0.15 * Lx)]
    shw = float(np.percentile(np.abs(torso[:, 1] - cy), 80)) if len(torso) else 0.2 * Wy
    hands = {}
    for s, nm in ((1, 'L'), (-1, 'R')):
        side = P[(s * (P[:, 1] - cy) > 0.3 * shw) & (P[:, 2] > hip * 0.8) & (P[:, 2] < sh) & (np.abs(P[:, 0] - cx) < 0.25 * Lx)]
        q = s * (side[:, 1] - cy)
        hands[nm] = Vector(side[q >= np.percentile(q, 96)].mean(0))
    arm = new_armature(key, root)
    bone(arm, 'raiz', (cx, cy, hip), (cx, cy, hip + 0.03), deform=False)
    bone(arm, 'quadril', (cx, cy, hip), (cx, cy, (hip + sh) / 2), 'raiz')
    bone(arm, 'peito', (cx, cy, (hip + sh) / 2), (cx, cy, nk), 'quadril', True)
    bone(arm, 'cabeca', (cx, cy, nk), (cx, cy, H), 'peito', True)
    for s, nm in ((1, 'L'), (-1, 'R')):
        shp = Vector((cx, cy + s * shw * 0.85, sh))
        el = shp.lerp(hands[nm], 0.5) + Vector((-0.02 * H, 0, 0))
        bone(arm, 'braco' + nm, shp, el, 'peito')
        bone(arm, 'antebraco' + nm, el, hands[nm], 'braco' + nm, True)
    tm = P[:, 2] < hip
    pts = path_through(P[tm], (cx, cy, hip), 4)
    chain(arm, 'cauda', [Vector((cx, cy, hip))] + [Vector(p) for p in pts], 'quadril')

    def allow(nm, Pv):
        x, y, z = Pv[:, 0], Pv[:, 1], Pv[:, 2]
        if nm.startswith(('braco', 'antebraco')):
            s = 1 if nm[-1] == 'L' else -1
            return (s * (y - cy) > 0.55 * shw) & (z > hip * 0.8) & (z < sh + 0.08 * H) & (np.abs(x - cx) < 0.3 * Lx)
        if nm.startswith('cauda'):
            return z < hip + 0.04 * H
        if nm == 'cabeca':
            return z > nk - 0.05 * H
        return z > hip - 0.06 * H
    skin(arm, ob, allow)
    return arm, {'H': H, 'L': Lx}


def rig_serpent(key, ob, root, cfg):
    P = verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = body_frame(P)
    coil = cfg.get('coil', 0.4) * H
    base = P[P[:, 2] < 0.2 * H].mean(0)
    head = P[P[:, 2] > 0.84 * H]
    hc = head.mean(0)
    tip = head[head[:, 0] >= np.percentile(head[:, 0], 92)].mean(0)
    neck = P[(P[:, 2] > coil) & (P[:, 2] < 0.84 * H)]
    pts = path_through(neck, (base[0], base[1], coil), 3)
    p0 = Vector((pts[0][0], pts[0][1], coil)) if pts else Vector((base[0], base[1], coil))
    arm = new_armature(key, root)
    bone(arm, 'raiz', (base[0], base[1], 0.02), (base[0], base[1], 0.06), deform=False)
    bone(arm, 'enrolado', (base[0], base[1], 0.0), p0, 'raiz')
    names = chain(arm, 'pesc', [p0] + [Vector(p) for p in pts[1:]] + [Vector(hc)], 'enrolado')
    bone(arm, 'cabeca', Vector(hc), Vector(tip) + Vector((0.01, 0, 0)), names[-1], True)

    def allow(nm, Pv):
        z = Pv[:, 2]
        if nm == 'enrolado':
            return z < coil + 0.06 * H
        if nm == 'cabeca':
            return z > 0.76 * H
        return z > coil - 0.05 * H
    skin(arm, ob, allow)
    return arm, {'H': H, 'L': Lx, 'neck': names}


def rig_flyer(key, ob, root, cfg):
    P = verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = body_frame(P)
    cy = float(np.median(P[:, 1]))
    core = P[np.abs(P[:, 1] - cy) < 0.14 * Wy]
    bc = core.mean(0)
    bhw = float(np.percentile(np.abs(core[:, 1] - cy), 90))
    wz = float(np.percentile(P[np.abs(P[:, 1] - cy) > 0.3 * Wy, 2], 50))
    arm = new_armature(key, root)
    bone(arm, 'raiz', (bc[0], cy, bc[2] - 0.05), (bc[0], cy, bc[2] - 0.02), deform=False)
    bone(arm, 'corpo', (bc[0], cy, core[:, 2].min() + 0.1 * H), (bc[0], cy, bc[2] + 0.1 * H), 'raiz')
    top = core[core[:, 2] > np.percentile(core[:, 2], 75)].mean(0)
    bone(arm, 'cabeca', (bc[0], cy, bc[2] + 0.1 * H), (top[0], cy, core[:, 2].max()), 'corpo', True)
    wings = {}
    for s, nm in ((1, 'L'), (-1, 'R')):
        side = P[s * (P[:, 1] - cy) > bhw]
        q = s * (side[:, 1] - cy)
        tip = side[q >= np.percentile(q, 95)].mean(0)
        root_p = Vector((bc[0], cy + s * bhw * 0.8, wz))
        mid = root_p.lerp(Vector(tip), 0.5)
        ring = np.abs(q - s * (mid.y - cy)) < 0.05 * Wy
        if ring.any():
            mid.z = float(side[ring, 2].mean())
        bone(arm, f'asa{nm}0', root_p, mid, 'corpo')
        bone(arm, f'asa{nm}1', mid, Vector(tip), f'asa{nm}0', True)
        wings[nm] = (root_p, mid, Vector(tip))

    def allow(nm, Pv):
        y = Pv[:, 1]
        if nm.startswith('asa'):
            s = 1 if nm[3] == 'L' else -1
            far = s * (y - cy)
            if nm.endswith('1'):
                return far > 0.5 * abs(wings[nm[3]][1].y - cy)
            return far > bhw * 0.7
        if nm == 'cabeca':
            return Pv[:, 2] > bc[2]
        return np.abs(y - cy) < bhw * 1.5
    skin(arm, ob, allow)
    return arm, {'H': H, 'L': Lx}


RIGS = {'quad': rig_quad, 'hexa': rig_hexa, 'biped': rig_biped, 'mermaid': rig_mermaid, 'serpent': rig_serpent, 'flyer': rig_flyer}


# ---------------------------------------------------------------- poses
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def pb(arm, n):
    return arm.pose.bones.get(n)


def turn(arm, n, *rots):
    """Gira o osso em torno de eixos do espaco do esqueleto (frente = +X, esquerda = +Y, cima = +Z).
    Em +Y: osso para baixo vai para tras; osso para a frente abaixa. Em +X: asa esquerda sobe."""
    b = pb(arm, n)
    if not b:
        return
    M = b.bone.matrix_local.to_3x3().inverted()
    q = Quaternion()
    for ax, ang in rots:
        q = Quaternion(M @ Vector(ax), ang) @ q
    b.rotation_quaternion = q


def grow(arm, n, k):
    b = pb(arm, n)
    if b:
        b.scale = (1.0, k, 1.0)


def reset(arm):
    for b in arm.pose.bones:
        b.rotation_quaternion = (1, 0, 0, 0)
        b.location = (0, 0, 0)
        b.scale = (1, 1, 1)


def place(parts, view, loc=(0, 0, 0), rx=0.0, ry=0.0):
    corpo = parts['body']
    extra = parts['cfg'].get('show8', TURN) if view[0] == 'w' else parts['cfg'].get('show', 0.0)
    corpo.rotation_euler = (rx, ry, VIEWS[view] + math.radians(extra))
    lift = 0.0
    if rx or ry:
        # tombado: sobe o corpo o quanto ele desceria abaixo do chao (o chao de sombra esconde o que fica embaixo)
        cx, sx, cyy, syy = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry)
        Pt = parts['pts']
        z1 = Pt[:, 1] * sx + Pt[:, 2] * cx
        x1 = Pt[:, 0]
        z2 = -x1 * syy + z1 * cyy
        lift = max(0.0, -float(z2.min()))
    corpo.location = (loc[0], loc[1], loc[2] + lift)


PHASE = {'FL': 0.0, 'BR': 0.0, 'FR': math.pi, 'BL': math.pi}   # trote: diagonais juntas


def pose_quad(parts, mode, f, view):
    arm = parts['arm']
    reset(arm)
    a = TAU * f / WALK_N
    sw, kn = 0.42, 0.75
    tails = [b.name for b in arm.pose.bones if b.name.startswith('cauda')]
    if mode == 'walk':
        cfg = parts['cfg']
        ging = cfg.get('ginga', 0.0)          # bicho baixo de perna curta: o corpo balanca de lado a cada passo
        sw, kn = cfg.get('passo', sw), cfg.get('joelho', kn)
        place(parts, view, (0, 0, cfg.get('pulo', 0.012) * abs(math.sin(2 * a if ging else a))), rx=ging * math.sin(a))
        for nm, ph in PHASE.items():
            b = a + ph
            turn(arm, 'coxa' + nm, (Y, -sw * math.sin(b)))
            turn(arm, 'canela' + nm, (Y, kn * max(0.0, math.cos(b)) * (1 if nm[0] == 'F' else -1)))
        turn(arm, 'quadril', (Z, 0.04 * math.sin(a)))
        turn(arm, 'cabeca', (Y, 0.05 * math.sin(2 * a)), (Z, 0.08 * ging / 0.1 * math.sin(a) if ging else 0.0))
        for i, t in enumerate(tails):
            turn(arm, t, (Z, cfg.get('cauda', 0.22) * math.sin(a - i * 0.7)), (Y, -0.05 * math.cos(a - i)))
    elif mode == 'atk':
        # bote: agacha, salta para a frente com as patas da frente esticadas e volta
        t = f / (ATK_N - 1)
        crouch = math.sin(math.pi * min(1.0, t / 0.4)) if t < 0.4 else 0.0
        leap = math.sin(math.pi * max(0.0, min(1.0, (t - 0.3) / 0.7)))
        place(parts, view, (0.12 * leap, 0, 0.06 * leap - 0.02 * crouch), ry=-0.15 * leap + 0.06 * crouch)
        for nm in ('FL', 'FR'):
            turn(arm, 'coxa' + nm, (Y, -0.9 * leap + 0.2 * crouch))
            turn(arm, 'canela' + nm, (Y, -0.3 * leap))
        for nm in ('BL', 'BR'):
            turn(arm, 'coxa' + nm, (Y, 0.5 * leap - 0.3 * crouch))
            turn(arm, 'canela' + nm, (Y, -0.6 * crouch))
        turn(arm, 'cabeca', (Y, -0.2 * leap))
        for t_ in tails:
            turn(arm, t_, (Y, -0.15 * leap))
    else:
        # morte: tomba de lado e as patas recolhem
        t = f / (DIE_N - 1)
        e = smooth01(t)
        place(parts, view, (0, 0.05 * e, 0.03 * math.sin(math.pi * min(1.0, t * 1.6))), rx=1.45 * e)
        for nm in PHASE:
            turn(arm, 'coxa' + nm, (Y, -0.35 * e * (1 if nm[0] == 'F' else -1)))
            turn(arm, 'canela' + nm, (Y, 0.6 * e * (1 if nm[0] == 'F' else -1)))
        turn(arm, 'cabeca', (Y, 0.3 * e))
        for t_ in tails:
            turn(arm, t_, (Z, 0.2 * e))


TRIPOD = {'L0': 0.0, 'R1': 0.0, 'L2': 0.0, 'R0': math.pi, 'L1': math.pi, 'R2': math.pi}


def pose_hexa(parts, mode, f, view):
    arm, legs = parts['arm'], parts['info']['legs']
    reset(arm)
    a = TAU * f / WALK_N

    def leg(nm, swing, lift, curl=0.0):
        hip, foot = legs[nm]
        d = (foot - hip)
        d.z = 0
        d.normalize()
        turn(arm, 'coxa' + nm, (Z, swing), ((d.y, -d.x, 0), lift))
        turn(arm, 'canela' + nm, ((d.y, -d.x, 0), -curl))
    if mode == 'walk':
        place(parts, view, (0, 0, 0.006 * abs(math.sin(2 * a))))
        for nm, ph in TRIPOD.items():
            if nm in legs:
                b = a + ph
                s = 1 if nm[0] == 'L' else -1
                leg(nm, s * 0.32 * math.sin(b), 0.35 * max(0.0, math.cos(b)))
        turn(arm, 'cabeca', (Z, 0.05 * math.sin(a)), (Y, 0.04 * math.sin(2 * a)))
        turn(arm, 'abdomen', (Z, -0.06 * math.sin(a)), (Y, 0.05 * math.cos(2 * a)))
    elif mode == 'atk':
        # empina e morde
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t / 0.6))
        bite = max(0.0, (t - 0.55) / 0.45)
        place(parts, view, (0.03 * bite, 0, 0.02 * up))
        turn(arm, 'torax', (Y, -0.35 * up + 0.3 * bite))
        turn(arm, 'cabeca', (Y, -0.2 * up + 0.5 * bite))
        turn(arm, 'abdomen', (Y, 0.15 * up))
        for nm in legs:
            if nm.endswith('0'):
                leg(nm, 0.0, 0.6 * up)
    else:
        # vira de costas e encolhe as patas
        t = f / (DIE_N - 1)
        e = smooth01(t)
        place(parts, view, (0, 0, 0.05 * math.sin(math.pi * min(1.0, t * 1.4)) + 0.06 * e), rx=math.pi * e * 0.95)
        for nm in legs:
            leg(nm, 0.0, 0.7 * e, 1.2 * e)


def pose_biped(parts, mode, f, view):
    arm = parts['arm']
    reset(arm)
    a = TAU * f / WALK_N
    tails = [b.name for b in arm.pose.bones if b.name.startswith('cauda')]
    if mode == 'walk':
        place(parts, view, (0, 0, 0.014 * abs(math.sin(a))))
        passo, joelho = parts['cfg'].get('passo', 0.45), parts['cfg'].get('joelho', 0.7)
        for nm, s in (('L', 1), ('R', -1)):
            ph = s * math.sin(a)
            turn(arm, 'coxa' + nm, (Y, -passo * ph))
            turn(arm, 'canela' + nm, (Y, joelho * max(0.0, s * math.cos(a))))
            sw = parts['cfg'].get('arm', 0.5)
            turn(arm, 'braco' + nm, (Y, sw * ph), (X, s * 0.12))
            turn(arm, 'antebraco' + nm, (Y, -0.5 * sw - 0.3 * sw * ph))
        turn(arm, 'peito', (Z, 0.1 * math.sin(a)), (Y, 0.04))
        turn(arm, 'cabeca', (Z, -0.06 * math.sin(a)), (Y, 0.04 * math.sin(2 * a)))
        for i, t in enumerate(tails):
            turn(arm, t, (Z, 0.25 * math.sin(a - i * 0.8)))
    elif mode == 'atk':
        # ergue os bracos e bate para a frente
        t = f / (ATK_N - 1)
        up = math.sin(math.pi * min(1.0, t / 0.55)) if t < 0.55 else 0.0
        hit = max(0.0, (t - 0.45) / 0.55)
        place(parts, view, (0.03 * hit, 0, 0))
        turn(arm, 'peito', (Y, -0.15 * up + 0.3 * hit))
        rz = parts['cfg'].get('ergue', 2.3)
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, 'braco' + nm, (Y, -rz * up - 0.5 * rz * hit), (X, s * 0.2))
            turn(arm, 'antebraco' + nm, (Y, -0.2 * rz * up))
            turn(arm, 'coxa' + nm, (Y, 0.25 * hit * s))
        turn(arm, 'cabeca', (Y, 0.15 * hit))
    else:
        # cai de costas
        t = f / (DIE_N - 1)
        e = smooth01(t)
        place(parts, view, (-0.06 * e, 0, 0.03 * math.sin(math.pi * min(1.0, t * 1.6))), ry=-1.45 * e)
        rz = parts['cfg'].get('ergue', 2.3)
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, 'braco' + nm, (Y, -0.5 * rz * e), (X, s * 0.2 * rz * e))
            turn(arm, 'coxa' + nm, (Y, -0.4 * e))
            turn(arm, 'canela' + nm, (Y, 0.5 * e))
        turn(arm, 'cabeca', (Y, -0.3 * e))


def pose_mermaid(parts, mode, f, view):
    arm = parts['arm']
    reset(arm)
    a = TAU * f / WALK_N
    tails = [b.name for b in arm.pose.bones if b.name.startswith('cauda')]
    if mode == 'walk':
        place(parts, view, (0, 0, 0.03 + 0.02 * math.sin(a)))
        for i, t in enumerate(tails):
            turn(arm, t, (Y, 0.18 * math.sin(a - i * 0.9)), (Z, 0.08 * math.sin(a - i)))
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, 'braco' + nm, (X, s * (0.25 + 0.1 * math.sin(a))), (Y, 0.1 * math.sin(a + s)))
        turn(arm, 'cabeca', (X, 0.06 * math.sin(a)))
        turn(arm, 'peito', (Y, 0.04 * math.sin(a)))
    elif mode == 'atk':
        # ergue os bracos e solta o canto
        t = f / (ATK_N - 1)
        k = math.sin(math.pi * t)
        place(parts, view, (0, 0, 0.03 + 0.04 * k))
        turn(arm, 'peito', (Y, -0.2 * k))
        turn(arm, 'cabeca', (Y, -0.25 * k))
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, 'braco' + nm, (Y, -1.6 * k), (X, s * 0.4 * k))
        for i, t_ in enumerate(tails):
            turn(arm, t_, (Y, 0.25 * k * (1 if i % 2 else -1)))
    else:
        t = f / (DIE_N - 1)
        e = smooth01(t)
        place(parts, view, (-0.04 * e, 0, 0.03 * (1 - e)), ry=-1.4 * e)
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, 'braco' + nm, (Y, -1.0 * e), (X, s * 0.6 * e))
        for t_ in tails:
            turn(arm, t_, (Y, -0.2 * e))


def pose_serpent(parts, mode, f, view):
    arm, neck = parts['arm'], parts['info']['neck']
    reset(arm)
    a = TAU * f / WALK_N
    if mode == 'walk':
        place(parts, view)
        turn(arm, 'enrolado', (Z, 0.05 * math.sin(a)))
        grow(arm, 'enrolado', 1.0 + 0.04 * math.sin(2 * a))
        for i, n in enumerate(neck):
            turn(arm, n, (X, 0.13 * math.sin(a - i * 0.9)), (Y, 0.05 * math.sin(2 * a - i)))
        turn(arm, 'cabeca', (Y, 0.1 * math.sin(2 * a)), (X, -0.1 * math.sin(a - 2.4)))
    elif mode == 'atk':
        # bote: recua o pescoco e da o bote para a frente
        t = f / (ATK_N - 1)
        back = math.sin(math.pi * min(1.0, t / 0.4)) if t < 0.4 else 0.0
        hit = math.sin(math.pi * max(0.0, min(1.0, (t - 0.3) / 0.7)))
        place(parts, view)
        for n in neck:
            turn(arm, n, (Y, -0.18 * back + 0.32 * hit))
        turn(arm, 'cabeca', (Y, 0.4 * hit - 0.2 * back))
    else:
        t = f / (DIE_N - 1)
        e = smooth01(t)
        place(parts, view)
        grow(arm, 'enrolado', 1.0 - 0.35 * e)
        for i, n in enumerate(neck):
            turn(arm, n, (Y, 0.55 * e), (X, 0.1 * e * (i - 1)))
        turn(arm, 'cabeca', (Y, 0.3 * e))


def pose_flyer(parts, mode, f, view):
    arm = parts['arm']
    reset(arm)
    a = TAU * f / WALK_N
    amp = parts['cfg'].get('flap', 0.6)
    if mode == 'walk':
        place(parts, view, (0, 0, -0.025 * math.sin(a)))
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, f'asa{nm}0', (X, s * amp * math.sin(a)))
            turn(arm, f'asa{nm}1', (X, s * 0.5 * amp * math.sin(a - 0.7)))
        turn(arm, 'cabeca', (Y, 0.06 * math.sin(a + 1)))
    elif mode == 'atk':
        # mergulho curto com as asas para tras
        t = f / (ATK_N - 1)
        k = math.sin(math.pi * t)
        place(parts, view, (0.06 * k, 0, -0.04 * k), ry=0.35 * k)
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, f'asa{nm}0', (X, s * 0.7 * k), (Z, -s * 0.5 * k))
        turn(arm, 'cabeca', (Y, 0.2 * k))
    else:
        t = f / (DIE_N - 1)
        e = smooth01(t)
        place(parts, view, (0, 0, -0.08 * e), rx=1.1 * e, ry=0.6 * e)
        for nm, s in (('L', 1), ('R', -1)):
            turn(arm, f'asa{nm}0', (X, -s * 0.9 * e))
            turn(arm, f'asa{nm}1', (X, -s * 0.8 * e))


POSES = {'quad': pose_quad, 'hexa': pose_hexa, 'biped': pose_biped, 'mermaid': pose_mermaid, 'serpent': pose_serpent, 'flyer': pose_flyer}


# ---------------------------------------------------------------- montagem na familia
def builder(key):
    cfg = CFG[key]

    def build(P, root):
        ob = import_glb(key, cfg, root)
        arm, info = RIGS[cfg['plan']](key, ob, root, cfg)
        corpo = empty(root, key + '_corpo')
        arm.parent = corpo
        P = verts_np(ob)
        pts = P[np.random.default_rng(1).choice(len(P), min(3000, len(P)), replace=False)]
        return {'tag': key, 'body': corpo, 'arm': arm, 'mesh': ob, 'info': info, 'cfg': cfg, 'pts': pts}
    return build


RES = 1.5   # densidade extra do render (o jogo em tela cheia usa ~4 px por unidade; 3 px borrava)


def walk_modes(pose):
    """Modos de andar nas 5 direcoes (r q u e d), WALK_N quadros cada."""
    return [(m, WALK_N, (lambda parts, P, root, f, m=m: pose(parts, 'walk', f, 'w' + m))) for m in DIRS]


def item(key):
    cfg = CFG[key]
    pose = POSES[cfg['plan']]
    ms = walk_modes(pose)
    if cfg.get('atk'):
        # ataque de lado (olhando o oponente, que fica do lado na pista); queda na vista antiga
        ms.append(('a', ATK_N, lambda parts, P, root, f: pose(parts, 'atk', f, 'wr')))
    ms.append(('x', DIE_N, lambda parts, P, root, f: pose(parts, 'die', f, 'r')))
    return {'key': key, 'label': cfg['label'], 'build': builder(key), 'boost': cfg.get('boost', K.EN_BOOST) * RES, 'pxk': RES,
            'shadow': cfg.get('shadow', True), 'margin': (0.08, 0.08, 0.1, 0.06),
            'pose0': lambda parts, P, root: pose(parts, 'walk', 0, 'wr'), 'modes': ms}


def only_keys():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    keys = [k for k in args[2:] if k in CFG] if args and args[0] in ('render', 'prova', 'liberto') and len(args) > 2 else list(CFG)
    return [k for k in keys if present(k)]


def prova(out, keys):
    """Quadros de conferencia (r andando 0/3/6/9, u, d, ataque, morte) em out/<tipo>/."""
    for key in keys:
        it = next(i for i in SPEC['crews'] if i['key'] == key)
        parts = BUILT[key]
        frames = [('r', 0), ('r', 4), ('r', 8), ('r', 12), ('q', 4), ('u', 4), ('e', 4), ('d', 4), ('a', 3), ('x', 7)]
        fns = {m[0]: m[2] for m in it['modes']}
        seq = [(f'{key}_{m}{n}', (lambda m=m, n=n: fns[m](parts, None, None, n))) for m, n in frames if m in fns]
        render_frames(key, out, seq, boost=it['boost'], shadow=it.get('shadow', True))
    print('PROVA_OK', out, keys)


def cru(out, keys):
    """Vitrine crua (sem esqueleto, giro 0): um quadro por modelo para descobrir para onde ele olha."""
    clear_scene()
    ST['coll'] = bpy.context.scene.collection
    setup_scene()
    os.makedirs(out, exist_ok=True)
    for key in keys:
        root = make_root('raiz_' + key, key, coll_for(key))
        cfg = dict(CFG.get(key, {}), yaw=0.0)
        cfg.pop('length', None)
        cfg.pop('ph', None)
        cfg['height'] = 0.5
        import_glb(key, cfg, root)
    cam = bpy.context.scene.camera
    set_px(1.2)
    for key in keys:
        ob = bpy.data.objects[key + '_malha']
        for yaw in (0, 90, 180, 270):
            # vista r do jogo: giro do modelo + giro da vista
            ob.rotation_euler = (0, 0, math.radians(yaw) + VIEWS['r'])
            bpy.context.view_layer.update()
            reset_vis()
            set_visible({key})
            lo, hi = bounds_of(meshes_of({key}))
            frame_camera(cam, lo, hi, margin=(0.05, 0.05, 0.05, 0.05))
            bpy.context.scene.cycles.samples = 12
            render_to(os.path.join(out, f'{key}_{yaw}.png'))
    print('CRU_OK', out)


def liberto(out, keys):
    """Quadros do bicho libertado (l_NN correndo de volta para a mata; lq/lu/le/ld nas outras direcoes; la atacando). O enquadramento e o mesmo do conjunto inteiro
    (uniao de todos os modos), para a ancora e o tamanho da folha continuarem valendo. Rodar logo depois do render."""
    import json
    cam = bpy.context.scene.camera
    sc = bpy.context.scene
    sc.render.use_persistent_data = True
    sc.cycles.samples = 40
    mp = os.path.join(out, 'meta.json')
    meta = json.load(open(mp))
    for key in keys:
        it = next(i for i in SPEC['crews'] if i['key'] == key)
        parts = BUILT[key]
        allf = [(m, f, fn) for m, n, fn in it['modes'] for f in range(n)]
        reset_vis()
        set_visible({key})
        bpy.data.objects['ChaoSombra'].hide_render = not it.get('shadow', True)
        set_px(it['boost'])
        boxes = []
        for m, f, fn in allf:
            fn(parts, None, None, f)
            boxes.append(bounds_of(meshes_of({key})))
        lo, hi = union(boxes)
        wpx, hpx, tl = frame_camera(cam, lo, hi, margin=it.get('margin', (0.06, 0.06, 0.08, 0.05)))
        old = meta['sets'].get(key, {})
        if (old.get('w'), old.get('h')) != (wpx, hpx):
            print('AVISO enquadramento diferente', key, (old.get('w'), old.get('h')), (wpx, hpx))
        # liberto andando nas 5 direcoes (l = leste, lq lu le ld) e atacando (la): o Estouro da Mata e os bichos
        # chamados pela Caipora correm e lutam do nosso lado com as cores naturais
        fns = {m: fn for m, n, fn in it['modes']}
        d = os.path.join(out, key)
        modos = meta['sets'][key].setdefault('modes', {})
        for m in list(DIRS) + (['a'] if 'a' in fns else []):
            nome = 'l' if m == 'r' else 'l' + m
            n = ATK_N if m == 'a' else WALK_N
            for f in range(n):
                fns[m](parts, None, None, f)
                render_to(os.path.join(d, f'{nome}_{f:02d}.png'))
            modos[nome] = n
        set_px(1.0)
        bpy.data.objects['ChaoSombra'].hide_render = False
        print('OK liberto', key, flush=True)
        json.dump(meta, open(mp, 'w'), indent=1)
    print('LIBERTO_OK')


SPEC = {'crews': [item(k) for k in only_keys()]}


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if args and args[0] == 'cru':
        cru(args[1], args[2:])
    elif args and args[0] == 'liberto':
        LIBERTO = True
        build_family(SPEC)
        liberto(args[1], [i['key'] for i in SPEC['crews']])
    elif args and args[0] == 'prova':
        build_family(SPEC)
        bpy.context.scene.cycles.samples = 24
        prova(args[1], [i['key'] for i in SPEC['crews']])
    elif args and args[0] == 'render':
        build_family(SPEC)
        sc = bpy.context.scene
        sc.render.use_persistent_data = True
        sc.cycles.samples = 40
        render_family(FAM, SPEC, args[1], set(args[2:]) or None)
        print('RENDER_OK', args[1])
    else:
        main(FAM, SPEC)
