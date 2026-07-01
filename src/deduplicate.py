def _normalize_name(name):
    if not name:
        return ""
    return " ".join(name.lower().strip().split())

def _normalize_company(experience_list):
    if not experience_list:
        return ""
    company = experience_list[0].get("company") if experience_list else None
    if not company:
        return ""
    return company.lower().strip()

def _profiles_match(a, b):
    # Rule 1 — shared email (strongest signal)
    emails_a = set(e.lower() for e in a.get("emails", []) if e)
    emails_b = set(e.lower() for e in b.get("emails", []) if e)
    if emails_a and emails_b and emails_a & emails_b:
        return True

    # Rule 2 — same name + same company
    name_a = _normalize_name(a.get("full_name"))
    name_b = _normalize_name(b.get("full_name"))
    company_a = _normalize_company(a.get("experience", []))
    company_b = _normalize_company(b.get("experience", []))

    if name_a and name_b and name_a == name_b:
        if company_a and company_b and company_a == company_b:
            return True
        if not company_a and not company_b:
            return True

    return False

def _merge_two_profiles(a, b):
    combined_provenance = a.get("provenance", []) + b.get("provenance", [])
    combined_provenance.append({
        "field": "candidate", "source": "deduplication",
        "method": "name_company_match",
        "note": f"Merged duplicate profiles: '{a.get('full_name')}' and '{b.get('full_name')}'"
    })
    merged = dict(a)
    merged["emails"] = list(dict.fromkeys(a.get("emails", []) + b.get("emails", [])))
    merged["phones"] = list(dict.fromkeys(a.get("phones", []) + b.get("phones", [])))
    merged["skills"] = a.get("skills", []) + b.get("skills", [])
    merged["experience"] = a.get("experience", []) + b.get("experience", [])
    merged["provenance"] = combined_provenance
    for field in ["full_name", "location", "years_experience", "headline"]:
        if not merged.get(field) and b.get(field):
            merged[field] = b[field]
    if not merged.get("links", {}).get("github") and b.get("links", {}).get("github"):
        merged["links"]["github"] = b["links"]["github"]
    return merged

def deduplicate(profiles):
    result = []
    used = set()
    for i, profile in enumerate(profiles):
        if i in used:
            continue
        current = profile
        for j, other in enumerate(profiles):
            if j <= i or j in used:
                continue
            if _profiles_match(current, other):
                print(f"Deduplication: merging '{current.get('full_name')}' "
                      f"and '{other.get('full_name')}' as same candidate.")
                current = _merge_two_profiles(current, other)
                used.add(j)
        result.append(current)
    return result