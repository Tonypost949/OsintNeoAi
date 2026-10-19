"""
watcher.py — Phase 1 main loop.
Polls CA SOS, matches entities, exports to BigQuery + Neo4j.
"""
import csv
import json
import re
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.cloud import bigquery

import config
from attorney_nodes import (
    extract_attorney_from_agent,
    enrich_attorney_bq,
    process_attorney_batch,
    write_attorney_csv,
)
from entity_match import match_entity, match_exact, normalize_name, clear_cache
from neo4j_export import export_entities, export_relationships, export_attorneys


def search_ca_sos(session: requests.Session, query: str, search_type: str = "CORP", page: int = 1):
    """Search CA SOS for entities."""
    data = {
        "SearchType": search_type,
        "SearchCriteria": query,
        "SearchSubType": "Name",
        "page": page,
    }
    try:
        resp = session.post(
            config.CA_SOS_SEARCH_URL,
            data=data,
            headers=config.CA_SOS_HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  [ERROR] SOS search failed: {e}")
        return None


def parse_sos_results(html: str) -> list[dict]:
    """Parse CA SOS search results HTML."""
    entities = []
    rows = re.findall(
        r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>.*?</tr>',
        html, re.DOTALL,
    )
    for name_raw, num_raw in rows:
        name = re.sub(r'<[^>]+>', '', name_raw).strip()
        num = re.sub(r'<[^>]+>', '', num_raw).strip()
        if name and num:
            entities.append({"entity_name": name, "entity_number": num})
    return entities


def get_entity_detail(session: requests.Session, entity_number: str) -> dict:
    """Get full details for a single entity from CA SOS."""
    try:
        resp = session.get(
            f"{config.CA_SOS_DETAIL_URL}?id={entity_number}",
            headers=config.CA_SOS_HEADERS,
            timeout=30,
        )
        html = resp.text

        def extract_field(pattern):
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            return re.sub(r'<[^>]+>', '', match.group(1)).strip() if match else ""

        return {
            "entity_number": entity_number,
            "registered_agent": extract_field(r'Agent for Service of Process.*?<td[^>]*>(.*?)</td>'),
            "agent_address": extract_field(r'Address.*?<td[^>]*>(.*?)</td>'),
            "status": extract_field(r'Status.*?<td[^>]*>(.*?)</td>') or "Unknown",
            "filing_date": extract_field(r'Filing Date.*?<td[^>]*>(.*?)</td>'),
            "entity_type": extract_field(r'Type.*?<td[^>]*>(.*?)</td>'),
        }
    except Exception as e:
        print(f"  [ERROR] Detail fetch failed {entity_number}: {e}")
        return {"entity_number": entity_number, "status": "Error"}


def load_existing_entities(bq_client: bigquery.Client) -> list[dict]:
    """Load existing entities from BigQuery for matching."""
    query = f"SELECT entity_id, entity_name, entity_type, entity_number FROM `{config.BQ_TABLE_ENTITIES}`"
    try:
        results = bq_client.query(query).result()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"  [WARN] Could not load existing entities: {e}")
        return []


def upsert_to_bq(bq_client: bigquery.Client, table: str, rows: list[dict]):
    """Upsert rows to BigQuery table."""
    if not rows:
        return
    errors = bq_client.insert_rows_json(table, rows)
    if errors:
        print(f"  [ERROR] BQ insert errors: {errors}")
    else:
        print(f"  [OK] Inserted {len(rows)} rows to {table}")


def run_pipeline():
    """Main pipeline execution."""
    print("=" * 60)
    print("OSINT PIPELINE — PHASE 1: Attorney/Entity Extraction")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Initialize clients
    bq_client = bigquery.Client(project=config.GCP_PROJECT)
    session = requests.Session()

    # Load existing entities for matching
    print("\n[1/5] Loading existing entities from BigQuery...")
    existing = load_existing_entities(bq_client)
    print(f"  Loaded {len(existing)} existing entities")

    # Search CA SOS
    print("\n[2/5] Searching CA SOS...")
    search_queries = []  # Add search terms here
    all_sos_entities = []

    # Example: search for known entity patterns
    # for query in search_queries:
    #     html = search_ca_sos(session, query)
    #     if html:
    #         entities = parse_sos_results(html)
    #         all_sos_entities.extend(entities)

    print(f"  Found {len(all_sos_entities)} entities from CA SOS")

    # Match and enrich
    print("\n[3/5] Matching entities...")
    new_entities = []
    attorneys = []

    for ent in all_sos_entities:
        # Try exact match first
        match = match_exact(ent["entity_name"], existing)
        if not match:
            match = match_entity(ent["entity_name"], existing)

        if match:
            print(f"  MATCHED: {ent['entity_name']} -> {match['entity_name']} (score: {match.get('match_score', 0)})")
        else:
            print(f"  NEW: {ent['entity_name']}")
            new_entities.append(ent)

        # Extract attorney if present
        agent = ent.get("registered_agent", "")
        if agent:
            att = extract_attorney_from_agent(agent, ent.get("entity_number", ""))
            if att:
                attorneys.append(att)

    # Process attorneys
    print("\n[4/5] Processing attorneys...")
    att_result = process_attorney_batch(attorneys)
    print(f"  Found {att_result['total']} unique attorneys")

    # Enrich attorneys for BQ
    att_rows = [enrich_attorney_bq(a) for a in att_result["attorneys"]]

    # Export to BigQuery
    print("\n[5/5] Exporting to BigQuery and Neo4j...")
    if new_entities:
        upsert_to_bq(bq_client, config.BQ_TABLE_ENTITIES, new_entities)
    if att_rows:
        upsert_to_bq(bq_client, config.BQ_TABLE_ATTORNEYS, att_rows)

    # Export to Neo4j JSONL
    entity_batch = export_entities(new_entities)
    att_batch = export_attorneys(att_rows)
    print(f"  Neo4j entity batch: {entity_batch}")
    print(f"  Neo4j attorney batch: {att_batch}")

    # Write attorney CSV for review
    csv_path = config.WORKSPACE / "attorney_review.csv"
    write_attorney_csv(att_rows, csv_path)
    print(f"  Attorney review CSV: {csv_path}")

    # Clear expired cache
    clear_cache()

    print("\n" + "=" * 60)
    print("PHASE 1 COMPLETE")
    print(f"  New entities: {len(new_entities)}")
    print(f"  Attorneys: {att_result['total']}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
