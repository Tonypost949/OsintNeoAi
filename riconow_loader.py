#!/usr/bin/env python3
"""
Riconow Direct Loader (Upgraded)
================================
A highly optimized, direct-load pipeline that consumes normalized Name,Role,Company CSVs
and streams them into the active graph structure, bypassing complex column mapping heuristics.
Supports optional Address columns, temporal batch tracing, and robust edge deduplication.
"""

import os
import csv
import json
import uuid
import datetime
from pathlib import Path

# Paths to the active graph database
NODES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/nodes.json")
EDGES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/edges.json")

def load_riconow_csv(csv_path: str, batch_id: str = None):
    """
    Reads a normalized Name,Role,Company (and optional Address) CSV and merges it directly
    into the nodes.json and edges.json database.
    """
    if not os.path.exists(csv_path):
        print(f"[ERROR] Source CSV path not found: {csv_path}")
        return False
        
    print(f"[+] Loading direct CSV: {csv_path}")
    
    # Generate a unique batch ID if not provided
    if not batch_id:
        batch_id = f"batch_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    ingested_at = datetime.datetime.utcnow().isoformat() + "Z"
    
    new_records = []
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Normalize headers
            headers = {h.strip().lower(): h for h in reader.fieldnames if h}
            
            # Identify mapped columns
            name_col = next((headers[k] for k in ["name", "person", "officer", "individual"] if k in headers), None)
            role_col = next((headers[k] for k in ["role", "type", "relationship"] if k in headers), None)
            company_col = next((headers[k] for k in ["company", "organization", "entity"] if k in headers), None)
            address_col = next((headers[k] for k in ["address", "registered_address", "location"] if k in headers), None)
            
            for row in reader:
                name = row.get(name_col) if name_col else None
                role = (row.get(role_col) if role_col else "OFFICER_OF") or "OFFICER_OF"
                company = row.get(company_col) if company_col else None
                address = row.get(address_col) if address_col else None
                
                if name and company:
                    new_records.append({
                        "name": name.strip(),
                        "role": role.strip(),
                        "company": company.strip(),
                        "address": address.strip() if address else None
                    })
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        return False

    print(f"[+] Parsed {len(new_records)} normalized records (Batch: {batch_id}).")
    
    if not new_records:
        print("[-] No records to ingest.")
        return True
        
    # Load active database
    if not NODES_PATH.exists() or not EDGES_PATH.exists():
        print("[ERROR] Riconow database not initialized.")
        return False
        
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(EDGES_PATH, "r", encoding="utf-8") as f:
        edges = json.load(f)
        
    # Convert list of nodes/edges to sets for fast deduplication
    node_ids = {n["id"] for n in nodes}
    edge_keys = {(e["source_id"], e["target_id"], e.get("type")) for e in edges}
    
    nodes_added = 0
    edges_added = 0
    
    for rec in new_records:
        person_id = rec["name"]
        company_id = rec["company"]
        role_type = rec["role"]
        address_id = rec["address"]
        
        # 1. Add Person Node if missing
        if person_id not in node_ids:
            nodes.append({
                "id": person_id,
                "label": "PERSON",
                "properties": {
                    "name": person_id,
                    "batch_id": batch_id,
                    "ingested_at": ingested_at
                }
            })
            node_ids.add(person_id)
            nodes_added += 1
            
        # 2. Add Company Node if missing
        if company_id not in node_ids:
            nodes.append({
                "id": company_id,
                "label": "ORGANIZATION",
                "properties": {
                    "name": company_id,
                    "batch_id": batch_id,
                    "ingested_at": ingested_at
                }
            })
            node_ids.add(company_id)
            nodes_added += 1
            
        # 3. Add Person -> Company Edge
        edge_key = (person_id, company_id, role_type)
        if edge_key not in edge_keys:
            edges.append({
                "source_id": person_id,
                "source_label": "PERSON",
                "type": role_type,
                "target_id": company_id,
                "target_label": "ORGANIZATION",
                "properties": {
                    "batch_id": batch_id,
                    "ingested_at": ingested_at
                }
            })
            edge_keys.add(edge_key)
            edges_added += 1
            
        # 4. Optional Address Ingestion & Relationship
        if address_id:
            if address_id not in node_ids:
                nodes.append({
                    "id": address_id,
                    "label": "ADDRESS",
                    "properties": {
                        "address": address_id,
                        "type": "REGISTERED",
                        "batch_id": batch_id,
                        "ingested_at": ingested_at
                    }
                })
                node_ids.add(address_id)
                nodes_added += 1
                
            # Connect Company -> Registered Address
            addr_edge_key = (company_id, address_id, "REGISTERED_AT")
            if addr_edge_key not in edge_keys:
                edges.append({
                    "source_id": company_id,
                    "source_label": "ORGANIZATION",
                    "type": "REGISTERED_AT",
                    "target_id": address_id,
                    "target_label": "ADDRESS",
                    "properties": {
                        "batch_id": batch_id,
                        "ingested_at": ingested_at
                    }
                })
                edge_keys.add(addr_edge_key)
                edges_added += 1

    # Save back to database
    with open(NODES_PATH, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2)
    with open(EDGES_PATH, "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2)
        
    print(f"[SUCCESS] Ingestion completed. Added {nodes_added} nodes and {edges_added} edges.")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python riconow_loader.py <path_to_csv> [batch_id]")
    else:
        b_id = sys.argv[2] if len(sys.argv) > 2 else None
        load_riconow_csv(sys.argv[1], b_id)

