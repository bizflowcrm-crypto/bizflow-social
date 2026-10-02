"""BizFlow brand kit shared by build.py and reel.py: palette, real logo, photo embedding."""
import base64, pathlib

ROOT = pathlib.Path(__file__).parent

# Palette sampled from the official BizFlow logo (blue on black).
VARS = ":root { --ink:#0A1230; --night:#05070F; --blue:#0A6CF0; --sky:#3D95FF; --deep:#00298D; --paper:#F2F6FF; --mint:#1FB57A; --muted:#5B6485; }"
BG_DARK = "radial-gradient(1300px 1000px at 90% -10%, #0B2A6B 0%, #05070F 62%)"
BG_ACCENT = "linear-gradient(160deg, #0A7BFF 0%, #0A55DA 55%, #00298D 100%)"

def data_uri(path):
    p = ROOT / path
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}[p.suffix.lower().lstrip(".")]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

_cache = {}
def logo(theme):
    """Full logo lockup: blue on light slides, white on dark and blue (accent) slides."""
    f = "assets/logo-blue.png" if theme == "light" else "assets/logo-white.png"
    if f not in _cache: _cache[f] = data_uri(f)
    return f'<img class="logo" src="{_cache[f]}" alt="BizFlow">'
