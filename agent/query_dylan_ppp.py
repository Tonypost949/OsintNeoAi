from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying PPP tables for DYLAN or ANDREW HOLDINGS ---")

q_150k = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%DYLAN%' OR UPPER(BorrowerName) LIKE '%ANDREW HOLDINGS%'
"""
try:
    results1 = list(client.query(q_150k).result())
    print(f"[150k+] Found {len(results1)} matches:")
    for r in results1:
        print(f"- {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_150k_plus: {e}")

q_under150k = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerName) LIKE '%DYLAN%' OR UPPER(BorrowerName) LIKE '%ANDREW HOLDINGS%'
"""
try:
    results2 = list(client.query(q_under150k).result())
    print(f"[Up to 150k] Found {len(results2)} matches (displaying first 15):")
    for r in results2[:15]:
        print(f"- {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_up_to_150k: {e}")
