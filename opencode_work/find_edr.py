"""Search for EDR reports across Drive and BQ"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()

print("=" * 60)
print("BQ DRIVE FILE INDEX — EDR / ESA REPORTS")
print("=" * 60)
q = """
SELECT file_name, mime_type, 
       CAST(size_bytes AS INT64) / 1048576 AS size_mb, 
       created_time, owner_names
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE LOWER(file_name) LIKE '%edr%' 
   OR LOWER(file_name) LIKE '%environmental data resources%'
   OR LOWER(file_name) LIKE '%phase%esa%'
   OR LOWER(file_name) LIKE '%t10000018579%'
   OR LOWER(file_name) LIKE '%sanborn%'
ORDER BY size_bytes DESC LIMIT 20
"""
for r in c.query(q).result():
    sz = r.get("size_mb") or 0
    print(f"  [{sz:.1f}MB] {r['file_name'][:80]}")
    print(f"    Owner: {str(r.get('owner_names','?'))[:50]}  Created: {r.get('created_time','?')}")

print()
print("=" * 60)
print("G: DRIVE — LARGE ENVIRONMENTAL PDFs (10MB+)")
print("=" * 60)
import glob
for pattern in [
    r"G:\DL BACKUP\**\*ESA*.pdf",
    r"G:\DL BACKUP\**\*Phase*I*.pdf",
    r"G:\DL BACKUP\**\*Assessment*.pdf",
    r"G:\DL BACKUP\**\*Sanborn*.pdf",
    r"G:\buckp moto\Download\**\*Environmental*.pdf",
    r"G:\buckp moto\Download\**\*ESA*.pdf",
]:
    for fp in glob.glob(pattern, recursive=True):
        sz = os.path.getsize(fp) / 1e6
        if sz > 0.5:
            print(f"  [{sz:.1f}MB] {os.path.basename(fp)[:80]}")
            print(f"    Path: {fp[:120]}")
