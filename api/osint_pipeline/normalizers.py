"""
api/osint_pipeline/normalizers.py
=================================
Forensic Normalization & Schema Validation Engine for OsintNeoAi.
Standardizes entity IDs, entity names, APNs, addresses (USPS Pub 28 CASS),
timestamps (ISO 8601 UTC), phones, emails, and foreign key relationships
across all 40 tabs and entity registries.
"""

import re
import datetime
from typing import Optional, Union, List, Dict, Any, Set, Tuple

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
    "ST": "STREET", "STR": "STREET", "ST.": "STREET",
    "AVE": "AVENUE", "AV": "AVENUE", "AVE.": "AVENUE",
    "BLVD": "BOULEVARD", "BLV": "BOULEVARD", "BOUL": "BOULEVARD", "BLVD.": "BOULEVARD",
    "RD": "ROAD", "RD.": "ROAD",
    "LN": "LANE", "LN.": "LANE",
    "CT": "COURT", "CT.": "COURT",
    "DR": "DRIVE", "DRV": "DRIVE", "DR.": "DRIVE",
    "WAY": "WAY",
    "PKWY": "PARKWAY", "PKY": "PARKWAY", "PARKWY": "PARKWAY", "PKWY.": "PARKWAY",
    "CIR": "CIRCLE", "CIRC": "CIRCLE", "CIR.": "CIRCLE",
    "HWY": "HIGHWAY", "HIGHWY": "HIGHWAY", "HWY.": "HIGHWAY",
    "PL": "PLACE", "PL.": "PLACE",
    "TER": "TERRACE", "TERR": "TERRACE", "TER.": "TERRACE",
    "TRL": "TRAIL", "TL": "TRAIL", "TRL.": "TRAIL",
    "ALY": "ALLEY",
    "EXPY": "EXPRESSWAY",
    "LOOP": "LOOP",
    "ROW": "ROW",
    "RUN": "RUN",
    "SQ": "SQUARE", "SQ.": "SQUARE",
}

# Directional Expansions
DIRECTIONAL_MAP = {
    "N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
    "NE": "NORTHEAST", "NW": "NORTHWEST", "SE": "SOUTHEAST", "SW": "SOUTHWEST",
    "N.": "NORTH", "S.": "SOUTH", "E.": "EAST", "W.": "WEST",
    "NE.": "NORTHEAST", "NW.": "NORTHWEST", "SE.": "SOUTHEAST", "SW.": "SOUTHWEST",
}

# Secondary Unit Expansions
UNIT_MAP = {
    "STE": "SUITE", "STE.": "SUITE",
    "APT": "APARTMENT", "APT.": "APARTMENT",
    "BLDG": "BUILDING", "BLDG.": "BUILDING",
    "FL": "FLOOR", "FL.": "FLOOR",
    "RM": "ROOM", "RM.": "ROOM",
    "DEPT": "DEPARTMENT", "DEPT.": "DEPARTMENT",
    "OFC": "OFFICE", "OFC.": "OFFICE",
    "SPC": "SPACE", "SPC.": "SPACE",
    "BSMT": "BASEMENT",
    "UNIT": "UNIT",
}

# Entity Scheme Mapping
ENTITY_PREFIX_TO_TYPE = {
    "PER": "PERSON",
    "GOV": "GOV_AGENCY",
    "CON": "CONTRACTOR",
    "SHL": "SHELL_CO",
    "NP": "NONPROFIT",
    "EV": "EVIDENCE",
    "RICO": "RICO_NODE",
    "TOX": "TOXIC_SITE",
    "UP": "UNCLAIMED_PROP",
    "ADDR": "ADDRESS",
    "PHONE": "PHONE",
    "EMAIL": "EMAIL",
    "LEG": "LEGAL",
    "TL": "TIMELINE",
    "TRAF": "TRAFFICKING_NODE",
    "FIN": "FINANCIAL_LEDGER",
    "FAC": "FACILITY",
}

