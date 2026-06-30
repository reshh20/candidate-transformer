import json
from src.extract_csv import extract_csv
from src.extract_github import extract_github
from src.merge import build_partial_from_csv, build_partial_from_github, merge_records
from src.project import project
from src.validate import validate_against_config


def run_pipeline(csv_path):
    """Builds the FULL canonical records (unchanged from Phase 4)."""
    csv_rows = extract_csv(csv_path)
    profiles = []

    for i, row in enumerate(csv_rows):
        partial_csv = build_partial_from_csv(row)
        partial_github = None
        if row.get("github_username"):
            gh_data = extract_github(row["github_username"])
            partial_github = build_partial_from_github(gh_data)
        merged = merge_records([partial_csv, partial_github])
        merged["candidate_id"] = f"cand_{i+1}"
        profiles.append(merged)

    return profiles


def run_pipeline_with_config(csv_path, config_path):
    """Builds full records, projects each through the config, then validates the result."""
    profiles = run_pipeline(csv_path)
    with open(config_path) as f:
        config = json.load(f)

    projected = []
    for p in profiles:
        result = project(p, config)
        validate_against_config(result, config)  # raises ValidationError if something's wrong
        projected.append(result)

    return projected


if __name__ == "__main__":
    # default: full canonical output, no config applied
    result = run_pipeline("sample_inputs/recruiter.csv")
    print(json.dumps(result, indent=2))