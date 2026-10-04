"""
oauth_poll.py — Waits for user to paste auth code into oauth_code.txt
========================================================================
1. Prints the OAuth URL
2. Waits for you to create agent/oauth_code.txt with the code
3. Exchanges it for tokens and saves

Steps:
  python agent/google_tasks_manager.py init-investigation
   -> Visit the URL, sign in as amd949609@gmail.com, authorize
   -> Copy the code from browser
   -> echo "CODE HERE" > agent/oauth_code.txt
  (script auto-detects the file and completes auth)
"""

import os, sys, json, time, webbrowser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(AGENT_DIR, "client_secret_tasks.json")
TOKEN_FILE = os.path.join(AGENT_DIR, "tasks_token.json")
CODE_FILE = os.path.join(AGENT_DIR, "oauth_code.txt")
SCOPES = ["https://www.googleapis.com/auth/tasks"]

def main():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        print("[AUTH] Refreshing expired token...")
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
        url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            include_granted_scopes="true",
        )
        print("\n[AUTH] ==================================================")
        print("[AUTH] OAuth for Google Tasks")
        print("[AUTH] ==================================================\n")
        webbrowser.open(url)
        print(f"  Visit this URL:\n  {url}\n")
        print("  Sign in as amd949609@gmail.com")
        print("  Copy the authorization code from your browser.\n")
        print(f"  Then create the file:\n    agent/oauth_code.txt\n")
        print(f"  With just the code inside (no extra text).")
        print(f"  I'll detect it automatically.\n")

        waited = 0
        while not os.path.exists(CODE_FILE):
            time.sleep(3)
            waited += 3
            if waited >= 5:
                print(f"  Waiting for agent/oauth_code.txt... (type 'skip' to abort)")
                waited = 0

        with open(CODE_FILE) as f:
            code = f.read().strip()

        if code.lower() == "skip":
            print("[AUTH] Skipped.")
            return None

        flow.fetch_token(code=code)
        creds = flow.credentials

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"[AUTH] Token saved to {TOKEN_FILE}")

        if os.path.exists(CODE_FILE):
            os.remove(CODE_FILE)

    return creds


if __name__ == "__main__":
    creds = main()
    if creds:
        print("[OK] Authenticated successfully.")
        print(f"  Scopes: {creds.scopes}")
        print(f"  Expiry: {creds.expiry}")
        print(f"\nNow run the tasks script:\n  python agent/google_tasks_manager.py list-lists")
