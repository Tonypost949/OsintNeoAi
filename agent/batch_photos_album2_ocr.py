"""
batch_photos_album2_ocr.py — Multimodal OCR and evidence extraction for Google Photos Album #2 (300 items).
"""
import os
import sys
import json
import time
import re
import requests
import google.generativeai as genai

MANIFEST_PATH = "data/google_photos_album2_manifest.json"
OUTPUT_PATH = "data/google_photos_album2_ocr.json"

FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.1-pro-preview"
]

def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[-] Manifest not found at {MANIFEST_PATH}")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY environment variable not found.")
        return

    genai.configure(api_key=api_key)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Load existing results
    results = {}
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
                results = {item["id"]: item for item in existing}
        except Exception:
            results = {}

    print(f"[*] Total items in Album #2 manifest: {len(manifest)}")
    print(f"[*] Already indexed items: {len(results)}")

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(manifest)
    processed_count = 0

    for item in manifest:
        item_id = item["id"]
        idx = item["index"]

        if item_id in results:
            continue

        if processed_count >= limit:
            print(f"[*] Reached batch target of {limit} items.")
            break

        img_url = item["image_url"] + "=w1600"
        print(f"\n[{idx}/{len(manifest)}] Fetching item ID {item_id[:12]}...")

        try:
            resp = requests.get(img_url, timeout=25)
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

            success = False
            for model_name in FALLBACK_MODELS:
                try:
                    model = genai.GenerativeModel(model_name)
                    ai_resp = model.generate_content([
                        {"mime_type": "image/jpeg", "data": img_bytes},
                        prompt
                    ])
                    analysis_text = getattr(ai_resp, 'text', '')
                    if not analysis_text and hasattr(ai_resp, 'candidates') and ai_resp.candidates:
                        c = ai_resp.candidates[0]
                        if hasattr(c, 'content') and hasattr(c.content, 'parts'):
                            analysis_text = "".join([p.text for p in c.content.parts if hasattr(p, 'text')])

                    if not analysis_text:
                        print(f"[~] Empty text returned by {model_name}, trying next model...")
                        continue

                    print(f"[+] Analyzed item {idx} with {model_name}:")
                    print(analysis_text[:280] + "...\n")

                    record = {
                        "index": idx,
                        "id": item_id,
                        "image_url": item["image_url"],
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "timestamp": item.get("timestamp"),
                        "analysis": analysis_text,
                        "model_used": model_name,
                        "processed_at": time.time()
                    }

                    results[item_id] = record
                    processed_count += 1
                    success = True

                    # Save incrementally
                    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                        json.dump(list(results.values()), f, indent=2)

                    time.sleep(2)
                    break

                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "Quota" in err_str:
                        delay_match = re.search(r'retry in ([0-9.]+)s', err_str)
                        wait_sec = float(delay_match.group(1)) if delay_match else 15.0
                        print(f"[~] Rate limit on {model_name}. Pausing {wait_sec:.1f}s...")
                        time.sleep(min(wait_sec, 20.0))
                    else:
                        print(f"[-] Model {model_name} error: {e}")

            if not success:
                print(f"[-] Could not process item {idx} across models. Skipping/pausing 5s...")
                time.sleep(5)

        except Exception as e:
            print(f"[-] Error processing item {idx}: {e}")
            time.sleep(3)

    print(f"\n[+] Batch complete. Total indexed items in Album #2: {len(results)} saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
