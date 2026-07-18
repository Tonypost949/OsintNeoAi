import sys
from google.cloud import bigquery

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"

print("Searching BigQuery I-Soon tables for overlaps/cross-connections...")

# Keywords representing Huntington Beach, Andrew Do, Viet America Society (VAS), Mercy House, local entities
local_kws = ["huntington", "surfcity", "surf city", "andrew", "vietamerica", "mercy house", "mercyhouse"]

# 1. Search WeChat Chats
print("\n--- Searching WeChat Chats ---")
chats_query = f"""
SELECT file_name, timestamp, sender, recipient, message
FROM `{dataset_id}.isoon_wechat_chats`
WHERE REGEXP_CONTAINS(LOWER(message), r'viet|vietnam|越南|huntington|surfcity|mercy|california|加州')
LIMIT 50
"""
df_chats = client.query(chats_query).to_dataframe()
print(f"Found {len(df_chats)} potential matches in WeChat chats.")
if len(df_chats) > 0:
    for idx, r in df_chats.head(15).iterrows():
        print(f"[{r['timestamp'] or 'No Date'}] {r['sender']} -> {r['recipient']} ({r['file_name']}):")
        print(f"  {r['message']}")
        print("-" * 40)

# 2. Search Telecom CRM
print("\n--- Searching Telecom CRM ---")
crm_query = f"""
SELECT operator, file_name, phone, name, iin_bin, address, passport, birth_date
FROM `{dataset_id}.isoon_telecom_crm`
WHERE REGEXP_CONTAINS(LOWER(name), r'viet|do|andrew|mercy|huntington')
   OR REGEXP_CONTAINS(LOWER(address), r'california|usa|huntington|加州')
LIMIT 50
"""
df_crm = client.query(crm_query).to_dataframe()
print(f"Found {len(df_crm)} matches in Telecom CRM.")
if len(df_crm) > 0:
    print(df_crm.head(10).to_string())

# 3. Search Telecom CDR
print("\n--- Searching Telecom CDR ---")
cdr_query = f"""
SELECT operator, file_name, called_num, calling_num, timestamp, duration_sec
FROM `{dataset_id}.isoon_telecom_cdr`
WHERE called_num LIKE '%714%' OR calling_num LIKE '%714%' -- 714 is the Area Code for Orange County / Huntington Beach!
LIMIT 50
"""
df_cdr = client.query(cdr_query).to_dataframe()
print(f"Found {len(df_cdr)} matches in Telecom CDR (Orange County Area Code 714).")
if len(df_cdr) > 0:
    print(df_cdr.head(10).to_string())
