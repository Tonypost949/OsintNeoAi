import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=== CPS TIMELINE ===")
q = f"""
SELECT event_id, event_date, subject, entity_referenced
FROM `{PRJ}.forensic_layers.fca_timeline`
WHERE UPPER(event_id) LIKE '%CPS%' 
   OR UPPER(subject) LIKE '%CPS%'
   OR UPPER(subject) LIKE '%FOSTER%' 
   OR UPPER(subject) LIKE '%MERCY%HOUSE%'
   OR UPPER(subject) LIKE '%CHILD%WELFARE%'
   OR UPPER(subject) LIKE '%TRAFFICK%'
   OR UPPER(subject) LIKE '%DEPENDENCY%'
   OR UPPER(subject) LIKE '%ICWA%'
   OR EXISTS (SELECT 1 FROM UNNEST(entity_referenced) e WHERE UPPER(e) LIKE '%CPS%' OR UPPER(e) LIKE '%MERCY%')
ORDER BY event_date DESC
"""
rows = list(client.query(q).result())
print(f"CPS timeline events: {len(rows)}")
for r in rows:
    entities = ", ".join(r['entity_referenced'][:3]) if r['entity_referenced'] else ""
    print(f"  {r['event_id']} | {r['event_date']} | {str(r['subject'])[:60]} | {entities}")
