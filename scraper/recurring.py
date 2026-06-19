"""Hardcoded recurring LGBTQ+ events for Lexington, KY.

Calculates which events fall in the current week (Monday-Sunday) and returns
them with proper YYYY-MM-DD dates. No scraping needed -- these are known,
stable recurring events.

NO FABRICATION RULE
-------------------
This file replaces a version that was blindly string-substituted from TulsaGays
and listed FAKE events at Tulsa venues (Club Majestic, Tulsa Eagle, Yellow Brick
Road) that do not exist in Lexington. Every entry below has a verified, real
recurring day/time at a real Lexington venue. If a recurring schedule cannot be
verified from a primary source (the venue's own site/Facebook, the org's own
page), it is NOT listed here. A short all-real list beats a long fabricated one.

Verified entries (2026-06-19):
  - TransKentucky: 1st Saturday monthly, 7:30 PM, at the Lexington Pride Center.
    Verified on transkentucky.com ("first Saturday of each month at 7:30 pm in
    Lexington, KY") and lexpridecenter.org/transkentucky.
  - Crossings Tuesday Karaoke: weekly Tuesday, 9 PM. Verified from Crossings
    Lexington's own Facebook post ("It's Tuesday Karaoke night at the Old Rugged
    Crossings Lexington from 9-1!").

Deliberately NOT listed (could not verify a fixed recurring day/time from a
primary source -- do not invent one):
  - The Bar Complex weekly drag/cabaret (no published recurring day/time).
  - Crossings weekly drag show / lesbian night / leather night (the venue defers
    to its Facebook for the rotating weekly agenda; no fixed day published).
  - Lexington Pride Center groups other than TransKentucky (GSA, Heart to Heart,
    Queer People of Color, SIP 50+, Board Game Group). The Pride Center states
    these "meet either weekly or monthly, depending on the group" and directs to
    Facebook/Instagram for days/times, noting groups "may be cancelled at last
    minute." When a fixed day/time is confirmed for one, add it below.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.base import BaseScraper

logger = logging.getLogger(__name__)

# freq options: "weekly", "1st", "2nd", "3rd", "4th"
# day: full weekday name matching Python's strftime %A
RECURRING = [
    # Weekly
    {
        "name": "Tuesday Karaoke Night at Crossings",
        "day": "Tuesday",
        "freq": "weekly",
        "time": "9:00 PM - 1:00 AM",
        "venue": "Crossings Lexington, 117 N Limestone, Lexington",
        "url": "https://www.facebook.com/CrossingsLexington",
        "priority": 1,
        "description": (
            "Tuesday karaoke at Crossings, Lexington's queer dive on North "
            "Limestone, with a host running the list and a friendly room "
            "happy to cheer for whatever you pick. Runs 9 to 1."
        ),
        "website_description": (
            "Crossings is Lexington's beloved LGBTQ+ dive bar on North "
            "Limestone, and Tuesday is karaoke night. The host gets going "
            "around 9 and keeps the rotation moving until 1 in the morning. "
            "This is the low-pressure, all-are-welcome kind of karaoke crowd, "
            "so it is a good first stop if you are new in town and want to "
            "meet people without committing to a big night out. Best-time tip "
            "for the shy ones: get there a little after 9 to put your name in "
            "early, order a drink to give your hands something to do, and you "
            "will usually be up within a song or two while the room is still "
            "warming up and forgiving."
        ),
    },
    # 1st occurrence of the month
    {
        "name": "TransKentucky Monthly Meeting",
        "day": "Saturday",
        "freq": "1st",
        "time": "7:30 PM",
        "venue": "Lexington Pride Center, 389 Waller Ave, Lexington",
        "url": "https://www.transkentucky.com/",
        "priority": 1,
        "description": (
            "TransKentucky meets the first Saturday of each month at 7:30 PM, "
            "a social support group for transgender and gender non-conforming "
            "people to share struggles and goals among peers."
        ),
        "website_description": (
            "TransKentucky is a long-running social support group for "
            "transgender and gender non-conforming people, meeting the first "
            "Saturday of every month at 7:30 PM at the Lexington Pride Center "
            "on Waller Avenue. It is a peer space to talk through the real "
            "stuff, from coming out to transition logistics to just finding "
            "your people, with folks at every stage of the journey in the "
            "room. Best-time tip for a first visit: come a few minutes before "
            "7:30 so you can settle in before the group starts, and know that "
            "there is no pressure to share anything until you are ready. Check "
            "the TransKentucky Facebook group for any last-minute changes "
            "before heading out."
        ),
    },
]

# Day name -> weekday number (Monday=0)
DAY_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

# Occurrence -> day-of-month range
OCCURRENCE_RANGES = {
    "1st": (1, 7),
    "2nd": (8, 14),
    "3rd": (15, 21),
    "4th": (22, 28),
}


def _get_week_dates(reference: datetime = None) -> List[datetime]:
    """Return a list of 7 datetime objects for Mon-Sun of the current week."""
    if reference is None:
        reference = datetime.now()
    monday = reference - timedelta(days=reference.weekday())
    return [monday + timedelta(days=i) for i in range(7)]


def _matches_occurrence(date: datetime, freq: str) -> bool:
    """Return True if `date` matches the occurrence rule."""
    if freq == "weekly":
        return True
    if freq in OCCURRENCE_RANGES:
        lo, hi = OCCURRENCE_RANGES[freq]
        return lo <= date.day <= hi
    return False


class RecurringScraper(BaseScraper):
    """Generate hardcoded recurring LGBTQ+ events for the current week."""

    source_name = "recurring"

    def scrape(self) -> List[Dict]:
        events = []
        week_dates = _get_week_dates()

        for entry in RECURRING:
            target_weekday = DAY_MAP.get(entry["day"])
            if target_weekday is None:
                logger.warning(f"[recurring] Unknown day '{entry['day']}' for '{entry['name']}'")
                continue

            for date in week_dates:
                if date.weekday() != target_weekday:
                    continue
                if not _matches_occurrence(date, entry["freq"]):
                    continue

                date_str = date.strftime("%Y-%m-%d")
                events.append(self.make_event(
                    name=entry["name"],
                    date=date_str,
                    time=entry.get("time", ""),
                    venue=entry.get("venue", ""),
                    description=entry.get("description", ""),
                    url=entry.get("url", ""),
                    priority=entry.get("priority", 2),
                ))
                # Each entry should only match once per week
                break

        logger.info(f"[recurring] Generated {len(events)} recurring events for this week")
        return events


def scrape() -> List[Dict]:
    """Module-level entry point."""
    return RecurringScraper().safe_scrape()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    results = scrape()
    for e in results:
        print(f"  {e['date']} {e['name']} | {e['time']} | {e['venue']}")
    print(f"\nTotal: {len(results)} events")
