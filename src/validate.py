class ValidationError(Exception):
    pass


def validate_against_config(projected_record, config):
    """
    Checks that the projected output matches what the config asked for:
    - required fields are present (unless on_missing == 'omit', which is allowed to skip them)
    - basic type checks (string, string[], number)
    """
    on_missing = config.get("on_missing", "null")
    errors = []

    for field_def in config["fields"]:
        path = field_def["path"]
        required = field_def.get("required", False)
        expected_type = field_def.get("type")

        if path not in projected_record:
            if required and on_missing != "omit":
                errors.append(f"Required field '{path}' is missing from output.")
            continue  # field intentionally omitted, that's fine

        value = projected_record[path]
        if value is None:
            continue  # nulls are allowed unless required+error, already handled in project()

        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Field '{path}' should be a string, got {type(value).__name__}.")
        elif expected_type == "string[]" and not isinstance(value, list):
            errors.append(f"Field '{path}' should be a list, got {type(value).__name__}.")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"Field '{path}' should be a number, got {type(value).__name__}.")

    if errors:
        raise ValidationError("; ".join(errors))

    return True