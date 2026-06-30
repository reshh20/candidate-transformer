import re
from src.normalize import normalize_phone, normalize_skill


class ProjectionError(Exception):
    """Raised when a required field is missing and on_missing is set to 'error'."""
    pass


def _resolve_path(record, path):
    """
    Reads a value out of the merged record using a simple path syntax.
    Supports: "full_name", "emails[0]", "skills[].name"
    Returns None if the path doesn't resolve to anything.
    """
    # Case: "skills[].name" -> grab .name from every item in the skills list
    list_all_match = re.match(r"^(\w+)\[\]\.(\w+)$", path)
    if list_all_match:
        list_field, sub_field = list_all_match.groups()
        items = record.get(list_field, [])
        return [item.get(sub_field) for item in items if isinstance(item, dict) and item.get(sub_field) is not None]

    # Case: "emails[0]" -> grab index 0 from the emails list
    index_match = re.match(r"^(\w+)\[(\d+)\]$", path)
    if index_match:
        list_field, idx = index_match.groups()
        items = record.get(list_field, [])
        idx = int(idx)
        return items[idx] if idx < len(items) else None

    # Case: plain field name, e.g. "full_name" or "links"
    return record.get(path)


def _apply_normalize(value, normalize_type):
    """Applies the requested normalization to a value (or list of values)."""
    if value is None:
        return None
    if normalize_type == "E164":
        if isinstance(value, list):
            return [normalize_phone(v) for v in value]
        return normalize_phone(value)
    if normalize_type == "canonical":
        if isinstance(value, list):
            return [normalize_skill(v) for v in value]
        return normalize_skill(value)
    return value


def project(record, config):
    """
    Reshapes a full merged canonical record into the structure requested by config.
    Does NOT modify the original record (the canonical record stays untouched).
    """
    output = {}
    on_missing = config.get("on_missing", "null")

    for field_def in config["fields"]:
        out_path = field_def["path"]
        source_path = field_def.get("from", out_path)
        required = field_def.get("required", False)

        value = _resolve_path(record, source_path)

        if field_def.get("normalize"):
            value = _apply_normalize(value, field_def["normalize"])

        is_missing = value is None or value == [] or value == ""

        if is_missing:
            if on_missing == "error" and required:
                raise ProjectionError(f"Required field '{out_path}' is missing.")
            elif on_missing == "omit":
                continue  # skip adding this key entirely
            else:  # "null" (default)
                output[out_path] = None
        else:
            output[out_path] = value

    if config.get("include_confidence", False):
        output["overall_confidence"] = record.get("overall_confidence")
        output["field_confidence"] = record.get("field_confidence")

    if config.get("include_provenance", False):
        output["provenance"] = record.get("provenance")

    return output