#!/usr/bin/env python3
"""Build each program's hub (<program>/index.html) and resources hub
(<program>/resources/index.html), plus the root program directory (index.html)
and the site-wide 404.html.

  python3 tools/build_hub.py

Path prefixes used below:
  prefix → this program's folder (program-relative links, data, docs)
  rp     → the site root (shared /assets/)
"""
import json, os, sys, html as htmllib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programs import ROOT, PROGRAMS, active, site_dir

SITE = None; M = {}
def use(slug):
    global SITE, M
    SITE = site_dir(slug)
    M = json.load(open(os.path.join(SITE, "data/modules.json"), encoding="utf-8"))
def _data(name):
    p=os.path.join(SITE,"data",name)
    return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else {}
V = "41"
def esc(s): return htmllib.escape(s or "", quote=True)

def head(title, desc, rp, program=""):
    prog = f' data-program="{program}"' if program else ""
    return f"""<!doctype html>
<html lang="en" data-theme="light"{prog}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#19679e">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https://i.ytimg.com; media-src 'self'; frame-src https://www.youtube-nocookie.com https://www.youtube.com; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'">
<link rel="icon" href="{rp}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{rp}assets/img/favicon.svg">
<link rel="stylesheet" href="{rp}assets/css/fonts.css?v={V}">
<link rel="stylesheet" href="{rp}assets/css/tokens.css?v={V}">
<link rel="stylesheet" href="{rp}assets/css/site.css?v={V}">
<link rel="stylesheet" href="{rp}assets/css/print.css?v={V}" media="print">
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

def scripts(rp, extra=None):
    names = ["icons","i18n","site","progress","search","read-aloud"] + (extra or [])
    return "\n".join(f'<script src="{rp}assets/js/{n}.js?v={V}"></script>' for n in names)

def foot(rp, extra=None):
    return f"""</main>
<div data-include="footer"></div>
{scripts(rp, extra)}
</body></html>"""

def bilingual(en, fr, tag="span", cls=""):
    fr = fr or en
    c = f' class="{cls}"' if cls else ""
    return (f'<{tag}{c} data-lang-block="en">{en}</{tag}><{tag}{c} data-lang-block="fr">{fr}</{tag}>')

def blf(d, key):
    v = d.get(key, {}); return v.get("en",""), (v.get("fr") or v.get("en",""))

# ---------------- HUB ----------------
KIND_KEY = {"read": "lesson.time", "watch": "lesson.time.watch", "listen": "lesson.time.listen", "do": "lesson.time.do"}

def lesson_row(l, prefix):
    icon = l.get("icon","book-open")
    en, fr = blf(l, "title")
    return f"""<a class="lesson-row" href="{prefix}{esc(l['url'])}" data-lesson-ref="{esc(l['id'])}">
      <span class="chip chip-sm" data-icon="{icon}"></span>
      <span>
        <span class="lr-title">{bilingual(esc(en),esc(fr))}</span><br>
        <span class="lr-meta">{l['minutes']} <span data-i18n="{KIND_KEY.get(l.get('kind','read'),'lesson.time')}">min read</span></span>
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
          <span class="eyebrow">{"Bonus" if m.get("optional") else f"Module {m['num']}"}</span>
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

