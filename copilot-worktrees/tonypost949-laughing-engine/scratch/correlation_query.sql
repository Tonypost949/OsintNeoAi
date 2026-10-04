SELECT
  event_date,
  sender,
  recipient,
  subject,
  snippet,
  signal_type
FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.fca_timeline`
WHERE event_date BETWEEN '2021-08-19' AND '2021-08-22'
ORDER BY event_date ASC;
