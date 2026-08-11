#!/usr/bin/env python3
"""Build index.html (hub), resources/index.html, and 404.html."""
import json, os, html as htmllib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "licensee")   # program is namespaced under /licensee/
M = json.load(open(os.path.join(SITE, "data/modules.json")))
def _data(name):
    p=os.path.join(SITE,"data",name)
    return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else {}
V = "22"
def esc(s): return htmllib.escape(s or "", quote=True)

def head(title, desc, prefix):
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#19679e">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https://i.ytimg.com; media-src 'self'; frame-src https://www.youtube-nocookie.com https://www.youtube.com; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'">
<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefix}assets/img/favicon.svg">
<link rel="stylesheet" href="{prefix}assets/css/fonts.css?v={V}">
<link rel="stylesheet" href="{prefix}assets/css/tokens.css?v={V}">
<link rel="stylesheet" href="{prefix}assets/css/site.css?v={V}">
<link rel="stylesheet" href="{prefix}assets/css/print.css?v={V}" media="print">
<script>(function(){{try{{var d=document.documentElement,s=localStorage;
d.setAttribute('data-theme',s.getItem('b4h-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));
d.setAttribute('lang',s.getItem('b4h-lang')||'en');
if(s.getItem('b4h-contrast')==='high')d.setAttribute('data-contrast','high');
d.style.setProperty('--font-scale',s.getItem('b4h-font')||'1');
d.style.setProperty('--line-mult',s.getItem('b4h-line')||'1');}}catch(e){{}}}})();</script>
</head>
<body>
<div data-include="header"></div>
<main id="main">
"""

def scripts(prefix, extra=None):
    names = ["icons","i18n","site","progress","search","read-aloud"] + (extra or [])
    return "\n".join(f'<script src="{prefix}assets/js/{n}.js?v={V}"></script>' for n in names)

def foot(prefix, extra=None):
    return f"""</main>
<div data-include="footer"></div>
{scripts(prefix, extra)}
</body></html>"""

def bilingual(en, fr, tag="span", cls=""):
    fr = fr or en
    c = f' class="{cls}"' if cls else ""
    return (f'<{tag}{c} data-lang-block="en">{en}</{tag}><{tag}{c} data-lang-block="fr">{fr}</{tag}>')

def blf(d, key):
    v = d.get(key, {}); return v.get("en",""), (v.get("fr") or v.get("en",""))

# ---------------- HUB ----------------
def lesson_row(l, prefix):
    icon = l.get("icon","book-open")
    en, fr = blf(l, "title")
    return f"""<a class="lesson-row" href="{prefix}{esc(l['url'])}" data-lesson-ref="{esc(l['id'])}">
      <span class="chip chip-sm" data-icon="{icon}"></span>
      <span>
        <span class="lr-title">{bilingual(esc(en),esc(fr))}</span><br>
        <span class="lr-meta">{l['minutes']} <span data-i18n="lesson.time">min read</span></span>
      </span>
      <span class="lr-mark"><span class="status-chip" data-lesson-status data-status="not-started"></span></span>
    </a>"""

def module_card(m, prefix):
    lessons = "\n".join(lesson_row(l, prefix) for l in m["lessons"])
    ten = esc(m['title']['en'].split('·')[-1].strip())
    tfr = esc((m['title'].get('fr') or m['title']['en']).split('·')[-1].strip())
    return f"""<article class="card module-card" data-reveal id="{esc(m['slug'])}" data-mod="{m['num']}">
      <div class="module-cover">
        <span class="module-cover-wm" data-icon="{m['icon']}" aria-hidden="true"></span>
        <span class="module-cover-chip" data-icon="{m['icon']}"></span>
        <div class="module-cover-txt">
          <span class="eyebrow">Module {m['num']}</span>
          <h3>{bilingual(ten, tfr)}</h3>
        </div>
        <span class="module-cover-count"><span data-progress-module="{esc(m['slug'])}"><span data-progress-count>0/{len(m['lessons'])}</span></span></span>
      </div>
      <div class="module-body">
        <p class="muted" style="margin:0 0 1rem;max-width:62ch">{bilingual(esc(m['desc']['en']), esc(m['desc'].get('fr') or m['desc']['en']))}</p>
        <div class="cluster" style="justify-content:space-between;margin-bottom:1rem" data-progress-module="{esc(m['slug'])}">
          <span class="lr-meta">{len(m['lessons'])} {bilingual('lessons','leçons')}</span>
          <div class="progressbar" style="flex:1;margin-left:1rem"><span data-progress-fill></span></div>
        </div>
        <div class="grid grid-2" style="gap:.6rem">{lessons}</div>
      </div>
    </article>"""

def build_hub():
    prefix = ""
    nlessons = sum(len(m["lessons"]) for m in M["modules"])
    total_min = sum(l["minutes"] for m in M["modules"] for l in m["lessons"])
    hours = round(total_min/60)
    h = head("Boxing4Health Licensee Training Program", "The complete training program for Boxing4Health licensees — Parkinson's education and class delivery.", prefix)
    hero = f"""<section class="hero">
      <div class="hero-media"><img src="{prefix}assets/img/photos/hero-class.jpg" alt="A Boxing4Health class training together" loading="eager" fetchpriority="high"></div>
      <div class="wrap">
      <p class="eyebrow"><span data-icon="graduation-cap"></span>{bilingual('Licensee Training','Formation des licenciés')}</p>
      <p class="hero-motto">{bilingual("Our challenges don't define us — our", "Nos défis ne nous définissent pas —")} <span class="accent">{bilingual("ACTIONS", "nos ACTIONS")}</span> {bilingual("do.", "oui.")}</p>
      <h1>{bilingual("Boxing4Health Licensee Training Program","Programme de formation des licenciés Boxing4Health","span")}</h1>
      <p>{bilingual("Everything you need to coach people living with Parkinson's — the science, the symptoms, and how to run a safe, empowering class.","Tout ce qu'il vous faut pour accompagner les personnes atteintes de la maladie de Parkinson — la science, les symptômes et comment animer un cours sécuritaire et stimulant.","span")}</p>
      <div class="hero-actions">
        <a class="btn btn-lg btn-warm" data-continue href="{prefix}{M['modules'][0]['lessons'][0]['url']}"><span data-icon="arrow-right"></span><span data-i18n="hub.continue">Continue where you left off</span></a>
        <a class="btn btn-lg btn-secondary" href="#modules"><span data-icon="layers"></span>{bilingual('Browse modules','Parcourir les modules')}</a>
      </div>
      <div class="stat-row" style="margin-top:2.2rem;max-width:640px">
        <div class="stat"><div class="stat-num">{len(M['modules'])}</div><div class="stat-label">Modules</div></div>
        <div class="stat"><div class="stat-num">{nlessons}</div><div class="stat-label">{bilingual('Lessons','Leçons')}</div></div>
        <div class="stat"><div class="stat-num">~{hours}h</div><div class="stat-label">{bilingual('of content','de contenu','span')}</div></div>
      </div>
      </div>
    </section>"""

    band = f"""<section class="band">
      <div class="band-media"><img src="{prefix}assets/img/photos/community-seniors.jpg" alt="Boxing4Health participants together" loading="lazy"></div>
      <div class="wrap">
        <p class="eyebrow" style="color:#ffd27a"><span data-icon="heart-pulse"></span>{bilingual('Who you serve','Ceux que vous accompagnez')}</p>
        <p class="pull-quote">{bilingual("You're not just teaching a workout —", "Vous n'enseignez pas qu'un entraînement —")} <span class="accent">{bilingual("you're giving people their fight back.", "vous redonnez aux gens leur combat.")}</span></p>
        <p class="quote-by">{bilingual("The Boxing4Health approach", "L'approche Boxing4Health")}</p>
      </div>
    </section>"""

    progress = f"""<section class="section-tight"><div class="wrap">
      <div class="panel panel-tinted" data-progress-overall>
        <div class="cluster" style="justify-content:space-between">
          <h3 style="margin:0"><span data-i18n="hub.progress">Your progress</span></h3>
          <span class="badge badge-primary"><span data-progress-count>0 / {nlessons}</span></span>
        </div>
        <div class="progressbar" style="margin-top:1rem"><span data-progress-fill></span></div>
        <p class="muted" style="margin:.6rem 0 0"><span data-progress-label>0%</span> <span data-i18n="hub.complete">complete</span><span data-reset-wrap hidden> · <button class="btn-ghost" style="padding:.2rem .4rem;font-size:.9rem;border:0;background:none;cursor:pointer;color:var(--link)" data-progress-reset><span data-i18n="progress.reset">Reset my progress</span></button></span></p>
      </div>
    </div></section>"""

    howto = f"""<section class="section section-tint"><div class="wrap">
      <p class="eyebrow center" style="justify-content:center">{bilingual('How this works','Comment ça marche')}</p>
      <div class="grid grid-3" style="margin-top:1rem">
        <div class="card" data-reveal><span class="chip" data-icon="book-open"></span><h4 style="margin:.8rem 0 .3rem">{bilingual('Work through the modules','Parcourez les modules','span')}</h4><p class="muted">{bilingual('Go in order, or jump to any lesson. Your place is saved on this device.','Suivez l’ordre ou allez à n’importe quelle leçon. Votre progression est enregistrée sur cet appareil.','span')}</p></div>
        <div class="card" data-reveal><span class="chip" data-icon="a-large-small"></span><h4 style="margin:.8rem 0 .3rem">{bilingual('Make it comfortable','Adaptez le confort','span')}</h4><p class="muted">{bilingual('Use the reading menu (top right) for larger text, dark mode, spacing, and French.','Utilisez le menu de lecture (en haut à droite) pour agrandir le texte, le mode sombre, l’interligne et le français.','span')}</p></div>
        <div class="card" data-reveal><span class="chip" data-icon="award"></span><h4 style="margin:.8rem 0 .3rem">{bilingual('Earn your certificate','Obtenez votre certificat','span')}</h4><p class="muted">{bilingual('Finish every lesson and quiz to unlock a printable certificate.','Terminez chaque leçon et questionnaire pour débloquer un certificat imprimable.','span')}</p></div>
      </div>
    </div></section>"""

    modules = "\n".join(module_card(m, prefix) for m in M["modules"])
    modsec = f"""<section class="section" id="modules"><div class="wrap">
      <div class="motif-line"></div>
      <h2>{bilingual('Program modules','Modules du programme','span')}</h2>
      <p class="lead" style="max-width:60ch">{bilingual('Five modules take you from understanding Parkinson’s to confidently running your own class.','Cinq modules vous mènent de la compréhension de la maladie de Parkinson à l’animation confiante de votre propre cours.','span')}</p>
      <div class="stack-lg" style="margin-top:2rem">{modules}</div>
    </div></section>"""

    res = "\n".join(f"""<a class="lesson-row" href="{prefix}{esc(r['url'])}"><span class="chip chip-sm" data-icon="{r.get('icon','book-open')}"></span><span><span class="lr-title">{bilingual(esc(r['title']['en']),esc(r['title'].get('fr') or r['title']['en']))}</span><br><span class="lr-meta">{bilingual(esc(r['summary']['en']),esc(r['summary'].get('fr') or r['summary']['en']))}</span></span><span class="lr-mark" data-icon="arrow-right"></span></a>""" for r in M["resources"])
    ressec = f"""<section class="section-tight"><div class="wrap">
      <h2>{bilingual('Learning resources','Ressources d’apprentissage','span')}</h2>
      <div class="grid grid-2" style="margin-top:1rem">{res}</div>
    </div></section>"""

    cert = f"""<section class="section"><div class="wrap wrap-narrow" data-cert-gate data-unlocked="false">
      <div class="panel" style="text-align:center">
        <span class="chip" data-icon="award" style="margin-inline:auto"></span>
        <h2 style="margin-top:1rem"><span data-i18n="cert.title">Certificate of Completion</span></h2>
        <p class="muted" data-cert-locked><span data-i18n="cert.locked">Complete all modules and quizzes to unlock your certificate.</span></p>
        <a class="btn btn-primary" href="{prefix}certificate.html" data-cert-open><span data-icon="award"></span>{bilingual('View certificate','Voir le certificat','span')}</a>
      </div>
    </div></section>"""

    about = f"""<section class="section-tight"><div class="wrap">
      <span class="eyebrow"><span data-icon="heart-pulse"></span>{bilingual('About this program','À propos du programme')}</span>
      <h2>{bilingual('Who’s behind your training','Qui est derrière votre formation','span')}</h2>
      <p class="lead" style="max-width:64ch">{bilingual('Boxing4Health is an independent health facility delivering research-backed, high-intensity exercise for seniors and people living with Parkinson’s. This licensee training distills the methods used in B4H classes — across its Ottawa, Kanata, Chelsea (QC), and Regina locations — into a coaching curriculum you can run yourself.','Boxing4Health est un établissement de santé indépendant offrant de l’exercice à haute intensité, fondé sur la recherche, pour les aînés et les personnes atteintes de la maladie de Parkinson. Cette formation des licenciés transpose les méthodes des cours B4H — offerts à Ottawa, Kanata, Chelsea (QC) et Regina — en un programme d’enseignement que vous pouvez animer vous-même.','span')}</p>
      <div class="grid grid-2" style="margin-top:1.5rem">
        <article class="card" style="display:flex;gap:1.1rem;align-items:flex-start">
          <img src="{prefix}assets/img/christine-seaby.jpg" alt="Christine Seaby, founder of Boxing4Health, with her dog" width="112" height="140" loading="lazy" style="flex:none;width:112px;height:140px;object-fit:cover;object-position:center 20%;border-radius:var(--r-md);box-shadow:var(--shadow-1)">
          <div style="min-width:0">
            <h3 style="margin:.1rem 0 .3rem">Christine Seaby, RMT</h3>
            <p class="muted" style="margin:0">{bilingual('Founder &amp; owner. A Regulated Health Professional (Registered Massage Therapist) with 14+ years of experience and a background in mixed martial arts, Christine created Boxing4Health to help people living with Parkinson’s improve their quality of life through purposeful exercise.','Fondatrice et propriétaire. Professionnelle de la santé réglementée (massothérapeute agréée) comptant plus de 14 ans d’expérience et une formation en arts martiaux mixtes, Christine a fondé Boxing4Health pour aider les personnes atteintes de la maladie de Parkinson à améliorer leur qualité de vie grâce à un exercice ciblé.','span')}</p>
          </div>
        </article>
        <article class="card">
          <span class="chip" data-icon="quote"></span>
          <h3 style="margin:.8rem 0 .3rem">{bilingual('Our approach','Notre approche','span')}</h3>
          <p class="muted" style="margin:0 0 .7rem">{bilingual('Exercise, education, and community — used together to help people living with Parkinson’s take action against their symptoms.','L’exercice, l’éducation et la communauté — réunis pour aider les personnes atteintes de la maladie de Parkinson à agir contre leurs symptômes.','span')}</p>
          <p style="margin:0;font-family:var(--font-sans);font-weight:var(--fw-black);color:var(--primary)">“{bilingual('Our challenges don’t define us — our ACTIONS do.','Nos défis ne nous définissent pas — nos ACTIONS, oui.','span')}”</p>
        </article>
      </div>
      <p class="muted" style="margin-top:1.4rem;display:inline-flex;align-items:center;gap:.5rem;font-size:var(--fs-sm)"><span data-icon="clipboard-check"></span>{bilingual('Current curriculum · reviewed August 2026 · v1.0','Programme à jour · révisé en août 2026 · v1.0','span')}</p>
    </div></section>"""

    body = hero + progress + howto + band + modsec + ressec + about + cert
    open(os.path.join(SITE,"index.html"),"w",encoding="utf-8").write(h + body + foot(prefix))
    print("built licensee/index.html")

if __name__ == "__main__":
    build_hub()

def _chip(ic): return f'<span class="chip" data-icon="{ic}"></span>'

DOCUMENTS=_data("documents.json").get("documents",[])
VIDEO_GROUPS=[
 {"en":"Getting started","fr":"Pour commencer","items":[("JPnb9okYxw8","Boxing 101")]},
 {"en":"Symptoms in action","fr":"Les symptômes en action","items":[("MIAFilOOloU","Freezing of Gait"),("wrxHJaPulgc","Freezing of Gait — example 2")]},
 {"en":"Exercise demos","fr":"Démonstrations d’exercices","items":[("40Py_LXA-kQ","Ball Throw"),("10Ybc-q-AaE","Stop & Squat"),("VhULAtOM24U","TAHDAHS"),("kw3XHS2swTE","Scarf Snatch"),("DjWv0vljlzw","Sky Reach"),("BeJMw-lkC9o","Double 007"),("EM-VzOs3Xz8","Over the River"),("Q9EWH7yaNmI","Penguin Waddle"),("JBC65ii_IAM","Banded Side Step"),("3fo1INxGGiI","Box Step")]},
]
FURTHER_READING=[
 {"icon":"heart-pulse","name":"Parkinson Canada","url":"https://www.parkinson.ca","en":"National charity — support services, education, and advocacy across Canada.","fr":"Organisme national — services de soutien, éducation et défense des droits au Canada."},
 {"icon":"map-pin","name":"Parkinson Québec","url":"https://parkinsonquebec.ca","en":"Québec-based support, French-language resources, and local groups.","fr":"Soutien au Québec, ressources en français et groupes locaux."},
 {"icon":"book-open","name":"Parkinson’s Foundation","url":"https://www.parkinson.org","en":"Research-backed library, a helpline, and practical living-well guides.","fr":"Bibliothèque fondée sur la recherche, ligne d’aide et guides pratiques."},
 {"icon":"sparkles","name":"Michael J. Fox Foundation","url":"https://www.michaeljfox.org","en":"Research funding, clinical-trial matching, and patient resources.","fr":"Financement de la recherche, essais cliniques et ressources pour les patients."},
 {"icon":"graduation-cap","name":"Davis Phinney Foundation","url":"https://davisphinneyfoundation.org","en":"“Living well” tools with a strong focus on exercise and daily function.","fr":"Outils « bien vivre » axés sur l’exercice et la fonction au quotidien."},
 {"icon":"dumbbell","name":"PD Warrior","url":"https://pdwarrior.com","en":"Neuroplasticity-based exercise program for people with Parkinson’s.","fr":"Programme d’exercices fondé sur la neuroplasticité pour la maladie de Parkinson."},
 {"icon":"megaphone","name":"LSVT Global (BIG & LOUD)","url":"https://www.lsvtglobal.com","en":"The LSVT BIG (movement) and LOUD (voice) therapy programs.","fr":"Les programmes de thérapie LSVT BIG (mouvement) et LOUD (voix)."},
]
GCAT={"parkinsons":("Parkinson’s","Parkinson"),"coaching":("Coaching","Encadrement"),"program":("Program","Programme")}

def _sec_head(anchor, icon, en, fr, intro_en, intro_fr):
    return (f'<section class="res-section" id="{anchor}"><h2>{_chip(icon)}{bilingual(en,fr)}</h2>'
            f'<p class="res-section-intro">{bilingual(intro_en,intro_fr)}</p>')

def _documents_section(prefix):
    def card(d):
        return (f'<a class="file-card" href="{prefix}assets/docs/{d["file"]}" download>'
                f'<span class="file-ico"><span class="file-ext">{d["ext"]}</span></span>'
                f'<span class="file-meta"><span class="file-name">{bilingual(esc(d["en"]),esc(d["fr"]))}</span>'
                f'<span class="file-sub">{bilingual("Download","Télécharger")} · {d["ext"]} · {d["size"]}</span></span>'
                f'<span class="file-dl" data-icon="download"></span></a>')
    intake="".join(card(d) for d in DOCUMENTS if d["cat"]=="intake")
    prog="".join(card(d) for d in DOCUMENTS if d["cat"]=="program")
    return (_sec_head("documents","folder-open","Documents & Forms","Documents et formulaires",
            "Print or download the forms you need to screen, protect, and run your program.",
            "Imprimez ou téléchargez les formulaires nécessaires pour évaluer, protéger et gérer votre programme.")
            +f'<p class="res-subhead">{bilingual("Intake &amp; screening","Admission et évaluation")}</p><div class="files-grid">{intake}</div>'
            +f'<p class="res-subhead">{bilingual("Running your program","Gérer votre programme")}</p><div class="files-grid">{prog}</div></section>')

def _glossary_section():
    g=_data("glossary.json").get("terms",[])
    items=""
    for t in g:
        cl,cf=GCAT.get(t["cat"],("",""))
        cat=f'<span class="gcat" data-cat="{t["cat"]}">{bilingual(cl,cf)}</span>' if cl else ""
        items+=(f'<dl class="gterm" data-cat="{t["cat"]}"><dt>{bilingual(esc(t["en"]),esc(t["fr"]))}{cat}</dt>'
                f'<dd>{bilingual(esc(t["def_en"]),esc(t["def_fr"]))}</dd></dl>')
    n=len(g)
    tools=(f'<div class="glossary-tools"><label class="glossary-search">'
           f'<span data-icon="search"></span><input id="gloss-q" type="search" autocomplete="off" '
           f'placeholder="Search terms…" data-i18n="glossary.search" data-i18n-attr="placeholder" '
           f'aria-label="Search glossary"></label>'
           f'<span class="glossary-count"><span id="gloss-count">{n}</span> {bilingual("terms","termes")}</span></div>')
    empty=f'<p class="glossary-empty" id="gloss-empty" hidden>{bilingual("No terms match your search.","Aucun terme ne correspond.","span")}</p>'
    script=("<script>(function(){var i=document.getElementById('gloss-q');if(!i)return;"
            "var terms=[].slice.call(document.querySelectorAll('#glossary .gterm'));"
            "var c=document.getElementById('gloss-count'),e=document.getElementById('gloss-empty');"
            "i.addEventListener('input',function(){var q=i.value.trim().toLowerCase(),n=0;"
            "terms.forEach(function(t){var m=!q||t.textContent.toLowerCase().indexOf(q)>-1;t.hidden=!m;if(m)n++;});"
            "if(c)c.textContent=n;if(e)e.hidden=n>0;});})();</script>")
    return (_sec_head("glossary","book-open","Glossary","Glossaire",
            "Plain-language definitions of the Parkinson’s, coaching, and program terms used throughout this training.",
            "Définitions en langage clair des termes liés à la maladie de Parkinson, à l’encadrement et au programme.")
            +tools+f'<div class="glossary">{items}</div>'+empty+script+"</section>")

def _videos_section():
    def vid(vid_id,title):
        return (f'<div><div class="video" data-yt="{vid_id}" data-title="{esc(title)}">'
                f'<img class="video-poster" src="https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" alt="" loading="lazy">'
                f'<div class="video-play"><span data-icon="circle-play"></span></div></div>'
                f'<p class="video-cap">{esc(title)}</p></div>')
    out=""
    for grp in VIDEO_GROUPS:
        cards="".join(vid(i,t) for i,t in grp["items"])
        out+=f'<p class="res-subhead">{bilingual(grp["en"],grp["fr"])}</p><div class="video-grid">{cards}</div>'
    return (_sec_head("videos","circle-play","Video Library","Vidéothèque",
            "Every program video in one place — click a thumbnail to play it here.",
            "Toutes les vidéos du programme au même endroit — cliquez sur une vignette pour la lire ici.")
            +out+"</section>")

def _assessments_section():
    tools=_data("assessment-tools.json").get("tools",[])
    def field(lbl_en,lbl_fr,v_en,v_fr):
        return (f'<div class="af"><div class="af-label">{bilingual(lbl_en,lbl_fr)}</div>'
                f'<div class="af-val">{bilingual(esc(v_en),esc(v_fr))}</div></div>')
    cards=""
    for t in tools:
        cards+=(f'<div class="assess-card"><div class="assess-head"><span class="assess-abbr">{esc(t.get("abbr",""))}</span>'
                f'<h3>{bilingual(esc(t["name_en"]),esc(t["name_fr"]))}</h3></div><div class="assess-body">'
                +field("Measures","Mesure",t["measures_en"],t["measures_fr"])
                +field("How","Comment",t["how_en"],t["how_fr"])
                +field("Scoring","Interprétation",t["scoring_en"],t["scoring_fr"])
                +"</div></div>")
    return (_sec_head("assessments","clipboard-list","Assessment Tools","Outils d’évaluation",
            "A quick reference for the balance and mobility tests used to classify and track clients. Not a diagnosis — use alongside professional judgement.",
            "Un aide-mémoire pour les tests d’équilibre et de mobilité servant à classer et suivre les clients. Ne remplace pas un diagnostic — à utiliser avec jugement professionnel.")
            +f'<div class="assess-grid">{cards}</div></section>')

def _quickref_section():
    cards=_data("quick-reference.json").get("cards",[])
    out=""
    for c in cards:
        danger=" qr-danger" if c.get("icon")=="triangle-alert" else ""
        items="".join(f'<li>{bilingual(esc(a),esc(b))}</li>' for a,b in zip(c["items_en"],c["items_fr"]))
        out+=(f'<article class="qr-card{danger}"><div class="qr-head">{_chip(c.get("icon","list-checks"))}'
              f'<h3>{bilingual(esc(c["title_en"]),esc(c["title_fr"]))}</h3></div><div class="qr-body">'
              f'<p class="qr-intro">{bilingual(esc(c["intro_en"]),esc(c["intro_fr"]))}</p>'
              f'<ul class="qr-list">{items}</ul></div></article>')
    return (_sec_head("quick-reference","printer","Quick-Reference Cards","Fiches de référence rapide",
            "One-page cheat-sheets to print and pin up in the gym. Use your browser’s print to save any card as a PDF.",
            "Aide-mémoire d’une page à imprimer et afficher dans la salle. Utilisez l’impression du navigateur pour enregistrer une fiche en PDF.")
            +f'<div class="qr-grid">{out}</div></section>')

def _further_section():
    def lc(r):
        return (f'<a class="link-card" href="{r["url"]}" target="_blank" rel="noopener noreferrer">{_chip(r["icon"])}'
                f'<span class="link-name">{esc(r["name"])}</span>'
                f'<span class="link-desc">{bilingual(esc(r["en"]),esc(r["fr"]))}</span>'
                f'<span class="link-ext" data-icon="external-link"></span></a>')
    cards="".join(lc(r) for r in FURTHER_READING)
    return (_sec_head("further-reading","external-link","Further Reading","Pour aller plus loin",
            "Trusted outside organisations for research, support, and continuing education. Links open in a new tab.",
            "Organismes externes de confiance pour la recherche, le soutien et la formation continue. Les liens s’ouvrent dans un nouvel onglet.")
            +f'<div class="link-grid">{cards}</div></section>')

def _articles_section(prefix):
    rows="".join(f'<a class="lesson-row" href="{prefix}{esc(r["url"])}"><span class="chip" data-icon="{r.get("icon","book-open")}"></span><span><span class="lr-title">{bilingual(esc(r["title"]["en"]),esc(r["title"].get("fr") or r["title"]["en"]))}</span><br><span class="lr-meta">{bilingual(esc(r["summary"]["en"]),esc(r["summary"].get("fr") or r["summary"]["en"]))}</span></span><span class="lr-mark" data-icon="arrow-right"></span></a>' for r in M["resources"])
    return (_sec_head("articles","file-text","Learning Articles","Articles d’apprentissage",
            "In-depth reads that go beyond the core lessons.",
            "Des lectures approfondies qui vont au-delà des leçons de base.")
            +f'<div class="stack">{rows}</div></section>')

def build_resources_index():
    prefix="../"
    h=head("Resources · Boxing4Health Training","Documents, glossary, videos, assessment tools, printable references, and further reading for Boxing4Health licensees.",prefix)
    toc=[("documents","Documents"),("glossary","Glossary"),("videos","Videos"),("assessments","Assessments"),("quick-reference","Quick reference"),("further-reading","Further reading"),("articles","Articles")]
    tocfr={"documents":"Documents","glossary":"Glossaire","videos":"Vidéos","assessments":"Évaluations","quick-reference":"Référence rapide","further-reading":"Pour aller plus loin","articles":"Articles"}
    chips="".join(f'<a href="#{a}">{bilingual(l,tocfr[a])}</a>' for a,l in toc)
    body=(f'<section class="section"><div class="wrap">'
          f'<span class="eyebrow"><span data-icon="folder-open"></span><span data-i18n="nav.resources">Resources</span></span>'
          f'<h1>{bilingual("Coach’s Resource Hub","Centre de ressources","span")}</h1>'
          f'<p class="lead" style="max-width:60ch">{bilingual("Everything in one place — forms, key terms, videos, assessment tools, printable references, and trusted links.","Tout au même endroit — formulaires, termes clés, vidéos, outils d’évaluation, fiches imprimables et liens de confiance.","span")}</p>'
          f'<nav class="toc-chips" aria-label="On this page">{chips}</nav>'
          +_documents_section(prefix)+_glossary_section()+_videos_section()
          +_assessments_section()+_quickref_section()+_further_section()+_articles_section(prefix)
          +'</div></section>')
    open(os.path.join(SITE,"resources/index.html"),"w",encoding="utf-8").write(h+body+foot(prefix))
    print("built licensee/resources/index.html")

def build_404():
    # Served from the domain root for the whole site; assets live under /licensee/.
    prefix="/licensee/"
    h=head("Page not found · Boxing4Health Training","",prefix)
    body=f"""<section class="section"><div class="wrap wrap-narrow center" style="padding-block:5rem">
      <span class="chip" data-icon="triangle-alert" style="margin-inline:auto;width:72px;height:72px"></span>
      <h1 style="margin-top:1.5rem">{bilingual('Page not found','Page introuvable','span')}</h1>
      <p class="lead">{bilingual('That page moved or never existed.','Cette page a été déplacée ou n’existe pas.','span')}</p>
      <div class="cluster" style="justify-content:center;margin-top:1.5rem">
        <a class="btn btn-primary" href="/licensee/"><span data-icon="house"></span>{bilingual('Licensee training','Formation des licenciés','span')}</a>
        <a class="btn btn-secondary" href="/"><span data-icon="layers"></span>{bilingual('All programs','Tous les programmes','span')}</a>
      </div>
    </div></section>"""
    open(os.path.join(ROOT,"404.html"),"w",encoding="utf-8").write(h+body+foot(prefix))
    print("built 404.html (root)")

def build_landing():
    # Program directory at the domain root — lists B4H training programs.
    # Assets/partials/data resolve under /licensee/ via prefix.
    prefix="licensee/"
    h=head("Boxing4Health Training","Boxing4Health training programs — start with the Licensee Training Program.",prefix)
    m0=M["modules"][0]["lessons"][0]["url"]
    nles=sum(len(m["lessons"]) for m in M["modules"])
    nmod=len(M["modules"])
    prog_card=f"""<a class="card card-hover program-card" href="{prefix}index.html">
        <div class="program-card-cover">
          <span class="program-card-wm" data-icon="graduation-cap" aria-hidden="true"></span>
          <span class="chip" data-icon="graduation-cap"></span>
          <span class="status-chip" data-status="next">{bilingual('Available now','Disponible','span')}</span>
        </div>
        <div class="program-card-body">
          <h2>{bilingual('Licensee Training Program','Programme de formation des licenciés','span')}</h2>
          <p class="muted">{bilingual("Everything a Boxing4Health licensee needs — Parkinson’s education, assessment, and class delivery.","Tout ce qu’un licencié Boxing4Health doit savoir — la maladie de Parkinson, l’évaluation et l’animation des cours.","span")}</p>
          <span class="lr-meta">{nmod} {bilingual('modules','modules')} · {nles} {bilingual('lessons','leçons')}</span>
          <span class="btn btn-primary" style="margin-top:1.1rem;pointer-events:none"><span data-icon="arrow-right"></span>{bilingual('Enter program','Ouvrir le programme','span')}</span>
        </div>
      </a>"""
    soon_card=f"""<div class="card program-card program-card-soon" aria-disabled="true">
        <div class="program-card-cover program-card-cover-muted">
          <span class="program-card-wm" data-icon="dumbbell" aria-hidden="true"></span>
          <span class="chip" data-icon="dumbbell"></span>
          <span class="status-chip" data-status="not-started">{bilingual('Coming soon','À venir','span')}</span>
        </div>
        <div class="program-card-body">
          <h2>{bilingual('More programs','Autres programmes','span')}</h2>
          <p class="muted">{bilingual("Additional Boxing4Health training tracks will appear here as they are released.","D’autres parcours de formation Boxing4Health apparaîtront ici au fur et à mesure.","span")}</p>
        </div>
      </div>"""
    body=f"""<section class="hero"><div class="hero-media"><img src="{prefix}assets/img/photos/hero-class.jpg" alt="A Boxing4Health class training together" loading="eager" fetchpriority="high"></div>
      <div class="wrap">
        <span class="eyebrow"><span data-icon="graduation-cap"></span><span>{bilingual('Boxing4Health','Boxing4Health')}</span></span>
        <h1>{bilingual('Training Programs','Programmes de formation','span')}</h1>
        <p>{bilingual('Choose a program to begin. Your progress is saved on this device as you go.','Choisissez un programme pour commencer. Votre progression est enregistrée sur cet appareil.','span')}</p>
      </div></section>
      <section class="section"><div class="wrap">
        <div class="grid grid-2">{prog_card}{soon_card}</div>
      </div></section>"""
    open(os.path.join(ROOT,"index.html"),"w",encoding="utf-8").write(h+body+foot(prefix))
    print("built index.html (root landing)")

if True:
    build_resources_index(); build_404(); build_landing()
