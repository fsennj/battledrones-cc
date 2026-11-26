"""The Hornet armoured airship (models.ts `hornet`). Run Blender with -- /absolute/out [samples].

Nodes: `hull` (everything) and `rotor` (one pusher prop, built at its own origin around the game z
axis so the game can place two of them at the models.ts rotor pivots [±0.35, -0.02, 0.262] and
counter-spin them). No turret node: the TS hornet has none. Shapes mirror models.ts shape for shape:
banded ellipsoid envelope, team spine stripe, cruciform tail fins, bomb gondola, podded outrigger
engines.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib as a

import bmesh
import bpy

GLASS = 0xAC712E
BLADE = 0x1A1C1F  # rotorGeo blade colour in models.ts

# the envelope (models.ts hornet constants, game space: -Z forward, y up)
L, RX, RY, Y = 0.62, 0.25, 0.21, 0.05


def rad(z):
    return math.sqrt(max(0.0, 1 - (z / L) ** 2))


def mesh(vertices, faces, colour):
    """Build a flat-shaded shell in the game's coordinates (aircraft.py pattern)."""
    data = bpy.data.meshes.new("shell")
    data.from_pydata([a.g2b(v) for v in vertices], [], faces)
    normals = bmesh.new()
    normals.from_mesh(data)
    bmesh.ops.recalc_face_normals(normals, faces=list(normals.faces))
    normals.to_mesh(data)
    normals.free()
    data.update()
    obj = bpy.data.objects.new("shell", data)
    a.sc.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return a._finish(obj, colour, (0, 0, 0), (0, 0, 0), 0)


def hull_shell(sections, colour, x_offset=0):
    """One closed faceted skin from lengthwise sections (z, half-width, floor, crown)."""
    vertices = []
    for z, width, floor, crown in sections:
        height = crown - floor
        profile = [(-0.72, 1), (0.72, 1), (1, 0.72), (0.92, 0.26), (0.62, 0),
                   (-0.62, 0), (-0.92, 0.26), (-1, 0.72)]
        vertices.extend((x_offset + width * x, floor + height * y, z) for x, y in profile)
    faces = [tuple(range(8))]
    for start in range(0, len(vertices) - 8, 8):
        for i in range(8):
            j = (i + 1) % 8
            faces.append((start + i, start + j, start + j + 8, start + i + 8))
    faces.append(tuple(range(len(vertices) - 8, len(vertices))))
    return mesh(vertices, faces, colour)


