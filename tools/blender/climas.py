"""Previa: a Torre de Arqueiros N3 (com arqueiros) sob a luz de cada clima.
uso: Blender -b -P tools/blender/climas.py -- <pasta_saida>
Serve de alvo visual para a iluminacao dinamica no jogo (ver PLANO-LUZ.md)."""
import bpy, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__name__': 'arq'}
exec(open(os.path.join(HERE, 'arqueiros.py')).read(), ns)
out = sys.argv[sys.argv.index('--') + 1]
os.makedirs(out, exist_ok=True)
ns['build'](showcase=True)
P = ns['palette']()
lin = ns['lin']
for v in ns['ARCHER_VARIANTS']:
    ns['archer_frame'](ns['BUILT'][v], P, ns['SETS'][v], 'aim', 0)
sc = bpy.context.scene
cam = sc.camera
# so a N3 com seus arqueiros, sem a fileira de arqueiros soltos atras
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'ChaoSombra':
        o.hide_render = o.get('set') not in ('n3', 'a3', 'a3b')
for v in ns['ARCHER_VARIANTS']:
    for o in bpy.data.objects:
        if o.get('set') == v and o.parent is None and o.type != 'EMPTY':
            pass
# arqueiros soltos (fonte das instancias) ficam fora do quadro: move para longe
for v in ('a3', 'a3b'):
    ns['SETS'][v].location = (40, 40, 0)
n3 = ns['SETS']['n3']
for i, s in enumerate(ns['BUILT']['n3']['slots']):
    inst = bpy.data.objects.get(f'inst_n3_{i}')
    v = ('a3', 'a3b')[i]
    inst.location = Vector(s) - ns['SETS'][v].location
objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('set') == 'n3']
lo, hi = ns['bounds_of'](objs)
ns['PX_PER_BU'] = 190
ns['frame_camera'](cam, lo, hi, margin=(0.35, 0.6, 0.3, 0.2))
sc.render.resolution_percentage = 100
sc.render.film_transparent = False
sc.cycles.samples = 96

bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
sun = bpy.data.objects['Sol']
fill = bpy.data.objects['Preenchimento']
gm = bpy.data.materials['lanterna']
gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
ground = bpy.data.objects['ChaoSombra']
ground.is_shadow_catcher = False
gmat = ns['mat']('chao_previa', '#d9b882', rough=0.95, var=0.0, bump=0.2)
ground.data.materials.clear()
ground.data.materials.append(gmat)
gbsdf = next(n for n in gmat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

lamps = []
for i, pos in enumerate(ns['BUILT']['n3']['lanterns']):
    ld = bpy.data.lights.new(f'lampPrev{i}', 'POINT')
    ld.shadow_soft_size = 0.05
    ld.color = lin('#ffb25a')[:3]
    lo_ = bpy.data.objects.new(f'lampPrev{i}', ld)
    sc.collection.objects.link(lo_)
    lo_.location = n3.location + Vector(pos)
    lamps.append(ld)
# luz extra de "tocha" no alto da torre (os arqueiros acendem um braseiro a noite)
bd = bpy.data.lights.new('braseiro', 'POINT')
bd.shadow_soft_size = 0.1
bd.color = lin('#ff9a48')[:3]
bo = bpy.data.objects.new('braseiro', bd)
sc.collection.objects.link(bo)
bo.location = n3.location + Vector((0.0, 0.25, 2.45))
lamps_all = lamps + [bd]


def aim_sun(vec):
    sun.rotation_euler = Vector(vec).normalized().to_track_quat('Z', 'Y').to_euler()


PRESETS = {
    'dia': dict(sky='#f3dfc2', sky_s=0.7, sun='#fff0d8', sun_e=3.8, sun_dir=(-1.0, -0.45, 1.35), sun_ang=18, fill_e=0.6, lamp=0, emit=4, ground='#d9b882', rough=0.95, exposure=0.0),
    'entardecer': dict(sky='#e9a27a', sky_s=0.55, sun='#ff9a52', sun_e=3.2, sun_dir=(-1.0, -0.2, 0.45), sun_ang=12, fill_e=0.35, lamp=8, emit=10, ground='#d4a070', rough=0.95, exposure=-0.1),
    'noite': dict(sky='#1d2648', sky_s=0.35, sun='#9fb6ff', sun_e=0.55, sun_dir=(0.6, 0.5, 1.2), sun_ang=6, fill_e=0.0, lamp=30, emit=22, ground='#8a7a6a', rough=0.95, exposure=0.15),
    'tempestade': dict(sky='#a07a52', sky_s=1.0, sun='#ffd9a0', sun_e=0.8, sun_dir=(-1.0, -0.45, 1.35), sun_ang=70, fill_e=0.0, lamp=18, emit=16, ground='#b8905e', rough=0.95, exposure=-0.15),
    'chuva': dict(sky='#7f8da3', sky_s=0.9, sun='#d8e2f0', sun_e=0.7, sun_dir=(-0.6, -0.4, 1.4), sun_ang=50, fill_e=0.0, lamp=14, emit=14, ground='#8f7f6a', rough=0.25, exposure=-0.05),
}
names = sys.argv[sys.argv.index('--') + 2:] or list(PRESETS)
for name in names:
    p = PRESETS[name]
    bg.inputs['Color'].default_value = lin(p['sky'])
    bg.inputs['Strength'].default_value = p['sky_s']
    sun.data.color = lin(p['sun'])[:3]
    sun.data.energy = p['sun_e']
    sun.data.angle = math.radians(p['sun_ang'])
    aim_sun(p['sun_dir'])
    fill.data.energy = p['fill_e']
    for ld in lamps:
        ld.energy = p['lamp']
    bd.energy = p['lamp'] * 0.8
    gb.inputs['Emission Strength'].default_value = p['emit']
    gbsdf.inputs['Base Color'].default_value = lin(p['ground'])
    gbsdf.inputs['Roughness'].default_value = p['rough']
    # chuva: tudo molhado (menos rugoso, mais escuro)
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b is None:
            continue
        if 'r0' not in m:
            m['r0'] = b.inputs['Roughness'].default_value
        b.inputs['Roughness'].default_value = m['r0'] * (0.45 if name == 'chuva' else 1.0)
    sc.view_settings.exposure = p['exposure']
    sc.render.filepath = os.path.join(out, f'clima_{name}.png')
    bpy.ops.render.render(write_still=True)
print('CLIMAS_OK')
