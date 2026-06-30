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

def normalize_phone(raw, default_region="IN"):
    """Converts a messy phone string into E.164 format, e.g. +919876543210."""
    if not raw:
        return None
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
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
    """Converts various date formats into YYYY-MM. Returns None if unparseable."""
    if not raw:
        return None
    formats_to_try = ["%Y-%m-%d", "%Y-%m", "%m/%Y", "%B %Y"]
    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue
    return None