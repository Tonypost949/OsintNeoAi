"""
osint_engine.py — Public OSINT Search Engine
==============================================
Searches free public data sources for intelligence related to investigation cases.
Sources: Google News RSS, Bing News, Data.gov, CA SOS business search.
No API keys required for core functionality.
"""

import re
import json
import time
import hashlib
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime

# Try to import requests, install if missing
try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# Smoking gun keywords for classification
SMOKING_GUN_TERMS = {
    'indictment', 'convicted', 'conviction', 'guilty plea', 'guilty',
    'fraud', 'embezzlement', 'bribery', 'corruption', 'restitution',
    'forfeiture', 'rico', 'conspiracy', 'obstruction', 'money laundering',
    'whistleblower', 'qui tam', 'false claims', 'kickback',
    'trafficking', 'exploitation', 'abuse', 'negligence',
    'arrested', 'charged', 'sentenced', 'plea deal', 'plea agreement',
    'federal investigation', 'grand jury', 'superseding indictment',
    'fbi', 'doj', 'hud oig', 'inspector general',
}


def classify_as_smoking_gun(headline: str, description: str = "") -> bool:
    """Check if a finding qualifies as a smoking gun based on keyword presence."""
    combined = (headline + " " + description).lower()
    matches = sum(1 for term in SMOKING_GUN_TERMS if term in combined)
    return matches >= 2  # Need at least 2 matches to reduce noise


def extract_tags(headline: str, description: str = "") -> List[str]:
    """Extract relevant tags from a finding's text."""
    combined = (headline + " " + description).lower()
    tags = []
    
    tag_groups = {
        'conviction': ['convicted', 'conviction', 'guilty', 'sentenced'],
        'indictment': ['indicted', 'indictment', 'charged', 'arraigned'],
        'fraud': ['fraud', 'embezzlement', 'false claims', 'double-billing'],
        'bribery': ['bribery', 'kickback', 'pay-to-play', 'corruption'],
        'restitution': ['restitution', 'forfeiture', 'settlement'],
        'conspiracy': ['conspiracy', 'rico', 'racketeering'],
        'environmental': ['toxic', 'contamination', 'chromium', 'ceqa', 'dtsc'],
        'federal': ['fbi', 'doj', 'federal', 'usao', 'u.s. attorney'],
        'audit': ['audit', 'inspector general', 'oig', 'oversight'],
        'trafficking': ['trafficking', 'exploitation'],
        'whistleblower': ['whistleblower', 'qui tam', 'relator'],
    }
    
    for tag, keywords in tag_groups.items():
        if any(kw in combined for kw in keywords):
            tags.append(tag)
    
    return tags[:5]  # Max 5 tags


def generate_finding_id(url: str, headline: str) -> str:
    """Generate a stable unique ID for deduplication."""
    raw = (url or "") + "|" + (headline or "")
    return hashlib.md5(raw.encode()).hexdigest()[:16]


# ============================================================================
#  GOOGLE NEWS RSS (No API key needed)
# ============================================================================

def search_google_news(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Google News via RSS feed. Free, no API key required."""
    findings = []
    encoded_q = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if resp.status_code != 200:
            return findings

        if HAS_BS4:
            soup = BeautifulSoup(resp.text, 'xml')
            items = soup.find_all('item')
        else:
            # Fallback: simple regex parsing of RSS XML
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            parsed_items = []
            for item_text in items:
                title_m = re.search(r'<title>(.*?)</title>', item_text)
                link_m = re.search(r'<link>(.*?)</link>', item_text)
                desc_m = re.search(r'<description>(.*?)</description>', item_text)
                pub_m = re.search(r'<pubDate>(.*?)</pubDate>', item_text)
                source_m = re.search(r'<source[^>]*>(.*?)</source>', item_text)
                parsed_items.append({
                    'title': title_m.group(1) if title_m else '',
                    'link': link_m.group(1) if link_m else '',
                    'description': desc_m.group(1) if desc_m else '',
                    'pubDate': pub_m.group(1) if pub_m else '',
                    'source': source_m.group(1) if source_m else 'google_news',
                })
            items = parsed_items

        for item in items[:max_results]:
            if HAS_BS4:
                title = item.find('title').text if item.find('title') else ''
                link = item.find('link').text if item.find('link') else ''
                desc = item.find('description').text if item.find('description') else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                source_tag = item.find('source')
                source_name = source_tag.text if source_tag else 'google_news'
            else:
                title = item.get('title', '')
                link = item.get('link', '')
                desc = item.get('description', '')
                pub_date = item.get('pubDate', '')
                source_name = item.get('source', 'google_news')
            
            # Clean HTML from description
            if HAS_BS4:
                desc = BeautifulSoup(desc, 'html.parser').get_text()
            else:
                desc = re.sub(r'<[^>]+>', '', desc)

            headline = title.strip()
            description = desc.strip()[:300]

            findings.append({
                'source': f'google_news ({source_name})',
                'headline': headline,
                'description': description,
                'url': link.strip(),
                'tags': extract_tags(headline, description),
                'is_smoking_gun': classify_as_smoking_gun(headline, description),
                'found_at': datetime.utcnow().isoformat() + 'Z',
                'dedup_id': generate_finding_id(link, headline),
            })
    except Exception as e:
        print(f"[OSINT] Google News error for '{query}': {e}")
    
    return findings


# ============================================================================
#  BING NEWS (No API key, scrapes RSS)
# ============================================================================

def search_bing_news(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Bing News via RSS feed."""
    findings = []
    encoded_q = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/news/search?q={encoded_q}&format=rss"
    
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if resp.status_code != 200:
            return findings

        # Parse RSS
        items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
        
        for item_text in items[:max_results]:
            title_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item_text)
            if not title_m:
                title_m = re.search(r'<title>(.*?)</title>', item_text)
            link_m = re.search(r'<link>(.*?)</link>', item_text)
            desc_m = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item_text)
            if not desc_m:
                desc_m = re.search(r'<description>(.*?)</description>', item_text)
            
            headline = title_m.group(1).strip() if title_m else ''
            link = link_m.group(1).strip() if link_m else ''
            desc = desc_m.group(1).strip() if desc_m else ''
            desc = re.sub(r'<[^>]+>', '', desc)[:300]
            
            if not headline:
                continue
            
            findings.append({
                'source': 'bing_news',
                'headline': headline,
                'description': desc,
                'url': link,
                'tags': extract_tags(headline, desc),
                'is_smoking_gun': classify_as_smoking_gun(headline, desc),
                'found_at': datetime.utcnow().isoformat() + 'Z',
                'dedup_id': generate_finding_id(link, headline),
            })
    except Exception as e:
        print(f"[OSINT] Bing News error for '{query}': {e}")
    
    return findings


