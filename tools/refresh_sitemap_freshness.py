"""Keep docs/sitemap.xml honest - freshness + dead-URL self-heal.

Ported to LexingtonGays 2026-09-08 from tulsagays/tools/refresh_sitemap_freshness.py,
which had no counterpart in this repo's tools/ directory (30 scripts, none of them
this one).

The defect it closes, measured on this repo the day of the port:
  docs/sitemap.xml said the homepage was last modified 2026-07-10 with
  changefreq weekly, while docs/index.html had been written 2026-09-07 and was
  serving the week of September 7-13. Every lastmod in the file was 2026-04-30,
  2026-05-06, 2026-05-27 or 2026-07-10; nothing had been stamped since July. A
  weekly page whose lastmod is two months old teaches crawlers to stop
  recrawling the one page on the site that actually changes every week.

It also prunes any <url> block whose local file no longer exists, so a dead link
cannot quietly sit in the sitemap eroding crawl trust.

Run weekly (wired into run_weekly.py's post phase). Idempotent.
Standalone: `python tools/refresh_sitemap_freshness.py [--check]`
  --check : exit 1 (no writes) if any sitemap URL maps to a missing local file.
            Use as a build guard so a dead URL can never silently re-enter.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date, timedelta
from urllib.parse import urlsplit

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")
SITEMAP = os.path.join(DOCS, "sitemap.xml")

# Host from config.SITE_URL, never hardcoded: LexingtonGays' docs/CNAME is the
# bare domain while TulsaGays' is www, and a hardcoded host here would silently
# stamp nothing (the <loc> would not match) on whichever city disagreed.
sys.path.insert(0, REPO)
import config  # noqa: E402
BASE = (getattr(config, "SITE_URL", "") or "").rstrip("/")

# Pages that genuinely change every week - stamp these to the current Monday.
# Every path here must be declared changefreq weekly in docs/sitemap.xml, or the
# sitemap would promise a refresh cadence the page does not keep.
WEEKLY_PATHS = {"/", "/archive.html", "/directory.html", "/blog/"}


def _monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _url_to_localfile(loc: str) -> str | None:
    """Map a sitemap <loc> to the local file that serves it, or None if it's a
    directory-style URL (…/ or …/dir/) that resolves to an index.html we can't
    always assume. Returns a path to test for existence, or None to skip the check."""
    path = urlsplit(loc).path
    if path.endswith("/"):
        # "/" -> index.html ; "/blog/" -> blog/index.html
        candidate = os.path.join(DOCS, path.strip("/"), "index.html")
        return candidate
    return os.path.join(DOCS, path.lstrip("/"))


def _split_url_blocks(xml: str):
    """Yield (full_block, loc) for each <url>...</url> in document order."""
    for m in re.finditer(r"<url>.*?</url>", xml, flags=re.DOTALL):
        block = m.group(0)
        loc_m = re.search(r"<loc>([^<]+)</loc>", block)
        yield block, (loc_m.group(1).strip() if loc_m else "")


def _missing_urls(xml: str) -> list[str]:
    missing = []
    for _block, loc in _split_url_blocks(xml):
        local = _url_to_localfile(loc)
        if local is None:
            continue
        if not os.path.exists(local):
            missing.append(loc)
    return missing


def main(argv: list[str]) -> int:
    with open(SITEMAP, encoding="utf-8") as f:
        xml = f.read()

    if "--check" in argv:
        missing = _missing_urls(xml)
        if missing:
            print("[sitemap-check] DEAD URLS (no local file):")
            for u in missing:
                print("   x", u)
            return 1
        print(f"[sitemap-check] OK, every sitemap URL resolves to a real file "
              f"({sum(1 for _ in _split_url_blocks(xml))} urls)")
        return 0

    today = date.today()
    mon = _monday(today).isoformat()

    # 1) Prune dead URLs (self-heal).
    pruned = []
    for block, loc in list(_split_url_blocks(xml)):
        local = _url_to_localfile(loc)
        if local is not None and not os.path.exists(local):
            xml = xml.replace(block, "", 1)
            pruned.append(loc)
    # collapse the blank lines a removed block leaves behind
    xml = re.sub(r"\n[ \t]*\n[ \t]*\n", "\n\n", xml)

    # 2) Freshness-stamp the weekly pages to this week's Monday.
    stamped = []
    for path in WEEKLY_PATHS:
        loc = f"{BASE}{path}"
        pat = re.compile(
            r"(<loc>" + re.escape(loc) + r"</loc>\s*<lastmod>)([^<]+)(</lastmod>)"
        )
        if pat.search(xml):
            xml = pat.sub(lambda m: m.group(1) + mon + m.group(3), xml)
            stamped.append(path)

    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"[sitemap-freshness] lastmod={mon} stamped={stamped} "
          f"pruned_dead={pruned or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
