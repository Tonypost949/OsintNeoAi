"""get_token.py — Get OAuth token for any scope using local server callback"""
import sys, os, json, webbrowser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading, time
from google_auth_oauthlib.flow import InstalledAppFlow

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_CODE = [None]

label = sys.argv[1] if len(sys.argv) > 1 else "App"
scope = sys.argv[2] if len(sys.argv) > 2 else "https://www.googleapis.com/auth/drive.readonly"
token_file = sys.argv[3] if len(sys.argv) > 3 else f"token_{label.lower()}.json"
client_secret = sys.argv[4] if len(sys.argv) > 4 else "client_secret.json"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        if "code" in qs:
            AUTH_CODE[0] = qs["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"OSINTNeoAi {label} authorized!".encode())
            print(f"[OK] Got auth code", flush=True)
        else:
            err = qs.get("error", ["unknown"])[0]
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {err}".encode())
            print(f"[ERR] Auth error: {err}", flush=True)
    def log_message(self, fmt, *args):
        pass

server = HTTPServer(("localhost", 0), Handler)
port = server.server_address[1]
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

flow = InstalledAppFlow.from_client_secrets_file(
    os.path.join(AGENT_DIR, client_secret), [scope])
flow.redirect_uri = f"http://localhost:{port}/"
url, _ = flow.authorization_url(prompt="consent", access_type="offline")

url_file = os.path.join(AGENT_DIR, "oauth_url.txt")
with open(url_file, "w") as f:
    f.write(url)

print(f"\n{'='*50}")
print(f"OAuth for {label}")
print(f"Scope: {scope}")
print(f"{'='*50}")
print(f"\nURL: {url}\n", flush=True)
webbrowser.open(url)

for _ in range(300):  # 5 min timeout
    if AUTH_CODE[0]:
        break
    time.sleep(1)

if AUTH_CODE[0]:
    print("Exchanging code for token...", flush=True)
    flow.fetch_token(code=AUTH_CODE[0])
    creds = flow.credentials
    path = os.path.join(AGENT_DIR, token_file)
    with open(path, "w") as f:
        f.write(creds.to_json())
    print(f"Token saved to {token_file}", flush=True)
else:
    print("TIMEOUT", flush=True)

server.shutdown()
