#!/usr/bin/env python3
"""Turn a Wix "video" that is a voice recording over a few still pictures into a
synced audio slideshow: the pictures change at the same moments as the original,
and a thumbnail strip lets people jump to each part.

  python3 tools/wix_slides.py <program> <wix-video-id> <name> "EN title" "FR title" alts.json

  alts.json  [{"en": "...", "fr": "..."}, …] — one alt text per picture, in order
             (run once without it to see how many pictures were found)

Writes <program>/assets/media/<name>.m4a and <name>-<n>.jpg (white borders
trimmed), then swaps the matching `data-video-pending` callout in
_authored/<program>/ (EN + FR). Rebuild and run QA afterwards.
"""
import glob, html, json, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from programs import ROOT, authored_dir, site_dir

SCENES_SWIFT = r'''
import AVFoundation
import AppKit
func px(_ img: CGImage) -> [Double] { let w=32,h=18; var b=[UInt8](repeating:0,count:w*h)
  let c=CGContext(data:&b,width:w,height:h,bitsPerComponent:8,bytesPerRow:w,space:CGColorSpaceCreateDeviceGray(),bitmapInfo:0)!
  c.draw(img,in:CGRect(x:0,y:0,width:w,height:h)); return b.map{Double($0)} }
func dist(_ a:[Double],_ b:[Double]) -> Double { var t=0.0; for i in 0..<a.count { t += abs(a[i]-b[i]) }; return t/Double(a.count) }
// Crop near-white margins (letterboxing baked into the video frame).
func trim(_ img: CGImage) -> CGImage {
  let w=img.width,h=img.height; var buf=[UInt8](repeating:0,count:w*h*4)
  let c=CGContext(data:&buf,width:w,height:h,bitsPerComponent:8,bytesPerRow:w*4,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue)!
  c.draw(img,in:CGRect(x:0,y:0,width:w,height:h))
  func white(_ x:Int,_ y:Int)->Bool { let i=(y*w+x)*4; return buf[i]>238 && buf[i+1]>238 && buf[i+2]>238 }
  func rowBlank(_ y:Int)->Bool { var n=0; for x in stride(from:0,to:w,by:4) where !white(x,y) { n+=1 }; return n < w/200+2 }
  func colBlank(_ x:Int)->Bool { var n=0; for y in stride(from:0,to:h,by:4) where !white(x,y) { n+=1 }; return n < h/200+2 }
  var top=0,bot=h-1,lft=0,rgt=w-1
  while top<bot && rowBlank(top) { top+=1 }; while bot>top && rowBlank(bot) { bot-=1 }
  while lft<rgt && colBlank(lft) { lft+=1 }; while rgt>lft && colBlank(rgt) { rgt-=1 }
  if (rgt-lft) < w/4 || (bot-top) < h/4 { return img }
  // keep a safety margin: on white-background artwork, faint text near the edge can read as blank
  let m=max(w,h)/40; lft=max(0,lft-m); top=max(0,top-m); rgt=min(w-1,rgt+m); bot=min(h-1,bot+m)
  // buffer rows are top-down in memory for this context
  return img.cropping(to: CGRect(x:lft,y:top,width:rgt-lft+1,height:bot-top+1)) ?? img }
let a=AVURLAsset(url:URL(fileURLWithPath:CommandLine.arguments[1])); let out=CommandLine.arguments[2]
let g=AVAssetImageGenerator(asset:a); g.maximumSize=CGSize(width:1280,height:1280)
g.requestedTimeToleranceBefore = .zero; g.requestedTimeToleranceAfter = .zero
let s=DispatchSemaphore(value:0)
Task {
  let d:Double=(try? await a.load(.duration))?.seconds ?? 0
  var prev:[Double]? = nil; var times:[Double]=[]; var t=0.25
  while t < d {
    if let r=try? await g.image(at:CMTime(seconds:t,preferredTimescale:600)) {
      let p=px(r.image)
      if prev==nil || dist(prev!,p) > 12 {
        // grab the picture a second later, once any cross-fade has settled
        let settle=min(t+1.5,d-0.1)
        let img=(try? await g.image(at:CMTime(seconds:settle,preferredTimescale:600)))?.image ?? r.image
        times.append(t)
        try? NSBitmapImageRep(cgImage:trim(img)).representation(using:.jpeg,properties:[.compressionFactor:0.78])!
          .write(to:URL(fileURLWithPath:out+"-\(times.count).jpg"))
      }
      prev=p
    }
    t += 0.5 }
  print(times.map{String(format:"%.1f",$0)}.joined(separator:","))
  s.signal() }
s.wait()
'''

