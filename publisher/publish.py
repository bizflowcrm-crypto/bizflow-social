"""Publish due posts from publisher/queue.json to Instagram, YouTube and Google Business Profile.

Run by .github/workflows/publish.yml every 15 minutes. A post is due when its `when` time has
passed (naive times are Asia/Kolkata). What was posted is recorded in publisher/state.json, so
each network is posted once. A network whose secrets are not set yet is skipped, not failed, and
goes out on a later run once the secrets exist (unless it is more than MAX_LATE_HOURS late).

Usage: python3 publisher/publish.py [--dry-run] [--now 2026-10-13T11:00:00+05:30]
Secrets (env): IG_USER_ID IG_ACCESS_TOKEN | YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN |
               GBP_LOCATION (e.g. accounts/123/locations/456; uses the same Google token)
"""
import argparse, datetime as dt, json, os, pathlib, sys, time
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE, STATE = ROOT / "publisher/queue.json", ROOT / "publisher/state.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
GRAPH = "https://graph.facebook.com/v21.0"
MAX_POSTS_PER_RUN = int(os.environ.get("MAX_POSTS_PER_RUN", "1"))  # a post = all its networks; late posts trickle out
MAX_LATE_HOURS = float(os.environ.get("MAX_LATE_HOURS", "48"))
MAX_ATTEMPTS = 3
REPO = os.environ.get("GITHUB_REPOSITORY", "bizflowcrm-crypto/bizflow-social")
REF = os.environ.get("MEDIA_REF", os.environ.get("GITHUB_REF_NAME", "main"))


def media_url(path):
    return f"https://raw.githubusercontent.com/{REPO}/{REF}/{path}"


def parse_when(s):
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=IST)


def check(r):
    if not r.ok:
        raise RuntimeError(f"{r.request.method} {r.url.split('?')[0]} -> {r.status_code} {r.text[:400]}")
    return r.json() if r.text else {}


# ---------- Instagram (Graph API content publishing) ----------
def ig_wait(cid, token):
    for _ in range(60):
        j = check(requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code,status", "access_token": token}, timeout=60))
        if j.get("status_code") == "FINISHED":
            return
        if j.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram processing failed: {j}")
        time.sleep(10)
    raise RuntimeError("Instagram processing timed out")


def post_instagram(p):
    uid, token = os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]

    def create(params):
        return check(requests.post(f"{GRAPH}/{uid}/media", data={**params, "access_token": token}, timeout=120))["id"]

    if p["kind"] == "reel":
        cid = create({"media_type": "REELS", "video_url": media_url(p["video"]), "caption": p["caption"], "share_to_feed": "true"})
    else:
        kids = [create({"image_url": media_url(s), "is_carousel_item": "true"}) for s in p["slides"]]
        for k in kids:
            ig_wait(k, token)
        cid = create({"media_type": "CAROUSEL", "children": ",".join(kids), "caption": p["caption"]})
    ig_wait(cid, token)
    mid = check(requests.post(f"{GRAPH}/{uid}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=120))["id"]
    link = check(requests.get(f"{GRAPH}/{mid}", params={"fields": "permalink", "access_token": token}, timeout=60)).get("permalink", "")
    return {"id": mid, "url": link}


# ---------- Google (YouTube + Business Profile share one OAuth refresh token) ----------
def google_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}, timeout=60)
    return check(r)["access_token"]


def post_youtube(p):
    f = ROOT / p["video"]
    title = p["youtube"]["title"]
    if "#shorts" not in title.lower():
        title += " #shorts"
    meta = {"snippet": {"title": title[:100], "description": p["youtube"].get("description") or p["caption"],
                        "tags": p["youtube"].get("tags", []), "categoryId": "22"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    h = {"Authorization": f"Bearer {google_token()}", "Content-Type": "application/json; charset=UTF-8",
         "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(f.stat().st_size)}
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                      headers=h, data=json.dumps(meta), timeout=60)
    check(r)
    with open(f, "rb") as fh:
        up = requests.put(r.headers["Location"], data=fh, headers={"Content-Type": "video/mp4"}, timeout=900)
    vid = check(up)["id"]
    return {"id": vid, "url": f"https://www.youtube.com/shorts/{vid}"}


def post_gmb(p):
    loc = os.environ["GBP_LOCATION"]
    body = {"languageCode": "mr", "topicType": "STANDARD", "summary": p["gbp_text"][:1500],
            "media": [{"mediaFormat": "PHOTO", "sourceUrl": media_url(p["gbp_image"])}]}
    j = check(requests.post(f"https://mybusiness.googleapis.com/v4/{loc}/localPosts",
                            headers={"Authorization": f"Bearer {google_token()}"}, json=body, timeout=120))
    return {"id": j.get("name", ""), "url": j.get("searchUrl", "")}


GOOGLE = ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]
NETWORKS = {
    "instagram": (post_instagram, ["IG_USER_ID", "IG_ACCESS_TOKEN"]),
    "youtube": (post_youtube, GOOGLE),
    "gmb": (post_gmb, GOOGLE + ["GBP_LOCATION"]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now")
    a = ap.parse_args()
    now = parse_when(a.now) if a.now else dt.datetime.now(IST)
    queue = json.loads(QUEUE.read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    done = 0
    for p in sorted(queue, key=lambda p: p["when"]):
        if done >= MAX_POSTS_PER_RUN:
            break
        when = parse_when(p["when"])
        if when > now:
            continue
        st = state.get(p["id"], {})
        tried = False
        for net in p["networks"]:
            s = st.get(net, {})
            if s.get("status") in ("posted", "expired") or s.get("attempts", 0) >= MAX_ATTEMPTS:
                continue
            fn, need = NETWORKS[net]
            missing = [k for k in need if not os.environ.get(k)]
            if missing and not a.dry_run:
                print(f"skip  {p['id']} {net}: secrets not set ({', '.join(missing)})")
                continue
            if (now - when).total_seconds() > MAX_LATE_HOURS * 3600:
                state.setdefault(p["id"], {})[net] = {"status": "expired", "at": now.isoformat()}
                print(f"late  {p['id']} {net}: more than {MAX_LATE_HOURS:g}h late, marked expired")
                continue
            print(f"post  {p['id']} -> {net}" + (" (dry run)" if a.dry_run else ""))
            tried = True
            if a.dry_run:
                continue
            try:
                res = fn(p)
                state.setdefault(p["id"], {})[net] = {"status": "posted", "at": now.isoformat(), **res}
                print(f"  ok  {res.get('url') or res.get('id')}")
            except Exception as e:
                state.setdefault(p["id"], {})[net] = {"status": "failed", "attempts": s.get("attempts", 0) + 1,
                                                      "error": str(e)[:500], "at": now.isoformat()}
                print(f"  FAILED {e}", file=sys.stderr)
        done += tried
    if not a.dry_run:
        STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n")
    failed = [(i, n) for i, s in state.items() for n, v in s.items() if v.get("status") == "failed"]
    print(f"done: {done} attempted, {len(failed)} failed so far")
    if any(state[i][n].get("attempts", 0) >= MAX_ATTEMPTS for i, n in failed):
        sys.exit(1)


if __name__ == "__main__":
    main()
