# Lichtcafé location map

This isolated Quarto notebook produces a 66 × 43 mm vector map for the flyer.

```sh
quarto render map/location.qmd
```

Or run `python3 map/build_map.py` directly. Set `MAP_PYTHON` for Quarto when Python is not on PATH. Dependencies: ReportLab, Arial fonts discoverable by `fc-match`, and Poppler `pdftoppm`.

Rendering is offline and reproducible from `data/location.osm`. The single original request was the public OSM map API bounding-box endpoint recorded in `data/provenance.json`. Data © OpenStreetMap contributors, ODbL; see https://www.openstreetmap.org/copyright. Attribution remains visible within the printable artwork.

The marker tip uses the supplied coordinate exactly. Simplified cartography preserves the stored geometry; no walking route is inferred. Verified landmark references: Hauptbahnhof building way 24796099; Europaplatz way 379070072; Neckar water relation 161200.

Outputs: `output/pdf/lichtcafe-standortkarte.pdf`, `output/preview/lichtcafe-standortkarte.png`, and `map/output/lichtcafe-standortkarte.svg`. The PDF has no annotation or raster images. Preserve 66 mm width when embedding; the resulting height is 43 mm.
