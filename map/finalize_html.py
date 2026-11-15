"""Remove incidental whitespace from Quarto's generated HTML scripts."""
from pathlib import Path

page = Path(__file__).resolve().parent / "output/location.html"
page.write_text(
    "\n".join(line.rstrip() for line in page.read_text(encoding="utf-8").splitlines()) + "\n",
    encoding="utf-8",
)
