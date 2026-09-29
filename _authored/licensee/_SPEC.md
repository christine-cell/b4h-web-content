# Lesson re-authoring spec (Boxing4Health training site)

You re-author a lesson's content into a fixed component system. **Preserve ALL real content faithfully** (medical/coaching material — never invent, drop, or alter facts, names, emails, or steps). Re-express presentation only.

## Output
Write ONLY the inner lesson-body HTML — no doctype/head/body, no page `<h1>`, no breadcrumb/header/footer/pager (the shell adds those). Valid, well-nested HTML.

## Hard rules
- **No inline styles. No `style=` attributes. No `<style>`. No hardcoded hex colors. No `<script>` except the quiz JSON block.** Everything is styled by classes below.
- **No emoji** — replace every emoji with a `data-icon="NAME"`.
- English only (French is added by a later pass).
- Rounded, consistent components only (the classes handle radius/color/spacing).
- Start with a short `<p class="lead">` intro and a "What you'll learn" objectives panel; end with a "Key takeaways" panel (then the quiz, if any).
- Give every `<h2>` a kebab `id` (powers the on-page table of contents).
- Don't bold whole paragraphs. Use `<strong>` only for genuine emphasis (a few words).

## Components (use these exact classes)
- Section heading: `<h2 id="setup">Setting Up</h2>` · optional label above: `<p class="label">Section 01</p>`
- Lead: `<p class="lead">…</p>`
- Objectives / takeaways panel:
  `<div class="panel panel-tinted"><h3><span data-icon="target"></span> What you'll learn</h3><ul class="check-list"><li>…</li></ul></div>`
  (takeaways: same with `data-icon="circle-check-big"` and title "Key takeaways")
- Numbered steps (USE for "STEP #1 / Step 1 / 1)" content):
  `<ol class="steps"><li class="step"><div class="step-body"><h4>Step title</h4><p>…</p></div></li></ol>`
- Expandable card (USE for symptom/exercise cards with a reveal):
  `<div class="accordion" data-open="false"><button class="acc-trigger"><span class="chip chip-sm" data-icon="ICON"></span> <span>NAME <span class="badge">tag</span></span> <span class="acc-chevron" data-icon="chevron-right"></span></button><div class="acc-panel"><div class="acc-panel-inner"><p>…</p></div></div></div>`
- Callouts: `<div class="callout callout-KIND"><span class="callout-icon" data-icon="ICON"></span><p class="callout-title">TITLE</p><div class="callout-body"><p>…</p></div></div>`
  - `callout-coach` (icon `hand`, title "Coach's Corner") — USE for every "Instructor Note"/coaching tip
  - `callout-safety` (icon `triangle-alert`, title "Safety")
  - `callout-info` (icon `info`, title "Good to know")
- Cards grid: `<div class="grid grid-cards"><article class="card"><span class="chip" data-icon="ICON"></span><h3>…</h3><p>…</p></article></div>`
- Stat row: `<div class="stat-row"><div class="stat"><div class="stat-num">70%</div><div class="stat-label">…</div></div></div>`
- Flip-card flashcards (wrap set in `<div class="grid grid-cards">`):
  `<div class="flip"><div class="flip-inner"><div class="flip-face flip-front"><h4>TERM</h4><span class="muted">Tap to flip</span></div><div class="flip-face flip-back"><p>DEFINITION</p></div></div></div>`
- Contact card (USE for "reach out to X@…"/phone): put inside a `callout-info`, with the email as a `<a href="mailto:…">` and phone as `<a href="tel:…">`.
- File / document (USE when the source references a downloadable form/PDF/doc). If you have a real URL use it as href; if not, mark it pending:
  `<div class="file-grid"><a class="file-card" href="URL_OR_#" data-pending="true"><span class="file-ico"><span class="file-ext">PDF</span></span><span class="file-meta"><span class="file-name">Document name</span><span class="file-sub">Download · PDF</span></span><span class="file-dl" data-icon="download"></span></a></div>`
  (omit `data-pending="true"` when you have a real URL)
- Video (USE for a YouTube video; you'll be given the IDs):
  `<div class="video" data-yt="VIDEO_ID" data-title="Title"><img class="video-poster" src="https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg" alt=""><div class="video-play"><span data-icon="circle-play"></span></div><div class="video-label">Title</div></div>`
  Multiple videos: wrap in `<div class="video-grid">…</div>`.
- Quiz (USE for a knowledge check; convert every question):
  `<div class="quiz" data-quiz data-quiz-for="LESSON_SLUG" data-pass="0.7"><script type="application/json" data-quiz-questions>[{"q":{"en":"Q"},"options":[{"en":"A"},{"en":"B"}],"answer":0,"explain":{"en":"why"}}]</script></div>`

## Icons (data-icon names available)
brain, activity, heart-pulse, shield-check, triangle-alert, info, circle-check-big, dumbbell, users, user, hand, footprints, wind, snowflake, timer, stethoscope, target, zap, book-open, clipboard-list, clipboard-check, accessibility, sparkles, list-checks, layers, move-right, graduation-cap, award, circle-play, download, file-text, clock, settings-2, shapes, star, flame, quote. Pick sensible ones.

## Tone
Empowering, warm, person-first ("a person living with Parkinson's"), coach-facing. Keep the founder's wording where it's already good; just structure it.
