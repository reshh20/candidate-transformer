from src.normalize import (
    normalize_phone,
    normalize_skill,
    normalize_date,
    normalize_country,
    normalize_years_experience,
)

STRUCTURED_SOURCES = {"csv"}
UNSTRUCTURED_SOURCES = {"github"}


def field_confidence(sources_for_field):
    """Implements design doc confidence policy exactly."""
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
    # --- location: parse "Chennai IN" → {city, region, country} ---
    location = None
    if row.get("location"):
        parts = row["location"].rsplit(" ", 1)
        location = {
            "city":    parts[0] if len(parts) == 2 else row["location"],
            "region":  None,
            "country": normalize_country(parts[1]) if len(parts) == 2 else None
        }

    # --- years_experience: use normalize function directly, no double conversion ---
    years_exp = normalize_years_experience(row.get("years_experience"))

    # --- skills: already a list from extract_csv, just normalize each name ---
    csv_skills = [
        {
            "name":       normalize_skill(s),
            "confidence": 0.6,
            "sources":    ["csv"]
        }
        for s in row.get("skills", [])   # safely iterate list, never None
        if s
    ]

    # --- experience: includes dates and summary ---
    experience = []
    if row.get("company") or row.get("title"):
        experience.append({
            "company": row.get("company"),
            "title":   row.get("title"),
            "start":   normalize_date(row.get("start_date")),
            "end":     normalize_date(row.get("end_date")),
            "summary": row.get("summary")
        })

    # --- education: only add if at least institution or degree present ---
    education = []
    if row.get("institution") or row.get("degree"):
        education.append({
            "institution": row.get("institution"),
            "degree":      row.get("degree"),
            "field":       row.get("field_of_study"),
            "end_year":    row.get("end_year")
        })

    # --- links: linkedin from CSV, github filled in later by GitHub source ---
    links = {
        "linkedin":  row.get("linkedin"),
        "github":    None,
        "portfolio": None,
        "other":     []
    }

    return {
        "full_name":        row.get("name"),
        "emails":           [row["email"]] if row.get("email") else [],
        "phones":           [normalize_phone(row["phone"])] if row.get("phone") else [],
        "location":         location,
        "years_experience": years_exp,
        "headline":         row.get("headline"),
        "skills":           csv_skills,
        "experience":       experience,
        "education":        education,
        "links":            links,
        "_source":          "csv",
        "_provenance": [
            {"field": "full_name",        "source": "csv", "method": "direct"},
            {"field": "emails",           "source": "csv", "method": "direct"},
            {"field": "phones",           "source": "csv", "method": "normalize_phone"},
            {"field": "location",         "source": "csv", "method": "direct"},
            {"field": "years_experience", "source": "csv", "method": "normalize_years_experience"},
            {"field": "skills",           "source": "csv", "method": "direct"},
            {"field": "headline",         "source": "csv", "method": "direct"},
            {"field": "links.linkedin",   "source": "csv", "method": "direct"},
            {"field": "education",        "source": "csv", "method": "direct"},
        ]
    }


def build_partial_from_github(gh_data):
    if not gh_data:
        return None
    skills = [
        {"name": normalize_skill(lang), "confidence": 0.3, "sources": ["github"]}
        for lang in gh_data.get("languages", [])
    ]
    return {
        "full_name":        gh_data.get("name"),
        "emails":           [],
        "phones":           [],
        "location":         None,
        "years_experience": None,
        "headline":         gh_data.get("bio"),
        "skills":           skills,
        "experience":       [],
        "education":        [],
        "links": {
            "linkedin":  None,
            "github":    gh_data.get("github_url"),
            "portfolio": None,
            "other":     []
        },
        "_source": "github",
        "_provenance": [
            {"field": "skills",       "source": "github", "method": "language_list"},
            {"field": "links.github", "source": "github", "method": "direct"},
            {"field": "headline",     "source": "github", "method": "direct"},
        ]
    }


