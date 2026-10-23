"""Esqueleto humano de verdade para os bonecos das pessoas reais (Ninguem Sobe a Rampa).

O esqueleto antigo (inimigos_glb.rig_biped) punha os ossos por proporcao e pesava cada vertice so pela distancia: com a
mao encostada no rosto (joinha, celular na orelha, o "L") o braco puxava a bochecha, e a mao erguida ficava fora do
braco. Aqui:

1. uma copia fechada do boneco (remesh em voxels) da um corpo continuo, sem pecas soltas;
2. a distancia andando pela superficie a partir do quadril acha as pontas do corpo (topo da cabeca, maos, pes) e o
   caminho de cada braco: ombro, cotovelo e mao saem desse caminho, no meio da secao do braco, onde quer que a mao esteja;
3. os pesos saem do "calor" do Blender (ARMATURE_AUTO) na copia fechada e passam para o modelo por transferencia de
   dados (vertice mais proximo na face), com no maximo 4 ossos por vertice.

Os nomes dos ossos sao os mesmos do rig_biped (raiz, quadril, peito, cabeca, braco/antebraco/coxa/canela L e R), entao
as poses que ja existem (andar, ataque, queda, espera, sentado, danca) funcionam sem mudar.
"""
import heapq, math
import numpy as np
import bpy
from mathutils import Vector
import inimigos_glb as G


def _proxy(ob, H):
    """Copia do boneco refeita em voxels: superficie fechada e conectada (o calor do Blender precisa disso)."""
    me = ob.data.copy()
    px = bpy.data.objects.new(ob.name + '_proxy', me)
    for c in ob.users_collection:
        c.objects.link(px)
    px.matrix_world = ob.matrix_world.copy()
    for m in list(px.modifiers):
        px.modifiers.remove(m)
    rm = px.modifiers.new('voxel', 'REMESH')
    rm.mode = 'VOXEL'
    rm.voxel_size = H / 95.0
    rm.adaptivity = 0.0
    bpy.ops.object.select_all(action='DESELECT')
    px.select_set(True)
    bpy.context.view_layer.objects.active = px
    bpy.ops.object.modifier_apply(modifier=rm.name)
    return px


def _grafo(px):
    me = px.data
    Q = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get('co', Q)
    Q = Q.reshape(-1, 3)
    E = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get('vertices', E)
    E = E.reshape(-1, 2)
    w = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1)
    adj = [[] for _ in range(len(Q))]
    for (a, b), ww in zip(E.tolist(), w.tolist()):
        adj[a].append((b, ww))
        adj[b].append((a, ww))
    return Q, adj


