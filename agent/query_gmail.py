from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# Query top senders
print("--- Top Senders ---")
query = "SELECT sender, COUNT(*) as c FROM `project-743aab84-f9a5-4ec7-954.national_audits.gmail_index` GROUP BY sender ORDER BY c DESC LIMIT 10"
for row in client.query(query).result():
    print(f"{row.sender}: {row.c}")

# Query scan timestamps
print("\n--- Scan Timestamps ---")
query = "SELECT scan_timestamp, COUNT(*) as c FROM `project-743aab84-f9a5-4ec7-954.national_audits.gmail_index` GROUP BY scan_timestamp"
for row in client.query(query).result():
    print(f"{row.scan_timestamp}: {row.c}")
