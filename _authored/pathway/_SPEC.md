# Pathway to Empowerment — lesson authoring spec

You re-author one lesson of **Parkinson's Pathway to Empowerment (PPE)**, a 10-week
program for **people living with Parkinson's** (and their care partners), created
and taught by Christine Seaby, RMT, founder of Boxing4Health. You write the lesson
body in a fixed component system, in **English** (`<slug>.html`) and **Canadian
French** (`<slug>.fr.html`), into `_authored/pathway/`.

## 1. Faithfulness (most important)
- **Preserve all real content** from the sources you're given: facts, numbers,
  study names/years, recipes, test instructions, exercise steps, names. Never
  invent clinical facts, statistics, studies, dosages, or quotes.
- Source priority where they overlap: **GitHub enhanced page** (`_sources/pathway/github/`)
  > **Google Doc / PDF text** (`_sources/pathway/gdocs/`, `_sources/pathway/text/`)
  > **Wix step** (`_sources/pathway/wix/part*.md`). Merge — don't drop — content that
  only one source has.
- Keep Christine's first-person, encouraging voice where the source uses it ("I",
  "my favourite", "TRUST me this works!"). Improve clarity and structure; don't blandify.
- **Remove** any invitation to book a consultation, call, or appointment with
  Christine or any outside practitioner (Christine no longer offers these).
  Keep "email us" / "talk to your care team / doctor / dietitian" wording.
- Supplements/medication: keep the source content, and make sure the lesson
  includes the standard care-team reminder (see §4). Never add dosing advice
  that isn't in the source.
- If a source is clearly wrong or missing, don't paper over it — leave an HTML
  comment `<!-- REVIEW: … -->` explaining, and write the best faithful lesson you can.

## 2. Audience & voice
- The reader **is** the person living with Parkinson's. Speak to them directly: "you".
- Warm, hopeful, practical. Plain words, short sentences (grade 6–8). Define any
  medical word in plain language the first time (e.g. "bradykinesia (slowness of movement)").
