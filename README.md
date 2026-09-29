# B4H Web Content

**Boxing4Health Training** — self-contained, bilingual (English / Canadian French), accessible static training programs rebuilt from the original Wix programs and enhanced GitHub content. Served via GitHub Pages.

**Live:**
- Program directory (root): https://training.boxing4health.com/
- Licensee Training: https://training.boxing4health.com/licensee/
- Parkinson's Pathway to Empowerment: https://training.boxing4health.com/pathway/

**Fallback:** https://christine-cell.github.io/b4h-web-content/

> **URL structure:** each program is namespaced under its own folder so programs can live side by side without breaking links. The domain **root** is a program directory.

## What's here
- `index.html` — **program directory** (one card per program) — served at `/`
- `404.html` — branded not-found page for the whole domain
- `styleguide.html` — live component library (design system)
- `assets/` — **shared** CSS (tokens + site + print), JS (theme, i18n, progress, quiz, search, read-aloud, certificate, glossary tooltips, icons), self-hosted fonts, images
- `partials/` — header/footer for the program directory
- `licensee/`, `pathway/` — one folder per program:
  - `index.html` — dashboard hub (modules, progress, certificate)
  - `modules/` — lesson pages · `resources/` — resources hub + articles · `certificate.html`
  - `partials/` — the program's header/footer (injected client-side)
  - `data/` — `modules.json` (nav, cards, progression, search), `glossary.json`, `documents.json`, …
  - `assets/docs/` — the program's downloadable documents
- `_authored/<program>/` — lesson sources (EN + FR) wrapped into pages by the build
- `tools/` — `programs.py` (registry), `build_pages.py`, `build_hub.py`, `qa.py`, `check_links.py`
- `_sources/` — archived Wix/GitHub sources (not served)

## Docs
- **`GO-LIVE.md`** — deploy checklist (enable Pages, DNS, translation review)
- **`STYLE_GUIDE.md`** — voice, design tokens, components, how to add a lesson
- **`TRANSLATION-REVIEW.md`** — French terms for clinician sign-off
- **`.claude/skills/b4h-content/`** — content-style skill for future edits

## Rebuild the pages
```bash
python3 tools/build_hub.py         # program hubs, resources hubs, directory, 404
python3 tools/build_pages.py all   # lessons + resources, every program
python3 tools/qa.py                # the full quality gate
```

## Preview locally
```bash
python3 -m http.server 8765
```
Then open http://localhost:8765/.

Design and content: run changes through `STYLE_GUIDE.md` + the `b4h-content` skill. Bump `?v=` on asset links when CSS/JS changes.
