import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=r'C:\OsintNeoAi\.playwright_session',
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto('https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC', wait_until='domcontentloaded')
    
    print("Waiting for Cloudflare Turnstile challenge completion...", flush=True)
    for i in range(25):
        title = page.title()
        print(f"[{i+1}/25] Title: '{title}'", flush=True)
        if "Just a moment" not in title and "Cloudflare" not in title:
            print("Successfully passed Cloudflare challenge!", flush=True)
            break
        time.sleep(2)
        
    context.close()
