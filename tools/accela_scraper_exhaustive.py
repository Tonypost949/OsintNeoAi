import json
from playwright.sync_api import sync_playwright

# Comprehensive Address Net for HBNC, Cameron, Beach Blvd, Cross Streets, and Adjacent Parcels
ADDRESSES = [
    # Primary Targets
    {"num": "17631", "street": "Cameron"},
    {"num": "17642", "street": "Beach"},
    
    # Adjacent & Neighboring Cameron Block
    {"num": "17532", "street": "Cameron"},
    {"num": "17621", "street": "Cameron"},
    {"num": "17622", "street": "Cameron"},
    {"num": "17652", "street": "Cameron"},
    {"num": "17500", "street": "Cameron"},
    {"num": "17700", "street": "Cameron"},
    
    # Across the street & Beach Blvd stretch
    {"num": "17641", "street": "Beach"},
    {"num": "17651", "street": "Beach"},
    {"num": "17600", "street": "Beach"},
    
    # Intersecting / Cross Streets (Slater, Talbert)
    {"num": "17600", "street": "Slater"},
    {"num": "17700", "street": "Slater"},
    {"num": "17600", "street": "Talbert"},
    
    # Stormtech / General keyword fallbacks via partial search if Accela permits it
    {"num": "", "street": "Stormtech"},
    {"num": "", "street": "Ascon"}
]

def exhaustive_scrape_accela():
    print("[+] Initiating Exhaustive Accela Scrape for Adjacent & Cross-Street Parcels...")
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36").new_page()
        
        for addr in ADDRESSES:
            target_name = f"{addr['num']} {addr['street']}".strip()
            print(f"\n[+] Querying Database for: {target_name}...")
            try:
                page.goto("https://aca-prod.accela.com/cohb/Cap/CapHome.aspx?module=Building&TabName=Building", timeout=60000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                
                # Fill what we have
                if addr['num']:
                    page.fill("input[id$='txtGSNumber_ChildControl0']", addr['num'])
                if addr['street']:
                    page.fill("input[id$='txtGSStreetName']", addr['street'])
                
                page.click("a[id$='btnNewSearch']")
                
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                
                if page.locator("text=No records found").count() > 0 or page.locator("text=0 records found").count() > 0:
                    print(f"  [-] ZERO records found.")
                    res[target_name] = "ZERO records found."
                    continue
                
                rows = page.locator("tr.ACA_TabRow, tr.ACA_TabRow_Odd, tr.ACA_TabRow_Even").all()
                if not rows:
                    print(f"  [?] Unexpected page state. Skipping.")
                    res[target_name] = "Table missing or error."
                    continue
                    
                records = []
                # Grab up to 50 permits for adjacent addresses if they exist
                for row in rows[:50]:
                    records.append(row.inner_text().replace('\t', ' | '))
                    
                print(f"  [!] Found {len(rows)} permit records. Extracting...")
                res[target_name] = records
                
            except Exception as e:
                print(f"  [!] Exception: {e}")
                res[target_name] = f"Error: {e}"
                
        b.close()
        
        out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/live_accela_permits_exhaustive.json"
        with open(out_path, "w") as f:
            json.dump(res, f, indent=2)
        print(f"\n[✓] Exhaustive Scrape complete. Dumped to {out_path}")

if __name__ == '__main__':
    exhaustive_scrape_accela()
