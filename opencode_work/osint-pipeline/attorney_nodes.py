"""
attorney_nodes.py — Extract and link attorney entities from CA SOS data.
Pulls registered agent info, builds attorney-to-entity relationships.
"""
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

import config
from entity_match import normalize_name


def generate_attorney_id(name: str, bar_number: str = "") -> str:
    raw = f"{normalize_name(name)}:{bar_number}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def extract_attorney_from_agent(agent_name: str, entity_number: str = "") -> Optional[dict]:
    """Parse a registered agent string into structured attorney data."""
    if not agent_name or agent_name.upper() in ["NONE", "N/A", ""]:
        return None

    # Skip corporate agents
    corporate_patterns = [
        r"INC\b", r"LLC\b", r"CORP\b", r"CORPORATION\b",
        r"CO\b", r"COMPANY\b", r"REGISTERED AGENTS?",
        r"C T CORPORATION", r"CT CORPORATION",
        r"NORTHWEST", r"CORPORATION SERVICE", r"CSC",
    ]
    for pattern in corporate_patterns:
        if re.search(pattern, agent_name, re.IGNORECASE):
            return None

    # Extract bar number if present
    bar_match = re.search(r"Bar\s*#?\s*(\d+)", agent_name, re.IGNORECASE)
    bar_number = bar_match.group(1) if bar_match else ""

    # Clean name
    name = re.sub(r"Bar\s*#?\s*\d+", "", agent_name).strip()
    name = re.sub(r",?\s*(Esq|Attorney|Lawyer|Law\s*Office).*", "", name, flags=re.IGNORECASE).strip()
    name = name.rstrip(",").strip()

    if len(name) < 3:
        return None

    return {
        "attorney_id": generate_attorney_id(name, bar_number),
        "name": name,
        "bar_number": bar_number,
        "entity_count": 1,
        "linked_entities": [entity_number] if entity_number else [],
    }


def enrich_attorney_bq(attorney: dict) -> dict:
    """Add BigQuery metadata to attorney record."""
    now = datetime.now(timezone.utc).isoformat()
    attorney.setdefault("firm_name", "")
    attorney.setdefault("address", "")
    attorney.setdefault("city", "")
    attorney.setdefault("state", "CA")
    attorney.setdefault("phone", "")
    attorney.setdefault("email", "")
    attorney.setdefault("total_loan_amount", 0.0)
    attorney["first_seen"] = now
    attorney["last_updated"] = now
    return attorney


def process_attorney_batch(attorneys: list[dict]) -> dict:
    """Deduplicate and merge attorney records."""
    merged = {}
    for att in attorneys:
        att_id = att["attorney_id"]
        if att_id in merged:
            existing = merged[att_id]
            existing["entity_count"] += 1
            for ent in att.get("linked_entities", []):
                if ent not in existing["linked_entities"]:
                    existing["linked_entities"].append(ent)
        else:
            merged[att_id] = att

    return {
        "total": len(merged),
        "attorneys": list(merged.values()),
    }


def write_attorney_csv(attorneys: list[dict], output_path: Path):
    """Write attorneys to CSV for manual review."""
    if not attorneys:
        return

    fieldnames = [
        "attorney_id", "name", "bar_number", "firm_name",
        "address", "city", "state", "phone", "email",
        "entity_count", "total_loan_amount", "linked_entities",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for att in sorted(attorneys, key=lambda x: x.get("entity_count", 0), reverse=True):
            att["linked_entities"] = "; ".join(att.get("linked_entities", []))
            writer.writerow(att)
