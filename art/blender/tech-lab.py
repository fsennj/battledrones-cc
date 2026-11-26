"""Tech Lab (research building, 2x2 tiles). See lib.py for how to run.

Mirrors the procedural tech-lab in src/game/three/models.ts: an octagonal lab drum on a
plinth with a team band and crown, an orange research dome on top caged by dark hoop rings,
four corner sensor masts with team collars and amber beacons, and a glazed entry block on the
south face. Authored at map scale (1 unit = 1 tile), ground at y = 0, centred on the
footprint: the game draws the GLB unscaled, exactly like the procedural model it replaces.
Node names: hull only (the ModelDef in models.ts returns hull, no turret/dome parts).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _finish

DOME = 0xFF8A24  # the TS sphere colour of the lit research dome


def cap(r, phi, at, hex_, rot=(0, 0, 0), grade=0.25, w=16, h=8):
    """Spherical cap of polar angle `phi` (builder.ts sphere phiLength), pole up before `rot`."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=w, ring_count=h)
    o = bpy.context.object
    zc = r * math.cos(phi)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in [v for v in bm.verts if v.co.z < zc - 1e-5]:
        bm.verts.remove(v)
    bm.to_mesh(o.data)
    bm.free()
    return _finish(o, hex_, at, rot, 0, grade=grade)


H = []
# plinth
H.append(box((1.92, 0.12, 1.92), (0, 0.06, 0), GM_D, 0.03, taper=0.03))
# the lab drum: octagonal body, dark team-dark band, team crown
H.append(drum(0.92, 0.84, 0.5, 8, (0, 0.37, 0), GM, 0.03, rot=(0, math.pi / 8, 0)))
H.append(cyl(0.87, 0.87, 0.1, 8, (0, 0.5, 0), T_DARK, rot=(0, math.pi / 8, 0)))
H.append(drum(0.84, 0.7, 0.08, 8, (0, 0.66, 0), T_MAIN, 0.02, rot=(0, math.pi / 8, 0)))
# the lit research dome and its four cage hoops (two horizontal, two meridional)
H.append(cap(0.48, math.pi / 2, (0, 0.66, 0), DOME, w=14, h=6))
H.append(torus(0.5, 0.03, (0, 0.72, 0), GM_D, seg=20, rot=(math.pi / 2, 0, 0)))
H.append(torus(0.38, 0.025, (0, 0.95, 0), GM_D, seg=18, rot=(math.pi / 2, 0, 0)))
H.append(torus(0.48, 0.025, (0, 0.66, 0), GM_D, seg=20))
H.append(torus(0.48, 0.025, (0, 0.66, 0), GM_D, seg=20, rot=(0, math.pi / 2, 0)))
# the four corner sensor masts: tapered post, team collar, amber beacon
for x, z in ((0.68, 0.68), (-0.68, 0.68), (0.68, -0.68), (-0.68, -0.68)):
    H.append(cyl(0.035, 0.06, 0.95, 6, (x, 0.55, z), GM_L))
    H.append(cyl(0.05, 0.05, 0.08, 6, (x, 0.8, z), T_MAIN))
    H.append(sphere(0.045, (x, 1.05, z), AMBER, w=6, h=4))
# entry block on the south face: body, team canopy, lit window strip
H.append(box((0.42, 0.3, 0.32), (0, 0.27, 0.86), GM_D, 0.02))
H.append(box((0.36, 0.025, 0.22), (0, 0.43, 0.86), T_MAIN, 0.01))
H.append(box((0.32, 0.06, 0.02), (0, 0.33, 1.02), AMBER, bevel=0))
hull = join(H, "hull", ao=(0.3, 0.38))
export_and_preview(hull, None, "tech-lab", ortho=2.3)
