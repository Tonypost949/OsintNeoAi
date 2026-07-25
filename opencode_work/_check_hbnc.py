import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=== CHECK PROP_HBNC ===")
q1 = f"""
SELECT node_id, node_type, node_name
FROM `{PRJ}.forensic_layers.rico_network_map`
WHERE UPPER(node_id) LIKE '%HBNC%' OR UPPER(node_id) LIKE '%CAMERON%'
   OR UPPER(node_name) LIKE '%17631%' OR UPPER(node_name) LIKE '%HBNC%'
"""
rows = list(client.query(q1).result())
print(f"HBNC nodes: {len(rows)}")
for r in rows:
    print(f"  {r['node_id']} | {r['node_name']}")

print("\n=== CPS TIMELINE (fixed) ===")
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
print(f"CPS timeline events: {len(rows2)}")
for r in rows2:
    print(f"  {r['event_id']} | {r['event_date']} | {str(r['subject'])[:70]}")
