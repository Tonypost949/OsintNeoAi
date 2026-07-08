"""
people_handler.py — Phase 2: Nexis people/officer pipeline.
Extracts person nodes from entity data, builds control clusters.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Optional

import config
from entity_match import normalize_name


def generate_person_id(name: str, addresses: list[str] = None) -> str:
    raw = f"{normalize_name(name)}:{','.join(sorted(addresses or []))}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def extract_person_from_entity(entity: dict) -> Optional[dict]:
    """Extract a person node from an entity's registered agent."""
    agent = entity.get("registered_agent", "")
    if not agent:
        return None

    # Skip corporate agents
    corporate = ["LLC", "INC", "CORP", "CORPORATION", "CO", "COMPANY",
                 "REGISTERED AGENT", "C T CORPORATION", "CT CORPORATION",
                 "NORTHWEST", "CORPORATION SERVICE", "CSC"]
    for word in corporate:
        if word in agent.upper():
            return None

    # Clean name
    name = re.sub(r"Bar\s*#?\s*\d+", "", agent).strip()
    name = re.sub(r",?\s*(Esq|Attorney|Lawyer|Law\s*Office).*", "", name, flags=re.IGNORECASE).strip()

    if len(name) < 3:
        return None

    address = entity.get("agent_address", "")
    addresses = [address] if address else []

    return {
        "person_id": generate_person_id(name, addresses),
        "full_name": name,
        "aliases": [],
        "addresses": addresses,
        "phone_numbers": [],
        "emails": [],
        "linked_entities": [entity.get("entity_id", "")],
        "linked_llc_count": 1,
        "total_ppp_amount": entity.get("loan_amount", 0.0),
        "source": entity.get("source", "ca_sos"),
        "confidence_score": entity.get("confidence_score", 0.5),
    }


def merge_person_records(records: list[dict]) -> dict:
    """Merge multiple person records by person_id."""
    merged = {}
    for rec in records:
        pid = rec["person_id"]
        if pid in merged:
            existing = merged[pid]
            # Merge linked entities
            for ent in rec.get("linked_entities", []):
                    if ent not in existing["linked_entities"]:
                        existing["linked_entities"].append(ent)
                    existing["linked_llc_count"] = existing.get("linked_llc_count", len(existing["linked_entities"]))
            # Merge addresses
            for addr in rec.get("addresses", []):
                if addr not in existing["addresses"]:
                    existing["addresses"].append(addr)
            # Merge phones
            for phone in rec.get("phone_numbers", []):
                if phone not in existing["phone_numbers"]:
                    existing["phone_numbers"].append(phone)
            # Merge emails
            for email in rec.get("emails", []):
                if email not in existing["emails"]:
                    existing["emails"].append(email)
            # Sum PPP amounts
            existing["total_ppp_amount"] += rec.get("total_ppp_amount", 0.0)
            # Keep highest confidence
            existing["confidence_score"] = max(
                existing["confidence_score"],
                rec.get("confidence_score", 0.0),
            )
        else:
            merged[pid] = dict(rec)

    return {
        "total": len(merged),
        "people": list(merged.values()),
    }


def build_control_clusters(people: list[dict], entities: list[dict]) -> list[dict]:
    """Build control clusters from person-entity relationships."""
    # Group entities by shared person
    person_entities = {}
    for person in people:
        for ent_id in person.get("linked_entities", []):
            if ent_id not in person_entities:
                person_entities[ent_id] = []
            person_entities[ent_id].append(person["person_id"])

    # Find clusters: entities connected by shared persons
    clusters = {}
    entity_map = {e["entity_id"]: e for e in entities}

    for ent_id, person_ids in person_entities.items():
        # Find all entities connected through any of these persons
        connected = set()
        for pid in person_ids:
            for person in people:
                if person["person_id"] == pid:
                    connected.update(person.get("linked_entities", []))

        # Create cluster key from sorted entity IDs
        cluster_key = tuple(sorted(connected))
        if cluster_key not in clusters:
            clusters[cluster_key] = {
                "cluster_id": hashlib.sha256(
                    "|".join(cluster_key).encode()
                ).hexdigest()[:16],
                "entity_ids": list(cluster_key),
                "person_ids": [],
                "total_entities": len(cluster_key),
                "total_loan_amount": 0.0,
                "geographic_span": [],
                "risk_score": 0.0,
            }

        # Add person IDs
        for pid in person_ids:
            if pid not in clusters[cluster_key]["person_ids"]:
                clusters[cluster_key]["person_ids"].append(pid)

    # Calculate risk scores
    for cluster in clusters.values():
        total_loan = 0.0
        states = set()
        for ent_id in cluster["entity_ids"]:
            ent = entity_map.get(ent_id, {})
            total_loan += ent.get("loan_amount", 0.0)
            if ent.get("state"):
                states.add(ent["state"])

        cluster["total_loan_amount"] = total_loan
        cluster["geographic_span"] = list(states)

        # Risk score
        cluster["risk_score"] = (
            min(len(states), 5) * 10 +
            min(cluster["total_entities"], 10) * 5 +
            (30 if total_loan > 1_000_000 else
             20 if total_loan > 500_000 else
             10 if total_loan > 100_000 else 0)
        )

    return list(clusters.values())


def person_to_bq_row(person: dict) -> dict:
    """Convert person record to BigQuery row format."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "person_id": person["person_id"],
        "full_name": person["full_name"],
        "aliases": person.get("aliases", []),
        "addresses": person.get("addresses", []),
        "phone_numbers": person.get("phone_numbers", []),
        "emails": person.get("emails", []),
        "linked_entities": person.get("linked_entities", []),
        "linked_llc_count": person.get("linked_llc_count", 0),
        "total_ppp_amount": person.get("total_ppp_amount", 0.0),
        "source": person.get("source", "unknown"),
        "confidence_score": person.get("confidence_score", 0.0),
        "first_seen": now,
        "last_updated": now,
    }
