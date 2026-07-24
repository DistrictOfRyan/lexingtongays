"""Central configuration for Lexington Gays automation."""
import os
from datetime import datetime

# ── City identity ────────────────────────────────────────────────────────
# CITY-SPECIFIC. Read by tools/geo_guard.py (via resolve_city) to drop events
# that belong to another metro before publish. Added 2026-07-23 for gap G204,
# after 14 of 84 events in 2026-W30 were published at TULSA venues (Philbrook,
# Circle Cinema, Dennis R. Neill Equality Center, qlist.app/events/Tulsa/...)
# relabelled as Lexington. Without this the guard fails OPEN and does nothing,
# so every city site needs its own value - never let it be inherited by sync.
CITY_NAME = "Lexington"
CITY_STATE = "KY"

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
ANTHROPIC_API_KEY = os.environ.get("SITES_ANTHROPIC_KEY", "")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
META_IG_USER_ID = os.environ.get("META_IG_USER_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
TICKETMASTER_API_KEY = os.environ.get("TICKETMASTER_API_KEY", "")

# ── Event Sources ────────────────────────────────────────────────────────
# Priority: 1 = always feature, 2 = feature if good, 3 = only if special/slow week
# Populated from LEXINGTON_GAYS_SOURCE_DIRECTORY.md (Phase 3 source discovery, 2026-04-30).
SOURCES = {
    # Tier 1 — Anchor LGBTQ+ orgs
    "lex_pride_center": {
        "name": "Lexington Pride Center / PCSO",
        "url": "https://www.lexpridecenter.org/",
        "alt_url": "https://www.glso.org/site/",
        "facebook": "https://www.facebook.com/LexPrideCenter/",
        "priority": 1,
        "type": "priority",
        "description": "Kentucky's oldest LGBTQ+ organization (founded 1977). Operates LGBTQIA+ community center at 389 Waller Avenue, Suite 100. Free monthly food bank, victim advocacy, support groups, library, community education. Produces Lexington Pride Festival.",
    },
    "lex_pride_festival": {
        "name": "Lexington Pride Festival",
        "url": "https://www.lexpridefest.org/",
        "facebook": "https://www.facebook.com/LexingtonPrideFestival/",
        "instagram": "https://www.instagram.com/lexpridefest/",
        "priority": 1,
        "type": "priority",
        "description": "Annual Pride festival, last Saturday of June. Parade down Main Street + festival at Central Bank Center. ~50,000 attendees, 200+ booths, 30 sponsors.",
    },
    "uk_lgbtq": {
        "name": "UK Office of LGBTQ* Resources",
        "url": "https://www.uky.edu/lgbtq/Events",
        "priority": 1,
        "type": "priority",
        "description": "University of Kentucky LGBTQ* Resources office. Calendar of events open to community. Located in Dinkle-Mas Suite, Gatton Student Center.",
    },
    "pflag_central_ky": {
        "name": "PFLAG Central Kentucky",
        "url": "https://pflaglexington.org/",
        "facebook": "https://www.facebook.com/pflag.lexington/",
        "priority": 1,
        "type": "community",
        "description": "Local PFLAG chapter — support and advocacy for LGBTQIA+ community and families. Rebranded as PFLAG Lexington/Fayette County; old pflagcentralky.org domain now returns 503.",
    },
    "fairness_campaign": {
        "name": "Fairness Campaign",
        "url": "https://www.fairness.org/",
        "priority": 1,
        "type": "advocacy",
        "description": "Kentucky's LGBTQ advocacy organization (founded 1991). Lobbies in Frankfort. Sends regular newsletter with KY LGBTQ+ events.",
    },
    "queer_kentucky": {
        "name": "Queer Kentucky",
        "url": "https://queerkentucky.com/",
        "priority": 2,
        "type": "media",
        "description": "Kentucky's only LGBTQ+ newsroom. Coverage of community, venues, events.",
    },
    "transkentucky": {
        "name": "TransKentucky",
        "url": "http://www.transkentucky.com/",
        "facebook": "https://www.facebook.com/TransKentucky/",
        "priority": 1,
        "type": "community",
        "description": "Trans support, social, and resource group. Meets first Saturday monthly at 7:30pm in Lexington.",
        "recurring": "1st Saturday monthly, 7:30pm",
    },
    "imperial_court_ky": {
        "name": "Imperial Court of Kentucky",
        "url": "https://imperialcourtkentucky.org/",
        "priority": 1,
        "type": "priority",
        "description": "501(c)(3) drag charity organization. Annual Coronation event, ongoing fundraising and community drag programming.",
    },
    "ky_black_pride": {
        "name": "Kentucky Black Pride",
        "url": "https://kentuckyblackpride.com/",
        "priority": 1,
        "type": "priority",
        "description": "Annual celebration + ongoing programming for KY's QTPOC community.",
    },
    "bluegrass_black_pride": {
        "name": "Bluegrass Black Pride",
        "url": "https://www.facebook.com/BluegrassBlackPride/",
        "priority": 1,
        "type": "community",
        "description": "African-American LGBTQ nonprofit advocating for equity in the Bluegrass region.",
    },
    "avol": {
        "name": "AIDS Volunteers of Lexington",
        "url": "https://avolky.org",
        "priority": 2,
        "type": "health",
        "description": "Provides housing and supportive services to 400+ low-income people living with HIV/AIDS in Lexington area.",
    },
    "ky_health_justice": {
        "name": "Kentucky Health Justice Network",
        "url": "https://kentuckyhealthjusticenetwork.org",
        "priority": 2,
        "type": "health",
        "description": "Advocacy, navigation, and financial assistance for trans health care + abortion care.",
    },

    # Tier 2 — Bars and drag venues
    "the_bar_complex": {
        "name": "The Bar Complex",
        "address": "224 East Main St, Lexington",
        "instagram": "https://www.instagram.com/the.bar.complex/",
        "priority": 2,
        "type": "bar",
        "description": "Kentucky's oldest gay bar (since 1980). Multiple rooms, dance floor modeled after Studio 54. Drag shows Thu-Sat 10:30pm-2am. 21+.",
    },
    "crossings": {
        "name": "Crossings Lexington",
        "url": "https://www.facebook.com/CrossingsLexington",
        "address": "117 N Limestone St, Lexington, KY 40507",
        "priority": 2,
        "type": "bar",
        "description": "LGBTQ+ dive bar. Opened as leather bar in 1980s. Mon-Sun 4pm-2:30am. Go-go boys, drag queens, full event calendar.",
    },
    "bar_ona": {
        "name": "Bar Ona",
        "address": "108 Church St, Lexington, KY",
        "instagram": "https://www.instagram.com/ona_is_a_bar/",
        "facebook": "https://www.facebook.com/ONA108/",
        "priority": 3,
        "type": "bar",
        "description": "Esquire-rated downtown Lexington cocktail bar. Queer-friendly crowd. Open 7 days 5p-1a; specials posted to Instagram.",
    },
    "lussi_brown": {
        "name": "Lussi Brown Coffee Bar",
        "address": "114 Church St, Lexington, KY",
        "facebook": "https://www.facebook.com/LussiBrownCoffeeBar/",
        "priority": 2,
        "type": "community",
        "description": "Queer-owned, woman-owned artisanal coffee shop and bar. Voted Best of Lex 2024. Opened June 2017. Coffee/tea cocktails from noon, 21+ during bar service.",
    },
    "third_street_stuff": {
        "name": "Third Street Stuff and Coffee",
        "priority": 3,
        "type": "community",
        "description": "LGBTQ+ owned cafe with Fair Trade Certified Organic coffee, baked goods, sandwiches.",
    },
    "lex_lesbian_coffeehouse": {
        "name": "Lexington Lesbian Coffee House",
        "url": "https://www.facebook.com/LLcoffeehouse/",
        "priority": 3,
        "type": "community",
        "description": "Lesbian-focused coffeehouse community.",
    },
    "eppings_eastside": {
        "name": "Epping's on Eastside (Poppy & Olive)",
        "priority": 2,
        "type": "arts",
        "description": "Queer-friendly upscale dining with regular drag brunch. House-cured meats, region's diverse farming community.",
    },
    "lockbox_21c": {
        "name": "Lockbox at 21c Museum Hotel",
        "priority": 2,
        "type": "arts",
        "description": "Queer-friendly art-hotel restaurant with revolving local-food menu and drag brunch programming.",
    },
    "diva_royale_lex": {
        "name": "Diva Royale Lexington",
        "priority": 2,
        "type": "arts",
        "description": "Drag dinner shows Fri/Sat, Sun brunch shows. Female celebrity impersonations.",
    },

    # Tier 2 — Sports
    "hotmess_sports": {
        "name": "HotMess Sports Lexington",
        "url": "https://hotmesssports.com/",
        "priority": 1,
        "type": "sports",
        "description": "LGBTQ+ rec sports league. Kickball (spring/fall), beach volleyball (summer), dodgeball + bowling (winter), cornhole. Founded 2021.",
    },
    "the_league_lex": {
        "name": "The League Lexington",
        "url": "https://theleaguelex.com/",
        "priority": 1,
        "type": "sports",
        "description": "LGBTQ+ rec sports league.",
    },
    "usgsn_lex": {
        "name": "USGSN Lexington",
        "url": "https://www.usgsn.com/lexington",
        "priority": 2,
        "type": "sports",
        "description": "US Gay Sports Network city page for Lexington.",
    },
    "outloud_sports": {
        "name": "OutLoud Sports",
        "url": "https://outloudsports.com/",
        "priority": 2,
        "type": "sports",
        "description": "National Queer+ recreational sports organization.",
    },
    "frontrunners_lex": {
        "name": "Frontrunners Lexington",
        "url": "https://frontrunnerslex.com",
        "priority": 1,
        "type": "sports",
        "description": "Queer runners and walkers, twice-weekly meetups for exercise and community.",
    },

    # Tier 2 — Arts and choruses
    "new_song_bluegrass": {
        "name": "New Song in the Bluegrass",
        "url": "https://www.facebook.com/NewSongInTheBluegrass",
        "priority": 1,
        "type": "priority",
        "description": "Community chorus for LGBT and LGBT-friendly singers in Lexington. Anchor cultural event. Concerts always get Event of the Week.",
    },
    "sister_sound": {
        "name": "Sister Sound",
        "url": "https://sistersound.org",
        "priority": 1,
        "type": "arts",
        "description": "Lexington's community choir for women. LGBTQAI+ affirming.",
    },
    "ky_bourbon_bears": {
        "name": "Kentucky Bourbon Bears",
        "url": "https://kentuckybourbonbears.com",
        "priority": 2,
        "type": "community",
        "description": "Social organization for bears + all LGBTQ+ community members in KY.",
    },
    "ky_fried_sisters": {
        "name": "Kentucky Fried Sisters",
        "url": "https://www.facebook.com/KYFriedSisters/",
        "priority": 2,
        "type": "community",
        "description": "Lexington's order of genderqueer clown nuns. Community fundraising + visibility. Original kyfriedsisters.org domain expired/parked-for-sale; Facebook is now the only active presence.",
    },
    "last_wednesgays": {
        "name": "Lexington's Last WednesGays",
        "url": "https://www.faulknermorgan.org/upcoming-events/last-wednesgays",
        "priority": 1,
        "type": "community",
        "description": "Recurring queer community social, last Wednesday of the month. Started by Andrew Shayde, brought to Lexington 2019, restarted March 2025. ~125 attendees; rotates among LGBTQ-friendly bars; 10% of sales to AVOL Kentucky. Strong signature event candidate.",
        "recurring": "Last Wednesday monthly",
    },
    "lex_queer_craft_club": {
        "name": "Lexington Queer Craft Club",
        "priority": 2,
        "type": "community",
        "description": "Monthly queer craft event — junk journaling, fan-making, etc. Eventbrite-listed.",
        "recurring": "Monthly (varies)",
    },
    "lex_gsa_youth": {
        "name": "Lexington Gender and Sexuality Alliance for Youth",
        "url": "https://www.facebook.com/LexingtonGSA/",
        "priority": 2,
        "type": "community",
        "description": "GSA youth group operating as part of Lexington Pride Center.",
    },
    "trans_parent_lex": {
        "name": "Trans Parent Lex",
        "priority": 2,
        "type": "community",
        "description": "Facebook group for parents and allies of transgender teens in and around Lexington.",
    },
    "translex": {
        "name": "TransLex",
        "priority": 2,
        "type": "community",
        "description": "Virtual space inclusive to anyone on the gender-spectrum.",
    },

    # Tier 4 — Affirming faith communities
    "bluegrass_ucc": {
        "name": "Bluegrass United Church of Christ",
        "url": "https://bluegrasschurch.org",
        "priority": 2,
        "type": "church",
        "description": "Open and Affirming UCC congregation.",
    },
    "uucl": {
        "name": "Unitarian Universalist Church of Lexington",
        "url": "https://www.uucl.org/",
        "facebook": "https://www.facebook.com/UULexington/",
        "priority": 2,
        "type": "church",
        "description": "UU Welcoming Congregation.",
    },
    "diolex": {
        "name": "Episcopal Diocese of Lexington",
        "url": "https://www.diolex.org/",
        "priority": 2,
        "type": "church",
        "description": "Open, affirming, inclusive Episcopal community. Diocesan-level entry; individual parishes vary.",
    },
    "christ_church_cathedral_lex": {
        "name": "Christ Church Cathedral",
        "url": "https://ccclex.org",
        "priority": 2,
        "type": "church",
        "description": "Episcopal cathedral, affirming. Emergency assistance fund.",
    },
    "lex_umc_sc": {
        "name": "Lexington UMC SC",
        "url": "https://lexumcsc.com",
        "priority": 3,
        "type": "church",
        "description": "Methodist congregation in Lexington.",
    },
    "beaumont_pcusa": {
        "name": "Beaumont Presbyterian Church",
        "priority": 2,
        "type": "church",
        "description": "More Light Presbyterian congregation. Full LGBTQIA+ inclusion in life, ministry, leadership.",
    },
    "maxwell_pres": {
        "name": "Maxwell Street Presbyterian Church",
        "url": "https://maxpres.org",
        "priority": 3,
        "type": "church",
        "description": "Presbyterian church in Bluegrass Rainbow Faith Communities Directory.",
    },
    "first_pres_lex": {
        "name": "First Presbyterian Church Lexington",
        "priority": 3,
        "type": "church",
        "description": "Presbyterian congregation, in Rainbow Faith Communities Directory. Monthly prepared meal service.",
    },
    "st_luke_umc": {
        "name": "St. Luke United Methodist Church",
        "priority": 3,
        "type": "church",
        "description": "Methodist congregation. God's Pantry location, Spanish-language services available.",
    },
    "bethesda_tabernacle": {
        "name": "Bethesda Tabernacle",
        "priority": 3,
        "type": "church",
        "description": "Pentecostal church started by a gay couple. LGBTQAI+ affirming.",
    },
    "woven_church_lex": {
        "name": "Woven Church Lex",
        "url": "https://www.wovenchurchlex.com/",
        "priority": 3,
        "type": "church",
        "description": "Independent affirming church.",
    },

    # Tier 3 — Aggregators
    "qlist_lex": {
        "name": "QLIST Lexington",
        "url": "https://qlist.app/cities/Kentucky/Lexington",
        "priority": 2,
        "type": "aggregator",
        "description": "LGBTQ+ event aggregator with structured listings (verify city ID — initial fetch returned 403).",
    },
    "eventbrite_lex_lgbt": {
        "name": "Eventbrite LGBT Lexington",
        "url": "https://www.eventbrite.com/d/ky--lexington/lgbt/",
        "priority": 2,
        "type": "aggregator",
        "description": "Eventbrite LGBT-tagged events in Lexington.",
    },
    "eventbrite_lex_fayette": {
        "name": "Eventbrite LGBTQ Lexington-Fayette",
        "url": "https://www.eventbrite.com/d/ky--lexington-fayette/lgbtq/",
        "priority": 2,
        "type": "aggregator",
        "description": "Eventbrite LGBTQ-tagged events for Lexington-Fayette area.",
    },
    "meetup_lex": {
        "name": "Meetup LGBTQ Lexington",
        "url": "https://www.meetup.com/find/us--ky--lexington/lgbtq/",
        "priority": 2,
        "type": "aggregator",
        "description": "LGBTQ+ meetup groups and events in Lexington.",
    },
    "visitlex_lgbtq": {
        "name": "VisitLEX LGBTQ Guide",
        "url": "https://www.visitlex.com/guides/post/lgbtq/",
        "priority": 2,
        "type": "aggregator",
        "description": "Lexington Convention & Visitors Bureau curated LGBTQ+ travel guide.",
    },
    "uk_libguides_lgbtq": {
        "name": "UK LibGuides Central KY LGBTQIA+ Resource Guide",
        "url": "https://libguides.uky.edu/LGBTQ",
        "priority": 3,
        "type": "aggregator",
        "description": "University of Kentucky academic LGBTQIA+ resource guide.",
    },
    "be_lexproud": {
        "name": "Be LexProud!",
        "url": "https://www.lexingtonky.gov/lexproud",
        "priority": 3,
        "type": "aggregator",
        "description": "City of Lexington LGBTQ+ initiative page. Pride flag program on Main Street.",
    },
    "lex_human_rights": {
        "name": "Lexington Human Rights Commission",
        "url": "https://lexhumanrights.org",
        "priority": 3,
        "type": "community",
        "description": "Local agency investigating discrimination in employment, housing, and accommodations.",
    },

    # Tier 5 — Annual events
    "north_american_bear_weekend": {
        "name": "North American Bear Weekend",
        "url": "https://nabweekend.com/schedule/",
        "website": "https://nabweekend.com/",
        "priority": 1,
        "type": "priority",
        "description": "Annual major LGBTQ+ event in Lexington at Marriott Griffin Gate Resort. 14th annual runs Feb 12-15 2026; ~1,800 attendees. Verify exact dates each year (site posts next-year dates by May 1).",
    },
    "pride_of_place_tour": {
        "name": "Pride of Place Tour",
        "priority": 3,
        "type": "community",
        "description": "Self-guided LGBTQ+ history tour from Lexington Visitors Center (215 W Main St, Suite 75). 200 years of history, rainbow crosswalks, Sweet Evening Breeze mural.",
    },

    # Site discovery 2026-05-07
    "bourbon_belonging": {
        "name": "Bourbon & Belonging",
        "url": "https://www.bourbonandbelonging.com/",
        "priority": 1,
        "type": "priority",
        "description": "Kentucky's Queer Bourbon Week. Annual early-October multi-city event run by Queer Kentucky. Lexington's Distillery District hosts drag happy hour, queer history walks, curated bourbon tastings.",
        "recurring": "Annual, early October",
    },
    "harveys_bar": {
        "name": "Harvey's Bar",
        "address": "200 W Main St, Lexington, KY 40507",
        "url": "https://qlist.app/venues/Lexington/Harveys-Bar/bENRL2F4c2JMY2xsV1hpYU1uS1RXZw",
        "priority": 2,
        "type": "bar",
        "description": "LGBTQ-friendly downtown cocktail bar. Listed on QLIST as a Lexington gay/queer venue. Spacious patio, dance floor, creative cocktails.",
    },
    "lex_public_library_pride": {
        "name": "Lexington Public Library Pride Programming",
        "url": "https://www.lexpublib.org/pride",
        "events_url": "https://events.lexpublib.org/",
        "priority": 2,
        "type": "community",
        "description": "LPL year-round LGBTQ programming. Pride Month Matinees (every Friday in June), LGBTQ+ Board Game Club (recurring), Pride Walking Tour, Pagan Babies Archive talks, queer history programming.",
    },
    "girlsgirlsgirls_burritos": {
        "name": "girlsgirlsgirls Burritos",
        "url": "https://girlsgirlsgirlsburritos.com/",
        "facebook": "https://www.facebook.com/eatgggirls/",
        "instagram": "https://www.instagram.com/girlsgirlsgirlsburritos/",
        "address": "395 S Limestone St, Lexington, KY",
        "priority": 2,
        "type": "community",
        "description": "Woman-owned, queer-aligned burrito and margarita spot near UK. Hub for LGBTQ+ fundraisers and Pride Festival benefits (e.g., art auctions). Monday Night Karaoke, Sunday Night Trivia.",
    },
    "lex_drag_troupe": {
        "name": "Lexington's Drag Troupe",
        "url": "https://www.facebook.com/p/Lexingtons-Drag-Troupe-100070019833647/",
        "priority": 2,
        "type": "arts",
        "description": "Local Lexington drag collective producing recurring drag shows around the city. Active Facebook event presence.",
    },
    "lex_lgbt_app": {
        "name": "Lex.LGBT Local Groups",
        "url": "https://www.lex.lgbt/local-groups",
        "priority": 3,
        "type": "aggregator",
        "description": "LGBTQ+ social/group-finding app. Lists queer hobby groups (Dyke Basketball, DnD Queers, Queer Witches, Over40+ queers, T4T Gym Buddies, Craft in the Park).",
    },
    "rainbow_index_lex": {
        "name": "Rainbow Index Lexington",
        "url": "https://rainbowindex.com/city/lexington",
        "priority": 3,
        "type": "aggregator",
        "description": "LGBTQ city guide aggregator listing Lexington gay bars, venues, and events.",
    },
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
    "#QueerLexington", "#LexingtonEvents", "#LGBTQLexington", "#KentuckyPride",
    "#LexingtonNightlife", "#LexProud", "#LexingtonQueer",
    "#GayKentucky", "#LexingtonCommunity", "#LoveIsLove", "#BluegrassPride",
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
    "bar_complex_ig", "crossings_ig",  # Lexington IG-primary gay bars (genuine LGBTQ venues, trust all posts)
    "rendered_sites",  # Lexington rendered specs (Pride Center gcal) are all lgbtq_only
    # Generic — work for any city if those source modules exist
    "recurring", "specific_orgs", "manual", "facebook_events",
    "aa_meetings", "community_groups", "qlist",
    # Lexington-specific (matches SOURCES dict keys above)
    "lex_pride_center", "lex_pride_festival", "uk_lgbtq",
    "pflag_central_ky", "fairness_campaign", "queer_kentucky",
    "transkentucky", "imperial_court_ky", "ky_black_pride", "bluegrass_black_pride",
    "avol", "ky_health_justice",
    "the_bar_complex", "crossings", "bar_ona", "lussi_brown",
    "third_street_stuff", "lex_lesbian_coffeehouse",
    "eppings_eastside", "lockbox_21c", "diva_royale_lex",
    "hotmess_sports", "the_league_lex", "usgsn_lex", "outloud_sports",
    "frontrunners_lex",
    "new_song_bluegrass", "sister_sound", "ky_bourbon_bears",
    "ky_fried_sisters", "last_wednesgays", "lex_queer_craft_club",
    "lex_gsa_youth", "trans_parent_lex", "translex",
    "north_american_bear_weekend", "pride_of_place_tour",
    # Affirming faith — included as LGBTQ sources because they're affirming-only
    "bluegrass_ucc", "uucl", "diolex", "christ_church_cathedral_lex",
    "beaumont_pcusa", "maxwell_pres", "first_pres_lex",
    "bethesda_tabernacle", "woven_church_lex",
    # Site discovery 2026-05-07
    "bourbon_belonging", "harveys_bar", "lex_public_library_pride",
    "lex_drag_troupe", "lex_lgbt_app", "rainbow_index_lex",
}

# Inclusive community partners (city-specific). Events from these orgs are welcome
# even when they don't contain LGBTQ keywords. Lexington has no equivalent of Tulsa's
# Sonic Ray yet — leave empty until a community partner emerges.
COMMUNITY_PARTNER_KEYWORDS = [
    # Lexington queer-welcoming venues - events here are kept as community events
    # even without an explicit LGBTQ keyword (matches TulsaGays' community filter
    # philosophy; William chose community-inclusive 2026-06-19). All verified-real
    # Lexington KY venues seen hosting real queer/community events.
    "the bar complex", "bar complex",
    "crossings lexington", "crossings",
    "lexington pride center", "pride center",
    "lexington pride festival", "lexington fairness",
    "foolish things",            # Foolish Things Coffee - hosts Shut Up & Write, queer-welcoming
    "tapster",                   # Tapster - hosts the Lexington Pride Bar Crawl
    "mortimer",                  # Mortimer's - Pride Night drag shows
    "the burl", "the green lantern", "al's bar",  # well-known Lexington queer-welcoming music/dive venues
    "ole hookers",               # downtown dive bar (205 S Limestone), karaoke, queer-welcoming
    "kentucky theatre", "kentucky theater",  # historic theater (214 E Main); runs queer film series (Disclosure, etc.)
    "carriage house", "studio players",      # Studio Players community theater (154 W Bell Ct)
]

# City-specific blocklist additions. Combined with the generic blocklist in runner.py.
# Lexington-specific exclusions: UK Wildcats sports, Keeneland horse racing,
# Kentucky Derby, Transy/Centre/Asbury non-LGBTQ collegiate sports.
NON_LGBTQ_BLOCKLIST_CITY = [
    # University of Kentucky sports
    "uk basketball", "uk football", "kentucky wildcats",
    "wildcats basketball", "wildcats football", "wildcats baseball",
    "rupp arena basketball", "kroger field football",
    # Other KY collegiate sports
    "louisville cardinals", "western kentucky hilltoppers",
    "transy basketball", "transylvania basketball",
    "centre college basketball", "asbury basketball",
    # Horse racing (huge Lexington category, but not LGBTQ-relevant)
    "keeneland race", "keeneland fall", "keeneland spring",
    "kentucky derby", "kentucky oaks",
    "the red mile", "spendthrift farm",
    # Bourbon industry events (also huge in KY but not LGBTQ-coded)
    "bourbon trail tour", "bourbon distillery tour",
]

# Address fragment → display business name. Used by clean_venue() in image_maker.py
# and gen_website_html.py to display business names instead of raw street addresses.
# Lexington venues only.
VENUE_NAME_MAP = {
    '224 east main':       'The Bar Complex',
    '224 e main':          'The Bar Complex',
    '224 e. main':         'The Bar Complex',
    '117 n limestone':     'Crossings',
    '117 n. limestone':    'Crossings',
    '117 north limestone': 'Crossings',
    '389 waller':          'Lexington Pride Center',
    '215 w main':          'Lexington Visitors Center',
    '215 w. main':         'Lexington Visitors Center',
}

# True gay bar venues — events at these always score 5 in flamingo scoring.
# Use lowercase substrings (matched against venue field, after clean_venue).
# Lexington has 2 confirmed true gay bars: The Bar Complex (since 1980) and Crossings.
TRUE_GAY_BAR_VENUES = {
    'the bar complex', 'bar complex',
    'crossings', 'crossings lexington',
    '224 east main', '224 e main', '224 e. main',
    '117 n limestone', '117 north limestone',
}

# Queer-friendly venues (not exclusively gay) — events here default to 4 unless
# higher tier matches first.
QUEER_FRIENDLY_VENUES = {
    'lussi brown', 'lussi brown coffee',
    'third street stuff', 'third street coffee',
    "epping's", 'eppings on eastside', 'poppy & olive', 'poppy and olive',
    'lockbox', '21c museum', '21c hotel',
    'bar ona',
    'lexington lesbian coffee',
    "harvey's bar", 'harveys bar',
    'girlsgirlsgirls', 'girlsgirlsgirls burritos', 'eatgggirls',
}

# Source keys that are LGBTQ-community-organized. Events from these sources matching
# COMMUNITY_KW score 3 minimum. Subset of LGBTQ_SOURCES.
LGBTQ_COMMUNITY_SOURCES = {
    "lex_pride_center", "lex_pride_festival",
    "transkentucky", "pflag_central_ky", "imperial_court_ky",
    "recurring", "manual",
}

# Signature event configuration (the "HHHH" slot).
# Per Phase 0 intake: left open. Strongest candidate is Last WednesGays — fill in
# once operator chooses one. Empty name_keywords means EOTW logic skips this priority.
SIGNATURE_EVENT = {
    "name": "",
    "name_keywords": [],
    "source_key": "",
    "schedule": "",
    "is_priority_one": False,
}

# Anchor cultural event (the "Council Oak Men's Chorale" slot).
# Lexington's New Song in the Bluegrass is the closest analog (community chorus).
ANCHOR_CULTURAL_EVENT = {
    "name": "New Song in the Bluegrass",
    "name_keywords": ["new song in the bluegrass", "new song bluegrass", "new song chorus"],
    "source_key": "new_song_bluegrass",
    "is_priority_two": True,
}

# Affirming venue keywords that score 3 (non-bar non-arts but reliably welcoming).
# Lexington's specific affirming UU/UCC anchors.
AFFIRMING_VENUE_KEYWORDS_CITY = [
    "uucl", "unitarian universalist church of lexington",
    "bluegrass ucc", "bluegrass church",
    "beaumont presbyterian", "maxwell presbyterian",
    "christ church cathedral",
    "woven church",
]

# City-specific keywords added to the FIVE-flamingo (super gay) keyword list.
# Lexington-specific signature events, drag collectives, anchor orgs.
FIVE_FL_KEYWORDS_CITY = [
    "imperial court of kentucky", "imperial court ky", "ick coronation",
    "kentucky black pride", "bluegrass black pride", "ky black pride",
    "kentucky bourbon bears", "ky bourbon bears",
    "kentucky fried sisters", "ky fried sisters",
    "last wednesgays", "wednesgays",
    "transkentucky", "trans kentucky",
    "frontrunners lex", "frontrunners lexington",
    "queer craft club", "lexington queer craft",
    "popp presents", "drag underground",
    "north american bear weekend", "world bear weekend", "bear weekend",
    "lex pride", "lexington pride festival",
    "queer communion", "davis shoulders",
]

# City-specific keywords added to the FOUR-flamingo (very queer) keyword list.
FOUR_FL_KEYWORDS_CITY = [
    "lexington pride center", "pride community services",
    "fairness campaign", "queer kentucky",
    "uk lgbtq", "university of kentucky lgbtq",
    "avol", "aids volunteers of lexington",
    "new song", "sister sound",
    "lex gsa", "trans parent lex", "translex",
    "be lexproud", "lexproud",
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
