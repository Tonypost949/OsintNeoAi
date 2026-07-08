from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Get all properties with out-of-state mail addresses
print("=== Out-of-state LLC property summary ===")
rows = client.query("""
    SELECT mail_city, mail_state, COUNT(*) as cnt, SUM(last_sale_value) as total_value
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE mail_state IS NOT NULL AND mail_state != 'CA'
    GROUP BY mail_city, mail_state
    ORDER BY cnt DESC
    LIMIT 30
""").result()
for row in rows:
    print(f"{row.mail_city}, {row.mail_state}: {row.cnt} properties, ${row.total_value:,.0f}")

print("\n=== Properties with NV mailing addresses (full list) ===")
rows = client.query("""
    SELECT owner_name, address, apn, mail_address, mail_city, mail_state, last_sale_value, last_sale_date
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE mail_state = 'NV'
    ORDER BY last_sale_value DESC
""").result()
for row in rows:
    print(f"{row.owner_name} | {row.address} | {row.apn} | {row.mail_address}, {row.mail_city} {row.mail_state} | ${row.last_sale_value} | {row.last_sale_date}")
