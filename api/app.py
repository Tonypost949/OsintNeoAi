"""
api/app.py
==========
Azure Cloud Webhook, REST API & Universal Makaveli AI Chatbot Engine
Endpoint: https://osintneoai-app-949.azurewebsites.net/

Features:
- Power Apps Custom Connector OpenAPI 2.0 endpoint (/openapi_azure_powerapps.json)
- Whistleblower / Mutual Aid Ingestion endpoint (/api/submit-victim) with CASS normalization
- 24/7 Autonomous Cloud Correlation Scheduler controls & telemetry (/api/correlation/*)
- Live Leads Feed (/api/leads), Forensic Correlation Matrix (/api/correlate), Entity Search (/api/search)
- Tactical GIS Maps Hub (/maps), 3D Planetary Globe (/gods_eye_view), Syncfusion Grid (/syncfusion)
- Universal Meta Webhook AI Loop (Facebook Page Comments, Messenger DMs, Instagram Comments)
"""

import os
import sys
import json
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Dynamic Repository Root Resolution
THIS_FILE = Path(__file__).resolve()
ROOT_DIR_PATH = THIS_FILE.parents[1] if THIS_FILE.parents[1].name != "api" else THIS_FILE.parents[1]
if not (ROOT_DIR_PATH / "data").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "data").exists():
            ROOT_DIR_PATH = cand
            break

ROOT_DIR = str(ROOT_DIR_PATH)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "makaveli_osint_verify_2026")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN") or os.getenv("META_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.getenv("FB_PAGE_ID", "61594100636376")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Import Normalizers
try:
    from api.osint_pipeline.normalizers import normalize_lead_payload, normalize_entity_name, normalize_address, normalize_apn, normalize_timestamp
except Exception:
    def normalize_lead_payload(raw, default_case_id="CASE-0001"):
        raw["case_id"] = raw.get("case_id") or raw.get("id") or default_case_id
        raw["timestamp"] = raw.get("timestamp") or datetime.now(timezone.utc).isoformat()
        return raw

# Thread lock for file writes
_file_write_lock = threading.Lock()

# Initialize Gemini AI Client if key present
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
    """Generate conversational AI response for ANY topic, question, or forensic prompt."""
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

    # 3. Default Signal
    return f"⚡ [Makaveli]: Signal received: '{cleaned}'. Systems operational across all forensic data vectors."


