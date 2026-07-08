"""
BQ Cross-Reference: HB LLC Owners [>] PPP [>] NPPES [>] Mercy House/Nonprofit Network
Corrected schemas.
"""
import os
from google.cloud import bigquery
import pandas as pd

os.environ['GOOGLE_CLOUD_PROJECT'] = 'noble-beanbag-497411-m4'
PROJECT = 'noble-beanbag-497411-m4'
client = bigquery.Client()

OUT = r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_crossref_full.csv"

# ============================================================
# QUERY 1: HB LLC owners who also appear in PPP data
# ============================================================
print("[1/7] HB LLC owners in PPP...")
q1 = f"""
WITH
llc_owners AS (
  SELECT DISTINCT
    Owner1 AS owner_name, Owner2, SiteAddress AS property_address,
    MailAddress, MailCity, APN,
    LastSeller, LastSaleDate, LastSaleValue AS sale_price,
    UPPER(REGEXP_REPLACE(Owner1, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.hb_llcs`
  WHERE Owner1 IS NOT NULL AND Owner1 != ''
),
ppp_all AS (
  SELECT
    BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
    CAST(CurrentApprovalAmount AS FLOAT64) AS CurrentApprovalAmount,
    CAST(ForgivenessAmount AS FLOAT64) AS ForgivenessAmount,
    DateApproved, LoanStatus, BusinessType, NAICSCode,
    UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT
    BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
    CAST(CurrentApprovalAmount AS FLOAT64),
    CAST(ForgivenessAmount AS FLOAT64),
    DateApproved, LoanStatus, BusinessType, NAICSCode,
    UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.ppp_up_to_150k`
)
SELECT
  l.owner_name, l.Owner2, l.property_address, l.MailCity,
  l.APN, l.LastSeller, l.LastSaleDate, l.sale_price,
  COUNT(DISTINCT p.BorrowerName) AS ppp_loan_count,
  ROUND(SUM(p.CurrentApprovalAmount), 2) AS ppp_total_approved,
  ROUND(SUM(p.ForgivenessAmount), 2) AS ppp_total_forgiven,
  STRING_AGG(DISTINCT p.BorrowerName, '; ') AS ppp_business_names,
  STRING_AGG(DISTINCT CONCAT(p.BorrowerCity, ', ', p.BorrowerState), '; ') AS ppp_locations,
  STRING_AGG(DISTINCT p.LoanStatus, '; ') AS loan_statuses,
  STRING_AGG(DISTINCT SUBSTR(p.DateApproved, 1, 7), '; ') AS approval_dates
FROM llc_owners l
JOIN ppp_all p ON l.clean_name = p.clean_name
GROUP BY l.owner_name, l.Owner2, l.property_address, l.MailCity,
         l.APN, l.LastSeller, l.LastSaleDate, l.sale_price
ORDER BY ppp_total_approved DESC
"""
df1 = client.query(q1).to_dataframe()
print(f"  [>] {len(df1)} LLC owners with PPP loans, top 10:")
df1.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_llc_owners_ppp.csv", index=False)
print(df1.head(10).to_string())
print()

# ============================================================
# QUERY 2: HB LLC owners [>] NPPES (OC health orgs by name)
# ============================================================
print("[2/7] HB LLC owners in NPPES (OC health orgs)...")
q2 = f"""
WITH
llc_owners AS (
  SELECT DISTINCT
    Owner1 AS owner_name,
    SiteAddress AS property_address,
    MailCity,
    UPPER(REGEXP_REPLACE(Owner1, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.hb_llcs`
  WHERE Owner1 IS NOT NULL AND Owner1 != ''
),
npi AS (
  SELECT
    UPPER(REGEXP_REPLACE(name, r'[-.,&/() ]', '')) AS clean_name,
    name AS npi_name, ein, city AS nppes_city, state AS nppes_state
  FROM `{PROJECT}.nppes_export.irs_ein_oc_lb_health`
)
SELECT
  l.owner_name, l.property_address, l.MailCity,
  n.npi_name, n.ein, n.nppes_city, n.nppes_state
FROM llc_owners l
JOIN npi n ON l.clean_name = n.clean_name
ORDER BY l.owner_name
"""
df2 = client.query(q2).to_dataframe()
print(f"  [>] {len(df2)} LLC owners also in NPPES health orgs")
df2.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_llc_owners_npppes.csv", index=False)
if len(df2) > 0:
    print(df2.head(10).to_string())
print()

