import os
from google.cloud import bigquery
import csv

project_id = 'noble-beanbag-497411-m4'
client = bigquery.Client(project=project_id)

datasets = [
    'forensic_layers',
    'forensic_views',
    'fraud_mart',
    'hb_church_osint',
    'national_audits',
    'nppes_export',
    'ppp_rico'
]

output_dir = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\noble_beanbag_evidence"
os.makedirs(output_dir, exist_ok=True)

for ds_id in datasets:
    print(f"Exporting dataset: {ds_id}")
    dataset_ref = f"{project_id}.{ds_id}"
    try:
        tables = list(client.list_tables(dataset_ref))
        if not tables:
            print(f" -> No tables found in {ds_id}")
            continue
            
        for table in tables:
            table_id = table.table_id
            print(f" -> Exporting table: {table_id}")
            # Limit to 15,000 rows to ensure it completes quickly and doesn't exhaust memory
            query = f"SELECT * FROM `{project_id}.{ds_id}.{table_id}` LIMIT 15000"
            
            try:
                query_job = client.query(query)
                results = query_job.result()
                
                csv_path = os.path.join(output_dir, f"{ds_id}_{table_id}.csv")
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    headers = [field.name for field in results.schema]
                    writer.writerow(headers)
                    
                    row_count = 0
                    for row in results:
                        writer.writerow(row.values())
                        row_count += 1
                        
                print(f"   [OK] Saved {row_count} rows to {ds_id}_{table_id}.csv")
            except Exception as e:
                print(f"   [ERROR] Failed to export {table_id}: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to access dataset {ds_id}: {e}")

print("\nAll evidence extraction complete. Files saved to:", output_dir)
