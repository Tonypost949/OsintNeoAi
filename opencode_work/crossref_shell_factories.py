from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Cross-reference remaining shell factories with PPP
query = """
SELECT 
  llc.Owner1,
  llc.SiteAddress,
  llc.MailAddress,
  llc.MailCity,
  ppp.BorrowerName,
  ppp.CurrentApprovalAmount,
  ppp.ForgivenessAmount,
  ppp.ServicingLenderName,
  ppp.LoanNumber,
  (ppp.ForgivenessAmount - ppp.CurrentApprovalAmount) as over_forgiven
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` llc
JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus` ppp
  ON llc.Owner1 = ppp.BorrowerName
WHERE llc.SiteAddress IN ('23000 NEWPORT COAST DR', '829 HARBOR ISLAND DR')
ORDER BY llc.SiteAddress, ppp.CurrentApprovalAmount DESC
"""

results = client.query(query).result()
print('=== SHELL FACTORY PPP CONNECTIONS ===\n')

for row in results:
    print(f'{row.Owner1}')
    print(f'  Address: {row.SiteAddress}')
    print(f'  Mail: {row.MailAddress}, {row.MailCity}')
    print(f'  Lender: {row.ServicingLenderName}')
    print(f'  Loan: {row.LoanNumber}')
    print(f'  PPP: ${row.CurrentApprovalAmount:,.0f} -> Forgiven: ${row.ForgivenessAmount:,.0f}')
    print(f'  Over-forgiven: ${row.over_forgiven:,.0f}')
    print()
