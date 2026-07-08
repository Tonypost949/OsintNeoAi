import csv

# Check for lender patterns and other connections
print('=== LENDER ANALYSIS ===')
lenders = []

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports\ppp_rico_ppp_150k_plus.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        lender = row.get('ServicingLenderName', '')
        if 'Harvest Small Business Finance' in lender or 'Mega Bank' in lender:
            try:
                lenders.append({
                    'borrower': row.get('BorrowerName'),
                    'loan': row.get('LoanNumber'),
                    'amount': float(row.get('CurrentApprovalAmount') or 0),
                    'forgiven': float(row.get('ForgivenessAmount') or 0),
                    'lender': lender,
                    'city': row.get('BorrowerCity'),
                    'state': row.get('BorrowerState')
                })
            except (ValueError, TypeError):
                pass

print(f'Found {len(lenders)} loans from Harvest/Mega Bank')
print()

# Check for over-forgiveness pattern
over_forgiven = [l for l in lenders if l['forgiven'] > l['amount']]
print(f'Over-forgiven loans: {len(over_forgiven)}')
for loan in over_forgiven[:10]:
    diff = loan['forgiven'] - loan['amount']
    print(f'  {loan["borrower"]}: +${diff:,.0f}')