TYPE_TO_ENTITY_PREFIX = {
    "PERSON": "PER",
    "INDIVIDUAL": "PER",
    "GOV_AGENCY": "GOV",
    "GOVERNMENT": "GOV",
    "GOVERNMENT AGENCY": "GOV",
    "CONTRACTOR": "CON",
    "VENDOR": "CON",
    "SHELL_CO": "SHL",
    "SHELL_COMPANY": "SHL",
    "SHELL COMPANY": "SHL",
    "NONPROFIT": "NP",
    "NON-PROFIT": "NP",
    "EVIDENCE": "EV",
    "EVIDENCE_ITEM": "EV",
    "EVIDENCE ITEM": "EV",
    "RICO_NODE": "RICO",
    "RICO NODE": "RICO",
    "TOXIC_SITE": "TOX",
    "TOXIC-SITE": "TOX",
    "UNCLAIMED_PROP": "UP",
    "UNCLAIMED PROPERTY": "UP",
    "ADDRESS": "ADDR",
    "PHONE": "PHONE",
    "EMAIL": "EMAIL",
    "LEGAL": "LEG",
    "LEGAL_EXPOSURE": "LEG",
    "TIMELINE": "TL",
    "TIMELINE_EVENT": "TL",
    "TRAFFICKING_NODE": "TRAF",
    "TRAFFICKING": "TRAF",
    "FINANCIAL_LEDGER": "FIN",
    "FINANCIAL": "FIN",
    "FACILITY": "FAC",
}

TAB_TO_PREFIX_MAP = {
    "People": "PER",
    "Gov_Agencies": "GOV",
    "Gov Agencies": "GOV",
    "Contractors": "CON",
    "Shell_Companies": "SHL",
    "Shell Companies": "SHL",
    "Nonprofits": "NP",
    "Evidence_Items": "EV",
    "Evidence Items": "EV",
    "RICO_Nodes": "RICO",
    "RICO Nodes": "RICO",
    "Toxic_Site": "TOX",
    "Toxic-Site": "TOX",
    "Unclaimed_Prop": "UP",
    "Unclaimed Prop": "UP",
    "Addresses": "ADDR",
    "Phones": "PHONE",
    "Emails": "EMAIL",
    "Legal_Exposure": "LEG",
    "Legal Exposure": "LEG",
    "Legal_Brief_Export": "LEG",
    "MASTER_TIMELINE": "TL",
    "Timeline": "TL",
    "Wintersburg_Timeline": "TL",
    "TIMELINE_CHART_2020_2026": "TL",
    "Child_Trafficking_Intel": "TRAF",
    "Audit_Report": "FIN",
}

PREFIX_TO_TAB_MAP = {
    "PER": "People",
    "GOV": "Gov_Agencies",
    "CON": "Contractors",
    "SHL": "Shell_Companies",
    "NP": "Nonprofits",
    "EV": "Evidence_Items",
    "RICO": "RICO_Nodes",
    "TOX": "Toxic_Site",
    "UP": "Unclaimed_Prop",
    "ADDR": "Addresses",
    "PHONE": "Phones",
    "EMAIL": "Emails",
    "LEG": "Legal_Exposure",
    "TL": "MASTER_TIMELINE",
    "TRAF": "Child_Trafficking_Intel",
    "FIN": "Audit_Report",
    "FAC": "Contractors",
}

# Regex for entity IDs (e.g., PER-001, GOV-002, FAC-STRTP-001, RICO-020)
ENTITY_ID_PATTERN = re.compile(
    r"^(PER|GOV|CON|SHL|NP|EV|RICO|TOX|UP|ADDR|PHONE|EMAIL|LEG|TL|TRAF|FIN|FAC)(?:-([A-Z0-9]+))?-(\d+)$",
    re.IGNORECASE
)

