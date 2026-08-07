"""
scrape_oc_procurement_v3.py — Full scraper with working pagination
27 pages x 50 projects = ~1,350 total
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time, json, csv, re
from pathlib import Path
from datetime import datetime

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
OUT_JSON = WORK_DIR / "oc_procurement_projects.json"
OUT_CSV = WORK_DIR / "oc_procurement_projects.csv"

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--incognito")
# Use a fresh temp user data dir each run
import tempfile, os
tmpdir = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={tmpdir}")


def extract_projects(driver, page_num):
    """Extract all projects from current ReactTable page"""
    projects = []
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr-group .rt-tr")
        for row in rows:
            try:
                cells = row.find_elements(By.CSS_SELECTOR, ".rt-td")
                if len(cells) < 3:
                    continue
                
                # Title from anchor inside first cell
                title = ""
                url = ""
                try:
                    link = cells[0].find_element(By.TAG_NAME, "a")
                    title = link.text.strip()
                    url = link.get_attribute("href") or ""
                except:
                    title = cells[0].text.strip()
                
                project_id = cells[1].text.strip() if len(cells) > 1 else ""
                status = cells[2].text.strip().replace("\n", " ").replace("  ", " ") if len(cells) > 2 else ""
                addenda = cells[3].text.strip() if len(cells) > 3 else ""
                release_date = cells[4].text.strip() if len(cells) > 4 else ""
                due_date = cells[5].text.strip() if len(cells) > 5 else ""
                
                if title:
                    projects.append({
                        "title": title,
                        "project_id": project_id,
                        "status": status,
                        "addenda": addenda,
                        "release_date": release_date,
                        "due_date": due_date,
                        "url": url,
                        "department": status.split("\n")[0] if "\n" in status else "",
                        "category": "",
                        "description": "",
                        "page": page_num,
                        "scraped_at": datetime.now().isoformat()
                    })
            except StaleElementReferenceException:
                continue
            except Exception as e:
                continue
    except Exception as e:
        print(f"  Extract error: {e}")
    
    return projects


def click_next_button(driver):
    """Click the Next page button in ReactTable pagination"""
    try:
        # Strategy 1: Find button containing exactly "Next"
        buttons = driver.find_elements(By.CSS_SELECTOR, 
            ".rt-pagination button, .-pagination button, [class*='pagination'] button")
        for btn in buttons:
            try:
                if btn.is_enabled() and btn.is_displayed():
                    text = btn.text.strip()
                    if text == "Next":
                        btn.click()
                        return True
            except StaleElementReferenceException:
                continue
        
        # Strategy 2: Find by aria or title
        for selector in ['button[aria-label="Next Page"]', 'button[aria-label="Next"]', 
                         'button[title="Next"]', 'button.-next', 'button.next']:
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in btns:
                    if btn.is_enabled() and btn.is_displayed():
                        btn.click()
                        return True
            except:
                continue
        
        # Strategy 3: Find the last button in pagination row
        pagination_row = driver.find_elements(By.CSS_SELECTOR, 
            ".-pagination, .rt-pagination, [class*='pagination-bottom']")
        if pagination_row:
            buttons = pagination_row[0].find_elements(By.TAG_NAME, "button")
            if buttons:
                # Next is usually the last enabled button
                for btn in reversed(buttons):
                    try:
                        if btn.is_enabled() and btn.is_displayed():
                            text = btn.text.strip()
                            if text in ("Next", ">", "»", "Next Page"):
                                btn.click()
                                return True
                            # If it's the last button and it's enabled, it's probably Next
                            if btn == buttons[-1] and text != "Previous":
                                btn.click()
                                return True
                    except:
                        continue
        
        # Strategy 4: Click the button that looks like last in pagination
        # The ReactTable has a specific structure with Previous | 1 | 2 | 3 | ... | Next
        all_page_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(@class, '-btn') or contains(@class, '-pageBtn') or contains(@class, 'page')]")
        if len(all_page_buttons) >= 2:
            # The last enabled button is usually Next
            enabled = [b for b in all_page_buttons if b.is_enabled()]
            if enabled:
                enabled[-1].click()
                return True
                
    except Exception as e:
        print(f"  Pagination click error: {e}")
    
    return False


def get_total_pages(driver):
    """Get total page count from pagination text"""
    try:
        pagination = driver.find_elements(By.CSS_SELECTOR, 
            ".-pagination, .rt-pagination, [class*='pagination-bottom']")
        for p in pagination:
            text = p.text
            # "Page 1 of 27"
            match = re.search(r'Page\s+\d+\s+of\s+(\d+)', text)
            if match:
                return int(match.group(1))
            # "Showing 1-50 of 1350"
            match = re.search(r'of\s+(\d+)', text)
            if match:
                total_items = int(match.group(1))
                return (total_items + 49) // 50  # ceil division by 50
    except:
        pass
    return 0


def main():
    print("Launching undetected Chrome (v149)...")
    driver = uc.Chrome(options=options, version_main=149)
    
    all_projects = []
    total_pages = 0
    
    try:
        # Load page 1
        url = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=proposalDeadline&sortDirection=DESC"
        print(f"Loading: {url[:90]}...")
        driver.get(url)
        time.sleep(10)
        
        # Wait for ReactTable to actually render data
        print("Waiting for ReactTable to render...")
        for attempt in range(10):
            rows = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr")
            if rows:
                print(f"  Table rendered with {len(rows)} rows after {attempt+1} attempts")
                break
            time.sleep(2)
        else:
            print("  Table never rendered. Dumping page state...")
            body = driver.find_element(By.TAG_NAME, "body").text
            print(f"  Body text (first 500): {body[:500]}")
        
        # Detect total pages
        total_pages = get_total_pages(driver)
        print(f"Total pages detected from pagination: {total_pages}")
        
        # Try to read page count from the ReactTable footer
        if total_pages <= 1:
            try:
                pagination_text = driver.find_element(By.CSS_SELECTOR, ".-pagination").text
                print(f"  Pagination raw text: {pagination_text}")
                match = re.search(r'Page\s+\d+\s+of\s+(\d+)', pagination_text)
                if match:
                    total_pages = int(match.group(1))
                    print(f"  Parsed total pages: {total_pages}")
            except:
                pass
        
        if total_pages <= 1:
            total_pages = 27  # fallback from source analysis
            print(f"Using fallback: {total_pages} pages")
        
        for page in range(1, total_pages + 1):
            # For page > 1, we click Next instead of reloading URL
            if page > 1:
                driver.get(f"https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page}&limit=50&sortField=proposalDeadline&sortDirection=DESC")
                time.sleep(6)
                # Wait for rows to appear
                for _ in range(5):
                    if driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr"):
                        break
                    time.sleep(1)
            
            print(f"\n--- PAGE {page}/{total_pages} ---")
            
            # Extract
            projects = extract_projects(driver, page)
            all_projects.extend(projects)
            
            print(f"  Got {len(projects)} projects (running total: {len(all_projects)})")
            if projects:
                p = projects[0]
                print(f"  First: [{p['project_id']}] {p['title'][:60]} | {p['status']} | Due: {p['due_date']}")
                if len(projects) > 1:
                    p = projects[-1]
                    print(f"  Last:  [{p['project_id']}] {p['title'][:60]} | {p['status']} | Due: {p['due_date']}")
            
            if not projects:
                print("  Empty page - stopping")
                break
            
            # Brief pause between pages
            if page < total_pages:
                time.sleep(2)
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
    
    # Deduplicate
    seen = set()
    unique = []
    for p in all_projects:
        key = (p.get("project_id", ""), p.get("title", ""))
        if key not in seen:
            seen.add(key)
            unique.append(p)
    
    print(f"\n{'='*60}")
    print(f"SCRAPED: {len(all_projects)} | UNIQUE: {len(unique)} | Removed {len(all_projects)-len(unique)} dupes")
    
    # Save
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    print(f"JSON: {OUT_JSON} ({len(unique)} projects)")
    
    fieldnames = ["title", "project_id", "status", "addenda", "release_date", "due_date", 
                  "url", "department", "category", "description", "page", "scraped_at"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique)
    print(f"CSV: {OUT_CSV}")
    
    # Stats
    statuses = {}
    for p in unique:
        s = p.get("status", "Unknown")
        statuses[s] = statuses.get(s, 0) + 1
    print(f"\nStatus breakdown:")
    for s, c in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")
    
    # Open projects specifically
    open_count = sum(1 for p in unique if p.get("status", "").startswith("Open"))
    print(f"\nOPEN: {open_count} | TOTAL: {len(unique)}")


if __name__ == "__main__":
    main()
