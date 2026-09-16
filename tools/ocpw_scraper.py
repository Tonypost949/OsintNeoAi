import json
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def scrape_ocpw_maps():
    print("[+] Ghosting into OCPW Environmental and Public Works Maps...")
    
    # We are targeting Map ID 8 (Environmental Resources) and Map ID 1 (OCPW Demo/Development)
    targets = [
        {"name": "Environmental Resources", "url": "https://webapps.ocgis.com/oclandinsights/map-viewer?id=8"},
        {"name": "OCPW Demo/Development", "url": "https://webapps.ocgis.com/oclandinsights/map-viewer?id=1"}
    ]
    
    res = {}
    
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        context = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        for t in targets:
            print(f"  [-] Navigating to {t['name']} map...")
            try:
                page.goto(t['url'], timeout=90000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(10000) # Give ESRI maps plenty of time to render
                
                # Try to dismiss any splash screens
                disclaimer_btn = page.locator("div.jimu-btn, button").filter(has_text="OK")
                if disclaimer_btn.count() > 0:
                    disclaimer_btn.first.click()
                    page.wait_for_timeout(2000)
                    
                # Take a forensic snapshot of the fully rendered map
                scratch_dir = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/scratch")
                scratch_dir.mkdir(parents=True, exist_ok=True)
                
                screenshot_name = t['name'].replace(" ", "_").replace("/", "_") + ".png"
                screenshot_path = str(scratch_dir / screenshot_name)
                page.screenshot(path=screenshot_path)
                
                print(f"  [+] Map captured to {screenshot_path}")
                
                # Check for layers or extractable text
                layers_text = ""
                layer_list = page.locator(".layer-title-text, .esriLayerList, .layer-item-title").all()
                if layer_list:
                    layers_text = [l.inner_text() for l in layer_list if l.inner_text()]
                    print(f"  [!] Extracted {len(layers_text)} available map layers.")
                
                res[t['name']] = {
                    "url": t['url'],
                    "status": "Captured successfully.",
                    "screenshot": screenshot_path,
                    "layers_found": layers_text
                }

            except Exception as e:
                print(f"  [!] Exception on {t['name']}: {e}")
                res[t['name']] = {"error": str(e)}
                
        b.close()
        
        out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/ocpw_gis_extractions.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"\n[✓] OCPW GIS Scrape complete. Data dumped to {out_path}")

if __name__ == '__main__':
    scrape_ocpw_maps()
