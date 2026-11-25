"""Stinger (fast light tank). See lib.py for how to run."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

H = tracks(0.235, 0.17, 0.15, 0.8)
H.append(box((0.34, 0.14, 0.72), (0, 0.2, 0.02), GM, 0.035, taper=0.16))                      # hull
H.append(box((0.32, 0.05, 0.14), (0, 0.19, -0.37), GM_D, 0.015, rot=(0.55, 0, 0)))            # glacis
H += pair_box((0.13, 0.014, 0.04), (0.055, 0.276, -0.215), T_MAIN, bevel=0, rot=(0, -0.5, 0))  # chevron
H.append(box((0.26, 0.045, 0.16), (0, 0.29, 0.27), GM_D, 0.015))                              # engine deck
H += pair_box((0.03, 0.03, 0.06), (0.08, 0.32, 0.33), BARREL, bevel=0.005)                    # exhausts
for s in (1, -1):
    H.append(box((0.02, 0.1, 0.5), (s * 0.176, 0.2, 0.02), T_DARK, 0.006))                    # side plate
    H.append(light((s * 0.12, 0.22, -0.41)))
for z in (0.2, 0.34):
    H.append(box((0.22, 0.01, 0.015), (0, 0.317, z), GM_L, 0.003))                            # deck ribs
hull = join(H, "hull")

MOUNT = (0, 0.27, 0.04)
def at(p): return (p[0] + MOUNT[0], p[1] + MOUNT[1], p[2] + MOUNT[2])
T = [
    drum(0.17, 0.14, 0.11, 7, at((0, 0.055, 0)), GM, 0.025),
    drum(0.115, 0.095, 0.03, 7, at((0, 0.125, 0.01)), T_MAIN, 0.012),
    box((0.1, 0.07, 0.07), at((0, 0.065, -0.15)), GM_D, 0.015),
    barrel(at((0, 0.065, -0.12)), 0.026, 0.34, 0.02, BARREL),
    tube(0.036, 0.06, 6, at((0, 0.07, -0.45)), GM_D),
    cyl(0.04, 0.045, 0.025, 6, at((0.045, 0.152, 0.05)), GM_D),
    light(at((-0.085, 0.13, -0.07)), 0.025),
    torus(0.04, 0.008, at((0, 0.065, -0.3)), GM_L),
    cyl(0.012, 0.012, 0.16, 6, at((0.07, 0.19, 0.12)), GM_D),                                # antenna
]
T += pair_box((0.05, 0.05, 0.16), at((0.13, 0.065, 0.03)), T_MAIN, bevel=0.012)
turret = join(T, "turret", shift=MOUNT)
export_and_preview(hull, turret, "stinger", ortho=1.7)
