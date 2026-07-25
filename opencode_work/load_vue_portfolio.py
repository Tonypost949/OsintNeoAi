from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Load VUE INVESTOR OWNER LLC portfolio (56 properties)
query = """
INSERT INTO `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
SELECT 
  Owner1 as entity_name,
  SiteAddress as property_address,
  'Huntington Beach' as property_city,
  APN as property_apn,
  MailAddress as property_mail_address,
  MailCity as property_mail_city,
  LastSeller as last_seller,
  PARSE_DATE('%m/%d/%Y', LastSaleDate) as property_acquisition_date,
  CAST(LastSaleValue AS FLOAT64) as property_acquisition_value,
  0 as ppp_loan_count,
  0.0 as ppp_total_amount,
  0.0 as ppp_total_forgiven,
  [] as ppp_business_addresses,
  [] as ppp_state_array,
  [] as ppp_naics_codes,
  [] as ppp_lenders,
  SiteAddress as ppp_borrower_address,
  'Huntington Beach' as ppp_borrower_city,
  'CA' as ppp_borrower_state,
  FALSE as is_multi_state_ppp,
  FALSE as is_naics_mismatch,
  FALSE as is_post_ppp_property_acquisition,
  TRUE as is_mailbox_address,
  TRUE as is_zero_dollar_transfer,
  FALSE as is_lender_fraud_flag
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
WHERE LastSeller = 'VUE INVESTOR OWNER LLC'
  AND Owner1 NOT IN (SELECT entity_name FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`)
"""

try:
    job = client.query(query)
    job.result()
    print(f'Loaded {job.num_dml_affected_rows} VUE INVESTOR OWNER LLC properties')
except Exception as e:
    print(f'Error: {e}')

# Get updated summary
summary_query = """
SELECT 
  COUNT(*) as total_entities,
  COUNTIF(is_zero_dollar_transfer = TRUE) as zero_dollar_transfers,
  COUNTIF(is_mailbox_address = TRUE) as shell_factory_pattern,
  COUNTIF(is_lender_fraud_flag = TRUE) as lender_fraud_flagged,
  SUM(ppp_total_amount) as total_ppp
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
"""

try:
    results = client.query(summary_query).result()
    for row in results:
        print(f'\nBridge table summary:')
        print(f'  Total entities: {row.total_entities}')
        print(f'  Zero-dollar transfers: {row.zero_dollar_transfers}')
        print(f'  Shell factory pattern: {row.shell_factory_pattern}')
        print(f'  Lender fraud flagged: {row.lender_fraud_flagged}')
        print(f'  Total PPP: ${row.total_ppp:,.0f}')
except Exception as e:
    print(f'Error: {e}')
