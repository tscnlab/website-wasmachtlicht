"""Check the exported static site using only Python's standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / "dist"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.refs = path, set(), []
        self.h1, self.lang = 0, None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate id in {self.path}: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "img":
            assert attrs.get("alt"), f"Missing image description in {self.path}"
        for attribute in ("href", "src"):
            if attribute in attrs:
                self.refs.append(attrs[attribute])


pages = {p.resolve(): Page(p) for p in ROOT.rglob("*.html")}
for route, expected_lang in {"index.html": "de", "en/index.html": "en"}.items():
    path = (ROOT / route).resolve()
    assert path in pages, f"Missing required page: {route}"
    assert pages[path].lang == expected_lang, f"Incorrect language for {route}"
for path, page in pages.items():
    assert path.read_text().lower().startswith("<!doctype html>"), f"Missing doctype: {path}"
    assert page.h1 == 1 and page.lang in ("de", "en"), f"Invalid document structure: {path}"
    for ref in page.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if target.is_dir():
            target /= "index.html"
        assert target.exists(), f"Broken local reference: {path.name} -> {ref}"
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f"Missing anchor: {ref}"
print(f"Checked {len(pages)} pages: HTML5, languages, headings, image descriptions, local files and anchors OK.")
