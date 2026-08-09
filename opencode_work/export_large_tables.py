import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

large_tables = [
    ("national_audits", "drive_file_index", 359273),
    ("ppp_rico", "ppp_150k_plus", 968524),
    ("ppp_rico", "ppp_up_to_150k", 10499686),
]

for ds_id, table_id, num_rows in large_tables:
    csv_path = WORK_DIR / f"{ds_id}_{table_id}.csv"
    if csv_path.exists():
        print(f"SKIP (exists): {ds_id}_{table_id}.csv")
        continue

    table_ref = f"{PROJECT}.{ds_id}.{table_id}"
    print(f"Exporting {ds_id}.{table_id} ({num_rows} rows)...", flush=True)

    try:
        chunk_size = 200000
        first = True
        total = 0

        while total < num_rows:
            query = f"SELECT * FROM `{table_ref}` LIMIT {chunk_size} OFFSET {total}"
            df = client.query(query, project=PROJECT).to_dataframe()
            if df.empty:
                break
            df.to_csv(csv_path, mode='w' if first else 'a', header=first, index=False)
            first = False
            total += len(df)
            print(f"  {total}/{num_rows} rows written", flush=True)
            if len(df) < chunk_size:
                break

        print(f" DONE - {total} rows total")
    except Exception as e:
        print(f" ERROR: {e}")
        if csv_path.exists():
            os.remove(csv_path)

print("\nLarge table exports complete.")
