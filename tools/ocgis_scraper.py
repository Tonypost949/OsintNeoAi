import json
import time
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

def scrape_ocgis():
    print("[+] Ghosting into OCGIS Land Insights for 0.25m radius around 17631 Cameron...")
    res = {
        "target": "17631 Cameron Ln, Huntington Beach", 
        "radius": "0.25 miles", 
        "apns": [], 
        "historical_data": []
    }
    
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        context = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        try:
            print("  [-] Navigating to https://webapps.ocgis.com/oclandinsights/home/ ...")
            page.goto("https://webapps.ocgis.com/oclandinsights/home/", timeout=90000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)
            
            # Click past any splash screens/disclaimers
            disclaimer_btn = page.locator("div.jimu-btn, button").filter(has_text="OK")
            if disclaimer_btn.count() > 0:
                disclaimer_btn.first.click()
                page.wait_for_timeout(2000)

            # Locate the ArcGIS search widget
            search_input = page.locator("input.searchInput, input[placeholder*='address'], input[title*='Search']")
            if search_input.count() > 0:
                search_input.first.fill("17631 Cameron Ln, Huntington Beach")
                page.keyboard.press("Enter")
                print("  [+] Address entered, querying spatial boundaries...")
                page.wait_for_timeout(8000)
                page.wait_for_load_state("networkidle")
                
                # Attempt to open layer list to activate historical layers if available
                print("  [!] Activating historical layers (1900+ permits/Sanborn maps) if present...")
                layer_btn = page.locator("[title='Layer List'], .icon-node-layerlist")
                if layer_btn.count() > 0:
                    layer_btn.first.click()
                    page.wait_for_timeout(2000)
                    
                    # Try to check boxes for historical or permit layers
                    historical_checkboxes = page.locator(".layer-title-text").filter(has_text=re.compile("historic|permit|1900|sanborn", re.IGNORECASE))
                    for i in range(historical_checkboxes.count()):
                        try:
                            # click the checkbox preceding the title
                            historical_checkboxes.nth(i).locator("xpath=preceding-sibling::*").first.click()
                        except: pass
                
                page.wait_for_timeout(3000)

                print("  [!] Capturing underlying ArcGIS REST API responses for historical data...")
                
                scratch_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch")
                scratch_dir.mkdir(parents=True, exist_ok=True)
                
                # Take a full screenshot of the targeted map area
                screenshot_path = str(scratch_dir / "ocgis_map_cameron_radius.png")
                page.screenshot(path=screenshot_path)
                res["status"] = f"Map rendering captured to {screenshot_path}."
                
                # Attempt to extract popup data
                popups = page.locator(".esriPopup .titlePane, .esriPopup .contentPane, .popup-content").all()
                if popups:
                    for popup in popups:
                        text = popup.inner_text().replace('\n', ' | ')
                        if text: res["historical_data"].append(text)
                else:
                    print("  [?] Specific parcel popup not rendered in DOM. Relies on screenshot/local data.")

            else:
                print("  [!] Search box not found, saving state.")
                page.screenshot(path="C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch/ocgis_error.png")
                res["error"] = "Could not locate ArcGIS search input."
                
        except Exception as e:
            print(f"  [!] Exception: {e}")
            res["error"] = str(e)
            
        b.close()
        
        # Merge with our local 142-XXX-XX APN cluster findings
        res["apns"] = [
            "142-073-33", "142-073-54", "142-075-01", "142-075-02", 
            "142-082-35", "142-122-07", "142-242-16", "142-253-04", 
            "142-321-20", "142-492-11", "14205653", "14206304", 
            "14216029", "14220790", "14235693"
        ]
        
        out_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "ocgis_historical_apn_data.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"\n[✓] OCGIS Scrape complete. Data dumped to {out_path}")

if __name__ == '__main__':
    scrape_ocgis()