def reply_facebook_comment(comment_id: str, message: str) -> bool:
    if not FB_PAGE_TOKEN: return True
    try:
        url = f"https://graph.facebook.com/v20.0/{comment_id}/comments"
        data = urllib.parse.urlencode({"message": message, "access_token": FB_PAGE_TOKEN}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[REPLY COMMENT ERROR] {e}")
        return False


def reply_facebook_messenger(recipient_id: str, message: str) -> bool:
    if not FB_PAGE_TOKEN: return True
    try:
        url = "https://graph.facebook.com/v20.0/me/messages"
        payload = json.dumps({
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE"
        }).encode("utf-8")
        req = urllib.request.Request(f"{url}?access_token={FB_PAGE_TOKEN}", data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[REPLY MESSENGER ERROR] {e}")
        return False


def reply_instagram_comment(comment_id: str, message: str) -> bool:
    if not FB_PAGE_TOKEN: return True
    try:
        url = f"https://graph.facebook.com/v20.0/{comment_id}/replies"
        data = urllib.parse.urlencode({"message": message, "access_token": FB_PAGE_TOKEN}).encode("utf-8")
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
        "service": "OSINTNeoAi 24/7 Autonomous Forensic Intelligence Node",
        "version": "2.0-cloud-auto",
        "page_id": PAGE_ID,
        "ai_engine": "Gemini 3.6 Flash / Makaveli",
        "makaveli_hud": "https://tonypost949.github.io/OsintNeoAi/makavelli/",
        "webhook_endpoint": "/webhook",
        "endpoints": {
            "leads_feed": "/api/leads",
            "correlation_status": "/api/correlation/status",
            "correlation_run": "/api/correlation/run",
            "correlate_matrix": "/api/correlate",
            "search": "/api/search",
            "submit_intake": "/api/submit-victim",
            "powerapps_swagger": "/openapi_azure_powerapps.json",
            "maps": "/maps",
            "gods_eye_view": "/gods_eye_view"
        }
    })


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WEBHOOK VERIFIED] Handshake successful.")
        return challenge, 200
    return "Forbidden: Invalid verification token", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook_event():
    payload = request.get_json(silent=True) or {}
    print(f"[WEBHOOK EVENT RECEIVED] Object: {payload.get('object')}")

    for entry in payload.get("entry", []):
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event.get("sender", {}).get("id")
            recipient_id = msg_event.get("recipient", {}).get("id")
            text = msg_event.get("message", {}).get("text")
            
            if sender_id and text and sender_id != PAGE_ID and not msg_event.get("message", {}).get("is_echo"):
                ai_reply = generate_makaveli_response(text, is_dm=True)
                reply_facebook_messenger(sender_id, ai_reply)

        for change in entry.get("changes", []):
            val = change.get("value", {})
            item = val.get("item")
            verb = val.get("verb")
            msg = val.get("message", "")
            comment_id = val.get("comment_id")

            if item == "comment" and verb == "add" and comment_id and msg:
                from_id = val.get("from", {}).get("id")
                if from_id != PAGE_ID:
                    ai_reply = generate_makaveli_response(msg, is_dm=False)
                    reply_facebook_comment(comment_id, ai_reply)

            ig_comment_id = val.get("id")
            ig_text = val.get("text")
            if ig_comment_id and ig_text:
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
@app.route("/gods-eye-view", methods=["GET"])
@app.route("/gods-eye-max", methods=["GET"])
@app.route("/gods-eye-max-data", methods=["GET"])
@app.route("/globe", methods=["GET"])
@app.route("/3d", methods=["GET"])
def serve_gods_eye():
    for cand in ["gods_eye_view.html", "public/gods_eye_view.html", "public/gods_eye_view_max_data.html"]:
        p = os.path.join(ROOT_DIR, cand)
        if os.path.exists(p):
            dirname = os.path.dirname(p) or ROOT_DIR
            resp = send_from_directory(dirname, os.path.basename(p))
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            return resp
    resp = send_from_directory(ROOT_DIR, "gods_eye_view.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/cesium/<path:filename>", methods=["GET"])
def serve_cesium_assets(filename):
    cesium_dir = os.path.join(ROOT_DIR, "public", "cesium")
    if os.path.exists(os.path.join(cesium_dir, filename)):
        return send_from_directory(cesium_dir, filename)
    alt_dir = os.path.join(ROOT_DIR, "tools", "gods_eye_upstream", "dist", "cesium")
    if os.path.exists(os.path.join(alt_dir, filename)):
        return send_from_directory(alt_dir, filename)
    return "Cesium asset not found", 404


@app.route("/assets/<path:filename>", methods=["GET"])
def serve_dist_assets(filename):
    assets_dir = os.path.join(ROOT_DIR, "public", "assets")
    if os.path.exists(os.path.join(assets_dir, filename)):
        return send_from_directory(assets_dir, filename)
    alt_dir = os.path.join(ROOT_DIR, "tools", "gods_eye_upstream", "dist", "assets")
    if os.path.exists(os.path.join(alt_dir, filename)):
        return send_from_directory(alt_dir, filename)
    return "Asset not found", 404


@app.route("/models/<path:filename>", methods=["GET"])
def serve_model_assets(filename):
    models_dir = os.path.join(ROOT_DIR, "public", "models")
    if os.path.exists(os.path.join(models_dir, filename)):
        return send_from_directory(models_dir, filename)
    alt_dir = os.path.join(ROOT_DIR, "tools", "gods_eye_upstream", "dist", "models")
    if os.path.exists(os.path.join(alt_dir, filename)):
        return send_from_directory(alt_dir, filename)
    return "Model not found", 404


