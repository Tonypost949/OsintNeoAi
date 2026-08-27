"""
cross_reference_extracted_evidence.py — Cross-references newly extracted Google Photos evidence against BigQuery forensic datasets.
"""
import os
import json
from google.cloud import bigquery

PROJECT = "noble-beanbag-497411-m4"
client = bigquery.Client(project=PROJECT)

SEARCH_TERMS = [
    "DiMarcello",
    "Anthony DiMarcello",
    "Christopher Ryan",
    "Timothy Anderson",
    "80 Huntington",
    "Colonial Land",
    "Ellwood Watson",
    "20-5007",
    "99451018G32195",
    "Watermarke",
    "Via Lucca"
]

TABLES_TO_SEARCH = [
    ("forensic_layers", "entity_resolution"),
    ("forensic_layers", "fca_timeline"),
    ("forensic_layers", "hbnc_convergence_points"),
    ("hb_church_osint", "entities"),
    ("hb_church_osint", "properties"),
    ("hb_church_osint", "relationships"),
    ("national_audits", "evidence_chain_of_custody"),
    ("national_audits", "all_state_records"),
    ("national_audits", "google_photos_index"),
    ("ppp_rico", "rico_evidence_matrix"),
    ("ppp_rico", "unified_enterprise"),
    ("ppp_rico", "hb_llcs"),
    ("ppp_rico", "beach_blvd_cluster"),
]

def search_bigquery():
    print(f"=== Cross-referencing {len(SEARCH_TERMS)} entities across BigQuery datasets ===")
    matches = []

    for dataset_id, table_id in TABLES_TO_SEARCH:
        full_table = f"{PROJECT}.{dataset_id}.{table_id}"
        try:
            table = client.get_table(full_table)
            string_cols = [f.name for f in table.schema if f.field_type in ("STRING", "TEXT")]
            if not string_cols:
                continue

            for term in SEARCH_TERMS:
                where_clauses = [f"LOWER(`{col}`) LIKE LOWER('%{term}%')" for col in string_cols]
                sql = f"""
                SELECT * FROM `{full_table}`
                WHERE {" OR ".join(where_clauses)}
                LIMIT 10
                """
                
                query_job = client.query(sql)
                rows = list(query_job.result())
                if rows:
                    print(f"\n[!] MATCH FOUND in {full_table} for '{term}' ({len(rows)} records):")
                    for row in rows:
                        row_dict = dict(row.items())
                        print(f"    -> {row_dict}")
                        matches.append({
                            "dataset": dataset_id,
                            "table": table_id,
                            "term": term,
                            "data": {k: str(v) for k, v in row_dict.items()}
                        })
        except Exception as e:
            # Table might not exist or schema differs
            # print(f"[-] Error querying {full_table}: {e}")
            pass

    os.makedirs("data", exist_ok=True)
    with open("data/bigquery_evidence_crossref_matches.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2)

    print(f"\n[+] Cross-referencing complete. Total BigQuery matches: {len(matches)}")
    print(f"[+] Results saved to data/bigquery_evidence_crossref_matches.json")

if __name__ == "__main__":
    search_bigquery()
