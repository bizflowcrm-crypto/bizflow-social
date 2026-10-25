"""Accounts (Instagram pages, YouTube channels, Google locations) the publisher manages.

publisher/accounts.json lists the account names (no secrets). Each queue entry has an `account` (default: the
`default` one). Credentials come from the environment:

- ACCOUNTS_SECRETS: one GitHub secret holding JSON like
    {"pos": {"ig_user_id": "1784...", "ig_token": "EAAB...", "yt_client_id": "...", "yt_client_secret": "...",
             "yt_refresh_token": "...", "gbp_location": "accounts/1/locations/2"}}
  Keys are optional; an account only posts to the networks it has keys for.
- The older single-account variables (IG_USER_ID, IG_ACCESS_TOKEN, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN,
  GBP_LOCATION) still work and belong to the default account (ACCOUNTS_SECRETS can override them).
"""
import json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "publisher/accounts.json"
KEYS = {"ig_user_id": "IG_USER_ID", "ig_token": "IG_ACCESS_TOKEN", "yt_client_id": "YT_CLIENT_ID",
        "yt_client_secret": "YT_CLIENT_SECRET", "yt_refresh_token": "YT_REFRESH_TOKEN", "gbp_location": "GBP_LOCATION"}
NEEDS = {"instagram": ["ig_user_id", "ig_token"], "youtube": ["yt_client_id", "yt_client_secret", "yt_refresh_token"],
         "gmb": ["yt_client_id", "yt_client_secret", "yt_refresh_token", "gbp_location"]}


def config():
    return json.loads(FILE.read_text())


def names():
    return list(config()["accounts"])


def default():
    return config()["default"]


def label(name):
    return config()["accounts"].get(name, {}).get("label", name)


def of(entry):
    return entry.get("account") or default()


def _secrets():
    raw = os.environ.get("ACCOUNTS_SECRETS", "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise SystemExit(f"ACCOUNTS_SECRETS is not valid JSON ({e}). Fix the GitHub secret; see publisher/SETUP.md, 'More accounts'.")
    return data if isinstance(data, dict) else {}


def creds(name):
    """Credentials for one account as {ig_user_id: ..., ig_token: ...}; missing ones are left out."""
    out = {}
    if name == default():
        out = {k: os.environ[v] for k, v in KEYS.items() if os.environ.get(v)}
    out.update({k: v for k, v in _secrets().get(name, {}).items() if k in KEYS and v})
    return out


def missing(name, network):
    c = creds(name)
    return [k for k in NEEDS[network] if not c.get(k)]
