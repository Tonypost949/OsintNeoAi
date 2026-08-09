"""
Scrape ALL project detail pages: numeric IDs + document lists (no file downloads)
Stores in JSON -> load to BigQuery
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time, json, csv, re, tempfile
from pathlib import Path
from datetime import datetime

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
OUT_PROJECTS = WORK_DIR / "oc_procurement_projects_full.json"
OUT_CSV = WORK_DIR / "oc_procurement_projects_full.csv"

tmpdir = tempfile.mkdtemp()
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument(f"--user-data-dir={tmpdir}")

driver = uc.Chrome(options=options, version_main=149)

all_projects = []

try:
    total_pages = 27
    
    for page in range(1, total_pages + 1):
        print(f"\n{'='*50}")
        print(f"PAGE {page}/{total_pages}")
        
        driver.get(f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page}&limit=50&sortField=proposalDeadline&sortDirection=DESC")
        time.sleep(6)
        
        # Wait for table
        for _ in range(8):
            rows = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr")
            if rows:
                break
            time.sleep(2)
        
        if not rows:
            print("  No rows - stopping")
            break
        
        # Extract all project links on this page
        project_links = []
        for row in rows:
            try:
                link = row.find_element(By.CSS_SELECTOR, ".rt-td a")
                text = link.text.strip()
                project_links.append({"title": text, "element": link})
            except:
                continue
        
        print(f"  {len(project_links)} projects on page")
        
        # Click into each project to get numeric ID + documents
        for i, pl in enumerate(project_links):
            try:
                # Re-find element (stale after page changes)
                if i > 0:
                    # Navigate back to listing
                    driver.get(f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page}&limit=50&sortField=proposalDeadline&sortDirection=DESC")
                    time.sleep(4)
                    for _ in range(8):
                        rows = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr")
                        if rows: break
                        time.sleep(2)
                    if not rows: continue
                
                # Click project via JS
                result = driver.execute_script(f"""
                    var rows = document.querySelectorAll('.rt-tbody .rt-tr');
                    if (rows.length > {i}) {{
                        var link = rows[{i}].querySelector('.rt-td a');
                        if (link) {{
                            link.click();
                            return link.textContent.trim();
                        }}
                    }}
                    return null;
                """)
                
                if not result:
                    continue
                    
                time.sleep(5)
                current_url = driver.current_url
                
                # Extract numeric project ID from URL
                num_id_match = re.search(r'/projects/(\d+)', current_url)
                num_id = num_id_match.group(1) if num_id_match else ""
                
                # Get document list from Downloads tab
                docs = []
                try:
                    # Click Downloads tab
                    dl_tab = driver.find_element(By.XPATH, "//a[contains(text(),'Downloads')]")
                    dl_tab.click()
                    time.sleep(2)
                    
                    # Get document names
                    doc_els = driver.execute_script("""
                        var docs = [];
                        var labels = document.querySelectorAll('label');
                        labels.forEach(function(l) {
                            var txt = l.textContent.trim();
                            if (txt && txt.length > 3 && txt.length < 200) {
                                docs.push(txt);
                            }
                        });
                        return docs;
                    """)
                    docs = doc_els if doc_els else []
                except:
                    pass
                
                # Extract project metadata from detail page
                body = driver.find_element(By.TAG_NAME, "body").text
                
                # Get status, dates etc.
                project_id = ""
                dept = ""
                release_date = ""
                due_date = ""
                
                for line in body.split('\n'):
                    if line.startswith("Project ID:"):
                        project_id = line.replace("Project ID:", "").strip()
                    if line.startswith("Release Date:"):
                        release_date = line.replace("Release Date:", "").strip()
                    if line.startswith("Due Date:"):
                        due_date = line.replace("Due Date:", "").strip()
                    if "OC Community Resources" in line or "OC" in line[:30]:
                        if "Event Posting" in line or len(line) < 80:
                            dept = line.replace("Event Posting", "").strip()[:60]
                
                proj = {
                    "numeric_id": num_id,
                    "project_id": project_id,
                    "title": result,
                    "url": current_url,
                    "department": dept,
                    "release_date": release_date,
                    "due_date": due_date,
                    "documents": docs,
                    "document_count": len(docs),
                    "page": page,
                    "scraped_at": datetime.now().isoformat()
                }
                
                all_projects.append(proj)
                print(f"  [{i+1}/{len(project_links)}] [{num_id}] {project_id} | {len(docs)} docs | {result[:50]}")
                
            except Exception as e:
                print(f"  [{i+1}] ERROR: {str(e)[:80]}")
                continue
        
        # Progress save
        with open(OUT_PROJECTS, "w", encoding="utf-8") as f:
            json.dump(all_projects, f, indent=2, ensure_ascii=False)
        print(f"  SAVED: {len(all_projects)} total projects so far")

finally:
    driver.quit()

# Final save
with open(OUT_PROJECTS, "w", encoding="utf-8") as f:
    json.dump(all_projects, f, indent=2, ensure_ascii=False)
    
# CSV
fieldnames = ["numeric_id", "project_id", "title", "url", "department", "release_date", "due_date", "document_count", "documents", "page", "scraped_at"]
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for p in all_projects:
        p_copy = dict(p)
        p_copy["documents"] = " | ".join(p.get("documents", []))
        writer.writerow(p_copy)

print(f"\n{'='*50}")
print(f"DONE: {len(all_projects)} projects with document indexes")
print(f"JSON: {OUT_PROJECTS}")
print(f"CSV: {OUT_CSV}")
total_docs = sum(p.get("document_count", 0) for p in all_projects)
print(f"Total documents available: {total_docs}")