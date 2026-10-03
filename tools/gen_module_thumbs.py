"""Renders build-card thumbnails of modules that have no Blender preview, assembled from the kit parts the way scripts/modgen.evox lays them out
(ui/th_<n>.png + .spr, n = defs.kindFromIndex). Currently the Docking Hub (8), shown with its shuttle docked.
Run with Blender:  blender --background --python tools/gen_module_thumbs.py      (from the project root)
Transparent background, three-quarter view from above, framed to the bounds, 256 x 168."""
import bpy, math, mathutils
from pathlib import Path
ROOT = Path('C:/projects/space_game')
W, H = 256, 168
PI = math.pi

# (part, Blender x, y, z, rx about the hull axis, rz about the vertical) - modgen.put()
HUB = [('hull_plain_white', -.5, 0, 0, 0, 0), ('hull_plain_white', -.5, 0, 0, PI, 0), ('hull_grille_red', .5, 0, 0, 0, 0), ('hull_plain_blue', .5, 0, 0, PI, 0),
       ('hull_enddock', -1, 0, 0, 0, 0), ('hull_enddock', -1, 0, 0, PI, 0), ('hull_enddock', 1, 0, 0, 0, PI), ('hull_enddock', 1, 0, 0, PI, PI),
       ('part_light', .3, 0, 1.02, 0, PI), ('ship_shuttle', 1.6, 0, 0, 0, 0)]

def render(n, layout):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for name, x, y, z, rx, rz in layout:
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.fbx(filepath=str(ROOT / 'models/parts' / (name + '.fbx')))
        m = mathutils.Matrix.Translation((x, y, z)) @ mathutils.Matrix.Rotation(rz, 4, 'Z') @ mathutils.Matrix.Rotation(rx, 4, 'X')
        for o in set(bpy.context.scene.objects) - before:
            if o.parent is None: o.matrix_world = m @ o.matrix_world
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = mathutils.Vector([min(p[i] for p in pts) for i in range(3)])
    hi = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
    centre = (lo + hi) * 0.5
    size = (hi - lo).length
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in scene.render.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('w'); scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[1].default_value = 0.9
    cam_data = bpy.data.cameras.new('cam'); cam_data.type = 'ORTHO'
    cam = bpy.data.objects.new('cam', cam_data); scene.collection.objects.link(cam); scene.camera = cam
    d = mathutils.Vector((0.5, -1.3, 0.8)).normalized()
    cam.location = centre + d * size * 3.0
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    right = cam.rotation_euler.to_matrix() @ mathutils.Vector((1, 0, 0))
    up = cam.rotation_euler.to_matrix() @ mathutils.Vector((0, 1, 0))
    corners = [mathutils.Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    ext_x = max(abs((c - centre).dot(right)) for c in corners) * 2
    ext_y = max(abs((c - centre).dot(up)) for c in corners) * 2
    cam_data.ortho_scale = max(ext_x, ext_y * W / H) * 1.05
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    out = ROOT / 'ui' / ('th_%d.png' % n)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    (ROOT / 'ui' / ('th_%d.spr' % n)).write_text('type = simple\ntop = 0\nbottom = 0\nleft = 0\nright = 0\ntexture = "ui/th_%d.png"\n' % n)
    (ROOT / 'ui' / ('th_%d.png.meta' % n)).write_text('srgb = true\ncompress = false\nmips = false\n')
    print('THUMB', n)

render(8, HUB)
