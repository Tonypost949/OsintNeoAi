import os
import asyncio
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.hooks.policy import allow, ask_user

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_live_agent.json")
CLIENT_SECRET_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")

VALID_SENDERS = [
    "anthonymichaeldimarcello@gmail.com",
    "9493502312@vtext.com",
    "9493502312@vzwpix.com",
    "9493502312@txt.att.net",
    "9493502312@mms.att.net",
    "9493502312@tmomail.net"
]

def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_unread_messages(service):
    # Search for unread messages from any valid sender
    query = "is:unread (" + " OR ".join([f"from:{s}" for s in VALID_SENDERS]) + ")"
    results = service.users().messages().list(userId='me', q=query).execute()
    return results.get('messages', [])

def mark_as_read(service, msg_id):
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

def send_reply(service, to_address, subject, response_text):
    message = EmailMessage()
    message.set_content(response_text)
    message['To'] = to_address
    message['From'] = 'anthonymichaeldimarcello@gmail.com'
    message['Subject'] = 'Re: ' + subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    service.users().messages().send(userId="me", body=create_message).execute()

def parse_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
    elif payload['mimeType'] == 'text/plain':
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return ""

async def main():
    service = authenticate_gmail()
    print("[+] Live Agent Loop Started. Monitoring for texts/emails...")
    
    # Configure the antigravity agent
    custom_policies = [
        allow("view_file"),
        allow("edit_file"),
        allow("list_dir"),
        allow("run_command") # Allowed command execution for autonomy
    ]
    config = LocalAgentConfig(policies=custom_policies)
    
    async with Agent(config) as agent:
        while True:
            try:
                messages = get_unread_messages(service)
                for msg in messages:
                    msg_id = msg['id']
                    msg_detail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                    
                    headers = msg_detail['payload']['headers']
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), None)
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Zeus Command')
                    
                    if sender and any(valid in sender for valid in VALID_SENDERS):
                        print(f"\n[!] Received Command from {sender}")
                        command_text = parse_email_body(msg_detail['payload']).strip()
                        print(f"Command: {command_text}")
                        
                        # Mark as read immediately to avoid dupes
                        mark_as_read(service, msg_id)
                        
                        if command_text:
                            # Feed the command to the agent
                            print("[*] Processing with google.antigravity SDK...")
                            response = await agent.chat(command_text)
                            response_text = await response.text()
                            
                            # Send reply
                            send_reply(service, sender, subject, response_text)
                            print("[+] Reply sent successfully.")
                            
            except Exception as e:
                print(f"Error in polling loop: {e}")
                
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
