"""Juggernaut (siege walker) as a detailed low-poly model, built headless in Blender.

    blender -b --factory-startup -P art/blender/juggernaut.py -- <out_dir> [preview_samples]

Writes <out_dir>/juggernaut.glb (nodes "hull" and "turret", vertex colours only, no
textures) and 8 preview PNGs. Game space: units point -Z, y up, 1 unit = 1 tile.
Blender space: forward = +Y, up = +Z; the glTF exporter maps (x, y, z) -> (x, z, -y),
so game (gx, gy, gz) = Blender (gx, -gz, gy). Colours are the game's palette
(models.ts); the loader (src/game/three/glb-models.ts) recolours the team shades per
faction and turns amber into glow, so keep these exact.
"""
import bpy, bmesh, sys, math
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
SAMPLES = int(sys.argv[sys.argv.index("--") + 2]) if len(sys.argv) > sys.argv.index("--") + 2 else 48

GM, GM_D, GM_L, TRACK, BARREL = 0x50575F, 0x31353B, 0x747D87, 0x1C1E21, 0x2A2D31
AMBER, HAZ = 0xFF9C1F, 0xE0B23A
T_MAIN, T_DARK, T_LIGHT = 0x2A6CF2, 0x1A3F94, 0x7AACFF
MOUNT = (0.0, 0.4, 0.1)  # turret pivot in hull space (game coords, as models.ts)


def lin(c):  # sRGB 0..1 -> linear (three.js Color.setHex does the same)
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hex_):
    return tuple(lin(((hex_ >> s) & 255) / 255) for s in (16, 8, 0))


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def g2b(p):  # game -> blender
    return Vector((p[0], -p[2], p[1]))


def finish(o, hex_, bevel=0.0, seg=1):
    if bevel:
        m = o.modifiers.new("bv", "BEVEL")
        m.width, m.segments, m.limit_method = bevel, seg, "ANGLE"
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier="bv")
    me = o.data
    attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    r, g, b = rgb(hex_)
    for i in range(len(me.loops)):
        attr.data[i].color = (r, g, b, 1)
    return o


