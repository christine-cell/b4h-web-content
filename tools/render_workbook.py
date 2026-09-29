"""Render the interactive Action Plan Workbook from pathway/data/workbook.json.

Used by build_pages.py for <!-- include:workbook -->. Every input carries
data-wb="<field id>" — assets/js/workbook.js saves and restores values on the
device, runs week navigation, the before/after test comparison, printing and
backup. Edit the workbook in the JSON, never in the generated page.
"""
import html, json, os

def _e(s): return html.escape(s or "", quote=True)

UI = {
 "en": dict(week="Week", tests_b="My test results — start of the program", tests_r="My re-test results",
            tests_hint="Write your time (or count) for each test.", date="Date", test="Test", result="Result",
            compare="Your progress", compare_hint="Your start and re-test results side by side.",
            before="Start", after="Re-test", change="Change", ss_title="Small steps, real progress",
            ss_hint="Turn a goal into a small action you can do even on a hard day.", ss_more="The 7 small-steps principles",
            open="Open the lesson", more_opts="More options", done="done", print="Print / save as PDF", blank="Print a blank copy",
            backup="Save a backup file", restore="Restore from a backup", clear="Clear my workbook",
            clear_q="Clear everything in your workbook on this device? This can’t be undone.",
            saved="Saved on this device", restored="Your workbook was restored.", badfile="That file isn’t a workbook backup.",
            better="better", worse="keep going", same="same", unit_s="s", unit_steps="steps", day="Day",
            faster="faster", slower="slower", more="{n} more steps", fewer="{n} fewer steps", longer="longer", shorter="shorter"),
 "fr": dict(week="Semaine", tests_b="Mes résultats de départ", tests_r="Mes résultats aux tests finaux",
            tests_hint="Inscrivez votre temps (ou votre nombre) pour chaque test.", date="Date", test="Test", result="Résultat",
            compare="Vos progrès", compare_hint="Vos résultats de départ et finaux côte à côte.",
            before="Départ", after="Tests finaux", change="Écart", ss_title="Petits pas, vrais progrès",
            ss_hint="Transformez un objectif en une petite action réalisable même dans une journée difficile.", ss_more="Les 7 principes des petits pas",
            open="Ouvrir la leçon", more_opts="Plus d’options", done="faits", print="Imprimer / enregistrer en PDF", blank="Imprimer une copie vierge",
            backup="Enregistrer une copie de sauvegarde", restore="Restaurer une sauvegarde", clear="Effacer mon cahier",
            clear_q="Effacer tout le contenu de votre cahier sur cet appareil ? Cette action est définitive.",
            saved="Enregistré sur cet appareil", restored="Votre cahier a été restauré.", badfile="Ce fichier n’est pas une sauvegarde du cahier.",
            better="mieux", worse="continuez", same="pareil", unit_s="s", unit_steps="pas", day="Jour",
            faster="plus rapide", slower="plus lent", more="{n} pas de plus", fewer="{n} pas de moins", longer="plus long", shorter="plus court"),
}

