from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Cross-reference VUE INVESTOR OWNER LLC portfolio with PPP
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
  ppp.LoanNumber
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` llc
LEFT JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus` ppp
  ON llc.Owner1 = ppp.BorrowerName
WHERE llc.LastSeller = 'VUE INVESTOR OWNER LLC'
ORDER BY ppp.CurrentApprovalAmount DESC NULLS LAST
LIMIT 20
"""

results = client.query(query).result()
print('=== VUE INVESTOR OWNER LLC PORTFOLIO (56 properties) ===\n')

for row in results:
    print(f'{row.Owner1}')
    print(f'  Address: {row.SiteAddress}')
    print(f'  Mail: {row.MailAddress}, {row.MailCity}')
    if row.BorrowerName:
        print(f'  PPP Lender: {row.ServicingLenderName}')
        print(f'  Loan: {row.LoanNumber}')
        print(f'  PPP: ${row.CurrentApprovalAmount:,.0f} -> Forgiven: ${row.ForgivenessAmount:,.0f}')
    else:
        print(f'  No PPP connection')
    print()