def _dijkstra(adj, src):
    n = len(adj)
    dist = np.full(n, np.inf)
    prev = np.full(n, -1, dtype=np.int64)
    dist[src] = 0.0
    h = [(0.0, src)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(h, (nd, v))
    return dist, prev


def _caminho(prev, v):
    out = []
    while v >= 0:
        out.append(v)
        v = prev[v]
    return out[::-1]


def _centro(Q, p, r):
    """Ponto da superficie puxado para o meio da secao do membro (media dos vizinhos num raio)."""
    m = np.linalg.norm(Q - p, axis=1) < r
    return Q[m].mean(0) if m.sum() > 3 else p


def _pontas(Q, adj, dist, H):
    """Maximos locais da distancia pela superficie: as pontas do corpo (cabeca, maos, pes, adereco na mao)."""
    fin = np.isfinite(dist)
    is_max = np.ones(len(Q), dtype=bool)
    for u in range(len(Q)):
        if not fin[u]:
            is_max[u] = False
            continue
        for v, _ in adj[u]:
            if dist[v] > dist[u]:
                is_max[u] = False
                break
    cand = np.nonzero(is_max & fin & (dist > 0.25 * H))[0]
    cand = cand[np.argsort(-dist[cand])]
    sel = []
    for v in cand:
        if all(np.linalg.norm(Q[v] - Q[s]) > 0.12 * H for s in sel):
            sel.append(int(v))
    return sel


def rig_humano(key, ob, root, cfg):
    P = G.verts_np(ob)
    H, x0, x1, y0, y1, Lx, Wy = G.body_frame(P)
    hip, sh, nk = cfg.get('hip', 0.36) * H, cfg.get('shoulder', 0.6) * H, cfg.get('neck', 0.64) * H
    band = P[(P[:, 2] > hip) & (P[:, 2] < sh)]
    cx, cy = float(np.median(band[:, 0])), float(np.median(band[:, 1]))
    low = P[P[:, 2] < 0.07 * H]
    C = G.kmeans(low[:, :2], [(cx, cy + 0.15 * Wy), (cx, cy - 0.15 * Wy)])
    C = sorted([Vector((c[0], c[1], 0)) for c in C], key=lambda c: -c.y)
    feet = {'L': C[0], 'R': C[1]}
    torso = P[(P[:, 2] > sh - 0.06 * H) & (P[:, 2] < sh + 0.02 * H)]
    shw = float(np.percentile(np.abs(torso[:, 1] - cy), 80)) if len(torso) else 0.2 * Wy

    px = _proxy(ob, H)
    Q, adj = _grafo(px)
    raiz_v = int(np.argmin(np.linalg.norm(Q - np.array([cx, cy, hip]), axis=1)))
    dist, prev = _dijkstra(adj, raiz_v)
    pontas = _pontas(Q, adj, dist, H)

    # cabeca: a ponta mais alta perto do eixo do corpo; pes: pontas no chao; o resto acima do quadril sao bracos
    eixo = lambda v: abs(Q[v][1] - cy)
    cab = [v for v in pontas if Q[v][2] > nk and eixo(v) < 0.18 * H]
    cab_v = max(cab, key=lambda v: Q[v][2]) if cab else None
    # mao (ou adereco na mao) e a ponta cujo caminho desde o quadril passa pelo ombro daquele lado: orelha, cabelo e
    # chapeu sobem pelo pescoco; mao grudada na perna nem vira ponta (fica sem mao detectada e o braco desce pelo lado)
    bracos = {'L': [], 'R': []}
    for v in pontas:
        if v == cab_v or Q[v][2] < 0.22 * H:
            continue
        lado = 'L' if Q[v][1] > cy else 'R'
        s_ = 1 if lado == 'L' else -1
        ombro_p = np.array([cx, cy + s_ * shw * 0.85, sh])
        cam = _caminho(prev, v)
        perto_cab = cab_v is not None and np.linalg.norm(Q[v] - np.array([cx, cy, (nk + Q[cab_v][2]) / 2])) < 0.75 * (Q[cab_v][2] - nk)
        if not perto_cab and np.min(np.linalg.norm(Q[cam] - ombro_p, axis=1)) < 0.12 * H and dist[v] - dist[raiz_v] > 0.3 * H:
            bracos[lado].append(v)
    maos = {}
    for lado, vs in bracos.items():
        if vs:
            # a ponta mais longe pela superficie (mao ou adereco segurado nela)
            maos[lado] = max(vs, key=lambda v: dist[v])

    arm = G.new_armature(key, root)
    G.bone(arm, 'raiz', (cx, cy, hip * 0.5), (cx, cy, hip * 0.5 + 0.03), deform=False)
    G.bone(arm, 'quadril', (cx, cy, hip), (cx, cy, (hip + sh) / 2), 'raiz')
    G.bone(arm, 'peito', (cx, cy, (hip + sh) / 2), (cx, cy, nk), 'quadril', True)
    topo = Q[cab_v] if cab_v is not None else np.array([cx, cy, H])
    G.bone(arm, 'cabeca', (cx, cy, nk), (cx, cy, float(topo[2])), 'peito', True)
    for nm, f in feet.items():
        knee = Vector((f.x + 0.02 * H, f.y, hip * 0.5))
        G.bone(arm, 'coxa' + nm, (f.x, f.y, hip), knee, 'quadril')
        G.bone(arm, 'canela' + nm, knee, (f.x, f.y, 0.02 * H), 'coxa' + nm, True)
    info_maos = {}
    for nm, s in (('L', 1), ('R', -1)):
        ombro = np.array([cx, cy + s * shw * 0.85, sh])
        if nm in maos:
            cam = _caminho(prev, maos[nm])
            # trecho do braco: do ponto do caminho mais perto do ombro ate a ponta
            i0 = int(np.argmin(np.linalg.norm(Q[cam] - ombro, axis=1)))
            trecho = cam[i0:]
            if len(trecho) < 3:
                trecho = cam[-3:]
            dd = dist[trecho] - dist[trecho[0]]
            Lb = dd[-1] if dd[-1] > 0 else 1.0
            el_v = trecho[int(np.argmin(np.abs(dd - 0.5 * Lb)))]
            r = 0.05 * H
            cot = _centro(Q, Q[el_v], r)
            mao = _centro(Q, Q[trecho[int(np.argmin(np.abs(dd - 0.92 * Lb)))]], r)
        else:
            cot = ombro + np.array([-0.03 * H, s * 0.04 * H, -0.14 * H])
            mao = ombro + np.array([0.0, s * 0.06 * H, -0.28 * H])
        G.bone(arm, 'braco' + nm, ombro, cot, 'peito')
        G.bone(arm, 'antebraco' + nm, cot, mao, 'braco' + nm, True)
        info_maos[nm] = mao
    bpy.ops.object.mode_set(mode='OBJECT')

    # mao grudada no corpo (o gerador funde a mao com o que ela encosta): coxa, cabeca ou peito. O braco desse lado fica
    # preso e as poses evitam movimento relativo no ponto de contato (rampa_glb: G.turn com as travas do esqueleto)
    topo_z = float(topo[2])
    cab_c = np.array([cx, cy, (nk + topo_z) / 2])
    cab_r = max(0.05 * H, (topo_z - nk) / 2)

    def seg_dist(p, a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        ab = b - a
        t = np.clip(((p - a) @ ab) / max(1e-9, ab @ ab), 0, 1)
        return float(np.linalg.norm(a + t * ab - p))
    presos = {}
    for nm in ('L', 'R'):
        m = np.asarray(info_maos[nm], float)
        f = feet[nm]
        d_coxa = min(seg_dist(m, (f.x, f.y, hip), (f.x + 0.02 * H, f.y, hip * 0.5)),
                     seg_dist(m, (f.x + 0.02 * H, f.y, hip * 0.5), (f.x, f.y, 0.02 * H)))
        d_cab = float(np.linalg.norm(m - cab_c))
        no_tronco = (hip < m[2] < sh) and abs(m[1] - cy) < shw * 1.05 and abs(m[0] - cx) < 0.16 * H
        if nm not in maos or d_coxa < 0.11 * H:
            presos[nm] = 'coxa' if (nm not in maos and m[2] < hip * 1.25) or d_coxa < 0.11 * H else 'peito'
        elif d_cab < cab_r * 1.35:
            presos[nm] = 'cabeca'
        elif no_tronco:
            presos[nm] = 'peito'
        else:
            presos[nm] = None
    # o gerador funde a mao com o que ela encosta e a deteccao da mao nao e confiavel nesses bonecos de cabeca grande:
    # por padrao os bracos ficam presos ao tronco (boneco de vinil) e o movimento vem do corpo; 'bracos_livres' solta
    livres = cfg.get('bracos_livres', False)
    for nm in ('L', 'R'):
        arm['preso_' + nm] = '' if livres else (presos[nm] or 'tronco')
    arm['preso_coxa'] = True
    arm['preso_cabeca'] = True

    # pesos: calor do Blender na copia fechada, depois transferidos para o boneco
    bpy.ops.object.select_all(action='DESELECT')
    px.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    for nm in [g.name for g in px.vertex_groups]:
        ob.vertex_groups.new(name=nm)
    dt = ob.modifiers.new('PesosDoProxy', 'DATA_TRANSFER')
    dt.object = px
    dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'
    dt.layers_vgroup_select_src = 'ALL'
    dt.layers_vgroup_select_dst = 'NAME'
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=dt.name)
    # no maximo 4 ossos por vertice e soma 1
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    bpy.data.objects.remove(px, do_unlink=True)
    ob.parent = arm
    md = ob.modifiers.new('Esqueleto', 'ARMATURE')
    md.object = arm
    for pb_ in arm.pose.bones:
        pb_.rotation_mode = 'QUATERNION'
    print('esqueleto humano:', key, 'pontas', len(pontas), 'maos', sorted(maos), 'cabeca', cab_v is not None, 'presos', presos)
    return arm, {'H': H, 'L': Lx, 'maos': info_maos, 'presos': presos}
