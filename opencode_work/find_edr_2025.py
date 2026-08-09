"""Find 2025 EDR reports — independent third-party environmental data"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
import glob

c = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 60)
print("2025+ EDR / ENVIRONMENTAL FILES IN GOOGLE DRIVE (BQ Index)")
print("=" * 60)

q = f"""
SELECT file_name, mime_type, CAST(size_bytes AS INT64)/1048576 AS size_mb, 
       created_time, modified_time, owner_names
FROM `{PRJ}.national_audits.drive_file_index`
WHERE (LOWER(file_name) LIKE '%edr%' 
   OR LOWER(file_name) LIKE '%environmental data%' 
   OR LOWER(file_name) LIKE '%radius%map%' 
   OR LOWER(file_name) LIKE '%phase%i%esa%'
   OR LOWER(file_name) LIKE '%sanborn%'
   OR LOWER(file_name) LIKE '%t10000018579%'
   OR LOWER(file_name) LIKE '%17642%'
   OR LOWER(file_name) LIKE '%17631%'
   OR LOWER(file_name) LIKE '%navigation center%'
   OR LOWER(file_name) LIKE '%hbnc%')
  AND EXTRACT(YEAR FROM created_time) >= 2025
ORDER BY created_time DESC LIMIT 30
"""
for r in c.query(q).result():
    sz = r.get("size_mb") or 0
    fn = str(r.get("file_name", ""))[:80]
    ct = r.get("created_time", "?")
    owner = str(r.get("owner_names", "?"))[:40]
    mod = r.get("modified_time", "?")
    print(f"  [{sz:.1f}MB] {fn}")
    print(f"    Created: {ct} | Modified: {mod} | Owner: {owner}")

# Also scan G: drive
print()
print("=" * 60)
print("G: DRIVE — EDR / ESA REPORTS (direct filesystem)")
print("=" * 60)
for d in [r"G:\DL BACKUP", r"G:\buckp moto\Download", r"G:\.gemini\antigravity-ide\scratch\truthfinder_pdfs"]:
    for fp in glob.glob(os.path.join(d, "**", "*"), recursive=True):
        fn = os.path.basename(fp).lower()
        if any(kw in fn for kw in ['edr','environmental data','radius map','geocheck','phase i esa',
                                     'database report','sanborn','historical aerial','t10000018579',
                                     'environmental site assessment']):
            sz = os.path.getsize(fp) / 1e6
            mt = os.path.getmtime(fp)
            from datetime import datetime
            dt = datetime.fromtimestamp(mt).strftime('%Y-%m-%d')
            print(f"  [{sz:.1f}MB] {os.path.basename(fp)[:80]}")
            print(f"    Modified: {dt} | Path: {fp[:120]}")
