import os
import re
import sys
from bs4 import BeautifulSoup
from google.cloud import bigquery

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Paths
base_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)"
md_dir = os.path.join(base_dir, "MD")
txt_dir = os.path.join(base_dir, "TXT")
log_dir = os.path.join(base_dir, "LOG")

client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"

print("Parsing WeChat chat logs...")
chats = []
md_files = [f for f in os.listdir(md_dir) if f.lower().endswith('.md')]

for idx, f in enumerate(md_files):
    fp = os.path.join(md_dir, f)
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            content = file_obj.read()
            if "<table" in content:
                soup = BeautifulSoup(content, 'html.parser')
                rows = soup.find_all('tr')
                for r in rows:
                    cols = r.find_all(['td', 'th'])
                    if len(cols) == 4:
                        # Skip header
                        if cols[0].get_text().strip().lower() == "time":
                            continue
                        time_str = cols[0].get_text().strip()
                        sender = cols[1].get_text().strip()
                        recipient = cols[2].get_text().strip()
                        
                        # Extract links / attachments
                        msg_col = cols[3]
                        msg_text = msg_col.get_text().strip()
                        attachments = []
                        for a in msg_col.find_all('a'):
                            attachments.append(f"{a.get_text().strip()} ({a.get('href', '')})")
                        
                        chats.append({
                            "file_name": f,
                            "timestamp": time_str if time_str else None,
                            "sender": sender,
                            "recipient": recipient,
                            "message": msg_text,
                            "attachments": ", ".join(attachments) if attachments else None
                        })
    except Exception as e:
        print(f"Error parsing {f}: {e}")

print(f"Parsed {len(chats)} WeChat chat messages.")

# Parse Telecom CDR records
print("Parsing Telecom CDR records...")
cdr_records = []

# 1. Beeline-cdr
beeline_files = [f for f in os.listdir(txt_dir) if f.startswith('beeline-7') or f == 'beeline-cdr.txt']
for bf in beeline_files:
    bfp = os.path.join(txt_dir, bf)
    try:
        with open(bfp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            lines = file_obj.readlines()
            # Headers: SUBS_KEY,CALL_START_TIME,CALLED_NUM,CALLING_NUM,CELL_ID,LAC,ROUNDED_CALL_DURATION_SEC,CALL_FORWARD_NUM,IMEI,IMSI,ORIG_CELL_ID
            headers = [h.strip().replace('\ufeff', '') for h in lines[0].split(',')]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= min(5, len(headers)):
                    row_dict = dict(zip(headers, parts))
                    # Handle timestamp formats
                    ts = row_dict.get('CALL_START_TIME')
                    if ts:
                        # format can be DD.MM.YYYY HH:MM:SS or other. Let's normalize it to YYYY-MM-DD HH:MM:SS
                        # Example: 01.06.2018 20:08:34 -> 2018-06-01 20:08:34
                        m = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2}:\d{2})', ts)
                        if m:
                            ts = f"{m.group(3)}-{m.group(2)}-{m.group(1)} {m.group(4)}"
                    
                    cdr_records.append({
                        "operator": "beeline",
                        "file_name": bf,
                        "subs_key": row_dict.get('SUBS_KEY'),
                        "timestamp": ts,
                        "called_num": row_dict.get('CALLED_NUM'),
                        "calling_num": row_dict.get('CALLING_NUM'),
                        "duration_sec": int(row_dict.get('ROUNDED_CALL_DURATION_SEC', 0)) if row_dict.get('ROUNDED_CALL_DURATION_SEC', '0').isdigit() else None,
                        "cell_id": row_dict.get('CELL_ID') or row_dict.get('ORIG_CELL_ID'),
                        "lac": row_dict.get('LAC'),
                        "imei": row_dict.get('IMEI'),
                        "imsi": row_dict.get('IMSI'),
                        "raw_data": line.strip()
                    })
    except Exception as e:
        print(f"Error parsing Beeline CDR {bf}: {e}")

