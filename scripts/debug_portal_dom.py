import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
SCREENSHOT_PATH = r"C:\OsintNeoAi\evidence\oc_procurement_portal\portal_live_state.png"

def debug_portal_dom():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
        print(f"Navigating to {url} with domcontentloaded...")
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        time.sleep(6)

        page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        print(f"Saved live page screenshot to {SCREENSHOT_PATH}")

        anchors = page.query_selector_all("a")
        hrefs = [a.get_attribute("href") for a in anchors if a.get_attribute("href")]
        print(f"Total links found: {len(hrefs)}")
        print("Sample links:", hrefs[:20])

        browser.close()

if __name__ == "__main__":
    debug_portal_dom()
