#!/usr/bin/env python3
"""Ship the biome rock materials the 3D terrain textures its rocks with.

The same painted rock materials art/terrain.py paints every map's outcrops
with (art/raw/tex-<biome>-rock.webp: granite with lichen, red sandstone with
layered strata, dark basalt with snow in its cracks, black obsidian, pale
pitted limestone with moss and ferns) become
small tileable textures: the game projects them onto the cliff walls and the
crags standing on the outcrops, so the walls and crags are the same stone as
the painted tops.

    public/assets/textures/rock-<biome>.webp   512 x 512, seamless

Usage:  python3 art/textures.py      (art/terrain.py also refreshes those of the biomes it paints)

Needs Pillow and numpy only. Deterministic: same raws -> same output.

Per biome: the source is made seamless along a noisy seam, flattened to
remove broad baked lighting, and colour-balanced. Fractures and strata
keep more contrast than fine grain. The albedo is resampled to SIZE from a
3 x 3 tiling so the filter wraps. WebP quality: the highest of WEBP_QUALITY
that fits BUDGET (it warns if even the lowest doesn't).

art/terrain.py uses the same rock albedos. It also shares the seamless and
resampling helpers for other materials, and passes a SciPy filter for its
larger blur fields. This script uses an FFT and needs no SciPy.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "art" / "raw"
OUT = ROOT / "public" / "assets" / "textures"

BIOMES = ("temperate", "desert", "arctic", "volcanic", "tropical")
SIZE = 512
WEBP_QUALITY = (88, 84, 80, 76, 72, 68, 64, 60)  # highest that fits the budget wins
BUDGET = 150 * 1024                                # bytes per texture
ROCK_TONES = {
    "temperate": (0.43, 0.44, 0.40),  # grey granite, green weathering
    "desert": (0.63, 0.40, 0.28),     # oxidised sandstone
    "arctic": (0.32, 0.36, 0.42),     # cold slate
    "volcanic": (0.21, 0.20, 0.21),   # basalt and fine ash
    "tropical": (0.52, 0.51, 0.45),   # salt-bleached limestone
}


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lum(c: np.ndarray) -> np.ndarray:
    return c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114


def blur_wrap(a: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian blur of a 2D field that wraps round its edges (exact, via the FFT)."""
    f0 = np.fft.fftfreq(a.shape[0])[:, None]
    f1 = np.fft.rfftfreq(a.shape[1])[None, :]
    g = np.exp(-2.0 * (np.pi * sigma) ** 2 * (f0 * f0 + f1 * f1))
    return np.fft.irfft2(np.fft.rfft2(a) * g, s=a.shape).astype(np.float32)


Blur = Callable[[np.ndarray, float], np.ndarray]


def periodic_noise(N: int, sigma: float, rng, blur: Blur = blur_wrap) -> np.ndarray:
    g = blur(rng.standard_normal((N, N)).astype(np.float32), sigma)
    return g / (g.std() + 1e-6)


def vp_blend(A, B, w, m):
    """Variance-preserving blend (keeps contrast inside the transition)."""
    w = w[..., None]
    return m + ((A - m) * w + (B - m) * (1.0 - w)) / np.sqrt(w * w + (1.0 - w) ** 2)


def make_seamless(a: np.ndarray, rng, blur: Blur = blur_wrap) -> np.ndarray:
    """Blend with itself rolled half-way round: its old edges meet in the middle along a noisy seam.
    `blur`: a Gaussian blur that wraps round the edges (sigma in px)."""
    N = a.shape[0]
    m = a.mean((0, 1))
    idx = np.arange(N, dtype=np.float32)
    d = np.minimum(idx, N - idx) / (N / 2.0)
    for axis in (1, 0):
        nz = np.clip(periodic_noise(N, N / 24, rng, blur), -1.5, 1.5)
        f = (d[None, :] if axis == 1 else d[:, None]) + 0.17 * nz
        w = sstep(0.44, 0.56, f)
        a = vp_blend(a, np.roll(a, N // 2, axis=axis), w, m)
    return np.clip(a, 0.0, 1.0)


def flatten(a: np.ndarray, strength: float, blur: Blur = blur_wrap) -> np.ndarray:
    """Remove low-frequency light so the repeat is less obvious."""
    if strength <= 0:
        return a
    N = a.shape[0]
    L = lum(a)
    low = blur(L, N / 12)
    ratio = (L.mean() / np.maximum(low, 1e-3)) ** strength
    return np.clip(a * ratio[..., None], 0.0, 1.0)


def rock_material(biome: str) -> np.ndarray:
    """One albedo for the painted outcrop and the stone projected onto its sides."""
    src = np.asarray(Image.open(RAW / f"tex-{biome}-rock.webp").convert("RGB"), np.float32) / 255.0
    rng = np.random.default_rng([ord(c) for c in biome + "rock"])
    a = flatten(make_seamless(src, rng), 0.62)
    L = lum(a)
    # Preserve mottled mineral colours, soften photographic grit and reveal the wider fracture bands.
    coarse = blur_wrap(L, 3.2)
    medium = coarse - blur_wrap(L, 27)
    tone = np.asarray(ROCK_TONES[biome], np.float32)
    a += (tone - a.mean((0, 1))) * 0.85
    a += (0.55 * medium - 0.26 * (L - coarse))[..., None]
    return np.clip(a, 0.0, 1.0)


def resample_periodic(a: np.ndarray, size: int) -> Image.Image:
    """Lanczos resize with real neighbours beyond the old texture edges."""
    tile = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
    n = tile.width
    big = Image.new("RGB", (3 * n, 3 * n))
    for y in (0, n, 2 * n):
        for x in (0, n, 2 * n):
            big.paste(tile, (x, y))
    return big.resize((3 * size, 3 * size), Image.LANCZOS).crop((size, size, 2 * size, 2 * size))


def write_rock_textures(biomes: Iterable[str] = BIOMES) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for biome in biomes:
        im = resample_periodic(rock_material(biome), SIZE)
        for q in WEBP_QUALITY:
            b = io.BytesIO()
            im.save(b, "WEBP", quality=q, method=6)
            if b.tell() <= BUDGET:
                break
        (OUT / f"rock-{biome}.webp").write_bytes(b.getvalue())
        over = f" (over the {BUDGET // 1024} KB budget)" if b.tell() > BUDGET else ""
        print(f"rock-{biome}: {SIZE}x{SIZE}, {b.tell() / 1024:.0f} KB at q{q}{over}")


if __name__ == "__main__":
    write_rock_textures()
