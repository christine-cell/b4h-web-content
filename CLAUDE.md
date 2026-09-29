# CLAUDE.md — working agreement for this repo

This repo is **Boxing4Health Training**: a set of self-contained, bilingual
(English / Canadian French), accessible static training programs, generated from
sources and served by GitHub Pages at training.boxing4health.com. Read this
before making changes. It exists so the site can grow without drifting.

| Program | Folder | Audience | Lesson sources |
|---|---|---|---|
| Licensee Training | `licensee/` | licensed coaches | `_authored/licensee/` |
| Parkinson's Pathway to Empowerment | `pathway/` | clients / participants (plain, warm language) | `_authored/pathway/` |

Programs are registered in `tools/programs.py`. The domain root (`index.html`)
is a program directory with one card per program.

## The one rule that prevents most breakage

**Never hand-edit generated files. Edit the source, then rebuild.**

Build output (do **not** edit): the root `index.html` and `404.html`, and for
each program `<program>/index.html`, `<program>/modules/*.html`, and
`<program>/resources/*.html`. The QA gate rebuilds and diffs, so hand edits are
rejected. Change the *source*, run the build, and commit the regenerated output.

## Definition of done (every change)

1. Make the change in the **right source** (see map below).
2. Rebuild:  `python3 tools/build_hub.py && python3 tools/build_pages.py all`
3. Run the gate:  `python3 tools/qa.py`  → it must print **✓ all gates passed**.
4. Stage everything (sources **and** regenerated output) and commit. The
   pre-commit hook runs `tools/qa.py` and blocks the commit if it fails.

New clone? Run `sh tools/setup.sh` once to enable the pre-commit hook.

## Source map — where to make each change

`<p>` = the program folder (`licensee` or `pathway`).

| To change… | Edit this source | Then |
|---|---|---|
| Lesson body text | `_authored/<p>/<slug>.html` (+ `<slug>.fr.html` for French) | rebuild |
| A new lesson | add to `<p>/data/modules.json` **and** create both `_authored/<p>/<slug>.html` + `.fr.html` | rebuild |
| Glossary term / definition | `<p>/data/glossary.json` (drives the Glossary **and** the in-context tooltips) | rebuild |
| A document/form | drop the file in `<p>/assets/docs/` **and** add it to `<p>/data/documents.json` | rebuild |
| Program hub / resources hub | the program's builder functions in `tools/build_hub.py` (+ `<p>/data/*.json`) | rebuild |
| Program directory card | `LANDING_CARDS` in `tools/build_hub.py` | rebuild |
| UI chrome text (nav, buttons, labels) | `assets/js/i18n.js` — add the key to **both** `en` and `fr` | — |
| Design tokens (colour, type, spacing, shadow) | `assets/css/tokens.css` (per-program overrides use `[data-program="<p>"]`) | bump `V`, rebuild |
| Component styles | `assets/css/site.css` | bump `V`, rebuild |
| Behaviour (JS) | `assets/js/*.js` | bump `V`, rebuild |
| Header/footer | `<p>/partials/header.html` / `footer.html` (root directory: `partials/`) | rebuild |

**Cache-busting:** if you change any CSS or JS, bump `V = "<n>"` in **both**
`tools/build_hub.py` and `tools/build_pages.py`, then update the hard-coded `?v=`
in the static pages (`styleguide.html`, `<p>/certificate.html`) — QA checks them.

## Non-negotiables (the QA gate enforces these)

- **Style stays in sync:** follow `STYLE_GUIDE.md` and run content through the
  `b4h-content` skill (`.claude/skills/b4h-content/`). Use design tokens — **no raw
  hex colours**, no inline colour styles, **no emoji** (use Lucide `data-icon="…"`).
- **Voice matches the audience:** Licensee speaks to coaches; Pathway speaks
  directly to people living with Parkinson's — warm, plain words, short
  sentences, no coaching jargon, and it never gives medical advice (encourage
  talking to their care team).
- **Bilingual always:** every lesson has an EN and an FR authored file; every
  `data-i18n` key exists in EN and FR. New/uncertain clinical French → log it in
  `TRANSLATION-REVIEW.md`.
- **Glossary & docs coverage:** a term added to content that deserves a definition
  goes in that program's `glossary.json`; a file in `<p>/assets/docs/` must be
  listed in `<p>/data/documents.json` (QA fails otherwise).
- **Accessibility:** one `<h1>` per page, real `alt` text, keyboard-operable,
  WCAG-AA contrast, respects reduced-motion.
- **Self-contained:** no external resource loads except opt-in YouTube video
  embeds (`youtube-nocookie`) and their `i.ytimg.com` posters.

## Architecture quick facts

- Shared CSS/JS/fonts/images live once in the root **`assets/`**; each program
  keeps its own `data/`, `partials/`, `assets/docs/`, pages, and certificate.
- Each page declares its program on `<html data-program="<p>">`. `site.js`
  derives the site root from its own script URL and the program base from that
  attribute, so paths stay **relative** and the tree can move. Keep it that way.
- Progress is stored per program on the device (`b4h-progress` for Licensee,
  `b4h-progress-<p>` for others).
- `CNAME`, DNS, and Pages serve the repo root — don't change these casually.

## Verifying visually

`tools/qa.py` covers structure, links, i18n, glossary, docs, and accessibility
basics — but not *how it looks*. For visual/content changes, also serve locally
(`python3 -m http.server` from repo root → `/licensee/` or `/pathway/`) and check
the affected pages in light **and** dark, at phone **and** desktop widths, in EN
**and** FR. When you QA a UI element, look at the rendered element itself —
don't just assert its behaviour in JS (a placeholder once shipped with raw
markup because only the function was tested, not the render).
