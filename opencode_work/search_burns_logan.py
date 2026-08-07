from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

names = ['PAT BURNS', 'LOGAN LITTLE', 'LONG BEACH', 'PATTI LONG']

for dataset_id in ['ppp_rico', 'hb_church_osint', 'national_audits', 'ai_sandbox', 'nppes_export']:
    try:
        tables = list(client.list_tables(dataset_id))
    except:
        continue
    for t in tables:
        table_id = f'noble-beanbag-497411-m4.{dataset_id}.{t.table_id}'
        for name in names:
            try:
                q = f"SELECT * FROM `{table_id}` WHERE UPPER(TO_JSON_STRING(t)) LIKE '%{name}%' LIMIT 5"
                rows = client.query(q).result()
                count = 0
                for row in rows:
                    count += 1
                    d = dict(row)
                    print(f'[{dataset_id}.{t.table_id}] {name}: {json.dumps({k:str(v)[:80] for k,v in d.items()})}')
                if count:
                    print()
            except Exception as e:
                err = str(e)
                if 'not found' not in err.lower() and 'invalid' not in err.lower():
                    if 'column' in err.lower():
                        pass  # TO_JSON_STRING not available
                    elif 'no such' not in err.lower():
                        pass

print('Done.')
