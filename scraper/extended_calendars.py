"""Extended Lexington event calendar scrapers — venues, tourism, arts, universities, libraries.

Uses a generic config-driven approach: JSON-LD first, then HTML fallback.
All events are filtered for LGBTQ relevance before returning.

Sources covered:
  TOURISM/CVB:
    TravelOK, Green Country OK, LexingtonGo
  NEWS/MEDIA:
    LexingtonKids, Lexington Events (lexington.events)
  CITY:
    City of Lexington Special Events
  MUSEUMS & CULTURAL:
    Philbrook, Woody Guthrie Center, Greenwood Cultural Center, Lexington Zoo, Gathering Place,
    Lexington Garden Center, Oklahoma Aquarium, Discovery Lab, 101 Archer
  PERFORMING ARTS:
    Lexington PAC, BOK Center, Cain's Ballroom, Lexington Theater,
    Hard Rock Live, River Spirit Casino, The Church Studio,
    Cox Business Convention Center
  SPORTS/EXPO:
    ONEOK Field (Lexington Drillers), FC Lexington, Lexington Oilers, Expo Square
  LIBRARIES:
    Lexington City-County Library
  UNIVERSITIES:
    University of Lexington, OSU-Lexington, ORU, Lexington Community College
  LGBTQ+:
    Lexington Pride
  TICKETING/AGGREGATORS:
    SeatGeek Lexington, Meetup Lexington
  NEIGHBORHOOD/NICHE:
    Brookside Business Association, Cherry Street Farmers Market,
    Lexington Farmers' Market, LexingtonGo
"""

import sys
import os
import json
import logging
import time
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.base import BaseScraper
from scraper import dynamic_sources as _dyn
from scraper.relevance import compile_lgbtq_keywords

logger = logging.getLogger(__name__)

LGBTQ_KEYWORDS = [
    # Explicit identity
    "lgbtq", "queer", "gay", "lesbian", "bi", "trans", "drag", "pride",
    "rainbow", "dyke", "nonbinary", "non-binary", "gender", "equality",
    "affirming", "inclusive", "homo", "sapphic", "two-spirit", "twospirit",
    # Queer-adjacent / community-coded
    "oddities", "curiosities",
    "burlesque", "cabaret",
    "feminist", "radical",
    "night market", "art market", "bazaar", "market",
    "wiz",
    "greenwood", "black wall street",
    "boots riley",
    # Cultural event types (effective at curated arts venues)
    "screening", "film festival", "documentary",
    "exhibition", "opening reception", "art opening",
    "workshop", "panel discussion", "panel", "lecture",
    "fundraiser", "benefit show", "benefit concert",
    "cultural festival", "heritage",
    "open mic", "poetry",
]


_LGBTQ_RX = compile_lgbtq_keywords(LGBTQ_KEYWORDS)


def _is_lgbtq_relevant(name: str, description: str = "") -> bool:
    combined = (name + " " + description).lower()
    return bool(_LGBTQ_RX.search(combined))


# ── Site configuration ─────────────────────────────────────────────────────
# Each entry: (url, display_name, category, lgbtq_only)
# lgbtq_only=False  → filter for LGBTQ keywords (general venues)
# lgbtq_only=True   → return ALL events (LGBTQ-specific orgs)

