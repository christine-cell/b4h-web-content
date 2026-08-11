#!/usr/bin/env python3
"""Build index.html (hub), resources/index.html, and 404.html."""
import json, os, html as htmllib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "data/modules.json")))
V = "7"
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
    return f"""<article class="card" data-reveal id="{esc(m['slug'])}" style="padding:clamp(1.2rem,3vw,2rem)">
      <div class="cluster" style="justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">
        <div class="cluster" style="gap:1rem">
          <span class="chip" data-icon="{m['icon']}" style="width:60px;height:60px"></span>
          <div>
            <span class="eyebrow" style="margin:0">Module {m['num']}</span>
            <h3 style="margin:.1rem 0 0">{bilingual(esc(m['title']['en'].split('·')[-1].strip()), esc((m['title'].get('fr') or m['title']['en']).split('·')[-1].strip()))}</h3>
            <p class="muted" style="margin:.3rem 0 0;max-width:60ch">{bilingual(esc(m['desc']['en']), esc(m['desc'].get('fr') or m['desc']['en']))}</p>
          </div>
        </div>
        <div style="min-width:180px;flex:0 0 auto" data-progress-module="{esc(m['slug'])}">
          <div class="cluster" style="justify-content:space-between"><span class="lr-meta">{len(m['lessons'])} {bilingual('lessons','leçons')}</span><span class="badge badge-primary" data-progress-count>0/{len(m['lessons'])}</span></div>
          <div class="progressbar" style="margin-top:.5rem"><span data-progress-fill></span></div>
        </div>
      </div>
      <div class="grid grid-2" style="margin-top:1.4rem;gap:.6rem">{lessons}</div>
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
        <p class="muted" style="margin:.6rem 0 0"><span data-progress-label>0%</span> <span data-i18n="hub.complete">complete</span> · <button class="btn-ghost" style="padding:.2rem .4rem;font-size:.9rem;border:0;background:none;cursor:pointer;color:var(--link)" data-progress-reset><span data-i18n="progress.reset">Reset my progress</span></button></p>
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

    body = hero + progress + howto + band + modsec + ressec + cert
    open(os.path.join(ROOT,"index.html"),"w",encoding="utf-8").write(h + body + foot(prefix))
    print("built index.html")

if __name__ == "__main__":
    build_hub()

def build_resources_index():
    prefix="../"
    h=head("Resources · Boxing4Health Training","Learning resources and tools for Boxing4Health licensees.",prefix)
    rows="\n".join(f"""<a class="lesson-row" href="{prefix}{esc(r['url'])}" data-reveal><span class="chip" data-icon="{r.get('icon','book-open')}"></span><span><span class="lr-title">{bilingual(esc(r['title']['en']),esc(r['title'].get('fr') or r['title']['en']))}</span><br><span class="lr-meta">{bilingual(esc(r['summary']['en']),esc(r['summary'].get('fr') or r['summary']['en']))}</span></span><span class="lr-mark" data-icon="arrow-right"></span></a>""" for r in M["resources"])
    body=f"""<section class="section"><div class="wrap wrap-narrow">
      <div class="motif-line"></div>
      <span class="eyebrow"><span data-icon="book-open"></span><span data-i18n="nav.resources">Resources</span></span>
      <h1>{bilingual('Learning Resources','Ressources d’apprentissage','span')}</h1>
      <p class="lead">{bilingual('Extra reading and tools to support your coaching.','Lectures et outils supplémentaires pour soutenir votre enseignement.','span')}</p>
      <div class="stack" style="margin-top:2rem">{rows}</div>
    </div></section>"""
    open(os.path.join(ROOT,"resources/index.html"),"w",encoding="utf-8").write(h+body+foot(prefix))
    print("built resources/index.html")

def build_404():
    prefix="/"
    h=head("Page not found · Boxing4Health Training","",prefix).replace('href="/assets','href="/assets')
    body=f"""<section class="section"><div class="wrap wrap-narrow center" style="padding-block:5rem">
      <span class="chip" data-icon="triangle-alert" style="margin-inline:auto;width:72px;height:72px"></span>
      <h1 style="margin-top:1.5rem">{bilingual('Page not found','Page introuvable','span')}</h1>
      <p class="lead">{bilingual('That page moved or never existed.','Cette page a été déplacée ou n’existe pas.','span')}</p>
      <a class="btn btn-primary" href="/index.html"><span data-icon="house"></span>{bilingual('Back to the program','Retour au programme','span')}</a>
    </div></section>"""
    open(os.path.join(ROOT,"404.html"),"w",encoding="utf-8").write(h+body+foot(prefix))
    print("built 404.html")

if True:
    build_resources_index(); build_404()
