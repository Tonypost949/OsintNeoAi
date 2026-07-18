import os
import re
import sys
import pandas as pd
from google.cloud import bigquery

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"
brain_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d"
master_sheet_path = r"C:\Users\HP\OneDrive\Documents\Master Osint Sheet.xlsx"

print("==================================================================")
print("RUNNING COMPREHENSIVE 'ALL AVENUES' DEEP FORENSICS AUDIT")
print("==================================================================\n")

# -------------------------------------------------------------
# AVENUE 1: US TARGET SCAN (US / GOV / MIL / EDU IN I-SOON DATA)
# -------------------------------------------------------------
print("Avenue 1: Searching I-Soon dataset for US Hacking Targets...")

us_queries = {
    "us_chats": f"""
        SELECT timestamp, sender, recipient, message, file_name
        FROM `{dataset_id}.isoon_wechat_chats`
        WHERE REGEXP_CONTAINS(LOWER(message), r'美国|美方|\\.gov|\\.mil|\\.edu|nasa|fbi|cia|whitehouse|pentagon|ca\\.gov|加州')
        LIMIT 50
    """,
    "us_crm": f"""
        SELECT operator, phone, name, address, file_name
        FROM `{dataset_id}.isoon_telecom_crm`
        WHERE REGEXP_CONTAINS(LOWER(address), r'usa|united states|america|california|\\.gov')
           OR REGEXP_CONTAINS(LOWER(name), r'\\.gov|\\.mil|\\.edu')
        LIMIT 50
    """
}

us_results = []
try:
    df_us_chats = client.query(us_queries["us_chats"]).to_dataframe()
    if len(df_us_chats) > 0:
        us_results.append(f"Found {len(df_us_chats)} mentions of US/CA/military/education keywords in WeChat chats:")
        for _, r in df_us_chats.iterrows():
            us_results.append(f"  - [{r['timestamp']}] {r['sender']} -> {r['recipient']} ({r['file_name']}): '{r['message']}'")
    else:
        us_results.append("No US/CA keywords found in WeChat chats.")
except Exception as e:
    us_results.append(f"Error querying US chats: {e}")

try:
    df_us_crm = client.query(us_queries["us_crm"]).to_dataframe()
    if len(df_us_crm) > 0:
        us_results.append(f"\nFound {len(df_us_crm)} matching US/Gov/Edu profiles in Telecom CRM records:")
        for _, r in df_us_crm.iterrows():
            us_results.append(f"  - [{r['operator']}] {r['name']} | Phone: {r['phone']} | Address: {r['address']} ({r['file_name']})")
    else:
        us_results.append("No US/Gov/Edu profiles found in Telecom CRM.")
except Exception as e:
    us_results.append(f"Error querying US CRM: {e}")

# -------------------------------------------------------------
# AVENUE 2: LOCAL PDF EVIDENCE & INTEL DOCUMENT CROSS-CHECKS
# -------------------------------------------------------------
print("\nAvenue 2: Searching local files (Chen PDF, etc.) for I-Soon references...")

local_docs_to_check = [
    os.path.join(brain_dir, "scratch", "chen_extracted_text.txt"),
    os.path.join(brain_dir, "scratch", "chinese_matches.txt")
]

threat_intel_actors = ["吴海兵", "陈诚", "安旬", "isoon", "shutdown", "lengmo", "yuxi", "雨希", "sichuan anxun"]
local_doc_matches = []

for doc_path in local_docs_to_check:
    if os.path.exists(doc_path):
        print(f"  Scanning: {doc_path}")
        try:
            with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                content_lower = content.lower()
                for actor in threat_intel_actors:
                    if actor.lower() in content_lower:
                        # find matches with surrounding context
                        for m in re.finditer(re.escape(actor), content, re.IGNORECASE):
                            start = max(0, m.start() - 60)
                            end = min(len(content), m.end() + 60)
                            snippet = content[start:end].replace('\n', ' ').strip()
                            local_doc_matches.append(f"MATCH '{actor}' in {os.path.basename(doc_path)}:\n    '... {snippet} ...'")
        except Exception as e:
            local_doc_matches.append(f"Error reading {doc_path}: {e}")
    else:
         print(f"  Local file not found: {doc_path}")

