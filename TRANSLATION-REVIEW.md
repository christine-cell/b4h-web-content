# French Translation — Clinician Review

The site's French (fr-CA) was AI-produced and published with a visible **« traduction en cours de révision »** flag. Verify the terms below, then clear the flag (edit `fr.reviewflag` in `assets/js/i18n.js` to an empty string).

## Coverage

- **Fully translated:** navigation, hub, controls, all lesson titles/summaries, and the 15 Wix-text lesson bodies.

- **Partial:** the 20 enhanced rich lessons + gut-health resource show English body + a French summary + an honest notice (their built-in quiz JS prevents a safe duplicated French copy). Finishing these is the main remaining French task.

- **Also flagged:** the credential 'PT' (Québec uses 'pht'/OPPQ) — confirm.

## Flagged terms


### review-flags-manifest.md

# Translation review flags — manifest titles & glossary (fr-CA)

Medical/clinical terms whose fr-CA rendering a clinician should confirm. Format: **English term → chosen fr-CA → why uncertain**.

- **Freezing of gait → gel de la marche** — Clinically also *enrayage cinétique* or *blocage de la marche*. Chose *gel de la marche* for a senior-friendly, non-specialist audience; confirm it's acceptable in your clinical materials.
- **Cueing → guidage** — No single settled fr-CA equivalent. Physiotherapy literature uses *stimulation*, *indices sensoriels*, *repères* (verbaux/visuels/auditifs). *Guidage* reads clearly for coaches; a clinician may prefer *stimulation sensorielle* / *repères externes*.
- **Client intake → admission** — Rendered *Admission du client*. Depending on how formal the process is, *Accueil* or *Prise en charge* may fit better. Confirm the preferred operational term.
- **Parkinson's-Plus → syndrome Parkinson plus** — Also *syndromes parkinsoniens atypiques*. Confirm which umbrella term your program uses.
- **CBD (Corticobasal Degeneration) → dégénérescence corticobasale (DCB)** — The abbreviation "CBD" collides with *cannabidiol*; spell out *DCB* in French to avoid confusion.
- **Dementia → démence** — Current diagnostic usage favours *trouble neurocognitif majeur* (DSM-5). Kept *démence* for lay readability; confirm the register you want in "Dementia 101".
- **Assessment → évaluation** — Fine generically, but *évaluation initiale* vs *bilan initial* vs *dépistage* (screening in Lesson 3) carry different clinical weight; confirm the distinction between *screening* (dépistage) and *assessment* (évaluation) is preserved.
- **Disease stages → stades** — Chose *stade* (Hoehn & Yahr) over *étape*. Confirm, since program prose sometimes mixes "stage" (clinical) and "step" (course step).
- **Bradykinesia / festination / dyskinesia → bradykinésie / festination / dyskinésie** — Standard medical terms; low risk, but flagged for completeness since spelling/accents matter.
- **Caregiver → aidant naturel** — Québec-standard, but *proche aidant* is increasingly the official term (e.g. government usage). Confirm house preference.


### review-flags-wix.md

# Review flags — Wix lesson bodies (fr-CA)

Medical / clinical / domain terms a clinician or fr-CA reviewer should confirm.

- **Freezing of gait** → *blocage de la marche (freezing of gait)* — kept the English term in parentheses on first use since it is the term coaches will hear in training. Alt: *enrayage cinétique*. (lesson: freezing-of-gait-video)
- **DBS (Deep Brain Stimulation)** → *stimulation cérébrale profonde (SCP)* — standard fr-CA term; confirm SCP abbreviation is acceptable for the audience. (lesson: volunteer-orientation)
- **Dual tasking** → *double tâche* — confirm preferred rehab term (also seen: *tâche double*). (lesson: class-breakdown-overview)
- **Amplitude-based movements** → *mouvements de grande amplitude* — ties to PWR/LSVG BIG philosophy; confirm wording. (lesson: class-breakdown-overview)
- **Muscle rigidity** → *rigidité musculaire* — standard PD symptom term; confirm. (lesson: cool-down)
- **Fall risk** → *risque de chute* — standard; confirm. (lessons: lesson-3, assessment-video, volunteer-orientation)
- **Fascial work / fascia** → *travail fascial / fascia* — confirm preferred term (also *travail des fascias*). (lesson: cool-down)
- **PT (Tina Cousineau, PT)** → left as *PT* (professional credential). In Québec the physiotherapist designation is *pht* (OPPQ). Confirm whether to localize to "pht" or keep "PT". (lesson: start-up-equipment)
- **High / Low functioning** → *haut / bas niveau de fonctionnement* — used for the Fighter/Champion class split; confirm phrasing is acceptable and person-first enough. (lessons: lesson-3, class-breakdown-overview, volunteer-orientation)
- **"pads" (boxing focus mitts)** → *pattes d'ours* — common fr-CA boxing term; confirm vs *paos / cibles*. (lesson: volunteer-orientation)

## Notes on choices
- Person-first language used throughout: *personne atteinte de la maladie de Parkinson* / *personnes atteintes de la maladie de Parkinson*; never "patient Parkinson".
- Brand/program names left as-is per spec: Boxing4Health / Boxing 4 Health, B4H, PD Warrior, PWR, VIGOR, Fighter, Champion, Champion Plus. "fighters" (their generic term for participants) kept untranslated to match program culture.
- Product names kept: Yoga Tune Up, YTU Therapy Balls, Alpha Ball, Boxing iTimer, Spotify, iPad, HIIT.
- Download labels localized ("Download PDF/DOCX" → "Télécharger le PDF/DOCX"); attached filenames left unchanged.
- Email addresses, phone numbers and bare URLs used as link text left unchanged; only descriptive link text was translated.
