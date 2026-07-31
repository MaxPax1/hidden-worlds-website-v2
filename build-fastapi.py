#!/usr/bin/env python3
"""Regenerate terms-viewer.html and fastapi-build/ from the root static site.

Run this after ANY change to index.html or story-card.html:

    python build-fastapi.py

What it does
  1. Derives terms-viewer.html (root) from index.html: the Terms/Privacy modal
     baked open at first paint, so an outside link can deep-link the legal text.
  2. Builds fastapi-build/templates/{index,story-card,terms-viewer}.html from the
     three root pages, rewiring asset paths to /static/ and internal links to routes.
  3. Copies only the assets those pages actually reference into
     fastapi-build/static/assets/ (unused art is not shipped).

Everything is derived. Never hand-edit fastapi-build/ or terms-viewer.html.
"""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
BUILD = ROOT / "fastapi-build"

# The public origin of the FastAPI service, used for absolute og:image URLs.
# Change this if the service is served from a different domain.
ORIGIN = "https://hiddenworlds.travel"

TERMS_URL = f"{ORIGIN}/terms"

# ── 1 · terms-viewer.html (root, relative paths) ───────────────────────────────

VIEWER_SCRIPT = """
<script>
// terms-viewer: the modal is baked open in the HTML above so an outside link (the
// WhatsApp onboarding message) lands on the live homepage with the legal text
// already open over it. Closing it drops the visitor onto the homepage.
// ?tc=privacy opens straight to the privacy section.
(function () {
  document.body.style.overflow = 'hidden';
  var frame = document.getElementById('tc-frame');
  var params = new URLSearchParams(location.search);
  if (frame && params.get('tc') === 'privacy'){
    frame.src = 'TERMS_URL_PLACEHOLDER#privacy';
  }
  var close = document.getElementById('tc-close');
  if (close) close.focus();
})();
</script>
"""


def make_terms_viewer(index_html: str) -> str:
    out = index_html.replace(
        '<div class="overlay" id="tc-overlay" aria-hidden="true">',
        '<div class="overlay open" id="tc-overlay" aria-hidden="false">',
    )
    out = out.replace(
        '<iframe id="tc-frame" title="Terms of Service and Privacy Policy" src="about:blank">',
        f'<iframe id="tc-frame" title="Terms of Service and Privacy Policy" src="{TERMS_URL}#terms">',
    )
    title = "Hidden Worlds &mdash; Terms &amp; Privacy"
    out = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", out, count=1, flags=re.S)
    script = VIEWER_SCRIPT.replace("TERMS_URL_PLACEHOLDER", TERMS_URL)
    out = out.replace("</body>", script + "</body>", 1)
    assert 'class="overlay open"' in out, "modal was not baked open"
    assert f'src="{TERMS_URL}#terms"' in out, "iframe src was not set"
    return out


# ── 2 · path rewiring for the FastAPI templates ────────────────────────────────

OG_IMAGES = {
    "index.html": "assets/hero-aerial.jpg",
    "story-card.html": "assets/card-front.jpg",
    "terms-viewer.html": "assets/hero-aerial.jpg",
}


def to_template(html: str, page: str) -> str:
    # og:image must be absolute for crawlers, so it is rewritten before the
    # general asset rewrite below.
    og = OG_IMAGES.get(page)
    if og:
        html = html.replace(f'content="{og}"', f'content="{ORIGIN}/static/{og}"')

    # assets -> /static/assets  (href=, src=, content=, and CSS url())
    html = re.sub(r'((?:href|src|content)=")assets/', r"\1/static/assets/", html)
    html = html.replace("url('assets/", "url('/static/assets/")

    # internal page links -> routes
    html = html.replace('href="story-card.html"', 'href="/story-card"')
    html = html.replace('href="terms-viewer.html"', 'href="/terms-viewer"')
    html = html.replace('href="index.html"', 'href="/"')

    assert '="assets/' not in html, "an un-rewired asset path remains"
    assert "url('assets/" not in html, "an un-rewired CSS asset path remains"
    assert ".html" not in html.replace("terms-viewer.html", ""), "an un-rewired page link remains"
    assert "{{" not in html and "}}" not in html, "a template token remains"
    return html


def referenced_assets(pages: dict) -> set:
    names = set()
    for html in pages.values():
        names |= set(re.findall(r"/static/assets/([A-Za-z0-9._-]+)", html))
    return names


def main():
    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    story_html = (ROOT / "story-card.html").read_text(encoding="utf-8")

    viewer_html = make_terms_viewer(index_html)
    (ROOT / "terms-viewer.html").write_text(viewer_html, encoding="utf-8", newline="")
    print("wrote terms-viewer.html")

    pages = {
        "index.html": to_template(index_html, "index.html"),
        "story-card.html": to_template(story_html, "story-card.html"),
        "terms-viewer.html": to_template(viewer_html, "terms-viewer.html"),
    }

    templates = BUILD / "templates"
    static_assets = BUILD / "static" / "assets"
    for d in (templates, static_assets):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    for name, html in pages.items():
        (templates / name).write_text(html, encoding="utf-8", newline="")
        print(f"wrote fastapi-build/templates/{name}")

    used = referenced_assets(pages)
    have = {p.name for p in (ROOT / "assets").iterdir() if p.is_file()}
    missing = used - have
    assert not missing, f"referenced but missing from assets/: {sorted(missing)}"
    for name in sorted(used):
        shutil.copy2(ROOT / "assets" / name, static_assets / name)
    print(f"copied {len(used)} assets to fastapi-build/static/assets/")
    unused = sorted(have - used)
    if unused:
        print("not shipped (unreferenced):", ", ".join(unused))


if __name__ == "__main__":
    main()
