"""Settings window: city, calculation method, and notification lead time.

A real top-level QWidget (not a modal dialog) so it can be reopened from
the tray menu and stays alive in the background between edits.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..config import APP_NAME, CALCULATION_METHODS
from ..data.api import validate_city_name

ERROR_STYLE = "color: #b00020;"
SUCCESS_STYLE = "color: #1a7f37;"


class SettingsWindow(QWidget):
    def __init__(self, settings, on_saved=None, parent=None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._on_saved = on_saved

        self.setWindowTitle(f"{APP_NAME} Settings")
        self.setMinimumWidth(380)

        self._city_edit = QLineEdit()
        self._city_edit.setPlaceholderText("e.g. Calgary  or  Calgary, Canada")

        self._method_combo = QComboBox()
        for method_id, method_name in sorted(CALCULATION_METHODS.items(), key=lambda kv: kv[1]):
            self._method_combo.addItem(method_name, userData=method_id)

        self._notify_spin = QSpinBox()
        self._notify_spin.setRange(0, 30)
        self._notify_spin.setSuffix(" min")

        form = QFormLayout()
        form.addRow("City:", self._city_edit)
        form.addRow("Calculation method:", self._method_combo)
        form.addRow("Notify before prayer:", self._notify_spin)

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)

        save_button = QPushButton("Save")
        save_button.setDefault(True)
        save_button.clicked.connect(self._on_save)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._on_cancel)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._status_label)
        layout.addLayout(button_row)

        self._load_from_settings()

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._load_from_settings()
        super().showEvent(event)

    def _load_from_settings(self) -> None:
        self._city_edit.setText(
            f"{self._settings.city}, {self._settings.country}"
            if self._settings.country
            else self._settings.city
        )
        index = self._method_combo.findData(self._settings.method)
        self._method_combo.setCurrentIndex(index if index >= 0 else 0)
        self._notify_spin.setValue(self._settings.notify_minutes)
        self._status_label.setText("")

    def _on_save(self) -> None:
        raw_city = self._city_edit.text().strip()
        if "," in raw_city:
            city_part, _, country_part = raw_city.partition(",")
            city = city_part.strip()
            country = country_part.strip() or self._settings.country
        else:
            city = raw_city
            country = self._settings.country

        if not validate_city_name(city):
            self._status_label.setStyleSheet(ERROR_STYLE)
            self._status_label.setText(
                "Please enter a valid city name (letters only, at least 2 characters)."
            )
            return

        self._settings.city = city
        self._settings.country = country
        self._settings.method = self._method_combo.currentData()
        self._settings.notify_minutes = self._notify_spin.value()
        self._settings.sync()

        self._status_label.setStyleSheet(SUCCESS_STYLE)
        self._status_label.setText("Settings saved. Prayer times will refresh shortly.")

        if self._on_saved:
            self._on_saved()

    def _on_cancel(self) -> None:
        self._load_from_settings()
        self.close()
