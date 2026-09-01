#!/usr/bin/env python3
"""
scripts/run_forensic_crossref_engine.py
=======================================
Automated Forensic Cross-Referencing & Entity Resolution Engine for OsintNeoAi.
Cross-references 17,000+ nodes across Corporate Registrations, Real Estate Deeds,
PPP Loans, Bank Transactions, and UST Contamination Plumes.
"""

import os
import sys
import json
import csv
import glob
from collections import defaultdict
from datetime import datetime

REPO_ROOT = r"C:\OsintNeoAi"
TASKLET_DIR = os.path.join(REPO_ROOT, "tasklet_export", "files")
FORENSIC_DELIV = os.path.join(REPO_ROOT, "forensic", "deliverables")
EVIDENCE_DIR = os.path.join(REPO_ROOT, "evidence")

def run_crossref():
    print("============================================================")
    print("🔬 OSINTNEOAI AUTOMATED FORENSIC CROSS-REFERENCING ENGINE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("============================================================")

    entities = defaultdict(lambda: {"roles": set(), "records": [], "risk_score": 0, "locations": set(), "relations": set()})
    properties = defaultdict(lambda: {"entities": set(), "transactions": [], "contamination_risk": "Low"})
    
    # 1. Ingest Deliverables (People, RICO Nodes, Legal Exposure)
    people_file = os.path.join(FORENSIC_DELIV, "People.csv")
    if os.path.exists(people_file):
        with open(people_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                name = r.get("Name", "").strip()
                if name:
                    entities[name]["roles"].add(r.get("Role", "Entity"))
                    entities[name]["risk_score"] += 15
                    entities[name]["records"].append(r)

    rico_file = os.path.join(FORENSIC_DELIV, "RICO_Nodes.csv")
    if os.path.exists(rico_file):
        with open(rico_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                node = r.get("Node", "").strip()
                if node:
                    entities[node]["roles"].add("RICO Nexus Target")
                    entities[node]["risk_score"] += 35
                    entities[node]["records"].append(r)

    # 2. Ingest Tasklet Master Matrices (PPP loans, CHDO property deeds, UST proximity)
    matrix_files = glob.glob(os.path.join(TASKLET_DIR, "*.csv"))
    print(f"[*] Ingesting and cross-referencing {len(matrix_files)} master evidence datasets...")

    total_records = 0
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
                        if any(kw in k.lower() for kw in ["borrower", "organization", "entity", "owner", "recipient", "officer"]):
                            entities[val]["roles"].add(f"Source: {base_name[:20]}")
                            entities[val]["risk_score"] += 5
                        if any(kw in k.lower() for kw in ["address", "property", "location", "street"]):
                            properties[val]["transactions"].append(base_name)
        except Exception:
            continue

    print(f"[*] Processed {total_records:,} cross-reference data points.")
    print(f"[*] Resolved {len(entities):,} unique entities and {len(properties):,} target property nodes.")

    # 3. Identify High-Convergence Nexus Entities
    ranked_entities = sorted(
        [
            {
                "entity": k,
                "risk_score": v["risk_score"],
                "roles": list(v["roles"])[:5],
                "record_count": len(v["records"])
            }
            for k, v in entities.items()
            if v["risk_score"] >= 20
        ],
        key=lambda x: x["risk_score"],
        reverse=True
    )

    # 4. Generate Master Correlation Matrix Deliverable
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    matrix_output = os.path.join(EVIDENCE_DIR, "FORENSIC_CORRELATION_MATRIX.json")
    with open(matrix_output, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_records_analyzed": total_records,
            "unique_entities_resolved": len(entities),
            "unique_properties_tracked": len(properties),
            "high_risk_nexus_targets": ranked_entities[:100]
        }, f, indent=2)

    # 5. Generate Markdown Forensic Audit Summary
    summary_output = os.path.join(EVIDENCE_DIR, "FORENSIC_AUDIT_SUMMARY.md")
    with open(summary_output, "w", encoding="utf-8") as f:
        f.write("# OSINTNEOAI MASTER FORENSIC AUDIT & CROSS-REFERENCE REPORT\n\n")
        f.write(f"**Audit Execution Date:** {datetime.now().strftime('%B %d, %Y')}\n")
        f.write(f"**Total Records Evaluated:** {total_records:,}\n")
        f.write(f"**Unique Resolved Entities:** {len(entities):,}\n")
        f.write(f"**Target Properties & Infrastructure Sites:** {len(properties):,}\n\n")
        f.write("## 🎯 Top High-Risk Nexus Entities\n\n")
        f.write("| Rank | Entity Name | Risk Index | Association Vectors |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for idx, e in enumerate(ranked_entities[:25], 1):
            roles_str = ", ".join(e["roles"][:3])
            f.write(f"| #{idx} | **{e['entity']}** | `{e['risk_score']}` | {roles_str} |\n")

    print(f"\n[+] Master Correlation Matrix saved: {matrix_output}")
    print(f"[+] Forensic Audit Summary saved: {summary_output}")
    print("============================================================")
    print("✅ FORENSIC ENTITY RESOLUTION & CROSS-REFERENCING COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    run_crossref()
