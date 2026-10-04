SELECT
  org_id,
  org_name
FROM `project-743aab84-f9a5-4ec7-954.fraud_mart.dim_organization`
WHERE org_name LIKE '%Viet America%' OR org_name LIKE '%VAS%'
LIMIT 50;
