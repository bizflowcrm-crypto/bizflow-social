"""Daily health check for the auto-publisher. Exits 1 (so the workflow fails and an issue is opened)
if anything needs attention, ideally BEFORE posting stops:

- Instagram token: valid, and how many days until it expires (never = fine, warns under 10 days).
- Google (YouTube / Business Profile) refresh token still accepted, when configured.
- The queue: how many days of posts are left (the recycler normally keeps this above 14).
- Posting itself: posts that are due but nothing has gone out; failed or expired posts in the last 3 days.

    python3 publisher/health.py [--now 2026-10-22T09:00:00+05:30]
Writes a markdown report to stdout, to $GITHUB_STEP_SUMMARY and to health_report.md.
"""
import argparse, datetime as dt, json, os, pathlib, sys
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
G = "https://graph.facebook.com/v21.0"
WARN_DAYS = 10
rows = []  # (level, name, text)


def add(level, name, text):
    rows.append((level, name, text))


def parse(s):
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=IST)


def have(*k):
    return all(os.environ.get(x) for x in k)


def check_instagram(now):
    if not have("IG_USER_ID", "IG_ACCESS_TOKEN"):
        return add("FAIL", "Instagram token", "IG_USER_ID / IG_ACCESS_TOKEN are not set.")
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]
    try:
        r = requests.get(f"{G}/debug_token", params={"input_token": tok, "access_token": tok}, timeout=60)
        d = r.json().get("data") if r.ok else None
    except requests.RequestException as e:
        return add("WARN", "Instagram token", f"Could not reach Meta to check it ({e}).")
    if d is not None:
        if not d.get("is_valid", False):
            return add("FAIL", "Instagram token", f"Meta says the token is invalid: {d.get('error', {}).get('message', 'expired or revoked')}. "
                       "Make a new one (publisher/SETUP.md, 'Token expired').")
        left = []
        for key, label in (("expires_at", "token"), ("data_access_expires_at", "data access")):
            ts = d.get(key, 0)
            if ts:
                left.append((label, (dt.datetime.fromtimestamp(ts, dt.timezone.utc) - now).total_seconds() / 86400))
        soon = [(l, x) for l, x in left if x < WARN_DAYS]
        if soon:
            when = lambda x: f"{x * 24:.0f} hours" if x < 2 else f"{x:.0f} days"
            return add("WARN", "Instagram token", "Expires soon: " + ", ".join(f"{l} in {when(x)}" for l, x in soon)
                       + ". Make a new token (publisher/SETUP.md) before then.")
        return add("OK", "Instagram token", "valid, " + (", ".join(f"{l} expires in {x:.0f} days" for l, x in left) if left else "does not expire"))
    # debug_token not available for this token type: at least check the token works
    try:
        r = requests.get(f"{G}/{uid}", params={"fields": "username", "access_token": tok}, timeout=60)
    except requests.RequestException as e:
        return add("WARN", "Instagram token", f"Could not reach Meta to check it ({e}).")
    if r.ok:
        add("OK", "Instagram token", f"works for @{r.json().get('username')} (expiry date not readable for this token type)")
    else:
        add("FAIL", "Instagram token", f"rejected by Meta: {r.text[:200]}")


def check_google():
    if not have("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        return add("INFO", "Google token", "YouTube / Business Profile not configured yet (posts for them are skipped).")
    try:
        r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={
            "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
            "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    except requests.RequestException as e:
        return add("WARN", "Google token", f"Could not reach Google to check it ({e}).")
    if r.ok:
        add("OK", "Google token", "refresh token accepted")
    else:
        add("FAIL", "Google token", f"refresh token rejected ({r.json().get('error', r.status_code)}). Run publisher/google_token.py again "
            "and make sure the Google app is published, not in Testing mode.")


def check_repo_size():
    repo, tok = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not repo or not tok:
        return
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}", headers={"Authorization": f"Bearer {tok}"}, timeout=30)
        mb = r.json()["size"] / 1024
    except Exception:
        return
    lvl = "FAIL" if mb > 4500 else "WARN" if mb > 1500 else "OK"
    add(lvl, "Repository size", f"{mb:,.0f} MB (GitHub recommends staying under 1,000 MB and never passing 5,000 MB)."
        + (" Time to move media to a separate rewritten branch (see content/README.md)." if lvl != "OK" else ""))


def check_queue_and_posting(now):
    queue = json.loads((ROOT / "publisher/queue.json").read_text())
    state_p = ROOT / "publisher/state.json"
    state = json.loads(state_p.read_text()) if state_p.exists() else {}
    ig = [e for e in queue if "instagram" in e["networks"]]
    if not ig:
        return add("FAIL", "Queue", "no Instagram posts are queued at all.")
    last = max(parse(e["when"]) for e in ig)
    days = (last - now).total_seconds() / 86400
    lvl = "FAIL" if days < 3 else "WARN" if days < 7 else "OK"
    add(lvl, "Queue", f"{days:.0f} days of Instagram posts left (last one {last.astimezone(IST):%d %b %Y})."
        + (" The daily recycler normally keeps this above 14; check the maintenance workflow." if lvl != "OK" else ""))

    def st(e, net="instagram"):
        return state.get(e["id"], {}).get(net, {})
    posted = [parse(st(e)["at"]) for e in ig if st(e).get("status") == "posted"]
    due_pending = [e for e in ig if parse(e["when"]) <= now - dt.timedelta(hours=12)
                   and st(e).get("status") not in ("posted", "expired")]
    recent_post = max(posted) if posted else None
    in_quiet = 0 <= now.astimezone(IST).hour < 7
    if due_pending and not in_quiet and (recent_post is None or now - recent_post > dt.timedelta(hours=12)):
        add("WARN", "Posting", f"{len(due_pending)} Instagram posts are due but none has gone out in 12 hours"
            + (f" (last post {recent_post.astimezone(IST):%d %b %H:%M})" if recent_post else "") + ". Check the Publish workflow runs.")
    else:
        add("OK", "Posting", f"last Instagram post {recent_post.astimezone(IST):%d %b %H:%M}" if recent_post else "nothing due yet")
    cutoff = now - dt.timedelta(days=3)
    failed = [(i, n, r) for i, v in state.items() for n, r in v.items() if r.get("status") == "failed" and parse(r["at"]) > cutoff]
    expired = [(i, n) for i, v in state.items() for n, r in v.items() if r.get("status") == "expired" and parse(r["at"]) > cutoff]
    if failed:
        add("WARN", "Failed posts", "; ".join(f"{i} ({n}): {r.get('error', '')[:90]}" for i, n, r in failed[:5]))
    if expired:
        add("INFO", "Expired posts", f"{len(expired)} posts were skipped as more than 7 days late: " + ", ".join(i for i, _ in expired[:5]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now")
    a = ap.parse_args()
    now = parse(a.now) if a.now else dt.datetime.now(IST)
    check_instagram(now)
    check_google()
    check_queue_and_posting(now)
    check_repo_size()
    bad = [r for r in rows if r[0] in ("WARN", "FAIL")]
    icon = {"OK": "✅", "INFO": "ℹ️", "WARN": "⚠️", "FAIL": "❌"}
    out = [f"# Social automation health, {now.astimezone(IST):%d %b %Y %H:%M} IST", "",
           "**" + ("Needs attention" if bad else "All good") + "**", "", "| | Check | Result |", "|---|---|---|"]
    out += [f"| {icon[l]} | {n} | {t.replace('|', '/')} |" for l, n, t in rows]
    text = "\n".join(out) + "\n"
    print(text)
    pathlib.Path("health_report.md").write_text(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(text)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
