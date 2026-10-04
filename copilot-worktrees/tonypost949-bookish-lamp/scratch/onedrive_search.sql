SELECT
  file_name,
  content_preview
FROM `project-743aab84-f9a5-4ec7-954.onedrive_forensics.onedrive_documents`
WHERE content_preview LIKE '%Southbrook%' OR file_name LIKE '%Southbrook%'
LIMIT 10;
