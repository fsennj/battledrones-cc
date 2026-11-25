"""HQ (headquarters, 3x3 tiles). See lib.py for how to run.

Mirrors the procedural hq in src/game/three/models.ts: a tapered base plinth, a tapered keep,
four corner towers, a central dome with a command cab and beacon on the crown, a comms dish on
the north-east roof, team bands, perimeter walls and the main gate with its hazard-edged ramp.
Authored at map scale (1 unit = 1 tile), ground at y = 0, centred on the footprint: the game
draws the GLB unscaled, exactly like the procedural model it replaces.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _finish


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
# plinth and keep
H.append(box((2.9, 0.16, 2.9), (0, 0.06, 0), GM_D, 0.04, taper=0.03))
H.append(box((2.76, 0.05, 2.76), (0, 0.155, 0), GM, 0.012))                      # cap slab on the plinth
H.append(box((2.3, 0.44, 2.3), (0, 0.36, 0), GM, 0.07, taper=0.08))
for s in (1, -1):                                                                # corner buttresses
    H.append(box((0.26, 0.6, 0.26), (s * 0.99, 0.41, 0.99), GM_L, 0.03))
    H.append(box((0.26, 0.6, 0.26), (s * 0.99, 0.41, -0.99), GM_L, 0.03))
# window rows along the keep's four faces
for z in (-1.155, 1.155):
    for x in (-0.75, 0, 0.75):
        H.append(box((0.16, 0.11, 0.02), (x, 0.4, z), AMBER, bevel=0, grade=0))
for x in (-1.155, 1.155):
    for z in (-0.75, 0, 0.75):
        H.append(box((0.02, 0.11, 0.16), (x, 0.4, z), AMBER, bevel=0, grade=0))
# team bands out from the dome, one to each side
for x, z, ry in ((0, -0.86, 0), (0, 0.86, 0), (0.86, 0, math.pi / 2), (-0.86, 0, math.pi / 2)):
    H.append(box((0.36, 0.03, 0.3), (x, 0.592, z), T_MAIN, 0.015, rot=(0, ry, 0)))
# the four corner towers
for x in (-1.05, 1.05):
    for z in (-1.05, 1.05):
        H.append(box((0.78, 0.06, 0.78), (x, 0.09, z), GM_D, 0.02))               # tower footing
        H.append(box((0.24, 0.2, 0.24), (x, 0.2, z), GM_D, 0.015))               # entry stub under the drum
        H.append(drum(0.31, 0.26, 0.74, 8, (x, 0.37, z), GM, 0.03))
        H.append(cyl(0.33, 0.33, 0.025, 8, (x, 0.28, z), GM_L))                   # corbel ring
        H.append(drum(0.28, 0.24, 0.1, 8, (x, 0.79, z), T_MAIN, 0.03))
        H.append(drum(0.17, 0.13, 0.06, 8, (x, 0.87, z), GM_L, 0.015))
        H.append(light((x, 0.92, z), 0.06))
# the dome and its collar rings
H.append(cap(0.74, math.pi / 2, (0, 0.56, 0), GM_L))
H.append(torus(0.75, 0.06, (0, 0.6, 0), T_MAIN, seg=24))
H.append(torus(0.55, 0.03, (0, 1.06, 0), GM_D, seg=20))
# command cab on the crown: amber windows, a team roof, the mast and beacon
H.append(drum(0.24, 0.22, 0.14, 8, (0, 1.3, 0), GM_D, 0.02))
H.append(drum(0.245, 0.245, 0.04, 8, (0, 1.3, 0), AMBER, 0, grade=0))
H.append(drum(0.22, 0.16, 0.06, 8, (0, 1.4, 0), T_MAIN, 0.02))
H.append(cyl(0.022, 0.04, 0.5, 6, (0, 1.68, 0), GM_D))
H.append(sphere(0.06, (0, 1.95, 0), AMBER))
# comms dish on the north-east roof: a shallow tilted dish (cone body, dark recessed face, feed)
H.append(cyl(0.03, 0.05, 0.16, 6, (0.66, 0.66, -0.66), GM_D))
DISH_ROT = (-0.6, 0, -0.6)
H.append(drum(0.07, 0.22, 0.09, 12, (0.66, 0.78, -0.66), GM_L, 0.015, rot=DISH_ROT))
H.append(cyl(0.185, 0.185, 0.02, 12, (0.665, 0.83, -0.685), GM_D, rot=DISH_ROT))
H.append(sphere(0.03, (0.72, 0.88, -0.73), AMBER, w=6, h=4))
# perimeter walls with team copings, amber strips on three faces
for x, z, ry in ((0, 1.16, 0), (0, -1.16, 0), (1.16, 0, math.pi / 2), (-1.16, 0, math.pi / 2)):
    H.append(box((1.0, 0.17, 0.025), (x, 0.4, z), T_MAIN, 0, rot=(0, ry, 0)))
for x, z, ry in ((0, -1.17, 0), (1.17, 0, math.pi / 2), (-1.17, 0, math.pi / 2)):
    H.append(box((0.8, 0.035, 0.02), (x, 0.25, z), AMBER, 0, rot=(0, ry, 0)))
# the main gate: dark door, lit lintel, hazard-edged ramp
H.append(box((0.74, 0.28, 0.06), (0, 0.28, 1.17), GM_D, 0.015))
H.append(box((0.62, 0.035, 0.02), (0, 0.44, 1.2), AMBER, bevel=0, grade=0))
H.append(box((0.82, 0.04, 0.38), (0, 0.12, 1.36), GM_L, 0, rot=(0.22, 0, 0)))
for x in (-0.43, 0.43):
    H.append(box((0.06, 0.05, 0.38), (x, 0.125, 1.36), HAZ, 0, rot=(0.22, 0, 0)))
H.append(box((0.3, 0.12, 0.2), (-0.75, 0.64, 0.55), GM_D, 0.02))                  # side blocks on the wall line
H.append(box((0.24, 0.1, 0.3), (0.7, 0.63, 0.7), GM_D, 0.02))
# corner lamps on the plinth, ducts and vents on the keep's back
for x in (-1.38, 1.38):
    for z in (-1.38, 1.38):
        H.append(box((0.08, 0.05, 0.08), (x, 0.145, z), GM_D, 0.01))
        H.append(light((x, 0.19, z), 0.05))
H.append(tube(0.03, 0.3, 6, (-0.9, 0.5, 0.85), GM_D, rot=(0.45, 0, 0)))
for x in (-0.6, -0.2, 0.2, 0.6):
    H.append(box((0.02, 0.24, 0.02), (x, 0.36, -1.16), GM_D, bevel=0))
hull = join(H, "hull", ao=(0.3, 0.38))
export_and_preview(hull, None, "hq", ortho=3.4)
