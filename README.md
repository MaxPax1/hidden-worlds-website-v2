# Hidden Worlds — landing page (v2)

Two builds of the same landing page live here.

## Repo root — the static site (preview)

Plain HTML, one inline `<style>`, ~60 lines of vanilla JS. No design-system
runtime, no build step, no framework. Only external dependency: Google Fonts
(Newsreader).

- **Live preview:** https://maxpax1.github.io/hidden-worlds-website-v2/
- **Pages setting:** Settings → Pages → **Source: GitHub Actions**
  (`.github/workflows/pages.yml`). Deploys land in about a minute.
  `.nojekyll` is kept.
- Pages: `index.html` (`/`), `story-card.html` (Season 1 / Story Card),
  `terms-viewer.html` (homepage with the Terms/Privacy modal already open, for
  deep-linking the legal text from the WhatsApp onboarding message).

Local preview:

```
python -m http.server 8000
```

## `fastapi-build/` — the hosting build (hand this to the team)

The page prepared for the Hidden Worlds FastAPI/forge service: `templates/` +
`static/`, asset paths rewired to `/static/`, internal links pointing at routes,
no template tokens. **See [`fastapi-build/INTEGRATION.md`](fastapi-build/INTEGRATION.md)**
for the static mount, the three routes to add (`GET /`, `GET /story-card`,
`GET /terms-viewer`), and the items to confirm before deploying.

This is the version to deploy. The static site at the repo root is the preview.

## Regenerating the derived files

`fastapi-build/` and `terms-viewer.html` are **generated, never hand-edited**.
After changing `index.html` or `story-card.html`:

```
python build-fastapi.py
```

The script rewires paths, rebuilds all three templates, ships only referenced
assets, and asserts nothing was missed. This is what stopped the previous build
from drifting out of sync with the preview.

---

### Notes

- WhatsApp number is hard-coded: `wa.me/385998427803` (6 places across the two
  pages; search and replace to change).
- The legal notice under the WhatsApp CTAs opens a Terms/Privacy modal that
  iframes `https://hiddenworlds.travel/terms`. The nav button additionally shows a
  short "you're heading to WhatsApp" confirmation.
- Palette: navy `#0A1F4B`, gold `#C9A84C`, paper `#FBF7EE`. Type: Newsreader.
- Unshipped art still in `assets/`: `art-cathedral.jpg`, `art-cove.jpg`,
  `art-tallship.jpg`, `celestial.jpg`, `walls-traveler.jpg` — kept for future use,
  deliberately excluded from `fastapi-build/`.
