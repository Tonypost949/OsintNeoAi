import json
from playwright.sync_api import sync_playwright

def inspect_accela():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("[*] Navigating to HB Accela...")
        page.goto("https://aca-prod.accela.com/cohb/Cap/CapHome.aspx?module=Building&TabName=Building", timeout=60000)
        page.wait_for_load_state("networkidle")
        
        inputs = page.query_selector_all("input")
        print(f"[+] Found {len(inputs)} input fields:")
        for inp in inputs:
            iid = inp.get_attribute("id") or ""
            name = inp.get_attribute("name") or ""
            itype = inp.get_attribute("type") or ""
            if iid or name:
                print(f"  - id: '{iid}' | name: '{name}' | type: '{itype}'")
                
        page.screenshot(path="C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch/accela_dom_inspect.png")
        print("[✓] Screenshot saved to scratch/accela_dom_inspect.png")
        browser.close()

if __name__ == "__main__":
    inspect_accela()
