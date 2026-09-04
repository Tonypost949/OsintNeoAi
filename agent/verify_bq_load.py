from google.cloud import bigquery

bq = bigquery.Client(project="noble-beanbag-497411-m4")
P = "noble-beanbag-497411-m4"

print("=== VERIFYING BIGQUERY TABLE: ai_sandbox.reports_ingest ===")
q = f"SELECT report_name FROM `{P}.ai_sandbox.reports_ingest`"
try:
    df = bq.query(q).to_dataframe()
    print(df.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