# 2. Chinese 话单.txt (which contains CDR rows too)
hd_fp = os.path.join(txt_dir, "话单.txt")
if os.path.exists(hd_fp):
    try:
        with open(hd_fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            lines = file_obj.readlines()
            headers = [h.strip().replace('\ufeff', '') for h in lines[0].split('\t')]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split('\t')]
                if len(parts) >= len(headers):
                    row_dict = dict(zip(headers, parts))
                    ts = row_dict.get('SEIZURE_TM') or row_dict.get('ANSWER_TM')
                    if ts:
                        m = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2}:\d{2})', ts)
                        if m:
                            ts = f"{m.group(3)}-{m.group(2)}-{m.group(1)} {m.group(4)}"
                    cdr_records.append({
                        "operator": "kazakhtelecom",
                        "file_name": "话单.txt",
                        "subs_key": row_dict.get('CDR_ID'),
                        "timestamp": ts,
                        "called_num": row_dict.get('CALLED_NUM'),
                        "calling_num": row_dict.get('CALLING_NUM'),
                        "duration_sec": int(row_dict.get('DURATION', 0)) if row_dict.get('DURATION', '0').isdigit() else None,
                        "cell_id": None,
                        "lac": None,
                        "imei": None,
                        "imsi": None,
                        "raw_data": line.strip()
                    })
    except Exception as e:
        print(f"Error parsing 话单.txt: {e}")

# 3. Tele2 CDR
tele2_cdr_fp = os.path.join(log_dir, "tele2-cdr.log")
if os.path.exists(tele2_cdr_fp):
    try:
        with open(tele2_cdr_fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            lines = file_obj.readlines()
            headers = [h.strip().replace('\ufeff', '') for h in lines[0].split('\t')]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split('\t')]
                if len(parts) >= len(headers):
                    row_dict = dict(zip(headers, parts))
                    cdr_records.append({
                        "operator": "tele2",
                        "file_name": "tele2-cdr.log",
                        "subs_key": row_dict.get('USI'),
                        "timestamp": row_dict.get("TO_CHAR(START_TIME,'YYYY-MM-DDHH24:MI:SS')"),
                        "called_num": row_dict.get('DIALED'),
                        "calling_num": row_dict.get('PHONE'),
                        "duration_sec": int(row_dict.get('DURATION', 0)) if row_dict.get('DURATION', '0').isdigit() else None,
                        "cell_id": row_dict.get('CELL_A'),
                        "lac": row_dict.get('LAC_A'),
                        "imei": row_dict.get('MS_NUM'),
                        "imsi": row_dict.get('USI'),
                        "raw_data": line.strip()
                    })
    except Exception as e:
        print(f"Error parsing tele2-cdr.log: {e}")

print(f"Parsed {len(cdr_records)} Telecom CDR records.")

# Parse Telecom CRM records
print("Parsing Telecom CRM records...")
crm_records = []

