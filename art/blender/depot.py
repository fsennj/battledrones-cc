"""Depot (2x2 tiles). See lib.py for how to run.

Mirrors the procedural depot in src/game/three/models.ts: a plinth, two storage tanks with
team bands and cone caps behind, an open scrap bay in front (dark interior, heap of scrap,
team band and hazard slats on the face, a tilted canopy over the bay) and yard lamps.
Authored at map scale, ground at y = 0, centred: drawn unscaled.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

H = []
# plinth with a cap slab and kerb steps at the bay mouth
H.append(box((1.92, 0.12, 1.92), (0, 0.06, 0), GM_D, 0.03, taper=0.03))
H.append(box((1.84, 0.04, 1.84), (0, 0.13, 0), GM, 0.01))
# the two storage tanks: skirt, shell, team band, cap, beacon; ladder and valve work
for x in (-0.46, 0.46):
    H.append(cyl(0.335, 0.335, 0.05, 14, (x, 0.3, -0.42), GM_D))
    H.append(cyl(0.32, 0.32, 0.9, 14, (x, 0.57, -0.42), GM))
    H.append(cyl(0.335, 0.335, 0.12, 14, (x, 0.78, -0.42), T_MAIN))
    H.append(cone(0.33, 0.24, 14, (x, 1.14, -0.42), GM_L))
    H.append(box((0.02, 0.7, 0.06), (x, 0.62, -0.085), GM_L, 0))               # ladder on the shell face
    for y in (0.42, 0.62, 0.82):
        H.append(box((0.05, 0.012, 0.02), (x, y, -0.085), GM_D, 0))            # ladder rungs
    H.append(cyl(0.035, 0.035, 0.1, 8, (x, 0.5, -0.1), GM_D, rot=(math.pi / 2, 0, 0)))  # valve stub
    H.append(sphere(0.045, (x, 0.5, -0.04), HAZ, w=6, h=4))                    # valve wheel
    H.append(light((x, 1.27, -0.42), 0.04))
# pipe run between the tanks (along x) and a drop from it toward the bay (tube axis is game z)
H.append(tube(0.028, 0.92, 6, (0.0, 0.36, -0.42), GM_D, rot=(0, math.pi / 2, 0)))
H.append(tube(0.028, 0.3, 6, (0.0, 0.45, -0.14), GM_D))
# the bay: wall block, dark interior, scrap heap, front band and hazard slats
H.append(box((1.32, 0.32, 0.62), (0, 0.28, 0.46), GM, 0.03))
H.append(box((1.12, 0.02, 0.42), (0, 0.445, 0.46), 0x121315, 0))
for i, (x, z, s, col) in enumerate([
    (-0.36, 0.07, 0.07, 0x8a6a3a), (-0.14, 0.52, 0.08, 0xb08a4a), (0.12, 0.42, 0.07, 0x6e5a40),
    (0.34, 0.54, 0.06, 0x9a7a44), (0.0, 0.46, 0.09, 0xc9a65a), (-0.3, 0.58, 0.05, 0x7a6448),
]):
    H.append(box((s * 2, s * 1.2, s * 1.8), (x, 0.44, z), col, 0, rot=(i * 0.5, i * 1.3, i * 0.3)))
H.append(box((1.22, 0.05, 0.02), (0, 0.3, 0.775), T_MAIN, 0))
for i in range(7):
    H.append(box((0.16, 0.03, 0.03), (-0.54 + i * 0.18, 0.445, 0.77), HAZ if i % 2 else HAZ_D, 0))
# the tilted canopy over the bay on its two posts
H.append(box((0.18, 0.06, 0.74), (0, 0.66, 0.02), GM_D, 0.015, rot=(-0.5, 0, 0)))
for x in (-0.62, 0.62):
    H.append(box((0.04, 0.42, 0.04), (x, 0.5, 0.16), GM_D, 0))
    H.append(light((x, 0.47, 0.76), 0.05))
# yard corner lamps
for x in (-0.86, 0.86):
    for z in (-0.86, 0.86):
        H.append(box((0.05, 0.14, 0.05), (x, 0.2, z), GM_D, 0.008))
        H.append(light((x, 0.29, z), 0.035))
hull = join(H, "hull", ao=(0.3, 0.38))
export_and_preview(hull, None, "depot", ortho=2.3)
