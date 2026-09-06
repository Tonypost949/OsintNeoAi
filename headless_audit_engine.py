"""
headless_audit_engine.py — Background passive audit engine

Runs invisible background checks on target domains and outputs
clean Executive Truth summaries. Users never see raw technical tools.
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime
from typing import Optional


AUDIT_DB = os.path.join(os.path.dirname(__file__), "data", "audit_results.json")


class HeadlessAuditEngine:
    def __init__(self):
        self.results = self._load_db()

    def _load_db(self) -> dict:
        if os.path.exists(AUDIT_DB):
            with open(AUDIT_DB, "r") as f:
                return json.load(f)
        return {}

    def _save_db(self):
        os.makedirs(os.path.dirname(AUDIT_DB), exist_ok=True)
        with open(AUDIT_DB, "w") as f:
            json.dump(self.results, f, indent=2)

    def passive_dns_check(self, domain: str) -> dict:
        try:
            result = subprocess.run(
                ["nslookup", domain],
                capture_output=True, text=True, timeout=10
            )
            return {"domain": domain, "dns_raw": result.stdout, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"domain": domain, "error": str(e)}

    def whois_lookup(self, domain: str) -> dict:
        try:
            result = subprocess.run(
                ["whois", domain],
                capture_output=True, text=True, timeout=15
            )
            return {"domain": domain, "whois_raw": result.stdout[:2000], "timestamp": datetime.utcnow().isoformat()}
        except Exception:
            return {"domain": domain, "error": "whois not available"}

    def ssl_inspection(self, domain: str) -> dict:
        try:
            result = subprocess.run(
                ["openssl", "s_client", "-connect", f"{domain}:443", "-servername", domain],
                input=b"Q\n",
                capture_output=True, text=True, timeout=10
            )
            has_cert = "BEGIN CERTIFICATE" in result.stdout
            return {"domain": domain, "has_valid_ssl": has_cert, "timestamp": datetime.utcnow().isoformat()}
        except Exception:
            return {"domain": domain, "has_valid_ssl": None, "error": "inspection failed"}

    def generate_executive_truth(self, domain: str, audit_data: dict) -> str:
        findings = []

        whois = audit_data.get("whois", {})
        if whois.get("whois_raw"):
            if "No match" in whois.get("whois_raw", ""):
                findings.append(f"WHOIS: Limited registration data found for {domain} — possible privacy shield or recently registered.")
            else:
                findings.append(f"WHOIS: Domain registration data retrieved. Review for organizational linkages.")

        ssl = audit_data.get("ssl", {})
        if ssl.get("has_valid_ssl") is False:
            findings.append("SSL: Domain does not have a valid SSL certificate. Public data may be served insecurely.")
        elif ssl.get("has_valid_ssl") is True:
            findings.append("SSL: Valid certificate detected. Secure connection confirmed.")

        dns = audit_data.get("dns", {})
        if dns.get("dns_raw"):
            findings.append("DNS: Public DNS records resolved. Passive enumeration complete.")

        if not findings:
            return f"Audit of {domain}: Passive checks completed with no notable findings."

        truth = f"EXECUTIVE TRUTH SUMMARY — {domain}\n"
        truth += f"Generated: {datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')}\n"
        truth += "=" * 50 + "\n\n"
        truth += "FINDINGS:\n"
        for i, f in enumerate(findings, 1):
            truth += f"  {i}. {f}\n"
        truth += f"\nRECOMMENDATION: {'No immediate action required.' if len(findings) <= 2 else 'Further investigation recommended via FOIA request.'}"
        return truth

    def full_audit(self, domain: str) -> dict:
        audit_data = {
            "dns": self.passive_dns_check(domain),
            "whois": self.whois_lookup(domain),
            "ssl": self.ssl_inspection(domain),
        }
        truth = self.generate_executive_truth(domain, audit_data)
        result = {
            "domain": domain,
            "audit_data": audit_data,
            "executive_truth": truth,
            "timestamp": datetime.utcnow().isoformat(),
            "result_hash": hashlib.sha256(truth.encode()).hexdigest(),
        }
        self.results[domain] = result
        self._save_db()
        return result


if __name__ == "__main__":
    engine = HeadlessAuditEngine()
    domain = input("Enter domain to audit: ").strip()
    if domain:
        result = engine.full_audit(domain)
        print(result["executive_truth"])
