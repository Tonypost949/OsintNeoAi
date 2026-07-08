from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

print("=== CM CLEANING SOLUTIONS INC — FULL PPP PROFILE ===\n")
q = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       BorrowerZip, InitialApprovalAmount, LoanStatus, DateApproved,
       ServicingLenderName, OriginatingLender, NAICSCode,
       ForgivenessAmount, ForgivenessDate
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%CM CLEANING%'
   OR UPPER(BorrowerName) LIKE '%C M CLEANING%'
"""
df = c.query(q).to_dataframe()
print(df.to_string())

# Check 333 Washington Blvd Marina del Rey — ALL entities there
print("\n=== ALL entities at 333 Washington Blvd Marina del Rey ===")
q2 = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       InitialApprovalAmount, LoanStatus, DateApproved, ServicingLenderName, NAICSCode
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%333 WASHINGTON BLVD MARINA%'
   OR UPPER(BorrowerAddress) LIKE '%333 WASHINGTON BLVD, MARINA%'
   OR UPPER(BorrowerAddress) LIKE '%333 WASHINGTON BLVD 409%'
   OR (UPPER(BorrowerCity) = 'MARINA DEL REY' AND UPPER(BorrowerAddress) LIKE '%333%')
ORDER BY InitialApprovalAmount DESC
LIMIT 20
"""
df2 = c.query(q2).to_dataframe()
print(df2.to_string())

# Also search LLC records for any other entities at this address
print("\n=== LLCs at 333 Washington Blvd Marina del Rey ===")
q3 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(MailAddress) LIKE '%333 WASHINGTON%'
   OR UPPER(SiteAddress) LIKE '%333 WASHINGTON%'
ORDER BY LastSaleValue DESC
LIMIT 20
"""
df3 = c.query(q3).to_dataframe()
print(df3.to_string())

# Check OSINT for CM CLEANING or similar
print("\n=== OSINT: CM CLEANING SOLUTIONS ===")
q4 = """
SELECT name, address, city, state, ein, type
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%CM CLEANING%'
   OR UPPER(name) LIKE '%CLEANING SOLUTIONS%'
LIMIT 10
"""
df4 = c.query(q4).to_dataframe()
print(df4.to_string() if not df4.empty else "  Not found in OSINT")

# Also check if CM CLEANING appears in any other datasets
print("\n=== Cross-ref CM CLEANING across all BigQuery datasets ===")
q5 = """
SELECT table_name, column_name
FROM `noble-beanbag-497411-m4.ppp_rico.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name IN ('BorrowerName', 'name', 'entity_name')
LIMIT 50
"""
try:
    df5 = c.query(q5).to_dataframe()
    print(f"Available tables: {df5['table_name'].unique().tolist()[:20]}")
except:
    pass

print("\nDone.")
