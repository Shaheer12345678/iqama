import datetime as dt

from iqama.data.models import PrayerTimes
from iqama.services.prayer_service import PrayerService, format_time_remaining


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
