"""Writes reports/content-calendar-nov-dec.md: one row per day, 11 Nov to 16 Dec 2026.
Run from the repo root: python3 content/calendar_nov_dec.py"""
import datetime as dt, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
cars = json.loads((ROOT / "posts/nov-dec-carousels.json").read_text())["posts"]
reels = json.loads((ROOT / "posts/nov-dec-reels.json").read_text())["reels"]
start = dt.date(2026, 11, 11)
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKS = [(0, "11-15 Nov: Bhaubeej and after Diwali"), (5, "16-22 Nov: Hotel week (TableFlow)"), (12, "23-29 Nov: Websites"),
         (19, "30 Nov-6 Dec: Traders (AccountFlow)"), (26, "7-13 Dec: Software, support, demo, wedding season"),
         (33, "14-16 Dec: Super shops, stock, year-end")]
# the weeks above are by day index; day 0 = 11 Nov
out = ["# Content calendar, 11 Nov to 16 Dec 2026", "",
       "One carousel (12:30, plus a Google update at 14:00) and one Reel (19:00) every day. "
       "Instagram gets all of them; YouTube gets the Short version of each. Times are IST. "
       "Queued in `publisher/queue.json`; specs in `posts/nov-dec-*.json`.", ""]
for i, (c, r) in enumerate(zip(cars, reels)):
    d = start + dt.timedelta(days=i)
    for idx, title in WEEKS:
        if i == idx:
            out += ["", f"## {title}", "", "| Date | 12:30 carousel (+ Google 14:00) | 19:00 Reel |", "|---|---|---|"]
    ct = c["youtube_title"].split(" | ")[0].replace(" #shorts", "")
    rt = r["youtube_title"].split(" | ")[0].replace(" #shorts", "")
    out.append(f"| {DAYS[d.weekday()]} {d.day} {d.strftime('%b')} | {ct} | {rt} |")
out += ["", "Not included: real customer videos (`bite.py`) and any post that names a customer; those need the owner's OK first, see CUSTOMERS.md."]
(ROOT / "reports/content-calendar-nov-dec.md").write_text("\n".join(out) + "\n")
print("wrote reports/content-calendar-nov-dec.md,", len(cars), "days")
