from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

# Search for names and Long Beach in address fields
for dataset_id in ['hb_church_osint', 'ppp_rico', 'national_audits', 'ai_sandbox', 'nppes_export']:
    try:
        tables = list(client.list_tables(dataset_id))
    except:
        continue
    for t in tables:
        table_ref = f'noble-beanbag-497411-m4.{dataset_id}.{t.table_id}'
        schema = client.get_table(table_ref).schema
        str_cols = [f.name for f in schema if f.field_type == 'STRING' and f.name.lower() not in ('source', 'assessment', 'description')]
        if not str_cols:
            continue
        
        # Search for Burns surname, Long Beach city, or 'Little' name
        for keyword in ['BURNS', 'LITTLE', 'LONG BEACH']:
            conditions = ' OR '.join([f"UPPER(CAST(`{c}` AS STRING)) LIKE '%{keyword}%'" for c in str_cols[:8]])
            try:
                q = f"SELECT * FROM `{table_ref}` WHERE {conditions} LIMIT 5"
                rows = client.query(q).result()
                count = 0
                for row in rows:
                    count += 1
                    d = {k: str(v)[:120] for k, v in dict(row).items() if v is not None}
                    print(f'[{dataset_id}.{t.table_id}] "{keyword}": {json.dumps(d)}')
                if count:
                    print()
            except Exception as e:
                pass

print('Done.')
