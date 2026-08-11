import os, re, glob, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
issues={}
EMOJI=re.compile(r'[\U0001F000-\U0001FAFF☀-➿←-⇿⬀-⯿]')
KNOWN_CLASSES=set("""lead label panel panel-tinted check-list steps step step-body accordion acc-trigger acc-panel acc-panel-inner acc-chevron chip chip-sm badge callout callout-info callout-coach callout-safety callout-danger callout-icon callout-title callout-body grid grid-cards grid-2 grid-3 card card-hover stat-row stat stat-num stat-label flip flip-inner flip-face flip-front flip-back muted quiz video video-grid video-poster video-play video-label file-grid file-card file-ico file-ext file-meta file-name file-sub file-dl btn btn-primary btn-secondary btn-ghost btn-warm btn-lg btn-block cluster stack tabs tablist tabpanel gloss gloss-pop eyebrow center""".split())
for f in sorted(glob.glob(os.path.join(ROOT,"_authored","*.html"))):
    if f.endswith("_SPEC.md"): continue
    s=open(f,encoding="utf-8").read(); base=os.path.basename(f); probs=[]
    if 'style="' in s or "style='" in s: probs.append("inline style=")
    if EMOJI.search(s): probs.append("emoji: "+repr(EMOJI.search(s).group()))
    if re.search(r'#[0-9a-fA-F]{3,6}\b', s): probs.append("raw hex color")
    # h2 without id
    for h2 in re.findall(r'<h2\b([^>]*)>', s):
        if 'id=' not in h2: probs.append("h2 without id")
    # scripts other than quiz json
    for sc in re.findall(r'<script\b([^>]*)>', s):
        if 'application/json' not in sc: probs.append("non-quiz script")
    # imgs without alt
    for img in re.findall(r'<img\b([^>]*)>', s):
        if 'alt=' not in img: probs.append("img without alt")
    # quiz JSON validity
    for m in re.findall(r'<script[^>]*data-quiz-questions[^>]*>(.*?)</script>', s, re.S):
        import json
        try: json.loads(m)
        except Exception as e: probs.append("bad quiz JSON: %s"%e)
    # unknown classes (sample - only flag clearly-nonexistent ones)
    if probs: issues[base]=sorted(set(probs))
print(f"Checked {len(glob.glob(os.path.join(ROOT,'_authored','*.html')))} authored pages")
if not issues: print("✅ No issues found")
for k,v in issues.items(): print(f"  {k}: {v}")
sys.exit(1 if issues else 0)
