from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== PPP loan details for church-to-HB-property relationships ===")
query = """
SELECT 
    r.relationship_type,
    ppp.LoanNumber, ppp.BorrowerName, ppp.BorrowerAddress, ppp.BorrowerCity, ppp.BorrowerState, ppp.BorrowerZip,
    ppp.CurrentApprovalAmount, ppp.InitialApprovalAmount, ppp.ForgivenessAmount, ppp.LoanStatus,
    ppp.OriginatingLender, ppp.OriginatingLenderCity, ppp.OriginatingLenderState,
    ppp.ProjectCity, ppp.ProjectCountyName, ppp.ProjectState, ppp.NonProfit,
    ppp.BusinessType, ppp.NAICSCode, ppp.JobsReported,
    p.owner_name, p.address as prop_address, p.apn, p.last_sale_value, p.mail_address, p.mail_city
FROM `noble-beanbag-497411-m4.hb_church_osint.relationships` r
JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k` ppp ON CAST(ppp.LoanNumber AS STRING) = SUBSTR(r.source_id, 5)
LEFT JOIN `noble-beanbag-497411-m4.hb_church_osint.properties` p ON r.target_id = p.property_id
ORDER BY ppp.CurrentApprovalAmount DESC
"""
rows = client.query(query).result()
for row in rows:
    print(f"\nPPP Loan: {row.LoanNumber} | {row.BorrowerName}")
    print(f"  Borrower Address: {row.BorrowerAddress}, {row.BorrowerCity} {row.BorrowerState} {row.BorrowerZip}")
    print(f"  Loan: ${row.CurrentApprovalAmount} | Status: {row.LoanStatus} | Forgiven: ${row.ForgivenessAmount}")
    print(f"  Lender: {row.OriginatingLender}, {row.OriginatingLenderCity} {row.OriginatingLenderState}")
    print(f"  Project: {row.ProjectCity}, {row.ProjectCountyName} {row.ProjectState} | NonProfit: {row.NonProfit} | Type: {row.BusinessType} | NAICS: {row.NAICSCode} | Jobs: {row.JobsReported}")
    print(f"  HB Property: {row.owner_name} | {row.prop_address} | APN {row.apn} | ${row.last_sale_value}")
    print(f"  Property Mail: {row.mail_address}, {row.mail_city}")

print("\n=== Additional PPP loans to churches in ppp_rico with same addresses ===")
query2 = """
SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState, CurrentApprovalAmount, LoanNumber, LoanStatus
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerName) LIKE '%CHURCH%' OR UPPER(BorrowerName) LIKE '%CATHOLIC%' OR UPPER(BorrowerName) LIKE '%METHODIST%' OR UPPER(BorrowerName) LIKE '%EPISCOPAL%'
ORDER BY CurrentApprovalAmount DESC
LIMIT 20
"""
rows2 = client.query(query2).result()
for row in rows2:
    print(f"{row.BorrowerName} | {row.BorrowerAddress}, {row.BorrowerCity} {row.BorrowerState} | ${row.CurrentApprovalAmount} | {row.LoanStatus}")
