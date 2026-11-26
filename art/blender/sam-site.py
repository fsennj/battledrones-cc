"""SAM site (surface-to-air missile site building, 1 tile). See lib.py for how to run.

Mirrors the procedural "sam-site" in src/game/three/models.ts shape for shape: a tapered
gunmetal pad with four team-corner pads and team side strips (hull), and on the yaw pivot an
octagonal turntable with elevation brackets, a pitched launcher body with team side rails and
a team top plate, and six pitched missile tubes with red nose cones (turret). Authored at map
scale (1 unit = 1 tile), ground at y = 0, centred.

Node split matches the loader: "hull" in map space, "turret" authored LOCAL to the game yaw
pivot at mount = [0, 0.18, 0] (models.ts keeps its procedural mount), so the turret numbers
here are exactly the turret numbers in the TS builder.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from building_detail import CONCRETE, RECESS, STEEL, export_building, threshold

WHITE = 0xD6DBE1     # models.ts WHITE (missile tubes)
NOSE = 0xC8402E      # models.ts nose-cone red

PITCH = 0.34         # launcher elevation, same as the TS builder

# ---------------------------------------------------------------- hull ----
H = []
H.append(octo(0.945, 0.945, 0.13, 0.045, (0, 0.065, 0), GM_D))
H.append(octo(0.879, 0.879, 0.039, 0.025, (0, 0.147, 0), CONCRETE))
for x in (-0.277, 0.277):                                                          # corner team pads
    for z in (-0.277, 0.277):
        H.append(octo(0.153, 0.153, 0.047, 0.11, (x, 0.18, z), T_MAIN))
        H.append(light((x, 0.205, z), 0.03))
H.extend(pair_box((0.03, 0.05, 0.41), (0.435, 0.105, 0), T_DARK, bevel=0.006))
H.extend(threshold(0, 0.179, 0.365, 0.45, 0.074, 4))
join(H, "hull", ao=(0.3, 0.38))

# -------------------------------------------------------------- turret ----
# local to the yaw pivot (0, 0.18, 0): identical coordinates to the TS turret block
T = []
T.append(drum(0.252, 0.216, 0.069, 12, (0, 0.035, 0), GM, 0.013))
T.append(cyl(0.21, 0.22, 0.018, 12, (0, 0.065, 0), STEEL))
T.extend(pair_box((0.057, 0.22, 0.148), (0.213, 0.171, 0.043), GM_D, bevel=0.008))
for x in (-0.245, 0.245):
    T.append(cyl(0.066, 0.066, 0.02, 10, (x, 0.216, 0.046), STEEL, rot=(0, 0, math.pi / 2)))
    T.append(cyl(0.041, 0.041, 0.023, 10, (x * 1.04, 0.216, 0.046), T_DARK, rot=(0, 0, math.pi / 2)))
T.append(box((0.352, 0.192, 0.31), (0, 0.258, 0.06), GM_D, 0.02, rot=(PITCH, 0, 0)))
T.extend(pair_box((0.026, 0.113, 0.37), (0.184, 0.275, -0.016), T_MAIN, bevel=0.004, rot=(PITCH, 0, 0)))
T.append(box((0.317, 0.028, 0.234), (0, 0.36, 0.04), T_MAIN, 0.005, rot=(PITCH, 0, 0)))
T.append(box((0.277, 0.026, 0.043), (0, 0.393, -0.046), RECESS, 0.004, rot=(PITCH, 0, 0)))
T.append(light((0, 0.418, -0.043), 0.032))
for x in (-0.11, 0, 0.11):                       # six missiles, two staggered rows
    for y in (0.21, 0.3):
        base = (x, y, 0.12)
        T.append(barrel(base, 0.031, 0.42, PITCH, WHITE, 8))
        T.append(tube(0.038, 0.07, 8, tip(base, 0.279, PITCH), GM_L, rot=(PITCH, 0, 0)))
        tp = tip(base, 0.42, PITCH)
        T.append(cone(0.032, 0.07, 6, (tp[0], tp[1] + math.sin(PITCH) * 0.035,
                                       tp[2] - math.cos(PITCH) * 0.035), NOSE,
                      rot=(PITCH - math.pi / 2, 0, 0)))
join(T, "turret")

export_building("sam-site")
