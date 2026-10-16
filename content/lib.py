"""Helpers that turn short content entries into full specs for build.py (carousels) and
motion/reels.py (Reels). Used by content/build_nov_dec.py.

Rules baked in: Instagram caption = body + phone + hashtags; the YouTube description repeats the
body with the phone and website; the Google text has no phone number and no hashtags.
"""
import re

PHONE = "📞 8888567870 | Free demo"
GBP_TAIL = "Free demo साठी call करा किंवा bizflowindia.cloud ला भेट द्या."
YT_TAIL = "📞 8888567870 वर free demo बुक करा\n🌐 bizflowindia.cloud"


def plain(s):
    return s.replace("[[", "").replace("]]", "")


def tagline(tags, kind):
    base = ["#bizflow", "#bizflowindia"]
    end = ["#marathireels", "#sangamner"] if kind == "reel" else ["#marathibusiness", "#sangamner"]
    return " ".join(base + ["#" + t.lstrip("#") for t in tags] + end)


def yt_tags(tags):
    return [t.lstrip("#") for t in tags][:4] + ["bizflow"]


def yt_hashtags(tags):
    return " ".join(["#" + t.lstrip("#") for t in tags[:3]] + ["#bizflow", "#marathi", "#shorts"])


def yt_title(t):
    return t if "#shorts" in t.lower() else f"{t} | BizFlow #shorts"


# ---------- Reels ----------
def reel(id, title, body, tags, scenes):
    out = []
    for s in scenes:
        k = s[0]
        if k == "B":      # big, dark
            out.append({"kind": "big", "theme": "dark", "tag": s[1], "text": s[2], "dur": 2.6})
        elif k == "A":    # big, accent
            out.append({"kind": "big", "theme": "accent", "tag": s[1], "text": s[2], "dur": 2.8})
        elif k == "M":    # mid, light, emoji
            out.append({"kind": "mid", "theme": "light", "emoji": s[1], "text": s[2], "dur": 2.6})
        elif k == "CH":   # chat: (who, text, me)
            out.append({"kind": "chat", "theme": "dark", "tag": s[1],
                        "bubbles": [{"who": w, "text": t, **({"me": True} if me else {})} for w, t, me in s[2]], "dur": 3.4})
        elif k == "C":
            out.append({"kind": "cta", "theme": "dark", "text": s[1], "dur": 3.0})
        else:
            raise ValueError(k)
    return {
        "id": id, "scenes": out,
        "caption": f"{body}\n\n{PHONE}\n\n{tagline(tags, 'reel')}",
        "youtube_title": yt_title(title), "youtube_tags": yt_tags(tags),
        "youtube_description": f"{body}\n\n{YT_TAIL}\n\n{yt_hashtags(tags)}",
    }


# ---------- Carousels ----------
def cover(kicker, title, body, theme="dark"):
    return {"kind": "cover", "theme": theme, "kicker": kicker, "title": title, "body": body}


def lst(kicker, title, items, theme="light"):
    return {"kind": "list", "theme": theme, "kicker": kicker, "title": title, "items": items}


def chips(kicker, title, body, chips_, price=None, theme="dark"):
    d = {"kind": "chips", "theme": theme, "kicker": kicker, "title": title, "body": body, "chips": chips_}
    if price:
        d["price"] = price
    return d


def chat(kicker, title, bubbles, theme="dark"):
    return {"kind": "chat", "theme": theme, "kicker": kicker, "title": title,
            "bubbles": [{"text": t, "time": tm} for t, tm in bubbles]}


def point(num, title, body, theme="light"):
    return {"kind": "point", "theme": theme, "num": num, "title": title, "body": body}


def cta(kicker, title, theme="accent"):
    return {"kind": "cta", "theme": theme, "kicker": kicker, "title": title, "body": "Call करा किंवा DEMO comment करा."}


def numbered(items):
    nums = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
    return "\n".join(f"{nums[i]} {plain(t)}" for i, t in enumerate(items))


def carousel(id, title, intro, outro, tags, slides, body=None, gbp=None):
    """If a list slide is present its items become the numbered list in the caption and Google text."""
    items = next((s["items"] for s in slides if s["kind"] == "list"), None)
    cap = body if body is not None else f"{intro}\n\n{numbered(items)}\n\n{outro}" if items else f"{intro}\n\n{outro}"
    g = gbp if gbp is not None else (f"{intro}\n\n{numbered(items)}" if items else intro)
    g = re.sub(r"#\w+", "", g).strip()
    return {
        "id": id, "slides": slides,
        "caption": f"{cap}\n\n{PHONE}\n\n{tagline(tags, 'car')}",
        "youtube_title": yt_title(title), "youtube_tags": yt_tags(tags),
        "youtube_description": f"{cap}\n\n{YT_TAIL}\n\n{yt_hashtags(tags)}",
        "gbp_text": f"{g}\n\n{GBP_TAIL}",
    }
