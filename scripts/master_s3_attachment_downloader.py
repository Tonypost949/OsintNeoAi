import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
S3_DOWNLOAD_DIR = os.path.join(EVIDENCE_DIR, "s3_downloads")
S3_MANIFEST_PATH = os.path.join(EVIDENCE_DIR, "ocgov_s3_all_attachments_manifest.json")
MAPPED_PROJECTS_JSON = os.path.join(EVIDENCE_DIR, "all_1500_mapped_projects.json")

os.makedirs(S3_DOWNLOAD_DIR, exist_ok=True)

def harvest_and_scrape_comprehensive():
    print("Starting master multi-tab scraper with verified session token...", flush=True)
    
    user_data_dir = r"C:\OsintNeoAi\.playwright_session"
    
    download_manifest = []
    mapped_projects = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            accept_downloads=True,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        main_page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to portal...", flush=True)
        main_page.goto("https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        for page_num in range(1, 30):
            p_url = f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page_num}&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
            print(f"\n[{page_num}/29] Accessing Portal Page {page_num}...", flush=True)
            main_page.goto(p_url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait for React table rows
            try:
                main_page.wait_for_selector(".rt-tbody .rt-tr-group", timeout=15000)
                time.sleep(2)
            except Exception:
                time.sleep(4)

            title_links = main_page.query_selector_all("._3B1yLmtTpBjMnRf-vy-5tj")
            print(f"  Found {len(title_links)} bid items on page {page_num}", flush=True)

            for idx in range(len(title_links)):
                try:
                    title_links = main_page.query_selector_all("._3B1yLmtTpBjMnRf-vy-5tj")
                    if idx >= len(title_links):
                        break
                    
                    link = title_links[idx]
                    title_text = link.inner_text().strip()

                    with context.expect_page(timeout=10000) as new_page_info:
                        link.click(button="middle")
                    detail_page = new_page_info.value
                    detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
                    time.sleep(1.5)

                    curr_url = detail_page.url
                    project_id = curr_url.split("/projects/")[-1].split("?")[0] if "/projects/" in curr_url else f"p{page_num}_{idx+1}"
                    print(f"    [{idx+1}/50] '{title_text[:35]}' -> Project ID {project_id}", flush=True)

                    project_record = {
                        "page_number": page_num,
                        "bid_index": idx + 1,
                        "title": title_text,
                        "project_id": project_id,
                        "project_url": curr_url,
                        "attachments": [],
                        "sections": []
                    }

                    # Iterate through sub-tabs (Attachments, Addenda, Documents)
                    sub_tabs = detail_page.query_selector_all("button[role='tab'], a[role='tab'], button:has-text('Attachments'), button:has-text('Addenda'), button:has-text('Timeline'), button:has-text('Documents')")
                    if sub_tabs:
                        for st in sub_tabs:
                            try:
                                t_name = st.inner_text().strip()
                                st.click()
                                time.sleep(1)
                                project_record["sections"].append(t_name)
                            except Exception:
                                pass

                    # Extract attachment download buttons
                    att_buttons = detail_page.query_selector_all("a[href*='downloads-project'], a[href*='s3.us-west-2.amazonaws.com'], button:has-text('Download'), a:has-text('Download'), a[href*='.pdf'], a[href*='.docx'], a[href*='.zip']")
                    if att_buttons:
                        print(f"      [+] Found {len(att_buttons)} attachment elements on Project {project_id}", flush=True)

                    for b_idx, btn in enumerate(att_buttons, 1):
                        href = btn.get_attribute("href") or ""
                        try:
                            with detail_page.expect_download(timeout=6000) as download_info:
                                btn.click()
                            download = download_info.value
                            filename = download.suggested_filename or f"proj_{project_id}_att_{b_idx}.pdf"
                            save_path = os.path.join(S3_DOWNLOAD_DIR, f"{project_id}_{filename}")
                            download.save_as(save_path)
                            file_size = os.path.getsize(save_path)

                            att_meta = {
                                "project_id": project_id,
                                "filename": f"{project_id}_{filename}",
                                "local_path": save_path,
                                "s3_url": href,
                                "size_bytes": file_size,
                                "status": "Downloaded"
                            }
                            project_record["attachments"].append(att_meta)
                            download_manifest.append(att_meta)
                            print(f"        -> DOWNLOADED: {filename} ({file_size:,} bytes)", flush=True)
                        except Exception as e:
                            if href:
                                att_meta = {
                                    "project_id": project_id,
                                    "filename": f"{project_id}_att_{b_idx}",
                                    "s3_url": href,
                                    "status": "Captured S3 Endpoint",
                                    "error": str(e)
                                }
                                project_record["attachments"].append(att_meta)
                                download_manifest.append(att_meta)

                    mapped_projects.append(project_record)
                    detail_page.close()

                except Exception as e:
                    print(f"    [-] Error on item #{idx+1}: {e}", flush=True)

        context.close()

    with open(S3_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(download_manifest, f, indent=2)

    with open(MAPPED_PROJECTS_JSON, "w", encoding="utf-8") as f:
        json.dump(mapped_projects, f, indent=2)

    print(f"\nScraping complete! Manifest saved to {S3_MANIFEST_PATH}", flush=True)

if __name__ == "__main__":
    harvest_and_scrape_comprehensive()
