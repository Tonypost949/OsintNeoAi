"""
Search for virtual office operator at 333 Washington Blvd Marina del Rey
and ProPublica Nonprofit Explorer for entity data
"""
import asyncio, json, subprocess
from pathlib import Path
from playwright.async_api import async_playwright

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

SEARCHES = [
    ("google_maps", "333 Washington Blvd Marina del Rey CA 90292"),
    ("google_places", "333 Washington Blvd #142 Marina del Rey"),
    ("propublica", "TRIUMVIRATE ENVIRONMENTAL"),
    ("propublica", "STEWART INDUSTRIES"),
    ("opencorporates", "TRIUMVIRATE LLC California"),
]

async def search_google_maps(query: str) -> dict:
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(5000)
            text = await page.inner_text("body")
            return {"source": "google_maps", "query": query, "text": text[:2000]}
        except Exception as e:
            return {"source": "google_maps", "query": query, "error": str(e)}
        finally:
            await browser.close()

async def search_propublica(query: str) -> dict:
    url = f"https://projects.propublica.org/nonprofits/search?q={query.replace(' ', '+')}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            results = await page.query_selector_all("tbody tr")
            entities = []
            for r in results[:5]:
                cols = await r.query_selector_all("td")
                if len(cols) >= 3:
                    name = await cols[0].inner_text()
                    city = await cols[1].inner_text()
                    state = await cols[2].inner_text()
                    entities.append(f"{name} | {city}, {state}")
            return {"source": "propublica", "query": query, "entities": entities}
        except Exception as e:
            return {"source": "propublica", "query": query, "error": str(e)}
        finally:
            await browser.close()

async def search_opencorporates(query: str) -> dict:
    url = f"https://opencorporates.com/companies?q={query.replace(' ', '+')}&jurisdiction=us_ca"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            text = await page.inner_text("body")
            return {"source": "opencorporates", "query": query, "text": text[:2000]}
        except Exception as e:
            return {"source": "opencorporates", "query": query, "error": str(e)}
        finally:
            await browser.close()

async def main():
    all_results = []
    for source, query in SEARCHES:
        print(f"\n=== {source}: {query} ===")
        if source == "google_maps":
            r = await search_google_maps(query)
        elif source == "propublica":
            r = await search_propublica(query)
        elif source == "opencorporates":
            r = await search_opencorporates(query)
        else:
            continue

        print(f"  Result: {str(r)[:300]}")
        all_results.append(r)
        await asyncio.sleep(3)

    out = WORK_DIR / "entity_lookups_results.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    asyncio.run(main())
