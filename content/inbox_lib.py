"""Parse and check the plain-text content format that any chatbot can write (see content/README.md
and content/PROMPT.md), and expand it into the specs build.py and motion/reels.py read.

Format sketch:
    account: pos                 (file header: which account posts this file, default: the main one)
    start: 2027-01-05            (file header: first posting day, optional slot times)
    === reel nd-reel-slug
    title: ...
    tags: tableflow, kot
    caption:
    text...
    scenes:
    big | tag | line one // line [[highlight]]
    === carousel nd-car-slug
    ...
    slides:
    cover | kicker | Title // [[hl]] | body
"""
import datetime as dt, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import reel, carousel, cover, lst, chips, chat, point, cta

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYS = ("title", "tags", "caption", "intro", "outro", "google", "scenes", "slides")
HEADER_KEYS = ("account", "start", "reel_time", "carousel_time", "google_time")
SCENE_COLS = {"big": 3, "mid": 3, "accent": 3, "cta": 2}
SLIDE_COLS = {"cover": 4, "list": 4, "chips": (5, 6), "point": 4, "chat": 4, "cta": 3}
BANNED = [r"guarantee", r"100\s?%", r"\bno\.?\s?1\b", r"number one", r"best in", r"cheapest", r"lowest price",
          r"double your", r"triple your", r"risk[- ]free", r"lifetime", r"unlimited"]
DESCENDER = re.compile(r"[A-Za-z]*[pygqj][A-Za-z]*")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def br(t):
    return re.sub(r"\s*//\s*", "\n", t.strip())


# ---------- parsing ----------
def parse(text):
    header, posts, cur, key, errors = {}, [], None, None, []
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if re.match(r"^\s*#(\s|$)", line):
            continue
        m = re.match(r"^===\s*(reel|carousel)\s+(\S+)\s*$", line, re.I)
        if m:
            cur = {"kind": m.group(1).lower(), "id": m.group(2), "line": no, "f": {}, "rows": {"scenes": [], "slides": []}}
            posts.append(cur); key = None
            continue
        if line.startswith("==="):
            errors.append((no, "Heading must look like '=== reel some-id' or '=== carousel some-id'."))
            continue
        if cur is None:
            m = re.match(r"^(\w+)\s*:\s*(.*)$", line)
            if m and m.group(1).lower() in HEADER_KEYS:
                header[m.group(1).lower()] = (no, m.group(2).strip())
            elif line.strip():
                errors.append((no, "Text before the first '===' heading. File header lines are account:, start:, reel_time:, carousel_time:, google_time:."))
            continue
        m = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        if m and m.group(1).lower() in KEYS:
            key = m.group(1).lower()
            cur["f"].setdefault(key, [no, []])
            if m.group(2).strip():
                cur["f"][key][1].append(m.group(2).strip())
            continue
        if key is None:
            if line.strip():
                errors.append((no, f"Unexpected text under '{cur['id']}'. Start with a field such as 'title:'."))
            continue
        if key in ("scenes", "slides"):
            if line.strip():
                cur["rows"][key].append((no, [c.strip() for c in line.split("|")]))
        else:
            cur["f"][key][1].append(line)
    for p in posts:
        for k, v in p["f"].items():
            v[1] = "\n".join(v[1]).strip()
    return header, posts, errors


# ---------- checking ----------
def customer_names():
    p = ROOT / "CUSTOMERS.md"
    if not p.exists():
        return set()
    names, agreed, section = set(), "", ""
    for ln in p.read_text().splitlines():
        if ln.startswith("## "):
            section = ln
        if "Agreed to be featured" in section and ln.startswith("- "):
            agreed += ln.lower()
        if ln.startswith("| ") and "---" not in ln and not ln.startswith("| Customer"):
            first = ln.split("|")[1].strip()
            for part in re.split(r"[()/,]", first):
                part = part.strip()
                if len(part) >= 5 and "." not in part:
                    names.add(part)
        if ln.startswith("Also on the sheet"):
            tail = ln.split(":", 1)[-1]
            for part in re.split(r"[(),]", tail):
                part = part.strip(" .")
                if len(part) >= 5 and "." not in part:
                    names.add(part)
    return {n for n in names if n.lower() not in agreed}


def existing_ids(skip_specs=()):
    """Ids already used in the queue and in posts/*.json. `skip_specs` are spec file names to ignore, so the spec
    files written from the very file being processed do not count as duplicates of it."""
    ids = set()
    q = ROOT / "publisher/queue.json"
    if q.exists():
        ids |= {e["id"].split("~r")[0] for e in json.loads(q.read_text())}
    for f in (ROOT / "posts").glob("*.json"):
        if f.name in skip_specs:
            continue
        try:
            d = json.loads(f.read_text())
        except ValueError:
            continue
        ids |= {x["id"] for k in ("posts", "reels") for x in d.get(k, [])}
    return ids


