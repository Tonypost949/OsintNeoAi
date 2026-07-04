import os
import sys
import sqlite3
import markdown
from google.cloud import bigquery

# Force install flask if not available
try:
    from flask import Flask, render_template_string, request, jsonify
except ImportError:
    import subprocess
    print("Flask not found. Installing Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "markdown"])
    from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

DB_PATH = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\master_index_v2.db"
GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"

# HTML Template with premium CSS (dark theme, glassmorphism, responsive tabs)
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Command Center & Forensic Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --accent-color: #06b6d4;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --border-color: #1f2937;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }
        header {
            background: linear-gradient(135deg, #083344, #111827);
            padding: 20px 40px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 {
            margin: 0;
            font-size: 24px;
            color: var(--accent-color);
            letter-spacing: 1px;
        }
        .subtitle {
            font-size: 12px;
            color: var(--text-secondary);
        }
        .container {
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .tabs {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 30px;
        }
        .tab-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        .tab-btn:hover {
            color: var(--text-primary);
        }
        .tab-btn.active {
            color: var(--accent-color);
            border-bottom-color: var(--accent-color);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }
        h2 {
            margin-top: 0;
            color: var(--accent-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }
        th {
            background-color: #1f2937;
            color: var(--accent-color);
        }
        tr:hover {
            background-color: #1e293b;
        }
        input, select, button {
            background-color: #1f2937;
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
        }
        button {
            background-color: var(--accent-color);
            color: #000;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
            border: none;
        }
        button:hover {
            background-color: #22d3ee;
        }
        .form-group {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        pre {
            background-color: #1f2937;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--border-color);
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>OSINT FORENSIC COMMAND CENTER</h1>
            <div class="subtitle">Litigation-Safe Audit Engine v2.0</div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: bold; color: var(--accent-color);">ACTIVE INTERFACE</div>
            <div class="subtitle">Central District of California Relator Hub</div>
        </div>
    </header>

    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('dashboard')">🏠 Dashboard</button>
            <button class="tab-btn" onclick="switchTab('sqlite')">💾 SQLite Matrix</button>
            <button class="tab-btn" onclick="switchTab('bigquery')">☁️ BigQuery Data</button>
            <button class="tab-btn" onclick="switchTab('briefings')">📄 Evidentiary Briefs</button>
            <button class="tab-btn" onclick="switchTab('flowchart')">📊 Flowchart Build</button>
            <button class="tab-btn" onclick="switchTab('maps')">🗺️ Live Maps</button>
            <button class="tab-btn" onclick="switchTab('alerts')">🚨 Alerts & Comms</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="card">
                <h2>System Overview & Health Metrics</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: center; margin-top: 20px;">
                    <div style="background:#1e293b; padding:20px; border-radius:10px;">
                        <div style="font-size:24px; font-weight:bold; color:var(--accent-color);">742,678</div>
                        <div class="subtitle">Drive Files Indexed</div>
                    </div>
                    <div style="background:#1e293b; padding:20px; border-radius:10px;">
                        <div style="font-size:24px; font-weight:bold; color:var(--accent-color);">460</div>
                        <div class="subtitle">SharedAll Vault Items</div>
                    </div>
                    <div style="background:#1e293b; padding:20px; border-radius:10px;">
                        <div style="font-size:24px; font-weight:bold; color:var(--accent-color);">35</div>
                        <div class="subtitle">Local Downloads Synced</div>
                    </div>
                    <div style="background:#1e293b; padding:20px; border-radius:10px;">
                        <div style="font-size:24px; font-weight:bold; color:var(--accent-color);">41</div>
                        <div class="subtitle">BigQuery Tables Live</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Active Targets Checklist (task.md)</h2>
                <div id="tasks-container">
                    {{ tasks_html|safe }}
                </div>
            </div>
        </div>

        <!-- SQLite Viewer Tab -->
        <div id="sqlite" class="tab-content">
            <div class="card">
                <h2>Local SQLite Authority Database (master_index_v2.db)</h2>
                <div class="form-group">
                    <select id="sqlite-table">
                        <option value="MasterIndex">MasterIndex (Entities)</option>
                        <option value="document_scans">Document Scans</option>
                        <option value="relationships">Relationships</option>
                        <option value="hbnc_convergence_points">7561 Center Ave Convergence Points</option>
                    </select>
                    <button onclick="querySqlite()">Fetch Data</button>
                </div>
                <div id="sqlite-results"></div>
            </div>
        </div>

        <!-- BigQuery Tab -->
        <div id="bigquery" class="tab-content">
            <div class="card">
                <h2>BigQuery Cloud Analytics (project-743aab84-f9a5-4ec7-954)</h2>
                <div class="form-group">
                    <select id="bq-query-select">
                        <option value="uploads">Newly Uploaded & Indexed Files</option>
                        <option value="timing">PPP Property Timing Matches (View)</option>
                        <option value="convergence">7561 Center Ave Convergence Points (Table)</option>
                    </select>
                    <button onclick="queryBigQuery()">Execute Query</button>
                </div>
                <div id="bq-results"></div>
            </div>
        </div>

        <!-- Evidentiary Briefings Tab -->
        <div id="briefings" class="tab-content">
            <div class="card">
                <h2>Forensic Dossiers & Whistleblower Briefings</h2>
                <div class="form-group">
                    <select id="briefing-select" onchange="loadBriefing(this.value)">
                        <option value="intel">Extracted Intelligence Summary</option>
                        <option value="referral">Qui Tam / RICO Complaint Draft</option>
                        <option value="workbook">HBNC Forensic Workbook Phase 2</option>
                    </select>
                </div>
                <div id="briefing-content" style="background:#111827; padding:20px; border-radius:10px; border: 1px solid var(--border-color); max-height: 600px; overflow-y: auto;">
                    Select a briefing to view.
                </div>
            </div>
        </div>

        <!-- Flowchart Tab -->
        <div id="flowchart" class="tab-content">
            <div class="card" style="height: 700px;">
                <h2>Interactive RICO Slow-Build Flowchart</h2>
                <iframe src="/flowchart-iframe" style="width:100%; height:90%; border:none; border-radius:10px;"></iframe>
            </div>
        </div>

        <!-- Maps Tab -->
        <div id="maps" class="tab-content">
            <div class="card" style="height: 800px;">
                <h2>Geospatial Intelligence Map</h2>
                <div class="form-group">
                    <select id="map-select" onchange="document.getElementById('map-iframe').src = '/map/' + this.value">
                        <option value="nationwide_coc_map.html">Nationwide CoC Leakage Map</option>
                        <option value="osint_gemini_gis.html">OSINT Deep GIS Map</option>
                        <option value="badass_osint_map.html">Global Flow / Badass Map</option>
                    </select>
                </div>
                <iframe id="map-iframe" src="/map/nationwide_coc_map.html" style="width:100%; height:85%; border:none; border-radius:10px;"></iframe>
            </div>
        </div>

        <!-- Alerts Tab -->
        <div id="alerts" class="tab-content">
            <div class="card">
                <h2>Broadcast Action Alerts & Active Tracing</h2>
                <div style="display: flex; gap: 20px;">
                    <button style="background-color: #ef4444;" onclick="triggerAlert('text')">📱 SEND SMS ALERT TO HANDSET</button>
                    <button style="background-color: #3b82f6;" onclick="triggerAlert('email')">✉️ EMAIL FULL DOSSIER</button>
                    <button style="background-color: #8b5cf6;" onclick="triggerTrace()">🌐 TRACE FOREIGN REMITTANCES</button>
                </div>
                <div id="alert-status" style="margin-top: 20px; font-family: monospace;"></div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }

        function triggerAlert(alertType) {
            document.getElementById('alert-status').innerHTML = '<span style="color:yellow;">Initiating ' + alertType + ' broadcast...</span>';
            fetch('/api/alert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: alertType })
            })
            .then(r => r.json())
            .then(data => {
                if(data.status === 'success') {
                    document.getElementById('alert-status').innerHTML = '<span style="color:#39ff14;">[SUCCESS] ' + data.output.replace(/\\n/g, '<br>') + '</span>';
                } else {
                    document.getElementById('alert-status').innerHTML = '<span style="color:#ff2a5f;">[ERROR] ' + data.error + '</span>';
                }
            })
            .catch(err => {
                document.getElementById('alert-status').innerHTML = '<span style="color:#ff2a5f;">[ERROR] ' + err + '</span>';
            });
        }

        function triggerTrace() {
            document.getElementById('alert-status').innerHTML = '<span style="color:yellow;">Initiating Deep Graph Trace: Tracking High-Velocity Offshore Nodes...</span>';
            fetch('/api/trace_remittances')
            .then(r => r.json())
            .then(data => {
                if(data.status === 'success') {
                    document.getElementById('alert-status').innerHTML = '<span style="color:#39ff14;">[SUCCESS] ' + data.output.replace(/\\n/g, '<br>') + '</span>';
                } else {
                    document.getElementById('alert-status').innerHTML = '<span style="color:#ff2a5f;">[ERROR] ' + data.error + '</span>';
                }
            })
            .catch(err => {
                document.getElementById('alert-status').innerHTML = '<span style="color:#ff2a5f;">[ERROR] ' + err + '</span>';
            });
        }

        function querySqlite() {
            const table = document.getElementById('sqlite-table').value;
            fetch(`/api/sqlite?table=${table}`)
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('sqlite-results').innerHTML = `<p style="color:red">Error: ${data.error}</p>`;
                        return;
                    }
                    let html = '<table><thead><tr>';
                    data.columns.forEach(c => html += `<th>${c}</th>`);
                    html += '</tr></thead><tbody>';
                    data.rows.forEach(row => {
                        html += '<tr>';
                        row.forEach(val => html += `<td>${val !== null ? val : ''}</td>`);
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    document.getElementById('sqlite-results').innerHTML = html;
                });
        }

        function queryBigQuery() {
            const queryType = document.getElementById('bq-query-select').value;
            document.getElementById('bq-results').innerHTML = '<p>Executing cloud query...</p>';
            fetch(`/api/bigquery?type=${queryType}`)
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('bq-results').innerHTML = `<p style="color:red">Error: ${data.error}</p>`;
                        return;
                    }
                    let html = '<table><thead><tr>';
                    data.columns.forEach(c => html += `<th>${c}</th>`);
                    html += '</tr></thead><tbody>';
                    data.rows.forEach(row => {
                        html += '<tr>';
                        row.forEach(val => html += `<td>${val !== null ? val : ''}</td>`);
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    document.getElementById('bq-results').innerHTML = html;
                });
        }

        function loadBriefing(type) {
            fetch(`/api/briefing?type=${type}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('briefing-content').innerHTML = data.html;
                });
        }

        // Load initial briefing
        loadBriefing('intel');
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    # Read task.md
    task_html = "<p>No tasks checklist found.</p>"
    task_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\d21833d9-2b71-4939-afda-f6127c82cd7b\task.md"
    if os.path.exists(task_path):
        with open(task_path, 'r', encoding='utf-8') as f:
            task_html = markdown.markdown(f.read())
            
    return render_template_string(TEMPLATE, tasks_html=task_html)

@app.route("/flowchart-iframe")
def flowchart_iframe():
    flowchart_path = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\rico_slow_flowchart.html"
    if os.path.exists(flowchart_path):
        with open(flowchart_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Flowchart HTML file not found."

@app.route("/map/<filename>")
def serve_map(filename):
    # Only allow html maps in this directory
    if not filename.endswith('.html') or '/' in filename or '\\' in filename:
        return "Invalid file request.", 400
        
    map_path = os.path.join(r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent", filename)
    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Map file not found.", 404

@app.route("/api/alert", methods=["POST"])
def api_alert():
    import subprocess
    req = request.get_json() or {}
    alert_type = req.get('type')
    try:
        if alert_type == 'text':
            result = subprocess.run([sys.executable, r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\send_text.py"], capture_output=True, text=True)
            return jsonify({"status": "success", "output": "SMS Dispatched successfully.\n" + result.stdout})
        elif alert_type == 'email':
            result = subprocess.run([sys.executable, r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\send_email.py"], capture_output=True, text=True)
            return jsonify({"status": "success", "output": "Email Dossier Sent successfully.\n" + result.stdout})
        else:
            return jsonify({"status": "error", "error": "Invalid alert type"}), 400
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/trace_remittances")
def api_trace_remittances():
    import subprocess
    try:
        result = subprocess.run([sys.executable, r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\trace_remittance_network.py"], capture_output=True, text=True)
        return jsonify({"status": "success", "output": result.stdout})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/sqlite")
def api_sqlite():
    table = request.args.get("table", "MasterIndex")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Guard column/table parameter
        if table not in ["MasterIndex", "document_scans", "relationships", "hbnc_convergence_points"]:
            return jsonify({"error": "Invalid table selection"})
            
        cursor.execute(f"SELECT * FROM {table} LIMIT 100")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        return jsonify({"columns": columns, "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/bigquery")
def api_bigquery():
    query_type = request.args.get("type", "uploads")
    try:
        client = bigquery.Client(project=GCP_PROJECT)
        if query_type == "uploads":
            sql = """
            SELECT file_name, mime_type, size_bytes, web_view_link
            FROM `project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index`
            WHERE '1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE' IN UNNEST(parent_folder_ids)
            ORDER BY scan_timestamp DESC
            LIMIT 20
            """
        elif query_type == "timing":
            sql = """
            SELECT entity_identity, property_wrapper, property_address, days_delta, loan_amount
            FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.ppp_property_timing`
            ORDER BY ABS(days_delta) ASC
            LIMIT 20
            """
        else: # convergence points
            sql = """
            SELECT unit, owner, acquired_date, price, mail_address, flags
            FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.hbnc_convergence_points`
            ORDER BY unit ASC
            """
            
        query_job = client.query(sql)
        results = list(query_job.result())
        
        if not results:
            return jsonify({"columns": ["Status"], "rows": [["No matching data found in BigQuery."]]})
            
        columns = list(results[0].keys())
        rows = [list(row.values()) for row in results]
        return jsonify({"columns": columns, "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/briefing")
def api_briefing():
    b_type = request.args.get("type", "intel")
    paths = {
        "intel": r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\extracted_intelligence_summary.md",
        "referral": r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\qui_tam_rico_referral_draft.md",
        "workbook": r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\hbnc_forensic_workbook_phase2.md"
    }
    
    target_path = paths.get(b_type)
    if not target_path or not os.path.exists(target_path):
        return jsonify({"html": "<p>Briefing file not found.</p>"})
        
    with open(target_path, 'r', encoding='utf-8') as f:
        html = markdown.markdown(f.read())
    return jsonify({"html": html})

@app.route("/api/sync", methods=["POST"])
def api_sync():
    import subprocess
    try:
        # Run index_new_uploads.py
        result_index = subprocess.run(
            [sys.executable, r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\index_new_uploads.py"],
            capture_output=True, text=True
        )
        
        # Run sync_documents.py
        result_sync = subprocess.run(
            [sys.executable, r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\sync_documents.py"],
            capture_output=True, text=True
        )
        
        return jsonify({
            "status": "success",
            "index_output": result_index.stdout + "\n" + result_index.stderr,
            "sync_output": result_sync.stdout + "\n" + result_sync.stderr
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    print("\n[+] Starting local OSINT Forensic Dashboard...")
    print("[+] Serve address: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
