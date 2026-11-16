#!/usr/bin/env python3
"""Render a luminous energy vortex for make.fun ai-excited-01.

Deterministic: fixed seed, pure Pillow, no external assets.
Writes entry.png (1024x1024) into this repository's root.
"""
from __future__ import annotations

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
SEED = 34021496
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(c1: tuple, c2: tuple, t: float) -> tuple:
    return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(len(c1)))


def radial_gradient(size: int, stops) -> Image.Image:
    """Square RGBA radial gradient. stops = [(t, (r, g, b, a)), ...], t in 0..1."""
    img = Image.new("RGBA", (size, size))
    px = img.load()
    c = (size - 1) / 2.0
    maxd = math.hypot(c, c)
    n = len(stops)
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / maxd
            color = stops[-1][1]
            if d <= stops[0][0]:
                color = stops[0][1]
            elif d >= stops[-1][0]:
                color = stops[-1][1]
            else:
                for i in range(n - 1):
                    t0, c0 = stops[i]
                    t1, c1 = stops[i + 1]
                    if t0 <= d <= t1:
                        tt = (d - t0) / (t1 - t0) if t1 > t0 else 0.0
                        color = mix(c0, c1, tt)
                        break
            px[x, y] = color
    return img


def linear_gradient(size: int, tl, tr, bl, br) -> Image.Image:
    """Smooth full-canvas gradient from four corner colors."""
    small = Image.new("RGBA", (2, 2))
    small.putpixel((0, 0), tl)
    small.putpixel((1, 0), tr)
    small.putpixel((0, 1), bl)
    small.putpixel((1, 1), br)
    return small.resize((size, size), Image.BICUBIC)


def draw_streak(layer: Image.Image, cx: float, cy: float, angle: float,
                r0: float, r1: float, glow: tuple, core: tuple, w: int) -> None:
    d = ImageDraw.Draw(layer)
    cos, sin = math.cos(angle), math.sin(angle)
    p0 = (cx + r0 * cos, cy + r0 * sin)
    p1 = (cx + r1 * cos, cy + r1 * sin)
    if r1 - r0 > w * 3:
        d.line([p0, p1], fill=glow, width=max(2, int(w * 2.6)))
    d.line([p0, p1], fill=core, width=max(1, w))


