import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
ALL_PROJECTS_JSON = os.path.join(EVIDENCE_DIR, "all_1500_opengov_projects.json")

def harvest_with_persistent_session():
    print("Launching Chromium with interactive persistent user session to bypass Cloudflare Turnstile...", flush=True)
    
    user_data_dir = r"C:\OsintNeoAi\.playwright_session"
    os.makedirs(user_data_dir, exist_ok=True)
    
    all_projects = []
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        page = context.pages[0] if context.pages else context.new_page()

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

        print("Checking Cloudflare status...", flush=True)
        time.sleep(5)

        for _ in range(15):
            title = page.title()
            print(f"Current Page Title: '{title}'", flush=True)
            if "Just a moment" not in title and "Cloudflare" not in title:
                print("Cloudflare Turnstile challenge passed!", flush=True)
                break
            time.sleep(2)

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

        context.close()

    print(f"\nTotal projects cataloged: {len(all_projects)}", flush=True)
    with open(ALL_PROJECTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_projects, f, indent=2)
    print(f"Saved project data to {ALL_PROJECTS_JSON}", flush=True)

if __name__ == "__main__":
    harvest_with_persistent_session()
