"""Desktop notifications via plyer (cross-platform; uses the native
Windows toast/balloon API under the hood on Windows).
"""
from __future__ import annotations

import logging

from ..config import APP_NAME, resource_path

logger = logging.getLogger(__name__)


def send_desktop_notification(title: str, message: str, timeout: int = 10) -> bool:
    """Show a desktop notification. Returns False (and logs) on failure
    instead of raising -- a broken notification backend shouldn't crash
    a background reminder app.
    """
    try:
        from plyer import notification

        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            app_icon=str(resource_path("icon.ico")),
            timeout=timeout,
        )
        return True
    except Exception:
        logger.exception("Failed to show desktop notification: %s / %s", title, message)
        return False
