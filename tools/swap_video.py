#!/usr/bin/env python3
"""Replace a "Video coming soon" placeholder with the real YouTube video.

  python3 tools/swap_video.py <program> <pending-id> <youtube-url-or-id> "EN title" ["FR title"]

Finds every `data-video-pending="<pending-id>"` callout in _authored/<program>/
(EN and FR files) and swaps it for the standard click-to-load video block.
Then rebuild and run QA as usual.
"""
import glob, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programs import authored_dir

def yt_id(s):
    m = re.search(r'(?:youtu\.be/|shorts/|v=|embed/)([\w-]{11})', s)
    return m.group(1) if m else (s if re.fullmatch(r'[\w-]{11}', s) else None)

def block(vid, title, short=False):
    t = html.escape(title, quote=True)
    shape = ' data-shape="short"' if short else ""
    return (f'<div class="video" data-yt="{vid}" data-title="{t}"{shape}>'
            f'<img class="video-poster" src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="">'
            f'<div class="video-play"><span data-icon="circle-play"></span></div>'
            f'<div class="video-label">{t}</div></div>')

def main():
    if len(sys.argv) < 5: sys.exit(__doc__)
    prog, pending, url, en = sys.argv[1:5]
    fr = sys.argv[5] if len(sys.argv) > 5 else en
    vid = yt_id(url)
    if not vid: sys.exit(f"not a YouTube URL/id: {url}")
    pat = re.compile(r'<div class="callout callout-info" data-video-pending="' + re.escape(pending) + r'">.*?</div></div>', re.S)
    hits = 0
    for p in sorted(glob.glob(os.path.join(authored_dir(prog), "*.html"))):
        s = open(p, encoding="utf-8").read()
        n = len(pat.findall(s))
        if not n: continue
        s = pat.sub(lambda m: block(vid, fr if p.endswith(".fr.html") else en, "shorts/" in url), s)
        open(p, "w", encoding="utf-8").write(s); hits += n
        print(f"  {os.path.basename(p)}: {n} replaced → {vid}")
    if not hits: sys.exit(f"no placeholder with id {pending} in {prog}")

if __name__ == "__main__":
    main()
