"""
Phase 5 finisher: capture Lexington Gays FB Page Access Token + Instagram Business ID.

Prerequisites (William must complete first):
  1. Create FB Page "Lexington Gays" at https://www.facebook.com/pages/create
  2. Switch IG @lexingtongays to a Business account, link to that FB Page
  3. **CRITICAL** Switch FB Page from New Pages Experience to Classic:
       facebook.com/profile.php?id=61589147379825
       Left sidebar: Settings -> See all settings -> General -> "Switch to Classic Pages Experience"
  4. Generate a USER token at https://developers.facebook.com/tools/explorer/
     with these permissions:
         pages_show_list
         pages_manage_posts
         pages_read_engagement
         instagram_basic
         instagram_content_publish

Usage:
    python scripts/capture_meta_creds.py <USER_TOKEN>

    With known page ID (skip me/accounts lookup — use after Classic switch):
    python scripts/capture_meta_creds.py <USER_TOKEN> --page-id 61589147379825

What it does:
  - Queries /me/accounts to find Lexington Gays FB Page (or uses --page-id)
  - Extracts the page-scoped access token (long-lived after page exchange)
  - Extracts the linked Instagram Business Account ID
  - Writes META_ACCESS_TOKEN, META_IG_USER_ID, META_FB_PAGE_ID into .env
  - Updates meta_api_config.json
  - Verifies by smoke-testing the page token

NOTE ON NEW PAGES EXPERIENCE (NPE):
  The Lexington Gays FB page was created in 2024+ and defaults to New Pages Experience.
  NPE pages are INVISIBLE to all classic Graph API endpoints (me/accounts, direct page
  queries, all API versions v19-v25). The ONLY fix is switching to Classic Pages Experience
  in Facebook Settings. Once Classic, this script works normally.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
META_CONFIG_FILE = ROOT / "meta_api_config.json"
GRAPH_BASE = "https://graph.facebook.com/v25.0"
PAGE_NAME_HINTS = ("lexington gays", "lex gays", "gay lexington", "lexington queer")

# Known page ID — set after page is switched to Classic Experience
KNOWN_PAGE_ID = "61589147379825"


def _api_get(path: str, token: str) -> dict:
    sep = "&" if "?" in path else "?"
    url = f"{GRAPH_BASE}/{path}{sep}access_token={urllib.parse.quote(token, safe='')}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return {"_http_error": e.code, **body}


def find_lexington_page_via_accounts(user_token: str) -> dict | None:
    """Try me/accounts first. Returns page dict or None if not found (NPE or no pages)."""
    res = _api_get(
        "me/accounts?fields=id,name,access_token,instagram_business_account{id,username}&limit=50",
        user_token,
    )
    pages = res.get("data", [])
    for p in pages:
        nm = p.get("name", "").lower()
        if any(h in nm for h in PAGE_NAME_HINTS):
            return p
    return None


def find_lexington_page_direct(user_token: str, page_id: str) -> dict:
    """
    Directly query a known page ID (works only after switching to Classic Pages Experience).
    NPE pages return error code 100/33 — we surface a clear message.
    """
    res = _api_get(
        f"{page_id}?fields=id,name,access_token,instagram_business_account{{id,username}}",
        user_token,
    )
    if "error" in res:
        err = res["error"]
        code = err.get("code")
        subcode = err.get("error_subcode")
        if code == 100 and subcode == 33:
            raise SystemExit(
                "\n"
                "BLOCKED: Lexington Gays FB page is still in New Pages Experience (NPE).\n"
                "The classic Graph API cannot access NPE pages at all.\n"
                "\n"
                "FIX (takes 30 seconds on desktop):\n"
                "  1. Go to: https://www.facebook.com/profile.php?id=61589147379825\n"
                "  2. Click 'Settings' in the left sidebar\n"
                "  3. Look for 'See all settings' -> General settings\n"
                "  4. Find 'Switch to Classic Pages Experience' and click it\n"
                "  5. Confirm the switch\n"
                "  6. Re-run: python scripts/capture_meta_creds.py <FRESH_TOKEN> --page-id 61589147379825\n"
                "\n"
                f"Current token expires: 2026-05-06 22:00 UTC (5pm CT). Get a fresh one if needed.\n"
                f"Raw error: {err.get('message')}\n"
            )
        raise SystemExit(f"Graph API error on page {page_id}: {err.get('message')} (code {code}/{subcode})")
    if "access_token" not in res:
        raise SystemExit(
            f"Page {page_id} found but returned no access_token.\n"
            "Ensure the token has pages_manage_posts permission."
        )
    return res


def write_env(values: dict) -> None:
    text = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    for k, v in values.items():
        pattern = re.compile(rf"^{re.escape(k)}=.*$", re.MULTILINE)
        if pattern.search(text):
            text = pattern.sub(f"{k}={v}", text)
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += f"{k}={v}\n"
    ENV_FILE.write_text(text, encoding="utf-8")


def write_meta_config(page_id: str, ig_id: str, page_token: str) -> None:
    data = {
        "app_id": "1468075241636760",
        "app_name": "Tulsa Gays Auto Poster (shared)",
        "page_id": page_id,
        "ig_user_id": ig_id,
        "page_access_token": page_token,
        "note": "lexington gays — switched to Classic Pages Experience for Graph API access",
    }
    META_CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2

    user_token = args[0].strip()

    # Parse --page-id flag
    forced_page_id = None
    if "--page-id" in args:
        idx = args.index("--page-id")
        if idx + 1 < len(args):
            forced_page_id = args[idx + 1].strip()

    # Step 1: find page
    if forced_page_id:
        print(f"[1/4] Using forced page ID {forced_page_id} (direct query, bypassing me/accounts)...")
        page = find_lexington_page_direct(user_token, forced_page_id)
    else:
        print("[1/4] Finding Lexington Gays FB Page via me/accounts...")
        page = find_lexington_page_via_accounts(user_token)
        if page is None:
            print(
                "\n  me/accounts returned no Lexington Gays page.\n"
                "  This almost always means the page is in New Pages Experience (NPE),\n"
                "  which is INVISIBLE to the classic Graph API.\n"
                "\n"
                "  Try with the known page ID to get a diagnostic:\n"
                f"  python scripts/capture_meta_creds.py <TOKEN> --page-id {KNOWN_PAGE_ID}\n"
            )
            return 1

    page_id = page["id"]
    page_name = page["name"]
    page_token = page.get("access_token")
    ig = page.get("instagram_business_account") or {}
    ig_id = ig.get("id")
    ig_username = ig.get("username", "(none)")

    print(f"      Found: {page_name!r} (id={page_id})")
    print(f"      Instagram: @{ig_username} (id={ig_id})")

    if not page_token:
        raise SystemExit("Page returned no access_token. Token missing pages_manage_posts permission.")
    if not ig_id:
        raise SystemExit(
            "FB Page found but no Instagram Business account linked.\n"
            "Link IG @lexingtongays as a Business account to the FB Page:\n"
            "  Instagram app -> Settings -> Account type and tools -> Connect to Facebook -> select 'Lexington Gays'"
        )

    print("[2/4] Writing .env...")
    write_env({
        "META_ACCESS_TOKEN": page_token,
        "META_IG_USER_ID": ig_id,
        "META_FB_PAGE_ID": page_id,
    })

    print("[3/4] Writing meta_api_config.json...")
    write_meta_config(page_id, ig_id, page_token)

    print("[4/4] Smoke-testing page token...")
    smoke = _api_get(f"{page_id}?fields=id,name,fan_count", page_token)
    if "error" in smoke:
        raise SystemExit(f"Page token smoke test failed: {smoke['error'].get('message')}")
    print(f"      OK -> {smoke}")

    print("\nDONE. Phase 5 complete. Lexington Gays can now post to FB + IG.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
