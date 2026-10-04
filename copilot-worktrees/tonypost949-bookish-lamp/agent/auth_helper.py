"""
Shared OAuth helper for Drive, Photos, Tasks scanners.
Uses local-server flow (opens browser automatically) or manual console fallback.
"""

import os, json, sys, webbrowser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(AGENT_DIR, "client_secret.json")

def authenticate(scope_label, scopes, token_filename, client_secret_filename=None):
    token_path = os.path.join(AGENT_DIR, token_filename)
    client_secret_path = os.path.join(AGENT_DIR, client_secret_filename) if client_secret_filename else CLIENT_SECRET_FILE
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if creds and creds.expired and creds.refresh_token:
        print(f"[AUTH] Refreshing expired {scope_label} token...")
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
        url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
        print(f"\n[AUTH] {'=' * 50}")
        print(f"[AUTH] OAuth for {scope_label}")
        print(f"[AUTH] {'=' * 50}")
        print(f"\n  Visit this URL in your browser:\n  {url}\n")
        webbrowser.open(url)
        code = input("  Enter the authorization code: ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"[AUTH] Token saved to {token_path}\n")

    return creds
