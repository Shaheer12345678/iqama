"""The system tray shell: icon, "time until next prayer" tooltip, and the
right-click menu. Owns the top-level windows (settings, weekly log, about)
as lazily-created singletons so re-opening one just re-shows it.
"""
from __future__ import annotations

import datetime as dt
import logging

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from ..config import APP_NAME, resource_path
from ..data.db import Database
from ..services.notification_scheduler import NotificationScheduler
from ..services.prayer_service import PrayerService, format_time_remaining
from ..services.settings import Settings
from ..services import startup

logger = logging.getLogger(__name__)

TOOLTIP_REFRESH_MS = 30_000
# A gap this much larger than TOOLTIP_REFRESH_MS between ticks means the
# process was suspended (system sleep), not just scheduler jitter.
CLOCK_DRIFT_TOLERANCE = dt.timedelta(minutes=2)


class TrayApplication:
    def __init__(self, app: QApplication) -> None:
        self._app = app
        self.settings = Settings()
        self.db = Database()
        self.prayer_service = PrayerService(self.db, self.settings)
        self._notification_scheduler = NotificationScheduler(self.settings, parent=app)

        self._today_times = None
        self._settings_window = None
        self._weekly_log_window = None

        self._tray_icon = QSystemTrayIcon(QIcon(str(resource_path("icon.ico"))), app)
        self._tray_icon.setToolTip(APP_NAME)
        self._build_menu()

        self._last_tick = dt.datetime.now()
        self._tooltip_timer = QTimer(app)
        self._tooltip_timer.setInterval(TOOLTIP_REFRESH_MS)
        self._tooltip_timer.timeout.connect(self._on_tooltip_tick)

        self._midnight_timer = QTimer(app)
        self._midnight_timer.setSingleShot(True)
        self._midnight_timer.timeout.connect(self._on_midnight)

    def start(self) -> None:
        self._tray_icon.show()
        self._refresh_prayer_times()
        self._tooltip_timer.start()
        self._schedule_midnight_refresh()

    # -- menu construction --------------------------------------------
    def _build_menu(self) -> None:
        menu = QMenu()

        open_settings_action = QAction("Open Settings", menu)
        open_settings_action.triggered.connect(self._open_settings)
        menu.addAction(open_settings_action)

        weekly_log_action = QAction("Show Weekly Log", menu)
        weekly_log_action.triggered.connect(self._open_weekly_log)
        menu.addAction(weekly_log_action)

        menu.addSeparator()

        self._startup_action = QAction("Start with Windows", menu)
        self._startup_action.setCheckable(True)
        self._startup_action.setChecked(startup.is_enabled())
        self._startup_action.toggled.connect(self._on_toggle_startup)
        menu.addAction(self._startup_action)

        menu.addSeparator()

        about_action = QAction("About", menu)
        about_action.triggered.connect(self._show_about)
        menu.addAction(about_action)

        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._app.quit)
        menu.addAction(quit_action)

        self._tray_icon.setContextMenu(menu)
        self._tray_icon.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._refresh_tooltip()

    # -- prayer times / tooltip -----------------------------------------
    def _on_tooltip_tick(self) -> None:
        now = dt.datetime.now()
        if now - self._last_tick > CLOCK_DRIFT_TOLERANCE:
            logger.info("Detected a wall-clock jump (likely system sleep); rescheduling notifications.")
            self._notification_scheduler.schedule_for_today(self._today_times)
        self._last_tick = now
        self._refresh_tooltip()

    def _refresh_prayer_times(self, force_refresh: bool = False) -> None:
        self._today_times = self.prayer_service.get_today_times(force_refresh=force_refresh)
        self._refresh_tooltip()
        self._notification_scheduler.schedule_for_today(self._today_times)

    def _refresh_tooltip(self) -> None:
        if self._today_times is None:
            self._tray_icon.setToolTip(f"{APP_NAME}: prayer times unavailable (offline)")
            return

        upcoming = self.prayer_service.next_prayer(self._today_times)
        if upcoming is None:
            self._tray_icon.setToolTip(f"{APP_NAME}: all of today's prayers have passed")
            return

        name, when = upcoming
        remaining = when - dt.datetime.now()
        tooltip = f"{name} in {format_time_remaining(remaining)} ({when:%H:%M})"
        if self.prayer_service.last_error:
            tooltip += " (cached times, server unreachable)"
        self._tray_icon.setToolTip(tooltip)

    # -- midnight refresh -------------------------------------------------
    def _schedule_midnight_refresh(self) -> None:
        now = dt.datetime.now()
        next_midnight = (now + dt.timedelta(days=1)).replace(
            hour=0, minute=0, second=5, microsecond=0
        )
        self._midnight_timer.start(int((next_midnight - now).total_seconds() * 1000))

    def _on_midnight(self) -> None:
        self._refresh_prayer_times(force_refresh=True)
        self._schedule_midnight_refresh()

    # -- menu actions ---------------------------------------------------
    def _open_settings(self) -> None:
        from .settings_window import SettingsWindow

        if self._settings_window is None:
            self._settings_window = SettingsWindow(self.settings, on_saved=self._on_settings_saved)
        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def _on_settings_saved(self) -> None:
        self._refresh_prayer_times(force_refresh=True)

    def _open_weekly_log(self) -> None:
        from .weekly_log_window import WeeklyLogWindow

        if self._weekly_log_window is None:
            self._weekly_log_window = WeeklyLogWindow(self.db)
        self._weekly_log_window.show()
        self._weekly_log_window.raise_()
        self._weekly_log_window.activateWindow()

    def _show_about(self) -> None:
        from .about_dialog import AboutDialog

        AboutDialog().exec()

    def _on_toggle_startup(self, checked: bool) -> None:
        try:
            startup.set_enabled(checked)
            self.settings.start_with_windows = checked
        except OSError as exc:
            logger.error("Failed to update Windows startup registration: %s", exc)
            QMessageBox.warning(
                None, APP_NAME, f"Could not update the Windows startup setting:\n{exc}"
            )
            self._startup_action.blockSignals(True)
            self._startup_action.setChecked(not checked)
            self._startup_action.blockSignals(False)
