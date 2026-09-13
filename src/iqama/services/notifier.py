"""Desktop notifications via the app's own system tray icon.

Uses QSystemTrayIcon.showMessage() rather than a standalone toast library:
Qt's Windows backend registers its own toast notifier for the running
process, so notifications are attributed to this app. A raw Shell_NotifyIcon
balloon (the previous approach) carries no such identity and always falls
back to whatever the OS resolves for the calling executable.
"""
from __future__ import annotations

import logging

from PySide6.QtWidgets import QSystemTrayIcon

logger = logging.getLogger(__name__)


def send_desktop_notification(
    tray_icon: QSystemTrayIcon, title: str, message: str, timeout: int = 10
) -> bool:
    """Show a desktop notification via the given tray icon. Returns False
    (and logs) on failure instead of raising -- a broken notification
    backend shouldn't crash a background reminder app.
    """
    try:
        tray_icon.showMessage(
            title, message, QSystemTrayIcon.MessageIcon.Information, timeout * 1000
        )
        return True
    except Exception:
        logger.exception("Failed to show desktop notification: %s / %s", title, message)
        return False
