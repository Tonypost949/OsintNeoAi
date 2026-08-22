from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

print("--- Querying rico_matches ---")
q1 = "SELECT * FROM `noble-beanbag-497411-m4.ppp_rico.rico_matches` LIMIT 100"
try:
    results1 = client.query(q1).result()
    for row in results1:
        print(dict(row))
        print("-" * 50)
except Exception as e:
    print(f"Error querying rico_matches: {e}")

print("\n--- Querying rico_evidence_matrix ---")
q2 = "SELECT * FROM `noble-beanbag-497411-m4.ppp_rico.rico_evidence_matrix` LIMIT 100"
try:
    results2 = client.query(q2).result()
    for row in results2:
        print(dict(row))
        print("-" * 50)
except Exception as e:
    print(f"Error querying rico_evidence_matrix: {e}")
