"""Render the interactive 10-day meal plan from pathway/data/meal-plan.json.

Used by build_pages.py: an authored lesson containing the marker
    <!-- include:meal-plan -->
gets this HTML (EN or FR) in its place at build time. The page is fully
readable without JavaScript; assets/js/meal-plan.js adds the food-sorting game,
day-by-day navigation, "day done" ticks and the grocery-list builder.
Edit the plan in the JSON, never in the generated page.
"""
import html, json, os

def _e(s): return html.escape(s or "", quote=True)

UI = {
 "en": dict(rules="The plan at a glance", sort="Quick game: where does it belong?",
            sort_intro="Tap where you think each food fits in a Mediterranean way of eating for Parkinson’s. You’ll see why right away.",
            score="correct", again="Play again", right="Yes!", wrong="Not quite —", next="Next food", finish="See my score", food="Food", result="You sorted {n} of {t} foods correctly!", plan="Your 10-day plan",
            plan_intro="Choose a day to see its meals. Tap a meal for the recipe. Tick the day when you’ve tried it.",
            day="Day", done="I tried this day", done_on="Day done", of="of", days_done="days tried",
            ingredients="Ingredients", steps="How to make it", min="min",
            levodopa="Contains animal protein — time it 1–2 hours after your levodopa.",
            grocery="Build your grocery list", grocery_intro="Pick the days you’re shopping for. Your list is grouped by store section — tick things off as you go.",
            print="Print my list", clear="Untick all", empty="Pick at least one day to build your list.",
            types=dict(breakfast="Breakfast", lunch="Lunch", dinner="Dinner", snack="Snack"),
            tags={"quick": "Quick", "make-ahead": "Make-ahead", "freezer": "Freezer-friendly", "plant-protein": "Plant protein",
                  "animal-protein": "Animal protein", "high-fibre": "High fibre", "gluten-free-option": "Gluten-free option"}),
 "fr": dict(rules="Le plan en un coup d’œil", sort="Petit jeu : où va cet aliment ?",
            sort_intro="Touchez l’endroit où chaque aliment trouve sa place dans une alimentation méditerranéenne adaptée à la maladie de Parkinson. Vous verrez pourquoi tout de suite.",
            score="bonnes réponses", again="Rejouer", right="Oui !", wrong="Pas tout à fait —", next="Aliment suivant", finish="Voir mon résultat", food="Aliment", result="Vous avez bien classé {n} aliments sur {t} !", plan="Votre plan de 10 jours",
            plan_intro="Choisissez un jour pour voir ses repas. Touchez un repas pour la recette. Cochez la journée quand vous l’avez essayée.",
            day="Jour", done="J’ai essayé cette journée", done_on="Journée faite", of="sur", days_done="jours essayés",
            ingredients="Ingrédients", steps="Préparation", min="min",
            levodopa="Contient des protéines animales — prenez ce repas 1 à 2 heures après votre lévodopa.",
            grocery="Créez votre liste d’épicerie", grocery_intro="Choisissez les jours pour lesquels vous faites l’épicerie. Votre liste est classée par rayon — cochez au fur et à mesure.",
            print="Imprimer ma liste", clear="Tout décocher", empty="Choisissez au moins un jour pour créer votre liste.",
            types=dict(breakfast="Déjeuner", lunch="Dîner", dinner="Souper", snack="Collation"),
            tags={"quick": "Rapide", "make-ahead": "À préparer d’avance", "freezer": "Se congèle", "plant-protein": "Protéines végétales",
                  "animal-protein": "Protéines animales", "high-fibre": "Riche en fibres", "gluten-free-option": "Option sans gluten"}),
}
TYPE_ICON = dict(breakfast="sun", lunch="salad", dinner="utensils", snack="apple")