# ============================================================
# QUERY 3: Mercy House / Waymakers / HB nonprofits in PPP
# ============================================================
print("[3/7] Mercy House / Waymakers / HB nonprofits in PPP...")
q3 = f"""
SELECT
  BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
  CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
  BusinessType, NAICSCode, NonProfit, Gender, Veteran,
  JobsReported, ForgivenessDate
FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%MERCY HOUSE%'
   OR UPPER(BorrowerName) LIKE '%WAYMAKERS%'
   OR UPPER(BorrowerName) LIKE '%AMERICAN FAMILY HOUSING%'
   OR UPPER(BorrowerName) LIKE '%FAMILIES FORWARD%'
   OR UPPER(BorrowerName) LIKE '%OC UNITED%'
   OR UPPER(BorrowerName) LIKE '%HOPE FOR%HOMELESS%'
   OR UPPER(BorrowerName) LIKE '%HUNTINGTON%SHELTER%'
   OR UPPER(BorrowerName) LIKE '%TRANSITIONAL%HOUSING%'
UNION ALL
SELECT
  BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
  CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
  BusinessType, NAICSCode, NonProfit, Gender, Veteran,
  JobsReported, ForgivenessDate
FROM `{PROJECT}.ppp_rico.ppp_up_to_150k`
WHERE UPPER(BorrowerName) LIKE '%MERCY HOUSE%'
   OR UPPER(BorrowerName) LIKE '%WAYMAKERS%'
   OR UPPER(BorrowerName) LIKE '%AMERICAN FAMILY HOUSING%'
   OR UPPER(BorrowerName) LIKE '%FAMILIES FORWARD%'
   OR UPPER(BorrowerName) LIKE '%OC UNITED%'
   OR UPPER(BorrowerName) LIKE '%HOPE FOR%HOMELESS%'
   OR UPPER(BorrowerName) LIKE '%HUNTINGTON%SHELTER%'
   OR UPPER(BorrowerName) LIKE '%TRANSITIONAL%HOUSING%'
ORDER BY CurrentApprovalAmount DESC
"""
df3 = client.query(q3).to_dataframe()
print(f"  [>] {len(df3)} nonprofit PPP loans found")
df3.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_nonprofits_ppp.csv", index=False)
if len(df3) > 0:
    print(df3.head(20).to_string())
print()

# ============================================================
# QUERY 4: Full enriched RICO matrix
# ============================================================
print("[4/7] Enriched RICO evidence matrix (ALL HB LLCs with full PPP join)...")
q4 = f"""
WITH
llc_full AS (
  SELECT
    Owner1 AS llc_name, Owner2, SiteAddress AS property_address,
    MailAddress, MailCity, APN,
    LastSeller, LastSaleDate, CAST(LastSaleValue AS FLOAT64) AS sale_price,
    UPPER(REGEXP_REPLACE(Owner1, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.hb_llcs`
),
ppp_full AS (
  SELECT
    BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
    CAST(CurrentApprovalAmount AS FLOAT64) AS CurrentApprovalAmount,
    CAST(ForgivenessAmount AS FLOAT64) AS ForgivenessAmount,
    DateApproved, LoanStatus, BusinessType, NAICSCode,
    Gender, Veteran, NonProfit, CAST(JobsReported AS FLOAT64) AS JobsReported,
    UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT
    BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
    CAST(CurrentApprovalAmount AS FLOAT64),
    CAST(ForgivenessAmount AS FLOAT64),
    DateApproved, LoanStatus, BusinessType, NAICSCode,
    Gender, Veteran, NonProfit, CAST(JobsReported AS FLOAT64) AS JobsReported,
    UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.ppp_up_to_150k`
)
SELECT
  l.llc_name, l.Owner2, l.property_address, l.MailCity,
  l.APN, l.LastSeller, l.LastSaleDate, l.sale_price,
  COUNT(DISTINCT p.BorrowerName) AS ppp_loan_count,
  ROUND(SUM(p.CurrentApprovalAmount), 2) AS ppp_total_approved,
  ROUND(SUM(p.ForgivenessAmount), 2) AS ppp_total_forgiven,
  STRING_AGG(DISTINCT p.BorrowerName, '; ') AS ppp_business_names,
  STRING_AGG(DISTINCT CONCAT(p.BorrowerCity, ', ', p.BorrowerState), '; ') AS ppp_locations,
  STRING_AGG(DISTINCT p.NAICSCode, '; ') AS naics_codes,
  STRING_AGG(DISTINCT p.NonProfit, '; ') AS nonprofit_flags,
  STRING_AGG(DISTINCT SUBSTR(p.DateApproved, 1, 7), '; ') AS approval_dates,
  STRING_AGG(DISTINCT p.LoanStatus, '; ') AS loan_statuses,
  ROUND(SUM(p.JobsReported), 0) AS jobs_reported
FROM llc_full l
LEFT JOIN ppp_full p ON l.clean_name = p.clean_name
GROUP BY l.llc_name, l.Owner2, l.property_address, l.MailCity,
         l.APN, l.LastSeller, l.LastSaleDate, l.sale_price
HAVING COUNT(DISTINCT p.BorrowerName) > 0
ORDER BY ppp_total_approved DESC
"""
df4 = client.query(q4).to_dataframe()
print(f"  [>] {len(df4)} LLCs with PPP matches (enriched matrix)")
df4.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_enriched_rico_matrix.csv", index=False)
print(df4.head(15).to_string())
print()

