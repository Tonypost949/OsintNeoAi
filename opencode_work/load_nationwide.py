import csv, json
from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

# Load nationwide scan results and format for bridge table
rows = []
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\nationwide_cross_state_map.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        name = row['borrower']
        state = row['state']
        # Skip already-loaded entities
        if name in ('STEWART INDUSTRIES LLC', 'TRIUMVIRATE LLC', 'A & D LLC', 'SMD INVESTMENTS LLC', 
                     'DRT INVESTMENTS LLC', 'JEK INVESTMENTS LLC', 'RAV LLC', 'L2T MEDIA LLC',
                     'PREMIERE ENTERTAINMENT SOLUTIONS', 'HD ENTERTAINMENT INC', 'PREMIERE ENTERTAINMENT LLC (AL)'):
            continue
        
        amt = float(row['amount']) if row['amount'] else 0
        forgiven = float(row['forgiven']) if row['forgiven'] else 0
        sale_val = float(row['sale_value']) if row['sale_value'] else 0
        
        # Parse date to ISO format
        sale_date_str = row.get('sale_date', '')
        iso_date = None
        if sale_date_str:
            parts = sale_date_str.split('/')
            if len(parts) == 3:
                iso_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        
        record = {
            'entity_name': name,
            'property_address': row['hb_address'],
            'property_city': 'HUNTINGTON BEACH',
            'property_apn': '',
            'property_mail_address': row['hb_mail'],
            'property_mail_city': row['hb_mail_city'],
            'last_seller': row['seller'],
            'property_acquisition_date': iso_date,
            'property_acquisition_value': sale_val,
            'ppp_loan_count': 1,
            'ppp_total_amount': amt,
            'ppp_total_forgiven': forgiven,
            'ppp_business_addresses': [f"{row['city']}, {state}"],
            'ppp_state_array': [state],
            'ppp_naics_codes': [row['naics']] if row['naics'] else [],
            'ppp_lenders': [row['lender']] if row['lender'] else [],
            'ppp_borrower_address': row['city'],
            'ppp_borrower_city': row['city'],
            'ppp_borrower_state': state,
            'is_multi_state_ppp': True,
            'is_naics_mismatch': True,
            'is_post_ppp_property_acquisition': True if (iso_date and row.get('date') and iso_date > row['date']) else False,
            'is_mailbox_address': '#' in (row['hb_mail'] or '') or 'STE' in (row['hb_mail'] or '').upper() or 'PO BOX' in (row['hb_mail'] or '').upper(),
            'is_zero_dollar_transfer': sale_val == 0,
        }
        rows.append(record)

table_id = "noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge"
errors = client.insert_rows_json(table_id, rows)
if errors:
    print(f"Errors: {errors}")
else:
    print(f"Inserted {len(rows)} new nationwide entities")

# Final counts
for row in client.query(f"SELECT ppp_borrower_state, COUNT(*) as cnt, SUM(ppp_total_amount) as total FROM {table_id} GROUP BY ppp_borrower_state ORDER BY total DESC").result():
    print(f"  {row.ppp_borrower_state}: {row.cnt} entities, ${row.total:,.0f}")

total = list(client.query(f"SELECT COUNT(*) as c, SUM(ppp_total_amount) as t FROM {table_id}").result())[0]
print(f"\nBridge table: {total.c} entities, ${total.t:,.0f} total cross-state PPP")