# -------------------------------------------------------------
# AVENUE 3: IP ADDRESS & DOMAIN NETWORK HARVESTING & MATCHING
# -------------------------------------------------------------
print("\nAvenue 3: Extracting IP Addresses & Domains from Master Sheet...")

ip_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}\b')

extracted_ips = set()
extracted_domains = set()

try:
    xl = pd.ExcelFile(master_sheet_path)
    for sheet in xl.sheet_names:
        if 'I-Soon' in sheet:
            continue
        df = xl.parse(sheet)
        for col in df.columns:
            for val in df[col].dropna():
                val_str = str(val)
                # Find IPs
                for ip in ip_pattern.findall(val_str):
                    extracted_ips.add(ip)
                # Find Domains
                for dom in domain_pattern.findall(val_str):
                    dom_lower = dom.lower()
                    # Skip common formatting or file extension false positives
                    if not dom_lower.endswith(('.xlsx', '.docx', '.pdf', '.txt', '.png', '.jpg', '.zip', '.7z', '.json', '.xml', '.html', '.md', '.log', '.js')):
                         extracted_domains.add(dom_lower)
except Exception as e:
    print(f"Error harvesting IPs/domains from Master Sheet: {e}")

print(f"Harvested from Master Sheet:\n  - IPs found: {len(extracted_ips)}\n  - Domains found: {len(extracted_domains)}")
if extracted_ips:
    print(f"  IP Samples: {list(extracted_ips)[:5]}")
if extracted_domains:
    print(f"  Domain Samples: {list(extracted_domains)[:5]}")

network_matches = []
# Match harvested IPs/domains inside BigQuery I-Soon tables
if extracted_ips:
    print("\n  Scrubbing harvested IPs against exfiltrated databases...")
    ip_regex = "|".join([re.escape(ip) for ip in extracted_ips])
    ip_query = f"""
    SELECT file_name, timestamp, sender, recipient, message
    FROM `{dataset_id}.isoon_wechat_chats`
    WHERE REGEXP_CONTAINS(message, r'{ip_regex}')
    """
    try:
        df_ip_matches = client.query(ip_query).to_dataframe()
        if len(df_ip_matches) > 0:
            for _, r in df_ip_matches.iterrows():
                network_matches.append(f"IP MATCH in WeChat [{r['timestamp']}] {r['sender']}: '{r['message']}'")
    except Exception as e:
        pass

if extracted_domains:
    print("  Scrubbing harvested domains against exfiltrated databases...")
    # Clean domain set to avoid query blowup, picking highly unique domains (removing common ones like gmail.com, yahoo.com, google.com etc.)
    exclude_common = {'gmail.com', 'yahoo.com', 'google.com', 'outlook.com', 'hotmail.com', 'github.com', 'microsoft.com', 'apple.com', 'baidu.com', 'qq.com'}
    unique_domains = {d for d in extracted_domains if d not in exclude_common}
    if unique_domains:
        dom_regex = "|".join([re.escape(d) for d in unique_domains])
        dom_query = f"""
        SELECT file_name, timestamp, sender, recipient, message
        FROM `{dataset_id}.isoon_wechat_chats`
        WHERE REGEXP_CONTAINS(LOWER(message), r'{dom_regex}')
        """
        try:
            df_dom_matches = client.query(dom_query).to_dataframe()
            if len(df_dom_matches) > 0:
                for _, r in df_dom_matches.iterrows():
                    network_matches.append(f"DOMAIN MATCH in WeChat [{r['timestamp']}] {r['sender']}: '{r['message']}'")
        except Exception as e:
             pass

# -------------------------------------------------------------
# FINAL CONSOLIDATED REPORT
# -------------------------------------------------------------
print("\n==================================================================")
print("DEEP AUDIT REPORT RESULTS SUMMARY")
print("==================================================================\n")

print("--- Avenue 1 Results (US Targets) ---")
for r in us_results:
    print(r)

print("\n--- Avenue 2 Results (Local Doc Cross-Checks) ---")
if local_doc_matches:
    for m in local_doc_matches:
        print(m)
else:
    print("No matches for I-Soon/Anxun threat actors or tools found in any local files.")

print("\n--- Avenue 3 Results (IP/Domain Network Cross-Matches) ---")
if network_matches:
    for m in network_matches:
        print(m)
else:
    print("No matching IP addresses or unique domain associations found in exfiltrated threat intelligence records.")
print("\nDeep Audit Finished successfully.")
print("==================================================================")
