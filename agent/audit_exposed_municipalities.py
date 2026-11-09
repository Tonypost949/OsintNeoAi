#!/usr/bin/env python3
"""
Full Sweep Municipal Security Exposure Auditor
Audits the complete target list from both:
- AUDIT_NUMBERS_v2_scan_july24.csv
- AUDIT_NUMBERS.csv
Merges all unique domains and IPs, tests live status, and saves to the Evidence Locker.
"""

import csv
import json
import socket
import ssl
import sys
import time
import urllib.request
import urllib.error

INPUT_FILES = [
    "/data/data/com.termux/files/home/osintneoai/AUDIT_NUMBERS_v2_scan_july24.csv",
    "/data/data/com.termux/files/home/osintneoai/AUDIT_NUMBERS.csv"
]
CSV_OUTPUT = "/data/data/com.termux/files/home/osintneoai/agent/municipal_security_exposure_report.csv"
SD_OUTPUT = "/storage/2004-1014/osintneoai_offload/evidence_locker/municipal_security_exposure_report.csv"
JSON_OUTPUT = "/storage/2004-1014/osintneoai_offload/evidence_locker/municipal_security_exposure_report.json"

PORTS_TO_CHECK = {
    21: "FTP",
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
}

SENSITIVE_PATHS = ["/.env", "/.git/config", "/backup.sql", "/.aws/credentials", "/.ssh"]

WAF_SIGNATURES = [
    "cloudflare",
    "cf-ray",
    "akamai",
    "cloudfront",
    "azure",
    "imperva",
    "incapsula",
    "sucuri",
    "barracuda",
    "f5",
    "bigip"
]

def check_port(ip, port, timeout=2.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except Exception:
        return False

def detect_waf(domain, headers):
    h_str = " ".join([f"{k}:{v}" for k, v in headers.items()]).lower()
    detected = []
    for sig in WAF_SIGNATURES:
        if sig in h_str:
            detected.append(sig.capitalize())
    return ", ".join(set(detected)) if detected else "None Detected (Direct Origin Exposed)"

def check_http_security(domain):
    res = {
        "https_enforced": False,
        "waf_detected": "Unknown",
        "server_header": "Unknown",
        "status_code": 0,
        "exposed_paths": []
    }
    
    try:
        req = urllib.request.Request(
            f"http://{domain}",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSINT-Audit/2.0"}
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            final_url = response.geturl()
            res["status_code"] = response.getcode()
            res["https_enforced"] = final_url.startswith("https://")
            headers = dict(response.info())
            res["server_header"] = headers.get("Server", "Hidden/None")
            res["waf_detected"] = detect_waf(domain, headers)
    except urllib.error.HTTPError as e:
        res["status_code"] = e.code
        headers = dict(e.headers)
        res["server_header"] = headers.get("Server", "Hidden/None")
        res["waf_detected"] = detect_waf(domain, headers)
        if e.code in [301, 302, 307, 308]:
            loc = headers.get("Location", "")
            res["https_enforced"] = loc.startswith("https://")
    except Exception as e:
        res["server_header"] = f"Connection Error: {type(e).__name__}"

    for path in SENSITIVE_PATHS:
        try:
            url = f"https://{domain}{path}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 OSINT-Audit/2.0"})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=4, context=ctx) as r:
                if r.getcode() == 200:
                    content_type = r.headers.get("Content-Type", "")
                    if "text/html" not in content_type or len(r.read(256)) > 10:
                        res["exposed_paths"].append(f"{path} (HTTP 200)")
        except urllib.error.HTTPError:
            pass
        except Exception:
            pass

    return res

