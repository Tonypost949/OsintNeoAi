import os
import sys
import json
import datetime
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import bigquery
from google.cloud import storage
from google.api_core.exceptions import NotFound

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\credentials.json"

PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "ai_sandbox"
TABLE_ID = "gmail_amd949609_hits"
GCS_BUCKET = "project-743aab84-transfer-bucket"
GCS_PREFIX = "gmail_scans/amd949609"
QUERY_STRING = "in:sent AMD949609"
CHUNK_SIZE = 1000

def get_oauth_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def run_oauth_flow():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"OAuth client secrets file not found at: {CREDENTIALS_FILE}")
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return creds

def ensure_bq_table(bq_client):
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    try:
        bq_client.get_table(table_ref)
        print(f"[*] Table {table_ref} already exists.")
    except NotFound:
        print(f"[*] Creating table {table_ref}...")
        schema = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date", "STRING"),
            bigquery.SchemaField("from_user", "STRING"),
            bigquery.SchemaField("subject", "STRING"),
            bigquery.SchemaField("snippet", "STRING"),
            bigquery.SchemaField("query_match", "STRING"),
            bigquery.SchemaField("scanned_at", "TIMESTAMP")
        ]
        table = bigquery.Table(table_ref, schema=schema)
        bq_client.create_table(table)
        print(f"[+] Table {table_ref} created.")

def upload_to_gcs_and_load_bq(local_file, bq_client, storage_client, chunk_index):
    bucket = storage_client.bucket(GCS_BUCKET)
    blob_name = f"{GCS_PREFIX}/chunk_{chunk_index}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    blob = bucket.blob(blob_name)
    
    print(f"[*] Uploading {local_file} to gs://{GCS_BUCKET}/{blob_name}...")
    blob.upload_from_filename(local_file)
    
    gcs_uri = f"gs://{GCS_BUCKET}/{blob_name}"
    print(f"[*] Starting BigQuery Load Job from {gcs_uri}...")
    
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=False,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    
    load_job = bq_client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
    load_job.result()  # Waits for the job to complete
    
    print(f"[+] Chunk {chunk_index} loaded successfully to {table_ref}.")

def process_chunk(rows, bq_client, storage_client, chunk_index):
    local_file = f"temp_chunk_{chunk_index}.jsonl"
    with open(local_file, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row) + '\n')
            
    upload_to_gcs_and_load_bq(local_file, bq_client, storage_client, chunk_index)
    os.remove(local_file)

def main():
    print("====================================================")
    print("  QAG2 GMAIL FORENSIC SCANNER (CHUNKED via GCS)     ")
    print("====================================================")
    
    creds = get_oauth_credentials()
    if not creds:
        print("[*] Starting OAuth flow...")
        creds = run_oauth_flow()
        print("[+] Authentication Successful!")
        
    bq_client = bigquery.Client(project=PROJECT_ID)
    storage_client = storage.Client(project=PROJECT_ID)
    ensure_bq_table(bq_client)
    
    headers = {"Authorization": f"Bearer {creds.token}"}
    gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": 500, "q": QUERY_STRING}
    
    print(f"[*] Fetching messages matching '{QUERY_STRING}' from Gmail API...")
    
    messages = []
    page_token = None
    
    while True:
        if page_token:
            params['pageToken'] = page_token
        response = requests.get(gmail_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[-] Gmail API error: {response.text}")
            sys.exit(1)
            
        data = response.json()
        messages.extend(data.get('messages', []))
        page_token = data.get('nextPageToken')
        
        if not page_token:
            break
            
    if not messages:
        print(f"[-] No messages found matching '{QUERY_STRING}'.")
        sys.exit(0)
        
    print(f"[+] Found {len(messages)} messages. Processing and uploading in chunks of {CHUNK_SIZE}...")
    
    rows_to_insert = []
    chunk_index = 1
    
    for count, msg in enumerate(messages):
        msg_detail_url = f"{gmail_url}/{msg['id']}"
        msg_res = requests.get(msg_detail_url, headers=headers)
        if msg_res.status_code == 200:
            msg_data = msg_res.json()
            headers_list = msg_data.get('payload', {}).get('headers', [])
            
            subject = "No Subject"
            from_user = "Unknown"
            date_str = "Unknown"
            
            for h in headers_list:
                name_lower = h['name'].lower()
                if name_lower == 'subject':
                    subject = h['value']
                elif name_lower == 'from':
                    from_user = h['value']
                elif name_lower == 'date':
                    date_str = h['value']
            
            rows_to_insert.append({
                "id": msg['id'],
                "date": date_str,
                "from_user": from_user,
                "subject": subject,
                "snippet": msg_data.get('snippet', ''),
                "query_match": QUERY_STRING,
                "scanned_at": datetime.datetime.utcnow().isoformat()
            })
            
            if len(rows_to_insert) >= CHUNK_SIZE:
                process_chunk(rows_to_insert, bq_client, storage_client, chunk_index)
                rows_to_insert = []
                chunk_index += 1
                
    if rows_to_insert:
        process_chunk(rows_to_insert, bq_client, storage_client, chunk_index)
        
    print("[+] All chunks processed and loaded into BigQuery.")
    print("====================================================")

if __name__ == '__main__':
    main()