def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f"failed: {' '.join(cmd)}\n{r.stderr[-600:]}")
    return r.stdout

def mmss(sec):
    sec = int(round(sec)); return f"{sec // 60} min {sec % 60:02d}"

def main():
    if len(sys.argv) < 6: sys.exit(__doc__)
    prog, wid, name, t_en, t_fr = sys.argv[1:6]
    alts = json.load(open(sys.argv[6], encoding="utf-8")) if len(sys.argv) > 6 else None
    wid = wid.replace("4e81e2_", "")
    media = os.path.join(site_dir(prog), "assets", "media"); os.makedirs(media, exist_ok=True)
    tmp = tempfile.mkdtemp(); mp4, wav = os.path.join(tmp, "v.mp4"), os.path.join(tmp, "a.wav")
    for q in ("720p", "1080p", "480p"):
        if run("curl", "-s", "-o", mp4, "-w", "%{http_code}", "-H", "Referer: https://www.boxing4health.com/",
               f"https://video.wixstatic.com/video/4e81e2_{wid}/{q}/mp4/file.mp4") == "200": break
    else: sys.exit("could not download the Wix video")
    for old in glob.glob(os.path.join(media, name + "-*.jpg")): os.remove(old)
    sw = os.path.join(tmp, "scenes.swift"); open(sw, "w").write(SCENES_SWIFT)
    times = [float(x) for x in run("swift", sw, mp4, os.path.join(media, name)).strip().split(",")]
    times[0] = 0.0
    print(f"  {len(times)} pictures at {times}")
    if not alts or len(alts) != len(times):
        sys.exit(f"  → write {len(times)} alt texts to a JSON file and pass it as the last argument")
    m4a = os.path.join(media, name + ".m4a")
    run("afconvert", "-f", "WAVE", "-d", "LEI16@22050", "-c", "1", mp4, wav)
    run("afconvert", "-f", "m4af", "-d", "aac", "-b", "64000", wav, m4a)
    dur = float(re.search(r"estimated duration: ([\d.]+)", run("afinfo", m4a)).group(1))
    print(f"  audio: {os.path.relpath(m4a, ROOT)} ({os.path.getsize(m4a)//1024} KB, {mmss(dur)})")

    def block(fr):
        lang = "fr" if fr else "en"
        t = html.escape(t_fr if fr else t_en, quote=True)
        slides = "".join(
            f'<img src="../assets/media/{name}-{i+1}.jpg" alt="{html.escape(alts[i][lang], quote=True)}" data-at="{at:g}"'
            f'{" data-active" if i == 0 else ""} loading="lazy">' for i, at in enumerate(times))
        jump = "Aller à la partie" if fr else "Jump to part"
        thumbs = "".join(
            f'<li><button type="button" data-seek="{at:g}" aria-label="{jump} {i+1} ({int(at)//60}:{int(at)%60:02d})">'
            f'<img src="../assets/media/{name}-{i+1}.jpg" alt="" loading="lazy"><span>{int(at)//60}:{int(at)%60:02d}</span></button></li>'
            for i, at in enumerate(times))
        return (f'<figure class="audio-slides" data-audio-slides><div class="as-stage">{slides}</div>'
                f'<figcaption>{t} (audio, {mmss(dur)})</figcaption>'
                f'<audio controls preload="metadata" src="../assets/media/{name}.m4a"></audio>'
                f'<ol class="as-thumbs">{thumbs}</ol></figure>')
    pat = re.compile(r'<div class="callout callout-info" data-video-pending="4e81e2_' + re.escape(wid) + r'">.*?</div></div>', re.S)
    hits = 0
    for p in sorted(glob.glob(os.path.join(authored_dir(prog), "*.html"))):
        s = open(p, encoding="utf-8").read(); n = len(pat.findall(s))
        if not n: continue
        open(p, "w", encoding="utf-8").write(pat.sub(lambda m: block(p.endswith(".fr.html")), s)); hits += n
        print(f"  {os.path.basename(p)}: {n} replaced")
    if not hits: print("  (no placeholder found — media written only)")

if __name__ == "__main__":
    main()
