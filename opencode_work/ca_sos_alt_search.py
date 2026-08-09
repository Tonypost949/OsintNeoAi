"""
Alternative: Use CA FTB (Franchise Tax Board) entity search which may have different DNS
Also try using Google Search cache for CA SOS results
"""
import asyncio, json, subprocess
from pathlib import Path
from playwright.async_api import async_playwright

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
SEARCHES = [
    "TRIUMVIRATE LLC California",
    "TS MARKETPLACE LLC California",
    "19822 BROOKHURST LLC California",
    "CM CLEANING SOLUTIONS INC California",
    "STEWART INDUSTRIES LLC California Secretary of State",
]

async def try_ftb_search(term: str) -> dict:
    """Try CA Franchise Tax Board entity search"""
    encoded = term.replace(' ', '+')
    url = "https://www.ftb.ca.gov/tools/business-search?name=" + encoded + "&type=Entities&status=Active"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            text = await page.inner_text("body")
            return {"source": "ftb", "term": term, "text": text[:1000], "blocked": "incapsula" in text.lower()}
        except Exception as e:
            return {"source": "ftb", "term": term, "error": str(e)}
        finally:
            await browser.close()

async def try_google_cache(term: str) -> dict:
    """Try Google cache of CA SOS search results"""
    search_url = f"https://www.google.com/search?q={term.replace(' ', '+')}+site:businesssearch.sos.ca.gov"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(2000)
            results = await page.query_selector_all("div.g")
            snippets = []
            for r in results[:5]:
                title = await r.query_selector("h3")
                snippet = await r.query_selector("div.VwiC3b")
                if title:
                    snippets.append({
                        "title": await title.inner_text(),
                        "snippet": await snippet.inner_text() if snippet else ""
                    })
            return {"source": "google", "term": term, "results": snippets[:3]}
        except Exception as e:
            return {"source": "google", "term": term, "error": str(e)}
        finally:
            await browser.close()

async def try_direct_api(term: str) -> dict:
    """Try the CA SOS API via direct IP"""
    # Try resolved IPs via curl
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "10",
             f"https://businesssearch.sos.ca.gov/api/v1/search?name={term.replace(' ', '%20')}"],
            capture_output=True, text=True, timeout=15
        )
        return {"source": "curl_api", "term": term, "response": r.stdout[:500]}
    except Exception as e:
        return {"source": "curl_api", "term": term, "error": str(e)}

async def main():
    all_results = []

    for term in SEARCHES:
        print(f"\n=== {term} ===")
        ftb = await try_ftb_search(term)
        print(f"  FTB: {'blocked' if ftb.get('blocked') else 'ok'} - {ftb.get('text', ftb.get('error', ''))[:200]}")
        all_results.append(ftb)

        google = await try_google_cache(term)
        print(f"  Google: found {len(google.get('results', []))} results")
        for g in google.get("results", [])[:3]:
            print(f"    -> {g['title']}: {g['snippet'][:100]}")
        all_results.append(google)

        api = await try_direct_api(term)
        print(f"  API: {api.get('response', api.get('error', ''))[:200]}")
        all_results.append(api)

        await asyncio.sleep(3)

    out = WORK_DIR / "ca_sos_alt_search_results.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    asyncio.run(main())
