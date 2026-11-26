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
from building_detail import CONCRETE, RECESS, STEEL, export_building, rim

MOUNT = 0.255           # def.mount [0, 0.255, 0]: the head pivot plane
PITCH = 0.13            # slight cosmetic barrel elevation (the game yaws only)

# --- hull: the octagonal base plate, ground at y = 0 (siteB in models.ts) ---
H = [
    octo(0.945, 0.945, 0.077, 0.035, (0, 0.0385, 0), GM_D),
    octo(0.903, 0.903, 0.03, 0.02, (0, 0.083, 0), CONCRETE),
    drum(0.411, 0.365, 0.118, 12, (0, 0.144, 0), GM_D, 0.016),
    cyl(0.375, 0.393, 0.064, 12, (0, 0.189, 0), T_MAIN),
    drum(0.344, 0.253, 0.05, 12, (0, 0.23, 0), STEEL, 0.01),
    rim(0.284, 0.315, 0.222, T_DARK, steps=24),
]
for a in (math.pi / 4, math.pi * 3 / 4, math.pi * 5 / 4, math.pi * 7 / 4):
    x, z = math.cos(a) * 0.418, math.sin(a) * 0.418
    H.append(cyl(0.041, 0.05, 0.035, 6, (x, 0.112, z), GM_L))
    H.append(light((x, 0.135, z), 0.027))
join(H, "hull", ao=(0.3, 0.38))

# --- head: built at world height, joined shifted down to the pivot (partB in models.ts) ---
T = [
    cyl(0.225, 0.224, 0.035, 12, (0, MOUNT + 0.018, 0), RECESS),
    box((0.413, 0.17, 0.356), (0, MOUNT + 0.094, 0.026), GM, 0.025, taper=0.12),
    box((0.332, 0.039, 0.267), (0, MOUNT + 0.176, 0.03), T_MAIN, 0.012, taper=0.13),
    box((0.122, 0.026, 0.168), (0, MOUNT + 0.205, 0.05), T_DARK, 0.006),
    box((0.113, 0.062, 0.06), (0, MOUNT + 0.17, -0.127), RECESS, 0.007),
    box((0.069, 0.031, 0.012), (0, MOUNT + 0.18, -0.16), AMBER, bevel=0, grade=0),
]
for x in (-0.065, 0.065):
    trunnion = (x, MOUNT + 0.095, -0.1)  # where the barrel meets the housing
    T.append(barrel(trunnion, 0.027, 0.404, PITCH, BARREL, seg=8))
    T.append(tube(0.051, 0.115, 8, tip(trunnion, 0.061, PITCH), STEEL, rot=(PITCH, 0, 0)))
    T.append(tube(0.043, 0.049, 8, tip(trunnion, 0.165, PITCH), GM_D, rot=(PITCH, 0, 0)))
    T.append(tube(0.041, 0.075, 8, tip(trunnion, 0.394, PITCH), GM_L, rot=(PITCH, 0, 0)))
    T.append(tube(0.023, 0.007, 8, tip(trunnion, 0.434, PITCH), RECESS, rot=(PITCH, 0, 0)))
T.extend(pair_box((0.058, 0.109, 0.258), (0.201, MOUNT + 0.093, 0.044), T_DARK, bevel=0.01))
T.extend(pair_box((0.036, 0.049, 0.142), (0.23, MOUNT + 0.104, 0.039), T_MAIN, bevel=0.005))
join(T, "turret", shift=(0, MOUNT, 0))

export_building("turret")
