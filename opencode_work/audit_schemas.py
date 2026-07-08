from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

tables = [
    'city_council_minutes', 'drive_file_index', 'drive_photos_exif', 
    'evidence_chain_of_custody', 'gmail_index', 'google_photos_index',
    'ingestion_audit_trail', 'mat_looker_forensic_base', 'all_state_records',
    'all_performance_reports'
]
for t in tables:
    print(f"\n=== national_audits.{t} ===")
    try:
        table = client.get_table(f'national_audits.{t}')
        print(f"Rows: {table.num_rows}, Size: {table.num_bytes}")
        for f in table.schema:
            print(f"  {f.name}: {f.field_type}")
    except Exception as e:
        print(f"Error: {e}")
