#!/usr/bin/env python3
"""Build A4 and A5 photo flyers in the design of roll-up v9.

Stripes, type, icons, QR and logo stay vector; supplied photographs use sRGB.
The design extends to the page edges without a white perimeter fade.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import struct
import subprocess

import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ArrayObject, FloatObject, NameObject
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfdoc, pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = json.loads((HERE / "flyer.json").read_text(encoding="utf-8"))
OUT = ROOT / "output"
TEMP = ROOT / "tmp" / "pdfs" / "a4-flyer"
PDF = OUT / "pdf" / "lichtcafe-a4-druck.pdf"
PDF_A5 = OUT / "pdf" / "lichtcafe-a5-druck.pdf"
PREVIEW = OUT / "preview" / "lichtcafe-a4-druck.png"
INK = HexColor("#103D3A")
TEAL = HexColor("#007F78")
ACCENT = HexColor("#FFE894")
CREAM = HexColor("#FFFCF2")
WIDTH, HEIGHT = A4


def draw_background(c):
    """Reuse roll-up v9's continuous stripe shading at A4 proportions."""
    c.saveState()
    c.scale(mm, mm)
    w, h = 210, 297
    pitch, stripe_width = 44 * w / 800, 12 * w / 800
    base, orange = HexColor("#FFF5D4"), HexColor("#F48432")
    c.setFillColor(base)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    region = c.beginPath()
    region.rect(0, 0, w, h)
    c.clipPath(region, stroke=0, fill=0)
    stripes = c.beginPath()
    for i in range(-2, math.ceil((w + h) / pitch) + 2):
        intercept = i * pitch
        stripes.moveTo(intercept - h, 0)
        stripes.lineTo(intercept - h + stripe_width, 0)
        stripes.lineTo(intercept + stripe_width, h)
        stripes.lineTo(intercept, h)
        stripes.close()
    c.clipPath(stripes, stroke=0, fill=0)
    nx, ny = 33, 85
    vertices = bytearray()
    for row in range(ny):
        y = row / (ny - 1)
        for col in range(nx):
            x = col / (nx - 1)
            strength = .78 * (.12 + .88 * x * x) * (1 - y) ** 2
            colours = [b - strength * (b - o) for b, o in zip(
                (base.red, base.green, base.blue), (orange.red, orange.green, orange.blue))]
            vertices.extend(struct.pack(">HHHHH", round(x * 65535), round((1 - y) * 65535),
                                        *[round(v * 65535) for v in colours]))
    c.shade(pdfdoc.PDFStream(pdfdoc.PDFDictionary({
        "ShadingType": 5, "ColorSpace": pdfdoc.PDFName("DeviceRGB"),
        "BitsPerCoordinate": 16, "BitsPerComponent": 16, "VerticesPerRow": nx,
        "Decode": pdfdoc.PDFArray([0, w, 0, h, 0, 1, 0, 1, 0, 1])
    }), bytes(vertices)))
    c.restoreState()


def icon(c, kind, x, y, size, colour=INK):
    """Original roll-up icon paths, on its shared 24-unit grid."""
    if kind == "link":
        paths = [
            [("M",10,13),("C",11.5,14.5,13.9,14.5,15.4,13),("L",18.4,10),
             ("C",20,8.4,20,5.8,18.4,4.2),("C",16.8,2.6,14.2,2.6,12.6,4.2),("L",11,5.8)],
            [("M",14,11),("C",12.5,9.5,10.1,9.5,8.6,11),("L",5.6,14),
             ("C",4,15.6,4,18.2,5.6,19.8),("C",7.2,21.4,9.8,21.4,11.4,19.8),("L",13,18.2)]]
    elif kind == "bulb":
        paths = [
            [("M",9,18),("C",9,15.7,8.4,14.8,7.5,13.6),("C",6.4,12.2,6,10.9,6,9.4),
             ("C",6,6.1,8.6,3.6,12,3.6),("C",15.4,3.6,18,6.1,18,9.4),
             ("C",18,10.9,17.6,12.2,16.5,13.6),("C",15.6,14.8,15,15.7,15,18),("Z",)],
            [("M",9.3,10.5),("L",12,13),("L",14.7,10.5)],[("M",12,13),("L",12,18)],
            [("M",9.5,20.3),("L",14.5,20.3)],[("M",10.5,22.5),("L",13.5,22.5)],
            [("M",12,0),("L",12,1.5)],[("M",3.3,2.7),("L",4.7,4.1)],
            [("M",20.7,2.7),("L",19.3,4.1)],[("M",1,9),("L",2.8,9)],[("M",23,9),("L",21.2,9)]]
    else:
        paths = [[("M",3,5),("L",21,5),("L",21,19),("L",3,19),("Z",)],
                 [("M",3,6),("L",12,13),("L",21,6)]]
    scale = size / 24
    c.saveState()
    c.setStrokeColor(colour)
    c.setLineWidth((1.1 if kind == "bulb" else 1.8) * scale * mm)
    c.setLineCap(1)
    c.setLineJoin(1)
    for commands in paths:
        path = c.beginPath()
        for operation, *values in commands:
            points = [((x + values[i] * scale) * mm, HEIGHT - (y + values[i + 1] * scale) * mm)
                      for i in range(0, len(values), 2)]
            if operation == "M": path.moveTo(*points[0])
            elif operation == "L": path.lineTo(*points[0])
            elif operation == "C": path.curveTo(*[n for point in points for n in point])
            elif operation == "Z": path.close()
        c.drawPath(path, fill=0, stroke=1)
    c.restoreState()


