"""Entry point for the Iqama tray application."""
from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from .config import APP_NAME, ORG_NAME
from .ui.tray import TrayApplication

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> int:
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
