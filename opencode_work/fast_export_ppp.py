import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

csv_path = WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"
table_ref = client.dataset("ppp_rico").table("ppp_up_to_150k")

existing_rows = 0
if csv_path.exists():
    with open(csv_path, 'r') as f:
        existing_rows = sum(1 for _ in f) - 1

t = client.get_table(table_ref)
total_rows = t.num_rows
remaining = total_rows - existing_rows

print(f"Table: {total_rows} rows, {existing_rows} already saved, {remaining} to go")

if remaining <= 0:
    print("Already complete")
else:
    chunk_size = 500000
    offset = existing_rows
    first = False

    while offset < total_rows:
        print(f"Querying offset {offset}...", flush=True)
        query = f"SELECT * FROM `{PROJECT}.ppp_rico.ppp_up_to_150k` LIMIT {chunk_size} OFFSET {offset}"
        df = client.query(query, project=PROJECT).to_dataframe()
        if df.empty:
            break
        df.to_csv(csv_path, mode='a', header=first, index=False)
        first = False
        offset += len(df)
        print(f"  Wrote {offset}/{total_rows}", flush=True)

    print(f"\nDONE - {offset} rows written to {csv_path.name}")
