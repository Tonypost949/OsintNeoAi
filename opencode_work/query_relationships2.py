from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== PPP-to-Property relationships ===")
rows = client.query("""
    SELECT 
        r.relationship_type,
        e.entity_id, e.name, e.type, e.address, e.city, e.state, e.ein,
        p.property_id, p.owner_name, p.address as prop_address, p.apn, p.last_sale_value
    FROM `noble-beanbag-497411-m4.hb_church_osint.relationships` r
    LEFT JOIN `noble-beanbag-497411-m4.hb_church_osint.entities` e ON r.source_id = e.entity_id
    LEFT JOIN `noble-beanbag-497411-m4.hb_church_osint.properties` p ON r.target_id = p.property_id
    ORDER BY p.last_sale_value DESC
""").result()
for row in rows:
    print(f"{row.entity_id} -> {row.property_id}")
    print(f"  Entity: {row.name} ({row.type}) | {row.address}, {row.city} {row.state} | EIN: {row.ein}")
    print(f"  Property: {row.owner_name} | {row.prop_address} | APN {row.apn} | ${row.last_sale_value}")
    print()

print("\n=== Entity types ===")
rows = client.query("""
    SELECT type, COUNT(*) as cnt
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    GROUP BY type
    ORDER BY cnt DESC
""").result()
for row in rows:
    print(f"{row.type}: {row.cnt}")

print("\n=== Sample entities with EIN ===")
rows = client.query("""
    SELECT name, type, address, city, state, ein
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    WHERE ein IS NOT NULL AND ein != ''
    LIMIT 20
""").result()
for row in rows:
    print(f"{row.name} | {row.type} | {row.address}, {row.city} {row.state} | EIN: {row.ein}")
