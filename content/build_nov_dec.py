"""Writes posts/nov-dec-carousels.json and posts/nov-dec-reels.json from the content/ entries and checks them.
Run from the repo root: python3 content/build_nov_dec.py"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from nov_dec_carousels import CAROUSELS
from nov_dec_reels import REELS

ROOT = pathlib.Path(__file__).resolve().parent.parent
problems = []
ids = [x["id"] for x in CAROUSELS + REELS]
if len(ids) != len(set(ids)): problems.append("duplicate ids")
for x in CAROUSELS + REELS:
    if len(x["youtube_title"]) > 100: problems.append(f"{x['id']}: YouTube title {len(x['youtube_title'])} chars")
    if len(x["caption"]) > 2200: problems.append(f"{x['id']}: caption too long")
    g = x.get("gbp_text")
    if g is not None and (re.search(r"\d{8,}", g.replace(" ", "")) or "#" in g): problems.append(f"{x['id']}: phone/hashtag in Google text")
    for s in x.get("slides", []):
        if s["kind"] == "list" and len(s["items"]) > 6: problems.append(f"{x['id']}: >6 list items")
for p in problems: print("PROBLEM", p)
if problems: sys.exit(1)
(ROOT / "posts/nov-dec-carousels.json").write_text(json.dumps({"week": "2026-11-12", "note": "11 Nov to 16 Dec 2026, one per day. Queue with publisher/enqueue.py.", "posts": CAROUSELS}, ensure_ascii=False, indent=1) + "\n")
(ROOT / "posts/nov-dec-reels.json").write_text(json.dumps({"week": "2026-11-12", "note": "11 Nov to 16 Dec 2026, one per day. Queue with publisher/enqueue.py.", "reels": REELS}, ensure_ascii=False, indent=1) + "\n")
print(len(CAROUSELS), "carousels,", len(REELS), "reels written;", max(len(x["youtube_title"]) for x in CAROUSELS + REELS), "= longest YouTube title")
