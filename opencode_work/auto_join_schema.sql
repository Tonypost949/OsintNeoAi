-- ============================================================
-- OSINT Network Cross-Reference: Permanent Auto-Join Schema
-- Project: noble-beanbag-497411-m4
-- Purpose: Join PPP + LLC + Church/OSINT + NPPES + CHDO
-- Run this in BigQuery UI or via bq CLI
-- ============================================================

-- 1. OC MERCY HOUSE ENTITIES (PPP borrowers + NPPES + LLC)
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.mercy_oc_crossref` AS
WITH

-- PPP: Mercy House + CA Orange County borrowers
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

-- NPPES: Mercy House licensed facilities in Orange County
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

-- OSINT entities: Mercy + HB entities in Orange County
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
SELECT * FROM osint_entities;


-- 2. HIGH-RISK BEACH BLVD / CENTER AVE LLC CLUSTER
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.beach_blvd_cluster` AS
SELECT
  Owner1,
  Owner2,
  SiteAddress,
  MailAddress,
  MailCity,
  APN,
  LastSeller,
  LastSaleDate,
  LastSaleValue,
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
ORDER BY LastSaleValue DESC;


-- 3. MERCY HOUSE PPP → LENDER → OTHER NONPROFIT CLIENTS
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.banc_of_california_nonprofits` AS
SELECT
  BorrowerName,
  BorrowerAddress,
  BorrowerCity,
  BorrowerState,
  InitialApprovalAmount,
  LoanStatus,
  DateApproved,
  LoanNumber,
  NAICSCode,
  ServicingLenderName,
  OriginatingLender
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(ServicingLenderName) = 'BANC OF CALIFORNIA'
   AND UPPER(NonProfit) = 'Y'
ORDER BY InitialApprovalAmount DESC;


-- 4. CENTURY HOUSING CORPORATION — ALL PPP LENDERS (as originating lender)
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.century_housing_ Borrowers` AS
SELECT
  BorrowerName,
  BorrowerAddress,
  BorrowerCity,
  BorrowerState,
  InitialApprovalAmount,
  LoanStatus,
  DateApproved,
  LoanNumber,
  NAICSCode,
  ServicingLenderName,
  OriginatingLender
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE UPPER(OriginatingLender) LIKE '%CENTURY%'
   OR UPPER(ServicingLenderName) LIKE '%CENTURY%'
ORDER BY InitialApprovalAmount DESC;


-- 5. CHDO TRANSACTION CROSS-REF (join CHDO extracted transactions to PPP + LLC + NPPES)
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.chdo_pipeline_crossref` AS
WITH chdo AS (
  SELECT
    'CHDO_AUDIT' AS source,
    chdo_llc AS entity,
    project_name AS project,
    ownership_structure AS structure,
    lp_entity_counterparty AS counterparty,
    transaction_type AS tx_type,
    CAST(REPLACE(REPLACE(amount, ',', ''), '$', '') AS NUMERIC) AS amount,
    interest_rate AS rate,
    terms_notes AS notes,
    flags AS risk_flag
  FROM `noble-beanbag-497411-m4.ppp_rico.chdo_transactions`  -- load from CSV
),

ppp_chdo AS (
  SELECT
    'PPP' AS source,
    BorrowerName AS entity,
    BorrowerCity AS city,
    InitialApprovalAmount AS amount,
    LoanStatus AS status,
    ServicingLenderName AS lender,
    DateApproved AS date
  FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
  WHERE UPPER(BorrowerName) LIKE '%MERCY%'
     OR UPPER(BorrowerName) LIKE '%CHDO%'
     OR UPPER(BorrowerName) LIKE '%HOUSING%'
)

SELECT * FROM chdo
UNION ALL
SELECT * FROM ppp_chdo;
