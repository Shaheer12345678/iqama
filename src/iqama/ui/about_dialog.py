"""About dialog: app name, version, a short description, and a link to
the GitHub repo.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from ..config import APP_NAME, APP_VERSION, GITHUB_URL, resource_path

DESCRIPTION = (
    "Prayer times, reminders, and a weekly prayer log that live quietly "
    "in your system tray."
)


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setWindowIcon(QIcon(str(resource_path("icon.ico"))))
        self.setFixedWidth(340)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon(str(resource_path("icon.ico"))).pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel(f"<h2>{APP_NAME}</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        description_label = QLabel(DESCRIPTION)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        link_label = QLabel(f'<a href="{GITHUB_URL}">{GITHUB_URL}</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        close_button = QPushButton("Close")
        close_button.setDefault(True)
        close_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(description_label)
        layout.addWidget(link_label)
        layout.addSpacing(8)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignHCenter)
