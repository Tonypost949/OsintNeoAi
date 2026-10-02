import asyncio
from playwright.async_api import async_playwright

async def submit_amapulse_form():
    async with async_playwright() as p:
        # Launch Chromium using existing Playwright persistent session if available
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to Amapulse website / starter plan claim page
        print("Navigating to Amapulse website...")
        try:
            await page.goto("https://www.google.com/search?q=Amapulse+free+starter+plan", timeout=30000)
            await page.wait_for_timeout(3000)
            print("Page loaded successfully.")
        except Exception as e:
            print(f"Error navigating: {e}")
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(submit_amapulse_form())
