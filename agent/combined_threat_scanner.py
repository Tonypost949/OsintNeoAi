#!/usr/bin/env python3
"""
Combined Threat Scanner
Integrates OTX, VirusTotal, and forensic pipeline data for comprehensive threat analysis.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from otx_threat_feed import OTXThreatFeed
except ImportError:
    OTXThreatFeed = None

try:
    from vt_threat_feed import VirusTotalFeed
except ImportError:
    VirusTotalFeed = None

try:
    from city_ip_geolocation_v2 import CityIPGeolocator
except ImportError:
    CityIPGeolocator = None

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'opencode_work')
MARKER_CACHE = os.path.join(CACHE_DIR, 'city_markers_cache.json')
THREAT_CACHE = os.path.join(CACHE_DIR, 'threat_intel_cache.json')
SCAN_LOG = os.path.join(CACHE_DIR, 'threat_scan_log.json')


class CombinedThreatScanner:
    def __init__(self):
        self.otx = OTXThreatFeed() if OTXThreatFeed else None
        self.vt = VirusTotalFeed() if VirusTotalFeed else None
        self.geolocator = CityIPGeolocator() if CityIPGeolocator else None
        self.marker_cache = self._load_cache(MARKER_CACHE)
        self.threat_cache = self._load_cache(THREAT_CACHE)

    def _load_cache(self, path: str) -> Dict:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def _save_cache(self, path: str, data: Dict):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def scan_target(self, domain: str, ip: Optional[str] = None, force: bool = False) -> Dict:
        """Comprehensive threat scan combining all sources."""
        cache_key = f"{domain}:{ip}"
        if not force and cache_key in self.threat_cache:
            cached = self.threat_cache[cache_key]
            # Check if scan is recent (last 24 hours)
            if cached.get("scan_time"):
                try:
                    scan_time = datetime.fromisoformat(cached["scan_time"])
                    if (datetime.utcnow() - scan_time).total_seconds() < 86400:
                        return cached
                except:
                    pass

        print(f"[+] Comprehensive scan: {domain} ({ip})")

        result = {
            "domain": domain,
            "ip": ip,
            "scan_time": datetime.utcnow().isoformat(),
            "sources": {},
            "combined_threat_score": 0,
            "severity": "unknown",
            "indicators": [],
            "recommendations": []
        }

        # OTX Scan
        if self.otx:
            try:
                otx_result = self.otx.scan_target(domain, ip)
                result["sources"]["otx"] = otx_result.get("threat_info", {})
                result["sources"]["otx"]["pulse_count"] = otx_result.get("domain_pulse_count", 0)
            except Exception as e:
                print(f"[!] OTX scan failed: {e}")

        # VirusTotal Scan
        if self.vt:
            try:
                vt_result = self.vt.scan_target(domain, ip)
                result["sources"]["virustotal"] = vt_result.get("threat_info", {})
            except Exception as e:
                print(f"[!] VT scan failed: {e}")

        # Geolocation enrichment
        if self.geolocator and ip:
            try:
                geo_data = self.geolocator.geolocate_ip(ip)
                if geo_data:
                    result["geolocation"] = {
                        "country": geo_data.get("country"),
                        "city": geo_data.get("city"),
                        "isp": geo_data.get("isp"),
                        "org": geo_data.get("org"),
                        "hosting": geo_data.get("hosting", False),
                        "proxy": geo_data.get("proxy", False)
                    }
                    # Flag hosting/proxy as potential risk
                    if geo_data.get("hosting"):
                        result["indicators"].append("Hosted on cloud infrastructure")
                    if geo_data.get("proxy"):
                        result["indicators"].append("Uses proxy/VPN")
            except Exception as e:
                print(f"[!] Geolocation failed: {e}")

        # Calculate combined score
        scores = []
        for source_name, source_data in result["sources"].items():
            if "score" in source_data:
                scores.append(source_data["score"])

        if scores:
            # Weighted average with max bias
            result["combined_threat_score"] = max(scores)  # Use highest score
            avg_score = sum(scores) / len(scores)
            # If avg is significantly lower than max, use weighted
            if avg_score < max(scores) * 0.7:
                result["combined_threat_score"] = int(max(scores) * 0.8 + avg_score * 0.2)

        # Determine severity
        score = result["combined_threat_score"]
        if score >= 70:
            result["severity"] = "critical"
        elif score >= 50:
            result["severity"] = "high"
        elif score >= 25:
            result["severity"] = "medium"
        elif score > 0:
            result["severity"] = "low"
        else:
            result["severity"] = "clean"

        # Aggregate indicators
        for source_name, source_data in result["sources"].items():
            for tag in source_data.get("tags", []):
                result["indicators"].append(f"[{source_name.upper()}] {tag}")

        # Generate recommendations
        if score >= 70:
            result["recommendations"].append("Immediate investigation recommended")
            result["recommendations"].append("Consider blocking or sandboxing")
        elif score >= 50:
            result["recommendations"].append("Enhanced monitoring recommended")
            result["recommendations"].append("Review recent activity logs")
        elif score >= 25:
            result["recommendations"].append("Standard monitoring in place")

        # Cache result
        self.threat_cache[cache_key] = result
        self._save_cache(THREAT_CACHE, self.threat_cache)

        return result

    def scan_all_markers(self, force: bool = False) -> List[Dict]:
        """Scan all markers in cache."""
        results = []
        total = len(self.marker_cache)

        for i, (domain, marker) in enumerate(self.marker_cache.items(), 1):
            print(f"[{i}/{total}] Scanning {domain}...")
            result = self.scan_target(domain, marker.get("ip"), force)
            results.append(result)

            # Rate limiting
            time.sleep(2)

        return results

    def get_threat_summary(self) -> Dict:
        """Get summary of all threat scans."""
        summary = {
            "total_scanned": len(self.threat_cache),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "clean": 0,
                "unknown": 0
            },
            "top_threats": [],
            "last_scan": None
        }

        for key, scan in self.threat_cache.items():
            severity = scan.get("severity", "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1

            if scan.get("scan_time"):
                if not summary["last_scan"] or scan["scan_time"] > summary["last_scan"]:
                    summary["last_scan"] = scan["scan_time"]

        # Get top threats
        sorted_threats = sorted(
            self.threat_cache.values(),
            key=lambda x: x.get("combined_threat_score", 0),
            reverse=True
        )
        summary["top_threats"] = [
            {
                "domain": t.get("domain"),
                "score": t.get("combined_threat_score"),
                "severity": t.get("severity")
            }
            for t in sorted_threats[:10]
        ]

        return summary

    def update_marker_cache(self):
        """Update marker cache with threat data."""
        for domain, marker in self.marker_cache.items():
            cache_key = f"{domain}:{marker.get('ip')}"
            if cache_key in self.threat_cache:
                threat_data = self.threat_cache[cache_key]
                marker["threat_intel"] = {
                    "score": threat_data.get("combined_threat_score", 0),
                    "severity": threat_data.get("severity", "unknown"),
                    "last_scan": threat_data.get("scan_time")
                }
                marker["risk_score"] = threat_data.get("combined_threat_score", marker.get("risk_score", 0))

        self._save_cache(MARKER_CACHE, self.marker_cache)
        print(f"[+] Updated {len(self.marker_cache)} markers with threat data")


def main():
    """CLI interface."""
    scanner = CombinedThreatScanner()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python combined_threat_scanner.py scan <domain> [ip]")
        print("  python combined_threat_scanner.py scan-all [--force]")
        print("  python combined_threat_scanner.py summary")
        print("  python combined_threat_scanner.py update-cache")
        sys.exit(1)

    command = sys.argv[1]

    if command == "scan":
        if len(sys.argv) < 3:
            print("[!] Please provide a domain")
            sys.exit(1)
        domain = sys.argv[2]
        ip = sys.argv[3] if len(sys.argv) > 3 else None
        result = scanner.scan_target(domain, ip, force="--force" in sys.argv)
        print(json.dumps(result, indent=2))

    elif command == "scan-all":
        results = scanner.scan_all_markers(force="--force" in sys.argv)
        print(json.dumps(scanner.get_threat_summary(), indent=2))

    elif command == "summary":
        print(json.dumps(scanner.get_threat_summary(), indent=2))

    elif command == "update-cache":
        scanner.update_marker_cache()

    else:
        print(f"[!] Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