# 40 Master Sheet Tab Definitions with schema expectations
MASTER_TAB_DEFINITIONS = {
    "MASTER": {
        "description": "Core entity registry indexing all entities across all tabs",
        "primary_key": "ENTITY_ID",
        "expected_columns": ["ENTITY_ID", "ENTITY_TYPE", "ENTITY_NAME", "PRIMARY_TAB", "RELATED_IDS", "LAST_UPDATED", "SOURCE_DOC", "NOTES", "STATUS", "PUBLIC_EVIDENCE", "NON_PUBLIC_EVIDENCE"]
    },
    "People": {
        "description": "All individuals (PER-###)",
        "primary_key": "PERSON_ID",
        "prefix": "PER",
        "expected_columns": ["PERSON_ID", "NAME", "ROLE", "LEGAL_STATUS", "ORGANIZATION", "AFFILIATION", "DETAILS", "LAST_UPDATED"]
    },
    "Gov_Agencies": {
        "description": "Government entities and regulatory bodies (GOV-###)",
        "primary_key": "AGENCY_ID",
        "prefix": "GOV",
        "expected_columns": ["AGENCY_ID", "AGENCY_NAME", "JURISDICTION", "ROLE", "RELEVANT_CASE", "FINDINGS", "LAST_UPDATED"]
    },
    "Contractors": {
        "description": "Contractors, vendors, and developers (CON-###)",
        "primary_key": "CON_ID",
        "prefix": "CON",
        "expected_columns": ["CON_ID", "COMPANY_NAME", "TYPE", "CONTRACT_VALUE", "CONTRACT_PURPOSE", "CONTRACTING_AGENCY", "KEY_PERSONNEL_IDS", "RED_FLAGS", "SOURCE_DOC", "SOURCE_PAGE", "QUOTE_SNIPPET", "NOTES", "LAST_UPDATED"]
    },
    "Shell_Companies": {
        "description": "Shell and suspect entities (SHL-###)",
        "primary_key": "SHL_ID",
        "prefix": "SHL",
        "expected_columns": ["SHL_ID", "ENTITY_NAME", "STATE_OF_FORMATION", "REG_AGENT", "PRINCIPALS", "PURPOSE", "BANK_ACCOUNTS", "RED_FLAGS", "SOURCE_DOC", "SOURCE_PAGE", "QUOTE_SNIPPET", "NOTES", "LAST_UPDATED"]
    },
    "Evidence_Items": {
        "description": "Evidence catalog and primary artifacts (EV-###)",
        "primary_key": "EVIDENCE_ID",
        "prefix": "EV",
        "expected_columns": ["EVIDENCE_ID", "NAME", "TYPE", "DATE", "RELEVANCE", "SOURCE_DOC", "RELATED_IDS", "NOTES", "LAST_UPDATED"]
    },
    "RICO_Nodes": {
        "description": "RICO enterprise network nodes (RICO-###)",
        "primary_key": "RICO_ID",
        "prefix": "RICO",
        "expected_columns": ["RICO_ID", "NODE_NAME", "NODE_TYPE", "ROLE_IN_ENTERPRISE", "PREDICATE_ACTS", "CONNECTED_NODE_IDS", "EVIDENCE_IDS", "STATUTE", "SOURCE_DOC", "SOURCE_PAGE", "QUOTE_SNIPPET", "NOTES", "LAST_UPDATED"]
    },
    "Neo4j_Graph_Schema": {
        "description": "Graph database schema and node/edge relationships",
        "primary_key": "Source",
        "expected_columns": ["Source", "Target", "Relationship", "Weight", "Category", "Notes"]
    },
    "MASTER_TIMELINE": {
        "description": "Comprehensive chronological event timeline (TL-###)",
        "primary_key": "EVENT_ID",
        "prefix": "TL",
        "expected_columns": ["EVENT_ID", "DATE", "ACTOR", "EVENT_DESCRIPTION", "CORROBORATING_EV", "RELATED_IDS", "LAST_UPDATED"]
    },
    "TIMELINE_CHART_2020_2026": {
        "description": "Timeline visualization matrix across 2020-2026",
        "primary_key": "Year_Month",
        "expected_columns": ["Year_Month", "Date", "Actor", "Category", "Event_Description", "Evidence_Ref", "Legal_Nexus"]
    },
    "Wintersburg_Timeline": {
        "description": "Wintersburg property and Japanese Mission historic timeline",
        "primary_key": "Year_Date",
        "expected_columns": ["Year_Date", "Event", "Entities_Involved", "Historical_Significance", "Source", "Notes"]
    },
    "Legal_Brief_Export": {
        "description": "Structured legal claims, statutes, and complaint elements",
        "primary_key": "Claim_ID",
        "prefix": "LEG",
        "expected_columns": ["Claim_ID", "Statute", "Title", "Defendants", "Predicate_Facts", "Penalty_Exposure", "Status"]
    },
    "Legal_Exposure": {
        "description": "Statutory liability matrix and penalty calculations",
        "primary_key": "Exposure_ID",
        "prefix": "LEG",
        "expected_columns": ["Exposure_ID", "Statute", "Jurisdiction", "Target_Entities", "Violation_Type", "Max_Penalty", "Status", "Notes"]
    },
    "Smoking_Gun_Matrix": {
        "description": "Key evidentiary nexus points and smoking gun findings",
        "primary_key": "Source Entity",
        "expected_columns": ["Source Entity", "Target Entity", "Connection Type", "Financial Value", "Timeline", "Address / Nexus", "Legal Exposure", "Evidence Source", "Smoking Gun Flag"]
    },
    "Audit_Report": {
        "description": "Comprehensive forensic audit discrepancies and findings (FIN-###)",
        "primary_key": "Audit_ID",
        "prefix": "FIN",
        "expected_columns": ["Audit_ID", "Category", "Entity_Target", "Discrepancy_Amount", "Evidence_Ref", "Statutory_Basis", "Risk_Level", "Remediation_Status"]
    },
    "DATA_QUALITY_AUDIT": {
        "description": "Data quality, missing field, and cross-tab validation issues",
        "primary_key": "Audit_Issue_ID",
        "expected_columns": ["Audit_Issue_ID", "Tab_Name", "Row_Index", "Entity_ID", "Issue_Type", "Severity", "Description", "Resolution_Action"]
    },
    "CLEANUP_SUMMARY": {
        "description": "Record sanitation and normalization audit log",
        "primary_key": "Clean_ID",
        "expected_columns": ["Clean_ID", "Timestamp", "Tab_Name", "Records_Processed", "Records_Cleaned", "Modifications_Made", "Status"]
    },
    "DEPLOYMENT_SUMMARY": {
        "description": "System deployment and synchronization checklist",
        "primary_key": "Checklist_Item",
        "expected_columns": ["Checklist_Item", "Component", "Target_Location", "Verification_Command", "Status", "Last_Verified"]
    },
    "DASHBOARD_AUTO": {
        "description": "Live automated intelligence query metrics and counts",
        "primary_key": "Metric",
        "expected_columns": ["Metric", "Value", "Category", "Last_Calculated", "Status"]
    },
    "Dashboard": {
        "description": "Summary KPI dashboard metrics",
        "primary_key": "Key",
        "expected_columns": ["Key", "Value", "Description"]
    },
    "Calc_Data": {
        "description": "Analytical calculation tables and aggregations",
        "primary_key": "Category",
        "expected_columns": ["Category", "Total_Count", "Total_Financial_Value", "Risk_Score", "Notes"]
    },
    "Unified_Dossier": {
        "description": "Consolidated subject and entity intelligence dossiers",
        "primary_key": "Dossier_ID",
        "expected_columns": ["Dossier_ID", "Subject_Name", "Role", "Entity_Links", "Financial_Exposure", "Summary_Findings", "Status"]
    },
    "Child_Trafficking_Intel": {
        "description": "Trafficking intelligence and pipeline nodes (TRAF-###)",
        "primary_key": "Entity_ID",
        "prefix": "TRAF",
        "expected_columns": ["Entity_ID", "Entity_Type", "Entity_Name", "Primary_Tab", "Related_IDs", "RICO_Connection", "Notes"]
    },
    "Trafficking_Dashboard": {
        "description": "Trafficking intelligence query metrics and vectors",
        "primary_key": "Query_Vector",
        "expected_columns": ["Query_Vector", "Node_Count", "Risk_Level", "Primary_Entities", "Status"]
    },
    "Fugitive_Tracking_Brief": {
        "description": "Fugitive and indicted person location tracking",
        "primary_key": "Target Name",
        "expected_columns": ["Target Name", "Aliases", "Last Known Location", "Indictment Details", "Associated Entities", "Status", "Notes"]
    },
    "Cross_References": {
        "description": "Direct entity cross-reference relationships",
        "primary_key": "Source_ID",
        "expected_columns": ["Source_ID", "Source_Name", "Target_ID", "Target_Name", "Relationship_Type", "Evidence_Ref", "Notes"]
    },
    "Addresses": {
        "description": "Physical addresses of significance (ADDR-###)",
        "primary_key": "ADDR_ID",
        "prefix": "ADDR",
        "expected_columns": ["ADDR_ID", "ADDRESS", "CITY", "STATE", "ZIP", "ENTITY_IDS", "SIGNIFICANCE", "SOURCE_DOC", "SOURCE_PAGE", "NOTES"]
    },
    "Entity_Addresses": {
        "description": "Mapping between entities and physical addresses",
        "primary_key": "Entity",
        "expected_columns": ["Entity", "Category", "Address", "Notes"]
    },
    "Emails": {
        "description": "Email communications and verified contacts (EMAIL-###)",
        "primary_key": "EMAIL_ID",
        "prefix": "EMAIL",
        "expected_columns": ["EMAIL_ID", "EMAIL_ADDRESS", "TYPE", "ENTITY_IDS", "VERIFIED", "SOURCE_DOC", "SOURCE_PAGE", "NOTES"]
    },
    "Phones": {
        "description": "Telephone numbers and switchboards (PHONE-###)",
        "primary_key": "PHONE_ID",
        "prefix": "PHONE",
        "expected_columns": ["PHONE_ID", "PHONE_NUMBER", "TYPE", "ENTITY_IDS", "VERIFIED", "SOURCE_DOC", "SOURCE_PAGE", "NOTES"]
    },
    "Nonprofits": {
        "description": "Nonprofit and 501(c)(3) entities (NP-###)",
        "primary_key": "NP_ID",
        "prefix": "NP",
        "expected_columns": ["NP_ID", "ORG_NAME", "EIN", "501C_STATUS", "ROLE_IN_MATTER", "ADDRESS", "KEY_PERSONNEL", "FUNDING_SOURCES", "RED_FLAGS", "SOURCE_DOC", "SOURCE_PAGE", "QUOTE_SNIPPET", "NOTES"]
    },
    "Toxic_Site": {
        "description": "Contamination data and toxic site sampling (TOX-###)",
        "primary_key": "TOX_ID",
        "prefix": "TOX",
        "expected_columns": ["TOX_ID", "SITE_NAME", "ADDRESS", "CONTAMINANT", "LEVEL_DETECTED", "REGULATORY_LIMIT", "EXCEEDANCE_FACTOR", "SAMPLE_DATE", "SAMPLE_ID", "MEDIA", "RESPONSIBLE_PARTIES", "REGULATORY_AGENCY", "REMEDIATION_STATUS", "HEALTH_RISK", "EVIDENCE_IDS", "SOURCE_DOC", "SOURCE_PAGE", "QUOTE_SNIPPET", "NOTES"]
    },
    "Unclaimed_Prop": {
        "description": "Unclaimed property and dormant asset leads (UP-###)",
        "primary_key": "UP_ID",
        "prefix": "UP",
        "expected_columns": ["UP_ID", "PROPERTY_TYPE", "HOLDER_NAME", "OWNER_NAME", "PROPERTY_VALUE", "ACCOUNT_NUMBER", "REPORT_DATE", "STATE", "STATUS", "RELATED_ENTITY_IDS", "ACTION_REQUIRED", "SOURCE_DOC", "SOURCE_PAGE", "NOTES"]
    },
    "USGS_Image_Analysis": {
        "description": "USGS aerial and satellite imagery analysis logs",
        "primary_key": "Image_ID",
        "expected_columns": ["Image_ID", "Date", "Coordinates", "Features_Identified", "Environmental_Anomalies", "Source_Collection", "Notes"]
    },
    "Anthony_DiMarcello": {
        "description": "Subject profile and testimony timeline for Relator",
        "primary_key": "Profile_Field",
        "expected_columns": ["Profile_Field", "Value", "Notes"]
    },
    "hud_pit_by_coc": {
        "description": "HUD Point-in-Time homeless count statistics by CoC",
        "primary_key": "CoC_Code",
        "expected_columns": ["CoC_Code", "CoC_Name", "Year", "Overall_Homeless", "Sheltered", "Unsheltered", "Notes"]
    },
    "Chart10": {
        "description": "Data freshness and synchronization audit metric 10",
        "primary_key": "Assessment_Metric",
        "expected_columns": ["Assessment_Metric", "Status", "Details", "Last_Evaluated"]
    },
    "Chart11": {
        "description": "Data freshness and synchronization audit metric 11",
        "primary_key": "Assessment_Metric",
        "expected_columns": ["Assessment_Metric", "Status", "Details", "Last_Evaluated"]
    },
    "Chart12": {
        "description": "Data freshness and synchronization audit metric 12",
        "primary_key": "Assessment_Metric",
        "expected_columns": ["Assessment_Metric", "Status", "Details", "Last_Evaluated"]
    },
    "Timeline": {
        "description": "Deprecated timeline tab pointing to MASTER_TIMELINE",
        "primary_key": "Notice",
        "expected_columns": ["Notice", "Redirect_Target", "Notes"]
    },
}


