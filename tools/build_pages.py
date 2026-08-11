#!/usr/bin/env python3
"""
B4H page builder.
- Enhanced-backed lessons: extract the source <body> + <style> + <script>,
  scope the CSS to `.enhanced-content`, remap the source's CSS custom
  properties to the site's blue / theme-aware tokens, bump fonts, and wrap
  in the unified site shell (shared header/footer/toolbar/features).
- Wix-text lessons: build clean unified content from the captured Wix text.
Outputs modules/*.html and resources/*.html. Run from repo root.
"""
import json, re, os, html as htmllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENH_DIRS = [os.path.join(ROOT, "_sources/enhanced/boxing-4-health-PD-symptoms"),
            os.path.join(ROOT, "_sources/enhanced/boxing4health-training")]
WIX = {r["stepId"]: r for r in json.load(open(os.path.join(ROOT, "_sources/wix/wix-extract.json")))}
MODULES = json.load(open(os.path.join(ROOT, "data/modules.json")))
V = "3"  # asset cache-bust version

# ---------------------------------------------------------------- helpers
def enh_path(fn):
    for d in ENH_DIRS:
        p = os.path.join(d, fn)
        if os.path.exists(p): return p
    return None

def esc(s): return htmllib.escape(s or "", quote=True)

# French lesson bodies (produced by the translation pass); optional.
WIXFR = {}
_wp = os.path.join(ROOT, "i18n/wix-bodies-fr.json")
if os.path.exists(_wp):
    try: WIXFR = json.load(open(_wp, encoding="utf-8"))
    except Exception: WIXFR = {}

def bl(en, fr, tag="span", cls=""):
    """Bilingual pair: shows EN or FR block per active language."""
    fr = fr or en
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-lang-block="en">{en}</{tag}><{tag}{c} data-lang-block="fr">{fr}</{tag}>'

def tfr(d, key="title"):
    """Return (en, fr) for a modules.json field dict like {'en':..,'fr':..}."""
    v = d.get(key, {})
    return v.get("en",""), (v.get("fr") or v.get("en",""))

# ---------------------------------------------------------------- CSS scoping
def split_rules(css):
    """Yield (selector_or_at, body, is_at_block) at top level."""
    out, i, n = [], 0, len(css)
    depth, buf = 0, ""
    # remove comments
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    n = len(css); i = 0; buf = ""
    while i < n:
        c = css[i]
        if c == "{":
            # find matching close
            sel = buf.strip(); buf = ""
            depth = 1; j = i + 1; inner = ""
            while j < n and depth > 0:
                if css[j] == "{": depth += 1
                elif css[j] == "}": depth -= 1
                if depth > 0: inner += css[j]
                j += 1
            out.append((sel, inner))
            i = j;
        else:
            buf += c; i += 1
    return out

def scope_selector(sel):
    parts = [s.strip() for s in sel.split(",") if s.strip()]
    fixed = []
    for p in parts:
        if p.startswith("@"):  # shouldn't happen here
            fixed.append(p); continue
        # replace leading html/body/:root token
        p2 = re.sub(r"^(?::root|html|body)\b", ".enhanced-content", p)
        if p2 == p:
            if p.startswith("*"):
                p2 = ".enhanced-content " + p
            else:
                p2 = ".enhanced-content " + p
        fixed.append(p2)
    return ", ".join(fixed)

def scope_css(css):
    out = []
    for sel, body in split_rules(css):
        s = sel.strip()
        low = s.lower()
        if low.startswith("@keyframes") or low.startswith("@-webkit-keyframes") or low.startswith("@font-face") or low.startswith("@import") or low.startswith("@charset"):
            if low.startswith("@font-face") or low.startswith("@import") or low.startswith("@charset"):
                continue  # drop external fonts/imports (we self-host)
            out.append("%s{%s}" % (s, body))  # keep keyframes as-is
        elif low.startswith("@media") or low.startswith("@supports"):
            inner = "".join("%s{%s}" % (scope_selector(ss), bb) for ss, bb in split_rules(body))
            out.append("%s{%s}" % (s, inner))
        else:
            out.append("%s{%s}" % (scope_selector(s), body))
    return "\n".join(out)