def box(size, at, hex_, bevel=0.02, rot=(0, 0, 0), taper=0.0):
    """size = game (x width, y height, z length), at = game centre, rot = game Euler."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(scale=True)
    if taper:  # narrow the top face
        bm = bmesh.new(); bm.from_mesh(o.data)
        for v in bm.verts:
            if v.co.z > 0:
                v.co.x *= 1 - taper; v.co.y *= 1 - taper
        bm.to_mesh(o.data); bm.free()
    o.rotation_euler = (rot[0], -rot[2], -rot[1])
    o.location = g2b(at)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    return finish(o, hex_, bevel)


def cyl(r, length, at, hex_, axis="z", verts=10, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length)
    o = bpy.context.object
    if axis == "x":
        o.rotation_euler = (0, math.pi / 2, 0)
    elif axis == "y":
        o.rotation_euler = (math.pi / 2, 0, 0)
    o.location = g2b(at)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    return finish(o, hex_, bevel)


def join(objs, name, shift=(0, 0, 0)):
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    me = o.data
    me.name = name
    off = g2b(shift)
    for v in me.vertices:
        v.co -= off
    # baked shading like builder.ts: darker toward the ground (contact AO) and each part's base
    attr = me.color_attributes["Col"]
    for li, loop in enumerate(me.loops):
        z = me.vertices[loop.vertex_index].co.z + off.z
        k = 1.0
        if name == "hull" and z < 0.4:
            k *= 1 - 0.4 * (1 - max(0.0, z) / 0.4)
        c = attr.data[li].color
        attr.data[li].color = (min(1, c[0] * k), min(1, c[1] * k), min(1, c[2] * k), 1)
    bpy.ops.object.shade_flat()
    o.location = g2b(shift)
    return o


# ------------------------------------------------------------------ hull ---
H = []
for side in (1, -1):
    x = side * 0.52
    H.append(box((0.26, 0.26, 1.46), (x, 0.13, 0.0), TRACK, 0.03))                     # track run
    H.append(box((0.30, 0.045, 1.5), (x, 0.285, 0.0), T_MAIN, 0.015))                   # team fender
    for z in (-0.62, -0.31, 0.0, 0.31, 0.62):                                          # road wheels
        H.append(cyl(0.085, 0.05, (x + side * 0.145, 0.12, z), GM_L, "x", 12))
        H.append(cyl(0.035, 0.07, (x + side * 0.15, 0.12, z), GM_D, "x", 8))
    H.append(cyl(0.1, 0.05, (x + side * 0.145, 0.15, -0.74), GM_D, "x", 12))             # idler
    H.append(cyl(0.1, 0.05, (x + side * 0.145, 0.15, 0.74), GM_D, "x", 12))             # sprocket
H.append(box((0.86, 0.22, 1.3), (0, 0.3, 0.0), GM, 0.045, taper=0.1))                   # main hull
H.append(box((0.8, 0.09, 0.22), (0, 0.28, -0.68), GM_D, 0.02, rot=(0.5, 0, 0)))         # glacis
H.append(box((0.5, 0.05, 0.3), (0, 0.4, 0.5), GM_D, 0.015))                             # engine deck
for x in (-0.14, 0, 0.14):
    H.append(box((0.08, 0.02, 0.2), (x, 0.43, 0.5), BARREL, 0.005))                     # vents
for z in (0.38, 0.62):
    H.append(box((0.5, 0.012, 0.02), (0, 0.435, z), GM_L, 0.004))                       # deck ribs
for side in (1, -1):
    H.append(box((0.2, 0.03, 0.34), (side * 0.22, 0.43, -0.42), T_MAIN, 0.012))         # armour wedge
    H.append(box((0.06, 0.16, 1.2), (side * 0.72, 0.24, 0.0), T_MAIN, 0.012))           # side skirt
    H.append(box((0.045, 0.1, 1.0), (side * 0.755, 0.24, 0.0), T_DARK, 0.01))            # skirt shadow plate
    H.append(box((0.26, 0.34, 0.06), (side * 0.28, 0.24, 0.76), GM_D, 0.012, rot=(-0.45, 0, 0)))  # spade
    H.append(box((0.03, 0.3, 0.05), (side * 0.28, 0.25, 0.79), GM_L, 0.006, rot=(-0.45, 0, 0)))   # spade rib
    H.append(cyl(0.03, 0.03, (side * 0.24, 0.27, -0.66), AMBER, "y", 8))               # head lamps
    H.append(box((0.06, 0.06, 0.04), (side * 0.3, 0.3, -0.68), HAZ, 0.008))            # hazard tabs
for sx in (-0.3, -0.1, 0.1, 0.3):
    for sz in (-0.5, 0.0):
        H.append(cyl(0.012, 0.02, (sx, 0.415, sz), GM_L, "z", 6))                      # rivets
hull = join(H, "hull")

# ---------------------------------------------------------------- turret ---
pitch = 0.62
base = Vector((0, 0.17, -0.1))  # barrel base in turret space (game coords)
d = Vector((0, math.sin(pitch), -math.cos(pitch)))  # game direction (forward = -z, up = +y)
M = Vector(MOUNT)
T = []
t_at = lambda p: (p[0] + M.x, p[1] + M.y, p[2] + M.z)  # turret-space -> hull-space for building


def tbox(size, at, hex_, bevel=0.02, **kw):
    return box(size, t_at(at), hex_, bevel, **kw)


T.append(tbox((0.66, 0.22, 0.6), (0, 0.11, 0.06), GM, 0.04, taper=0.16))              # shield
T.append(tbox((0.46, 0.05, 0.36), (0, 0.235, 0.06), T_MAIN, 0.015))                    # roof plate
T.append(tbox((0.34, 0.015, 0.2), (0, 0.26, 0.1), T_LIGHT, 0.004))                     # roof highlight
for side in (1, -1):
    T.append(tbox((0.05, 0.14, 0.34), (side * 0.36, 0.11, 0.04), T_MAIN, 0.012))       # side plates
    T.append(tbox((0.03, 0.1, 0.2), (side * 0.385, 0.11, 0.04), T_DARK, 0.008))
T.append(cyl(0.07, 0.05, t_at((0.16, 0.27, 0.2)), GM_L, "z", 8))                       # hatch
T.append(cyl(0.03, 0.03, t_at((-0.16, 0.22, 0.2)), AMBER, "z", 8))                    # lamp
T.append(cyl(0.012, 0.3, t_at((-0.24, 0.34, 0.26)), GM_D, "z", 6))                     # antenna


def barrel_seg(r, length, k, hex_, verts=10):  # centred k along the barrel
    centre = base + d * k
    gp = t_at((centre.x, centre.y, centre.z))
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length)
    o = bpy.context.object
    th = pitch - math.pi / 2
    o.rotation_euler = (th, 0, 0)
    o.location = g2b(gp)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    return finish(o, hex_)


T.append(barrel_seg(0.1, 0.95, 0.475, BARREL))                                         # barrel
for k in (0.15, 0.4, 0.65):
    T.append(barrel_seg(0.125, 0.07, k, GM_D))                                          # collars
T.append(barrel_seg(0.15, 0.1, 0.9, GM_D))                                              # muzzle brake
T.append(barrel_seg(0.155, 0.02, 0.87, GM_L))
T.append(barrel_seg(0.155, 0.02, 0.93, GM_L))
T.append(barrel_seg(0.08, 0.006, 0.97, TRACK))                                          # bore
T.append(tbox((0.3, 0.16, 0.2), (0, 0.17, -0.06), GM_D, 0.03))                         # cradle
turret = join(T, "turret", shift=MOUNT)

# --------------------------------------------------------------- export ---
bpy.ops.export_scene.gltf(
    filepath=f"{OUT}/juggernaut.glb", export_format="GLB", export_vertex_color="ACTIVE",
    export_materials="NONE", export_animations=False, export_apply=True,
    export_draco_mesh_compression_enable=False,
)

# --------------------------------------------------------------- preview ---
mat = bpy.data.materials.new("vc"); mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.55
bsdf.inputs["Metallic"].default_value = 0.25
node = nt.nodes.new("ShaderNodeVertexColor"); node.layer_name = "Col"
nt.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
for o in (hull, turret):
    o.data.materials.append(mat)
# glow lamps: amber stays flat colour in the preview, fine

sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.5
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(-35))
cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = 2.9
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
co.location = (0, -4.0, 3.4); co.rotation_euler = (math.radians(50), 0, 0)
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 768
sc.render.film_transparent = True
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.5, 0.55, 0.6)
pivot = bpy.data.objects.new("pivot", None); sc.collection.objects.link(pivot)
hull.parent = pivot; turret.parent = hull
for i in (0, 2, 5):
    pivot.rotation_euler[2] = math.radians(45 * i + 20)
    sc.render.filepath = f"{OUT}/preview_{i}.png"
    bpy.ops.render.render(write_still=True)
print("DONE")
