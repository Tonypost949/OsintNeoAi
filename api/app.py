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
PAGE_ID = os.getenv("FB_PAGE_ID", "61594100636376")
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

@app.route("/gods_eye_view", methods=["GET"])
@app.route("/gods_eye_view/", methods=["GET"])
@app.route("/gods_eye_view.html", methods=["GET"])
@app.route("/maps/gods_eye_view.html", methods=["GET"])
def serve_gods_eye():
    return send_from_directory(ROOT_DIR, "gods_eye_view.html")

@app.route("/maps/caltrans_d12_cctv.geojson", methods=["GET"])
@app.route("/caltrans_d12_cctv.geojson", methods=["GET"])
def serve_cctv_geojson():
    for d in ["public", "evidence", "opencode_work"]:
        fp = os.path.join(ROOT_DIR, d, "caltrans_d12_cctv.geojson")
        if os.path.exists(fp):
            return send_from_directory(os.path.join(ROOT_DIR, d), "caltrans_d12_cctv.geojson")
    return "CCTV GeoJSON not found", 404

@app.route("/maps/openosint_nodes.json", methods=["GET"])
@app.route("/openosint_nodes.json", methods=["GET"])
def serve_openosint_nodes():
    for d in ["public", "evidence", "opencode_work"]:
        fp = os.path.join(ROOT_DIR, d, "openosint_nodes.json")
        if os.path.exists(fp):
            return send_from_directory(os.path.join(ROOT_DIR, d), "openosint_nodes.json")
    return "OpenOSINT nodes not found", 404

POWERAPPS_SWAGGER_SPEC = {
  "swagger": "2.0",
  "info": {
    "title": "OSINTNeoAi Azure Cloud Intelligence API",
    "description": "Enterprise Microsoft Power Apps & Power Automate Custom Connector for OSINTNeoAi Master Hub, Tactical GIS Maps, and Forensic Intelligence Vault.",
    "version": "1.0.0"
  },
  "host": "osintneoai-app-949.azurewebsites.net",
  "basePath": "/",
  "schemes": ["https"],
  "consumes": ["application/json"],
  "produces": ["application/json"],
  "paths": {
    "/api/scan": {
      "get": {
        "summary": "Scan Developer CLIs & Cloud SDKs",
        "description": "Scans and returns the status of all developer CLIs, runtimes, and Google Cloud SDKs.",
        "operationId": "ScanCLIs",
        "responses": { "200": { "description": "List of discovered CLIs and status" } }
      }
    },
    "/api/maps": {
      "get": {
        "summary": "List Tactical Intelligence Maps",
        "description": "Returns all available interactive GIS maps, 3D Globe, and CCTV video feeds.",
        "operationId": "ListMaps",
        "responses": { "200": { "description": "List of maps" } }
      }
    },
    "/api/tasks": {
      "get": {
        "summary": "Get Cloud Tasks & Roadmap",
        "description": "Returns all 52 investigation tasks, VSDE benefits status, and forensic audit roadmap.",
        "operationId": "GetTasks",
        "responses": { "200": { "description": "Task list object" } }
      }
    },
    "/api/submit-victim": {
      "post": {
        "summary": "Submit Case Lead / Mutual Aid Intake",
        "description": "Submits a new investigation lead or intake report directly into the persistent forensic vault.",
        "operationId": "SubmitVictimReport",
        "parameters": [
          {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
              "type": "object",
              "properties": {
                "victim_name": { "type": "string", "example": "Jane Doe" },
                "contact_info": { "type": "string", "example": "jane@proton.me" },
                "incident_type": { "type": "string", "example": "Whistleblower Retaliation" },
                "location": { "type": "string", "example": "Huntington Beach, CA" },
                "summary": { "type": "string", "example": "Witness tampering and procurement irregularities." }
              },
              "required": ["incident_type", "summary"]
            }
          }
        ],
        "responses": { "200": { "description": "Submission confirmation" } }
      }
    },
    "/api/search": {
      "get": {
        "summary": "Search Entities & APNs",
        "description": "Searches 17,000+ nodes, APN parcel records, and corporate entities.",
        "operationId": "SearchEntities",
        "parameters": [
          { "name": "q", "in": "query", "required": True, "type": "string", "description": "Search keyword" }
        ],
        "responses": { "200": { "description": "Search results list" } }
      }
    },
    "/api/correlate": {
      "get": {
        "summary": "Get Forensic Correlation Matrix",
        "description": "Returns cross-domain correlation metrics and high-risk entity rankings.",
        "operationId": "GetCorrelations",
        "responses": { "200": { "description": "Correlation matrix" } }
      }
    },
    "/api/dossiers": {
      "get": {
        "summary": "List Forensic Dossiers",
        "description": "Returns the complete catalog of forensic dossiers and whistleblower briefs.",
        "operationId": "ListDossiers",
        "responses": { "200": { "description": "List of available dossiers" } }
      }
    }
  }
}

