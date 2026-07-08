from google.cloud import bigquery
import csv
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Build a smaller network: out-of-state LLCs with PPP loans
print("Building out-of-state LLC PPP network...")
query = """
SELECT 
    p.owner_name,
    p.address as property_address,
    p.apn,
    p.last_sale_value,
    p.last_sale_date,
    p.mail_address as property_mail_address,
    p.mail_city as property_mail_city,
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
JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k` ppp
    ON UPPER(TRIM(p.owner_name)) = UPPER(REGEXP_REPLACE(TRIM(ppp.BorrowerName), r'[^A-Z0-9 ]', ''))
WHERE p.mail_city NOT IN ('HUNTINGTON BEACH', 'FOUNTAIN VALLEY', 'COSTA MESA', 'NEWPORT BEACH', 'WESTMINSTER', 'GARDEN GROVE', 'ANAHEIM', 'ORANGE', 'IRVINE', 'BREA', 'YORBA LINDA', 'LONG BEACH', 'LOS ANGELES', 'SAN DIEGO', 'SAN FRANCISCO', 'SANTA ANA', 'TUSTIN', 'MISSION VIEJO', 'LAKE FOREST', 'LAGUNA BEACH', 'DANA POINT', 'SEAL BEACH', 'CYPRESS', 'BUENA PARK', 'FULLERTON', 'HUNTINGTN BCH', 'HUNTINGTONBCH')
ORDER BY ppp.CurrentApprovalAmount DESC
LIMIT 5000
"""
rows = client.query(query).result()
out_path = r"C:\Users\HP\OneDrive\Documents\out_of_state_llc_ppp_network.csv"
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([f.name for f in rows.schema])
    count = 0
    for row in rows:
        writer.writerow(list(row))
        count += 1
print(f"Saved {out_path} with {count} rows")
