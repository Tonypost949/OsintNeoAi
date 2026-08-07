import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

q1 = f"""
SELECT node_id, node_type, label, description
FROM `{PRJ}.forensic_layers.rico_network_map`
WHERE UPPER(node_id) LIKE '%CPS%' OR UPPER(node_id) LIKE '%SSA%' 
   OR UPPER(node_id) LIKE '%MERCY%' OR UPPER(node_id) LIKE '%HBNC%'
   OR UPPER(node_id) LIKE '%IV_E%' OR UPPER(node_id) LIKE '%ICWA%'
   OR UPPER(node_id) LIKE '%CHILD%' OR UPPER(node_id) LIKE '%TRAFFICK%'
   OR UPPER(node_id) LIKE '%211%' OR UPPER(label) LIKE '%CPS%'
   OR UPPER(label) LIKE '%FOSTER%' OR UPPER(label) LIKE '%MERCY%HOUSE%'
ORDER BY node_id
"""
rows = list(client.query(q1).result())
print(f"Existing CPS-related nodes: {len(rows)}")
for r in rows:
    print(f"  {r['node_id']} | {r['node_type']} | {r['label']}")

print("\n--- TIMELINE ---")
q2 = f"""
SELECT event_id, event_date, event_type, description
FROM `{PRJ}.forensic_layers.fca_timeline`
WHERE UPPER(event_id) LIKE '%CPS%' OR UPPER(description) LIKE '%CPS%'
   OR UPPER(description) LIKE '%FOSTER%' OR UPPER(description) LIKE '%MERCY%HOUSE%'
   OR UPPER(description) LIKE '%CHILD%' OR UPPER(description) LIKE '%TRAFFICK%'
   OR UPPER(description) LIKE '%DEPENDENCY%' OR UPPER(description) LIKE '%ICWA%'
ORDER BY event_date DESC
"""
rows2 = list(client.query(q2).result())
print(f"Existing CPS timeline events: {len(rows2)}")
for r in rows2:
    print(f"  {r['event_id']} | {r['event_date']} | {str(r['description'])[:100]}")
