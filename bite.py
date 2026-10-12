"""Turn a real customer video ("customer bite") into a branded Reel / YouTube Short.

Intro card with the customer's own line -> their clip (cropped to 9:16, loudness-normalised)
with a name strip, the BizFlow logo and burned-in Marathi subtitles -> CTA card.

Usage: python3 bite.py posts/2026-w43-bites.json
Outputs media/<bite-id>/reel.mp4 and media/<bite-id>/cover.jpg

Spec shape:
{"week": "2026-W43", "bites": [{
  "id": "2026-10-23-bite-hotel-tarang", "date": "2026-10-23T10:00:00",
  "src": "photos/customers/hotel-tarang/bite.mp4", "trim": [3.0, 31.5],
  "name": "<owner's name>", "role": "मालक", "shop": "Hotel Tarang", "town": "संगमनेर", "product": "TableFlow",
  "hook": "“KOT आता [[हरवत नाही]]”",              # a line the customer actually said
  "subs": [{"t": [0.0, 3.4], "text": "आधी KOT हाताने लिहायचो..."}, ...],  # times after trim
  "outro": "तुमच्या hotel मध्येही\n[[TableFlow]]",
  "caption": "...", "youtube_title": "...", "youtube_description": "...", "youtube_tags": [...]
}]}
Subtitles are what the customer said, transcribed, never reworded into claims they didn't make.
"""
import json, sys, pathlib, html, subprocess, shutil
from playwright.sync_api import sync_playwright
from brand import VARS, BG_DARK, logo
from reel import CSS as REEL_CSS, rich, scene_html

ROOT = pathlib.Path(__file__).parent
W, H, FPS = 1080, 1920, 30
INTRO, OUTRO = 2.4, 3.2

OVERLAY_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
""" + VARS + """
html, body { width:1080px; height:1920px; background:transparent; font-family:'Poppins',sans-serif; overflow:hidden; }
.bug { position:absolute; left:64px; top:150px; height:60px; filter:drop-shadow(0 4px 14px rgba(0,0,0,.55)); }
.bug .logo { height:60px; display:block; }
.strip { position:absolute; left:64px; top:990px; max-width:952px; background:rgba(5,7,15,.82); color:#fff;
         border-left:12px solid var(--blue); border-radius:0 28px 28px 0; padding:26px 36px 28px; }
.strip .n { font-size:52px; font-weight:800; line-height:1.2; }
.strip .s { font-size:36px; font-weight:600; line-height:1.35; opacity:.9; margin-top:6px; }
.strip .p { display:inline-block; margin-top:14px; background:var(--blue); border-radius:999px; padding:6px 22px; font-size:30px; font-weight:700; }
.sub { position:absolute; left:70px; right:70px; top:1330px; display:flex; justify-content:center; }
.sub span { background:rgba(5,7,15,.78); color:#fff; border-radius:22px; padding:18px 30px; text-align:center;
            font-size:54px; font-weight:700; line-height:1.35; -webkit-box-decoration-break:clone; box-decoration-break:clone; }
