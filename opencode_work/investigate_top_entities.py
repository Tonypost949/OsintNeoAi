import csv

# Investigate Pacific City Hotel LLC and Rocker Solenoid Company
print('=== PACIFIC CITY HOTEL LLC ===')
print('PPP Amount: $1,995,000')
print('HB Address: 21080 Pacific Coast Hwy')
print()

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'PACIFIC CITY HOTEL' in row.get('BorrowerName', '').upper():
            print(f"Loan: {row.get('LoanNumber')}")
            print(f"Amount: ${row.get('CurrentApprovalAmount')}")
            print(f"Forgiven: ${row.get('ForgivenessAmount')}")
            print(f"Date: {row.get('DateApproved')}")
            print(f"City: {row.get('BorrowerCity')}")
            print(f"State: {row.get('BorrowerState')}")
            print(f"NAICS: {row.get('NAICSCode')}")
            print(f"Lender: {row.get('ServicingLenderName')}")
            print(f"Jobs: {row.get('JobsReported')}")
            print(f"Business Type: {row.get('BusinessType')}")
            print()
            break

print('=== ROCKER SOLENOID COMPANY ===')
print('PPP Amount: $1,984,195')
print('HB Address: 5492 Bolsa Ave')
print()

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'ROCKER SOLENOID' in row.get('BorrowerName', '').upper():
            print(f"Loan: {row.get('LoanNumber')}")
            print(f"Amount: ${row.get('CurrentApprovalAmount')}")
            print(f"Forgiven: ${row.get('ForgivenessAmount')}")
            print(f"Date: {row.get('DateApproved')}")
            print(f"City: {row.get('BorrowerCity')}")
            print(f"State: {row.get('BorrowerState')}")
            print(f"NAICS: {row.get('NAICSCode')}")
            print(f"Lender: {row.get('ServicingLenderName')}")
            print(f"Jobs: {row.get('JobsReported')}")
            print(f"Business Type: {row.get('BusinessType')}")
            print()
            break
