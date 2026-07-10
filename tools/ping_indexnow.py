"""Notify search engines of updated URLs via the IndexNow protocol.

IndexNow (indexnow.org) is a simple push protocol: one POST tells Bing, Yandex,
Seznam, and a growing set of engines that URLs changed, so they recrawl in hours
instead of waiting to rediscover. Bing's index feeds ChatGPT / Copilot search, so
this is a direct, fully-automatable AEO lever (no Google account, no login).

The site already hosts the key file at /<KEY>.txt (verified live). This reads the
sitemap and submits every URL. Safe to run repeatedly (idempotent on the engine
side). Called automatically at the end of the weekly refresh, and runnable by hand:

    python tools/ping_indexnow.py           # submit all sitemap URLs
    python tools/ping_indexnow.py --url https://lexingtongays.com/   # one URL
    python tools/ping_indexnow.py --selftest # no network; proves payload build
"""
import json
import os
import re
import sys
import urllib.request

HOST = "lexingtongays.com"
KEY = "679b407811f8482d867cf9b750be34ea"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
_HERE = os.path.dirname(os.path.abspath(__file__))
SITEMAP = os.path.join(_HERE, "..", "docs", "sitemap.xml")


def sitemap_urls():
    with open(SITEMAP, encoding="utf-8") as f:
        return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", f.read())


def build_payload(urls):
    return {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": [u for u in urls if u.startswith(f"https://{HOST}")],
    }


def submit(urls):
    payload = build_payload(urls)
    if not payload["urlList"]:
        return {"ok": False, "status": None, "message": "no eligible URLs", "count": 0}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.getcode()
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:
        return {"ok": False, "status": None, "message": str(e), "count": len(payload["urlList"])}
    # IndexNow: 200 = accepted, 202 = accepted/pending validation. Both are success.
    ok = code in (200, 202)
    return {"ok": ok, "status": code, "message": "accepted" if ok else f"HTTP {code}",
            "count": len(payload["urlList"])}


def main(argv):
    if "--selftest" in argv:
        p = build_payload(["https://lexingtongays.com/", "https://evil.example/x",
                            "https://lexingtongays.com/blog/gay-bars-lexington.html"])
        assert p["urlList"] == ["https://lexingtongays.com/",
                                "https://lexingtongays.com/blog/gay-bars-lexington.html"], p
        assert p["key"] == KEY and p["host"] == HOST
        print("selftest OK: off-host URLs filtered, payload well-formed")
        return 0
    if "--url" in argv:
        urls = [argv[argv.index("--url") + 1]]
    else:
        urls = sitemap_urls()
    res = submit(urls)
    print(f"IndexNow: submitted {res['count']} URLs -> status={res['status']} ({res['message']})")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