# ============================================================================
#  DATA.GOV (Free public datasets API)
# ============================================================================

def search_data_gov(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search data.gov for relevant public datasets."""
    findings = []
    encoded_q = urllib.parse.quote_plus(query)
    url = f"https://catalog.data.gov/api/3/action/package_search?q={encoded_q}&rows={max_results}"
    
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return findings
        
        data = resp.json()
        results = data.get('result', {}).get('results', [])
        
        for item in results:
            title = item.get('title', '')
            notes = item.get('notes', '')[:300]
            org = item.get('organization', {}).get('title', 'data.gov')
            pkg_url = f"https://catalog.data.gov/dataset/{item.get('name', '')}"
            
            findings.append({
                'source': f'data.gov ({org})',
                'headline': title,
                'description': notes,
                'url': pkg_url,
                'tags': extract_tags(title, notes),
                'is_smoking_gun': classify_as_smoking_gun(title, notes),
                'found_at': datetime.utcnow().isoformat() + 'Z',
                'dedup_id': generate_finding_id(pkg_url, title),
            })
    except Exception as e:
        print(f"[OSINT] Data.gov error for '{query}': {e}")
    
    return findings


# ============================================================================
#  CA SECRETARY OF STATE (Business Search)
# ============================================================================

def search_ca_sos(query: str) -> List[Dict[str, Any]]:
    """Search California Secretary of State business records."""
    findings = []
    # CA SOS doesn't have a clean API, but we can point to the search page
    search_url = f"https://bizfileonline.sos.ca.gov/search/business"
    
    findings.append({
        'source': 'ca_sos',
        'headline': f'CA Secretary of State: Search for "{query}"',
        'description': f'Search the California Business Registry for entities matching "{query}". '
                       f'Check for LLC filings, corporate status, agent of service, and filing dates.',
        'url': search_url,
        'tags': ['business_registry', 'corporate'],
        'is_smoking_gun': False,
        'found_at': datetime.utcnow().isoformat() + 'Z',
        'dedup_id': generate_finding_id(search_url, query),
    })
    return findings


# ============================================================================
#  MASTER SEARCH FUNCTION
# ============================================================================

def run_osint_search(queries: List[str], sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Run OSINT searches across all configured sources for the given queries.
    Deduplicates results by URL+headline hash.
    
    Args:
        queries: List of search query strings
        sources: Optional list of source names to search. Default: all.
    
    Returns:
        List of finding dicts, deduplicated and sorted (smoking guns first).
    """
    if sources is None:
        sources = ['google_news', 'bing_news', 'data_gov']
    
    all_findings = []
    seen_ids = set()
    
    for query in queries:
        if 'google_news' in sources:
            for f in search_google_news(query):
                if f['dedup_id'] not in seen_ids:
                    seen_ids.add(f['dedup_id'])
                    all_findings.append(f)
            time.sleep(0.5)  # Rate limit
        
        if 'bing_news' in sources:
            for f in search_bing_news(query):
                if f['dedup_id'] not in seen_ids:
                    seen_ids.add(f['dedup_id'])
                    all_findings.append(f)
            time.sleep(0.5)
        
        if 'data_gov' in sources:
            for f in search_data_gov(query, max_results=3):
                if f['dedup_id'] not in seen_ids:
                    seen_ids.add(f['dedup_id'])
                    all_findings.append(f)
            time.sleep(0.3)
    
    # Sort: smoking guns first, then by timestamp
    all_findings.sort(key=lambda f: (not f.get('is_smoking_gun', False), f.get('found_at', '')))
    
    return all_findings


if __name__ == "__main__":
    # Quick test
    print("=== OSINT Engine Test ===")
    results = run_osint_search(["Andrew Do Orange County fraud"])
    print(f"Found {len(results)} results")
    for r in results[:5]:
        gun = "🔥 SMOKING GUN" if r['is_smoking_gun'] else ""
        print(f"  [{r['source']}] {gun} {r['headline'][:80]}")
        if r['tags']:
            print(f"    Tags: {', '.join(r['tags'])}")
