"""
api/osint_pipeline/normalizers_v1.py
====================================
Forensic Normalization & Sanitization Engine for OsintNeoAi (v1 Archive).
Standardizes entity names, APNs, addresses (USPS Pub 28 CASS), and timestamps (ISO 8601 UTC).
"""

import re
import datetime
from typing import Optional, Union, List, Dict, Any

# Corporate suffix patterns (longest first)
CORP_SUFFIXES = [
    r"\bL\.L\.C\b\.?", r"\bLLC\b\.?",
    r"\bI\.N\.C\b\.?", r"\bINC\b\.?",
    r"\bC\.O\.R\.P\b\.?", r"\bCORP\b\.?", r"\bCORPORATION\b",
    r"\bL\.P\b\.?", r"\bLP\b\.?",
    r"\bL\.T\.D\b\.?", r"\bLTD\b\.?", r"\bLIMITED\b",
    r"\bC\.O\b\.?", r"\bCO\b\.?", r"\bCOMPANY\b",
    r"\bP\.C\b\.?", r"\bPC\b\.?",
    r"\bP\.L\.L\.C\b\.?", r"\bPLLC\b\.?",
]

# USPS Pub 28 Street Suffix Expansions
STREET_SUFFIX_MAP = {
    "ST": "STREET", "STR": "STREET",
    "AVE": "AVENUE", "AV": "AVENUE",
    "BLVD": "BOULEVARD", "BLV": "BOULEVARD", "BOUL": "BOULEVARD",
    "RD": "ROAD",
    "LN": "LANE",
    "CT": "COURT",
    "DR": "DRIVE", "DRV": "DRIVE",
    "WAY": "WAY",
    "PKWY": "PARKWAY", "PKY": "PARKWAY", "PARKWY": "PARKWAY",
    "CIR": "CIRCLE", "CIRC": "CIRCLE",
    "HWY": "HIGHWAY", "HIGHWY": "HIGHWAY",
    "PL": "PLACE",
    "TER": "TERRACE", "TERR": "TERRACE",
    "TRL": "TRAIL", "TL": "TRAIL",
    "ALY": "ALLEY",
    "EXPY": "EXPRESSWAY",
    "LOOP": "LOOP",
    "ROW": "ROW",
    "RUN": "RUN",
    "SQ": "SQUARE",
}

# Directional Expansions
DIRECTIONAL_MAP = {
    "N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
    "NE": "NORTHEAST", "NW": "NORTHWEST", "SE": "SOUTHEAST", "SW": "SOUTHWEST",
}

# Secondary Unit Expansions
UNIT_MAP = {
    "STE": "SUITE",
    "APT": "APARTMENT",
    "BLDG": "BUILDING",
    "FL": "FLOOR",
    "RM": "ROOM",
    "DEPT": "DEPARTMENT",
    "OFC": "OFFICE",
    "SPC": "SPACE",
    "BSMT": "BASEMENT",
}


def normalize_entity_name(name: Optional[str]) -> str:
    """
    Normalize entity or person name:
    - Upper-cases & trims whitespace
    - Strips corporate legal suffixes (LLC, INC, CORP, etc.)
    - Removes punctuation noise while retaining alphanumeric chars and spaces
    """
    if not name:
        return ""
    cleaned = str(name).upper().strip()
    
    # Strip corporate suffixes
    for suff in CORP_SUFFIXES:
        cleaned = re.sub(suff, " ", cleaned, flags=re.IGNORECASE)
    
    # Remove punctuation
    cleaned = re.sub(r"[-.,&/()'\"]", " ", cleaned)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_apn(apn: Optional[str]) -> str:
    """
    Standardize Assessor Parcel Numbers (APNs):
    - Strips non-alphanumerics and common prefixes (APN, PARCEL, etc.)
    - Canonical Orange County 8-digit format: ###-###-## (e.g. 178-431-14)
    - Canonical 10-digit format: ###-###-#### (e.g. 178-431-1400)
    """
    if not apn:
        return ""
    cleaned = re.sub(r"\b(APN|PARCEL|NO|NUMBER)\b[:#\s]*", "", str(apn), flags=re.IGNORECASE)
    raw = re.sub(r"[^0-9A-Za-z]", "", cleaned).upper()
    if not raw:
        return ""
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[0:3]}-{raw[3:6]}-{raw[6:8]}"
    elif len(raw) == 10 and raw.isdigit():
        return f"{raw[0:3]}-{raw[3:6]}-{raw[6:10]}"
    return raw