def merge_records(partials):
    partials = [p for p in partials if p]
    merged = {
        "full_name":        None,
        "emails":           [],
        "phones":           [],
        "location":         None,
        "years_experience": None,
        "headline":         None,
        "skills":           [],
        "experience":       [],
        "education":        [],
        "links": {
            "linkedin":  None,
            "github":    None,
            "portfolio": None,
            "other":     []
        },
        "provenance": []
    }

    # --- full_name conflict resolution: GitHub preferred when both present and differ ---
    csv_partial    = next((p for p in partials if p["_source"] == "csv"),    None)
    github_partial = next((p for p in partials if p["_source"] == "github"), None)

    csv_name    = csv_partial["full_name"]    if csv_partial    else None
    github_name = github_partial["full_name"] if github_partial else None

    name_sources = []
    if csv_name:    name_sources.append("csv")
    if github_name: name_sources.append("github")

    if github_name and csv_name and github_name != csv_name:
        merged["full_name"] = github_name
        merged["provenance"].append({
            "field":  "full_name",
            "source": "github",
            "method": "conflict_resolved",
            "note":   f"CSV said '{csv_name}', GitHub said '{github_name}'. GitHub preferred (self-reported)."
        })
    elif github_name:
        merged["full_name"] = github_name
    elif csv_name:
        merged["full_name"] = csv_name

    # --- track which sources contributed to each field (for confidence scoring) ---
    field_sources = {
        "full_name":        name_sources,
        "emails":           [],
        "phones":           [],
        "skills":           [],
        "links.github":     [],
        "links.linkedin":   [],
        "location":         [],
        "years_experience": [],
        "headline":         [],
        "education":        [],
    }

    for p in partials:
        # emails
        merged["emails"] += [e for e in p.get("emails", []) if e]
        if p.get("emails"):
            field_sources["emails"].append(p["_source"])

        # phones
        merged["phones"] += [ph for ph in p.get("phones", []) if ph]
        if p.get("phones"):
            field_sources["phones"].append(p["_source"])

        # skills — combine from all sources
        merged["skills"] += p.get("skills", [])
        if p.get("skills"):
            field_sources["skills"].append(p["_source"])

        # experience — combine from all sources
        merged["experience"] += p.get("experience", [])

        # education — combine from all sources
        merged["education"] += p.get("education", [])
        if p.get("education"):
            field_sources["education"].append(p["_source"])

        # links.github
        if p.get("links", {}).get("github"):
            merged["links"]["github"] = p["links"]["github"]
            field_sources["links.github"].append(p["_source"])

        # links.linkedin
        if p.get("links", {}).get("linkedin"):
            merged["links"]["linkedin"] = p["links"]["linkedin"]
            field_sources["links.linkedin"].append(p["_source"])

        # headline — first non-null wins
        if p.get("headline") and not merged["headline"]:
            merged["headline"] = p["headline"]
            field_sources["headline"].append(p["_source"])

        # location — first non-null wins
        if p.get("location") and not merged["location"]:
            merged["location"] = p["location"]
            field_sources["location"].append(p["_source"])

        # years_experience — first non-null wins
        if p.get("years_experience") is not None and merged["years_experience"] is None:
            merged["years_experience"] = p["years_experience"]
            field_sources["years_experience"].append(p["_source"])

        # provenance — collect from all sources except full_name (handled above)
        merged["provenance"] += [
            pr for pr in p.get("_provenance", [])
            if pr["field"] != "full_name"
        ]

    # dedupe emails and phones
    merged["emails"] = list(dict.fromkeys(merged["emails"]))
    merged["phones"] = list(dict.fromkeys(merged["phones"]))

    # --- confidence scoring: per field, then overall average ---
    confidences = {
        field: field_confidence(srcs)
        for field, srcs in field_sources.items()
    }
    merged["field_confidence"]   = confidences
    merged["overall_confidence"] = round(
        sum(confidences.values()) / len(confidences), 2
    )

    return merged