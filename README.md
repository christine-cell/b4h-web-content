# B4H Web Content

The **Boxing4Health Licensee Training Program** — a self-contained, bilingual (English / Canadian French), accessible static site rebuilt from the original Wix program and enhanced GitHub content. Served via GitHub Pages.

**Live (once DNS is set):** https://training.boxing4health.com
**Fallback:** https://christine-cell.github.io/b4h-web-content/

## What's here
- `index.html` — dashboard hub (modules, progress, certificate)
- `modules/` — 35 rebuilt lesson pages
- `resources/` — standalone resources
- `certificate.html` — printable completion certificate
- `assets/` — `css/` (tokens + site + print), `js/` (theme, i18n, progress, quiz, search, read-aloud, certificate, icons), self-hosted `fonts/`, `icons/`, `img/`
- `partials/` — shared header/footer injected client-side
- `data/modules.json` — single source for nav, cards, progression, search
- `i18n/` — French translations + bilingual glossary
- `tools/` — page generators (`build_pages.py`, `build_hub.py`) and `check_links.py`
- `_sources/` — archived Wix + enhanced sources (not served)

## Docs
- **`GO-LIVE.md`** — deploy checklist (enable Pages, DNS, translation review)
- **`STYLE_GUIDE.md`** — voice, design tokens, components, how to add a lesson
- **`TRANSLATION-REVIEW.md`** — French terms for clinician sign-off
- **`.claude/skills/b4h-content/`** — content-style skill for future edits

## Rebuild the pages
```bash
python3 tools/build_pages.py all   # lessons + resources
python3 tools/build_hub.py         # hub, resources index, 404
python3 tools/check_links.py       # verify no broken local links
```

## Preview locally
```bash
python3 -m http.server 8765
```
Then open http://localhost:8765/.

Design and content: run changes through `STYLE_GUIDE.md` + the `b4h-content` skill. Bump `?v=` on asset links when CSS/JS changes.
