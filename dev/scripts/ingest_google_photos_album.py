#!/usr/bin/env python3
"""
scripts/ingest_google_photos_album.py
=====================================
Multi-album Google Photos ingestion engine for OsintNeoAi.
Extracts photo URLs, calculates SHA-256 signatures, and generates
structured evidence manifests for BigQuery, Dataverse, and local neural OCR.

Supported Albums:
1. https://photos.app.goo.gl/9xCvzdihZ64RxH4y7 (Album 1 - 72 assets)
2. https://photos.app.goo.gl/exYCpbrYKtfu9V6E7 (Album 2 - 202 assets)
"""

import os
import re
import json
import hashlib
import urllib.request
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence", "google_photos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_ALBUMS = [
    {
        "album_id": "9xCvzdihZ64RxH4y7",
        "album_name": "Evidence Vault 1",
        "url": "https://photos.app.goo.gl/9xCvzdihZ64RxH4y7",
        "prefix": "PHOTO-A1"
    },
    {
        "album_id": "exYCpbrYKtfu9V6E7",
        "album_name": "Evidence Vault 2",
        "url": "https://photos.app.goo.gl/exYCpbrYKtfu9V6E7",
        "prefix": "PHOTO-A2"
    }
]

def ingest_all_albums():
    master_inventory = []

    for album in TARGET_ALBUMS:
        print(f"--> Fetching {album['album_name']} from {album['url']}...")
        req = urllib.request.Request(album['url'], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        raw_urls = re.findall(r'https:\/\/lh3\.googleusercontent\.com\/pw\/[a-zA-Z0-9_-]+', html)
        unique_urls = list(dict.fromkeys(raw_urls))
        print(f"✓ Found {len(unique_urls)} unique photo assets in {album['album_name']}.")

        photo_records = []
        for idx, url in enumerate(unique_urls, 1):
            url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
            record = {
                "album_id": album["album_id"],
                "asset_index": idx,
                "exhibit_id": f"{album['prefix']}-{idx:04d}",
                "source_album": album["url"],
                "image_url": f"{url}=w1920-h1080",
                "thumbnail_url": f"{url}=w400-h300",
                "sha256_url_hash": url_hash,
                "status": "Indexed / Ready for OCR",
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
            photo_records.append(record)
            master_inventory.append(record)

        manifest = {
            "album_id": album["album_id"],
            "album_name": album["album_name"],
            "album_share_url": album["url"],
            "total_assets": len(photo_records),
            "indexed_timestamp": datetime.now(timezone.utc).isoformat(),
            "photos": photo_records
        }

        manifest_path = os.path.join(OUTPUT_DIR, f"shared_album_{album['album_id']}.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"✓ Wrote {manifest_path}")

    # Write Master Consolidated Index
    master_path = os.path.join(OUTPUT_DIR, "master_google_photos_index.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_albums": len(TARGET_ALBUMS),
            "total_photo_assets": len(master_inventory),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "albums": [a["album_id"] for a in TARGET_ALBUMS],
            "inventory": master_inventory
        }, f, indent=2)
    
    print(f"\n=======================================================")
    print(f"✓ Master Photo Index compiled: {len(master_inventory)} total photos across {len(TARGET_ALBUMS)} albums.")
    print(f"✓ Output file: {master_path}")
    print(f"=======================================================")

if __name__ == "__main__":
    ingest_all_albums()
