from google.cloud import bigquery
import pandas as pd
from pathlib import Path

client = bigquery.Client(project='noble-beanbag-497411-m4')
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 50)

# Check hb_llcs for Mercy House addresses or OC addresses
print("=== HB LLCs with OC addresses ===")
q = """
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue, LastSaleDate
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE UPPER(MailCity) LIKE '%SANTA ANA%'
       OR UPPER(MailCity) LIKE '%ORANGE%'
       OR UPPER(MailCity) LIKE '%HUNTINGTON%'
       OR UPPER(SiteAddress) LIKE '%SANTA ANA%'
    LIMIT 50
"""
df = client.query(q).to_dataframe()
print(f"Found {len(df)} rows")
print(df.to_string())

# Also check the entities table for Mercy House related
print("\n=== OSINT entities: Mercy House ===")
q2 = """
    SELECT entity_id, name, type, address, city, state, ein
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    WHERE UPPER(name) LIKE '%MERCY%'
       OR UPPER(name) LIKE '%CENTURY%'
       OR UPPER(name) LIKE '%VAGABOND%'
    LIMIT 50
"""
df2 = client.query(q2).to_dataframe()
print(f"Found {len(df2)} rows")
print(df2.to_string())

# NPPES for Mercy House
print("\n=== NPPES: Mercy House ===")
q3 = """
    SELECT org_name, city, taxonomy
    FROM `noble-beanbag-497411-m4.nppes_export.oc_lb_orgs`
    WHERE UPPER(org_name) LIKE '%MERCY%'
    LIMIT 50
"""
df3 = client.query(q3).to_dataframe()
print(f"Found {len(df3)} rows")
print(df3.to_string())

df.to_csv(WORK_DIR / "oc_llcs.csv", index=False)
df2.to_csv(WORK_DIR / "mercy_osint_entities.csv", index=False)
df3.to_csv(WORK_DIR / "mercy_nppes.csv", index=False)
