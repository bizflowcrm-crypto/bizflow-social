"""Make a copy-paste sheet for posting by hand (YouTube Studio / Google Business Profile) while
the API approvals are pending.

python3 publisher/manual_sheet.py 2026-10-13 2026-10-16 > reports/manual-sheet.md
Lists, per day, each YouTube Short (title, description, tags, video file link) and each Google update
(text, image link) that is queued in that date range (inclusive).
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "bizflowcrm-crypto/bizflow-social"


def url(p):
    return f"https://raw.githubusercontent.com/{REPO}/main/{p}"


def main(a, b):
    q = [e for e in json.loads((ROOT / "publisher/queue.json").read_text()) if a <= e["when"][:10] <= b]
    print(f"# Manual posting sheet, {a} to {b}\n")
    print("Download the file from the link, then upload and paste. Schedule it in YouTube Studio (Schedule) at the time shown.\n")
    for e in q:
        day, t = e["when"][:10], e["when"][11:16]
        if "youtube" in e["networks"]:
            y = e["youtube"]
            print(f"## {day} {t}: YouTube Short, {e['id']}\n")
            print(f"- Video: {url(e['video'])}\n- Title: {y['title']}\n- Tags: {', '.join(y['tags'])}\n- Not made for kids\n")
            print("Description:\n\n```\n" + y["description"] + "\n```\n")
        if "gmb" in e["networks"]:
            print(f"## {day} {t}: Google Business Profile update, {e['id']}\n")
            print(f"- Image: {url(e['gbp_image'])}\n")
            print("Text:\n\n```\n" + e["gbp_text"] + "\n```\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
