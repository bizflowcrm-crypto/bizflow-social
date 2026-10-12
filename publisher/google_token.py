"""One-time helper: get a Google refresh token for YouTube uploads + Business Profile posts.

Run this on your own computer (not in GitHub), signed in as the bizflowcrm Google account:
    python3 publisher/google_token.py CLIENT_ID CLIENT_SECRET
Open the printed link, approve, and the refresh token is printed here. Save it as the GitHub
secret YT_REFRESH_TOKEN. The OAuth client must be type "Desktop app" (loopback redirect).
"""
import http.server, sys, urllib.parse, webbrowser
import requests

SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/business.manage"
PORT = 8765


def main(cid, secret):
    redirect = f"http://127.0.0.1:{PORT}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": SCOPES,
        "access_type": "offline", "prompt": "consent"})
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200); self.end_headers()
            self.wfile.write(b"Done. You can close this tab and go back to the terminal.")
        def log_message(self, *a): pass

    print("Open this link and approve:\n" + url)
    try: webbrowser.open(url)
    except Exception: pass
    srv = http.server.HTTPServer(("127.0.0.1", PORT), H)
    while "code" not in got and "error" not in got:
        srv.handle_request()
    if "error" in got: sys.exit(f"Google said: {got['error']}")
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "code": got["code"][0], "client_id": cid, "client_secret": secret,
        "redirect_uri": redirect, "grant_type": "authorization_code"}, timeout=60)
    j = r.json()
    if "refresh_token" not in j: sys.exit(f"No refresh token: {j}")
    print("\nYT_REFRESH_TOKEN =", j["refresh_token"])


if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
