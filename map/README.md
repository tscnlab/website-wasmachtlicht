# Lichtcafé location map

This isolated Quarto notebook produces a 66 × 43 mm vector map for the flyer.

```sh
quarto render map/location.qmd
```

Or run `python3 map/build_map.py` directly. Set `MAP_PYTHON` for Quarto when Python is not on PATH. Dependencies: ReportLab, Arial fonts discoverable by `fc-match`, and Poppler `pdftoppm`.

Rendering is offline and reproducible from `data/location.osm`. The single original request was the public OSM map API bounding-box endpoint recorded in `data/provenance.json`. Data © OpenStreetMap contributors, ODbL; see https://www.openstreetmap.org/copyright. Attribution remains visible within the printable artwork.

The marker tip uses the supplied coordinate exactly. Simplified cartography preserves the stored geometry; no walking route is inferred. Verified landmark references: Hauptbahnhof building way 24796099; station forecourt / bus station area way 1159357124; Neckar water relation 161200.

“Europaplatz” is an area label centred at 9.0557° E, 48.51645° N in the station forecourt / ZOB, checked against the [official city plan](https://www.tuebingen.de/gemeinderat/getfile.php?id=99136&type=do) and the [city's description](https://www.tuebingen.de/europaplatz/). The former fixed display position was too far east. The nearby street of the same name is not used as the anchor for this area label. Coordinates and verification sources are recorded in `data/provenance.json`.

Outputs: `output/pdf/lichtcafe-standortkarte.pdf`, `output/preview/lichtcafe-standortkarte.png`, and `map/output/lichtcafe-standortkarte.svg`. The PDF has no annotation or raster images. Preserve 66 mm width when embedding; the resulting height is 43 mm.
