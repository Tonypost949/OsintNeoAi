from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"

new_tables = ["dehashed_hbpd_scan", "orange_county_structural_failure", "osint_neo_chat_transcript", "acrobat_adobe_urls"]

print("=========================================")
print("SCHEMAS FOR NEW PHASE 2 TABLES")
print("=========================================\n")

for tn in new_tables:
    table_ref = f"{dataset_id}.{tn}"
    table = client.get_table(table_ref)
    print(f"Table: {tn} ({table.num_rows} rows)")
    for field in table.schema:
        print(f"  - {field.name}: {field.field_type} ({field.mode})")
    print()

print("=========================================")
print("QUICK FORENSIC LINK: SEARCHING NUNEZ/BARNES")
print("=========================================\n")

# Let's search dehashed_hbpd_scan and orange_county_structural_failure for "Nunez" or "Barnes"
queries = {
    "Nunez in Dehashed HBPD": f"SELECT * FROM `{dataset_id}.dehashed_hbpd_scan` WHERE LOWER(contents_raw) LIKE '%nunez%'",
    "Barnes in Dehashed HBPD": f"SELECT * FROM `{dataset_id}.dehashed_hbpd_scan` WHERE LOWER(contents_raw) LIKE '%barnes%'",
    "Nunez in Structural Failure": f"SELECT * FROM `{dataset_id}.orange_county_structural_failure` WHERE LOWER(contents_raw) LIKE '%nunez%'",
    "Barnes in Structural Failure": f"SELECT * FROM `{dataset_id}.orange_county_structural_failure` WHERE LOWER(contents_raw) LIKE '%barnes%'",
    "Nunez in OSINT Neo Chat": f"SELECT * FROM `{dataset_id}.osint_neo_chat_transcript` WHERE LOWER(user_prompt) LIKE '%nunez%' OR LOWER(assistant_response) LIKE '%nunez%'",
    "Barnes in OSINT Neo Chat": f"SELECT * FROM `{dataset_id}.osint_neo_chat_transcript` WHERE LOWER(user_prompt) LIKE '%barnes%' OR LOWER(assistant_response) LIKE '%barnes%'"
}

for desc, q in queries.items():
    try:
        query_job = client.query(q)
        results = list(query_job.result())
        print(f"{desc}: Found {len(results)} matches.")
        if len(results) > 0:
            for idx, r in enumerate(results[:3]):
                print(f"  Match {idx+1}: {dict(r)}")
    except Exception as e:
        print(f"Error querying for {desc}: {e}")
    print()
