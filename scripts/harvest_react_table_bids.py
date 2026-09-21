import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\OsintNeoAi\public\evidence\oc_procurement_portal"
DOM_1500_BIDS_JSON = os.path.join(EVIDENCE_DIR, "dom_1500_bids_manifest.json")

def harvest_react_table_bids():
    print("Launching ReactTable harvester across all 30 pages...", flush=True)
    
    user_data_dir = r"C:\OsintNeoAi\.playwright_session"
    os.makedirs(user_data_dir, exist_ok=True)
    
    all_bids = []
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0] if context.pages else context.new_page()

        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
        print(f"Navigating to initial portal page...", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        for page_num in range(1, 31):
            p_url = f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page_num}&limit=50&sortField=releaseProjectDate&sortDirection=ASC"
            print(f"[{page_num}/30] Harvesting page {page_num}...", flush=True)
            try:
                page.goto(p_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(3)
                page.wait_for_selector(".rt-tr-group", timeout=15000)

                # Extract row data via JavaScript evaluate
                rows_data = page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('.rt-tbody .rt-tr-group');
                        const data = [];
                        rows.forEach((row, idx) => {
                            const cells = row.querySelectorAll('.rt-td');
                            const click_el = row.querySelector('.rt-tr');
                            const text_content = row.innerText.split('\\n').filter(t => t.trim().length > 0);
                            
                            // Check for any embedded project URL or onclick handlers
                            let project_id = null;
                            const innerHtml = row.innerHTML;
                            const match = innerHtml.match(/projects\\/(\\d+)/);
                            if (match) {
                                project_id = match[1];
                            }

                            data.push({
                                row_index: idx + 1,
                                cells: text_content,
                                project_id: project_id,
                                raw_text: row.innerText.substring(0, 200)
                            });
                        });
                        return data;
                    }
                """)

                print(f"  Extracted {len(rows_data)} ReactTable row bids on page {page_num}", flush=True)
                for r in rows_data:
                    r["page_number"] = page_num
                    all_bids.append(r)

            except Exception as e:
                print(f"  [-] Error on page {page_num}: {e}", flush=True)

        context.close()

    print(f"\nTotal ReactTable bids harvested: {len(all_bids)}", flush=True)
    with open(DOM_1500_BIDS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_bids, f, indent=2)
    print(f"Saved ReactTable bids to {DOM_1500_BIDS_JSON}", flush=True)

if __name__ == "__main__":
    harvest_react_table_bids()
