import json, os, sys, io, csv, uuid
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).parent / "osint_pipeline"))

app = Flask(__name__, static_folder=None)
START_TIME = datetime.now(timezone.utc)
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

GCP_PROJECT = os.getenv("GCP_PROJECT", "project-743aab84-f9a5-4ec7-954")

# ── Vertex AI Client ───────────────────────────────────────────
def get_ai_client():
    import google.auth
    from vertexai import init
    from vertexai.generative_models import GenerativeModel
    credentials, _ = google.auth.default()
    init(credentials=credentials, project=GCP_PROJECT, location="us-central1")
    return GenerativeModel("gemini-2.0-flash-001")

# ── Frontend (SPA) ─────────────────────────────────────────────
FRONTEND_HTML = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

@app.route("/")
def index():
    return FRONTEND_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/assets/<path:path>")
def static_assets(path):
    return send_from_directory(str(Path(__file__).parent / "templates"), path)

# ── AI Chat ────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400
    try:
        client = get_ai_client()
        resp = client.generate_content(
            f"You are OsintNeoAi, a forensic OSINT analysis assistant. "
            f"The user's GCP project is {GCP_PROJECT}. "
            f"Answer clearly and concisely. User: {message}"
        )
        return jsonify({"response": resp.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400
    def generate():
        try:
            client = get_ai_client()
            resp = client.generate_content(
                f"You are OsintNeoAi, a forensic OSINT analysis assistant. "
                f"User: {message}",
                stream=True
            )
            for chunk in resp:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
    return app.response_class(generate(), mimetype="text/event-stream")

# ── File Upload ────────────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    uid = str(uuid.uuid4())[:8]
    path = UPLOAD_DIR / f"{uid}_{f.filename}"
    f.save(str(path))
    text = path.read_text(encoding="utf-8", errors="replace")[:50000]
    client = get_ai_client()
    resp = client.generate_content(
        f"Analyze this uploaded file ({f.filename}) for forensic intelligence. "
        f"Extract names, entities, addresses, and patterns:\n\n{text}"
    )
    return jsonify({"status": "ok", "file": f.filename, "analysis": resp.text})

# ── BigQuery Proxy ─────────────────────────────────────────────
@app.route("/api/bq/query", methods=["POST"])
def bq_query():
    data = request.get_json(silent=True) or {}
    sql = data.get("sql", "").strip()
    if not sql:
        return jsonify({"error": "SQL is required"}), 400
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=GCP_PROJECT)
        job = client.query(sql)
        rows = [dict(r) for r in job.result()]
        return jsonify({"rows": rows, "total": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bq/tables", methods=["GET"])
def bq_tables():
    dataset = request.args.get("dataset", "")
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=GCP_PROJECT)
        if dataset:
            tables = list(client.list_tables(f"{GCP_PROJECT}.{dataset}"))
            return jsonify({"tables": [t.table_id for t in tables]})
        datasets = list(client.list_datasets())
        return jsonify({"datasets": [d.dataset_id for d in datasets]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Pipeline ───────────────────────────────────────────────────
@app.route("/api/pipeline/run", methods=["POST"])
def run_pipeline():
    from osint_pipeline.watcher import run_pipeline as rp
    try:
        rp()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pipeline/resolve", methods=["POST"])
def resolve_pipeline():
    from osint_pipeline.watcher_v2 import run_phase2
    try:
        run_phase2()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Status ─────────────────────────────────────────────────────
@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok", "service": "OsintNeoAi", "version": "2.0.0",
        "uptime": str(datetime.now(timezone.utc) - START_TIME),
        "project": GCP_PROJECT
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
