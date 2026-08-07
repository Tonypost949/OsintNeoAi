from google.cloud import bigquery
import sys

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
PROJECT = "project-743aab84-f9a5-4ec7-954"

print("=== Bridge Table Summary ===")
summary = bq.query(f"""
SELECT
  COUNT(*) AS total_entities,
  COUNTIF(ppp_loan_count > 0) AS entities_with_ppp,
  COUNTIF(is_multi_state_ppp) AS multi_state_ppp,
  COUNTIF(is_mailbox_address) AS mailbox_addresses,
  COUNTIF(is_zero_dollar_transfer) AS zero_dollar_transfers,
  COUNTIF(is_post_ppp_property_acquisition) AS post_ppp_acquisitions,
  ROUND(SUM(ppp_total_amount), 2) AS total_ppp_dollars,
  ROUND(SUM(ppp_total_forgiven), 2) AS total_ppp_forgiven
FROM `{PROJECT}.ppp_rico.hb_ppp_bridge`
""").to_dataframe()
print(summary.to_string(index=False))

print("\n=== Top 20 Suspects by PPP Amount ===")
top = bq.query(f"""
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
FROM `{PROJECT}.ppp_rico.hb_ppp_bridge`
WHERE ppp_total_amount IS NOT NULL
ORDER BY ppp_total_amount DESC
LIMIT 20
""").to_dataframe()
print(top.to_string(index=False))
