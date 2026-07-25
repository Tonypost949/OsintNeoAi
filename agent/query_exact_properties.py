from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying PPP tables for exact property matches ---")
exact_addresses = [
    "2614 ORCHARD",
    "13801 SHIRLEY",
    "7100 CERRITOS"
]

for addr in exact_addresses:
    print(f"\nSearching for exact address: {addr}")
    q_150k = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerAddress) LIKE '%{addr}%'
    """
    try:
        r1 = list(client.query(q_150k).result())
        print(f"[150k+] Found {len(r1)} matches:")
        for r in r1:
            print(f"- {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
    except Exception as e:
        print(f"Error querying ppp_150k_plus: {e}")

    q_under150k = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    WHERE UPPER(BorrowerAddress) LIKE '%{addr}%'
    """
    try:
        r2 = list(client.query(q_under150k).result())
        print(f"[Up to 150k] Found {len(r2)} matches:")
        for r in r2:
            print(f"- {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
    except Exception as e:
        print(f"Error querying ppp_up_to_150k: {e}")
