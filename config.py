"""Central configuration for Lexington Gays automation."""
import os
from datetime import datetime

# Load .env if present
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                if _v.strip():
                    # Always set from .env — overrides empty env vars (e.g. inherited shell vars)
                    os.environ[_k.strip()] = _v.strip()

# ── Paths ────────────────────────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
EVENTS_DIR = os.path.join(DATA_DIR, "events")
LOGO_PATH = os.path.join(PROJECT_DIR, "logo", "lexingtongays_logo.png")
BLOG_DIR = os.path.join(PROJECT_DIR, "blog")
SOURCES_FILE = os.path.join(DATA_DIR, "sources.json")
GROWTH_LOG = os.path.join(DATA_DIR, "growth_log.json")

# ── API Keys (set via environment variables) ─────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
META_IG_USER_ID = os.environ.get("META_IG_USER_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
TICKETMASTER_API_KEY = os.environ.get("TICKETMASTER_API_KEY", "")

# ── Event Sources ────────────────────────────────────────────────────────
# Priority: 1 = always feature, 2 = feature if good, 3 = only if special/slow week
SOURCES = {
    # Empty after scaffold. Phase 3 (source discovery) populates this.
    # See [[city-growth-playbook]] §3.2.1 for the 13-method discovery sweep.

}

# ── Posting Schedule ─────────────────────────────────────────────────────
WEEKDAY_POST_DAY = "monday"
WEEKDAY_POST_HOUR = 9  # 9am CT
WEEKEND_POST_DAY = "thursday"
WEEKEND_POST_HOUR = 17  # 5pm CT

# ── Instagram ────────────────────────────────────────────────────────────
IG_HANDLE = "lexingtongays"
IG_DISPLAY_NAME = "Lexington Gays"
IG_BIO = "Your weekly LGBTQ+ event guide for Lexington \nEvents every Mon & Thu \nHomoHotelHappyHour"

# ── Blog ─────────────────────────────────────────────────────────────────
BLOG_URL = "https://www.lexingtongays.com"
GITHUB_REPO = "lexingtongays/lexingtongays.github.io"

# ── Hashtags ─────────────────────────────────────────────────────────────
HASHTAGS = [
    "#LexingtonGays", "#LexingtonPride", "#GayLexington", "#LexingtonLGBTQ",
    "#QueerLexington", "#LexingtonEvents", "#LGBTQLexington", "#OklahomaPride",
    "#LexingtonNightlife", "#HomoHotelHappyHour", "#LexingtonQueer",
    "#GayOklahoma", "#LexingtonCommunity", "#LoveIsLove",
]

# ── Self-Improvement ─────────────────────────────────────────────────────
SEARCH_QUERIES = [
    "lexington lgbtq events",
    "lexington gay events this week",
    "lexington queer events",
    "lexington pride events",
    "lexington drag show",
    "lexington lgbtq community",
]

# ── City-specific filters and scoring ────────────────────────────────────
# These data structures are CITY-SPECIFIC. Shared code (runner.py, image_maker.py,
# gen_website_html.py, generator.py) reads from these. NEVER hardcode city values
# in shared code — that breaks the sync pattern. See city-growth-playbook §15.5.
#
# When scaffolding a new city, this section gets reset to empty/generic defaults.
# Each city populates its own values during launch (Phase 3 source discovery).
#
# Lexington Gays values below are the reference implementation.

# Source keys (subset of SOURCES) considered always-LGBTQ.
# Used by runner.py to decide whether an event needs the LGBTQ keyword filter.
LGBTQ_SOURCES = {
    # Generic — work for any city if those source modules exist
    "recurring", "specific_orgs", "manual", "facebook_events",
    "aa_meetings", "community_groups", "qlist",
    # City-specific (Lexington)
    "okeq", "okeq_calendar", "homo_hotel", "twisted_arts",
    "council_oak", "hotmess_sports", "all_souls_special",
    "pflag_lexington", "black_queer_lexington", "freedom_oklahoma",
    "ulexington_pride", "osu_lexington",
    "circle_cinema", "philbrook_museum", "lexington_arts_district",
    "lexington_isnt_boring",
    "slack_events_local", "slack_unite_lgbtq_plus",
}

# Inclusive community partners (city-specific). Events from these orgs are welcome
# even when they don't contain LGBTQ keywords. Add the actual org name as a substring.
COMMUNITY_PARTNER_KEYWORDS = [
    "the sonic ray", "sonic ray", "sonicray",
]

# City-specific blocklist additions. Combined with the generic blocklist in runner.py.
# Use lowercase substrings. Generic blocklist (sports/oil/non-LGBTQ-religious) lives in
# shared code as _GENERIC_NON_LGBTQ_BLOCKLIST.
NON_LGBTQ_BLOCKLIST_CITY = [
    "oral roberts university", "oru football", "oru basketball", "oru baseball",
    "golden eagles football", "golden eagles basketball",
    "tu football", "osu football", "ou football", "sooners football",
    "spe lexington",
]

# Address fragment → display business name. Used by clean_venue() in image_maker.py
# and gen_website_html.py to display business names instead of raw street addresses.
VENUE_NAME_MAP = {
    '302 south frankfort': 'DVL Club & Lounge',
    '302 s. frankfort':    'DVL Club & Lounge',
    '302 s frankfort':     'DVL Club & Lounge',
    '1338 e 3rd':          'Lexington Eagle',
    '1330 e 3rd':          'Lexington Eagle',
    '602 south lewis':     'Pump Bar',
    '602 s. lewis':        'Pump Bar',
    '602 s lewis':         'Pump Bar',
    '6808 s. memorial':    'Loony Bin Comedy Club',
    '6808 s memorial':     'Loony Bin Comedy Club',
    '1124 s. lewis':       'WEL Bar',
    '1301 s. boston':      'Boston Ave UMC',
    '2224 w 51st':         'Zarrow Library',
}

# True gay bar venues — events at these always score 5 in flamingo scoring.
# Use lowercase substrings (matched against venue field, after clean_venue).
TRUE_GAY_BAR_VENUES = {
    'club majestic', 'lexington eagle', 'yellow brick', 'majestic lexington',
    '1330 e 3rd', '1338 e 3rd', 'the vanguard',
    'pump bar', '602 south lewis', '602 s. lewis', '602 s lewis',
}

# Queer-friendly venues (not exclusively gay) — events here default to 4 unless
# higher tier matches first.
QUEER_FRIENDLY_VENUES = {
    'dvl', '302 south frankfort', '302 s. frankfort', '302 s frankfort', 'elote',
}

# Source keys that are LGBTQ-community-organized. Events from these sources matching
# COMMUNITY_KW score 3 minimum. Subset of LGBTQ_SOURCES.
LGBTQ_COMMUNITY_SOURCES = {"homo_hotel", "okeq", "recurring", "manual"}

# Signature event configuration (the "HHHH" slot). City-specific.
# If a city has no signature event yet, set "name_keywords": [] — EOTW logic will
# skip directly to anchor cultural event or generic priority.
SIGNATURE_EVENT = {
    "name": "Homo Hotel Happy Hour",
    "name_keywords": ["homo hotel", "hhhh"],
    "source_key": "homo_hotel",
    "schedule": "1st Friday monthly, 7pm",
    "is_priority_one": True,
}

# Anchor cultural event (the "Council Oak Men's Chorale" slot). City-specific.
# If none, set "name_keywords": [].
ANCHOR_CULTURAL_EVENT = {
    "name": "Council Oak Men's Chorale",
    "name_keywords": ["council oak", "comc"],
    "source_key": "council_oak_chorus",
    "is_priority_two": True,
}

# Affirming venue keywords that score 3 (non-bar non-arts but reliably welcoming).
# E.g. specific UU congregations.
AFFIRMING_VENUE_KEYWORDS_CITY = ["all souls"]

# City-specific keywords added to the FIVE-flamingo (super gay) keyword list.
# Generic queer terms (drag, pride, queer night, etc.) live in shared code.
# Add city-specific org names, signature events, etc.
FIVE_FL_KEYWORDS_CITY = [
    "homo hotel", "hhhh", "twisted arts",
    "osu lexington queer", "pflag lexington",
    "lambda bowling", "lambda unity",
    "gabbin with gabbi", "pride nation entertainment",
    "brad lee", "lesbian attachment",
]

# City-specific keywords added to the FOUR-flamingo (very queer) keyword list.
FOUR_FL_KEYWORDS_CITY = [
    "equality center", "okeq", "pflag", "sonic ray", "council oak", "hrc",
    "queer collective", "queer crafters",
]


# ── Helpers ──────────────────────────────────────────────────────────────
def ensure_dirs():
    """Create data directories if they don't exist."""
    for d in [DATA_DIR, EVENTS_DIR]:
        os.makedirs(d, exist_ok=True)

def current_week_key():
    """Get a key for the current week like '2026-W13'."""
    now = datetime.now()
    return f"{now.year}-W{now.isocalendar()[1]:02d}"
