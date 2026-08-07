import csv

print('=== ALL ROCKER SOLENOID LOANS ===')
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    total = 0
    for row in reader:
        if 'ROCKER SOLENOID' in row.get('BorrowerName', '').upper():
            count += 1
            amt = float(row.get('CurrentApprovalAmount', 0))
            forg = float(row.get('ForgivenessAmount', 0))
            total += amt
            print(f'Loan #{count}: {row.get("LoanNumber")}')
            print(f'  Amount: ${amt:,.0f} -> Forgiven: ${forg:,.0f}')
            print(f'  Date: {row.get("DateApproved")}')
            print()
    print(f'Total loans: {count}')
    print(f'Total amount: ${total:,.0f}')

print('\n=== ALL PACIFIC CITY HOTEL LOANS ===')
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    total = 0
    for row in reader:
        if 'PACIFIC CITY HOTEL' in row.get('BorrowerName', '').upper():
            count += 1
            amt = float(row.get('CurrentApprovalAmount', 0))
            forg = float(row.get('ForgivenessAmount', 0))
            total += amt
            print(f'Loan #{count}: {row.get("LoanNumber")}')
            print(f'  Amount: ${amt:,.0f} -> Forgiven: ${forg:,.0f}')
            print(f'  Date: {row.get("DateApproved")}')
            print()
    print(f'Total loans: {count}')
    print(f'Total amount: ${total:,.0f}')
