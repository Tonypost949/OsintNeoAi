import json
import urllib.request
import time
import subprocess
import os

ip_file = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\UNIQUE_PUBLIC_IPS.txt"
out_json = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\PUBLIC_IPS_ENRICHED_SWEEP.json"
out_dossier_section = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\PUBLIC_IPS_FORENSIC_SWEEP_DOSSIER.md"

with open(ip_file, "r", encoding="utf-8") as f:
    ips = [line.strip() for line in f if line.strip()]

total_ips = len(ips)
print(f"Loaded {total_ips} public IP addresses for forensic sweep.")

# Perform bulk ASN & Geolocation enrichment via ip-api batch endpoint
results = []
batch_size = 100

for i in range(0, total_ips, batch_size):
    batch = ips[i:i + batch_size]
    print(f"Processing batch {i // batch_size + 1} / {(total_ips + batch_size - 1) // batch_size} ({len(batch)} IPs)...")
    
    req_data = json.dumps([{"query": ip} for ip in batch]).encode("utf-8")
    req = urllib.request.Request("http://ip-api.com/batch", data=req_data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            batch_res = json.loads(resp.read().decode("utf-8"))
            results.extend(batch_res)
    except Exception as e:
        print(f"Batch failed: {e}")
        for ip in batch:
            results.append({"query": ip, "status": "fail", "message": str(e)})
    
    time.sleep(1.5)  # Rate limiting compliance for public API

# Save enriched results
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Saved enriched forensic IP dataset to {out_json}")

# Summarize top ASNs and Organizations
org_counts = {}
country_counts = {}
for r in results:
    if r.get("status") == "success":
        org = r.get("org", r.get("isp", "Unknown"))
        country = r.get("country", "Unknown")
        org_counts[org] = org_counts.get(org, 0) + 1
        country_counts[country] = country_counts.get(country, 0) + 1

top_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:15]
top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]

md_lines = [
    "# Forensic IP Address Sweep Dossier",
    f"- **Total Public IPs Swept:** {total_ips}",
    f"- **Enriched Results File:** file:///C:/EVIDENCE_LOCKER_MASTER/20_ANALYSIS/PUBLIC_IPS_ENRICHED_SWEEP.json",
    "",
    "## Top Autonomous Systems / Organizations",
    "| Organization / ISP | Count | Percentage |",
    "|---|---|---|"
]

for org, count in top_orgs:
    pct = round((count / total_ips) * 100, 2)
    md_lines.append(f"| {org} | {count} | {pct}% |")

md_lines.extend([
    "",
    "## Top Geographic Countries",
    "| Country | Count | Percentage |",
    "|---|---|---|"
])

for cty, count in top_countries:
    pct = round((count / total_ips) * 100, 2)
    md_lines.append(f"| {cty} | {count} | {pct}% |")

with open(out_dossier_section, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")

print(f"Generated Forensic IP Dossier at {out_dossier_section}")

# Mirror results to Google Drive
subprocess.run(["rclone", "copy", out_json, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/20_ANALYSIS", "-v"])
subprocess.run(["rclone", "copy", out_dossier_section, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX", "-v"])
