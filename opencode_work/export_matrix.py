from google.cloud import bigquery
import csv
client = bigquery.Client(project='noble-beanbag-497411-m4')

# List accessible datasets
print("Accessible datasets:")
for ds in client.list_datasets():
    print(f"  {ds.dataset_id}")
    try:
        for t in client.list_tables(ds.dataset_id):
            print(f"    {t.table_id} ({t.table_type})")
    except Exception as e:
        print(f"    [access denied: {e}]")

# Export rico_evidence_matrix
print("\nExporting rico_evidence_matrix...")
query = """
SELECT *
FROM `noble-beanbag-497411-m4.ppp_rico.rico_evidence_matrix`
ORDER BY ppp_total_amount DESC
"""
try:
    rows = client.query(query).result()
    out_path = r"C:\Users\HP\OneDrive\Documents\rico_evidence_matrix.csv"
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([f.name for f in rows.schema])
        for row in rows:
            writer.writerow(list(row))
    print(f"Saved to {out_path}")
except Exception as e:
    print(f"Export error: {e}")
