import json
import os
import re
from google.cloud import bigquery

# Hardcode the project mappings for robust cross-project queries
PHASE2_PROJECT = "project-743aab84-f9a5-4ec7-954"
BASELINE_PROJECT = "noble-beanbag-497411-m4"

client = bigquery.Client()

# Dataset IDs
phase2_dataset = f"{PHASE2_PROJECT}.national_audits"
baseline_dataset = f"{BASELINE_PROJECT}.national_audits"
ppp_dataset = f"{BASELINE_PROJECT}.ppp_rico"

print("\n==================================================")
print("1. RUNNING JOINT MATRIX FORENSIC INVESTIGATION (PHASE 2)")
print("==================================================\n")

results_dict = {}

# 1. Dehashed HBPD scan credentials & endpoints matching katana/kroll/conway/nunez/barnes
print("Auditing Dehashed HBPD credential logs...")
q_dehashed = f"""
SELECT id, chatGroupId, role, created_at, contents_raw 
FROM `{phase2_dataset}.dehashed_hbpd_scan` 
WHERE LOWER(contents_raw) LIKE '%katana%' 
   OR LOWER(contents_raw) LIKE '%kroll%' 
   OR LOWER(contents_raw) LIKE '%conway%'
   OR LOWER(contents_raw) LIKE '%nunez%'
   OR LOWER(contents_raw) LIKE '%barnes%'
"""
try:
    rows = list(client.query(q_dehashed).result())
    print(f" -> Found {len(rows)} matching dehashed rows.")
    results_dict["dehashed_matches"] = [dict(r) for r in rows]
    for idx, r in enumerate(rows[:2]):
        print(f"    Match {idx+1}: ID={r['id']} | Date={r['created_at']} | Text Snippet: {r['contents_raw'][:300]}...")
except Exception as e:
    print(f"Error querying dehashed_hbpd_scan: {e}")
    results_dict["dehashed_matches"] = []

# 2. Orange County structural failure investigation matching Barnes, Shea, eviction, witness tampering
print("\nAuditing Structural Failure & Eviction timeline...")
q_structural = f"""
SELECT id, chatGroupId, role, created_at, contents_raw 
FROM `{phase2_dataset}.orange_county_structural_failure` 
WHERE LOWER(contents_raw) LIKE '%barnes%' 
   OR LOWER(contents_raw) LIKE '%shea%'
   OR LOWER(contents_raw) LIKE '%eviction%'
   OR LOWER(contents_raw) LIKE '%tampering%'
"""
try:
    rows = list(client.query(q_structural).result())
    print(f" -> Found {len(rows)} matching structural failure investigation rows.")
    results_dict["structural_matches"] = [dict(r) for r in rows]
    for idx, r in enumerate(rows[:2]):
        print(f"    Match {idx+1}: ID={r['id']} | Date={r['created_at']} | Text Snippet: {r['contents_raw'][:300]}...")
except Exception as e:
    print(f"Error querying orange_county_structural_failure: {e}")
    results_dict["structural_matches"] = []

# 3. OSINT Neo Chat transcripts
print("\nAuditing OSINT Neo Chat transcript logs...")
q_chat = f"""
SELECT sequence_id, timestamp, user_prompt, assistant_response
FROM `{phase2_dataset}.osint_neo_chat_transcript`
WHERE LOWER(user_prompt) LIKE '%nunez%' OR LOWER(assistant_response) LIKE '%nunez%'
   OR LOWER(user_prompt) LIKE '%barnes%' OR LOWER(assistant_response) LIKE '%barnes%'
   OR LOWER(user_prompt) LIKE '%shea%' OR LOWER(assistant_response) LIKE '%shea%'
"""
try:
    rows = list(client.query(q_chat).result())
    print(f" -> Found {len(rows)} matching chat transcript sessions.")
    results_dict["chat_matches"] = [dict(r) for r in rows]
except Exception as e:
    print(f"Error querying osint_neo_chat_transcript: {e}")
    results_dict["chat_matches"] = []

# 4. Acrobat Adobe URLs tracking index
print("\nAuditing Acrobat Adobe tracker links...")
q_acrobat = f"""
SELECT * FROM `{phase2_dataset}.acrobat_adobe_urls` LIMIT 10
"""
try:
    rows = list(client.query(q_acrobat).result())
    print(f" -> Found {len(rows)} Acrobat URL tracker records.")
    results_dict["acrobat_urls"] = [dict(r) for r in rows]
    for r in rows:
        print(f"    URL: {r.get('URL')} | Title: {r.get('Title')} | Source: {r.get('source_file')}")
except Exception as e:
    print(f"Error querying acrobat_adobe_urls: {e}")
    results_dict["acrobat_urls"] = []

print("\n==================================================")
print("2. AUDITING OUT-OF-STATE & OFFSHORE REMITTANCE PATHS")
print("==================================================\n")

