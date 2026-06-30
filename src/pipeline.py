import json
from src.extract_csv import extract_csv
from src.extract_github import extract_github
from src.merge import build_partial_from_csv, build_partial_from_github, merge_records

def run_pipeline(csv_path):
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

if __name__ == "__main__":
    result = run_pipeline("sample_inputs/recruiter.csv")
    print(json.dumps(result, indent=2))