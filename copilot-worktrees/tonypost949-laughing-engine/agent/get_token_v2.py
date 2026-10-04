"""get_token_v2.py — Get OAuth token using run_local_server() in background"""
import sys, os, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
label = sys.argv[1] if len(sys.argv) > 1 else "App"
scope = sys.argv[2] if len(sys.argv) > 2 else "https://www.googleapis.com/auth/drive.readonly"
token_file = sys.argv[3] if len(sys.argv) > 3 else f"token_{label.lower()}.json"
client_secret = sys.argv[4] if len(sys.argv) > 4 else "client_secret.json"

token_path = os.path.join(AGENT_DIR, token_file)
secret_path = os.path.join(AGENT_DIR, client_secret)

# Check existing token
creds = None
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, [scope])
if creds and creds.expired and creds.refresh_token:
    print("Refreshing...", flush=True)
    creds.refresh(Request())

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(secret_path, [scope])
    port = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    creds = flow.run_local_server(host="localhost", port=port, open_browser=True)
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    print(f"Token saved to {token_file}", flush=True)
else:
    print("Token already valid", flush=True)
