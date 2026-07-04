from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("--- Querying PPP tables for Orchard, Shirley, and Cerritos addresses ---")
addresses = ["ORCHARD", "SHIRLEY", "CERRITOS"]

for addr in addresses:
    print(f"\nAddress keyword: {addr}")
    q_150k = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerAddress) LIKE '%{addr}%'
    """
    try:
        r1 = list(client.query(q_150k).result())
        print(f"[150k+] Found {len(r1)} matches:")
        for r in r1[:10]:
            print(f"- {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
    except Exception as e:
        print(f"Error querying ppp_150k_plus for {addr}: {e}")

    q_under150k = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, InitialApprovalAmount, ForgivenessAmount
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    WHERE UPPER(BorrowerAddress) LIKE '%{addr}%'
    """
    try:
        r2 = list(client.query(q_under150k).result())
        print(f"[Up to 150k] Found {len(r2)} matches:")
        for r in r2[:10]:
            print(f"- {r.BorrowerName} | Address: {r.BorrowerAddress} | Loan: ${r.InitialApprovalAmount:,.2f}")
    except Exception as e:
        print(f"Error querying ppp_up_to_150k for {addr}: {e}")
