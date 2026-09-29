#!/usr/bin/env python3
"""
B4H lesson builder — wraps each authored lesson body in the unified site shell.

  python3 tools/build_pages.py all              # every program
  python3 tools/build_pages.py all licensee     # one program

Sources:  _authored/<program>/<slug>.html  (+ <slug>.fr.html for French)
Output:   <program>/modules/<slug>.html, <program>/resources/<slug>.html
Shared assets are served from the root /assets/ (two levels up from a lesson).
"""
import json, re, os, sys, html as htmllib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programs import ROOT, active, site_dir, authored_dir

V = "34"  # asset cache-bust version (keep in sync with build_hub.py)

# Set per program by use()
PROGRAM = SITE = AUTH = None
MODULES = {}

def use(slug):
    global PROGRAM, SITE, AUTH, MODULES
    PROGRAM, SITE, AUTH = slug, site_dir(slug), authored_dir(slug)
    MODULES = json.load(open(os.path.join(SITE, "data/modules.json"), encoding="utf-8"))

# ---------------------------------------------------------------- helpers
def esc(s): return htmllib.escape(s or "", quote=True)

def bl(en, fr, tag="span", cls=""):
    """Bilingual pair: shows EN or FR block per active language."""
    fr = fr or en
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-lang-block="en">{en}</{tag}><{tag}{c} data-lang-block="fr">{fr}</{tag}>'

def tfr(d, key="title"):
    """Return (en, fr) for a modules.json field dict like {'en':..,'fr':..}."""
    v = d.get(key, {})
    return v.get("en",""), (v.get("fr") or v.get("en",""))

# ---------------------------------------------------------------- shell
RP = "../../"   # lesson pages sit at <program>/<dir>/<page>.html → root is two up

def head(title, desc, extra_css="", extra_head=""):
    return f"""<!doctype html>
<html lang="en" data-theme="light" data-program="{PROGRAM}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} · Boxing4Health Training</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#19679e">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https://i.ytimg.com; media-src 'self'; frame-src https://www.youtube-nocookie.com https://www.youtube.com; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'">
<link rel="icon" href="{RP}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{RP}assets/img/favicon.svg">
<link rel="stylesheet" href="{RP}assets/css/fonts.css?v={V}">
<link rel="stylesheet" href="{RP}assets/css/tokens.css?v={V}">
<link rel="stylesheet" href="{RP}assets/css/site.css?v={V}">
<link rel="stylesheet" href="{RP}assets/css/print.css?v={V}" media="print">
{extra_head}
<script>(function(){{try{{var d=document.documentElement,s=localStorage;
d.setAttribute('data-theme',s.getItem('b4h-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));
d.setAttribute('lang',s.getItem('b4h-lang')||'en');
if(s.getItem('b4h-contrast')==='high')d.setAttribute('data-contrast','high');
d.style.setProperty('--font-scale',s.getItem('b4h-font')||'1');
d.style.setProperty('--line-mult',s.getItem('b4h-line')||'1');}}catch(e){{}}}})();</script>
{('<style>'+extra_css+'</style>') if extra_css else ''}
</head>
<body{{BODYATTRS}}>
<div data-include="header"></div>
<main id="main">
"""

def scripts_tag(feature_scripts):
    base = ['icons', 'i18n', 'site', 'progress', 'search', 'read-aloud', 'glossary-terms'] + feature_scripts
    seen=set(); order=[]
    for s in base:
        if s not in seen: seen.add(s); order.append(s)
    return "\n".join(f'<script src="{RP}assets/js/{s}.js?v={V}"></script>' for s in order)

def foot(feature_scripts):
    return f"""</main>
<div data-include="footer"></div>
{scripts_tag(feature_scripts)}
</body>
</html>
"""

def lesson_header(mod, lesson):
    icon = lesson.get("icon","book-open")
    men, mfr = tfr(mod, "title")
    len_, lfr = tfr(lesson, "title")
    kind = lesson.get("kind", "read")
    meta = ('<span class="meta-pill"><span data-icon="hourglass"></span>'
            f'{lesson["minutes"]} <span data-i18n="lesson.time{"" if kind=="read" else "." + kind}">min read</span></span>')
    return f"""<section class="section-tight"><div class="wrap wrap-narrow">
  <div class="lesson-head">
    <p class="crumbs"><a href="../index.html" data-i18n="nav.home">Home</a> · <a href="../index.html#modules">{bl(esc(men),esc(mfr))}</a></p>
    <span class="eyebrow"><span class="chip-sm chip" data-icon="{icon}"></span>{bl(esc(men),esc(mfr))}</span>
    <h1>{bl(esc(len_),esc(lfr))}</h1>
    <div class="lesson-meta">
      {meta}
      <span class="meta-pill"><span data-icon="type"></span><span data-i18n="lesson.updated">Updated</span> 2026</span>
    </div>
  </div>
</div></section>
"""

