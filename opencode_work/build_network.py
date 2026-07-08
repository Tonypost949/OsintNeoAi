from google.cloud import bigquery
import csv
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Build a comprehensive suspicious network CSV
print("Building comprehensive suspicious network...")
query = """
SELECT 
    p.owner_name,
    p.address as property_address,
    p.apn,
    p.last_sale_value,
    p.last_sale_date,
    p.mail_address as property_mail_address,
    p.mail_city as property_mail_city,
    e.name as matched_entity_name,
    e.type as matched_entity_type,
    e.address as entity_address,
    e.city as entity_city,
    e.state as entity_state,
    e.ein as entity_ein,
    ppp.BorrowerName as ppp_borrower_name,
    ppp.BorrowerCity as ppp_borrower_city,
    ppp.BorrowerState as ppp_borrower_state,
    ppp.CurrentApprovalAmount as ppp_amount,
    ppp.LoanNumber as ppp_loan_number,
    ppp.LoanStatus as ppp_loan_status,
    ppp.OriginatingLender as ppp_lender,
    ppp.OriginatingLenderCity as ppp_lender_city,
    ppp.OriginatingLenderState as ppp_lender_state,
    ppp.DateApproved as ppp_date_approved
FROM `noble-beanbag-497411-m4.hb_church_osint.properties` p
LEFT JOIN `noble-beanbag-497411-m4.hb_church_osint.entities` e 
    ON UPPER(TRIM(p.address)) = UPPER(TRIM(e.address))
LEFT JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k` ppp
    ON UPPER(TRIM(p.owner_name)) = UPPER(REGEXP_REPLACE(TRIM(ppp.BorrowerName), r'[^A-Z0-9 ]', ''))
WHERE p.mail_city NOT IN ('HUNTINGTON BEACH', 'FOUNTAIN VALLEY', 'COSTA MESA', 'NEWPORT BEACH', 'WESTMINSTER', 'GARDEN GROVE', 'ANAHEIM', 'ORANGE', 'IRVINE', 'BREA', 'YORBA LINDA', 'LONG BEACH', 'LOS ANGELES', 'SAN DIEGO', 'SAN FRANCISCO', 'SANTA ANA', 'TUSTIN', 'MISSION VIEJO', 'LAKE FOREST', 'LAGUNA BEACH', 'DANA POINT', 'SEAL BEACH', 'CYPRESS', 'BUENA PARK', 'FULLERTON', 'HUNTINGTN BCH', 'HUNTINGTONBCH')
    AND (e.entity_id IS NOT NULL OR ppp.LoanNumber IS NOT NULL)
ORDER BY p.last_sale_value DESC, ppp.CurrentApprovalAmount DESC
LIMIT 5000
"""
rows = client.query(query).result()
out_path = r"C:\Users\HP\OneDrive\Documents\suspicious_hb_network.csv"
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([f.name for f in rows.schema])
    for row in rows:
        writer.writerow(list(row))
print(f"Saved {out_path}")

# Count
count = sum(1 for _ in rows)
print(f"Rows exported: {count}")
