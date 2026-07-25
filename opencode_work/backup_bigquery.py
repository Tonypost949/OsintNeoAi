from google.cloud import bigquery
import json, csv, os
from datetime import datetime

client = bigquery.Client(project='noble-beanbag-497411-m4')
backup_dir = r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs(backup_dir, exist_ok=True)

tables = [
    ('forensic_layers', 'ppp_property_bridge'),
    ('forensic_layers', 'fca_timeline'),
    ('forensic_layers', 'rico_network_map'),
    ('forensic_layers', 'lender_fraud_pattern'),
    ('forensic_layers', 'geotracker_ust'),
]

print(f'Backing up to: {backup_dir}\n')

for dataset, table in tables:
    full = f'{dataset}.{table}'
    try:
        query = f'SELECT * FROM `{full}`'
        rows = client.query(query).result()
        
        # Save as JSON
        json_path = os.path.join(backup_dir, f'{dataset}_{table}.json')
        data = [dict(row) for row in rows]
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        size = os.path.getsize(json_path) / 1024 / 1024
        print(f'  BACKED UP: {full} -> {len(data)} rows ({size:.1f}MB)')
    except Exception as e:
        print(f'  ERROR: {full} - {e}')

# Summary
total_size = sum(os.path.getsize(os.path.join(backup_dir, f)) for f in os.listdir(backup_dir)) / 1024 / 1024
print(f'\nBackup complete: {len(os.listdir(backup_dir))} files, {total_size:.1f}MB total')
print(f'Location: {backup_dir}')
