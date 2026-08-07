import os
from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# List of target search terms
targets = [
    "360 CLINIC", "360 HEALTH PLAN", "VINCE TIEN",
    "2T MEDIA", "AARON NGO", "VIETVISION", "VIETV",
    "PREMIERE ENTERTAINMENT",
    "VIET AMERICA SOCIETY", "CHERIE LUONG", "RHONA SUOLO",
    "MD24", "SIP DC",
    "INDEPENDENT BROADCAST", "IBC TV", "IBC",
    "SAIGON TELEVISION", "SAIGON TV", "MICHAEL NGUYEN",
    "VIETNAMESE AMERICAN PHILHARMONICS",
    "ME VIET NAM", "HAO NHU LE",
    "PT GROUP", "PETER VO", "PETER T VO",
    "DTN TECH", "SERENA NGUYEN",
    "CLAYTON CHAU", "WANGSAPORN",
    "ABOUND FOOD", "LEARAKOS",
    "GARDEN GROVE COMMUNITY", "TAM NGUYEN",
    "WESTMINSTER CHAMBER", "SOPHAK OK"
]

print("--- Searching ppp_150k_plus for audit targets ---")
for target in targets:
    q = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, JobsReported, OriginatingLender, ForgivenessAmount
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerName) LIKE '%{target}%'
       OR UPPER(BorrowerAddress) LIKE '%{target}%'
    """
    try:
        rows = list(client.query(q).result())
        if rows:
            print(f"\n[TARGET: {target}] Found {len(rows)} matches in ppp_150k_plus:")
            for r in rows:
                print(f"- Borrower: {r.BorrowerName} | Address: {r.BorrowerAddress}, {r.BorrowerCity}, {r.BorrowerState}")
                print(f"  Loan: ${r.InitialApprovalAmount:,.2f} | Lender: {r.OriginatingLender} | Forgiven: ${r.ForgivenessAmount:,.2f} | Jobs: {r.JobsReported}")
    except Exception as e:
        print(f"Error querying {target} in ppp_150k_plus: {e}")

print("\n--- Searching ppp_up_to_150k for audit targets ---")
for target in targets:
    q = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, JobsReported, OriginatingLender, ForgivenessAmount
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
    WHERE UPPER(BorrowerName) LIKE '%{target}%'
       OR UPPER(BorrowerAddress) LIKE '%{target}%'
    """
    try:
        rows = list(client.query(q).result())
        if rows:
            print(f"\n[TARGET: {target}] Found {len(rows)} matches in ppp_up_to_150k:")
            for r in rows:
                print(f"- Borrower: {r.BorrowerName} | Address: {r.BorrowerAddress}, {r.BorrowerCity}, {r.BorrowerState}")
                print(f"  Loan: ${r.InitialApprovalAmount:,.2f} | Lender: {r.OriginatingLender} | Forgiven: ${r.ForgivenessAmount:,.2f} | Jobs: {r.JobsReported}")
    except Exception as e:
        print(f"Error querying {target} in ppp_up_to_150k: {e}")

print("\n--- Searching hb_llcs / ppp_property_bridge for matches ---")
for target in targets:
    q = f"""
    SELECT Owner1, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue
    FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
    WHERE UPPER(Owner1) LIKE '%{target}%'
       OR UPPER(SiteAddress) LIKE '%{target}%'
       OR UPPER(MailAddress) LIKE '%{target}%'
    """
    try:
        rows = list(client.query(q).result())
        if rows:
            print(f"\n[TARGET: {target}] Found {len(rows)} matches in hb_llcs:")
            for r in rows:
                print(f"- Owner: {r.Owner1} | Address: {r.SiteAddress} | Mail: {r.MailAddress}, {r.MailCity}")
                print(f"  Seller: {r.LastSeller} | Sale Value: ${r.LastSaleValue:,.2f}")
    except Exception as e:
        print(f"Error querying {target} in hb_llcs: {e}")
