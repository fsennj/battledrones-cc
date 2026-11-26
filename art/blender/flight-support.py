"""Export the Airpad and Radar. Run Blender with -- /absolute/output/path."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib as a

import bpy


OFF_WHITE = 0xCED1CD


def airpad():
    # Two-tile footprint with a clear landing disc, emergency ladders and an elevated control cabin.
    hull = [a.box((1.94, 0.14, 1.94), (0, 0.07, 0), a.GM_D, taper=0.045, bevel=0.034),
            a.cyl(0.78, 0.81, 0.043, 32, (0, 0.152, 0), a.GM, bevel=0.006)]
    for side in (-1, 1):
        hull.append(a.box((0.049, 0.012, 0.44), (side * 0.145, 0.18, 0), OFF_WHITE, bevel=0.003))
        for z in (-0.72, 0.72):
            hull.append(a.box((0.12, 0.033, 0.12), (side * 0.86, 0.154, z), a.GM_L, bevel=0.009))
            hull.append(a.light((side * 0.86, 0.181, z), 0.038))
    hull.append(a.box((0.30, 0.012, 0.051), (0, 0.18, 0), OFF_WHITE, bevel=0.003))
    for i in range(12):
        angle = math.tau * i / 12
        x, z = math.cos(angle), math.sin(angle)
        hull.append(a.box((0.25, 0.009, 0.046), (x * 0.655, 0.178, z * 0.655), a.T_MAIN,
                          bevel=0.003, rot=(0, -angle - math.pi / 2, 0)))
        hull.append(a.light((x * 0.755, 0.182, z * 0.755), 0.025, OFF_WHITE))
    tx, tz = 0.70, -0.70
    hull.extend([
        a.box((0.29, 0.62, 0.29), (tx, 0.44, tz), a.GM, taper=0.12, bevel=0.015),
        a.box((0.44, 0.14, 0.44), (tx, 0.81, tz), a.GM_D, taper=0.12, bevel=0.018),
        a.box((0.414, 0.072, 0.414), (tx, 0.868, tz), 0xAD762C, bevel=0.012),
        a.box((0.45, 0.036, 0.45), (tx, 0.925, tz), a.T_MAIN, taper=0.18, bevel=0.012),
        a.tube(0.012, 0.28, 8, (tx + 0.11, 1.073, tz - 0.13), a.GM_L, rot=(math.pi / 2, 0, 0)),
        a.light((tx + 0.11, 1.225, tz - 0.13), 0.021),
    ])
    for y in (0.24, 0.34, 0.44, 0.54, 0.64):
        hull.append(a.box((0.105, 0.015, 0.025), (tx - 0.054, y, tz + 0.154), a.GM_L, bevel=0.003))
    for z in (-0.77, -0.52):
        hull.append(a.tube(0.091, 0.3, 12, (-0.74, 0.238, z), a.GM_L, rot=(0, math.pi / 2, 0)))
        hull.append(a.tube(0.094, 0.047, 12, (-0.74, 0.238, z), a.T_MAIN, rot=(0, math.pi / 2, 0)))
    a.join(hull, "hull")


def radar():
    hull = [a.box((0.87, 0.18, 0.87), (0, 0.09, 0), a.GM_D, taper=0.07, bevel=0.021),
            a.drum(0.25, 0.19, 0.07, 12, (0, 0.204, 0), a.GM_L, bevel=0.009)]
    for x in (-0.34, 0.34):
        for z in (-0.34, 0.34):
            hull.append(a.box((0.135, 0.044, 0.135), (x, 0.169, z), a.T_MAIN, bevel=0.007))
            hull.append(a.light((x, 0.199, z), 0.027))
    a.join(hull, "hull")

    # All coordinates are local to the existing yaw pivot at y = 0.20.
    head = [a.drum(0.084, 0.058, 0.41, 10, (0, 0.205, 0), a.GM, bevel=0.007),
            a.box((0.15, 0.12, 0.12), (0, 0.388, 0.018), a.GM_D, bevel=0.009),
            a.box((0.56, 0.16, 0.047), (0, 0.54, -0.065), a.GM_D,
                  bevel=0.014, rot=(0.33, 0, 0)),
            a.box((0.36, 0.13, 0.051), (0, 0.54, -0.088), a.GM_L, bevel=0.01, rot=(0.33, 0, 0))]
    for side in (-1, 1):
        head.append(a.box((0.153, 0.14, 0.037), (side * 0.232, 0.547, -0.117),
                          a.T_MAIN, bevel=0.008, rot=(0.33, side * 0.34, 0)))
        head.append(a.light((side * 0.289, 0.568, -0.133), 0.021))
    for x in (-0.11, -0.055, 0, 0.055, 0.11):
        head.append(a.box((0.015, 0.092, 0.01), (x, 0.546, -0.116), a.GM_D,
                          bevel=0.002, rot=(0.33, 0, 0)))
    head.append(a.light((0, 0.622, -0.066), 0.023))
    a.join(head, "turret")


for model in (airpad, radar):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    model()
    a.export_model(model.__name__)
