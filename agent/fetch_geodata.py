#!/usr/bin/env python3
"""
Fetch GeoData - Populates marker cache for CityCyberReconMap
Combines IP geolocation with domain recon data from BigQuery.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from city_ip_geolocation_v2 import CityIPGeolocator
except ImportError:
    print("[!] city_ip_geolocation_v2 not found, using basic mode")
    CityIPGeolocator = None

try:
    from google.cloud import bigquery
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False
    print("[!] google-cloud-bigquery not available, using local data only")


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'opencode_work')
CACHE_FILE = os.path.join(CACHE_DIR, 'city_markers_cache.json')
BQ_PROJECT = 'project-743aab84-f9a5-4ec7-954'


def get_bq_targets() -> List[Dict]:
    """Fetch target domains from BigQuery."""
    if not BQ_AVAILABLE:
        print("[!] BigQuery not available, using default target list")
        return get_default_targets()

    try:
        bq = bigquery.Client(project=BQ_PROJECT)
        query = """
        SELECT DISTINCT domain, city, state, org_type, risk_score
        FROM `ppp_rico.city_targets`
        WHERE active = TRUE
        LIMIT 100
        """
        results = bq.query(query).result()
        targets = [dict(row) for row in results]
        print(f"[+] Fetched {len(targets)} targets from BigQuery")
        return targets
    except Exception as e:
        print(f"[!] BigQuery query failed: {e}")
        return get_default_targets()


def get_default_targets() -> List[Dict]:
    """Default target list when BigQuery is unavailable."""
    return [
        {"domain": "huntingtonbeachca.gov", "city": "Huntington Beach", "state": "CA", "org_type": "municipal"},
        {"domain": "newportbeachca.gov", "city": "Newport Beach", "state": "CA", "org_type": "municipal"},
        {"domain": "santamonica.gov", "city": "Santa Monica", "state": "CA", "org_type": "municipal"},
        {"domain": "cityofirvine.org", "city": "Irvine", "state": "CA", "org_type": "municipal"},
        {"domain": "lacity.org", "city": "Los Angeles", "state": "CA", "org_type": "municipal"},
        {"domain": "santaana.gov", "city": "Santa Ana", "state": "CA", "org_type": "municipal"},
        {"domain": "anaheim.net", "city": "Anaheim", "state": "CA", "org_type": "municipal"},
        {"domain": "fullertonca.gov", "city": "Fullerton", "state": "CA", "org_type": "municipal"},
        {"domain": "ocgov.com", "city": "Orange County", "state": "CA", "org_type": "county"},
    ]


def resolve_domain_to_ip(domain: str) -> Optional[str]:
    """Resolve domain to IP address."""
    import socket
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None


def fetch_marker_data(use_cache: bool = True) -> List[Dict]:
    """Fetch and geolocate all target IPs for map markers."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Load cache if available
    cache = {}
    if use_cache and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        print(f"[+] Loaded {len(cache)} cached markers")

    targets = get_bq_targets()
    geolocator = CityIPGeolocator() if CityIPGeolocator else None
    markers = []

    for target in targets:
        domain = target.get('domain', '')
        city = target.get('city', '')
        state = target.get('state', '')

        # Check cache first
        if domain in cache:
            markers.append(cache[domain])
            continue

        # Resolve domain to IP
        ip = resolve_domain_to_ip(domain)
        if not ip:
            print(f"[!] Could not resolve {domain}")
            continue

        # Geolocate
        geo_data = None
        if geolocator:
            geo_data = geolocator.geolocate_ip(ip)
        else:
            # Basic fallback without geoip2
            geo_data = {
                "ip": ip,
                "city": city,
                "region": state,
                "country": "US",
                "lat": None,
                "lon": None,
                "source": "default"
            }

        if geo_data:
            marker = {
                "id": domain,
                "domain": domain,
                "ip": ip,
                "city": geo_data.get('city', city),
                "state": geo_data.get('region', state),
                "country": geo_data.get('country', 'US'),
                "lat": geo_data.get('lat'),
                "lng": geo_data.get('lon'),
                "isp": geo_data.get('isp'),
                "org": geo_data.get('org'),
                "org_type": target.get('org_type', 'unknown'),
                "risk_score": target.get('risk_score', 0),
                "source": geo_data.get('source', 'unknown'),
                "last_updated": datetime.utcnow().isoformat()
            }
            cache[domain] = marker
            markers.append(marker)
            print(f"[+] {domain} -> {ip} ({marker['city']}, {marker['state']})")
        else:
            print(f"[!] Could not geolocate {domain} ({ip})")

    # Save cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    print(f"[+] Saved {len(cache)} markers to {CACHE_FILE}")

    return markers


def get_cache_stats() -> Dict:
    """Get statistics about the marker cache."""
    if not os.path.exists(CACHE_FILE):
        return {"total": 0, "cached": 0, "file": CACHE_FILE}

    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)

    return {
        "total": len(cache),
        "cached": len(cache),
        "file": CACHE_FILE,
        "cities": list(set(m.get('city', 'Unknown') for m in cache.values())),
        "last_updated": max((m.get('last_updated', '') for m in cache.values()), default='never')
    }


def main():
    """CLI interface."""
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        stats = get_cache_stats()
        print(json.dumps(stats, indent=2))
        return

    no_cache = "--no-cache" in sys.argv
    markers = fetch_marker_data(use_cache=not no_cache)

    print(f"\n[+] Total markers: {len(markers)}")
    print(f"[+] Cache file: {CACHE_FILE}")

    # Print summary by city
    cities = {}
    for m in markers:
        city = m.get('city', 'Unknown')
        cities[city] = cities.get(city, 0) + 1

    print("\n[+] Markers by city:")
    for city, count in sorted(cities.items()):
        print(f"    {city}: {count}")


if __name__ == "__main__":
    main()
