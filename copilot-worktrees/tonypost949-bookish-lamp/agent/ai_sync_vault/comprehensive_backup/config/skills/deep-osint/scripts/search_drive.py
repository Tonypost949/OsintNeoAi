import os
import sys
import json
import urllib.parse
import http.server
import socketserver
import webbrowser
import argparse
import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import requests

# Scopes required to search Google Drive and Gmail
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.readonly'
]
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
SERVICE_ACCOUNT_FILE = 'service_account.json'
PORT = 8080

def get_oauth_credentials():
    """Load or refresh OAuth2 credentials."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading {TOKEN_FILE}: {e}")
            
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            creds = None
            
    return creds

def run_oauth_flow():
    """Initiate local OAuth2 flow."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"OAuth client secret file '{CREDENTIALS_FILE}' not found. "
            "Please download it from Google Cloud Console (OAuth 2.0 Client IDs -> Desktop Application) "
            "and place it in this directory."
        )
    
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return creds

def get_service_account_credentials():
    """Load service account credentials if available."""
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            return ServiceAccountCredentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
        except Exception as e:
            print(f"Error loading service account credentials: {e}")
    return None

def query_drive_api(query, creds):
    """Query Google Drive API files.list endpoint using requests."""
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        "Authorization": f"Bearer {creds.token}"
    }
    
    params = {
        "q": query,
        "pageSize": 25,
        "fields": "nextPageToken, files(id, name, mimeType, webViewLink, owners(displayName, emailAddress), modifiedTime, size)",
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Drive API Error {response.status_code}: {response.text}")

def generate_dorks(keyword):
    """Generate specialized Google Dork URLs for OSINT Google Drive search."""
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
        encoded = urllib.parse.quote(d["query"])
        url = f"https://www.google.com/search?q={encoded}"
        dorks.append({
            "title": d["title"],
            "query": d["query"],
            "url": url
        })
    return dorks

class SearchAPIRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler that implements API endpoints and serves static files."""
    
    def log_message(self, format, *args):
        pass
        
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Route API queries
        if path == '/api/status':
            self.handle_api_status()
        elif path == '/api/dork':
            self.handle_api_dork(query_params)
        elif path == '/api/search':
            self.handle_api_search(query_params)
        elif path == '/api/daily_assets':
            self.handle_daily_assets(query_params)
        elif path == '/api/auth':
            self.handle_api_auth()
        elif path.startswith('/local_file/'):
            self.handle_serve_local_file(path)
        else:
            if path == '/' or path == '/index.html':
                self.path = '/dashboard.html'
            super().do_GET()
            
    def handle_serve_local_file(self, path):
        # Decode and retrieve the absolute path
        file_path = urllib.parse.unquote(path[12:])
        # Clean potential leading slash on Windows (e.g. /C:/ -> C:/)
        if len(file_path) > 2 and file_path[0] == '/' and file_path[2] == ':':
            file_path = file_path[1:]
        # Replace forward slashes with system path separator if on Windows
        if os.name == 'nt':
            file_path = file_path.replace('/', '\\')
            
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found")
            return
            
        try:
            self.send_response(200)
            # Determine content type
            mime_type = "application/octet-stream"
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.html': mime_type = "text/html"
            elif ext == '.css': mime_type = "text/css"
            elif ext == '.js': mime_type = "application/javascript"
            elif ext == '.json': mime_type = "application/json"
            elif ext == '.png': mime_type = "image/png"
            elif ext == '.jpg' or ext == '.jpeg': mime_type = "image/jpeg"
            elif ext == '.txt': mime_type = "text/plain"
            elif ext == '.pdf': mime_type = "application/pdf"
            
            self.send_header('Content-Type', mime_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            stat = os.stat(file_path)
            self.send_header('Content-Length', str(stat.st_size))
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error reading file: {e}".encode())
            
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        body = json.dumps(data).encode('utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        
    def handle_api_status(self):
        has_token = os.path.exists(TOKEN_FILE)
        has_creds = os.path.exists(CREDENTIALS_FILE)
        has_sa = os.path.exists(SERVICE_ACCOUNT_FILE)
        
        status_data = {
            "authenticated": False,
            "has_token_file": has_token,
            "has_credentials_file": has_creds,
            "has_service_account": has_sa,
            "auth_type": None
        }
        
        creds = get_oauth_credentials()
        if creds:
            status_data["authenticated"] = True
            status_data["auth_type"] = "OAuth2 User (token.json)"
        else:
            sa_creds = get_service_account_credentials()
            if sa_creds:
                status_data["authenticated"] = True
                status_data["auth_type"] = "Service Account (service_account.json)"
                
        self.send_json(status_data)
        
    def handle_api_dork(self, params):
        q = params.get('q', [''])[0]
        if not q:
            self.send_json({"error": "Missing query parameter 'q'"}, 400)
            return
            
        dorks = generate_dorks(q)
        self.send_json({"dorks": dorks})
        
    def handle_api_search(self, params):
        q = params.get('q', [''])[0]
        if not q:
            self.send_json({"error": "Missing search query parameter 'q'"}, 400)
            return
            
        drive_query = f"name contains '{q}' or fullText contains '{q}'"
        
        creds = get_oauth_credentials()
        if not creds:
            creds = get_service_account_credentials()
            
        if not creds:
            self.send_json({
                "error": "Not Authenticated",
                "message": "No valid OAuth token or Service Account credentials found."
            }, 401)
            return
            
        if hasattr(creds, 'valid') and not creds.valid:
            try:
                creds.refresh(Request())
            except Exception as e:
                self.send_json({"error": "Authentication Refresh Failed", "message": str(e)}, 401)
                return
                
        try:
            results = query_drive_api(drive_query, creds)
            self.send_json(results)
        except Exception as e:
            self.send_json({"error": "Google Drive API Error", "message": str(e)}, 500)
            
    def handle_daily_assets(self, params):
        date_str = params.get('date', [''])[0]
        if not date_str:
            self.send_json({"error": "Missing date parameter"}, 400)
            return

        # Whistleblower incident preset assets dictionary
        preset_assets = {
            "2021-01-01": [
                {"name": "case-file-init-001.doc", "type": "Local File", "time": "09:00:00", "link": "#", "mimeType": "application/msword"}
            ],
            "2021-01-15": [
                {"name": "audit-2021-01-15.log", "type": "Local File", "time": "22:30:00", "link": "http://sec-logs.local/ssh/audit-2021-01-15", "mimeType": "text/plain"}
            ],
            "2021-02-01": [
                {"name": "defense-deployment-plan-v1.pdf", "type": "Local File", "time": "14:00:00", "link": "#", "mimeType": "application/pdf"}
            ],
            "2021-02-15": [
                {"name": "block-2021-02-15.log", "type": "Local File", "time": "11:00:00", "link": "http://sec-logs.local/intrusion/block-2021-02-15", "mimeType": "text/plain"}
            ],
            "2021-04-10": [
                {"name": "nworico_extortion_threat.eml", "type": "Gmail Email", "time": "08:30:00", "link": "#", "mimeType": "message/rfc822"}
            ],
            "2021-06-20": [
                {"name": "whistleblower-dossier-final.pdf", "type": "Google Drive File", "time": "10:00:00", "link": "https://drive.google.com/file/d/whistleblower-dossier-final/view", "mimeType": "application/pdf"}
            ],
            "2022-01-15": [
                {"name": "unclaimed-property-rico-audit.xlsx", "type": "Google Drive File", "time": "08:30:00", "link": "https://drive.google.com/file/d/unclaimed-property-rico-audit/view", "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
            ],
            "2022-09-08": [
                {"name": "harassment_surveillance_report.eml", "type": "Gmail Email", "time": "14:00:00", "link": "#", "mimeType": "message/rfc822"}
            ],
            "2023-04-19": [
                {"name": "hud-grant-fraud-audit.pdf", "type": "Google Drive File", "time": "16:20:00", "link": "https://drive.google.com/file/d/hud-grant-fraud-audit/view", "mimeType": "application/pdf"}
            ],
            "2023-11-30": [
                {"name": "eviction-civil-access-CJ-399.pdf", "type": "Local File", "time": "09:00:00", "link": "#", "mimeType": "application/pdf"}
            ],
            "2024-05-14": [
                {"name": "rcra-citizen-suit-draft.docx", "type": "Local File", "time": "11:05:00", "link": "#", "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
            ],
            "2024-10-22": [
                {"name": "court-complaint-exhibit-B.pdf", "type": "Local File", "time": "15:45:00", "link": "#", "mimeType": "application/pdf"}
            ],
            "2025-08-05": [
                {"name": "court-transcript-2025-08-05.pdf", "type": "Local File", "time": "13:10:00", "link": "#", "mimeType": "application/pdf"}
            ],
            "2026-05-20": [
                {"name": "incident-audit-2026-05-20.json", "type": "Local File", "time": "09:30:00", "link": "https://company.status/incidents/audit-2026-05-20", "mimeType": "application/json"}
            ],
            "2026-05-24": [
                {"name": "Takeout_Location_History.json", "type": "Local File", "time": "08:00:00", "link": "#", "mimeType": "application/json"}
            ]
        }

        assets = preset_assets.get(date_str, []).copy()
        target_date = None
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            self.send_json({"error": "Invalid date format. Expected YYYY-MM-DD"}, 400)
            return

        # 1. Scan local device folders for files created/modified on this date
        try:
            workspace_dir = os.getcwd()
            user_home = os.path.expanduser('~')
            scan_targets = [
                os.path.join(user_home, 'Desktop'),
                os.path.join(user_home, 'Documents'),
                os.path.join(user_home, 'Downloads'),
                os.path.join(user_home, 'Pictures'),
                os.path.join(user_home, 'Videos'),
                workspace_dir
            ]
            
            # De-duplicate paths and ensure they exist
            scan_paths = list(set([os.path.abspath(p) for p in scan_targets if os.path.exists(p)]))
            
            SKIP_DIRS = {
                'appdata', 'node_modules', 'venv', 'env', '.git', '.github', '.gemini', 
                '__pycache__', 'microsoft', 'package', 'packages', 'program files', 
                'windows', 'system32', 'local settings', 'application data', 'temp'
            }

            for target in scan_paths:
                for root, dirs, files in os.walk(target):
                    # Skip hidden and system folders in-place
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in SKIP_DIRS]
                    
                    for file in files:
                        if file.startswith('.'):
                            continue
                        # Skip database, ICS, temp JSON, and script files to avoid timeline pollution
                        if file.endswith('.db') or file.endswith('.py') or file == 'token.json' or file == 'credentials.json':
                            continue
                            
                        filepath = os.path.join(root, file)
                        try:
                            stat = os.stat(filepath)
                            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).date()
                            ctime = datetime.datetime.fromtimestamp(stat.st_ctime).date()
                            
                            if mtime == target_date or ctime == target_date:
                                # Determine relative or absolute clean link
                                if filepath.startswith(workspace_dir):
                                    rel_path = os.path.relpath(filepath, workspace_dir)
                                    url_path = rel_path.replace(os.sep, '/')
                                    host = self.headers.get('Host', 'localhost:8080')
                                    link = f"http://{host}/{urllib.parse.quote(url_path)}"
                                    detail_path = rel_path
                                else:
                                    # Use the /local_file/ routing endpoint for out-of-workspace files
                                    url_path = filepath.replace(os.sep, '/')
                                    host = self.headers.get('Host', 'localhost:8080')
                                    link = f"http://{host}/local_file/{urllib.parse.quote(url_path)}"
                                    detail_path = filepath
                                    
                                assets.append({
                                    "name": file,
                                    "type": "Local File",
                                    "mimeType": "local/" + file.split('.')[-1] if '.' in file else "local/unknown",
                                    "link": link,
                                    "time": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%H:%M:%S"),
                                    "detail": f"Local File: {detail_path}\nSize: {stat.st_size} bytes"
                                })
                        except Exception:
                            pass
        except Exception as e:
            print(f"Error scanning local files: {e}")

        # Load Google Credentials
        creds = get_oauth_credentials()
        if not creds:
            creds = get_service_account_credentials()

        if creds:
            if hasattr(creds, 'valid') and not creds.valid:
                try:
                    creds.refresh(Request())
                except Exception:
                    pass

            # 2. Query Google Drive API for files created/modified on this date
            try:
                t_start = f"{date_str}T00:00:00Z"
                t_end = f"{date_str}T23:59:59Z"
                drive_query = f"(createdTime >= '{t_start}' and createdTime <= '{t_end}') or (modifiedTime >= '{t_start}' and modifiedTime <= '{t_end}')"
                
                results = query_drive_api(drive_query, creds)
                for file in results.get('files', []):
                    mtime_str = file.get('modifiedTime', '')
                    time_part = "12:00:00"
                    if 'T' in mtime_str:
                        time_part = mtime_str.split('T')[1].split('.')[0]
                    
                    owner_name = file.get('owners', [{}])[0].get('displayName', 'Unknown')
                    assets.append({
                        "name": file['name'],
                        "type": "Google Drive File",
                        "mimeType": file['mimeType'],
                        "link": file.get('webViewLink', '#'),
                        "time": time_part,
                        "detail": f"Drive File (Owner: {owner_name})\nID: {file['id']}"
                    })
            except Exception as e:
                print(f"Error querying Google Drive: {e}")

            # 3. Query Gmail API for messages received/sent on this date
            try:
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                after_dt = dt - datetime.timedelta(days=1)
                before_dt = dt + datetime.timedelta(days=1)
                gmail_query = f"after:{after_dt.strftime('%Y/%m/%d')} before:{before_dt.strftime('%Y/%m/%d')}"
                
                gmail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages"
                headers = {"Authorization": f"Bearer {creds.token}"}
                params = {"q": gmail_query, "maxResults": 15}
                
                response = requests.get(gmail_url, headers=headers, params=params)
                if response.status_code == 200:
                    messages = response.json().get('messages', [])
                    for msg in messages:
                        msg_detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}"
                        msg_res = requests.get(msg_detail_url, headers=headers)
                        if msg_res.status_code == 200:
                            msg_data = msg_res.json()
                            headers_list = msg_data.get('payload', {}).get('headers', [])
                            
                            subject = "No Subject"
                            from_user = "Unknown"
                            for h in headers_list:
                                if h['name'].lower() == 'subject':
                                    subject = h['value']
                                elif h['name'].lower() == 'from':
                                    from_user = h['value']
                                    
                            msg_time_ms = int(msg_data.get('internalDate', 0))
                            msg_dt = datetime.datetime.fromtimestamp(msg_time_ms / 1000.0, tz=datetime.timezone.utc)
                            
                            # Filter to exact date
                            if msg_dt.strftime("%Y-%m-%d") == date_str:
                                link = f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}"
                                assets.append({
                                    "name": subject,
                                    "type": "Gmail Email",
                                    "mimeType": "gmail/email",
                                    "link": link,
                                    "time": msg_dt.strftime("%H:%M:%S"),
                                    "detail": f"Email from: {from_user}\nSnippet: {msg_data.get('snippet', '')}"
                                })
            except Exception as e:
                print(f"Gmail API query skipped: {e}")

        # Deduplicate assets by name and link
        seen = set()
        deduped_assets = []
        for a in assets:
            key = (a['name'], a['link'])
            if key not in seen:
                seen.add(key)
                deduped_assets.append(a)

        # Sort all assets chronologically by time
        deduped_assets.sort(key=lambda x: x['time'])
        self.send_json({"date": date_str, "assets": deduped_assets})
            
    def handle_api_auth(self):
        try:
            creds = run_oauth_flow()
            self.send_json({
                "success": True, 
                "message": "OAuth2 authentication completed successfully.",
                "owner": creds.to_json()
            })
        except Exception as e:
            self.send_json({
                "success": False,
                "error": "Authentication Failed",
                "message": str(e)
            }, 500)

def serve_dashboard():
    """Run local HTTP server."""
    handler = SearchAPIRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"\n=============================================")
            print(f"OSINT Google Drive & Local Daily Search Engine")
            print(f"Server running at: http://localhost:{PORT}")
            print(f"=============================================\n")
            try:
                webbrowser.open(f"http://localhost:{PORT}")
            except Exception as e:
                print(f"Note: Could not open browser automatically: {e}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error starting server on port {PORT}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Google Drive OSINT & Search Tool")
    parser.add_argument('--serve', action='store_true', help="Launch the Web Search Dashboard")
    parser.add_argument('--query', type=str, help="Run an authenticated CLI search query against Google Drive")
    parser.add_argument('--dork', type=str, help="Generate Google Dorking search links for OSINT")
    parser.add_argument('--auth', action='store_true', help="Initiate OAuth2 browser flow to authenticate")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        args.serve = True
        
    if args.auth:
        print("Starting OAuth2 Login Flow...")
        try:
            run_oauth_flow()
            print("Authentication successful! token.json created.")
        except Exception as e:
            print(f"Authentication Failed: {e}")
            
    elif args.dork:
        print(f"\nGenerating OSINT Dorks for: '{args.dork}'\n")
        dorks = generate_dorks(args.dork)
        print(f"{'Dork Purpose':<35} | {'Query Search Operator'}")
        print("-" * 80)
        for d in dorks:
            print(f"{d['title']:<35} | {d['query']}")
            print(f"Link: {d['url']}\n")
            
    elif args.query:
        print(f"Running Google Drive API search for: '{args.query}'...")
        creds = get_oauth_credentials()
        if not creds:
            creds = get_service_account_credentials()
        if not creds:
            print("Error: No authentication found. Please run with --auth first or put service_account.json in place.")
            sys.exit(1)
            
        if hasattr(creds, 'valid') and not creds.valid:
            creds.refresh(Request())
            
        try:
            drive_query = f"name contains '{args.query}' or fullText contains '{args.query}'"
            results = query_drive_api(drive_query, creds)
            files = results.get('files', [])
            if not files:
                print("No files found matching the query.")
            else:
                print(f"\nFound {len(files)} files:\n")
                for f in files:
                    owner = f.get('owners', [{}])[0].get('displayName', 'Unknown')
                    print(f"- {f['name']} ({f['mimeType']})")
                    print(f"  ID:   {f['id']}")
                    print(f"  Link: {f.get('webViewLink', 'N/A')}")
                    print(f"  Owner: {owner} | Modified: {f.get('modifiedTime', 'N/A')}\n")
        except Exception as e:
            print(f"Search failed: {e}")
            
    elif args.serve:
        serve_dashboard()

if __name__ == '__main__':
    main()
