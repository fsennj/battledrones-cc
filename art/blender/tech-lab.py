"""Octagonal research station around an amber-glass containment dome."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, marking, threshold

H = [
    box((1.94, 0.12, 1.94), (0, 0.06, 0), GM_D, bevel=0.034, taper=0.025),
    box((1.86, 0.034, 1.86), (0, 0.128, 0), CONCRETE, bevel=0.01),
    drum(0.862, 0.81, 0.5, 8, (0, 0.395, 0), GM, 0.025, rot=(0, math.pi / 8, 0)),
    drum(0.84, 0.85, 0.072, 8, (0, 0.497, 0), T_DARK, 0.006, rot=(0, math.pi / 8, 0)),
    drum(0.861, 0.749, 0.09, 8, (0, 0.649, 0), T_MAIN, 0.016, rot=(0, math.pi / 8, 0)),
    cyl(0.594, 0.663, 0.056, 20, (0, 0.71, 0), STEEL, bevel=0.009),
    cyl(0.531, 0.555, 0.075, 20, (0, 0.744, 0), RECESS, bevel=0.006),
]

# Individual tinted glazing bays give the dome depth under its metal cage.
base, radius = 0.741, 0.449
angles = (0, 0.24, 0.49, 0.77, 1.06, 1.34)
tints = (0xAE6229, 0xD7742B, 0xEB8732, 0xF39D43, 0xC88749)
for i in range(16):
    a0, a1 = math.tau * i / 16, math.tau * (i + 1) / 16
    for j, (lo, hi) in enumerate(zip(angles, angles[1:])):
        verts = [(radius * math.cos(t) * math.cos(a), base + radius * math.sin(t),
                  radius * math.cos(t) * math.sin(a)) for t, a in ((lo, a0), (hi, a0), (hi, a1), (lo, a1))]
        tint = tints[min(len(tints) - 1, j + (i % 5 == 1))]
        H.append(marking(verts, [(0, 1, 2, 3)], tint))
for y, r in ((0.785, 0.454), (0.958, 0.395), (1.128, 0.229)):
    H.append(torus(r, 0.018, (0, y, 0), GM_D, seg=24, rot=(math.pi / 2, 0, 0)))
for i in range(8):
    a = math.tau * i / 8
    rail = [(r * math.cos(a), y, r * math.sin(a)) for r, y in
            ((0.467, 0.78), (0.402, 0.956), (0.301, 1.067), (0.214, 1.134), (0.107, 1.182))]
    for start, end in zip(rail, rail[1:]):
        H.append(beam(start, end, 0.026, 0.027, GM_D))
H.extend([
    drum(0.126, 0.106, 0.031, 12, (0, 1.18, 0), T_MAIN, 0.006),
    cyl(0.041, 0.057, 0.03, 8, (0, 1.204, 0), GM_D),
    light((0, 1.225, 0), 0.046),
])

# Corner instruments are visibly independent of the containment shell.
for x, z in ((0.693, 0.693), (-0.693, 0.693), (0.693, -0.693), (-0.693, -0.693)):
    H.extend([
        box((0.216, 0.125, 0.216), (x, 0.207, z), GM_D, 0.016),
        box((0.132, 0.312, 0.142), (x, 0.398, z), STEEL, 0.012, taper=0.18),
        cyl(0.031, 0.049, 0.46, 8, (x, 0.711, z), GM_D),
        box((0.114, 0.088, 0.114), (x, 0.883, z), T_DARK, 0.009),
        drum(0.06, 0.092, 0.074, 8, (x, 0.984, z), T_MAIN, 0.007),
        cyl(0.057, 0.057, 0.018, 8, (x, 1.029, z), GM_L),
        light((x, 1.047, z), 0.054),
    ])
    H.append(beam((x * 0.76, 0.69, z * 0.76), (x, 0.905, z), 0.024, 0.023, GM_D))
for x in (-0.753, 0.753):
    for z in (-0.32, 0, 0.32):
        H.append(box((0.037, 0.162, 0.186), (x, 0.36, z), GM_D, 0.006))
        H.append(box((0.04, 0.032, 0.15), (x * 1.028, 0.397, z), AMBER, bevel=0, grade=0))
for x in (-0.48, 0.48):
    H.extend(grille(x, 0.701, -0.405, 0.178, 0.168, 4))

# An angled entrance canopy and lit frame project just above the apron.
H.extend([
    box((0.51, 0.272, 0.279), (0, 0.285, 0.799), GM_D, 0.016, taper=0.08),
    box((0.36, 0.196, 0.022), (0, 0.251, 0.938), RECESS, 0.005),
    box((0.422, 0.06, 0.218), (0, 0.443, 0.824), T_MAIN, 0.01),
    box((0.268, 0.04, 0.026), (0, 0.392, 0.937), AMBER, bevel=0, grade=0),
    box((0.55, 0.034, 0.141), (0, 0.153, 0.889), GM_L, 0.005),
])
H.extend(threshold(0, 0.169, 0.921, 0.54, 0.096, 4))

join(H, "hull", ao=(0.24, 0.32))
export_building("tech-lab")
