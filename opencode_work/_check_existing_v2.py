import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=== EXISTING CPS NODES ===")
q1 = f"""
SELECT node_id, node_type, node_name, layer, connected_to
FROM `{PRJ}.forensic_layers.rico_network_map`
WHERE UPPER(node_id) LIKE '%CPS%' OR UPPER(node_id) LIKE '%SSA%' 
   OR UPPER(node_id) LIKE '%MERCY%' OR UPPER(node_id) LIKE '%HBNC%'
   OR UPPER(node_id) LIKE '%IV_E%' OR UPPER(node_id) LIKE '%ICWA%'
   OR UPPER(node_id) LIKE '%CHILD%' OR UPPER(node_id) LIKE '%TRAFFICK%'
   OR UPPER(node_id) LIKE '%211%' OR UPPER(node_name) LIKE '%CPS%'
   OR UPPER(node_name) LIKE '%FOSTER%' OR UPPER(node_name) LIKE '%MERCY%HOUSE%'
ORDER BY node_id
"""
rows = list(client.query(q1).result())
print(f"Count: {len(rows)}")
for r in rows:
    print(f"  {r['node_id']} | {r['node_type']} | {r['node_name'][:50]}")

print("\n=== EXISTING CPS TIMELINE ===")
q2 = f"""
SELECT event_id, event_date, subject, entity_referenced
FROM `{PRJ}.forensic_layers.fca_timeline`
WHERE UPPER(event_id) LIKE '%CPS%' OR UPPER(subject) LIKE '%CPS%'
   OR UPPER(subject) LIKE '%FOSTER%' OR UPPER(subject) LIKE '%MERCY%HOUSE%'
   OR UPPER(subject) LIKE '%CHILD%' OR UPPER(subject) LIKE '%TRAFFICK%'
   OR UPPER(subject) LIKE '%DEPENDENCY%' OR UPPER(subject) LIKE '%ICWA%'
   OR UPPER(entity_referenced) LIKE '%CPS%' OR UPPER(entity_referenced) LIKE '%MERCY%'
ORDER BY event_date DESC
"""
rows2 = list(client.query(q2).result())
print(f"Count: {len(rows2)}")
for r in rows2:
    print(f"  {r['event_id']} | {r['event_date']} | {str(r['subject'])[:70]}")
