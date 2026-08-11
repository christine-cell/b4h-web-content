# Source Reconciliation Notes

Captured 2026-08-10 from the live Wix participant page + the two enhanced-content GitHub repos.

## Sources
- `_sources/wix/` — full extract of the live Wix program (34 records: overview + 33 steps), structure, step→content map.
- `_sources/enhanced/boxing-4-health-PD-symptoms/` — 22 enhanced HTML pages (the primary "better content" repo, served at `christine-cell.github.io/boxing-4-health-PD-symptoms/`).
- `_sources/enhanced/boxing4health-training/` — 1 page (`b4h_module1_intro (1).html`); the Wix "Parkinson's 101" intro links here.
- `_sources/build-blueprint.json` — the definitive per-lesson content plan driving the rebuild.

## Program structure (Wix IA — mirrored in the rebuild)
1. **Module 1 · Parkinson's 101** — 9 steps
2. **Module 2 · Class Breakdown** — 17 steps
3. **Practical Steps** — 1 step
4. **Learning Resources** — 5 steps
5. **Admin Forms** — 1 step
(+ Overview) = 34.

## Content priority (per approved plan)
**Enhanced content wins.** 19 lessons are backed by an enhanced page; 14 are Wix-text-only (build from the captured Wix text).

## Broken / missing links found in Wix (flag for Christine)
- `b4h_lesson2_stages.html` → **404 live**, but the repo has `b4h_lesson2_stages (1).html`. Using the `(1)` file. ✅ resolved.
- `b4h_module2_class_breakdown (3).html` → **404 / does not exist** in either repo. This is the **Module 2 intro** step, which has its own rich Wix text (class structure: warm-up / high-intensity / cool-down, and the Fighter / Champion / Champion Plus classifications). **Rebuild uses the Wix text**; no enhanced page exists. ⚠️ Christine may want to confirm nothing else was intended here.

## Enhanced pages NOT linked from any Wix step (bonus content to fold in)
- `b4h_lesson3b_intake.html` → Module 1 (client intake) — insert as a Module 1 lesson.
- `b4h_module2_champion_plus.html` → Module 2 (Champion Plus program) — pairs with the "Class Breakdown" classifications.
- `b4h_module2_pro_tips.html` → Module 2 (Pro tips) — merge with / near "PRO tips & Q&A".
- `pd-constipation-education.html` → Resources (gut health / Mediterranean diet) — standalone resource page.

## Repo hygiene to fix in rebuild
- Duplicate/versioned filenames in the enhanced repo (`... (1).html`, `... (2).html`) — dedupe to clean slugs.
- Two divergent design systems in the enhanced repo (dark "fight" theme vs. light editorial constipation page) — unify into the single new design system.

## Videos (→ click-to-load embeds)
- "ACTION- Freezing Video" (Module 1): 2 YouTube embeds.
- "PD warrior Exercises- ACTION" (Module 2): 10 YouTube videos.
- Plus scattered YouTube links inside other steps — captured in `wix-extract.json`.

## External links captured (keep as outbound links)
- `dementiasolutions.ca/landing-page-free-course/` (Dementia 101 free course)
- `boxing4health.com/product-page/alpha-ball`, `.../therapy-balls` (equipment)
- `mailto:` Christine@ and Tina@boxing4health.com
