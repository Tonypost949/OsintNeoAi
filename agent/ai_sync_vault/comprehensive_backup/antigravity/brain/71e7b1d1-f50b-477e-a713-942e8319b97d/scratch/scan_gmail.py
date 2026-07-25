import os
import sys
import json
import datetime
import urllib.parse
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.readonly'
]
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\.agents\skills\deep-osint\credentials.json"

def get_oauth_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading {TOKEN_FILE}: {e}")
            
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            creds = None
            
    return creds

def run_oauth_flow():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"OAuth client secrets file not found at: {CREDENTIALS_FILE}")
    
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    # run on a local port so the user can authenticate in their browser
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return creds

def main():
    print("====================================================")
    print("            QAG2 GMAIL FORENSIC SCANNER             ")
    print("====================================================")
    
    creds = get_oauth_credentials()
    if not creds:
        print("[*] No existing token.json found or expired. Starting OAuth flow...")
        print("[!] Please authorize the application in the browser tab that opens.")
        try:
            creds = run_oauth_flow()
            print("[+] Authentication Successful! Created token.json.")
        except Exception as e:
            print(f"[-] Authentication failed: {e}")
            sys.exit(1)
            
    print("[+] Authenticated successfully.")
    
    headers = {"Authorization": f"Bearer {creds.token}"}
    
    # Query latest 50 messages from Gmail
    gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": 50}
    
    print("[*] Fetching latest 50 messages from Gmail API...")
    response = requests.get(gmail_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"[-] Gmail API error: {response.status_code} - {response.text}")
        sys.exit(1)
        
    messages = response.json().get('messages', [])
    if not messages:
        print("[-] No messages found in this Gmail account.")
        sys.exit(0)
        
    print(f"[+] Found {len(messages)} messages. Retrieving details...")
    print("-" * 80)
    print(f"{'DATE':<20} | {'FROM':<30} | {'SUBJECT'}")
    print("-" * 80)
    
    connections = []
    for msg in messages:
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
            
            snippet = msg_data.get('snippet', '')
            
            # Print brief details
            print(f"{date_str[:20]:<20} | {from_user[:30]:<30} | {subject[:26]}")
            
            connections.append({
                "id": msg['id'],
                "date": date_str,
                "from": from_user,
                "subject": subject,
                "snippet": snippet
            })
            
    # Save the output to a text file for evidence and easy viewing by the user
    output_file = "gmail_connections_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(connections, f, indent=2)
        
    print("-" * 80)
    print(f"[+] Successfully scanned Gmail! Connections saved to: {os.path.abspath(output_file)}")
    print("====================================================")

if __name__ == '__main__':
    main()
