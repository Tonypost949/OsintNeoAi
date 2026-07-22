from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Search for The Brink Center / Navigation Center / 17672 Beach Blvd
print("=== Search properties for Navigation Center / 17672 Beach Blvd ===")
rows = client.query("""
    SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value, last_sale_date
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE UPPER(address) LIKE '%17672 BEACH%' OR UPPER(address) LIKE '%17772 BEACH%' OR UPPER(address) LIKE '%BRINK%'
    ORDER BY last_sale_value DESC
""").result()
for row in rows:
    print(f"{row.owner_name} | {row.address} | APN {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value} | {row.last_sale_date}")

print("\n=== Search entities for 17672 Beach Blvd / Brink / Navigation Center ===")
rows = client.query("""
    SELECT name, type, address, city, state, ein
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    WHERE REGEXP_CONTAINS(UPPER(CONCAT(name, ' ', address)), r'17672|17772|BRINK|NAVIGATION|NAV CENTER|THE BRINK')
    LIMIT 20
""").result()
for row in rows:
    print(f"{row.name} | {row.type} | {row.address}, {row.city} {row.state} | EIN: {row.ein}")

# Search nearby Beach Blvd medical properties
print("\n=== Properties on Beach Blvd with medical/healthcare/shelter names ===")
rows = client.query("""
    SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE UPPER(address) LIKE '%BEACH BLVD%'
      AND REGEXP_CONTAINS(UPPER(owner_name), r'HEALTH|MEDICAL|REHAB|RECOVERY|HOSPICE|CARE|SHELTER|CENTER|CLINIC|WELLNESS')
    ORDER BY last_sale_value DESC
    LIMIT 30
""").result()
for row in rows:
    print(f"{row.owner_name} | {row.address} | APN {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value}")
