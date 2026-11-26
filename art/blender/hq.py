"""Raise the headquarters around a domed command centre and four security towers."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _finish
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, threshold


def dome(radius, base):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=12)
    obj = bpy.context.object
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    for vertex in [v for v in mesh.verts if v.co.z < -1e-5]:
        mesh.verts.remove(vertex)
    mesh.to_mesh(obj.data)
    mesh.free()
    return _finish(obj, STEEL, (0, base, 0), (0, 0, 0), 0, grade=0.35)


H = [
    octo(2.96, 2.96, 0.13, 0.02, (0, 0.065, 0), GM_D),
    octo(2.86, 2.86, 0.045, 0, (0, 0.145, 0), CONCRETE),
    box((2.29, 0.41, 2.29), (0, 0.367, 0), GM, 0.05, taper=0.05),
    box((2.24, 0.08, 2.24), (0, 0.571, 0), RECESS, 0.018),
    octo(2.16, 2.16, 0.046, 0.025, (0, 0.62, 0), GM_L),
]

# Broad team shoulders and raised walkways surround the dome.
for side in (-1, 1):
    H.append(box((0.26, 0.052, 1.34), (side * 0.91, 0.646, 0), T_MAIN, 0.009))
    H.append(box((0.04, 0.034, 1.18), (side * 1.06, 0.681, 0), T_DARK, 0.004))
    H.append(box((1.34, 0.052, 0.26), (0, 0.646, side * 0.91), T_MAIN, 0.009))
    H.append(box((1.18, 0.034, 0.04), (0, 0.681, side * 1.06), T_DARK, 0.004))
    for x in (-0.54, 0.54):
        H.extend(grille(x, 0.665, side * 0.9, 0.21, 0.14, 3))

# Armoured security towers with raised observation rooms and independent service hatches.
for sx in (-1, 1):
    for sz in (-1, 1):
        x, z = sx * 1.05, sz * 1.05
        H.extend([
            octo(0.73, 0.73, 0.10, 0.08, (x, 0.198, z), GM_D),
            drum(0.31, 0.24, 0.60, 8, (x, 0.492, z), GM, 0.016),
            cyl(0.31, 0.31, 0.054, 8, (x, 0.37, z), STEEL),
            drum(0.257, 0.29, 0.11, 8, (x, 0.742, z), RECESS, 0.012),
            cyl(0.28, 0.28, 0.048, 8, (x, 0.803, z), AMBER, grade=0),
            drum(0.32, 0.255, 0.095, 8, (x, 0.869, z), T_MAIN, 0.021),
            cyl(0.126, 0.142, 0.04, 8, (x, 0.925, z), GM_D),
            light((x, 0.954, z), 0.055),
            box((0.14, 0.26, 0.033), (x, 0.24, z + sz * 0.289), T_DARK, 0.008),
            box((0.03, 0.1, 0.21), (x + sx * 0.268, 0.52, z), GM_D, 0.006),
        ])

# Concentric trim follows the command dome, with radial ribs rising from the collar.
base, radius = 0.654, 0.69
H.append(dome(radius, base))
H.append(cyl(0.72, 0.72, 0.063, 24, (0, base + 0.01, 0), T_DARK))
H.append(torus(0.70, 0.025, (0, base + 0.047, 0), T_MAIN, seg=24, rot=(math.pi / 2, 0, 0)))
H.append(torus(0.51, 0.019, (0, base + 0.47, 0), GM_D, seg=24, rot=(math.pi / 2, 0, 0)))
for i in range(8):
    a = math.tau * (i + 0.5) / 8
    rib = [(math.cos(a) * 0.695 * math.cos(t), base + 0.695 * math.sin(t),
            math.sin(a) * 0.695 * math.cos(t)) for t in (0.09, 0.34, 0.6, 0.86, 1.12, 1.3)]
    for start, end in zip(rib, rib[1:]):
        H.append(beam(start, end, 0.034, 0.029, GM_D))

H.extend([
    drum(0.29, 0.29, 0.086, 10, (0, 1.299, 0), GM_D, 0.012),
    drum(0.275, 0.24, 0.057, 10, (0, 1.362, 0), AMBER, grade=0),
    drum(0.29, 0.218, 0.074, 10, (0, 1.42, 0), T_MAIN, 0.009),
    cyl(0.04, 0.073, 0.105, 8, (0, 1.482, 0), GM_D),
    cyl(0.013, 0.028, 0.36, 6, (0, 1.703, 0), STEEL),
    beam((-0.15, 1.695, 0), (0.15, 1.695, 0), 0.02, 0.022, GM_D),
    beam((0, 1.776, -0.09), (0, 1.776, 0.09), 0.018, 0.018, GM_L),
    sphere(0.048, (0, 1.914, 0), AMBER),
])

# Outside service shutters and the inset blast door and approach.
for x in (-1.115, 1.115):
    for z in (-0.67, -0.23, 0.23, 0.67):
        H.append(box((0.06, 0.28, 0.33), (x, 0.35, z), RECESS, 0.01))
        H.append(box((0.07, 0.041, 0.24), (x, 0.422, z), AMBER, bevel=0, grade=0))
for x in (-0.65, 0.65):
    H.append(box((0.17, 0.38, 0.17), (x, 0.36, 1.10), GM_L, 0.018))
    H.append(box((0.078, 0.15, 0.025), (x, 0.405, 1.191), T_MAIN, 0.005))
H.extend([
    box((1.12, 0.37, 0.12), (0, 0.348, 1.125), RECESS, 0.02),
    box((1.19, 0.11, 0.18), (0, 0.554, 1.132), T_MAIN, 0.017),
    box((0.79, 0.026, 0.028), (0, 0.506, 1.229), AMBER, bevel=0, grade=0),
    box((1.12, 0.027, 0.29), (0, 0.172, 1.31), GM_L, 0.008),
])
for i in range(5):
    H.append(box((0.91, 0.034, 0.037), (0, 0.223 + i * 0.06, 1.193), GM, 0.004))
H.extend(threshold(0, 0.187, 1.364, 1.10, 0.14, 6))

# A tilted comms dish sits over the roof on its own pedestal.
position = (0.75, 0.755, -0.64)
tilt = (-0.55, 0, -0.48)
H.append(cyl(0.039, 0.075, 0.16, 8, position, RECESS))
H.append(drum(0.09, 0.204, 0.07, 12, (0.75, 0.858, -0.65), STEEL, 0.009, rot=tilt))
H.append(cyl(0.171, 0.171, 0.016, 12, (0.768, 0.894, -0.672), RECESS, rot=tilt))
H.append(beam((0.773, 0.897, -0.674), (0.817, 0.998, -0.723), 0.028, 0.025, GM_L))
H.append(light((0.817, 0.998, -0.723), 0.047))

join(H, "hull", ao=(0.24, 0.33))
export_building("hq")
