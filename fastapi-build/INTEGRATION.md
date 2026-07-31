# FastAPI integration — Hidden Worlds landing (v2)

This folder is the v2 landing page prepared for the Hidden Worlds FastAPI/forge
service: `templates/` + `static/`, with asset paths rewired to `/static/` and
internal links pointing at routes.

**v2 is simpler than the previous build.** There is no design-system runtime, no
`_ds/` bundle, no `support.js`, and no `{{ }}` template tokens. The pages are
plain HTML with an inline `<style>` and about 60 lines of vanilla JS. They can be
served as Jinja templates or as flat static files, whichever suits you.

## Files

```
templates/
  index.html          ->  the homepage
  story-card.html     ->  the Season 1 / Story Card page
  terms-viewer.html   ->  homepage with the Terms & Privacy modal already open
static/
  assets/...          ->  10 images (only the ones the pages reference)
```

Only external dependency: Google Fonts (Newsreader), loaded over https. If the
service must run without third-party requests, the pages degrade to Georgia and
stay fully usable.

## Static mount

Serve `static/` at `/static` — the templates reference `/static/assets/...`.

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Routes to add

| Route               | Template            | Purpose                                        |
|---------------------|---------------------|------------------------------------------------|
| `GET /`             | `index.html`        | Homepage                                       |
| `GET /story-card`   | `story-card.html`   | Season 1 / Story Card page                     |
| `GET /terms-viewer` | `terms-viewer.html` | Homepage with the legal modal open (see below)  |

```python
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/story-card", response_class=HTMLResponse)
async def story_card(request: Request):
    return templates.TemplateResponse("story-card.html", {"request": request})

@app.get("/terms-viewer", response_class=HTMLResponse)
async def terms_viewer(request: Request):
    return templates.TemplateResponse("terms-viewer.html", {"request": request})
```

The templates contain **no `{{ }}` tokens**, so no template context is required.

**The route names matter**: the homepage links to `/story-card` in two places, and
the Season 1 page links back to `/`. Serving these templates under different paths
will break those links.

## About `/terms-viewer`

A copy of the homepage with the **Terms & Privacy modal open from first paint**, so
an outside link can deep-link straight into the legal text. The visitor lands on
the live homepage with the terms open over it, and closing the modal drops them
onto the homepage to explore.

- Default opens the Terms section. `GET /terms-viewer?tc=privacy` opens the
  Privacy section.
- The modal iframes `https://hiddenworlds.travel/terms` (the raw legal page, served
  elsewhere and unchanged). Verified responding 200 on 2026-07-31.
- The **WhatsApp onboarding link** should point at
  `https://hiddenworlds.travel/terms-viewer`.

## Things to confirm on your side

1. **`og:image` is absolute** and currently points at
   `https://hiddenworlds.travel/static/assets/hero-aerial.jpg`. If the service is
   served from another domain, change `ORIGIN` in `build-fastapi.py` and rerun it.
2. **`/terms-viewer` was specified for the previous build but currently 404s in
   production**, as does `/`. Worth checking whether the earlier FastAPI build was
   ever deployed, so this one does not land in the same place.
3. **WhatsApp number is hard-coded**: `wa.me/385998427803`, in 6 places across the
   two pages. Search and replace to change it.

## Regenerating this folder

`fastapi-build/` and the root `terms-viewer.html` are **derived, never hand-edited**.
After any change to `index.html` or `story-card.html`:

```
python build-fastapi.py
```

That rewires asset paths and internal links, rebuilds all three templates, and
copies across only the assets the pages actually reference. It asserts that no
un-rewired path, page link, or template token survives, so a silent drift between
the preview site and this build is not possible.
