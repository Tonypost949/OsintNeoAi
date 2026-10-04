import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")
APK_PATH = r"C:\Users\HP\OneDrive\Desktop\tapk\OSINTNeoAI\osintneoai.apk"

def send_apk_email():
    if not os.path.exists(TOKEN_FILE):
        print("[!] Token file missing.")
        return
        
    if not os.path.exists(APK_PATH):
        print(f"[!] APK file not found at: {APK_PATH}")
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

    message = EmailMessage()
    message.set_content(
        "Here is your compiled OSINTNeoAI Android application (osintneoai.apk) attached below.\n\n"
        "You can download and install this on your Android device to access the mobile interface."
    )
    message['To'] = 'anthonymichaeldimarcello@gmail.com'
    message['From'] = 'anthonymichaeldimarcello@gmail.com'
    message['Subject'] = 'OSINT Zeus: OSINTNeoAI Android APK Shell'

    # Read APK binary data
    with open(APK_PATH, 'rb') as f:
        file_data = f.read()
    
    # Attach binary APK
    message.add_attachment(
        file_data, 
        maintype='application', 
        subtype='vnd.android.package-archive', 
        filename='osintneoai.apk'
    )

    try:
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        print(f"[+] Sending APK email to anthonymichaeldimarcello@gmail.com...")
        service.users().messages().send(userId="me", body=create_message).execute()
        print("[+] APK email successfully sent!")
    except Exception as e:
        print(f"[!] Error sending email: {e}")

if __name__ == "__main__":
    send_apk_email()
