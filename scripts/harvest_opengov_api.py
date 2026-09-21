import time
import json
from playwright.sync_api import sync_playwright

def harvest_api_endpoint():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        XHR_URLS = []

        def handle_response(response):
            XHR_URLS.append({
                "url": response.url,
                "status": response.status,
                "content_type": response.headers.get("content-type", "")
            })

        page.on("response", handle_response)
        
        print("Navigating to OpenGov portal page 1...")
        page.goto("https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC", wait_until="domcontentloaded")
        time.sleep(8)

        print(f"\nCaptured {len(XHR_URLS)} total network requests.")

        with open(r"C:\OsintNeoAi\evidence\oc_procurement_portal\all_network_requests.json", "w", encoding="utf-8") as f:
            json.dump(XHR_URLS, f, indent=2)

        browser.close()

if __name__ == "__main__":
    harvest_api_endpoint()
