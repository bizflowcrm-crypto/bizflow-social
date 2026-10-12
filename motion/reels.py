"""Animated motion-graphics Reels from the same spec reel.py reads.

Instead of still cards with a zoom, every scene is animated from time t: words spring in
one by one, highlighted words get a marker sweep, emoji pop and bob, chat bubbles arrive
after a typing indicator, the CTA card springs up with a pulse, and scenes change with
zoom / slide / whip transitions. A soundtrack (beat, bass, pad) and sound effects timed to
the animation are synthesized here, so every Reel is original and copyright-free.

Usage: python3 motion/reels.py posts/2026-w41-reels.json [reel-id ...]
Outputs media/<reel-id>/reel.mp4 and cover.jpg (same paths reel.py writes).
"""
import json, sys, pathlib, re, html, subprocess, shutil
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from brand import VARS, BG_DARK, BG_ACCENT, logo

TR = 0.4          # scene transition overlap (s)
SR = 44100


# ---------- timeline (shared by the animation and the sound) ----------

def tokens(text):
    """'a [[b c]]\nd' -> lines of words [{'w':..,'hl':bool}]. Punctuation that touches a word
    (no space between) stays with that word, so quotes and full stops never float alone."""
    import unicodedata
    is_punct = lambda w: all(unicodedata.category(c).startswith("P") for c in w)
    lines, hl = [], False
    for raw in text.split("\n"):
        words, gap = [], True
        for part in re.split(r"(\[\[|\]\])", raw):
            if part == "[[": hl = True; continue
            if part == "]]": hl = False; continue
            chunks = part.split(" ")
            for k, w in enumerate(chunks):
                if k > 0: gap = True
                if not w: continue
                if words and not gap and is_punct(w):
                    words[-1]["w"] += w
                elif words and not gap and is_punct(words[-1]["w"]):
                    words[-1]["w"] += w; words[-1]["hl"] = words[-1]["hl"] or hl
                else:
                    words.append({"w": w, "hl": hl})
                gap = False
            if part.endswith(" "): gap = True
        lines.append(words)
    return lines


def timeline(reel):
    scenes, start = [], 0.0
    for i, sc in enumerate(reel["scenes"]):
        k = sc["kind"]
        dur = float(sc.get("dur", 2.6))
        if k == "chat": dur = max(dur, 0.6 + 1.15 * len(sc["bubbles"]) + 0.9)
        s = {"i": i, "kind": k, "theme": sc.get("theme", "dark"), "start": start, "end": start + dur,
             "trans": ["zoom", "slide", "whip"][i % 3], "ev": []}
        t = 0.08
        if sc.get("emoji"): s["emoji"] = sc["emoji"]; s["emojiT"] = t; s["ev"].append(("boing", t)); t += 0.22
        if sc.get("tag"): s["tag"] = sc["tag"]; s["tagT"] = t; s["ev"].append(("tick", t)); t += 0.22
        if k == "chat":
            s["bubbles"] = []
            for j, b in enumerate(sc["bubbles"]):
                ty = t + 0.15 + j * 1.15
                s["bubbles"].append({"who": b.get("who", ""), "me": bool(b.get("me")), "lines": tokens(b["text"]),
                                     "typeT": ty, "showT": ty + 0.5})
                s["ev"] += [("typing", ty), ("bubble", ty + 0.5)]
        else:
            lines = tokens(sc["text"])
            n = sum(len(l) for l in lines)
            stag = min(0.075, 0.75 / max(n, 1))
            idx, hl_words = 0, []
            for li, line in enumerate(lines):
                for w in line:
                    w["d"] = round(t + idx * stag, 3); idx += 1
                    if w["hl"]: hl_words.append(w)
                if line: s["ev"].append(("pop", line[0]["d"]))
            t_words = t + idx * stag + 0.35
            for j, w in enumerate(hl_words):
                w["hd"] = round(t_words + j * 0.07, 3)
            if hl_words:
                s["hlT"] = t_words + 0.07 * len(hl_words) + 0.2
                s["ev"].append(("ding", t_words + 0.05))
            s["lines"] = lines
            t = t_words + (0.07 * len(hl_words) + 0.25 if hl_words else 0)
            if sc.get("sub"): s["sub"] = tokens(sc["sub"]); s["subT"] = t; s["ev"].append(("soft", t)); t += 0.3
            if k == "cta":
                s["phone"] = sc.get("phone", "8888567870"); s["cardT"] = t; s["ev"] += [("whoosh_up", t), ("bell", t + 0.3)]
        s["ev"] = [(name, round(s["start"] + at, 3)) for name, at in s["ev"]]
        if i > 0: s["ev"].append(("whoosh", round(start - 0.06, 3)))
        scenes.append(s)
        start += dur - TR
    total = scenes[-1]["end"]
    return scenes, total


