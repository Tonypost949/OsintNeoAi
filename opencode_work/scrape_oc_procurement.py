"""
scrape_oc_procurement.py — Scrape Orange County OpenGov procurement portal
All projects across all pages -> JSON + CSV -> BigQuery
"""
import asyncio, json, csv, re, sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
OUT_JSON = WORK_DIR / "oc_procurement_projects.json"
OUT_CSV = WORK_DIR / "oc_procurement_projects.csv"
SCREENSHOTS = WORK_DIR / "procurement_screenshots"
SCREENSHOTS.mkdir(exist_ok=True)

BASE_URL = "https://procurement.opengov.com/portal/ocgov"

def fmt(v):
    return str(v).strip() if v else ""

async def extract_page_data(page, page_num):
    print(f"\n--- PAGE {page_num} ---")
    await page.wait_for_timeout(3000)
    
    projects = []
    
    # Try to find project cards/rows — OpenGov uses various layouts
    # Strategy: look for structured data via multiple approaches
    
    # 1. Try card-based layout
    cards = await page.query_selector_all('[class*="card"], [class*="project"], [class*="listing"], [class*="result"], [class*="row"]')
    print(f"  Found {len(cards)} potential containers")
    
    # 2. Try table rows
    table_rows = await page.query_selector_all("table tbody tr, table tr")
    print(f"  Found {len(table_rows)} table rows")
    
    # 3. Get all text links that look like project titles
    links = await page.query_selector_all("a")
    project_links = []
    for link in links:
        href = await link.get_attribute("href") or ""
        text = (await link.inner_text()).strip()
        if text and len(text) > 5 and ("project" in href.lower() or "bid" in href.lower() or "rfp" in href.lower() or "solicitation" in href.lower() or "portal/ocgov" in href.lower()):
            project_links.append({"text": text, "href": href})
    print(f"  Found {len(project_links)} project-looking links")
    
    # 4. Structured extraction — try to find repeating patterns
    # Check for data attributes or React/Vue component structure
    all_text = await page.inner_text("body")
    
    # 5. Try API interception approach — look for XHR/fetch responses
    # Most OpenGov portals use a REST API
    try:
        api_responses = await page.evaluate("""() => {
            const entries = performance.getEntriesByType('resource');
            return entries.filter(e => e.name.includes('api') || e.name.includes('graphql') || e.name.includes('search') || e.name.includes('portal')).map(e => e.name);
        }""")
        if api_responses:
            print(f"  API endpoints found: {api_responses[:10]}")
    except:
        pass
    
    # 6. Look for JSON-LD or embedded data
    try:
        scripts = await page.query_selector_all('script[type="application/json"], script[type="application/ld+json"], script[data-*]')
        for s in scripts:
            content = await s.inner_text()
            if 'project' in content.lower() or 'solicitation' in content.lower():
                print(f"  Found embedded JSON with project data ({len(content)} chars)")
    except:
        pass
    
    # 7. Dump visible text structure to understand page layout
    text_lines = [l.strip() for l in all_text.split('\n') if l.strip()]
    print(f"  Page text lines: {len(text_lines)}")
    print(f"  First 20 lines:")
    for line in text_lines[:20]:
        print(f"    {line[:120]}")
    
    # 8. If we found project links, collect details
    if project_links:
        for pl in project_links:
            projects.append({
                "title": pl["text"],
                "url": pl["href"],
                "department": "",
                "status": "",
                "category": "",
                "deadline": "",
                "published": "",
                "description": "",
                "page": page_num,
                "scraped_at": datetime.now().isoformat()
            })
    
    return projects, text_lines


