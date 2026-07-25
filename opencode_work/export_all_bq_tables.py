import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

datasets_tables = {}
for dataset in client.list_datasets():
    ds_id = dataset.dataset_id
    for table in client.list_tables(dataset.reference):
        datasets_tables.setdefault(ds_id, []).append(table.table_id)

for ds_id, tables in sorted(datasets_tables.items()):
    for table_id in tables:
        full_id = f"{ds_id}.{table_id}"
        table_ref = f"{PROJECT}.{ds_id}.{table_id}"
        csv_name = f"{ds_id}_{table_id}.csv"
        csv_path = WORK_DIR / csv_name

        if csv_path.exists():
            print(f"SKIP (exists): {csv_name}")
            continue

        print(f"Exporting: {full_id} ...", end="", flush=True)
        try:
            t = client.get_table(table_ref)
            num_rows = t.num_rows

            if num_rows == 0:
                pd.DataFrame().to_csv(csv_path, index=False)
                print(f" DONE (0 rows)")
                continue

            if num_rows <= 100000:
                df = client.query(f"SELECT * FROM `{table_ref}` LIMIT 100000").to_dataframe()
                df.to_csv(csv_path, index=False)
                print(f" DONE ({len(df)} rows)")
            else:
                chunk_size = 500000
                written = 0
                first = True
                for chunk in pd.read_gbq(f"SELECT * FROM `{table_ref}`", project_id=PROJECT, chunksize=chunk_size):
                    chunk.to_csv(csv_path, mode='w' if first else 'a', header=first, index=False)
                    first = False
                    written += len(chunk)
                    print(f" {written}/{num_rows}", end="", flush=True)
                print(f" DONE ({written} rows)")

        except Exception as e:
            print(f" ERROR: {e}")
            if csv_path.exists():
                os.remove(csv_path)

print("\nAll exports complete.")
