import asyncio
import random
import os
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# Setup targets and output paths
TARGETS = ["TS MARKETPLACE LLC", "19822 BROOKHURST", "CM CLEANING", "STEWART INDUSTRIES"]
OUTPUT_DIR = "osint-agent/sos_scrapes/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def search_sos(playwright, target):
    """
    Navigates to the CA SOS portal, searches for a business, and saves a screenshot.
    """
    print(f"[+] Searching for: {target}")
    browser = await playwright.chromium.launch(headless=False) # Headful for debugging
    context = await browser.new_context()
    page = await context.new_page()
    
    # Apply stealth to the page
    await stealth_async(page)

    try:
        # Go to the search page
        await page.goto("https://bizfileonline.sos.ca.gov/search/business", timeout=60000)
        
        # Wait for the search input to be visible
        await page.wait_for_selector('input[aria-label="search-input"]', timeout=30000)
        
        # Fill in the search term and press Enter
        await page.fill('input[aria-label="search-input"]', target)
        await page.press('input[aria-label="search-input"]', 'Enter')
        
        # Wait for navigation/results to load
        await page.wait_for_load_state('networkidle', timeout=30000)
        
        # Take a screenshot of the results
        screenshot_path = os.path.join(OUTPUT_DIR, f"{target.replace(' ', '_').lower()}_results.png")
        await page.screenshot(path=screenshot_path)
        print(f"  [+] Saved screenshot to {screenshot_path}")

    except Exception as e:
        print(f"  [-] An error occurred while searching for {target}: {e}")
    finally:
        await browser.close()
        print(f"[+] Finished search for: {target}")

async def main():
    async with async_playwright() as p:
        tasks = [search_sos(p, target) for target in TARGETS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
