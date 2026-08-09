import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

large_tables = [
    ("national_audits", "drive_file_index"),
    ("ppp_rico", "ppp_150k_plus"),
    ("ppp_rico", "ppp_up_to_150k"),
]

for ds_id, table_id in large_tables:
    csv_path = WORK_DIR / f"{ds_id}_{table_id}.csv"
    if csv_path.exists():
        print(f"SKIP: {ds_id}_{table_id}.csv")
        continue

    table_ref = client.dataset(ds_id).table(table_id)
    print(f"Exporting {ds_id}.{table_id} via list_rows...", flush=True)

    try:
        first = True
        total = 0
        page_size = 100000

        for page in client.list_rows(table_ref, page_size=page_size).pages:
            df = page.to_dataframe()
            df.to_csv(csv_path, mode='w' if first else 'a', header=first, index=False)
            first = False
            total += len(df)
            print(f"  {total} rows written", flush=True)

        print(f" DONE - {total} rows total")
    except Exception as e:
        print(f" ERROR: {e}")
        if csv_path.exists():
            os.remove(csv_path)

print("\nDone.")