# Variable remap + font/size normalization appended AFTER scoped CSS.
ENHANCE_OVERRIDE = """
/* --- Unified blue remap for ported content (theme-aware) --- */
.enhanced-content{
  --red:#19679e; --dark:transparent; --charcoal:var(--surface-2); --mid:var(--border);
  --light:var(--text); --muted:var(--text-muted); --gold:#c98a1f; --green:#1e9e77;
  --blue:#2a7fc4; --amber:#c9791a; --teal:#178f7a; --purple:#5a6bd8; --orange:#c96a1a;
  --cream:var(--surface); --warm-cream:var(--surface); --deep:var(--text);
  --olive:#5f7a3a; --terracotta:#c26b3f; --sand:var(--surface-2); --sage:#7f9a5a; --accent:var(--azure);
  background:transparent!important; color:var(--text);
  font-size:clamp(1.02rem,1rem + .2vw,1.12rem); line-height:var(--lh-body);
}
:root[data-theme="dark"] .enhanced-content{
  --charcoal:var(--surface-2); --mid:var(--border); --light:var(--text); --muted:var(--text-muted);
  --red:#4aa3db; --gold:#e0b25a; --blue:#6bb6e6;
}
.enhanced-content, .enhanced-content p, .enhanced-content li, .enhanced-content td,
.enhanced-content .hero-sub, .enhanced-content .card-body, .enhanced-content .st-detail{ font-family:var(--font-body)!important; }
.enhanced-content h1,.enhanced-content h2,.enhanced-content h3,.enhanced-content h4,
.enhanced-content .hero-title,.enhanced-content .section-label,.enhanced-content .card-title,
.enhanced-content .quiz-q,.enhanced-content .st-name{ font-family:var(--font-sans)!important; letter-spacing:normal; }
/* neutralize their full-page chrome — the site shell provides header, hero, footer */
.enhanced-content .breadcrumb, .enhanced-content nav.breadcrumb,
.enhanced-content .module-footer, .enhanced-content .hero,
.enhanced-content header, .enhanced-content .top-nav, .enhanced-content .site-nav{ display:none!important; }
.enhanced-content > .section:first-of-type,
.enhanced-content > section:first-of-type{ padding-top:0!important; }
.enhanced-content a{ color:var(--link); }
.enhanced-content img{ border-radius:var(--r-md); }
/* readable minimum for their small text */
.enhanced-content [style*="font-size"]{ }
.enhanced-content .meta-pill, .enhanced-content .section-label{ font-size:.8rem; }
"""

def extract_parts(fn):
    html = open(enh_path(fn), encoding="utf-8", errors="replace").read()
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.S)
    scripts = [s for s in scripts if "gtag" not in s and "googletag" not in s]
    body = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    body = body.group(1) if body else html
    # strip any leftover <script>/<style>/<link> from body
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<style\b[^>]*>.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<link\b[^>]*>", "", body)
    return styles, scripts, body

# ---------------------------------------------------------------- shell
def head(title, desc, extra_css="", extra_head=""):
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} · Boxing4Health Training</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#19679e">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https://i.ytimg.com; media-src 'self'; frame-src https://www.youtube-nocookie.com https://www.youtube.com; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'">
<link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/img/favicon.svg">
<link rel="stylesheet" href="../assets/css/fonts.css?v={V}">
<link rel="stylesheet" href="../assets/css/tokens.css?v={V}">
<link rel="stylesheet" href="../assets/css/site.css?v={V}">
<link rel="stylesheet" href="../assets/css/print.css?v={V}" media="print">
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
    base = ['icons', 'i18n', 'site', 'progress', 'search', 'read-aloud'] + feature_scripts
    seen=set(); order=[]
    for s in base:
        if s not in seen: seen.add(s); order.append(s)
    return "\n".join(f'<script src="../assets/js/{s}.js?v={V}"></script>' for s in order)

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
    return f"""<section class="section-tight"><div class="wrap wrap-narrow">
  <div class="lesson-head">
    <p class="crumbs"><a href="../index.html" data-i18n="nav.home">Home</a> · <a href="../index.html#modules">{bl(esc(men),esc(mfr))}</a></p>
    <span class="eyebrow"><span class="chip-sm chip" data-icon="{icon}"></span>{bl(esc(men),esc(mfr))}</span>
    <h1>{bl(esc(len_),esc(lfr))}</h1>
    <div class="lesson-meta">
      <span class="meta-pill"><span data-icon="hourglass"></span>{lesson['minutes']} <span data-i18n="lesson.time">min read</span></span>
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
    return f"""<div class="wrap wrap-narrow"><div class="panel panel-tinted" style="text-align:center;margin-top:2rem">
  <button class="btn btn-primary" data-mark-complete data-done="false"><span data-icon="circle-check-big"></span><span data-mc-label>Mark this lesson complete</span></button>
