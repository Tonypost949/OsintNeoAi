import csv
from collections import defaultdict

# Load properties
props = {}
with open(r"C:\Users\HP\OneDrive\Documents\hb_church_osint_properties.csv", 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        props[row['owner_name'].strip().upper()] = row

# Load rico_matches
matches = []
with open(r"C:\Users\HP\OneDrive\Documents\ppp_rico_matches.csv", 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        matches.append(row)

# Join
out_path = r"C:\Users\HP\OneDrive\Documents\out_of_state_llc_ppp_network.csv"
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['owner_name', 'property_address', 'apn', 'last_sale_value', 'last_sale_date',
                  'property_mail_address', 'property_mail_city',
                  'ppp_loan_count', 'ppp_total_amount', 'ppp_total_forgiven', 'ppp_names', 'loan_locations', 'loan_statuses']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    for m in matches:
        name = m['llc_name'].strip().upper()
        if name in props:
            p = props[name]
            writer.writerow({
                'owner_name': p['owner_name'],
                'property_address': p['address'],
                'apn': p['apn'],
                'last_sale_value': p['last_sale_value'],
                'last_sale_date': p['last_sale_date'],
                'property_mail_address': p['mail_address'],
                'property_mail_city': p['mail_city'],
                'ppp_loan_count': m['ppp_loan_count'],
                'ppp_total_amount': m['ppp_total_amount'],
                'ppp_total_forgiven': m['ppp_total_forgiven'],
                'ppp_names': m['ppp_names'],
                'loan_locations': m['loan_locations'],
                'loan_statuses': m['loan_statuses'],
            })
            count += 1

print(f"Saved {out_path} with {count} rows")
