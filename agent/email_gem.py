import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")
GEM_FILE = os.path.join(SCRIPT_DIR, "Gemini_Gem_Antigravity.md")

def send_gem_email():
    if not os.path.exists(TOKEN_FILE):
        print("[!] Token file missing.")
        return
        
    if not os.path.exists(GEM_FILE):
        print("[!] Gem configuration file missing.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"[!] Failed to refresh token: {e}")
                return
        else:
            print("[!] Credentials invalid.")
            return

    service = build('gmail', 'v1', credentials=creds)

    with open(GEM_FILE, 'r', encoding='utf-8') as f:
        gem_content = f.read()

    message = EmailMessage()
    message.set_content(f"Here is the Gemini Gem configuration instructions for your phone. Copy the instructions block below and paste it into the Gem Instructions manager:\n\n{gem_content}")
    message['To'] = 'txtdjdrop@gmail.com'
    message['From'] = 'txtdjdrop@gmail.com'
    message['Subject'] = 'OSINT Zeus: Makaveli Gemini Gem Configuration'

    # Also attach the file
    with open(GEM_FILE, 'rb') as f:
        file_data = f.read()
    message.add_attachment(file_data, maintype='text', subtype='markdown', filename='Gemini_Gem_Antigravity.md')

    try:
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        service.users().messages().send(userId="me", body=create_message).execute()
        print("[+] Gem configuration email successfully sent!")
    except Exception as e:
        print(f"[!] Error sending email: {e}")

if __name__ == "__main__":
    send_gem_email()
