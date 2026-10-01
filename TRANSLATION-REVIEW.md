# French (fr-CA) — Clinician / House-Style Review

The site is now **fully bilingual** — every lesson has an English and a French (fr-CA) version, toggled from the reading menu. The French was AI-produced and is published with a visible **« traduction en cours de révision »** flag. Verify the terms below, then clear the flag (set `fr.reviewflag` to `""` in `assets/js/i18n.js`).

## Coverage
- **Fully translated:** navigation, hub, all lesson titles/summaries, and **all 35 lesson bodies + the resource** (re-translated onto the redesigned pages).
- Structure is preserved exactly — the French is substituted into the same components as the English.

## Terms flagged by the translators (pick your house style)
| English | Used in FR | Alternative to consider |
|---|---|---|
| PT (Tina Cousineau, PT) | physiothérapeute | Québec regulated title **pht** (OPPQ) |
| freezing of gait (FOG) | gel de la marche / blocage (freezing) | enrayage cinétique; keep **FOG** acronym? |
| Target Heart Rate (THR) | fréquence cardiaque cible (FCC) | keep **THR**? |
| Health History Form (PD) | Formulaire d'antécédents médicaux (MP) | keep "(PD)" if the physical PDF says PD |
| Fullerton Advanced Balance Scale | Échelle d'équilibre avancée de Fullerton | some clinics keep the English scale name |
| facial masking | masquage facial | amimie / hypomimie |
| shuffling gait | démarche traînante | marche à petits pas |
| dementia | démence | trouble neurocognitif majeur (newer term) |
| Parkinson's-Plus (MSA/CBD/PSP) | AMS / DCB / PSP | keep English MSA/CBD/PSP to match video labels? |
| Mediterranean diet | diète méditerranéenne | régime méditerranéen |
| CPR / AED / DBS | RCR / DEA / SCP | keep English acronyms? |

Kept as-is (brand/standard): Boxing4Health, B4H, PD Warrior, PWR, VIGOR, Fighter, Champion, Champion Plus, TUG, Berg, LSVT BIG, ACSM, BDNF, MDS-UPDRS, PDQ-39; all emails, URLs, prices, and numbers.

Note: the two tongue-twister vocal warm-ups were **adapted** to real French *vire-langues* (a literal translation wouldn't work as a speech exercise) — confirm you're happy with the substitutes.

## Resources hub — new bilingual + clinical content (added later)
The **Coach's Resource Hub** (`/licensee/resources/`) adds AI-authored content that needs the same review pass:
- **Glossary** (`licensee/data/glossary.json`) — 28 term definitions, EN + fr-CA. Two clinical scales and the program tiers (Fighter / Champion / Champion Plus) were verified against the program content; the rest are standard descriptions — skim for tone.
- **Assessment tools** (`licensee/data/assessment-tools.json`) — TUG, 30-sec chair stand, Berg, Fullerton, MDS-UPDRS. **A clinician should confirm the cut-off / scoring numbers** before you rely on them (they use commonly-cited, conservative values and are labelled "not a diagnosis").
- **Quick-reference cards** (`licensee/data/quick-reference.json`) — safety checklist, freezing-of-gait cueing, exertion (talk-test/RPE only, no bpm), and a red-flags card. Confirm the red-flags card matches your own emergency guidance.
- **Further reading** links are to well-known Parkinson's organisations — confirm you're comfortable pointing licensees to them.

Each of these is a small JSON file, so edits are quick — change the text and re-run `python3 tools/build_hub.py`.

---

# Pathway to Empowerment (`/pathway/`) — French review

> **Status (Oct 1, 2026):** approved by Christine to run as is; the review badge is off for Pathway. The list below stays as a reference for future polishing.

All 77 Pathway lessons have EN + fr-CA versions. Where Christine's GitHub pages had French versions (constipation, dairy, cognitive exercise, immune system, supplements, NR, magnesium, recipes, freezing, osteoarthritis), the French is based on **her own French**; everything else is AI-translated and carries the same « traduction en cours de révision » flag.

## House-style choices to confirm
| Topic | Used | Note |
|---|---|---|
| Levodopa gender | **la** lévodopa | Christine's pages use « le lévodopa » |
| Motto | « Nos défis ne nous définissent pas. Nos actions, oui. » | one GitHub page had a different wording |
| Mediterranean diet | « alimentation méditerranéenne » (titles) / « régime méditerranéen » (some bodies, from Christine's French) | pick one |
| Meals | déjeuner / dîner / souper (Québec usage) | Christine's OA page said « dîner » for dinner → changed to « souper » |
| Voice box | « larynx (l'organe de la voix) » | « boîte vocale » means voicemail in Québec |
| Spotter | « une personne pour vous surveiller » | |
| Down to the ground | « descente au sol » | |
| Freezing of gait | « blocage de la marche » | Licensee uses « gel de la marche » — align? |
| Cues | « indices / indiçage » | Christine's own choice |
| Masked face | « expression faciale réduite / figée » | or amimie / hypomimie |
| Accountability | « responsabilité » | or « engagement » |
| Find your people | « Trouvez votre gang » | informal Québec phrasing |
| Kept in English | Fighter, Champion, VIGOR, PWR!, TUG, PDQ-39, BDNF, UPDRS | |

## Clinical / research terms to verify
bradykinésie · rigidité musculaire · instabilité posturale · périodes « on/off » · micrographie · anosmie · hypotension · dyskinésies · phase prodromique · spécialiste des troubles du mouvement · libération myofasciale · ostéopathe (approche crânio-sacrée) · IRM · densité de la matière grise · amygdale · neuro-inflammation · thérapie cognitive basée sur la pleine conscience (MBCT) · photobiomodulation (PBM) · axe intestin-cerveau · microbiote intestinal · acides gras à chaîne courte (AGCC) · dysbiose · alpha-synucléine · nerf vague · motilité intestinale · greffe de microbiote fécal · amidon résistant · randomisation mendélienne · rapport de cotes · causalité inverse · sarcopénie · liquide céphalorachidien · excitotoxicité · récepteurs NMDA · axe HHS · magnésium érythrocytaire / sérique · syndrome des jambes sans repos · hormonothérapie (HTR / de la ménopause) · inhibiteurs de la COMT · syndrome musculosquelettique de la ménopause · capsulite rétractile · ganglions de la base · festination · rétroaction proprioceptive · oléocanthal · solanacées.

## Glossary
`pathway/data/glossary.json` — 34 plain-language definitions (EN + fr-CA), AI-written for a participant audience. Review for accuracy and tone.
