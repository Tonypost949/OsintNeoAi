"""
public_app.py — OSINTNeoAi: Public OSINT Investigation Platform
======================================================================
Flask backend for the public-facing OSINT dashboard.
Separate from app.py (private forensic dashboard).

Run: python public_app.py
Access: http://127.0.0.1:8080
"""

import os
import sys
import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, render_template, request, jsonify, send_from_directory

from entity_extractor import extract_from_file, build_search_queries
from osint_engine import run_osint_search

# ============================================================================
#  CONFIG
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "cases.db")
UPLOAD_DIR = os.path.join(SCRIPT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__,
            template_folder=os.path.join(SCRIPT_DIR, "templates"),
            static_folder=os.path.join(SCRIPT_DIR, "static"))

# ============================================================================
#  DATABASE SETUP
# ============================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT,
            description TEXT,
            status TEXT DEFAULT 'active',
            interval_minutes INTEGER DEFAULT 20,
            entities TEXT,
            created_at TEXT,
            last_run TEXT
        );

        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            dedup_id TEXT,
            source TEXT,
            headline TEXT,
            description TEXT,
            url TEXT,
            tags TEXT,
            is_smoking_gun INTEGER DEFAULT 0,
            found_at TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id),
            UNIQUE(case_id, dedup_id)
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            action TEXT,
            details TEXT,
            timestamp TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        );

        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            filename TEXT,
            extracted_text TEXT,
            entities_json TEXT,
            uploaded_at TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        );
    """)
    conn.commit()
    conn.close()


# ============================================================================
#  HELPERS
# ============================================================================
def slugify(text):
    import re
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
    slug = re.sub(r'[\s-]+', '_', slug).strip('_')
    return slug[:50]


def log_activity(conn, case_id, action, details=""):
    conn.execute(
        "INSERT INTO activity_log (case_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
        (case_id, action, details, datetime.utcnow().isoformat() + 'Z')
    )
    conn.commit()


def case_to_dict(row):
    """Convert a sqlite3.Row to a regular dict."""
    d = dict(row)
    # Add computed counts
    conn = get_db()
    counts = conn.execute(
        "SELECT COUNT(*) as total, SUM(CASE WHEN is_smoking_gun = 1 THEN 1 ELSE 0 END) as guns "
        "FROM findings WHERE case_id = ?", (d['id'],)
    ).fetchone()
    d['finding_count'] = counts['total'] or 0
    d['smoking_gun_count'] = counts['guns'] or 0
    conn.close()
    return d


# ============================================================================
#  ROUTES — Pages
# ============================================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================================
#  ROUTES — Cases API
# ============================================================================
@app.route("/api/cases", methods=["GET"])
def list_cases():
    conn = get_db()
    rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    cases = [case_to_dict(r) for r in rows]
    return jsonify({"cases": cases})


@app.route("/api/cases", methods=["POST"])
def create_case():
    data = request.get_json() or {}
    name = data.get("name", "Untitled Investigation").strip()
    description = data.get("description", "").strip()
    entities = data.get("entities")

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO cases (name, slug, description, status, interval_minutes, entities, created_at) "
        "VALUES (?, ?, ?, 'active', 20, ?, ?)",
        (name, slugify(name), description, json.dumps(entities) if entities else None,
         datetime.utcnow().isoformat() + 'Z')
    )
    case_id = cursor.lastrowid
    log_activity(conn, case_id, "Case created", f"Investigation '{name}' initialized.")
    conn.close()

    return jsonify({"case_id": case_id, "status": "created"})


@app.route("/api/cases/<int:case_id>", methods=["GET"])
def get_case(case_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Case not found"}), 404
    return jsonify({"case": case_to_dict(row)})


# ============================================================================
#  ROUTES — Findings API
# ============================================================================
@app.route("/api/cases/<int:case_id>/findings", methods=["GET"])
def get_findings(case_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM findings WHERE case_id = ? ORDER BY is_smoking_gun DESC, found_at DESC",
        (case_id,)
    ).fetchall()
    conn.close()

    findings = []
    for r in rows:
        d = dict(r)
        # Parse tags JSON
        try:
            d['tags'] = json.loads(d['tags']) if d['tags'] else []
        except (json.JSONDecodeError, TypeError):
            d['tags'] = []
        d['is_smoking_gun'] = bool(d.get('is_smoking_gun'))
        findings.append(d)

    return jsonify({"findings": findings})


# ============================================================================
#  ROUTES — Activity API
# ============================================================================
@app.route("/api/cases/<int:case_id>/activity", methods=["GET"])
def get_activity(case_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM activity_log WHERE case_id = ? ORDER BY timestamp DESC LIMIT 50",
        (case_id,)
    ).fetchall()
    conn.close()
    return jsonify({"activity": [dict(r) for r in rows]})


# ============================================================================
#  ROUTES — Run Scan
# ============================================================================
@app.route("/api/cases/<int:case_id>/run", methods=["POST"])
def run_scan(case_id):
    conn = get_db()
    case_row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not case_row:
        conn.close()
        return jsonify({"error": "Case not found"}), 404

    case = dict(case_row)
    log_activity(conn, case_id, "Manual scan triggered", "User initiated OSINT sweep.")

    # Build search queries from case data
    queries = []

    # From entities
    entities = {}
    if case.get('entities'):
        try:
            entities = json.loads(case['entities'])
        except (json.JSONDecodeError, TypeError):
            pass

    if entities:
        queries = build_search_queries(entities)
    
    # From case name and description
    if case.get('name'):
        queries.insert(0, case['name'])
    if case.get('description'):
        # Extract key phrases from description
        desc_words = case['description'].split()
        if len(desc_words) > 3:
            queries.append(' '.join(desc_words[:8]))

    if not queries:
        queries = [case.get('name', 'investigation')]

    # Limit to top 5 queries to avoid rate limits
    queries = queries[:5]

    log_activity(conn, case_id, "Searching", f"Querying {len(queries)} search terms across Google News, Bing News, Data.gov")

    # Run the OSINT search
    findings = run_osint_search(queries)

    # Insert new findings (skip duplicates)
    new_count = 0
    gun_count = 0
    for f in findings:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO findings "
                "(case_id, dedup_id, source, headline, description, url, tags, is_smoking_gun, found_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (case_id, f['dedup_id'], f['source'], f['headline'],
                 f['description'], f['url'], json.dumps(f['tags']),
                 1 if f['is_smoking_gun'] else 0, f['found_at'])
            )
            if conn.total_changes:
                new_count += 1
                if f['is_smoking_gun']:
                    gun_count += 1
        except sqlite3.IntegrityError:
            pass  # Duplicate, skip

    # Update last_run timestamp
    conn.execute("UPDATE cases SET last_run = ? WHERE id = ?",
                 (datetime.utcnow().isoformat() + 'Z', case_id))
    
    log_activity(conn, case_id, "Scan complete",
                 f"Found {new_count} new findings ({gun_count} smoking guns) from {len(queries)} queries.")
    conn.commit()
    conn.close()

    return jsonify({
        "status": "complete",
        "new_findings": new_count,
        "smoking_guns": gun_count,
        "queries_run": len(queries)
    })


# ============================================================================
#  ROUTES — Pause / Resume
# ============================================================================
@app.route("/api/cases/<int:case_id>/pause", methods=["POST"])
def toggle_pause(case_id):
    conn = get_db()
    row = conn.execute("SELECT status FROM cases WHERE id = ?", (case_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Case not found"}), 404

    new_status = 'paused' if row['status'] == 'active' else 'active'
    conn.execute("UPDATE cases SET status = ? WHERE id = ?", (new_status, case_id))
    log_activity(conn, case_id,
                 "Paused" if new_status == 'paused' else "Resumed",
                 f"Auto-scanning {'paused' if new_status == 'paused' else 'resumed'}.")
    conn.commit()
    conn.close()
    return jsonify({"status": new_status})


# ============================================================================
#  ROUTES — File Upload
# ============================================================================
@app.route("/api/upload", methods=["POST"])
def upload_dossier():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Validate extension
    allowed = {'.pdf', '.docx', '.md', '.txt'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({"error": f"Unsupported file type: {ext}. Use: {', '.join(allowed)}"}), 400

    # Save file
    safe_name = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    file.save(filepath)

    # Extract entities
    entities = extract_from_file(filepath)
    entity_count = sum(len(v) for v in entities.values())

    # Create case from dossier
    case_name = os.path.splitext(file.filename)[0].replace('_', ' ').replace('-', ' ').title()
    
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO cases (name, slug, description, status, interval_minutes, entities, created_at) "
        "VALUES (?, ?, ?, 'active', 20, ?, ?)",
        (case_name, slugify(case_name),
         f"Investigation created from uploaded dossier: {file.filename}",
         json.dumps(entities),
         datetime.utcnow().isoformat() + 'Z')
    )
    case_id = cursor.lastrowid

    # Save upload record
    conn.execute(
        "INSERT INTO uploads (case_id, filename, entities_json, uploaded_at) VALUES (?, ?, ?, ?)",
        (case_id, file.filename, json.dumps(entities), datetime.utcnow().isoformat() + 'Z')
    )

    log_activity(conn, case_id, "Dossier uploaded",
                 f"File '{file.filename}' processed. {entity_count} entities extracted.")

    # Log extracted entities
    if entities.get('names'):
        log_activity(conn, case_id, "Entities: Names", ', '.join(entities['names'][:10]))
    if entities.get('organizations'):
        log_activity(conn, case_id, "Entities: Organizations", ', '.join(entities['organizations'][:5]))
    if entities.get('case_numbers'):
        log_activity(conn, case_id, "Entities: Case Numbers", ', '.join(entities['case_numbers']))
    if entities.get('amounts'):
        log_activity(conn, case_id, "Entities: Dollar Amounts", ', '.join(entities['amounts'][:10]))

    conn.commit()
    conn.close()

    return jsonify({
        "case_id": case_id,
        "case_name": case_name,
        "entity_count": entity_count,
        "entities": entities,
    })


# ============================================================================
#  ROUTES — Manual Search
# ============================================================================
@app.route("/api/search", methods=["POST"])
def manual_search():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    findings = run_osint_search([query])
    return jsonify({"findings": findings, "count": len(findings)})


# ============================================================================
#  BACKGROUND SCANNER THREAD
# ============================================================================
def background_scanner():
    """
    Background thread that auto-scans active cases at their configured intervals.
    Runs continuously alongside the Flask server.
    """
    print("[SCANNER] Background OSINT scanner started.")
    while True:
        try:
            conn = get_db()
            active_cases = conn.execute(
                "SELECT * FROM cases WHERE status = 'active'"
            ).fetchall()
            conn.close()

            now = datetime.utcnow()

            for case_row in active_cases:
                case = dict(case_row)
                interval = case.get('interval_minutes', 20)
                last_run = case.get('last_run')

                # Check if it's time to run
                should_run = False
                if not last_run:
                    should_run = True
                else:
                    try:
                        last_dt = datetime.fromisoformat(last_run.replace('Z', ''))
                        if now - last_dt >= timedelta(minutes=interval):
                            should_run = True
                    except (ValueError, AttributeError):
                        should_run = True

                if should_run:
                    case_id = case['id']
                    print(f"[SCANNER] Auto-scanning case {case_id}: {case.get('name', '?')}")

                    # Build queries
                    queries = []
                    entities = {}
                    if case.get('entities'):
                        try:
                            entities = json.loads(case['entities'])
                        except (json.JSONDecodeError, TypeError):
                            pass
                    if entities:
                        queries = build_search_queries(entities)
                    if case.get('name'):
                        queries.insert(0, case['name'])
                    queries = queries[:5]

                    if not queries:
                        continue

                    # Run search
                    findings = run_osint_search(queries)

                    # Insert findings
                    conn = get_db()
                    new_count = 0
                    gun_count = 0
                    for f in findings:
                        try:
                            conn.execute(
                                "INSERT OR IGNORE INTO findings "
                                "(case_id, dedup_id, source, headline, description, url, tags, is_smoking_gun, found_at) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (case_id, f['dedup_id'], f['source'], f['headline'],
                                 f['description'], f['url'], json.dumps(f['tags']),
                                 1 if f['is_smoking_gun'] else 0, f['found_at'])
                            )
                            new_count += 1
                            if f['is_smoking_gun']:
                                gun_count += 1
                        except sqlite3.IntegrityError:
                            pass

                    conn.execute("UPDATE cases SET last_run = ? WHERE id = ?",
                                 (now.isoformat() + 'Z', case_id))
                    log_activity(conn, case_id, "Auto-scan complete",
                                 f"{new_count} new findings ({gun_count} smoking guns)")
                    conn.commit()
                    conn.close()

                    print(f"[SCANNER] Case {case_id}: {new_count} new findings, {gun_count} smoking guns")

        except Exception as e:
            print(f"[SCANNER] Error: {e}")

        # Sleep 60 seconds between scan cycles
        time.sleep(60)


# ============================================================================
#  MAIN
# ============================================================================
if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("  ⚡ OSINTNeoAi — Public OSINT Investigation Platform")
    print("  Serve address: http://127.0.0.1:8080")
    print("=" * 60)

    # Start background scanner in a daemon thread
    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()

    app.run(host="127.0.0.1", port=8080, debug=False)
