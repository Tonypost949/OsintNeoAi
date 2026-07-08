#!/usr/bin/env python3
"""
tavares_expander.py — Expand Kimberly Tavares portfolio from CA SOS.
Searches bizfileonline.sos.ca.gov by agent name, extracts all linked entities.
No API keys. Pure requests + BeautifulSoup.
Run from Cloud Workstation (local machine blocked by Incapsula WAF).
"""

import requests
import csv
import re
import time
from datetime import datetime, timezone
from pathlib import Path

AGENT_NAME = "Kimberly Tavares"
SEARCH_URL = "https://businesssearch.sos.ca.gov/DocumentSearch/Search"
DETAIL_URL = "https://businesssearch.sos.ca.gov/DocumentSearch/Detail"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://businesssearch.sos.ca.gov",
    "Referer": "https://businesssearch.sos.ca.gov/",
}


def search_by_agent(session, agent_name, page=1):
    data = {
        "SearchType": "CORP",
        "SearchCriteria": agent_name,
        "SearchSubType": "Agent",
        "page": page,
    }
    try:
        resp = session.post(SEARCH_URL, data=data, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  Search failed page {page}: {e}")
        return None


def extract_entities(html):
    entities = []
    rows = re.findall(r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>.*?</tr>', html, re.DOTALL)
    for name_raw, num_raw in rows:
        name = re.sub(r'<[^>]+>', '', name_raw).strip()
        num = re.sub(r'<[^>]+>', '', num_raw).strip()
        if name and num:
            entities.append({"name": name, "entity_number": num})
    return entities


def get_entity_details(session, entity_number):
    try:
        resp = session.get(f"{DETAIL_URL}?id={entity_number}", headers=HEADERS, timeout=30)
        html = resp.text

        agent_match = re.search(r'Agent for Service of Process.*?<td[^>]*>(.*?)</td>', html, re.DOTALL | re.IGNORECASE)
        agent = re.sub(r'<[^>]+>', '', agent_match.group(1)).strip() if agent_match else ""

        addr_match = re.search(r'Address.*?<td[^>]*>(.*?)</td>', html, re.DOTALL | re.IGNORECASE)
        addr = re.sub(r'<[^>]+>', '', addr_match.group(1)).strip() if addr_match else ""

        status_match = re.search(r'Status.*?<td[^>]*>(.*?)</td>', html, re.DOTALL | re.IGNORECASE)
        status = re.sub(r'<[^>]+>', '', status_match.group(1)).strip() if status_match else "Unknown"

        filing_match = re.search(r'Filing Date.*?<td[^>]*>(.*?)</td>', html, re.DOTALL | re.IGNORECASE)
        filing_date = re.sub(r'<[^>]+>', '', filing_match.group(1)).strip() if filing_match else ""

        type_match = re.search(r'Type.*?<td[^>]*>(.*?)</td>', html, re.DOTALL | re.IGNORECASE)
        entity_type = re.sub(r'<[^>]+>', '', type_match.group(1)).strip() if type_match else ""

        return {
            "agent": agent, "address": addr, "status": status,
            "filing_date": filing_date, "entity_type": entity_type,
        }
    except Exception as e:
        print(f"  Detail failed {entity_number}: {e}")
        return {"agent": "", "address": "", "status": "Error", "filing_date": "", "entity_type": ""}


def main():
    print(f"=== TAVARES PORTFOLIO EXPANDER ===")
    print(f"Target: {AGENT_NAME}")
    print(f"Source: CA Secretary of State\n")

    session = requests.Session()
    all_entities = []
    page = 1

    while True:
        print(f"[PAGE {page}] Searching...")
        html = search_by_agent(session, AGENT_NAME, page)
        if not html:
            break

        entities = extract_entities(html)
        if not entities:
            print("  No more results.")
            break

        print(f"  Found {len(entities)} entities")
        all_entities.extend(entities)

        if 'Next' not in html and 'next' not in html.lower():
            break

        page += 1
        time.sleep(2)

    print(f"\nTotal entities: {len(all_entities)}")

    results = []
    for idx, ent in enumerate(all_entities, 1):
        print(f"  [{idx}/{len(all_entities)}] {ent['name']}")
        details = get_entity_details(session, ent["entity_number"])
        results.append({
            "entity_name": ent["name"],
            "entity_number": ent["entity_number"],
            "registered_agent": details["agent"],
            "agent_address": details["address"],
            "status": details["status"],
            "filing_date": details["filing_date"],
            "entity_type": details["entity_type"],
            "source_agent": AGENT_NAME,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
        time.sleep(1.5)

    output_path = "tavares_portfolio.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "entity_name", "entity_number", "registered_agent",
            "agent_address", "status", "filing_date", "entity_type",
            "source_agent", "scraped_at",
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n=== RESULTS ===")
    print(f"Wrote {len(results)} records to {output_path}")

    same_agent = [r for r in results if AGENT_NAME.lower() in r["registered_agent"].lower()]
    active = [r for r in results if "active" in r["status"].lower()]
    print(f"Still controlled by {AGENT_NAME}: {len(same_agent)}")
    print(f"Active entities: {len(active)}")
    print(f"Transferred/dissolved: {len(results) - len(active)}")

    print(f"\n=== ENTITY LIST ===")
    for r in results:
        flag = " <-- STILL AGENT" if AGENT_NAME.lower() in r["registered_agent"].lower() else ""
        print(f"  {r['entity_number']}  {r['entity_name'][:50]:50s}  {r['status']:15s}{flag}")


if __name__ == "__main__":
    main()
