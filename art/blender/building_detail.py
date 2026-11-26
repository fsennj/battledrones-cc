"""Shared architectural trim for the Blender buildings, in game coordinates."""
import math
import os

from lib import GM_D, HAZ, HAZ_D, OUT, _finish, box, bpy, g2b

STEEL = 0x8E969C
RECESS = 0x22262A
CONCRETE = 0x646663


def beam(start, end, width, depth, color):
    """A square-section bar between two endpoints."""
    a, b = g2b(start), g2b(end)
    delta = b - a
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.scale = (width, depth, delta.length)
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    centre = tuple((p + q) / 2 for p, q in zip(start, end))
    return _finish(obj, color, centre, (0, 0, 0), 0)


def rim(inner, outer, y, color, *, centre=(0, 0), start=0, end=math.tau, steps=24):
    """A flat painted or machined band on a deck. Normals face up."""
    verts = []
    for step in range(steps + 1):
        angle = start + (end - start) * step / steps
        for r in (inner, outer):
            verts.append((centre[0] + r * math.cos(angle),
                          y, centre[1] + r * math.sin(angle)))
    return marking(verts, [(i + 2, i + 3, i + 1, i) for i in range(0, steps * 2, 2)], color)


def marking(verts, faces, color):
    mesh = bpy.data.meshes.new('marking')
    mesh.from_pydata([g2b(v) for v in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new('marking', mesh)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return _finish(obj, color, (0, 0, 0), (0, 0, 0), 0, grade=0)


def threshold(x, y, z, width, depth, count):
    """Angled hazard paint on a dark kerb, with the paint inset from the edges."""
    trim = [box((width, 0.024, depth), (x, y - 0.012, z), HAZ_D, bevel=0.005)]
    pitch = width / (count + 0.5)
    back, front = z - depth * 0.43, z + depth * 0.43
    for i in range(count):
        lhs = x - width / 2 + pitch * (i + 0.14)
        trim.append(marking([(lhs, y + 0.001, back), (lhs + pitch * 0.3, y + 0.001, front),
                             (lhs + pitch * 0.86, y + 0.001, front), (lhs + pitch * 0.56, y + 0.001, back)],
                            [(0, 1, 2, 3)], HAZ))
    return trim


def grille(x, y, z, width, depth, slats):
    parts = [box((width, 0.022, depth), (x, y, z), GM_D, bevel=0.008)]
    for i in range(slats):
        vz = z + depth * ((i + 0.5) / slats - 0.5) * 0.78
        parts.append(box((width * 0.85, 0.01, depth * 0.35 / slats), (x, y + 0.016, vz), STEEL, bevel=0))
    return parts


def export_building(name):
    # The renderer builds flat normals on load and uses only positions and palette colours.
    bpy.ops.export_scene.gltf(filepath=os.path.join(os.path.abspath(OUT), f'{name}.glb'),
                              export_format='GLB', export_vertex_color='ACTIVE',
                              export_materials='NONE', export_animations=False, export_apply=True,
                              export_texcoords=False, export_normals=False)
