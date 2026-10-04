from google.cloud import bigquery
bq = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== ALL DATASETS & TABLES ===")
datasets = list(bq.list_datasets())
for ds in datasets:
    tables = list(bq.list_tables(ds.dataset_id))
    for t in tables:
        table = bq.get_table(t)
        print(f'{t.dataset_id}.{t.table_id}: {table.num_rows} rows, {table.num_bytes} bytes')

print("\n=== FINDINGS TABLE ===")
results = bq.query("SELECT * FROM `noble-beanbag-497411-m4.ai_sandbox.findings`").result()
for row in results:
    print(f"Title: {row.title}")
    print(f"Desc: {row.description[:400]}...")
    print(f"Evidence: {row.evidence_links}")
    print(f"Time: {row.timestamp}")
    print("---")

print("\n=== REPORTS INGEST ===")
results = bq.query("SELECT report_name, LENGTH(content) as chars FROM `noble-beanbag-497411-m4.ai_sandbox.reports_ingest`").result()
for row in results:
    print(f"  {row.report_name}: {row.chars} chars")

print("\n=== AG_STATUS_TRACKER ===")
results = bq.query("SELECT * FROM `noble-beanbag-497411-m4.ai_sandbox.ag_status_tracker` ORDER BY timestamp DESC").result()
for row in results:
    print(f"  {row.timestamp}: {row.event_type} - {row.description[:100]}")

print("\n=== PERMIT_OCR_RESULTS ===")
results = bq.query("SELECT filename, page_count, key_value_count, LEFT(extracted_text, 300) as preview FROM `noble-beanbag-497411-m4.ai_sandbox.permit_ocr_results`").result()
for row in results:
    print(f"  {row.filename}: {row.page_count}pp, {row.key_value_count} KVs")
    print(f"    {row.preview}...")
    print()