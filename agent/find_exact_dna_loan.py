from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying ppp_up_to_150k for loan amount 2452 ---")
q1 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, DateApproved, OriginatingLender
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE InitialApprovalAmount = 2452 OR CurrentApprovalAmount = 2452
"""
try:
    results1 = client.query(q1).result()
    for row in results1:
        print(dict(row))
except Exception as e:
    print(f"Error querying ppp_up_to_150k: {e}")
