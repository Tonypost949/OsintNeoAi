from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

# Query top senders
print("--- Top Senders ---")
query = "SELECT sender, COUNT(*) as c FROM `noble-beanbag-497411-m4.national_audits.gmail_index` GROUP BY sender ORDER BY c DESC LIMIT 10"
for row in client.query(query).result():
    print(f"{row.sender}: {row.c}")

# Query scan timestamps
print("\n--- Scan Timestamps ---")
query = "SELECT scan_timestamp, COUNT(*) as c FROM `noble-beanbag-497411-m4.national_audits.gmail_index` GROUP BY scan_timestamp"
for row in client.query(query).result():
    print(f"{row.scan_timestamp}: {row.c}")
