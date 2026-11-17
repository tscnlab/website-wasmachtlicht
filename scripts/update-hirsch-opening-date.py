"""Correct the Light Café opening date in the supplied Hirsch event flyer.

The event date remains 4 December 2026. Only the project footer's opening
date changes from 19 to 20 November, following the project lead's correction
on 17 November 2026. Existing artwork, fonts and photo are retained.

Run with Python containing pypdf, pypdfium2 and Pillow. The immutable input
is stored outside the published assets so builds never patch their own output.
"""

from hashlib import sha256
from pathlib import Path

from PIL import ImageChops
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, TextStringObject
import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "print/assets/source-hirsch-04-dez-2026-a4.pdf"
SOURCE_SHA256 = "2f0836992dbb54792897cab615275bdacc3051d369f0200037f668eb58608507"
OUTPUT = ROOT / "assets/events/hirsch-04-dez-2026-a4.pdf"
PREVIEW = OUTPUT.with_suffix(".png")
OLD = "Ab 19. November 2026 am Europaplatz"
NEW = "Ab 20. November 2026 am Europaplatz"


def raster(path):
    with pdfium.PdfDocument(str(path)) as document:
        page = document[0]
        bitmap = page.render(scale=150 / 72)
        image = bitmap.to_pil().convert("RGB")
        bitmap.close()
        page.close()
    return image


def main():
    assert sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    original = PdfReader(SOURCE)
    assert len(original.pages) == 1
    original_text = original.pages[0].extract_text()
    assert original_text.count(OLD) == 1

    writer = PdfWriter(clone_from=SOURCE)
    page = writer.pages[0]
    content = ContentStream(page.get_contents(), writer)
    replaced = 0
    for operands, operator in content.operations:
        if operator == b"Tj" and isinstance(operands[0], str) and OLD in operands[0]:
            # The existing subset font encodes ü as \x01. Preserve that mapping
            # and every other character; only the already-embedded digits change.
            operands[0] = TextStringObject(operands[0].replace(OLD, NEW))
            replaced += 1
    assert replaced == 1, replaced
    page.replace_contents(content)
    writer.write(OUTPUT)

    updated = PdfReader(OUTPUT)
    updated_text = updated.pages[0].extract_text()
    assert updated_text == original_text.replace(OLD, NEW)
    assert updated.pages[0].mediabox == original.pages[0].mediabox
    assert len(updated.pages[0].get("/Annots", [])) == len(original.pages[0].get("/Annots", []))

    before, after = raster(SOURCE), raster(OUTPUT)
    assert before.size == after.size == (1241, 1754)
    difference = ImageChops.difference(before, after)
    bounds = difference.getbbox()
    assert bounds is not None
    # Permit changes only within the two-digit date in the footer, using the
    # unchanged poster's 210 × 297 mm geometry. All other pixels must match.
    allowed = (125, 1535, 225, 1585)
    assert bounds[0] >= allowed[0] and bounds[1] >= allowed[1], bounds
    assert bounds[2] <= allowed[2] and bounds[3] <= allowed[3], bounds
    after.save(PREVIEW, dpi=(150, 150))
    print(f"Updated {OUTPUT.relative_to(ROOT)}; one date replaced.")
    print(f"Preview: {after.width} × {after.height}; changed pixels: {bounds}.")
    print(f"Source SHA-256: {sha256(SOURCE.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
