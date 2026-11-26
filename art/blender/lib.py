"""Shared helpers for the Blender unit models (art/blender/<kind>.py). Run headless:

    blender -b --factory-startup -P art/blender/<kind>.py -- <out_dir> [preview_samples]

Game space (models.ts): units point -Z, y up, 1 unit = 1 tile. Blender space: forward +Y,
up +Z. game (gx, gy, gz) = Blender (gx, -gz, gy); the glTF exporter maps Blender (x, y, z) to
(x, z, -y), so the GLB comes out in game space. Colours are the game's palette: glb-models.ts
recolours the blue team shades per faction and turns amber into glow, so keep these exact.
Shapes mirror the builder.ts helpers (block/pairBlock/drum/tube/cyl/cone/torus/sphere).
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

_a = sys.argv[sys.argv.index("--") + 1:]
OUT = _a[0]
SAMPLES = int(_a[1]) if len(_a) > 1 else 48
os.makedirs(OUT, exist_ok=True)

GM, GM_D, GM_L, TRACK, BARREL = 0x50575F, 0x31353B, 0x747D87, 0x1C1E21, 0x2A2D31
AMBER, HAZ, HAZ_D, EXHAUST = 0xFF9C1F, 0xE0B23A, 0x2B2A28, 0xFFA040
T_MAIN, T_DARK, T_LIGHT = 0x2A6CF2, 0x1A3F94, 0x7AACFF  # the blue team shades (blue = the GLB's paint)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

_M = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))  # game -> blender axes (a proper rotation)
_AXIS_Z = Matrix.Rotation(math.pi / 2, 3, "X")  # blender cylinder/torus axis Z -> game Z (B -Y)


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(h):
    return tuple(lin(((h >> s) & 255) / 255) for s in (16, 8, 0))


def g2b(p):
    return Vector((p[0], -p[2], p[1]))


def _rot(rot):  # game Euler (three.js 'XYZ' = Rx*Ry*Rz) -> blender rotation matrix
    rg = Matrix.Rotation(rot[0], 3, "X") @ Matrix.Rotation(rot[1], 3, "Y") @ Matrix.Rotation(rot[2], 3, "Z")
    return _M @ rg @ _M.inverted()


def _finish(o, hex_, at, rot, bevel, axis_fix=False, grade=0.25):
    """Apply scale/axis fix, place, bevel, paint (flat colour + per-part grade toward its base)."""
    if axis_fix:
        o.rotation_euler = _AXIS_Z.to_euler()
        bpy.ops.object.transform_apply(rotation=True)
    o.rotation_euler = _rot(rot).to_euler()
    o.location = g2b(at)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    if bevel:
        m = o.modifiers.new("bv", "BEVEL")
        m.width, m.segments, m.limit_method = bevel, 1, "ANGLE"
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier="bv")
    me = o.data
    attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    r, g, b = rgb(hex_)
    zs = [v.co.z for v in me.vertices]
    lo, hi = min(zs), max(zs)
    for i, loop in enumerate(me.loops):
        k = 1 - grade * (1 - (me.vertices[loop.vertex_index].co.z - lo) / max(1e-4, hi - lo))
        attr.data[i].color = (r * k, g * k, b * k, 1)
    return o


def box(size, at, hex_, bevel=0.02, rot=(0, 0, 0), taper=0.0, **kw):
    """size = game (x width, y height, z length)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(scale=True)
    if taper:
        bm = bmesh.new(); bm.from_mesh(o.data)
        for v in bm.verts:
            if v.co.z > 0:
                v.co.x *= 1 - taper; v.co.y *= 1 - taper
        bm.to_mesh(o.data); bm.free()
    return _finish(o, hex_, at, rot, bevel, **kw)


def pair_box(size, at, hex_, **kw):
    """The same box mirrored across x (rotations about y/z mirror too)."""
    rot = kw.pop("rot", (0, 0, 0))
    return [box(size, at, hex_, rot=rot, **kw),
            box(size, (-at[0], at[1], at[2]), hex_, rot=(rot[0], -rot[1], -rot[2]), **kw)]


def drum(r_bot, r_top, h, seg, at, hex_, bevel=0.0, rot=(0, 0, 0), **kw):
    """Upright tapered drum (game y axis)."""
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r_bot, radius2=r_top, depth=h)
    return _finish(bpy.context.object, hex_, at, rot, bevel, **kw)


def cyl(r_top, r_bot, h, seg, at, hex_, rot=(0, 0, 0), **kw):
    """Cylinder along the game y axis, then rotated by `rot` (rot z = pi/2 lays it along x)."""
    return drum(r_bot, r_top, h, seg, at, hex_, rot=rot, **kw)


