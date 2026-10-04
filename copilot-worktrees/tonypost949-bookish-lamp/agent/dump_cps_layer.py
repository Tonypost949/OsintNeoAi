from google.cloud import bigquery
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

client = bigquery.Client(project='noble-beanbag-497411-m4')
rows = list(client.query('SELECT * FROM `noble-beanbag-497411-m4.forensic_layers.cps_trafficking_layer` ORDER BY layer, amount DESC').result())
print(f'TOTAL ROWS: {len(rows)}\n')

layers = {}
for r in rows:
    l = r.layer
    if l not in layers: layers[l] = []
    layers[l].append(dict(r))

for layer, items in layers.items():
    print(f'=== {layer} ===')
    for item in items:
        amt = f" {item['amount']:,.0f}" if item.get('amount') else ''
        kids = f" ({item['children_affected']} kids)" if item.get('children_affected') else ''
        status = item.get('status', '')
        print(f"  {item['entity']}: {item['role']}{amt}{kids} [{status}]")
    print()
