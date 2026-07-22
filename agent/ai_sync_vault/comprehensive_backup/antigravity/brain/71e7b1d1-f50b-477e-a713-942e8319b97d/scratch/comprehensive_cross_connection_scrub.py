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

print("Step 1: Extracting ALL entities from Master OSINT Sheet...")
xl = pd.ExcelFile(file_path)

# Sets to store extracted indicators
unique_names = set()
unique_phones = set()
unique_emails = set()
unique_orgs = set()

# Helper patterns
phone_pattern = re.compile(r'\b\d{7,15}\b')
email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Exclusion list of generic terms and Excel headers
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
        col_lower = str(col).lower()
        
        # Check cell values
        for val in df[col].dropna():
            val_str = str(val).strip()
            val_lower = val_str.lower()
            
            # Skip empty, numeric codes, or generic headers
            if not val_str or val_lower in generic_terms or len(val_str) < 3:
                continue
            if re.match(r'^\d+$', val_str) and len(val_str) < 7:
                continue # Skip small numbers
            if val_str.startswith('Next ID:') or val_str.startswith('CON-') or val_str.startswith('EV-') or val_str.startswith('PE-') or val_str.startswith('TL-'):
                continue # Skip ID references
            
            # Find emails
            emails = email_pattern.findall(val_str)
            for email in emails:
                unique_emails.add(email.lower())
                
            # Find phone numbers
            phones = phone_pattern.findall(val_str)
            for phone in phones:
                unique_phones.add(phone)
                
            # Distinguish Names and Orgs based on column types
            if 'name' in col_lower or 'person' in col_lower or 'contact' in col_lower or 'custodian' in col_lower:
                if len(val_str) > 3:
                    # Clean up enclosing quotes
                    val_clean = val_str.strip('"').strip("'").strip()
                    if val_clean.lower() not in generic_terms:
                        unique_names.add(val_clean)
            elif 'agency' in col_lower or 'company' in col_lower or 'contractor' in col_lower or 'nonprofit' in col_lower or 'organization' in col_lower:
                if len(val_str) > 3:
                    val_clean = val_str.strip('"').strip("'").strip()
                    if val_clean.lower() not in generic_terms:
                        unique_orgs.add(val_clean)

print(f"Extracted Indicators:")
print(f"  - Unique Emails: {len(unique_emails)}")
print(f"  - Unique Phones: {len(unique_phones)}")
print(f"  - Unique Names: {len(unique_names)}")
print(f"  - Unique Organizations: {len(unique_orgs)}")

print("\nStep 2: Scrubbing against BigQuery I-Soon tables...")

matches = []

# Helper function to query BQ
def bq_query(q):
    return client.query(q).to_dataframe()

# A. Phone and Email Exact Matches
if unique_emails:
    emails_list = ", ".join([f"'{e}'" for e in unique_emails])
    print("Checking exact email matches in CRM databases...")
    crm_email_q = f"""
    SELECT 'CRM' as source_table, operator, file_name, phone, name, raw_data
    FROM `{dataset_id}.isoon_telecom_crm`
    WHERE LOWER(raw_data) LIKE ANY ({", ".join([f"'%{e}%'" for e in unique_emails])})
    """
    try:
        res = bq_query(crm_email_q)
        if len(res) > 0:
            for _, r in res.iterrows():
                matches.append(f"EMAIL MATCH in CRM: {r['name']} ({r['phone']}) in file {r['file_name']} (Operator: {r['operator']})")
    except Exception as e:
        print(f"Email check error: {e}")

if unique_phones:
    # We clean phone numbers from regional formats to check matches
    cleaned_phones = set()
    for p in unique_phones:
        # standard 10-digit check
        p_clean = re.sub(r'\D', '', p)
        if len(p_clean) >= 7:
            cleaned_phones.add(p_clean[-10:]) # last 10 digits
            
    if cleaned_phones:
        print("Checking exact phone matches in CDR and CRM...")
        # Check CRM
        crm_phone_q = f"""
        SELECT 'CRM' as source_table, operator, file_name, phone, name, raw_data
        FROM `{dataset_id}.isoon_telecom_crm`
        WHERE REGEXP_CONTAINS(phone, r'{"|".join(cleaned_phones)}')
        """
        try:
            res = bq_query(crm_phone_q)
            if len(res) > 0:
                for _, r in res.iterrows():
                    matches.append(f"PHONE MATCH in CRM: {r['name']} ({r['phone']}) in file {r['file_name']}")
        except Exception as e:
            print(f"Phone CRM check error: {e}")
            
        # Check CDR
        cdr_phone_q = f"""
        SELECT 'CDR' as source_table, operator, file_name, called_num, calling_num, timestamp
        FROM `{dataset_id}.isoon_telecom_cdr`
        WHERE REGEXP_CONTAINS(called_num, r'{"|".join(cleaned_phones)}')
           OR REGEXP_CONTAINS(calling_num, r'{"|".join(cleaned_phones)}')
        """
        try:
            res = bq_query(cdr_phone_q)
            if len(res) > 0:
                for _, r in res.iterrows():
                    matches.append(f"PHONE MATCH in CDR: {r['calling_num']} -> {r['called_num']} at {r['timestamp']} in file {r['file_name']}")
        except Exception as e:
            print(f"Phone CDR check error: {e}")

# B. Name and Organization Matches
print("Checking Name & Organization matches in WeChat chats and Telecom CRM...")

# To prevent BigQuery SQL overflow or excessive query times, we do a combined pattern match.
# We will check names that are likely to be unique or high-value.
all_text_entities = unique_names.union(unique_orgs)
# Exclude entities with purely generic names or short tokens
filtered_text_entities = {e for e in all_text_entities if len(e) >= 4 and not re.match(r'^\d+$', e)}

print(f"Total filtered names/orgs to check: {len(filtered_text_entities)}")

# Chunk entities to prevent regex size limitations in BigQuery
entities_list = list(filtered_text_entities)
chunk_size = 50

for i in range(0, len(entities_list), chunk_size):
    chunk = entities_list[i:i+chunk_size]
    # Escape single quotes and build query
    regex_pattern = "|".join([re.escape(e) for e in chunk])
    
    # Check CRM Name Field
    crm_name_q = f"""
    SELECT operator, file_name, phone, name, raw_data
    FROM `{dataset_id}.isoon_telecom_crm`
    WHERE REGEXP_CONTAINS(LOWER(name), r'(?i){regex_pattern}')
    """
    try:
        res = bq_query(crm_name_q)
        if len(res) > 0:
            for _, r in res.iterrows():
                matches.append(f"NAME MATCH in CRM: {r['name']} ({r['phone']}) in file {r['file_name']}")
    except Exception as e:
         pass

    # Check WeChat Messages
    chat_msg_q = f"""
    SELECT file_name, timestamp, sender, recipient, message
    FROM `{dataset_id}.isoon_wechat_chats`
    WHERE REGEXP_CONTAINS(LOWER(message), r'(?i){regex_pattern}')
    """
    try:
        res = bq_query(chat_msg_q)
        if len(res) > 0:
            for _, r in res.iterrows():
                matches.append(f"NAME/ORG MATCH in WeChat [{r['timestamp']}]: {r['sender']} -> {r['recipient']}: '{r['message']}' ({r['file_name']})")
    except Exception as e:
         pass

print("\n=== FINAL SCRUB RESULTS ===")
print(f"Total Matches Found: {len(matches)}")
for match in matches:
    print(match)
