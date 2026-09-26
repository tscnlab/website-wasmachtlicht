"""Preserve HTML5 standards mode after Quarto 1.6's HTML postprocessing."""
from pathlib import Path

for page in Path("dist").rglob("*.html"):
    html = page.read_text(encoding="utf-8")
    if not html.lstrip().lower().startswith("<!doctype html>"):
        page.write_text("<!doctype html>\n" + html, encoding="utf-8")
