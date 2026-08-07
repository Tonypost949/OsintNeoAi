"""get_token_v3.py — Get token using run_local_server with URL saved to file"""
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

creds = None
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, [scope])
if creds and creds.expired and creds.refresh_token:
    print("Refreshing...", flush=True)
    creds.refresh(Request())

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(secret_path, [scope])
    # Get the URL and save it before starting the server
    url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    with open(os.path.join(AGENT_DIR, "oauth_url.txt"), "w") as f:
        f.write(url)
    print(f"URL: {url}", flush=True)
    print("Starting local server...", flush=True)
    try:
        creds = flow.run_local_server(host="localhost", port=0, open_browser=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"Token saved to {token_file}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        # Fallback: create URL for manual flow
        with open(os.path.join(AGENT_DIR, "oauth_url.txt"), "w") as f:
            f.write(url)
        print(f"Manual URL: {url}", flush=True)
else:
    print("Token already valid", flush=True)
