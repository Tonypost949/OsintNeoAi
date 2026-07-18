import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")

# Target mobile phone gateways (SMS & MMS) for 949-350-2312
GATEWAYS = [
    "9493502312@vtext.com",      # Verizon SMS
    "9493502312@vzwpix.com",     # Verizon MMS
    "9493502312@txt.att.net",    # AT&T SMS
    "9493502312@mms.att.net",    # AT&T MMS
    "9493502312@tmomail.net"     # T-Mobile SMS/MMS
]

def send_text_message():
    if not os.path.exists(TOKEN_FILE):
        print("[!] Token file missing.")
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

    print("[+] Sending texts to 949-350-2312 via carrier gateways...")
    
    # Send a separate email to each gateway to ensure delivery regardless of carrier
    for recipient in GATEWAYS:
        message = EmailMessage()
        # Keep SMS body short and simple
        message.set_content(
            "Zeus Links:\n"
            "Dashboard (Wi-Fi): http://192.168.1.121:8501\n"
            "Dashboard (Tailscale): http://100.103.157.60:8501\n"
            "Repo: https://github.com/Tonypost949/osint-agent\n"
            "Exhibit: https://github.com/Tonypost949/osint-agent/blob/master/FEDERAL_WHISTLEBLOWER_EXHIBIT.md\n"
            "OC Map: https://github.com/Tonypost949/osint-agent/blob/master/osint_gemini_gis.html"
        )
        message['To'] = recipient
        message['From'] = 'anthonymichaeldimarcello@gmail.com'
        message['Subject'] = 'OSINT Zeus'

        try:
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            service.users().messages().send(userId="me", body=create_message).execute()
            print(f"  -> Sent via: {recipient}")
        except Exception as e:
            print(f"  [!] Error sending to {recipient}: {e}")

if __name__ == "__main__":
    send_text_message()
