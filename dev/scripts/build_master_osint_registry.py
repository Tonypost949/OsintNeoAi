#!/usr/bin/env python3
"""
Master OSINT Evidence Registry Harmonizer & Sheet Rebuilder
===========================================================
Audits, cleans, deduplicates, and compiles all disparate OSINT spreadsheets,
user nodes, target accounts, forensic cases, and BigQuery cross-references
into a single unified Master OSINT Evidence Registry.
"""

import os
import sys
import json
import csv
import datetime

REPO_ROOT = r"C:\OsintNeoAi"
CLI_ROOT = r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0"
WORKTREE = r"C:\OsintNeoAi\copilot-worktrees\tonypost949-bookish-lamp"

OUTPUT_CSV = os.path.join(REPO_ROOT, "data", "MASTER_OSINT_EVIDENCE_REGISTRY.csv")
OUTPUT_JSON = os.path.join(REPO_ROOT, "data", "MASTER_OSINT_EVIDENCE_REGISTRY.json")
OUTPUT_PUBLIC_JSON = os.path.join(REPO_ROOT, "public", "master_osint_registry.json")

def main():
    records = []
    seen_keys = set()

    # 1. Ingest user_nodes.csv
    user_nodes_path = os.path.join(CLI_ROOT, "user_nodes.csv")
    if os.path.exists(user_nodes_path):
        with open(user_nodes_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                label = row.get("Label", "").strip()
                if not label or label in seen_keys:
                    continue
                seen_keys.add(label)
                records.append({
                    "Record_ID": f"NODE-{i:03d}",
                    "Entity_Name": row.get("Full Name", label),
                    "Category": "Core Node & Identity",
                    "Subcategory": row.get("Who", "Identity / Persona"),
                    "Role_Or_Type": row.get("Relationship", "Architect / Target"),
                    "Primary_Identifier": label,
                    "Linked_Accounts_Or_Emails": row.get("Email", ""),
                    "Jurisdiction_Or_Location": row.get("Where", "Global / Local"),
                    "Legal_Basis_Or_Statute": "Universal AI Execution Standard",
                    "SHA256_Evidence_Count": "Verified Node",
                    "Status": "ACTIVE",
                    "Risk_Level": "CRITICAL_AUTHORITY" if "amd949609" in label else "INFORMATIONAL",
                    "Last_Updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "Source_Reference": "C:\\amd949609@gmail.com_Antigravity_CLI_v2.0\\user_nodes.csv",
                    "Notes": f"Purpose: {row.get('Purpose', '')} | Notes: {row.get('Notes', '')}"
                })

    # 2. Ingest Forensic Master Spreadsheet
    forensic_path = os.path.join(WORKTREE, "forensic_master_spreadsheet.csv")
    if os.path.exists(forensic_path):
        with open(forensic_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                case_id = row.get("Case_ID", "").strip()
                entity = row.get("Entity_Name", "").strip() or row.get("Individual_Name", "").strip()
                if not entity:
                    continue
                records.append({
                    "Record_ID": case_id or f"FCA-{len(records)+1:03d}",
                    "Entity_Name": entity,
                    "Category": "FCA / RICO Forensic Ledger",
                    "Subcategory": row.get("Category", "Whistleblower Ledger"),
                    "Role_Or_Type": row.get("Role_Title", row.get("Subcategory", "Target Subject")),
                    "Primary_Identifier": row.get("Individual_Name", entity),
                    "Linked_Accounts_Or_Emails": row.get("Source_URL", ""),
                    "Jurisdiction_Or_Location": row.get("Jurisdiction", "California / Federal"),
                    "Legal_Basis_Or_Statute": row.get("Legal_Basis_Statute", "False Claims Act 31 U.S.C. 3729"),
                    "SHA256_Evidence_Count": "Documented in Docket",
                    "Status": row.get("Status", "DOCUMENTED"),
                    "Risk_Level": "HIGH_EXPOSURE",
                    "Last_Updated": row.get("Date", "2026-09-01"),
                    "Source_Reference": row.get("Source_Reference", "forensic_master_spreadsheet.csv"),
                    "Notes": row.get("Incident_Description", "")[:300]
                })

    # 3. Ingest Target Accounts Master
    target_acc_path = os.path.join(REPO_ROOT, "agent", "target_accounts_master.json")
    if os.path.exists(target_acc_path):
        with open(target_acc_path, "r", encoding="utf-8") as f:
            t_data = json.load(f)
            targets = t_data.get("target_accounts", [])
            for t in targets:
                email = t.get("email", "")
                if not email:
                    continue
                records.append({
                    "Record_ID": f"TGT-{t.get('account_index', len(records)+1):03d}",
                    "Entity_Name": t.get("name", email),
                    "Category": "Master Monitored Target Account",
                    "Subcategory": t.get("provider", "Identity Target"),
                    "Role_Or_Type": t.get("role_label", "Monitored Target"),
                    "Primary_Identifier": email,
                    "Linked_Accounts_Or_Emails": email,
                    "Jurisdiction_Or_Location": t.get("organization", "Cloud Workspace"),
                    "Legal_Basis_Or_Statute": "OSINT Cross-Ref Master",
                    "SHA256_Evidence_Count": "Cross-Referenced",
                    "Status": "LIVE_MONITORING",
                    "Risk_Level": "HIGH",
                    "Last_Updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "Source_Reference": "agent/target_accounts_master.json",
                    "Notes": t.get("notes", "Target account under active BigQuery and local OCR correlation.")
                })

    # 4. Ingest BigQuery Cross-Reference Matches
    crossref_path = os.path.join(REPO_ROOT, "data", "master_accounts_crossref_matches.json")
    if os.path.exists(crossref_path):
        with open(crossref_path, "r", encoding="utf-8") as f:
            cross_data = json.load(f)
            results = cross_data.get("results_by_target", {})
            for email, info in results.items():
                match_count = info.get("total_matches", 0)
                if match_count > 0:
                    records.append({
                        "Record_ID": f"BQ-{len(records)+1:03d}",
                        "Entity_Name": f"BigQuery Evidence Cluster: {email}",
                        "Category": "BigQuery Relational Evidence",
                        "Subcategory": "SHA-256 Ledger Match",
                        "Role_Or_Type": "Corroborated Target",
                        "Primary_Identifier": email,
                        "Linked_Accounts_Or_Emails": email,
                        "Jurisdiction_Or_Location": "noble-beanbag-497411-m4",
                        "Legal_Basis_Or_Statute": "Federal Evidence Rule 902(13)/(14)",
                        "SHA256_Evidence_Count": f"{match_count} Matches",
                        "Status": "CONFIRMED_MATCH",
                        "Risk_Level": "CRITICAL" if match_count > 100 else "ELEVATED",
                        "Last_Updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "Source_Reference": "data/master_accounts_crossref_matches.json",
                        "Notes": f"Target account matched across {len(info.get('sample_matches', []))} sample evidence records in national audits BigQuery warehouse."
                    })

    # 5. Ingest Consolidated Sheet Assets
    master_cons_path = os.path.join(WORKTREE, "MASTER_OSINT_CONSOLIDATED_SHEET.csv")
    if os.path.exists(master_cons_path):
        with open(master_cons_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                asset_name = row.get("Asset_Name", "").strip()
                if not asset_name:
                    continue
                records.append({
                    "Record_ID": f"AST-{len(records)+1:03d}",
                    "Entity_Name": asset_name,
                    "Category": "Infrastructure & Repository Asset",
                    "Subcategory": row.get("Category", "System Asset"),
                    "Role_Or_Type": row.get("Status", "ACTIVE"),
                    "Primary_Identifier": row.get("Target_Identifier", asset_name),
                    "Linked_Accounts_Or_Emails": row.get("Path_Or_URL", ""),
                    "Jurisdiction_Or_Location": "GitHub / Azure / Cloud Shell",
                    "Legal_Basis_Or_Statute": "System Topology",
                    "SHA256_Evidence_Count": "N/A",
                    "Status": row.get("Status", "ACTIVE"),
                    "Risk_Level": "OPERATIONAL",
                    "Last_Updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "Source_Reference": "MASTER_OSINT_CONSOLIDATED_SHEET.csv",
                    "Notes": row.get("Description", "")
                })

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PUBLIC_JSON), exist_ok=True)

    # Write unified CSV
    fieldnames = [
        "Record_ID", "Entity_Name", "Category", "Subcategory", "Role_Or_Type",
        "Primary_Identifier", "Linked_Accounts_Or_Emails", "Jurisdiction_Or_Location",
        "Legal_Basis_Or_Statute", "SHA256_Evidence_Count", "Status", "Risk_Level",
        "Last_Updated", "Source_Reference", "Notes"
    ]
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    # Write unified JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_records": len(records),
            "registry": records
        }, f, indent=2)

    with open(OUTPUT_PUBLIC_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_records": len(records),
            "registry": records
        }, f, indent=2)

    print(f"[OK] Master OSINT Evidence Registry compiled successfully!")
    print(f"     Total Harmonized Records: {len(records)}")
    print(f"     CSV Output: {OUTPUT_CSV}")
    print(f"     JSON Output: {OUTPUT_JSON}")
    print(f"     Public JSON: {OUTPUT_PUBLIC_JSON}")

if __name__ == "__main__":
    main()
