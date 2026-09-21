import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
S3_DOWNLOAD_DIR = os.path.join(EVIDENCE_DIR, "s3_downloads")
ALL_PROJECTS_JSON = os.path.join(EVIDENCE_DIR, "all_1500_opengov_projects.json")
USER_DATA_DIR = r"C:\Users\Amd949609\AppData\Local\Google\Chrome\User Data\Default"

os.makedirs(S3_DOWNLOAD_DIR, exist_ok=True)

def harvest_with_stealth():
    print("Launching Playwright with Chrome stealth context to resolve Cloudflare challenge...", flush=True)
    
    all_projects = []
    
    with sync_playwright() as p:
        # Launch Chrome with stealth arguments to pass Cloudflare challenge
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()

        def handle_response(response):
            try:
                if "projects" in response.url or "api" in response.url:
                    if response.status == 200:
                        ct = response.headers.get("content-type", "")
                        if "json" in ct:
                            data = response.json()
                            if isinstance(data, dict) and "projects" in data:
                                plist = data["projects"]
                                print(f"[API Intercept] Captured {len(plist)} projects from {response.url}", flush=True)
                                all_projects.extend(plist)
            except Exception:
                pass

        page.on("response", handle_response)

        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
        print(f"Navigating to {url}...", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        print("Waiting for Cloudflare verification to pass...", flush=True)
        time.sleep(8)

        # Check if page passed Cloudflare
        title = page.title()
        print(f"Loaded Page Title: {title}", flush=True)

        for page_num in range(1, 31):
            p_url = f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page_num}&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
            print(f"[{page_num}/30] Navigating to page {page_num}...", flush=True)
            try:
                page.goto(p_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(3)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
            except Exception as e:
                print(f"  [-] Error on page {page_num}: {e}", flush=True)

        browser.close()

    print(f"\nTotal projects cataloged: {len(all_projects)}", flush=True)
    with open(ALL_PROJECTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_projects, f, indent=2)
    print(f"Saved project data to {ALL_PROJECTS_JSON}", flush=True)

if __name__ == "__main__":
    harvest_with_stealth()
