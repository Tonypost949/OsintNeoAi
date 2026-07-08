from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Search entities for Mercy House / Viet America Society / homeless shelter names
print("=== Search entities for Mercy House, Viet America Society, shelter names ===")
rows = client.query("""
    SELECT name, type, address, city, state, ein
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    WHERE REGEXP_CONTAINS(UPPER(name), r'MERCY|VIET AMERICA|SHELTER|HOMELESS|NAVIGATION|COLETTE|TRANSITION')
    ORDER BY name
    LIMIT 50
""").result()
for row in rows:
    print(f"{row.name} | {row.type} | {row.address}, {row.city} {row.state} | EIN: {row.ein}")

# Search properties for related owners
print("\n=== Search properties for Mercy House, Viet America, shelter-related owners ===")
rows = client.query("""
    SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value
    FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
    WHERE REGEXP_CONTAINS(UPPER(owner_name), r'MERCY|VIET AMERICA|SHELTER|HOMELESS|NAVIGATION|COLETTE|TRANSITION')
    ORDER BY last_sale_value DESC
""").result()
for row in rows:
    print(f"{row.owner_name} | {row.address} | {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value}")

# Search drive files
print("\n=== Search drive_file_index for Mercy House / Viet America / HB ===")
rows = client.query("""
    SELECT file_name, owner_emails, owner_names, web_view_link, created_time
    FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
    WHERE REGEXP_CONTAINS(UPPER(file_name), r'MERCY|VIET AMERICA|HUNTINGTON|NAVIGATION|SHELTER|HOMELESS|PPP|CHURCH')
    LIMIT 30
""").result()
for row in rows:
    print(f"{row.file_name} | {row.owner_names} | {row.created_time}")

# Search emails (avoid unicode errors by encoding)
print("\n=== Search gmail_index for Mercy House / Viet America / HB ===")
rows = client.query("""
    SELECT subject, sender, recipient, snippet, date_header
    FROM `noble-beanbag-497411-m4.national_audits.gmail_index`
    WHERE REGEXP_CONTAINS(UPPER(CONCAT(subject, ' ', snippet)), r'MERCY|VIET AMERICA|HUNTINGTON|NAVIGATION|SHELTER|HOMELESS')
    LIMIT 30
""").result()
for row in rows:
    try:
        print(f"{row.date_header} | {row.sender} -> {row.recipient}")
        print(f"  Subject: {row.subject}")
        print(f"  Snippet: {row.snippet}")
    except UnicodeEncodeError:
        print(f"  [unicode error - skipping]")
    print()
