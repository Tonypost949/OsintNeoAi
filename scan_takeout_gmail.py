import os
import sys
import mailbox
import email
from email.header import decode_header
import json
from google.cloud import storage, bigquery

# Config
KEYWORD = "AMD949609"
PROJECT_ID = "project-743aab84"
BUCKET_NAME = "project-743aab84-transfer-bucket"
DATASET_ID = "ai_sandbox"
TABLE_ID = "gmail_amd949609_hits"
CHUNK_FILE = "gmail_takeout_hits.jsonl"
GCS_BLOB_NAME = "takeout_ingestion/gmail_takeout_hits.jsonl"

def get_text_from_email(msg):
    text_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    text_content += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                except:
                    pass
    else:
        try:
            text_content = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
        except:
            pass
    return text_content

def decode_mime_header(h):
    if not h: return ""
    decoded_parts = decode_header(h)
    result = ""
    for string, charset in decoded_parts:
        if isinstance(string, bytes):
            try:
                result += string.decode(charset or 'utf-8', errors='ignore')
            except:
                result += string.decode('utf-8', errors='ignore')
        else:
            result += string
    return result

def scan_mbox(mbox_path):
    print(f"Scanning {mbox_path}...")
    mb = mailbox.mbox(mbox_path)
    hits = []
    
    for i, msg in enumerate(mb):
        if i % 1000 == 0 and i > 0:
            print(f"Scanned {i} emails...")
            
        labels_header = msg.get('X-Gmail-Labels', '')
        if 'Sent' not in labels_header:
            continue
            
        body = get_text_from_email(msg)
        subject = decode_mime_header(msg.get('Subject', ''))
        
        # Check if keyword is in subject or body
        if KEYWORD in subject or KEYWORD in body:
            hits.append({
                "message_id": msg.get('Message-ID', ''),
                "date": msg.get('Date', ''),
                "subject": subject,
                "from_addr": decode_mime_header(msg.get('From', '')),
                "to_addr": decode_mime_header(msg.get('To', '')),
                "labels": labels_header,
                "body_snippet": body[:1000] # store a snippet to avoid huge rows
            })
            print(f"Hit found! Subject: {subject}")
            
    return hits

def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_takeout_gmail.py <path_to_takeout_folder>")
        sys.exit(1)
        
    takeout_dir = sys.argv[1]
    
    # Find mbox files
    mbox_files = []
    for root, dirs, files in os.walk(takeout_dir):
        for f in files:
            if f.endswith('.mbox'):
                mbox_files.append(os.path.join(root, f))
                
    if not mbox_files:
        print(f"No .mbox files found in {takeout_dir}")
        sys.exit(1)
        
    all_hits = []
    for mbox_file in mbox_files:
        hits = scan_mbox(mbox_file)
        all_hits.extend(hits)
        
    print(f"Total hits found: {len(all_hits)}")
    if not all_hits:
        return
        
    # Write to local JSONL
    print(f"Writing to {CHUNK_FILE}...")
    with open(CHUNK_FILE, 'w', encoding='utf-8') as f:
        for hit in all_hits:
            f.write(json.dumps(hit) + '\n')
            
    # Upload to GCS
    print("Uploading to GCS...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_BLOB_NAME)
    blob.upload_from_filename(CHUNK_FILE)
    print(f"Uploaded to gs://{BUCKET_NAME}/{GCS_BLOB_NAME}")
    
    # Load into BigQuery
    print("Loading into BigQuery...")
    bq_client = bigquery.Client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    
    uri = f"gs://{BUCKET_NAME}/{GCS_BLOB_NAME}"
    load_job = bq_client.load_table_from_uri(uri, table_ref, job_config=job_config)
    
    print(f"Starting BigQuery load job {load_job.job_id}...")
    load_job.result()  # Wait for the job to complete
    print(f"Successfully loaded {load_job.output_rows} rows into {table_ref}.")

if __name__ == "__main__":
    main()
