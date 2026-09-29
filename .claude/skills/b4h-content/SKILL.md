---
name: b4h-content
description: Author or edit content for the Boxing4Health training programs (Licensee for coaches, Pathway to Empowerment for participants) so it matches the house voice, component system, bilingual structure, and accessibility rules. Use whenever writing, rewriting, or reviewing any lesson, resource, hub copy, or UI string for this repo (_authored/<program>/*.html, hub builders, partials, i18n).
---

# Boxing4Health content skill

Apply this whenever you create or change content in this repo. It encodes the house style so every page reads as one professional, senior-friendly training program. Read `STYLE_GUIDE.md` (repo root) for the full reference and `CLAUDE.md` for where each source lives; this skill is the working checklist.

## Voice (match it exactly)
- Empowering, action-oriented, warm, reassuring.
- **Know the audience per program.** *Licensee* (`licensee/`): coaches are the reader; people living with Parkinson's are who they serve. *Pathway to Empowerment* (`pathway/`): the reader IS a person living with Parkinson's (or their care partner) — speak to them directly ("you"), in Christine's encouraging first-person voice where the source uses it; plainer words, shorter sentences, no coaching or clinical jargon, and never medical advice (point them to their care team for medication, supplements, and diagnosis questions).
- Boxing metaphor is welcome but never trivializes the disease. Person-first language ("a person living with Parkinson's"). they/them when gender unknown.
- Plain, short sentences, ~grade-8 reading level, senior-friendly. Define jargon on first use (wrap the term in `.gloss` with a definition).
- Preserve the founder's existing wording where it's already on-voice — improve clarity, don't blandify.

## Rewrite checklist
1. **Structure**: lesson opens with a "What you'll learn" objectives panel and closes with "Key takeaways". Use H2/H3 in logical order (one H1, provided by the shell).
2. **Components, not ad-hoc HTML**: use the cheatsheet in `STYLE_GUIDE.md` — callouts (info / coach / safety), panels, cards, quiz, video click-to-load, glossary. No inline color styles; no raw hex — use tokens.
3. **Icons**: Lucide via `data-icon="name"`. No emoji in content. Add missing icons to `assets/js/icons.js`.
4. **Bilingual**: every user-facing string needs EN + fr-CA. Body copy uses paired `data-lang-block="en"/"fr"`; UI labels use `data-i18n` keys defined in `assets/js/i18n.js`. Canadian French; reuse the program's `data/glossary.json` terms.
5. **Medical safety**: never invent clinical facts. Keep source medical content intact. Any medical term you translate to French goes into `TRANSLATION-REVIEW.md` for a clinician to verify. Add a "translation under review" note (already wired via `.fr-review-flag`).
6. **Accessibility**: real alt text; contrast via tokens; keyboard-operable; nothing that relies on color alone; don't break the text-size/contrast controls.
7. **Consistency**: match the reading time in `data/modules.json`; keep slugs/titles in sync with the manifest; bump `?v=` on assets if CSS/JS changed.

## When adding a whole lesson
Follow "Adding a lesson" in `STYLE_GUIDE.md`: update `<program>/data/modules.json`, create `_authored/<program>/<slug>.html` (+ `.fr.html`) from an existing lesson, fill objectives → body → takeaways, add French blocks, verify in the browser at desktop + phone in light + dark + EN + FR.

## Output
When editing, keep diffs minimal and on-voice. When reviewing, report concrete fixes (voice, missing objectives/takeaways, raw hex, missing French, a11y) rather than vague notes.
