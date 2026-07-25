from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"

search_terms = ["kroll", "katana", "conway", "nunez", "mellody", "shelter", "eviction"]
tables_to_search = {
    "dehashed_hbpd_scan": ["contents_raw"],
    "orange_county_structural_failure": ["contents_raw"],
    "osint_neo_chat_transcript": ["user_prompt", "assistant_response"],
    "acrobat_adobe_urls": ["URL", "Title"]
}

print("=========================================")
print("CROSS-TABLE MULTI-TERM RICO MATCHES")
print("=========================================\n")

for term in search_terms:
    print(f"--- SEARCH TERM: '{term.upper()}' ---")
    for table, columns in tables_to_search.items():
        # Build dynamic OR condition across columns
        conds = [f"LOWER({col}) LIKE '%{term}%'" for col in columns]
        or_cond = " OR ".join(conds)
        q = f"SELECT * FROM `{dataset_id}.{table}` WHERE {or_cond} LIMIT 3"
        try:
            query_job = client.query(q)
            results = list(query_job.result())
            if len(results) > 0:
                print(f"  [{table}]: Found matches (total {len(results)} shown below):")
                for idx, r in enumerate(results):
                    # print some metadata
                    row_dict = dict(r)
                    # summarize contents_raw if present
                    if "contents_raw" in row_dict:
                        text_val = row_dict["contents_raw"][:250] + "..."
                    elif "assistant_response" in row_dict:
                        text_val = row_dict["assistant_response"][:250] + "..."
                    else:
                        text_val = str(row_dict)[:250] + "..."
                    
                    print(f"    Match {idx+1}: ID={row_dict.get('id', row_dict.get('sequence_id', 'N/A'))} | Text: {text_val}")
            else:
                pass
        except Exception as e:
            print(f"  [{table}]: Error: {e}")
    print()
