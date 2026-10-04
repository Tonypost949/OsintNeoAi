import asyncio
import os
import re
import time
from playwright.async_api import async_playwright
import fitz  # PyMuPDF

ENTITIES = [
    "TRIUMVIRATE LLC",
    "TS MARKETPLACE LLC",
    "19822 BROOKHURST LLC",
    "CM CLEANING SOLUTIONS INC",
    "STEWART INDUSTRIES LLC"
]

OUT_DIR = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\opencode_work"
os.makedirs(OUT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        # Launch headful chromium to bypass bot protection
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        print("Navigating to CA SOS Business Search...")
        await page.goto("https://bizfileonline.sos.ca.gov/search/business", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        for name in ENTITIES:
            print(f"\n=========================================")
            print(f"Searching for: {name}")
            print(f"=========================================")
            try:
                # Wait for search input to be stable and visible
                await page.locator(".search-input").first.wait_for(state="visible", timeout=15000)
                # Fill search input directly
                await page.locator(".search-input").first.fill(name)
                await page.wait_for_timeout(1000)
                # Click the search button or press Enter
                search_btn = page.locator(".search-button").first
                if await search_btn.is_visible():
                    await search_btn.click()
                else:
                    await page.locator(".search-input").first.press("Enter")
                await page.wait_for_timeout(4000)
                
                # Try to click on the matching element in the results
                # SOS bizfile lists matches in a table grid. Let's find cells matching the name
                target_locator = page.get_by_text(name, exact=False).first
                if await target_locator.is_visible():
                    print(f"Found matching element, clicking...")
                    await target_locator.click()
                    await page.wait_for_timeout(3000)
                    
                    # Check if View History button is visible and click it
                    view_history_btn = page.get_by_text("View History").first
                    if not await view_history_btn.is_visible():
                        # Try button locator
                        view_history_btn = page.locator("button:has-text('View History')").first
                        
                    if await view_history_btn.is_visible():
                        print("Clicking View History...")
                        await view_history_btn.click()
                        await page.wait_for_timeout(3000)
                        
                        # In the history modal, click "Expand All"
                        expand_btn = page.locator("button:has-text('Expand All')").first
                        if await expand_btn.is_visible():
                            await expand_btn.click()
                            await page.wait_for_timeout(2000)
                        
                        # Locate download links
                        links = page.locator("a:has-text('Download')")
                        link_count = await links.count()
                        print(f"Found {link_count} download links.")
                        
                        # Download the first link (most recent Statement of Information)
                        if link_count > 0:
                            print("Triggering download...")
                            async with page.expect_download() as download_info:
                                await links.first.click()
                            download = await download_info.value
                            
                            # Save download
                            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
                            pdf_path = os.path.join(OUT_DIR, f"{safe_name}_filing.pdf")
                            await download.save_as(pdf_path)
                            print(f"Saved filing PDF to: {pdf_path}")
                            
                            # Parse PDF
                            try:
                                doc = fitz.open(pdf_path)
                                text = ""
                                for page_num in range(len(doc)):
                                    text += f"\n--- Page {page_num+1} ---\n" + doc[page_num].get_text()
                                doc.close()
                                
                                txt_path = os.path.join(OUT_DIR, f"{safe_name}_officers.txt")
                                with open(txt_path, "w", encoding="utf-8") as f:
                                    f.write(text)
                                print(f"Extracted text saved to: {txt_path}")
                                
                                # Analyze extracted text for officers
                                print("Parsing officers from PDF...")
                                lines = [line.strip() for line in text.split("\n") if line.strip()]
                                # Write out key lines matching names/addresses
                                for line in lines[:40]:
                                    print(f"  {line}")
                            except Exception as pdf_err:
                                print(f"Error parsing PDF: {pdf_err}")
                        else:
                            print("No download links found in history.")
                            
                        # Close the history modal
                        close_btn = page.locator("button.close-button, button:has-text('Close')").first
                        if await close_btn.is_visible():
                            await close_btn.click()
                            await page.wait_for_timeout(1000)
                    else:
                        print("View History button not found/visible.")
                        
                        # Let's take a screenshot of the drawer to see if officers are shown directly
                        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
                        screenshot_path = os.path.join(OUT_DIR, f"{safe_name}_drawer.png")
                        await page.screenshot(path=screenshot_path)
                        print(f"Saved drawer screenshot to {screenshot_path}")
                else:
                    print(f"Could not find matching text for: {name}")
                    
            except Exception as e:
                print(f"Error searching for {name}: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
