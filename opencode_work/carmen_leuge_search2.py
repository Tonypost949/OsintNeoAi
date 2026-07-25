from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

print("=== Drive file index: Carmen/Leuge ===")
q4 = """
SELECT file_name, file_id, mime_type, size_bytes
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE UPPER(file_name) LIKE '%CARMEN%'
   OR UPPER(file_name) LIKE '%LEUGE%'
LIMIT 20
"""
df4 = c.query(q4).to_dataframe()
print(df4.to_string() if not df4.empty else "  None found")

print("\n=== All 'CARMEN HIGH SCHOOL' ===")
q5 = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       InitialApprovalAmount, LoanStatus, DateApproved, ServicingLenderName
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%CARMEN HIGH%'
LIMIT 10
"""
df5 = c.query(q5).to_dataframe()
print(df5.to_string() if not df5.empty else "  None found")
print("\nDone.")
