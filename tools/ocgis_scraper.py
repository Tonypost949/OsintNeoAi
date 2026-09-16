import json
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import re

def scrape_ocgis():
    print("[+] Ghosting into OCGIS Land Insights for 0.25m radius around 17631 Cameron...")
    res = {
        "target": "17631 Cameron Ln, Huntington Beach", 
        "radius": "0.25 miles", 
        "apns": [
            "142-073-33", "142-073-54", "142-075-01", "142-075-02", 
            "142-082-35", "142-122-07", "142-242-16", "142-253-04", 
            "142-321-20", "142-492-11", "14205653", "14206304", 
            "14216029", "14220790", "14235693"
        ], 
        "historical_data": []
    }
    
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        context = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()
        
        try:
            page.goto("https://webapps.ocgis.com/oclandinsights/home/", timeout=90000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)
            
            disclaimer_btn = page.locator("div.jimu-btn, button").filter(has_text="OK")
            if disclaimer_btn.count() > 0:
                disclaimer_btn.first.click()
                page.wait_for_timeout(2000)

            search_input = page.locator("input.searchInput, input[placeholder*='address'], input[title*='Search']")
            if search_input.count() > 0:
                search_input.first.fill("17631 Cameron Ln, Huntington Beach")
                page.keyboard.press("Enter")
                page.wait_for_timeout(8000)
                page.wait_for_load_state("networkidle")
                
                layer_btn = page.locator("[title='Layer List'], .icon-node-layerlist")
                if layer_btn.count() > 0:
                    layer_btn.first.click()
                    page.wait_for_timeout(2000)
                    
                    historical_checkboxes = page.locator(".layer-title-text").filter(has_text=re.compile("historic|permit|1900|sanborn", re.IGNORECASE))
                    for i in range(historical_checkboxes.count()):
                        try:
                            historical_checkboxes.nth(i).locator("xpath=preceding-sibling::*").first.click()
                        except: pass
                
                page.wait_for_timeout(3000)

                scratch_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch")
                scratch_dir.mkdir(parents=True, exist_ok=True)
                
                screenshot_path = str(scratch_dir / "ocgis_map_cameron_radius.png")
                page.screenshot(path=screenshot_path)
                res["status"] = f"Map rendering captured to {screenshot_path}."
                
                popups = page.locator(".esriPopup .titlePane, .esriPopup .contentPane, .popup-content").all()
                if popups:
                    for popup in popups:
                        text = popup.inner_text().replace('\n', ' | ')
                        if text: res["historical_data"].append(text)
            else:
                res["error"] = "Could not locate ArcGIS search input."
                
        except Exception as e:
            res["error"] = str(e)
            
        b.close()
        
        out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/ocgis_historical_apn_data.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"[✓] OCGIS Scrape complete. Dumped to {out_path}")

if __name__ == '__main__':
    scrape_ocgis()
