import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
S3_DOWNLOAD_DIR = os.path.join(EVIDENCE_DIR, "s3_downloads")
ALL_PROJECTS_JSON = os.path.join(EVIDENCE_DIR, "all_1500_opengov_projects.json")

os.makedirs(S3_DOWNLOAD_DIR, exist_ok=True)

def harvest_all_1500_projects():
    print("Starting Playwright browser session for full OpenGov procurement portal crawling...", flush=True)
    
    all_projects = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            try:
                if "api" in response.url or "projects" in response.url or "json" in response.headers.get("content-type", ""):
                    if response.status == 200:
                        data = response.json()
                        if isinstance(data, dict) and "projects" in data:
                            plist = data["projects"]
                            print(f"[API Intercept] Captured {len(plist)} projects from {response.url}", flush=True)
                            all_projects.extend(plist)
            except Exception:
                pass

        page.on("response", handle_response)

        for page_num in range(1, 31):
            url = f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page_num}&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
            print(f"[{page_num}/30] Navigating to {url}", flush=True)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(3)

                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

                project_links = page.query_selector_all("a[href*='/portal/ocgov/projects/']")
                print(f"  Found {len(project_links)} project links on DOM page {page_num}", flush=True)

            except Exception as e:
                print(f"  [-] Error on page {page_num}: {e}", flush=True)

        browser.close()

    print(f"\nTotal projects cataloged: {len(all_projects)}", flush=True)
    with open(ALL_PROJECTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_projects, f, indent=2)
    print(f"Saved project data to {ALL_PROJECTS_JSON}", flush=True)

if __name__ == "__main__":
    harvest_all_1500_projects()
