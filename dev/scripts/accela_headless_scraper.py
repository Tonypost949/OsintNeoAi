import os
import json
from playwright.sync_api import sync_playwright

ADDRESSES = [
    {"num": "17631", "street": "Cameron"},
    {"num": "17642", "street": "Beach"},
    {"num": "17532", "street": "Cameron"},
    {"num": "17621", "street": "Cameron"},
    {"num": "17622", "street": "Cameron"},
    {"num": "17652", "street": "Cameron"}
]

out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/live_accela_permits.json"
scratch_dir = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch"

def scrape_accela():
    print("[+] Initializing Chromium Headless Ghost Browser...")
    results = {}
    os.makedirs(scratch_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for addr in ADDRESSES:
            key = f"{addr['num']} {addr['street']}"
            print(f"\n[+] Querying Accela Live Database for {key}...")
            try:
                # Direct navigation to the Building Permits Search tab
                page.goto("https://aca-prod.accela.com/cohb/Cap/CapHome.aspx?module=Building&TabName=Building", timeout=60000)
                page.wait_for_load_state("networkidle")
                
                # Fill address fields using verified Accela DOM IDs
                num_sel = "input[id*='txtGSNumber_ChildControl0'], input[id$='txtAddressNo'], input[id*='txtGSNumber']"
                street_sel = "input[id*='txtGSStreetName'], input[id$='txtStreetName']"
                btn_sel = "a[id*='btnNewSearch'], a[id$='btnSearch'], input[value*='Search']"

                page.fill(num_sel, addr['num'])
                page.fill(street_sel, addr['street'])
                
                # Click Search button
                page.click(btn_sel)
                
                # Wait for network to settle
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)

                # Detect "No records found"
                if page.locator("text=No records found").count() > 0 or page.locator("text=0 records found").count() > 0 or page.locator("text=No search results").count() > 0:
                    print(f"  [-] Verified: ZERO records found for {key}")
                    results[key] = "No records found."
                    continue

                # Extract results table if it exists
                rows = page.locator("tr.ACA_TabRow, tr.ACA_TabRow_Odd, tr.ACA_TabRow_Even, tr[class*='gdvList'], tr[class*='gdvItem']").all()
                if not rows:
                    print(f"  [?] Table missing or no rows found. Taking forensic screenshot...")
                    screenshot_path = f"{scratch_dir}/accela_{addr['num']}_error.png"
                    page.screenshot(path=screenshot_path)
                    results[key] = f"Table missing. Screenshot saved to {screenshot_path}"
                    continue

                records = []
                for row in rows[:15]:
                    records.append(row.inner_text().replace('\t', ' | '))
                print(f"  [!] Found {len(rows)} permit records. Extracting...")
                results[key] = records

            except Exception as e:
                print(f"  [!] Critical Exception on {addr['num']}: {e}")
                results[key] = f"Error: {e}"

        browser.close()

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[✓] Headless Accela Scrape Complete. Full JSON dumped to {out_path}")

if __name__ == "__main__":
    scrape_accela()