def pager(prev, nxt):
    def cell(l, dirn, cls):
        if not l:
            return f'<a class="{cls} disabled" aria-hidden="true"></a>'
        label = "lesson.prev" if dirn=="prev" else "lesson.next"
        icon = "arrow-left" if dirn=="prev" else "arrow-right"
        en, fr = tfr(l, "title")
        return (f'<a class="{cls}" href="{esc(l["slug"])}.html">'
                f'<span class="pager-ico" data-icon="{icon}"></span>'
                f'<span class="pager-txt"><span class="pager-dir" data-i18n="{label}">{dirn}</span>'
                f'<span class="pager-title">{bl(esc(en),esc(fr))}</span></span></a>')
    return f'<div class="wrap wrap-narrow"><nav class="pager" aria-label="Lesson navigation">{cell(prev,"prev","prev")}{cell(nxt,"next","next")}</nav></div>'

def complete_block(lesson):
    return f"""<div class="wrap wrap-narrow" style="text-align:center;margin-top:1rem">
  <button class="btn btn-primary btn-complete" data-mark-complete data-done="false"><span data-icon="circle-check-big"></span><span data-mc-label>Mark this lesson complete</span></button>
  <span data-complete-sentinel aria-hidden="true"></span>
</div>"""

# ---------------------------------------------------------------- page builders
def flat_lessons():
    return [(m, l) for m in MODULES["modules"] for l in m["lessons"]]

def body_attrs(lesson, hasquiz):
    return (f' data-lesson-id="{esc(lesson["id"])}" data-lesson-title="{esc(lesson["title"]["en"])}"'
            f' data-lesson-url="{esc(lesson["url"])}" data-lesson-hasquiz="{"true" if hasquiz else "false"}"')

def wrap_tables(html):
    """Wrap bare <table> in a horizontally-scrollable container so wide tables
    scroll inside their box instead of overflowing the page on mobile."""
    return re.sub(r"(<table\b.*?</table>)", r'<div class="table-wrap">\1</div>', html, flags=re.S)

def read_authored(slug):
    inner = wrap_tables(open(os.path.join(AUTH, slug+".html"), encoding="utf-8").read())
    fr_path = os.path.join(AUTH, slug+".fr.html")
    fr_inner = wrap_tables(open(fr_path, encoding="utf-8").read()) if os.path.exists(fr_path) else None
    return inner, fr_inner

def lang_body(inner, fr_inner):
    if fr_inner:
        return '<div data-lang-block="en">'+inner+'</div>\n<div data-lang-block="fr">'+fr_inner+'</div>'
    return inner

def build_authored_page(mod, lesson, prev, nxt):
    """Wrap a hand/AI re-authored lesson body (unified components) in the shell."""
    inner, fr_inner = read_authored(lesson["slug"])
    hasquiz = "data-quiz" in inner
    feature = (["quiz"] if hasquiz else []) + (["selfcheck"] if "data-selfcheck" in inner else []) \
              + (["audio-slides"] if "data-audio-slides" in inner else []) \
              + (["finale"] if "data-finale" in inner else [])
    h = head(lesson["title"]["en"], lesson["summary"]["en"] or mod["desc"]["en"])
    h = h.replace("{BODYATTRS}", body_attrs(lesson, hasquiz))
    parts = [h, lesson_header(mod, lesson)]
    parts.append('<section class="section-tight"><div class="wrap wrap-narrow"><div class="prose lesson-body" data-lesson-content>')
    parts.append(lang_body(inner, fr_inner))
    parts.append('</div></div></section>')
    parts.append('<section class="section-tight">'+complete_block(lesson)+'</section>')
    parts.append('<section class="section-tight">'+pager(prev,nxt)+'</section>')
    parts.append(foot(feature))
    return "\n".join(parts)

def build_all():
    seq = flat_lessons(); made=[]
    for i,(m,l) in enumerate(seq):
        prev = seq[i-1][1] if i>0 else None
        nxt = seq[i+1][1] if i<len(seq)-1 else None
        out = build_authored_page(m,l,prev,nxt)
        p = os.path.join(SITE, l["url"]); os.makedirs(os.path.dirname(p),exist_ok=True)
        open(p,"w",encoding="utf-8").write(out); made.append(l["url"])
    return made

def build_resources():
    made=[]
    for r in MODULES.get("resources", []):
        inner, fr_inner = read_authored(r["slug"])
        hasquiz = "data-quiz" in inner
        pseudo = {"title":{"en":"Resources","fr":"Ressources"}, "desc":{"en":r["summary"]["en"],"fr":r["summary"].get("fr","")}}
        h = head(r["title"]["en"], r["summary"]["en"]).replace("{BODYATTRS}", body_attrs(r, hasquiz))
        parts=[h, lesson_header(pseudo, r),
               '<section class="section-tight"><div class="wrap wrap-narrow"><div class="prose lesson-body" data-lesson-content>',
               lang_body(inner, fr_inner), '</div></div></section>',
               '<section class="section-tight">'+complete_block(r)+'</section>',
               foot(["quiz"] if hasquiz else [])]
        p = os.path.join(SITE, r["url"]); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p,"w",encoding="utf-8").write("\n".join(parts)); made.append(r["url"])
    return made

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        progs = sys.argv[2:] or active()
        for slug in progs:
            use(slug)
            n = build_all(); rr = build_resources()
            print(f"{slug}: built {len(n)} lessons + {len(rr)} resources")
    else:
        print("usage: python3 tools/build_pages.py all [program ...]")
