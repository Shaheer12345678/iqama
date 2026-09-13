import datetime as dt
from unittest.mock import Mock, patch

from iqama.data.api import AladhanAPIError
from iqama.data.db import Database, PrayerTimesRepository
from iqama.data.models import PrayerTimes
from iqama.services.prayer_service import PrayerService, format_time_remaining, refresh_is_stale


def make_times() -> PrayerTimes:
    return PrayerTimes(
        date="2026-09-06",
        city="Calgary",
        country="Canada",
        method=2,
        fajr="05:12",
        dhuhr="13:10",
        asr="16:45",
        maghrib="19:50",
        isha="21:20",
    )


def test_next_prayer_returns_the_first_one_still_ahead():
    times = make_times()
    now = dt.datetime(2026, 9, 6, 12, 0)

    result = PrayerService.next_prayer(times, now=now)

    assert result is not None
    name, when = result
    assert name == "Dhuhr"
    assert when == dt.datetime(2026, 9, 6, 13, 10)


def test_next_prayer_returns_none_after_isha():
    times = make_times()
    now = dt.datetime(2026, 9, 6, 22, 0)

    assert PrayerService.next_prayer(times, now=now) is None


def test_next_prayer_before_fajr_returns_fajr():
    times = make_times()
    now = dt.datetime(2026, 9, 6, 4, 0)

    name, when = PrayerService.next_prayer(times, now=now)

    assert name == "Fajr"
    assert when == dt.datetime(2026, 9, 6, 5, 12)


def test_format_time_remaining_hours_and_minutes():
    assert format_time_remaining(dt.timedelta(hours=2, minutes=15)) == "2h 15m"


def test_format_time_remaining_whole_hours():
    assert format_time_remaining(dt.timedelta(hours=3)) == "3h"


def test_format_time_remaining_minutes_only():
    assert format_time_remaining(dt.timedelta(minutes=45)) == "45m"


def test_format_time_remaining_negative_clamped_to_zero():
    assert format_time_remaining(dt.timedelta(minutes=-5)) == "0m"


def test_refresh_is_stale_true_when_the_date_has_changed():
    last_refresh = dt.date(2026, 9, 6)
    now = dt.datetime(2026, 9, 7, 0, 4)

    assert refresh_is_stale(last_refresh, now) is True


def test_refresh_is_stale_false_on_the_same_day():
    last_refresh = dt.date(2026, 9, 6)
    now = dt.datetime(2026, 9, 6, 23, 55)

    assert refresh_is_stale(last_refresh, now) is False


def test_refresh_is_stale_true_when_never_refreshed():
    now = dt.datetime(2026, 9, 6, 12, 0)

    assert refresh_is_stale(None, now) is True


def test_get_today_times_does_not_fall_back_to_a_prior_days_cache(tmp_path):
    # Only yesterday's row is cached; force_refresh skips the cache-hit
    # path, and the fetch itself fails (e.g. no network right after waking
    # up on a new day). The exact-date cache lookup must not hand back
    # yesterday's times as if they were today's.
    db = Database(db_path=tmp_path / "test.db")
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    PrayerTimesRepository(db).save(
        PrayerTimes(
            date=yesterday,
            city="Calgary",
            country="Canada",
            method=2,
            fajr="05:12",
            dhuhr="13:10",
            asr="16:45",
            maghrib="19:50",
            isha="21:20",
            fetched_at="2026-09-06T08:00:00",
        )
    )
    settings = Mock(city="Calgary", country="Canada", method=2)
    service = PrayerService(db, settings)

    with patch(
        "iqama.services.prayer_service.fetch_prayer_times",
        side_effect=AladhanAPIError("offline"),
    ):
        result = service.get_today_times(force_refresh=True)

    assert result is None
    assert service.last_error == "offline"
