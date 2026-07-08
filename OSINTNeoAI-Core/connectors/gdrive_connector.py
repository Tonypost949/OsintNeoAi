import os
import urllib.parse
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GDriveConnector:
    """Consolidated Google Drive API Client and OSINT search engine."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        
    def authenticate(self):
        """Standardized Google Desktop/OAuth login."""
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                print(f"[GDrive] Error loading cached token: {e}")
                
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.creds.to_json())
                print("[GDrive] Token refreshed successfully.")
            except Exception as e:
                print(f"[GDrive] Error refreshing token: {e}")
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
            print("[GDrive] OAuth consent completed and token saved.")
            
        return self.creds

    def search_drive(self, query_string, limit=50):
        """Query Google Drive files.list using direct HTTP request to avoid massive SDK overhead."""
        if not self.creds:
            self.authenticate()
            
        url = "https://www.googleapis.com/drive/v3/files"
        headers = {"Authorization": f"Bearer {self.creds.token}"}
        params = {
            "q": query_string,
            "pageSize": limit,
            "fields": "nextPageToken, files(id, name, mimeType, webViewLink, owners(displayName, emailAddress), modifiedTime, size)",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('files', [])
        else:
            raise Exception(f"Drive API Failure {response.status_code}: {response.text}")

    @staticmethod
    def generate_dorks(keyword):
        """Generate targeted OSINT Google Dork links for public Google Workspace indexing."""
        dork_templates = [
            {"title": "Public Google Drive Folders", "query": f"site:drive.google.com/drive/folders/ \"{keyword}\""},
            {"title": "Public Google Sheets", "query": f"site:docs.google.com/spreadsheets/ \"{keyword}\""},
            {"title": "Public Google Docs", "query": f"site:docs.google.com/document/ \"{keyword}\""},
            {"title": "Public PDF files on Google Drive", "query": f"site:drive.google.com filetype:pdf \"{keyword}\""},
            {"title": "Google Drive index directories", "query": f"site:drive.google.com inurl:\"/view\" \"{keyword}\""},
            {"title": "Public Google Forms", "query": f"site:docs.google.com/forms/ \"{keyword}\""},
        ]
        
        dorks = []
        for d in dork_templates:
            encoded_query = urllib.parse.quote(d["query"])
            dorks.append({
                "title": d["title"],
                "query": d["query"],
                "url": f"https://www.google.com/search?q={encoded_query}"
            })
        return dorks