# ---------- page ----------

CSS = VARS + """
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; height:1920px; overflow:hidden; background:#05070F; font-family:'Poppins',sans-serif; -webkit-font-smoothing:antialiased; }
.scene { position:absolute; inset:0; overflow:hidden; will-change:transform, opacity, filter; }
.bg { position:absolute; inset:-60px; }
.dark .bg { background:""" + BG_DARK + """; }
.light .bg { background:var(--paper); }
.accent .bg { background:""" + BG_ACCENT + """; }
.orb { position:absolute; width:900px; height:900px; border-radius:50%; filter:blur(40px); }
.dark .orb { background:radial-gradient(circle, rgba(10,108,240,.45), rgba(10,108,240,0) 65%); }
.accent .orb { background:radial-gradient(circle, rgba(255,255,255,.28), rgba(255,255,255,0) 65%); }
.light .orb { background:radial-gradient(circle, rgba(10,108,240,.16), rgba(10,108,240,0) 65%); }
.grid { position:absolute; inset:-100px; opacity:.5;
  background-image:radial-gradient(rgba(10,18,48,.13) 3px, transparent 3.5px); background-size:56px 56px; }
.dot { position:absolute; border-radius:50%; background:#fff; }
.light .dot { background:var(--blue); }
.cam { position:absolute; inset:0; padding:250px 90px 330px; display:flex; flex-direction:column; justify-content:center; }
.dark, .accent { color:#fff; } .light { color:var(--ink); }
.tag { align-self:flex-start; font-size:40px; font-weight:700; letter-spacing:1px; padding:14px 30px; border-radius:999px; margin-bottom:46px; }
.dark .tag { background:rgba(61,149,255,.18); color:var(--sky); }
.light .tag { background:rgba(10,108,240,.12); color:var(--blue); }
.accent .tag { background:rgba(255,255,255,.18); color:#fff; }
.emoji { font-size:210px; line-height:1; margin-bottom:34px; align-self:flex-start; transform-origin:50% 80%; }
.txt { font-weight:800; letter-spacing:-1px; }
.big .txt { font-size:118px; line-height:1.3; }
.mid .txt, .cta .txt { font-size:86px; line-height:1.32; }
.ln { display:block; }
.w { display:inline-block; position:relative; margin-right:.26em; transform-origin:50% 90%; }
.w .bar { position:absolute; left:-.1em; right:-.1em; border-radius:.12em; transform-origin:left center; z-index:0; }
.w .tx { position:relative; z-index:1; }
.dark .w.hl .tx { color:var(--sky); } .light .w.hl .tx { color:var(--blue); }
.dark .w .bar { bottom:.1em; height:.3em; background:rgba(61,149,255,.35); }
.light .w .bar { bottom:.1em; height:.3em; background:rgba(10,108,240,.2); }
.accent .w .bar { top:.08em; bottom:.04em; background:#fff; }
.sub { font-size:54px; line-height:1.42; font-weight:600; margin-top:48px; opacity:.92; }
.sub .w { margin-right:.22em; } .sub .hl .tx { color:inherit; font-weight:800; }
.who { font-size:36px; font-weight:700; opacity:.65; margin:40px 0 14px; }
.who.me { text-align:right; }
.bubble { display:inline-block; max-width:880px; background:#fff; color:var(--ink); border-radius:10px 48px 48px 48px; padding:40px 50px;
  font-size:56px; line-height:1.38; font-weight:600; box-shadow:0 18px 44px rgba(0,0,0,.22); transform-origin:left top; }
.bubble .w { margin-right:.24em; } .bubble .hl .tx { color:var(--blue); font-weight:800; }
.brow.me { text-align:right; } .brow.me .bubble { background:#DCF8C6; border-radius:48px 10px 48px 48px; transform-origin:right top; text-align:left; }
.typing { display:inline-flex; gap:14px; background:#fff; border-radius:10px 40px 40px 40px; padding:32px 40px; box-shadow:0 12px 30px rgba(0,0,0,.18); }
.brow.me .typing { background:#DCF8C6; border-radius:40px 10px 40px 40px; }
.typing i { width:22px; height:22px; border-radius:50%; background:#8C93B0; display:block; }
.card { margin-top:64px; background:#fff; color:var(--deep); border-radius:46px; padding:54px 50px; text-align:center; position:relative; }
.card .ph { font-size:98px; font-weight:800; letter-spacing:1px; }
.card small { display:block; font-size:42px; color:var(--blue); font-weight:700; margin-top:10px; }
.ring { position:absolute; inset:0; border-radius:46px; border:6px solid #fff; pointer-events:none; }
.light .ring { border-color:var(--blue); } .light .card { background:var(--ink); color:#fff; } .light .card small { color:var(--sky); }
.brand { position:absolute; left:90px; bottom:150px; } .brand .logo { height:72px; display:block; }
"""