- Boxing/fighting spirit is on-brand ("fight back", "Our challenges don't define us.
  Our actions do.") — never trivialize the disease.
- Canadian spelling in English (colour, fibre, practise [verb]); Québec French in French.

## 3. Output format
Write ONLY the inner lesson-body HTML — no doctype/head/body, **no `<h1>`** (the page
shell adds the title, breadcrumbs, completion button and pager). Valid, well-nested HTML.

Hard rules (a QA gate enforces them):
- **No `style=` attributes, no `<style>`, no hex colours, no emoji** (use `data-icon="…"`).
- No `<script>` except a quiz JSON block.
- Every `<h2>` has a kebab-case `id`.
- `<strong>` only for a few words of genuine emphasis.

Lesson shape:
1. `<p class="lead">` — one or two warm sentences on what this lesson gives them.
2. For **read** and **do** lessons: a short "What you'll learn" (or "What you'll do")
   panel. For short **watch** lessons (one video + a little text), skip it.
3. The body (sections with `<h2 id>`).
4. A short "Key takeaways" panel (skip for very short watch lessons — then end with
   a one-line "Your action this week" callout instead).
5. The quiz last, if this lesson carries one.

## 4. Components (exact classes)
- Lead: `<p class="lead">…</p>`
- Objectives / takeaways:
  `<div class="panel panel-tinted"><h3><span data-icon="target"></span> What you'll learn</h3><ul class="check-list"><li>…</li></ul></div>`
  (takeaways: `data-icon="circle-check-big"`, "Key takeaways")
- Section: `<h2 id="kebab-id">Title</h2>` (optional `<p class="label">Step 1</p>` above)
- Steps: `<ol class="steps"><li class="step"><div class="step-body"><h4>Title</h4><p>…</p></div></li></ol>`
- Accordion (tests, exercises, recipes, FAQs):
  `<div class="accordion" data-open="false"><button class="acc-trigger"><span class="chip chip-sm" data-icon="ICON"></span> <span>NAME</span> <span class="acc-chevron" data-icon="chevron-right"></span></button><div class="acc-panel"><div class="acc-panel-inner">…</div></div></div>`
- Callouts: `<div class="callout callout-KIND"><span class="callout-icon" data-icon="ICON"></span><p class="callout-title">TITLE</p><div class="callout-body"><p>…</p></div></div>`
  - `callout-info` (icon `info` or `lightbulb`) — "Good to know"
  - `callout-coach` (icon `heart-handshake`) — "Christine’s tip" / « Le conseil de Christine » — use for Christine's personal advice
  - `callout-safety` (icon `triangle-alert`) — "Safety first" / « La sécurité d’abord » — for any test/exercise with fall risk
  - **Care-team reminder** (required on any lesson about supplements, diet changes, medication, or new treatments):
    `<div class="callout callout-safety"><span class="callout-icon" data-icon="stethoscope"></span><p class="callout-title">Talk to your care team</p><div class="callout-body"><p>This lesson is for education only and isn’t medical advice. Check with your doctor, neurologist or pharmacist before starting a supplement or making a big change to your diet or medication.</p></div></div>`
    FR: title « Parlez-en à votre équipe de soins », body « Cette leçon est offerte à titre éducatif seulement et ne remplace pas un avis médical. Consultez votre médecin, votre neurologue ou votre pharmacien avant de commencer un supplément ou de modifier de façon importante votre alimentation ou votre médication. »
  - "Your action this week": `callout-coach` with icon `footprints`, title "Your action this week" / « Votre action de la semaine ».
- Cards: `<div class="grid grid-cards"><article class="card"><span class="chip" data-icon="ICON"></span><h3>…</h3><p>…</p></article></div>`
- Stats: `<div class="stat-row"><div class="stat"><div class="stat-num">…</div><div class="stat-label">…</div></div></div>`
- Tables: plain `<table><thead>…</thead><tbody>…</tbody></table>` (auto-wrapped for mobile).
- **Download** (files live in `pathway/assets/docs/`; path from a lesson is `../assets/docs/FILE`):
  `<div class="files-grid"><a class="file-card" href="../assets/docs/FILE" download><span class="file-ico"><span class="file-ext">PDF</span></span><span class="file-meta"><span class="file-name">Name</span><span class="file-sub">Download · PDF · SIZE</span></span><span class="file-dl" data-icon="download"></span></a></div>`
  FR: `Télécharger · PDF · SIZE`. Use only the files listed in your brief, with the sizes given.
- **YouTube video** (IDs given in your brief — use them exactly):
  `<div class="video" data-yt="ID" data-title="Title"><img class="video-poster" src="https://i.ytimg.com/vi/ID/hqdefault.jpg" alt=""><div class="video-play"><span data-icon="circle-play"></span></div><div class="video-label">Title</div></div>`
  Several: wrap in `<div class="video-grid">…</div>`. In the FR file use the same IDs; translate the title/label.
- **Video not on YouTube yet** (the brief says "PENDING <wixId>"): use exactly
  `<div class="callout callout-info" data-video-pending="WIXID"><span class="callout-icon" data-icon="circle-play"></span><p class="callout-title">Video coming soon</p><div class="callout-body"><p>Christine’s video “TITLE” is being moved to this site and will appear here shortly.</p></div></div>`
  FR: title « Vidéo à venir », body « La vidéo de Christine « TITRE » est en cours de transfert vers ce site et apparaîtra ici sous peu. »
- **French-language video/audio** that exists only in French: put it only in the FR file.
- External link (research, organisations): `<a href="URL" target="_blank" rel="noopener noreferrer">…</a>`.
- Quiz (only if your brief asks for one on this lesson): 4 questions, friendly, answerable from THIS lesson, with a kind explanation:
  `<div class="quiz" data-quiz data-quiz-for="pw-SLUG" data-pass="0.75"><script type="application/json" data-quiz-questions>[{"q":{"en":"…"},"options":[{"en":"…"},{"en":"…"},{"en":"…"}],"answer":0,"explain":{"en":"…"}}]</script></div>`
  Put it under `<h2 id="quick-check">Quick check</h2>` with one line inviting them to try it. In the FR file, the same quiz with `"fr"` keys instead of `"en"`. Vary the position of the correct answer.

## 5. Icons (`data-icon`)
accessibility, activity, apple, armchair, arrow-down, award, bed, bike, bone, book-open, brain, calendar, calendar-check, carrot, chef-hat, circle-check-big, circle-play, clipboard-check, clipboard-list, clock, cup-soda, download, droplets, dumbbell, ear, eye, file-text, fish, flame, flask-conical, footprints, glass-water, graduation-cap, hand, hand-heart, headphones, heart, heart-handshake, heart-pulse, info, layers, leaf, lightbulb, list-checks, map, message-circle, mic, moon, mountain, move, move-right, music, notebook-pen, party-popper, pill, play, presentation, printer, puzzle, quote, rotate-cw, salad, shapes, shield-check, smile, snowflake, sparkles, sprout, star, stethoscope, sun, target, timer, triangle-alert, trophy, user, users, utensils, venus, wheat, wind, zap.

## 6. French
- Translate faithfully into natural Québec French (vous). Where the GitHub source has
  a `-fr.html` version, base the FR file on it (it's Christine's own French).
- Clinical terms: use standard Canadian French (maladie de Parkinson, bradykinésie,
  rigidité, blocage de la marche, neurologue, lévodopa). Add any term you're unsure of
  to the list you return (it goes into TRANSLATION-REVIEW.md).
- Keep the same structure, ids, video IDs and file links as the EN file.

## 7. When done
Return a short report per lesson: sources used, anything dropped or uncertain,
REVIEW comments left, and French terms to review.
