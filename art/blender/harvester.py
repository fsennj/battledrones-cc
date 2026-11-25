"""Harvester (hull only; the scrap cargo stays procedural in models.ts). See lib.py."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

R = math.pi / 2
H = [box((0.4, 0.1, 0.86), (0, 0.16, 0), GM_D, 0.02)]
for z in (-0.3, 0, 0.3):
    for s in (1, -1):
        H.append(cyl(0.11, 0.11, 0.1, 10, (s * 0.24, 0.11, z), TRACK, rot=(0, 0, R), grade=0))   # tyres
        H.append(cyl(0.05, 0.05, 0.11, 6, (s * 0.24, 0.11, z), GM_L, rot=(0, 0, R), grade=0))    # hubs
        H.append(cyl(0.015, 0.015, 0.125, 6, (s * 0.24, 0.11, z), GM_D, rot=(0, 0, R), grade=0))
H += [
    box((0.4, 0.2, 0.24), (0, 0.31, -0.29), GM, 0.035),                                     # cab
    box((0.36, 0.03, 0.2), (0, 0.425, -0.29), T_MAIN, 0.012),
    box((0.28, 0.012, 0.12), (0, 0.44, -0.29), T_LIGHT, 0.004),
    box((0.32, 0.07, 0.02), (0, 0.34, -0.415), AMBER, bevel=0, grade=0),                    # windscreen glow
    cyl(0.022, 0.022, 0.04, 6, (0.12, 0.46, -0.24), AMBER, grade=0),                        # beacon
    box((0.46, 0.08, 0.12), (0, 0.13, -0.5), HAZ_D, 0.01, rot=(-0.35, 0, 0)),               # scoop
    box((0.4, 0.03, 0.56), (0, 0.22, 0.14), GM_D, 0.005),                                    # bin floor
    box((0.42, 0.18, 0.03), (0, 0.3, -0.14), GM, 0.01),
    box((0.42, 0.18, 0.03), (0, 0.3, 0.42), GM, 0.01),
    box((0.44, 0.02, 0.045), (0, 0.398, 0.42), T_MAIN, 0.008),
]
for x in (-0.18, -0.06, 0.06, 0.18):
    H.append(box((0.055, 0.084, 0.124), (x, 0.13, -0.5), HAZ, 0.008, rot=(-0.35, 0, 0)))
for x in (-0.16, -0.08, 0, 0.08, 0.16):
    H.append(cone(0.022, 0.06, 4, (x, 0.08, -0.57), GM_D, rot=(-R - 0.3, 0, 0)))             # teeth
H += pair_box((0.03, 0.18, 0.56), (0.2, 0.3, 0.14), GM, bevel=0.01)
H += pair_box((0.045, 0.02, 0.6), (0.2, 0.398, 0.14), T_MAIN, bevel=0.008)
H += pair_box((0.012, 0.05, 0.5), (0.218, 0.32, 0.14), T_MAIN, bevel=0)
for z in (0.0, 0.14, 0.28):
    H += pair_box((0.034, 0.12, 0.02), (0.21, 0.3, z), GM_D, bevel=0.004)                    # bin ribs
hull = join(H, "hull")
export_and_preview(hull, None, "harvester", ortho=1.7)
