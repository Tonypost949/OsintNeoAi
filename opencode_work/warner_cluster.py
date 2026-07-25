from google.cloud import bigquery
import csv

client = bigquery.Client(project='noble-beanbag-497411-m4')
table_ref = 'noble-beanbag-497411-m4.ppp_rico.hb_llcs'

print("=== WARNER AVE ENTITY CLUSTER — 11770 WARNER AVE STE 215 ===\n")

q = f"""
SELECT Owner1, Owner2, MailAddress, SiteAddress, APN, LastSaleDate, LastSaleValue, LastSeller
FROM `{table_ref}`
WHERE UPPER(MailAddress) LIKE '%11770%WARNER%'
ORDER BY LastSaleDate
"""
rows = list(client.query(q).result())
print(f"Total entities: {len(rows)}\n")

owners_seen = set()
for i, row in enumerate(rows):
    print(f"  {i+1}. {row.Owner1}")
    print(f"     Site: {row.SiteAddress} | APN: {row.APN} | Sold: {row.LastSaleDate} | ${row.LastSaleValue:,.0f}" if row.LastSaleValue else f"     Site: {row.SiteAddress} | APN: {row.APN}")
    if row.Owner2 and row.Owner2.strip():
        print(f"     Owner2: {row.Owner2}")
    owners_seen.add(row.Owner1)

# Get unique owners
print(f"\nUnique entities at 11770 Warner: {len(owners_seen)}")
print(f"\nOwner list:")
for o in sorted(owners_seen):
    print(f"  {o}")

# Cross-reference: check these owners in PPP data
print("\n\n=== CROSS-REFERENCE: WARNER ENTITIES IN PPP DATA ===")
ppp_hits = 0
for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
    ppp_table = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
    for owner in list(owners_seen)[:20]:  # Check first 20
        name_parts = owner.split()[:2]
        name_search = '%' + '%'.join(name_parts) + '%'
        try:
            q = f"""
            SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, LoanStatus, ForgivenessAmount, DateApproved
            FROM `{ppp_table}`
            WHERE UPPER(BorrowerName) LIKE '{name_search}'
            LIMIT 3
            """
            rows2 = list(client.query(q).result())
            if rows2:
                ppp_hits += 1
                for r in rows2:
                    fg = f'${r.ForgivenessAmount:,.0f}' if r.ForgivenessAmount else 'N/A'
                    print(f"  [{table_name}] {owner} → {r.BorrowerName} | ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerCity}, {r.BorrowerState} | {r.LoanStatus} | Forgiven: {fg}")
        except:
            pass

print(f"\nPPP cross-reference hits: {ppp_hits}")

# Also check local CSV for Warner entities
print("\n\n=== LOCAL CSV: out_of_state_llc_ppp_network.csv ===")
csv_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv"
try:
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mail = str(row.get('property_mail_address', '')).upper()
            if '11770' in mail and 'WARNER' in mail:
                print(f"  {row.get('owner_name')} | Mail: {row.get('property_mail_city')} | PPP: ${row.get('ppp_amount')} | {row.get('ppp_borrower_name')}")
except:
    pass

print("\nDone.")
