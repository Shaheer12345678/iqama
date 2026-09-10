from iqama.config import PRAYER_NAMES
from iqama.data.db import Database, WeeklyLogRepository


def test_unlogged_prayer_defaults_to_not_prayed(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = WeeklyLogRepository(db)

    assert repo.is_prayed("2026-09-06", "Fajr") is False


def test_set_prayed_persists(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = WeeklyLogRepository(db)

    repo.set_prayed("2026-09-06", "Fajr", True)

    assert repo.is_prayed("2026-09-06", "Fajr") is True


def test_toggle_flips_state_and_returns_new_value(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = WeeklyLogRepository(db)

    first = repo.toggle("2026-09-06", "Dhuhr")
    second = repo.toggle("2026-09-06", "Dhuhr")

    assert first is True
    assert second is False
    assert repo.is_prayed("2026-09-06", "Dhuhr") is False


def test_get_week_includes_all_requested_dates_and_prayers(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = WeeklyLogRepository(db)
    repo.set_prayed("2026-09-06", "Fajr", True)

    week = repo.get_week(["2026-09-06", "2026-09-07"])

    assert set(week.keys()) == {"2026-09-06", "2026-09-07"}
    assert set(week["2026-09-06"].keys()) == set(PRAYER_NAMES)
    assert week["2026-09-06"]["Fajr"] is True
    assert week["2026-09-06"]["Dhuhr"] is False
    assert week["2026-09-07"]["Fajr"] is False


def test_get_week_with_empty_dates_returns_empty_dict(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = WeeklyLogRepository(db)

    assert repo.get_week([]) == {}


def test_completion_percentage_reflects_prayed_count(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = WeeklyLogRepository(db)

    assert repo.completion_percentage("2026-09-06") == 0.0

    repo.set_prayed("2026-09-06", "Fajr", True)
    repo.set_prayed("2026-09-06", "Dhuhr", True)

    # 2 of 5 prayers logged as prayed.
    assert repo.completion_percentage("2026-09-06") == 40.0

    for prayer in PRAYER_NAMES:
        repo.set_prayed("2026-09-06", prayer, True)

    assert repo.completion_percentage("2026-09-06") == 100.0
