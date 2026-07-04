-- address_cluster_monitor.sql
-- Runs against BigQuery npi_forensic schema to monitor new out-of-state entities registering to OC hubs

WITH known_oc_hubs AS (
  SELECT '11770 WARNER AVE STE 215' AS hub_address, 'FOUNTAIN VALLEY' AS hub_name, 5270 AS known_parcels
  UNION ALL SELECT '3187 RED HILL AVE STE 213', 'COSTA MESA', 3572
  UNION ALL SELECT '220 NEWPORT CENTER DR', 'NEWPORT BEACH', 3249
),
new_registrations AS (
  SELECT
    e.entity_id,
    e.name AS entity_name,
    e.jurisdiction,
    p.name AS registered_agent,
    p.person_id,
    r.role,
    r.ingestion_timestamp AS discovered_at
  FROM `hardy-order-496117-p3.npi_forensic.edges_officer_of` r
  JOIN `hardy-order-496117-p3.npi_forensic.nodes_person` p ON r.person_id = p.person_id
  JOIN `hardy-order-496117-p3.npi_forensic.entities` e ON r.entity_id = e.entity_id
  WHERE r.ingestion_timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
)
SELECT
  h.hub_name,
  h.hub_address,
  h.known_parcels,
  n.entity_name,
  n.jurisdiction,
  n.registered_agent,
  n.discovered_at,
  -- Flag if this entity is from an out-of-state jurisdiction registering to OC hub
  CASE WHEN n.jurisdiction NOT IN ('CA', 'California') THEN 'OUT-OF-STATE_FUNNEL' ELSE 'LOCAL' END AS funnel_type
FROM new_registrations n
JOIN known_oc_hubs h
  ON LOWER(n.registered_agent) LIKE CONCAT('%', LOWER(REPLACE(h.hub_address, ' ', '%')), '%')
   OR LOWER(n.entity_name) LIKE CONCAT('%', LOWER(REPLACE(h.hub_address, ' ', '%')), '%')
ORDER BY n.discovered_at DESC;
