"""Render a seek(t)-driven HTML animation to MP4.

The page must expose window.seek(t) and window.DUR, and compute every style
from t (no timers, no CSS transitions), so each frame is reproducible.

  python3 render.py bizflow-promo.html --preview        # one frame per half second -> contact sheet
  python3 render.py bizflow-promo.html --audio a.wav     # full render with motion blur

Motion blur: SUB subframes are captured per output frame and averaged by ffmpeg.
"""
import sys, pathlib, subprocess, shutil, argparse
from playwright.sync_api import sync_playwright

W, H, FPS, SUB = 1080, 1920, 30, 3

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("--preview", action="store_true")
ap.add_argument("--audio"); ap.add_argument("--out")
a = ap.parse_args()

src = pathlib.Path(a.html).resolve()
out = pathlib.Path(a.out).resolve() if a.out else src.with_suffix(".mp4")
tmp = src.parent / "_frames"; shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()

with sync_playwright() as pw:
    b = pw.chromium.launch()
    page = b.new_page(viewport={"width": W, "height": H})
    page.goto(src.as_uri() + "#render"); page.wait_for_timeout(400)
    dur = page.evaluate("window.DUR")
    if a.preview:
        times = [i * 0.5 + 0.25 for i in range(int(dur * 2))]
        for i, t in enumerate(times):
            page.evaluate("t => window.seek(t)", t)
            page.screenshot(path=str(tmp / f"p{i:03d}.jpg"), type="jpeg", quality=80)
        b.close()
        sheet = src.with_name(src.stem + "-preview.jpg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1", "-i", str(tmp / "p%03d.jpg"),
                        "-vf", "scale=216:384,tile=10x3", "-frames:v", "1", "-q:v", "3", str(sheet)], check=True)
        shutil.rmtree(tmp); print("preview", sheet); sys.exit()
    n = int(dur * FPS * SUB)
    for i in range(n):
        page.evaluate("t => window.seek(t)", i / (FPS * SUB))
        page.screenshot(path=str(tmp / f"f{i:05d}.jpg"), type="jpeg", quality=93)
        if i % 300 == 0: print(f"{i}/{n}", flush=True)
    b.close()

cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS * SUB), "-i", str(tmp / "f%05d.jpg")]
if a.audio: cmd += ["-i", a.audio]
else: cmd += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo"]
cmd += ["-vf", f"tmix=frames={SUB},fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "17"]
cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
cmd += ["-movflags", "+faststart", str(out)]
subprocess.run(cmd, check=True)
shutil.rmtree(tmp); print("wrote", out)
