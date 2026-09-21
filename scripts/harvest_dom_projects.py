import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
DOM_PROJECTS_JSON = os.path.join(EVIDENCE_DIR, "dom_extracted_1500_projects.json")

def harvest_dom_project_links():
    print("Launching persistent Chromium to extract project links directly from DOM with wait_for_selector...", flush=True)
    
    user_data_dir = r"C:\OsintNeoAi\.playwright_session"
    os.makedirs(user_data_dir, exist_ok=True)
    
    extracted_records = []
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0] if context.pages else context.new_page()

        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
        print(f"Navigating to initial page...", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        for _ in range(15):
            title = page.title()
            if "Just a moment" not in title and "Cloudflare" not in title:
                print("Cloudflare Turnstile challenge passed!", flush=True)
                break
            time.sleep(2)

        for page_num in range(1, 31):
            p_url = f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page_num}&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
            print(f"[{page_num}/30] Extracting DOM items from page {page_num}...", flush=True)
            try:
                page.goto(p_url, wait_until="domcontentloaded", timeout=45000)
                
                # Wait for React table container to hydrate
                page.wait_for_selector("a, tr, div", timeout=15000)
                time.sleep(3)

                anchors = page.query_selector_all("a[href*='projects']")
                print(f"  Found {len(anchors)} project anchor links on DOM page {page_num}", flush=True)

                for a in anchors:
                    href = a.get_attribute("href") or ""
                    text = a.inner_text().strip()
                    extracted_records.append({
                        "page": page_num,
                        "href": href,
                        "title": text
                    })

            except Exception as e:
                print(f"  [-] Error on page {page_num}: {e}", flush=True)

        context.close()

    print(f"\nTotal DOM project records harvested: {len(extracted_records)}", flush=True)
    with open(DOM_PROJECTS_JSON, "w", encoding="utf-8") as f:
        json.dump(extracted_records, f, indent=2)
    print(f"Saved DOM records to {DOM_PROJECTS_JSON}", flush=True)

if __name__ == "__main__":
    harvest_dom_project_links()
