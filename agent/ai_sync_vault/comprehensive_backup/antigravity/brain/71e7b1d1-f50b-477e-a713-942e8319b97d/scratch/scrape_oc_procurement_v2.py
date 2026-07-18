"""
scrape_oc_procurement_v2.py — Full OC procurement scraper using undetected-chromedriver
Bypasses Cloudflare Turnstile, extracts ALL projects across ALL pages, saves CSV + JSON
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time, json, csv, re, sys
from pathlib import Path
from datetime import datetime

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
OUT_JSON = WORK_DIR / "oc_procurement_projects.json"
OUT_CSV = WORK_DIR / "oc_procurement_projects.csv"

BASE_URL = "https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page={page}&limit=50&sortField=proposalDeadline&sortDirection=DESC"

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")

def extract_projects_from_page(driver):
    """Extract project data from the ReactTable on the current page"""
    projects = []
    
    try:
        # Find all data rows (rt-tr inside rt-tbody)
        rows = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr-group .rt-tr")
        
        for row in rows:
            try:
                cells = row.find_elements(By.CSS_SELECTOR, ".rt-td")
                if len(cells) >= 5:
                    title_el = cells[0].find_element(By.TAG_NAME, "a") if cells[0].find_elements(By.TAG_NAME, "a") else cells[0]
                    title = title_el.text.strip()
                    
                    project_id = cells[1].text.strip()
                    status = cells[2].text.strip()
                    addenda = cells[3].text.strip() if len(cells) > 3 else ""
                    release_date = cells[4].text.strip() if len(cells) > 4 else ""
                    due_date = cells[5].text.strip() if len(cells) > 5 else ""
                    
                    # Get the project link
                    link_el = cells[0].find_elements(By.TAG_NAME, "a")
                    url = link_el[0].get_attribute("href") if link_el else ""
                    
                    if title:
                        projects.append({
                            "title": title,
                            "project_id": project_id,
                            "status": status,
                            "addenda": addenda,
                            "release_date": release_date,
                            "due_date": due_date,
                            "url": url,
                            "department": "",
                            "category": "",
                            "description": "",
                            "page": 0,  # filled later
                            "scraped_at": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"  Row parse error: {e}")
                continue
    except Exception as e:
        print(f"  Extract error: {e}")
    
    return projects


def get_pagination_info(driver):
    """Get total page count and current page"""
    try:
        # Look for pagination controls
        # ReactTable pagination typically shows "Page X of Y" or has page buttons
        page_info = driver.find_elements(By.CSS_SELECTOR, ".-pagination, .pagination-bottom, [class*='pagination']")
        for pi in page_info:
            text = pi.text
            # Try to find total count
            match = re.search(r'(\d+)\s*-\s*(\d+)\s*of\s*(\d+)', text)
            if match:
                return int(match.group(3))
            
            # Or look for page buttons
            buttons = pi.find_elements(By.TAG_NAME, "button")
            if buttons:
                # Get last numeric button
                nums = []
                for b in buttons:
                    try:
                        n = int(b.text.strip())
                        nums.append(n)
                    except ValueError:
                        pass
                if nums:
                    return max(nums)  # This is the total number of pages
        
        # Fallback: count page buttons
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        page_nums = []
        for b in all_buttons:
            try:
                n = int(b.text.strip())
                page_nums.append(n)
            except:
                pass
        if page_nums:
            return max(page_nums)
        
    except Exception as e:
        print(f"  Pagination error: {e}")
    
    return 0


def click_next_page(driver, current_page):
    """Click the next page button"""
    try:
        # Try the 'Next' button
        next_btns = driver.find_elements(By.CSS_SELECTOR, 
            "button.-next, button.next, button:has-text('Next'), [aria-label='Next Page'], button.-btn:last-child")
        
        for btn in next_btns:
            try:
                if btn.is_enabled() and btn.is_displayed():
                    btn.click()
                    return True
            except:
                continue
        
        # Try clicking a specific page number
        next_num = current_page + 1
        page_btns = driver.find_elements(By.CSS_SELECTOR, "button")
        for btn in page_btns:
            try:
                if btn.text.strip() == str(next_num) and btn.is_enabled():
                    btn.click()
                    return True
            except:
                continue
        
    except Exception as e:
        print(f"  Next page error: {e}")
    
    return False


def main():
    print("Launching undetected Chrome...")
    driver = uc.Chrome(options=options, version_main=149)
    
    all_projects = []
    page = 1
    max_pages = 100  # safety limit
    
    try:
        while page <= max_pages:
            url = BASE_URL.format(page=page)
            print(f"\n{'='*60}")
            print(f"PAGE {page}: {url[:100]}...")
            
            if page == 1:
                driver.get(url)
            else:
                driver.get(url)
            
            time.sleep(6)  # wait for React to render
            
            # Extract projects
            projects = extract_projects_from_page(driver)
            
            if not projects:
                print("  No projects found on this page - stopping")
                break
            
            # Set page number
            for p in projects:
                p["page"] = page
            
            all_projects.extend(projects)
            
            print(f"  Extracted {len(projects)} projects (total: {len(all_projects)})")
            for p in projects[:3]:
                print(f"    {p['project_id']} | {p['status']} | {p['title'][:60]} | Due: {p['due_date']}")
            
            # Check if there are more pages
            if page == 1:
                total_pages = get_pagination_info(driver)
                if total_pages > 0:
                    max_pages = min(total_pages, max_pages)
                    print(f"  Total pages detected: {total_pages}")
            
            # Check if there's a next page
            if page < max_pages:
                has_next = click_next_page(driver, page)
                if has_next:
                    page += 1
                    time.sleep(3)
                else:
                    print("  No next page button - stopping")
                    break
            else:
                break
    
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
    
    # Save results
    print(f"\n{'='*60}")
    print(f"TOTAL PROJECTS: {len(all_projects)}")
    
    # Remove duplicates
    seen = set()
    unique = []
    for p in all_projects:
        key = p.get("project_id", "") + p.get("title", "")
        if key not in seen:
            seen.add(key)
            unique.append(p)
    print(f"UNIQUE: {len(unique)} (removed {len(all_projects) - len(unique)} duplicates)")
    
    # Save JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    print(f"JSON saved: {OUT_JSON}")
    
    # Save CSV
    fieldnames = ["title", "project_id", "status", "addenda", "release_date", "due_date", "url", "department", "category", "description", "page", "scraped_at"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique)
    print(f"CSV saved: {OUT_CSV}")
    
    # Print summary by status
    statuses = {}
    for p in unique:
        s = p.get("status", "Unknown")
        statuses[s] = statuses.get(s, 0) + 1
    print("\nBy Status:")
    for s, c in sorted(statuses.items()):
        print(f"  {s}: {c}")


if __name__ == "__main__":
    main()