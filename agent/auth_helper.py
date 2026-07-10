"""
Shared OAuth helper for Drive + Photos scanners.
Uses device flow so no browser needed on the server.
"""

import os, json, sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(AGENT_DIR, "client_secret.json")

def authenticate(scope_label, scopes, token_filename):
    """
    Authenticate with device OAuth flow.
    - scope_label: human-readable name (e.g. "Drive", "Photos")
    - scopes: list of OAuth scope URLs
    - token_filename: where to save the token (relative to agent dir)
    Returns Credentials object.
    """
    token_path = os.path.join(AGENT_DIR, token_filename)
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if creds and creds.expired and creds.refresh_token:
        print(f"[AUTH] Refreshing expired {scope_label} token...")
        creds.refresh(Request())

    if not creds or not creds.valid:
        print(f"\n[AUTH] {'=' * 50}")
        print(f"[AUTH] Device OAuth for {scope_label}")
        print(f"[AUTH] 1. Visit the URL below in your browser")
        print(f"[AUTH] 2. Sign in as amd949609@gmail.com")
        print(f"[AUTH] 3. Enter the code shown")
        print(f"[AUTH] {'=' * 50}\n")
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes)
        creds = flow.run_console()
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"[AUTH] Token saved to {token_path}\n")

    return creds
