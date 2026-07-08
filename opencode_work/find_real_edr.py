"""Find REAL EDR commercial reports (not government GeoTracker) — ordered 2025"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 60)
print("REAL EDR COMMERCIAL REPORTS IN DRIVE (2025)")
print("=" * 60)

# EDR products have specific naming: Radius Map, GeoCheck, Certified Sanborn,
# EDR Inquiry Number, EDR Site Report, etc.
q = f"""
SELECT file_name, mime_type, 
       CAST(size_bytes AS INT64)/1048576 AS size_mb, 
       created_time, modified_time, owner_names,
       web_view_link
FROM `{PRJ}.national_audits.drive_file_index`
WHERE (
    LOWER(file_name) LIKE '%radius%map%'
    OR LOWER(file_name) LIKE '%geocheck%'
    OR LOWER(file_name) LIKE '%certified%sanborn%'
    OR LOWER(file_name) LIKE '%edr%inquiry%'
    OR LOWER(file_name) LIKE '%edr%report%'
    OR LOWER(file_name) LIKE '%edr%site%'
    OR LOWER(file_name) LIKE '%historical%topographic%'
    OR LOWER(file_name) LIKE '%city%directory%abstract%'
    OR LOWER(file_name) LIKE '%aerial%photo%decade%'
    OR LOWER(file_name) LIKE '%environmental%lien%'
    OR LOWER(file_name) LIKE '%database%search%'
    OR (LOWER(file_name) LIKE '%edr%' AND LOWER(file_name) LIKE '%.pdf%')
    OR LOWER(file_name) LIKE '%phase%i%environmental%site%assessment%'
    OR (LOWER(file_name) LIKE '%%17642%' AND mime_type = 'application/pdf')
    OR (LOWER(file_name) LIKE '%%17631%' AND mime_type = 'application/pdf')
    OR (LOWER(file_name) LIKE '%%17472%' AND mime_type = 'application/pdf')
    OR LOWER(file_name) LIKE '%huntington beach%environmental%'
)
ORDER BY created_time DESC LIMIT 40
"""
for r in c.query(q).result():
    sz = r.get("size_mb") or 0
    fn = str(r.get("file_name", ""))[:90]
    ct = r.get("created_time", "?")
    owner = str(r.get("owner_names", "?"))[:35]
    print(f"  [{sz:.1f}MB] {fn}")
    print(f"    Drive Created: {ct} | Owner: {owner}")

# Also search specifically for files created in 2025 that are PDFs and large
print()
print("=" * 60)
print("LARGE PDFs CREATED IN 2025 (commercial reports)")
print("=" * 60)
q2 = f"""
SELECT file_name, mime_type, 
       CAST(size_bytes AS INT64)/1048576 AS size_mb, 
       created_time, owner_names
FROM `{PRJ}.national_audits.drive_file_index`
WHERE mime_type = 'application/pdf'
  AND size_bytes > 1000000  -- >1MB
  AND EXTRACT(YEAR FROM created_time) = 2025
  AND (LOWER(file_name) LIKE '%environmental%' 
    OR LOWER(file_name) LIKE '%phase%' 
    OR LOWER(file_name) LIKE '%esa%'
    OR LOWER(file_name) LIKE '%assessment%'
    OR LOWER(file_name) LIKE '%huntington%beach%'
    OR LOWER(file_name) LIKE '%beach%blvd%'
    OR LOWER(file_name) LIKE '%cameron%')
ORDER BY size_bytes DESC LIMIT 20
"""
for r in c.query(q2).result():
    sz = r.get("size_mb") or 0
    fn = str(r.get("file_name", ""))[:90]
    ct = r.get("created_time", "?")
    owner = str(r.get("owner_names", "?"))[:35]
    print(f"  [{sz:.1f}MB] {fn}")
    print(f"    Created: {ct} | Owner: {owner}")