JS = r"""
const D = window.DATA, TR = D.TR; window.DUR = D.total;
const clamp = (x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const eo = x=>1-Math.pow(1-clamp(x),3);
const eio = x=>{x=clamp(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
const back = x=>{x=clamp(x);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const spring = x=>{x=Math.max(0,x);return 1-Math.exp(-6*x)*Math.cos(11*x)};
function rnd(i){const s=Math.sin(i*127.1+311.7)*43758.5453;return s-Math.floor(s);}
const stage=document.getElementById('stage');
const els=[];
function wordHTML(w){return `<span class="w${w.hl?' hl':''}">${w.hl?'<span class="bar"></span>':''}<span class="tx">${w.w}</span></span>`;}
function linesHTML(lines,cls){return `<div class="${cls}">`+lines.map(l=>`<span class="ln">${l.map(wordHTML).join('')}</span>`).join('')+'</div>';}
D.scenes.forEach((s,si)=>{
  const el=document.createElement('div'); el.className=`scene ${s.theme} ${s.kind}`;
  let h='<div class="bg"><div class="grid"></div><div class="orb o1"></div><div class="orb o2"></div>';
  for(let k=0;k<16;k++) h+=`<div class="dot" data-k="${k}"></div>`;
  h+='</div><div class="cam">';
  if(s.emoji) h+=`<div class="emoji">${s.emoji}</div>`;
  if(s.tag) h+=`<div class="tag">${s.tag}</div>`;
  if(s.lines) h+=linesHTML(s.lines,'txt');
  if(s.sub) h+=linesHTML(s.sub,'sub');
  if(s.bubbles) s.bubbles.forEach(b=>{ h+=`<div class="who${b.me?' me':''}">${b.who}</div><div class="brow${b.me?' me':''}"><div class="typing"><i></i><i></i><i></i></div><div class="bubble">`+
      b.lines.map(l=>l.map(wordHTML).join('')).join('<br>')+'</div></div>'; });
  if(s.phone) h+=`<div class="card"><div class="ring"></div><div class="ph">📞 ${s.phone}</div><small>Free demo · bizflowindia.cloud</small></div>`;
  h+=`</div><div class="brand">${D.logos[s.theme]}</div>`;
  el.innerHTML=h; el.style.zIndex=si+1; stage.appendChild(el);
  const q=sel=>Array.from(el.querySelectorAll(sel));
  els.push({s,el,cam:el.querySelector('.cam'),bg:el.querySelector('.bg'),o1:el.querySelector('.o1'),o2:el.querySelector('.o2'),grid:el.querySelector('.grid'),
    dots:q('.dot'),emoji:el.querySelector('.emoji'),tag:el.querySelector('.tag'),
    words:s.lines?q('.txt .w'):[],flat:s.lines?s.lines.flat():[],sub:el.querySelector('.sub'),
    rows:q('.brow'),whos:q('.who'),card:el.querySelector('.card'),ring:el.querySelector('.ring')});
});
window.seek=function(t){
  els.forEach(o=>{
    const s=o.s, lt=t-s.start, vis=t>=s.start-0.001 && t<s.end;
    o.el.style.display=vis?'block':'none'; if(!vis) return;
    // transitions
    let tf='', op=1, bl=0;
    if(s.i>0 && lt<TR){ const p=eo(lt/TR);
      if(s.trans==='zoom'){tf=`scale(${0.82+0.18*p})`; op=p; bl=(1-p)*14;}
      else if(s.trans==='slide'){tf=`translateY(${(1-p)*520}px)`; op=p;}
      else {tf=`translateX(${(1-p)*1080}px) skewX(${-(1-p)*8}deg)`; bl=(1-p)*10;} }
    const out=s.end-t;
    if(out<TR && s.i<D.scenes.length-1){ const nx=D.scenes[s.i+1].trans, p=eio(1-out/TR);
      if(nx==='zoom'){tf+=` scale(${1+0.35*p})`; op*=1-p; bl+=p*16;}
      else if(nx==='slide'){tf+=` translateY(${-p*360}px)`; op*=1-p*0.9;}
      else {tf+=` translateX(${-p*700}px)`; op*=1-p; bl+=p*8;} }
    o.el.style.transform=tf; o.el.style.opacity=op; o.el.style.filter=bl>0.2?`blur(${bl}px)`:'none';
    // background life
    o.o1.style.transform=`translate(${-200+140*Math.sin(t*0.7)}px, ${-260+120*Math.cos(t*0.5)}px)`;
    o.o2.style.transform=`translate(${420+160*Math.cos(t*0.6)}px, ${1180+140*Math.sin(t*0.8)}px)`;
    o.grid.style.transform=`translateY(${-(t*22)%56}px)`;
    o.dots.forEach((d,k)=>{ const sz=6+rnd(k)*14, x=rnd(k+40)*1140, sp=40+rnd(k+80)*90;
      const y=((rnd(k+120)*2100 - t*sp)%2100+2100)%2100; d.style.width=d.style.height=sz+'px';
      d.style.transform=`translate(${x+18*Math.sin(t+k)}px,${y}px)`; d.style.opacity=(s.theme==='light'?0.10:0.22)*(0.5+0.5*Math.sin(t*1.3+k)); });
    // camera push + punch shake on highlight landing
    let cx=0, cy=0, cs=1+0.035*clamp(lt/(s.end-s.start));
    if(s.hlT!==undefined && s.kind==='big'){ const d=lt-s.hlT; if(d>0){ const a=14*Math.exp(-d/0.13); cx=a*Math.sin(d*70); cy=a*Math.cos(d*55); cs+=0.04*Math.exp(-d/0.18);} }
    o.cam.style.transform=`translate(${cx}px,${cy}px) scale(${cs})`;
    if(o.emoji){ const d=lt-s.emojiT; const p=spring(d*1.1); o.emoji.style.transform=`scale(${clamp(p,0,1.4)}) rotate(${d>0.5?7*Math.sin((d-0.5)*4.2):(1-clamp(d/0.5))*-25}deg)`; o.emoji.style.opacity=clamp(d*6); }
    if(o.tag){ const d=lt-s.tagT; o.tag.style.transform=`translateX(${(1-eo(d/0.45))*-240}px)`; o.tag.style.opacity=clamp(d/0.25); }
    o.words.forEach((w,k)=>{ const m=o.flat[k], d=lt-m.d, p=back(d/0.5);
      w.style.transform=`translateY(${(1-eo(d/0.45))*90}px) scale(${0.6+0.4*p}) rotate(${(1-eo(d/0.45))*-6}deg)`; w.style.opacity=clamp(d/0.18);
      if(m.hl){ const b=w.querySelector('.bar'), hp=eo((lt-m.hd)/0.28); b.style.transform=`scaleX(${hp})`;
        if(s.theme==='accent') w.querySelector('.tx').style.color=hp>0.45?'#0A55DA':'#fff'; } });
    if(o.sub){ const d=lt-s.subT; o.sub.style.opacity=clamp(d/0.3)*0.92; o.sub.style.transform=`translateY(${(1-eo(d/0.45))*50}px)`; }
    if(s.bubbles) s.bubbles.forEach((b,j)=>{ const row=o.rows[j], who=o.whos[j], ty=row.querySelector('.typing'), bu=row.querySelector('.bubble');
      const dt=lt-b.typeT, ds=lt-b.showT;
      who.style.opacity=clamp(dt/0.2)*0.65;
      ty.style.display=(dt>0 && ds<0)?'inline-flex':'none';
      ty.querySelectorAll('i').forEach((i,k)=>i.style.transform=`translateY(${-12*Math.max(0,Math.sin((dt*9)-k*0.9))}px)`);
      bu.style.display=ds>=0?'inline-block':'none'; const p=spring(ds*1.15);
      bu.style.transform=`scale(${clamp(0.55+0.45*p,0,1.08)})`; bu.style.opacity=clamp(ds/0.12);
      bu.querySelectorAll('.w').forEach((w)=>{ w.style.opacity=1; });
      bu.querySelectorAll('.w.hl .bar').forEach(bb=>bb.style.display='none'); });
    if(o.card){ const d=lt-s.cardT, p=spring(d*1.05); o.card.style.transform=`translateY(${(1-clamp(p,0,1.1))*260}px) scale(${0.85+0.15*clamp(p,0,1.05)})`; o.card.style.opacity=clamp(d/0.15);
      const r=((d-0.4)%1.1+1.1)%1.1; o.ring.style.transform=`scale(${1+0.12*r})`; o.ring.style.opacity=d>0.4?(1-r/1.1)*0.8:0; }
  });
};
window.seek(0);
"""


