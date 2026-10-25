"""Turn one content file (written by any chatbot, see content/README.md) into queued posts.

    python3 content/process_inbox.py content/inbox/2027-01.txt --stage check      # only validate
    python3 content/process_inbox.py content/inbox/2027-01.txt --stage prepare    # validate, write specs, render, verify
    python3 content/process_inbox.py content/inbox/2027-01.txt --stage queue      # add to publisher/queue.json, archive the file

Run by .github/workflows/content.yml. Exit code 2 means the file has errors to fix; the messages carry line numbers
so they can be pasted back to the chatbot.
"""
import argparse, datetime as dt, json, os, pathlib, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inbox_lib as il

sys.path.insert(0, str(il.ROOT / "publisher"))
import accounts

ROOT = il.ROOT


def report(path, errs, warns):
    gh = os.environ.get("GITHUB_ACTIONS")
    for kind, items in (("error", errs), ("warning", warns)):
        for no, msg in sorted(items):
            print(f"{kind.upper()} line {no}: {msg}")
            if gh:
                print(f"::{kind} file={path},line={no}::{msg}")


def load(path):
    text = pathlib.Path(path).read_text()
    header, posts, perr = il.parse(text)
    stem = pathlib.Path(path).stem
    own = {f"inbox-{stem}-reels.json", f"inbox-{stem}-carousels.json"}   # specs this very file produced
    errs, warns = il.check(header, posts, perr, taken=il.existing_ids(own))
    return header, posts, errs, warns


def spec_paths(stem):
    return ROOT / f"posts/inbox-{stem}-reels.json", ROOT / f"posts/inbox-{stem}-carousels.json"


def verify_media(reels, cars):
    import numpy as np
    bad = []
    for c in cars:
        d = ROOT / "media" / c["id"]
        have = sorted(d.glob("[0-9][0-9].jpg"))
        if len(have) != len(c["slides"]) or any(f.stat().st_size < 20_000 for f in have):
            bad.append(f"{c['id']}: expected {len(c['slides'])} slide images, found {len(have)} (or one is nearly empty)")
    for r in reels:
        f = ROOT / "media" / r["id"] / "reel.mp4"
        if not f.exists() or f.stat().st_size < 200_000 or not (f.parent / "cover.jpg").exists():
            bad.append(f"{r['id']}: reel.mp4 or cover.jpg missing or too small"); continue
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                   capture_output=True, text=True).stdout.strip() or 0)
        if not 8 <= dur <= 25:
            bad.append(f"{r['id']}: duration {dur:.1f}s is outside 8-25s")
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(dur / 2), "-i", str(f), "-frames:v", "1", "-vf", "scale=108:192,format=gray",
                              "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(raw) < 108 * 192 or float(np.frombuffer(raw, dtype=np.uint8).std()) < 6:
            bad.append(f"{r['id']}: the middle frame looks blank")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--stage", choices=["check", "prepare", "queue"], default="check")
    a = ap.parse_args()
    path = pathlib.Path(a.file)
    stem = path.stem
    header, posts, errs, warns = load(a.file)
    report(a.file, errs, warns)
    if errs:
        print(f"\n{len(errs)} error(s). Fix them (paste the lines above to your chatbot) and commit the file again.")
        sys.exit(2)
    reels, cars = il.expand(posts)
    print(f"{path.name}: {len(reels)} reels, {len(cars)} carousels, {len(warns)} warnings")
    if a.stage == "check":
        return
    rp, cp = spec_paths(stem)
    if a.stage == "prepare":
        if reels:
            rp.write_text(json.dumps({"week": stem, "reels": reels}, ensure_ascii=False, indent=1) + "\n")
        if cars:
            cp.write_text(json.dumps({"week": stem, "posts": cars}, ensure_ascii=False, indent=1) + "\n")
        if cars:
            subprocess.run([sys.executable, str(ROOT / "build.py"), str(cp)], check=True, cwd=ROOT)
        if reels:   # one process, one reel at a time
            subprocess.run([sys.executable, str(ROOT / "motion/reels.py"), str(rp)], check=True, cwd=ROOT)
        bad = verify_media(reels, cars)
        for b in bad:
            print("MEDIA PROBLEM", b); print(f"::error::{b}") if os.environ.get("GITHUB_ACTIONS") else None
        if bad:
            sys.exit(3)
        print("media rendered and verified")
        return
    # stage queue
    q = json.loads((ROOT / "publisher/queue.json").read_text())
    account = header.get("account", (0, accounts.default()))[1]
    start = header.get("start", (0, ""))[1]
    if not start:
        mine = [e for e in q if accounts.of(e) == account]
        last = max(dt.datetime.fromisoformat(e["when"]) for e in mine) if mine else dt.datetime.now()
        start = (last.date() + dt.timedelta(days=1)).isoformat()
    t = lambda k, d: header.get(k, (0, d))[1]
    enq = [sys.executable, str(ROOT / "publisher/enqueue.py"), "--account", account]
    if cars:
        subprocess.run(enq + [str(cp), "--start", start, "--slots", t("carousel_time", "12:30"), "--gbp-slot", t("google_time", "14:00")], check=True, cwd=ROOT)
    if reels:
        subprocess.run(enq + [str(rp), "--start", start, "--slots", t("reel_time", "19:00")], check=True, cwd=ROOT)
    done = ROOT / "content/done"; done.mkdir(exist_ok=True)
    shutil.move(str(path), str(done / path.name))
    print(f"queued for account '{account}' from {start}; archived to content/done/{path.name}")


if __name__ == "__main__":
    main()
