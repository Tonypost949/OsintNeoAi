"""
Meta Graph API Webhook Bridge for Facebook & Instagram Auto-Replying
Handles @mentions, comments, and DMs, correlating responses via Makaveli Agent Engine.
Reference: https://developer.meta.com/ai/ & https://dev.meta.ai/docs/api-reference/
"""

import os
import sys
import json
import http.server
import socketserver
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

# Ensure root directory on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.meta_model_client import MetaModelClient
from core.meta_agent_loop import MakaveliAgentLoop

PORT = int(os.environ.get("PORT", 8080))
VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN", "makaveli_osint_verify_2026")
PAGE_ACCESS_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN", "")

agent_loop = MakaveliAgentLoop()

def post_facebook_comment_reply(comment_id: str, message: str) -> bool:
    """Post a reply comment to Facebook feed via Graph API."""
    if not PAGE_ACCESS_TOKEN:
        print(f"[DRY-RUN FB REPLY] To Comment ID: {comment_id} | Msg: {message}")
        return True

    url = f"https://graph.facebook.com/v20.0/{comment_id}/comments"
    data = urllib.parse.urlencode({
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR FB REPLY] {e}")
        return False

def post_instagram_reply(comment_id: str, message: str) -> bool:
    """Post a reply to Instagram comment via Graph API."""
    if not PAGE_ACCESS_TOKEN:
        print(f"[DRY-RUN IG REPLY] To Comment ID: {comment_id} | Msg: {message}")
        return True

    url = f"https://graph.facebook.com/v20.0/{comment_id}/replies"
    data = urllib.parse.urlencode({
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR IG REPLY] {e}")
        return False

class MetaWebhookHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Handler for Meta Webhooks (Verification & Event Ingestion)."""

    def do_GET(self):
        """Handle Meta Webhook verification handshake (hub.challenge)."""
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        mode = query_params.get("hub.mode", [""])[0]
        token = query_params.get("hub.verify_token", [""])[0]
        challenge = query_params.get("hub.challenge", [""])[0]

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("[WEBHOOK VERIFIED] Meta subscription confirmed.")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(challenge.encode("utf-8"))
        else:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden: Invalid verification token.")

    def do_POST(self):
        """Handle incoming webhook events (comments, mentions, messages)."""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        print(f"[WEBHOOK EVENT RECEIVED] Object: {payload.get('object')}")

        # Process entries
        for entry in payload.get("entry", []):
            # Facebook Page Changes (Feed / Comments)
            for change in entry.get("changes", []):
                val = change.get("value", {})
                item = val.get("item")
                verb = val.get("verb")
                msg = val.get("message", "")
                comment_id = val.get("comment_id")

                if item == "comment" and verb == "add" and comment_id:
                    # Check if tagged or targeting Makaveli
                    if "@makaveli" in msg.lower() or "@osintneoai" in msg.lower():
                        print(f"[MENTION TRIGGER] Processing comment: {msg}")
                        reply_text = agent_loop.run(msg)
                        post_facebook_comment_reply(comment_id, reply_text)

            # Instagram Mentions / Comments
            for change in entry.get("changes", []):
                val = change.get("value", {})
                text = val.get("text", "")
                comment_id = val.get("id")
                if comment_id and ("@makaveli" in text.lower() or "@osintneoai" in text.lower()):
                    print(f"[IG MENTION TRIGGER] Processing IG text: {text}")
                    reply_text = agent_loop.run(text)
                    post_instagram_reply(comment_id, reply_text)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"EVENT_RECEIVED")

def run_server(port=PORT):
    with socketserver.TCPServer(("", port), MetaWebhookHandler) as httpd:
        print(f"[BRIDGE SERVER LIVE] Listening on port {port}")
        print(f"[VERIFY TOKEN] {VERIFY_TOKEN}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
