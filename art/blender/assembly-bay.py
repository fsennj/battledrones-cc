"""Infantry works with charging alcoves, a parts conveyor, and a welding gantry."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, marking, rim, threshold


def trooper(x, y, z, scale=1, legs=True):
    parts = []
    def piece(centre, size, color, bevel=0.004):
        px, py, pz = centre
        return box(tuple(d * scale for d in size), (x + px * scale, y + py * scale, z + pz * scale),
                   color, bevel * scale)
    if legs:
        for side in (-1, 1):
            parts.append(piece((side * 0.031, 0.026, 0.017), (0.043, 0.044, 0.073), GM_D))
            parts.append(piece((side * 0.031, 0.101, 0.002), (0.035, 0.113, 0.038), STEEL))
    parts.extend([
        piece((0, 0.155, 0), (0.084, 0.046, 0.042), GM_D),
        piece((0, 0.208, 0), (0.101, 0.075, 0.061), GM_L),
        piece((0, 0.219, 0.036), (0.064, 0.047, 0.016), T_DARK),
        piece((0, 0.276, 0.006), (0.068, 0.052, 0.06), GM),
        piece((0, 0.275, 0.037), (0.05, 0.015, 0.01), AMBER, bevel=0),
    ])
    for side in (-1, 1):
        parts.append(piece((side * 0.073, 0.219, 0.004), (0.047, 0.052, 0.068), T_MAIN))
        parts.append(piece((side * 0.078, 0.166, 0.026), (0.029, 0.067, 0.041), GM_D))
    return parts


H = [
    octo(1.94, 1.94, 0.12, 0.027, (0, 0.06, 0), GM_D),
    octo(1.88, 1.88, 0.033, 0, (0, 0.129, 0), CONCRETE),
    box((1.698, 0.02, 1.34), (0, 0.151, 0.255), GM, 0.006),
    box((1.73, 0.57, 0.44), (0, 0.43, -0.728), GM_D, 0.02),
    box((1.813, 0.072, 0.177), (0, 0.713, -0.859), T_DARK, 0.012),
    box((1.821, 0.09, 0.575), (0, 0.749, -0.647), GM_L, 0.022, taper=0.08),
    box((1.73, 0.047, 0.17), (0, 0.792, -0.412), T_MAIN, 0.011),
]

# Three separate charging bays visibly house the finished robots.
for x in (-0.531, 0, 0.531):
    H.extend([
        box((0.402, 0.421, 0.021), (x, 0.416, -0.497), RECESS, 0.008),
        box((0.411, 0.027, 0.143), (x, 0.645, -0.452), GM_L, 0.006),
        box((0.319, 0.021, 0.023), (x, 0.629, -0.368), AMBER, bevel=0, grade=0),
        box((0.36, 0.044, 0.288), (x, 0.179, -0.348), GM_D, 0.008),
        rim(0.081, 0.101, 0.204, T_LIGHT, centre=(x, -0.317), steps=12),
    ])
    H.extend(grille(x, 0.795, -0.683, 0.271, 0.263, 4))
    H.extend(trooper(x, 0.202, -0.317, 1.13))
for x in (-0.831, -0.271, 0.271, 0.831):
    H.append(box((0.06, 0.472, 0.16), (x, 0.382, -0.436), T_DARK, 0.009))
    H.append(box((0.07, 0.07, 0.174), (x, 0.67, -0.436), STEEL, 0.008))

H.append(box((1.697, 0.061, 0.344), (0, 0.177, 0.188), RECESS, 0.01))
for i in range(10):
    H.append(box((0.112, 0.012, 0.282), (-0.729 + 0.162 * i, 0.211, 0.188), GM_D, bevel=0))
for z in (0.022, 0.355):
    H.extend(threshold(0, 0.225, z, 1.67, 0.048, 11))
H.extend([
    drum(0.167, 0.129, 0.127, 10, (0, 0.277, 0.205), GM_L, 0.01),
    drum(0.11, 0.104, 0.026, 10, (0, 0.342, 0.205), T_DARK),
    box((0.125, 0.15, 0.126), (0, 0.369, 0.205), GM_D, 0.008),
    box((0.26, 0.075, 0.173), (0.471, 0.248, 0.206), HAZ_D, 0.009),
    box((0.141, 0.054, 0.116), (-0.491, 0.239, 0.211), GM_L, 0.008),
])
H.extend(trooper(0, 0.173, 0.205, 1.61, legs=False))

# Portal beam and twin articulated welding tools suspended above the workpiece.
for sx in (-1, 1):
    x = sx * 0.745
    H.append(box((0.174, 0.063, 0.22), (x, 0.174, 0.188), GM_D, 0.01))
    H.append(box((0.08, 0.86, 0.10), (x, 0.61, 0.192), GM_D, 0.01))
    H.append(beam((x, 0.209, 0.318), (x, 0.597, 0.184), 0.045, 0.04, STEEL))
    H.append(beam((x, 0.83, 0.21), (sx * 0.554, 0.993, 0.21), 0.047, 0.046, GM_L))
    H.append(light((x, 1.078, 0.189), 0.037))
    H.append(cyl(0.052, 0.057, 0.086, 8, (sx * 0.33, 0.959, 0.196), GM_D))
    p1, p2, p3 = (sx * 0.33, 0.93, 0.196), (sx * 0.38, 0.747, 0.20), (sx * 0.158, 0.627, 0.231)
    H.extend([
        beam(p1, p2, 0.061, 0.066, HAZ), beam(p2, p3, 0.058, 0.056, GM_L),
        tube(0.048, 0.086, 8, p2, RECESS),
        beam(p3, (sx * 0.104, 0.581, 0.231), 0.034, 0.032, GM_D),
        light((sx * 0.093, 0.57, 0.231), 0.029),
    ])
H.extend([
    box((1.588, 0.088, 0.138), (0, 1.011, 0.196), T_MAIN, 0.011),
    box((1.426, 0.046, 0.094), (0, 1.069, 0.196), STEEL, 0.009),
    box((1.247, 0.028, 0.144), (0, 0.96, 0.196), GM_D, 0.005),
    box((1.38, 0.019, 0.023), (0, 1.013, 0.269), T_LIGHT, bevel=0),
])

# A paint-marked test pad and a dark parts bin on the apron.
px, pz = -0.31, 0.669
H.append(cyl(0.241, 0.274, 0.04, 18, (px, 0.177, pz), GM_D))
H.append(rim(0.206, 0.23, 0.199, T_MAIN, centre=(px, pz), steps=18))
H.append(marking([(px + x, 0.2, pz + z) for x, z in
                  ((0, 0.167), (0.108, 0.03), (0.048, 0.03), (0.048, -0.113),
                   (-0.048, -0.113), (-0.048, 0.03), (-0.108, 0.03))],
                 [(0, 1, 2, 5, 6), (2, 3, 4, 5)], HAZ))
H.extend(threshold(0.258, 0.168, 0.877, 0.59, 0.072, 4))
H.extend([
    box((0.348, 0.156, 0.341), (0.646, 0.216, 0.67), T_DARK, 0.012),
    box((0.302, 0.025, 0.29), (0.646, 0.297, 0.67), RECESS, 0.006),
    box((0.193, 0.048, 0.092), (0.646, 0.319, 0.67), STEEL, 0.006, rot=(0.11, 0.27, 0.07)),
    box((0.111, 0.049, 0.056), (0.71, 0.32, 0.606), GM_L, 0.006, rot=(0.19, -0.4, 0.09)),
    light((-0.86, 0.18, 0.724), 0.041),
])

join(H, "hull", ao=(0.23, 0.3))
export_building("assembly-bay")
