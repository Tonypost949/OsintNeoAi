import json
import os
import re
import pandas as pd
from google.cloud import bigquery

# Initialize BigQuery Client
client = bigquery.Client()
dataset_id = "project-743aab84-f9a5-4ec7-954.national_audits"
downloads_path = r"C:\Users\HP\Downloads"

print("=========================================")
print("STARTING PHASE 2 BIGQUERY INGESTION")
print("=========================================\n")

# ----------------------------------------------------
# 1. Ingest Dehashed-HBPD-scan.json
# ----------------------------------------------------
dehashed_path = os.path.join(downloads_path, "Dehashed-HBPD-scan.json")
if os.path.exists(dehashed_path):
    print("Step 1/4: Ingesting Dehashed-HBPD-scan.json...")
    try:
        with open(dehashed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        flat_data = []
        for idx, item in enumerate(data):
            flat_data.append({
                "id": item.get("id", f"msg_{idx}"),
                "chatGroupId": item.get("chatGroupId", "unknown"),
                "role": item.get("role", "unknown"),
                "model": item.get("model", ""),
                "displayModel": item.get("displayModel", ""),
                "contents_raw": json.dumps(item.get("contents", [])),
                "created_at": str(item.get("created_at", "")),
                "updated_at": int(item.get("updated_at", 0)) if item.get("updated_at") is not None else None
            })
            
        table_ref = f"{dataset_id}.dehashed_hbpd_scan"
        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_json(flat_data, table_ref, job_config=job_config)
        job.result()
        print(f"Successfully loaded {len(flat_data)} rows into {table_ref}.\n")
    except Exception as e:
        print(f"Error processing Dehashed-HBPD-scan.json: {e}\n")
else:
    print(f"Skipping Dehashed-HBPD-scan.json (not found at {dehashed_path}).\n")

# ----------------------------------------------------
# 2. Ingest Orange-County-Structural-Failure-Investigation.json
# ----------------------------------------------------
structural_path = os.path.join(downloads_path, "Orange-County-Structural-Failure-Investigation.json")
if os.path.exists(structural_path):
    print("Step 2/4: Ingesting Orange-County-Structural-Failure-Investigation.json...")
    try:
        with open(structural_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        flat_data = []
        for idx, item in enumerate(data):
            flat_data.append({
                "id": item.get("id", f"msg_{idx}"),
                "chatGroupId": item.get("chatGroupId", "unknown"),
                "role": item.get("role", "unknown"),
                "model": item.get("model", ""),
                "displayModel": item.get("displayModel", ""),
                "contents_raw": json.dumps(item.get("contents", [])),
                "created_at": str(item.get("created_at", "")),
                "updated_at": int(item.get("updated_at", 0)) if item.get("updated_at") is not None else None
            })
            
        table_ref = f"{dataset_id}.orange_county_structural_failure"
        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_json(flat_data, table_ref, job_config=job_config)
        job.result()
        print(f"Successfully loaded {len(flat_data)} rows into {table_ref}.\n")
    except Exception as e:
        print(f"Error processing Orange-County-Structural-Failure-Investigation.json: {e}\n")
else:
    print(f"Skipping Orange-County-Structural-Failure-Investigation.json (not found at {structural_path}).\n")

# ----------------------------------------------------
# 3. Ingest and Parse OSINTNeoAiXXL_chat.json
# ----------------------------------------------------
chat_text_path = os.path.join(downloads_path, "OSINTNeoAiXXL_chat.json")
if os.path.exists(chat_text_path):
    print("Step 3/4: Parsing and Ingesting OSINTNeoAiXXL_chat.json...")
    try:
        with open(chat_text_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("you asked")
        chat_rows = []
        
        # We start index at 1 since split before the first "you asked" is usually metadata/headers
        header_info = parts[0].strip() if len(parts) > 0 else ""
        
        for idx, part in enumerate(parts[1:]):
            time_match = re.search(r'message time:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', part)
            timestamp = time_match.group(1) if time_match else "2026-06-16 08:00:00"  # default approx timestamp
            
            subparts = part.split("gemini response")
            user_msg = ""
            assistant_msg = ""
            
            if len(subparts) > 0:
                user_text = subparts[0]
                user_text = re.sub(r'message time:\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', user_text)
                user_msg = user_text.strip()
            if len(subparts) > 1:
                assistant_msg = subparts[1].strip()
                
            chat_rows.append({
                "sequence_id": idx + 1,
                "timestamp": timestamp,
                "user_prompt": user_msg,
                "assistant_response": assistant_msg,
                "source_header": header_info[:1000] if header_info else None
            })
            
        table_ref = f"{dataset_id}.osint_neo_chat_transcript"
        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_json(chat_rows, table_ref, job_config=job_config)
        job.result()
        print(f"Successfully loaded {len(chat_rows)} parsed chat sessions into {table_ref}.\n")
    except Exception as e:
        print(f"Error parsing and processing OSINTNeoAiXXL_chat.json: {e}\n")
else:
    print(f"Skipping OSINTNeoAiXXL_chat.json (not found at {chat_text_path}).\n")

# ----------------------------------------------------
# 4. Ingest acrobat.adobe.com_*.csv Files
# ----------------------------------------------------
print("Step 4/4: Scanning and Loading acrobat.adobe.com CSV tracking files...")
csv_files = [f for f in os.listdir(downloads_path) if f.startswith("acrobat.adobe.com_") and f.endswith(".csv")]
if csv_files:
    try:
        combined_df = []
        for ef in csv_files:
            ef_path = os.path.join(downloads_path, ef)
            df = pd.read_csv(ef_path)
            # Add file origin column
            df["source_file"] = ef
            combined_df.append(df)
            
        unified_df = pd.concat(combined_df, ignore_index=True)
        # Drop duplicates based on URL to keep clean index
        unified_df.drop_duplicates(subset=["URL"], inplace=True)
        
        # Load unified dataframe to BigQuery
        table_ref = f"{dataset_id}.acrobat_adobe_urls"
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        # Convert df to dictionary format for insert
        rows = unified_df.to_dict(orient="records")
        # Ensure strings
        clean_rows = []
        for r in rows:
            clean_rows.append({k: str(v) if pd.notna(v) else None for k, v in r.items()})
            
        job = client.load_table_from_json(clean_rows, table_ref, job_config=job_config)
        job.result()
        print(f"Successfully loaded {len(clean_rows)} tracking links into {table_ref}.\n")
    except Exception as e:
        print(f"Error loading Acrobat CSV files: {e}\n")
else:
    print("No Acrobat tracker CSV files found.\n")

print("=========================================")
print("PHASE 2 BIGQUERY INGESTION COMPLETE!")
print("=========================================")
