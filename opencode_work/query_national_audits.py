from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Check national_audits for HB-related content
print("=== national_audits tables ===")
rows = client.query("""
    SELECT table_name
    FROM `noble-beanbag-497411-m4.national_audits.INFORMATION_SCHEMA.TABLES`
    ORDER BY table_name
""").result()
for row in rows:
    print(f"  {row.table_name}")

print("\n=== Sample city_council_minutes with HB keywords ===")
try:
    rows = client.query("""
        SELECT * EXCEPT(content)
        FROM `noble-beanbag-497411-m4.national_audits.city_council_minutes`
        WHERE REGEXP_CONTAINS(LOWER(content), r'huntington|surf city|delaware|main st|ppp')
        LIMIT 10
    """).result()
    for row in rows:
        print(row)
except Exception as e:
    print(f"Error: {e}")

print("\n=== Sample evidence_chain_of_custody ===")
try:
    rows = client.query("""
        SELECT *
        FROM `noble-beanbag-497411-m4.national_audits.evidence_chain_of_custody`
        LIMIT 5
    """).result()
    for row in rows:
        print(row)
except Exception as e:
    print(f"Error: {e}")

print("\n=== Sample drive_file_index ===")
try:
    rows = client.query("""
        SELECT * EXCEPT(content)
        FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
        LIMIT 5
    """).result()
    for row in rows:
        print(row)
except Exception as e:
    print(f"Error: {e}")
