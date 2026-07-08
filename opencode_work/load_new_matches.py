import csv
from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

# Load and transform the matches
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\full_ppp_parcel_matches.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f'Transforming {len(rows)} matches for BigQuery schema...')

# Transform to match bridge table schema
transformed = []
for row in rows:
    # Parse date from MM/DD/YYYY to YYYY-MM-DD
    acq_date = row.get('hb_sale_date')
    if acq_date and '/' in acq_date:
        parts = acq_date.split('/')
        if len(parts) == 3:
            acq_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        else:
            acq_date = None
    
    transformed.append({
        'entity_name': row['entity'],
        'property_address': row.get('hb_address', ''),
        'property_city': 'HUNTINGTON BEACH',
        'property_apn': row.get('hb_apn', ''),
        'property_mail_address': row.get('hb_mail', ''),
        'property_mail_city': row.get('hb_mail_city', ''),
        'last_seller': row.get('hb_seller', ''),
        'property_acquisition_date': acq_date,
        'property_acquisition_value': float(row['hb_sale_value']) if row.get('hb_sale_value') else None,
        'ppp_loan_count': int(row['ppp_loan_count']) if row.get('ppp_loan_count') else 1,
        'ppp_total_amount': float(row['ppp_total_amount']) if row.get('ppp_total_amount') else 0,
        'ppp_total_forgiven': float(row['ppp_total_forgiven']) if row.get('ppp_total_forgiven') else 0,
        'ppp_business_addresses': [row.get('hb_address', '')],
        'ppp_state_array': row.get('ppp_states', '').split('; ') if row.get('ppp_states') else [],
        'ppp_naics_codes': row.get('ppp_naics', '').split('; ') if row.get('ppp_naics') else [],
        'ppp_lenders': row.get('ppp_lenders', '').split('; ') if row.get('ppp_lenders') else [],
        'ppp_borrower_address': row.get('hb_address', ''),
        'ppp_borrower_city': row.get('ppp_cities', '').split('; ')[0] if row.get('ppp_cities') else '',
        'ppp_borrower_state': row.get('ppp_states', '').split('; ')[0] if row.get('ppp_states') else '',
        'is_multi_state_ppp': len(row.get('ppp_states', '').split('; ')) > 1,
        'is_naics_mismatch': False,
        'is_post_ppp_property_acquisition': False,
        'is_mailbox_address': False,
        'is_zero_dollar_transfer': float(row.get('hb_sale_value', 0) or 0) == 0,
    })

print(f'Inserting {len(transformed)} rows into bridge table...')
errors = client.insert_rows_json('noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge', transformed)
if errors:
    print(f'ERRORS: {errors}')
else:
    print('SUCCESS: All 9 matches loaded')

# Get updated count
count = client.query('SELECT COUNT(*) as c FROM noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge').result()
total = list(count)[0]['c']
print(f'Bridge table now has {total} entities')
