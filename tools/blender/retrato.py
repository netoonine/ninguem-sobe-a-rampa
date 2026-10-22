"""Retrato de heroi da satira (canto da tela, tela de herois e mapa) a partir do mesmo modelo 3D da unidade.

uso: Blender -b -P tools/blender/retrato.py -- sprites/ui/jaci_retrato.png [modelo] [giro_graus] [alvo_z] [distancia]
     (modelo em arte/modelos/rampa; padrao lulala, giro -40, alvo 0.76, distancia 1.4; herois v3: -65 0.80 1.9)
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *   # noqa: F401,F403
import inimigos_glb as G

import rampa_glb as R   # cor do GLB sem a brasa da mata
G.MODELOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'arte', 'modelos', 'rampa')


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    out = args[0]
    key = args[1] if len(args) > 1 else 'lulala'
    giro = float(args[2]) if len(args) > 2 else -40.0
    alvo_z = float(args[3]) if len(args) > 3 else 0.76
    dist = float(args[4]) if len(args) > 4 else 1.4
    clear_scene()
    ST['coll'] = bpy.context.scene.collection
    setup_scene()
    sc = bpy.context.scene
    root = make_root('raiz_' + key, key, coll_for(key))
    cobra = False
    ob = G.import_glb(key, {'height': 1.0, 'yaw': 0.0}, root)
    # rosto a 3/4 para a camera
    ob.rotation_euler = (0, 0, math.radians(giro))
    if cobra:
        # cobra: a cabeca e o ponto mais alto do pescoco erguido
        bpy.context.view_layer.update()
        import numpy as np
        P = np.array([ob.matrix_world @ v.co for v in ob.data.vertices])
        top = P[P[:, 2] > P[:, 2].max() - 0.12]
        hx, hy, hz = top.mean(0)
        ob.location.x -= hx
        ob.location.y -= hy
        alvo_z = hz - 0.04
    bpy.data.objects['ChaoSombra'].hide_render = True
    # camera de busto: perspectiva curta, levemente de cima
    cam_d = bpy.data.cameras.new('CamRetrato')
    cam_d.type = 'PERSP'
    cam_d.lens = 85
    cam = bpy.data.objects.new('CamRetrato', cam_d)
    sc.collection.objects.link(cam)
    alvo = Vector((0.0, 0.0, alvo_z))
    pos = alvo + Vector((0.12, -dist, 0.22))
    cam.location = pos
    cam.rotation_euler = (alvo - pos).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    # luz de recorte quente por tras para descolar do fundo do medalhao
    rim_d = bpy.data.lights.new('Recorte', 'AREA')
    rim_d.energy = 60
    rim_d.size = 1.5
    rim_d.color = lin('#ffd9a0')[:3]
    rim = bpy.data.objects.new('Recorte', rim_d)
    sc.collection.objects.link(rim)
    rim.location = (0.8, 1.6, 1.6)
    rim.rotation_euler = (Vector((0, 0, 0.85)) - rim.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 512
    sc.render.film_transparent = True
    sc.cycles.samples = 96
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    render_to(os.path.abspath(out))
    print('RETRATO_OK', out)


main()
