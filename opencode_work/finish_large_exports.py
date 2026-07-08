import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

partial_csv = WORK_DIR / "ppp_rico_ppp_150k_plus.csv"
full_csv = WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"

chunk_size = 200000

print("=== Finishing ppp_150k_plus (from offset 600000) ===")
table_ref = f"{PROJECT}.ppp_rico.ppp_150k_plus"
total_rows = client.get_table(table_ref).num_rows
offset = 600000

while offset < total_rows:
    query = f"SELECT * FROM `{table_ref}` LIMIT {chunk_size} OFFSET {offset}"
    df = client.query(query, project=PROJECT).to_dataframe()
    if df.empty:
        break
    df.to_csv(partial_csv, mode='a', header=False, index=False)
    offset += len(df)
    print(f"  {offset}/{total_rows}", flush=True)
print(f"DONE - {offset} rows total")

print("\n=== Exporting ppp_up_to_150k (10.5M rows) via list_rows ===")
table_ref_obj = client.dataset("ppp_rico").table("ppp_up_to_150k")
total_rows = client.get_table(table_ref_obj).num_rows
print(f"Total rows to export: {total_rows}", flush=True)

first = True
total = 0
page_size = 100000

for page in client.list_rows(table_ref_obj, page_size=page_size).pages:
    df = page.to_dataframe()
    if df.empty:
        break
    df.to_csv(full_csv, mode='w' if first else 'a', header=first, index=False)
    first = False
    total += len(df)
    print(f"  {total}/{total_rows}", flush=True)
    if total >= total_rows:
        break

print(f"\nDONE - {total} rows total")
