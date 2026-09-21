import os
import sys
import time
import json
import glob
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
S3_DOWNLOAD_DIR = os.path.join(EVIDENCE_DIR, "s3_downloads")
MANIFEST_PATH = os.path.join(EVIDENCE_DIR, "ocgov_s3_all_attachments_manifest.json")
EXTRACTED_IDS_PATH = r"C:\OsintNeoAi\evidence\oc_procurement_portal\extracted_project_ids.json"

os.makedirs(S3_DOWNLOAD_DIR, exist_ok=True)

def collect_project_ids():
    project_ids = set()
    if os.path.exists(EXTRACTED_IDS_PATH):
        try:
            with open(EXTRACTED_IDS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for pid in data:
                    project_ids.add(str(pid))
        except Exception as e:
            print(f"Error reading {EXTRACTED_IDS_PATH}: {e}")

    # Ensure reference project 63874 is present
    project_ids.add("63874")
    return sorted(list(project_ids))

def batch_download_s3():
    project_ids = collect_project_ids()
    print(f"Loaded {len(project_ids)} target project IDs for S3 extraction.")

    manifest = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for idx, pid in enumerate(project_ids, 1):
            project_url = f"https://procurement.opengov.com/portal/ocgov/projects/{pid}"
            print(f"[{idx}/{len(project_ids)}] Processing Project ID {pid} -> {project_url}")

            project_record = {
                "project_id": pid,
                "project_url": project_url,
                "attachments": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            try:
                page.goto(project_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(3)

                download_buttons = page.query_selector_all("a[href*='downloads-project'], button:has-text('Download'), a:has-text('Download'), a[href*='s3.us-west-2.amazonaws.com']")
                print(f"  Found {len(download_buttons)} candidate attachment elements.")

                for b_idx, btn in enumerate(download_buttons, 1):
                    href = btn.get_attribute("href") or ""
                    try:
                        with page.expect_download(timeout=8000) as download_info:
                            btn.click()
                        download = download_info.value
                        filename = download.suggested_filename or f"project_{pid}_att_{b_idx}.pdf"
                        save_path = os.path.join(S3_DOWNLOAD_DIR, f"{pid}_{filename}")
                        download.save_as(save_path)
                        file_size = os.path.getsize(save_path)

                        att_info = {
                            "filename": f"{pid}_{filename}",
                            "local_path": save_path,
                            "s3_url": href,
                            "size_bytes": file_size,
                            "status": "Downloaded"
                        }
                        project_record["attachments"].append(att_info)
                        print(f"    [+] Saved: {pid}_{filename} ({file_size:,} bytes)")
                    except Exception as e:
                        if href:
                            project_record["attachments"].append({
                                "filename": f"{pid}_att_{b_idx}",
                                "s3_url": href,
                                "status": "Logged S3 Endpoint",
                                "note": str(e)
                            })

            except Exception as e:
                print(f"  [-] Error accessing project {pid}: {e}")
                project_record["error"] = str(e)

            manifest.append(project_record)

        browser.close()

    with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)
    print(f"\nMaster S3 attachment manifest saved to {MANIFEST_PATH}")

if __name__ == "__main__":
    batch_download_s3()