def tube(r, length, seg, at, hex_, rot=(0, 0, 0), **kw):
    """Cylinder along game z (barrels), then rotated by `rot`."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=length)
    return _finish(bpy.context.object, hex_, at, rot, 0, axis_fix=True, **kw)


def octo(w, d, h, taper, at, hex_, **kw):
    """models.ts skirt(): tapered octagonal slab, flat faces to front/back/sides."""
    k = 1 / math.cos(math.pi / 8)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1, radius2=1 - taper, depth=1)
    o = bpy.context.object
    o.rotation_euler = (0, 0, math.pi / 8)
    bpy.ops.object.transform_apply(rotation=True)
    o.scale = (w / 2 * k, d / 2 * k, h)
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, hex_, at, (0, 0, 0), 0, **kw)


def cone(r, h, seg, at, hex_, rot=(0, 0, 0), **kw):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=0, depth=h)
    return _finish(bpy.context.object, hex_, at, rot, 0, **kw)


def torus(R, r, at, hex_, seg=8, rot=(0, 0, 0), **kw):
    """Ring around the game z axis (a coil on a barrel)."""
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=5)
    return _finish(bpy.context.object, hex_, at, rot, 0, axis_fix=True, **kw)


def sphere(r, at, hex_, w=6, h=4, **kw):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=w, ring_count=h)
    return _finish(bpy.context.object, hex_, at, (0, 0, 0), 0, grade=0, **kw)


def barrel(base, r, length, pitch, hex_, seg=6, k=None):
    """models.ts barrel(): from `base`, pitched up, along -Z. k = centre distance (default half)."""
    k = length / 2 if k is None else k
    p = (base[0], base[1] + math.sin(pitch) * k, base[2] - math.cos(pitch) * k)
    return tube(r, length, seg, p, hex_, rot=(pitch, 0, 0))


def tip(base, length, pitch):
    return (base[0], base[1] + math.sin(pitch) * length, base[2] - math.cos(pitch) * length)


def light(at, s=0.03, hex_=AMBER):
    return box((s, s * 0.8, s), at, hex_, bevel=0, grade=0)


def tracks(x, w, h, length, team=T_MAIN, z=0.0):
    """models.ts tracks(): track block, road wheels, sprockets and a team fender per side."""
    out = []
    n = max(3, round(length / 0.16))
    for s in (1, -1):
        out.append(box((w, h, length), (s * x, h / 2 + 0.01, z), TRACK, bevel=h * 0.3))
        for i in range(n):
            wz = z - length / 2 + length * (i + 0.5) / n
            out.append(cyl(h * 0.32, h * 0.32, w + 0.012, 8, (s * x, h * 0.42, wz), GM_D, rot=(0, 0, math.pi / 2), grade=0))
        for ez in (-1, 1):  # idler / sprocket discs
            out.append(cyl(h * 0.4, h * 0.4, w + 0.02, 10, (s * x, h * 0.45, z + ez * (length / 2 - h * 0.35)), GM_L,
                           rot=(0, 0, math.pi / 2), grade=0))
        out.append(box((w + 0.03, 0.03, length * 0.86), (s * x, h + 0.025, z + length * 0.03), team, bevel=0.012))
    return out


def join(objs, name, shift=(0, 0, 0), ao=(0.15, 0.4)):
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = o.data.name = name
    me = o.data
    off = g2b(shift)
    attr = me.color_attributes["Col"]
    for li, loop in enumerate(me.loops):
        z = me.vertices[loop.vertex_index].co.z  # hull parts are built in game space (turret: shifted below)
        k = 1.0
        if name == "hull" and z < ao[0]:
            k = 1 - ao[1] * (1 - max(0.0, z) / ao[0])
        c = attr.data[li].color
        attr.data[li].color = (min(1, c[0] * k), min(1, c[1] * k), min(1, c[2] * k), 1)
    for v in me.vertices:
        v.co -= off
    bpy.ops.object.shade_flat()
    o.location = off
    return o


def export_model(name):
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(os.path.abspath(OUT), f"{name}.glb"),
        export_format="GLB", export_vertex_color="ACTIVE", export_materials="NONE",
        export_animations=False, export_apply=True)


def export_and_preview(hull, turret, name, ortho=2.0):
    export_model(name)
    mat = bpy.data.materials.new("vc"); mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.55
    bsdf.inputs["Metallic"].default_value = 0.25
    node = nt.nodes.new("ShaderNodeVertexColor"); node.layer_name = "Col"
    nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    for o in (hull, turret):
        if o:
            o.data.materials.append(mat)
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.5
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), 0, math.radians(-35))
    cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = ortho
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    co.location = (0, -4.0, 3.4); co.rotation_euler = (math.radians(50), 0, 0)
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 640
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.5, 0.55, 0.6)
    pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
    hull.parent = pivot
    if turret:
        turret.parent = hull
    for i, a in enumerate((20, 155)):
        pivot.rotation_euler[2] = math.radians(a)
        sc.render.filepath = f"{OUT}/preview_{i}.png"
        bpy.ops.render.render(write_still=True)
    print("DONE")
