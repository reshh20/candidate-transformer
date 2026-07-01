from src.normalize import normalize_phone, normalize_skill

STRUCTURED_SOURCES = {"csv"}
UNSTRUCTURED_SOURCES = {"github"}

def field_confidence(sources_for_field):
    sources_for_field = set(sources_for_field)
    if len(sources_for_field) >= 2:
        return 1.0
    if len(sources_for_field) == 1:
        only = next(iter(sources_for_field))
        if only in STRUCTURED_SOURCES:
            return 0.6
        if only in UNSTRUCTURED_SOURCES:
            return 0.3
    return 0.0

def build_partial_from_csv(row):
    # Parse "Chennai IN" into city + country
    location = None
    if row.get("location"):
        parts = row["location"].rsplit(" ", 1)
        location = {
            "city": parts[0] if len(parts) == 2 else row["location"],
            "region": None,
            "country": parts[1] if len(parts) == 2 else None
        }

    # Parse years_experience safely
    years_exp = None
    if row.get("years_experience"):
        try:
            years_exp = int(row["years_experience"])
        except ValueError:
            pass

    return {
        "full_name": row.get("name"),
        "emails": [row["email"]] if row.get("email") else [],
        "phones": [normalize_phone(row["phone"])] if row.get("phone") else [],
        "location": location,
        "years_experience": years_exp,
        "experience": [{
            "company": row.get("company"),
            "title": row.get("title"),
            "start": None, "end": None, "summary": None
        }] if row.get("company") or row.get("title") else [],
        "skills": [],
        "links": {"github": None, "linkedin": None, "portfolio": None, "other": []},
        "_source": "csv",
        "_provenance": [
            {"field": "full_name", "source": "csv", "method": "direct"},
            {"field": "emails", "source": "csv", "method": "direct"},
            {"field": "phones", "source": "csv", "method": "normalize_phone"},
            {"field": "location", "source": "csv", "method": "direct"},
            {"field": "years_experience", "source": "csv", "method": "direct"},
        ]
    }

def build_partial_from_github(gh_data):
    if not gh_data:
        return None
    skills = [{"name": normalize_skill(lang), "confidence": 0.6, "sources": ["github"]}
              for lang in gh_data.get("languages", [])]
    return {
        "full_name": gh_data.get("name"),
        "emails": [],
        "phones": [],
        "location": None,
        "years_experience": None,
        "experience": [],
        "skills": skills,
        "links": {"github": gh_data.get("github_url"), "linkedin": None, "portfolio": None, "other": []},
        "headline": gh_data.get("bio"),
        "_source": "github",
        "_provenance": [
            {"field": "skills", "source": "github", "method": "language_list"},
            {"field": "links.github", "source": "github", "method": "direct"},
        ]
    }

def merge_records(partials):
    partials = [p for p in partials if p]
    merged = {
        "full_name": None,
        "emails": [], "phones": [],
        "location": None,
        "years_experience": None,
        "skills": [], "experience": [], "education": [],
        "links": {"github": None, "linkedin": None, "portfolio": None, "other": []},
        "headline": None, "provenance": []
    }

    # full_name conflict resolution — GitHub preferred when both present and differ
    csv_partial = next((p for p in partials if p["_source"] == "csv"), None)
    github_partial = next((p for p in partials if p["_source"] == "github"), None)

    csv_name = csv_partial["full_name"] if csv_partial else None
    github_name = github_partial["full_name"] if github_partial else None
    name_sources = []
    if csv_name:
        name_sources.append("csv")
    if github_name:
        name_sources.append("github")

    if github_name and csv_name and github_name != csv_name:
        merged["full_name"] = github_name
        merged["provenance"].append({
            "field": "full_name", "source": "github", "method": "conflict_resolved",
            "note": f"CSV said '{csv_name}', GitHub said '{github_name}'. GitHub preferred (self-reported)."
        })
    elif github_name:
        merged["full_name"] = github_name
    elif csv_name:
        merged["full_name"] = csv_name

    field_sources = {
        "full_name": name_sources,
        "emails": [], "phones": [],
        "skills": [], "links.github": [],
        "location": [], "years_experience": []
    }

    for p in partials:
        merged["emails"] += [e for e in p.get("emails", []) if e]
        if p.get("emails"):
            field_sources["emails"].append(p["_source"])

        merged["phones"] += [ph for ph in p.get("phones", []) if ph]
        if p.get("phones"):
            field_sources["phones"].append(p["_source"])

        merged["skills"] += p.get("skills", [])
        if p.get("skills"):
            field_sources["skills"].append(p["_source"])

        merged["experience"] += p.get("experience", [])

        if p.get("links", {}).get("github"):
            merged["links"]["github"] = p["links"]["github"]
            field_sources["links.github"].append(p["_source"])

        if p.get("headline") and not merged["headline"]:
            merged["headline"] = p["headline"]

        if p.get("location") and not merged["location"]:
            merged["location"] = p["location"]
            field_sources["location"].append(p["_source"])

        if p.get("years_experience") and not merged["years_experience"]:
            merged["years_experience"] = p["years_experience"]
            field_sources["years_experience"].append(p["_source"])

        merged["provenance"] += [pr for pr in p.get("_provenance", [])
                                  if pr["field"] != "full_name"]

    merged["emails"] = list(dict.fromkeys(merged["emails"]))
    merged["phones"] = list(dict.fromkeys(merged["phones"]))

    confidences = {field: field_confidence(srcs) for field, srcs in field_sources.items()}
    merged["field_confidence"] = confidences
    merged["overall_confidence"] = round(sum(confidences.values()) / len(confidences), 2)

    return merged