SITES: List[Tuple[str, str, str, bool]] = [
    # ── REBUILT 2026-07-23 ────────────────────────────────────────────────
    # The previous list was the TulsaGays list with "Tulsa" string-replaced by
    # "Lexington". That produced 29 domains that never existed (lexingtonzoo.org,
    # coxcenterlexington.com, calendar.ulexington.edu, ...) plus 10 REAL TULSA
    # venues (Philbrook, Woody Guthrie Center, Cain's Ballroom, BOK Center,
    # Gathering Place, Expo Square, ...) quietly feeding OKLAHOMA events into a
    # Kentucky site. Verified live 2026-07-23: 29/39 dead, 10/39 Tulsa. That is
    # the whole reason source-health reported "63 sources, 0 events."
    # Every URL below was HTTP-verified live on 2026-07-23. Never add a source
    # by find-and-replacing a city name - verify the domain exists first.

    # TOURISM / CVB
    ("https://www.visitlex.com/events/", "VisitLEX", "tourism", False),

    # CITY / GOVERNMENT
    ("https://www.lexingtonky.gov/events", "City of Lexington KY", "city", False),

    # LIBRARIES
    ("https://www.lexpublib.org/events", "Lexington Public Library", "library", False),

    # ARTS / MUSIC / VENUES
    ("https://www.rupparena.com/events", "Rupp Arena", "arts", False),
    ("https://lexingtonoperahouse.com/events/", "Lexington Opera House", "arts", False),
    ("https://manchestermusichall.com/events/", "Manchester Music Hall", "arts", False),
    ("https://www.kentuckytheatre.org/", "Kentucky Theatre", "arts", False),

    # UNIVERSITIES
    ("https://calendar.uky.edu/", "University of Kentucky", "university", False),
    ("https://www.transy.edu/calendar/", "Transylvania University", "university", False),

    # NEIGHBORHOOD / MARKETS
    ("https://www.lexingtonfarmersmarket.com/", "Lexington Farmers Market", "neighborhood", False),

    # LGBTQ+ SPECIFIC (return ALL events, no keyword filter)
    ("https://lexpridefest.org/", "Lexington Pride Festival", "lgbtq", True),
    ("https://www.lexpridecenter.org/events", "Pride Community Services Organization", "lgbtq", True),
]

# Merge in calendar sites discovered + promoted by the weekly source-growth
# engine (data/dynamic_sources.json). De-duped by URL.
SITES = _dyn.merge_unique(SITES, _dyn.calendar_sites())


