"""Two bulk storage silos over a recessed scrap sorting yard."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, threshold

H = [
    box((1.94, 0.12, 1.94), (0, 0.06, 0), GM_D, bevel=0.033, taper=0.024),
    box((1.87, 0.035, 1.87), (0, 0.131, 0), CONCRETE, bevel=0.011),
    box((1.24, 0.03, 0.68), (0, 0.163, 0.468), RECESS, 0.008),
]
TANK_PAINT = 0x657475
for x in (-0.437, 0.437):
    z = -0.428
    H.extend([
        octo(0.81, 0.81, 0.08, 0.085, (x, 0.174, z), GM_D),
        drum(0.342, 0.325, 0.18, 16, (x, 0.279, z), GM_D, 0.009),
        cyl(0.33, 0.33, 0.625, 16, (x, 0.629, z), TANK_PAINT),
        cyl(0.343, 0.343, 0.027, 16, (x, 0.49, z), GM_D),
        cyl(0.346, 0.346, 0.12, 16, (x, 0.757, z), T_MAIN),
        cyl(0.344, 0.344, 0.022, 16, (x, 0.825, z), T_LIGHT),
        cyl(0.348, 0.348, 0.035, 16, (x, 0.94, z), STEEL),
        drum(0.337, 0.234, 0.112, 16, (x, 1.0, z), GM_L, 0.009),
        drum(0.231, 0.09, 0.09, 16, (x, 1.092, z), STEEL),
        cyl(0.077, 0.101, 0.047, 10, (x, 1.154, z), GM_D),
        cyl(0.073, 0.073, 0.014, 10, (x, 1.184, z), HAZ_D),
        light((x, 1.205, z), 0.039),
    ])
    # Reinforcements and the caged access ladder on the sorting side.
    for a in (math.pi / 2, math.pi * 7 / 6, math.pi * 11 / 6):
        px, pz = x + 0.325 * math.cos(a), z + 0.325 * math.sin(a)
        H.append(box((0.056, 0.376, 0.027), (px, 0.45, pz), GM_L, 0.006,
                     rot=(0, math.pi / 2 - a, 0)))
    for dx in (-0.062, 0.062):
        H.append(box((0.024, 0.78, 0.026), (x + dx, 0.593, z + 0.362), GM_D, bevel=0))
        H.append(beam((x + dx, 0.96, z + 0.36), (x + dx, 1.066, z + 0.22), 0.021, 0.019, STEEL))
    for i in range(7):
        H.append(box((0.127, 0.019, 0.027), (x, 0.276 + i * 0.108, z + 0.364), STEEL, bevel=0))
    H.append(tube(0.043, 0.105, 8, (x + 0.117, 0.36, z + 0.35), GM_D))
    H.append(tube(0.052, 0.022, 8, (x + 0.117, 0.36, z + 0.408), HAZ))

# Manifold, pressure regulator, and raised service bridge between silos.
H.extend([
    tube(0.046, 0.49, 10, (0, 0.88, -0.43), GM_D, rot=(0, math.pi / 2, 0)),
    tube(0.058, 0.058, 10, (0, 0.88, -0.43), HAZ, rot=(0, math.pi / 2, 0)),
    drum(0.055, 0.055, 0.33, 8, (0, 0.717, -0.43), GM_L),
    box((0.45, 0.07, 0.225), (0, 0.532, -0.302), GM_D, 0.012),
])
H.extend(grille(0, 0.574, -0.302, 0.42, 0.215, 5))

# The bay is open. Heavy trough walls and track guides frame loose castings on its floor.
for side in (-1, 1):
    x = 0.658 * side
    H.append(box((0.155, 0.32, 0.69), (x, 0.301, 0.471), GM, 0.015))
    H.append(box((0.162, 0.045, 0.62), (x, 0.469, 0.464), T_MAIN, 0.007))
    H.append(box((0.057, 0.05, 0.604), (side * 0.505, 0.182, 0.49), STEEL, 0.005))
    H.append(box((0.09, 0.13, 0.074), (x, 0.47, 0.754), RECESS, 0.006))
    H.append(light((x, 0.541, 0.764), 0.047))
    for z in (0.27, 0.48, 0.69):
        H.append(box((0.045, 0.23, 0.066), (side * 0.742, 0.276, z), GM_L, 0.006))
H.append(box((1.26, 0.19, 0.116), (0, 0.262, 0.187), GM_D, 0.015))
for i, (x, z, s, col) in enumerate([
    (-0.35, 0.35, 0.093, 0x987546), (-0.17, 0.44, 0.137, 0xAC8249), (0.025, 0.49, 0.103, 0x776044),
    (0.24, 0.415, 0.109, 0xB38C5A), (0.365, 0.55, 0.086, 0x8C7860), (-0.31, 0.615, 0.071, 0xA8A39A),
]):
    H.append(box((s * 1.45, s * 1.24, s * 1.66), (x, 0.205 + s * 0.52, z), col, 0.016,
                 rot=(0.25 + i * 0.18, i * 1.3, i * 0.3)))
H.extend([
    tube(0.038, 0.28, 8, (-0.21, 0.25, 0.63), STEEL, rot=(0, 0.87, 0)),
    tube(0.046, 0.035, 8, (-0.11, 0.25, 0.717), GM_D, rot=(0, 0.87, 0)),
    box((0.32, 0.032, 0.15), (0.29, 0.231, 0.67), GM_L, 0.006, rot=(0, -0.35, 0)),
])
H.extend(threshold(0, 0.173, 0.864, 1.27, 0.16, 7))

# Short belt cover over the inlet, with visible supports and an inspection grille.
for x in (-0.44, 0.44):
    H.append(beam((x, 0.197, 0.08), (x, 0.595, 0.239), 0.055, 0.062, GM_D))
    H.append(beam((x, 0.595, 0.235), (x, 0.737, -0.085), 0.055, 0.065, GM_D))
H.append(box((0.94, 0.073, 0.385), (0, 0.715, 0.078), GM_L, 0.016, rot=(0.42, 0, 0)))
H.append(box((0.94, 0.04, 0.065), (0, 0.654, 0.267), T_DARK, 0.004))
for x in (-0.861, 0.861):
    for z in (-0.768, 0.768):
        H.append(box((0.054, 0.104, 0.054), (x, 0.194, z), GM_D, 0.007))
        H.append(light((x, 0.257, z), 0.036))

join(H, "hull", ao=(0.24, 0.32))
export_building("depot")
