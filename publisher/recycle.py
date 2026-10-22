"""Keep the queue from running dry by re-queuing evergreen posts.

When a day within the next `min_days` days has no carousel or no Reel in publisher/queue.json, this fills
every such day up to `fill_days` days ahead with a carousel (12:30, plus its Google update at 14:00 if it had one)
and a Reel (19:00). It always picks the posts used longest ago, so nothing repeats until the whole pool has
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


def plan(queue, rules, now, min_days=None, fill_days=None, state=None):
    """Returns the new queue entries (possibly none). Fills every day in the next `fill_days` days that has no
    carousel or no Reel, but only acts when a gap falls within the next `min_days` days."""
    min_days = rules.get("min_days", 14) if min_days is None else min_days
    fill_days = rules.get("fill_days", 28) if fill_days is None else fill_days
    today = now.astimezone(IST).date()
    have = {"carousel": set(), "reel": set()}
    for e in queue:
        if e["kind"] in have and "instagram" in e["networks"]:
            have[e["kind"]].add(parse(e["when"]).astimezone(IST).date())
    window = [today + dt.timedelta(days=n) for n in range(1, fill_days + 1)]
    gaps = [d for d in window if d not in have["carousel"] or d not in have["reel"]]
    if not any(d <= today + dt.timedelta(days=min_days) for d in gaps):
        return []
    last_used, first = {}, {}
    gbp = {}
    state = state or {}
    for e in queue:
        b = base_id(e["id"])
        if e["kind"] == "gbp":
            gbp[b[:-4]] = e          # companion of the carousel whose id is b without "-gbp"
            continue
        first.setdefault(b, e)       # the original entry, with its media paths
        # "used" = actually posted (by the time it went out) or still scheduled in the future.
        # A post whose slot passed without it going out (expired, failed) counts as never used, so it is picked first.
        posted = state.get(e["id"], {}).get("instagram", {})
        if posted.get("status") == "posted":
            used = posted["at"]
        elif parse(e["when"]) > now:
            used = e["when"]
        else:
            used = ""
        last_used[b] = max(last_used.get(b, ""), used)
    pools = {k: [b for b, e in first.items() if e["kind"] == k and evergreen(b, rules)] for k in ("carousel", "reel")}
    if not pools["carousel"] or not pools["reel"]:
        print("recycler: no evergreen posts to recycle", file=sys.stderr)
        return []
    count = {}
    for e in queue:
        count[base_id(e["id"])] = count.get(base_id(e["id"]), 0) + 1
    new = []
    for day in gaps:
        for kind in ("carousel", "reel"):
            if day in have[kind]:
                continue
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
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now")
    a = ap.parse_args()
    now = parse(a.now) if a.now else dt.datetime.now(IST)
    queue = json.loads(QUEUE.read_text())
    rules = json.loads(RULES.read_text())
    state_p = ROOT / "publisher/state.json"
    new = plan(queue, rules, now, state=json.loads(state_p.read_text()) if state_p.exists() else {})
    if not new:
        print(f"recycler: no gaps in the next {rules['min_days']} days; nothing to add")
        return
    days = sorted({e["when"][:10] for e in new})
    print(f"recycler: filling {len(days)} day(s) with gaps ({days[0]} to {days[-1]}), adding {len(new)} entries"
          + (" (dry run)" if a.dry_run else ""))
    for e in new:
        print("  ", e["when"][:16], e["id"], "+".join(e["networks"]))
    if not a.dry_run:
        queue += new
        queue.sort(key=lambda e: e["when"])
        QUEUE.write_text(json.dumps(queue, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
