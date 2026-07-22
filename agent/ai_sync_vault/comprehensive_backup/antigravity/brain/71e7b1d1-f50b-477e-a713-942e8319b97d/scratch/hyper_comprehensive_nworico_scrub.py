import os
import re
import sys
import pandas as pd
from google.cloud import bigquery

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

file_path = r"C:\Users\HP\OneDrive\Documents\Master Osint Sheet.xlsx"
client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"

print("==================================================================")
print("RUNNING HYPER-COMPREHENSIVE NWORICO WORKBOOK SCRUB")
print("==================================================================\n")

print("Step 1: Extracting ALL cell contents across all 38 original sheets...")
xl = pd.ExcelFile(file_path)

all_extracted_entities = set()
words_to_check = set()

generic_terms = {
    'next id', 'id', 'name', 'type', 'notes', 'status', 'n/a', 'tbd', 'none', 'unknown', 
    'yes', 'no', 'active', 'inactive', 'contractor', 'person', 'agency', 'company', 
    'organization', 'nonprofit', 'shell_co', 'toxic_site', 'unclaimed_prop', 'phone', 
    'email', 'address', 'bates_ref', 'date', 'last_updated', 'source_doc', 'source_page', 
    'quote_snippet', 'file_hash', 'legal_relevance', 'related_entity_ids', 'related_ids',
    'primary_tab', 'entity_id', 'entity_type', 'entity_name', 'public_evidence', 
    'non_public_evidence', 'placeholder', 'total', 'grand total', 'null', 'nan'
}

for sheet in xl.sheet_names:
    if 'I-Soon' in sheet:
        continue # Avoid matching against our own new I-Soon tabs
    
    df = xl.parse(sheet)
    for col in df.columns:
        for val in df[col].dropna():
            val_str = str(val).strip()
            val_lower = val_str.lower()
            
            # Skip short values or generic ones
            if not val_str or val_lower in generic_terms or len(val_str) < 3:
                continue
            if re.match(r'^\d+$', val_str) and len(val_str) < 7:
                continue # Skip small numbers
            if val_str.startswith('Next ID:') or val_str.startswith('CON-') or val_str.startswith('EV-') or val_str.startswith('PE-') or val_str.startswith('TL-'):
                continue # Skip ID references
            
            # Add full string to entities to check
            all_extracted_entities.add(val_str)
            
            # Extract individual word parts to catch names
            for word in re.split(r'[\s,;.()\-"]+', val_str):
                word_clean = word.strip().strip("'").strip('"')
                if len(word_clean) >= 4 and word_clean.lower() not in generic_terms:
                    words_to_check.add(word_clean)

print(f"Extracted:\n  - Unique Cell Strings: {len(all_extracted_entities)}\n  - Unique Word Tokens: {len(words_to_check)}")

print("\nStep 2: Scrubbing all tokens against BigQuery I-Soon tables...")
matches = []

# Let's filter words_to_check to avoid extremely common English words or general verbs
common_english_words = {
    'association', 'organization', 'foundation', 'corporation', 'committee', 'incorporated',
    'department', 'district', 'california', 'county', 'american', 'national', 'services',
    'housing', 'health', 'public', 'social', 'family', 'alliance', 'community', 'center',
    'board', 'street', 'avenue', 'road', 'court', 'state', 'federal', 'united', 'states',
    'office', 'management', 'project', 'program', 'officer', 'director', 'attorney', 'lawyer'
}
filtered_words = {w for e in all_extracted_entities for w in re.split(r'[\s,;.()\-"]+', e) if len(w) >= 4 and w.lower() not in generic_terms and w.lower() not in common_english_words and not re.match(r'^\d+$', w)}

print(f"Filtered to {len(filtered_words)} unique high-value search tokens.")

# Let's chunk and search in BigQuery
filtered_list = list(filtered_words)
chunk_size = 80

for i in range(0, len(filtered_list), chunk_size):
    chunk = filtered_list[i:i+chunk_size]
    # Build regex patterns
    regex_pattern = "|".join([re.escape(e) for e in chunk])
    
    # WeChat Search
    chat_q = f"""
    SELECT file_name, timestamp, sender, recipient, message
    FROM `{dataset_id}.isoon_wechat_chats`
    WHERE REGEXP_CONTAINS(LOWER(message), r'(?i)\\b({regex_pattern})\\b')
    """
    try:
        df_chats = client.query(chat_q).to_dataframe()
        for _, r in df_chats.iterrows():
            # Find which word(s) matched
            matched_words = [w for w in chunk if w.lower() in r['message'].lower()]
            matches.append(f"[WeChat Chat Match] Token(s) {matched_words} found in chat by {r['sender']} at {r['timestamp']}: '{r['message']}' ({r['file_name']})")
    except Exception as e:
        pass

    # CRM Search
    crm_q = f"""
    SELECT operator, file_name, phone, name, raw_data
    FROM `{dataset_id}.isoon_telecom_crm`
    WHERE REGEXP_CONTAINS(LOWER(name), r'(?i)\\b({regex_pattern})\\b')
       OR REGEXP_CONTAINS(LOWER(raw_data), r'(?i)\\b({regex_pattern})\\b')
    """
    try:
        df_crm = client.query(crm_q).to_dataframe()
        for _, r in df_crm.iterrows():
            matched_words = [w for w in chunk if w.lower() in str(r['name']).lower() or w.lower() in str(r['raw_data']).lower()]
            matches.append(f"[Telecom CRM Match] Token(s) {matched_words} found in CRM subscriber: {r['name']} | Phone: {r['phone']} | Address: {r['raw_data']} ({r['file_name']})")
    except Exception as e:
         pass

print("\n==================================================================")
print("HYPER-COMPREHENSIVE NWORICO SCRUB RESULTS SUMMARY")
print("==================================================================\n")

if matches:
    print(f"SUCCESS: Found {len(matches)} potential overlaps/connections!")
    for m in matches[:100]: # print first 100
        print(m)
    if len(matches) > 100:
        print(f"... and {len(matches) - 100} more matches.")
else:
    print("No connections found between any NWORICO workbook tokens and the exfiltrated I-Soon databases.")
print("\nScrub finished successfully.")
print("==================================================================")
