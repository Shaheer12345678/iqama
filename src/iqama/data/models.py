"""Plain data structures shared by the API client and the SQLite layer."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional

from ..config import PRAYER_NAMES


@dataclass
class PrayerTimes:
    """One day's set of prayer times, in "HH:MM" 24-hour local time."""

    date: str  # ISO format, e.g. "2026-09-06"
    city: str
    country: str
    method: int
    fajr: str
    dhuhr: str
    asr: str
    maghrib: str
    isha: str
    fetched_at: Optional[str] = None
    source: str = "live"  # "live" (just fetched) or "cache" (loaded from SQLite)

    def as_dict(self) -> dict[str, str]:
        """Map of prayer name -> time string, in PRAYER_NAMES order."""
        return {name: getattr(self, name.lower()) for name in PRAYER_NAMES}

    def as_datetimes(self, on_date: Optional[dt.date] = None) -> dict[str, dt.datetime]:
        """Map of prayer name -> full datetime, combining each "HH:MM"
        time with a calendar date (defaults to this record's own date).
        """
        base_date = on_date or dt.date.fromisoformat(self.date)
        result = {}
        for name in PRAYER_NAMES:
            hour, minute = map(int, getattr(self, name.lower()).split(":"))
            result[name] = dt.datetime.combine(base_date, dt.time(hour, minute))
        return result
