import re, json, os, glob, html as htmllib
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH=os.path.join(ROOT,"_authored")
tokens=json.load(open("/tmp/fr/tokens.json"))
# merge translated chunks
fr={}
for cf in sorted(glob.glob("/tmp/fr/chunk_*_fr.json")):
    fr.update(json.load(open(cf)))
built=0; skipped=[]
for slug, toks in tokens.items():
    if slug not in fr: skipped.append(slug); continue
    strs=fr[slug]; idx=0; out=[]; ok=True
    for kind,content in toks:
        if kind=='tag' or kind=='raw':
            out.append(content)
        elif kind=='text':
            if content.strip():
                if idx>=len(strs): ok=False; break
                out.append(htmllib.escape(strs[idx], quote=False)); idx+=1
            else:
                out.append(content)
        elif kind=='quiz':
            try: data=json.loads(content)
            except: out.append(content); continue
            for q in data:
                if idx<len(strs): q['q']={'fr':strs[idx]}; idx+=1
                newopts=[]
                for o in q['options']:
                    if idx<len(strs): newopts.append({'fr':strs[idx]}); idx+=1
                    else: newopts.append(o)
                q['options']=newopts
                if q.get('explain',{}).get('en') is not None or 'explain' in q:
                    if idx<len(strs): q['explain']={'fr':strs[idx]}; idx+=1
            out.append(json.dumps(data, ensure_ascii=False))
    if not ok or idx!=len(strs):
        skipped.append(f"{slug}(idx {idx}/{len(strs)})"); continue
    open(os.path.join(AUTH, slug+".fr.html"),"w",encoding="utf-8").write("".join(out)); built+=1
print(f"Built {built} .fr.html files")
if skipped: print("Skipped (missing/mismatch):", skipped)
