"""
batch_photos_evidence_ocr.py — Batch multimodal OCR & evidence extraction for Google Photos shared album.
Saves structured findings to data/google_photos_evidence_ocr.json.
"""
import os
import sys
import json
import time
import requests
import google.generativeai as genai

MANIFEST_PATH = "data/google_photos_evidence_manifest.json"
OUTPUT_PATH = "data/google_photos_evidence_ocr.json"

def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[-] Manifest not found at {MANIFEST_PATH}")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY environment variable not found.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Load existing results if any
    results = {}
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
                results = {item["id"]: item for item in existing}
        except Exception:
            results = {}

    print(f"[*] Total items in manifest: {len(manifest)}")
    print(f"[*] Already processed items: {len(results)}")

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(manifest)
    processed_this_run = 0

    for item in manifest:
        item_id = item["id"]
        idx = item["index"]

        if item_id in results:
            continue

        if processed_this_run >= limit:
            print(f"[*] Reached limit of {limit} items for this run.")
            break

        img_url = item["image_url"] + "=w1600"
        print(f"\n[{idx}/{len(manifest)}] Fetching item ID {item_id[:12]}...")

        try:
            resp = requests.get(img_url, timeout=20)
            if resp.status_code != 200:
                print(f"[-] Failed to fetch image (status {resp.status_code})")
                continue

            img_bytes = resp.content

            prompt = """Analyze this image with high forensic accuracy:
1. Category: (e.g., Legal Pleading, Court Docket, Police Report, Medical Record, Email/Text Screenshot, Financial Document, Physical Photo/Scene, Map/GIS)
2. Document Title / Form Type:
3. Case / Record / Tracking Number:
4. Court / Agency / Jurisdiction:
5. Named Entities (Persons, Organizations, Judges, Attorneys, Victims, Perpetrators):
6. Dates / Timestamps:
7. Key Evidence Transcript & Factual Summary: (Transcribe all critical text and bullet-point key factual assertions/findings).

Be thorough, precise, and objective."""

            ai_resp = model.generate_content([
                {"mime_type": "image/jpeg", "data": img_bytes},
                prompt
            ])

            analysis_text = ai_resp.text
            print(f"[+] Analyzed item {idx}:")
            print(analysis_text[:350] + "...\n")

            record = {
                "index": idx,
                "id": item_id,
                "image_url": item["image_url"],
                "width": item.get("width"),
                "height": item.get("height"),
                "timestamp": item.get("timestamp"),
                "analysis": analysis_text,
                "processed_at": time.time()
            }

            results[item_id] = record
            processed_this_run += 1

            # Save incrementally after each item
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(list(results.values()), f, indent=2)

            time.sleep(1) # Rate limit safety

        except Exception as e:
            print(f"[-] Error processing item {idx}: {e}")
            time.sleep(2)

    print(f"\n[+] Batch run complete. Total indexed items: {len(results)} saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
