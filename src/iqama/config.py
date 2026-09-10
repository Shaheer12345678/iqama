"""App-wide constants and filesystem/settings locations.

Kept dependency-free (no PySide6/requests imports) so it can be imported
from any layer, including unit tests, without pulling in the GUI stack.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Iqama"
APP_VERSION = "0.1.0"
ORG_NAME = "IqamaApp"
GITHUB_URL = "https://github.com/Shaheer12345678/iqama"

# Sensible defaults for a Calgary-based university MSA; all user-configurable.
DEFAULT_CITY = "Calgary"
DEFAULT_COUNTRY = "Canada"
DEFAULT_METHOD = 2  # Aladhan method id for ISNA
DEFAULT_NOTIFY_MINUTES = 10

PRAYER_NAMES = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

# A curated subset of Aladhan's documented calculation method IDs.
# Full list: https://aladhan.com/calculation-methods
CALCULATION_METHODS: dict[int, str] = {
    2: "Islamic Society of North America (ISNA)",
    3: "Muslim World League (MWL)",
    5: "Egyptian General Authority of Survey",
    4: "Umm Al-Qura University, Makkah",
    1: "University of Islamic Sciences, Karachi",
    16: "Dubai (experimental)",
    10: "Qatar",
    9: "Kuwait",
    11: "Majlis Ugama Islam Singapura, Singapore",
    13: "Diyanet Isleri Baskanligi, Turkey",
    7: "Institute of Geophysics, University of Tehran",
    15: "Moonsighting Committee Worldwide",
}


def get_app_data_dir() -> Path:
    """Per-user writable directory for the SQLite cache/log database.

    Uses %APPDATA%\\Iqama on Windows so a packaged .exe (no Python, no
    write access to Program Files) always has somewhere to store data.
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        app_dir = Path(appdata) / APP_NAME
    else:
        app_dir = Path.home() / f".{APP_NAME.lower()}"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def resource_path(relative: str) -> Path:
    """Locate a bundled resource such as the tray icon.

    Works both when running from source and from a PyInstaller-frozen
    .exe, whose bundled data files are extracted under sys._MEIPASS.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).resolve().parents[2]
    return base / "resources" / relative
