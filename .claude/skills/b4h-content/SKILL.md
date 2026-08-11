---
name: b4h-content
description: Author or edit content for the Boxing4Health licensee training site so it matches the house voice, component system, bilingual structure, and accessibility rules. Use whenever writing, rewriting, or reviewing any lesson, resource, hub copy, or UI string for this repo (modules/*.html, resources/*.html, index.html, partials, i18n).
---

# Boxing4Health content skill

Apply this whenever you create or change content in this repo. It encodes the house style so every page reads as one professional, senior-friendly training program. Read `STYLE_GUIDE.md` (repo root) for the full reference; this skill is the working checklist.

## Voice (match it exactly)
- Empowering, action-oriented, warm, reassuring. Coaches are the audience; people living with Parkinson's are who they serve.
- Boxing metaphor is welcome but never trivializes the disease. Person-first language ("a person living with Parkinson's"). they/them when gender unknown.
- Plain, short sentences, ~grade-8 reading level, senior-friendly. Define jargon on first use (wrap the term in `.gloss` with a definition).
- Preserve the founder's existing wording where it's already on-voice — improve clarity, don't blandify.

## Rewrite checklist
1. **Structure**: lesson opens with a "What you'll learn" objectives panel and closes with "Key takeaways". Use H2/H3 in logical order (one H1, provided by the shell).
2. **Components, not ad-hoc HTML**: use the cheatsheet in `STYLE_GUIDE.md` — callouts (info / coach / safety), panels, cards, quiz, video click-to-load, glossary. No inline color styles; no raw hex — use tokens.
3. **Icons**: Lucide via `data-icon="name"`. No emoji in content. Add missing icons to `assets/js/icons.js`.
4. **Bilingual**: every user-facing string needs EN + fr-CA. Body copy uses paired `data-lang-block="en"/"fr"`; UI labels use `data-i18n` keys defined in `assets/js/i18n.js`. Canadian French; reuse `i18n/glossary.json` terms.
5. **Medical safety**: never invent clinical facts. Keep source medical content intact. Any medical term you translate to French goes into `TRANSLATION-REVIEW.md` for a clinician to verify. Add a "translation under review" note (already wired via `.fr-review-flag`).
6. **Accessibility**: real alt text; contrast via tokens; keyboard-operable; nothing that relies on color alone; don't break the text-size/contrast controls.
7. **Consistency**: match the reading time in `data/modules.json`; keep slugs/titles in sync with the manifest; bump `?v=` on assets if CSS/JS changed.

## When adding a whole lesson
Follow "Adding a lesson" in `STYLE_GUIDE.md`: update `data/modules.json`, create `modules/<slug>.html` from an existing lesson, fill objectives → body → takeaways, add French blocks, verify in the browser at desktop + phone in light + dark + EN + FR.

## Output
When editing, keep diffs minimal and on-voice. When reviewing, report concrete fixes (voice, missing objectives/takeaways, raw hex, missing French, a11y) rather than vague notes.
