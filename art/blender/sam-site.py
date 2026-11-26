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

WHITE = 0xD6DBE1     # models.ts WHITE (missile tubes)
NOSE = 0xC8402E      # models.ts nose-cone red

PITCH = 0.34         # launcher elevation, same as the TS builder

# ---------------------------------------------------------------- hull ----
H = []
H.append(box((0.86, 0.18, 0.86), (0, 0.09, 0), GM_D, 0.025, taper=0.06))          # pad
for x in (-0.34, 0.34):                                                            # corner team pads
    for z in (-0.34, 0.34):
        H.append(box((0.14, 0.03, 0.14), (x, 0.19, z), T_MAIN, 0.01))
H.extend(pair_box((0.03, 0.06, 0.4), (0.43, 0.1, 0), T_MAIN, bevel=0.006))        # side strips
hull = join(H, "hull", ao=(0.3, 0.38))

# -------------------------------------------------------------- turret ----
# local to the yaw pivot (0, 0.18, 0): identical coordinates to the TS turret block
T = []
T.append(drum(0.25, 0.22, 0.08, 8, (0, 0.04, 0), GM, 0.015))                       # turntable
T.extend(pair_box((0.04, 0.22, 0.12), (0.21, 0.17, 0.02), GM_D, bevel=0.008))     # elevation brackets
T.append(box((0.36, 0.2, 0.42), (0, 0.26, -0.02), GM, 0.02, rot=(PITCH, 0, 0)))   # launcher body
T.extend(pair_box((0.02, 0.1, 0.36), (0.185, 0.27, -0.02), T_MAIN, bevel=0.004, rot=(PITCH, 0, 0)))
T.append(box((0.3, 0.02, 0.26), (0, 0.364, 0.02), T_MAIN, 0.004, rot=(PITCH, 0, 0)))  # top plate
for x in (-0.11, 0, 0.11):                       # six missiles, two staggered rows
    for y in (0.21, 0.3):
        base = (x, y, 0.12)
        T.append(barrel(base, 0.032, 0.42, PITCH, WHITE, 6))
        tp = tip(base, 0.42, PITCH)
        T.append(cone(0.032, 0.07, 6, (tp[0], tp[1] + math.sin(PITCH) * 0.035,
                                       tp[2] - math.cos(PITCH) * 0.035), NOSE,
                      rot=(PITCH - math.pi / 2, 0, 0)))
turret = join(T, "turret")

export_and_preview(hull, turret, "sam-site", ortho=1.35)
