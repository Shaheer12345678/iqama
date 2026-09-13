"""Entry point for the Iqama tray application."""
from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from .config import APP_NAME, ORG_NAME
from .ui.tray import TrayApplication

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

AUMID = "ShaheerShakir.Iqama"


def _register_app_identity() -> None:
    """So Windows attributes notifications/taskbar grouping to Iqama
    instead of falling back to the interpreter (e.g. "Python 3.11").
    Cosmetic only -- must never block startup.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        result = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(AUMID)
        logger.info("Registered Windows AppUserModelID %r (result=%s)", AUMID, result)
    except (AttributeError, OSError):
        logger.warning("Could not register the Windows AppUserModelID.", exc_info=True)


def main() -> int:
    _register_app_identity()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    # A tray app has no main window; without this, closing the last
    # (possibly hidden) window would silently kill the whole app.
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None, APP_NAME, "No system tray was detected on this machine. Iqama cannot run."
        )
        return 1

    tray = TrayApplication(app)
    tray.start()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