</div>
<span data-complete-sentinel aria-hidden="true"></span>
</div>"""

print("build_pages.py loaded — use build_all() from a driver.")

# ---------------------------------------------------------------- page builders
def flat_lessons():
    seq=[]
    for m in MODULES["modules"]:
        for l in m["lessons"]:
            seq.append((m,l))
    return seq

def body_attrs(lesson, hasquiz):
    return (f' data-lesson-id="{esc(lesson["id"])}" data-lesson-title="{esc(lesson["title"]["en"])}"'
            f' data-lesson-url="{esc(lesson["url"])}" data-lesson-hasquiz="{"true" if hasquiz else "false"}"')

def build_enhanced_page(mod, lesson, prev, nxt):
    styles, scripts, body = extract_parts(lesson["enhancedFile"])
    scoped = scope_css(styles) + ENHANCE_OVERRIDE
    feature = []  # enhanced pages carry their own quiz JS; completion via sentinel/button
    hasquiz = False
    h = head(lesson["title"]["en"], lesson["summary"]["en"] or mod["desc"]["en"], extra_css=scoped)
    h = h.replace("{BODYATTRS}", body_attrs(lesson, hasquiz))
    parts = [h, lesson_header(mod, lesson)]
    # French summary + honest notice (detailed body stays English to avoid
    # duplicating the source page's own interactive JS across two copies).
    _, sfr = tfr(lesson, "summary")
    fr_notice = (f'<div data-lang-block="fr"><div class="wrap wrap-narrow">'
                 f'<div class="callout callout-info"><span class="callout-icon" data-icon="languages"></span>'
                 f'<p class="callout-title">{esc(sfr)}</p><div class="callout-body">'
                 f'<p>Le contenu détaillé de cette leçon est présenté en anglais ci-dessous. '
                 f'La traduction française complète est en cours de révision.</p></div></div></div></div>')
    parts.append('<div class="section-tight">'+fr_notice)
    parts.append('<div class="wrap"><div class="enhanced-content lesson-body" data-lesson-content>')
    parts.append(body)
    parts.append('</div></div></div>')
    parts.append('<section class="section-tight">'+complete_block(lesson)+'</section>')
    parts.append('<section class="section-tight">'+pager(prev,nxt)+'</section>')
    # re-inject their scripts at end (after content)
    inline = "\n".join(f'<script>{s}</script>' for s in scripts)
    tail = foot(feature).replace("</main>", inline+"\n</main>",1) if False else foot(feature)
    parts.append(inline)
    parts.append(tail)
    return "\n".join(parts)

def build_all_enhanced_only():
    seq = flat_lessons()
    made=[]
    for i,(m,l) in enumerate(seq):
        if not l.get("enhancedFile"): continue
        prev = seq[i-1][1] if i>0 else None
        nxt = seq[i+1][1] if i<len(seq)-1 else None
        htmlout = build_enhanced_page(m,l,prev,nxt)
        outp = os.path.join(ROOT, l["url"])
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        open(outp,"w",encoding="utf-8").write(htmlout)
        made.append(l["url"])
    return made

if __name__ == "__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="one":
        # build just lesson1 symptoms for preview
        for m in MODULES["modules"]:
            for l in m["lessons"]:
                if l["enhancedFile"]=="b4h_lesson1_symptoms.html":
                    seq=flat_lessons(); idx=[i for i,(mm,ll) in enumerate(seq) if ll["id"]==l["id"]][0]
                    prev=seq[idx-1][1]; nxt=seq[idx+1][1]
                    open(os.path.join(ROOT,l["url"]),"w").write(build_enhanced_page(m,l,prev,nxt))
                    print("built",l["url"])
    elif len(sys.argv)>1 and sys.argv[1]=="enhanced":
        made=build_all_enhanced_only(); print(f"built {len(made)} enhanced pages")

# ---------------------------------------------------------------- Wix cleaner
from html.parser import HTMLParser

KEEP = {"p","h1","h2","h3","h4","ul","ol","li","a","strong","b","em","i","br","blockquote"}
MAPTAG = {"h1":"h3","h2":"h3","h3":"h4","b":"strong","i":"em"}

# github enhanced filename (normalized) -> internal slug
def _norm(fn):
    fn = re.sub(r'%20',' ', fn); fn = re.sub(r'\s*\(\d+\)','', fn); return fn.lower()
ENH_TO_SLUG = {}
for _m in MODULES["modules"]:
    for _l in _m["lessons"]:
        if _l.get("enhancedFile"): ENH_TO_SLUG[_norm(_l["enhancedFile"])] = _l["slug"]
for _r in MODULES["resources"]:
    if _r.get("enhancedFile"): ENH_TO_SLUG[_norm(_r["enhancedFile"])] = "../resources/"+_r["slug"]

def map_href(href):
    if "github.io" in href and href.endswith(".html"):
        base = _norm(href.split("/")[-1])
        if base in ENH_TO_SLUG:
            s = ENH_TO_SLUG[base]
            return (s + ".html") if not s.startswith("../") else (s + ".html")
    return href

class Cleaner(HTMLParser):
    def __init__(self):
        super().__init__(); self.out=[]; self.stack=[]
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href","")
            if re.search(r'youtu', href): self._skip_a=True; self._a_href=href; return
            self.out.append('<a href="%s">' % esc(map_href(href))); self.stack.append("a"); self._skip_a=False
        elif tag in KEEP:
            t = MAPTAG.get(tag, tag)
            self.out.append("<%s>" % t); self.stack.append(t)
    def handle_endtag(self, tag):
        if tag == "a" and getattr(self,"_skip_a",False): self._skip_a=False; return
        t = MAPTAG.get(tag, tag)
        if tag in KEEP and self.stack and self.stack[-1]==t:
            self.out.append("</%s>" % t); self.stack.pop()
    def handle_data(self, data):
        if getattr(self,"_skip_a",False): return
        txt = re.sub(r'[ \t\n]+',' ', data)
        if txt.strip() or txt==' ': self.out.append(esc(txt))
    def result(self):
        html = "".join(self.out)
        html = re.sub(r'<p>\s*</p>','',html)
        html = re.sub(r'(<br>\s*){2,}','<br>',html)
        return html.strip()

def clean_wix_html(h):
    c = Cleaner(); 
    try: c.feed(h or "")
    except Exception: return ""
    return c.result()

def yt_ids(rec):
    out=[]
    for l in rec.get("links",[]):
        m=re.search(r'(?:youtu\.be/|youtube\.com/(?:embed/|shorts/|watch\?v=))([\w-]{11})', l["href"])
        if m and m.group(1) not in out: out.append(m.group(1))
    for f in rec.get("iframes",[]):
        m=re.search(r'youtube\.com/embed/([\w-]{11})', f)
        if m and m.group(1) not in out: out.append(m.group(1))
    return out

def video_block(vid, title=""):
    poster = "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid
    return (f'<div class="video" data-yt="{esc(vid)}" data-title="{esc(title)}" aria-label="{esc(title or "Video")}">'
            f'<img class="video-poster" src="{poster}" alt="" loading="lazy">'
            f'<div class="video-play"><span data-icon="circle-play"></span></div>'
            f'<div class="video-label">{esc(title)}</div></div>')

def build_wix_page(mod, lesson, prev, nxt):
    rec = WIX.get(lesson.get("wixStepId")) if lesson.get("wixStepId") else None
    vids = lesson.get("videos") or (yt_ids(rec) if rec else [])
    content = clean_wix_html(rec["html"]) if rec else ""
    # external non-video, non-internal links → button row
    ext = []
    if rec:
        for l in rec.get("links",[]):
            h=l["href"]
            if not h or "github.io" in h or "youtu" in h or h.startswith("https://www.boxing4health.com/participant-page"): continue
            if h.startswith("mailto:") or h.startswith("tel:"): continue
            ext.append((l["text"] or h, h))
    feature=[]
    h = head(lesson["title"]["en"], lesson["summary"]["en"] or mod["desc"]["en"])
    h = h.replace("{BODYATTRS}", body_attrs(lesson, False))
    parts=[h, lesson_header(mod, lesson)]
    frbody = WIXFR.get(lesson["slug"])
    parts.append('<section class="section-tight"><div class="wrap wrap-narrow"><div class="prose lesson-body" data-lesson-content>')
    if content:
        parts.append('<div data-lang-block="en">'+content+'</div>')
        parts.append('<div data-lang-block="fr">'+(frbody or content)+'</div>')
    if vids:
        parts.append('<div class="video-grid" style="margin-top:1.5rem">')
        for v in vids: parts.append(video_block(v, lesson["title"]["en"]))
        parts.append('</div>')
    # NOTE: external links are already rendered inline within `content` — do not
    # duplicate them as a button row (that caused the double-URL treatment).
    if lesson.get("type") == "video" and not vids:
        # Native Wix video didn't expose a shareable URL during capture.
        parts.append('<div class="callout callout-info"><span class="callout-icon" data-icon="circle-play"></span>'
                     '<p class="callout-title">'+bl("Video","Vidéo")+'</p><div class="callout-body">'
                     '<p>'+bl("The video for this lesson will be added here.",
                             "La vidéo de cette leçon sera ajoutée ici.")+'</p></div></div>')
    if not content and not vids:
        parts.append('<p class="muted">'+bl("Content coming soon.","Contenu à venir.")+'</p>')
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
        if l.get("enhancedFile"):
            out = build_enhanced_page(m,l,prev,nxt)
        else:
            out = build_wix_page(m,l,prev,nxt)
        p = os.path.join(ROOT, l["url"]); os.makedirs(os.path.dirname(p),exist_ok=True)
        open(p,"w",encoding="utf-8").write(out); made.append(l["url"])
    return made

def build_resources():
    made=[]
    for r in MODULES["resources"]:
        if r.get("enhancedFile"):
            # reuse enhanced porter with a pseudo-module
            pseudo = {"title":{"en":"Resources"}, "desc":{"en":r["summary"]["en"]}}
            styles, scripts, body = extract_parts(r["enhancedFile"])
            scoped = scope_css(styles) + ENHANCE_OVERRIDE
            h = head(r["title"]["en"], r["summary"]["en"], extra_css=scoped).replace("{BODYATTRS}", body_attrs(r, False))
            # resources are one level deep like modules -> ../ paths OK
            parts=[h, lesson_header(pseudo, r),
                   '<div class="section-tight"><div class="wrap"><div class="enhanced-content lesson-body" data-lesson-content>',
                   body, '</div></div></div>',
                   '<section class="section-tight">'+complete_block(r)+'</section>']
            parts += ["\n".join(f'<script>{s}</script>' for s in scripts), foot([])]
            open(os.path.join(ROOT, r["url"]),"w",encoding="utf-8").write("\n".join(parts)); made.append(r["url"])
    return made

if __name__ == "__main__" and len(__import__('sys').argv)>1 and __import__('sys').argv[1]=="all":
    n=build_all(); rr=build_resources()
    print("built", len(n), "module lessons +", len(rr), "resources")
