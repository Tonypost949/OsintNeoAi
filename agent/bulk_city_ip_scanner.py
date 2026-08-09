#!/usr/bin/env python3
"""
Bulk City IP Scanner - OSINT Integration
Collects IPs from multiple sources and geolocation-maps them to cities.

Sources:
- City government websites (from city_web_recon.py)
- DNS records for city domains
- Shodan/Censys API queries
- RIPE/ARIN whois data
- Historical DNS records (dnsdumpster)
"""

import os
import json
import requests
import socket
import subprocess
import pandas as pd
from typing import Dict, List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BQ_CLIENT = bigquery.Client()
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "national_audits"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.city_ip_inventory"


class BulkCityIPScanner:
    """Scan and collect IPs associated with city organizations."""

    def __init__(self):
        self.ips_found: Set[str] = set()
        self.domain_ips: Dict[str, List[str]] = {}

    def resolve_domain_to_ips(self, domain: str) -> List[str]:
        """Resolve domain to all its IP addresses."""
        ips = []
        try:
            # A records
            try:
                for info in socket.getaddrinfo(domain, None, socket.AF_INET):
                    ip = info[4][0]
                    if ip not in ips:
                        ips.append(ip)
            except Exception:
                pass

            # MX records (mail servers)
            try:
                mx_data = subprocess.check_output(
                    ["nslookup", "-q=MX", domain],
                    stderr=subprocess.DEVNULL,
                    universal_newlines=True,
                ).split("\n")
                for line in mx_data:
                    if "mail exchanger" in line.lower():
                        mx_host = line.split("=")[-1].strip()
                        for info in socket.getaddrinfo(mx_host, None, socket.AF_INET):
                            ip = info[4][0]
                            if ip not in ips:
                                ips.append(ip)
            except Exception:
                pass

            # NS records (nameservers)
            try:
                ns_data = subprocess.check_output(
                    ["nslookup", "-q=NS", domain],
                    stderr=subprocess.DEVNULL,
                    universal_newlines=True,
                ).split("\n")
                for line in ns_data:
                    if "nameserver" in line.lower():
                        ns_host = line.split("=")[-1].strip()
                        for info in socket.getaddrinfo(ns_host, None, socket.AF_INET):
                            ip = info[4][0]
                            if ip not in ips:
                                ips.append(ip)
            except Exception:
                pass

        except Exception as e:
            logger.debug(f"DNS resolution failed for {domain}: {e}")

        return ips

    def scan_city_domains(self, domains: List[str]) -> Dict[str, List[str]]:
        """Scan a list of city domains and extract IPs."""
        logger.info(f"Scanning {len(domains)} domains...")
        results = {}

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {
                executor.submit(self.resolve_domain_to_ips, domain): domain
                for domain in domains
            }

            for i, future in enumerate(as_completed(futures)):
                domain = futures[future]
                try:
                    ips = future.result()
                    if ips:
                        results[domain] = ips
                        self.ips_found.update(ips)
                        logger.info(f"  {domain}: {len(ips)} IPs")
                    if (i + 1) % 20 == 0:
                        logger.info(f"  Processed {i + 1}/{len(domains)} domains")
                except Exception as e:
                    logger.error(f"Error scanning {domain}: {e}")

        return results

    def query_shodan(self, query: str, api_key: str) -> List[str]:
        """Query Shodan for IPs matching criteria."""
        ips = []
        try:
            url = "https://api.shodan.io/shodan/host/search"
            params = {
                "query": query,
                "key": api_key,
                "page": 1,
            }

            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                ips = [match["ip_str"] for match in data.get("matches", [])]
                logger.info(f"Shodan found {len(ips)} IPs for query: {query}")
        except Exception as e:
            logger.warning(f"Shodan query failed: {e}")

        return ips

    def build_inventory(self, domain_ips: Dict[str, List[str]]) -> List[Dict]:
        """Build inventory record for each IP with source tracking."""
        records = []
        
        for domain, ips in domain_ips.items():
            for ip in ips:
                records.append({
                    "ip": ip,
                    "source_domain": domain,
                    "domain_type": self._classify_domain(domain),
                    "scan_date": pd.Timestamp.now().isoformat(),
                })

        return records

    def _classify_domain(self, domain: str) -> str:
        """Classify domain type."""
        if ".gov" in domain:
            return "government"
        elif "police" in domain or "sheriff" in domain or "pd." in domain:
            return "law_enforcement"
        elif "chamber" in domain:
            return "chamber_commerce"
        elif "fire" in domain or "fd." in domain:
            return "fire_department"
        else:
            return "municipal"

    def upload_inventory(self, records: List[Dict]):
        """Upload IP inventory to BigQuery."""
        if not records:
            logger.warning("No records to upload")
            return

        df = pd.DataFrame(records)
        logger.info(f"Uploading {len(df)} IP inventory records...")

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            schema_update_options=[bigquery.SchemaUpdateOptions.ALLOW_FIELD_ADDITION],
        )

        try:
            job = BQ_CLIENT.load_table_from_dataframe(df, TABLE_ID, job_config=job_config)
            job.result()
            logger.info(f"✓ Inventory upload complete!")
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            df.to_csv("city_ip_inventory.csv", index=False)
            logger.info("Saved to local CSV")

    def export_summary(self, domain_ips: Dict[str, List[str]], output_file: str = "city_ip_scan_summary.json"):
        """Export summary of IP scan results."""
        summary = {
            "total_domains_scanned": len(domain_ips),
            "total_ips_found": len(self.ips_found),
            "domain_breakdown": {
                domain: {
                    "ip_count": len(ips),
                    "ips": ips,
                    "type": self._classify_domain(domain),
                }
                for domain, ips in domain_ips.items()
            },
            "top_ip_frequency": self._analyze_ip_frequency(domain_ips),
        }

        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"✓ Summary exported: {output_file}")
        return output_file

    def _analyze_ip_frequency(self, domain_ips: Dict[str, List[str]]) -> Dict:
        """Identify IPs shared across multiple domains."""
        ip_freq = {}
        for domain, ips in domain_ips.items():
            for ip in ips:
                if ip not in ip_freq:
                    ip_freq[ip] = []
                ip_freq[ip].append(domain)

        # Return IPs appearing in 2+ domains (potential shared infrastructure)
        return {
            ip: {"domains": domains, "count": len(domains)}
            for ip, domains in ip_freq.items()
            if len(domains) > 1
        }


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Bulk City IP Scanner")
    parser.add_argument("--domains-file", help="File with city domains")
    parser.add_argument("--scan-california-cities", action="store_true")
    parser.add_argument("--scan-huntington-beach", action="store_true")
    parser.add_argument("--upload-bq", action="store_true")

    args = parser.parse_args()
    scanner = BulkCityIPScanner()

    domains = []

    if args.scan_california_cities:
        # California cities of interest
        domains = [
            # OC Cities
            "huntingtonbeachca.gov", "newportbeachca.gov", "irvine.ca.gov",
            "santaana.gov", "anaheim.net", "fullertonca.gov",
            "costamesaca.gov", "garden-grove.org",
            # LA Cities
            "lacity.org", "lafd.org", "lapd.org",
            # State
            "ca.gov", "ocgov.com",
        ]

    if args.scan_huntington_beach:
        domains = [
            "huntingtonbeachca.gov",
            "hbpd.org",
            "hbfd.org",
            "volunteer.huntingtonbeachca.gov",
            "huntingtonbeachcu.org",
        ]

    if args.domains_file:
        with open(args.domains_file) as f:
            domains.extend(line.strip() for line in f if line.strip())

    if domains:
        # Scan domains
        domain_ips = scanner.scan_city_domains(domains)
        logger.info(f"\n✓ Total IPs discovered: {len(scanner.ips_found)}")

        # Build inventory
        inventory = scanner.build_inventory(domain_ips)

        # Upload to BigQuery
        if args.upload_bq:
            scanner.upload_inventory(inventory)

        # Export summary
        scanner.export_summary(domain_ips)

        # Show top findings
        logger.info("\n=== Top Shared Infrastructure ===")
        shared = scanner._analyze_ip_frequency(domain_ips)
        for ip, data in sorted(
            shared.items(), key=lambda x: x[1]["count"], reverse=True
        )[:10]:
            logger.info(f"{ip}: {data['count']} domains")
            for domain in data["domains"][:3]:
                logger.info(f"  - {domain}")


if __name__ == "__main__":
    main()