async def main():
    all_projects = []
    all_text = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=['--no-sandbox','--disable-dev-shm-usage','--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
            bypass_csp=True
        )
        page = await context.new_page()
        # Evade bot detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
            window.chrome = {runtime: {}};
        """)
        
        print(f"Navigating to {BASE_URL}...")
        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        print("Page loaded, waiting for React hydration + Cloudflare...")
        # Wait for Cloudflare challenge to complete
        for i in range(12):
            await page.wait_for_timeout(5000)
            title = await page.title()
            print(f"  [{i*5}s] Title: {title}")
            if "Just a moment" not in title:
                print("  Cloudflare passed!")
                break
        await page.wait_for_timeout(5000)
        
        # Take initial screenshot
        await page.screenshot(path=str(SCREENSHOTS / "page_1_initial.png"), full_page=False)
        print("Screenshot saved: page_1_initial.png")
        
        # Check for Cloudflare
        content = await page.content()
        if "Checking your browser" in content or "cf-browser-verification" in content:
            print("Cloudflare detected — waiting for challenge...")
            await page.wait_for_timeout(10000)
            content = await page.content()
        
        # Dump page HTML for inspection (first 5000 chars)
        print("\n--- PAGE HTML (first 3000 chars) ---")
        print(content[:3000])
        
        # Try to find API calls by monitoring network
        api_urls = []
        def on_response(response):
            url = response.url
            if any(k in url for k in ['api', 'graphql', 'search', 'project', 'solicitation']) and response.status == 200:
                try:
                    ct = response.headers.get('content-type', '')
                    if 'json' in ct:
                        api_urls.append(url)
                        print(f"  API JSON response: {url}")
                except:
                    pass
        
        page.on("response", on_response)
        
        # Wait more for React to hydrate
        await page.wait_for_timeout(5000)
        
        # Try scrolling to trigger lazy loads
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1000)
        
        # Extract page 1
        projects, text_lines = await extract_page_data(page, 1)
        all_projects.extend(projects)
        all_text.extend(text_lines)
        
        # Try pagination — look for next page button
        page_num = 1
        while page_num < 50:  # safety limit
            next_btn = await page.query_selector_all('a[rel="next"], button:has-text("Next"), [aria-label="Next"], [class*="pagination"] button:last-child, a:has-text("Next")')
            if not next_btn:
                # Try numeric pagination
                page_num += 1
                next_btn = await page.query_selector_all(f'a:has-text("{page_num}"), button:has-text("{page_num}")')
            
            if not next_btn:
                print(f"No more pagination found. Stopping at page {page_num-1}")
                break
            
            try:
                await next_btn[0].click()
                await page.wait_for_timeout(3000)
                projects, text_lines = await extract_page_data(page, page_num)
                all_projects.extend(projects)
                all_text.extend(text_lines)
                
                await page.screenshot(path=str(SCREENSHOTS / f"page_{page_num}.png"), full_page=False)
                
                if not projects:
                    print(f"  No projects found on page {page_num}, may be end")
                    # Try once more
                    await page.wait_for_timeout(2000)
                    projects2, _ = await extract_page_data(page, page_num)
                    if not projects2:
                        break
                    all_projects.extend(projects2)
                    
            except Exception as e:
                print(f"Pagination error at page {page_num}: {e}")
                break
        
        # Final screenshot
        await page.screenshot(path=str(SCREENSHOTS / "final.png"), full_page=True)
        
        await browser.close()
    
    # Save results
    print(f"\n{'='*60}")
    print(f"TOTAL PROJECTS EXTRACTED: {len(all_projects)}")
    
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_projects, f, indent=2, ensure_ascii=False)
    print(f"JSON saved: {OUT_JSON}")
    
    if all_projects:
        # CSV
        fieldnames = ["title", "url", "department", "status", "category", "deadline", "published", "description", "page", "scraped_at"]
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_projects)
        print(f"CSV saved: {OUT_CSV}")
    
    # Save raw text for debugging
    raw_text = WORK_DIR / "oc_procurement_raw_text.txt"
    with open(raw_text, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    print(f"Raw text saved: {raw_text}")


if __name__ == "__main__":
    asyncio.run(main())