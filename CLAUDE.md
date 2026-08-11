# CLAUDE.md — working agreement for this repo

This is the **Boxing4Health Licensee Training** site: a self-contained, bilingual
(English / Canadian French), accessible static site generated from sources and
served by GitHub Pages. Read this before making changes. It exists so the site
can grow without drifting.

## The one rule that prevents most breakage

**Never hand-edit generated files. Edit the source, then rebuild.**

The pages under `licensee/modules/`, `licensee/resources/index.html`,
`licensee/index.html`, the root `index.html`, and `404.html` are **build output**.
Editing them directly is drift and the QA gate will reject it (it rebuilds and
diffs). Change the *source*, run the build, and commit the regenerated output.

## Definition of done (every change)

1. Make the change in the **right source** (see map below).
2. Rebuild:  `python3 tools/build_hub.py && python3 tools/build_pages.py all`
3. Run the gate:  `python3 tools/qa.py`  → it must print **✓ all gates passed**.
4. Stage everything (sources **and** regenerated output) and commit. The
   pre-commit hook runs `tools/qa.py` and blocks the commit if it fails; GitHub
   Actions re-runs it on push.

New clone? Run `sh tools/setup.sh` once to enable the pre-commit hook.

## Source map — where to make each change

| To change… | Edit this source | Then |
|---|---|---|
| Lesson body text | `_authored/<slug>.html` (+ `_authored/<slug>.fr.html` for French) | rebuild |
| A new lesson | add to `licensee/data/modules.json` **and** create both `_authored/<slug>.html` + `.fr.html` | rebuild |
| Glossary term / definition | `licensee/data/glossary.json` (drives the Glossary page **and** the in-context tooltips) | rebuild |
| A document/form | drop the file in `licensee/assets/docs/` **and** add an entry to `licensee/data/documents.json` | rebuild |
| Resources: videos / assessments / quick-ref / further-reading | the data lists in `tools/build_hub.py` (or `licensee/data/*.json`) | rebuild |
| UI chrome text (nav, buttons, labels) | `licensee/assets/js/i18n.js` — add the key to **both** `en` and `fr` | — |
| Design tokens (colour, type, spacing, shadow) | `licensee/assets/css/tokens.css` | bump `V`, rebuild |
| Component styles | `licensee/assets/css/site.css` | bump `V`, rebuild |
| Behaviour (JS) | `licensee/assets/js/*.js` | bump `V`, rebuild |
| Header/footer | `licensee/partials/header.html` / `footer.html` | rebuild |

**Cache-busting:** if you change any CSS or JS, bump `V = "<n>"` in **both**
`tools/build_hub.py` and `tools/build_pages.py`, then rebuild (asset URLs carry `?v=`).

## Non-negotiables (the QA gate enforces these)

- **Style stays in sync:** follow `STYLE_GUIDE.md` and run content through the
  `b4h-content` skill (`.claude/skills/b4h-content/`). Use design tokens — **no raw
  hex colours**, no inline colour styles, **no emoji** (use Lucide `data-icon="…"`).
- **Bilingual always:** every lesson has an EN and an FR authored file; every
  `data-i18n` key exists in EN and FR. New/uncertain clinical French → log it in
  `TRANSLATION-REVIEW.md`.
- **Glossary & docs coverage:** a term added to content that deserves a definition
  goes in `glossary.json`; a file in `assets/docs/` must be listed in
  `documents.json` (QA fails otherwise).
- **Accessibility:** one `<h1>` per page, real `alt` text, keyboard-operable,
  WCAG-AA contrast, respects reduced-motion.
- **Self-contained:** no external resource loads except opt-in YouTube video
  embeds (`youtube-nocookie`) and their `i.ytimg.com` posters.

## Architecture quick facts

- The program lives under **`/licensee/`**; the domain root is a small program
  directory. `CNAME`, DNS, and Pages serve the repo root — don't change these
  casually.
- Paths are **relative**; JS derives its base from its own script URL, so the
  whole `/licensee/` tree can move without breaking. Keep it that way.
- Generated files (do **not** edit): `index.html`, `404.html`,
  `licensee/index.html`, `licensee/modules/*.html`, `licensee/resources/index.html`.

## Verifying visually

`tools/qa.py` covers structure, links, i18n, glossary, docs, and accessibility
basics — but not *how it looks*. For visual/content changes, also serve locally
(`python3 -m http.server` from repo root → `/licensee/`) and check the affected
pages in light **and** dark, at phone **and** desktop widths, in EN **and** FR.
When you QA a UI element, look at the rendered element itself — don't just assert
its behaviour in JS (a placeholder once shipped with raw markup because only the
function was tested, not the render).
