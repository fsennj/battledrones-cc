"""Flak Crawler (anti-air crawler) as a detailed low-poly model, built headless in Blender.

    blender -b --factory-startup -P art/blender/flak-crawler.py -- <out_dir> [preview_samples]

Writes <out_dir>/flak-crawler.glb (nodes "hull" and "turret", vertex colours only, no
textures). Like the procedural builder (models.ts "flak-crawler") it is a hex body on a
team carapace with a head of amber eyes and a turret of four guns pitched at the sky;
the six jointed legs stay procedural (ModelDef.parts animate the walk, glb-models.ts
replaces hull/turret only). See lib.py for the coordinate contract.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from lib import _finish


def sdrum(r_bot, r_top, h, seg, at, hex_, sz, bevel=0.0, rot=(0, 0, 0), **kw):
    """models.ts drum with scale [1, 1, 1.3]: the hex body stretched along game z (= blender y)."""
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r_bot, radius2=r_top, depth=h)
    o = bpy.context.object
    o.scale = (1, sz, 1)
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, hex_, at, rot, bevel, **kw)


SZ = 1.3  # the body drums' z stretch (models.ts scale [1, 1, 1.3])
H = [
    sdrum(0.20, 0.17, 0.08, 6, (0, 0.13, 0), GM_D, SZ, bevel=0.015),               # belly drum
    sdrum(0.24, 0.20, 0.12, 6, (0, 0.19, 0), GM, SZ, bevel=0.03),                  # main hex body
    sdrum(0.19, 0.15, 0.03, 6, (0, 0.31, 0), T_MAIN, SZ, bevel=0.012),             # team carapace
    box((0.16, 0.08, 0.10), (0, 0.22, -0.32), GM_D, 0.015),                        # head
    light((0.045, 0.24, -0.37), 0.025),                                             # amber eyes
    light((-0.045, 0.24, -0.37), 0.025),
]
hull = join(H, "hull")

MOUNT = (0, 0.32, 0.04)
def at(p): return (p[0] + MOUNT[0], p[1] + MOUNT[1], p[2] + MOUNT[2])
PITCH = 0.85
T = [
    drum(0.12, 0.10, 0.08, 8, at((0, 0.04, 0.02)), GM, 0.02),                      # gun mantlet drum
    box((0.18, 0.06, 0.06), at((0, 0.07, -0.07)), GM_D, 0.01, rot=(PITCH, 0, 0)),  # gun mount, pitched
    light(at((0, 0.09, 0.08)), 0.02),                                               # rear aiming light
]
for x in (-0.065, -0.025, 0.025, 0.065):                                            # four flak barrels
    T.append(barrel(at((x, 0.07, -0.07)), 0.014, 0.3, PITCH, BARREL, seg=5))
turret = join(T, "turret", shift=MOUNT)
export_and_preview(hull, turret, "flak-crawler", ortho=1.6)
