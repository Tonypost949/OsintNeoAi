import os
from pathlib import Path
from google.cloud import bigquery

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

table_rows = {}
for dataset in client.list_datasets():
    ds_id = dataset.dataset_id
    for table in client.list_tables(dataset.reference):
        table_id = table.table_id
        full_id = f"{ds_id}.{table_id}"
        try:
            t = client.get_table(table.reference)
            num_rows = t.num_rows
        except Exception as e:
            num_rows = "?"
        table_rows[full_id] = num_rows

# Check for local CSV backups
csv_files = {p.stem.lower(): p for p in WORK_DIR.glob("*.csv")}

print(f"{'BigQuery Table':<50} {'Rows':>12} {'Local CSV Backup':<50}")
print("-" * 120)
missing = []
backed_up = []
for full_id, rows in sorted(table_rows.items()):
    ds, table = full_id.split(".", 1)
    possible_names = [
        table.lower(),
        f"{ds}_{table}".lower(),
        f"bq_{table}".lower(),
    ]
    local_match = None
    for name in possible_names:
        if name in csv_files:
            local_match = csv_files[name]
            break

    if local_match:
        backed_up.append((full_id, rows, local_match))
        status = str(local_match.relative_to(WORK_DIR))
    else:
        missing.append((full_id, rows))
        status = "NOT FOUND"

    print(f"{full_id:<50} {str(rows):>12} {status:<50}")

print("\n" + "=" * 120)
print(f"BACKED UP: {len(backed_up)} / {len(table_rows)} tables")
print(f"MISSING:   {len(missing)} / {len(table_rows)} tables")

if missing:
    print("\nMissing local backups:")
    for full_id, rows in missing:
        print(f"  - {full_id} ({rows} rows)")
