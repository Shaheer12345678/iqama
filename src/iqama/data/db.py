"""SQLite persistence: today's prayer-times cache and the weekly prayer log.

Two tables, deliberately simple:

  prayer_times_cache  -- one row per calendar day already fetched
  weekly_log          -- one row per (date, prayer) marking it prayed
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from ..config import PRAYER_NAMES, get_app_data_dir
from .models import PrayerTimes

SCHEMA = """
CREATE TABLE IF NOT EXISTS prayer_times_cache (
    date TEXT PRIMARY KEY,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    method INTEGER NOT NULL,
    fajr TEXT NOT NULL,
    dhuhr TEXT NOT NULL,
    asr TEXT NOT NULL,
    maghrib TEXT NOT NULL,
    isha TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_log (
    date TEXT NOT NULL,
    prayer TEXT NOT NULL,
    prayed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (date, prayer)
);
"""


def get_db_path() -> Path:
    return get_app_data_dir() / "iqama.db"


class Database:
    """Owns the sqlite3 connection and guarantees the schema exists."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_db_path()
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()


class PrayerTimesRepository:
    """Reads/writes the cached prayer times for a given calendar day."""

    def __init__(self, db: Database):
        self._db = db

    def get(self, date: str) -> Optional[PrayerTimes]:
        row = self._db.connection.execute(
            "SELECT * FROM prayer_times_cache WHERE date = ?", (date,)
        ).fetchone()
        if row is None:
            return None
        return PrayerTimes(
            date=row["date"],
            city=row["city"],
            country=row["country"],
            method=row["method"],
            fajr=row["fajr"],
            dhuhr=row["dhuhr"],
            asr=row["asr"],
            maghrib=row["maghrib"],
            isha=row["isha"],
            fetched_at=row["fetched_at"],
            source="cache",
        )

    def save(self, times: PrayerTimes) -> None:
        self._db.connection.execute(
            """
            INSERT INTO prayer_times_cache
                (date, city, country, method, fajr, dhuhr, asr, maghrib, isha, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                city=excluded.city, country=excluded.country, method=excluded.method,
                fajr=excluded.fajr, dhuhr=excluded.dhuhr, asr=excluded.asr,
                maghrib=excluded.maghrib, isha=excluded.isha, fetched_at=excluded.fetched_at
            """,
            (
                times.date, times.city, times.country, times.method,
                times.fajr, times.dhuhr, times.asr, times.maghrib, times.isha,
                times.fetched_at,
            ),
        )
        self._db.connection.commit()


class WeeklyLogRepository:
    """Tracks which prayers the user has checked off, per day."""

    def __init__(self, db: Database):
        self._db = db

    def is_prayed(self, date: str, prayer: str) -> bool:
        row = self._db.connection.execute(
            "SELECT prayed FROM weekly_log WHERE date = ? AND prayer = ?",
            (date, prayer),
        ).fetchone()
        return bool(row["prayed"]) if row else False

    def get_week(self, dates: list[str]) -> dict[str, dict[str, bool]]:
        """Return {date: {prayer_name: prayed}} for every date/prayer pair.

        Dates with no log rows yet come back as all-False rather than
        being omitted, so callers can always index the full grid.
        """
        result = {date: {prayer: False for prayer in PRAYER_NAMES} for date in dates}
        if not dates:
            return result
        placeholders = ",".join("?" for _ in dates)
        rows = self._db.connection.execute(
            f"SELECT date, prayer, prayed FROM weekly_log WHERE date IN ({placeholders})",
            dates,
        ).fetchall()
        for row in rows:
            if row["date"] in result and row["prayer"] in result[row["date"]]:
                result[row["date"]][row["prayer"]] = bool(row["prayed"])
        return result

    def set_prayed(self, date: str, prayer: str, prayed: bool) -> None:
        self._db.connection.execute(
            """
            INSERT INTO weekly_log (date, prayer, prayed) VALUES (?, ?, ?)
            ON CONFLICT(date, prayer) DO UPDATE SET prayed=excluded.prayed
            """,
            (date, prayer, int(prayed)),
        )
        self._db.connection.commit()

    def toggle(self, date: str, prayer: str) -> bool:
        """Flip a cell's prayed state and return the new value."""
        new_value = not self.is_prayed(date, prayer)
        self.set_prayed(date, prayer, new_value)
        return new_value

    def completion_percentage(self, date: str) -> float:
        statuses = self.get_week([date])[date]
        prayed_count = sum(1 for prayed in statuses.values() if prayed)
        return (prayed_count / len(PRAYER_NAMES)) * 100
