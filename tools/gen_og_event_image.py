"""Generate the branded 1200x630 Open Graph image used for event share previews.

Output: docs/images/og-event.png   (one-time / idempotent asset)

WHY THIS FILE EXISTS (2026-09-08)
tools/gen_website_html.py already emits, on every one of the docs/e/*.html share
pages and on every Event JSON-LD node:

    <meta property="og:image" content="<SITE_URL>/images/og-event.png">

but that file did not exist. docs/images/ held only flamingo.png (816 bytes), so
every shared LexingtonGays event link rendered with a broken preview image. The
reference was already being generated; only the asset was missing. TulsaGays has
the equivalent script and a real asset, and this repo's tools/ directory had no
copy, so this is sync drift rather than a design choice.

Ported from C:\\Users\\willi\\tulsagays\\tools\\gen_og_event_image.py and restyled
to the Lexington Gays brand recorded in DESIGN_STANDARD.md (verified 2026-09-08):
  Background #0a0a0a, Neon Pink #FF1493, White #FFFFFF, Light Gray #CCCCCC,
  Poiret One for the wordmark.
Font resolution mirrors tools/gen_blog_og_images.py::_font (project fonts/ dir
first, then Windows fonts, then a fallback chain) so this never dies on a
missing typeface the way a bare truetype() call would.

Run standalone:  python tools/gen_og_event_image.py
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow is not installed.  pip install Pillow")
    sys.exit(1)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(_ROOT, "fonts")
OUT_PATH = os.path.join(_ROOT, "docs", "images", "og-event.png")

# 1200x630 is the size a summary_large_image / og card expects.
W, H = 1200, 630

# Lexington Gays palette (DESIGN_STANDARD.md).
BG = (10, 10, 10)             # #0a0a0a
PINK = (255, 20, 147)         # #FF1493 Neon Pink
WHITE = (255, 255, 255)
LIGHT_GRAY = (204, 204, 204)  # #CCCCCC
MID_BAND = (17, 10, 15)       # #110a0f, the subtle depth band gen_blog_og_images uses

PRIDE = [(228, 3, 3), (255, 140, 0), (255, 237, 0),
         (0, 128, 38), (0, 77, 255), (117, 7, 135)]


def _font(name, size):
    """Load a font by logical name. Mirrors tools/gen_blog_og_images.py::_font."""
    project_map = {
        "poiret": "PoiretOne-Regular.ttf",
        "cinzel": "Cinzel.ttf",
        "playfair": "PlayfairDisplay.ttf",
    }
    if name.lower() in project_map:
        path = os.path.join(FONTS_DIR, project_map[name.lower()])
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    win_fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    system_map = {
        "segoe": "segoeui.ttf",
        "segoe-light": "segoeuil.ttf",
        "segoe-semi": "seguisb.ttf",
        "arial": "arial.ttf",
    }
    path = os.path.join(win_fonts, system_map.get(name.lower(), f"{name}.ttf"))
    if os.path.exists(path):
        return ImageFont.truetype(path, size)

    for fallback in ("segoeuil.ttf", "segoeui.ttf", "arial.ttf"):
        fb = os.path.join(win_fonts, fallback)
        if os.path.exists(fb):
            return ImageFont.truetype(fb, size)
    return ImageFont.load_default()


def _center(draw, text, fnt, y, fill, tracking=0):
    """Draw text horizontally centred at baseline-ish y, with optional tracking."""
    if tracking:
        widths = [draw.textbbox((0, 0), ch, font=fnt)[2] for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = (W - total) / 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + tracking
    else:
        bb = draw.textbbox((0, 0), text, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), text, font=fnt, fill=fill)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Subtle mid-band for depth (same device as the blog OG banners).
    d.rectangle([(0, 232), (W, 398)], fill=MID_BAND)

    # Top and bottom pink rules.
    d.rectangle([(0, 0), (W, 5)], fill=PINK)
    d.rectangle([(0, H - 6), (W, H)], fill=PINK)

    # Geometric deco frame, one thick + one hairline (Modern Geometric Deco).
    d.rectangle([34, 34, W - 35, H - 35], outline=PINK, width=3)
    d.rectangle([48, 48, W - 49, H - 49], outline=(60, 20, 40), width=1)

    # Corner ticks.
    for cx, cy in ((48, 48), (W - 49, 48), (48, H - 49), (W - 49, H - 49)):
        sx = 1 if cx < W / 2 else -1
        sy = 1 if cy < H / 2 else -1
        d.line([(cx, cy), (cx + sx * 26, cy)], fill=PINK, width=3)
        d.line([(cx, cy), (cx, cy + sy * 26)], fill=PINK, width=3)

    # Eyebrow.
    _center(d, "THE LGBTQ+ EVENT GUIDE", _font("segoe-semi", 26), 158,
            LIGHT_GRAY, tracking=8)

    # Wordmark: LEXINGTON white, GAYS pink, per DESIGN_STANDARD.md.
    wm = _font("poiret", 122)
    left, right = "LEXINGTON ", "GAYS"
    lb = d.textbbox((0, 0), left, font=wm)
    rb = d.textbbox((0, 0), right, font=wm)
    total = (lb[2] - lb[0]) + (rb[2] - rb[0])
    x = (W - total) / 2
    d.text((x - lb[0], 210), left, font=wm, fill=WHITE)
    d.text((x + (lb[2] - lb[0]) - rb[0], 210), right, font=wm, fill=PINK)

    # Pink underline.
    d.rectangle([(W / 2 - 210, 386), (W / 2 + 210, 392)], fill=PINK)

    # Tagline. Deliberately a FREQUENCY claim, not a coverage claim: the site
    # does not know it has every event, so it does not say so here either.
    _center(d, "Queer Lexington, week by week.", _font("segoe-light", 36), 424,
            LIGHT_GRAY)

    # Pride accent bar.
    bar_w, bar_h, by = 360, 10, 508
    seg = bar_w / len(PRIDE)
    bx = (W - bar_w) / 2
    for i, col in enumerate(PRIDE):
        d.rectangle([(bx + i * seg, by), (bx + (i + 1) * seg, by + bar_h)], fill=col)

    # Domain. Bare host, matching docs/CNAME.
    _center(d, "lexingtongays.com", _font("segoe", 27), 546, PINK, tracking=4)
    return img


def run():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img = build()
    img.save(OUT_PATH, "PNG")
    size = os.path.getsize(OUT_PATH)
    print(f"wrote {OUT_PATH} {img.size} {size} bytes")
    if img.size != (W, H):
        raise SystemExit(f"ERROR: expected {(W, H)}, got {img.size}")
    if size < 5000:
        raise SystemExit(f"ERROR: {size} bytes looks empty; refusing to call this done")
    return OUT_PATH


if __name__ == "__main__":
    run()
