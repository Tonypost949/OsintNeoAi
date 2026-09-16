import json
import time
from playwright.sync_api import sync_playwright

def diagnose_accela():
    print("[+] Taking a snapshot of the exact DOM state of the Accela search page to debug the form...")
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)").new_page()
        
        page.goto("https://aca-prod.accela.com/cohb/Cap/CapHome.aspx?module=Building&TabName=Building")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(4000)
        
        # Save a screenshot so we know what it looks like
        page.screenshot(path="C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch/accela_debug.png", full_page=True)
        
        # Dump the HTML to figure out the actual input IDs
        html = page.content()
        with open("C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch/accela_dom.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("[✓] Saved DOM and Screenshot to scratch folder.")
        b.close()

if __name__ == '__main__':
    diagnose_accela()
