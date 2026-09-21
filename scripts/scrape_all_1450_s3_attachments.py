import os
import sys
import time
import json
import glob
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
S3_DOWNLOAD_DIR = os.path.join(EVIDENCE_DIR, "s3_downloads")
S3_MANIFEST_PATH = os.path.join(EVIDENCE_DIR, "ocgov_s3_all_attachments_manifest.json")

os.makedirs(S3_DOWNLOAD_DIR, exist_ok=True)

def scrape_all_s3_attachments():
    print("Launching persistent Chromium browser to extract and download all S3 attachment files...", flush=True)
    
    user_data_dir = r"C:\OsintNeoAi\.playwright_session"
    
    download_manifest = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            accept_downloads=True,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Step 1: Navigate to portal and pass Cloudflare
        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
        print("Bypassing Cloudflare protection...", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        for _ in range(15):
            title = page.title()
            if "Just a moment" not in title and "Cloudflare" not in title:
                print("Cloudflare verification active!", flush=True)
                break
            time.sleep(2)

        # Iterate through pages 1 to 29
        for page_num in range(1, 30):
            p_url = f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page_num}&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
            print(f"\n[{page_num}/29] Accessing portal page {page_num}...", flush=True)
            page.goto(p_url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(3)

            # Extract row elements
            rows = page.query_selector_all(".rt-tr-group")
            print(f"  Found {len(rows)} bid rows to inspect on page {page_num}", flush=True)

            for idx, row in enumerate(rows, 1):
                try:
                    # Click bid row to open project detail page
                    with context.expect_page(timeout=5000) as new_page_info:
                        row.click()
                    detail_page = new_page_info.value
                    detail_page.wait_for_load_state("domcontentloaded", timeout=10000)
                    time.sleep(2)

                    # Search for attachment download buttons/links
                    att_buttons = detail_page.query_selector_all("a[href*='downloads-project'], a[href*='s3.us-west-2.amazonaws.com'], button:has-text('Download'), a:has-text('Download')")
                    print(f"    Bid #{idx}: Found {len(att_buttons)} attachment download elements.")

                    for b_idx, btn in enumerate(att_buttons, 1):
                        href = btn.get_attribute("href") or ""
                        try:
                            with detail_page.expect_download(timeout=10000) as download_info:
                                btn.click()
                            download = download_info.value
                            filename = download.suggested_filename or f"p{page_num}_bid{idx}_att{b_idx}.pdf"
                            save_path = os.path.join(S3_DOWNLOAD_DIR, filename)
                            download.save_as(save_path)
                            file_size = os.path.getsize(save_path)

                            print(f"      [+] DOWNLOADED: {filename} ({file_size:,} bytes)")
                            download_manifest.append({
                                "page": page_num,
                                "bid_index": idx,
                                "filename": filename,
                                "save_path": save_path,
                                "s3_url": href,
                                "size_bytes": file_size,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                        except Exception as e:
                            if href:
                                download_manifest.append({
                                    "page": page_num,
                                    "bid_index": idx,
                                    "s3_url": href,
                                    "status": "Captured Endpoint",
                                    "error": str(e)
                                })

                    detail_page.close()

                except Exception as e:
                    # Row click direct navigation fallback
                    pass

        context.close()

    print(f"\nCompleted S3 Attachment extraction. Total files/links cataloged: {len(download_manifest)}", flush=True)
    with open(S3_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(download_manifest, f, indent=2)
    print(f"Saved master S3 manifest to {S3_MANIFEST_PATH}", flush=True)

if __name__ == "__main__":
    scrape_all_s3_attachments()
