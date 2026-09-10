"""Typed wrapper around QSettings for all user-configurable preferences.

Backed by the registry on Windows (HKCU\\Software\\IqamaApp\\Iqama), so
settings persist between launches with no file of our own to manage.
"""
from __future__ import annotations

from PySide6.QtCore import QSettings

from ..config import (
    APP_NAME,
    DEFAULT_CITY,
    DEFAULT_COUNTRY,
    DEFAULT_METHOD,
    DEFAULT_NOTIFY_MINUTES,
    ORG_NAME,
)


class Settings:
    def __init__(self) -> None:
        self._qs = QSettings(ORG_NAME, APP_NAME)

    @property
    def city(self) -> str:
        return str(self._qs.value("prayer/city", DEFAULT_CITY))

    @city.setter
    def city(self, value: str) -> None:
        self._qs.setValue("prayer/city", value)

    @property
    def country(self) -> str:
        return str(self._qs.value("prayer/country", DEFAULT_COUNTRY))

    @country.setter
    def country(self, value: str) -> None:
        self._qs.setValue("prayer/country", value)

    @property
    def method(self) -> int:
        return int(self._qs.value("prayer/method", DEFAULT_METHOD))

    @method.setter
    def method(self, value: int) -> None:
        self._qs.setValue("prayer/method", int(value))

    @property
    def notify_minutes(self) -> int:
        return int(self._qs.value("notifications/lead_minutes", DEFAULT_NOTIFY_MINUTES))

    @notify_minutes.setter
    def notify_minutes(self, value: int) -> None:
        self._qs.setValue("notifications/lead_minutes", int(value))

    @property
    def start_with_windows(self) -> bool:
        return bool(int(self._qs.value("startup/enabled", 0)))

    @start_with_windows.setter
    def start_with_windows(self, value: bool) -> None:
        self._qs.setValue("startup/enabled", int(bool(value)))

    def sync(self) -> None:
        self._qs.sync()
