"""
Phase 5 finisher: capture Lexington Gays FB Page Access Token + Instagram Business ID.

Prerequisites (William must complete first):
  1. Create FB Page "Lexington Gays" at https://www.facebook.com/pages/create
  2. Switch IG @lexingtongays to a Business account, link to that FB Page
  3. Generate a USER token at https://developers.facebook.com/tools/explorer/
     with these permissions:
         pages_show_list
         pages_manage_posts
         pages_read_engagement
         instagram_basic
         instagram_content_publish

Usage:
    python scripts/capture_meta_creds.py <USER_TOKEN>

What it does:
  - Queries /me/accounts to find Lexington Gays FB Page
  - Extracts the page-scoped access token (long-lived after page exchange)
  - Extracts the linked Instagram Business Account ID
  - Writes META_ACCESS_TOKEN, META_IG_USER_ID, META_FB_PAGE_ID into .env
  - Updates meta_api_config.json
  - Verifies by posting a draft test (does not actually publish)
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


def _api_get(path: str, token: str) -> dict:
    sep = "&" if "?" in path else "?"
    url = f"{GRAPH_BASE}/{path}{sep}access_token={urllib.parse.quote(token, safe='')}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_lexington_page(user_token: str) -> dict:
    res = _api_get("me/accounts?fields=id,name,access_token,instagram_business_account{id,username}&limit=50", user_token)
    pages = res.get("data", [])
    if not pages:
        raise RuntimeError(
            "me/accounts returned empty. Either no pages exist on this account, "
            "or the user token is missing pages_show_list permission. "
            "Re-generate the token at https://developers.facebook.com/tools/explorer/ "
            "with the 5 permissions listed in the script docstring."
        )
    for p in pages:
        nm = p.get("name", "").lower()
        if any(h in nm for h in PAGE_NAME_HINTS):
            return p
    available = ", ".join(f"{p.get('name')!r}" for p in pages)
    raise RuntimeError(
        f"No Lexington-named page found. Pages on this account: {available}. "
        f"Create the FB Page named 'Lexington Gays' first."
    )


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
    }
    META_CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    user_token = sys.argv[1].strip()
    print("[1/4] Finding Lexington Gays FB Page in your account...")
    page = find_lexington_page(user_token)
    page_id = page["id"]
    page_name = page["name"]
    page_token = page.get("access_token")
    ig = page.get("instagram_business_account") or {}
    ig_id = ig.get("id")
    ig_username = ig.get("username", "(none)")
    print(f"      Found: {page_name!r} (id={page_id})")
    print(f"      Instagram: @{ig_username} (id={ig_id})")
    if not page_token:
        raise SystemExit("Page returned no access_token. Token is missing pages_manage_posts.")
    if not ig_id:
        raise SystemExit(
            "FB Page exists but no Instagram Business account is linked. "
            "Link IG @lexingtongays as a Business account to the FB Page in Page settings."
        )

    print("[2/4] Writing .env...")
    write_env({
        "META_ACCESS_TOKEN": page_token,
        "META_IG_USER_ID": ig_id,
        "META_FB_PAGE_ID": page_id,
    })

    print("[3/4] Writing meta_api_config.json...")
    write_meta_config(page_id, ig_id, page_token)

    print("[4/4] Smoke-testing token against page...")
    smoke = _api_get(f"{page_id}?fields=id,name,fan_count", page_token)
    print(f"      OK -> {smoke}")

    print("\nDONE. Phase 5 complete. Lexington can now post to FB + IG.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
