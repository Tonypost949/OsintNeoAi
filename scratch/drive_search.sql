SELECT
  file_name,
  web_view_link,
  created_time
FROM `project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index`
WHERE file_name LIKE '%2021-08-20%' OR file_name LIKE '%Kinetic%' OR file_name LIKE '%VAS%'
LIMIT 100;
