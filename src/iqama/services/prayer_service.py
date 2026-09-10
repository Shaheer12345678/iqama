"""Bridges the data layer (API + SQLite cache) with what the tray UI needs:
today's times (fetched live, falling back to cache when offline) and the
next upcoming prayer.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

from ..data.api import AladhanAPIError, fetch_prayer_times
from ..data.db import Database, PrayerTimesRepository
from ..data.models import PrayerTimes

logger = logging.getLogger(__name__)


class PrayerService:
    """Owns "what are today's times" so the UI never has to fall back itself."""

    def __init__(self, db: Database, settings) -> None:
        self._repo = PrayerTimesRepository(db)
        self._settings = settings
        self.last_error: Optional[str] = None

    def get_today_times(self, force_refresh: bool = False) -> Optional[PrayerTimes]:
        """Today's times: from cache if it matches current settings, else
        fetched live; on any fetch failure, falls back to whatever is
        cached (even if stale/mismatched) so the app degrades instead of
        going blank. Returns None only if there's truly nothing to show.
        """
        today = dt.date.today().isoformat()
        self.last_error = None

        if not force_refresh:
            cached = self._repo.get(today)
            if cached and self._matches_settings(cached):
                return cached

        try:
            tz_name = _local_timezone_name()
        except Exception:  # pragma: no cover - defensive, tzlocal is normally reliable
            tz_name = None

        try:
            times = fetch_prayer_times(
                city=self._settings.city,
                country=self._settings.country,
                method=self._settings.method,
                timezone_name=tz_name,
            )
            self._repo.save(times)
            return times
        except AladhanAPIError as exc:
            logger.warning("Prayer time fetch failed, falling back to cache: %s", exc)
            self.last_error = str(exc)
            return self._repo.get(today)

    def _matches_settings(self, times: PrayerTimes) -> bool:
        return times.city == self._settings.city and times.method == self._settings.method

    @staticmethod
    def next_prayer(
        times: PrayerTimes, now: Optional[dt.datetime] = None
    ) -> Optional[tuple[str, dt.datetime]]:
        """The next prayer today that hasn't happened yet, or None if all
        of today's prayers have already passed.
        """
        now = now or dt.datetime.now()
        for name, when in times.as_datetimes(now.date()).items():
            if when > now:
                return name, when
        return None


def _local_timezone_name() -> Optional[str]:
    from tzlocal import get_localzone_name

    return get_localzone_name()


def format_time_remaining(delta: dt.timedelta) -> str:
    total_minutes = max(0, int(delta.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"
