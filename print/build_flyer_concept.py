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
    text(DATA["brand"], 19, 11.2, bold=True, x=24.5)
    rounded(16, 29, 72, 10, 1.8, HexColor("#FFD52D"))
    text(DATA["kicker"], 36.3, 12, bold=True, x=20)
    text(DATA["headline"][0], 56, 54, bold=True)
    text(DATA["headline"][1], 77, 54, bold=True)

    # Five lines connect shorter days, morning light, the visit and the research.
    for i, line in enumerate(DATA["concept_lines"]):
        text(line, 87.2 + i * 5.65, 13.3)

    for photo, x in zip(DATA["photos"], (16, 108)):
        c.drawImage(str(HERE / "assets/photos" / photo["file"]),
                    x * mm, HEIGHT - (116 + 86 * 2 / 3) * mm,
                    width=86 * mm, height=86 * 2 / 3 * mm)
        text(photo["caption"], 179, 10, x=x)

    text(DATA["offer"], 190, 15.3, bold=True)
    text(DATA["start_date"], 199.5, 19, bold=True)
    text(DATA["place"], 208, 13.3, bold=True)
    text(DATA["study"], 216, 12, bold=True)
    text(DATA["website_hint"], 222, 11.5)
    c.setFillColor(ACCENT)
    c.circle(174 * mm, HEIGHT - 201 * mm, 13 * mm, fill=1, stroke=0)
    icon(c, "bulb", 163.5, 201 - 21 * 11.25 / 24, 21)

    rounded(8, 230, 194, 43, 4.5, INK)
    text(DATA["contact"], 235.5, 10, bold=True, colour=ACCENT)
    rounded(16, 239, 127, 13.5, 1.8, ACCENT)
    rounded(16, 255.5, 127, 13.5, 1.8, CREAM)
    icon(c, "link", 20, 242.75, 6)
    icon(c, "mail", 20, 259.25, 6)
    text(DATA["website"], 248, 19, bold=True, x=30)
    text(DATA["email"], 264, 12.8, x=30)
    c.linkURL(DATA["url"], (16 * mm, HEIGHT - 252.5 * mm,
                           143 * mm, HEIGHT - 239 * mm), relative=0)
    c.linkURL("mailto:" + DATA["email"], (16 * mm, HEIGHT - 269 * mm,
                                        143 * mm, HEIGHT - 255.5 * mm), relative=0)

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
    text(DATA["qr_label"], 235.5, 10, bold=True, x=162.5, colour=ACCENT)
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
    for absent in ("Verena", "Müller", "Fotos:", "30. November", "23.–27.", "07:00", "ERÖFFNUNG"):
        assert absent not in extracted, absent
    assert len(page.images) == 2, "Expected precisely the two chosen photographs"
    links = [ref.get_object()["/A"]["/URI"] for ref in page.get("/Annots", [])]
    assert links == [DATA["url"], "mailto:" + DATA["email"], DATA["url"]], links
    report = {"pages": 1, "page_mm": [210, 297], "photos": DATA["photos"],
              "photo_credit_present": False, "qr_extent_mm": extent,
              "qr_url": DATA["url"], "qr_quiet_modules": quiet,
              "contact_gap_after_hint_baseline_mm": 8, "content": bounds, "links": links}
    VALIDATION.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([find_poppler(), "-r", str(DATA["raster_dpi"]), "-png", "-singlefile",
                    str(PDF), str(PREVIEW.with_suffix(""))], check=True)
    print(f"Created and validated {PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
