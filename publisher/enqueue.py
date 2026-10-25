"""Add posts from a spec file (posts/*.json) to publisher/queue.json.

python3 publisher/enqueue.py posts/new-account-reels-1.json --start 2026-10-13 --slots 11:00,17:30,20:30
python3 publisher/enqueue.py posts/new-account-carousels-1.json --start 2026-10-13 --slots 12:30,19:00 --gbp-slot 14:00

Posts fill the slots day by day, in spec order (or --ids order). Reels go to Instagram + YouTube,
carousels to Instagram + YouTube (short.mp4), and, with --gbp-slot, one carousel a day that has a
`gbp_text` also goes to Google Business Profile. `--account NAME` picks the account (publisher/accounts.json). Times are Asia/Kolkata. Re-running skips ids already queued.
"""
import argparse, datetime as dt, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import accounts

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "publisher/queue.json"


def entry(p, kind, when, account):
    mdir = f"media/{p['id']}"
    yt = {"title": p.get("youtube_title") or p.get("title"),
          "description": p.get("youtube_description") or p["caption"], "tags": p.get("youtube_tags", [])}
    if kind == "reel":
        e = {"video": f"{mdir}/reel.mp4"}
    else:
        slides = sorted(f.name for f in (ROOT / mdir).glob("[0-9][0-9].jpg"))
        e = {"slides": [f"{mdir}/{s}" for s in slides], "video": f"{mdir}/short.mp4"}
    for need in (e["video"], *e.get("slides", [])):
        if not (ROOT / need).exists() and (kind == "reel" or need != e["video"]):
            sys.exit(f"missing media: {need}")
    nets = ["instagram"] + (["youtube"] if yt["title"] and (ROOT / e["video"]).exists() else [])   # no Short file, no YouTube
    return {"id": p["id"], "account": account, "when": when, "kind": kind, "networks": nets, "caption": p["caption"], "youtube": yt, **e}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--start", required=True)
    ap.add_argument("--slots", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--gbp-slot")
    ap.add_argument("--account", help="which account in publisher/accounts.json posts these (default: the default account)")
    a = ap.parse_args()
    account = a.account or accounts.default()
    if account not in accounts.names():
        sys.exit(f"unknown account '{account}'. Known: {', '.join(accounts.names())} (publisher/accounts.json)")
    spec = json.loads(pathlib.Path(a.spec).read_text())
    kind, items = ("reel", spec["reels"]) if "reels" in spec else ("carousel", spec["posts"])
    if a.ids:
        by = {p["id"]: p for p in items}
        items = [by[i] for i in a.ids.split(",")]
    queue = json.loads(QUEUE.read_text()) if QUEUE.exists() else []
    have = {q["id"] for q in queue}
    slots = a.slots.split(",")
    start = dt.date.fromisoformat(a.start)
    gbp_days = {q["when"][:10] for q in queue if "gmb" in q["networks"] and accounts.of(q) == account}
    n = added = 0
    for p in items:
        if p["id"] in have:
            continue
        d = (start + dt.timedelta(days=n // len(slots))).isoformat()
        queue.append(entry(p, kind, f"{d}T{slots[n % len(slots)]}:00+05:30", account))
        n += 1
        added += 1
        if kind == "carousel" and a.gbp_slot and p.get("gbp_text") and d not in gbp_days:
            gbp_days.add(d)
            queue.append({"id": p["id"] + "-gbp", "account": account, "when": f"{d}T{a.gbp_slot}:00+05:30", "kind": "gbp", "networks": ["gmb"],
                          "caption": p["caption"], "gbp_text": p["gbp_text"], "gbp_image": f"media/{p['id']}/01.jpg"})
    queue.sort(key=lambda q: q["when"])
    QUEUE.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n")
    print(f"queued {added} post(s); queue now has {len(queue)} entries")


if __name__ == "__main__":
    main()