def plate(outline, y, thickness, colour):
    """Horizontal slab from an (x, z) outline, `thickness` tall in y (aircraft.py pattern)."""
    count = len(outline)
    vertices = [(x, level, z) for level in (y, y + thickness) for x, z in outline]
    faces = [tuple(range(count)), tuple(range(count, 2 * count))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    return mesh(vertices, faces, colour)


def fin_plate(outline, x, thickness, up, colour):
    """Vertical tail fin: (height, z) outline, y = Y + up * height, `thickness` wide in x.

    models.ts b.prism(fin, 0.014, [±0.007, Y, 0], rot [0, 0, ±pi/2])."""
    count = len(outline)
    vertices = [(level, Y + up * h, z) for level in (x, x + thickness) for h, z in outline]
    faces = [tuple(range(count)), tuple(range(count, 2 * count))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    return mesh(vertices, faces, colour)


H = []

# the envelope: b.sphere(1, [0,Y,0], GM, scale [RX, L, RY], rot [pi/2,0,0]) — after that
# rotation it is an axis-aligned ellipsoid x=RX, y=RY, z=L
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=1)
o = bpy.context.object
o.scale = (RX, L, RY)  # blender (x, y=game z, z=game y)
bpy.ops.object.transform_apply(scale=True)
H.append(a._finish(o, a.GM, (0, Y, 0), (0, 0, 0), 0))

# armour bands: elliptical rings riding the envelope (team fore and aft, dark ribs between)
for z, hexc, w in ((-0.36, a.T_MAIN, 1.8), (-0.12, a.GM_D, 0.8), (0.12, a.GM_D, 0.8), (0.36, a.T_MAIN, 1.8)):
    bpy.ops.mesh.primitive_torus_add(major_radius=RX * rad(z) + 0.004, minor_radius=0.012,
                                     major_segments=18, minor_segments=5)
    o = bpy.context.object
    o.rotation_euler = a._AXIS_Z.to_euler()  # ring around the game z axis
    bpy.ops.object.transform_apply(rotation=True)
    o.scale = (1.0, w, RY / RX)  # blender y = game z (band width), blender z = game y (flatten)
    bpy.ops.object.transform_apply(scale=True)
    H.append(a._finish(o, hexc, (0, Y, z), (0, 0, 0), 0))

# the team stripe along the spine: b.fuselage over sections riding the envelope crown
H.append(hull_shell([(z, 0.03, Y + RY * rad(z) + 0.004 - 0.03, Y + RY * rad(z) + 0.004)
                     for z in (-0.5, -0.36, -0.15, 0.05, 0.25, 0.42, 0.54)], a.T_MAIN))

# nose sensor ball and the fore light
H.append(a.sphere(0.05, (0, Y, -L + 0.02), a.GM_D, w=8, h=5))
H.append(a.light((0, Y, -L - 0.03), 0.024))

# cruciform tail fins (up, down, out both sides) and a nav light on each side tip
fin = ((0.1, 0.4), (0.3, 0.56), (0.3, 0.68), (0.02, 0.64))
H.append(fin_plate(fin, -0.007, 0.014, +1, a.T_MAIN))
H.append(fin_plate(fin, -0.007, 0.014, -1, a.T_MAIN))
for s in (1, -1):
    H.append(plate([(s * h, z) for h, z in fin], Y - 0.007, 0.014, a.T_MAIN))
    H.append(a.light((s * 0.3, Y, 0.62), 0.02))

# the bomb gondola with amber windows and three bombs racked underneath
H.append(a.box((0.13, 0.07, 0.34), (0, Y - RY - 0.02, 0), a.GM_D, bevel=0.015))
H.extend(a.pair_box((0.004, 0.018, 0.24), (0.066, Y - RY - 0.01, 0), a.AMBER, bevel=0, grade=0))
for z in (-0.1, 0.0, 0.1):
    H.append(a.tube(0.022, 0.1, 8, (0, Y - RY - 0.075, z), a.GM_D))
    H.append(a.sphere(0.022, (0, Y - RY - 0.075, z - 0.05), a.T_MAIN, w=6, h=4))

# two engine pods on outriggers with team cowlings, spinners and prop pivots behind them
for s in (1, -1):
    x = s * 0.35
    y = Y - 0.07
    H.append(a.box((0.14, 0.016, 0.05), (s * 0.27, y, 0.14), a.GM_D, bevel=0))
    H.append(a.tube(0.042, 0.17, 8, (x, y, 0.14), a.GM))
    H.append(a.tube(0.045, 0.03, 8, (x, y, 0.08), a.T_MAIN))
    H.append(a.cone(0.03, 0.04, 6, (x, y, 0.24), a.GM_D, rot=(math.pi / 2, 0, 0)))

hull = a.join(H, "hull", ao=(0.07, 0.15))

# the pusher prop: rotorGeo(0.075, "z") — crossed blades in the game x/y plane about the z axis
R = [a.box((0.15, 0.0135, 0.008), (0, 0, 0), BLADE, bevel=0, grade=0),
     a.box((0.0135, 0.15, 0.008), (0, 0, 0), BLADE, bevel=0, grade=0),
     a.tube(0.0165, 0.03, 6, (0, 0, 0), a.GM_L, grade=0)]
rotor = a.join(R, "rotor")

# bounds report (game space)
for nm, ob in (("hull", hull), ("rotor", rotor)):
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.z for v in ob.data.vertices]
    zs = [-v.co.y for v in ob.data.vertices]
    print(f"BOUNDS {nm}: x {min(xs):.3f}..{max(xs):.3f} y {min(ys):.3f}..{max(ys):.3f} z {min(zs):.3f}..{max(zs):.3f}")

# ------------------------------------------------------------------ export ---
a.export_model("hornet")

# ----------------------------------------------------------------- preview ---
# same as lib.export_and_preview, but the rotor is moved onto its game pivot first so the
# preview shows it where the game will draw it (both props share this one geometry)
mat = bpy.data.materials.new("vc")
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.55
bsdf.inputs["Metallic"].default_value = 0.25
node = nt.nodes.new("ShaderNodeVertexColor")
node.layer_name = "Col"
nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
for o in (hull, rotor):
    o.data.materials.append(mat)

sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.5
so = bpy.data.objects.new("sun", sun)
a.sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(-35))
cam = bpy.data.cameras.new("cam")
cam.type = "ORTHO"
cam.ortho_scale = 2.0
co = bpy.data.objects.new("cam", cam)
a.sc.collection.objects.link(co)
a.sc.camera = co
co.location = (0, -4.0, 3.4)
co.rotation_euler = (math.radians(50), 0, 0)
a.sc.render.engine = "CYCLES"
a.sc.cycles.device = "CPU"
a.sc.cycles.samples = a.SAMPLES
a.sc.cycles.use_denoising = True
a.sc.render.resolution_x = a.sc.render.resolution_y = 640
a.sc.render.film_transparent = True
a.sc.render.image_settings.file_format = "PNG"
a.sc.render.image_settings.color_mode = "RGBA"
a.sc.world = bpy.data.worlds.new("w")
a.sc.world.color = (0.5, 0.55, 0.6)
pivot = bpy.data.objects.new("pivot", None)
a.sc.collection.objects.link(pivot)
hull.parent = pivot
rotor.parent = pivot
rotor.location = a.g2b((0.35, Y - 0.07, 0.262))  # preview only: after the export above
for i, (ang, camz) in enumerate(((20, 3.4), (90, 3.4), (155, 3.4), (130, -2.6))):
    pivot.rotation_euler[2] = math.radians(ang)
    co.location = (0, -4.0, camz)
    # 123° aims from (0, -4, -2.6) up at the origin (sin123=0.84, -cos123=0.55)
    co.rotation_euler = (math.radians(50 if camz > 0 else 123), 0, 0)
    a.sc.render.filepath = f"{a.OUT}/preview_{i}.png"
    bpy.ops.render.render(write_still=True)
print("DONE")
