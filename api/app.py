"""
Azure Cloud Webhook & Universal Makaveli AI Chatbot Engine
Supports Facebook Page Comments, Messenger DMs, Instagram Comments & Mentions.
Answers ANYTHING like a normal conversational AI chatbot, powered by Gemini & Forensic OSINT Tools.
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
PAGE_ID = os.getenv("FB_PAGE_ID", "1264271163441359")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Gemini AI Client
gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        for m_name in ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]:
            try:
                gemini_model = genai.GenerativeModel(m_name)
                print(f"[AI MODEL READY] Initialized: {m_name}")
                break
            except Exception:
                continue
    except Exception as e:
        print(f"[AI INIT NOTICE] {e}")

# Initialize Forensic Tool Loop if available
try:
    from core.meta_agent_loop import MakaveliAgentLoop
    agent_loop = MakaveliAgentLoop()
except Exception:
    agent_loop = None

def generate_makaveli_response(prompt: str, is_dm: bool = False) -> str:
    """
    Generate conversational AI response for ANY topic, question, or forensic prompt.
    """
    cleaned = prompt.strip()
    
    # 1. Check if user is asking for forensic tool audit
    if agent_loop and any(k in cleaned.lower() for k in ["audit", "trace", "plume", "17642", "shell network", "docket"]):
        try:
            return agent_loop.run(cleaned)
        except Exception as e:
            print(f"[AGENT TOOL ERROR] {e}")

    # 2. Universal Conversational AI via Gemini
    if gemini_model:
        try:
            length_rule = "Keep replies detailed, natural, and helpful like a high-IQ assistant." if is_dm else "Keep reply punchy and under 3 sentences for public comments."
            system_prompt = (
                "You are Makaveli — Lead OSINT Agent & AI Companion of OsintNeoAi. "
                "You can discuss ANYTHING: answer everyday questions, banter, explain concepts, "
                "give advice, analyze data, or conduct OSINT research. "
                "Personality: sharp, tactical, intelligent, authentic, respectful, and zero-bullshit. "
                f"{length_rule}\n\n"
                f"User Message: {cleaned}"
            )
            res = gemini_model.generate_content(system_prompt)
            if res and res.text:
                return res.text.strip()
        except Exception as e:
            print(f"[GEMINI GENERATION ERROR] {e}")

    # 3. Meta Model API Fallback
    meta_key = os.getenv("META_API_KEY")
    if meta_key:
        try:
            url = "https://api.meta.ai/v1/chat/completions"
            data = json.dumps({
                "model": "llama-3.3-70b-instruct",
                "messages": [
                    {"role": "system", "content": "You are Makaveli, a sharp and helpful AI chatbot. Reply concisely."},
                    {"role": "user", "content": cleaned}
                ],
                "max_tokens": 250
            }).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {meta_key}"
            }, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                r = json.loads(resp.read().decode("utf-8"))
                return r["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[META API ERROR] {e}")

    # 4. Fallback Default
    return f"⚡ [Makaveli]: Signal received: '{cleaned}'. Systems operational across all data vectors."

def reply_facebook_comment(comment_id: str, message: str) -> bool:
    """Post public reply back to a Facebook comment."""
    if not FB_PAGE_TOKEN:
        print(f"[NO FB_PAGE_TOKEN] Dry-run comment reply to {comment_id}: {message}")
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
        print(f"[REPLY COMMENT ERROR] {e}")
        return False

def reply_facebook_messenger(recipient_id: str, message: str) -> bool:
    """Reply directly to a Messenger / Direct Message (text)."""
    if not FB_PAGE_TOKEN:
        print(f"[NO FB_PAGE_TOKEN] Dry-run Messenger reply to {recipient_id}: {message}")
        return True
    try:
        url = "https://graph.facebook.com/v20.0/me/messages"
        payload = json.dumps({
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE"
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{url}?access_token={FB_PAGE_TOKEN}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[REPLY MESSENGER ERROR] {e}")
        return False

def reply_instagram_comment(comment_id: str, message: str) -> bool:
    """Post reply back to an Instagram comment."""
    if not FB_PAGE_TOKEN:
        print(f"[NO FB_PAGE_TOKEN] Dry-run IG reply to {comment_id}: {message}")
        return True
    try:
        url = f"https://graph.facebook.com/v20.0/{comment_id}/replies"
        data = urllib.parse.urlencode({
            "message": message,
            "access_token": FB_PAGE_TOKEN
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[REPLY IG ERROR] {e}")
        return False

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ONLINE",
        "service": "OSINTNeoAi Universal AI Chatbot Node",
        "page_id": PAGE_ID,
        "ai_engine": "Gemini 3.6 Flash / Makaveli",
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
    """
    Universal Meta Webhook Ingestion:
    - Handles Facebook Page Comments (auto-replies to any comment or mention)
    - Handles Facebook Messenger DMs (auto-replies to any direct message text)
    - Handles Instagram Comments & Mentions
    """
    payload = request.get_json(silent=True) or {}
    print(f"[WEBHOOK EVENT RECEIVED] Object: {payload.get('object')}")

    for entry in payload.get("entry", []):
        # 1. Messenger / Direct Message Ingestion (Texting)
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event.get("sender", {}).get("id")
            recipient_id = msg_event.get("recipient", {}).get("id")
            text = msg_event.get("message", {}).get("text")
            
            # Avoid self-reply loops
            if sender_id and text and sender_id != PAGE_ID and not msg_event.get("message", {}).get("is_echo"):
                print(f"[MESSENGER DM RECEIVED] From {sender_id}: {text}")
                ai_reply = generate_makaveli_response(text, is_dm=True)
                reply_facebook_messenger(sender_id, ai_reply)

        # 2. Page Feed / Comment Ingestion
        for change in entry.get("changes", []):
            val = change.get("value", {})
            item = val.get("item")
            verb = val.get("verb")
            msg = val.get("message", "")
            comment_id = val.get("comment_id")

            # Reply to any comment added
            if item == "comment" and verb == "add" and comment_id and msg:
                # Filter out our own page's comments to prevent loops
                from_id = val.get("from", {}).get("id")
                if from_id != PAGE_ID:
                    print(f"[FEED COMMENT RECEIVED] ID: {comment_id} | Msg: {msg}")
                    ai_reply = generate_makaveli_response(msg, is_dm=False)
                    reply_facebook_comment(comment_id, ai_reply)

            # Instagram Comments
            ig_comment_id = val.get("id")
            ig_text = val.get("text")
            if ig_comment_id and ig_text:
                print(f"[INSTAGRAM COMMENT RECEIVED] ID: {ig_comment_id} | Msg: {ig_text}")
                ai_reply = generate_makaveli_response(ig_text, is_dm=False)
                reply_instagram_comment(ig_comment_id, ai_reply)

    return "EVENT_RECEIVED", 200

@app.route("/syncfusion", methods=["GET"])
@app.route("/syncfusion/", methods=["GET"])
def serve_syncfusion():
    public_dir = os.path.join(ROOT_DIR, "public")
    for f in ["syncfusion_grid_v3_steroids.html", "syncfusion_grid.html_v2", "syncfusion_grid.html"]:
        fp = os.path.join(public_dir, f)
        if os.path.exists(fp):
            return send_from_directory(public_dir, f)
    return "Syncfusion grid not found", 404

@app.route("/tasks", methods=["GET"])
@app.route("/tasks/", methods=["GET"])
def serve_tasks():
    public_dir = os.path.join(ROOT_DIR, "public")
    return send_from_directory(public_dir, "tasks.html")

@app.route("/api/tasks", methods=["GET"])
def serve_api_tasks():
    tasks_file = os.path.join(ROOT_DIR, "data", "tasks.json")
    if os.path.exists(tasks_file):
        with open(tasks_file, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"tasks": [], "status": "empty"}), 200

@app.route("/maps", methods=["GET"])
@app.route("/maps/", methods=["GET"])
def serve_maps_hub():
    maps_hub_file = os.path.join(ROOT_DIR, "maps_hub.html")
    if os.path.exists(maps_hub_file):
        return send_from_directory(ROOT_DIR, "maps_hub.html")
    return "Maps hub not found", 404

@app.route("/gods_eye_view.html", methods=["GET"])
@app.route("/maps/gods_eye_view.html", methods=["GET"])
def serve_gods_eye():
    return send_from_directory(ROOT_DIR, "gods_eye_view.html")

@app.route("/public/<path:filename>", methods=["GET"])
def serve_public_files(filename):
    public_dir = os.path.join(ROOT_DIR, "public")
    return send_from_directory(public_dir, filename)

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

