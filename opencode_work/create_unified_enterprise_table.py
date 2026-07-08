from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")

q = """
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.ppp_rico.unified_enterprise` AS

SELECT
  'PPP-Property' AS pipeline,
  'TRIUMVIRATE LLC' AS entity_name,
  'LLC' AS entity_type,
  '21951 Brookhurst St, Fountain Valley CA' AS oc_property,
  2800000.00 AS property_value,
  1145251.00 AS ppp_amount,
  'AK' AS ppp_state,
  'Community Banks of CO' AS ppp_lender,
  '562211' AS naics,
  'Hazardous Waste Treatment' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  'Virtual office: 333 Washington Blvd Marina del Rey' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split multi-state PPP; property acquired 2021 from Rosell family' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'TRIUMVIRATE ENVIRONMENTAL INC' AS entity_name,
  'CORP' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  9050000.00 AS ppp_amount,
  'MA' AS ppp_state,
  'Webster Bank' AS ppp_lender,
  '562211' AS naics,
  'Hazardous Waste Treatment' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  '200 Inner Belt Rd, Somerville MA — industrial hazmat address' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Largest single TRIUMVIRATE entity; likely laundered funds to OC properties' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'TRIUMVIRATE OF BATON ROUGE INC' AS entity_name,
  'CORP' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  549458.00 AS ppp_amount,
  'LA' AS ppp_state,
  'First Horizon Bank' AS ppp_lender,
  '722410' AS naics,
  'Mobile food services' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split; unrelated NAICS to other TRIUMVIRATE entities' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'STEWART INDUSTRIES LLC' AS entity_name,
  'LLC' AS entity_type,
  '3311 Bounty Cir, Seal Beach CA' AS oc_property,
  0.00 AS property_value,
  1128800.00 AS ppp_amount,
  'MI' AS ppp_state,
  'Bank of America' AS ppp_lender,
  '336211' AS naics,
  'Aerospace products' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  'Property transferred from Stewart family 2021' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split across MI, OH, AL; property acquired $0 from Stewart family' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'STEWART INDUSTRIES INC / INT L' AS entity_name,
  'CORP' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  851448.00 AS ppp_amount,
  'OH, AL' AS ppp_state,
  'Huntington, Wells Fargo' AS ppp_lender,
  '336411' AS naics,
  'Aircraft parts' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split with STEWART INDUSTRIES LLC' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'L2T MEDIA LLC' AS entity_name,
  'LLC' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  1053297.00 AS ppp_amount,
  'IL' AS ppp_state,
  'JPMorgan Chase' AS ppp_lender,
  '541810' AS naics,
  'Advertising agencies' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split with 2L2TF LLC HI' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  '2L2TF LLC' AS entity_name,
  'LLC' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  209000.00 AS ppp_amount,
  'HI' AS ppp_state,
  'American Savings Bank' AS ppp_lender,
  '541810' AS naics,
  'Advertising agencies' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split with L2T MEDIA LLC IL' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'CM CLEANING SOLUTIONS INC' AS entity_name,
  'CORP' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  453944.00 AS ppp_amount,
  'CA' AS ppp_state,
  'Wells Fargo, Mortgage Capital' AS ppp_lender,
  '561720' AS naics,
  'Janitorial services' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  '333 Washington Blvd #142, Marina del Rey — virtual office hub' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split with CM CLEANING CO MA; shares virtual office with 19822 BROOKHURST + RAI PARTNERS' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'CM CLEANING CO, IC' AS entity_name,
  'CORP' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  462747.00 AS ppp_amount,
  'MA' AS ppp_state,
  'Rockland Trust' AS ppp_lender,
  '561720' AS naics,
  'Janitorial services' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'EIN-split with CM CLEANING SOLUTIONS INC CA' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  '19822 BROOKHURST LLC' AS entity_name,
  'LLC' AS entity_type,
  '19822 Brookhurst St, Huntington Beach CA' AS oc_property,
  12700000.00 AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  NULL AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  '333 Washington Blvd virtual office; $12.7M OC property; linked to CM CLEANING virtual office hub' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Real estate holding LLC; beneficial owner unknown; CA SOS lookup required' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'RAI PARTNERS LLC' AS entity_name,
  'LLC' AS entity_type,
  '20972 Brookhurst St, Huntington Beach CA' AS oc_property,
  2800000.00 AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  NULL AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  '333 Washington Blvd virtual office; $2.8M OC property; linked to 19822 BROOKHURST + CM CLEANING' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Real estate holding LLC; beneficial owner unknown; CA SOS lookup required' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'TS MARKETPLACE LLC' AS entity_name,
  'LLC' AS entity_type,
  '20002/20052 Brookhurst St, Westminster CA' AS oc_property,
  18500000.00 AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  NULL AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  '$18.5M OC property; Brookhurst corridor; beneficial owner unknown; CA SOS required' AS flags

UNION ALL

SELECT
  'PPP-Property' AS pipeline,
  'HRAPTS1 LLC' AS entity_name,
  'LLC' AS entity_type,
  '19001 Brookhurst St, Westminster CA' AS oc_property,
  11200000.00 AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  NULL AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  NULL AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  '$11.2M OC property; Brookhurst corridor; beneficial owner unknown; CA SOS required' AS flags

UNION ALL

SELECT
  'Grant-Toxics' AS pipeline,
  'MERCY HOUSE CHDO' AS entity_name,
  'CHDO' AS entity_type,
  NULL AS oc_property,
  NULL AS property_value,
  1339000.00 AS ppp_amount,
  'CA' AS ppp_state,
  'Banc of California' AS ppp_lender,
  NULL AS naics,
  'Nonprofit affordable housing developer' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  'PPP forgiven Jan 2021; $13.5M deferred carryback; $6.5M grant-to-CDFI; $3.96M undrawn' AS address_note,
  14600000.00 AS hud_grant,
  NULL AS ive_billing,
  'CHDO operator of HBNC; connected to toxic Cr VI plume; financial signature matches RICO network' AS flags

UNION ALL

SELECT
  'Grant-Toxics' AS pipeline,
  'HBNC (Huntington Beach Navigation Center)' AS entity_name,
  'SHELTER' AS entity_type,
  'Huntington Beach CA' AS oc_property,
  NULL AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  'Homeless shelter / navigation center' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  'Hexavalent chromium 49x EPA MCL at monitoring well; Mercy House CHDO operator' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Placement endpoint for CPS removal pipeline; toxic exposure = cause of death hypothesis' AS flags

UNION ALL

SELECT
  'Grant-Toxics' AS pipeline,
  '211 ORANGE COUNTY' AS entity_name,
  'GOV' AS entity_type,
  'Orange County CA' AS oc_property,
  NULL AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  'Social services call center / HMIS administrator' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  'Central choke point: all OC homeless must pass through 211 to access services; controls HMIS data' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Billing node for Grant-Toxics pipeline; data node for CPS pipeline; coordinates Coordinated Entry System' AS flags

UNION ALL

SELECT
  'CPS-Trafficking' AS pipeline,
  'OC SSA (Orange County Social Services Agency)' AS entity_name,
  'GOV' AS entity_type,
  'Orange County CA' AS oc_property,
  NULL AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  'Child welfare / foster care agency' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  '~30,000 removals/yr; $200M-$300M+/yr IV-E billing; 29,300 missing children' AS address_note,
  NULL AS hud_grant,
  300000000.00 AS ive_billing,
  'Removing agency for Pipeline 3; IV-E billing mechanism; OC SSA own records show 29,300 missing' AS flags

UNION ALL

SELECT
  'CPS-Trafficking' AS pipeline,
  'OC SSA CHILD DEATHS (4 CONFIRMED)' AS entity_name,
  'GOV' AS entity_type,
  'Mercy House / HBNC facilities OC' AS oc_property,
  NULL AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  'Child welfare' AS sector,
  4 AS deaths,
  NULL AS missing_children,
  '4 children died at or near Mercy House / HBNC contracted facilities' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Hypothesis: toxic Cr VI plume as mechanism of death; each death stops IV-E billing revenue stream' AS flags

UNION ALL

SELECT
  'CPS-Trafficking' AS pipeline,
  'OC SSA MISSING CHILDREN (29,300)' AS entity_name,
  'GOV' AS entity_type,
  'Orange County CA' AS oc_property,
  NULL AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  'Child welfare' AS sector,
  NULL AS deaths,
  29300 AS missing_children,
  'OC SSA own records; distinct from NCIC / NCMEC; possible: runaways, ICWA violations, trafficking, data fraud' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Hypothesis: children removed and placed for IV-E billing who were not in legitimate foster care placements' AS flags

UNION ALL

SELECT
  'CPS-Trafficking' AS pipeline,
  'TITLE IV-E (Federal)' AS entity_name,
  'FED' AS entity_type,
  'Federal — reimburses CA placements' AS oc_property,
  NULL AS property_value,
  NULL AS ppp_amount,
  NULL AS ppp_state,
  NULL AS ppp_lender,
  NULL AS naics,
  'Federal foster care reimbursement' AS sector,
  NULL AS deaths,
  NULL AS missing_children,
  '42 U.S.C. 670 et seq.; ~50-70% federal match per child per night; CA IV-E billing ~ billions/yr' AS address_note,
  NULL AS hud_grant,
  NULL AS ive_billing,
  'Billing mechanism for Pipeline 3; fraud = removal without lawful basis + billing for services not rendered' AS flags
"""

job = c.query(q)
job.result()
print("unified_enterprise table created.")
