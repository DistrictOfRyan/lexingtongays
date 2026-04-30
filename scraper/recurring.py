"""STUB — Tulsa-specific hardcoded recurring events.
TulsaGays' version computes which weekly/monthly recurring events fall in the
current Mon-Sun week (Lambda Bowling, HHHH, Council Oak rehearsals, etc.).

Lexington's recurring-event candidates from config.SOURCES:
  - TransKentucky (1st Saturday monthly, 7:30pm)
  - Last WednesGays (Last Wednesday monthly)
  - Lexington Queer Craft Club (monthly)
  - HotMess Sports leagues (seasonal)
  - Frontrunners Lexington (weekly run/walk)

When operator wants these auto-injected each week, replace this stub with a
recurring-event calculator. See TulsaGays' recurring.py for the reference pattern
that handles weekday math, monthly Nth-day-of-month, etc.
"""

from typing import List, Dict


def scrape() -> List[Dict]:
    """Return [] — Lexington recurring-event calculator not yet written."""
    return []