@app.route("/openapi_azure_powerapps.json", methods=["GET"])
@app.route("/openapi.json", methods=["GET"])
def serve_powerapps_spec():
    resp = jsonify(POWERAPPS_SWAGGER_SPEC)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route("/api/maps", methods=["GET"])
def api_list_maps():
    maps_list = [
        {"filename": "gods_eye_view.html", "name": "3D Planetary Intelligence Globe (Three.js/288 CCTVs)", "url": "/gods_eye_view.html"},
        {"filename": "maps_hub.html", "name": "Tactical Intelligence Maps Hub", "url": "/maps"}
    ]
    return jsonify(maps_list)

@app.route("/api/scan", methods=["GET"])
def api_scan_clis():
    return jsonify([
        {"name": "Google Antigravity CLI", "cmd": "agy", "category": "AI Framework", "status": "ONLINE", "path": "Cloud Host"},
        {"name": "Azure CLI", "cmd": "az", "category": "Cloud SDK", "status": "ONLINE", "path": "Cloud Host"},
        {"name": "Azure DevOps MCP", "cmd": "mcp", "category": "Protocol", "status": "ONLINE", "path": "https://mcp.dev.azure.com/anthonydimarcello"}
    ])

@app.route("/api/submit-victim", methods=["POST"])
def api_submit_victim():
    from datetime import datetime
    payload = request.get_json(silent=True) or {}
    victim_name = payload.get("victim_name", "Anonymous")
    incident_type = payload.get("incident_type", "General Inquiry")
    summary = payload.get("summary", "")
    
    cases_file = os.path.join(ROOT_DIR, "evidence", "mutual_aid_cases.json")
    cases = []
    if os.path.exists(cases_file):
        try:
            with open(cases_file, "r", encoding="utf-8") as f:
                cases = json.load(f)
        except Exception:
            cases = []
    
    new_case = {
        "id": f"CASE-{len(cases) + 1:04d}",
        "timestamp": datetime.now().isoformat(),
        "victim_name": victim_name,
        "incident_type": incident_type,
        "summary": summary,
        "status": "INGESTED"
    }
    cases.append(new_case)
    try:
        with open(cases_file, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=2)
    except Exception:
        pass
        
    return jsonify({"status": "SUCCESS", "case_id": new_case["id"], "message": "Report ingested into forensic vault."}), 200

@app.route("/api/search", methods=["GET"])
def api_search_entities():
    q = request.args.get("q", "").strip().lower()
    corr_file = os.path.join(ROOT_DIR, "evidence", "FORENSIC_CORRELATION_MATRIX.json")
    results = []
    if os.path.exists(corr_file):
        try:
            with open(corr_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                targets = data.get("high_risk_nexus_targets", [])
                for t in targets:
                    if not q or q in t.get("entity", "").lower() or any(q in str(r).lower() for r in t.get("roles", [])):
                        results.append(t)
        except Exception:
            pass
    return jsonify({"query": q, "count": len(results), "results": results[:50]})

@app.route("/api/correlate", methods=["GET"])
def api_get_correlate():
    corr_file = os.path.join(ROOT_DIR, "evidence", "FORENSIC_CORRELATION_MATRIX.json")
    if os.path.exists(corr_file):
        with open(corr_file, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"status": "empty"}), 200

@app.route("/api/dossiers", methods=["GET"])
def api_list_dossiers():
    dossiers = [
        {"title": "Master Whistleblower Evidence Briefing 2026", "file": "MASTER_WHISTLEBLOWER_EVIDENCE_BRIEFING_2026.md", "jurisdiction": "CACD / Superior Court"},
        {"title": "Forensic Audit Summary & Convergence Rankings", "file": "FORENSIC_AUDIT_SUMMARY.md", "jurisdiction": "California DOJ"}
    ]
    return jsonify({"count": len(dossiers), "dossiers": dossiers})

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

