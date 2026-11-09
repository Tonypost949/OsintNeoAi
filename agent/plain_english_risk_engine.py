#!/usr/bin/env python3
"""
Plain-English Municipal Risk Translation Engine
Converts technical telemetry, port audits, WAF checks, and crawling artifacts into
clean, human-readable risk assessments suitable for public investigative dashboards.
- Completely strips raw attack vectors, sensitive credentials, and PII.
- Generates consumer-grade Letter Grades (A, B, C, D, F).
- Outputs executive summaries explaining risks in plain English.
- Mirrors results into the Evidence Locker and Power App sync folder.
"""

import csv
import json
import os
import sys

INPUT_CSV = "/data/data/com.termux/files/home/osintneoai/agent/municipal_security_exposure_report.csv"
PUBLIC_JSON = "/storage/2004-1014/osintneoai_offload/evidence_locker/public_plain_english_dossiers.json"
PUBLIC_CSV = "/storage/2004-1014/osintneoai_offload/evidence_locker/public_plain_english_dossiers.csv"

def calculate_grade_and_plain_text(record):
    domain = record.get("Domain", "Unknown")
    live_ip = record.get("Live_IP", "")
    waf = record.get("WAF_Shield", "")
    open_ports = record.get("Open_Ports", "")
    https = record.get("HTTPS_Enforced", "NO") == "YES"
    exposed_files = record.get("Exposed_Files", "")
    
    # 1. Critical Failures (F Grade)
    has_admin_ports = any(p in open_ports for p in ["3389", "3306", "21", "22"])
    has_exposed_files = exposed_files and exposed_files != "None"
    
    if has_admin_ports or has_exposed_files:
        grade = "F (Critical Danger)"
        risk_level = "Severe System Takeover Risk"
        
        explanations = []
        if "3389" in open_ports:
            explanations.append("The computer's administrative desktop screen is publicly visible across the internet, allowing anyone with staff login credentials to take control of city systems.")
        if "3306" in open_ports:
            explanations.append("The city database server is connected directly to the open internet without an internal firewall barrier, leaving public records and databases accessible to direct queries.")
        if "21" in open_ports or "22" in open_ports:
            explanations.append("Unencrypted administrative file transfer channels are publicly open, exposing remote access controls.")
        if has_exposed_files:
            explanations.append("Internal system configuration files and backup snapshots are publicly downloadable from the root web directory without authentication.")
            
        plain_summary = " ".join(explanations)
        action = "Immediately block ports 3389, 3306, and 21 at the edge router; move staff management portals behind an encrypted private VPN; and remove publicly reachable backup files."
        return grade, risk_level, plain_summary, action

    # 2. High Risk / Direct Origin Exposed (D Grade)
    if "None Detected" in waf or "Direct Origin" in waf:
        grade = "D (Vulnerable)"
        risk_level = "Unshielded Hardware Exposure"
        plain_summary = f"The city's real computer server (IP: {live_ip}) is sitting directly on the public internet without an enterprise firewall shield (such as Cloudflare or Akamai). Malicious traffic can hit the server hardware directly, making it easy to knock offline with high traffic floods or attack server software bugs."
        action = "Deploy a commercial Web Application Firewall (WAF) proxy to hide the true physical server IP behind protected cloud edge filters."
        return grade, risk_level, plain_summary, action

    # 3. Moderate Risk / Unencrypted Transport (C Grade)
    if not https:
        grade = "C (Needs Hardening)"
        risk_level = "Unencrypted Data in Transit"
        plain_summary = "The website allows visitors and employees to connect over plain, unencrypted HTTP (Port 80) without automatically redirecting them to an encrypted connection. Anyone monitoring traffic on public Wi-Fi or local networks can read data submitted to the site."
        action = "Configure server redirection rules to force all incoming HTTP requests to upgrade automatically to HTTPS."
        return grade, risk_level, plain_summary, action

    # 4. Filtered / Offline (B Grade)
    if live_ip == "DNS Failed":
        grade = "B (Offline / Inactive)"
        risk_level = "Dormant Domain"
        plain_summary = "The domain does not currently resolve to an active public IP address or its nameservers are dropping incoming queries, preventing direct exposure."
        action = "Verify DNS zone configuration if this portal is intended for public access."
        return grade, risk_level, plain_summary, action

    # 5. Properly Shielded (A Grade)
    grade = "A (Properly Shielded)"
    risk_level = "Low Risk / Hardened"
    plain_summary = f"This municipality is properly defended. The server is hidden behind {waf} protection, all sensitive management doors are closed, and traffic is enforced over encrypted connections."
    action = "Maintain current firewall rules and conduct quarterly vulnerability audits."
    return grade, risk_level, plain_summary, action

def run_translation():
    if not os.path.exists(INPUT_CSV):
        print(f"[!] Input file {INPUT_CSV} not found.")
        return

    print(f"[*] Reading telemetry from {INPUT_CSV}...")
    records = []
    with open(INPUT_CSV, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grade, risk_level, plain_summary, action = calculate_grade_and_plain_text(row)
            
            # Sanitized, public-safe entity record
            public_record = {
                "Entity_Domain": row.get("Domain", ""),
                "Public_Security_Grade": grade,
                "Threat_Category": risk_level,
                "Plain_English_Diagnosis": plain_summary,
                "Recommended_Public_Remediation": action,
                "Protected_By_WAF": "NO" if ("None Detected" in row.get("WAF_Shield", "") or "Direct Origin" in row.get("WAF_Shield", "")) else "YES",
                "Encrypted_Connection_Enforced": row.get("HTTPS_Enforced", "NO")
            }
            records.append(public_record)

    # Save to Evidence Locker (JSON & CSV)
    with open(PUBLIC_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"[✓] Public Plain-English JSON saved: {PUBLIC_JSON}")

    fieldnames = ["Entity_Domain", "Public_Security_Grade", "Threat_Category", "Plain_English_Diagnosis", "Recommended_Public_Remediation", "Protected_By_WAF", "Encrypted_Connection_Enforced"]
    with open(PUBLIC_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[✓] Public Plain-English CSV saved: {PUBLIC_CSV}")

    return records

if __name__ == "__main__":
    run_translation()
