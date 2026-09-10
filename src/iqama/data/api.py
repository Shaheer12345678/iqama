"""Thin client for the free Aladhan prayer-times API.

https://aladhan.com/prayer-times-api
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import requests

from .models import PrayerTimes

ALADHAN_BASE_URL = "https://api.aladhan.com/v1/timingsByCity"
REQUEST_TIMEOUT_SECONDS = 10


class AladhanAPIError(Exception):
    """Raised for any network failure, timeout, or unexpected API response.

    Callers should catch this and fall back to cached data rather than
    let it crash the app -- a flaky connection is the normal case, not
    an exceptional one, for a background prayer-times tool.
    """


def _clean_time(raw: str) -> str:
    """Aladhan returns times like "05:12 (MDT)"; strip the tz annotation."""
    return raw.split(" ")[0].strip()


def fetch_prayer_times(
    city: str,
    country: str,
    method: int,
    timezone_name: Optional[str] = None,
    date: Optional[dt.date] = None,
) -> PrayerTimes:
    """Fetch one day's prayer times for a city.

    `timezone_name` should be an IANA zone (e.g. "America/Edmonton") so the
    times Aladhan returns already match the user's local clock regardless
    of where its servers infer the city to be.

    Raises AladhanAPIError on any failure; never returns partial/garbage data.
    """
    target_date = date or dt.date.today()
    params = {"city": city, "country": country, "method": method}
    if timezone_name:
        params["timezonestring"] = timezone_name

    url = f"{ALADHAN_BASE_URL}/{target_date.strftime('%d-%m-%Y')}"

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise AladhanAPIError(f"Could not reach Aladhan API: {exc}") from exc
    except ValueError as exc:
        raise AladhanAPIError(f"Aladhan API returned invalid JSON: {exc}") from exc

    if payload.get("code") != 200:
        raise AladhanAPIError(f"Aladhan API error: {payload.get('status', 'unknown error')}")

    try:
        timings = payload["data"]["timings"]
        return PrayerTimes(
            date=target_date.isoformat(),
            city=city,
            country=country,
            method=method,
            fajr=_clean_time(timings["Fajr"]),
            dhuhr=_clean_time(timings["Dhuhr"]),
            asr=_clean_time(timings["Asr"]),
            maghrib=_clean_time(timings["Maghrib"]),
            isha=_clean_time(timings["Isha"]),
            fetched_at=dt.datetime.now().isoformat(timespec="seconds"),
            source="live",
        )
    except KeyError as exc:
        raise AladhanAPIError(f"Aladhan API response missing expected field: {exc}") from exc


def validate_city_name(city: str) -> bool:
    """Basic sanity check for a city name typed into the settings form."""
    city = city.strip()
    if len(city) < 2:
        return False
    return all(ch.isalpha() or ch in " -.'" for ch in city)
