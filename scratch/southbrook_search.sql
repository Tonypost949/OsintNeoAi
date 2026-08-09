SELECT
  *
FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.fca_timeline`
WHERE snippet LIKE '%Southbrook%' OR subject LIKE '%Southbrook%'
ORDER BY event_date DESC;
