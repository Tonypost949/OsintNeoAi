from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

names = ['BURNS', 'LOGAN LITTLE', 'PAT BURNS', 'LITTLE', 'PATTI LONG']

for dataset_id in ['ppp_rico', 'hb_church_osint', 'national_audits', 'ai_sandbox', 'nppes_export']:
    try:
        tables = list(client.tables.list(dataset_id))
    except:
        continue
    for t in tables:
        table_ref = f'noble-beanbag-497411-m4.{dataset_id}.{t.table_id}'
        # Get schema to find string columns
        schema = client.get_table(table_ref).schema
        str_cols = [f.name for f in schema if f.field_type == 'STRING']
        if not str_cols:
            continue
        
        for name in names:
            conditions = ' OR '.join([f"UPPER(CAST(`{c}` AS STRING)) LIKE '%{name}%'" for c in str_cols[:10]])
            try:
                q = f"SELECT * FROM `{table_ref}` WHERE {conditions} LIMIT 10"
                rows = client.query(q).result()
                count = 0
                for row in rows:
                    count += 1
                    d = {k: str(v)[:100] for k, v in dict(row).items()}
                    print(f'[{dataset_id}.{t.table_id}] "{name}": {json.dumps(d)}')
                if count:
                    print()
            except Exception as e:
                err = str(e)
                if 'not found' in err.lower() or 'invalid' in err.lower():
                    pass
                elif 'no such' in err.lower():
                    pass
                else:
                    print(f'ERR [{dataset_id}.{t.table_id}] {name}: {err[:100]}')

print('\nDone.')
