"""oauth_server.py — Local OAuth server that captures Google Tasks callback"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser, threading, time
from google_auth_oauthlib.flow import InstalledAppFlow

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/tasks"]
AUTH_CODE = [None]
LOG_FILE = os.path.join(AGENT_DIR, "oauth_server.log")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        if "code" in qs:
            AUTH_CODE[0] = qs["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OSINTNeoAi authorized! Close this window.")
            log("Got auth code, length=" + str(len(AUTH_CODE[0])))
        else:
            err = qs.get("error", ["unknown"])[0]
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {err}".encode())
            log(f"Auth error: {err}")
    def log_message(self, fmt, *args):
        pass

# Start server
server = HTTPServer(("localhost", 0), Handler)
port = server.server_address[1]
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

# Generate URL
flow = InstalledAppFlow.from_client_secrets_file(
    os.path.join(AGENT_DIR, "client_secret_tasks.json"), SCOPES)
flow.redirect_uri = f"http://localhost:{port}/"
url, _ = flow.authorization_url(prompt="consent", access_type="offline")

# Save URL for the tool to read
with open(os.path.join(AGENT_DIR, "oauth_url.txt"), "w") as f:
    f.write(url)

log(f"Server on port {port}")
log(f"URL: {url}")
webbrowser.open(url)

# Wait up to 10 minutes
for _ in range(600):
    if AUTH_CODE[0]:
        break
    time.sleep(1)

if AUTH_CODE[0]:
    log("Exchanging code for token...")
    flow.fetch_token(code=AUTH_CODE[0])
    creds = flow.credentials
    with open(os.path.join(AGENT_DIR, "tasks_token.json"), "w") as f:
        f.write(creds.to_json())
    log("Token saved!")
else:
    log("TIMEOUT - no auth received")

server.shutdown()
