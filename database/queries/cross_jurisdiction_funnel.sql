-- cross_jurisdiction_funnel.sql
-- Runs against BigQuery npi_forensic schema to track out-of-state entities funneling back to local OC hubs

SELECT
  e.jurisdiction AS source_jurisdiction,
  p.name AS controlling_person,
  p.person_id,
  COUNT(DISTINCT e.entity_id) AS entities_controlled,
  ARRAY_AGG(DISTINCT e.name) AS entity_names,
  -- Link back to OC hub if known
  MAX(CASE
    WHEN LOWER(e.name) LIKE '%11770 warner%' THEN 'FOUNTAIN VALLEY HUB'
    WHEN LOWER(e.name) LIKE '%3187 red hill%' THEN 'COSTA MESA HUB'
    WHEN LOWER(e.name) LIKE '%220 newport center%' THEN 'NEWPORT BEACH HUB'
    ELSE 'UNKNOWN_HUB'
  END) AS oc_hub_link
FROM `hardy-order-496117-p3.npi_forensic.edges_officer_of` r
JOIN `hardy-order-496117-p3.npi_forensic.nodes_person` p ON r.person_id = p.person_id
JOIN `hardy-order-496117-p3.npi_forensic.entities` e ON r.entity_id = e.entity_id
WHERE e.jurisdiction != 'CA'
GROUP BY e.jurisdiction, p.name, p.person_id
HAVING COUNT(DISTINCT e.entity_id) >= 2
ORDER BY entities_controlled DESC;
