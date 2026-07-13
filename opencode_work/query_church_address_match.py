from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Find churches whose addresses match HB properties
print("=== Churches with addresses matching HB LLC properties ===")
query = """
SELECT 
    e.name as church_name,
    e.address as church_address,
    e.city as church_city,
    e.state as church_state,
    p.owner_name,
    p.address as prop_address,
    p.apn,
    p.last_sale_value,
    p.mail_address,
    p.mail_city
FROM `noble-beanbag-497411-m4.hb_church_osint.entities` e
JOIN `noble-beanbag-497411-m4.hb_church_osint.properties` p
  ON UPPER(TRIM(e.address)) = UPPER(TRIM(p.address))
WHERE e.type IN ('church', 'nonprofit')
ORDER BY p.last_sale_value DESC
LIMIT 100
"""
rows = client.query(query).result()
count = 0
for row in rows:
    print(f"{row.church_name}")
    print(f"  Church addr: {row.church_address}, {row.church_city} {row.church_state}")
    print(f"  HB Property: {row.owner_name} | {row.prop_address} | APN {row.apn} | ${row.last_sale_value}")
    print(f"  Property mail: {row.mail_address}, {row.mail_city}")
    print()
    count += 1
print(f"Total matches: {count}")

# Find HB LLC owners that appear to be church-related or multichurch
print("\n=== HB Properties possibly linked to churches or multichurch networks ===")
query2 = """
SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value, COUNT(*) OVER (PARTITION BY owner_name) as owner_count
FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
WHERE REGEXP_CONTAINS(UPPER(owner_name), r'CHURCH|FELLOWSHIP|MINISTRY|GOSPEL|BAPTIST|METHODIST|EPISCOPAL|CATHOLIC|FAITH|CHRISTIAN|TEMPLE|SYNAGOGUE|ALLIANCE|COMMUNITY')
ORDER BY last_sale_value DESC
LIMIT 50
"""
rows2 = client.query(query2).result()
for row in rows2:
    print(f"{row.owner_name} | {row.address} | APN {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value} | owner_count={row.owner_count}")
