from google.cloud import bigquery

bq = bigquery.Client(project="noble-beanbag-497411-m4")
P = "noble-beanbag-497411-m4"

print("=== VERIFYING BIGQUERY TABLE: ai_sandbox.reports_ingest ===")
q = f"SELECT report_name FROM `{P}.ai_sandbox.reports_ingest`"
try:
    results = list(bq.query(q).result())
    for r in results:
        print(f"  • {r.report_name}")
except Exception as e:
    print(f"Error: {e}")


