"""Keep the queue from running dry by re-queuing evergreen posts.

When fewer than `min_days` days of posts remain in publisher/queue.json, this appends one carousel
(12:30, plus its Google update at 14:00 if it had one) and one Reel (19:00) per day, up to `fill_days`
days ahead. It always picks the posts used longest ago, so nothing repeats until the whole pool has
been used. Recycled posts go to Instagram and Google only (not YouTube, which dislikes repeats), and
festival or seasonal posts are never recycled (see publisher/evergreen.json).

    python3 publisher/recycle.py [--dry-run] [--now 2026-12-02T09:00:00+05:30]
Run daily by .github/workflows/maintenance.yml.
"""
import argparse, copy, datetime as dt, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE, RULES = ROOT / "publisher/queue.json", ROOT / "publisher/evergreen.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
SLOT = {"carousel": "12:30", "gbp": "14:00", "reel": "19:00"}


def parse(s):
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=IST)


def base_id(i):
    return i.split("~r")[0]


def evergreen(base, rules):
    return base not in rules["exclude_ids"] and not any(k in base for k in rules["exclude_keywords"])


def plan(queue, rules, now, min_days=None, fill_days=None):
    """Returns the new queue entries (possibly none)."""
    min_days = rules.get("min_days", 14) if min_days is None else min_days
    fill_days = rules.get("fill_days", 28) if fill_days is None else fill_days
    last = max(parse(e["when"]) for e in queue)
    if (last - now).total_seconds() >= min_days * 86400:
        return []
    last_used, first = {}, {}
    gbp = {}
    for e in queue:
        b = base_id(e["id"])
        if e["kind"] == "gbp":
            gbp[b[:-4]] = e          # companion of the carousel whose id is b without "-gbp"
            continue
        last_used[b] = max(last_used.get(b, ""), e["when"])
        first.setdefault(b, e)       # the original entry, with its media paths
    pools = {k: [b for b, e in first.items() if e["kind"] == k and evergreen(b, rules)] for k in ("carousel", "reel")}
    if not pools["carousel"] or not pools["reel"]:
        print("recycler: no evergreen posts to recycle", file=sys.stderr)
        return []
    count = {}
    for e in queue:
        count[base_id(e["id"])] = count.get(base_id(e["id"]), 0) + 1
    new = []
    day = max(last.astimezone(IST).date(), now.astimezone(IST).date()) + dt.timedelta(days=1)
    end = now.astimezone(IST).date() + dt.timedelta(days=fill_days)
    while day <= end:
        for kind in ("carousel", "reel"):
            b = min(pools[kind], key=lambda x: (last_used.get(x, ""), x))
            n = count[b] = count.get(b, 0) + 1
            e = copy.deepcopy(first[b])
            e["id"], e["when"] = f"{b}~r{n}", f"{day.isoformat()}T{SLOT[kind]}:00+05:30"
            e["networks"] = ["instagram"]
            e.pop("youtube", None)
            new.append(e)
            last_used[b] = e["when"]
            if kind == "carousel" and b in gbp:
                g = copy.deepcopy(gbp[b])
                g["id"], g["when"] = f"{g['id'].split('~r')[0]}~r{n}", f"{day.isoformat()}T{SLOT['gbp']}:00+05:30"
                new.append(g)
        day += dt.timedelta(days=1)
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now")
    a = ap.parse_args()
    now = parse(a.now) if a.now else dt.datetime.now(IST)
    queue = json.loads(QUEUE.read_text())
    rules = json.loads(RULES.read_text())
    last = max(parse(e["when"]) for e in queue)
    days = (last - now).total_seconds() / 86400
    new = plan(queue, rules, now)
    if not new:
        print(f"recycler: queue has {days:.0f} days of posts ahead (threshold {rules['min_days']}); nothing to add")
        return
    print(f"recycler: only {days:.0f} days ahead, adding {len(new)} entries "
          f"({new[0]['when'][:10]} to {new[-1]['when'][:10]})" + (" (dry run)" if a.dry_run else ""))
    for e in new:
        print("  ", e["when"][:16], e["id"], "+".join(e["networks"]))
    if not a.dry_run:
        queue += new
        queue.sort(key=lambda e: e["when"])
        QUEUE.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