def check(header, posts, parse_errors, taken=None, names=None):
    errs = [(n, m) for n, m in parse_errors]
    warns = []
    taken = existing_ids() if taken is None else taken
    names = customer_names() if names is None else names
    seen = set()

    def E(no, msg): errs.append((no, msg))
    def W(no, msg): warns.append((no, msg))

    for k, (no, v) in header.items():
        if k == "start":
            try:
                d = dt.date.fromisoformat(v)
                if d <= dt.date.today():
                    W(no, f"start: {v} is not in the future; posts due in the past are skipped or posted late.")
            except ValueError:
                E(no, f"start: must be a date like 2027-01-05, got '{v}'.")
        elif k == "account":
            known = json.loads((ROOT / "publisher/accounts.json").read_text())["accounts"]
            if v not in known:
                E(no, f"account: '{v}' is not in publisher/accounts.json (known: {', '.join(known)}).")
        elif not re.fullmatch(r"\d{2}:\d{2}", v):
            E(no, f"{k}: must be a time like 12:30, got '{v}'.")
    if not posts:
        E(1, "No posts found. Each post starts with '=== reel some-id' or '=== carousel some-id'.")
    for p in posts:
        L, i, f = p["line"], p["id"], p["f"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{5,59}", i):
            E(L, f"id '{i}': use 6 to 60 lowercase letters, digits and hyphens.")
        if i in seen or i in taken:
            E(L, f"id '{i}' is already used. Pick a new one.")
        seen.add(i)
        need = ["title", "tags", "caption", "scenes"] if p["kind"] == "reel" else ["title", "tags", "slides"]
        if p["kind"] == "carousel" and "caption" not in f and not ("intro" in f and "outro" in f):
            E(L, f"{i}: a carousel needs 'intro:' and 'outro:' (or a full 'caption:').")
        for k in need:
            if k not in f or not f[k][1] and k not in ("scenes", "slides"):
                E(L, f"{i}: missing '{k}:'.")
        if "title" in f and len(f["title"][1]) > 80:
            E(f["title"][0], f"{i}: title is {len(f['title'][1])} characters, the limit is 80.")
        tags = [t.strip().lstrip("#") for t in f.get("tags", [0, ""])[1].split(",") if t.strip()]
        if "tags" in f and not 2 <= len(tags) <= 6:
            E(f["tags"][0], f"{i}: give 2 to 6 tags, comma separated.")
        for t in tags:
            if not re.fullmatch(r"[a-z0-9]+", t):
                E(f["tags"][0], f"tag '{t}': lowercase letters and digits only, no spaces.")
        # text rules on every free-text field
        texts = [(k, f[k][0], f[k][1]) for k in ("title", "caption", "intro", "outro", "google") if k in f]
        for k, no, t in texts:
            if "#" in t:
                E(no, f"{i} {k}: no hashtags, they are added automatically.")
            if re.search(r"\d[\d\s-]{7,}\d", t):
                E(no, f"{i} {k}: no phone numbers, the call to action adds it.")
            if re.search(r"https?://|www\.", t):
                E(no, f"{i} {k}: no links.")
        alltext = "\n".join(t for _, _, t in texts) + "\n" + "\n".join(
            c for _, cols in p["rows"]["scenes"] + p["rows"]["slides"] for c in cols)
        for pat in BANNED:
            if re.search(pat, alltext, re.I):
                E(L, f"{i}: avoid the claim matching '{pat}'. We never promise results.")
        for n in names:
            if re.search(re.escape(n), alltext, re.I):
                E(L, f"{i}: names the customer '{n}'. Customers are named only after they agree (see CUSTOMERS.md).")
        for m in re.finditer(r"₹\s?([\d,]+)", alltext):
            if m.group(1) != "399":
                W(L, f"{i}: mentions ₹{m.group(1)}. Only ₹399 is a real BizFlow price; fine if it is an example sum.")
        if re.search(r"\d\s?%", alltext):
            W(L, f"{i}: contains a percentage. Fine for GST rates, never for results or savings.")
        if p["kind"] == "reel":
            rows = p["rows"]["scenes"]
            if not 4 <= len(rows) <= 7:
                E(L, f"{i}: a Reel needs 4 to 7 scenes, found {len(rows)}.")
            for no, cols in rows:
                kind = cols[0].lower()
                if kind not in SCENE_COLS:
                    E(no, f"scene type '{cols[0]}' must be one of: big, mid, accent, cta.")
                elif len(cols) != SCENE_COLS[kind]:
                    E(no, f"'{kind}' scene needs {SCENE_COLS[kind]} columns separated by |, found {len(cols)}.")
                else:
                    t = cols[-1]
                    if not t:
                        E(no, "scene text is empty.")
                    for ln in br(t).split("\n"):
                        if len(re.sub(r"\[\[|\]\]", "", ln)) > 32:
                            W(no, f"scene line '{ln[:30]}...' is long; keep lines under 32 characters so it fits.")
            if rows and rows[0][1][0].lower() != "big":
                E(rows[0][0], "the first scene should be 'big' (the hook).")
            if rows and rows[-1][1][0].lower() != "cta":
                E(rows[-1][0], "the last scene must be 'cta'.")
        else:
            rows = p["rows"]["slides"]
            if not 3 <= len(rows) <= 10:
                E(L, f"{i}: a carousel needs 3 to 10 slides, found {len(rows)}.")
            for idx, (no, cols) in enumerate(rows):
                kind = cols[0].lower()
                want = SLIDE_COLS.get(kind)
                if want is None:
                    E(no, f"slide type '{cols[0]}' must be one of: cover, list, chips, point, chat, cta.")
                    continue
                ok = len(cols) in (want if isinstance(want, tuple) else (want,))
                if not ok:
                    E(no, f"'{kind}' slide needs {want} columns separated by |, found {len(cols)}.")
                    continue
                if kind == "list":
                    items = [x.strip() for x in cols[3].split(";") if x.strip()]
                    if not 3 <= len(items) <= 6:
                        E(no, f"a list slide needs 3 to 6 items separated by ;, found {len(items)}.")
                    for it in items:
                        if len(re.sub(r"\[\[|\]\]", "", it)) > 55:
                            W(no, f"list item '{it[:30]}...' is long; it will wrap to two lines.")
                title = {"cover": 2, "list": 2, "chips": 2, "point": 2, "chat": 2, "cta": 2}[kind]
                lines = br(cols[title]).split("\n")
                for a, b in zip(lines, lines[1:]):
                    if DESCENDER.search(re.sub(r"[^A-Za-z ]", " ", a)) and DEVANAGARI.search(b):
                        E(no, f"title line '{a}' has a Latin letter with a tail (p, y, g, q, j) directly above a Marathi line, "
                              "which clips. Move that word to the last line or write it in Marathi.")
            if rows and not any(r[1][0].lower() == "list" for r in rows) and "caption" not in f:
                E(L, f"{i}: no 'list' slide, so the caption would have only the intro and question. "
                     "Add a full 'caption:' (the tips or points written out), or include a list slide.")
            if rows and rows[0][1][0].lower() != "cover":
                E(rows[0][0], "the first slide must be 'cover'.")
            if rows and rows[-1][1][0].lower() != "cta":
                E(rows[-1][0], "the last slide must be 'cta'.")
    return errs, warns


# ---------- expanding ----------
def expand(posts):
    reels, cars = [], []
    for p in posts:
        f = p["f"]
        tags = [t.strip().lstrip("#") for t in f["tags"][1].split(",") if t.strip()]
        if p["kind"] == "reel":
            sc = []
            for _, c in p["rows"]["scenes"]:
                k = c[0].lower()
                if k == "big": sc.append(("B", c[1], br(c[2])))
                elif k == "mid": sc.append(("M", c[1], br(c[2])))
                elif k == "accent": sc.append(("A", c[1], br(c[2])))
                else: sc.append(("C", br(c[-1])))
            reels.append(reel(p["id"], f["title"][1], f["caption"][1], tags, sc))
            continue
        sl = []
        for _, c in p["rows"]["slides"]:
            k = c[0].lower()
            if k == "cover": sl.append(cover(c[1], br(c[2]), br(c[3])))
            elif k == "list": sl.append(lst(c[1], br(c[2]), [x.strip() for x in c[3].split(";") if x.strip()]))
            elif k == "chips": sl.append(chips(c[1], br(c[2]), br(c[3]), [x.strip() for x in c[4].split(",") if x.strip()],
                                               c[5] if len(c) > 5 and c[5] else None))
            elif k == "point": sl.append(point(c[1], br(c[2]), br(c[3])))
            elif k == "chat":
                bub = []
                for b in c[3].split(";;"):
                    t, _, tm = b.partition("@")
                    bub.append((t.strip(), tm.strip() or "10:30"))
                sl.append(chat(c[1], br(c[2]), bub))
            else: sl.append(cta(c[1], br(c[2])))
        body = f["caption"][1] if "caption" in f else None
        cars.append(carousel(p["id"], f["title"][1], f.get("intro", [0, ""])[1], f.get("outro", [0, ""])[1], tags, sl,
                             body=body, gbp=f["google"][1] if "google" in f else None))
    return reels, cars
