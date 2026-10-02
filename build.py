"""Render BizFlow carousel slides (1080x1350) from a JSON spec using Playwright.

Usage: python3 build.py posts/2026-w41.json
Outputs JPGs to media/<post-id>/NN.jpg
"""
import json, sys, pathlib, html, shutil, subprocess
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent

CSS = """
@font-face { font-family: 'Deva'; src: local('FreeSans'); unicode-range: U+0900-097F, U+A8E0-A8FF; }
* { margin:0; padding:0; box-sizing:border-box; }
:root {
  --ink:#14183D; --navy:#1F2A6B; --saffron:#FF8A1F; --cream:#FFF6EA; --mint:#1FB57A; --muted:#5B6185;
}
body { width:1080px; height:1350px; font-family:'Deva','Poppins','Inter',sans-serif; overflow:hidden; }
.slide { width:1080px; height:1350px; position:relative; padding:96px 88px; display:flex; flex-direction:column; }
.light { background:var(--cream); color:var(--ink); }
.dark { background:var(--navy); color:#fff; }
.accent { background:var(--saffron); color:var(--ink); }
.brand { position:absolute; left:88px; bottom:72px; display:flex; align-items:center; gap:14px; font-weight:700; font-size:30px; letter-spacing:.5px; }
.brand .dot { width:34px; height:34px; border-radius:10px; background:var(--saffron); display:grid; place-items:center; color:var(--navy); font-size:22px; font-weight:800; }
.dark .brand .dot, .accent .brand .dot { background:#fff; }
.page { position:absolute; right:88px; bottom:76px; font-size:26px; font-weight:600; opacity:.6; }
.swipe { position:absolute; right:88px; bottom:72px; font-size:28px; font-weight:700; color:var(--saffron); }
.kicker { font-size:30px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--saffron); margin-bottom:36px; }
.accent .kicker { color:var(--navy); }
h1 { font-size:104px; line-height:1.12; font-weight:800; letter-spacing:-1px; }
h2 { font-size:88px; line-height:1.15; font-weight:800; margin-bottom:40px; }
p.body { font-size:46px; line-height:1.45; font-weight:500; opacity:.88; }
.hl { color:var(--saffron); }
.accent .hl { color:#fff; }
.bignum { font-size:260px; font-weight:800; line-height:.9; color:var(--saffron); margin-bottom:24px; }
.wrap { margin:auto 0; padding-bottom:60px; }
.wrap > div[style*='margin-top:auto'] { margin:0 !important; }
.list { list-style:none; margin-top:20px; }
.list li { font-size:50px; font-weight:600; line-height:1.3; padding:30px 0 30px 92px; position:relative; border-bottom:2px solid rgba(20,24,61,.12); }
.dark .list li { border-color:rgba(255,255,255,.15); }
.list li .n { position:absolute; left:0; top:24px; width:64px; height:64px; border-radius:50%; background:var(--saffron); color:var(--navy); font-size:34px; font-weight:800; display:grid; place-items:center; }
.chip { display:inline-block; background:var(--navy); color:#fff; border-radius:999px; padding:18px 36px; font-size:40px; font-weight:700; margin:0 14px 18px 0; }
.dark .chip { background:#fff; color:var(--navy); }
.cta-box { margin-top:56px; background:#fff; color:var(--ink); border-radius:36px; padding:52px 56px; }
.cta-box .label { font-size:32px; font-weight:600; color:var(--muted); }
.cta-box .phone { font-size:88px; font-weight:800; color:var(--navy); letter-spacing:1px; margin-top:6px; }
.cta-box .sub { font-size:34px; font-weight:600; margin-top:14px; color:var(--mint); }
.deco { position:absolute; right:-120px; top:-120px; width:520px; height:520px; border-radius:50%; border:60px solid rgba(255,138,31,.18); }
.dark .deco { border-color:rgba(255,255,255,.08); }
.chat { margin-top:30px; display:flex; flex-direction:column; gap:26px; }
.bubble { align-self:flex-start; max-width:860px; background:#fff; color:var(--ink); border-radius:8px 36px 36px 36px; padding:34px 42px; font-size:42px; line-height:1.4; font-weight:500; box-shadow:0 10px 30px rgba(0,0,0,.15); }
.bubble b { color:var(--mint); }
.bubble .t { display:block; font-size:24px; opacity:.5; margin-top:10px; text-align:right; }
.price { font-size:40px; font-weight:700; margin-top:40px; }
.price .hl { font-size:64px; }
"""

def esc(s):
    return html.escape(s, quote=False).replace("**", "")

def rich(s):
    # [[text]] -> highlighted span ; keep everything else escaped
    out, parts = [], s.split("[[")
    out.append(html.escape(parts[0]))
    for p in parts[1:]:
        hl, _, rest = p.partition("]]")
        out.append(f'<span class="hl">{html.escape(hl)}</span>{html.escape(rest)}')
    return "".join(out).replace("\n", "<br>")

