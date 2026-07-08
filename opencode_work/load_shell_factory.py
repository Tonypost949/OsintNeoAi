from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Load 88 Fair Dr shell factory entities - with proper DATE casting
query = """
INSERT INTO `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
SELECT 
  llc.Owner1 as entity_name,
  llc.SiteAddress as property_address,
  'Huntington Beach' as property_city,
  llc.APN as property_apn,
  llc.MailAddress as property_mail_address,
  llc.MailCity as property_mail_city,
  llc.LastSeller as last_seller,
  PARSE_DATE('%m/%d/%Y', llc.LastSaleDate) as property_acquisition_date,
  CAST(llc.LastSaleValue AS FLOAT64) as property_acquisition_value,
  CAST(match.ppp_loan_count AS INT64) as ppp_loan_count,
  CAST(match.ppp_total_amount AS FLOAT64) as ppp_total_amount,
  CAST(match.ppp_total_forgiven AS FLOAT64) as ppp_total_forgiven,
  [llc.SiteAddress] as ppp_business_addresses,
  [] as ppp_state_array,
  [] as ppp_naics_codes,
  [] as ppp_lenders,
  llc.SiteAddress as ppp_borrower_address,
  'Huntington Beach' as ppp_borrower_city,
  'CA' as ppp_borrower_state,
  FALSE as is_multi_state_ppp,
  TRUE as is_naics_mismatch,
  FALSE as is_post_ppp_property_acquisition,
  TRUE as is_mailbox_address,
  CASE WHEN CAST(llc.LastSaleValue AS FLOAT64) = 0 THEN TRUE ELSE FALSE END as is_zero_dollar_transfer
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` llc
JOIN `noble-beanbag-497411-m4.ppp_rico.rico_matches` match
  ON llc.Owner1 = match.llc_name
WHERE llc.SiteAddress LIKE '%88 FAIR DR%'
"""

try:
    client.query(query).result()
    print('Loaded 88 Fair Dr shell factory entities')
except Exception as e:
    print(f'Error: {e}')

# Get updated summary
summary_query = """
SELECT 
  COUNT(*) as total_entities,
  SUM(ppp_total_amount) as total_ppp_amount,
  SUM(ppp_total_forgiven) as total_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
"""

try:
    results = client.query(summary_query).result()
    for row in results:
        print(f'\nBridge table summary:')
        print(f'  Total entities: {row.total_entities}')
        print(f'  Total PPP: ${row.total_ppp_amount:,.0f}')
        print(f'  Total forgiven: ${row.total_forgiven:,.0f}')
except Exception as e:
    print(f'Error getting summary: {e}')
