#!/usr/bin/env python3
"""
City IP Geolocation - REST API Fallback Version
Uses ip-api.com (free, no key required) with geoip2 local DB as primary option.
"""

import json
import os
import sys
import time
import requests
from typing import Optional, Dict, List

# Try local geoip2 first, fallback to REST API
USE_GEOIP2 = False
try:
    import geoip2.database
    import geoip2.errors
    GEOIP2_DB_PATH = os.environ.get('GEOIP2_DB_PATH', 'GeoLite2-City.mmdb')
    if os.path.exists(GEOIP2_DB_PATH):
        USE_GEOIP2 = True
        print(f"[+] Using local geoip2 database: {GEOIP2_DB_PATH}")
except ImportError:
    print("[!] geoip2 not available, using REST API fallback")

REST_API_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting"
RATE_LIMIT_DELAY = 1.0  # 1 request per second for free tier

class CityIPGeolocator:
    def __init__(self, geoip2_db_path: Optional[str] = None):
        self.geoip2_reader = None
        if USE_GEOIP2:
            db_path = geoip2_db_path or GEOIP2_DB_PATH
            if os.path.exists(db_path):
                try:
                    self.geoip2_reader = geoip2.database.Reader(db_path)
                    print(f"[+] geoip2 reader initialized: {db_path}")
                except Exception as e:
                    print(f"[!] Failed to load geoip2 database: {e}")

    def geolocate_ip(self, ip: str) -> Optional[Dict]:
        """Geolocate a single IP address."""
        # Try local geoip2 first
        if self.geoip2_reader:
            try:
                response = self.geoip2_reader.city(ip)
                return {
                    "ip": ip,
                    "country": response.country.name,
                    "country_code": response.country.iso_code,
                    "region": response.subdivisions.most_specific.name if response.subdivisions else None,
                    "city": response.city.name,
                    "zip": response.postal.code if response.postal else None,
                    "lat": response.location.latitude,
                    "lon": response.location.longitude,
                    "timezone": response.location.time_zone,
                    "source": "geoip2"
                }
            except Exception as e:
                print(f"[!] geoip2 lookup failed for {ip}: {e}")

        # Fallback to REST API
        return self._geolocate_ip_rest(ip)

    def _geolocate_ip_rest(self, ip: str) -> Optional[Dict]:
        """Fallback: Geolocate via ip-api.com REST API."""
        try:
            url = REST_API_URL.format(ip=ip)
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if data.get("status") == "success":
                return {
                    "ip": ip,
                    "country": data.get("country"),
                    "country_code": data.get("countryCode"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "zip": data.get("zip"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "timezone": data.get("timezone"),
                    "isp": data.get("isp"),
                    "org": data.get("org"),
                    "as": data.get("as"),
                    "mobile": data.get("mobile", False),
                    "proxy": data.get("proxy", False),
                    "hosting": data.get("hosting", False),
                    "source": "ip-api.com"
                }
            else:
                print(f"[!] REST API error for {ip}: {data.get('message')}")
                return None
        except Exception as e:
            print(f"[!] REST API request failed for {ip}: {e}")
            return None

    def geolocate_batch(self, ips: List[str], cache_file: Optional[str] = None) -> List[Dict]:
        """Geolocate multiple IPs with caching and rate limiting."""
        cache = {}
        if cache_file and os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            print(f"[+] Loaded {len(cache)} cached entries")

        results = []
        for i, ip in enumerate(ips):
            if ip in cache:
                results.append(cache[ip])
                continue

            result = self.geolocate_ip(ip)
            if result:
                cache[ip] = result
                results.append(result)

            # Rate limiting for REST API
            if not USE_GEOIP2 and i < len(ips) - 1:
                time.sleep(RATE_LIMIT_DELAY)

            # Save cache periodically
            if cache_file and (i + 1) % 10 == 0:
                with open(cache_file, 'w') as f:
                    json.dump(cache, f, indent=2)

        # Final cache save
        if cache_file:
            with open(cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            print(f"[+] Saved {len(cache)} entries to cache")

        return results

    def __del__(self):
        if self.geoip2_reader:
            self.geoip2_reader.close()


def main():
    """CLI interface for city IP geolocation."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python city_ip_geolocation_v2.py <ip_address>")
        print("  python city_ip_geolocation_v2.py --file <ips_file.txt>")
        print("  python city_ip_geolocation_v2.py --batch <ip1> <ip2> ...")
        sys.exit(1)

    geolocator = CityIPGeolocator()

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("[!] Please provide a file with IPs (one per line)")
            sys.exit(1)
        with open(sys.argv[2], 'r') as f:
            ips = [line.strip() for line in f if line.strip()]
        results = geolocator.geolocate_batch(ips)
        print(json.dumps(results, indent=2))

    elif sys.argv[1] == "--batch":
        ips = sys.argv[2:]
        results = geolocator.geolocate_batch(ips)
        print(json.dumps(results, indent=2))

    else:
        result = geolocator.geolocate_ip(sys.argv[1])
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"[-] Could not geolocate {sys.argv[1]}")
            sys.exit(1)


if __name__ == "__main__":
    main()
