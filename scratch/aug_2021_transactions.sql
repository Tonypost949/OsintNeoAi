SELECT
  transaction_id,
  organization_name,
  fund_delta,
  ingestion_ts
FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.fact_transactions`
WHERE ingestion_ts BETWEEN '2021-08-01' AND '2021-09-01'
ORDER BY ingestion_ts ASC;
