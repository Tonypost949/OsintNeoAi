from google.cloud import bigquery
client = bigquery.Client(project="noble-beanbag-497411-m4")

print("Creating mercy_oc_crossref...")
q1 = """
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.mercy_oc_crossref` AS
WITH
ppp_oc AS (
  SELECT
    'PPP_150K' AS source,
    LoanNumber,
    BorrowerName,
    BorrowerAddress,
    BorrowerCity,
    BorrowerState,
    ProjectCountyName AS county,
    InitialApprovalAmount AS amount,
    LoanStatus AS status,
    DateApproved AS date,
    ServicingLenderName AS lender,
    OriginatingLender AS orig_lender,
    NAICSCode,
    'NA' AS ein
  FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
  WHERE (UPPER(BorrowerName) LIKE '%MERCY%' OR UPPER(BorrowerName) LIKE '%CHDO%')
    AND (BorrowerState = 'CA' OR UPPER(ProjectCountyName) = 'ORANGE')
),
nppes_mercy AS (
  SELECT
    'NPPES' AS source,
    'NA' AS LoanNumber,
    org_name AS BorrowerName,
    'NA' AS BorrowerAddress,
    city AS BorrowerCity,
    'CA' AS BorrowerState,
    'ORANGE' AS county,
    0.0 AS amount,
    'Active' AS status,
    'NA' AS date,
    'NA' AS lender,
    'NA' AS orig_lender,
    taxonomy AS NAICSCode,
    'NA' AS ein
  FROM `noble-beanbag-497411-m4.nppes_export.oc_lb_orgs`
  WHERE UPPER(org_name) LIKE '%MERCY%'
     OR UPPER(org_name) LIKE '%CHDO%'
     OR UPPER(org_name) LIKE '%HOUSING%'
),
osint_entities AS (
  SELECT
    'OSINT' AS source,
    'NA' AS LoanNumber,
    name AS BorrowerName,
    address AS BorrowerAddress,
    city AS BorrowerCity,
    state AS BorrowerState,
    'ORANGE' AS county,
    0.0 AS amount,
    type AS status,
    'NA' AS date,
    'NA' AS lender,
    'NA' AS orig_lender,
    ein AS NAICSCode,
    ein AS ein
  FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
  WHERE UPPER(city) IN ('HUNTINGTON BEACH','SANTA ANA','WESTMINSTER','GARDEN GROVE','ORANGE')
     OR UPPER(name) LIKE '%MERCY%'
     OR UPPER(name) LIKE '%CHDO%'
)
SELECT * FROM ppp_oc
UNION ALL
SELECT * FROM nppes_mercy
UNION ALL
SELECT * FROM osint_entities
"""
client.query(q1).result()
print("mercy_oc_crossref done")

print("Creating beach_blvd_cluster...")
q2 = """
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.beach_blvd_cluster` AS
SELECT
  Owner1, Owner2, SiteAddress, MailAddress, MailCity,
  APN, LastSeller, LastSaleDate, LastSaleValue,
  CASE
    WHEN UPPER(SiteAddress) LIKE '%7561 CENTER%' THEN 'STEERING_NODE'
    WHEN UPPER(SiteAddress) LIKE '%1767%' OR UPPER(SiteAddress) LIKE '%1764%' THEN 'HBNC_PROXIMITY'
    WHEN CAST(LastSaleValue AS NUMERIC) > 10000000 THEN 'HIGH_VALUE'
    ELSE 'STANDARD'
  END AS risk_tier
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE UPPER(MailCity) IN ('HUNTINGTON BEACH','COSTA MESA','FOUNTAIN VALLEY','ANAHEIM','WESTMINSTER')
   OR UPPER(SiteAddress) LIKE '%CENTER AVE%'
   OR UPPER(SiteAddress) LIKE '%BEACH BLVD%'
ORDER BY LastSaleValue DESC
"""
client.query(q2).result()
print("beach_blvd_cluster done")

print("Creating banc_of_california_nonprofits...")
q3 = """
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.banc_of_california_nonprofits` AS
SELECT
  BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
  InitialApprovalAmount, LoanStatus, DateApproved, LoanNumber,
  NAICSCode, ServicingLenderName, OriginatingLender
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(ServicingLenderName) LIKE '%BANC OF CALIFORNIA%'
   AND UPPER(NonProfit) = 'Y'
ORDER BY InitialApprovalAmount DESC
"""
client.query(q3).result()
print("banc_of_california_nonprofits done")

print("Creating century_housing_borrowers...")
q4 = """
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.century_housing_borrowers` AS
SELECT
  BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
  InitialApprovalAmount, LoanStatus, DateApproved, LoanNumber,
  NAICSCode, ServicingLenderName, OriginatingLender
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(OriginatingLender) LIKE '%CENTURY%'
   OR UPPER(ServicingLenderName) LIKE '%CENTURY%'
ORDER BY InitialApprovalAmount DESC
"""
client.query(q4).result()
print("century_housing_borrowers done")

print("All 4 permanent BigQuery tables created.")
