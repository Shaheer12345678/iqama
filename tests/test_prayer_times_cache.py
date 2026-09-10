from iqama.data.db import Database, PrayerTimesRepository
from iqama.data.models import PrayerTimes


def make_times(date: str = "2026-09-06") -> PrayerTimes:
    return PrayerTimes(
        date=date,
        city="Calgary",
        country="Canada",
        method=2,
        fajr="05:12",
        dhuhr="13:10",
        asr="16:45",
        maghrib="19:50",
        isha="21:20",
        fetched_at="2026-09-06T08:00:00",
        source="live",
    )


def test_get_returns_none_when_not_cached(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = PrayerTimesRepository(db)

    assert repo.get("2026-09-06") is None


def test_save_then_get_round_trips(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = PrayerTimesRepository(db)
    times = make_times()

    repo.save(times)
    cached = repo.get("2026-09-06")

    assert cached is not None
    assert cached.fajr == "05:12"
    assert cached.isha == "21:20"
    assert cached.city == "Calgary"
    assert cached.source == "cache"


def test_save_overwrites_existing_day(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = PrayerTimesRepository(db)
    repo.save(make_times())

    updated = make_times()
    updated.fajr = "05:15"
    repo.save(updated)

    cached = repo.get("2026-09-06")
    assert cached.fajr == "05:15"


def test_different_days_do_not_collide(tmp_path):
    db = Database(db_path=tmp_path / "test.db")
    repo = PrayerTimesRepository(db)
    repo.save(make_times("2026-09-06"))
    repo.save(make_times("2026-09-07"))

    assert repo.get("2026-09-06").date == "2026-09-06"
    assert repo.get("2026-09-07").date == "2026-09-07"


def test_data_persists_across_connections(tmp_path):
    db_path = tmp_path / "test.db"
    db1 = Database(db_path=db_path)
    PrayerTimesRepository(db1).save(make_times())
    db1.close()

    db2 = Database(db_path=db_path)
    cached = PrayerTimesRepository(db2).get("2026-09-06")
    assert cached is not None
    assert cached.fajr == "05:12"