def render(root, lang):
    D = json.load(open(os.path.join(root, "pathway", "data", "workbook.json"), encoding="utf-8"))
    t = UI[lang]; L = lambda o, k="": o.get(f"{k}_{lang}" if k else lang) or o.get(f"{k}_en" if k else "en", "")
    days = D["days"][lang]
    tests = D["tests"]
    def unit(u): return t["unit_s"] if u == "s" else t["unit_steps"]
    attrs = " ".join(f'data-t-{k.replace("_", "-")}="{_e(v)}"' for k, v in t.items() if k in (
        "clear_q", "saved", "restored", "badfile", "better", "worse", "same", "faster", "slower", "more", "fewer", "longer", "shorter", "unit_s", "unit_steps", "done"))
    o = [f'<div class="workbook" data-workbook {attrs}>']
    # toolbar
    o.append(f'<div class="wb-tools"><button type="button" class="btn btn-primary" data-wb-print><span data-icon="printer"></span>{t["print"]}</button>'
             f'<details class="wb-more"><summary>{t["more_opts"]}</summary><div class="wb-more-menu">'
             f'<button type="button" class="btn btn-secondary" data-wb-print-blank><span data-icon="file-text"></span>{t["blank"]}</button>'
             f'<button type="button" class="btn btn-secondary" data-wb-backup><span data-icon="download"></span>{t["backup"]}</button>'
             f'<label class="btn btn-secondary wb-restore"><span data-icon="rotate-cw"></span>{t["restore"]}<input type="file" accept="application/json,.json" data-wb-restore hidden></label>'
             f'<button type="button" class="btn btn-ghost wb-clear" data-wb-clear><span data-icon="triangle-alert"></span>{t["clear"]}</button>'
             f'</div></details><span class="wb-saved" data-wb-saved aria-live="polite"></span></div>')
    # week nav
    o.append(f'<div class="wb-weeknav" role="tablist" aria-label="{_e(t["week"])}">' + "".join(
        f'<button type="button" role="tab" data-wb-week-btn="{w["n"]}" aria-controls="wb-week-{w["n"]}"><span class="wb-wn">{w["n"]}</span><span class="wb-wcount" data-wb-count="{w["n"]}"></span></button>'
        for w in D["weeks"]) + '</div>')
    for w in D["weeks"]:
        o.append(f'<section class="wb-week" id="wb-week-{w["n"]}" data-wb-week="{w["n"]}" role="tabpanel">'
                 f'<header class="wb-week-head"><span class="chip" data-icon="{_e(w["icon"])}"></span><div><p class="wb-week-kicker">{t["week"]} {w["n"]}</p>'
                 f'<h3 class="wb-week-title">{_e(L(w, "title"))}</h3></div></header>')
        for s in w["sections"]:
            ty = s["type"]
            head = ""
            if s.get("title_en"):
                head = f'<div class="wb-sec-head"><h4>{_e(L(s, "title"))}</h4>' + (f'<p class="wb-hint">{_e(L(s, "hint"))}</p>' if L(s, "hint") else "") + '</div>'
            if ty == "todo":
                items = ""
                for it in s["items"]:
                    link = f' <a class="wb-link" href="{_e(it["link"])}">{t["open"]}</a>' if it.get("link") else ""
                    extra = f'<input type="text" class="wb-input wb-inline" data-wb="{_e(it["id"])}.text" aria-label="{_e(it[lang])}">' if it.get("text") else ""
                    items += (f'<li><label class="wb-check"><input type="checkbox" data-wb="{_e(it["id"])}" data-wb-todo>'
                              f'<span>{_e(it[lang])}</span></label>{extra}{link}</li>')
                o.append(f'<div class="wb-sec">{head}<ul class="wb-todos">{items}</ul></div>')
            elif ty == "fields":
                fs = ""
                for fd in s["fields"]:
                    note = f'<span class="wb-note">{_e(L(fd, "note"))}</span>' if L(fd, "note") else ""
                    if fd["kind"] == "textarea":
                        ctl = f'<textarea class="wb-input" rows="3" data-wb="{_e(fd["id"])}" id="wbf-{lang}-{_e(fd["id"])}"></textarea>'
                    else:
                        typ = "time" if fd["kind"] == "time" else "text"
                        ctl = f'<input type="{typ}" class="wb-input" data-wb="{_e(fd["id"])}" id="wbf-{lang}-{_e(fd["id"])}">'
                    fs += f'<div class="wb-field wb-{fd["kind"]}"><label for="wbf-{lang}-{_e(fd["id"])}">{_e(fd[lang])}</label>{note}{ctl}</div>'
                o.append(f'<div class="wb-sec">{head}<div class="wb-fields">{fs}</div></div>')
            elif ty == "log":
                rows = "".join(f'<div class="wb-logrow"><label for="wbl-{lang}-{s["id"]}-{i}">{_e(d)}</label>'
                               f'<input type="text" class="wb-input" id="wbl-{lang}-{s["id"]}-{i}" data-wb="{_e(s["id"])}.{i}"></div>' for i, d in enumerate(days))
                o.append(f'<div class="wb-sec">{head}<div class="wb-log">{rows}</div></div>')
            elif ty == "grid":
                ths = "".join(f'<th scope="col">{_e(c[lang])}</th>' for c in s["cols"])
                trs = "".join(f'<tr><th scope="row">{_e(d)}</th>' + "".join(
                    f'<td><input type="checkbox" data-wb="{_e(s["id"])}.{i}.{c["id"]}" aria-label="{_e(d)} — {_e(c[lang])}"></td>' for c in s["cols"]) + "</tr>"
                    for i, d in enumerate(days))
                o.append(f'<div class="wb-sec">{head}<div class="table-wrap"><table class="wb-grid"><thead><tr><td></td>{ths}</tr></thead><tbody>{trs}</tbody></table></div></div>')
            elif ty == "tests":
                ph = s["phase"]
                rows = "".join(f'<tr><th scope="row">{_e(x[lang])}</th><td><span class="wb-num"><input type="text" inputmode="decimal" class="wb-input" data-wb="test.{ph}.{x["id"]}" aria-label="{_e(x[lang])}"><span class="wb-unit">{unit(x["unit"])}</span></span></td></tr>' for x in tests)
                o.append(f'<div class="wb-sec wb-tests"><div class="wb-sec-head"><h4>{t["tests_b"] if ph == "baseline" else t["tests_r"]}</h4><p class="wb-hint">{t["tests_hint"]}</p></div>'
                         f'<div class="wb-field wb-date"><label for="wbd-{lang}-{ph}">{t["date"]}</label><input type="date" class="wb-input" id="wbd-{lang}-{ph}" data-wb="test.{ph}.date"></div>'
                         f'<div class="table-wrap"><table class="wb-testtable"><thead><tr><th scope="col">{t["test"]}</th><th scope="col">{t["result"]}</th></tr></thead><tbody>{rows}</tbody></table></div></div>')
            elif ty == "compare":
                rows = "".join(f'<tr data-wb-compare="{x["id"]}" data-better="{x["better"]}" data-unit="{x["unit"]}"><th scope="row">{_e(x[lang])}</th><td data-c="b">—</td><td data-c="a">—</td><td data-c="d">—</td></tr>' for x in tests)
                o.append(f'<div class="wb-sec wb-compare"><div class="wb-sec-head"><h4>{t["compare"]}</h4><p class="wb-hint">{t["compare_hint"]}</p></div>'
                         f'<div class="table-wrap"><table class="wb-comparetable"><thead><tr><th scope="col">{t["test"]}</th><th scope="col">{t["before"]}</th><th scope="col">{t["after"]}</th><th scope="col">{t["change"]}</th></tr></thead><tbody>{rows}</tbody></table></div></div>')
            elif ty == "note":
                link = f' <a href="{_e(s["link"])}">{t["open"]}</a>' if s.get("link") else ""
                o.append(f'<p class="wb-callout"><span data-icon="{_e(s.get("icon","info"))}"></span><span>{_e(s[lang])}{link}</span></p>')
            elif ty == "smallsteps":
                ss = D["smallsteps"]
                pr = "".join(f"<li>{_e(p[lang])}</li>" for p in ss["principles"])
                fs = "".join(f'<div class="wb-field"><label for="wbs-{lang}-{_e(x["id"])}">{_e(x[lang])}</label><input type="text" class="wb-input" id="wbs-{lang}-{_e(x["id"])}" data-wb="{_e(x["id"])}"></div>' for x in ss["fields"])
                o.append(f'<div class="wb-sec wb-smallsteps"><div class="wb-sec-head"><h4>{t["ss_title"]}</h4><p class="wb-hint">{t["ss_hint"]}</p></div>'
                         f'<details class="wb-details"><summary>{t["ss_more"]}</summary><ol>{pr}</ol></details><div class="wb-fields">{fs}</div></div>')
        o.append('</section>')
    o.append('</div>')
    return "".join(o)