def page(scenes, total):
    data = {"TR": TR, "total": total, "scenes": scenes,
            "logos": {th: logo(th) for th in ("dark", "light", "accent")}}
    for s in data["scenes"]: s.pop("ev", None)
    return (f'<!doctype html><html lang="mr"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body><div id="stage"></div><script>window.DATA={json.dumps(data, ensure_ascii=False)};</script>'
            f'<script>{JS}</script></body></html>')


# ---------- sound ----------

def soundtrack(events, total, seed):
    N = int(SR * (total + 0.3)); mix = np.zeros(N); rng = np.random.default_rng(seed)
    def add(sig, at, g=1.0):
        i = max(0, int(at * SR)); j = min(N, i + len(sig))
        if j > i: mix[i:j] += sig[: j - i] * g
    def env(n, a=0.005, d=0.2):
        x = np.arange(n) / SR; return np.minimum(1, x / a) * np.exp(-np.maximum(0, x - a) / d)
    def tone(f, dur, a=0.005, d=0.2):
        n = int(dur * SR); x = np.arange(n) / SR; return np.sin(2 * np.pi * f * x) * env(n, a, d)
    def noise(dur, lo, hi):
        n = int(dur * SR); sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos"); return sosfilt(sos, rng.standard_normal(n))
    def sweep(f0, f1, dur, dec):
        n = int(dur * SR); x = np.arange(n) / SR; f = np.linspace(f0, f1, n)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / dec)
    def kick():
        n = int(0.3 * SR); x = np.arange(n) / SR; f = 45 + 80 * np.exp(-x / 0.035)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.1)
    def pad(freqs, dur):
        n = int(dur * SR); x = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 1.004 * x) for f in freqs)
        return s * np.minimum(1, x / 0.4) * np.minimum(1, (dur - x) / 0.4) / len(freqs)

    # music: 116 BPM, I-V-vi-IV in C, a bar per chord
    beat = 60 / 116; bar = 4 * beat
    prog = [([130.81, 196.0, 261.63, 329.63], 65.41), ([98.0, 196.0, 246.94, 293.66], 49.0),
            ([110.0, 164.81, 220.0, 261.63], 55.0), ([87.31, 174.61, 220.0, 261.63], 43.65)]
    k, tb = 0, 0.0
    while tb < total:
        ch, root = prog[k % 4]; add(pad(ch, min(bar + 0.3, total - tb + 0.3)), tb, 0.09)
        for b in range(4):
            bt = tb + b * beat
            if bt >= total - 0.05: break
            add(kick(), bt, 0.5)
            add(tone(root * (2 if b % 2 else 1), 0.2, 0.004, 0.08), bt + beat / 2, 0.2)
            add(noise(0.04, 7000, 14000) * env(int(0.04 * SR), 0.001, 0.012), bt + beat / 2, 0.09)
            if b in (1, 3): add(noise(0.12, 1500, 6000) * env(int(0.12 * SR), 0.001, 0.04), bt, 0.12)
        tb += bar; k += 1
    # duck the music a little under the effects, fade in/out
    x = np.arange(N) / SR; mix *= np.minimum(1, x / 0.3) * np.clip((total + 0.2 - x) / 0.8, 0, 1)

    def mx(*sigs):
        out = np.zeros(max(len(x) for x in sigs))
        for x in sigs: out[: len(x)] += x
        return out
    fx = {
        "whoosh": lambda: noise(0.5, 400, 7000) * np.sin(np.pi * np.linspace(0, 1, int(0.5 * SR))) ** 2,
        "whoosh_up": lambda: noise(0.4, 900, 9000) * np.sin(np.pi * np.linspace(0, 1, int(0.4 * SR))) ** 2,
        "pop": lambda: sweep(380, 820, 0.08, 0.025),
        "soft": lambda: sweep(500, 700, 0.06, 0.02),
        "tick": lambda: tone(1500, 0.04, 0.001, 0.01),
        "boing": lambda: sweep(220, 520, 0.22, 0.09) * (1 + 0.3 * np.sin(np.linspace(0, 60, int(0.22 * SR)))),
        "ding": lambda: mx(tone(1318.5, 0.9, 0.002, 0.28), 0.5 * tone(1975.5, 0.7, 0.002, 0.18)),
        "bubble": lambda: mx(sweep(600, 1300, 0.07, 0.025), 0.6 * tone(1760, 0.12, 0.002, 0.04)),
        "bell": lambda: mx(tone(1046.5, 1.4, 0.002, 0.45), 0.4 * tone(2093, 1.0, 0.002, 0.25)),
    }
    gain = {"whoosh": 0.32, "whoosh_up": 0.28, "pop": 0.22, "soft": 0.15, "tick": 0.25, "boing": 0.3,
            "ding": 0.18, "bubble": 0.32, "bell": 0.2}
    for name, at in events:
        if name == "typing":
            for q in range(5): add(noise(0.025, 2500, 8000) * env(int(0.025 * SR), 0.001, 0.008), at + q * 0.09, 0.12)
        else:
            add(fx[name](), at, gain[name])
    mix /= max(1e-9, np.abs(mix).max()) / 0.89
    return (np.stack([mix, mix], 1) * 32767).astype(np.int16)


# ---------- build ----------

def build(reel, workdir):
    scenes, total = timeline(reel)
    events = [e for s in scenes for e in s["ev"]]
    out = ROOT / "media" / reel["id"]; out.mkdir(parents=True, exist_ok=True)
    htmlp = workdir / f"{reel['id']}.html"; htmlp.write_text(page(scenes, total))
    wav = workdir / f"{reel['id']}.wav"; wavfile.write(str(wav), SR, soundtrack(events, total, abs(hash(reel["id"])) % 1000))
    subprocess.run([sys.executable, str(ROOT / "motion" / "render.py"), str(htmlp), "--audio", str(wav),
                    "--out", str(out / "reel.mp4")], check=True)
    # cover: end of the first scene, when its text and highlight are all in
    cov = max(0.5, scenes[0]["end"] - TR - 0.15)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{cov:.2f}", "-i", str(out / "reel.mp4"),
                    "-frames:v", "1", "-q:v", "3", str(out / "cover.jpg")], check=True)
    print(reel["id"], f"{total:.1f}s")


def main(spec_path, only):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    work = ROOT / "motion" / "_gen"; work.mkdir(exist_ok=True)
    for reel in spec["reels"]:
        if only and reel["id"] not in only: continue
        build(reel, work)
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
