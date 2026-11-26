"""Export the airfield and its independent, yawing radar installation."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bpy

import lib as a
from building_detail import CONCRETE, RECESS, STEEL, beam, export_building, grille, marking, rim, threshold


OFF_WHITE = 0xD1D4CB


def airpad():
    # The markings are flush so the aircraft can hover and land over an unobstructed pad.
    hull = [
        a.box((1.95, 0.125, 1.95), (0, 0.0625, 0), a.GM_D, bevel=0.033, taper=0.026),
        a.box((1.895, 0.044, 1.895), (0, 0.139, 0), CONCRETE, bevel=0.012),
        a.cyl(0.795, 0.845, 0.048, 40, (0, 0.175, 0), a.GM_D, bevel=0.008),
        a.cyl(0.771, 0.785, 0.014, 40, (0, 0.195, 0), 0x51585B),
        rim(0.765, 0.79, 0.204, STEEL, steps=40),
        rim(0.605, 0.623, 0.204, a.T_DARK, steps=40),
        a.box((0.328, 0.01, 0.064), (0, 0.207, 0), OFF_WHITE, bevel=0),
    ]
    for x in (-0.148, 0.148):
        hull.append(a.box((0.061, 0.01, 0.468), (x, 0.207, 0), OFF_WHITE, bevel=0))
        for side in (-1, 1):
            hull.append(a.box((0.194, 0.006, 0.027), (x * 1.85, 0.207, side * 0.335),
                              a.GM_L, bevel=0))
    for i in range(8):
        angle = math.tau * (i + 0.5) / 8
        hull.append(rim(0.627, 0.696, 0.206, a.T_MAIN, start=angle - 0.32, end=angle + 0.32, steps=5))
        hull.append(rim(0.626, 0.642, 0.207, a.T_LIGHT, start=angle - 0.29, end=angle + 0.29, steps=5))
        x, z = math.cos(angle), math.sin(angle)
        hull.append(a.box((0.074, 0.022, 0.058), (x * 0.739, 0.21, z * 0.739), RECESS, bevel=0.006,
                          rot=(0, -angle - math.pi / 2, 0)))
        hull.append(a.light((x * 0.742, 0.228, z * 0.742), 0.031))
    for z in (-0.804, 0.834):
        hull.extend(threshold(0, 0.168, z, 0.54, 0.095, 4))
    for side in (-1, 1):
        for z in (-0.67, 0.67):
            hull.append(a.box((0.125, 0.047, 0.117), (side * 0.854, 0.161, z), a.GM_D, bevel=0.009))
            hull.append(a.light((side * 0.854, 0.197, z), 0.048))
        hull.append(a.box((0.115, 0.007, 0.51), (side * 0.872, 0.164, 0.302), a.T_DARK,
                          bevel=0))
        for z in (0.103, 0.298, 0.493):
            hull.append(a.box((0.055, 0.007, 0.052), (side * 0.873, 0.17, z), OFF_WHITE,
                              bevel=0))
    for z in (-0.53, 0.53):
        side = math.copysign(1, z)
        hull.append(marking([(-0.081, 0.204, z - side * 0.044), (0.081, 0.204, z - side * 0.044),
                             (0, 0.204, z + side * 0.064)], [(2, 1, 0) if side > 0 else (0, 1, 2)],
                            OFF_WHITE))

    # The cabin projects over the tower footing; its angled glass wraps around the landing zone.
    tx, tz = 0.666, -0.667
    hull.extend([
        a.box((0.36, 0.07, 0.36), (tx, 0.19, tz), RECESS, bevel=0.013),
        a.box((0.28, 0.55, 0.28), (tx, 0.486, tz), a.GM, taper=0.1, bevel=0.014),
        a.box((0.42, 0.069, 0.42), (tx, 0.722, tz), STEEL, taper=0.16, bevel=0.013),
        a.box((0.356, 0.172, 0.356), (tx, 0.812, tz), RECESS, bevel=0.012),
        a.box((0.423, 0.091, 0.423), (tx, 0.831, tz), a.AMBER, bevel=0.01, grade=0),
        a.box((0.469, 0.055, 0.469), (tx, 0.904, tz), a.T_MAIN, taper=0.19, bevel=0.013),
        a.box((0.36, 0.017, 0.36), (tx, 0.936, tz), a.GM_L, taper=0.12, bevel=0.007),
        a.cyl(0.035, 0.044, 0.04, 8, (tx + 0.102, 0.948, tz - 0.113), a.GM_D),
        a.cyl(0.011, 0.017, 0.27, 8, (tx + 0.102, 1.093, tz - 0.113), STEEL),
        a.light((tx + 0.102, 1.239, tz - 0.113), 0.037),
    ])
    for x in (tx - 0.195, tx, tx + 0.195):
        hull.append(a.box((0.027, 0.121, 0.03), (x, 0.824, tz + 0.215), a.GM_D, bevel=0.004))
    for z in (tz - 0.165, tz, tz + 0.165):
        hull.append(a.box((0.029, 0.121, 0.025), (tx - 0.215, 0.824, z), a.GM_D, bevel=0.004))
    for x in (tx - 0.112, tx - 0.015):
        hull.append(a.box((0.017, 0.45, 0.024), (x, 0.43, tz + 0.147), a.GM_D, bevel=0))
    for y in (0.246, 0.322, 0.398, 0.474, 0.55, 0.626):
        hull.append(a.box((0.1, 0.014, 0.02), (tx - 0.064, y, tz + 0.157), STEEL, bevel=0))
    hull.append(beam((tx, 0.571, tz + 0.13), (tx, 0.707, tz + 0.212), 0.047, 0.038, a.GM_D))
    hull.extend(grille(tx - 0.064, 0.955, tz, 0.135, 0.145, 3))

    # Service tanks and the transfer hose sit in the opposite corner.
    hull.append(a.box((0.383, 0.05, 0.421), (-0.716, 0.186, -0.663), a.GM_D, bevel=0.009))
    for z in (-0.788, -0.569):
        hull.append(a.tube(0.082, 0.305, 12, (-0.735, 0.275, z), a.GM_L, rot=(0, math.pi / 2, 0)))
        for x in (-0.808, -0.669):
            hull.append(a.tube(0.086, 0.037, 12, (x, 0.275, z), a.T_MAIN, rot=(0, math.pi / 2, 0)))
        hull.append(a.tube(0.035, 0.061, 8, (-0.566, 0.275, z), a.GM_D, rot=(0, math.pi / 2, 0)))
    hull.append(a.tube(0.021, 0.22, 8, (-0.544, 0.275, -0.678), a.GM_D))
    hull.append(a.cyl(0.04, 0.035, 0.024, 8, (-0.544, 0.291, -0.675), a.HAZ))
    a.join(hull, "hull", ao=(0.2, 0.28))


def radar():
    hull = [
        a.octo(0.91, 0.91, 0.147, 0.045, (0, 0.074, 0), a.GM_D),
        a.octo(0.833, 0.833, 0.037, 0, (0, 0.159, 0), CONCRETE),
        a.drum(0.252, 0.207, 0.062, 12, (0, 0.187, 0), a.GM_L, bevel=0.009),
        a.cyl(0.187, 0.207, 0.028, 12, (0, 0.218, 0), RECESS),
    ]
    for x in (-0.27, 0.27):
        for z in (-0.27, 0.27):
            hull.append(a.box((0.131, 0.05, 0.131), (x, 0.178, z), a.T_MAIN, bevel=0.008))
            hull.append(a.light((x, 0.209, z), 0.031))
    hull.extend(grille(0, 0.182, 0.327, 0.272, 0.12, 3))
    a.join(hull, "hull", ao=(0.2, 0.28))

    # The mesh uses the game's existing yaw pivot at y = 0.20.
    tilt = (0.35, 0, 0)
    head = [
        a.drum(0.132, 0.116, 0.062, 10, (0, 0.036, 0), a.GM_D, bevel=0.008),
        a.drum(0.081, 0.052, 0.38, 10, (0, 0.236, 0), a.GM_L, bevel=0.009),
        a.box((0.126, 0.146, 0.139), (0, 0.408, 0.043), RECESS, bevel=0.011),
        a.box((0.467, 0.187, 0.078), (0, 0.528, -0.042), a.GM_D, bevel=0.017, rot=tilt),
        a.box((0.412, 0.134, 0.058), (0, 0.53, -0.089), 0x807D66, bevel=0.009, rot=tilt),
        a.box((0.393, 0.021, 0.031), (0, 0.624, -0.087), a.T_LIGHT, bevel=0.003, rot=tilt),
        a.light((0, 0.657, -0.075), 0.027),
    ]
    for side in (-1, 1):
        wing = (tilt[0], side * 0.45, 0)
        head.append(a.box((0.143, 0.174, 0.071), (side * 0.255, 0.53, -0.093), a.T_MAIN,
                          bevel=0.011, rot=wing))
        head.append(a.box((0.101, 0.121, 0.024), (side * 0.259, 0.527, -0.135), a.T_DARK,
                          bevel=0.006, rot=wing))
        head.append(a.light((side * 0.31, 0.574, -0.157), 0.024))
        head.append(beam((0, 0.337, 0.012), (side * 0.183, 0.473, 0.026), 0.032, 0.034, a.GM_D))
    for x in (-0.155, -0.103, -0.051, 0, 0.051, 0.103, 0.155):
        head.append(a.box((0.016, 0.11, 0.013), (x, 0.529, -0.124), RECESS, bevel=0, rot=tilt))
    a.join(head, "turret")


for model in (airpad, radar):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    model()
    export_building(model.__name__)
