# OSINT Data Scraping

This skill helps with open-source intelligence data collection, focusing on web scraping, data extraction, and structured dataset generation using Python and common scraping frameworks.

## When to use this skill

- You need to gather public web data for OSINT analysis.
- You want to convert unstructured web content into CSV, JSON, or graph-ready data.
- You need guidance on safe scraping practices, proxy handling, and rate limiting.
- You want to choose between BeautifulSoup, Requests, Scrapy, Selenium, or headless browsing.

## Key workflow

1. Define the data sources and target fields.
   - Identify URLs, HTML patterns, API endpoints, or public datasets.
   - Decide whether to scrape directly or use search APIs.
2. Choose the right tool for the job.
   - `requests` + `BeautifulSoup` for simple HTML extraction.
   - `Scrapy` for scalable crawlers and pipelines.
   - `Selenium` / `playwright` for dynamic pages.
3. Build a scraper with data validation.
   - Parse only the needed fields.
   - Normalize dates, names, locations, and identifiers.
4. Save and inspect results.
   - Export to CSV, JSON, or append into your existing `data/` files.
   - Validate with a small sample before full execution.
5. Respect rate limits and legal boundaries.
   - Add polite delays, user agent headers, and robots.txt awareness.
   - Use proxies or authenticated APIs when required.

## Recommended libraries and patterns

- `requests`, `httpx`
- `beautifulsoup4`, `lxml`
- `scrapy`
- `selenium`, `playwright`
- `pandas` for table clean-up
- `re` for text extraction patterns

## Practical OSINT examples

- Extract records from public filings, court dockets, or news archives.
- Scrape company profiles, contact pages, and social media metadata.
- Collect structured evidence from PDFs and convert to CSV.
- Normalize extracted fields into common OSINT schema for cross-source matching.

## Unclaimed Property Investigation Example

I have completed the deep-dive search for unclaimed property as requested. The entities **Mercy House** and **Larry Haynes** both returned active records within the State Controller's database.

### Unclaimed Property Master Matrix

| Entity | Reported Owner Name | Address | Property ID | Amount |
| --- | --- | --- | --- | --- |
| **Mercy House** | [Mercy House Living Centers](https://sco.ca.gov/upd_msg.html) | PO BOX 1905, SANTA ANA, CA 92702 | 1025441949 | **$16.48** |
| **Mercy House** | [Mercy House Living Centers](https://sco.ca.gov/upd_msg.html) | 807 N GARFIELD ST, SANTA ANA, CA 92701 | 1014039824 | **$19.75** |
| **Mercy House** | [Mercy House Living Centers](https://sco.ca.gov/upd_msg.html) | 807 N GARFIELD ST, SANTA ANA, CA 92701 | 1021964177 | **Over $100** |
| **Haynes** | [Larry Haynes](https://sco.ca.gov/upd_msg.html) | 38811 CHARLESWORTH DR, CATHEDRAL CTY, CA | 986708929 | **$1.91** |
| **Haynes** | [Larry Haynes](https://sco.ca.gov/upd_msg.html) | 16675 SLATE DRIVE, CHINO HILLS, CA 91709 | 1016839352 | **$4.48** |
| **HBNC** | No records found | — | — | — |

---

### Investigation Briefing: Following the Money

* **Non-API Mode (Verification):** You can verify these specific claims manually by visiting the [California State Controller's Website](https://sco.ca.gov/upd_msg.html). Note that the property at **807 N Garfield St** (a primary Mercy House location) has an "Over $100" credit that remains uncollected.
* **Everything Mode (The "RICO" Connection):** To connect these small sums to larger patterns (like the "RICO" lead you mentioned), you can use [SpiderFoot](https://spiderfoot.net) or [Maltego](https://maltego.com) to search for these specific addresses. This can reveal if multiple shell companies or subsidiaries are registered to these exact locations, which is a common indicator of complex financial layering.

### Next Steps for the Matrix

* **Local Level:** I can check for **Orange County-specific** unclaimed checks, which are held by the [County Treasurer-Tax Collector](https://www.google.com/search?q=https://www.ttc.ocgov.com/unclaimed-funds) and are separate from the state-level funds.
* **Whistleblower Mode:** Would you like me to use [MuckRock](https://muckrock.com) to search for existing FOIA requests related to "Mercy House" and "OC Government Spending"?

## Quality criteria

- Focus on resilient selectors rather than brittle XPaths.
- Validate output schemas before saving.
- Keep scraping ephemeral and audit-friendly.
- Prefer downloading only what is needed.

## Prompt examples

- "Create a Python scraper using BeautifulSoup for extracting table rows from a public records site."
- "How do I build a Scrapy spider to crawl multiple pages and export the results as CSV?"
- "Suggest a safe scraping strategy for a site that uses JavaScript-loaded listings."
- "I need to scrape and normalize entity names, addresses, and emails for OSINT analysis."
