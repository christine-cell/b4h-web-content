import os, re, sys, glob
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
htmls=[f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_sources","partials","_authored"))]
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
        if not os.path.exists(f"partials/{name}.html"): missing.append((f,f"partial:{name}","partials/"+name+".html"))
print(f"HTML files: {len(htmls)} | local refs checked: {checked} | missing: {len(missing)}")
for f,u,t in missing[:60]: print(f"  MISSING in {f}: {u} -> {t}")
sys.exit(1 if missing else 0)