TALL = """
body, .slide { height:1920px; }
.slide { padding:240px 88px 320px; }
.brand { bottom:190px; }
.page, .swipe { display:none; }
"""

def render_slide(s, idx, total, tall=False):
    theme = s.get("theme", "light")
    kind = s["kind"]
    inner = ""
    if kind == "cover":
        inner = f'<div class="deco"></div><div style="margin-top:auto;margin-bottom:auto">' \
                f'<div class="kicker">{rich(s.get("kicker",""))}</div><h1>{rich(s["title"])}</h1>' \
                f'<p class="body" style="margin-top:44px">{rich(s.get("body",""))}</p></div>'
    elif kind == "point":
        inner = f'<div style="margin-top:40px"><div class="bignum">{html.escape(s["num"])}</div>' \
                f'<h2>{rich(s["title"])}</h2><p class="body">{rich(s["body"])}</p></div>'
    elif kind == "list":
        lis = "".join(f'<li><span class="n">{i+1}</span>{rich(t)}</li>' for i, t in enumerate(s["items"]))
        inner = f'<div class="kicker">{rich(s.get("kicker",""))}</div><h2>{rich(s["title"])}</h2><ul class="list">{lis}</ul>'
    elif kind == "chips":
        chips = "".join(f'<span class="chip">{html.escape(c)}</span>' for c in s["chips"])
        inner = f'<div class="deco"></div><div class="kicker">{rich(s.get("kicker",""))}</div>' \
                f'<h2>{rich(s["title"])}</h2><p class="body" style="margin-bottom:48px">{rich(s.get("body",""))}</p><div>{chips}</div>' \
                + (f'<div class="price">{rich(s["price"])}</div>' if s.get("price") else "")
    elif kind == "chat":
        bubbles = "".join(f'<div class="bubble">{rich(b["text"])}<span class="t">{html.escape(b.get("time",""))} ✓✓</span></div>' for b in s["bubbles"])
        inner = f'<div class="kicker">{rich(s.get("kicker",""))}</div><h2>{rich(s["title"])}</h2><div class="chat">{bubbles}</div>'
    elif kind == "cta":
        inner = f'<div class="deco"></div><div style="margin-top:40px"><div class="kicker">{rich(s.get("kicker",""))}</div>' \
                f'<h2>{rich(s["title"])}</h2><p class="body">{rich(s.get("body",""))}</p>' \
                f'<div class="cta-box"><div class="label">{rich(s.get("label","Free demo बुक करा"))}</div>' \
                f'<div class="phone">📞 {html.escape(s.get("phone","8888567870"))}</div>' \
                f'<div class="sub">{rich(s.get("sub","bizflowindia.cloud"))}</div></div></div>'
    footer = '<div class="brand"><span class="dot">B</span>BizFlow India</div>'
    if idx == 0 and total > 1:
        footer += '<div class="swipe">Swipe →</div>'
    elif total > 1:
        footer += f'<div class="page">{idx+1}/{total}</div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{TALL if tall else ""}</style></head>' \
           f'<body><div class="slide {theme}"><div class="wrap">{inner}</div>{footer}</div></body></html>'

def main(spec_path):
    from reel import stitch
    spec = json.loads(pathlib.Path(spec_path).read_text())
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        for post in spec["posts"]:
            out = ROOT / "media" / post["id"]
            out.mkdir(parents=True, exist_ok=True)
            n = len(post["slides"])
            for i, s in enumerate(post["slides"]):
                page.set_content(render_slide(s, i, n))
                page.wait_for_timeout(150)
                page.screenshot(path=str(out / f"{i+1:02d}.jpg"), type="jpeg", quality=92)
            print(post["id"], n, "slides")
            if n < 2: continue
            # 9:16 video version (media/<id>/short.mp4 + cover.jpg) for YouTube Shorts
            tmp = out / "_tall"; tmp.mkdir(exist_ok=True)
            page.set_viewport_size({"width": 1080, "height": 1920})
            pngs, durs = [], []
            for i, s in enumerate(post["slides"]):
                page.set_content(render_slide(s, i, n, tall=True)); page.wait_for_timeout(150)
                f = tmp / f"{i:02d}.png"; page.screenshot(path=str(f)); pngs.append(f)
                durs.append({"cover": 2.6, "list": 4.2, "chat": 4.2, "cta": 3.2}.get(s["kind"], 3.0))
            page.set_viewport_size({"width": 1080, "height": 1350})
            stitch(pngs, durs, out / "short.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pngs[0]), "-q:v", "3", str(out / "cover.jpg")], check=True)
            shutil.rmtree(tmp)
            print(post["id"], "short.mp4", f"{sum(durs) - 0.4 * (n - 1):.1f}s")
        b.close()

if __name__ == "__main__":
    main(sys.argv[1])
