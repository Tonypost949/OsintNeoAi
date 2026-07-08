import csv
import re
from collections import defaultdict
import time

start = time.time()

# Load HB Parcels
print("Loading HB Parcels...")
parcels = {}
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\arcgis_exports\HB_Parcels.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        owner = (row.get('Huntington.dbo.W2_HB.OWNERNAME1', '') or '').strip().upper()
        if owner and owner != 'EMPTY':
            parcels[owner] = {
                'address': row.get('Huntington.dbo.W2_HB.SITEADDRESS', ''),
                'mail': row.get('Huntington.dbo.W2_HB.MAILADDRESS', ''),
                'mail_city': row.get('Huntington.dbo.W2_HB.MAILCITY', ''),
                'mail_state': row.get('Huntington.dbo.W2_HB.MAILSTATE', ''),
                'apn': row.get('Huntington.DBO.Parcels.APN', row.get('Huntington.dbo.W2_HB.APN', '')),
                'sale_value': row.get('Huntington.dbo.W2_HB.LASTSALEVALTRANSFER', ''),
                'seller': row.get('Huntington.dbo.W2_HB.LASTSALESELLERNAME', ''),
                'sale_date': row.get('Huntington.dbo.W2_HB.LASTSALEDATETRANSFER', ''),
                'tract': row.get('Huntington.dbo.W2_HB.TRACTNUMBER', ''),
                'doc_number': row.get('Huntington.dbo.W2_HB.LASTSALEDOCNUMBER', ''),
                'title_company': row.get('Huntington.dbo.W2_HB.TITLECOMPANYNAME', ''),
            }

print(f"  Loaded {len(parcels)} parcel owners")

# Load PPP 150k+
print("Loading PPP 150k+ dataset...")
ppp_borrowers = {}
total_ppp = 0
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = (row.get('BorrowerName', '') or '').strip().upper()
        if name:
            if name not in ppp_borrowers:
                ppp_borrowers[name] = []
            ppp_borrowers[name].append({
                'loan_number': row.get('LoanNumber', ''),
                'amount': float(row.get('CurrentApprovalAmount', '0') or '0'),
                'forgiven': float(row.get('ForgivenessAmount', '0') or '0'),
                'date': row.get('DateApproved', ''),
                'city': row.get('BorrowerCity', ''),
                'state': row.get('BorrowerState', ''),
                'naics': row.get('NAICSCode', ''),
                'lender': row.get('ServicingLenderName', ''),
                'jobs': row.get('JobsReported', ''),
                'business_type': row.get('BusinessType', ''),
            })
            total_ppp += float(row.get('CurrentApprovalAmount', '0') or '0')

print(f"  Loaded {len(ppp_borrowers)} unique PPP borrowers (${total_ppp/1e9:.1f}B total)")

# Phase 1: Exact name matches
print("\n=== PHASE 1: Exact Name Matches ===")
exact_matches = []
for name, loans in ppp_borrowers.items():
    if name in parcels:
        total_amount = sum(l['amount'] for l in loans)
        exact_matches.append({
            'entity': name,
            'hb_address': parcels[name]['address'],
            'hb_apn': parcels[name]['apn'],
            'hb_mail': parcels[name]['mail'],
            'hb_mail_city': parcels[name]['mail_city'],
            'hb_mail_state': parcels[name]['mail_state'],
            'hb_sale_value': parcels[name]['sale_value'],
            'hb_seller': parcels[name]['seller'],
            'hb_sale_date': parcels[name]['sale_date'],
            'ppp_loan_count': len(loans),
            'ppp_total_amount': total_amount,
            'ppp_total_forgiven': sum(l['forgiven'] for l in loans),
            'ppp_states': '; '.join(set(l['state'] for l in loans)),
            'ppp_cities': '; '.join(set(l['city'] for l in loans)),
            'ppp_naics': '; '.join(set(l['naics'] for l in loans)),
            'ppp_lenders': '; '.join(set(l['lender'] for l in loans)),
            'match_type': 'EXACT',
        })

print(f"  Found {len(exact_matches)} exact matches")

