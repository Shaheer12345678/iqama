"""Schedules the two desktop notifications per prayer -- a lead-time
reminder and one right at the Adhan time -- using QTimer.singleShot.
"""
from __future__ import annotations

import datetime as dt
from typing import NamedTuple, Optional

from PySide6.QtCore import QTimer

from ..data.models import PrayerTimes
from .notifier import send_desktop_notification


class ScheduledNotification(NamedTuple):
    when: dt.datetime
    prayer: str
    is_adhan: bool
    prayer_when: dt.datetime  # the prayer's own Adhan time, for recomputing "in N minutes" at fire time


# A slept/suspended machine can leave a QTimer's countdown paused for hours;
# anything more than this far past its intended moment is dropped instead of
# shown with a stale or now-false countdown.
STALE_TOLERANCE = dt.timedelta(minutes=2)


def compute_notifications(
    times: PrayerTimes, lead_minutes: int, now: Optional[dt.datetime] = None
) -> list[ScheduledNotification]:
    """Every still-upcoming notification for today's prayer times.

    Two per prayer -- a lead-time reminder (skipped if lead_minutes is 0)
    and one at the Adhan time -- filtered to only what's still ahead of
    `now`, so notifications for prayers that already passed aren't fired
    late when this is (re)computed mid-day.
    """
    now = now or dt.datetime.now()
    notifications: list[ScheduledNotification] = []

    for prayer, prayer_dt in times.as_datetimes(now.date()).items():
        if lead_minutes > 0:
            reminder_dt = prayer_dt - dt.timedelta(minutes=lead_minutes)
            if reminder_dt > now:
                notifications.append(ScheduledNotification(reminder_dt, prayer, False, prayer_dt))

        if prayer_dt > now:
            notifications.append(ScheduledNotification(prayer_dt, prayer, True, prayer_dt))

    return notifications


class NotificationScheduler:
    """Owns the live QTimers backing today's notifications.

    Call schedule_for_today() again (e.g. after a settings change, the
    midnight refresh, or a detected wall-clock jump) to replace whatever
    is currently pending.
    """

    def __init__(self, settings, parent=None) -> None:
        self._settings = settings
        self._parent = parent
        self._timers: list[QTimer] = []

    def schedule_for_today(self, times: Optional[PrayerTimes]) -> None:
        self.cancel_all()
        if times is None:
            return
        for entry in compute_notifications(times, self._settings.notify_minutes):
            self._schedule(entry)

    def _schedule(self, entry: ScheduledNotification) -> None:
        delay_ms = int((entry.when - dt.datetime.now()).total_seconds() * 1000)
        if delay_ms <= 0:
            return

        timer = QTimer(self._parent)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._fire(entry))
        timer.start(delay_ms)
        self._timers.append(timer)

    def _fire(self, entry: ScheduledNotification, now: Optional[dt.datetime] = None) -> None:
        now = now or dt.datetime.now()
        if now - entry.when > STALE_TOLERANCE:
            return

        if entry.is_adhan:
            send_desktop_notification(f"{entry.prayer}: Adhan", f"It's time for {entry.prayer} prayer.")
        else:
            minutes = max(0, round((entry.prayer_when - now).total_seconds() / 60))
            plural = "s" if minutes != 1 else ""
            send_desktop_notification(
                f"{entry.prayer} soon", f"{entry.prayer} is in {minutes} minute{plural}."
            )

    def cancel_all(self) -> None:
        for timer in self._timers:
            timer.stop()
        self._timers.clear()
