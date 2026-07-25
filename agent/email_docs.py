import os
import base64
import mimetypes
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")
BRAIN_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
WORKSPACE_DIR = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"

FILES_TO_ATTACH = [
    os.path.join(BRAIN_DIR, "Huizar_Presentation_Deck.md"),
    os.path.join(BRAIN_DIR, "Precedent_Case_Analysis.md"),
    os.path.join(BRAIN_DIR, "Emergency_Criminal_Referral_HBNC.md"),
    os.path.join(BRAIN_DIR, "RICO_Network_Chart.md"),
    os.path.join(WORKSPACE_DIR, "Antigravity_Resurrection_Protocol.md")
]

def send_docs():
    print("[+] Building email bundle for tablet access...")
    
    if not os.path.exists(TOKEN_FILE):
        print("[!] Token missing. Cannot send.")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message.set_content("Here are all the critical case files, presentation decks, and evidence templates you requested. You can open these directly on your tablet.")
    message['To'] = 'anthonymichaeldimarcello@gmail.com'
    message['From'] = 'anthonymichaeldimarcello@gmail.com'
    message['Subject'] = 'OSINT Zeus: RICO Master Case Files & Presentation Deck'

    for file_path in FILES_TO_ATTACH:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            file_name = os.path.basename(file_path)
            
            # Markdown is plain text
            maintype = 'text'
            subtype = 'markdown'
            
            message.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
            print(f"  -> Attached: {file_name}")
        else:
            print(f"  [!] Missing file: {file_path}")

    try:
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        print("[+] Sending email...")
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"[+] Email successfully sent! Message ID: {send_message['id']}")
    except Exception as e:
        print(f"[!] Error sending email: {e}")

if __name__ == "__main__":
    send_docs()
