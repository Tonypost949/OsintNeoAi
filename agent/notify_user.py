import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")

GATEWAYS = [
    "9493502312@vtext.com",      # Verizon SMS
    "9493502312@vzwpix.com",     # Verizon MMS
    "9493502312@txt.att.net",    # AT&T SMS
    "9493502312@mms.att.net",    # AT&T MMS
    "9493502312@tmomail.net"     # T-Mobile SMS/MMS
]

# Add the main email address as well
GATEWAYS.append("txtdjdrop@gmail.com")

def notify_user():
    if not os.path.exists(TOKEN_FILE):
        print("[!] Token file missing.")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        else:
            print("[!] Credentials invalid.")
            return

    service = build('gmail', 'v1', credentials=creds)

    print("[+] Sending vault command to email and phone...")
    
    body = (
        "Zeus: OSINT Vault Uploaded.\n\n"
        "Run this command on any machine to pull your files:\n"
        "gcloud storage cp gs://osint-ai-evidence-vault-m4/pc_backup/OSINT_VAULT_BACKUP.zip ."
    )

    for recipient in GATEWAYS:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['From'] = 'txtdjdrop@gmail.com'
        message['Subject'] = 'OSINT Zeus: Vault Command'

        try:
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            service.users().messages().send(userId="me", body=create_message).execute()
            print(f"  -> Sent to: {recipient}")
        except Exception as e:
            print(f"  [!] Error sending to {recipient}: {e}")

if __name__ == "__main__":
    notify_user()
