# Boxing4Health Training — Style Guide

The single reference for voice, design, and components. **All content — new or edited — should follow this**, and run through the `b4h-content` skill (`.claude/skills/b4h-content/`).

> **Live component library:** open **`/styleguide.html`** in the site to see every component rendered (and toggle theme / text size / language to test them). The authoring contract used to build lesson bodies is **`_authored/_SPEC.md`**; re-authored lesson bodies live in **`_authored/<slug>.html`** and are wrapped into the page shell by `tools/build_pages.py`.

---

## 1. Voice & tone

Boxing4Health speaks to **coaches** who work with people living with Parkinson's. The voice is:

- **Empowering & action-oriented** — "Our challenges don't define us, our ACTIONS do." Focus on what the coach and client *can do*.
- **Warm & reassuring** — never clinical-cold. We're supporting real people through a hard diagnosis.
- **Boxing metaphor, used with care** — "Before we put on the gloves, we need to understand who we're fighting for." Fighters, champions, rounds — but never trivializing the disease.
- **Plain and senior-friendly** — short sentences, common words, define jargon on first use. Reading age ~grade 8.
- **Respectful of dignity** — e.g. *"Never comment on or draw attention to a client's tremor in front of others."*

**Do:** "You'll learn how to spot freezing of gait and cue your client through it."
**Don't:** "This module elucidates the pathophysiology of festination."

Person-first language: "a person living with Parkinson's," not "a Parkinson's patient/sufferer." Use **they/them** when gender is unknown.

---

## 2. Lesson structure (every lesson)

1. **Unified header** — breadcrumb, module eyebrow + icon, H1 title, meta (time, updated). *Provided by the shell — don't hand-write.*
2. **Learning objectives** — open with a "What you'll learn" panel (`.panel.panel-tinted` + `.check-list`).
3. **Body** — sections with H2/H3, callouts, cards, videos.
4. **Key takeaways** — close with a takeaways panel.
5. **Mark-complete** + **prev/next** — provided by the shell.

---

## 3. Design tokens (never hardcode a hex)

- Colour: `--primary` `#19679E`, navy `--blue-900`, accent `--azure`. Full ramp `--blue-50…900`. Status: `--info` `--success` `--safety` `--danger`.
- Type: headings/UI `--font-sans` (Raleway), body `--font-body` (Roboto). Base ≈ 18px, senior-friendly. Fluid `--fs-*`.
- Spacing: 8pt grid `--space-1…9`. Radius `--r-sm…xl`. Shadow `--shadow-1…3`.
- Everything is theme-aware (light/dark) and responds to the user's text-size / spacing / contrast controls. **Use the semantic tokens** (`--surface`, `--text`, `--border`…), not raw ramp values, so dark mode and contrast keep working.

---

## 4. Component cheatsheet

| Need | Markup |
|---|---|
| Callout (info) | `<div class="callout callout-info"><span class="callout-icon" data-icon="info"></span><p class="callout-title">…</p><div class="callout-body">…</div></div>` |
| Coach's Corner | `.callout.callout-coach` (icon `hand`) |
| Safety note | `.callout.callout-safety` (icon `triangle-alert`) |
| Objectives / takeaways | `.panel.panel-tinted` + `<ul class="check-list">` |
| Card grid | `.grid.grid-cards` › `.card.card-hover` |
| Icon chip | `<span class="chip" data-icon="brain"></span>` (Lucide names) |
| Accordion | `.accordion[data-open]` › `.acc-trigger` + `.acc-panel>.acc-panel-inner` |
| Video (click-to-load) | `<div class="video" data-yt="VIDEOID" data-title="…"><img class="video-poster" src="https://i.ytimg.com/vi/VIDEOID/hqdefault.jpg" alt=""><div class="video-play"><span data-icon="circle-play"></span></div></div>` |
| Quiz | `.quiz[data-quiz][data-quiz-for="lesson-id"][data-pass="0.7"]` + `<script type="application/json" data-quiz-questions>` |
| Glossary term | `<span class="gloss">term<span class="gloss-pop">definition</span></span>` |
| Stat | `.stat-row` › `.stat` › `.stat-num` + `.stat-label` |

Icons: use [Lucide](https://lucide.dev) names via `data-icon="…"`. Add new ones to `assets/js/icons.js`. **No emoji** in new content.

---

## 5. Bilingual (EN / fr-CA)

- UI strings live in `assets/js/i18n.js` (`data-i18n="key"`). Add both languages.
- Body content: wrap each language in `data-lang-block="en"` / `data-lang-block="fr"`; CSS shows the active one.
- French is **Canadian French (fr-CA)** — see `i18n/glossary.json` for approved domain terms. New/uncertain medical terms go to `TRANSLATION-REVIEW.md`.

---

## 6. Accessibility (non-negotiable)

- Semantic HTML, one `<h1>` per page, logical heading order.
- Real `alt` text (empty `alt=""` only for decorative images).
- Colour is never the only signal; maintain WCAG AA contrast (AAA for body where possible).
- Everything keyboard-operable; visible focus; respects `prefers-reduced-motion`.
- Large tap targets (≥44px). Don't disable zoom.

---

## 7. Adding a lesson

1. Add it to `data/modules.json` (id, slug, url, title{en,fr}, summary, keywords, type, icon, minutes, hasQuiz, videos).
2. Create `modules/<slug>.html` from the template (copy an existing lesson; keep the shell head/scripts).
3. Fill objectives → body → takeaways using the components above.
4. Add the French `data-lang-block` content and any new `data-i18n` keys.
5. Run it through the `b4h-content` skill. Bump `?v=` on assets if you changed CSS/JS.
