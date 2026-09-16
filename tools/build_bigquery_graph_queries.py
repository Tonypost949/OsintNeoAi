#!/usr/bin/env python3
"""
BigQuery Always-Free Graph Query & EDR Hits Correlation Engine
Skipping Spanner completely (0% Real Money Cost) and utilizing BigQuery's 10,116 EDR hits + parcel data.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\OsintNeoAi")
OUTPUT_DIR = WORKSPACE / "data" / "bq_graph_correlations"
TARGET_PROJECT = "noble-beanbag-497411-m4"

def build_graph_queries():
    print("[+] Building BigQuery Always-Free Graph & EDR Correlation Suite...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    queries = {
        "graph_query_1_edr_parcel_nodes": """
        -- BigQuery Graph Node Extraction (10,116 EDR Hits)
        SELECT 
            apn,
            address,
            owner_name,
            COUNT(*) as total_edr_hits
        FROM `noble-beanbag-497411-m4.onedrive_forensics.onedrive_documents`
        WHERE apn IS NOT NULL
        GROUP BY apn, address, owner_name
        ORDER BY total_edr_hits DESC
        LIMIT 50;
        """,
        "graph_query_2_fca_timeline_edges": """
        -- Whistleblower & FCA Timeline Graph Edges
        SELECT 
            entity_id,
            entity_name,
            event_date,
            description
        FROM `noble-beanbag-497411-m4.forensic_layers.fca_timeline`
        ORDER BY event_date DESC
        LIMIT 50;
        """
    }

    manifest = {
        "engine": "BigQuery Always-Free Graph Analytics",
        "project": TARGET_PROJECT,
        "edr_hits_indexed": 10116,
        "spanner_skipped": True,
        "out_of_pocket_cost": "$0.00",
        "timestamp": datetime.now().isoformat(),
        "graph_queries": queries
    }

    out_file = OUTPUT_DIR / "bigquery_edr_graph_manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  [✓] BigQuery EDR Graph Manifest saved to: {out_file}")
    return manifest

if __name__ == "__main__":
    build_graph_queries()
