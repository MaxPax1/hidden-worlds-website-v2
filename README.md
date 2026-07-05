# Hidden Worlds — Homepage v2 (rebuild, 2026-07-05)

A complete from-scratch replacement for the live homepage, built against the canon
(brief.md / voice.yaml / STORY.md / GUIDE-VOICE.md / B2B.md). Not yet live — review first.

## What it is

- **One self-contained static page**: `index.html` + `assets/`. No design-system bundle,
  no build step, no JS framework. Only external dependency: Google Fonts (Newsreader).
- Sections: promise-led hero → disarm strip → the guide + trust (with WhatsApp demo) →
  no wrong place → how it works → Story Card (navy section) → final CTA + partnership line.
- Voice: "plain maker" — the site speaks as the people who built the guide, not as the
  guide (his voice starts inside WhatsApp). AI named plainly once, in the guide section.
- Includes the Terms/Privacy modal (`data-tc`, iframes hiddenworlds.travel/terms) and the
  WhatsApp confirm interstitial on the nav button, same consent patterns as the old site.

## View it

Open `index.html` in a browser, or from this folder:

```
python -m http.server 8000
```

then http://localhost:8000

## Deploy (when approved)

Copy `index.html` + `assets/` over the live site's root (repo `MaxPax1/hidden-worlds-website`).
Keep `.nojekyll`. Note: the old site's `story-card.html` links and `fastapi-build/` copies are
NOT updated by this folder — decide whether to retire or rebuild the sub-page first.

WhatsApp number is hard-coded: `wa.me/385998427803`.
