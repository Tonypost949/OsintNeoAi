SELECT
  transaction_id,
  organization_name,
  fund_delta,
  ingestion_ts
FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions`
WHERE organization_name LIKE '%Viet America%' OR organization_name LIKE '%VAS%'
ORDER BY ingestion_ts DESC
LIMIT 100;
