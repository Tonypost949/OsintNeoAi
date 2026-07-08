import sqlite3
import os
from utils.api_clients import abuseipdb_check, virustotal_ip, virustotal_domain


def score_entity(entity, relationships, file_scans):
    """
    Returns: {"score": 0-100, "level": "High/Medium/Low/Unknown", "factors": [...], "breakdown": {...}}
    """
    score = 0
    factors = []
    breakdown = {}

    notes = (entity.get("notes") or "").lower()
    label = (entity.get("label") or "").lower()
    category = (entity.get("category") or "").lower()
    source = (entity.get("source") or "").lower()
    risk_level = entity.get("risk_level") or "Unknown"

    # 1. Notes contain threat keywords: +15 each, max 40
    threat_keywords = ["weapon", "threat", "assault", "fraud", "rico", "warrant", "felony", "criminal", "arrest"]
    keyword_score = 0
    found_keywords = []
    for kw in threat_keywords:
        if kw in notes:
            keyword_score += 15
            found_keywords.append(kw)
    keyword_score = min(keyword_score, 40)
    if keyword_score > 0:
        score += keyword_score
        factors.append(f"Threat keywords in notes: {', '.join(found_keywords)}")
    breakdown["keywords"] = keyword_score

    # 2. Source is TruthFinder or court filing: +10
    if "truthfinder" in source or "court" in source:
        score += 10
        factors.append(f"Source: {entity.get('source')}")
        breakdown["source"] = 10
    else:
        breakdown["source"] = 0

    # 3. Has criminal/legal category: +20
    if "criminal" in category or "legal" in category:
        score += 20
        factors.append(f"Category: {entity.get('category')}")
        breakdown["category"] = 20
    else:
        breakdown["category"] = 0

    # 4. Number of relationships: each relationship +3, max 25
    entity_id = entity.get("entity_id")
    rel_count = 0
    for rel in relationships:
        if rel.get("source_entity") == entity_id or rel.get("target_entity") == entity_id:
            rel_count += 1
    rel_score = min(rel_count * 3, 25)
    if rel_score > 0:
        score += rel_score
        factors.append(f"Relationships: {rel_count} connections")
    breakdown["relationships"] = rel_score

    # 5. Geo proximity to known high-risk locations: +5
    high_risk_locs = ["santa ana", "compton"]
    geo_loc = (entity.get("geo_location") or "").lower()
    if any(loc in geo_loc for loc in high_risk_locs):
        score += 5
        factors.append(f"High-risk geo location: {entity.get('geo_location')}")
        breakdown["geo"] = 5
    else:
        breakdown["geo"] = 0

    # 6. File scans with names_found matching this entity's label: +5 per high-risk file, max 20
    file_score = 0
    matched_files = 0
    if label:
        for scan in file_scans:
            names_found = (scan.get("names_found") or "").lower()
            risk_flag = (scan.get("risk_flag") or "").lower()
            if label in names_found and risk_flag == "high":
                file_score += 5
                matched_files += 1
    file_score = min(file_score, 20)
    if file_score > 0:
        score += file_score
        factors.append(f"Linked to {matched_files} high-risk file scans")
    breakdown["files"] = file_score

    # 7. Multiple aliases in notes (AKA): +10
    if "aka" in notes or "alias" in notes:
        score += 10
        factors.append("Aliases detected (AKA)")
        breakdown["aliases"] = 10
    else:
        breakdown["aliases"] = 0

    # 8. Existing risk_level already High: baseline 60, Medium: 30
    baseline = 0
    if risk_level == "High":
        baseline = 60
    elif risk_level == "Medium":
        baseline = 30
    
    if baseline > 0:
        score += baseline
        factors.append(f"Initial risk level: {risk_level}")
    breakdown["baseline"] = baseline

    # 9. API threat intelligence
    api_score = 0
    api_factors = []
    label_val = entity.get("label", "")
    ent_type = entity.get("type", "")
    if ent_type == "IP Address" or ent_type == "IP Address":
        vt = virustotal_ip(label_val)
        if vt and "error" not in vt:
            mal = vt.get("malicious", 0)
            sus = vt.get("suspicious", 0)
            rep = vt.get("reputation", 0)
            if mal > 0:
                api_score += mal * 10
                api_factors.append(f"VirusTotal: {mal} malicious detections")
            if sus > 0:
                api_score += sus * 5
                api_factors.append(f"VirusTotal: {sus} suspicious detections")
            if rep < -10:
                api_score += 15
                api_factors.append(f"VirusTotal: Negative reputation ({rep})")
        abuse = abuseipdb_check(label_val)
        if abuse and "error" not in abuse:
            conf = abuse.get("abuse_confidence", 0)
            if conf > 50:
                api_score += 20
                api_factors.append(f"AbuseIPDB: {conf}% abuse confidence")
            elif conf > 20:
                api_score += 10
                api_factors.append(f"AbuseIPDB: {conf}% abuse confidence")
    elif ent_type == "Domain" or "domain" in ent_type.lower():
        vt = virustotal_domain(label_val)
        if vt and "error" not in vt:
            mal = vt.get("malicious", 0)
            if mal > 0:
                api_score += mal * 10
                api_factors.append(f"VirusTotal: {mal} malicious detections")
    if api_score > 0:
        score += min(api_score, 30)
        factors.extend(api_factors)
    breakdown["api_intel"] = min(api_score, 30)

    # Final normalization
    score = min(score, 100)
    
    level = "Unknown"
    if score >= 80:
        level = "High"
    elif score >= 50:
        level = "Medium"
    elif score >= 20:
        level = "Low"
    else:
        level = "Unknown"

    return {
        "score": score,
        "level": level,
        "factors": factors,
        "breakdown": breakdown
    }

def score_all_entities(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    entities = [dict(r) for r in cursor.execute("SELECT * FROM entities").fetchall()]
    relationships = [dict(r) for r in cursor.execute("SELECT * FROM relationships").fetchall()]
    file_scans = [dict(r) for r in cursor.execute("SELECT * FROM file_scan_results").fetchall()]
    
    conn.close()
    
    results = []
    for entity in entities:
        score_data = score_entity(entity, relationships, file_scans)
        results.append({
            "entity_id": entity["entity_id"],
            "label": entity["label"],
            "type": entity["type"],
            "old_level": entity["risk_level"],
            "score": score_data["score"],
            "level": score_data["level"],
            "factors": score_data["factors"],
            "breakdown": score_data["breakdown"]
        })
    
    return sorted(results, key=lambda x: x["score"], reverse=True)

def apply_scores_to_db(db_path, scores):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    level_rank = {"High": 3, "Medium": 2, "Low": 1, "Unknown": 0}
    upgraded_count = 0
    
    for score_info in scores:
        new_level = score_info["level"]
        old_level = score_info["old_level"]
        
        if level_rank.get(new_level, 0) > level_rank.get(old_level, 0):
            cursor.execute("UPDATE entities SET risk_level = ? WHERE entity_id = ?", (new_level, score_info["entity_id"]))
            upgraded_count += 1
            
    conn.commit()
    conn.close()
    return upgraded_count