def normalize_entity_id(entity_id: Optional[str]) -> str:
    """
    Standardize entity IDs:
    - Uppercases and trims whitespace/punctuation
    - Formats standard 3+ digit padded number (e.g. per-1 -> PER-001, GOV_2 -> GOV-002)
    - Supports facility subtags (e.g. FAC-STRTP-1 -> FAC-STRTP-001, FAC-EBSH-2 -> FAC-EBSH-002)
    - Returns standardized ID or empty string if not recognizable
    """
    if not entity_id:
        return ""
    raw = str(entity_id).strip().upper()
    if raw.startswith("NEXT ID:") or "ROW PER" in raw:
        return ""
    
    # Strip leading/trailing quotes and brackets
    raw = raw.strip("\"'()[]{} :")
    if not raw:
        return ""
    
    # Split by hyphen, underscore, or space
    parts = [p for p in re.split(r"[-_\s]+", raw) if p]
    if len(parts) == 1:
        m = re.match(r"^([A-Z]+)(\d+)$", parts[0])
        if m:
            parts = [m.group(1), m.group(2)]

    if len(parts) == 2 and parts[0] in ENTITY_PREFIX_TO_TYPE and parts[1].isdigit():
        return f"{parts[0]}-{int(parts[1]):03d}"
    elif len(parts) == 3 and parts[0] in ENTITY_PREFIX_TO_TYPE and parts[2].isdigit():
        return f"{parts[0]}-{parts[1]}-{int(parts[2]):03d}"
    elif len(parts) == 2 and parts[1].isdigit() and len(parts[0]) <= 6:
        return f"{parts[0]}-{int(parts[1]):03d}"
    elif len(parts) == 3 and parts[2].isdigit() and len(parts[0]) <= 6:
        return f"{parts[0]}-{parts[1]}-{int(parts[2]):03d}"
        
    return raw if len(raw) <= 30 and not any(c in raw for c in ",; ") else ""