.sub .hl { color:var(--sky); background:none; padding:0; }
"""

INTRO_CSS = """
.who { margin-top:70px; display:flex; flex-wrap:wrap; gap:18px; }
.who span { background:rgba(255,255,255,.12); border-radius:999px; padding:14px 30px; font-size:38px; font-weight:700; }
.who span.p { background:var(--blue); }
.q { font-size:104px; line-height:1.25; font-weight:800; }
"""


def page_html(css, body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def intro_html(b):
    who = f'<span>{html.escape(b["shop"])}</span><span>{html.escape(b["town"])}</span><span class="p">{html.escape(b["product"])}</span>'
    return page_html(REEL_CSS + INTRO_CSS,
        f'<div class="s dark"><div class="tag">BizFlow वापरणारे</div><div class="q">{rich(b["hook"])}</div>'
        f'<div class="who">{who}</div><div class="brand">{logo("dark")}</div></div>')


def strip_html(b):
    who = " · ".join(x for x in (b.get("role"), b["shop"], b["town"]) if x)
    return page_html(OVERLAY_CSS,
        f'<div class="strip"><div class="n">{html.escape(b["name"])}</div><div class="s">{html.escape(who)}</div>'
        f'<div class="p">{html.escape(b["product"])}</div></div>')


def has_audio(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout
    return bool(out.strip())


def still_clip(png, dur, mp4):
    """A card as video: slow zoom, silent stereo track, same format as the main clip."""
    n = int(dur * FPS)
    vf = f"scale={W*2}:{H*2},zoompan=z='min(1+0.0006*on,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", vf, "-t", f"{dur}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", str(mp4)], check=True)


def build(b, page):
    out = ROOT / "media" / b["id"]; out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_frames"; tmp.mkdir(exist_ok=True)
    src = ROOT / b["src"]
    a, z = b.get("trim", [0, None])

    def shot(markup, name, transparent=False):
        page.set_content(markup); page.wait_for_timeout(250)
        p = tmp / name; page.screenshot(path=str(p), omit_background=transparent); return p

    intro = shot(intro_html(b), "intro.png")
    outro = shot(scene_html({"kind": "cta", "theme": "accent", "text": b.get("outro", f"तुमच्या व्यवसायातही\n[[{b['product']}]]")}), "outro.png")
    bug = shot(page_html(OVERLAY_CSS, f'<div class="bug">{logo("dark")}</div>'), "bug.png", True)
    strip = shot(strip_html(b), "strip.png", True)
    subs = [shot(page_html(OVERLAY_CSS, f'<div class="sub"><span>{rich(s["text"])}</span></div>'), f"sub{i:02d}.png", True)
            for i, s in enumerate(b.get("subs", []))]

    # Main clip: trim, fill 9:16, overlays, loudness-normalised audio (silent track if none).
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a}"] + (["-to", f"{z}"] if z else []) + ["-i", str(src)]
    for p in [bug, strip, *subs]: cmd += ["-loop", "1", "-i", str(p)]
    audio = has_audio(src)
    if not audio: cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    fc = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[v0]",
          "[v0][1:v]overlay=0:0:shortest=1[v1]",
          "[v1][2:v]overlay=0:0:shortest=1:enable='between(t,0.4,5.4)'[v2]"]
    last = "v2"
    for i, s in enumerate(b.get("subs", [])):
        t0, t1 = s["t"]; lab = f"s{i}"
        fc.append(f"[{last}][{3+i}:v]overlay=0:0:shortest=1:enable='between(t,{t0},{t1})'[{lab}]"); last = lab
    fc.append(f"[{last}]format=yuv420p[vout]")
    a_in = "0:a" if audio else f"{3+len(subs)}:a"
    fc.append(f"[{a_in}]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo[aout]")
    main = tmp / "main.mp4"
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-shortest", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k", str(main)]
    subprocess.run(cmd, check=True)

    i_mp4, o_mp4 = tmp / "intro.mp4", tmp / "outro.mp4"
    still_clip(intro, INTRO, i_mp4); still_clip(outro, OUTRO, o_mp4)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(i_mp4), "-i", str(main), "-i", str(o_mp4),
                    "-filter_complex", "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out / "reel.mp4")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(intro), "-q:v", "3", str(out / "cover.jpg")], check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out / "reel.mp4")],
                         capture_output=True, text=True).stdout.strip()
    shutil.rmtree(tmp)
    print(b["id"], f"{float(dur):.1f}s")


def main(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    with sync_playwright() as pw:
        br = pw.chromium.launch(); page = br.new_page(viewport={"width": W, "height": H})
        for b in spec["bites"]: build(b, page)
        br.close()


if __name__ == "__main__":
    main(sys.argv[1])
