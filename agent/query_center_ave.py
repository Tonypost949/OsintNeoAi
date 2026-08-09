from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying ppp_150k_plus for 7561 CENTER ---")
q1 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%7561%CENTER%'
"""
try:
    results1 = list(client.query(q1).result())
    for r in results1:
        print(f"[150k+] {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Querying ppp_up_to_150k for 7561 CENTER ---")
q2 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerAddress) LIKE '%7561%CENTER%'
"""
try:
    results2 = list(client.query(q2).result())
    for r in results2:
        print(f"[Up to 150k] {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Querying hb_llcs for 7561 CENTER ---")
q3 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue, APN
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE UPPER(SiteAddress) LIKE '%7561%CENTER%' OR UPPER(MailAddress) LIKE '%7561%CENTER%'
"""
try:
    results3 = list(client.query(q3).result())
    for r in results3:
        print(f"Owner1: {r.Owner1} | Owner2: {r.Owner2}")
        print(f"Site: {r.SiteAddress} | Mail: {r.MailAddress}")
        print(f"Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f} | APN: {r.APN}")
        print("-" * 30)
except Exception as e:
    print(f"Error: {e}")