def build() -> Image.Image:
    rng = random.Random(SEED)
    cx, cy = 512.0, 472.0
    axis = math.radians(-42.0)  # momentum points toward upper-right

    # --- background: deep space gradient -------------------------------
    bg = linear_gradient(
        SIZE,
        (8, 4, 22, 255), (18, 8, 44, 255),
        (4, 3, 14, 255), (26, 10, 58, 255),
    )

    # --- nebula clouds (soft color pools) ------------------------------
    nebula = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    neb_cyan = radial_gradient(
        384,
        [(0.0, (40, 170, 255, 70)), (0.5, (30, 90, 190, 34)), (1.0, (0, 0, 0, 0))],
    ).resize((760, 760), Image.BICUBIC)
    nebula.alpha_composite(neb_cyan, (60, 140))
    neb_mag = radial_gradient(
        384,
        [(0.0, (255, 60, 190, 60)), (0.5, (160, 30, 150, 28)), (1.0, (0, 0, 0, 0))],
    ).resize((820, 820), Image.BICUBIC)
    nebula.alpha_composite(neb_mag, (260, -80))
    bg = Image.alpha_composite(bg, nebula)

    # --- star field ------------------------------------------------------
    stars = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)
    for _ in range(340):
        x, y = rng.uniform(0, SIZE), rng.uniform(0, SIZE)
        b = rng.randint(120, 255)
        r = rng.uniform(0.3, 1.4)
        kind = rng.random()
        if kind < 0.75:
            col = (b, b, min(255, b + 20), rng.randint(120, 230))
            sd.ellipse([x - r, y - r, x + r, y + r], fill=col)
        elif kind < 0.9:
            col = (min(255, b + 30), b, b, rng.randint(120, 230))
            sd.ellipse([x - r, y - r, x + r, y + r], fill=col)
        else:
            col = (b, b, min(255, b + 45), rng.randint(140, 255))
            sd.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2], fill=col)
    bg = Image.alpha_composite(bg, stars)

    # --- energy FX layer: streaks, arcs, shockwave ----------------------
    fx = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    palette_core = [
        (255, 255, 255, 235),
        (170, 240, 255, 220),
        (255, 140, 225, 215),
        (175, 130, 255, 215),
    ]
    palette_glow = [
        (90, 200, 255, 70),
        (255, 100, 200, 60),
        (140, 100, 255, 60),
    ]

    # radial burst (omnidirectional energy)
    for _ in range(120):
        a = rng.uniform(0.0, 2.0 * math.pi)
        r0 = rng.uniform(70, 150)
        r1 = r0 + rng.uniform(150, 520)
        w = rng.randint(1, 3)
        core = palette_core[rng.randrange(len(palette_core))]
        glow = palette_glow[rng.randrange(len(palette_glow))]
        draw_streak(fx, cx, cy, a, r0, r1, glow, core, w)

    # momentum trails clustered around the axis
    for _ in range(34):
        off = rng.uniform(-0.5, 0.5)
        a = axis + off * rng.uniform(0.0, 1.0)
        r0 = rng.uniform(60, 130)
        r1 = r0 + rng.uniform(420, 720)
        w = rng.randint(2, 4)
        core = (rng.randint(235, 255), rng.randint(235, 255), 255, rng.randint(190, 240))
        glow = (120, 210, 255, rng.randint(50, 90))
        draw_streak(fx, cx, cy, a, r0, r1, glow, core, w)

    # a few crisp comet tails along the axis for direction
    for _ in range(8):
        a = axis + rng.uniform(-0.22, 0.22)
        r0 = rng.uniform(70, 110)
        r1 = r0 + rng.uniform(560, 780)
        draw_streak(fx, cx, cy, a, r0, r1, (90, 200, 255, 45), (240, 252, 255, 220), 3)

    # swirl arcs suggesting rotation
    ad = ImageDraw.Draw(fx)
    for _ in range(3):
        a0 = rng.uniform(0, 2 * math.pi)
        radius = rng.uniform(300, 470)
        w = rng.randint(1, 2)
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        ad.arc(bbox, start=math.degrees(a0), end=math.degrees(a0) + rng.uniform(70, 150),
               fill=(255, 255, 255, rng.randint(60, 110)), width=w)

    # shockwave ring
    ring_r = 332.0
    for w, col in ((10, (120, 220, 255, 55)), (4, (210, 245, 255, 120)), (2, (255, 255, 255, 210))):
        ad.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], outline=col, width=w)
        ring_r += 14

    # spark flecks at streak tips
    for _ in range(150):
        a = rng.uniform(0.0, 2.0 * math.pi)
        r = rng.uniform(260, 620)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        s = rng.uniform(0.5, 2.0)
        col = (rng.randint(200, 255), rng.randint(200, 255), 255, rng.randint(120, 230))
        ad.ellipse([x - s, y - s, x + s, y + s], fill=col)

    bg = Image.alpha_composite(bg, fx)

    # --- luminous core ---------------------------------------------------
    core_glow = radial_gradient(
        384,
        [
            (0.00, (255, 255, 255, 255)),
            (0.12, (250, 244, 255, 235)),
            (0.30, (130, 224, 255, 185)),
            (0.55, (120, 80, 235, 95)),
            (1.00, (0, 0, 0, 0)),
        ],
    ).resize((820, 820), Image.BICUBIC)
    bg.alpha_composite(core_glow, (int(cx - 410), int(cy - 410)))

    hot = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hot)
    hd.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=(255, 255, 255, 255))
    hd.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 250, 240, 255))
    hot = hot.filter(ImageFilter.GaussianBlur(6))
    bg = Image.alpha_composite(bg, hot)

    # diffraction spikes (lens flare cross)
    sp = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    spd = ImageDraw.Draw(sp)
    for ang in (0.0, math.pi / 2.0, math.pi / 4.0, -math.pi / 4.0):
        dx, dy = math.cos(ang), math.sin(ang)
        x0, y0 = cx + dx * 40, cy + dy * 40
        x1, y1 = cx + dx * 180, cy + dy * 180
        spd.line([x0, y0, x1, y1], fill=(200, 240, 255, 70), width=5)
        spd.line([x0, y0, x1, y1], fill=(255, 255, 255, 150), width=2)
    sp = sp.filter(ImageFilter.GaussianBlur(1.5))
    bg = Image.alpha_composite(bg, sp)

    # --- vignette --------------------------------------------------------
    vig = radial_gradient(
        512,
        [(0.0, (0, 0, 0, 0)), (0.58, (0, 0, 0, 0)), (1.0, (0, 0, 0, 185))],
    ).resize((SIZE, SIZE), Image.BICUBIC)
    bg = Image.alpha_composite(bg, vig)

    return bg.convert("RGB")


def main() -> None:
    img = build()
    img.save(OUT, "PNG", optimize=True)
    size_bytes = os.path.getsize(OUT)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]}, {size_bytes} bytes)")


if __name__ == "__main__":
    main()
