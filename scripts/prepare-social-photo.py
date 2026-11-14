#!/usr/bin/env python3
"""Export the selected photograph 038 for Open Graph and social cards.

Run with Python and Pillow; the full 3:2 composition is retained.
The original is read from the ignored photo-originals directory.
"""
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "photo-originals/Max_Planck_Licht_038.jpg"
OUTPUT = ROOT / "assets/social-preview-038.jpg"

with Image.open(SOURCE) as original:
    photograph = ImageOps.exif_transpose(original)
    profile = original.info.get("icc_profile")
    srgb = ImageCms.createProfile("sRGB")
    if profile:
        photograph = ImageCms.profileToProfile(photograph,
            ImageCms.ImageCmsProfile(io.BytesIO(profile)), srgb, outputMode="RGB")
    else:
        photograph = photograph.convert("RGB")
    original_dimensions = list(photograph.size)
    height = round(photograph.height * 1200 / photograph.width)
    photograph = photograph.resize((1200, height), Image.Resampling.LANCZOS)
    # Do not publish embedded EXIF/GPS or camera identifiers.
    photograph.save(OUTPUT, "JPEG", quality=92, subsampling=0, optimize=True,
        icc_profile=ImageCms.ImageCmsProfile(srgb).tobytes())

(ROOT / "scripts/social-photo-provenance.json").write_text(json.dumps({
    "source_gallery": "https://www.picdrop.com/verenamuellerfotografie/7e4Z7c46Ma",
    "photographer": "Verena Müller", "source": SOURCE.name,
    "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "original_dimensions": original_dimensions,
    "output": str(OUTPUT.relative_to(ROOT)), "dimensions": [1200, height],
    "processing": "EXIF orientation, sRGB, resize; no crop or retouching"
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Prepared {OUTPUT.relative_to(ROOT)}: 1200 x {height}")
