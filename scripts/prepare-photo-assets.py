"""Make responsive website photos and JPEGs for the Quarto photo review.

Usage: python3 scripts/prepare-photo-assets.py photo-originals
Requires Pillow. Normal site builds use the checked-in assets.
Full photographs are preserved; portrait framing is controlled by CSS.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("originals", type=Path)
    args = parser.parse_args()
    selection = json.loads((ROOT / "scripts/photo-selection.json").read_text())
    web = ROOT / "assets/photos"
    review = ROOT / "review/images"
    web.mkdir(parents=True, exist_ok=True)
    review.mkdir(parents=True, exist_ok=True)
    records = []
    srgb = ImageCms.createProfile("sRGB")

    for item in selection["photos"]:
        matches = list(args.originals.rglob(item["source"]))
        if len(matches) != 1:
            raise ValueError(f"Expected one original for {item['source']}, found {len(matches)}")
        source = matches[0]
        record = {**item, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        with Image.open(source) as original:
            photograph = ImageOps.exif_transpose(original)
            profile = original.info.get("icc_profile")
            if profile:
                photograph = ImageCms.profileToProfile(
                    photograph, ImageCms.ImageCmsProfile(io.BytesIO(profile)), srgb, outputMode="RGB"
                )
            else:
                photograph = photograph.convert("RGB")
            record["original_dimensions"] = list(photograph.size)
            record["derivatives"] = []
            for width in item["widths"]:
                height = round(photograph.height * width / photograph.width)
                resized = photograph.resize((width, height), Image.Resampling.LANCZOS)
                suffix = "" if width == max(item["widths"]) else f"-{width}"
                target = web / f"{item['output']}{suffix}.webp"
                # Save only image pixels: no embedded EXIF/GPS or camera identifiers.
                resized.save(target, "WEBP", quality=86, method=6)
                record["derivatives"].append({
                    "file": str(target.relative_to(ROOT)), "width": width,
                    "height": height, "bytes": target.stat().st_size,
                })
            # The final iteration is the largest, suitable for both PDF and HTML.
            resized.save(review / f"{item['output']}.jpg", "JPEG", quality=92, optimize=True)
        records.append(record)
        print(f"Prepared {item['source']} → {item['output']}")

    provenance = {key: value for key, value in selection.items() if key != "photos"}
    provenance["photos"] = records
    (ROOT / "scripts/photo-provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
