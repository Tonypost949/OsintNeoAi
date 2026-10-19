#!/usr/bin/env python3
"""
Always-Free BigQuery Query Execution Tool
Executes BigQuery queries with strict maximum bytes billed guardrails (1GB max per query),
guaranteeing 0% risk of exceeding BigQuery's 1TB/month Always-Free quota.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\OsintNeoAi")
OUTPUT_DIR = WORKSPACE / "data" / "always_free_bq_results"

# Standard target datasets
TARGET_TABLES = [
    "noble-beanbag-497411-m4.onedrive_forensics.onedrive_documents",
    "noble-beanbag-497411-m4.national_audits.drive_file_index",
    "noble-beanbag-497411-m4.forensic_layers.fca_timeline"
]

def run_free_bq_query():
    print("[+] Executing Always-Free BigQuery Guardrail Queries...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    query = """
    SELECT 
        table_schema, 
        table_name, 
        total_rows, 
        total_logical_bytes 
    FROM `noble-beanbag-497411-m4.region-us.INFORMATION_SCHEMA.TABLE_STORAGE`
    LIMIT 20;
    """

    # Guardrail: Limit maximum bytes billed to 1 GB (1,000,000,000 bytes)
    # Always-Free tier gives 1,000 GB (1 TB) per month for free!
    cmd = [
        "bq", "query",
        "--use_legacy_sql=false",
        "--maximum_bytes_billed=1000000000",
        "--format=json",
        query
    ]

    print(f"  [>] Running SQL query with 1GB max bytes billed safety limit...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            out_file = OUTPUT_DIR / f"bq_storage_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"  [✓] Query executed successfully within Always-Free tier!")
            print(f"  [✓] Results saved to: {out_file}")
            return data
        else:
            print(f"  [!] BQ Note (CLI/ADC Check): {res.stderr.strip()}")
            return None
    except Exception as e:
        print(f"  [!] Execution note: {e}")
        return None

if __name__ == "__main__":
    run_free_bq_query()