# Phase 2: LLC name variations (strip LLC/INC/LTD/etc)
print("\n=== PHASE 2: LLC Name Variations ===")
suffixes = [' LLC', ' INC', ' LTD', ' CORP', ' CORPORATION', ' COMPANY', ' CO', ' LP', ' LLLP', ' LLP', ' PC', ' PA', ' PL', ' PROFESSIONAL CORPORATION', ' PROFESSIONAL ASSOCIATION']

def normalize_name(name):
    n = name.upper().strip()
    for s in suffixes:
        n = n.replace(s, '')
    n = re.sub(r'\s+', ' ', n).strip()
    return n

ppp_normalized = {}
for name, loans in ppp_borrowers.items():
    norm = normalize_name(name)
    if norm:
        if norm not in ppp_normalized:
            ppp_normalized[norm] = []
        ppp_normalized[norm].extend(loans)

parcel_normalized = {}
for name, data in parcels.items():
    norm = normalize_name(name)
    if norm:
        parcel_normalized[norm] = data

llc_matches = []
for norm, loans in ppp_normalized.items():
    if norm in parcel_normalized:
        # Skip if already found as exact match
        if any(m['entity'] == norm for m in exact_matches):
            continue
        total_amount = sum(l['amount'] for l in loans)
        llc_matches.append({
            'entity': norm,
            'hb_address': parcel_normalized[norm]['address'],
            'hb_apn': parcel_normalized[norm]['apn'],
            'hb_mail': parcel_normalized[norm]['mail'],
            'hb_mail_city': parcel_normalized[norm]['mail_city'],
            'hb_mail_state': parcel_normalized[norm]['mail_state'],
            'hb_sale_value': parcel_normalized[norm]['sale_value'],
            'hb_seller': parcel_normalized[norm]['seller'],
            'hb_sale_date': parcel_normalized[norm]['sale_date'],
            'ppp_loan_count': len(loans),
            'ppp_total_amount': total_amount,
            'ppp_total_forgiven': sum(l['forgiven'] for l in loans),
            'ppp_states': '; '.join(set(l['state'] for l in loans)),
            'ppp_cities': '; '.join(set(l['city'] for l in loans)),
            'ppp_naics': '; '.join(set(l['naics'] for l in loans)),
            'ppp_lenders': '; '.join(set(l['lender'] for l in loans)),
            'match_type': 'LLC_VARIATION',
        })

print(f"  Found {len(llc_matches)} LLC variation matches")

# Combine all matches
all_matches = exact_matches + llc_matches

# Sort by PPP amount descending
all_matches.sort(key=lambda x: -x['ppp_total_amount'])

# Save to CSV
out_path = r'C:\Users\HP\OneDrive\Documents\opencode_work\full_ppp_parcel_matches.csv'
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    if all_matches:
        writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
        writer.writeheader()
        writer.writerows(all_matches)

# Summary stats
total_matched_ppp = sum(m['ppp_total_amount'] for m in all_matches)
total_matched_forgiven = sum(m['ppp_total_forgiven'] for m in all_matches)
states = set()
for m in all_matches:
    for s in m['ppp_states'].split('; '):
        if s:
            states.add(s)

print(f"\n{'='*60}")
print(f"FULL PPP-PARCEL CROSS-REFERENCE COMPLETE")
print(f"{'='*60}")
print(f"Exact matches:        {len(exact_matches)}")
print(f"LLC variation matches: {len(llc_matches)}")
print(f"{'='*60}")
print(f"TOTAL MATCHES:        {len(all_matches)}")
print(f"Total PPP matched:    ${total_matched_ppp:,.0f}")
print(f"Total forgiven:       ${total_matched_forgiven:,.0f}")
print(f"States represented:   {len(states)} ({', '.join(sorted(states))})")
print(f"Saved to: {out_path}")
print(f"Time: {time.time() - start:.1f}s")

# Top 20 by PPP amount
print(f"\n=== TOP 20 MATCHES BY PPP AMOUNT ===")
for i, m in enumerate(all_matches[:20], 1):
    print(f"{i:3}. {m['entity'][:40]:<42} ${m['ppp_total_amount']:>12,.0f}  {m['match_type']:<20} {m['hb_address'][:30]}")
