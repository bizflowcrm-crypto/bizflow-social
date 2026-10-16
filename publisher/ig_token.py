"""One-time helper: turn a short-lived Facebook/Instagram token into a Page token that does not expire.

Run on your own computer (not in GitHub, and do not paste the output in chat):
    python3 publisher/ig_token.py APP_ID APP_SECRET SHORT_LIVED_USER_TOKEN

APP_ID and APP_SECRET: Meta developer dashboard > your app > Settings > Basic.
SHORT_LIVED_USER_TOKEN: Graph API Explorer > select your app > Generate Access Token, with the
permissions instagram_basic, instagram_content_publish, pages_show_list, pages_read_engagement.

It prints, for each Facebook Page that has an Instagram business account, the account ID and a Page
token. A Page token made from a long-lived user token never expires. Save them as the GitHub secrets
INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN.
"""
import sys
import requests

G = "https://graph.facebook.com/v21.0"


def get(path, **params):
    r = requests.get(f"{G}/{path}", params=params, timeout=60)
    j = r.json()
    if "error" in j:
        sys.exit(f"Facebook said: {j['error'].get('message')}")
    return j


def main(app_id, secret, short):
    long_user = get("oauth/access_token", grant_type="fb_exchange_token", client_id=app_id,
                    client_secret=secret, fb_exchange_token=short)["access_token"]
    pages = get("me/accounts", access_token=long_user, fields="name,access_token,instagram_business_account")["data"]
    found = 0
    for p in pages:
        ig = p.get("instagram_business_account")
        if not ig:
            continue
        found += 1
        info = get("debug_token", input_token=p["access_token"], access_token=f"{app_id}|{secret}")["data"]
        exp = info.get("expires_at", 0)
        print(f"\nPage: {p['name']}")
        print(f"  INSTAGRAM_ACCOUNT_ID  = {ig['id']}")
        print(f"  INSTAGRAM_ACCESS_TOKEN = {p['access_token']}")
        print(f"  token expires: {'never' if exp == 0 else exp}")
    if not found:
        sys.exit("No Facebook Page with a linked Instagram business account was found for this token. "
                 "Check the permissions and that @bizflowindia is linked to a Page.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
