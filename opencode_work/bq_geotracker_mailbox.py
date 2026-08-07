import os, pandas as pd
os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PROJECT = "noble-beanbag-497411-m4"

HEADER = "=" * 60

# ============ QUERY 1: GeoTracker address search ============
print(HEADER)
print("QUERY 1: 17472, 17642, Cameron in properties")
print(HEADER)
q1 = f"""
SELECT *
FROM `{PROJECT}.hb_church_osint.properties`
WHERE UPPER(address) LIKE '%17472%'
   OR UPPER(address) LIKE '%17642%'
   OR UPPER(address) LIKE '%CAMERON%'
ORDER BY address
"""
df1 = client.query(q1).to_dataframe()
print(f"Found: {len(df1)} properties")
if len(df1) > 0:
    print(df1.to_string())
print()

# Also hb_llcs
print("QUERY 1b: 17472/17642/Cameron in hb_llcs")
q1b = f"""
SELECT Owner1, SiteAddress, MailAddress, MailCity, APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{PROJECT}.ppp_rico.hb_llcs`
WHERE UPPER(SiteAddress) LIKE '%17472%'
   OR UPPER(SiteAddress) LIKE '%17642%'
   OR UPPER(SiteAddress) LIKE '%CAMERON%'
ORDER BY SiteAddress
"""
df1b = client.query(q1b).to_dataframe()
print(f"Found: {len(df1b)} LLCs")
if len(df1b) > 0:
    print(df1b.to_string())
print()

# ============ QUERY 2: MAILBOX CLUSTER 1077 PCH ============
print(HEADER)
print("QUERY 2: 1077 PCH Mailbox Cluster")
print(HEADER)
q2 = f"""
SELECT Owner1, SiteAddress, MailAddress, APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{PROJECT}.ppp_rico.hb_llcs`
WHERE UPPER(MailAddress) LIKE '%1077%PACIFIC%COAST%'
ORDER BY LastSaleDate
"""
df2 = client.query(q2).to_dataframe()
print(f"Found: {len(df2)} LLCs at 1077 PCH")
if len(df2) > 0:
    date_min = df2["LastSaleDate"].min()
    date_max = df2["LastSaleDate"].max()
    print(f"Date range: {date_min} to {date_max}")
    print(df2.to_string())
else:
    # Broader
    q2b = f"""
    SELECT Owner1, SiteAddress, MailAddress, APN, LastSeller, LastSaleDate, LastSaleValue
    FROM `{PROJECT}.ppp_rico.hb_llcs`
    WHERE UPPER(MailAddress) LIKE '%1077%PCH%'
       OR UPPER(MailAddress) LIKE '%1077%PACIFIC%'
    ORDER BY LastSaleDate
    """
    df2b = client.query(q2b).to_dataframe()
    print(f"Broader search: {len(df2b)} LLCs")
    if len(df2b) > 0:
        print(df2b.to_string())
print()

# ============ QUERY 3: Top mailbox clusters ============
print(HEADER)
print("QUERY 3: Top 15 mailbox clusters (>=3 LLCs)")
print(HEADER)
q3 = f"""
SELECT 
    MailAddress, 
    COUNT(*) AS llc_count, 
    ROUND(AVG(SAFE_CAST(LastSaleValue AS FLOAT64)),0) AS avg_sale_value,
    MIN(LastSaleDate) AS first_sale, 
    MAX(LastSaleDate) AS last_sale,
    STRING_AGG(DISTINCT Owner1, ' | ') AS llc_names
FROM `{PROJECT}.ppp_rico.hb_llcs`
WHERE MailAddress IS NOT NULL AND MailAddress != ''
GROUP BY MailAddress
HAVING COUNT(*) >= 3
ORDER BY llc_count DESC
LIMIT 15
"""
df3 = client.query(q3).to_dataframe()
print(df3.to_string())
print()

# ============ QUERY 4: ALSO check hb_church_osint.entities for G&M, ONNI, 17472 ============
print(HEADER)
print("QUERY 4: Entities matching G&M, ONNI, 17472, Exxon, Mobil")
print(HEADER)
q4 = f"""
SELECT name, type, address, city, state, ein, source
FROM `{PROJECT}.hb_church_osint.entities`
WHERE UPPER(name) LIKE '%G&M%'
   OR UPPER(name) LIKE '%ONNI%'
   OR UPPER(name) LIKE '%EXXON%'
   OR UPPER(name) LIKE '%MOBIL%'
   OR UPPER(address) LIKE '%17472%'
   OR UPPER(address) LIKE '%17642%'
ORDER BY name
"""
df4 = client.query(q4).to_dataframe()
print(f"Found: {len(df4)} entities")
if len(df4) > 0:
    print(df4.to_string())
print()

# ============ QUERY 5: CA environmental from all_state_records ============
print(HEADER)
print("QUERY 5: CA environmental_site_assessments from all_state_records")
print(HEADER)
q5 = f"""
SELECT state, environmental_site_assessments
FROM `{PROJECT}.national_audits.all_state_records`
WHERE state = 'CA'
"""
df5 = client.query(q5).to_dataframe()
if len(df5) > 0:
    esa_col = str(df5.iloc[0]["environmental_site_assessments"])
    print(f"CA ESA data ({len(esa_col)} chars)")
    # Check for key addresses
    for addr in ["17472", "17642", "Cameron", "G&M", "ONNI", "Beach Blvd"]:
        if addr.lower() in esa_col.lower():
            idx = esa_col.lower().find(addr.lower())
            snippet = esa_col[max(0,idx-40):idx+80]
            print(f"  [{addr}]: ...{snippet}...")
    print(f"\nFirst 800 chars:\n{esa_col[:800]}")

print(f"\n{HEADER}")
print("DONE")
