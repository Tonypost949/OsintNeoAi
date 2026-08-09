import json, urllib.request, configparser, datetime
from google.cloud import bigquery

config = configparser.ConfigParser()
config.read(r"C:\Users\HP\AppData\Roaming\rclone\rclone.conf")
token_data = json.loads(config.get("gphotos", "token"))
access_token = token_data["access_token"]

PROJECT = "project-743aab84-f9a5-4ec7-954"
TABLE = f"{PROJECT}.national_audits.google_photos_index"
client = bigquery.Client(project=PROJECT)

# First check albums
url = "https://photoslibrary.googleapis.com/v1/albums?pageSize=50"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
albums = data.get("albums", [])
print(f"Albums found: {len(albums)}")
for a in albums:
    print(f"  {a.get('title')} - {a.get('mediaItemsCount', 0)} items")

# Now try mediaItems
total_loaded = 0
page_token = None
page_count = 0

while True:
    if page_token:
        full_url = f"https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=100&pageToken={page_token}"
    else:
        full_url = "https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=100"

    req = urllib.request.Request(full_url, headers={"Authorization": f"Bearer {access_token}"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())

    items = data.get("mediaItems", [])
    page_count += 1

    if items:
        rows = []
        for item in items:
            meta = item.get("mediaMetadata", {})
            photo_meta = meta.get("photo", {})
            rows.append({
                "photo_id": item.get("id", ""),
                "filename": item.get("filename", ""),
                "mime_type": item.get("mimeType", ""),
                "creation_time": meta.get("creationTime", ""),
                "camera_make": photo_meta.get("cameraMake", ""),
                "camera_model": photo_meta.get("cameraModel", ""),
                "focal_length": str(photo_meta.get("focalLength", "")),
                "aperture": str(photo_meta.get("apertureFNumber", "")),
                "iso_equivalent": str(photo_meta.get("isoEquivalent", "")),
                "ingest_timestamp": datetime.datetime.utcnow().isoformat(),
            })

        errors = client.insert_rows_json(TABLE, rows)
        loaded = len(rows) if not errors else len(rows) - len(errors)
        total_loaded += loaded
        print(f"Page {page_count}: loaded {loaded} (total: {total_loaded})")
    else:
        print(f"Page {page_count}: 0 items")

    page_token = data.get("nextPageToken")
    if not page_token:
        break

    if page_count > 500:
        print("Safety limit reached")
        break

print(f"\nDONE. Total photos loaded: {total_loaded}")
