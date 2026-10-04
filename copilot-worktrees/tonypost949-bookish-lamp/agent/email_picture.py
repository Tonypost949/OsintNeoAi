import os
import base64
import zlib
import urllib.request
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_send.json")

MERMAID_GRAPH = """graph TD
    VAS[VAS / Vanguard of the Old]:::orchestrator
    DOJ_Target[Federal Indictment Targets / UFC]:::orchestrator
    Andrew_Do[Supervisor Andrew Do]:::political
    HB_City[City of Huntington Beach]:::political
    State_Exemptions[Fraudulent CEQA Exemptions]:::political
    RPM[RPM Team / RPM Modular]:::shell
    Mercy[Mercy House]:::shell
    VAS_Subsidiaries[VAS Local LLCs]:::shell
    HBNC[Huntington Beach Navigation Center]:::physical
    Toxic_Plume[Hexavalent Chromium & Arsenic Plume]:::physical
    Failed_Cap[1-Year Asphalt Cap]:::physical

    VAS -->|Directs/Funds| DOJ_Target
    VAS -->|Launders through| VAS_Subsidiaries
    DOJ_Target -->|Influence| Andrew_Do
    Andrew_Do -->|Directs $2.2M Contracts| RPM
    Andrew_Do -->|Political Pressure| HB_City
    HB_City -->|Files Fraudulent Paperwork| State_Exemptions
    State_Exemptions -->|Bypasses DTSC| HBNC
    RPM -->|Builds| HBNC
    Mercy -->|Operates| HBNC
    VAS_Subsidiaries -->|Funnel Money| Mercy
    Toxic_Plume -->|Located beneath| HBNC
    HBNC -->|Cheap Encapsulation| Failed_Cap

    classDef orchestrator fill:#4a0000,stroke:#ff0000,stroke-width:2px,color:#fff;
    classDef political fill:#002244,stroke:#0066cc,stroke-width:2px,color:#fff;
    classDef shell fill:#333333,stroke:#ffcc00,stroke-width:2px,color:#fff;
    classDef physical fill:#003300,stroke:#00ff00,stroke-width:2px,color:#fff;
"""

def get_kroki_url(mermaid_code):
    compressed = zlib.compress(mermaid_code.encode('utf-8'))
    payload = base64.urlsafe_b64encode(compressed).decode('ascii')
    return f"https://kroki.io/mermaid/png/{payload}"

def send_image_email():
    print("[+] Rendering Mermaid graph to PNG via Kroki API...")
    url = get_kroki_url(MERMAID_GRAPH)
    
    png_data = None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            png_data = response.read()
        print("[+] Image successfully rendered and downloaded.")
    except Exception as e:
        print(f"[!] Failed to download image: {e}")
        return

    from google.auth.transport.requests import Request
    # Authenticate
    creds = None
    if os.path.exists(TOKEN_FILE):
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
            print("[AUTH] Launching browser to authorize sending email...")
            CLIENT_SECRET_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

    try:
        print("[+] Building email with image attachment...")
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()
        message.set_content("Here is the visual architecture graph of the Vanguard RICO network. See attached image.")
        message['To'] = 'anthonymichaeldimarcello@gmail.com'
        message['From'] = 'anthonymichaeldimarcello@gmail.com'
        message['Subject'] = 'OSINT Zeus: Vanguard RICO Network Visual Graph'

        # Attach the image
        message.add_attachment(png_data, maintype='image', subtype='png', filename='Vanguard_RICO_Network.png')

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        print("[+] Sending email...")
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"[+] Email successfully sent! Message ID: {send_message['id']}")

    except Exception as error:
        print(f"[!] An error occurred: {error}")

if __name__ == '__main__':
    send_image_email()
