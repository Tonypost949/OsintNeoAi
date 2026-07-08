"""
Try direct IP access and alternative CA SOS endpoints
"""
import asyncio, json, socket
from pathlib import Path
from playwright.async_api import async_playwright

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
SEARCHES = [
    "TRIUMVIRATE LLC",
    "TS MARKETPLACE LLC",
    "19822 BROOKHURST LLC",
    "CM CLEANING SOLUTIONS INC",
    "STEWART INDUSTRIES LLC",
]

async def try_urls(term: str) -> dict:
    results = []
    queries = {
        "businesssearch": f"https://businesssearch.sos.ca.gov/?searchTerm={term.replace(' ', '+')}",
        "bizfile": f"https://bizfileonline.sos.ca.gov/search/search?searchType=entity&searchName={term.replace(' ', '+')}",
        "sosca_main": f"https://www.sos.ca.gov/business/bbs-search/",
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        for name, url in queries.items():
            print(f"  Trying: {name}")
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(3000)
                status = resp.status if resp else "no_response"
                text = await page.inner_text("body")
                blocked = "incapsula" in text.lower() or "access denied" in text.lower()
                results.append({
                    "source": name,
                    "url": url,
                    "status": status,
                    "blocked": blocked,
                    "preview": text[:500]
                })
                print(f"    Status: {status}, Blocked: {blocked}, Text: {text[:200]}")
            except Exception as e:
                results.append({"source": name, "url": url, "error": str(e)})
                print(f"    Error: {e}")

        await browser.close()
    return {"term": term, "results": results}

async def main():
    all_results = []
    for term in SEARCHES:
        print(f"\n=== {term} ===")
        r = await try_urls(term)
        all_results.append(r)
        await asyncio.sleep(2)

    out = WORK_DIR / "ca_sos_alt_urls_results.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    asyncio.run(main())
