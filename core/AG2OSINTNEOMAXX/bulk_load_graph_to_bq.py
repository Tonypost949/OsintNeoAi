import os
import json
from datetime import datetime
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

# Project and Dataset configs
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "npi_forensic"
WORKSPACE = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"

client = bigquery.Client(project=PROJECT_ID)

# Define schemas
entity_addresses_schema = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("address_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("address_string", "STRING"),
    bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP"),
]

alerts_flagged_schema = [
    bigquery.SchemaField("alert_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("severity", "STRING"),
    bigquery.SchemaField("details", "STRING"),
]

def create_table_if_not_exists(table_name, schema):
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    table = bigquery.Table(table_ref, schema=schema)
    try:
        table = client.create_table(table)
        print(f"[OK] Table {table_ref} created successfully.")
    except Conflict:
        print(f"[INFO] Table {table_ref} already exists.")

def truncate_table(table_name):
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    query = f"TRUNCATE TABLE `{table_ref}`"
    try:
        client.query(query).result()
        print(f"[OK] Table {table_name} truncated/cleared successfully.")
    except Exception as e:
        print(f"[WARNING] Failed to truncate {table_name}: {e}")

def load_graph_data():
    nodes_path = os.path.join(WORKSPACE, "nodes.json")
    edges_path = os.path.join(WORKSPACE, "edges.json")
    
    with open(nodes_path, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(edges_path, "r", encoding="utf-8") as f:
        edges = json.load(f)
        
    return nodes, edges

def bulk_load():
    print("Initializing Table Creation and Schema Validation...")
    create_table_if_not_exists("entity_addresses", entity_addresses_schema)
    create_table_if_not_exists("alerts_flagged", alerts_flagged_schema)
    
    print("\nTruncating existing tables to ensure clean sync...")
    truncate_table("entities")
    truncate_table("nodes_person")
    truncate_table("edges_officer_of")
    truncate_table("entity_addresses")
    
    print("\nReading local graph nodes and edges...")
    nodes, edges = load_graph_data()
    print(f"Loaded {len(nodes)} nodes, {len(edges)} edges.")
    
    # 1. Populate Entities
    print("\nExtracting organizations...")
    entities_rows = []
    for n in nodes:
        if n.get("label") == "ORGANIZATION":
            name = n.get("name") or n.get("text") or n.get("id") or "unnamed"
            properties = n.get("properties") or {}
            jurisdiction = properties.get("jurisdiction") or "CA"
            entities_rows.append({
                "entity_id": n["id"],
                "name": name,
                "entity_type": properties.get("type") or "LLC",
                "jurisdiction": jurisdiction,
                "first_seen_date": datetime.today().date().isoformat(),
                "ingestion_timestamp": datetime.utcnow().isoformat(),
            })
            
    print(f" -> Found {len(entities_rows)} organization entities. Loading to BigQuery...")
    if entities_rows:
        errors = client.insert_rows_json(f"{PROJECT_ID}.{DATASET_ID}.entities", entities_rows)
        if errors:
            print(f"[ERROR] Loading entities failed: {errors}")
        else:
            print("[OK] Successfully ingested entities into BigQuery.")
            
    # 2. Populate Nodes Person
    print("\nExtracting person nodes...")
    person_rows = []
    # Count officer_of affiliations to fill total_affiliations field
    affiliations = {}
    for e in edges:
        if e.get("type") in ("OFFICER_OF", "MANAGER_OF", "MEMBER_OF") and e.get("source_label") == "PERSON":
            pid = e.get("source_id")
            affiliations[pid] = affiliations.get(pid, 0) + 1
            
    for n in nodes:
        if n.get("label") == "PERSON":
            pid = n["id"]
            name = n.get("name") or n.get("text") or pid or "unnamed"
            properties = n.get("properties") or {}
            person_rows.append({
                "person_id": pid,
                "name": name,
                "role_type": properties.get("role") or "OFFICER",
                "first_seen_date": datetime.today().date().isoformat(),
                "total_affiliations": affiliations.get(pid, 0),
                "ingestion_timestamp": datetime.utcnow().isoformat(),
            })
            
    print(f" -> Found {len(person_rows)} person nodes. Loading to BigQuery...")
    if person_rows:
        errors = client.insert_rows_json(f"{PROJECT_ID}.{DATASET_ID}.nodes_person", person_rows)
        if errors:
            print(f"[ERROR] Loading nodes_person failed: {errors}")
        else:
            print("[OK] Successfully ingested person nodes into BigQuery.")
            
    # 3. Populate Edges Officer Of
    print("\nExtracting officer relationships...")
    officer_rows = []
    for e in edges:
        if e.get("type") in ("OFFICER_OF", "MANAGER_OF", "MEMBER_OF") and e.get("source_label") == "PERSON" and e.get("target_label") == "ORGANIZATION":
            officer_rows.append({
                "person_id": e["source_id"],
                "entity_id": e["target_id"],
                "role": e["type"],
                "source_file": "nodes_edges_json",
                "ingestion_timestamp": datetime.utcnow().isoformat(),
            })
            
    print(f" -> Found {len(officer_rows)} officer relationships. Loading to BigQuery...")
    if officer_rows:
        errors = client.insert_rows_json(f"{PROJECT_ID}.{DATASET_ID}.edges_officer_of", officer_rows)
        if errors:
            print(f"[ERROR] Loading edges_officer_of failed: {errors}")
        else:
            print("[OK] Successfully ingested officer relationships into BigQuery.")
            
    # 4. Populate Entity Addresses
    print("\nExtracting entity registered address connections...")
    addr_rows = []
    for e in edges:
        if e.get("type") == "REGISTERED_AT" and e.get("source_label") == "ORGANIZATION" and e.get("target_label") == "ADDRESS":
            addr_rows.append({
                "entity_id": e["source_id"],
                "address_id": e["target_id"],
                "address_string": e["target_id"],
                "ingestion_timestamp": datetime.utcnow().isoformat(),
            })
            
    print(f" -> Found {len(addr_rows)} entity-address associations. Loading to BigQuery...")
    if addr_rows:
        errors = client.insert_rows_json(f"{PROJECT_ID}.{DATASET_ID}.entity_addresses", addr_rows)
        if errors:
            print(f"[ERROR] Loading entity_addresses failed: {errors}")
        else:
            print("[OK] Successfully ingested entity addresses into BigQuery.")
            
    print("\n=== BULK GRAPH SYNC PROCESS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    bulk_load()
