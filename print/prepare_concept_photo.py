#!/usr/bin/env python3
"""Prepare photo 078 for the current A4 flyer without modifying older assets."""
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "photo-originals/Max_Planck_Licht_078.jpg"
OUTPUT = ROOT / "print/assets/photos/lichtcafe-aussen-078.jpg"

with Image.open(SOURCE) as original:
    photograph = ImageOps.exif_transpose(original)
    profile = original.info.get("icc_profile")
    srgb = ImageCms.createProfile("sRGB")
    if profile:
        photograph = ImageCms.profileToProfile(photograph,
            ImageCms.ImageCmsProfile(io.BytesIO(profile)), srgb, outputMode="RGB")
    else:
        photograph = photograph.convert("RGB")
    photograph.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    photograph.save(OUTPUT, "JPEG", quality=94, subsampling=0, optimize=True,
        icc_profile=ImageCms.ImageCmsProfile(srgb).tobytes())
    dimensions = list(photograph.size)

OUTPUT.with_suffix(".json").write_text(json.dumps({
    "source_gallery": "https://www.picdrop.com/verenamuellerfotografie/7e4Z7c46Ma",
    "photographer": "Verena Müller", "source": SOURCE.name,
    "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "output": OUTPUT.name, "dimensions": dimensions,
    "processing": "EXIF orientation, sRGB, downsample; no crop or retouching"
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Prepared {OUTPUT.relative_to(ROOT)}: {dimensions}")
