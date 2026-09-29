#!/usr/bin/env python3
"""
B4H quality gate — one command that must pass before anything ships.

Run from the repo root:   python3 tools/qa.py

It rebuilds the site from sources and then enforces:
  1. Build succeeds (no tracebacks).
  2. Generated files are in sync with sources (rebuild leaves git clean) —
     proves nobody hand-edited a generated page instead of its source.
  3. Links + partials resolve; no raw HTML leaked into attributes.
  4. Glossary integrity (every term complete; no dupes).
  5. Documents coverage (every file in assets/docs is listed in Resources).
  6. Lesson coverage (every lesson has an authored EN + FR source).
  7. i18n parity (every UI string exists in EN and FR; used keys defined).
  8. Style-drift lint on authored content (no raw hex colours, no emoji).
  9. Accessibility basics on generated pages (one <h1>, every <img> has alt).

Exit code 0 = clean, 1 = one or more gates failed (details printed).
Pure Python stdlib so it runs the same locally, in the pre-commit hook, and in CI.
"""
import json, os, re, sys, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programs import ROOT, active, site_dir, authored_dir

PROGS = active()   # every program folder with a data/modules.json
os.chdir(ROOT)

problems = []
notes = []
def fail(check, msg): problems.append((check, msg))
def note(msg): notes.append(msg)

def read(p):
    with open(p, encoding="utf-8", errors="replace") as f: return f.read()

# ---------------------------------------------------------------- 1. build
def check_build():
    for cmd in (["python3", "tools/build_hub.py"], ["python3", "tools/build_pages.py", "all"]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or "Traceback" in r.stderr:
            fail("build", f"{' '.join(cmd)} failed:\n{r.stderr.strip()[:800]}")

# ---------------------------------------------------------------- 2. drift
GENERATED = ["index.html", "404.html"] + [p for s in PROGS for p in
             (f"{s}/index.html", f"{s}/modules", f"{s}/resources")]
def check_generated_in_sync():
    # After the rebuild above, the working tree must match what's staged/committed.
    # `git diff` (working vs index) is empty when the committer rebuilt and staged
    # the output, and non-empty when they forgot to rebuild or hand-edited a
    # generated page (the rebuild overwrote it). Works the same in CI (index=HEAD).
    r = subprocess.run(["git", "diff", "--name-only", "--"] + GENERATED,
                       capture_output=True, text=True)
    dirty = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if dirty:
        fail("generated-drift",
             "Generated files are out of sync with their sources. Rebuild "
             "(python3 tools/build_hub.py && python3 tools/build_pages.py all) "
             "and stage the output — never hand-edit generated pages:\n  " +
             "\n  ".join(dirty[:20]))

# ---------------------------------------------------------------- 3. links
def check_links():
    r = subprocess.run(["python3", "tools/check_links.py"], capture_output=True, text=True)
    if r.returncode != 0:
        fail("links", r.stdout.strip()[-800:])

# ---------------------------------------------------------------- 4. glossary
GLOSS_CATS = ("parkinsons", "coaching", "program", "wellness")
def check_glossary():
    for s in PROGS: _check_glossary(s)
def _check_glossary(prog):
    p = os.path.join(site_dir(prog), "data/glossary.json")
    try: terms = json.loads(read(p))["terms"]
    except Exception as e: return fail("glossary", f"{prog}: cannot load glossary.json: {e}")
    seen = set()
    for t in terms:
        name = t.get("en", "?")
        for k in ("en", "fr", "def_en", "def_fr", "cat"):
            if not t.get(k): fail("glossary", f"term {name!r} missing '{k}'")
        if t.get("cat") not in GLOSS_CATS:
            fail("glossary", f"{prog}: term {name!r} has invalid cat {t.get('cat')!r}")
        if t.get("en") in seen: fail("glossary", f"{prog}: duplicate term {name!r}")
        seen.add(t.get("en"))
    note(f"{prog} glossary: {len(terms)} terms")

# ---------------------------------------------------------------- 5. documents
def check_documents():
    for s in PROGS: _check_documents(s)
def _check_documents(prog):
    SITE = site_dir(prog)
    p = os.path.join(SITE, "data/documents.json")
    try: docs = json.loads(read(p))["documents"]
    except Exception as e: return fail("documents", f"{prog}: cannot load documents.json: {e}")
    listed = set()
    for d in docs:
        for k in ("file", "en", "fr", "ext", "size", "cat"):
            if not d.get(k): fail("documents", f"doc {d.get('file','?')!r} missing '{k}'")
        f = d.get("file")
        if f:
            listed.add(f)
            if not os.path.exists(os.path.join(SITE, "assets/docs", f)):
                fail("documents", f"{prog}: listed doc not found on disk: assets/docs/{f}")
    on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(SITE, "assets/docs/*"))
               if not os.path.basename(p).startswith(".")}
    for f in sorted(on_disk - listed):
        fail("documents", f"{prog}/assets/docs/{f} exists but is NOT listed in data/documents.json "
                          f"(it won't appear in Resources — add it)")
    note(f"{prog} documents: {len(listed)} listed, {len(on_disk)} on disk")