def normalize_address(address: Optional[str]) -> str:
    """
    Cleanse and standardize real estate street addresses per USPS Pub 28:
    - Normalizes abbreviations (ST -> STREET, AVE -> AVENUE, LN -> LANE, etc.)
    - Directionals (N -> NORTH, S -> SOUTH, etc.)
    - Unit designators (STE -> SUITE, APT -> APARTMENT, # -> UNIT)
    """
    if not address:
        return ""
    addr = str(address).upper().strip()
    
    # Replace '#' with 'UNIT '
    addr = re.sub(r"#\s*", "UNIT ", addr)
    
    # Remove periods and extra commas
    addr = addr.replace(".", " ")
    addr = re.sub(r",\s*,+", ",", addr)
    
    # Tokenize and expand abbreviations
    tokens = re.split(r"(\s+|[,])", addr)
    expanded = []
    for tok in tokens:
        word = tok.strip()
        if not word:
            expanded.append(tok)
            continue
        if word in STREET_SUFFIX_MAP:
            expanded.append(STREET_SUFFIX_MAP[word])
        elif word in DIRECTIONAL_MAP:
            expanded.append(DIRECTIONAL_MAP[word])
        elif word in UNIT_MAP:
            expanded.append(UNIT_MAP[word])
        else:
            expanded.append(tok)
            
    result = "".join(expanded)
    # Clean multiple spaces and comma spacing
    result = re.sub(r"\s+", " ", result).strip()
    result = re.sub(r"\s*,\s*", ", ", result)
    return result


def normalize_timestamp(ts: Optional[Union[str, int, float, datetime.datetime]] = None) -> str:
    """
    Normalize timestamp to ISO 8601 UTC canonical string.
    Format: YYYY-MM-DDTHH:MM:SS+00:00 (or with microseconds)
    """
    if ts is None or str(ts).strip() in ("", "None", "null", "nan"):
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if isinstance(ts, (int, float)):
        # Epoch timestamp
        try:
            return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat()
        except Exception:
            return datetime.datetime.now(datetime.timezone.utc).isoformat()
            
    if isinstance(ts, datetime.datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        else:
            ts = ts.astimezone(datetime.timezone.utc)
        return ts.isoformat()
        
    s = str(ts).strip()
    # Try ISO formats
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]:
        try:
            dt = datetime.datetime.strptime(s.replace("Z", "+0000"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.isoformat()
        except Exception:
            continue
            
    # Try fromisoformat directly
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.isoformat()
    except Exception:
        pass

    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def normalize_lead_payload(raw: Dict[str, Any], default_case_id: str = "CASE-0001") -> Dict[str, Any]:
    """
    Normalizes a full lead or victim intake payload.
    """
    case_id = raw.get("case_id") or raw.get("id") or default_case_id
    source = raw.get("source") or "mutual_aid_intake"
    entity_name = raw.get("entity_name") or raw.get("victim_name") or raw.get("name") or "Anonymous"
    
    aliases = raw.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [a.strip() for a in aliases.split(",") if a.strip()]
    norm_aliases = [normalize_entity_name(a) for a in aliases if normalize_entity_name(a)]
    
    raw_addr = raw.get("address") or raw.get("location") or ""
    norm_addr = normalize_address(raw_addr)
    
    raw_apn = raw.get("apn") or ""
    norm_apn = normalize_apn(raw_apn)
    
    lat = raw.get("lat") or raw.get("latitude")
    lon = raw.get("lon") or raw.get("longitude")
    try:
        lat = float(lat) if lat is not None else None
    except Exception:
        lat = None
    try:
        lon = float(lon) if lon is not None else None
    except Exception:
        lon = None
        
    ts = normalize_timestamp(raw.get("timestamp") or raw.get("created_at"))
    
    return {
        "case_id": str(case_id),
        "source": str(source),
        "entity_name": normalize_entity_name(entity_name),
        "raw_entity_name": str(entity_name),
        "aliases": norm_aliases,
        "address": norm_addr,
        "raw_address": str(raw_addr),
        "apn": norm_apn,
        "lat": lat,
        "lon": lon,
        "timestamp": ts,
        "summary": str(raw.get("summary", "")),
        "incident_type": str(raw.get("incident_type", "General Inquiry")),
        "contact_info": str(raw.get("contact_info", "")),
        "status": str(raw.get("status", "INGESTED"))
    }
