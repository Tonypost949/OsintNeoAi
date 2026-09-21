import os
import time
import json
from playwright.sync_api import sync_playwright

BASE_URL = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&limit=50"
DOWNLOAD_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal\opengov_bids"

def run_scraper():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    captured_api_data = []

    print(f"Launching Playwright Chromium Scraper for {BASE_URL}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # Network Interception to capture raw OpenGov JSON API responses
        def handle_response(response):
            if "api" in response.url or "project" in response.url or "portal" in response.url:
                try:
                    if "json" in response.headers.get("content-type", ""):
                        body = response.json()
                        captured_api_data.append({"url": response.url, "data": body})
                        print(f"[API Intercepted] {response.url}")
                except Exception:
                    pass

        page.on("response", handle_response)

        print("Navigating to OpenGov Procurement Portal...")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # Extract project links
        project_links = page.query_selector_all("a[href*='/portal/ocgov/projects/']")
        project_urls = []
        for el in project_links:
            href = el.get_attribute("href")
            if href:
                full_url = f"https://procurement.opengov.com{href}" if href.startswith("/") else href
                if full_url not in project_urls:
                    project_urls.append(full_url)

        print(f"Extracted {len(project_urls)} project URLs from Playwright DOM render.")

        # Save extracted project metadata manifest
        manifest_path = os.path.join(DOWNLOAD_DIR, "opengov_playwright_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as fp:
            json.dump({
                "base_url": BASE_URL,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_project_urls": len(project_urls),
                "project_urls": project_urls,
                "captured_api_endpoints": [c["url"] for c in captured_api_data]
            }, fp, indent=2)

        print(f"Saved manifest to {manifest_path}")
        browser.close()

if __name__ == "__main__":
    run_scraper()
