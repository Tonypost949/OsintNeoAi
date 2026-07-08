from google.cloud import bigquery
import pandas as pd
import os

PROJECT = "noble-beanbag-497411-m4"
client = bigquery.Client(project=PROJECT)

DATASETS = ["ppp_rico", "hb_church_osint", "national_audits", "nppes_export", "ai_sandbox"]
OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"

summary = []

for ds_name in DATASETS:
    print(f"\n{'='*60}")
    print(f"DATASET: {ds_name}")
    print(f"{'='*60}")
    dataset = client.dataset(ds_name, project=PROJECT)
    
    try:
        tables = list(client.list_tables(dataset))
        print(f"Tables found: {len(tables)}")
        
        for table in tables:
            table_ref = f"{PROJECT}.{ds_name}.{table.table_id}"
            print(f"\n--- {table_ref} ---")
            
            # Schema
            t = client.get_table(table_ref)
            print(f"Rows: {t.num_rows:,} | Size: {t.num_bytes/1024/1024:.2f} MB")
            print("Schema (first 20 cols):")
            for field in t.schema[:20]:
                print(f"  {field.name} ({field.field_type})")
            if len(t.schema) > 20:
                print(f"  ... and {len(t.schema)-20} more columns")
            
            # Sample rows
            q = f"SELECT * FROM `{table_ref}` LIMIT 3"
            try:
                df = client.query(q).to_dataframe()
                print(f"Sample ({len(df)} rows):")
                print(df.head(3).to_string(index=False, max_colwidth=60))
                
                # Save sample
                sample_path = os.path.join(OUTPUT_DIR, f"bq_sample_{ds_name}_{table.table_id}.csv")
                df.to_csv(sample_path, index=False)
                print(f"Saved sample to {sample_path}")
                
                summary.append({
                    "dataset": ds_name,
                    "table": table.table_id,
                    "rows": t.num_rows,
                    "size_mb": round(t.num_bytes/1024/1024, 2),
                    "columns": len(t.schema),
                    "sample_saved": sample_path
                })
            except Exception as e:
                print(f"Error sampling: {e}")
                summary.append({
                    "dataset": ds_name,
                    "table": table.table_id,
                    "rows": t.num_rows,
                    "size_mb": round(t.num_bytes/1024/1024, 2),
                    "columns": len(t.schema),
                    "sample_saved": f"ERROR: {e}"
                })
    except Exception as e:
        print(f"Error accessing dataset {ds_name}: {e}")

# Save summary
summary_df = pd.DataFrame(summary)
summary_path = os.path.join(OUTPUT_DIR, "bq_dataset_summary.csv")
summary_df.to_csv(summary_path, index=False)
print(f"\n\nSummary saved to {summary_path}")
print(summary_df.to_string(index=False))
