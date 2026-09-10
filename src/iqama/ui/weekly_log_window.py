"""Weekly log window: a click-to-toggle prayer grid for the current week,
plus a completion-percentage bar chart underneath.
"""
from __future__ import annotations

import datetime as dt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..config import APP_NAME, PRAYER_NAMES
from ..data.db import WeeklyLogRepository

CHECK_MARK = "✓"
CHECKED_COLOR = QColor("#dff5e1")
UNCHECKED_COLOR = QColor("#ffffff")
BAR_COLOR = "#123a52"


class WeeklyLogWindow(QWidget):
    def __init__(self, db, parent=None) -> None:
        super().__init__(parent)
        self._repo = WeeklyLogRepository(db)
        self._week_dates: list[dt.date] = self._current_week_dates()

        self.setWindowTitle(f"{APP_NAME} - Weekly Log")
        self.resize(600, 500)

        self._table = QTableWidget(len(PRAYER_NAMES), len(self._week_dates))
        self._table.setVerticalHeaderLabels(PRAYER_NAMES)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.cellClicked.connect(self._on_cell_clicked)

        self._figure = Figure(figsize=(5, 2.2))
        self._axes = self._figure.add_subplot(111)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._canvas.setMinimumHeight(180)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table, stretch=3)
        layout.addWidget(self._canvas, stretch=2)

        self._populate_table()
        self._update_chart()

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        # Re-derive the week in case the app has been running across a
        # week boundary since this window was last shown.
        self._week_dates = self._current_week_dates()
        self._populate_table()
        self._update_chart()
        super().showEvent(event)

    @staticmethod
    def _current_week_dates() -> list[dt.date]:
        today = dt.date.today()
        monday = today - dt.timedelta(days=today.weekday())
        return [monday + dt.timedelta(days=offset) for offset in range(7)]

    def _populate_table(self) -> None:
        self._table.setHorizontalHeaderLabels(
            [date.strftime("%a\n%m/%d") for date in self._week_dates]
        )
        iso_dates = [date.isoformat() for date in self._week_dates]
        week_status = self._repo.get_week(iso_dates)

        for row, prayer in enumerate(PRAYER_NAMES):
            for col, date in enumerate(iso_dates):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._apply_cell_state(item, week_status[date][prayer])
                self._table.setItem(row, col, item)

    def _apply_cell_state(self, item: QTableWidgetItem, prayed: bool) -> None:
        font = item.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)
        item.setFont(font)
        item.setText(CHECK_MARK if prayed else "")
        item.setBackground(CHECKED_COLOR if prayed else UNCHECKED_COLOR)

    def _on_cell_clicked(self, row: int, col: int) -> None:
        prayer = PRAYER_NAMES[row]
        date = self._week_dates[col].isoformat()
        new_state = self._repo.toggle(date, prayer)
        self._apply_cell_state(self._table.item(row, col), new_state)
        self._update_chart()

    def _update_chart(self) -> None:
        iso_dates = [date.isoformat() for date in self._week_dates]
        percentages = [self._repo.completion_percentage(date) for date in iso_dates]
        labels = [date.strftime("%a") for date in self._week_dates]

        self._axes.clear()
        self._axes.bar(labels, percentages, color=BAR_COLOR)
        self._axes.set_ylim(0, 100)
        self._axes.set_ylabel("% prayed")
        self._axes.set_title("This week's completion")
        self._figure.tight_layout()
        self._canvas.draw_idle()
