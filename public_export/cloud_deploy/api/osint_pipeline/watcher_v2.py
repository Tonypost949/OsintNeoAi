"""
watcher_v2.py — Phase 2 main loop.
Extracts people, builds control clusters, exports to BigQuery + Neo4j.
"""
import json
from datetime import datetime, timezone

from google.cloud import bigquery

import config
from entity_match import clear_cache
from neo4j_export import export_entities, export_relationships
from people_handler import (
    extract_person_from_entity,
    merge_person_records,
    build_control_clusters,
    person_to_bq_row,
)


def load_entities(bq_client: bigquery.Client) -> list[dict]:
    """Load all entities from BigQuery."""
    query = f"""
    SELECT entity_id, entity_name, entity_type, entity_number, status,
           state, registered_agent, agent_address, source, confidence_score,
           loan_amount
    FROM `{config.BQ_TABLE_ENTITIES}`
    WHERE status = 'ACTIVE'
    """
    try:
        results = bq_client.query(query).result()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"  [WARN] Could not load entities: {e}")
        return []


def run_phase2():
    """Main Phase 2 execution."""
    print("=" * 60)
    print("OSINT PIPELINE — PHASE 2: People/Control Clusters")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    bq_client = bigquery.Client(project=config.GCP_PROJECT)

    # Load entities
    print("\n[1/4] Loading entities...")
    entities = load_entities(bq_client)
    print(f"  Loaded {len(entities)} active entities")

    # Extract people
    print("\n[2/4] Extracting people...")
    people = []
    for ent in entities:
        person = extract_person_from_entity(ent)
        if person:
            people.append(person)

    merged = merge_person_records(people)
    print(f"  Extracted {merged['total']} unique people")

    # Build control clusters
    print("\n[3/4] Building control clusters...")
    clusters = build_control_clusters(merged["people"], entities)
    print(f"  Found {len(clusters)} control clusters")

    # Export to BigQuery
    print("\n[4/4] Exporting to BigQuery and Neo4j...")

    # People
    if merged["people"]:
        rows = [person_to_bq_row(p) for p in merged["people"]]
        errors = bq_client.insert_rows_json(config.BQ_TABLE_PEOPLE, rows)
        if errors:
            print(f"  [ERROR] People insert: {errors}")
        else:
            print(f"  [OK] Inserted {len(rows)} people")

    # Control clusters
    if clusters:
        errors = bq_client.insert_rows_json(config.BQ_TABLE_CONTROL, clusters)
        if errors:
            print(f"  [ERROR] Control cluster insert: {errors}")
        else:
            print(f"  [OK] Inserted {len(clusters)} control clusters")

    # Neo4j export
    people_batch = export_entities(
        [{"entity_id": p["person_id"], "entity_name": p["full_name"],
          "entity_type": "PERSON", "source": p["source"],
          "confidence_score": p["confidence_score"]}
         for p in merged["people"]],
        batch_id="people",
    )
    print(f"  Neo4j people batch: {people_batch}")

    # Summary
    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE")
    print(f"  People: {merged['total']}")
    print(f"  Control clusters: {len(clusters)}")

    # Top clusters by risk
    top_clusters = sorted(clusters, key=lambda c: c.get("risk_score", 0), reverse=True)[:5]
    if top_clusters:
        print("\n  TOP RISK CLUSTERS:")
        for c in top_clusters:
            print(f"    Cluster {c['cluster_id']}: {c['total_entities']} entities, "
                  f"${c['total_loan_amount']:,.0f} loans, risk={c['risk_score']:.0f}")

    print("=" * 60)


if __name__ == "__main__":
    run_phase2()
