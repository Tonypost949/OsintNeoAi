#!/usr/bin/env python3
"""
OTX Threat Feed Integration
Queries AlienVault OTX for IoCs related to target domains/IPs.
Requires: OTX_API_KEY environment variable
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("[!] requests not installed. Run: pip install requests")
    sys.exit(1)

OTX_API_BASE = "https://otx.alienvault.com/api/v1"
OTX_API_KEY = os.environ.get("OTX_API_KEY", "")

class OTXThreatFeed:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OTX_API_KEY
        if not self.api_key:
            print("[!] OTX_API_KEY not set. Using limited public endpoints.")
        self.headers = {
            "X-OTX-API-KEY": self.api_key,
            "Accept": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_pulses_for_domain(self, domain: str) -> List[Dict]:
        """Get threat pulses associated with a domain."""
        try:
            url = f"{OTX_API_BASE}/indicators/domain/{domain}/pulses"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", [])
            elif resp.status_code == 403:
                print(f"[!] OTX API key required for domain lookup: {domain}")
                return []
            else:
                print(f"[!] OTX error for {domain}: {resp.status_code}")
                return []
        except Exception as e:
            print(f"[!] OTX request failed for {domain}: {e}")
            return []

    def get_pulses_for_ip(self, ip: str) -> List[Dict]:
        """Get threat pulses associated with an IP."""
        try:
            url = f"{OTX_API_BASE}/indicators/IPv4/{ip}/pulses"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", [])
            else:
                print(f"[!] OTX error for {ip}: {resp.status_code}")
                return []
        except Exception as e:
            print(f"[!] OTX request failed for {ip}: {e}")
            return []

    def get_alerts_for_indicator(self, indicator: str, indicator_type: str = "domain") -> List[Dict]:
        """Get recent alerts for an indicator."""
        try:
            if indicator_type == "domain":
                url = f"{OTX_API_BASE}/indicators/domain/{indicator}/alerts"
            elif indicator_type == "ip":
                url = f"{OTX_API_BASE}/indicators/IPv4/{indicator}/alerts"
            else:
                return []

            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            return []
        except Exception as e:
            print(f"[!] OTX alerts request failed: {e}")
            return []

    def get_url_info(self, url: str) -> Dict:
        """Get threat info for a URL."""
        try:
            from urllib.parse import quote
            encoded_url = quote(url, safe='')
            api_url = f"{OTX_API_BASE}/indicators/url/{encoded_url}/general"
            resp = self.session.get(api_url, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return {}
        except Exception as e:
            print(f"[!] OTX URL lookup failed: {e}")
            return {}

    def calculate_threat_score(self, pulses: List[Dict]) -> Dict:
        """Calculate a threat score based on pulse data."""
        if not pulses:
            return {"score": 0, "severity": "unknown", "tags": [], "pulse_count": 0}

        # Count recent pulses (last 30 days)
        now = datetime.utcnow()
        recent_count = 0
        all_tags = []
        malware_families = set()

        for pulse in pulses:
            created = pulse.get("created", "")
            if created:
                try:
                    pulse_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if (now - pulse_date.replace(tzinfo=None)).days <= 30:
                        recent_count += 1
                except:
                    pass

            all_tags.extend(pulse.get("tags", []))
            for malware in pulse.get("malware_families", []):
                if isinstance(malware, dict):
                    malware_families.add(malware.get("name", ""))
                elif isinstance(malware, str):
                    malware_families.add(malware)

        # Calculate score (0-100)
        base_score = min(len(pulses) * 5, 50)
        recency_bonus = min(recent_count * 10, 30)
        malware_bonus = min(len(malware_families) * 10, 20)

        score = min(base_score + recency_bonus + malware_bonus, 100)

        # Determine severity
        if score >= 70:
            severity = "critical"
        elif score >= 50:
            severity = "high"
        elif score >= 30:
            severity = "medium"
        elif score > 0:
            severity = "low"
        else:
            severity = "clean"

        # Get top tags
        from collections import Counter
        tag_counts = Counter(all_tags).most_common(5)

        return {
            "score": score,
            "severity": severity,
            "tags": [t[0] for t in tag_counts],
            "pulse_count": len(pulses),
            "recent_pulse_count": recent_count,
            "malware_families": list(malware_families)[:5],
            "last_checked": datetime.utcnow().isoformat()
        }

    def scan_target(self, domain: str, ip: Optional[str] = None) -> Dict:
        """Full threat scan for a target domain/IP."""
        print(f"[+] Scanning {domain} via OTX...")

        domain_pulses = self.get_pulses_for_domain(domain)
        ip_pulses = []
        if ip:
            ip_pulses = self.get_pulses_for_ip(ip)

        all_pulses = domain_pulses + ip_pulses
        threat_info = self.calculate_threat_score(all_pulses)

        return {
            "domain": domain,
            "ip": ip,
            "threat_info": threat_info,
            "domain_pulse_count": len(domain_pulses),
            "ip_pulse_count": len(ip_pulses),
            "top_pulses": [
                {
                    "name": p.get("name", "Unknown"),
                    "tags": p.get("tags", [])[:3],
                    "created": p.get("created", "")
                }
                for p in all_pulses[:5]
            ]
        }


def main():
    """CLI interface for OTX threat feed."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python otx_threat_feed.py <domain>")
        print("  python otx_threat_feed.py --file <domains.txt>")
        print("  python otx_threat_feed.py --ip <ip_address>")
        print("\nSet OTX_API_KEY environment variable for full access.")
        sys.exit(1)

    feed = OTXThreatFeed()

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("[!] Please provide a file with domains (one per line)")
            sys.exit(1)
        with open(sys.argv[2], 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        results = []
        for domain in domains:
            result = feed.scan_target(domain)
            results.append(result)
            time.sleep(1)  # Rate limiting
        print(json.dumps(results, indent=2))

    elif sys.argv[1] == "--ip":
        if len(sys.argv) < 3:
            print("[!] Please provide an IP address")
            sys.exit(1)
        result = feed.scan_target("unknown", sys.argv[2])
        print(json.dumps(result, indent=2))

    else:
        result = feed.scan_target(sys.argv[1])
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