def register_fonts():
    for name, filename in (("Campaign", "LiberationSans-Regular.ttf"),
                           ("Campaign-Bold", "LiberationSans-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(HERE / "assets" / filename)))


def build_pdf():
    raw = TEMP / "flyer-before-logo.pdf"
    c = canvas.Canvas(str(raw), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle("Das Lichtcafé in Tübingen - A4-Druckflyer")
    c.setAuthor("Was macht Licht? / Max-Planck-Institut für biologische Kybernetik")
    c.setSubject("A4-Adaption des Lichtcafé-Roll-ups, Gestaltung v9")
    draw_background(c)
    text_bounds = []

    def text(value, y, size, bold=False, x=16, colour=INK):
        font = "Campaign-Bold" if bold else "Campaign"
        width = pdfmetrics.stringWidth(value, font, size) / mm
        assert x >= 16 and x + width <= 194.01, (value, x + width)
        c.setFont(font, size)
        c.setFillColor(colour)
        c.drawString(x * mm, HEIGHT - y * mm, value)
        text_bounds.append({"text": value, "x_mm": x, "baseline_from_top_mm": y,
                            "width_mm": round(width, 3), "size_pt": size})

    def rounded(x, y, width, height, radius, colour):
        c.setFillColor(colour)
        c.roundRect(x * mm, HEIGHT - (y + height) * mm, width * mm, height * mm,
                    radius * mm, fill=1, stroke=0)

    c.setFillColor(TEAL)
    c.circle(18.3 * mm, HEIGHT - 17.4 * mm, 2.3 * mm, fill=1, stroke=0)
    c.setStrokeColor(CREAM)
    c.setLineWidth(.65 * mm)
    c.line(17.4 * mm, HEIGHT - 18.6 * mm, 19.2 * mm, HEIGHT - 16.2 * mm)
    text(DATA["brand"], 19, 11.2, bold=True, x=24.5)

    rounded(16, 29, 72, 10, 1.8, HexColor("#FFD52D"))
    text(DATA["kicker"], 36.3, 12, bold=True, x=20)
    text(DATA["headline"][0], 61, 60, bold=True)
    text(DATA["headline"][1], 84, 60, bold=True)
    text(DATA["subtitle"], 97, 14.4)

    # Full compositions: one exterior and one interior, sized for both formats.
    for photo, x in zip(DATA["photos"], (16, 108)):
        c.drawImage(str(HERE / "assets/photos" / photo["file"]),
                    x * mm, HEIGHT - (109 + 86 * 2 / 3) * mm,
                    width=86 * mm, height=86 * 2 / 3 * mm)
        text(photo["caption"], 172.3, 10, x=x)

    text(DATA["offer"], 186, 18.3, bold=True)
    text(DATA["start_date"], 197, 19, bold=True)
    text(DATA["place"], 207, 13.3, bold=True)
    text(DATA["study"], 218, 12.5, bold=True)
    text(DATA["website_hint"], 226, 11.8)
    c.setFillColor(ACCENT)
    c.circle(174 * mm, HEIGHT - 202 * mm, 15 * mm, fill=1, stroke=0)
    icon(c, "bulb", 162, 202 - 24 * 11.25 / 24, 24)

    rounded(8, 230, 194, 43, 4.5, INK)
    text(DATA["contact"], 235.5, 10, bold=True, colour=ACCENT)
    rounded(16, 239, 127, 13.5, 1.8, ACCENT)
    rounded(16, 255.5, 127, 13.5, 1.8, CREAM)
    icon(c, "link", 20, 242.75, 6)
    icon(c, "mail", 20, 259.25, 6)
    text(DATA["website"], 248, 19, bold=True, x=30)
    text(DATA["email"], 264, 12.8, x=30)
    c.linkURL(DATA["url"], (16 * mm, HEIGHT - 252.5 * mm, 143 * mm, HEIGHT - 239 * mm), relative=0)
    c.linkURL("mailto:" + DATA["email"], (16 * mm, HEIGHT - 269 * mm, 143 * mm, HEIGHT - 255.5 * mm), relative=0)

    # Four-module quiet zone; all QR modules remain vectors.
    code = QRCode(version=None, errorCorrectLevel=QRErrorCorrectLevel.M)
    code.addData(DATA["url"])
    code.make()
    count, quiet, extent = code.getModuleCount(), 4, 30
    cell = extent * mm / (count + 2 * quiet)
    qx, qtop = 159, 239
    c.setFillColor(white)
    c.rect(qx * mm, HEIGHT - (qtop + extent) * mm, extent * mm, extent * mm, fill=1, stroke=0)
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

    text(DATA["photo_credit"], 287.5, 10, x=155)
    c.showPage()
    c.save()

    # Place the original institutional logo as transparent vector artwork.
    reader = PdfReader(raw)
    logo = PdfReader(HERE / "assets" / "mpi-logo.pdf").pages[0]
    factor = 44 * mm / float(logo.mediabox.width)
    logo_height = float(logo.mediabox.height) * factor
    reader.pages[0].merge_transformed_page(logo, Transformation().scale(factor).translate(
        16 * mm, HEIGHT - 276 * mm - logo_height))
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    writer.add_metadata({str(k): str(v) for k, v in reader.metadata.items()})
    with PDF.open("wb") as stream:
        writer.write(stream)
    return text_bounds


def build_a5():
    """Uniformly reduce A4, trimming only 0.24 mm of background at each side."""
    reader = PdfReader(PDF)
    factor = A5[1] / A4[1]
    offset = (A5[0] - A4[0] * factor) / 2
    source = reader.pages[0]
    source.add_transformation(Transformation().scale(factor).translate(offset, 0))
    source.mediabox.lower_left = (0, 0)
    source.mediabox.upper_right = A5
    source.cropbox.lower_left = (0, 0)
    source.cropbox.upper_right = A5
    # Link rectangles do not follow content-stream transforms automatically.
    for reference in source.get("/Annots", []):
        annotation = reference.get_object()
        left, bottom, right, top = annotation["/Rect"]
        annotation[NameObject("/Rect")] = ArrayObject([FloatObject(float(left) * factor + offset),
            FloatObject(float(bottom) * factor), FloatObject(float(right) * factor + offset),
            FloatObject(float(top) * factor)])
    writer = PdfWriter()
    writer.add_page(source)
    writer.add_metadata({"/Title": "Das Lichtcafé in Tübingen - A5-Flyer",
        "/Author": "Was macht Licht? / Max-Planck-Institut für biologische Kybernetik"})
    with PDF_A5.open("wb") as stream:
        writer.write(stream)


def find_poppler():
    result = shutil.which("pdftoppm")
    if result:
        return result
    bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"
    if bundled.is_file():
        return str(bundled)
    raise FileNotFoundError("pdftoppm (Poppler) is required to render the preview.")


def verify(text_bounds):
    reader = PdfReader(PDF)
    assert len(reader.pages) == 1, "Flyer must have exactly one page"
    box = reader.pages[0].mediabox
    assert abs(float(box.width) - WIDTH) < 0.01
    assert abs(float(box.height) - HEIGHT) < 0.01
    extracted = reader.pages[0].extract_text()
    for item in text_bounds:
        assert item["text"] in extracted, f"Missing text: {item['text']}"
    for old in ("30. November", "23.–27.", "07:00", "ERÖFFNUNG"):
        assert old not in extracted, f"Old scheduling copy remains: {old}"
    a5 = PdfReader(PDF_A5)
    assert len(a5.pages) == 1
    assert abs(float(a5.pages[0].mediabox.width) - A5[0]) < .01
    assert abs(float(a5.pages[0].mediabox.height) - A5[1]) < .01
    assert a5.pages[0].extract_text() == extracted
    rgb = np.asarray(Image.open(PREVIEW).convert("RGB"))
    # Verify the pale-yellow base now reaches all four corners; no white fade.
    corners = [rgb[y, x].tolist() for y, x in ((2, 2), (2, -3), (-3, 2), (-3, -3))]
    assert all(pixel[2] < 240 for pixel in corners), corners
    report = {"pages": 1, "page_mm": [210, 297], "design_reference": "rollup-v9",
              "edge_fade": False, "corner_rgb": corners, "raster_dpi": DATA["raster_dpi"],
              "qr_url": DATA["url"], "qr_extent_mm": 30, "photos": DATA["photos"],
              "a5_page_mm": [148, 210], "a5_qr_extent_mm": 30 * A5[1] / A4[1], "content": text_bounds}
    (OUT / "preview" / "lichtcafe-a4-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {PDF.relative_to(ROOT)}; one A4 page; roll-up v9 design; content verified.")


def main():
    for directory in (PDF.parent, PREVIEW.parent, TEMP):
        directory.mkdir(parents=True, exist_ok=True)
    register_fonts()
    text_bounds = build_pdf()
    build_a5()
    subprocess.run([find_poppler(), "-r", str(DATA["raster_dpi"]), "-png", "-singlefile",
                    str(PDF), str(PREVIEW.with_suffix(""))], check=True)
    verify(text_bounds)
    subprocess.run([find_poppler(), "-r", str(DATA["raster_dpi"]), "-png", "-singlefile",
                    str(PDF_A5), str(OUT / "preview/lichtcafe-a5-druck")], check=True)


if __name__ == "__main__":
    main()
