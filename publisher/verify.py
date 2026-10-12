"""Check that the secrets work, without posting anything. Run from the workflow with "verify".

Instagram: reads the connected account's username. YouTube: reads the channel title (must be
bizflowcrm, not BizFlow POS). Business Profile: reads the location title. Prints OK / FAIL / not set.
"""
import os, sys
import requests

bad = 0


def line(name, ok, msg):
    global bad
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {msg}")
    bad += (not ok)


def get(url, **kw):
    r = requests.get(url, timeout=60, **kw)
    return r.status_code, (r.json() if r.text else {})


def have(*keys):
    return all(os.environ.get(k) for k in keys)


if have("IG_USER_ID", "IG_ACCESS_TOKEN"):
    c, j = get(f"https://graph.facebook.com/v21.0/{os.environ['IG_USER_ID']}",
               params={"fields": "username,media_count", "access_token": os.environ["IG_ACCESS_TOKEN"]})
    line("instagram", c == 200, f"@{j.get('username')} ({j.get('media_count')} posts)" if c == 200 else str(j)[:300])
else:
    print("skip instagram: IG_USER_ID / IG_ACCESS_TOKEN not set")

if have("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
    r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    if not r.ok:
        line("google token", False, r.text[:300])
    else:
        tok = {"Authorization": "Bearer " + r.json()["access_token"]}
        line("google token", True, "refresh token works")
        c, j = get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"}, headers=tok)
        items = j.get("items", [])
        line("youtube", c == 200 and bool(items),
             f"channel: {items[0]['snippet']['title']} (must be bizflowcrm)" if items else f"no channel on this login: {str(j)[:300]}")
        if have("GBP_LOCATION"):
            c, j = get(f"https://mybusinessbusinessinformation.googleapis.com/v1/{os.environ['GBP_LOCATION']}",
                       params={"readMask": "title"}, headers=tok)
            line("google business", c == 200, j.get("title", "") if c == 200 else str(j)[:300])
        else:
            print("skip google business: GBP_LOCATION not set")
else:
    print("skip youtube / google business: YT_* secrets not set")

sys.exit(1 if bad else 0)