# ---------------------------------------------------------------- 6. lessons
def check_lesson_sources():
    for s in PROGS: _check_lesson_sources(s)
def _check_lesson_sources(prog):
    AUTH = authored_dir(prog); rel = os.path.relpath(AUTH, ROOT)
    try: mods = json.loads(read(os.path.join(site_dir(prog), "data/modules.json")))
    except Exception as e: return fail("lessons", f"{prog}: cannot load modules.json: {e}")
    items = [l for m in mods.get("modules", []) for l in m["lessons"]] + mods.get("resources", [])
    slugs, urls = set(), set()
    for l in items:
        slug = l.get("slug")
        if slug in slugs: fail("lessons", f"duplicate slug {slug!r}")
        slugs.add(slug)
        if l.get("url") in urls: fail("lessons", f"duplicate url {l.get('url')!r}")
        urls.add(l.get("url"))
        en = os.path.join(AUTH, f"{slug}.html")
        fr = os.path.join(AUTH, f"{slug}.fr.html")
        if not os.path.exists(en): fail("lessons", f"{prog}/{slug}: missing {rel}/{slug}.html")
        if not os.path.exists(fr): fail("lessons", f"{prog}/{slug}: missing French {rel}/{slug}.fr.html")
    note(f"{prog} lessons: {len(items)} items checked for EN+FR sources")

# ---------------------------------------------------------------- 7. i18n
def check_i18n():
    p = os.path.join(ROOT, "assets/js/i18n.js")
    src = read(p)
    m = re.search(r"\ben\s*:\s*\{", src); f = re.search(r"\bfr\s*:\s*\{", src)
    if not (m and f): return fail("i18n", "could not locate en/fr blocks in i18n.js")
    en_src, fr_src = src[m.end():f.start()], src[f.end():]
    en_keys = set(re.findall(r'"([\w.]+)"\s*:', en_src))
    fr_keys = set(re.findall(r'"([\w.]+)"\s*:', fr_src))
    for k in sorted(en_keys - fr_keys): fail("i18n", f"key {k!r} in EN but missing in FR")
    for k in sorted(fr_keys - en_keys): fail("i18n", f"key {k!r} in FR but missing in EN")
    # every data-i18n key actually used must be defined
    used = set()
    for hp in [h for h in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True)
               if not os.path.relpath(h, ROOT).startswith(("_sources", "_authored"))]:
        used |= set(re.findall(r'data-i18n="([\w.]+)"', read(hp)))
    for k in sorted(used - en_keys):
        fail("i18n", f"data-i18n=\"{k}\" is used but not defined in i18n.js")
    note(f"i18n: {len(en_keys)} keys (EN/FR in parity), {len(used)} used")

