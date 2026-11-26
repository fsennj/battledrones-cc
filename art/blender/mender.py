"""Mender (hovering repair drone). See lib.py for how to run.

Mirrors models.ts `mender:` part for part: a low dodecagonal skirt, a hemisphere dome,
an amber repair cross on the dome (TS paints it GREEN with glow — lights become amber
in the GLB palette), a team-blue rotor ring at r 0.25, an amber torch emitter under the
belly and three rotor pods on the ring. The crossed rotor (TS rotorGeo(0.07)) exports
as a separate mesh named "rotor" that the game spins at the three pod anchors.
"""
import sys, os, math
import bpy, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _finish  # `import *` skips underscore names

BLADE = 0x1A1C1F  # models.ts rotorGeo blade colour

H = []
H.append(drum(0.19, 0.17, 0.08, 12, (0, 0, 0), GM_L, bevel=0.015))  # skirt puck

# dome: hemisphere (TS sphere w=10 h=5 phi=pi/2) sitting on the skirt
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, segments=10, ring_count=10)
d = bpy.context.object
bm = bmesh.new(); bm.from_mesh(d.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-6], context="VERTS")
bm.to_mesh(d.data); bm.free()
_finish(d, GM, (0, 0.03, 0), (0, 0, 0), 0)
H.append(d)

H.append(box((0.15, 0.022, 0.048), (0, 0.146, 0), AMBER, bevel=0, grade=0))    # repair cross
# cross arm along z, split beside the x-arm's footprint: same silhouette as TS's one box,
# but no coplanar overlapping top faces (they z-fight as a black diamond in the middle)
H.append(box((0.048, 0.022, 0.051), (0, 0.146, 0.0495), AMBER, bevel=0, grade=0))
H.append(box((0.048, 0.022, 0.051), (0, 0.146, -0.0495), AMBER, bevel=0, grade=0))
H.append(torus(0.25, 0.024, (0, 0, 0), T_MAIN, seg=20, rot=(math.pi / 2, 0, 0)))  # rotor ring
H.append(cyl(0.05, 0.03, 0.04, 8, (0, -0.06, 0), AMBER, grade=0))               # torch emitter
for i in range(3):  # rotor pods on the ring at a = i*2pi/3 + pi/6, radius 0.25
    a = i / 3 * math.pi * 2 + math.pi / 6
    H.append(cyl(0.03, 0.03, 0.04, 6, (math.cos(a) * 0.25, 0.01, math.sin(a) * 0.25), GM_D))
hull = join(H, "hull")

# the rotor the game spins at the three pod anchors (TS rotorGeo(0.07), axis y)
R = [
    box((0.14, 0.008, 0.0126), (0, 0, 0), BLADE, bevel=0, grade=0),
    box((0.0126, 0.008, 0.14), (0, 0, 0), BLADE, bevel=0, grade=0),
    cyl(0.0154, 0.0154, 0.03, 6, (0, 0, 0), GM_L, grade=0),
]
rotor = join(R, "rotor")

export_and_preview(hull, None, "mender", ortho=0.95)
