from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Check which zero-dollar transfer LLCs have PPP loans
query = """
SELECT 
  bridge.entity_name,
  bridge.property_address,
  bridge.last_seller,
  bridge.property_acquisition_date,
  ppp.BorrowerName,
  ppp.CurrentApprovalAmount,
  ppp.ForgivenessAmount,
  ppp.ServicingLenderName,
  ppp.LoanNumber,
  (ppp.ForgivenessAmount - ppp.CurrentApprovalAmount) as over_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge` bridge
LEFT JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus` ppp
  ON bridge.entity_name = ppp.BorrowerName
WHERE bridge.is_zero_dollar_transfer = TRUE
  AND ppp.BorrowerName IS NOT NULL
ORDER BY ppp.CurrentApprovalAmount DESC
"""

results = client.query(query).result()
print('=== ZERO-DOLLAR TRANSFER LLCs WITH PPP LOANS ===\n')

count = 0
for row in results:
    count += 1
    print(f'{row.entity_name}')
    print(f'  Address: {row.property_address}')
    print(f'  Seller: {row.last_seller}')
    print(f'  Acquired: {row.property_acquisition_date}')
    print(f'  Lender: {row.ServicingLenderName}')
    print(f'  Loan: {row.LoanNumber}')
    if row.CurrentApprovalAmount and row.ForgivenessAmount:
        print(f'  PPP: ${row.CurrentApprovalAmount:,.0f} -> Forgiven: ${row.ForgivenessAmount:,.0f}')
        if row.over_forgiven > 0:
            print(f'  Over-forgiven: ${row.over_forgiven:,.0f}')
    print()

print(f'Total zero-dollar LLCs with PPP: {count}')
