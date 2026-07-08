from google.cloud import bigquery
import csv
client = bigquery.Client(project='noble-beanbag-497411-m4')

def export_table(dataset, table, out_path, limit=None):
    print(f"Exporting {dataset}.{table}...")
    query = f"SELECT * FROM `noble-beanbag-497411-m4.{dataset}.{table}`"
    if limit:
        query += f" LIMIT {limit}"
    rows = client.query(query).result()
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([f.name for f in rows.schema])
        for row in rows:
            writer.writerow(list(row))
    print(f"  Saved {out_path}")

export_table('hb_church_osint', 'properties', r"C:\Users\HP\OneDrive\Documents\hb_church_osint_properties.csv")
export_table('hb_church_osint', 'entities', r"C:\Users\HP\OneDrive\Documents\hb_church_osint_entities.csv")
export_table('hb_church_osint', 'relationships', r"C:\Users\HP\OneDrive\Documents\hb_church_osint_relationships.csv")
export_table('ppp_rico', 'rico_matches', r"C:\Users\HP\OneDrive\Documents\ppp_rico_matches.csv")
export_table('ppp_rico', 'ppp_150k_plus', r"C:\Users\HP\OneDrive\Documents\ppp_150k_plus_sample.csv", limit=1000)
export_table('national_audits', 'mat_looker_forensic_base', r"C:\Users\HP\OneDrive\Documents\mat_looker_forensic_base.csv")

print("\nAll exports complete.")
