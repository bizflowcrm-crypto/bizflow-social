"""BizFlow brand kit shared by build.py and reel.py: palette, real logo, photo embedding."""
import base64, pathlib

ROOT = pathlib.Path(__file__).parent

# Palette sampled from the official BizFlow logo (blue on black).
VARS = ":root { --ink:#0A1230; --night:#05070F; --blue:#0A6CF0; --sky:#3D95FF; --deep:#00298D; --paper:#F2F6FF; --mint:#1FB57A; --muted:#5B6485; }"
BG_DARK = "radial-gradient(1300px 1000px at 90% -10%, #0B2A6B 0%, #05070F 62%)"
BG_ACCENT = "linear-gradient(160deg, #0A7BFF 0%, #0A55DA 55%, #00298D 100%)"

# Poppins (OFL, assets/fonts/OFL.txt) is embedded so slides render the same on any machine,
# Devanagari included. Subsets and ranges from @fontsource/poppins.
_RANGES = {
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
    "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF",
    "devanagari": "U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+20F0,U+25CC,U+A830-A839,U+A8E0-A8FF,U+11B00-11B09",
}

def _fonts():
    css = []
    for sub, rng in _RANGES.items():
        for w in (400, 500, 600, 700, 800):
            f = ROOT / "assets" / "fonts" / f"poppins-{sub}-{w}-normal.woff2"
            b64 = base64.b64encode(f.read_bytes()).decode()
            css.append(f"@font-face{{font-family:'Poppins';font-style:normal;font-weight:{w};"
                       f"src:url(data:font/woff2;base64,{b64}) format('woff2');unicode-range:{rng};}}")
    return "\n".join(css)

def data_uri(path):
    p = ROOT / path
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}[p.suffix.lower().lstrip(".")]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

VARS = _fonts() + "\n" + VARS

_cache = {}
def logo(theme):
    """Full logo lockup: blue on light slides, white on dark and blue (accent) slides."""
    f = "assets/logo-blue.png" if theme == "light" else "assets/logo-white.png"
    if f not in _cache: _cache[f] = data_uri(f)
    return f'<img class="logo" src="{_cache[f]}" alt="BizFlow">'
