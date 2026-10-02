"""Generate matching smooth, unit-radius Earth/atmosphere spheres (Blender background)."""
import math
from pathlib import Path
import bpy

root = Path(__file__).resolve().parent.parent / 'models/earth_atmosphere'
root.mkdir(exist_ok=True)
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
segments, rings = 192, 96
verts = [(0, 0, 1)]
for j in range(1, rings):
    phi = math.pi * j / rings
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        verts.append((math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi)))
south = len(verts)
verts.append((0, 0, -1))
faces = []
for i in range(segments):
    ni = (i + 1) % segments
    faces.append((0, 1 + i, 1 + ni))
    for j in range(rings - 2):
        a = 1 + j * segments
        b = a + segments
        faces.append((a + i, b + i, b + ni, a + ni))
    a = 1 + (rings - 2) * segments
    faces.append((a + i, south, a + ni))
for asset, label, textured in [('earth_atmosphere', 'Earth atmosphere', False), ('earth', 'Earth', True)]:
    folder = root.parent / asset
    folder.mkdir(exist_ok=True)
    mesh = bpy.data.meshes.new(label)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    if textured:
        uv = mesh.uv_layers.new(name='UV0')
        for polygon in mesh.polygons:
            indices = list(polygon.loop_indices)
            values = []
            for li in indices:
                v = mesh.vertices[mesh.loops[li].vertex_index].co
                u = (math.atan2(v.y, v.x) / (2 * math.pi) + 0.5) % 1.0
                latitude = 1.0 - math.acos(max(-1.0, min(1.0, v.z))) / math.pi
                values.append([u, latitude, abs(v.z) > 0.999999])
            # Unwrap each face across the longitude seam; give pole loops
            # the mean longitude of their ring neighbours to avoid pinching.
            us = [u for u, _, pole in values if not pole]
            crosses_seam = max(us) - min(us) > 0.5
            if crosses_seam:
                for value in values:
                    if not value[2] and value[0] < 0.5:
                        value[0] += 1.0
            mean_u = sum(value[0] for value in values if not value[2]) / len(us)
            for li, (u, v, pole) in zip(indices, values):
                uv.data[li].uv = (mean_u if pole else u, v)
    obj = bpy.data.objects.new(label, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(bpy.data.materials.new(asset))
    for other in bpy.context.selected_objects:
        other.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=str(folder / f'{asset}.fbx'), use_selection=True,
        apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
        path_mode='RELATIVE', mesh_smooth_type='FACE', use_tspace=textured, bake_anim=False)
    print(asset, 'exported:', len(verts), 'vertices, unit radius, outward smooth normals')
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'earth_atmosphere.blend'))
