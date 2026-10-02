"""Render BizFlow Reels (1080x1920 mp4) from a JSON spec.

Each scene is rendered to a PNG with Playwright, then ffmpeg adds a slow zoom
per scene and crossfades between them, plus a silent audio track.

Usage: python3 reel.py posts/2026-w41-reels.json
Outputs media/<reel-id>/reel.mp4 and media/<reel-id>/cover.jpg
"""
import json, sys, pathlib, html, subprocess, shutil
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
W, H, FPS, XF = 1080, 1920, 30, 0.4

CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
:root { --ink:#14183D; --navy:#1F2A6B; --saffron:#FF8A1F; --cream:#FFF6EA; --mint:#1FB57A; }
body { width:1080px; height:1920px; font-family:'Poppins','Inter',sans-serif; overflow:hidden; }
.s { width:1080px; height:1920px; padding:260px 90px 300px; display:flex; flex-direction:column; justify-content:center; position:relative; }
.light { background:var(--cream); color:var(--ink); }
.dark { background:var(--navy); color:#fff; }
.accent { background:var(--saffron); color:var(--ink); }
.tag { font-size:40px; font-weight:700; letter-spacing:2px; color:var(--saffron); margin-bottom:40px; text-transform:uppercase; }
.accent .tag { color:var(--navy); }
.big { font-size:118px; line-height:1.15; font-weight:800; letter-spacing:-1px; }
.mid { font-size:84px; line-height:1.22; font-weight:800; }
.sub { font-size:54px; line-height:1.4; font-weight:500; margin-top:50px; opacity:.9; }
.hl { color:var(--saffron); }
.accent .hl { color:#fff; }
.emoji { font-size:200px; margin-bottom:30px; line-height:1; }
.bubble { background:#fff; color:var(--ink); border-radius:10px 48px 48px 48px; padding:44px 52px; font-size:58px; line-height:1.35; font-weight:600; box-shadow:0 16px 40px rgba(0,0,0,.18); margin-top:36px; max-width:900px; }
.bubble.me { align-self:flex-end; background:#DCF8C6; border-radius:48px 10px 48px 48px; }
.who { font-size:38px; font-weight:700; opacity:.6; margin-top:40px; }
.phone { background:#fff; color:var(--navy); border-radius:44px; padding:56px; margin-top:60px; font-size:96px; font-weight:800; text-align:center; }
.phone small { display:block; font-size:44px; color:var(--mint); font-weight:700; margin-top:10px; }
.brand { position:absolute; left:90px; bottom:150px; display:flex; align-items:center; gap:18px; font-weight:700; font-size:40px; }
.brand .dot { width:48px; height:48px; border-radius:14px; background:var(--saffron); display:grid; place-items:center; color:var(--navy); font-size:30px; font-weight:800; }
.dark .brand .dot, .accent .brand .dot { background:#fff; }
"""

def rich(s):
    out, parts = [], s.split("[[")
    out.append(html.escape(parts[0]))
    for p in parts[1:]:
        hl, _, rest = p.partition("]]")
        out.append(f'<span class="hl">{html.escape(hl)}</span>{html.escape(rest)}')
    return "".join(out).replace("\n", "<br>")

def scene_html(sc):
    k, t = sc["kind"], sc.get("theme", "dark")
    inner = ""
    if sc.get("tag"): inner += f'<div class="tag">{rich(sc["tag"])}</div>'
    if sc.get("emoji"): inner += f'<div class="emoji">{sc["emoji"]}</div>'
    if k == "big": inner += f'<div class="big">{rich(sc["text"])}</div>'
    if k == "mid": inner += f'<div class="mid">{rich(sc["text"])}</div>'
    if sc.get("sub"): inner += f'<div class="sub">{rich(sc["sub"])}</div>'
    if k == "chat":
        for b in sc["bubbles"]:
            if b.get("who"): inner += f'<div class="who">{html.escape(b["who"])}</div>'
            inner += f'<div class="bubble {"me" if b.get("me") else ""}">{rich(b["text"])}</div>'
    if k == "cta":
        inner += f'<div class="mid">{rich(sc["text"])}</div>' \
                 f'<div class="phone">📞 {html.escape(sc.get("phone","8888567870"))}<small>Free demo · bizflowindia.cloud</small></div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>' \
           f'<div class="s {t}">{inner}<div class="brand"><span class="dot">B</span>BizFlow India</div></div></body></html>'

def stitch(pngs, durs, mp4):
    """Join 1080x1920 stills into an mp4: slow zoom per still, crossfades, silent audio track."""
    tmp = pathlib.Path(pngs[0]).parent
    clips = []
    for i, (p, d) in enumerate(zip(pngs, durs)):
        c = tmp / f"clip{i:02d}.mp4"; n = int(d * FPS)
        vf = f"scale={W*2}:{H*2},zoompan=z='min(1+0.0006*on,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(p), "-vf", vf, "-t", f"{d}", "-r", str(FPS),
                        "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(c)], check=True)
        clips.append(c)
    inputs, fc, last, off = [], [], "0:v", 0.0
    for c in clips: inputs += ["-i", str(c)]
    for i in range(1, len(clips)):
        off += durs[i-1] - XF
        lab = f"v{i}"
        fc.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.2f}[{lab}]")
        last = lab
    total = sum(durs) - XF * (len(clips) - 1)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
    cmd += (["-filter_complex", ";".join(fc), "-map", f"[{last}]"] if fc else ["-map", "0:v"])
    cmd += ["-map", f"{len(clips)}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(mp4)]
    subprocess.run(cmd, check=True)

def build(reel, page):
    out = ROOT / "media" / reel["id"]; out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_frames"; tmp.mkdir(exist_ok=True)
    pngs, durs = [], []
    for i, sc in enumerate(reel["scenes"]):
        page.set_content(scene_html(sc)); page.wait_for_timeout(150)
        p = tmp / f"{i:02d}.png"; page.screenshot(path=str(p)); pngs.append(p); durs.append(float(sc.get("dur", 2.6)))
    shutil.copy(pngs[0], out / "cover.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pngs[0]), "-q:v", "3", str(out / "cover.jpg")], check=True)
    stitch(pngs, durs, out / "reel.mp4")
    shutil.rmtree(tmp); (out / "cover.png").unlink()
    print(reel["id"], f"{sum(durs) - XF * (len(durs) - 1):.1f}s")

def main(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    with sync_playwright() as pw:
        b = pw.chromium.launch(); page = b.new_page(viewport={"width": W, "height": H})
        for reel in spec["reels"]: build(reel, page)
        b.close()

if __name__ == "__main__":
    main(sys.argv[1])
