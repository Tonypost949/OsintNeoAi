from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

query = """
SELECT DISTINCT
  bridge.entity_name,
  bridge.property_address,
  ppp.ServicingLenderName,
  ppp.LoanNumber,
  ppp.CurrentApprovalAmount,
  ppp.ForgivenessAmount,
  (ppp.ForgivenessAmount - ppp.CurrentApprovalAmount) as over_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge` bridge
JOIN `noble-beanbag-497411-m4.ppp_rico.rico_matches` match
  ON bridge.entity_name = match.llc_name
JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus` ppp
  ON match.llc_name = ppp.BorrowerName
WHERE ppp.ServicingLenderName LIKE '%Harvest Small Business Finance%'
   OR ppp.ServicingLenderName LIKE '%Mega Bank%'
ORDER BY over_forgiven DESC
"""

results = client.query(query).result()
print('=== HARVEST/MEGA BANK NETWORK ===\n')
for row in results:
    print(f'{row.entity_name}')
    print(f'  Address: {row.property_address}')
    print(f'  Lender: {row.ServicingLenderName}')
    print(f'  Loan: {row.LoanNumber}')
    print(f'  PPP: ${row.CurrentApprovalAmount:,.0f} -> Forgiven: ${row.ForgivenessAmount:,.0f}')
    print(f'  Over-forgiven: ${row.over_forgiven:,.0f}')
    print()
