import os
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.cloud import bigquery

# Authenticate with Gmail
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token_gmail.json")
creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/gmail.readonly"])
gmail_service = build("gmail", "v1", credentials=creds)

# Connect to BigQuery
bq_client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# Query the priority hits
query = """
SELECT message_id, subject, date_header 
FROM `project-743aab84-f9a5-4ec7-954.national_audits.gmail_index`
WHERE REGEXP_CONTAINS(subject, r'8:26-cv-00348|OC SSA|Mercy House charity fraud|Child Deaths|Parallel Qui Tam|Supplemental Qui Tam')
   OR message_id = '19e9dabdb83a65f8'
"""

print("Querying BigQuery for FCA message IDs...")
query_job = bq_client.query(query)
results = query_job.result()

message_ids = [row.message_id for row in results]
print(f"Found {len(message_ids)} priority FCA emails in BigQuery.")

# Fallback: if BigQuery doesn't have them (maybe they were in a different scan), we can also just search Gmail directly.
if len(message_ids) == 0:
    print("Searching Gmail directly for the FCA signals...")
    search_queries = ['8:26-cv-00348', 'Mercy House charity fraud', 'Child Deaths', 'OC SSA']
    message_ids = set()
    for sq in search_queries:
        res = gmail_service.users().messages().list(userId='me', q=sq).execute()
        if 'messages' in res:
            for m in res['messages']:
                message_ids.add(m['id'])
    
    # Also ensure the specific blocked message ID is in there if the user mentioned it:
    message_ids.add('19e9dabdb83a65f8')
    message_ids = list(message_ids)
    print(f"Found {len(message_ids)} priority FCA emails via direct Gmail search.")

output_file = "fca_email_bodies_extracted.jsonl"

print(f"Extracting full bodies for {len(message_ids)} emails. Saving incrementally...")

def get_email_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'parts' in part:
                body += get_email_body(part)
    elif 'body' in payload and 'data' in payload['body']:
        data = payload['body']['data']
        body += base64.urlsafe_b64decode(data).decode('utf-8')
    return body

extracted_count = 0
with open(output_file, "w", encoding="utf-8") as f:
    for mid in message_ids:
        try:
            print(f"Fetching body for message_id: {mid}...")
            msg = gmail_service.users().messages().get(userId='me', id=mid, format='full').execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            date_val = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            full_body = get_email_body(msg['payload'])
            
            # Save immediately to disk (incremental save)
            record = {
                "message_id": mid,
                "subject": subject,
                "date": date_val,
                "full_body": full_body
            }
            f.write(json.dumps(record) + "\n")
            f.flush()  # Force save to disk so we don't lose data
            extracted_count += 1
            
        except Exception as e:
            print(f"Error fetching {mid}: {e}")

print(f"Done! Successfully extracted {extracted_count} full email bodies.")
