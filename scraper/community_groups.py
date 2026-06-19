"""Scraper for LGBTQ+ community groups and venues in Lexington, KY.

Covers verified, currently-operating Lexington organizations only:
Lexington Pride Center, Lexington Pride Festival, Lexington Fairness,
Crossings Lexington, The Bar Complex.

Sources whose existence or event URL could not be verified were removed
rather than fabricated. An accurate short list beats an invented long one.
"""

import sys
import os
import logging
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.base import BaseScraper

logger = logging.getLogger(__name__)


class CommunityGroupsScraper(BaseScraper):
    """Scrape events from verified Lexington LGBTQ+ community groups and venues."""

    source_name = "community_groups"

    # ── Verified real Lexington, KY LGBTQ+ orgs and venues ─────────────
    # Every entry below was confirmed as a real, currently-operating
    # Lexington organization with a working URL. Do not add a source
    # here unless you have verified it the same way.
    SOURCES = {
        "lexington_pride_center": "https://www.lexpridecenter.org/pride-community-event-calendar",
        "lexington_pride_festival": "https://www.lexpridefest.org/events-2-1",
        "lexington_fairness": "https://www.lexfair.org/",
        "crossings_lexington": "https://crossingslexington.com/",
        "bar_complex": "https://thebarcomplex.com/",
    }

    def scrape(self) -> List[Dict]:
        events = []
        for source_key, url in self.SOURCES.items():
            try:
                source_events = self._scrape_source(source_key, url)
                events.extend(source_events)
            except Exception as e:
                logger.error(f"[community_groups] Failed scraping {source_key}: {e}")
        return events

    def _scrape_source(self, source_key: str, url: str) -> List[Dict]:
        """Attempt to scrape event listings from a community group website."""
        soup = self.fetch_page(url)
        if not soup:
            return []

        events = []

        # Look for event-like containers
        containers = (
            soup.select(".event, .events-list li, article, .event-card, .sqs-block-content")
        )

        for container in containers[:20]:  # Limit to avoid noise
            try:
                name_el = container.select_one("h1, h2, h3, h4, .event-title, a")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if not name or len(name) < 5:
                    continue

                # Skip navigation links and non-event content
                skip_words = ["home", "about", "contact", "donate", "menu", "privacy", "terms"]
                if name.lower() in skip_words:
                    continue

                date_el = container.select_one("time, .date, [class*='date']")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)
                date_str = self.parse_date_flexible(date_str)

                link_el = container.find("a", href=True)
                event_url = ""
                if link_el:
                    href = link_el["href"]
                    event_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")

                events.append(self.make_event(
                    name=name,
                    date=date_str,
                    venue=self._venue_for_source(source_key),
                    url=event_url,
                    priority=2,
                ))
            except Exception as e:
                logger.debug(f"[community_groups] Parse error in {source_key}: {e}")

        self._random_delay()
        return events

    def _venue_for_source(self, source_key: str) -> str:
        """Return the default venue for a source."""
        venues = {
            "lexington_pride_center": "Lexington Pride Center",
            "lexington_pride_festival": "Lexington Pride Festival",
            "lexington_fairness": "Lexington Fairness",
            "crossings_lexington": "Crossings, 117 N Limestone, Lexington",
            "bar_complex": "The Bar Complex, 224 E Main St, Lexington",
        }
        return venues.get(source_key, "Lexington")


def scrape() -> List[Dict]:
    """Module-level entry point."""
    return CommunityGroupsScraper().safe_scrape()
