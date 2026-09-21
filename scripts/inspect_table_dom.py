import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
SCREENSHOT_PATH = r"C:\OsintNeoAi\evidence\oc_procurement_portal\portal_table_state.png"

def inspect_table_structure():
    with sync_playwright() as p:
        user_data_dir = r"C:\OsintNeoAi\.playwright_session"
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
        print(f"Navigating to {url}...", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)

        page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        print(f"Saved table screenshot to {SCREENSHOT_PATH}", flush=True)

        page_title = page.title()
        print(f"Page Title: {page_title}", flush=True)

        # Inspect all interactive elements
        elements = page.evaluate("""
            () => {
                const results = [];
                const all = document.querySelectorAll('*');
                all.forEach(el => {
                    if (el.innerText && (el.innerText.includes('OC') || el.innerText.includes('RFP') || el.innerText.includes('Bid') || el.innerText.includes('County'))) {
                        results.push({
                            tag: el.tagName,
                            className: el.className,
                            text: el.innerText.substring(0, 100)
                        });
                    }
                });
                return results.slice(0, 25);
            }
        """)

        print(f"Captured {len(elements)} matching DOM elements:")
        for item in elements:
            print(" -", item)

        context.close()

if __name__ == "__main__":
    inspect_table_structure()
