from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

tables = [
    "national_audits.deepseek_conversations",
    "national_audits.local_scan_emails",
    "national_audits.takeout_documents",
    "onedrive_forensics.onedrive_documents"
]

for table_id in tables:
    print(f"\nSchema for {table_id}:")
    try:
        table = client.get_table(table_id)
        for field in table.schema:
            print(f"  {field.name}: {field.field_type}")
    except Exception as e:
        print(f"  Error: {e}")
