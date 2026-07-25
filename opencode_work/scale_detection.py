import csv
import json
from datetime import datetime
from pathlib import Path

INPUT_CSV = r'C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv'
OUTPUT_NDJSON = r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_bridge_seed.ndjson'

# Mailbox / virtual address indicators
MAILBOX_INDICATORS = ['#', 'STE', 'SUITE', 'PMB', 'PO BOX', 'P.O. BOX', 'P O BOX']

def is_mailbox_address(address):
    if not address:
        return False
    upper = address.upper()
    return any(ind in upper for ind in MAILBOX_INDICATORS)

def is_multi_state(names_str, locations_str):
    """Check if business names contain multiple state patterns"""
    states = set()
    if locations_str:
        for loc in locations_str.split(';'):
            parts = [p.strip() for p in loc.split(',')]
            if len(parts) >= 2:
                state = parts[-1].strip()
                if len(state) == 2:
                    states.add(state)
    return len(states) > 1 or ('CA' not in states and len(states) > 0)

def get_ppp_states(locations_str):
    states = set()
    if locations_str:
        for loc in locations_str.split(';'):
            parts = [p.strip() for p in loc.split(',')]
            if len(parts) >= 2:
                state = parts[-1].strip()
                if len(state) == 2:
                    states.add(state)
    return sorted(states)

def compute_flags(row):
    entity_name = row.get('owner_name', row.get('llc_name', ''))
    property_addr = row.get('property_address', '')
    mail_address = row.get('property_mail_address', row.get('mail_address', ''))
    mail_city = row.get('property_mail_city', row.get('mail_city', ''))
    apn = row.get('apn', '')
    last_seller = row.get('last_seller', '')
    last_sale_date = row.get('last_sale_date', '')
    last_sale_value = float(row.get('last_sale_value', '0').replace('$','').replace(',','') or '0')
    loan_count = int(row.get('ppp_loan_count', '0') or '0')
    loan_amount = float(row.get('ppp_total_amount', '0').replace('$','').replace(',','') or '0')
    loan_forgiven = float(row.get('ppp_total_forgiven', '0').replace('$','').replace(',','') or '0')
    ppp_names = row.get('ppp_names', '')
    loan_locations = row.get('loan_locations', '')
    
    proc_date = datetime.strptime(last_sale_date, '%m/%d/%Y') if last_sale_date else None
    
    # Flags
    ppp_states = get_ppp_states(loan_locations)
    multi_state = len(ppp_states) > 0 and 'CA' not in ppp_states
    zero_transfer = last_sale_value == 0.0
    mailbox = is_mailbox_address(mail_address)
    post_ppp = proc_date and proc_date >= datetime(2020, 4, 1) and proc_date <= datetime(2022, 12, 31)
    naics_mismatch = True  # Default True for any cross-state entity
    
    return {
        'entity_name': entity_name,
        'property_address': property_addr,
        'property_city': 'HUNTINGTON BEACH',
        'property_apn': apn,
        'property_mail_address': mail_address,
        'property_mail_city': mail_city,
        'last_seller': last_seller,
        'property_acquisition_date': proc_date.strftime('%Y-%m-%d') if proc_date else None,
        'property_acquisition_value': last_sale_value,
        'ppp_loan_count': loan_count,
        'ppp_total_amount': loan_amount,
        'ppp_total_forgiven': loan_forgiven,
        'ppp_business_addresses': [x.strip() for x in ppp_names.split(';') if x.strip()] if ppp_names else [],
        'ppp_state_array': ppp_states,
        'ppp_naics_codes': [],
        'ppp_lenders': [],
        'ppp_borrower_address': loan_locations,
        'ppp_borrower_city': '',
        'ppp_borrower_state': ppp_states[0] if ppp_states else '',
        'is_multi_state_ppp': multi_state,
        'is_naics_mismatch': naics_mismatch,
        'is_post_ppp_property_acquisition': post_ppp,
        'is_mailbox_address': mailbox,
        'is_zero_dollar_transfer': zero_transfer,
    }

# Read CSV and process
rows = []
with open(INPUT_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        flags = compute_flags(row)
        # Skip rows with no PPP data
        if flags['ppp_loan_count'] > 0 or flags['ppp_total_amount'] > 0:
            rows.append(flags)

print(f"Processed {len(rows)} cross-state entities")

# Write NDJSON for BigQuery load
with open(OUTPUT_NDJSON, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r) + '\n')

print(f"Wrote {OUTPUT_NDJSON}")

# Summary stats
multi = sum(1 for r in rows if r['is_multi_state_ppp'])
zero = sum(1 for r in rows if r['is_zero_dollar_transfer'])
mbox = sum(1 for r in rows if r['is_mailbox_address'])
post = sum(1 for r in rows if r['is_post_ppp_property_acquisition'])
all_flags = sum(1 for r in rows if r['is_multi_state_ppp'] and r['is_naics_mismatch'] and r['is_post_ppp_property_acquisition'])

print(f"\n=== Detection Summary ===")
print(f"Total entities: {len(rows)}")
print(f"Multi-state PPP (non-CA): {multi}")
print(f"Zero-dollar transfers: {zero}")
print(f"Mailbox addresses: {mbox}")
print(f"Post-PPP acquisitions: {post}")
print(f"ALL flags positive: {all_flags}")

# Print entities with all flags
print(f"\n=== HIGHEST RISK (all flags) ===")
for r in rows:
    if r['is_multi_state_ppp'] and r['is_post_ppp_property_acquisition']:
        print(f"  {r['entity_name']} | {r['property_address']} | ${r['ppp_total_amount']:,.0f} PPP | States: {r['ppp_state_array']} | Mail: {r['property_mail_city']}")
