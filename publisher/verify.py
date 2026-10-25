"""Check that the secrets work, without posting anything. Run from the workflow with "verify".

For every account in accounts.json. Instagram: reads the connected account's username. YouTube: reads the channel title. Business Profile: reads the location title. Prints OK / FAIL / not set.
"""
import os, pathlib, sys
import requests
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import accounts

bad = 0


def line(name, ok, msg):
    global bad
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {msg}")
    bad += (not ok)


def get(url, **kw):
    r = requests.get(url, timeout=60, **kw)
    return r.status_code, (r.json() if r.text else {})


def check_account(name):
    c = accounts.creds(name)
    print(f"--- account '{name}': {accounts.label(name)}")
    if c.get("ig_user_id") and c.get("ig_token"):
        code, j = get(f"https://graph.facebook.com/v21.0/{c['ig_user_id']}",
                      params={"fields": "username,media_count", "access_token": c["ig_token"]})
        line(f"{name} instagram", code == 200, f"@{j.get('username')} ({j.get('media_count')} posts)" if code == 200 else str(j)[:300])
    else:
        print("skip instagram: ig_user_id / ig_token not set")
    if c.get("yt_client_id") and c.get("yt_client_secret") and c.get("yt_refresh_token"):
        r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={
            "client_id": c["yt_client_id"], "client_secret": c["yt_client_secret"],
            "refresh_token": c["yt_refresh_token"], "grant_type": "refresh_token"})
        if not r.ok:
            line(f"{name} google token", False, r.text[:300])
            return
        tok = {"Authorization": "Bearer " + r.json()["access_token"]}
        line(f"{name} google token", True, "refresh token works")
        code, j = get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"}, headers=tok)
        items = j.get("items", [])
        line(f"{name} youtube", code == 200 and bool(items),
             f"channel: {items[0]['snippet']['title']} (is this the channel you meant?)" if items else f"no channel on this login: {str(j)[:300]}")
        if c.get("gbp_location"):
            code, j = get(f"https://mybusinessbusinessinformation.googleapis.com/v1/{c['gbp_location']}",
                          params={"readMask": "title"}, headers=tok)
            line(f"{name} google business", code == 200, j.get("title", "") if code == 200 else str(j)[:300])
        else:
            print("skip google business: gbp_location not set")
    else:
        print("skip youtube / google business: yt_* keys not set")


for n in accounts.names():
    check_account(n)

sys.exit(1 if bad else 0)
