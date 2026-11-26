"""Export the Condor, Wasp and Raptor. Run Blender with -- /absolute/output/path."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib as a

import bmesh
import bpy


GLASS = 0xAC712E
RUBBER = 0x24282B
ALLOY = 0xB0B7BB


def mesh(vertices, faces, colour):
    """Build a flat-shaded shell in the game's coordinates."""
    data = bpy.data.meshes.new("shell")
    data.from_pydata([a.g2b(v) for v in vertices], [], faces)
    normals = bmesh.new()
    normals.from_mesh(data)
    bmesh.ops.recalc_face_normals(normals, faces=list(normals.faces))
    normals.to_mesh(data)
    normals.free()
    data.update()
    obj = bpy.data.objects.new("shell", data)
    a.sc.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return a._finish(obj, colour, (0, 0, 0), (0, 0, 0), 0)


def hull_shell(sections, colour, x_offset=0):
    """One closed faceted skin from lengthwise sections (z, half-width, floor, crown)."""
    vertices = []
    for z, width, floor, crown in sections:
        height = crown - floor
        profile = [(-0.72, 1), (0.72, 1), (1, 0.72), (0.92, 0.26), (0.62, 0),
                   (-0.62, 0), (-0.92, 0.26), (-1, 0.72)]
        vertices.extend((x_offset + width * x, floor + height * y, z) for x, y in profile)
    faces = [tuple(range(8))]
    for start in range(0, len(vertices) - 8, 8):
        for i in range(8):
            j = (i + 1) % 8
            faces.append((start + i, start + j, start + j + 8, start + i + 8))
    faces.append(tuple(range(len(vertices) - 8, len(vertices))))
    return mesh(vertices, faces, colour)


