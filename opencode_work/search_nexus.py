from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

for dataset_id in ['national_audits', 'ai_sandbox', 'ppp_rico', 'hb_church_osint']:
    try:
        tables = list(client.list_tables(dataset_id))
    except:
        continue
    for t in tables:
        table_ref = f"noble-beanbag-497411-m4.{dataset_id}.{t.table_id}"
        schema = client.get_table(table_ref).schema
        str_cols = [c.name for c in schema if c.field_type == 'STRING']
        if not str_cols:
            continue
        for kw in ['TAM NGUYEN', '7561 CENTER', 'PETER PHAM', 'GARDEN GROVE COMMUNITY', 'CP PREMIER', 'DYLAN ANDREW', 'WEAVER', 'TIDWELL']:
            conds = ' OR '.join([f"UPPER(CAST(`{c}` AS STRING)) LIKE '%{kw}%'" for c in str_cols[:8]])
            try:
                q = f"SELECT * FROM `{table_ref}` WHERE {conds} LIMIT 5"
                rows = list(client.query(q).result())
                if rows:
                    print(f'[{dataset_id}.{t.table_id}] "{kw}": {len(rows)}')
                    for r in rows[:2]:
                        d = {k: str(v)[:120] for k, v in dict(r).items() if v}
                        print(f'  {json.dumps(d)}')
            except:
                pass
print('Done.')
