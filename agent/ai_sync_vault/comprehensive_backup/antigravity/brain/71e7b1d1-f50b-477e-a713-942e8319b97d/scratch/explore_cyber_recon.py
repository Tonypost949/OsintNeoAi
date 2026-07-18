from google.cloud import bigquery
import json
import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
output_file = os.path.join(scratch_dir, "cyber_recon_exploration.txt")

client = bigquery.Client()
project = client.project
dataset = "ppp_rico"

sql = f"""
SELECT domain, path, is_exposed, status_code
FROM `{project}.{dataset}.city_cyber_recon`
LIMIT 500
"""

print("Querying city_cyber_recon...")
query_job = client.query(sql)
results = list(query_job.result())

print(f"Retrieved {len(results)} rows. Writing to file...")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("city_cyber_recon Table Exploration\n")
    f.write("===================================\n\n")
    f.write(f"Total rows queried: {len(results)}\n\n")
    
    unique_domains = set()
    exposed_by_domain = {}
    
    for row in results:
        domain = row.get("domain")
        path = row.get("path")
        is_exposed = row.get("is_exposed")
        status_code = row.get("status_code")
        
        unique_domains.add(domain)
        if domain not in exposed_by_domain:
            exposed_by_domain[domain] = 0
        if is_exposed:
            exposed_by_domain[domain] += 1
            
        f.write(f"Domain: {domain} | Path: {path} | Exposed: {is_exposed} | Status: {status_code}\n")
        
    f.write("\nUnique Domains Found:\n")
    for dom in sorted(unique_domains):
        f.write(f"  - {dom} (Exposed count: {exposed_by_domain.get(dom, 0)})\n")

print(f"Done! Results written to {output_file}")