# ---------------------------------------------------------------- 8. style lint
# Real emoji only: the astral pictograph planes, regional-indicator flags, and
# the emoji variation selector (U+FE0F). Deliberately NOT the BMP Arrows/symbols
# blocks — →, ↑, ★, ✓, •, — etc. are legitimate typography, not emoji.
EMOJI = re.compile("[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF\uFE0F]")
HEX6 = re.compile(r"#[0-9a-fA-F]{6}\b")
STYLE_HEX = re.compile(r'style\s*=\s*"[^"]*#[0-9a-fA-F]{3,6}')
def check_style_lint():
    for p in glob.glob(os.path.join(ROOT, "_authored/*/*.html")):
        s = read(p); rel = os.path.relpath(p, ROOT)
        if HEX6.search(s):
            fail("style", f"{rel}: raw 6-digit hex colour — use design tokens, not hardcoded colours")
        if STYLE_HEX.search(s):
            fail("style", f"{rel}: inline style with a hardcoded colour — use component classes/tokens")
        if EMOJI.search(s):
            fail("style", f"{rel}: emoji in content — use Lucide icons (data-icon=...) instead")
    # data files that render into pages (meal plan, glossary, …) follow the same no-emoji rule
    for s_ in PROGS:
        for p in glob.glob(os.path.join(site_dir(s_), "data", "*.json")):
            if EMOJI.search(read(p)):
                fail("style", f"{os.path.relpath(p, ROOT)}: emoji in data — use Lucide icon names instead")
    note("style: authored content + data scanned for raw hex / inline colours / emoji")

# ---------------------------------------------------------------- 8b. asset version
def check_asset_version():
    # Static (non-generated) served pages hardcode their ?v= cache-bust token and
    # can silently fall behind when V bumps. Confirm they match the build version.
    src = read(os.path.join(ROOT, "tools/build_pages.py"))
    m = re.search(r'^V\s*=\s*"(\d+)"', src, re.M)
    if not m: return
    V = m.group(1)
    for rel in ["styleguide.html"] + [f"{s}/certificate.html" for s in PROGS]:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p): continue
        vers = set(re.findall(r'(?:href|src)="[^"]+\?v=(\d+)"', read(p)))
        stale = sorted(vers - {V})
        if stale:
            fail("asset-version", f"{rel}: asset ?v={','.join(stale)} but build V={V} "
                                  f"(bump this page's ?v to {V} so it cache-busts)")
    note(f"asset-version: static pages pinned to build V={V}")

# ---------------------------------------------------------------- 8c. pending
def check_pending():
    # Not a failure — a running tally of work still owed to the content owner:
    # videos not yet on YouTube, and <!-- REVIEW: … --> notes left by authors.
    for s in PROGS:
        pend, rev = set(), 0
        for p in glob.glob(os.path.join(authored_dir(s), "*.html")):
            t = read(p)
            pend |= set(re.findall(r'data-video-pending="([^"]+)"', t))
            rev += len(re.findall(r"<!--\s*REVIEW:", t))
        if pend or rev:
            note(f"{s} pending: {len(pend)} video(s) awaiting upload, {rev} REVIEW note(s) in sources")

# ---------------------------------------------------------------- 9. a11y
def check_a11y():
    pages = [os.path.join(ROOT, "index.html")]
    for s in PROGS:
        SITE = site_dir(s)
        pages += glob.glob(os.path.join(SITE, "modules/*.html")) + \
                 glob.glob(os.path.join(SITE, "resources/*.html")) + [os.path.join(SITE, "index.html")]
    for p in pages:
        if not os.path.exists(p): continue
        s = read(p); rel = os.path.relpath(p, ROOT)
        h1 = len(re.findall(r"<h1\b", s))
        if h1 != 1: fail("a11y", f"{rel}: expected exactly one <h1>, found {h1}")
        imgs = re.findall(r"<img\b[^>]*>", s)
        for tag in imgs:
            if "alt=" not in tag: fail("a11y", f"{rel}: <img> without alt attribute")
    note(f"a11y: {len(pages)} generated pages checked (one h1, img alt)")

# ---------------------------------------------------------------- run
CHECKS = [check_build, check_generated_in_sync, check_links, check_glossary,
          check_documents, check_lesson_sources, check_i18n, check_style_lint,
          check_asset_version, check_pending, check_a11y]

def main():
    for c in CHECKS:
        try: c()
        except Exception as e: fail(c.__name__, f"check crashed: {e}")
    print("── B4H QA ─────────────────────────────────────────")
    for n in notes: print(f"  · {n}")
    if problems:
        print(f"\n  ✗ {len(problems)} problem(s):\n")
        for check, msg in problems:
            print(f"  [{check}] {msg}")
        print("\nQA FAILED — fix the above before committing.")
        return 1
    print("\n  ✓ all gates passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
