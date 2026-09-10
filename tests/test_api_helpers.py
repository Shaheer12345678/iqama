from iqama.data.api import _clean_time, validate_city_name


def test_clean_time_strips_timezone_annotation():
    assert _clean_time("05:12 (MDT)") == "05:12"


def test_clean_time_leaves_plain_time_untouched():
    assert _clean_time("13:10") == "13:10"


def test_validate_city_name_accepts_normal_names():
    assert validate_city_name("Calgary") is True
    assert validate_city_name("St. John's") is True
    assert validate_city_name("Al-Madinah") is True


def test_validate_city_name_rejects_empty_or_too_short():
    assert validate_city_name("") is False
    assert validate_city_name("  ") is False
    assert validate_city_name("A") is False


def test_validate_city_name_rejects_digits_and_symbols():
    assert validate_city_name("Calgary123") is False
    assert validate_city_name("<script>") is False
