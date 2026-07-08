from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

print("=== PPP: Carmen Leuge ===")
q1 = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       InitialApprovalAmount, LoanStatus, DateApproved, ServicingLenderName
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%CARMEN%'
   OR UPPER(BorrowerName) LIKE '%LEUGE%'
LIMIT 20
"""
df1 = c.query(q1).to_dataframe()
print(df1.to_string() if not df1.empty else "  None found")

print("\n=== LLC: Carmen Leuge ===")
q2 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%CARMEN%'
   OR UPPER(Owner2) LIKE '%CARMEN%'
   OR UPPER(Owner1) LIKE '%LEUGE%'
   OR UPPER(Owner2) LIKE '%LEUGE%'
LIMIT 20
"""
df2 = c.query(q2).to_dataframe()
print(df2.to_string() if not df2.empty else "  None found")

print("\n=== OSINT entities: Carmen Leuge ===")
q3 = """
SELECT name, address, city, state, ein, type
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%CARMEN%'
   OR UPPER(name) LIKE '%LEUGE%'
LIMIT 20
"""
df3 = c.query(q3).to_dataframe()
print(df3.to_string() if not df3.empty else "  None found")

print("\n=== Drive file index: Carmen/Leuge ===")
q4 = """
SELECT file_name, file_path, mime_type
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE UPPER(file_name) LIKE '%CARMEN%'
   OR UPPER(file_name) LIKE '%LEUGE%'
   OR UPPER(file_path) LIKE '%CARMEN%'
LIMIT 20
"""
df4 = c.query(q4).to_dataframe()
print(df4.to_string() if not df4.empty else "  None found")

print("\n=== All CARMEN/LEUGE anywhere in PPP addresses ===")
q5 = """
SELECT DISTINCT BorrowerName, BorrowerCity, BorrowerState, BorrowerAddress
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%LEUGE%'
   OR UPPER(BorrowerAddress) LIKE '%CARMEN%'
LIMIT 20
"""
df5 = c.query(q5).to_dataframe()
print(df5.to_string() if not df5.empty else "  None found")

print("\nDone.")