class ExtendedCalendarsScraper(BaseScraper):
    """Scrape all extended Lexington calendar sources and filter for LGBTQ relevance."""

    source_name = "extended_calendars"

    def scrape(self) -> List[Dict]:
        all_events = []
        for url, name, category, lgbtq_only in SITES:
            try:
                events = self._scrape_site(url, name, lgbtq_only)
                all_events.extend(events)
                logger.info(f"[extended_calendars] {name}: {len(events)} events")
            except Exception as e:
                logger.warning(f"[extended_calendars] {name} failed: {e}")
        logger.info(f"[extended_calendars] Total: {len(all_events)} events across {len(SITES)} sites")
        return all_events

    def _scrape_site(self, url: str, site_name: str, lgbtq_only: bool) -> List[Dict]:
        """Generic scraper: JSON-LD first, then HTML. Filter for LGBTQ if not lgbtq_only site."""
        soup = self.fetch_page(url)
        if not soup:
            return []

        events = []

        # 1. Try JSON-LD structured data (works on ~40% of modern sites)
        events = self._extract_json_ld(soup, site_name)

        # 2. Try Localist platform (used by universities and libraries)
        if not events:
            events = self._extract_localist(soup, site_name, url)

        # 3. Try The Events Calendar (tribe) plugin (used by ~30% of WP sites)
        if not events:
            events = self._extract_tribe(soup, site_name, url)

        # 4. Generic HTML fallback
        if not events:
            events = self._extract_generic(soup, site_name, url)

        # Filter unless LGBTQ-specific org
        if not lgbtq_only:
            events = [e for e in events if _is_lgbtq_relevant(e.get("name", ""), e.get("description", ""))]

        self._random_delay()
        return events

    def _extract_json_ld(self, soup, site_name: str) -> List[Dict]:
        """Extract Event items from JSON-LD blocks."""
        events = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                raw = script.string
                if not raw:
                    continue
                data = json.loads(raw)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    # Handle @graph wrapper
                    if item.get("@type") == "WebPage" and "@graph" in item:
                        items = item["@graph"]
                        continue
                    if item.get("@type") not in ("Event", "SocialEvent", "MusicEvent", "DanceEvent",
                                                   "ComedyEvent", "TheaterEvent", "ScreeningEvent",
                                                   "ExhibitionEvent", "Festival", "SportsEvent"):
                        continue
                    name = item.get("name", "")
                    if not name:
                        continue
                    start = item.get("startDate", "")
                    date_str = str(start)[:10] if start else ""
                    time_str = str(start)[11:16] if start and "T" in str(start) else ""
                    location = item.get("location", {})
                    venue = site_name
                    if isinstance(location, dict):
                        venue = location.get("name", site_name) or site_name
                    elif isinstance(location, str):
                        venue = location or site_name
                    description = str(item.get("description", ""))[:500]
                    event_url = item.get("url", "")
                    events.append(self.make_event(
                        name=name, date=date_str, time=time_str,
                        venue=venue, description=description, url=event_url, priority=2
                    ))
            except Exception:
                continue
        return events

    def _extract_localist(self, soup, site_name: str, base_url: str) -> List[Dict]:
        """Extract events from Localist platform (used by Lexington Library, ULexington, OSU-Lexington)."""
        events = []
        # Localist uses specific data attributes
        containers = (
            soup.select(".lw_events_summary_item")
            or soup.select("[data-id][class*='event']")
            or soup.select(".em-item")
            or soup.select(".event-node")
        )
        for container in containers[:30]:
            name_el = container.select_one(".lw_events_title a, h3 a, h2 a, .event-title a")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 4:
                continue
            url = name_el.get("href", "")
            if url and not url.startswith("http"):
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            date_el = container.select_one("time, .lw_events_time, [class*='date']")
            date_str = ""
            if date_el:
                raw = date_el.get("datetime", "") or date_el.get_text(strip=True)
                date_str = self.parse_date_flexible(raw[:10] if len(raw) > 10 else raw)
            desc_el = container.select_one(".lw_events_description, p, [class*='desc']")
            description = desc_el.get_text(strip=True)[:400] if desc_el else ""
            events.append(self.make_event(
                name=name, date=date_str, venue=site_name,
                description=description, url=url, priority=2
            ))
        return events

    def _extract_tribe(self, soup, site_name: str, base_url: str) -> List[Dict]:
        """Extract events from The Events Calendar (tribe) WordPress plugin."""
        events = []
        containers = (
            soup.select(".tribe-events-calendar-list__event")
            or soup.select(".type-tribe_events")
            or soup.select(".tribe-events-list-event")
            or soup.select(".tribe-event")
        )
        for container in containers[:30]:
            name_el = (
                container.select_one(".tribe-events-calendar-list__event-title")
                or container.select_one(".tribe-events-list-event-title")
                or container.select_one("h2, h3")
            )
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 4:
                continue
            link = name_el.find("a", href=True) or container.find("a", href=True)
            url = ""
            if link:
                href = link["href"]
                url = href if href.startswith("http") else base_url + href
            date_el = container.select_one("time, [class*='date'], abbr")
            date_str = ""
            if date_el:
                raw = date_el.get("datetime", "") or date_el.get_text(strip=True)
                if raw and "T" in raw:
                    raw = raw[:10]
                date_str = self.parse_date_flexible(raw)
            venue_el = container.select_one("[class*='venue']")
            venue = venue_el.get_text(strip=True) if venue_el else site_name
            desc_el = container.select_one("p, [class*='description']")
            description = desc_el.get_text(strip=True)[:400] if desc_el else ""
            events.append(self.make_event(
                name=name, date=date_str, venue=venue or site_name,
                description=description, url=url, priority=2
            ))
        return events

    def _extract_generic(self, soup, site_name: str, base_url: str) -> List[Dict]:
        """Generic HTML extraction — tries common event container patterns."""
        events = []
        containers = (
            soup.select(".event-item")
            or soup.select(".event-card")
            or soup.select(".event-listing")
            or soup.select("[class*='event-row']")
            or soup.select("[itemtype*='schema.org/Event']")
            or soup.select("article[class*='event']")
        )
        for container in containers[:30]:
            name_el = container.select_one("h1, h2, h3, h4, .event-title, .title, [class*='event-name']")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 4:
                continue
            link = container.find("a", href=True)
            url = ""
            if link:
                href = link["href"]
                url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
            date_el = container.select_one("time, [class*='date'], [class*='time']")
            date_str = ""
            if date_el:
                raw = date_el.get("datetime", "") or date_el.get_text(strip=True)
                date_str = self.parse_date_flexible(raw[:10] if len(raw) > 10 else raw)
            desc_el = container.select_one("p, [class*='desc'], [class*='excerpt']")
            description = desc_el.get_text(strip=True)[:400] if desc_el else ""
            events.append(self.make_event(
                name=name, date=date_str, venue=site_name,
                description=description, url=url, priority=2
            ))
        return events


def scrape() -> List[Dict]:
    """Module-level entry point."""
    return ExtendedCalendarsScraper().safe_scrape()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = scrape()
    for e in results:
        print(f"  [{e['source']}] {e['date']} | {e['name']} | {e['venue']}")
    print(f"\nTotal LGBTQ-relevant: {len(results)} events across extended sources")
