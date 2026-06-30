import csv

def extract_csv(filepath):
    """Reads the recruiter CSV and returns a list of raw candidate dicts."""
    records = []
    try:
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "name": row.get("name", "").strip() or None,
                    "email": row.get("email", "").strip() or None,
                    "phone": row.get("phone", "").strip() or None,
                    "company": row.get("current_company", "").strip() or None,
                    "title": row.get("title", "").strip() or None,
                    "github_username": row.get("github_username", "").strip() or None,
                    "_source": "csv"
                })
    except FileNotFoundError:
        print(f"Warning: CSV file not found at {filepath}, skipping.")
    except Exception as e:
        print(f"Warning: failed to read CSV ({e}), skipping.")
    return records