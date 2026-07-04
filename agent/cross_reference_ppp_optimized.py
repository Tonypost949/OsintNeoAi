import os
from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# Compile targets into a regex pattern
patterns = [
    "360 CLINIC", "360 HEALTH PLAN", "VINCE TIEN",
    "2T MEDIA", "AARON NGO", "VIETVISION", "VIETV",
    "PREMIERE ENTERTAINMENT",
    "VIET AMERICA SOCIETY", "CHERIE LUONG", "RHONA SUOLO",
    "MD24", "SIP DC",
    "INDEPENDENT BROADCAST", "IBC TV",
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

regex_pattern = "(?i)" + "|".join(patterns)

def safe_float(val):
    if val is None:
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

def safe_int(val):
    if val is None:
        return 0
    try:
        return int(val)
    except:
        return 0

# Query 1: ppp_150k_plus
print("\n--- Querying ppp_150k_plus ---")
q1 = f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, JobsReported, OriginatingLender, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE REGEXP_CONTAINS(BorrowerName, r'{regex_pattern}')
   OR REGEXP_CONTAINS(BorrowerAddress, r'{regex_pattern}')
"""
try:
    results1 = list(client.query(q1).result())
    print(f"Found {len(results1)} matches in ppp_150k_plus:")
    for r in results1:
        loan_amt = safe_float(r.InitialApprovalAmount)
        forg_amt = safe_float(r.ForgivenessAmount)
        jobs = safe_int(r.JobsReported)
        print(f"- Borrower: {r.BorrowerName} | Address: {r.BorrowerAddress}, {r.BorrowerCity}, {r.BorrowerState}")
        print(f"  Loan: ${loan_amt:,.2f} | Lender: {r.OriginatingLender} | Forgiven: ${forg_amt:,.2f} | Jobs: {jobs}")
        print("-" * 30)
except Exception as e:
    print(f"Error querying ppp_150k_plus: {e}")

# Query 2: ppp_up_to_150k
print("\n--- Querying ppp_up_to_150k ---")
q2 = f"""
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, InitialApprovalAmount, JobsReported, OriginatingLender, ForgivenessAmount
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_up_to_150k`
WHERE REGEXP_CONTAINS(BorrowerName, r'{regex_pattern}')
   OR REGEXP_CONTAINS(BorrowerAddress, r'{regex_pattern}')
"""
try:
    results2 = list(client.query(q2).result())
    print(f"Found {len(results2)} matches in ppp_up_to_150k:")
    for r in results2:
        loan_amt = safe_float(r.InitialApprovalAmount)
        forg_amt = safe_float(r.ForgivenessAmount)
        jobs = safe_int(r.JobsReported)
        print(f"- Borrower: {r.BorrowerName} | Address: {r.BorrowerAddress}, {r.BorrowerCity}, {r.BorrowerState}")
        print(f"  Loan: ${loan_amt:,.2f} | Lender: {r.OriginatingLender} | Forgiven: ${forg_amt:,.2f} | Jobs: {jobs}")
        print("-" * 30)
except Exception as e:
    print(f"Error querying ppp_up_to_150k: {e}")

# Query 3: hb_llcs
print("\n--- Querying hb_llcs ---")
q3 = f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE REGEXP_CONTAINS(Owner1, r'{regex_pattern}')
   OR REGEXP_CONTAINS(SiteAddress, r'{regex_pattern}')
   OR REGEXP_CONTAINS(MailAddress, r'{regex_pattern}')
"""
try:
    results3 = list(client.query(q3).result())
    print(f"Found {len(results3)} matches in hb_llcs:")
    for r in results3:
        sale_val = safe_float(r.LastSaleValue)
        print(f"- Owner: {r.Owner1} | Address: {r.SiteAddress} | Mail: {r.MailAddress}, {r.MailCity}")
        print(f"  Seller: {r.LastSeller} | Sale Value: ${sale_val:,.2f}")
        print("-" * 30)
except Exception as e:
    print(f"Error querying hb_llcs: {e}")
