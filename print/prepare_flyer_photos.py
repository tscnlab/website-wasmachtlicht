#!/usr/bin/env python3
"""Export the two user-supplied gallery originals as reproducible print assets."""
from pathlib import Path
import hashlib
import io
import json
from PIL import Image, ImageCms, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'print/assets/photos'
DEST.mkdir(parents=True, exist_ok=True)
items = [('Max_Planck_Licht_045.jpg', 'lichtcafe-aussen.jpg'),
         ('Max_Planck_Licht_073.jpg', 'lichtcafe-innen.jpg')]
profile = ImageCms.createProfile('sRGB')
manifest = []
for original, output in items:
    path = ROOT / 'photo-originals' / original
    with Image.open(path) as source:
        im = ImageOps.exif_transpose(source)
        icc = source.info.get('icc_profile')
        if icc:
            im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), profile, outputMode='RGB')
        else:
            im = im.convert('RGB')
        im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        im.save(DEST / output, quality=94, subsampling=0, optimize=True,
                icc_profile=ImageCms.ImageCmsProfile(profile).tobytes())
        manifest.append({'source': original, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'output': output, 'dimensions': list(im.size)})
(DEST / 'provenance.json').write_text(json.dumps({
    'source_gallery': 'https://www.picdrop.com/verenamuellerfotografie/7e4Z7c46Ma',
    'photographer': 'Verena Müller', 'processing': 'EXIF orientation, sRGB, downsample; no crop or retouching',
    'photos': manifest}, ensure_ascii=False, indent=2) + '\n')
