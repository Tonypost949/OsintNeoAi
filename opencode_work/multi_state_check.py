from google.cloud import bigquery
client = bigquery.Client(project="noble-beanbag-497411-m4")

# 1. Mercy House PPP by state
print("=== MERCY HOUSE PPP BY STATE ===")
q1 = """
SELECT BorrowerState, COUNT(*) as loans, SUM(InitialApprovalAmount) as total_amount
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%MERCY%' OR UPPER(BorrowerName) LIKE '%MERCY HOUSE%'
GROUP BY BorrowerState
ORDER BY total_amount DESC
"""
df1 = client.query(q1).to_dataframe()
print(df1.to_string())

# 2. CHDO-named borrowers by state
print("\n=== CHDO ENTITIES PPP BY STATE ===")
q2 = """
SELECT BorrowerState, BorrowerName, COUNT(*) as loans, SUM(InitialApprovalAmount) as total
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%CHDO%'
   OR UPPER(BorrowerName) LIKE '%COMMUNITY HOUSING%'
   OR UPPER(BorrowerName) LIKE '%HOUSING DEVELOPMENT ORGANIZATION%'
GROUP BY BorrowerState, BorrowerName
ORDER BY total DESC
LIMIT 30
"""
df2 = client.query(q2).to_dataframe()
print(df2.to_string())

# 3. Mercy in OSINT by state
print("\n=== MERCY / CHDO IN OSINT BY STATE ===")
q3 = """
SELECT state, COUNT(*) as count
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%MERCY%'
   OR UPPER(name) LIKE '%CHDO%'
   OR UPPER(name) LIKE '%HOUSING%'
   OR UPPER(name) LIKE '%VAGABOND%'
GROUP BY state
ORDER BY count DESC
"""
df3 = client.query(q3).to_dataframe()
print(df3.to_string())

# 4. High-value nonprofit PPP by state (top 5M+)
print("\n=== HIGH-VALUE NONPROFIT PPP ($5M+) ===")
q4 = """
SELECT BorrowerState, BorrowerName, InitialApprovalAmount, LoanStatus, ServicingLenderName
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(NonProfit) = 'Y' AND InitialApprovalAmount > 5000000
ORDER BY InitialApprovalAmount DESC
LIMIT 25
"""
df4 = client.query(q4).to_dataframe()
print(df4.to_string())

# 5. All Mercy House addresses across datasets
print("\n=== ALL MERCY HOUSE ADDRESSES ACROSS STATES ===")
q5 = """
SELECT 'PPP' as source, BorrowerName, BorrowerCity, BorrowerState, BorrowerAddress
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%MERCY%'
UNION ALL
SELECT 'OSINT' as source, name, city, state, address
FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%MERCY%'
ORDER BY BorrowerState, BorrowerCity
"""
df5 = client.query(q5).to_dataframe()
print(df5.to_string())

print("\nDone.")
