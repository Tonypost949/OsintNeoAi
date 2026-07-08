"""
Advanced Cross-Dataset Join: High-Risk Proximity Analysis
Joins: hb_llcs + church_osint entities + PPP loans + NPPES
On geo-coordinates and named entity overlaps.

Target addresses:
  - 7561 Center Ave, Huntington Beach (steering node)
  - 17472/17642 Beach Blvd, Huntington Beach
  - 807 N Garfield St, Santa Ana (Mercy House HQ)
  - 15822 Garnet St, Westminster (mailbox drop)
"""

from google.cloud import bigquery
import pandas as pd
from pathlib import Path

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
client = bigquery.Client(project=PROJECT)

TARGET_ZIPS = ["92647", "92646", "92683", "92655", "92701", "92703"]
TARGET_STREETS = ["CENTER AVE", "BEACH BLVD", "GARNET ST", "GARFIELD ST"]
TARGET_CITIES = ["HUNTINGTON BEACH", "SANTA ANA", "WESTMINSTER", "GARDEN GROVE"]

results = {}

# 1. hb_llcs — Orange County LLC records
print("=== hb_llcs: High-Risk Properties ===")
q_llcs = f"""
    SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, APN,
           LastSeller, LastSaleDate, LastSaleValue
    FROM `{PROJECT}.ppp_rico.hb_llcs`
    WHERE UPPER(MailCity) IN ({','.join(f"'{c}'" for c in TARGET_CITIES)})
       OR UPPER(SiteAddress) LIKE '%CENTER AVE%'
       OR UPPER(SiteAddress) LIKE '%BEACH BLVD%'
       OR UPPER(MailAddress) LIKE '%GARNET%'
       OR UPPER(Owner1) LIKE '%TAM%'
       OR UPPER(Owner1) LIKE '%PETER PHAM%'
       OR UPPER(Owner1) LIKE '%DYLAN%'
       OR UPPER(Owner1) LIKE '%ANDREW%'
       OR UPPER(Owner2) LIKE '%TAM%'
       OR UPPER(Owner2) LIKE '%PETER PHAM%'
    LIMIT 200
"""
df_llcs = client.query(q_llcs).to_dataframe()
results['hb_llcs'] = df_llcs
print(f"  {len(df_llcs)} rows")
if not df_llcs.empty:
    print(df_llcs[['Owner1','Owner2','SiteAddress','MailCity','LastSaleValue']].head(20).to_string())

# 2. Church OSINT entities — addresses and names
print("\n=== hb_church_osint.entities: Named + Geographic ===")
q_ent = f"""
    SELECT entity_id, name, type, address, city, state, ein, source
    FROM `{PROJECT}.hb_church_osint.entities`
    WHERE UPPER(city) IN ({','.join(f"'{c}'" for c in ["HUNTINGTON BEACH","SANTA ANA","WESTMINSTER","GARDEN GROVE","ORANGE"])})
       OR UPPER(address) LIKE '%CENTER AVE%'
       OR UPPER(address) LIKE '%BEACH BLVD%'
       OR UPPER(address) LIKE '%GARNET%'
       OR UPPER(name) LIKE '%PHAM%'
       OR UPPER(name) LIKE '%TAM%'
       OR UPPER(name) LIKE '%CHAU%'
       OR UPPER(name) LIKE '%DYLAN%'
       OR UPPER(name) LIKE '%ANDREW%'
       OR UPPER(name) LIKE '%HD ENTERTAINMENT%'
       OR UPPER(name) LIKE '%CP PREMIER%'
    LIMIT 200
"""
df_ent = client.query(q_ent).to_dataframe()
results['entities'] = df_ent
print(f"  {len(df_ent)} rows")
if not df_ent.empty:
    print(df_ent[['name','type','address','city']].head(20).to_string())

# 3. PPP loans — Orange County borrowers
print("\n=== PPP loans: Orange County + Named Entities ===")
q_ppp = f"""
    SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
           InitialApprovalAmount, LoanStatus, DateApproved, LoanNumber,
           ServicingLenderName, OriginatingLender, NAICSCode
    FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
    WHERE UPPER(ProjectCountyName) = 'ORANGE'
       OR UPPER(BorrowerCity) IN ({','.join(f"'{c}'" for c in ["HUNTINGTON BEACH","SANTA ANA","WESTMINSTER","GARDEN GROVE","ORANGE"])})
       OR UPPER(BorrowerName) LIKE '%PHAM%'
       OR UPPER(BorrowerName) LIKE '%TAM%'
       OR UPPER(BorrowerName) LIKE '%CHAU%'
       OR UPPER(BorrowerName) LIKE '%HD ENTERTAINMENT%'
       OR UPPER(BorrowerName) LIKE '%CP PREMIER%'
       OR UPPER(BorrowerName) LIKE '%MERCY HOUSE%'
    LIMIT 200
"""
df_ppp = client.query(q_ppp).to_dataframe()
results['ppp_150k'] = df_ppp
print(f"  {len(df_ppp)} rows")
if not df_ppp.empty:
    print(df_ppp[['BorrowerName','BorrowerCity','InitialApprovalAmount','LoanStatus']].head(20).to_string())

# 4. NPPES — OC licensed facilities
print("\n=== NPPES: Orange County Providers ===")
q_nppes = f"""
    SELECT org_name, city, taxonomy, npi
    FROM `{PROJECT}.nppes_export.oc_lb_orgs`
    WHERE UPPER(city) IN ({','.join(f"'{c}'" for c in ["HUNTINGTON BEACH","SANTA ANA","WESTMINSTER","GARDEN GROVE","ORANGE"])})
    LIMIT 100
"""
df_nppes = client.query(q_nppes).to_dataframe()
results['nppes'] = df_nppes
print(f"  {len(df_nppes)} rows")
if not df_nppes.empty:
    print(df_nppes[['org_name','city','taxonomy']].head(20).to_string())

# Save all
for name, df in results.items():
    if not df.empty:
        df.to_csv(WORK_DIR / f"crossref_{name}.csv", index=False)
        print(f"\nSaved crossref_{name}.csv ({len(df)} rows)")

print("\n=== SUMMARY ===")
for name, df in results.items():
    print(f"  {name}: {len(df)} rows")
