"""Pull EDR report Drive links — direct access"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

q = f"""
SELECT file_name, 
       CAST(size_bytes AS INT64)/1048576 AS size_mb, 
       created_time, owner_names, web_view_link,
       mime_type, modified_time
FROM `{PRJ}.national_audits.drive_file_index`
WHERE (
    LOWER(file_name) LIKE '%attachment_11%phase%esa%' 
    OR LOWER(file_name) LIKE '%attachment_11%esa%'
    OR LOWER(file_name) LIKE '%nuclearshelterphase%'
    OR (LOWER(file_name) LIKE '%phase%i%environmental%site%assessment%' 
        AND size_bytes > 30000000 
        AND EXTRACT(YEAR FROM created_time) = 2025)
    OR LOWER(file_name) = 'T10000018579.20200318.Phase I Environmental Site Assessment.pdf'
    OR LOWER(file_name) = 'T10000018579.20200318.Phase I Environmental Site Assessment (1).pdf'
)
ORDER BY created_time ASC
"""
print("=" * 60)
print("EDR / PHASE I ESA REPORTS — DIRECT GOOGLE DRIVE LINKS")
print("=" * 60)
for r in c.query(q).result():
    sz = r.get("size_mb") or 0
    fn = r["file_name"]
    ct = r.get("created_time", "?")
    owner = str(r.get("owner_names", "?"))[:50]
    link = r.get("web_view_link", "N/A")
    print(f"\n[{sz:.1f}MB] {fn[:85]}")
    print(f"  Created: {ct}")
    print(f"  Owner:   {owner}")
    print(f"  Link:    {link}")
