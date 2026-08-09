from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

SQL = """
CREATE OR REPLACE TABLE `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_ppp_bridge` AS

WITH hb AS (
  SELECT
    COALESCE(Owner1, Owner2)                          AS entity_name,
    SiteAddress                                       AS property_address,
    'Huntington Beach'                                AS property_city,
    APN                                               AS property_apn,
    MailAddress                                       AS property_mail_address,
    MailCity                                          AS property_mail_city,
    LastSeller                                        AS last_seller,
    SAFE.PARSE_DATE('%m/%d/%Y', LastSaleDate)         AS property_acquisition_date,
    LastSaleValue                                     AS property_acquisition_value,
    -- Mailbox flag: mail address differs from site address
    (MailAddress IS NOT NULL AND TRIM(MailAddress) != TRIM(SiteAddress)) AS is_mailbox_address,
    -- Zero dollar transfer
    (LastSaleValue = 0)                               AS is_zero_dollar_transfer,
    -- Post-PPP acquisition (after Jan 1 2021)
    (SAFE.PARSE_DATE('%m/%d/%Y', LastSaleDate) > DATE '2021-01-01') AS is_post_ppp_property_acquisition
  FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_llcs`
  WHERE Owner1 IS NOT NULL OR Owner2 IS NOT NULL
),

rm AS (
  SELECT
    llc_name,
    property_address,
    mail_city,
    last_sale_value,
    ppp_loan_count,
    ppp_total_amount,
    ppp_total_forgiven,
    ppp_names,
    loan_locations                                    AS ppp_business_addresses,
    loan_statuses,
    -- Extract first city from loan_locations (e.g. "Battle Creek, MI; BATTLE CREEK, MI")
    TRIM(SPLIT(loan_locations, ';')[OFFSET(0)])       AS ppp_borrower_city_raw,
    -- Multi-state: check if more than one unique state in loan_locations
    (ARRAY_LENGTH(
      ARRAY(SELECT DISTINCT TRIM(REGEXP_EXTRACT(loc, r',\\s*([A-Z]{2})$'))
            FROM UNNEST(SPLIT(loan_locations, ';')) AS loc)
    ) > 1)                                            AS is_multi_state_ppp
  FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.rico_matches`
),

joined AS (
  SELECT
    hb.entity_name,
    hb.property_address,
    hb.property_city,
    hb.property_apn,
    hb.property_mail_address,
    hb.property_mail_city,
    hb.last_seller,
    hb.property_acquisition_date,
    hb.property_acquisition_value,
    -- PPP fields from rico_matches joined on address or entity name
    rm.ppp_loan_count,
    rm.ppp_total_amount,
    rm.ppp_total_forgiven,
    rm.ppp_business_addresses,
    -- State array from loan_locations
    ARRAY_TO_STRING(
      ARRAY(SELECT DISTINCT TRIM(REGEXP_EXTRACT(loc, r',\\s*([A-Z]{2})$'))
            FROM UNNEST(SPLIT(rm.ppp_business_addresses, ';')) AS loc
            WHERE REGEXP_EXTRACT(loc, r',\\s*([A-Z]{2})$') IS NOT NULL),
      ', '
    )                                                 AS ppp_state_array,
    NULL                                              AS ppp_naics_codes,
    NULL                                              AS ppp_lenders,
    NULL                                              AS ppp_borrower_address,
    TRIM(REGEXP_EXTRACT(rm.ppp_borrower_city_raw, r'^(.+),'))  AS ppp_borrower_city,
    TRIM(REGEXP_EXTRACT(rm.ppp_borrower_city_raw, r',\\s*([A-Z]{2})$')) AS ppp_borrower_state,
    rm.is_multi_state_ppp,
    FALSE                                             AS is_naics_mismatch,
    hb.is_post_ppp_property_acquisition,
    hb.is_mailbox_address,
    hb.is_zero_dollar_transfer
  FROM hb
  LEFT JOIN rm
    ON UPPER(TRIM(hb.entity_name)) = UPPER(TRIM(rm.llc_name))
    OR UPPER(TRIM(hb.property_address)) = UPPER(TRIM(rm.property_address))
)

SELECT * FROM joined
"""

print("Building hb_ppp_bridge table in BigQuery...")
job = bq.query(SQL)
job.result()
print("✅ hb_ppp_bridge table created successfully!")

# Show summary stats
summary = bq.query("""
SELECT
  COUNT(*) AS total_entities,
  COUNTIF(ppp_loan_count > 0) AS entities_with_ppp,
  COUNTIF(is_multi_state_ppp) AS multi_state_ppp,
  COUNTIF(is_mailbox_address) AS mailbox_addresses,
  COUNTIF(is_zero_dollar_transfer) AS zero_dollar_transfers,
  COUNTIF(is_post_ppp_property_acquisition) AS post_ppp_acquisitions,
  ROUND(SUM(ppp_total_amount), 2) AS total_ppp_dollars,
  ROUND(SUM(ppp_total_forgiven), 2) AS total_ppp_forgiven
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_ppp_bridge`
""").to_dataframe()

print("\n── Bridge Table Summary ──")
print(summary.to_string(index=False))

# Show top suspects
print("\n── Top 20 Suspects by PPP Amount ──")
top = bq.query("""
SELECT
  entity_name,
  property_address,
  property_mail_city,
  ROUND(ppp_total_amount, 0) AS ppp_total,
  ROUND(ppp_total_forgiven, 0) AS forgiven,
  ppp_loan_count,
  is_multi_state_ppp,
  is_mailbox_address,
  is_zero_dollar_transfer,
  is_post_ppp_property_acquisition
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.hb_ppp_bridge`
WHERE ppp_total_amount IS NOT NULL
ORDER BY ppp_total_amount DESC
LIMIT 20
""").to_dataframe()
print(top.to_string(index=False))
