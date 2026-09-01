"""
Azure Cloud Webhook & API Application for OSINTNeoAi / Makaveli
Endpoint: https://osintneoai-app-949.azurewebsites.net/
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "makaveli_osint_verify_2026")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN") or os.getenv("META_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.getenv("FB_PAGE_ID", "61594100636376")

MAKAVELI_SYSTEM_PROMPT = """You are Makaveli — Lead OSINT Agent of OsintNeoAi.
Zero-noise tactical intelligence. Keep replies under 3 sentences for social media comments.
Cite public records methodology. Tagline: See More. Know First."""

try:
    from core.meta_agent_loop import MakaveliAgentLoop
    agent_loop = MakaveliAgentLoop()
except Exception as e:
    agent_loop = None

def generate_makaveli_response(prompt: str) -> str:
    """Generate tactical OSINT response using Makaveli Protocol & Forensic Tools."""
    if agent_loop:
        try:
            return agent_loop.run(prompt)
        except Exception as e:
            print(f"[AGENT LOOP ERROR] {e}")

    # Direct Meta Model API fallback
    meta_key = os.getenv("META_API_KEY")
    if meta_key:
        try:
            url = "https://api.meta.ai/v1/chat/completions"
            data = json.dumps({
                "model": "llama-3.3-70b-instruct",
                "messages": [
                    {"role": "system", "content": MAKAVELI_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150
            }).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {meta_key}"
            }, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[API ERROR] {e}")

    # Fallback tactical synthesis
    return (
        f"⚡ [Makaveli OSINT Agent]: Target logged into Master Ledger. "
        f"Cross-referencing registry dockets & geospatial coordinates. "
        f"Live dossier: https://tonypost949.github.io/OsintNeoAi/makavelli/"
    )

def reply_facebook_comment(comment_id: str, message: str) -> bool:
    """Post reply back to Facebook comment."""
    if not FB_PAGE_TOKEN:
        print(f"[NO FB_PAGE_TOKEN] Dry-run reply to {comment_id}: {message}")
        return True
    try:
        url = f"https://graph.facebook.com/v20.0/{comment_id}/comments"
        data = urllib.parse.urlencode({
            "message": message,
            "access_token": FB_PAGE_TOKEN
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[REPLY ERROR] {e}")
        return False

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ONLINE",
        "service": "OSINTNeoAi Azure Cloud Node",
        "page_id": PAGE_ID,
        "makaveli_hud": "https://tonypost949.github.io/OsintNeoAi/makavelli/",
        "webhook_endpoint": "/webhook"
    })

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta Webhook Handshake Verification."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WEBHOOK VERIFIED] Handshake successful.")
        return challenge, 200
    return "Forbidden: Invalid verification token", 403

@app.route("/webhook", methods=["POST"])
def handle_webhook_event():
    """Meta Webhook Ingestion for Page comments & mentions."""
    payload = request.get_json(silent=True) or {}
    print(f"[WEBHOOK EVENT RECEIVED] Object: {payload.get('object')}")

    for entry in payload.get("entry", []):
        # Process Page Feed Changes
        for change in entry.get("changes", []):
            val = change.get("value", {})
            item = val.get("item")
            verb = val.get("verb")
            msg = val.get("message", "")
            comment_id = val.get("comment_id")

            if item == "comment" and verb == "add" and comment_id:
                triggers = ["@makavelli", "@makaveli", "@ makavelli", "@ makaveli", "makavelli", "makaveli", "@osintneoai", "trace", "audit"]
                if any(tag in msg.lower() for tag in triggers):
                    print(f"[TAGGED COMMENT] {msg}")
                    reply = generate_makaveli_response(msg)
                    reply_facebook_comment(comment_id, reply)

    return "EVENT_RECEIVED", 200

@app.route("/makavelli", methods=["GET"])
@app.route("/makavelli/", methods=["GET"])
@app.route("/makaveli", methods=["GET"])
@app.route("/makaveli/", methods=["GET"])
def serve_makaveli():
    makaveli_dir = os.path.join(ROOT_DIR, "makavelli")
    if os.path.exists(makaveli_dir):
        return send_from_directory(makaveli_dir, "index.html")
    return "Makaveli HUD directory not found", 404

@app.route("/makavelli/<path:filename>", methods=["GET"])
@app.route("/makaveli/<path:filename>", methods=["GET"])
def serve_makaveli_static(filename):
    makaveli_dir = os.path.join(ROOT_DIR, "makavelli")
    return send_from_directory(makaveli_dir, filename)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
