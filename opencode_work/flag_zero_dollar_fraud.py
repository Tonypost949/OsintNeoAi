from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Flag zero-dollar transfer LLCs with PPP loans
query = """
UPDATE `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
SET is_lender_fraud_flag = TRUE
WHERE is_zero_dollar_transfer = TRUE
  AND entity_name IN (
    'PACIFIC CITY HOTEL LLC',
    'STEWART INDUSTRIES LLC',
    'NEWPORT LLC',
    'DRT LLC',
    'LIGHTHOUSE CAFE LLC',
    'INCUPLACE LLC',
    'RAV LLC',
    'THE LE FAMILY LLC',
    'FIRST HIGHLAND LLC'
  )
"""

try:
    job = client.query(query)
    job.result()
    print(f'Flagged {job.num_dml_affected_rows} zero-dollar PPP fraud entities')
except Exception as e:
    print(f'Error: {e}')

# Get updated summary
summary_query = """
SELECT 
  COUNT(*) as total_entities,
  COUNTIF(is_zero_dollar_transfer = TRUE) as zero_dollar_transfers,
  COUNTIF(is_lender_fraud_flag = TRUE) as lender_fraud_flagged,
  SUM(ppp_total_amount) as total_ppp,
  SUM(ppp_total_forgiven) as total_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
"""

try:
    results = client.query(summary_query).result()
    for row in results:
        print(f'\nBridge table summary:')
        print(f'  Total entities: {row.total_entities}')
        print(f'  Zero-dollar transfers: {row.zero_dollar_transfers}')
        print(f'  Lender fraud flagged: {row.lender_fraud_flagged}')
        print(f'  Total PPP: ${row.total_ppp:,.0f}')
        print(f'  Total forgiven: ${row.total_forgiven:,.0f}')
except Exception as e:
    print(f'Error: {e}')