def render(root, lang):
    data = json.load(open(os.path.join(root, "pathway", "data", "meal-plan.json"), encoding="utf-8"))
    t = UI[lang]; L = lambda o, k: o.get(f"{k}_{lang}") or o.get(f"{k}_en", "")
    out = [f'<div class="meal-plan" data-meal-plan data-t-right="{_e(t["right"])}" data-t-wrong="{_e(t["wrong"])}" '
           f'data-t-score="{_e(t["score"])}" data-t-of="{_e(t["of"])}" data-t-done="{_e(t["done"])}" data-t-done-on="{_e(t["done_on"])}" '
           f'data-t-empty="{_e(t["empty"])}" data-t-day="{_e(t["day"])}" data-t-next="{_e(t["next"])}" '
           f'data-t-finish="{_e(t["finish"])}" data-t-food="{_e(t["food"])}" data-t-result="{_e(t["result"])}">']
    # rules
    out.append(f'<h2 id="plan-at-a-glance">{t["rules"]}</h2><ul class="mp-rules">')
    for r in data.get("rules", []):
        out.append(f'<li><span class="chip chip-sm" data-icon="{_e(r.get("icon","leaf"))}"></span><span>{_e(r[lang])}</span></li>')
    out.append('</ul>')
    # food sort game
    bins = data["sort"]["bins"]; binname = {b["id"]: b[lang] for b in bins}
    out.append(f'<h2 id="food-game">{t["sort"]}</h2><p>{t["sort_intro"]}</p>'
               f'<div class="food-sort" data-food-sort><div class="fs-score" aria-live="polite"><span data-fs-right>0</span> / {len(data["sort"]["foods"])} {t["score"]}</div><ul class="fs-list">')
    for f in data["sort"]["foods"]:
        btns = "".join(f'<button type="button" data-pick="{_e(b["id"])}"><span data-icon="{_e(b["icon"])}"></span>{_e(b[lang])}</button>' for b in bins)
        out.append(f'<li class="fs-item" data-bin="{_e(f["bin"])}"><p class="fs-food"><span class="chip chip-sm" data-icon="{_e(f.get("icon","leaf"))}"></span>{_e(f[lang])}</p>'
                   f'<div class="fs-choices" role="group" aria-label="{_e(f[lang])}">{btns}</div>'
                   f'<p class="fs-why"><strong class="fs-answer">{_e(binname[f["bin"]])}.</strong> {_e(L(f, "why"))}</p></li>')
    out.append(f'</ul><button type="button" class="btn btn-secondary fs-again" data-fs-again><span data-icon="rotate-cw"></span>{t["again"]}</button></div>')
    # days
    days = data["days"]
    out.append(f'<h2 id="ten-day-plan">{t["plan"]}</h2><p>{t["plan_intro"]}</p>')
    out.append(f'<div class="mp-daynav" role="tablist" aria-label="{_e(t["plan"])}">' + "".join(
        f'<button type="button" role="tab" data-day-btn="{d["day"]}" aria-controls="mp-day-{d["day"]}"><span class="mp-dn">{d["day"]}</span><span class="mp-dcheck" data-icon="circle-check-big" aria-hidden="true"></span></button>'
        for d in days) + '</div>')
    out.append(f'<p class="mp-progress"><span data-days-done>0</span> {t["of"]} {len(days)} {t["days_done"]}</p>')
    for d in days:
        out.append(f'<!-- source: {d.get("source","")} -->' if d.get("source") == "new" else "")
        out.append(f'<article class="mp-day" id="mp-day-{d["day"]}" data-day="{d["day"]}" role="tabpanel">'
                   f'<h3 class="mp-day-title"><span class="mp-day-num">{t["day"]} {d["day"]}</span> {_e(L(d, "theme"))}</h3>')
        for m in d["meals"]:
            tags = "".join(f'<span class="badge mp-tag" data-tag="{_e(g)}">{_e(t["tags"].get(g, g))}</span>' for g in m.get("tags", []))
            ings = "".join(f'<li data-item="{_e(i["item_"+lang] if i.get("item_"+lang) else i["item_en"])}" data-aisle="{_e(i["aisle"])}">'
                           f'<span class="mp-qty">{_e(i.get("qty_"+lang) or i.get("qty_en",""))}</span> {_e(i.get("item_"+lang) or i["item_en"])}</li>'
                           for i in m.get("ingredients", []))
            steps = "".join(f"<li>{_e(s)}</li>" for s in (m.get("steps_"+lang) or m.get("steps_en", [])))
            extra = ""
            if "animal-protein" in m.get("tags", []):
                extra += f'<p class="mp-levodopa"><span data-icon="clock"></span>{t["levodopa"]}</p>'
            if L(m, "tip"): extra += f'<p class="mp-tip"><span data-icon="lightbulb"></span>{_e(L(m, "tip"))}</p>'
            if L(m, "note"): extra += f'<p class="mp-note"><span data-icon="info"></span>{_e(L(m, "note"))}</p>'
            out.append(
                f'<div class="accordion mp-meal" data-open="false"><button class="acc-trigger">'
                f'<span class="chip chip-sm" data-icon="{TYPE_ICON.get(m["type"],"utensils")}"></span> '
                f'<span class="mp-meal-head"><span class="mp-type">{t["types"][m["type"]]}</span><span class="mp-name">{_e(L(m, "name"))}</span>'
                f'<span class="mp-meta"><span class="mp-time"><span data-icon="timer"></span>{m.get("time_min","")} {t["min"]}</span>{tags}</span></span>'
                f' <span class="acc-chevron" data-icon="chevron-right"></span></button>'
                f'<div class="acc-panel"><div class="acc-panel-inner">'
                f'<h4>{t["ingredients"]}</h4><ul class="mp-ings">{ings}</ul>'
                f'<h4>{t["steps"]}</h4><ol class="mp-steps">{steps}</ol>{extra}</div></div></div>')
        out.append(f'<button type="button" class="btn btn-secondary mp-done" data-day-done="{d["day"]}" aria-pressed="false"><span data-icon="circle-check-big"></span><span data-done-label>{t["done"]}</span></button></article>')
    # grocery list
    aisles = data["aisles"]
    out.append(f'<h2 id="grocery-list">{t["grocery"]}</h2><p>{t["grocery_intro"]}</p>'
               f'<div class="mp-grocery" data-grocery><div class="mp-gdays" role="group" aria-label="{_e(t["grocery"])}">' + "".join(
        f'<label class="mp-gday"><input type="checkbox" value="{d["day"]}"{" checked" if d["day"] <= 3 else ""}><span>{t["day"]} {d["day"]}</span></label>' for d in days) +
        '</div><div class="mp-glist" data-glist aria-live="polite">' +
        "".join(f'<section class="mp-aisle" data-aisle-id="{_e(a["id"])}"><h4>{_e(a[lang])}</h4><ul></ul></section>' for a in aisles) +
        f'</div><div class="mp-gactions"><button type="button" class="btn btn-primary" data-gprint><span data-icon="printer"></span>{t["print"]}</button>'
        f'<button type="button" class="btn btn-secondary" data-gclear><span data-icon="rotate-cw"></span>{t["clear"]}</button></div></div>')
    out.append('</div>')
    return "".join(out)
