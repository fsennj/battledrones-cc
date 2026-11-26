"""Mortar (siege mortar: squat carriage on four big wheels, blue cradle cheeks, one huge barrel).
See lib.py for how to run. Mirrors models.ts mortar:() shape-for-shape; the game keeps the
procedural def's mount [0,0.22,0.02], muzzle (barrelTip of the 0.9-pitch barrel) and height 0.6,
so the turret geometry is built around that same pivot (join shift=MOUNT, as stinger.py)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

H = []
H.append(box((0.4, 0.1, 0.72), (0, 0.16, 0.02), GM_D, 0.02))                                   # carriage deck
for z in (-0.22, 0.24):                                                                          # four big wheels
    for s in (1, -1):
        H.append(cyl(0.13, 0.13, 0.1, 10, (s * 0.25, 0.13, z), TRACK, rot=(0, 0, math.pi / 2)))
        H.append(cyl(0.0585, 0.0585, 0.11, 6, (s * 0.25, 0.13, z), GM_L, rot=(0, 0, math.pi / 2)))
H.append(box((0.36, 0.13, 0.18), (0, 0.27, -0.26), GM, 0.03, taper=0.12))                       # front armour box
H.append(box((0.24, 0.03, 0.012), (0, 0.29, -0.352), AMBER, bevel=0, grade=0))                  # amber sight slit
H.append(box((0.3, 0.08, 0.12), (0, 0.24, 0.32), GM, 0.015))                                    # shell locker
for x in (-0.09, -0.03, 0.03, 0.09):                                                            # ready shells
    H.append(cyl(0.014, 0.014, 0.056, 6, (x, 0.28, 0.32), GM_L))
    H.append(cone(0.014, 0.028, 6, (x, 0.322, 0.32), AMBER, grade=0))
for s in (1, -1):
    H.append(light((s * 0.12, 0.25, -0.36), 0.025))                                             # carriage lights
hull = join(H, "hull")

MOUNT = (0, 0.22, 0.02)
def at(p): return (p[0] + MOUNT[0], p[1] + MOUNT[1], p[2] + MOUNT[2])
PITCH = 0.9
BARREL_AT = (0, 0.13, 0.06)                                                                     # barrel base, turret space
T = [
    box((0.28, 0.05, 0.24), at((0, 0.025, 0.02)), GM_D, 0.012),                                 # cradle base
    *pair_box((0.05, 0.17, 0.2), at((0.16, 0.09, 0.02)), T_MAIN, bevel=0.015),                  # team cradle cheeks
    barrel(at(BARREL_AT), 0.11, 0.34, PITCH, BARREL, 10),                                       # the huge fat barrel
    barrel(at(tip(BARREL_AT, 0.1, PITCH)), 0.12, 0.05, PITCH, T_MAIN, 10),                      # blue band
    barrel(at(tip(BARREL_AT, 0.22, PITCH)), 0.12, 0.05, PITCH, T_MAIN, 10),                     # blue band
    barrel(at(tip(BARREL_AT, 0.3, PITCH)), 0.128, 0.05, PITCH, GM_D, 10),                       # muzzle collar
    cyl(0.085, 0.085, 0.006, 10, at(tip(BARREL_AT, 0.345, PITCH)), TRACK, rot=(PITCH - math.pi / 2, 0, 0)),
]
turret = join(T, "turret", shift=MOUNT)                                                          # muzzle def: that same tip
export_and_preview(hull, turret, "mortar", ortho=1.3)