# 1. Beeline CRM
beeline_crm_fp = os.path.join(txt_dir, "beeline-crm.txt")
if os.path.exists(beeline_crm_fp):
    try:
        with open(beeline_crm_fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            lines = file_obj.readlines()
            headers = [h.strip().replace('\ufeff', '') for h in lines[0].split(',')]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= len(headers):
                    row_dict = dict(zip(headers, parts))
                    phone = row_dict.get('PHONE')
                    name = f"{row_dict.get('FIRST_NAME', '')} {row_dict.get('LAST_NAME', '')}".strip()
                    address = f"{row_dict.get('HOUSE_NUMBER', '')} {row_dict.get('STREET_NAME', '')} {row_dict.get('STREET_SUFFIX', '')}, {row_dict.get('CITY', '')}, {row_dict.get('COUNTRY', '')}".strip()
                    crm_records.append({
                        "operator": "beeline",
                        "file_name": "beeline-crm.txt",
                        "phone": phone,
                        "name": name,
                        "iin_bin": None,
                        "city": row_dict.get('CITY'),
                        "address": address,
                        "passport": None,
                        "birth_date": None,
                        "raw_data": line.strip()
                    })
    except Exception as e:
        print(f"Error parsing Beeline CRM: {e}")

# 2. CRM.txt (Another massive CRM dump)
crm_txt_fp = os.path.join(txt_dir, "CRM.txt")
if os.path.exists(crm_txt_fp):
    try:
        with open(crm_txt_fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            lines = file_obj.readlines()
            headers = [h.strip().replace('\ufeff', '') for h in lines[0].split('\t')]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split('\t')]
                if len(parts) >= len(headers):
                    row_dict = dict(zip(headers, parts))
                    crm_records.append({
                        "operator": "kazakhtelecom",
                        "file_name": "CRM.txt",
                        "phone": row_dict.get('MOBILE_PHONE') or row_dict.get('PRIMARY_MOBILE_PHONE'),
                        "name": row_dict.get('CUSTOMER_NAME') or row_dict.get('NAME'),
                        "iin_bin": row_dict.get('IDENTIFICATION_NUMBER'),
                        "city": row_dict.get('TOWN_NAME'),
                        "address": row_dict.get('ADDRESS'),
                        "passport": None,
                        "birth_date": None,
                        "raw_data": line.strip()
                    })
    except Exception as e:
        print(f"Error parsing CRM.txt: {e}")

# 3. Tele2 CRM
tele2_crm_fp = os.path.join(log_dir, "tele2-crm.log")
if os.path.exists(tele2_crm_fp):
    try:
        with open(tele2_crm_fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
            lines = file_obj.readlines()
            headers = [h.strip().replace('\ufeff', '') for h in lines[0].split('\t')]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split('\t')]
                if len(parts) >= len(headers):
                    row_dict = dict(zip(headers, parts))
                    crm_records.append({
                        "operator": "tele2",
                        "file_name": "tele2-crm.log",
                        "phone": row_dict.get('PHONE手机号') or row_dict.get('PHONE_ID用户手机ID'),
                        "name": row_dict.get('NAME姓名'),
                        "iin_bin": row_dict.get('INN身份证号'),
                        "city": row_dict.get('ADDR_CITY城市'),
                        "address": f"{row_dict.get('ADDR_STREET街道', '')} {row_dict.get('ADDR_HOUSE房间号', '')} {row_dict.get('ADDR_NAME具体地址', '')}".strip(),
                        "passport": row_dict.get('PASPORT证件？'),
                        "birth_date": row_dict.get('DATE_OF_BIRTH出生日期'),
                        "raw_data": line.strip()
                    })
    except Exception as e:
        print(f"Error parsing tele2-crm.log: {e}")

print(f"Parsed {len(crm_records)} Telecom CRM records.")

# Helper function to create BigQuery tables
def create_table_if_not_exists(table_name, schema):
    table_ref = f"{dataset_id}.{table_name}"
    try:
        client.get_table(table_ref)
        print(f"Table {table_name} already exists.")
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"Table {table_name} created successfully.")

# Create Tables
chats_schema = [
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("timestamp", "STRING"),
    bigquery.SchemaField("sender", "STRING"),
    bigquery.SchemaField("recipient", "STRING"),
    bigquery.SchemaField("message", "STRING"),
    bigquery.SchemaField("attachments", "STRING"),
]

cdr_schema = [
    bigquery.SchemaField("operator", "STRING"),
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("subs_key", "STRING"),
    bigquery.SchemaField("timestamp", "STRING"),
    bigquery.SchemaField("called_num", "STRING"),
    bigquery.SchemaField("calling_num", "STRING"),
    bigquery.SchemaField("duration_sec", "INTEGER"),
    bigquery.SchemaField("cell_id", "STRING"),
    bigquery.SchemaField("lac", "STRING"),
    bigquery.SchemaField("imei", "STRING"),
    bigquery.SchemaField("imsi", "STRING"),
    bigquery.SchemaField("raw_data", "STRING"),
]

crm_schema = [
    bigquery.SchemaField("operator", "STRING"),
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("phone", "STRING"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("iin_bin", "STRING"),
    bigquery.SchemaField("city", "STRING"),
    bigquery.SchemaField("address", "STRING"),
    bigquery.SchemaField("passport", "STRING"),
    bigquery.SchemaField("birth_date", "STRING"),
    bigquery.SchemaField("raw_data", "STRING"),
]

create_table_if_not_exists("isoon_wechat_chats", chats_schema)
create_table_if_not_exists("isoon_telecom_cdr", cdr_schema)
create_table_if_not_exists("isoon_telecom_crm", crm_schema)

# Chunk and insert into BigQuery
def insert_chunks(table_name, rows):
    table_ref = f"{dataset_id}.{table_name}"
    chunk_size = 500
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i+chunk_size]
        errors = client.insert_rows_json(table_ref, chunk)
        if errors:
            print(f"Error inserting chunk into {table_name}: {errors[:5]}")
        else:
            print(f"Successfully inserted {len(chunk)} rows into {table_name}.")

print("Uploading to BigQuery...")
if chats:
    insert_chunks("isoon_wechat_chats", chats)
if cdr_records:
    insert_chunks("isoon_telecom_cdr", cdr_records)
if crm_records:
    insert_chunks("isoon_telecom_crm", crm_records)

print("BigQuery Ingestion Complete!")
