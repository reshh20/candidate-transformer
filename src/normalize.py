import phonenumbers
from datetime import datetime

SKILL_MAP = {
    "js": "javascript",
    "javascript": "javascript",
    "py": "python",
    "python": "python",
    "golang": "go",
    "go": "go",
    "reactjs": "react",
    "react": "react",
}


COUNTRY_MAP = {
    "india": "IN",
    "ind": "IN",
    "in": "IN",
    "united states": "US",
    "usa": "US",
    "us": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "great britain": "GB",
    "canada": "CA",
    "australia": "AU",
}


def normalize_phone(raw, default_region="IN"):
    """Converts a messy phone string into E.164 format."""

    if not raw:
        return None

    try:
        parsed = phonenumbers.parse(raw, default_region)

        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )

    except phonenumbers.NumberParseException:
        pass

    return None


def normalize_skill(raw):
    """Maps a raw skill/language name to a canonical lowercase name."""

    if not raw:
        return None

    key = raw.strip().lower()

    return SKILL_MAP.get(key, key)


def normalize_date(raw):
    """Converts various date formats into YYYY-MM."""

    if not raw:
        return None

    formats_to_try = [
        "%Y-%m-%d",
        "%Y-%m",
        "%m/%Y",
        "%B %Y"
    ]

    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue

    return None


def normalize_country(raw):
    """Converts common country names into ISO-3166 alpha-2 codes."""

    if not raw:
        return None

    key = raw.strip().lower()

    return COUNTRY_MAP.get(key, raw.upper())


def normalize_years_experience(raw):
    """Converts years of experience into a numeric value."""

    if raw is None or raw == "":
        return None

    try:
        return float(raw)
    except ValueError:
        return None