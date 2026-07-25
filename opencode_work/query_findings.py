from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== ai_sandbox.findings ===")
rows = client.query("SELECT * FROM `noble-beanbag-497411-m4.ai_sandbox.findings`").result()
for row in rows:
    print(f"\nTitle: {row.title}")
    print(f"Description: {row.description}")
    print(f"Evidence: {row.evidence_links}")
    print(f"Timestamp: {row.timestamp}")

print("\n=== hb_church_osint.relationships ===")
rows = client.query("SELECT * FROM `noble-beanbag-497411-m4.hb_church_osint.relationships`").result()
for row in rows:
    print(f"{row.relationship_type}: {row.source_id} -> {row.target_id}")

print("\n=== Sample hb_church_osint.properties (mail_city NV or AZ) ===")
rows = client.query("""
    SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE mail_city IN ('LAS VEGAS', 'SCOTTSDALE', 'PHOENIX', 'RENO', 'HENDERSON')
    ORDER BY last_sale_value DESC
    LIMIT 30
""").result()
for row in rows:
    print(f"{row.owner_name} | {row.address} | {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value}")
