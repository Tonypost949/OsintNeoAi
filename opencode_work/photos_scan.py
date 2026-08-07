"""Google Photos: Nov/Dec mapping evidence"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
c = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("GOOGLE PHOTOS — LAST 100")
q = f"SELECT filename, creation_time FROM `{PRJ}.national_audits.google_photos_index` ORDER BY creation_time DESC LIMIT 100"
for r in c.query(q).result():
    print(f"  [{r['creation_time']}] {r['filename'][:70]}")

print()
print("DRIVE PHOTOS WITH GPS COORDINATES")
q2 = f"SELECT file_name, datetime_original, latitude, longitude FROM `{PRJ}.national_audits.drive_photos_exif` WHERE latitude IS NOT NULL AND latitude != 0 ORDER BY datetime_original DESC LIMIT 50"
for r in c.query(q2).result():
    print(f"  [{r['datetime_original']}] ({r['latitude']:.4f},{r['longitude']:.4f}) {r['file_name'][:60]}")

print()
print("PHOTOS BY MONTH (2025-2026)")
q3 = f"SELECT FORMAT_TIMESTAMP('%Y-%m', creation_time) AS month, COUNT(*) AS cnt FROM `{PRJ}.national_audits.google_photos_index` WHERE creation_time >= '2025-01-01' GROUP BY month ORDER BY month"
for r in c.query(q3).result():
    print(f"  {r['month']}: {r['cnt']} photos")
