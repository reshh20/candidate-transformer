from src.merge import build_partial_from_csv, build_partial_from_github, merge_records


def test_merge_resolves_name_conflict_in_favor_of_github():
    csv_row = {
        "name": "Octo Cat", "email": "octocat@github.com", "phone": "9876543210",
        "company": "GitHub Inc", "title": "Mascot Engineer", "github_username": "octocat"
    }
    csv_partial = build_partial_from_csv(csv_row)

    fake_github_data = {
        "name": "The Octocat",
        "bio": "Mascot for GitHub",
        "github_url": "https://github.com/octocat",
        "languages": ["Python", "Go"]
    }
    github_partial = build_partial_from_github(fake_github_data)

    merged = merge_records([csv_partial, github_partial])

    assert merged["full_name"] == "The Octocat"  # GitHub should win
    conflict_notes = [p for p in merged["provenance"] if p["field"] == "full_name"]
    assert len(conflict_notes) == 1
    assert "Octo Cat" in conflict_notes[0]["note"]


def test_merge_handles_csv_only_record_gracefully():
    csv_row = {
        "name": "Priya Singh", "email": None, "phone": "9123456780",
        "company": "Infosys", "title": "Data Analyst", "github_username": None
    }
    csv_partial = build_partial_from_csv(csv_row)
    merged = merge_records([csv_partial, None])  # no github data at all

    assert merged["full_name"] == "Priya Singh"
    assert merged["emails"] == []
    assert merged["overall_confidence"] >= 0


def test_merge_confidence_follows_design_policy():
    csv_row = {
        "name": "Test Person", "email": "test@x.com", "phone": "9876543210",
        "company": "X", "title": "Y", "github_username": "someuser"
    }
    csv_partial = build_partial_from_csv(csv_row)
    github_partial = build_partial_from_github({
        "name": "Test Person", "bio": None,
        "github_url": "https://github.com/someuser", "languages": ["Python"]
    })
    merged = merge_records([csv_partial, github_partial])

    # full_name confirmed by both sources -> should score 1.0 per design doc
    assert merged["field_confidence"]["full_name"] == 1.0
    # phones only came from CSV (structured) -> should score 0.6
    assert merged["field_confidence"]["phones"] == 0.6