def build_hub_licensee():
    prefix, rp = "", "../"
    nlessons = sum(len(m["lessons"]) for m in M["modules"])
    total_min = sum(l["minutes"] for m in M["modules"] for l in m["lessons"])
    hours = round(total_min/60)
    h = head("Boxing4Health Licensee Training Program", "The complete training program for Boxing4Health licensees — Parkinson's education and class delivery.", rp, "licensee")
    hero = f"""<section class="hero">
      <div class="hero-media"><img src="{rp}assets/img/photos/hero-class.jpg" alt="A Boxing4Health class training together" loading="eager" fetchpriority="high"></div>
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
      <div class="band-media"><img src="{rp}assets/img/photos/community-seniors.jpg" alt="Boxing4Health participants together" loading="lazy"></div>
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
          <img src="{rp}assets/img/christine-seaby.jpg" alt="Christine Seaby, founder of Boxing4Health, with her dog" width="112" height="140" loading="lazy" style="flex:none;width:112px;height:140px;object-fit:cover;object-position:center 20%;border-radius:var(--r-md);box-shadow:var(--shadow-1)">
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
    open(os.path.join(SITE,"index.html"),"w",encoding="utf-8").write(h + body + foot(rp))
    print("built licensee/index.html")

def _dl(fname):
    """PDFs open in a new tab (every phone can show them); other files download."""
    return ' target="_blank" rel="noopener"' if fname.lower().endswith(".pdf") else " download"

def _chip(ic): return f'<span class="chip" data-icon="{ic}"></span>'

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
GCAT={"parkinsons":("Parkinson’s","Parkinson"),"coaching":("Coaching","Encadrement"),"program":("Program","Programme"),"wellness":("Wellness","Mieux-être")}

def _sec_head(anchor, icon, en, fr, intro_en, intro_fr):
    return (f'<section class="res-section" id="{anchor}"><h2>{_chip(icon)}{bilingual(en,fr)}</h2>'
            f'<p class="res-section-intro">{bilingual(intro_en,intro_fr)}</p>')

def _documents_section(prefix):
    def card(d):
        return (f'<a class="file-card" href="{prefix}assets/docs/{d["file"]}"{_dl(d["file"])}>'
                f'<span class="file-ico"><span class="file-ext">{d["ext"]}</span></span>'
                f'<span class="file-meta"><span class="file-name">{bilingual(esc(d["en"]),esc(d["fr"]))}</span>'
                f'<span class="file-sub">{bilingual("Download","Télécharger")} · {d["ext"]} · {d["size"]}</span></span>'
                f'<span class="file-dl" data-icon="download"></span></a>')
    DOCUMENTS=_data("documents.json").get("documents",[])
    intake="".join(card(d) for d in DOCUMENTS if d["cat"]=="intake")
    prog="".join(card(d) for d in DOCUMENTS if d["cat"]=="program")
    return (_sec_head("documents","folder-open","Documents & Forms","Documents et formulaires",
            "Print or download the forms you need to screen, protect, and run your program.",
            "Imprimez ou téléchargez les formulaires nécessaires pour évaluer, protéger et gérer votre programme.")
            +f'<p class="res-subhead">{bilingual("Intake &amp; screening","Admission et évaluation")}</p><div class="files-grid">{intake}</div>'
            +f'<p class="res-subhead">{bilingual("Running your program","Gérer votre programme")}</p><div class="files-grid">{prog}</div></section>')

def _glossary_section(intro_en="Plain-language definitions of the Parkinson’s, coaching, and program terms used throughout this training.",
                      intro_fr="Définitions en langage clair des termes liés à la maladie de Parkinson, à l’encadrement et au programme."):
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
    return (_sec_head("glossary","book-open","Glossary","Glossaire", intro_en, intro_fr)
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

def build_resources_index_licensee():
    prefix, rp = "../", "../../"
    h=head("Resources · Boxing4Health Training","Documents, glossary, videos, assessment tools, printable references, and further reading for Boxing4Health licensees.",rp,"licensee")
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
    open(os.path.join(SITE,"resources/index.html"),"w",encoding="utf-8").write(h+body+foot(rp))
    print("built licensee/resources/index.html")

def build_404():
    # Served from the domain root for the whole site (any depth) → absolute paths.
    rp="/"
    h=head("Page not found · Boxing4Health Training","",rp)
    body=f"""<section class="section"><div class="wrap wrap-narrow center" style="padding-block:5rem">
      <span class="chip" data-icon="triangle-alert" style="margin-inline:auto;width:72px;height:72px"></span>
      <h1 style="margin-top:1.5rem">{bilingual('Page not found','Page introuvable','span')}</h1>
      <p class="lead">{bilingual('That page moved or never existed.','Cette page a été déplacée ou n’existe pas.','span')}</p>
      <div class="cluster" style="justify-content:center;margin-top:1.5rem">
        <a class="btn btn-primary" href="/licensee/"><span data-icon="house"></span>{bilingual('Licensee training','Formation des licenciés','span')}</a>
        <a class="btn btn-secondary" href="/"><span data-icon="layers"></span>{bilingual('All programs','Tous les programmes','span')}</a>
      </div>
    </div></section>"""
    open(os.path.join(ROOT,"404.html"),"w",encoding="utf-8").write(h+body+foot(rp))
    print("built 404.html (root)")


# ======================================================================
# Pathway to Empowerment (participants)
# ======================================================================
PW_FURTHER=[
 {"icon":"heart-pulse","name":"Parkinson Canada","url":"https://www.parkinson.ca","en":"Support services, education, a helpline and local support groups across Canada.","fr":"Services de soutien, éducation, ligne d’aide et groupes de soutien partout au Canada."},
 {"icon":"map","name":"Parkinson Québec","url":"https://parkinsonquebec.ca","en":"French-language information, support and local groups in Québec.","fr":"Information, soutien et groupes locaux en français au Québec."},
 {"icon":"book-open","name":"Parkinson’s Foundation","url":"https://www.parkinson.org","en":"Easy-to-read guides on symptoms, treatment and living well, plus a helpline.","fr":"Guides faciles à lire sur les symptômes, le traitement et le mieux-vivre, plus une ligne d’aide."},
 {"icon":"sparkles","name":"Davis Phinney Foundation","url":"https://davisphinneyfoundation.org","en":"“Every Victory Counts” tools for living well, with a strong focus on exercise.","fr":"Outils « Every Victory Counts » pour bien vivre, axés sur l’exercice."},
 {"icon":"venus","name":"Parkinson’s Europe — Women & Parkinson’s","url":"https://parkinsonseurope.org/i-have-parkinsons/self-help-and-living-well/women-and-parkinsons/","en":"Women’s health and Parkinson’s: periods, pregnancy, breastfeeding and menopause.","fr":"Santé des femmes et maladie de Parkinson : règles, grossesse, allaitement et ménopause."},
 {"icon":"megaphone","name":"LSVT Global (BIG & LOUD)","url":"https://www.lsvtglobal.com","en":"Find LSVT BIG (movement) and LSVT LOUD (voice) therapists near you.","fr":"Trouvez des thérapeutes LSVT BIG (mouvement) et LSVT LOUD (voix) près de chez vous."},
]
PW_DOC_GROUPS=[("start","Getting started & tracking progress","Premiers pas et suivi des progrès"),
               ("health","Understanding Parkinson’s, stress & sleep","Comprendre la maladie, le stress et le sommeil"),
               ("movement","Exercise, voice & brain","Exercice, voix et cerveau"),
               ("nutrition","Nutrition & gut health","Nutrition et santé intestinale"),
               ("women","Women’s health","Santé des femmes")]

def _pw_documents_section(prefix):
    docs=_data("documents.json").get("documents",[])
    def card(d):
        return (f'<a class="file-card" href="{prefix}assets/docs/{d["file"]}"{_dl(d["file"])}>'
                f'<span class="file-ico"><span class="file-ext">{d["ext"]}</span></span>'
                f'<span class="file-meta"><span class="file-name">{bilingual(esc(d["en"]),esc(d["fr"]))}</span>'
                f'<span class="file-sub">{bilingual("Download","Télécharger")} · {d["ext"]} · {d["size"]}</span></span>'
                f'<span class="file-dl" data-icon="download"></span></a>')
    out=""
    for cat,en,fr in PW_DOC_GROUPS:
        cards="".join(card(d) for d in docs if d["cat"]==cat)
        if cards: out+=f'<p class="res-subhead">{bilingual(en,fr)}</p><div class="files-grid">{cards}</div>'
    return (_sec_head("documents","folder-open","Worksheets & Handouts","Fiches et documents",
            "Every worksheet, checklist and handout from the program — print them or save them to your device.",
            "Toutes les fiches, listes et documents du programme — imprimez-les ou enregistrez-les sur votre appareil.")+out+"</section>")

def _pw_video_library():
    """Every YouTube video used in a Pathway lesson, grouped by module (read from the authored lessons)."""
    import re as _re
    from programs import authored_dir
    AUTH=authored_dir("pathway"); out=""; seen=set(); total=0
    for m in M["modules"]:
        items=[]
        for l in m["lessons"]:
            p=os.path.join(AUTH, l["slug"]+".html")
            if not os.path.exists(p): continue
            src=open(p,encoding="utf-8").read()
            for vid,title in _re.findall(r'data-yt="([\w-]{11})"\s+data-title="([^"]*)"', src):
                if vid in seen: continue
                seen.add(vid); items.append((vid,title,l))
        if not items: continue
        cards="".join(
            f'<div><div class="video" data-yt="{v}" data-title="{t}">'
            f'<img class="video-poster" src="https://i.ytimg.com/vi/{v}/hqdefault.jpg" alt="" loading="lazy">'
            f'<div class="video-play"><span data-icon="circle-play"></span></div></div>'
            f'<p class="video-cap">{t}</p></div>' for v,t,l in items)
        total+=len(items)
        mt=m["title"]
        out+=f'<p class="res-subhead">{bilingual(esc(mt["en"]),esc(mt["fr"]))}</p><div class="video-grid">{cards}</div>'
    return (_sec_head("videos","circle-play","Video Library","Vidéothèque",
            f"All {total} program videos in one place — tap a thumbnail to play it here.",
            f"Les {total} vidéos du programme au même endroit — touchez une vignette pour la lire ici.")+out+"</section>")

def _pw_further_section():
    def lc(r):
        return (f'<a class="link-card" href="{r["url"]}" target="_blank" rel="noopener noreferrer">{_chip(r["icon"])}'
                f'<span class="link-name">{esc(r["name"])}</span>'
                f'<span class="link-desc">{bilingual(esc(r["en"]),esc(r["fr"]))}</span>'
                f'<span class="link-ext" data-icon="external-link"></span></a>')
    return (_sec_head("further-reading","external-link","Trusted Organizations","Organismes de confiance",
            "Reliable places to learn more and find support. Links open in a new tab.",
            "Des sources fiables pour en apprendre davantage et trouver du soutien. Les liens s’ouvrent dans un nouvel onglet.")
            +f'<div class="link-grid">{"".join(lc(r) for r in PW_FURTHER)}</div></section>')

def build_resources_index_pathway():
    prefix, rp = "../", "../../"
    h=head("Resources · Pathway to Empowerment","Worksheets, glossary, video library and trusted organizations for Pathway to Empowerment participants.",rp,"pathway")
    toc=[("documents","Worksheets","Fiches"),("videos","Videos","Vidéos"),("glossary","Glossary","Glossaire"),("further-reading","Trusted organizations","Organismes de confiance")]
    chips="".join(f'<a href="#{a}">{bilingual(en,fr)}</a>' for a,en,fr in toc)
    body=(f'<section class="section"><div class="wrap">'
          f'<span class="eyebrow"><span data-icon="folder-open"></span><span data-i18n="nav.resources">Resources</span></span>'
          f'<h1>{bilingual("Your Resource Library","Votre bibliothèque de ressources","span")}</h1>'
          f'<p class="lead" style="max-width:60ch">{bilingual("Everything from the program in one place — worksheets to print, every video, plain-language definitions, and trusted places for more support.","Tout le programme au même endroit — fiches à imprimer, toutes les vidéos, des définitions en langage clair et des sources fiables de soutien.","span")}</p>'
          f'<nav class="toc-chips" aria-label="On this page">{chips}</nav>'
          +_pw_documents_section(prefix)+_pw_video_library()
          +_glossary_section("Plain-language meanings of the words you’ll meet in this program.","La signification, en langage clair, des mots que vous rencontrerez dans ce programme.")
          +_pw_further_section()
          +'</div></section>')
    os.makedirs(os.path.join(SITE,"resources"),exist_ok=True)
    open(os.path.join(SITE,"resources/index.html"),"w",encoding="utf-8").write(h+body+foot(rp))
    print("built pathway/resources/index.html")

def build_hub_pathway():
    prefix, rp = "", "../"
    core=[m for m in M["modules"] if not m.get("optional")]
    bonus=[m for m in M["modules"] if m.get("optional")]
    nreq=sum(len(m["lessons"]) for m in core)
    h = head("Parkinson’s Pathway to Empowerment · Boxing4Health", "A 10-week program for people living with Parkinson’s — exercise, sleep, stress, balance, nutrition, voice and more.", rp, "pathway")
    first=core[0]["lessons"][0]["url"]
    hero = f"""<section class="hero">
      <div class="hero-media"><img src="{rp}assets/img/photos/class-rings.jpg" alt="A Boxing4Health class moving together under the motto Our challenges don’t define us" loading="eager" fetchpriority="high"></div>
      <div class="wrap">
      <p class="eyebrow"><span data-icon="heart-handshake"></span>{bilingual('Pathway to Empowerment','Parcours d’autonomisation')}</p>
      <p class="hero-motto">{bilingual("Our challenges don’t define us. Our", "Nos défis ne nous définissent pas. Nos")} <span class="accent">{bilingual("ACTIONS", "ACTIONS")}</span> {bilingual("do.", "oui.")}</p>
      <h1>{bilingual("Parkinson’s Pathway to Empowerment","Parcours d’autonomisation Parkinson","span")}</h1>
      <p>{bilingual("Welcome — you made it, and that already says so much about you. Over the next 10 weeks you’ll learn simple, powerful ways to move better, sleep better, eat well and feel stronger. Go at your own pace.","Bienvenue — vous êtes là, et c’est déjà une belle preuve de votre courage. Au cours des 10 prochaines semaines, vous découvrirez des moyens simples et puissants de mieux bouger, mieux dormir, bien manger et vous sentir plus fort(e). Allez à votre rythme.","span")}</p>
      <div class="hero-actions">
        <a class="btn btn-lg btn-warm" data-continue href="{prefix}{first}"><span data-icon="arrow-right"></span><span data-i18n="hub.start">Start the program</span></a>
        <a class="btn btn-lg btn-secondary" href="#modules"><span data-icon="layers"></span>{bilingual('See all modules','Voir tous les modules')}</a>
      </div>
      <div class="stat-row" style="margin-top:2.2rem;max-width:640px">
        <div class="stat"><div class="stat-num">{len(core)}</div><div class="stat-label">Modules</div></div>
        <div class="stat"><div class="stat-num">10</div><div class="stat-label">{bilingual('weeks','semaines')}</div></div>
        <div class="stat"><div class="stat-num">{len(bonus)}</div><div class="stat-label">{bilingual('bonus libraries','bibliothèques bonus','span')}</div></div>
      </div>
      </div>
    </section>"""
    progress = f"""<section class="section-tight"><div class="wrap">
      <div class="panel panel-tinted" data-progress-overall>
        <div class="cluster" style="justify-content:space-between">
          <h3 style="margin:0"><span data-i18n="hub.progress">Your progress</span></h3>
          <span class="badge badge-primary"><span data-progress-count>0 / {nreq}</span></span>
        </div>
        <div class="progressbar" style="margin-top:1rem"><span data-progress-fill></span></div>
        <p class="muted" style="margin:.6rem 0 0"><span data-progress-label>0%</span> <span data-i18n="hub.complete">complete</span><span data-reset-wrap hidden> · <button class="btn-ghost" style="padding:.2rem .4rem;font-size:.9rem;border:0;background:none;cursor:pointer;color:var(--link)" data-progress-reset><span data-i18n="progress.reset">Reset my progress</span></button></span></p>
      </div>
    </div></section>"""
    howto = f"""<section class="section section-tint"><div class="wrap">
      <p class="eyebrow center" style="justify-content:center">{bilingual('How this works','Comment ça marche')}</p>
      <div class="grid grid-3" style="margin-top:1rem">
        <div class="card" data-reveal><span class="chip" data-icon="footprints"></span><h4 style="margin:.8rem 0 .3rem">{bilingual('One step at a time','Un pas à la fois','span')}</h4><p class="muted">{bilingual('You don’t need to do everything at once. Choose what feels right for you today — you can come back to any lesson, any time. Your place is saved on this device.','Pas besoin de tout faire d’un coup. Choisissez ce qui vous convient aujourd’hui — vous pouvez revenir à n’importe quelle leçon, en tout temps. Votre progression est enregistrée sur cet appareil.','span')}</p></div>
        <div class="card" data-reveal><span class="chip" data-icon="message-circle"></span><h4 style="margin:.8rem 0 .3rem">{bilingual('Bring your questions','Apportez vos questions','span')}</h4><p class="muted">{bilingual('Bring your questions to our weekly calls — no question is too big or too small. Between sessions, reach out any time.','Apportez vos questions à nos appels hebdomadaires — aucune question n’est trop grande ou trop petite. Entre les séances, écrivez-nous en tout temps.','span')}</p></div>
        <div class="card" data-reveal><span class="chip" data-icon="a-large-small"></span><h4 style="margin:.8rem 0 .3rem">{bilingual('Make it comfortable','Adaptez le confort','span')}</h4><p class="muted">{bilingual('Tap the reading menu (top right) for bigger text, dark mode, extra spacing, French — or have any page read aloud to you.','Touchez le menu de lecture (en haut à droite) pour agrandir le texte, passer en mode sombre, espacer les lignes, lire en français — ou faire lire la page à voix haute.','span')}</p></div>
      </div>
      <div class="callout callout-safety" style="margin-top:2rem;max-width:860px;margin-inline:auto">
        <span class="callout-icon" data-icon="stethoscope"></span>
        <p class="callout-title">{bilingual('Education, not medical advice','Éducation, et non avis médical','span')}</p>
        <div class="callout-body"><p>{bilingual('This program is for education and support. It doesn’t replace advice from your doctor, neurologist or pharmacist. Check with your care team before starting a new exercise routine, supplement, or big change to your diet or medication — and stop any exercise that causes pain or dizziness.','Ce programme est offert à des fins d’éducation et de soutien. Il ne remplace pas les conseils de votre médecin, de votre neurologue ou de votre pharmacien. Consultez votre équipe de soins avant de commencer un nouveau programme d’exercice, un supplément ou un changement important à votre alimentation ou à votre médication — et arrêtez tout exercice qui cause de la douleur ou des étourdissements.','span')}</p></div>
      </div>
    </div></section>"""
    band = f"""<section class="band">
      <div class="band-media"><img src="{rp}assets/img/photos/snowball-crew.jpg" alt="Smiling Boxing4Health participants holding snowballs" loading="lazy"></div>
      <div class="wrap">
        <p class="eyebrow" style="color:#ffd27a"><span data-icon="users"></span>{bilingual('You’re not alone','Vous n’êtes pas seul(e)')}</p>
        <p class="pull-quote">{bilingual("You don’t have to navigate Parkinson’s alone —", "Vous n’avez pas à affronter la maladie de Parkinson seul(e) —")} <span class="accent">{bilingual("with the right tools and community, there is so much strength to be found.", "avec les bons outils et la bonne communauté, on trouve tant de force.")}</span></p>
        <p class="quote-by">Christine Seaby, RMT</p>
      </div>
    </section>"""
    modsec = f"""<section class="section" id="modules"><div class="wrap">
      <div class="motif-line"></div>
      <h2>{bilingual('Your 12 modules','Vos 12 modules','span')}</h2>
      <p class="lead" style="max-width:60ch">{bilingual('From understanding Parkinson’s to sleep, balance, nutrition, voice and your brain — each module gives you knowledge and a simple action to take.','De la compréhension de la maladie au sommeil, à l’équilibre, à la nutrition, à la voix et au cerveau — chaque module vous donne des connaissances et une action simple à poser.','span')}</p>
      <div class="stack-lg" style="margin-top:2rem">{"".join(module_card(m, prefix) for m in core)}</div>
    </div></section>
    <section class="section section-tint" id="bonus"><div class="wrap">
      <span class="eyebrow"><span data-icon="star"></span>{bilingual('Bonus libraries','Bibliothèques bonus')}</span>
      <h2>{bilingual('Extra resources, whenever you want them','Des ressources en plus, quand vous voulez','span')}</h2>
      <p class="lead" style="max-width:60ch">{bilingual('Women’s health and menopause, freezing and joint health, and recorded webinars with guest experts. These are optional — they don’t count toward your certificate.','Santé des femmes et ménopause, blocage de la marche et santé articulaire, et webinaires enregistrés avec des experts invités. Ils sont facultatifs — ils ne comptent pas pour votre certificat.','span')}</p>
      <div class="stack-lg" style="margin-top:2rem">{"".join(module_card(m, prefix) for m in bonus)}</div>
    </div></section>"""
    about = f"""<section class="section-tight"><div class="wrap">
      <span class="eyebrow"><span data-icon="heart-pulse"></span>{bilingual('Your guide','Votre guide')}</span>
      <h2>{bilingual('Meet Christine','Faites la connaissance de Christine','span')}</h2>
      <div class="grid grid-2" style="margin-top:1.5rem">
        <article class="card" style="display:flex;gap:1.1rem;align-items:flex-start">
          <img src="{rp}assets/img/christine-seaby.jpg" alt="Christine Seaby, founder of Boxing4Health, with her dog" width="112" height="140" loading="lazy" style="flex:none;width:112px;height:140px;object-fit:cover;object-position:center 20%;border-radius:var(--r-md);box-shadow:var(--shadow-1)">
          <div style="min-width:0">
            <h3 style="margin:.1rem 0 .3rem">Christine Seaby, RMT</h3>
            <p class="muted" style="margin:0">{bilingual('Founder of Boxing4Health and a Registered Massage Therapist, Christine created this program to help people living with Parkinson’s take action — through exercise, education and community. “I am truly honoured to be part of your journey.”','Fondatrice de Boxing4Health et massothérapeute agréée, Christine a créé ce programme pour aider les personnes atteintes de la maladie de Parkinson à passer à l’action — par l’exercice, l’éducation et la communauté. « C’est un véritable honneur de faire partie de votre chemin. »','span')}</p>
          </div>
        </article>
        <article class="card">
          <span class="chip" data-icon="message-circle"></span>
          <h3 style="margin:.8rem 0 .3rem">{bilingual('Questions?','Des questions ?','span')}</h3>
          <p class="muted" style="margin:0 0 .7rem">{bilingual('Bring them to your weekly call, or reach Christine any time:','Apportez-les à votre appel hebdomadaire, ou joignez Christine en tout temps :','span')}</p>
          <p style="margin:0"><a href="mailto:christine@boxing4health.com">christine@boxing4health.com</a><br><a href="tel:+16132242694">613.224.2694</a></p>
        </article>
      </div>
    </div></section>"""
    cert = f"""<section class="section"><div class="wrap wrap-narrow" data-cert-gate data-unlocked="false">
      <div class="panel" style="text-align:center">
        <span class="chip" data-icon="award" style="margin-inline:auto"></span>
        <h2 style="margin-top:1rem"><span data-i18n="cert.title">Certificate of Completion</span></h2>
        <p class="muted" data-cert-locked><span data-i18n="cert.locked.pathway">Finish Modules 1–12 to unlock your certificate. The bonus libraries are optional.</span></p>
        <a class="btn btn-primary" href="{prefix}certificate.html" data-cert-open><span data-icon="award"></span>{bilingual('View certificate','Voir le certificat','span')}</a>
      </div>
    </div></section>"""
    body = hero + progress + howto + modsec + band + about + cert
    open(os.path.join(SITE,"index.html"),"w",encoding="utf-8").write(h + body + foot(rp))
    print("built pathway/index.html")

# Root program directory cards — one per program (add a program here when it ships).
LANDING_CARDS = {
    "licensee": {"icon": "graduation-cap",
        "desc": ("Everything a Boxing4Health licensee needs — Parkinson’s education, assessment, and class delivery.",
                 "Tout ce qu’un licencié Boxing4Health doit savoir — la maladie de Parkinson, l’évaluation et l’animation des cours."),
        "who": ("For licensed coaches", "Pour les entraîneurs licenciés")},
    "pathway": {"icon": "heart-handshake",
        "desc": ("A 10-week program for people living with Parkinson’s — exercise, sleep, stress, balance, nutrition, voice, and more.",
                 "Un programme de 10 semaines pour les personnes atteintes de la maladie de Parkinson — exercice, sommeil, stress, équilibre, nutrition, voix et plus."),
        "who": ("For program participants", "Pour les participants")},
}

def build_landing():
    # Program directory at the domain root — one card per active program.
    rp = ""
    h=head("Boxing4Health Training","Boxing4Health training programs.",rp)
    cards=""
    for slug in active():
        use(slug); c=LANDING_CARDS.get(slug, {"icon":"book-open","desc":("",""),"who":("","")})
        name=PROGRAMS[slug]["name"]
        nles=sum(len(m["lessons"]) for m in M["modules"]); nmod=len(M["modules"])
        cards+=f"""<a class="card card-hover program-card" href="{slug}/index.html">
        <div class="program-card-cover">
          <span class="program-card-wm" data-icon="{c['icon']}" aria-hidden="true"></span>
          <span class="chip" data-icon="{c['icon']}"></span>
          <span class="status-chip" data-status="next">{bilingual(*c['who'],'span')}</span>
        </div>
        <div class="program-card-body">
          <h2>{bilingual(*name,'span')}</h2>
          <p class="muted">{bilingual(*c['desc'],'span')}</p>
          <span class="lr-meta">{nmod} {bilingual('modules','modules')} · {nles} {bilingual('lessons','leçons')}</span>
          <span class="btn btn-primary" style="margin-top:1.1rem;pointer-events:none"><span data-icon="arrow-right"></span>{bilingual('Enter program','Ouvrir le programme','span')}</span>
        </div>
      </a>"""
    body=f"""<section class="hero"><div class="hero-media"><img src="{rp}assets/img/photos/hero-class.jpg" alt="A Boxing4Health class training together" loading="eager" fetchpriority="high"></div>
      <div class="wrap">
        <span class="eyebrow"><span data-icon="graduation-cap"></span><span>{bilingual('Boxing4Health','Boxing4Health')}</span></span>
        <h1>{bilingual('Training Programs','Programmes de formation','span')}</h1>
        <p>{bilingual('Choose a program to begin. Your progress is saved on this device as you go.','Choisissez un programme pour commencer. Votre progression est enregistrée sur cet appareil.','span')}</p>
      </div></section>
      <section class="section"><div class="wrap">
        <div class="grid grid-2">{cards}</div>
      </div></section>"""
    open(os.path.join(ROOT,"index.html"),"w",encoding="utf-8").write(h+body+foot(rp))
    print("built index.html (root landing)")

BUILDERS = {
    "licensee": (build_hub_licensee, build_resources_index_licensee),
    "pathway":  (build_hub_pathway, build_resources_index_pathway),
}

if __name__ == "__main__":
    for slug in active():
        use(slug)
        for fn in BUILDERS.get(slug, ()): fn()
    build_404(); build_landing()
