"""Fab Plant (2x2 tiles). See lib.py for how to run.

Mirrors the procedural fab-plant in src/game/three/models.ts: a plinth, a long hall under a
three-tooth sawtooth roof (amber north lights, team ridge caps), a big team-slatted door on the
front apron with hazard striping, side team stripes, a chimney glowing at the throat and a
small gantry crane. Authored at map scale, ground at y = 0, centred: drawn unscaled.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

H = []
# plinth with a cap slab
H.append(box((1.92, 0.12, 1.92), (0, 0.05, 0), GM_D, 0.03, taper=0.03))
H.append(box((1.84, 0.04, 1.84), (0, 0.115, 0), GM, 0.01))
# the hall and its wall pilasters
H.append(box((1.7, 0.62, 1.3), (0, 0.41, -0.16), GM, 0.04))
for x in (-0.855, 0.855):
    for z in (-0.7, -0.16, 0.38):
        H.append(box((0.025, 0.56, 0.09), (x, 0.41, z), GM_L, 0.008))
# side window rows (the workshops are lit inside)
for x in (-0.855, 0.855):
    for z in (-0.52, -0.34, 0.0, 0.18):
        H.append(box((0.02, 0.1, 0.13), (x, 0.52, z), AMBER, bevel=0, grade=0))
# sawtooth roof: glazed amber north lights, a team ridge cap on each tooth
for i in range(3):
    z = -0.66 + i * 0.44
    H.append(box((1.66, 0.04, 0.46), (0, 0.82, z), GM_L, 0, rot=(-0.38, 0, 0)))
    H.append(box((0.04, 0.16, 0.42), (0, 0.8, z - 0.02), GM_D, 0, rot=(-0.38, 0, 0)))
    H.append(box((1.5, 0.16, 0.02), (0, 0.82, z + 0.2), AMBER, bevel=0, grade=0))
    H.append(box((1.68, 0.035, 0.07), (0, 0.905, z + 0.2), T_MAIN, 0))
# roof extract vents on the middle tooth
for x in (-0.5, 0.5):
    H.append(cyl(0.05, 0.06, 0.12, 8, (x, 0.92, -0.22), GM_D))
    H.append(cyl(0.062, 0.062, 0.02, 8, (x, 0.99, -0.22), GM_L))
# the big door: frame, team slats, amber seams
H.append(box((1.12, 0.52, 0.04), (0, 0.35, 0.505), GM_L, 0.012))
H.append(box((1.04, 0.46, 0.05), (0, 0.34, 0.51), GM_D, 0.012))
for i in range(3):
    H.append(box((1.0, 0.05, 0.02), (0, 0.2 + i * 0.13, 0.54), T_MAIN, 0))
# apron with hazard striping and kerbs
H.append(box((1.22, 0.03, 0.42), (0, 0.12, 0.73), GM_L))
for x in (-0.64, 0.64):
    H.append(box((0.05, 0.05, 0.42), (x, 0.14, 0.73), GM_D, 0.01))
for i in range(6):
    H.append(box((0.1, 0.034, 0.08), (-0.5 + i * 0.2, 0.128, 0.9), HAZ if i % 2 else HAZ_D, 0))
H.append(light((0.57, 0.6, 0.54), 0.05))
H.append(light((-0.57, 0.6, 0.54), 0.05))
# side team stripes
for x in (0.86, -0.86):
    H.append(box((0.03, 0.24, 0.94), (x, 0.46, -0.16), T_MAIN, 0.01))
# chimney stack, glowing at the throat, banded
H.append(drum(0.13, 0.1, 0.86, 8, (0.62, 1.0, -0.62), GM_D, 0.02))
H.append(torus(0.125, 0.018, (0.62, 1.18, -0.62), GM, seg=8))
H.append(drum(0.125, 0.12, 0.08, 8, (0.62, 1.32, -0.62), T_MAIN, 0.015))
H.append(cyl(0.07, 0.07, 0.02, 8, (0.62, 1.43, -0.62), EXHAUST, grade=0))
# gantry crane: leg, jib over the apron, trolley, hook and a brace
H.append(box((0.08, 0.5, 0.08), (-0.72, 1.0, 0.36), GM_D, 0.015))
H.append(box((0.12, 0.04, 0.12), (-0.72, 0.76, 0.36), GM_D, 0.01))
H.append(box((0.08, 0.08, 0.9), (-0.72, 1.24, 0.0), GM_D, 0.015))
H.append(box((0.045, 0.5, 0.045), (-0.72, 1.01, 0.27), GM_D, 0, rot=(-0.376, 0, 0)))
H.append(box((0.06, 0.12, 0.06), (-0.72, 1.15, -0.3), HAZ, 0))
H.append(box((0.012, 0.16, 0.012), (-0.72, 1.0, -0.3), GM_L, 0))
H.append(box((0.05, 0.03, 0.05), (-0.72, 0.9, -0.3), HAZ_D, 0))
# pipe run along the hall's back wall (tube's axis is game z; rot y = pi/2 lays it along x)
H.append(tube(0.03, 1.5, 6, (0.0, 0.78, -0.83), GM_D, rot=(0, math.pi / 2, 0)))
for x in (-0.6, 0.6):
    H.append(box((0.02, 0.1, 0.02), (x, 0.72, -0.83), GM_L, 0))
hull = join(H, "hull", ao=(0.3, 0.38))
export_and_preview(hull, None, "fab-plant", ortho=2.3)
