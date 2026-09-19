#!/usr/bin/env python3
"""
Auto-Tag BigQuery Audit Files & Records with Law IDs (LAW-XXX).
Links every cost, public deal, land contract, or toxic risk record to governing legal statutes.
"""

import os
import json
from datetime import datetime
from google.cloud import bigquery

PROJECT_ID = "noble-beanbag-497411-m4"

LAW_MAPPING_RULES = [
    {
        "law_id": "LAW-001",
        "code": "Cal. Gov. Code § 1090",
        "title": "Prohibition Against Financial Interest in Public Contracts",
        "keywords": ["contract", "purchase", "vendor", "agreement", "lease", "land", "asphalt", "bid", "payment"],
        "category": "FINANCIAL_COST_AND_CONTRACTS",
        "hyperlink": "[Cal. Gov. Code § 1090](file:///C:/OsintNeoAi/statutory_legal_mapping_registry.json#L6-L10)"
    },
    {
        "law_id": "LAW-002",
        "code": "Cal. Gov. Code § 87100 (PRA)",
        "title": "Conflict of Interest & Form 700 Disclosure",
        "keywords": ["conflict", "form 700", "interest", "disclosure", "trust", "official", "economic"],
        "category": "FINANCIAL_COST_AND_CONTRACTS",
        "hyperlink": "[Cal. Gov. Code § 87100](file:///C:/OsintNeoAi/statutory_legal_mapping_registry.json#L11-L15)"
    },
    {
        "law_id": "LAW-003",
        "code": "31 U.S.C. § 3729 (False Claims Act)",
        "title": "Federal Qui Tam & Public Waste Liability",
        "keywords": ["false claim", "qui tam", "fraud", "overbilling", "grant", "waste", "federal fund"],
        "category": "FINANCIAL_COST_AND_CONTRACTS",
        "hyperlink": "[31 U.S.C. § 3729](file:///C:/OsintNeoAi/statutory_legal_mapping_registry.json#L16-L20)"
    },
    {
        "law_id": "LAW-004",
        "code": "Cal. Health & Safety Code § 25249.5 (Prop 65)",
        "title": "Toxic Chemical & Carcinogen Discharge Prohibition",
        "keywords": ["chromium", "lead", "arsenic", "dust", "toxic", "prop 65", "carcinogen", "contamination"],
        "category": "PHYSICAL_HARM_AND_ENVIRONMENTAL_RISK",
        "hyperlink": "[Cal. Health & Safety Code § 25249.5](file:///C:/OsintNeoAi/statutory_legal_index.html#L65-L68)"
    },
    {
        "law_id": "LAW-005",
        "code": "Cal. Pub. Res. Code § 21000 (CEQA)",
        "title": "California Environmental Quality Act Mandatory Review",
        "keywords": ["ceqa", "environmental", "impact report", "eir", "remediation", "public health"],
        "category": "PHYSICAL_HARM_AND_ENVIRONMENTAL_RISK",
        "hyperlink": "[Cal. Pub. Res. Code § 21000](file:///C:/OsintNeoAi/statutory_legal_index.html#L69-L72)"
    },
    {
        "law_id": "LAW-006",
        "code": "42 U.S.C. § 9601 (CERCLA / Superfund)",
        "title": "Comprehensive Environmental Response & Liability",
        "keywords": ["superfund", "cercla", "hazardous", "cap warranty", "release", "cleanup"],
        "category": "PHYSICAL_HARM_AND_ENVIRONMENTAL_RISK",
        "hyperlink": "[42 U.S.C. § 9601](file:///C:/OsintNeoAi/statutory_legal_index.html#L70-L74)"
    },
    {
        "law_id": "LAW-007",
        "code": "Cal. Gov. Code § 54956.8 (Brown Act)",
        "title": "Real Property Negotiation Disclosure Mandate",
        "keywords": ["brown act", "closed session", "real property", "price", "terms", "negotiation"],
        "category": "DEALS_TRADES_AND_AGREEMENTS",
        "hyperlink": "[Cal. Gov. Code § 54956.8](file:///C:/OsintNeoAi/statutory_legal_index.html#L91-L95)"
    },
    {
        "law_id": "LAW-008",
        "code": "Cal. Gov. Code § 6250 (CPRA / Public Records)",
        "title": "Mandatory Public Access to Government Contracts & Agreements",
        "keywords": ["cpra", "public record", "foia", "inspection", "agency agreement", "public right"],
        "category": "DEALS_TRADES_AND_AGREEMENTS",
        "hyperlink": "[Cal. Gov. Code § 6250](file:///C:/OsintNeoAi/statutory_legal_index.html#L96-L100)"
    }
]

def auto_tag_bigquery_tables():
    print(f"[*] Connecting to BigQuery Project: {PROJECT_ID}...")
    client = bigquery.Client(project=PROJECT_ID)

    tagged_results = {
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "total_tagged_records": 0,
        "law_id_breakdown": {},
        "records": []
    }

    datasets = ["drive_forensics", "forensic_layers", "national_audits", "onedrive_forensics"]
    
    for ds in datasets:
        print(f"[*] Scanning dataset: {ds}...")
        try:
            tables = list(client.list_tables(f"{PROJECT_ID}.{ds}"))
            for tbl in tables:
                table_id = f"{PROJECT_ID}.{ds}.{tbl.table_id}"
                print(f"  - Auditing table: {table_id}...")
                
                # Fetch sample rows for tagging
                query = f"SELECT * FROM `{table_id}` LIMIT 100"
                try:
                    query_job = client.query(query)
                    rows = list(query_job.result())
                    
                    for row in rows:
                        row_dict = dict(row)
                        row_str = json.dumps(row_dict, default=str).lower()
                        
                        matched_laws = []
                        for rule in LAW_MAPPING_RULES:
                            if any(kw in row_str for kw in rule["keywords"]):
                                matched_laws.append({
                                    "law_id": rule["law_id"],
                                    "code": rule["code"],
                                    "title": rule["title"],
                                    "hyperlink": rule["hyperlink"]
                                })
                                tagged_results["law_id_breakdown"][rule["law_id"]] = tagged_results["law_id_breakdown"].get(rule["law_id"], 0) + 1

                        if matched_laws:
                            tagged_results["total_tagged_records"] += 1
                            tagged_results["records"].append({
                                "table": table_id,
                                "matched_laws": matched_laws,
                                "sample_data": {k: str(v)[:100] for k, v in list(row_dict.items())[:5]}
                            })
                except Exception as ex:
                    print(f"    [!] Query skipped for {table_id}: {ex}")
        except Exception as e:
            print(f"  [!] Dataset scanning error: {e}")

    # Write output
    os.makedirs(r"C:\OsintNeoAi\data", exist_ok=True)
    out_file = r"C:\OsintNeoAi\data\bigquery_law_id_audit_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(tagged_results, f, indent=2)

    print(f"\n[+] Auto-tagging complete! Saved to: {out_file}")
    print(f"[+] Total Records Tagged: {tagged_results['total_tagged_records']}")
    print(f"[+] Law ID Breakdown: {json.dumps(tagged_results['law_id_breakdown'], indent=2)}")

if __name__ == "__main__":
    auto_tag_bigquery_tables()