def validate_entity_id(entity_id: Optional[str]) -> bool:
    """
    Validates whether an entity ID strictly adheres to the recognized canonical scheme.
    """
    if not entity_id:
        return False
    norm = normalize_entity_id(entity_id)
    if not norm:
        return False
    return bool(ENTITY_ID_PATTERN.match(norm))


def extract_entity_type_from_id(entity_id: Optional[str]) -> str:
    """
    Derives canonical entity type string from an entity ID.
    E.g. PER-001 -> PERSON, GOV-001 -> GOV_AGENCY, etc.
    """
    if not entity_id:
        return "UNKNOWN"
    norm = normalize_entity_id(entity_id)
    m = ENTITY_ID_PATTERN.match(norm)
    if m:
        prefix = m.group(1).upper()
        return ENTITY_PREFIX_TO_TYPE.get(prefix, "UNKNOWN")
    return "UNKNOWN"


def parse_foreign_keys(val: Optional[Union[str, List[str]]]) -> List[str]:
    """
    Parses and standardizes semicolon or comma delimited foreign keys.
    Returns deduplicated list of canonical entity IDs.
    """
    if not val:
        return []
    if isinstance(val, list):
        raw_list = val
    else:
        # Split on semicolon, comma, or slash
        raw_list = re.split(r"[;,/]+", str(val))
        
    results: List[str] = []
    seen: Set[str] = set()
    for item in raw_list:
        norm = normalize_entity_id(item)
        if norm and norm not in seen and validate_entity_id(norm):
            seen.add(norm)
            results.append(norm)
    return results


