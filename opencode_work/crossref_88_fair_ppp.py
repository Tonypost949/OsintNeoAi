import csv

# List of 88 Fair Dr LLCs
fair_dr_llcs = [
    'INCUPLACE LLC',
    'ADT SECURITY SERVICES LLC',
    'RM ART DESIGNS LLC',
    'CELLULAR SALES MANAGEMENT GROUP LLC',
    'TLG ADHESIVES LLC',
    'CREATIVE BABE MARKET LLC',
    'HSE HOLDINGS 6 LLC'
]

print('=== 88 FAIR DR LLCs - PPP CROSS-REFERENCE ===')
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        borrower = (row.get('BorrowerName', '') or '').upper()
        for llc in fair_dr_llcs:
            if llc in borrower:
                print(f'{llc}')
                print(f'   Loan: {row.get("LoanNumber")}')
                print(f'   Amount: ${float(row.get("CurrentApprovalAmount", 0)):,.0f}')
                print(f'   Forgiven: ${float(row.get("ForgivenessAmount", 0)):,.0f}')
                print(f'   Date: {row.get("DateApproved")}')
                print(f'   City: {row.get("BorrowerCity")}')
                print(f'   State: {row.get("BorrowerState")}')
                print(f'   NAICS: {row.get("NAICSCode")}')
                print(f'   Lender: {row.get("ServicingLenderName")}')
                print(f'   Jobs: {row.get("JobsReported")}')
                print()
