"""L2T MEDIA — full out-of-state analysis"""
from google.cloud import bigquery
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
client = bigquery.Client(project="noble-beanbag-497411-m4")

print("=== L2T MEDIA — PPP + OSINT + NPPES ===\n")

# L2T MEDIA PPP — full detail
q1 = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       BorrowerZip, InitialApprovalAmount, LoanStatus, DateApproved,
       ServicingLenderName, OriginatingLender, NAICSCode, JobsReported,
       ForgivenessAmount, ForgivenessDate
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%L2T%'
   OR UPPER(BorrowerName) LIKE '%L 2 T%'
"""
df1 = client.query(q1).to_dataframe()
print("L2T MEDIA PPP loans:")
print(df1.to_string())

# L2T MEDIA — same address in OSINT entities
q2 = """
SELECT name, address, city, state, ein, type
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(address) IN (
    SELECT DISTINCT BorrowerAddress
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerName) LIKE '%L2T%'
)
   OR UPPER(name) LIKE '%L2T%'
   OR UPPER(name) LIKE '%L2T MEDIA%'
LIMIT 20
"""
df2 = client.query(q2).to_dataframe()
print("\nL2T MEDIA in OSINT:")
print(df2.to_string() if not df2.empty else "  Not found")

# L2T MEDIA address 1840 OAK AVE STE 315N EVANSTON — find other entities there
addr = "1840 OAK AVE"
q3 = f"""
SELECT 'PPP' as source, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%{addr}%'
UNION ALL
SELECT 'OSINT' as source, name, address, city, state
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(address) LIKE '%{addr}%'
LIMIT 20
"""
df3 = client.query(q3).to_dataframe()
print(f"\nOther entities at/near '{addr}':")
print(df3.to_string() if not df3.empty else "  Not found")

# STEWART INDUSTRIES — same approach
print("\n=== STEWART INDUSTRIES FULL PPP ===\n")
q4 = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       BorrowerZip, InitialApprovalAmount, LoanStatus, DateApproved,
       ServicingLenderName, OriginatingLender, NAICSCode,
       ForgivenessAmount, ForgivenessDate
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%STEWART INDUSTRIES%'
"""
df4 = client.query(q4).to_dataframe()
print(df4.to_string())

# Stewart Industries address: 150 McQuiston Dr — find others there
addr2 = "150 MCQUISTON"
q5 = f"""
SELECT 'PPP' as source, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%{addr2}%'
UNION ALL
SELECT 'OSINT' as source, name, address, city, state
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(address) LIKE '%{addr2}%'
LIMIT 20
"""
df5 = client.query(q5).to_dataframe()
print(f"\nOther entities at 150 McQuiston Dr:")
print(df5.to_string() if not df5.empty else "  Not found")

# TRIUMVIRATE LLC — same
print("\n=== TRIUMVIRATE LLC FULL PPP ===\n")
q6 = """
SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
       BorrowerZip, InitialApprovalAmount, LoanStatus, DateApproved,
       ServicingLenderName, OriginatingLender, NAICSCode,
       ForgivenessAmount, ForgivenessDate
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%TRIUMVIRATE%'
"""
df6 = client.query(q6).to_dataframe()
print(df6.to_string())

# TRIUMVIRATE Anchorage address: 3705 Arctic Blvd — find others
addr3 = "3705 ARCTIC"
q7 = f"""
SELECT 'PPP' as source, BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerAddress) LIKE '%{addr3}%'
UNION ALL
SELECT 'OSINT' as source, name, address, city, state
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(address) LIKE '%{addr3}%'
LIMIT 20
"""
df7 = client.query(q7).to_dataframe()
print(f"\nOther entities at 3705 Arctic Blvd:")
print(df7.to_string() if not df7.empty else "  Not found")

print("\nDone.")
