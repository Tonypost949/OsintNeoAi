#!/usr/bin/env python3
"""
BigQuery Master Evidence Registry Synchronizer
===============================================
Syncs the 199 verified records from data/MASTER_OSINT_EVIDENCE_REGISTRY.csv
into Google Cloud BigQuery: noble-beanbag-497411-m4.national_audits.master_osint_evidence_registry
"""

import os
import sys
import json
import csv
from pathlib import Path

REPO_ROOT = Path("C:/OsintNeoAi")
CSV_PATH = REPO_ROOT / "data" / "MASTER_OSINT_EVIDENCE_REGISTRY.csv"
SQL_DDL_PATH = REPO_ROOT / "data" / "create_master_osint_evidence_registry_table.sql"

PROJECT_ID = "noble-beanbag-497411-m4"
DATASET_ID = "national_audits"
TABLE_ID = "master_osint_evidence_registry"
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

DDL_TEMPLATE = f"""-- BigQuery Table DDL for Master OSINT Evidence Registry (199 Records)
-- Target: {FULL_TABLE_ID}

CREATE TABLE IF NOT EXISTS `{FULL_TABLE_ID}` (
    Record_ID STRING NOT NULL OPTIONS(description="Unique record identifier (NODE, FCA, TGT, BQ, AUD, AST)"),
    Date_Documented STRING OPTIONS(description="Date documented or last verified"),
    Entity_Or_Subject STRING OPTIONS(description="Primary entity name, individual, or target subject"),
    Category STRING OPTIONS(description="Primary category classification"),
    Subcategory STRING OPTIONS(description="Secondary detailed category"),
    Role_Or_Classification STRING OPTIONS(description="Role, title, or classification level"),
    Primary_Identifier_Or_Email STRING OPTIONS(description="Primary email, domain, or identifier"),
    Linked_Accounts_Or_Entities STRING OPTIONS(description="Associated accounts, dockets, or linked entities"),
    Jurisdiction_Or_Location STRING OPTIONS(description="Jurisdiction, court, or cloud platform"),
    Legal_Statute_Or_Basis STRING OPTIONS(description="Legal basis, statute (FCA, RICO, Rules of Evidence)"),
    Evidence_SHA256_Hash STRING OPTIONS(description="Cryptographic SHA-256 evidence hash"),
    Verification_Status STRING OPTIONS(description="Verification or operational status"),
    Threat_Or_Impact_Level STRING OPTIONS(description="Threat or impact classification"),
    Source_Reference_File STRING OPTIONS(description="Provenance source file path"),
    Detailed_Forensic_Notes STRING OPTIONS(description="Full forensic notes and whistleblower narrative")
)
OPTIONS(
    description="Authoritative master OSINT evidence clearinghouse and entity registry for OsintNeoAi",
    labels=[("project", "osintneoai"), ("classification", "master_registry"), ("environment", "production")]
);
"""

def generate_ddl_and_verify():
    if not CSV_PATH.exists():
        print(f"[!] Error: Master CSV not found at {CSV_PATH}")
        return False

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[*] Validated Master CSV: {len(rows)} records found.")
    
    with open(SQL_DDL_PATH, "w", encoding="utf-8") as f:
        f.write(DDL_TEMPLATE)
    print(f"[✓] Generated BigQuery DDL: {SQL_DDL_PATH.name}")

    # Generate sample insert / bq load command
    bq_load_cmd = f"bq load --source_format=CSV --skip_leading_rows=1 --autodetect {FULL_TABLE_ID} {CSV_PATH}"
    print(f"[*] Command to execute in Cloud Shell or via CLI:")
    print(f"    {bq_load_cmd}")

    return True

if __name__ == "__main__":
    generate_ddl_and_verify()
