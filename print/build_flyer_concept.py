#!/usr/bin/env python3
"""Build only the new A4 concept edition; never overwrite earlier flyers.

The campaign background, icon paths and embedded fonts are shared with the
original builder. Its main/build functions are deliberately never called.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from build_flyer import draw_background, find_poppler, icon, register_fonts

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = json.loads((HERE / "flyer-concept.json").read_text(encoding="utf-8"))
PDF = ROOT / "output/pdf/lichtcafe-a4-konzept.pdf"
PREVIEW = ROOT / "output/preview/lichtcafe-a4-konzept.png"
VALIDATION = ROOT / "output/preview/lichtcafe-a4-konzept-validation.json"
MAP = ROOT / "output/pdf/lichtcafe-standortkarte.pdf"
MAP_URL = "https://www.google.com/maps?q=48.5171469,9.0566625"
TEMP = ROOT / "tmp/pdfs/a4-concept"
INK, TEAL = HexColor("#103D3A"), HexColor("#007F78")
ACCENT, CREAM = HexColor("#FFE894"), HexColor("#FFFCF2")
WIDTH, HEIGHT = A4


def build():
    for directory in (PDF.parent, PREVIEW.parent, TEMP):
        directory.mkdir(parents=True, exist_ok=True)
    register_fonts()
    raw = TEMP / "before-logo.pdf"
    c = canvas.Canvas(str(raw), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle("Das Lichtcafé - A4-Flyer mit Konzepterklärung")
    c.setAuthor("Was macht Licht? / Max-Planck-Institut für biologische Kybernetik")
    c.setSubject("Mobiler Forschungstrailer: offenes Angebot ab 20. November 2026")
    draw_background(c)
    bounds = []

    def text(value, y, size, bold=False, x=16, colour=INK):
        font = "Campaign-Bold" if bold else "Campaign"
        width = pdfmetrics.stringWidth(value, font, size) / mm
        assert x >= 16 and x + width <= 194.01, (value, x + width)
        c.setFont(font, size)
        c.setFillColor(colour)
        c.drawString(x * mm, HEIGHT - y * mm, value)
        bounds.append({"text": value, "x_mm": x, "baseline_from_top_mm": y,
                       "width_mm": round(width, 3), "size_pt": size})

    def rounded(x, y, width, height, radius, colour):
        c.setFillColor(colour)
        c.roundRect(x * mm, HEIGHT - (y + height) * mm, width * mm,
                    height * mm, radius * mm, fill=1, stroke=0)

    c.setFillColor(TEAL)
    c.circle(18.3 * mm, HEIGHT - 17.4 * mm, 2.3 * mm, fill=1, stroke=0)
    c.setStrokeColor(CREAM)
    c.setLineWidth(.65 * mm)
    c.line(17.4 * mm, HEIGHT - 18.6 * mm, 19.2 * mm, HEIGHT - 16.2 * mm)
    text(DATA["brand"], 19, 12, bold=True, x=24.5)
    rounded(16, 29, 72, 10, 1.8, HexColor("#FFD52D"))
    text(DATA["kicker"], 36.3, 12, bold=True, x=20)
    text(DATA["headline"][0], 56, 54, bold=True)
    text(DATA["headline"][1], 77, 54, bold=True)

    # Short columns align with the photographs and separate context from research.
    for block, x in zip(DATA["concept_blocks"], (16, 108)):
        text(block["title"], 86, 14, bold=True, x=x)
        assert pdfmetrics.stringWidth(block["title"], "Campaign-Bold", 14) / mm <= 86
        for i, line in enumerate(block["lines"]):
            assert pdfmetrics.stringWidth(line, "Campaign", 13) / mm <= 86
            text(line, 93.4 + i * 5.5, 13, x=x)

    for photo, x in zip(DATA["photos"], (16, 108)):
        c.drawImage(str(HERE / "assets/photos" / photo["file"]),
                    x * mm, HEIGHT - (116 + 86 * 2 / 3) * mm,
                    width=86 * mm, height=86 * 2 / 3 * mm)
        text(photo["caption"], 179, 10, x=x)

    text(DATA["offer"], 190, 13)
    text(DATA["start_date"], 199.5, 19, bold=True)
    text(DATA["place"], 208, 13)
    text(DATA["study"], 216, 12)
    # The exact-location vector map replaces the decorative bulb.
    location = PdfReader(MAP).pages[0]
    map_scale = 66 * mm / float(location.mediabox.width)
    map_height_mm = float(location.mediabox.height) * map_scale / mm
    assert map_height_mm <= 43.01, "Map must fit beside the visit information"
    rounded(127.5, 181.5, 67, map_height_mm + 1, 1.5, CREAM)
    c.linkURL(MAP_URL, (128 * mm, HEIGHT - (182 + map_height_mm) * mm,
                        194 * mm, HEIGHT - 182 * mm), relative=0)

    rounded(8, 230, 194, 43, 4.5, INK)
    text(DATA["contact"], 235.5, 12, bold=True, colour=ACCENT)
    rounded(16, 245, 127, 18, 1.8, ACCENT)
    icon(c, "link", 20, 251, 6)
    text(DATA["website"], 256.5, 22, bold=True, x=30)
    c.linkURL(DATA["url"], (16 * mm, HEIGHT - 263 * mm,
                           143 * mm, HEIGHT - 245 * mm), relative=0)

    code = QRCode(version=None, errorCorrectLevel=QRErrorCorrectLevel.M)
    code.addData(DATA["url"])
    code.make()
    count, quiet, extent = code.getModuleCount(), 4, 30
    cell = extent * mm / (count + 2 * quiet)
    qx, qtop = 159, 239
    c.setFillColor(white)
    c.rect(qx * mm, HEIGHT - (qtop + extent) * mm,
           extent * mm, extent * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    for row in range(count):
        for col in range(count):
            if code.isDark(row, col):
                c.rect(qx * mm + (col + quiet) * cell,
                       HEIGHT - qtop * mm - (row + quiet + 1) * cell,
                       cell, cell, stroke=0, fill=1)
    text(DATA["qr_label"], 235.5, 10, bold=True, x=159, colour=ACCENT)
    c.linkURL(DATA["url"], (qx * mm, HEIGHT - (qtop + extent) * mm,
                           (qx + extent) * mm, HEIGHT - qtop * mm), relative=0)
    c.showPage()
    c.save()

    reader = PdfReader(raw)
    logo = PdfReader(HERE / "assets/mpi-logo.pdf").pages[0]
    factor = 44 * mm / float(logo.mediabox.width)
    logo_height = float(logo.mediabox.height) * factor
    reader.pages[0].merge_transformed_page(logo, Transformation().scale(factor).translate(
        16 * mm, HEIGHT - 276 * mm - logo_height))
    reader.pages[0].merge_transformed_page(location, Transformation().scale(map_scale).translate(
        128 * mm, HEIGHT - (182 + map_height_mm) * mm))
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    writer.add_metadata({str(k): str(v) for k, v in reader.metadata.items()})
    with PDF.open("wb") as stream:
        writer.write(stream)

    result = PdfReader(PDF)
    assert len(result.pages) == 1
    page = result.pages[0]
    assert abs(float(page.mediabox.width) - WIDTH) < .01
    assert abs(float(page.mediabox.height) - HEIGHT) < .01
    extracted = page.extract_text()
    for item in bounds:
        assert item["text"] in extracted, item["text"]
    for absent in ("Verena", "Müller", "Fotos:", "30. November", "23.–27.", "07:00", "ERÖFFNUNG", "@"):
        assert absent not in extracted, absent
    assert len(page.images) == 2, "Expected precisely the two chosen photographs"
    links = [ref.get_object()["/A"]["/URI"] for ref in page.get("/Annots", [])]
    assert links == [MAP_URL, DATA["url"], DATA["url"]], links
    report = {"pages": 1, "page_mm": [210, 297], "photos": DATA["photos"],
              "photo_credit_present": False, "email_present": False, "qr_extent_mm": extent,
              "qr_url": DATA["url"], "qr_quiet_modules": quiet,
              "contact_gap_after_study_baseline_mm": 14,
              "concept_column_width_mm": 86, "concept_body_size_pt": 13,
              "concept_leading_pt": round(5.5 * mm, 2),
              "type_sizes_pt": sorted({item["size_pt"] for item in bounds}),
              "map": {"pin": [48.5171469, 9.0566625], "url": MAP_URL,
                      "box_mm": [128, 182, 66, round(map_height_mm, 3)]},
              "content": bounds, "links": links}
    VALIDATION.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([find_poppler(), "-r", str(DATA["raster_dpi"]), "-png", "-singlefile",
                    str(PDF), str(PREVIEW.with_suffix(""))], check=True)
    print(f"Created and validated {PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
