from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying ppp_150k_plus for DNA ---")
q1 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE BorrowerName LIKE '%DNA%' OR BorrowerName LIKE '%D.N.A.%'
"""
try:
    results1 = client.query(q1).result()
    for row in results1:
        print(dict(row))
except Exception as e:
    print(f"Error querying ppp_150k_plus: {e}")

print("\n--- Querying ppp_up_to_150k for DNA ---")
q2 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE BorrowerName LIKE '%DNA%' OR BorrowerName LIKE '%D.N.A.%'
"""
try:
    results2 = client.query(q2).result()
    for row in results2:
        print(dict(row))
except Exception as e:
    print(f"Error querying ppp_up_to_150k: {e}")
