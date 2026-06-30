from src.extract_csv import extract_csv


def test_extract_csv_reads_all_rows():
    rows = extract_csv("sample_inputs/recruiter.csv")
    assert len(rows) == 4


def test_extract_csv_missing_email_becomes_none():
    rows = extract_csv("sample_inputs/recruiter.csv")
    priya = next(r for r in rows if r["name"] == "Priya Singh")
    assert priya["email"] is None


def test_extract_csv_missing_file_does_not_crash():
    rows = extract_csv("sample_inputs/this_file_does_not_exist.csv")
    assert rows == []