import os
import re
import json
from collections import Counter

# Define Paths
BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup\KATANA_WORKING_20260702"
OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\new_program_scratch"
KATANA_V2 = os.path.join(BACKUP_DIR, "katana_v2.jsonl")
KATANA_FULL = os.path.join(BACKUP_DIR, "katana_full.jsonl")

OUTPUT_JSON = os.path.join(OUTPUT_DIR, "katana_analyzed_nodes.json")
OUTPUT_MD = os.path.join(OUTPUT_DIR, "katana_threat_reconnaissance_report.md")

def parse_crawl_data():
    print("[*] Initializing Katana-Crawl Forensic Analysis...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    domain_totals = Counter()
    domain_admins = Counter()
    exposed_endpoints = []
    
    # Regular expression for identifying sensitive paths
    admin_pats = re.compile(
        r'(/admin|/editform|/cpanel|/config|/login|/backend|/sso|/sys/|/trident|/loadingmode|/editcontent|\.jsp|/quest|/shared/|/components/|/engagement|codepublishing|showpublished|legistar)', 
        re.I
    )

    # 1. PROCESS KATANA_V2 (Line-by-line URLs)
    if os.path.exists(KATANA_V2):
        print(f"[*] Parsing line-based crawl database: {KATANA_V2}...")
        with open(KATANA_V2, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                url = line.strip()
                if not url:
                    continue
                # Extract domain
                m = re.match(r'https?://([^/]+)', url)
                if not m:
                    continue
                domain = m.group(1)
                domain_totals[domain] += 1
                
                if admin_pats.search(url):
                    domain_admins[domain] += 1
                    exposed_endpoints.append({
                        "domain": domain,
                        "url": url,
                        "type": "Admin Path Exposure"
                    })
    else:
        print(f"[-] Warning: {KATANA_V2} not found.")

    # 2. PROCESS KATANA_FULL (JSONL format if present)
    if os.path.exists(KATANA_FULL):
        print(f"[*] Parsing JSONL-based crawl database: {KATANA_FULL}...")
        with open(KATANA_FULL, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    url = data.get("url", "")
                    src = data.get("source", data.get("input", "unknown"))
                except:
                    continue
                
                if not url:
                    continue
                    
                m = re.match(r'https?://([^/]+)', url)
                if not m:
                    continue
                domain = m.group(1)
                domain_totals[domain] += 1
                
                if admin_pats.search(url):
                    domain_admins[domain] += 1
                    exposed_endpoints.append({
                        "domain": domain,
                        "url": url,
                        "source": src,
                        "type": "JSONL-Crawled Admin Path"
                    })

    # Compile Top Exposed Domains
    compiled_results = {
        "summary": {
            "total_urls_processed": sum(domain_totals.values()),
            "unique_domains": len(domain_totals),
            "total_flagged_admin_urls": sum(domain_admins.values())
        },
        "top_domains": []
    }

    for domain, total in domain_totals.most_common(100):
        adm = domain_admins.get(domain, 0)
        status = "EXPOSED" if adm > 15 else ("FLAG" if adm > 3 else "CLEAN")
        compiled_results["top_domains"].append({
            "domain": domain,
            "total_urls": total,
            "flagged_admins": adm,
            "security_status": status
        })

    # Write JSON Summary
    with open(OUTPUT_JSON, "w", encoding="utf-8") as jf:
        json.dump(compiled_results, jf, indent=4)
    print(f"[+] Exported structured threat matrix JSON to: {OUTPUT_JSON}")

    # Generate Markdown Report
    with open(OUTPUT_MD, "w", encoding="utf-8") as mf:
        mf.write("# KATANA CRAWL THREAT RECONNAISSANCE REPORT\n")
        mf.write("## EXECUTIVE SYSTEM AUDIT\n\n")
        mf.write(f"- **Total Scan Footprint:** {compiled_results['summary']['total_urls_processed']} URLs\n")
        mf.write(f"- **Unique Authority Domains Scanned:** {compiled_results['summary']['unique_domains']}\n")
        mf.write(f"- **Flagged Exposed Admin/Config Nodes:** {compiled_results['summary']['total_flagged_admin_urls']} URLs\n\n")
        
        mf.write("## TOP EXPOSED MUNICIPALITY & AGENCY DOMAINS\n\n")
        mf.write("| Domain | Total Scanned URLs | Flagged Admin Paths | Security Status |\n")
        mf.write("| :--- | :---: | :---: | :--- |\n")
        for idx, d_data in enumerate(compiled_results["top_domains"][:30]):
            mf.write(f"| {d_data['domain']} | {d_data['total_urls']} | {d_data['flagged_admins']} | **{d_data['security_status']}** |\n")
            
        mf.write("\n## DETAILED ACTIONABLE MITIGATION STEPS\n")
        mf.write("1. **Path Hardening:** Restrict access to all `/admin`, `_config`, and backend `.jsp` services behind zero-trust networks.\n")
        mf.write("2. **Revize CMS & Legistar Access Control:** Coordinate with municipal web managers to implement IP-whitelisting on content publishing modules.\n")

    print(f"[+] Generated comprehensive threat report at: {OUTPUT_MD}")

if __name__ == "__main__":
    parse_crawl_data()
