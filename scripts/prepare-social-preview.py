#!/usr/bin/env python3
"""Rebuild the 1200 × 630 sharing image from the project's local Roboto font.

Run from any working directory with Python 3 and Pillow installed:
    python3 scripts/prepare-social-preview.py
No remote files, generated photos or external renderers are used.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "social-preview.png"
FONT = ROOT / "assets" / "fonts" / "Roboto-Variable.ttf"
SIZE = (1200, 630)
SCALE = 3
YELLOW = "#fed300"
ORANGE = "#f48432"
INK = "#2d2930"


def font(size: int, weight: int = 500) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(FONT), size * SCALE)
    face.set_variation_by_axes([weight, 100])
    return face


def scaled(points):
    return [(round(x * SCALE), round(y * SCALE)) for x, y in points]


def text(draw, xy, content, size, weight=500):
    draw.text((xy[0] * SCALE, xy[1] * SCALE), content,
              font=font(size, weight), fill=INK, anchor="lt")


def main():
    width, height = SIZE
    image = Image.new("RGB", (width * SCALE, height * SCALE), YELLOW)
    draw = ImageDraw.Draw(image)

    # The same ascending diagonal hatch as the favicon, enlarged for sharing.
    # Keep a broad, diagonal-edged text-safe area on the left.
    hatch = Image.new("RGB", image.size, YELLOW)
    hatch_draw = ImageDraw.Draw(hatch)
    for offset in range(-height, width + height, 88):
        hatch_draw.polygon(scaled([
            (offset, height), (offset + 36, height),
            (offset + height + 36, 0), (offset + height, 0),
        ]), fill=ORANGE)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon(scaled([
        (945, 0), (width, 0), (width, height), (710, height)
    ]), fill=255)
    image.paste(hatch, (0, 0), mask)

    text(draw, (78, 80), "Das Lichtcafé · Tübingen", 28, 500)
    text(draw, (72, 204), "Was macht", 111, 700)
    text(draw, (72, 326), "Licht?", 132, 700)
    draw.line(scaled([(78, 526), (126, 526)]), fill=INK, width=3 * SCALE)
    text(draw, (145, 513), "wasmachtlicht.de", 27, 500)

    image = image.resize(SIZE, Image.Resampling.LANCZOS)
    image.save(OUTPUT, format="PNG", optimize=True)
    print(f"Created {OUTPUT} ({width} × {height}, RGB PNG)")


if __name__ == "__main__":
    main()
