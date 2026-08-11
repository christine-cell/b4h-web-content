# `_sources/` — Provenance Archive

Raw source material the rebuilt site is derived from. **Not served** (kept for reference/audit).

- **`wix/`** — the live Wix program, captured 2026-08-10 via authenticated browser:
  - `wix-extract.json` — all 34 records (overview + 33 steps) with text, HTML, links, images, video embeds.
  - `structure.json` — ordered section/step tree (the information architecture).
  - `step-content-map.json` — per-step links + videos.
  - `INDEX.md` — human-readable table of the whole program.
- **`enhanced/`** — the "better content" GitHub repos, cloned verbatim:
  - `boxing-4-health-PD-symptoms/` (22 pages, primary) and `boxing4health-training/` (1 page).
  - `wix-to-enhanced-map.json` — which enhanced file each Wix step links to.
- **`build-blueprint.json`** — the definitive per-lesson plan (module, slug, type, content source, videos) driving the rebuild.
- **`RECONCILIATION.md`** — decisions, broken links, bonus pages, and hygiene notes.

See `../STYLE_GUIDE.md` for how this content is transformed into the live site.