def format_foreign_keys(keys: Optional[Union[List[str], str]]) -> str:
    """
    Formats a list of entity IDs into a canonical semicolon-separated string.
    """
    parsed = parse_foreign_keys(keys)
    return ";".join(parsed)


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


def standardize_phone(phone: Optional[str]) -> str:
    """
    Standardize US and international phone numbers:
    - Formats US 10-digit numbers to: (###) ###-####
    - Formats US 11-digit numbers (leading 1) to: +1 (###) ###-####
    """
    if not phone:
        return ""
    raw = str(phone).strip()
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    return raw


def standardize_email(email: Optional[str]) -> str:
    """
    Standardize email address: lowercases, trims whitespace.
    """
    if not email:
        return ""
    raw = str(email).strip().lower()
    if "@" in raw and "." in raw:
        return raw
    return raw


def normalize_timestamp(ts: Optional[Union[str, int, float, datetime.datetime]] = None) -> str:
    """
    Normalize timestamp to ISO 8601 UTC canonical string.
    Format: YYYY-MM-DDTHH:MM:SS+00:00 (or with microseconds)
    """
    if ts is None or str(ts).strip() in ("", "None", "null", "nan", "-"):
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
    
    # Check for Month Name formats like "August 12, 2025" or "Aug 2020"
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %Y",
        "%b %Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]:
        try:
            clean_s = s.replace("Z", "+0000").replace("Sept", "Sep")
            dt = datetime.datetime.strptime(clean_s, fmt)
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

    # Extract year if present
    year_match = re.search(r"\b(19\d\d|20\d\d)\b", s)
    if year_match:
        year = int(year_match.group(1))
        return datetime.datetime(year, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).isoformat()

    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def normalize_master_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a single entity row from the MASTER sheet.
    """
    raw_id = raw.get("ENTITY_ID") or raw.get("entity_id") or raw.get("ID") or ""
    entity_id = normalize_entity_id(raw_id)
    
    raw_type = raw.get("ENTITY_TYPE") or raw.get("entity_type") or raw.get("TYPE") or ""
    if not raw_type and entity_id:
        entity_type = extract_entity_type_from_id(entity_id)
    else:
        entity_type = TYPE_TO_ENTITY_PREFIX.get(str(raw_type).upper().strip(), str(raw_type).upper().strip())
        
    entity_name = str(raw.get("ENTITY_NAME") or raw.get("entity_name") or raw.get("NAME") or "").strip()
    primary_tab = str(raw.get("PRIMARY_TAB") or raw.get("primary_tab") or "").strip()
    if not primary_tab and entity_id:
        m = ENTITY_ID_PATTERN.match(entity_id)
        if m:
            prefix = m.group(1).upper()
            primary_tab = PREFIX_TO_TAB_MAP.get(prefix, "MASTER")
            
    related_ids = parse_foreign_keys(raw.get("RELATED_IDS") or raw.get("related_ids"))
    last_updated = normalize_timestamp(raw.get("LAST_UPDATED") or raw.get("last_updated"))
    source_doc = str(raw.get("SOURCE_DOC") or raw.get("source_doc") or "").strip()
    notes = str(raw.get("NOTES") or raw.get("notes") or "").strip()
    status = str(raw.get("STATUS") or raw.get("status") or "Active").strip()
    public_evidence = str(raw.get("PUBLIC_EVIDENCE") or raw.get("public_evidence") or "").strip()
    non_public_evidence = str(raw.get("NON_PUBLIC_EVIDENCE") or raw.get("non_public_evidence") or "").strip()

    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "canonical_name": normalize_entity_name(entity_name),
        "raw_name": entity_name,
        "primary_tab": primary_tab,
        "related_ids": related_ids,
        "related_ids_str": ";".join(related_ids),
        "last_updated": last_updated,
        "source_doc": source_doc,
        "notes": notes,
        "status": status,
        "public_evidence": public_evidence,
        "non_public_evidence": non_public_evidence,
    }


def resolve_cross_references(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Performs bidirectional cross-referencing resolution:
    If entity A lists B in related_ids, entity B is updated to include A in its related_ids.
    """
    entity_map: Dict[str, Dict[str, Any]] = {}
    adjacency: Dict[str, Set[str]] = {}
    
    for r in records:
        eid = r.get("entity_id")
        if not eid:
            continue
        entity_map[eid] = r
        if eid not in adjacency:
            adjacency[eid] = set()
            
        r_ids = r.get("related_ids") or []
        for target in r_ids:
            if target and target != eid:
                adjacency[eid].add(target)
                if target not in adjacency:
                    adjacency[target] = set()
                # Bidirectional back-edge
                adjacency[target].add(eid)

    # Reconstruct updated records
    updated: List[Dict[str, Any]] = []
    for r in records:
        eid = r.get("entity_id")
        if eid and eid in adjacency:
            all_related = sorted(list(adjacency[eid]))
            r_copy = dict(r)
            r_copy["related_ids"] = all_related
            r_copy["related_ids_str"] = ";".join(all_related)
            updated.append(r_copy)
        else:
            updated.append(r)
            
    return updated


