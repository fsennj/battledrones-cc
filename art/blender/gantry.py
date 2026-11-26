"""Static scaffold and assembly cradle for the Gantry's in-game articulated machinery."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, rim, threshold

H = [
    octo(2.965, 2.965, 0.126, 0.027, (0, 0.063, 0), GM_D),
    octo(2.881, 2.881, 0.043, 0, (0, 0.138, 0), CONCRETE),
    box((2.31, 0.027, 2.79), (0, 0.16, 0), GM, 0.009),
    box((1.574, 0.095, 1.41), (0, 0.217, 0), GM_L, 0.018),
    box((1.424, 0.027, 1.22), (0, 0.272, 0), RECESS, 0.01),
]
for z in (-1.295, 1.295):
    H.extend(threshold(0, 0.179, z, 1.98, 0.165, 11))
    H.extend(grille(0, 0.178, z * 0.701, 1.255, 0.132, 4))

# Fixtures cradle the Goliath at the same height as the construction stages.
for side in (-1, 1):
    x = side * 0.407
    H.append(box((0.531, 0.052, 0.79), (x, 0.292, -0.034), GM_D, 0.009))
    H.append(box((0.446, 0.02, 0.688), (x, 0.324, -0.034), GM, 0.006))
    for z in (-0.365, 0.27):
        H.append(box((0.12, 0.054, 0.091), (x + side * 0.213, 0.346, z), STEEL, 0.006))
        H.append(box((0.091, 0.031, 0.065), (x + side * 0.214, 0.377, z), HAZ, 0.003))
    H.append(box((0.052, 0.062, 1.39), (side * 0.777, 0.222, 0), T_MAIN, 0.009))
    H.append(box((0.023, 0.018, 1.31), (side * 0.794, 0.255, 0), T_LIGHT, 0.003))

# Open lattice towers keep the Goliath and welding arms visible at gameplay zoom.
for side in (-1, 1):
    x, inner, outer = (side * v for v in (1.291, 1.194, 1.393))
    H.append(box((0.362, 0.171, 1.995), (x, 0.237, 0), GM, 0.023))
    for z in (-0.868, 0.868):
        H.append(box((0.335, 0.086, 0.263), (x, 0.346, z), T_DARK, 0.01))
        H.append(box((0.27, 0.074, 0.186), (x, 0.412, z), GM_L, 0.008))
        for post in (inner, outer):
            H.append(box((0.065, 2.628, 0.067), (post, 1.734, z), GM_D, 0.006))
    for i in range(6):
        y = 0.525 + i * 0.489
        for post in (inner, outer):
            H.append(box((0.039, 0.047, 1.752), (post, y, 0), STEEL if i % 2 else GM, 0.004))
            for z in (-0.88, 0.88):
                H.append(box((0.06, 0.083, 0.081), (post, y, z), GM_D, 0.005))
        for z in (-0.871, 0.871):
            H.append(box((0.256, 0.05, 0.045), (x, y, z), GM_L, 0.004))
        if i < 5:
            z0, z1 = (-0.857, 0.857) if i % 2 else (0.857, -0.857)
            H.append(beam((outer, y, z0), (outer, y + 0.489, z1), 0.043, 0.036, GM_D))
    for y in (1.271, 2.348):
        H.append(box((0.338, 0.036, 1.827), (x, y, 0), GM_L, 0.008))
        H.append(box((0.037, 0.028, 1.66), (inner, y + 0.02, 0), HAZ, 0.004))
        H.append(box((0.028, 0.028, 1.66), (outer, y + 0.02, 0), T_DARK, 0.004))
        H.append(box((0.32, 0.042, 0.212), (x, y - 0.035, 0.849), T_MAIN, 0.008))
    H.append(box((0.336, 0.104, 1.876), (x, 3.095, 0), T_MAIN, 0.014))
    H.append(box((0.29, 0.016, 1.798), (x, 3.157, 0), STEEL, 0.006))
    H.append(box((0.24, 0.065, 0.098), (x, 3.074, 0.95), T_DARK, 0.005))
    H.append(cyl(0.094, 0.115, 0.048, 10, (side * 1.2, 3.032, 0), GM_D))
    for z in (-0.88, 0.88):
        # A blinking light at y = 3.2 is painted by the game's overlay.
        H.append(box((0.082, 0.052, 0.098), (side * 1.4, 3.17, z), RECESS, 0.006))
    for z in (-0.525, 0.49):
        H.append(box((0.104, 0.1, 0.12), (x, 2.935, z), GM_D, 0.006))
        H.append(box((0.059, 0.053, 0.083), (inner - side * 0.016, 2.92, z),
                     AMBER, bevel=0, grade=0))

# Crane cab and bearing meet the animated jib root exactly at (1.3, 3.84, -0.72).
H.extend([
    cyl(0.112, 0.132, 0.06, 12, (1.3, 3.197, -0.72), GM_D, bevel=0.008),
    box((0.16, 0.52, 0.16), (1.3, 3.47, -0.72), RECESS, 0.012),
    box((0.266, 0.15, 0.277), (1.3, 3.698, -0.72), HAZ, 0.02),
    box((0.195, 0.062, 0.015), (1.3, 3.702, -0.571), AMBER, bevel=0, grade=0),
    box((0.018, 0.058, 0.189), (1.16, 3.702, -0.72), AMBER, bevel=0, grade=0),
    cyl(0.085, 0.1, 0.093, 10, (1.3, 3.797, -0.72), GM_D, bevel=0.007),
    box((0.455, 0.063, 0.411), (0.927, 0.199, -1.076), GM_D, 0.01),
    box((0.363, 0.193, 0.322), (-0.94, 0.269, 1.067), GM, 0.012),
    box((0.385, 0.05, 0.341), (-0.94, 0.378, 1.067), T_DARK, 0.009),
])
for i in range(3):
    H.append(box((0.394, 0.049, 0.348), (0.938, 0.26 + i * 0.055, -1.071),
                 T_MAIN if i == 2 else GM_L, 0.008, rot=(0, 0.08 * i, 0)))
for x in (-1.38, 1.38):
    for z in (-1.128, 1.128):
        H.append(box((0.08, 0.063, 0.092), (x, 0.172, z), GM_D, 0.007))
        H.append(light((x, 0.213, z), 0.05))
for x in (-0.145, 0.145):
    H.append(rim(0.086, 0.11, 0.174, T_DARK, centre=(x, 1.104), steps=12))

join(H, "hull", ao=(0.235, 0.32))
export_building("gantry")