# 1. State-level records with offshore/foreign keywords (all_state_records in BASELINE_PROJECT)
print("Tracing international/Philippine remittance entities in state audit records...")
q_remit = f"""
SELECT state, npi.organization_name, npi.cms_billing_code, npi.unaccounted_fund_delta
FROM `{baseline_dataset}.all_state_records`,
UNNEST(non_profiteers_index) as npi
WHERE REGEXP_CONTAINS(LOWER(npi.organization_name), r'(remit|overseas|foreign|international|philippines|manila)')
ORDER BY CAST(npi.unaccounted_fund_delta AS NUMERIC) DESC
"""
try:
    rows = list(client.query(q_remit).result())
    print(f" -> Found {len(rows)} international/Philippine entries in state audits.")
    results_dict["all_state_remittances"] = [dict(r) for r in rows]
    for r in rows[:10]:
         print(f"    State: {r['state']} | Delta: ${float(r.get('unaccounted_fund_delta', 0)):,.2f} | Organization: {r['organization_name']}")
except Exception as e:
    print(f"Error querying all_state_records: {e}")
    results_dict["all_state_remittances"] = []

# 2. Out-of-state PPP loans for Triumvirate, Stewart, L2T (ppp_150k_plus in BASELINE_PROJECT)
print("\nScanning PPP records for target out-of-state corporate shells...")
q_ppp = f"""
SELECT BorrowerName, BorrowerCity, BorrowerState, InitialApprovalAmount, DateApproved, ServicingLenderName
FROM `{ppp_dataset}.ppp_150k_plus`
WHERE UPPER(BorrowerName) LIKE '%TRIUMVIRATE%'
   OR UPPER(BorrowerName) LIKE '%STEWART INDUSTRIES%'
   OR UPPER(BorrowerName) LIKE '%L2T MEDIA%'
ORDER BY InitialApprovalAmount DESC
"""
try:
    rows = list(client.query(q_ppp).result())
    print(f" -> Found {len(rows)} out-of-state PPP borrower records.")
    results_dict["out_of_state_ppp"] = [dict(r) for r in rows]
    for r in rows:
        print(f"    Name: {r['BorrowerName']} | Amt: ${float(r['InitialApprovalAmount']):,.2f} | Location: {r['BorrowerCity']}, {r['BorrowerState']}")
except Exception as e:
    print(f"Error querying ppp_150k_plus: {e}")
    results_dict["out_of_state_ppp"] = []

# 3. Global/Offshore indicators in Gmail (gmail_index in BASELINE_PROJECT)
print("\nAuditing mail spool for remittance wire transfers & overseas transactions...")
q_gmail = f"""
SELECT subject, sender, date_header, snippet
FROM `{baseline_dataset}.gmail_index`
WHERE REGEXP_CONTAINS(LOWER(subject), r'(remit|wire transfer|philippin|manila|foreign fund|overseas|western union|international transfer)')
ORDER BY date_header DESC LIMIT 15
"""
try:
    rows = list(client.query(q_gmail).result())
    print(f" -> Found {len(rows)} matching email logs.")
    results_dict["remittance_emails"] = [dict(r) for r in rows]
    for r in rows[:5]:
        print(f"    [{r['date_header']}] Sender: {r['sender']} | Subject: {r['subject']}")
except Exception as e:
    print(f"Error querying gmail_index: {e}")
    results_dict["remittance_emails"] = []

# 4. Out-of-state LLC shared address tracking (Triumvirate, Stewart, L2T in BASELINE_PROJECT)
print("\nAnalyzing OC LLC properties with out-of-state shared mailing addresses...")
q_llc = f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, LastSeller, LastSaleValue
FROM `{ppp_dataset}.hb_llcs`
WHERE REGEXP_CONTAINS(LOWER(MailAddress), r'(philippin|manila|foreign|overseas)')
   OR REGEXP_CONTAINS(LOWER(MailCity), r'(philippin|manila|foreign|overseas)')
   OR Owner1 IN ('STEWART INDUSTRIES LLC', 'TRIUMVIRATE LLC', 'L2T MEDIA LLC')
   OR Owner2 IN ('STEWART INDUSTRIES LLC', 'TRIUMVIRATE LLC', 'L2T MEDIA LLC')
ORDER BY LastSaleValue DESC
"""
try:
    rows = list(client.query(q_llc).result())
    print(f" -> Found {len(rows)} matching property shell records.")
    results_dict["llc_connections"] = [dict(r) for r in rows]
    for r in rows[:10]:
        print(f"    Owner: {r['Owner1']} | Site: {r['SiteAddress']} | Mail City: {r['MailCity']} | Sale: ${float(r.get('LastSaleValue') or 0):,.2f}")
except Exception as e:
    print(f"Error querying hb_llcs: {e}")
    results_dict["llc_connections"] = []

# Save unified data output
output_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\master_trace_results.json"
try:
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                return obj.isoformat()
            except AttributeError:
                return str(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, cls=DateTimeEncoder, indent=2)
    print(f"\n==================================================")
    print(f"SUCCESS: Unified master trace results written to:")
    print(f"  {output_path}")
    print(f"==================================================")
except Exception as e:
    print(f"\nError writing output file: {e}")
