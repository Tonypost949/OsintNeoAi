import asyncio
from playwright.async_api import async_playwright
import json
import os

async def scrape_bannon():
    print("Starting Playwright scrape for Patrick Bannon footprint...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        queries = [
            '"Patrick Bannon" "Huntington Beach"',
            '"Patrick Bannon" "Ardebili"',
            '"Patrick Bannon" "Sprung" engineering',
            'bannonp engineering huntington beach'
        ]
        
        results = []
        
        for q in queries:
            print(f"Searching: {q}")
            try:
                await page.goto(f'https://html.duckduckgo.com/html/?q={q}', timeout=30000)
                await page.wait_for_selector('.result__title', timeout=10000)
                
                links = await page.query_selector_all('.result__snippet')
                titles = await page.query_selector_all('.result__title')
                
                for t, l in zip(titles, links):
                    title_text = await t.inner_text()
                    snippet_text = await l.inner_text()
                    href = await t.eval_on_selector('a', 'el => el.href') if await t.query_selector('a') else None
                    results.append({
                        "query": q,
                        "title": title_text.strip(),
                        "snippet": snippet_text.strip(),
                        "url": href
                    })
            except Exception as e:
                print(f"Error on query {q}: {e}")
                
        await browser.close()
        
        out_path = r"C:\OsintNeoAi\evidence\bannon_network_scrape.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        
        print(f"Scrape complete. Found {len(results)} results. Saved to {out_path}")

if __name__ == "__main__":
    asyncio.run(scrape_bannon())
