import re, json, os, glob, html as htmllib
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH=os.path.join(ROOT,"_authored")

def tokenize(h):
    toks=[]; parts=re.split(r'(<[^>]+>)', h); in_script=False; sattr=''
    for p in parts:
        if not p: continue
        if p.startswith('<') and p.endswith('>'):
            toks.append(['tag',p]); low=p.lower()
            if low.startswith('<script'): in_script=True; sattr=p
            elif low.startswith('</script'): in_script=False; sattr=''
        else:
            if in_script:
                toks.append(['quiz' if 'data-quiz-questions' in sattr else 'raw', p])
            else:
                toks.append(['text', p])
    return toks

def strings_from(toks):
    out=[]
    for t in toks:
        if t[0]=='text':
            s=htmllib.unescape(t[1])
            if s.strip(): out.append(s)
        elif t[0]=='quiz':
            try: data=json.loads(t[1])
            except: continue
            for q in data:
                out.append(q['q']['en'])
                for o in q['options']: out.append(o['en'])
                if q.get('explain',{}).get('en'): out.append(q['explain']['en'])
    return out

jobs={}; tokens_store={}
for f in sorted(glob.glob(os.path.join(AUTH,"*.html"))):
    slug=os.path.basename(f)[:-5]
    toks=tokenize(open(f,encoding="utf-8").read())
    jobs[slug]=strings_from(toks)
    tokens_store[slug]=toks
os.makedirs("/tmp/fr", exist_ok=True)
json.dump(tokens_store, open("/tmp/fr/tokens.json","w"), ensure_ascii=False)
json.dump(jobs, open("/tmp/fr/to_translate.json","w"), ensure_ascii=False, indent=1)
total=sum(len(v) for v in jobs.values())
print(f"pages: {len(jobs)}  total strings: {total}")
# chunk slugs into 6 groups balanced by string count
items=sorted(jobs.items(), key=lambda x:-len(x[1])); groups=[[] for _ in range(6)]; load=[0]*6
for slug,strs in items:
    i=load.index(min(load)); groups[i].append(slug); load[i]+=len(strs)
for gi,g in enumerate(groups):
    sub={s:jobs[s] for s in g}
    json.dump(sub, open(f"/tmp/fr/chunk_{gi}.json","w"), ensure_ascii=False, indent=1)
    print(f"  chunk {gi}: {len(g)} pages, {sum(len(jobs[s]) for s in g)} strings")
