# A4 and A5 photo flyers in the roll-up design

The copy in `flyer.json` follows the project lead's 14 November 2026 revision:
"Offenes Angebot ab Freitag, 20. November 2026", "Studienphase folgt später."
and all further information on the website. The original A5 source is retained
as `assets/source-lichtmobil-projekt-a5.pdf`. The visual reference is the final Lichtcafé
roll-up v9 / revision 9.1 (11 November 2026, 80 x 200 cm).

The A4 adaptation uses the same continuous pale-yellow background, orange
diagonal stripes that soften downward, yellow title badge, rounded dark petrol
contact panel, two contact cards, QR, bulb motif, and bottom-left institute logo.
The latest user direction explicitly accepts the printer's white margins, so
there is no fade to white at the perimeter and no designed white border.

The two photographs show the exterior (045) and interior in use (073), from the
user-supplied Verena Müller gallery. Both compositions are preserved. They are
exported to sRGB JPEGs with `prepare_flyer_photos.py`; supplied derivatives and
provenance are in `assets/photos/`. One photo credit appears at the bottom.

The continuous mesh shading, logo, icons, type and QR remain vector.
Liberation Sans Regular/Bold are embedded, matching the roll-up.
Fonts and the original institutional logo are supplied in `assets/` with provenance.

## Reproduce

Requirements: Quarto, R with knitr/rmarkdown, Python with ReportLab, Pillow,
NumPy and pypdf, and Poppler (`pdftoppm`). No separate font installation is needed.

From this directory:

```sh
quarto render lichtcafe-a4.qmd
```

The notebook runs `build_flyer.py`, checks the PDF and preview, then embeds the
preview in a standalone HTML file. It uses the installed Codex Python runtime
when present; otherwise it uses `python3`. Set `FLYER_PYTHON` to choose another
Python. To build only the PDF and PNG, run `python3 build_flyer.py` with the
required Python dependencies installed.

Outputs:

- `../output/pdf/lichtcafe-a4-druck.pdf`
- `../output/pdf/lichtcafe-a5-druck.pdf`
- `../output/html/lichtcafe-a4-druck.html`
- `../output/preview/lichtcafe-a4-druck.png`
- `../output/preview/lichtcafe-a5-druck.png`
- `../output/preview/lichtcafe-a4-validation.json`

The build verifies one page per format, every expected text line, identical A4/A5
copy, absence of the old detailed schedule, and a coloured base at all four A4
corners. The A5 version is uniformly scaled from A4, trimming only 0.24 mm of
background at each side. Link annotations are scaled with the page. The QR
encodes `https://wasmachtlicht.de` with a four-module quiet zone. Both PDFs have
300 dpi previews for visual checking. The final PDFs are copied to the website's
`../assets/lichtmobil-projekt-a4.pdf` and `../assets/lichtmobil-projekt-a5.pdf`.

## Print

Choose the matching paper size, portrait. Normal printer margins are acceptable. Use fit-to-printable-
area if you want the complete artwork inside the printer's printable area.