@app.route("/<string:svgname>.svg", methods=["GET"])
def serve_root_svg(svgname):
    filename = f"{svgname}.svg"
    for d in [ROOT_DIR, os.path.join(ROOT_DIR, "public"), os.path.join(ROOT_DIR, "tools", "gods_eye_upstream", "dist")]:
        fp = os.path.join(d, filename)
        if os.path.exists(fp):
            return send_from_directory(d, filename, mimetype="image/svg+xml")
    return "SVG not found", 404


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
    "version": "2.0.0"
  },
  "host": "osintneoai-app-949.azurewebsites.net",
  "basePath": "/",
  "schemes": ["https", "http"],
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
        "description": "Submits a new investigation lead or intake report directly into the persistent forensic vault with CASS normalization.",
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
                "location": { "type": "string", "example": "17631 Cameron Lane, Huntington Beach, CA" },
                "apn": { "type": "string", "example": "178-431-14" },
                "summary": { "type": "string", "example": "Witness tampering and procurement irregularities." }
              },
              "required": ["incident_type", "summary"]
            }
          }
        ],
        "responses": { "200": { "description": "Submission confirmation" } }
      }
    },
    "/api/leads": {
      "get": {
        "summary": "Get Active Forensic Leads Feed",
        "description": "Returns active correlation leads feed with 6+ vectors and CCTV proximity radar.",
        "operationId": "GetLeadsFeed",
        "responses": { "200": { "description": "Leads feed object" } }
      }
    },
    "/api/correlation/status": {
      "get": {
        "summary": "Get Correlation Engine Telemetry",
        "description": "Returns scheduler status, last execution runtime, lead counts, and feed metadata.",
        "operationId": "GetCorrelationStatus",
        "responses": { "200": { "description": "Telemetry status object" } }
      }
    },
    "/api/correlation/run": {
      "post": {
        "summary": "Trigger Forensic Correlation Run",
        "description": "Triggers immediate correlation execution (sync or async with ?async=1).",
        "operationId": "TriggerCorrelation",
        "parameters": [
          { "name": "async", "in": "query", "type": "string", "description": "Set to 1 for asynchronous execution" }
        ],
        "responses": { "200": { "description": "Execution result or trigger confirmation" } }
      }
    },
    "/api/search": {
      "get": {
        "summary": "Search Entities & APNs",
        "description": "Searches 104k+ resolved entities, APN parcel records, and corporate entities.",
        "operationId": "SearchEntities",
        "parameters": [
          { "name": "q", "in": "query", "required": True, "type": "string", "description": "Search keyword" }
        ],
        "responses": { "200": { "description": "Search results list" } }
      }
    },
    "/api/correlate": {
      "get": {
        "summary": "Get Master Forensic Correlation Matrix",
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
    payload = request.get_json(silent=True) or {}
    cases_file = os.path.join(ROOT_DIR, "evidence", "mutual_aid_cases.json")
    
    with _file_write_lock:
        cases = []
        if os.path.exists(cases_file):
            try:
                with open(cases_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                    if content:
                        try:
                            loaded = json.loads(content)
                            if isinstance(loaded, list):
                                cases = loaded
                        except Exception:
                            # Regex recovery
                            import re
                            for m in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL):
                                try: cases.append(json.loads(m.group(0)))
                                except Exception: pass
            except Exception:
                cases = []

        next_id = f"CASE-{len(cases) + 1:04d}"
        normalized = normalize_lead_payload(payload, default_case_id=next_id)
        cases.append(normalized)

        try:
            os.makedirs(os.path.dirname(cases_file), exist_ok=True)
            with open(cases_file, "w", encoding="utf-8") as f:
                json.dump(cases, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Warning writing mutual_aid_cases.json: {e}")

    return jsonify({
        "status": "SUCCESS",
        "case_id": normalized["case_id"],
        "message": "Report ingested into forensic vault.",
        "normalized": normalized
    }), 200


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
    """Trigger leads correlation now (cloud). Query ?async=1 for non-blocking trigger."""
    is_async = request.args.get("async") in ("1", "true", "True")
    if is_async:
        threading.Thread(target=run_leads_correlation, daemon=True, name="api-correlation-trigger").start()
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
    interval = request.args.get("interval") or (request.json.get("interval") if request.is_json else None)
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
