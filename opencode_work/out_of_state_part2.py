"""Out-of-state network — shared address linkage"""
from google.cloud import bigquery
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
client = bigquery.Client(project="noble-beanbag-497411-m4")

# Get TRIUMVIRATE mailing address
q1 = """
SELECT DISTINCT MailAddress, MailCity
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%TRIUMVIRATE%'
"""
tri_df = client.query(q1).to_dataframe()
print("TRIUMVIRATE mail addresses:", tri_df.to_string())

# Get STEWART mailing address
q2 = """
SELECT DISTINCT MailAddress, MailCity
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%STEWART INDUSTRIES%'
"""
stw_df = client.query(q2).to_dataframe()
print("STEWART mail addresses:", stw_df.to_string())

# Find LLCs sharing TRIUMVIRATE address
if not tri_df.empty:
    addr = tri_df.iloc[0]['MailAddress']
    q3 = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE MailAddress = '{addr.replace("'", "''")}'
       AND UPPER(Owner1) NOT LIKE '%TRIUMVIRATE%'
    ORDER BY LastSaleValue DESC
    LIMIT 20
    """
    df3 = client.query(q3).to_dataframe()
    print(f"\nOC LLCs sharing TRIUMVIRATE address '{addr}':")
    print(df3.to_string())

# Find LLCs sharing STEWART address
if not stw_df.empty:
    addr = stw_df.iloc[0]['MailAddress']
    q4 = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE MailAddress = '{addr.replace("'", "''")}'
       AND UPPER(Owner1) NOT LIKE '%STEWART%'
    ORDER BY LastSaleValue DESC
    LIMIT 20
    """
    df4 = client.query(q4).to_dataframe()
    print(f"\nOC LLCs sharing STEWART address '{addr}':")
    print(df4.to_string())

# TRIUMVIRATE owner ROSELL — search for their other LLCs
q5 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(Owner1) LIKE '%ROSELL%' OR UPPER(Owner2) LIKE '%ROSELL%'
ORDER BY LastSaleValue DESC
LIMIT 20
"""
df5 = client.query(q5).to_dataframe()
print("\nROSELL-owned LLCs in OC:")
print(df5.to_string())

# TRIUMVIRATE property: 21951 Brookhurst St — who else owns near there?
q6 = """
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSaleValue
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(SiteAddress) LIKE '%21951%' OR UPPER(SiteAddress) LIKE '%BROOKHURST%'
ORDER BY LastSaleValue DESC
LIMIT 20
"""
df6 = client.query(q6).to_dataframe()
print("\nLLCs near 21951 Brookhurst St:")
print(df6.to_string())

print("\nDone.")
