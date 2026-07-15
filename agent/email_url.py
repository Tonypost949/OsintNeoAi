import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")

def send_url_email():
    if not os.path.exists(TOKEN_FILE):
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message.set_content("Click this link on your tablet to open the Makaveli OSINT Command Center Dashboard:\n\nhttp://192.168.1.121:8080/osint_gemini_gis.html")
    message['To'] = 'txtdjdrop@gmail.com'
    message['From'] = 'txtdjdrop@gmail.com'
    message['Subject'] = 'OSINT Zeus: Dashboard Tablet Link'

    try:
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        service.users().messages().send(userId="me", body=create_message).execute()
        print("[+] URL email successfully sent!")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    send_url_email()