def run_full_sweep():
    targets = {}
    
    for fpath in INPUT_FILES:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 3:
                        continue
                    domain = row[0].strip()
                    if not domain or domain.startswith("#") or "Domain" in domain or domain in ["socalgovernments", "municipal_portals", "TOTAL_TARGETS"]:
                        continue
                    if domain not in targets:
                        targets[domain] = {"documented_ip": ""}
                    
                    # Check for IP in any column
                    for col in row[1:]:
                        col = col.strip()
                        if col.startswith("IP ") or "ORIGIN_IP" in col or "DNS_A" in col:
                            parts = col.split()
                            for p in parts:
                                if p.count(".") == 3 and not targets[domain]["documented_ip"]:
                                    targets[domain]["documented_ip"] = p.strip(",")
                        elif col.count(".") == 3 and col.replace(".", "").isdigit():
                            targets[domain]["documented_ip"] = col
        except Exception as e:
            print(f"[!] Error reading {fpath}: {e}")

    print(f"[*] Ingested {len(targets)} unique municipal target nodes.")
    results = []

    for domain, data in targets.items():
        print(f"[+] Sweeping {domain}...")
        live_ip = "DNS Failed"
        try:
            live_ip = socket.gethostbyname(domain)
        except Exception:
            pass
        
        doc_ip = data["documented_ip"] or live_ip
        ip_to_test = live_ip if live_ip != "DNS Failed" else doc_ip
        
        open_ports = []
        if ip_to_test and ip_to_test != "DNS Failed":
            for port, name in PORTS_TO_CHECK.items():
                if check_port(ip_to_test, port):
                    open_ports.append(f"{port}({name})")
        
        http_sec = check_http_security(domain)
        
        exposure_level = "SECURED / SHIELDED"
        reasons = []
        
        admin_ports = [p for p in open_ports if any(k in p for k in ["3389", "3306", "21", "22"])]
        if admin_ports:
            exposure_level = "CRITICAL: EXPOSED ADMIN SERVICES"
            reasons.append(f"Admin ports open publicly: {', '.join(admin_ports)}")
            
        if http_sec["exposed_paths"]:
            exposure_level = "CRITICAL: EXPOSED FILES"
            reasons.append(f"Direct sensitive file exposure: {', '.join(http_sec['exposed_paths'])}")
            
        if "None Detected" in http_sec["waf_detected"]:
            if exposure_level == "SECURED / SHIELDED":
                exposure_level = "HIGH: UNPROTECTED DIRECT ORIGIN"
            reasons.append(f"Raw origin server directly exposed without WAF shield (IP: {ip_to_test})")
            
        if not http_sec["https_enforced"] and "80(HTTP)" in open_ports:
            if "CRITICAL" not in exposure_level:
                exposure_level = "HIGH: UNENCRYPTED CLEARTEXT"
            reasons.append("HTTP port 80 fails to enforce HTTPS redirect")
            
        if not reasons:
            reasons.append(f"Shielded by {http_sec['waf_detected']}, HTTPS enforced, administrative ports closed.")

        record = {
            "Domain": domain,
            "Live_IP": live_ip,
            "Documented_IP": doc_ip,
            "WAF_Shield": http_sec["waf_detected"],
            "Server_Banner": http_sec["server_header"],
            "Open_Ports": ", ".join(open_ports) if open_ports else "None (Filtered)",
            "HTTPS_Enforced": "YES" if http_sec["https_enforced"] else "NO",
            "Exposed_Files": ", ".join(http_sec["exposed_paths"]) if http_sec["exposed_paths"] else "None",
            "Exposure_Status": exposure_level,
            "Security_Details": " | ".join(reasons)
        }
        results.append(record)

    fieldnames = ["Domain", "Live_IP", "Documented_IP", "WAF_Shield", "Server_Banner", "Open_Ports", "HTTPS_Enforced", "Exposed_Files", "Exposure_Status", "Security_Details"]
    
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    try:
        with open(SD_OUTPUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"[!] Warning: Could not write SD output: {e}")

    try:
        with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        pass

    print(f"[✓] Full sweep complete: {len(results)} targets saved.")

if __name__ == "__main__":
    run_full_sweep()
