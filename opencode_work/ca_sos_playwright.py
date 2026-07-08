"""
CA SOS Business Search using Playwright — bypasses Imperva/Incapsula anti-bot
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

SEARCHES = [
    "TRIUMVIRATE LLC",
    "TS MARKETPLACE LLC",
    "19822 BROOKHURST LLC",
    "RAI PARTNERS LLC",
    "HRAPTS1 LLC",
    "ROSELL",
    "STEWART INDUSTRIES LLC",
    "CM CLEANING SOLUTIONS INC",
    "L2T MEDIA LLC",
    "19822 BROOKHURST",
]

async def search_entity(term: str) -> dict:
    url = f"https://businesssearch.sos.ca.gov/?searchTerm={term.replace(' ', '+')}&entityType=LLC&status=Active"
    result = {"term": term, "url": url, "entities": [], "raw_text": ""}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                locale="en-US",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
            )
            page = await context.new_page()

            # Enable request interception to find API calls
            api_data = []
            def handle_response(response):
                if "api" in response.url or "json" in response.content_type:
                    api_data.append({"url": response.url, "status": response.status})

            page.on("response", handle_response)

            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)  # wait for JS to render

            # Get page title
            title = await page.title()

            # Try to find result rows — CA SOS uses Angular/DOJO style tables
            entities = []
            selectors = [
                "table.results tbody tr",
                ".search-results tr",
                "tr.entity-result",
                "table tbody tr",
            ]
            for sel in selectors:
                rows = await page.query_selector_all(sel)
                if rows:
                    print(f"    Found {len(rows)} rows with selector: {sel}")
                    for row in rows[:10]:
                        cells = await row.query_selector_all("td")
                        if len(cells) >= 2:
                            name_td = cells[0]
                            name_link = await name_td.query_selector("a")
                            name = await name_link.inner_text() if name_link else await name_td.inner_text()
                            status_td = cells[1] if len(cells) > 1 else None
                            status = await status_td.inner_text() if status_td else ""
                            entities.append({"name": name.strip(), "status": status.strip()})
                    if entities:
                        break

            # Get all text content as fallback
            if not entities:
                body_text = await page.inner_text("body")
                result["raw_text"] = body_text[:2000]
                print(f"    No table rows found. Page title: {title}")
                print(f"    Body preview: {body_text[:300]}")

            # Check for Incapsula block
            content = await page.content()
            if "Incapsula" in content or "Access Denied" in content:
                print(f"    BLOCKED by Incapsula!")
                result["blocked"] = True
            else:
                result["blocked"] = False

            result["entities"] = entities
            result["title"] = title
            result["api_calls"] = api_data[:5]

            await browser.close()
    except Exception as e:
        result["error"] = str(e)
        print(f"    Exception: {e}")

    return result

async def main():
    all_results = []
    for term in SEARCHES:
        print(f"\nSearching CA SOS: {term}")
        r = await search_entity(term)
        all_results.append(r)
        if r.get("entities"):
            for e in r["entities"]:
                print(f"  -> {e['name']} | {e['status']}")
        elif r.get("blocked"):
            print(f"  -> BLOCKED by anti-bot")
        elif r.get("raw_text"):
            print(f"  -> Got raw text: {r['raw_text'][:200]}")
        await asyncio.sleep(3)  # polite delay between requests

    out = WORK_DIR / "ca_sos_playwright_results.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved to {out}")
    print(f"Total entities found: {sum(len(r.get('entities', [])) for r in all_results)}")

if __name__ == "__main__":
    asyncio.run(main())
