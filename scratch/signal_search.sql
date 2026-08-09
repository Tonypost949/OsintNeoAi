SELECT
  *
FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.fca_timeline`
WHERE snippet LIKE '%04:12%' OR subject LIKE '%04:12%' OR snippet LIKE '%Kinetic Signal%'
ORDER BY event_date DESC;
