"""Defence Turret (building, 1x1 tile). See lib.py for how to run.

Mirrors the procedural `turret` building in src/game/three/models.ts: a low octagonal
gunmount base plate — dark tapered drum, team ring, grey race drum — and a rotating head
(tapered gun housing with a team cap, twin barrels with muzzle brakes, team side pods and an
amber sight light). Authored at map scale (1 unit = 1 tile), ground at y = 0, centred: drawn
unscaled, exactly like the procedural model it replaces.

The head is emitted as node "turret", joined with a shift of def.mount [0, 0.255, 0], so its
mesh sits in head-local coordinates around the y pivot at the mount plane (models.ts builds the
head with partB() from y = 0, and the game rotates it yaw about that pivot and offsets it by
def.mount). The barrels carry a slight fixed elevation (PITCH) so the model reads as an aiming
gun; the game only yaws the head, so this is cosmetic.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

MOUNT = 0.255           # def.mount [0, 0.255, 0]: the head pivot plane
PITCH = 0.13            # slight cosmetic barrel elevation (the game yaws only)

# --- hull: the octagonal base plate, ground at y = 0 (siteB in models.ts) ---
H = [
    drum(0.46, 0.4, 0.22, 8, (0, 0.11, 0), GM_D, 0.03, rot=(0, math.pi / 8, 0)),
    cyl(0.415, 0.415, 0.06, 8, (0, 0.19, 0), T_MAIN, rot=(0, math.pi / 8, 0)),
    drum(0.38, 0.3, 0.04, 8, (0, 0.235, 0), GM, 0.015, rot=(0, math.pi / 8, 0)),
]
hull = join(H, "hull", ao=(0.3, 0.38))

# --- head: built at world height, joined shifted down to the pivot (partB in models.ts) ---
T = [
    box((0.36, 0.17, 0.36), (0, MOUNT + 0.085, 0.03), GM, 0.03, taper=0.2),
    box((0.18, 0.02, 0.18), (0, MOUNT + 0.175, 0.05), T_MAIN, 0.01),
]
for x in (-0.065, 0.065):
    trunnion = (x, MOUNT + 0.095, -0.1)  # where the barrel meets the housing
    T.append(barrel(trunnion, 0.026, 0.4, PITCH, BARREL, seg=6))
    T.append(tube(0.037, 0.06, 6, tip(trunnion, 0.4, PITCH), GM_D, rot=(PITCH, 0, 0)))
T.extend(pair_box((0.035, 0.09, 0.22), (0.19, MOUNT + 0.085, 0.04), T_MAIN, bevel=0.01))
T.append(light((0, MOUNT + 0.17, -0.1), 0.035))
turret = join(T, "turret", shift=(0, MOUNT, 0))

export_and_preview(hull, turret, "turret", ortho=1.3)
