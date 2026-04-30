"""STUB — Tulsa-specific dedicated scrapers for hand-coded LGBTQ+ orgs.
TulsaGays' version covers PFLAG Tulsa, Black Queer Tulsa, Council Oak Men's Chorale,
HotMess Sports, Circle Cinema, etc.

Lexington has its own anchor orgs (Lexington Pride Center, PFLAG Central Kentucky,
Kentucky Black Pride, Imperial Court of Kentucky, New Song in the Bluegrass,
Sister Sound, Kentucky Bourbon Bears, Kentucky Fried Sisters — see config.SOURCES).

When operator wants any of these scraped automatically, replace this stub with a
multi-org scraper. See TulsaGays' specific_orgs.py for the JSON-LD-first / HTML-fallback
reference pattern.
"""

from typing import List, Dict


def scrape() -> List[Dict]:
    """Return [] — Lexington-specific org scrapers not yet written."""
    return []
