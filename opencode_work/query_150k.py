from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Check ppp_150k_plus for high-value and suspicious entities
print("=== ppp_150k_plus matches for our targets ===")
query = """
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, LoanNumber, LoanStatus, OriginatingLender, OriginatingLenderCity, OriginatingLenderState, DateApproved
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%PACE RECOVERY%' 
   OR UPPER(BorrowerName) LIKE '%STEWART INDUSTRIES%'
   OR UPPER(BorrowerName) LIKE '%TRIUMVIRATE%'
   OR UPPER(BorrowerName) LIKE '%LAZER LLC%'
   OR UPPER(BorrowerName) LIKE '%INCUPLACE%'
   OR UPPER(BorrowerName) LIKE '%NEWPORT LLC%'
   OR UPPER(BorrowerName) LIKE '%HB LLC%'
   OR UPPER(BorrowerName) LIKE '%DBS-ENTERPRISES%'
   OR UPPER(BorrowerName) LIKE '%RAV LLC%'
   OR UPPER(BorrowerName) LIKE '%DRT LLC%'
   OR UPPER(BorrowerName) LIKE '%BETTER FUTURE%'
   OR UPPER(BorrowerName) LIKE '%BWB SURF%'
   OR UPPER(BorrowerName) LIKE '%303 PARTNERS%'
   OR UPPER(BorrowerName) LIKE '%8TH STREET INVESTMENTS%'
   OR UPPER(BorrowerName) LIKE '%YAHWEH IS ABEL%'
   OR UPPER(BorrowerName) LIKE '%PRIME HEALTHCARE%'
   OR UPPER(BorrowerName) LIKE '%BEACH BLVD MEDICAL%'
   OR UPPER(BorrowerName) LIKE '%COMPASSIONATE CARE HOSPICE%'
ORDER BY CurrentApprovalAmount DESC
LIMIT 100
"""
rows = client.query(query).result()
for row in rows:
    print(f"{row.BorrowerName} | {row.BorrowerCity} {row.BorrowerState} | ${row.CurrentApprovalAmount} | {row.LoanStatus} | {row.OriginatingLender}, {row.OriginatingLenderCity} {row.OriginatingLenderState} | {row.DateApproved}")

print("\n=== Churches in ppp_150k_plus ===")
query2 = """
SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, LoanStatus, OriginatingLenderCity, OriginatingLenderState, DateApproved
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%CHURCH%' 
   OR UPPER(BorrowerName) LIKE '%CATHOLIC%'
   OR UPPER(BorrowerName) LIKE '%METHODIST%'
   OR UPPER(BorrowerName) LIKE '%EPISCOPAL%'
   OR UPPER(BorrowerName) LIKE '%BAPTIST%'
   OR UPPER(BorrowerName) LIKE '%PRESBYTERIAN%'
   OR UPPER(BorrowerName) LIKE '%LUTHERAN%'
ORDER BY CurrentApprovalAmount DESC
LIMIT 50
"""
rows2 = client.query(query2).result()
for row in rows2:
    print(f"{row.BorrowerName} | {row.BorrowerCity} {row.BorrowerState} | ${row.CurrentApprovalAmount} | {row.LoanStatus} | {row.OriginatingLenderCity} {row.OriginatingLenderState}")
