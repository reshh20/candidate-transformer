from src.normalize import normalize_phone, normalize_skill, normalize_date


def test_normalize_phone_valid_indian_number():
    result = normalize_phone("9876543210")
    assert result == "+919876543210"


def test_normalize_phone_with_dashes_and_country_code():
    result = normalize_phone("+91-98765-43211")
    assert result == "+919876543211"


def test_normalize_phone_empty_input_returns_none():
    result = normalize_phone("")
    assert result is None


def test_normalize_phone_garbage_input_returns_none():
    result = normalize_phone("not-a-phone-number")
    assert result is None


def test_normalize_skill_maps_to_canonical():
    assert normalize_skill("JS") == "javascript"
    assert normalize_skill("Go") == "go"


def test_normalize_skill_unknown_skill_passes_through_lowercased():
    assert normalize_skill("Rust") == "rust"


def test_normalize_date_standard_format():
    assert normalize_date("2023-05-01") == "2023-05"


def test_normalize_date_garbage_returns_none():
    assert normalize_date("not a date") is None