def plate(outline, y, thickness, colour):
    count = len(outline)
    vertices = [(x, level, z) for level in (y, y + thickness) for x, z in outline]
    faces = [tuple(range(count)), tuple(range(count, count * 2))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    return mesh(vertices, faces, colour)


def wings(outline, y, thickness, colour):
    return [plate([(side * x, z) for x, z in outline], y, thickness, colour) for side in (-1, 1)]


def fan(radius, axial=False):
    if axial:
        hub = a.tube(radius * 0.2, 0.025, 10, (0, 0, 0), a.GM_L)
    else:
        hub = a.cyl(radius * 0.2, radius * 0.22, 0.025, 10, (0, 0, 0), a.GM_L)
    pieces = [hub]
    for i in range(5):
        angle = math.tau * i / 5
        x, ortho = math.cos(angle) * radius * 0.52, math.sin(angle) * radius * 0.52
        size = (radius * 0.81, radius * 0.24, 0.009) if axial else (radius * 0.81, 0.009, radius * 0.24)
        pos = (x, ortho, 0) if axial else (x, 0, ortho)
        rotation = (0, 0, angle + 0.22) if axial else (0, -angle - 0.22, 0)
        pieces.append(a.box(size, pos, ALLOY, bevel=0.003, rot=rotation))
    a.join(pieces, "rotor")


def condor():
    # Match the existing troop slots, ramp hinge and lift-fan pivots in models.ts.
    hull = [hull_shell([(-0.75, 0.045, -0.13, -0.09), (-0.62, 0.13, -0.17, 0),
                        (-0.42, 0.2, -0.20, 0.018), (-0.31, 0.218, -0.20, 0.006)], a.GM),
            hull_shell([(-0.6, 0.045, 0.001, 0.022), (-0.48, 0.10, 0.009, 0.083),
                        (-0.35, 0.10, 0.012, 0.082), (-0.312, 0.105, 0.008, 0.049)], GLASS),
            a.box((0.34, 0.08, 0.65), (0, -0.143, 0.015), a.GM_D, bevel=0.014),
            a.box((0.34, 0.012, 0.65), (0, -0.106, 0.015), RUBBER, bevel=0.003),
            hull_shell([(0.16, 0.145, 0.014, 0.062), (0.34, 0.116, 0.027, 0.074),
                        (0.56, 0.058, 0.05, 0.083), (0.65, 0.032, 0.054, 0.079)], a.GM_L)]
    hull.extend(wings([(0.17, -0.29), (0.32, -0.19), (0.38, 0.05), (0.18, 0.12)], -0.098, 0.045, a.GM))
    hull.extend(wings([(0.184, -0.23), (0.31, -0.15), (0.345, 0.01), (0.19, 0.065)], -0.053, 0.008, a.T_MAIN))
    for side in (-1, 1):
        wall = [(0.17, -0.31), (0.224, -0.31), (0.225, -0.12), (0.204, 0.17),
                (0.148, 0.34), (0.136, 0.34), (0.17, 0.17)]
        hull.append(plate([(side * x, z) for x, z in wall], -0.102, 0.102, a.GM_L))
        hull.append(plate([(side * x, z) for x, z in wall], 0, 0.01, a.T_MAIN))
        hull.append(a.box((0.029, 0.035, 0.44), (side * 0.151, -0.082, -0.08), a.GM_D, bevel=0.005))
        for z in (-0.27, -0.1, 0.09, 0.28):
            hull.append(a.light((side * 0.16, -0.033, z), 0.013))
        x = side * 0.45
        hull.append(a.drum(0.145, 0.151, 0.072, 18, (x, -0.075, -0.08), a.GM_D, bevel=0.009))
        hull.append(a.torus(0.143, 0.019, (x, -0.024, -0.08), a.T_MAIN, seg=24, rot=(math.pi / 2, 0, 0)))
        hull.append(a.light((x + side * 0.151, -0.041, -0.11), 0.018))
        hull.append(a.box((0.043, 0.135, 0.16), (side * 0.11, 0.114, 0.557), a.T_MAIN,
                          rot=(0.18, 0, -side * 0.67), taper=0.65, bevel=0.009))
        hull.append(a.box((0.047, 0.014, 0.091), (side * 0.153, -0.262, 0.12), RUBBER, bevel=0.007))
        hull.append(a.box((0.018, 0.072, 0.026), (side * 0.153, -0.223, 0.12), a.GM_L))
    hull.append(a.light((0, -0.078, -0.725), 0.027))
    hull.append(a.light((0, 0.082, 0.346), 0.023))
    a.join(hull, "hull", ao=(0.07, 0.15))
    ramp = [a.box((0.264, 0.12, 0.023), (0, 0.06, 0), a.GM, bevel=0.006)]
    for y in (0.022, 0.047, 0.072, 0.097):
        ramp.append(a.box((0.183, 0.006, 0.005), (0, y, -0.012), a.GM_L, bevel=0.001))
    for x in (-0.111, 0.111):
        ramp.append(a.box((0.022, 0.106, 0.007), (x, 0.058, 0.015), a.HAZ, bevel=0.002))
        ramp.append(a.light((x, 0.112, -0.012), 0.016))
    a.join(ramp, "ramp")
    fan(0.129)


def wasp():
    hull = [hull_shell([(-0.33, 0.022, -0.025, 0.012), (-0.21, 0.063, -0.045, 0.047),
                        (0.035, 0.069, -0.046, 0.043), (0.22, 0.048, -0.033, 0.036)], a.GM),
            hull_shell([(-0.234, 0.028, 0.028, 0.042), (-0.16, 0.043, 0.038, 0.073),
                        (-0.054, 0.042, 0.042, 0.065), (-0.017, 0.025, 0.042, 0.047)], GLASS),
            a.torus(0.081, 0.015, (0, 0.03, 0.265), a.T_MAIN, seg=18),
            a.box((0.017, 0.045, 0.084), (0, -0.025, 0.208), a.GM_D, bevel=0.006)]
    hull.extend(wings([(0.045, -0.11), (0.36, 0.052), (0.37, 0.104), (0.26, 0.12), (0.052, 0.055)], -0.025, 0.032, a.GM_D))
    hull.extend(wings([(0.19, -0.027), (0.353, 0.055), (0.352, 0.085), (0.24, 0.079)], 0.007, 0.006, a.T_MAIN))
    for x in (-0.34, 0.34):
        hull.append(a.light((x, 0.012, 0.085), 0.017))
    hull.append(a.light((0, -0.005, -0.324), 0.02))
    a.join(hull, "hull", ao=(0.04, 0.21))
    fan(0.072, axial=True)


def raptor():
    hull = [hull_shell([(-0.52, 0.018, -0.022, 0.005), (-0.39, 0.059, -0.038, 0.025),
                        (-0.23, 0.076, -0.05, 0.064), (0.04, 0.07, -0.053, 0.045),
                        (0.19, 0.043, -0.049, 0.037)], a.GM),
            hull_shell([(-0.326, 0.035, 0.031, 0.047), (-0.25, 0.049, 0.049, 0.088),
                        (-0.15, 0.047, 0.053, 0.080), (-0.108, 0.039, 0.058, 0.065)], GLASS),
            a.box((0.48, 0.021, 0.09), (0, 0.034, 0.342), a.GM_L, bevel=0.01)]
    hull.extend(wings([(0.053, -0.216), (0.51, 0.014), (0.53, 0.071), (0.40, 0.124), (0.07, 0.109)], -0.044, 0.039, a.GM_D))
    hull.extend(wings([(0.291, -0.051), (0.505, 0.026), (0.501, 0.059), (0.351, 0.085)], -0.005, 0.009, a.T_MAIN))
    for side in (-1, 1):
        x = side * 0.219
        hull.append(hull_shell([(-0.351, 0.036, -0.039, 0.026), (-0.28, 0.058, -0.047, 0.057),
                                (0.16, 0.055, -0.036, 0.063), (0.409, 0.034, -0.015, 0.051)], a.GM_L, x))
        hull.append(a.tube(0.027, 0.051, 10, (x, 0.015, -0.334), a.GM_D))
        hull.append(a.tube(0.029, 0.021, 10, (x, 0.016, 0.419), a.GM_D))
        hull.append(a.tube(0.015, 0.004, 8, (x, 0.016, 0.431), a.EXHAUST, grade=0))
        hull.append(a.box((0.02, 0.113, 0.123), (x + side * 0.013, 0.081, 0.325), a.T_MAIN,
                          rot=(0.25, 0, -side * 0.28), taper=0.65, bevel=0.005))
        hull.append(a.light((side * 0.507, -0.001, 0.046), 0.018))
    a.join(hull, "hull", ao=(0.04, 0.21))


for model in (condor, wasp, raptor):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    model()
    a.export_model(model.__name__)
