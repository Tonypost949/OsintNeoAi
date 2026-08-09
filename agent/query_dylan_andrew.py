from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying ppp_loans for Westminster addresses ---")
q1 = f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE BorrowerAddress LIKE '%15822%' OR BorrowerAddress LIKE '%GARNET%'
"""
try:
    rows = list(client.query(q1).result())
    for r in rows:
        print(f"[150k+] Borrower: {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_150k_plus: {e}")

q2 = f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE BorrowerAddress LIKE '%15822%' OR BorrowerAddress LIKE '%GARNET%'
"""
try:
    rows = list(client.query(q2).result())
    for r in rows:
        print(f"[Up to 150k] Borrower: {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
except Exception as e:
    print(f"Error querying ppp_up_to_150k: {e}")

print("\n--- Querying hb_llcs for DYLAN & ANDREW ---")
q3 = f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleValue
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE Owner1 LIKE '%DYLAN%' OR Owner1 LIKE '%ANDREW%'
"""
try:
    rows = list(client.query(q3).result())
    for r in rows:
        print(f"Owner1: {r.Owner1} | Owner2: {r.Owner2}")
        print(f"Site: {r.SiteAddress} | Mail: {r.MailAddress}")
        print(f"Seller: {r.LastSeller} | Value: ${r.LastSaleValue:,.2f}")
        print("-" * 30)
except Exception as e:
    print(f"Error querying hb_llcs: {e}")
