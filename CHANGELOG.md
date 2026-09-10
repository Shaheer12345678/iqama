# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [0.1.0] - 2026-09-06
### Added
- Project scaffolding: `src/iqama` package layout, `pyproject.toml`, dev/runtime requirements.
- Data layer: SQLite schema and repositories for the daily prayer-times cache and the weekly prayer log (`iqama.data.db`).
- Aladhan API client (`iqama.data.api`) with local-timezone-aware fetching and graceful error handling.
- App-wide config module with calculation method IDs, defaults (Calgary, ISNA), and the per-user app data directory.
- Unit tests covering prayer-time caching, weekly log tracking, and API helper validation.
- System tray shell (`iqama.ui.tray`) with a placeholder icon, a tooltip showing time remaining until the next prayer, and a right-click menu (Open Settings, Show Weekly Log, Start with Windows, About, Quit).
- "Start with Windows" toggle wired to the Windows registry Run key (`iqama.services.startup`).
- `PrayerService` bridging the data layer with the UI: live fetch with cache fallback, and next-upcoming-prayer calculation.
- Settings window: city input (accepts "City, Country") with validation, calculation method dropdown, and a 0-30 minute notification lead-time spinbox, persisted via QSettings.
- Weekly log window: click-to-toggle prayer grid (Fajr-Isha x current week) backed by the SQLite weekly log, with a matplotlib bar chart of daily completion percentage below it.
- Desktop notifications (`iqama.services.notifier`, via plyer): a configurable lead-time reminder before each prayer plus a second notification at the Adhan time, scheduled with QTimer and rescheduled automatically on settings changes and at the midnight refresh.
- About dialog with app name, version, description, and a link to the GitHub repo.
- PyInstaller packaging (`packaging/iqama.spec` + `packaging/entry_point.py`) producing a single-file `Iqama.exe` that needs no Python installation to run. Verified by building and launching the packaged exe directly.
- README "How to Install" section for non-technical users, plus a "For Developers" section with build-from-source and packaging instructions.
