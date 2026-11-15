#!/usr/bin/env python3
"""authorize_tasks.py - one-shot loopback OAuth for Google Tasks (Law 3).

Writes the consent URL to tasks_auth_url.txt, listens on 127.0.0.1:8765 for the
redirect, exchanges the code, and writes tasks_token.json.
Non-interactive: never prompts on stdin.
"""
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from google_auth_oauthlib.flow import Flow

BASE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(BASE, "client_secret_tasks.json")
TOKEN = os.path.join(BASE, "tasks_token.json")
URLFILE = os.path.join(BASE, "tasks_auth_url.txt")
SCOPES = ["https://www.googleapis.com/auth/tasks"]
PORT = 8765
REDIRECT = f"http://127.0.0.1:{PORT}/"

captured = {"code": None, "error": None, "state": None}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        captured["code"] = (q.get("code") or [None])[0]
        captured["error"] = (q.get("error") or [None])[0]
        captured["state"] = (q.get("state") or [None])[0]
        body = b"<html><body style='font-family:sans-serif'><h2>OsintNeoAi Google Tasks authorization received.</h2><p>You can close this tab.</p></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def main() -> int:
    flow = Flow.from_client_secrets_file(CLIENT, scopes=SCOPES, redirect_uri=REDIRECT)
    flow.oauth2session.scope = SCOPES
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    with open(URLFILE, "w", encoding="utf-8") as f:
        f.write(auth_url)

    srv = HTTPServer(("127.0.0.1", PORT), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    deadline = time.time() + 420
    while time.time() < deadline and not captured["code"] and not captured["error"]:
        time.sleep(1)
    srv.shutdown()

    if captured["error"]:
        print(json.dumps({"ok": False, "error": captured["error"]}))
        return 1
    if not captured["code"]:
        print(json.dumps({"ok": False, "error": "timeout waiting for redirect"}))
        return 1

    flow.fetch_token(code=captured["code"])
    creds = flow.credentials
    with open(TOKEN, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(json.dumps({
        "ok": True,
        "token_path": TOKEN,
        "scopes": creds.scopes,
        "has_refresh_token": bool(creds.refresh_token),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
