from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

q = """SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, CurrentApprovalAmount, OriginatingLender, DateApproved
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerAddress) LIKE '%12 OAKLAND AVE%' AND UPPER(BorrowerCity) = 'EVERETT'"""

print("=== LOANS AT 12 OAKLAND AVE, EVERETT ===")
for r in client.query(q).result():
    print(f"  {r.BorrowerName} | {r.BorrowerAddress} | ${r.CurrentApprovalAmount:,.2f} | Approved: {r.DateApproved} | Lender: {r.OriginatingLender}")
