from google.cloud import bigquery
import csv

# Load lender fraud pattern into bridge table
client = bigquery.Client(project='noble-beanbag-497411-m4')

# First, let's create a lender fraud table
lender_fraud_query = """
CREATE OR REPLACE TABLE `noble-beanbag-497411-m4.forensic_layers.lender_fraud_pattern` AS
SELECT 
  ServicingLenderName,
  COUNT(*) as total_loans,
  COUNTIF(ForgivenessAmount > CurrentApprovalAmount) as over_forgiven_count,
  ROUND(COUNTIF(ForgivenessAmount > CurrentApprovalAmount) / COUNT(*) * 100, 2) as over_forgiveness_rate,
  SUM(CurrentApprovalAmount) as total_approved,
  SUM(ForgivenessAmount) as total_forgiven,
  SUM(ForgivenessAmount - CurrentApprovalAmount) as total_over_forgiven
FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
WHERE ServicingLenderName LIKE '%Harvest Small Business Finance%'
   OR ServicingLenderName LIKE '%Mega Bank%'
GROUP BY ServicingLenderName
"""

try:
    client.query(lender_fraud_query).result()
    print("Created lender_fraud_pattern table")
except Exception as e:
    print(f"Error creating table: {e}")

# Now load the 88 Fair Dr shell factory entities
shell_factory_query = """
INSERT INTO `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
SELECT 
  Owner1 as entity_name,
  SiteAddress as property_address,
  NULL as property_city,
  NULL as property_apn,
  MailAddress as property_mail_address,
  MailCity as property_mail_city,
  NULL as property_acquisition_date,
  NULL as property_acquisition_value,
  ppp_loan_count,
  ppp_total_amount,
  ppp_total_forgiven,
  ppp_states,
  ppp_naics_codes,
  ppp_lenders,
  ppp_borrower_address,
  ppp_borrower_city,
  ppp_borrower_state,
  is_multi_state_ppp,
  is_naics_mismatch,
  is_post_ppp_property_acquisition,
  is_mailbox_address,
  is_zero_dollar_transfer
FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` llc
JOIN `noble-beanbag-497411-m4.ppp_rico.rico_matches` match
  ON llc.Owner1 = match.BorrowerName
WHERE llc.SiteAddress LIKE '%88 FAIR DR%'
"""

try:
    client.query(shell_factory_query).result()
    print("Loaded 88 Fair Dr shell factory entities")
except Exception as e:
    print(f"Error loading shell factory: {e}")

# Get summary stats
summary_query = """
SELECT 
  COUNT(*) as total_entities,
  COUNTIF(is_lender_fraud_flag = TRUE) as lender_fraud_entities,
  SUM(ppp_total_amount) as total_ppp_amount,
  SUM(ppp_total_forgiven) as total_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
"""

try:
    results = client.query(summary_query).result()
    for row in results:
        print(f"\nBridge table summary:")
        print(f"  Total entities: {row.total_entities}")
        print(f"  Lender fraud flagged: {row.lender_fraud_entities}")
        print(f"  Total PPP: ${row.total_ppp_amount:,.0f}")
        print(f"  Total forgiven: ${row.total_forgiven:,.0f}")
except Exception as e:
    print(f"Error getting summary: {e}")
