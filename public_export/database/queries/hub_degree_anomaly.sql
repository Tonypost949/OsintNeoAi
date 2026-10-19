-- hub_degree_anomaly.sql
-- Runs against BigQuery npi_forensic schema to flag when an agent's relationship degree centrality spikes

WITH person_degrees AS (
  SELECT
    person_id,
    name,
    COUNT(DISTINCT entity_id) AS controlled_entities,
    ARRAY_AGG(DISTINCT entity_id) AS entity_list
  FROM `hardy-order-496117-p3.npi_forensic.edges_officer_of`
  GROUP BY person_id, name
),
baseline AS (
  -- Historical average degree
  SELECT AVG(controlled_entities) AS avg_degree FROM person_degrees
)
SELECT
  pd.person_id,
  pd.name,
  pd.controlled_entities,
  pd.entity_list,
  b.avg_degree,
  pd.controlled_entities / NULLIF(b.avg_degree, 0) AS degree_ratio
FROM person_degrees pd
CROSS JOIN baseline b
WHERE pd.controlled_entities > b.avg_degree * 5  -- 5x baseline = anomaly
ORDER BY degree_ratio DESC;
