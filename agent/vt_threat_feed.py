#!/usr/bin/env python3
"""
VirusTotal Threat Feed Integration
Queries VirusTotal API for IoCs related to target domains/IPs.
Requires: VT_API_KEY environment variable
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("[!] requests not installed. Run: pip install requests")
    sys.exit(1)

VT_API_BASE = "https://www.virustotal.com/api/v3"
VT_API_KEY = os.environ.get("VT_API_KEY", "")

class VirusTotalFeed:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or VT_API_KEY
        if not self.api_key:
            print("[!] VT_API_KEY not set. Using public lookup (limited).")
        self.headers = {
            "x-apikey": self.api_key,
            "Accept": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_domain_report(self, domain: str) -> Dict:
        """Get full domain report from VirusTotal."""
        try:
            url = f"{VT_API_BASE}/domains/{domain}"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("attributes", {})
            elif resp.status_code == 401:
                print("[!] Invalid VirusTotal API key")
                return {}
            elif resp.status_code == 404:
                print(f"[!] Domain not found in VirusTotal: {domain}")
                return {}
            else:
                print(f"[!] VT error for {domain}: {resp.status_code}")
                return {}
        except Exception as e:
            print(f"[!] VT request failed for {domain}: {e}")
            return {}

    def get_ip_report(self, ip: str) -> Dict:
        """Get full IP report from VirusTotal."""
        try:
            url = f"{VT_API_BASE}/ip_addresses/{ip}"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("attributes", {})
            else:
                print(f"[!] VT error for {ip}: {resp.status_code}")
                return {}
        except Exception as e:
            print(f"[!] VT request failed for {ip}: {e}")
            return {}

    def get_url_report(self, url: str) -> Dict:
        """Get URL report from VirusTotal."""
        try:
            # VirusTotal uses URL id which is base64 encoded
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            api_url = f"{VT_API_BASE}/urls/{url_id}"
            resp = self.session.get(api_url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("attributes", {})
            else:
                return {}
        except Exception as e:
            print(f"[!] VT URL lookup failed: {e}")
            return {}

    def get_file_report(self, file_hash: str) -> Dict:
        """Get file report by hash (MD5, SHA1, SHA256)."""
        try:
            url = f"{VT_API_BASE}/files/{file_hash}"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("attributes", {})
            else:
                return {}
        except Exception as e:
            print(f"[!] VT file lookup failed: {e}")
            return {}

    def get_domain_dns resolutions(self, domain: str) -> List[Dict]:
        """Get DNS resolutions for a domain."""
        try:
            url = f"{VT_API_BASE}/domains/{domain}/resolutions"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", [])
            return []
        except Exception as e:
            print(f"[!] VT DNS resolution failed: {e}")
            return []

    def get_domain_communicating_files(self, domain: str, limit: int = 10) -> List[Dict]:
        """Get files that communicate with the domain."""
        try:
            url = f"{VT_API_BASE}/domains/{domain}/communicating_files?limit={limit}"
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("data", [])
            return []
        except Exception as e:
            print(f"[!] VT communicating files failed: {e}")
            return []

    def calculate_threat_score(self, domain_data: Dict, ip_data: Dict) -> Dict:
        """Calculate threat score from VT data."""
        score = 0
        severity = "clean"
        tags = []
        categories = []
        malware_families = []

        # Domain analysis stats
        if domain_data:
            last_analysis = domain_data.get("last_analysis_stats", {})
            malicious = last_analysis.get("malicious", 0)
            suspicious = last_analysis.get("suspicious", 0)
            total = sum(last_analysis.values()) if last_analysis else 0

            if total > 0:
                malicious_ratio = malicious / total
                score += min(int(malicious_ratio * 50), 50)
                if malicious > 0:
                    tags.append(f"{malicious}/{total} engines flag as malicious")
                if suspicious > 0:
                    tags.append(f"{suspicious}/{total} engines flag as suspicious")

            # Community score
            community = domain_data.get("last_analysis_results", {})
            rep = domain_data.get("reputation", 0)
            if rep < -50:
                score += 20
                tags.append("Low reputation score")
            elif rep < 0:
                score += 10

            # Categories
            cats = domain_data.get("categories", {})
            if cats:
                categories = list(cats.values())[:3]

            # Popularity rank
            popularity = domain_data.get("popularity_ranks", {})
            if popularity:
                tags.append(f"Alexa rank: {list(popularity.values())[0].get('rank', 'N/A')}")

        # IP analysis stats
        if ip_data:
            last_analysis = ip_data.get("last_analysis_stats", {})
            malicious = last_analysis.get("malicious", 0)
            if malicious > 0:
                score += min(malicious * 5, 30)
                tags.append(f"IP flagged by {malicious} engines")

            # AS owner info
            as_owner = ip_data.get("as_owner", "")
            if as_owner:
                tags.append(f"ASN: {as_owner}")

        # Determine severity
        score = min(score, 100)
        if score >= 70:
            severity = "critical"
        elif score >= 50:
            severity = "high"
        elif score >= 25:
            severity = "medium"
        elif score > 0:
            severity = "low"
        else:
            severity = "clean"

        return {
            "score": score,
            "severity": severity,
            "tags": tags[:10],
            "categories": categories,
            "malware_families": malware_families,
            "last_checked": datetime.utcnow().isoformat()
        }

    def scan_target(self, domain: str, ip: Optional[str] = None) -> Dict:
        """Full threat scan for a target."""
        print(f"[+] Scanning {domain} via VirusTotal...")

        domain_data = self.get_domain_report(domain)
        ip_data = {}
        if ip:
            ip_data = self.get_ip_report(ip)

        threat_info = self.calculate_threat_score(domain_data, ip_data)

        # Extract useful data
        result = {
            "domain": domain,
            "ip": ip,
            "threat_info": threat_info,
            "whois": domain_data.get("whois", "")[:500] if domain_data else "",
            "registrar": domain_data.get("registrar", ""),
            "creation_date": domain_data.get("creation_date", ""),
            "popularity_rank": None
        }

        if domain_data:
            popularity = domain_data.get("popularity_ranks", {})
            if popularity:
                result["popularity_rank"] = list(popularity.values())[0].get("rank")

        return result


def main():
    """CLI interface for VT threat feed."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python vt_threat_feed.py <domain>")
        print("  python vt_threat_feed.py --file <domains.txt>")
        print("  python vt_threat_feed.py --ip <ip_address>")
        print("\nSet VT_API_KEY environment variable for full access.")
        sys.exit(1)

    feed = VirusTotalFeed()

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
            time.sleep(15)  # VT rate limit: 4 requests/minute for free tier
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
