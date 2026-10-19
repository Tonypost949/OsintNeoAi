import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GmailConnector:
    """Consolidated Gmail Mailbox and Conversation Harvesting Client."""
    
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    
    def __init__(self, credentials_path='credentials.json', token_path='token_gmail.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """Gmail-specific read-only OAuth consent authentication."""
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                print(f"[Gmail] Error loading cached token: {e}")
                
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.creds.to_json())
            except Exception as e:
                print(f"[Gmail] Error refreshing token: {e}")
                self.creds = None
                
        if not self.creds:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    f"OAuth credentials secret file '{self.credentials_path}' not found."
                )
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token_file:
                token_file.write(self.creds.to_json())
                
        self.service = build("gmail", "v1", credentials=self.creds)
        return self.service

    def get_header(self, headers, name):
        """Helper to safely extract headers from mail message structures."""
        for h in headers:
            if h['name'].lower() == name.lower():
                return h['value']
        return ""

    def scan_mailbox(self, limit=1000):
        """Audit and scan the authenticated mailbox, retrieving a list of normalized message metadata."""
        if not self.service:
            self.authenticate()
            
        messages_metadata = []
        page_token = None
        
        while len(messages_metadata) < limit:
            results = self.service.users().messages().list(
                userId='me', q='', pageToken=page_token
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                break
                
            for msg_summary in messages:
                if len(messages_metadata) >= limit:
                    break
                    
                msg_id = msg_summary['id']
                try:
                    # Get full details of individual email message
                    msg = self.service.users().messages().get(
                        userId='me', id=msg_id, format='metadata',
                        metadataHeaders=['Subject', 'From', 'To', 'Date']
                    ).execute()
                    
                    headers = msg.get('payload', {}).get('headers', [])
                    messages_metadata.append({
                        "id": msg_id,
                        "thread_id": msg.get('threadId', ''),
                        "subject": self.get_header(headers, "Subject"),
                        "from": self.get_header(headers, "From"),
                        "to": self.get_header(headers, "To"),
                        "date": self.get_header(headers, "Date"),
                        "snippet": msg.get('snippet', '')
                    })
                except Exception as e:
                    print(f"[Gmail] Error fetching message {msg_id}: {e}")
                    
            page_token = results.get('nextPageToken')
            if not page_token:
                break
                
        return messages_metadata