# ============================================================
# QUERY 5: hb_church_osint entities [>] PPP
# ============================================================
print("[5/7] HB Church OSINT entities [>] PPP cross-ref...")
q5 = f"""
WITH
entities AS (
  SELECT DISTINCT
    name, type, address, city, state, zip, ein,
    UPPER(REGEXP_REPLACE(name, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.hb_church_osint.entities`
  WHERE name IS NOT NULL AND name != ''
),
ppp_all AS (
  SELECT
    BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
    CAST(CurrentApprovalAmount AS FLOAT64) AS CurrentApprovalAmount,
    CAST(ForgivenessAmount AS FLOAT64) AS ForgivenessAmount,
    DateApproved, LoanStatus, BusinessType, NAICSCode, NonProfit,
    UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
  UNION ALL
  SELECT
    BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
    CAST(CurrentApprovalAmount AS FLOAT64),
    CAST(ForgivenessAmount AS FLOAT64),
    DateApproved, LoanStatus, BusinessType, NAICSCode, NonProfit,
    UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
  FROM `{PROJECT}.ppp_rico.ppp_up_to_150k`
)
SELECT
  e.name AS entity_name, e.type, e.address, e.city, e.state, e.zip, e.ein,
  COUNT(DISTINCT p.BorrowerName) AS ppp_loan_count,
  ROUND(SUM(p.CurrentApprovalAmount), 2) AS ppp_total,
  STRING_AGG(DISTINCT p.BorrowerName, '; ') AS ppp_business_names,
  STRING_AGG(DISTINCT CONCAT(p.BorrowerCity, ', ', p.BorrowerState), '; ') AS ppp_locations,
  STRING_AGG(DISTINCT p.LoanStatus, '; ') AS loan_statuses
FROM entities e
JOIN ppp_all p ON e.clean_name = p.clean_name
GROUP BY e.name, e.type, e.address, e.city, e.state, e.zip, e.ein
ORDER BY ppp_total DESC
"""
df5 = client.query(q5).to_dataframe()
print(f"  [>] {len(df5)} HB church entities with PPP loans")
df5.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_church_ppp.csv", index=False)
if len(df5) > 0:
    print(df5.head(15).to_string())
print()

# ============================================================
# QUERY 6: Big PPP loans in OC/HB area — look for RICO patterns
# ============================================================
print("[6/7] Large PPP loans in OC/HB (>$500K) — RICO pattern scan...")
q6 = f"""
SELECT
  BorrowerName, BorrowerCity, BorrowerState, BorrowerZip,
  CurrentApprovalAmount, ForgivenessAmount, DateApproved, LoanStatus,
  BusinessType, NAICSCode, NonProfit, Gender, Veteran,
  JobsReported, ForgivenessDate,
  ServicingLenderName, OriginatingLender, OriginatingLenderCity, OriginatingLenderState
FROM `{PROJECT}.ppp_rico.ppp_150k_plus`
WHERE (BorrowerState = 'CA' AND BorrowerCity IN (
    'Huntington Beach','Costa Mesa','Newport Beach','Fountain Valley',
    'Seal Beach','Westminster','Anaheim','Santa Ana','Long Beach','Los Alamitos'))
  AND CAST(CurrentApprovalAmount AS FLOAT64) > 500000
ORDER BY CurrentApprovalAmount DESC
LIMIT 100
"""
df6 = client.query(q6).to_dataframe()
print(f"  [>] {len(df6)} large OC PPP loans (>$500K)")
df6.to_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\bq_large_oc_ppp.csv", index=False)
print(df6.head(20).to_string())
print()

# ============================================================
# QUERY 7: Write combined output
# ============================================================
print("[7/7] Writing combined cross-reference...")
combined = pd.concat([
    df1.assign(category="HB LLC Owner [>] PPP"),
    df2.assign(category="HB LLC Owner [>] NPPES OC Health") if len(df2) > 0 else pd.DataFrame(),
    df3.assign(category="Nonprofit [>] PPP") if len(df3) > 0 else pd.DataFrame(),
    df4.assign(category="Enriched RICO Matrix") if len(df4) > 0 else pd.DataFrame(),
    df5.assign(category="HB Church Entity [>] PPP") if len(df5) > 0 else pd.DataFrame(),
    df6.assign(category="Large OC PPP Loans >$500K") if len(df6) > 0 else pd.DataFrame(),
], ignore_index=True)

combined.to_csv(OUT, index=False)
print(f"  [>] Wrote {len(combined)} total rows to bq_crossref_full.csv")
print()
print("=== TOP 20 BY PPP AMOUNT ===")
top = combined[combined['ppp_total_approved'].notna()].nlargest(20, 'ppp_total_approved')
for _, r in top.iterrows():
    name = str(r.get('llc_name', r.get('name', r.get('BorrowerName', ''))))[:40]
    amt = r['ppp_total_approved']
    cat = r['category']
    print(f"  ${amt:>12,.0f}  [{cat[:25]}]  {name}")
print()
print("=== DONE ===")