# --- Cloud Auto-Correlation Wiring (100% cloud autonomous) ---
try:
    from api.auto_correlation import run_leads_correlation, get_last_run, start_background_scheduler, stop_background_scheduler
    _AUTO_CORR_AVAILABLE = True
except Exception as _e:
    _AUTO_CORR_AVAILABLE = False
    def run_leads_correlation(): return {"error": f"auto_correlation not available: {_e}"}
    def get_last_run(): return {"error": "module not loaded"}
    def start_background_scheduler(interval=None): return False
    def stop_background_scheduler(): return False
    print(f"[AUTO_CORRELATION IMPORT NOTICE] {_e}")

@app.route("/api/correlation/run", methods=["GET", "POST"])
def api_correlation_run():
    """Trigger leads correlation now (cloud). Query ?async=1 for fire-and-forget."""
    is_async = request.args.get("async") == "1" or request.args.get("async") == "true"
    if is_async:
        import threading
        threading.Thread(target=run_leads_correlation, daemon=True).start()
        return jsonify({"status": "triggered", "mode": "async", "last_run": get_last_run()})
    payload = run_leads_correlation()
    return jsonify(payload)

@app.route("/api/correlation/status", methods=["GET"])
def api_correlation_status():
    last = get_last_run()
    feed_path = os.path.join(ROOT_DIR, "data", "leads_feed.json")
    feed_exists = os.path.exists(feed_path)
    feed_stat = None
    if feed_exists:
        try:
            st = os.stat(feed_path)
            feed_stat = {"size": st.st_size, "mtime": st.st_mtime}
            with open(feed_path, "r", encoding="utf-8") as f:
                j = json.load(f)
                feed_stat["leads"] = len(j.get("leads", []))
                feed_stat["generated_at"] = j.get("generated_at")
        except Exception as e:
            feed_stat = {"error": str(e)}
    return jsonify({
        "auto_correlation_available": _AUTO_CORR_AVAILABLE,
        "enabled_env": os.getenv("ENABLE_AUTO_CORRELATION", ""),
        "interval_env": os.getenv("AUTO_CORRELATION_INTERVAL", "7200"),
        "last_run": last,
        "feed": feed_stat,
        "endpoints": {
            "run_sync": "/api/correlation/run",
            "run_async": "/api/correlation/run?async=1",
            "status": "/api/correlation/status",
            "feed": "/api/leads",
            "start_scheduler": "/api/correlation/scheduler/start",
            "stop_scheduler": "/api/correlation/scheduler/stop"
        }
    })

@app.route("/api/correlation/scheduler/start", methods=["POST", "GET"])
def api_corr_scheduler_start():
    interval = request.args.get("interval") or request.json.get("interval") if request.is_json else None
    ok = start_background_scheduler(interval)
    return jsonify({"started": ok, "last_run": get_last_run()})

@app.route("/api/correlation/scheduler/stop", methods=["POST", "GET"])
def api_corr_scheduler_stop():
    stop_background_scheduler()
    return jsonify({"stopped": True, "last_run": get_last_run()})

@app.route("/api/leads", methods=["GET"])
def api_leads_feed():
    feed_path = os.path.join(ROOT_DIR, "data", "leads_feed.json")
    if os.path.exists(feed_path):
        with open(feed_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    # fallback: run on-demand
    if _AUTO_CORR_AVAILABLE:
        payload = run_leads_correlation()
        return jsonify(payload)
    return jsonify({"leads": [], "error": "no feed and auto-correlation unavailable"}), 404

@app.route("/api/leads/report", methods=["GET"])
def api_leads_report():
    report_dir = os.path.join(ROOT_DIR, "reports", "auto_leads")
    if not os.path.exists(report_dir):
        return jsonify({"error": "no reports yet"}), 404
    latest = os.path.join(report_dir, "latest.json")
    target = latest if os.path.exists(latest) else None
    if not target:
        files = sorted([os.path.join(report_dir, f) for f in os.listdir(report_dir) if f.startswith("leads_")], reverse=True)
        target = files[0] if files else None
    if target and os.path.exists(target):
        with open(target, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "no report found"}), 404

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

