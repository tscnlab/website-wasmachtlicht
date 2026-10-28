#!/usr/bin/env python3
"""Rebuild the crop-safe square sharing image (Python 3 + Pillow).

Run: python3 scripts/prepare-social-preview.py
The pure diagonal hatch remains recognisable in small and cropped previews.
"""
from math import sqrt
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets' / 'social-preview-schraffur-v2.png'
SIZE = 1200
SCALE = 2
YELLOW = '#fed300'
ORANGE = '#f48432'


def main():
    edge = SIZE * SCALE
    image = Image.new('RGB', (edge, edge), YELLOW)
    draw = ImageDraw.Draw(image)
    # Match the favicon's 16-unit repeat and 6-unit stripe, rotated 45 degrees.
    repeat = 16 / 64 * edge * sqrt(2)
    stripe = 6 / 64 * edge * sqrt(2)
    for i in range(-1, 8):
        start = i * repeat
        draw.polygon([
            (start, 0), (start + stripe, 0),
            (start + stripe - edge, edge), (start - edge, edge),
        ], fill=ORANGE)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUTPUT, optimize=True)
    print(f'Created {OUTPUT} ({SIZE} × {SIZE}, RGB PNG)')


if __name__ == '__main__':
    main()
