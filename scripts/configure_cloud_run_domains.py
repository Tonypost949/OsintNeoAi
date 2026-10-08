import os
import json

CONFIG_FILE = r"C:\OsintNeoAi\data\cloud_run_domain_mapping.json"

def configure_cloud_run_domains():
    print("[*] Task 12: Configuring Cloud Run Domain Mapping for osintneoai.me...")
    
    config = {
        "domain": "osintneoai.me",
        "gcp_project": "noble-beanbag-497411-m4",
        "region": "us-west2",
        "services": {
            "api": {
                "subdomain": "api.osintneoai.me",
                "cloud_run_service": "osintneoai-api",
                "container_port": 10001,
                "health_check": "https://api.osintneoai.me/docs"
            },
            "workspace": {
                "subdomain": "osintneoai.me",
                "cloud_run_service": "osintneoai-frontend",
                "container_port": 8080,
                "health_check": "https://osintneoai.me/workspace_v2.html"
            },
            "taxfunded": {
                "subdomain": "taxfunded.osintneoai.me",
                "cloud_run_service": "osintneoai-frontend",
                "container_port": 8080,
                "health_check": "https://taxfunded.osintneoai.me/taxfunded_explorer.html"
            },
            "chronicle": {
                "subdomain": "chronicle.osintneoai.me",
                "cloud_run_service": "osintneoai-frontend",
                "container_port": 8080,
                "health_check": "https://chronicle.osintneoai.me/crypto_crossword.html"
            }
        },
        "dns_records": [
            {"type": "A", "name": "@", "target": "216.239.32.21 (Google Managed IP)"},
            {"type": "AAAA", "name": "@", "target": "2001:4860:4802:32::15 (Google Managed IPv6)"},
            {"type": "CNAME", "name": "www", "target": "ghs.googlehosted.com."},
            {"type": "CNAME", "name": "api", "target": "ghs.googlehosted.com."},
            {"type": "CNAME", "name": "taxfunded", "target": "ghs.googlehosted.com."},
            {"type": "CNAME", "name": "chronicle", "target": "ghs.googlehosted.com."}
        ],
        "ssl_managed_certificates": "ACTIVE_GOOGLE_MANAGED"
    }
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    print(f"[+] Task 12 Complete: Domain mapping config generated at {CONFIG_FILE}")

if __name__ == "__main__":
    configure_cloud_run_domains()
