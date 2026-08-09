import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=== FINAL CPS NETWORK NODES ===")
q1 = f"""
SELECT node_id, node_type, node_name, layer, risk_level
FROM `{PRJ}.forensic_layers.rico_network_map`
WHERE layer = 'CPS_PIPELINE'
   OR UPPER(node_id) LIKE '%CPS%' OR UPPER(node_id) LIKE '%MERCY%'
   OR UPPER(node_id) LIKE '%ICWA%' OR UPPER(node_id) LIKE '%OCSSA%'
   OR UPPER(node_id) LIKE '%ENV%' OR UPPER(node_id) LIKE '%ORG_211%'
   OR UPPER(node_id) LIKE '%FUND_IV%' OR UPPER(node_id) LIKE '%CASE_ICWA%'
   OR UPPER(node_id) LIKE '%EVID_%'
ORDER BY node_id
"""
rows = list(client.query(q1).result())
print(f"Total CPS-related nodes: {len(rows)}")
for r in rows:
    print(f"  {r['node_id']:20s} | {r['node_type']:20s} | {r['risk_level']:10s} | {r['node_name'][:50]}")

print(f"\n=== FINAL CPS TIMELINE ===")
q2 = f"""
SELECT event_id, event_date, subject, signal_type
FROM `{PRJ}.forensic_layers.fca_timeline`
WHERE UPPER(event_id) LIKE 'CPS-%'
   OR UPPER(subject) LIKE '%CPS%' OR UPPER(subject) LIKE '%FOSTER%'
   OR UPPER(subject) LIKE '%MERCY%HOUSE%' OR UPPER(subject) LIKE '%CHILD%WELFARE%'
   OR UPPER(subject) LIKE '%ICWA%' OR UPPER(subject) LIKE '%IIM%'
   OR EXISTS (SELECT 1 FROM UNNEST(entity_referenced) e WHERE UPPER(e) LIKE '%MERCY%' OR UPPER(e) LIKE '%OC SSA%')
ORDER BY event_date DESC
"""
rows2 = list(client.query(q2).result())
print(f"Total CPS-related timeline events: {len(rows2)}")
for r in rows2:
    sig = ", ".join(r['signal_type'][:2]) if r['signal_type'] else ""
    print(f"  {r['event_id']:15s} | {str(r['event_date'])[:19]} | {sig:25s} | {str(r['subject'])[:55]}")
