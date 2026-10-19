import os
import sys
import time
import json
import glob
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"C:\OsintNeoAi\scraped_tabs"
MANIFEST_PATH = os.path.join(OUTPUT_DIR, "scraped_tabs_manifest.json")
EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
PUB_MANIFEST_PATH = os.path.join(EVIDENCE_DIR, "scraped_chrome_tabs_manifest.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def scrape_all_browser_tabs():
    print("Launching Chromium persistent context with user data profile...", flush=True)
    
    user_data_dir = r"C:\Users\Amd949609\AppData\Local\Google\Chrome\User Data"
    scraped_tabs = []

    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=r"C:\OsintNeoAi\.playwright_session",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            pages = context.pages
            print(f"Captured {len(pages)} open tab(s) in Playwright session.", flush=True)

            for idx, page in enumerate(pages, 1):
                try:
                    title = page.title() or "Untitled Tab"
                    url = page.url or "about:blank"
                    print(f"[{idx}/{len(pages)}] Scraping Tab #{idx}: '{title}' ({url})", flush=True)

                    html_content = page.content()
                    safe_name = f"tab_{idx}_" + "".join(c if c.isalnum() or c in "._-" else "_" for c in url)[:80]
                    html_path = os.path.join(OUTPUT_DIR, f"{safe_name}.html")
                    screenshot_path = os.path.join(OUTPUT_DIR, f"{safe_name}.png")

                    with open(html_path, "w", encoding="utf-8", errors="ignore") as f:
                        f.write(html_content)

                    try:
                        page.screenshot(path=screenshot_path, full_page=True)
                    except Exception:
                        pass

                    scraped_tabs.append({
                        "tab_index": idx,
                        "title": title,
                        "url": url,
                        "html_path": html_path,
                        "screenshot_path": screenshot_path,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    print(f"  [-] Error on tab #{idx}: {e}", flush=True)

            context.close()

        except Exception as e:
            print(f"[-] Session launch note: {e}", flush=True)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(scraped_tabs, f, indent=2)

    with open(PUB_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(scraped_tabs, f, indent=2)

    print(f"\nTab harvesting finished. Saved manifest to {MANIFEST_PATH}", flush=True)

if __name__ == "__main__":
    scrape_all_browser_tabs()
