import os, re, sys, glob
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
htmls=[f for f in glob.glob("**/*.html", recursive=True)
       if not f.startswith(("_sources","_authored")) and "/partials/" not in "/"+f]
missing=[]; checked=0
attr=re.compile(r'(?:href|src)="([^"#?]+)(?:[?#][^"]*)?"')
for f in htmls:
    s=open(f,encoding="utf-8",errors="replace").read()
    base=os.path.dirname(f)
    for m in attr.findall(s):
        u=m.strip()
        if '{{' in u: continue
        if u.startswith(("http://","https://","mailto:","tel:","data:","//","javascript:")): continue
        if u in ("","/"): continue
        # resolve
        if u.startswith("/"):
            target=u.lstrip("/")
        else:
            target=os.path.normpath(os.path.join(base,u))
        checked+=1
        if not os.path.exists(target):
            missing.append((f,u,target))
# partial includes are fetched by JS at runtime: verify they exist
for f in htmls:
    s=open(f,encoding="utf-8",errors="replace").read()
    for name in re.findall(r'data-include="([^"]+)"', s):
        # partials are fetched at runtime from <program>/partials/ (data-program
        # on <html>), or from the root partials/ for program-less pages
        m=re.search(r'<html[^>]*data-program="([^"]+)"', s)
        pdir=(m.group(1)+"/partials") if m else "partials"
        if not os.path.exists(f"{pdir}/{name}.html"):
            missing.append((f,f"partial:{name}",f"{pdir}/{name}.html"))
# regression guard: a raw HTML tag leaking into an attribute value (e.g. a
# bilingual() span dumped into placeholder="…") — almost always a bug.
attrtag=re.compile(r'\b(?:placeholder|title|alt|value|aria-[a-z]+|content|data-title)="[^"]*<[^"]*"')
badattr=[]
for f in htmls:
    s=open(f,encoding="utf-8",errors="replace").read()
    for m in attrtag.findall(s):
        badattr.append((f, m[:80]))
if badattr:
    print(f"ATTR-TAG LEAKS: {len(badattr)}")
    for f,m in badattr[:20]: print(f"  {f}: {m}")

print(f"HTML files: {len(htmls)} | local refs checked: {checked} | missing: {len(missing)} | attr-tag leaks: {len(badattr)}")
missing = missing + badattr
for f,u,t in missing[:60]: print(f"  MISSING in {f}: {u} -> {t}")
sys.exit(1 if missing else 0)
