from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying ppp_150k_plus for PETER PHAM or CYNTHIA CHAU ---")
q1 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%PETER PHAM%' OR UPPER(BorrowerName) LIKE '%CYNTHIA CHAU%'
"""
try:
    results1 = list(client.query(q1).result())
    for r in results1:
        print(f"[150k+] {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_150k_plus: {e}")

print("\n--- Querying ppp_up_to_150k for PETER PHAM or CYNTHIA CHAU ---")
q2 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerName) LIKE '%PETER PHAM%' OR UPPER(BorrowerName) LIKE '%CYNTHIA CHAU%'
"""
try:
    results2 = list(client.query(q2).result())
    for r in results2:
        print(f"[Up to 150k] {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_up_to_150k: {e}")

print("\n--- Querying hb_llcs for PETER PHAM or CYNTHIA CHAU ---")
q3 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%PETER PHAM%' OR UPPER(Owner1) LIKE '%CYNTHIA CHAU%'
   OR UPPER(Owner2) LIKE '%PETER PHAM%' OR UPPER(Owner2) LIKE '%CYNTHIA CHAU%'
"""
try:
    results3 = list(client.query(q3).result())
    for r in results3:
        print(f"Owner1: {r.Owner1} | Owner2: {r.Owner2}")
        print(f"Site: {r.SiteAddress} | Mail: {r.MailAddress}")
        print(f"Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f}")
        print("-" * 30)
except Exception as e:
    print(f"Error querying hb_llcs: {e}")
