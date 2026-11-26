"""Fabrication hall, covered in three glazed sawtooth roof bays."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, marking, rim, threshold

H = [
    octo(1.94, 1.94, 0.115, 0.035, (0, 0.0575, 0), GM_D),
    octo(1.87, 1.88, 0.036, 0, (0, 0.129, 0), CONCRETE),
    box((1.63, 0.58, 1.3), (0, 0.437, -0.19), GM, 0.025),
    box((1.69, 0.06, 1.31), (0, 0.701, -0.18), GM_D, 0.009),
]

# The steep glazed faces meet the low side of the next roof section.
pitch = -math.atan2(0.174, 0.426)
for i in range(3):
    back = -0.84 + i * 0.43
    front = back + 0.426
    vertices = [(x, y, z) for x in (-0.826, 0.826)
                for y, z in ((0.71, back), (0.71, front), (0.912, front), (0.738, back))]
    H.append(marking(vertices, [(0, 1, 2, 3), (7, 6, 5, 4), (1, 5, 6, 2)], RECESS))
    centre = (back + front) / 2
    for j in range(4):
        x = (j - 1.5) * 0.405
        color = STEEL if (i + j) % 3 == 0 else GM_L
        H.append(box((0.398, 0.033, 0.461), (x, 0.826, centre), color, 0.006, rot=(pitch, 0, 0)))
        H.append(box((0.324, 0.108, 0.022), (x, 0.82, front + 0.009), AMBER,
                     0.004, grade=0))
        H.append(box((0.042, 0.152, 0.026), (x + 0.2, 0.818, front + 0.02), GM_D, bevel=0))
    H.append(box((1.71, 0.043, 0.057), (0, 0.914, front + 0.006), T_MAIN, 0.008))
    H.append(box((1.62, 0.011, 0.021), (0, 0.937, front + 0.006), T_LIGHT, bevel=0))

# Ribbed exterior, with the pipes and window strips above the service plinth.
for side in (-1, 1):
    x = side * 0.835
    for z in (-0.73, -0.32, 0.08, 0.4):
        H.append(box((0.061, 0.52, 0.052), (x, 0.425, z), STEEL, 0.006))
    for z in (-0.55, -0.01, 0.24):
        H.append(box((0.033, 0.21, 0.24), (x, 0.444, z), T_DARK, 0.008))
        H.append(box((0.041, 0.062, 0.20), (x, 0.543, z), RECESS, 0.003))
        H.append(box((0.045, 0.024, 0.163), (x, 0.548, z), AMBER, bevel=0, grade=0))
    H.append(tube(0.026, 1.13, 8, (side * 0.886, 0.265, -0.195), GM_D))
    for z in (-0.68, -0.23, 0.29):
        H.append(tube(0.04, 0.07, 8, (side * 0.886, 0.265, z), STEEL))

# Blast door panels and a shallow approach with guide rails and a striped edge.
H.extend([
    box((1.22, 0.53, 0.11), (0, 0.405, 0.475), GM_D, 0.02),
    box((1.09, 0.38, 0.023), (0, 0.386, 0.541), RECESS, 0.008),
    box((1.31, 0.083, 0.18), (0, 0.65, 0.476), T_MAIN, 0.018),
    box((0.91, 0.021, 0.023), (0, 0.599, 0.572), AMBER, bevel=0, grade=0),
    box((1.27, 0.025, 0.392), (0, 0.161, 0.721), GM_L, 0.005),
])
for side in (-1, 1):
    for i in range(4):
        H.append(box((0.49, 0.053, 0.022), (side * 0.257, 0.244 + i * 0.078, 0.565),
                     T_DARK if i % 3 == 0 else GM, 0.004))
    H.append(box((0.052, 0.054, 0.345), (side * 0.58, 0.184, 0.716), GM_D, 0.007))
    H.append(box((0.022, 0.011, 0.323), (side * 0.41, 0.18, 0.715), RECESS, bevel=0))
    H.append(light((side * 0.626, 0.595, 0.574), 0.052))
H.extend(threshold(0, 0.184, 0.881, 1.11, 0.07, 7))

# Furnace exhaust rises above the roof; the lip surrounds a dark opening.
for x, z, stack_top in ((0.60, -0.66, 1.412), (0.34, -0.68, 1.25)):
    H.extend([
        cyl(0.124, 0.137, 0.07, 12, (x, 0.9, z), GM_D),
        drum(0.092, 0.076, stack_top - 0.9, 12, (x, (stack_top + 0.9) / 2, z), GM, 0.005),
        cyl(0.105, 0.093, 0.052, 12, (x, stack_top - 0.082, z), T_DARK),
        cyl(0.106, 0.092, 0.029, 12, (x, stack_top - 0.019, z), RECESS),
        rim(0.066, 0.108, stack_top, STEEL, centre=(x, z), steps=12),
        cyl(0.053, 0.053, 0.006, 12, (x, stack_top - 0.003, z), EXHAUST, grade=0),
    ])
H.extend(grille(0.34, 0.897, -0.11, 0.27, 0.17, 4))

# Overhead service crane, with an open truss, trolley, cable and a suspended hook block.
x = -0.64
H.extend([
    box((0.19, 0.05, 0.19), (x, 0.908, -0.02), GM_D, 0.008),
    box((0.075, 0.36, 0.075), (x, 1.083, -0.02), GM_D, 0.01),
    box((0.10, 0.047, 0.84), (x, 1.262, 0.242), HAZ, 0.006),
    box((0.054, 0.045, 0.81), (x, 1.126, 0.242), GM_D, 0.004),
    box((0.132, 0.095, 0.12), (x, 1.105, 0.552), GM, 0.007),
    box((0.014, 0.255, 0.014), (x, 0.932, 0.552), RECESS, bevel=0),
    box((0.09, 0.045, 0.05), (x, 0.794, 0.552), HAZ, 0.006),
    light((x, 1.266, 0.672), 0.046),
])
for i in range(4):
    z = -0.158 + i * 0.2
    y0, y1 = (1.25, 1.135) if i % 2 else (1.135, 1.25)
    H.append(beam((x, y0, z), (x, y1, z + 0.2), 0.029, 0.03, GM_L))

join(H, "hull", ao=(0.24, 0.32))
export_building("fab-plant")
