import csv
from collections import defaultdict

# Step 1: Load HB LLC owners and their property info
hb_owners = {}
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        name = (row.get('Owner1', '') or '').strip().upper()
        if name and name != 'NAN':
            if name not in hb_owners:
                hb_owners[name] = {
                    'address': row.get('SiteAddress', ''),
                    'mail': row.get('MailAddress', ''),
                    'mail_city': row.get('MailCity', ''),
                    'seller': row.get('LastSeller', ''),
                    'sale_date': row.get('LastSaleDate', ''),
                    'sale_value': row.get('LastSaleValue', ''),
                    'apn': row.get('APN', ''),
                }

print(f"Loaded {len(hb_owners)} HB LLC property owners")

# Step 2: Scan PPP 150k+ for matches where state != CA
matches = []
state_counts = defaultdict(int)
state_amounts = defaultdict(float)

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    total_rows = 0
    for row in reader:
        total_rows += 1
        name = (row.get('BorrowerName', '') or '').strip().upper()
        state = (row.get('BorrowerState', '') or '').strip().upper()
        
        if state == 'CA' or not name:
            continue
        
        if name in hb_owners:
            amt = float(row.get('CurrentApprovalAmount', '0') or '0')
            matches.append({
                'borrower': name,
                'state': state,
                'city': row.get('BorrowerCity', ''),
                'amount': amt,
                'forgiven': float(row.get('ForgivenessAmount', '0') or '0'),
                'naics': row.get('NAICSCode', ''),
                'date': row.get('DateApproved', ''),
                'lender': row.get('ServicingLenderName', ''),
                'jobs': row.get('JobsReported', ''),
                'hb_address': hb_owners[name]['address'],
                'hb_mail': hb_owners[name]['mail'],
                'hb_mail_city': hb_owners[name]['mail_city'],
                'seller': hb_owners[name]['seller'],
                'sale_date': hb_owners[name]['sale_date'],
                'sale_value': hb_owners[name]['sale_value'],
            })
            state_counts[state] += 1
            state_amounts[state] += amt

print(f"Scanned {total_rows} PPP 150k+ rows")
print(f"Found {len(matches)} cross-state matches")

# Step 3: Also scan PPP up_to_150k
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_ppp_up_to_150k.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    total_small = 0
    for row in reader:
        total_small += 1
        name = (row.get('BorrowerName', '') or '').strip().upper()
        state = (row.get('BorrowerState', '') or '').strip().upper()
        
        if state == 'CA' or not name:
            continue
        
        if name in hb_owners:
            amt = float(row.get('CurrentApprovalAmount', '0') or '0')
            matches.append({
                'borrower': name,
                'state': state,
                'city': row.get('BorrowerCity', ''),
                'amount': amt,
                'forgiven': float(row.get('ForgivenessAmount', '0') or '0'),
                'naics': row.get('NAICSCode', ''),
                'date': row.get('DateApproved', ''),
                'lender': row.get('ServicingLenderName', ''),
                'jobs': row.get('JobsReported', ''),
                'hb_address': hb_owners[name]['address'],
                'hb_mail': hb_owners[name]['mail'],
                'hb_mail_city': hb_owners[name]['mail_city'],
                'seller': hb_owners[name]['seller'],
                'sale_date': hb_owners[name]['sale_date'],
                'sale_value': hb_owners[name]['sale_value'],
            })
            state_counts[state] += 1
            state_amounts[state] += amt

print(f"Scanned {total_small} PPP up_to_150k rows")
print(f"Total cross-state matches: {len(matches)}")

# Step 4: Summary by state
print(f"\n=== NATIONWIDE CROSS-STATE PPP MAP ===")
print(f"{'State':<8} {'Entities':>8} {'Total PPP':>14}")
print("-" * 32)
for state in sorted(state_counts.keys(), key=lambda s: -state_amounts[s]):
    print(f"{state:<8} {state_counts[state]:>8} ${state_amounts[state]:>12,.0f}")

print(f"\n{'TOTAL':<8} {sum(state_counts.values()):>8} ${sum(state_amounts.values()):>12,.0f}")
print(f"States with hits: {len(state_counts)}")

# Step 5: Top entities
print(f"\n=== TOP 20 CROSS-STATE ENTITIES ===")
seen = set()
for m in sorted(matches, key=lambda x: -x['amount']):
    key = m['borrower'] + m['state']
    if key in seen: continue
    seen.add(key)
    print(f"{m['borrower'][:40]:<42} {m['state']:<4} ${m['amount']:>10,.0f}   {m['city'][:20]:<22} NAICS:{m['naics']:<8}  HB:{m['hb_address'][:30]}")
    if len(seen) >= 20: break

# Step 6: Save to CSV
out_path = r'C:\Users\HP\OneDrive\Documents\opencode_work\nationwide_cross_state_map.csv'
with open(out_path, 'w', encoding='utf-8', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=matches[0].keys() if matches else [])
    writer.writeheader()
    writer.writerows(matches)
print(f"\nSaved {len(matches)} records to {out_path}")
