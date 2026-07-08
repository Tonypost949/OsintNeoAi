"""Quick playwright test"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com", timeout=15000)
        print(await page.title())
        await browser.close()

asyncio.run(test())
