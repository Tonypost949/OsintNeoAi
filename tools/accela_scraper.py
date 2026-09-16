import json
import time
from playwright.sync_api import sync_playwright

ADDRESSES = [
    {"num": "17631", "street": "Cameron"},
    {"num": "17642", "street": "Beach"},
    {"num": "17532", "street": "Cameron"}
]

def scrape_accela():
    print("[+] Ghosting into Accela ACA...")
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36").new_page()
        
        for addr in ADDRESSES:
            print(f"\n[+] Querying Accela Live Database for {addr['num']} {addr['street']}...")
            try:
                # Direct navigation to the Building Permits Search tab
                page.goto("https://aca-prod.accela.com/cohb/Cap/CapHome.aspx?module=Building&TabName=Building", timeout=60000)
                
                # Fill address fields based on Accela's standard input IDs (verified via DOM inspection)
                page.fill("input[id$='txtGSNumber_ChildControl0']", addr['num'])
                page.fill("input[id$='txtGSStreetName']", addr['street'])
                
                # Click Search
                page.click("a[id$='btnNewSearch']")
                
                # Wait for network to settle
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                
                # Detect "No records found"
                if page.locator("text=No records found").count() > 0 or page.locator("text=0 records found").count() > 0:
                    print(f"  [-] Verified: ZERO records found for {addr['num']} {addr['street']}")
                    res[f"{addr['num']} {addr['street']}"] = "ZERO records found."
                    continue
                
                # Extract results table if it exists
                rows = page.locator("tr.ACA_TabRow, tr.ACA_TabRow_Odd, tr.ACA_TabRow_Even").all()
                if not rows:
                    print(f"  [?] Unexpected page state. Taking forensic screenshot...")
                    screenshot_path = f"C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch/accela_{addr['num']}_error.png"
                    page.screenshot(path=screenshot_path)
                    res[f"{addr['num']} {addr['street']}"] = f"Table missing. Screenshot saved to {screenshot_path}"
                    continue
                    
                records = []
                for row in rows[:15]:
                    records.append(row.inner_text().replace('\t', ' | '))
                    
                print(f"  [!] Found {len(rows)} permit records. Extracting...")
                res[f"{addr['num']} {addr['street']}"] = records
                
            except Exception as e:
                print(f"  [!] Critical Exception on {addr['num']}: {e}")
                res[f"{addr['num']} {addr['street']}"] = f"Error: {e}"
                
        b.close()
        
        out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/live_accela_permits.json"
        with open(out_path, "w") as f:
            json.dump(res, f, indent=2)
        print(f"\n[✓] Headless Accela Scrape Complete. Full JSON dumped to {out_path}")

if __name__ == '__main__':
    scrape_accela()
