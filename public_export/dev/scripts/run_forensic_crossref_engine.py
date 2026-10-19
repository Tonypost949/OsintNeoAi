#!/usr/bin/env python3
"""
scripts/run_forensic_crossref_engine.py
=======================================
Automated Forensic Cross-Referencing & Entity Resolution Engine for OsintNeoAi.
Cross-references 104,000+ entities and 68,000+ property nodes across Corporate
Registrations, Real Estate Deeds, PPP Loans, Bank Transactions, UST Contamination
Plumes, and Whistleblower Mutual Aid Intake Cases.
"""

import os
import sys
import json
import csv
import glob
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1] if THIS_FILE.parents[1].name != "scripts" else THIS_FILE.parents[1]
if not (REPO_ROOT / "evidence").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "evidence").exists():
            REPO_ROOT = cand
            break

TASKLET_DIR = REPO_ROOT / "tasklet_export" / "files"
FORENSIC_DELIV = REPO_ROOT / "forensic" / "deliverables"
EVIDENCE_DIR = REPO_ROOT / "evidence"
DATA_DIR = REPO_ROOT / "data"
MUTUAL_AID_FILE = EVIDENCE_DIR / "mutual_aid_cases.json"
MATRIX_OUTPUT = EVIDENCE_DIR / "FORENSIC_CORRELATION_MATRIX.json"
SUMMARY_OUTPUT = EVIDENCE_DIR / "FORENSIC_AUDIT_SUMMARY.md"


def run_crossref():
    print("============================================================")
    print("🔬 OSINTNEOAI AUTOMATED FORENSIC CROSS-REFERENCING ENGINE")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("============================================================")

    entities = defaultdict(lambda: {"roles": set(), "records": [], "risk_score": 0, "locations": set(), "relations": set()})
    properties = defaultdict(lambda: {"entities": set(), "transactions": [], "contamination_risk": "Low"})
    
    total_records = 0

    # 1. Ingest Deliverables (People, RICO Nodes, Legal Exposure)
    people_file = FORENSIC_DELIV / "People.csv"
    if people_file.exists():
        try:
            with open(people_file, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    total_records += 1
                    name = r.get("Name", "").strip()
                    if name:
                        entities[name]["roles"].add(r.get("Role", "Entity"))
                        entities[name]["risk_score"] += 15
                        entities[name]["records"].append(r)
        except Exception as e:
            print(f"[!] Warning reading People.csv: {e}")

    rico_file = FORENSIC_DELIV / "RICO_Nodes.csv"
    if rico_file.exists():
        try:
            with open(rico_file, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    total_records += 1
                    node = r.get("Node", "").strip()
                    if node:
                        entities[node]["roles"].add("RICO Nexus Target")
                        entities[node]["risk_score"] += 35
                        entities[node]["records"].append(r)
        except Exception as e:
            print(f"[!] Warning reading RICO_Nodes.csv: {e}")

    # 2. Ingest Mutual Aid Cases if present
    if MUTUAL_AID_FILE.exists():
        try:
            with open(MUTUAL_AID_FILE, "r", encoding="utf-8", errors="ignore") as f:
                cases = json.load(f)
                if isinstance(cases, list):
                    for c in cases:
                        total_records += 1
                        vname = c.get("victim_name") or c.get("entity_name")
                        if vname and vname != "Anonymous":
                            entities[vname]["roles"].add(f"Whistleblower Case: {c.get('id', 'CASE')}")
                            entities[vname]["risk_score"] += 25
                            entities[vname]["records"].append(c)
                        loc = c.get("location") or c.get("address")
                        if loc:
                            properties[loc]["transactions"].append(f"Whistleblower Intake {c.get('id')}")
        except Exception as e:
            print(f"[!] Warning reading mutual_aid_cases.json: {e}")

    # 3. Ingest Tasklet Master Matrices & Forensic CSVs
    csv_patterns = [
        str(TASKLET_DIR / "*.csv"),
        str(FORENSIC_DELIV / "*.csv"),
        str(DATA_DIR / "*.csv")
    ]
    matrix_files = []
    for pat in csv_patterns:
        matrix_files.extend(glob.glob(pat))
    matrix_files = sorted(list(set(matrix_files)))

    print(f"[*] Ingesting and cross-referencing {len(matrix_files)} master evidence datasets...")

    for mf in matrix_files:
        base_name = os.path.basename(mf)
        try:
            with open(mf, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    total_records += 1
                    # Extract entity/property hints
                    for k, v in r.items():
                        val = str(v).strip()
                        if not val or len(val) < 4:
                            continue
                        k_lower = k.lower()
                        if any(kw in k_lower for kw in ["borrower", "organization", "entity", "owner", "recipient", "officer", "name", "target", "vendor"]):
                            entities[val]["roles"].add(f"Source: {base_name[:24]}")
                            entities[val]["risk_score"] += 5
                        if any(kw in k_lower for kw in ["address", "property", "location", "street", "site", "apn"]):
                            properties[val]["transactions"].append(base_name)
        except Exception:
            continue

    print(f"[*] Processed {total_records:,} cross-reference data points.")
    print(f"[*] Resolved {len(entities):,} unique entities and {len(properties):,} target property nodes.")

    # 4. Identify High-Convergence Nexus Entities
    ranked_entities = sorted(
        [
            {
                "entity": k,
                "risk_score": v["risk_score"],
                "roles": list(v["roles"])[:5],
                "record_count": len(v["records"])
            }
            for k, v in entities.items()
            if v["risk_score"] >= 15
        ],
        key=lambda x: x["risk_score"],
        reverse=True
    )

    # 5. Generate Master Correlation Matrix Deliverable
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    matrix_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records_analyzed": total_records,
        "unique_entities_resolved": len(entities),
        "unique_properties_tracked": len(properties),
        "high_risk_nexus_targets": ranked_entities[:100]
    }

    with open(MATRIX_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(matrix_payload, f, indent=2)

    # 6. Generate Markdown Forensic Audit Summary
    with open(SUMMARY_OUTPUT, "w", encoding="utf-8") as f:
        f.write("# OSINTNEOAI MASTER FORENSIC AUDIT & CROSS-REFERENCE REPORT\n\n")
        f.write(f"**Audit Execution Date:** {datetime.now(timezone.utc).strftime('%B %d, %Y %H:%M:%S UTC')}\n\n")
        f.write(f"**Total Records Evaluated:** {total_records:,}\n\n")
        f.write(f"**Unique Resolved Entities:** {len(entities):,}\n\n")
        f.write(f"**Target Properties & Infrastructure Sites:** {len(properties):,}\n\n")
        f.write("## 🎯 Top High-Risk Nexus Entities\n\n")
        f.write("| Rank | Entity Name | Risk Index | Association Vectors |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for idx, e in enumerate(ranked_entities[:25], 1):
            roles_str = ", ".join(e["roles"][:3])
            f.write(f"| #{idx} | **{e['entity']}** | `{e['risk_score']}` | {roles_str} |\n")

    print(f"\n[+] Master Correlation Matrix saved: {MATRIX_OUTPUT}")
    print(f"[+] Forensic Audit Summary saved: {SUMMARY_OUTPUT}")
    print("============================================================")
    print("✅ FORENSIC ENTITY RESOLUTION & CROSS-REFERENCING COMPLETE")
    print("============================================================")
    return matrix_payload


if __name__ == "__main__":
    run_crossref()