def validate_tab_schema(tab_name: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates rows of a given tab against expected schemas and conventions.
    Returns audit statistics dictionary.
    """
    tab_def = MASTER_TAB_DEFINITIONS.get(tab_name, {})
    expected_cols = tab_def.get("expected_columns", [])
    primary_key = tab_def.get("primary_key")
    expected_prefix = tab_def.get("prefix")
    
    total_rows = len(rows)
    valid_rows = 0
    invalid_rows = 0
    entities_found: List[str] = []
    issues: List[Dict[str, Any]] = []
    
    for idx, row in enumerate(rows):
        row_issues: List[str] = []
        pk_val = str(row.get(primary_key, "")).strip() if primary_key else ""
        
        # Check instruction / skip rows
        if any("ROW PER" in str(v).upper() for v in row.values()):
            continue
            
        if expected_prefix and pk_val:
            norm_pk = normalize_entity_id(pk_val)
            if not validate_entity_id(norm_pk):
                row_issues.append(f"Invalid primary key format: {pk_val} (expected {expected_prefix}-###)")
            else:
                entities_found.append(norm_pk)
                
        # Validate foreign keys if present
        for col_name in ["RELATED_IDS", "ENTITY_IDS", "CONNECTED_NODE_IDS", "EVIDENCE_IDS", "KEY_PERSONNEL_IDS"]:
            if col_name in row and row[col_name]:
                fks = parse_foreign_keys(row[col_name])
                for fk in fks:
                    if not validate_entity_id(fk):
                        row_issues.append(f"Invalid foreign key ID: {fk} in column {col_name}")

        # Validate addresses if present
        for addr_col in ["ADDRESS", "Address", "location"]:
            if addr_col in row and row[addr_col]:
                norm_a = normalize_address(row[addr_col])
                if not norm_a:
                    row_issues.append(f"Empty normalized address from: {row[addr_col]}")

        # Validate APN if present
        for apn_col in ["APN", "apn", "Parcel"]:
            if apn_col in row and row[apn_col]:
                norm_apn_val = normalize_apn(row[apn_col])
                if norm_apn_val and not re.match(r"^\d{3}-\d{3}-\d{2,4}$", norm_apn_val):
                    row_issues.append(f"Non-standard APN format: {row[apn_col]} -> {norm_apn_val}")

        if row_issues:
            invalid_rows += 1
            issues.append({
                "tab": tab_name,
                "row_index": idx,
                "primary_key": pk_val,
                "issues": row_issues
            })
        else:
            valid_rows += 1
            
    return {
        "tab_name": tab_name,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "entities_count": len(entities_found),
        "entities_found": entities_found,
        "issues": issues,
        "compliance_rate": (valid_rows / total_rows * 100.0) if total_rows > 0 else 100.0
    }


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
