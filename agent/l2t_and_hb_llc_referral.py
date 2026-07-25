from google.cloud import bigquery
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("=== L2T MEDIA LLC — FULL CROSS-REFERENCE ===\n")

# PPP data
for t in ['ppp_150k_plus', 'ppp_up_to_150k']:
    q = f"SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.{t} WHERE UPPER(BorrowerName) LIKE '%L2T%MEDIA%' ORDER BY DateApproved"
    rows = list(client.query(q).result())
    if rows:
        print(f"[{t}] {len(rows)} loan(s):")
        for r in rows:
            fg = f"${r.ForgivenessAmount:,.0f}" if r.ForgivenessAmount else "N/A"
            print(f"  ${r.CurrentApprovalAmount:,.0f} | {r.DateApproved} | {r.BorrowerCity}, {r.BorrowerState} | {r.LoanStatus} | Forgiven: {fg}")
            print(f"    Lender: {r.OriginatingLender} ({r.OriginatingLenderState}) | NAICS: {r.NAICSCode} | Jobs: {r.JobsReported} | Type: {r.BusinessType}")

# HB property
q = "SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs WHERE UPPER(Owner1) LIKE '%L2T%' OR UPPER(Owner1) LIKE '%MEDIA%'"
rows = list(client.query(q).result())
if rows:
    print(f"\nHB property matches: {len(rows)}")
    for r in rows:
        sv = f" | Sale: {r.LastSaleDate} ${r.LastSaleValue:,.0f}" if r.LastSaleValue else ""
        print(f"  {r.Owner1} | {r.SiteAddress} | Mail: {r.MailAddress}, {r.MailCity} | APN: {r.APN}{sv}")
else:
    print("\nNo HB property matches for L2T MEDIA")

# RICO matrix
for kw in ['L2T', 'MEDIA']:
    q = f"SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.rico_evidence_matrix WHERE UPPER(llc_name) LIKE '%{kw}%'"
    rows = list(client.query(q).result())
    if rows:
        print(f"\nRICO matrix '{kw}': {len(rows)} match(es)")
        for r in rows[:3]:
            d = {k: str(v)[:100] for k, v in dict(r).items() if v}
            print(f"  {json.dumps(d)}")

# Suspicious HB network
for kw in ['L2T', 'MEDIA']:
    try:
        q = f"SELECT * FROM project-743aab84-f9a5-4ec7-954.ppp_rico.suspicious_hb_network WHERE UPPER(owner_name) LIKE '%{kw}%' OR UPPER(ppp_borrower_name) LIKE '%{kw}%'"
        rows = list(client.query(q).result())
        if rows:
            print(f"\nSuspicious network '{kw}': {len(rows)}")
            for r in rows[:3]:
                print(f"  {r.owner_name} | {r.property_address} | PPP: {r.ppp_borrower_name} ${r.ppp_amount}")
    except:
        pass

print("\n=== HB LLC FEDERAL REFERRAL FLAG ===\n")
print("ENTITY: HB LLC (9472 Rambler Dr, Huntington Beach, CA)")
print("PATTERN: PPP loan stacking — 8 loans from 6 states using identical entity name")
print("TOTAL FORGIVEN: $566,911")
print()
print("Loan breakdown:")
loans_data = [
    ("$193,170", "04/15/2020", "Providence, RI", "Webster Bank (CT)"),
    ("$30,900", "01/30/2021", "Wichita, KS", "Community National Bank"),
    ("$146,130", "02/11/2021", "Long Beach, CA", "East West Bank"),
    ("$34,922", "03/03/2021", "Las Vegas, NV", "Bank of America (NC)"),
    ("$16,882", "03/26/2021", "Denver, CO", "Wells Fargo (SD)"),
    ("$105,100", "04/09/2020", "Long Beach, CA", "East West Bank"), 
    ("$34,923", "04/15/2020", "Las Vegas, NV", "Bank of America (NC)"),
    ("$8,206", "05/12/2021", "Fairfax, VA", "Leader Bank (MA)"),
]
for amt, dt, city, lender in loans_data:
    print(f"  {amt} | {dt} | {city} | {lender}")

print()
print("RED FLAGS:")
print("  - Same entity name (HB LLC) used across 6 states")
print("  - Two duplicate pairs (Long Beach CA x2, Las Vegas NV x2)")
print("  - Multiple lenders; no single-lender consolidation")
print("  - 100% forgiveness on 7 of 8 loans")
print("  - Property in HB, mail in Edmonds WA (out-of-state)")
print("  - In RICO evidence matrix")
print()
print("REFERRAL RECOMMENDATION: SBA OIG Hotline (sba.gov/oig/hotline)")
print("POTENTIAL VIOLATIONS: 15 USC 645 (PPP fraud), 18 USC 1343 (wire fraud), 18 USC 1014 (false statements to SBA)")
print("\nDone.")
