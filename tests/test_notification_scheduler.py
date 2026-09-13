import datetime as dt
from unittest.mock import Mock

from iqama.data.models import PrayerTimes
from iqama.services.notification_scheduler import (
    NotificationScheduler,
    ScheduledNotification,
    compute_notifications,
)


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


def test_includes_reminder_and_adhan_for_each_upcoming_prayer():
    times = make_times()
    now = dt.datetime(2026, 9, 6, 4, 0)

    notifications = compute_notifications(times, lead_minutes=10, now=now)

    # 5 prayers ahead x 2 notifications each (reminder + adhan).
    assert len(notifications) == 10
    fajr_reminder = next(n for n in notifications if n.prayer == "Fajr" and not n.is_adhan)
    assert fajr_reminder.when == dt.datetime(2026, 9, 6, 5, 2)
    fajr_adhan = next(n for n in notifications if n.prayer == "Fajr" and n.is_adhan)
    assert fajr_adhan.when == dt.datetime(2026, 9, 6, 5, 12)


def test_skips_reminder_when_lead_minutes_is_zero():
    times = make_times()
    now = dt.datetime(2026, 9, 6, 4, 0)

    notifications = compute_notifications(times, lead_minutes=0, now=now)

    assert all(n.is_adhan for n in notifications)
    assert len(notifications) == 5


def test_excludes_prayers_already_passed():
    times = make_times()
    # Between Fajr and Dhuhr: Fajr's reminder+adhan already passed.
    now = dt.datetime(2026, 9, 6, 6, 0)

    notifications = compute_notifications(times, lead_minutes=10, now=now)

    assert not any(n.prayer == "Fajr" for n in notifications)
    assert any(n.prayer == "Dhuhr" for n in notifications)


def test_excludes_reminder_when_lead_time_has_already_elapsed_but_prayer_has_not():
    times = make_times()
    # 5 minutes before Dhuhr: the 10-minute-lead reminder point has passed,
    # but the Adhan itself hasn't.
    now = dt.datetime(2026, 9, 6, 13, 5)

    notifications = compute_notifications(times, lead_minutes=10, now=now)

    dhuhr_notifications = [n for n in notifications if n.prayer == "Dhuhr"]
    assert len(dhuhr_notifications) == 1
    assert dhuhr_notifications[0].is_adhan is True


def test_no_notifications_after_isha():
    times = make_times()
    now = dt.datetime(2026, 9, 6, 22, 0)

    assert compute_notifications(times, lead_minutes=10, now=now) == []


def test_as_datetimes_combines_date_and_each_prayer_time():
    times = make_times()

    result = times.as_datetimes()

    assert result["Fajr"] == dt.datetime(2026, 9, 6, 5, 12)
    assert result["Isha"] == dt.datetime(2026, 9, 6, 21, 20)


def test_as_datetimes_accepts_an_override_date():
    times = make_times()

    result = times.as_datetimes(on_date=dt.date(2026, 9, 7))

    assert result["Fajr"] == dt.datetime(2026, 9, 7, 5, 12)


def make_scheduler() -> tuple[NotificationScheduler, Mock]:
    settings = Mock(notify_minutes=14)
    tray_icon = Mock()
    return NotificationScheduler(settings, tray_icon), tray_icon


def test_fire_drops_a_notification_far_past_its_intended_time():
    scheduler, tray_icon = make_scheduler()
    now = dt.datetime(2026, 9, 6, 23, 4)
    stale_entry = ScheduledNotification(
        when=dt.datetime(2026, 9, 6, 19, 50),
        prayer="Maghrib",
        is_adhan=True,
        prayer_when=dt.datetime(2026, 9, 6, 19, 50),
    )

    scheduler._fire(stale_entry, now=now)

    tray_icon.showMessage.assert_not_called()


def test_fire_sends_a_notification_within_the_stale_tolerance():
    scheduler, tray_icon = make_scheduler()
    now = dt.datetime(2026, 9, 6, 19, 51, 30)
    entry = ScheduledNotification(
        when=dt.datetime(2026, 9, 6, 19, 50),
        prayer="Maghrib",
        is_adhan=True,
        prayer_when=dt.datetime(2026, 9, 6, 19, 50),
    )

    scheduler._fire(entry, now=now)

    tray_icon.showMessage.assert_called_once()


def test_fire_reminder_body_uses_actual_remaining_time_not_configured_lead():
    scheduler, tray_icon = make_scheduler()
    now = dt.datetime(2026, 9, 6, 19, 30)
    entry = ScheduledNotification(
        when=now,
        prayer="Maghrib",
        is_adhan=False,
        prayer_when=now + dt.timedelta(minutes=3),
    )

    scheduler._fire(entry, now=now)

    title, body = tray_icon.showMessage.call_args[0][:2]
    assert title == "Maghrib soon"
    assert "3 minute" in body
    assert "14 minute" not in body
