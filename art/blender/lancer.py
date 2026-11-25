"""Lancer (hover tank with a laser lance). See lib.py for how to run."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

H = [
    octo(0.66, 0.97, 0.022, 0, (0, 0.03, 0), AMBER, grade=0),                              # lift-field glow
    octo(0.58, 0.88, 0.09, 0.04, (0, 0.08, 0), TRACK),                                     # skirt
    box((0.56, 0.13, 0.82), (0, 0.19, 0.02), GM, 0.035, taper=0.14),
    box((0.46, 0.05, 0.16), (0, 0.19, -0.38), GM_D, 0.015, rot=(0.5, 0, 0)),
    box((0.3, 0.02, 0.1), (0, 0.265, 0.34), T_MAIN, 0.008),
    light((0.15, 0.2, -0.47)), light((-0.15, 0.2, -0.47)),
]
H += pair_box((0.1, 0.02, 0.5), (0.15, 0.265, 0.02), T_MAIN, bevel=0.008)
H += pair_box((0.02, 0.05, 0.6), (0.285, 0.19, 0), T_DARK, bevel=0.005)                    # flank plate
for s in (1, -1):
    H.append(box((0.11, 0.04, 0.012), (s * 0.12, 0.19, 0.434), EXHAUST, bevel=0, grade=0))
    for z in (-0.2, 0, 0.2):
        H.append(box((0.012, 0.025, 0.08), (s * 0.282, 0.19, z), 0x15171A, 0.003))
hull = join(H, "hull")

MOUNT = (0, 0.255, 0.04)
def at(p): return (p[0] + MOUNT[0], p[1] + MOUNT[1], p[2] + MOUNT[2])
T = [
    drum(0.17, 0.13, 0.09, 6, at((0, 0.045, 0.02)), GM, 0.02),
    drum(0.11, 0.09, 0.025, 6, at((0, 0.1, 0.04)), T_MAIN, 0.01),
    box((0.1, 0.07, 0.1), at((0, 0.05, -0.13)), GM_D, 0.015),
    tube(0.026, 0.46, 6, at((0, 0.05, -0.33)), BARREL),
    tube(0.038, 0.04, 8, at((0, 0.05, -0.57)), GM_D),
    sphere(0.03, at((0, 0.05, -0.595)), AMBER),
    light(at((-0.08, 0.1, -0.05)), 0.022),
]
for z in (-0.238, -0.33, -0.422):
    T.append(torus(0.042, 0.013, at((0, 0.05, z)), GM_L))
T += pair_box((0.03, 0.06, 0.1), at((0.09, 0.06, 0.13)), GM_D, bevel=0.008)
turret = join(T, "turret", shift=MOUNT)
export_and_preview(hull, turret, "lancer", ortho=1.9)
