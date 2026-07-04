# ============================================================================
# PPP ↔ Property Timing Cross-Join
# Purpose: Flag entities where PPP loan disbursement occurred within 2 years
#          of HB-area property acquisition
# Save to: scratch\osint-agent\
# ============================================================================

from google.cloud import bigquery
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("=== PPP <-> PROPERTY TIMING CROSS-JOIN ===\n")

# Step 1: Get HB properties with sale dates
hb_query = """
SELECT 
    Owner1 AS llc_name,
    SiteAddress AS property_address,
    APN,
    LastSaleDate,
    CAST(LastSaleValue AS FLOAT64) AS sale_value,
    MailAddress,
    MailCity
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
WHERE LastSaleDate IS NOT NULL
  AND LastSaleDate != ''
  AND Owner1 LIKE '%LLC%'
"""

# Step 2: Normalize and match with PPP
print("Fetching HB properties...")
hb_rows = list(client.query(hb_query).result())
print(f"HB properties with sale dates: {len(hb_rows)}")

# Step 3: Get PPP borrowers (150k+ for significant loans)
ppp_query = """
SELECT 
    BorrowerName,
    BorrowerCity,
    BorrowerState,
    CurrentApprovalAmount,
    DateApproved,
    LoanStatus,
    ForgivenessAmount,
    JobsReported,
    NAICSCode,
    BusinessType,
    OriginatingLender,
    OriginatingLenderState,
    ProjectCity,
    ProjectState
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus`
WHERE CurrentApprovalAmount > 50000
"""
print("Fetching PPP data...")
ppp_rows = list(client.query(ppp_query).result())
print(f"PPP loans >50K: {len(ppp_rows)}")

# Step 4: Normalize and match
def normalize(s):
    import re
    return re.sub(r'[^A-Z0-9]', '', str(s).upper().strip())

ppp_index = {}
for p in ppp_rows:
    key = normalize(p.BorrowerName)
    if key not in ppp_index:
        ppp_index[key] = []
    ppp_index[key].append(p)

# Step 5: Cross-match and compute timing
from datetime import datetime
matches = []

for h in hb_rows:
    key = normalize(h.llc_name)
    if key in ppp_index:
        try:
            sale_date = datetime.strptime(h.LastSaleDate, '%m/%d/%Y')
        except:
            try:
                sale_date = datetime.strptime(h.LastSaleDate, '%Y-%m-%d')
            except:
                continue
        
        for p in ppp_index[key]:
            try:
                ppp_date = datetime.strptime(p.DateApproved, '%m/%d/%Y')
            except:
                try:
                    ppp_date = datetime.strptime(p.DateApproved, '%Y-%m-%d')
                except:
                    continue
            
            delta = abs((sale_date - ppp_date).days)
            if delta <= 730:  # 2 years
                matches.append({
                    'llc_name': h.llc_name,
                    'property': h.property_address,
                    'apn': h.APN,
                    'sale_date': h.LastSaleDate,
                    'sale_value': h.sale_value,
                    'mail': f"{h.MailAddress}, {h.MailCity}",
                    'ppp_name': p.BorrowerName,
                    'ppp_city': p.BorrowerCity,
                    'ppp_state': p.BorrowerState,
                    'ppp_amount': p.CurrentApprovalAmount,
                    'ppp_date': p.DateApproved,
                    'ppp_status': p.LoanStatus,
                    'forgiven': p.ForgivenessAmount,
                    'days_delta': delta,
                    'lender': p.OriginatingLender,
                    'lender_state': p.OriginatingLenderState,
                    'ppp_project': f"{p.ProjectCity}, {p.ProjectState}",
                    'naics': p.NAICSCode,
                    'jobs': p.JobsReported,
                    'business_type': p.BusinessType
                })

# Deduplicate and sort
seen = set()
unique_matches = []
for m in sorted(matches, key=lambda x: x['days_delta']):
    uid = (m['llc_name'], m['ppp_date'])
    if uid not in seen:
        seen.add(uid)
        unique_matches.append(m)

print(f"\n=== TIMING MATCHES (within 2 years): {len(unique_matches)} ===\n")

# Group by out-of-state vs in-state
out_of_state = [m for m in unique_matches if m['ppp_state'] != 'CA' and m['ppp_project'] != 'CA, CA']
in_state = [m for m in unique_matches if m not in out_of_state]

print(f"OUT-OF-STATE PPP → CA PROPERTY: {len(out_of_state)}")
for m in out_of_state:
    flag = "!!" if m['days_delta'] <= 180 else "--" if m['days_delta'] <= 365 else "  "
    print(f"  {flag} {m['llc_name']} | {m['ppp_name']} | {m['ppp_city']}, {m['ppp_state']} --> {m['property']}")
    print(f"     ${m['ppp_amount']:,.0f} PPP on {m['ppp_date']} | Property sale: {m['sale_date']} | delta: {m['days_delta']}d")
    print(f"     Lender: {m['lender']} ({m['lender_state']}) | Project: {m['ppp_project']} | Forgiven: ${m['forgiven']:,.0f}" if m['forgiven'] else f"     Lender: {m['lender']} ({m['lender_state']}) | Project: {m['ppp_project']}")
    print()

print(f"\nIN-STATE (CA PPP → CA PROPERTY): {len(in_state)}")

# Save results
out_path = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\ppp_property_timing_matches.json"
with open(out_path, 'w') as f:
    json.dump({'out_of_state': out_of_state, 'in_state': in_state, 'total': len(unique_matches)}, f, indent=2, default=str)
print(f"\nSaved to: {out_path}")

# Also save as CSV
import csv
csv_path = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\ppp_property_timing_matches.csv"
with open(csv_path, 'w', newline='') as f:
    if unique_matches:
        w = csv.DictWriter(f, fieldnames=unique_matches[0].keys())
        w.writeheader()
        w.writerows(unique_matches)
print(f"Saved to: {csv_path}")
