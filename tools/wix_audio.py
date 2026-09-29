#!/usr/bin/env python3
"""Turn a Wix "video" that is really a voice recording over a still picture into a
self-hosted audio player (with that picture), replacing its "coming soon" box.

  python3 tools/wix_audio.py <program> <wix-video-id> <name> "EN title" "FR title" "EN alt" "FR alt"

  <wix-video-id>  the id in the placeholder, e.g. 4e81e2_c3a54ca1…
  <name>          file stem for <program>/assets/media/<name>.m4a and .jpg

Downloads the Wix MP4 (needs the site Referer), extracts mono 64 kbps AAC audio
and one still frame (macOS afconvert + AVFoundation via swift), then swaps every
matching `data-video-pending` callout in _authored/<program>/ (EN and FR files;
in a FR file an English-only recording is labelled « en anglais »).
Then rebuild and run QA as usual.
"""
import glob, html, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programs import ROOT, authored_dir, site_dir

FRAME_SWIFT = r'''
import AVFoundation
import AppKit
let a = AVURLAsset(url: URL(fileURLWithPath: CommandLine.arguments[1]))
let g = AVAssetImageGenerator(asset: a); g.maximumSize = CGSize(width: 960, height: 960); g.appliesPreferredTrackTransform = true
let s = DispatchSemaphore(value: 0)
Task {
  let d = (try? await a.load(.duration))?.seconds ?? 2
  if let (i, _) = try? await g.image(at: CMTime(seconds: d * 0.5, preferredTimescale: 600)) {
    try? NSBitmapImageRep(cgImage: i).representation(using: .jpeg, properties: [.compressionFactor: 0.72])!
      .write(to: URL(fileURLWithPath: CommandLine.arguments[2]))
  }
  s.signal()
}
s.wait()
'''

def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f"failed: {' '.join(cmd)}\n{r.stderr[-400:]}")
    return r.stdout

def mmss(sec):
    sec = int(round(sec)); return f"{sec // 60} min {sec % 60:02d}"

def main():
    if len(sys.argv) < 8: sys.exit(__doc__)
    prog, wid, name, t_en, t_fr, alt_en, alt_fr = sys.argv[1:8]
    wid = wid.replace("4e81e2_", "")
    media = os.path.join(site_dir(prog), "assets", "media"); os.makedirs(media, exist_ok=True)
    tmp = tempfile.mkdtemp()
    mp4, wav = os.path.join(tmp, "v.mp4"), os.path.join(tmp, "a.wav")
    for q in ("480p", "360p", "720p", "1080p"):
        code = run("curl", "-s", "-o", mp4, "-w", "%{http_code}", "-H", "Referer: https://www.boxing4health.com/",
                   f"https://video.wixstatic.com/video/4e81e2_{wid}/{q}/mp4/file.mp4")
        if code == "200": break
    else: sys.exit("could not download the Wix video")
    m4a, jpg = os.path.join(media, name + ".m4a"), os.path.join(media, name + ".jpg")
    run("afconvert", "-f", "WAVE", "-d", "LEI16@22050", "-c", "1", mp4, wav)
    run("afconvert", "-f", "m4af", "-d", "aac", "-b", "64000", wav, m4a)
    sw = os.path.join(tmp, "frame.swift"); open(sw, "w").write(FRAME_SWIFT)
    run("swift", sw, mp4, jpg)
    dur = float(re.search(r"estimated duration: ([\d.]+)", run("afinfo", m4a)).group(1))
    print(f"  media: {os.path.relpath(m4a, ROOT)} ({os.path.getsize(m4a)//1024} KB, {mmss(dur)}), {os.path.relpath(jpg, ROOT)}")

    def card(fr):
        t = html.escape(t_fr if fr else t_en, quote=True); alt = html.escape(alt_fr if fr else alt_en, quote=True)
        cap = f"{t} (audio, {mmss(dur)})" if not fr else f"{t} (audio, {mmss(dur)})"
        return (f'<figure class="audio-card"><img src="../assets/media/{name}.jpg" alt="{alt}" loading="lazy">'
                f'<figcaption>{cap}</figcaption>'
                f'<audio controls preload="none" src="../assets/media/{name}.m4a"></audio></figure>')
    pat = re.compile(r'<div class="callout callout-info" data-video-pending="4e81e2_' + re.escape(wid) + r'">.*?</div></div>', re.S)
    hits = 0
    for p in sorted(glob.glob(os.path.join(authored_dir(prog), "*.html"))):
        s = open(p, encoding="utf-8").read()
        n = len(pat.findall(s))
        if not n: continue
        s = pat.sub(lambda m: card(p.endswith(".fr.html")), s)
        open(p, "w", encoding="utf-8").write(s); hits += n
        print(f"  {os.path.basename(p)}: {n} replaced")
    if not hits: print("  (no placeholder found — media files written only)")

if __name__ == "__main__":
    main()
