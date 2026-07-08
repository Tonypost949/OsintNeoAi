"""Systematic Drive extraction: unzip all archives, find all content types"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 60)
print("ALL ZIP ARCHIVES IN GOOGLE DRIVE")
print("=" * 60)
q = f"""
SELECT file_name, CAST(size_bytes AS INT64)/1048576 AS size_mb, created_time, owner_names, web_view_link
FROM `{PRJ}.national_audits.drive_file_index`
WHERE (LOWER(file_name) LIKE '%.zip' OR LOWER(file_name) LIKE '%.7z' OR LOWER(file_name) LIKE '%.tar%' OR LOWER(file_name) LIKE '%.gz')
  AND size_bytes > 100000
ORDER BY size_bytes DESC
"""
for r in c.query(q).result():
    sz = r.get("size_mb") or 0
    print(f"  [{sz:.1f}MB] {r['file_name'][:85]}")
    print(f"    Created: {r['created_time']} | Owner: {str(r.get('owner_names','?'))[:35]}")
    print(f"    Link: {r.get('web_view_link','')}")
    print()

print("=" * 60)
print("GOOGLE DOCS (Docs, Sheets, Slides) IN DRIVE")
print("=" * 60)
q2 = f"""
SELECT file_name, mime_type, created_time, owner_names, web_view_link
FROM `{PRJ}.national_audits.drive_file_index`
WHERE mime_type LIKE 'application/vnd.google-apps.%'
  AND size_bytes < 5000000
ORDER BY created_time DESC LIMIT 30
"""
for r in c.query(q2).result():
    mt = str(r.get("mime_type","")).replace("application/vnd.google-apps.","")
    print(f"  [{mt}] {r['file_name'][:70]}")
    print(f"    Created: {r['created_time']} | Link: {r.get('web_view_link','')[:100]}")

print()
print("=" * 60)
print("FILE TYPE BREAKDOWN")
print("=" * 60)
q3 = f"""
SELECT 
  CASE 
    WHEN mime_type LIKE 'image/%' THEN 'images'
    WHEN mime_type = 'application/pdf' THEN 'pdfs'
    WHEN mime_type LIKE 'application/vnd.google-apps.%' THEN 'google_docs'
    WHEN mime_type LIKE 'application/zip%' OR mime_type LIKE 'application/x-zip%' THEN 'archives'
    WHEN mime_type LIKE 'video/%' THEN 'videos'
    WHEN mime_type LIKE 'text/%' THEN 'text'
    ELSE 'other'
  END AS category,
  COUNT(*) AS count,
  SUM(size_bytes)/1073741824 AS total_gb
FROM `{PRJ}.national_audits.drive_file_index`
GROUP BY category
ORDER BY total_gb DESC
"""
for r in c.query(q3).result():
    gb = r.get("total_gb") or 0
    print(f"  {r['category']:15s}: {r['count']:>8,} files, {gb:>8.1f} GB")
