import csv

def extract_csv(filepath):
    records = []

    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skills: semicolon-separated string → list
                # e.g. "python;java;react" → ["python", "java", "react"]
                raw_skills = row.get("skills", "").strip()
                skills_list = [
                    s.strip()
                    for s in raw_skills.split(";")
                    if s.strip()
                ] if raw_skills else []

                records.append({
                    # Basic candidate info
                    "name":             row.get("name", "").strip() or None,
                    "email":            row.get("email", "").strip() or None,
                    "phone":            row.get("phone", "").strip() or None,

                    # Current job
                    "company":          row.get("current_company", "").strip() or None,
                    "title":            row.get("title", "").strip() or None,

                    # GitHub linkage
                    "github_username":  row.get("github_username", "").strip() or None,

                    # Canonical profile fields
                    "headline":         row.get("headline", "").strip() or None,
                    "location":         row.get("location", "").strip() or None,
                    "years_experience": row.get("years_experience", "").strip() or None,
                    "skills":           skills_list,  # always a list, never None

                    # Social links
                    "linkedin":         row.get("linkedin", "").strip() or None,

                    # Experience details
                    "start_date":       row.get("start_date", "").strip() or None,
                    "end_date":         row.get("end_date", "").strip() or None,
                    "summary":          row.get("summary", "").strip() or None,

                    # Education details
                    "institution":      row.get("institution", "").strip() or None,
                    "degree":           row.get("degree", "").strip() or None,
                    "field_of_study":   row.get("field", "").strip() or None,
                    "end_year":         row.get("end_year", "").strip() or None,

                    "_source": "csv"
                })

    except FileNotFoundError:
        print(f"Warning: CSV file not found at {filepath}, skipping.")
    except Exception as e:
        print(f"Warning: failed to read CSV ({e}), skipping.")

    return records