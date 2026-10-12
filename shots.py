"""Screenshot the customer websites listed in CUSTOMERS.md (desktop + phone).

Usage: python3 shots.py                  # every site in the Websites table
       python3 shots.py shyamoils.in ... # just these
Outputs photos/sites/<domain>-desktop.jpg and photos/sites/<domain>-phone.jpg,
and prints which sites failed to load. Look at every image before using it in a
post: no photos of children (crop school and college sites), nothing broken.
"""
import re, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "photos" / "sites"
SKIP = {"storiesby9.com", "bodhidharmasociety.org"}  # flagged as having problems

VIEWS = {
    "desktop": dict(viewport={"width": 1440, "height": 900}, device_scale_factor=1),
    "phone": dict(viewport={"width": 390, "height": 844}, device_scale_factor=3,
                  is_mobile=True, has_touch=True),
}


def site_domains():
    text = (ROOT / "CUSTOMERS.md").read_text()
    table = text.split("## Websites", 1)[1].split("\n## ", 1)[0]
    return [d for d in re.findall(r"^\|[^|]+\| ([a-z0-9.-]+\.[a-z]+) \|", table, re.M)
            if d not in SKIP]


def main():
    domains = sys.argv[1:] or site_domains()
    OUT.mkdir(parents=True, exist_ok=True)
    failed = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for d in domains:
            url = d if "://" in d else f"https://{d}"
            name = re.sub(r"^\w+://(www\.)?", "", url).strip("/").replace("/", "_")
            for view, opts in VIEWS.items():
                page = browser.new_page(**opts)
                try:
                    page.goto(url, wait_until="networkidle", timeout=45000)
                    page.wait_for_timeout(1500)  # let sliders and fonts settle
                    page.screenshot(path=str(OUT / f"{name}-{view}.jpg"), type="jpeg", quality=85)
                    print("ok  ", name, view)
                except Exception as e:
                    failed.append(f"{name} ({view}): {str(e).splitlines()[0]}")
                finally:
                    page.close()
        browser.close()
    if failed:
        print("\nFailed:\n  " + "\n  ".join(failed))


if __name__ == "__main__":
    main()
