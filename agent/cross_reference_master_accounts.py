"""
cross_reference_master_accounts.py — Cross-references all 31 target accounts against BigQuery datasets.
"""
import os
import json
from google.cloud import bigquery

PROJECT = "noble-beanbag-497411-m4"
client = bigquery.Client(project=PROJECT)

with open("agent/target_accounts_master.json", "r") as f:
    target_data = json.load(f)

all_accounts = (
    target_data["primary_gmail_accounts"] +
    target_data["new_gmail_accounts"] +
    target_data["microsoft_onedrive_accounts"] +
    target_data["google_workspace_edu"] +
    target_data["firefox_browser_profiles"]
)

ACCOUNTS = sorted(list(set(all_accounts)))

TABLES_TO_SEARCH = [
    ("national_audits", "drive_file_index"),
    ("national_audits", "gmail_index"),
    ("onedrive_forensics", "onedrive_documents"),
    ("forensic_layers", "entity_resolution"),
    ("forensic_layers", "fca_timeline"),
    ("ppp_rico", "rico_evidence_matrix"),
    ("ppp_rico", "unified_enterprise"),
    ("ppp_rico", "hb_llcs")
]

def run_crossref():
    print(f"=== Cross-referencing {len(ACCOUNTS)} target accounts across BigQuery tables ===")
    matches = []

    for dataset_id, table_id in TABLES_TO_SEARCH:
        full_table = f"{PROJECT}.{dataset_id}.{table_id}"
        try:
            table = client.get_table(full_table)
            string_cols = [f.name for f in table.schema if f.field_type in ("STRING", "TEXT")]
            if not string_cols:
                continue

            for acc in ACCOUNTS:
                where_clauses = [f"LOWER(`{col}`) LIKE LOWER('%{acc}%')" for col in string_cols]
                sql = f"""
                SELECT * FROM `{full_table}`
                WHERE {" OR ".join(where_clauses)}
                LIMIT 5
                """
                rows = list(client.query(sql).result())
                if rows:
                    print(f"[MATCH] Found {len(rows)} rows for {acc} in {dataset_id}.{table_id}")
                    matches.append({
                        "account": acc,
                        "table": f"{dataset_id}.{table_id}",
                        "count": len(rows),
                        "sample": [dict(r) for r in rows]
                    })
        except Exception as e:
            print(f"[ERROR] Searching {dataset_id}.{table_id}: {e}")

    os.makedirs("data", exist_ok=True)
    with open("data/master_accounts_crossref_matches.json", "w") as f:
        json.dump(matches, f, indent=2, default=str)
    print(f"\n[+] Complete. Total matching tables: {len(matches)}")

if __name__ == "__main__":
    run_crossref()
