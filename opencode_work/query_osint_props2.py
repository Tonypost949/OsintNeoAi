from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Get all properties with out-of-state mail addresses using mail_city
print("=== Out-of-state LLC property summary (by mail city) ===")
rows = client.query("""
    SELECT mail_city, COUNT(*) as cnt, SUM(last_sale_value) as total_value
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE mail_city IS NOT NULL AND mail_city NOT IN ('HUNTINGTON BEACH', 'FOUNTAIN VALLEY', 'COSTA MESA', 'NEWPORT BEACH', 'WESTMINSTER', 'GARDEN GROVE', 'ANAHEIM', 'ORANGE', 'IRVINE', 'BREA', 'YORBA LINDA', 'LONG BEACH', 'LOS ANGELES', 'SAN DIEGO', 'SAN FRANCISCO', 'SANTA ANA', 'TUSTIN', 'MISSION VIEJO', 'LAKE FOREST', 'LAGUNA BEACH', 'DANA POINT', 'SEAL BEACH', 'CYPRESS', 'BUENA PARK', 'FULLERTON', 'HUNTINGTN BCH', 'HUNTINGTONBCH')
    GROUP BY mail_city
    ORDER BY cnt DESC
    LIMIT 30
""").result()
for row in rows:
    print(f"{row.mail_city}: {row.cnt} properties, ${row.total_value:,.0f}")

print("\n=== Properties with NV mailing addresses (full list) ===")
rows = client.query("""
    SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value, last_sale_date
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE mail_city IN ('LAS VEGAS', 'HENDERSON', 'RENO', 'NORTH LAS VEGAS')
    ORDER BY last_sale_value DESC
""").result()
for row in rows:
    print(f"{row.owner_name} | {row.address} | {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value} | {row.last_sale_date}")
