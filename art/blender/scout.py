"""Scout (fast light recon drone on four ducted rotors). See lib.py for how to run."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as a
from lib import *

# models.ts rearRing(t): halfway from T_DARK to T_MAIN (per channel, halves added)
REAR_RING = 0x2255C3


def ellipsoid(r, scale, at, hex_, w=8, h=6):
    """models.ts sphere() with a non-uniform scale (game axes)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=w, ring_count=h)
    o = bpy.context.object
    o.scale = (scale[0], scale[2], scale[1])
    bpy.ops.object.transform_apply(scale=True)
    return a._finish(o, hex_, at, (0, 0, 0), 0)


H = [
    ellipsoid(0.1, (1, 0.6, 1.3), (0, 0, 0), GM, w=8, h=6),                                     # hull pod
    sphere(0.038, (0, -0.01, -0.125), AMBER, w=6, h=4),                                         # amber eye
    box((0.03, 0.02, 0.4), (0, 0, 0), GM_D, 0, rot=(0, math.pi / 4, 0)),                        # crossed booms
    box((0.03, 0.02, 0.4), (0, 0, 0), GM_D, 0, rot=(0, -math.pi / 4, 0)),
]
for x, z in ((0.14, -0.14), (-0.14, -0.14), (0.14, 0.14), (-0.14, 0.14)):
    H.append(cyl(0.03, 0.03, 0.05, 8, (x, 0.005, z), GM))                                       # rotor pylons
    H.append(torus(0.085, 0.015, (x, 0.02, z), T_MAIN if z < 0 else REAR_RING,
                   seg=14, rot=(math.pi / 2, 0, 0)))                                            # duct rings
H.append(box((0.08, 0.03, 0.09), (0, 0.055, 0.02), T_MAIN, 0.012))                              # sensor hump
hull = join(H, "hull", ao=(-1.0, 0.0))  # partB has no ground occlusion: threshold below any vertex

# models.ts rotorGeo(0.075) as its own builder: no grade — the game spins it at the 4 pylons
R = [
    box((0.15, 0.008, 0.0135), (0, 0, 0), 0x1A1C1F, 0, grade=0),
    box((0.0135, 0.008, 0.15), (0, 0, 0), 0x1A1C1F, 0, grade=0),
    cyl(0.0165, 0.0165, 0.03, 6, (0, 0, 0), GM_L, grade=0),
]
join(R, "rotor")
export_and_preview(hull, None, "scout", ortho=1.2)
