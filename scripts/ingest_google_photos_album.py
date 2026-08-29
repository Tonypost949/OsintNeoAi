#!/usr/bin/env python3
"""
scripts/ingest_google_photos_album.py
=====================================
Fetches and indexes photos from shared Google Photos album:
https://photos.app.goo.gl/9xCvzdihZ64RxH4y7

Extracts photo URLs, calculates SHA-256 signatures, and generates
a structured evidence index for BigQuery and Dataverse.
"""

import os
import re
import json
import hashlib
import urllib.request
from datetime import datetime, timezone

ALBUM_URL = "https://photos.app.goo.gl/9xCvzdihZ64RxH4y7"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence", "google_photos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ingest_album():
    print(f"--> Fetching Google Photos album from {ALBUM_URL}...")
    req = urllib.request.Request(ALBUM_URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    
    # Extract unique Google Photos high-res image endpoints
    raw_urls = re.findall(r'https:\/\/lh3\.googleusercontent\.com\/pw\/[a-zA-Z0-9_-]+', html)
    unique_urls = list(dict.fromkeys(raw_urls))
    
    print(f"✓ Extracted {len(unique_urls)} unique photo assets.")

    photo_records = []
    for idx, url in enumerate(unique_urls, 1):
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
        photo_records.append({
            "asset_index": idx,
            "exhibit_id": f"PHOTO-EX-{idx:04d}",
            "source_album": ALBUM_URL,
            "image_url": f"{url}=w1920-h1080",
            "thumbnail_url": f"{url}=w400-h300",
            "sha256_url_hash": url_hash,
            "status": "Indexed / Ready for OCR",
            "indexed_at": datetime.now(timezone.utc).isoformat()
        })

    manifest = {
        "album_title": "OsintNeoAi Shared Photographic Evidence Vault",
        "album_share_url": ALBUM_URL,
        "total_assets": len(photo_records),
        "indexed_timestamp": datetime.now(timezone.utc).isoformat(),
        "photos": photo_records
    }

    manifest_path = os.path.join(OUTPUT_DIR, "shared_album_9xCvzdihZ64RxH4y7.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Successfully wrote photo evidence manifest ({len(photo_records)} items) to: {manifest_path}")
    return manifest

if __name__ == "__main__":
    ingest_album()
