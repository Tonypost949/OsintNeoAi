from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Add lender fraud flag to bridge table
alter_query = """
ALTER TABLE `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
ADD COLUMN is_lender_fraud_flag BOOL
"""

try:
    client.query(alter_query).result()
    print('Added is_lender_fraud_flag column')
except Exception as e:
    if 'already exists' in str(e).lower():
        print('Column already exists')
    else:
        print(f'Error adding column: {e}')

# Flag entities with Harvest/Mega Bank loans
update_query = """
UPDATE `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
SET is_lender_fraud_flag = TRUE
WHERE entity_name IN (
  SELECT DISTINCT llc.Owner1
  FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` llc
  JOIN `noble-beanbag-497411-m4.ppp_rico.rico_matches` match
    ON llc.Owner1 = match.llc_name
  JOIN `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus` ppp
    ON match.llc_name = ppp.BorrowerName
  WHERE ppp.ServicingLenderName LIKE '%Harvest Small Business Finance%'
     OR ppp.ServicingLenderName LIKE '%Mega Bank%'
)
"""

try:
    job = client.query(update_query)
    job.result()
    print(f'Flagged {job.num_dml_affected_rows} entities with lender fraud')
except Exception as e:
    print(f'Error updating: {e}')

# Get lender fraud summary
summary_query = """
SELECT 
  COUNTIF(is_lender_fraud_flag = TRUE) as lender_fraud_entities,
  SUM(CASE WHEN is_lender_fraud_flag = TRUE THEN ppp_total_amount ELSE 0 END) as lender_fraud_ppp,
  SUM(CASE WHEN is_lender_fraud_flag = TRUE THEN ppp_total_forgiven ELSE 0 END) as lender_fraud_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
"""

try:
    results = client.query(summary_query).result()
    for row in results:
        print(f'\nLender fraud summary:')
        print(f'  Entities flagged: {row.lender_fraud_entities}')
        print(f'  PPP amount: ${row.lender_fraud_ppp:,.0f}')
        print(f'  Forgiven: ${row.lender_fraud_forgiven:,.0f}')
except Exception as e:
    print(f'Error: {e}')
