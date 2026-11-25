"""Mastodon (heavy twin-barrel tank). See lib.py for how to run."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

H = tracks(0.37, 0.21, 0.21, 0.5, z=-0.27) + tracks(0.37, 0.21, 0.21, 0.5, z=0.27)
H.append(box((0.6, 0.22, 1.02), (0, 0.27, 0), GM, 0.045, taper=0.12))
H.append(box((0.56, 0.09, 0.2), (0, 0.25, -0.53), GM_D, 0.02, rot=(0.5, 0, 0)))
H += pair_box((0.04, 0.12, 0.92), (0.475, 0.22, 0), T_MAIN, bevel=0.012)
H += pair_box((0.03, 0.08, 0.8), (0.495, 0.22, 0), T_DARK, bevel=0.008)                    # skirt shadow plate
H += pair_box((0.15, 0.025, 0.2), (0.14, 0.39, -0.34), T_MAIN, bevel=0.012)
H.append(box((0.4, 0.05, 0.2), (0, 0.4, 0.38), GM_D, 0.015))
for x in (-0.12, 0, 0.12):
    H.append(box((0.07, 0.02, 0.16), (x, 0.43, 0.38), BARREL, 0.005))
for z in (0.33, 0.43):
    H.append(box((0.4, 0.012, 0.015), (0, 0.428, z), GM_L, 0.003))
for sx in (-0.2, -0.07, 0.07, 0.2):
    for sz in (-0.1, 0.1):
        H.append(cyl(0.012, 0.012, 0.015, 6, (sx, 0.385, sz), GM_L, grade=0))              # rivets
H.append(light((0.2, 0.26, -0.57)))
H.append(light((-0.2, 0.26, -0.57)))
hull = join(H, "hull")

MOUNT = (0, 0.39, 0.06)
def at(p): return (p[0] + MOUNT[0], p[1] + MOUNT[1], p[2] + MOUNT[2])
T = [
    box((0.44, 0.17, 0.46), at((0, 0.085, 0.05)), GM, 0.04, taper=0.18),
    box((0.3, 0.13, 0.09), at((0, 0.09, -0.2)), GM_D, 0.02),
    box((0.24, 0.022, 0.24), at((0, 0.18, 0.09)), T_MAIN, 0.012),
    cyl(0.06, 0.07, 0.05, 6, at((0.1, 0.205, 0.15)), GM_L),
    light(at((-0.12, 0.18, -0.12)), 0.03),
    cyl(0.012, 0.012, 0.22, 6, at((-0.17, 0.27, 0.2)), GM_D),                              # antenna
]
for x in (-0.075, 0.075):
    T.append(barrel(at((x, 0.095, -0.22)), 0.035, 0.56, 0.01, BARREL))
    T.append(tube(0.05, 0.08, 6, at((x, 0.1, -0.78)), GM_D))
    T.append(torus(0.045, 0.01, at((x, 0.097, -0.45)), GM_L))
T += pair_box((0.04, 0.09, 0.26), at((0.225, 0.08, 0.06)), T_MAIN, bevel=0.012)
turret = join(T, "turret", shift=MOUNT)
export_and_preview(hull, turret, "mastodon", ortho=2.3)
