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
