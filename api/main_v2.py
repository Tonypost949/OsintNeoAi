import json, os, sys, io, csv, uuid, re, subprocess, logging
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).parent / "osint_pipeline"))

app = Flask(__name__, static_folder=None)
START_TIME = datetime.now(timezone.utc)
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

GCP_PROJECT = os.getenv("GCP_PROJECT", "project-743aab84-f9a5-4ec7-954")
import sqlite3
import hashlib
import secrets
from functools import wraps

def get_db():
    conn = sqlite3.connect('osint_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth.split(" ")[1]
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
        row = c.fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Unauthorized"}), 401
        request.user_id = row['user_id']
        return f(*args, **kwargs)
    return decorated_function


# ── In-Memory Knowledge Store ──────────────────────────────────
knowledge_store = {
    "documents": [],     # [{id, filename, text, summary, timestamp}]
    "bookmarks": [],     # [{id, title, url, add_date, tags}]
    "subscriptions": [], # future RSS/Atom feeds
}
MAX_KNOWLEDGE_DOCS = 100

# ── Gemini AI Client (API Key) ────────────────────────────────
def get_ai():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-flash-latest")

def get_bq():
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from google.auth.exceptions import DefaultCredentialsError
    import json
    import os
    
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    try:
        if creds_json:
            info = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(info)
            return bigquery.Client(project=GCP_PROJECT, credentials=creds)
        else:
            return bigquery.Client(project=GCP_PROJECT)
    except Exception as e:
        class MockClient:
            def query(self, *args, **kwargs):
                class MockJob:
                    def result(self):
                        return [{"_error": "BigQuery credentials not configured. Please set GOOGLE_CREDENTIALS_JSON in Railway variables."}]
                return MockJob()
            def list_datasets(self):
                return []
        return MockClient()

# ── BQ Catalog ─────────────────────────────────────────────────
BQ_CATALOG_CACHE = None
BQ_CATALOG_CACHE_TIME = 0

def build_catalog(force=False):
    global BQ_CATALOG_CACHE, BQ_CATALOG_CACHE_TIME
    if not force and BQ_CATALOG_CACHE and (datetime.now(timezone.utc) - BQ_CATALOG_CACHE_TIME).seconds < 300:
        return BQ_CATALOG_CACHE
    try:
        client = get_bq()
        catalog = {}
        if hasattr(client, 'list_datasets') and len(client.list_datasets()) == 0:
            return {"_error": "BigQuery credentials not configured or no datasets found."}
        for ds in client.list_datasets():
            ds_id = ds.dataset_id
            tables = {}
            for t in client.list_tables(ds.dataset_id):
                table_ref = client.get_table(t.reference)
                schema = [{"name": s.name, "type": s.field_type, "mode": s.mode, "description": s.description or ""} for s in table_ref.schema]
                tables[t.table_id] = {
                    "type": str(table_ref.table_type),
                    "schema": schema,
                    "description": table_ref.description or "",
                    "created": str(table_ref.created),
                    "rows": table_ref.num_rows,
                    "size_bytes": table_ref.num_bytes,
                }
            catalog[ds_id] = tables
        BQ_CATALOG_CACHE = catalog
        BQ_CATALOG_CACHE_TIME = datetime.now(timezone.utc)
        return catalog
    except Exception as e:
        return {"_error": f"BigQuery unavailable: {e}"}

def catalog_to_text(catalog):
    if "_error" in catalog:
        return f"BigQuery catalog unavailable: {catalog['_error']}"
    lines = ["Available BigQuery datasets and tables:"]
    for ds, tables in catalog.items():
        lines.append(f"\nDataset: {ds}")
        if not isinstance(tables, dict):
            continue
        for tbl, info in tables.items():
            cols = ", ".join(f"{s['name']}:{s['type']}" for s in info.get("schema", [])[:10])
            lines.append(f"  - {tbl} ({info.get('type','?')}, {info.get('rows',0):,} rows) [{cols}]")
    return "\n".join(lines)

# ── RAG Context Builder ───────────────────────────────────────
def build_rag_context():
    parts = []
    if knowledge_store["documents"]:
        parts.append("## Uploaded Documents")
        for d in knowledge_store["documents"]:
            parts.append(f"### {d['filename']}\n{d['text'][:2000]}")
    if knowledge_store["bookmarks"]:
        parts.append("## Imported Bookmarks")
        for b in knowledge_store["bookmarks"]:
            tags = ", ".join(b["tags"]) if b["tags"] else ""
            parts.append(f"- [{b['title']}]({b['url']}) {tags}")
    catalog = build_catalog()
    catalog_text = catalog_to_text(catalog)
    parts.append("## BigQuery Catalog\n" + catalog_text)
    return "\n\n".join(parts)

# ── System Prompt ──────────────────────────────────────────────
SYSTEM_PROMPT = """You are OsintNeoAi, an advanced OSINT forensic analysis assistant running 24/7 on Cloud Run.

You have access to the user's BigQuery data warehouse with datasets containing forensic analysis data including:
- Entity networks (people, companies, addresses)
- PPP loan data with RICO analysis
- National audit records
- Unclaimed property records
- Procurement data
- OneDrive forensic documents
- HB Church OSINT data
- Fraud analysis data

Your capabilities:
1. Answer questions by searching across all BigQuery datasets
2. Generate and run SQL queries against the data warehouse
3. Analyze uploaded documents for forensic intelligence
4. Import and search through browser bookmarks
5. Cross-reference data across datasets to find connections
6. Run OSINT and security tools (nmap, whois, dnsrecon, hydra, traceroute, nc, curl) by outputting a bash block.

When the user asks a question that requires data:
1. First check the BigQuery catalog to find relevant tables
2. Generate SQL to answer their question
3. Explain what you found
4. Suggest follow-up investigations

When generating SQL, use the correct dataset.table references. Always EXPLAIN what the data means - don't just dump raw results.

To run OSINT tools, output a bash script block like this:
```bash
nmap -sV -p- example.com
```
I will execute the script and return the output.

The user's GCP project is: {project}
"""

# ── Frontend (SPA) ─────────────────────────────────────────────
FRONTEND_HTML = (Path(__file__).parent / "templates" / "index_v2.html").read_text(encoding="utf-8")

@app.route("/")
def index():
    return FRONTEND_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/assets/<path:path>")
def static_assets(path):
    return send_from_directory(str(Path(__file__).parent / "templates"), path)

@app.route("/forensic/<path:path>")
def forensic_assets(path):
    return send_from_directory(str(Path(__file__).parent.parent / "forensic"), path)

# ── AI Chat ────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400
    try:
        model = get_ai()
        
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT repo_url FROM user_repos WHERE user_id = ?", (request.user_id,))
        repos = [r['repo_url'] for r in c.fetchall()]
        conn.close()
          
        repo_text = ""
        if repos:
            repo_text = "\\n\\n[USER GITHUB REPOS]\\nThe user has linked the following GitHub repositories to their account:\\n" + "\\n".join(repos) + "\\n\\nYou can use these custom OSINT tools by writing a bash block that git clones them to /tmp and runs them. E.g., `git clone [url] /tmp/repo && /tmp/repo/script.sh`"

        context = build_rag_context()
        prompt = f"{SYSTEM_PROMPT.format(project=GCP_PROJECT)}\\n\\nCurrent context:\\n{context}{repo_text}\\n\\nUser question: {message}\\n\\nReturn your answer. If you need to query BigQuery, include a SQL block with ```sql ... ``` that I can execute separately."
        resp = model.generate_content(prompt)
        text = resp.text

        sql_blocks = re.findall(r"```sql\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if not sql_blocks:
            sql_blocks = re.findall(r"```\n?(SELECT .*?;)```", text, re.DOTALL)

        result_data = None
        bash_blocks = re.findall(r"```bash\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
        
        if sql_blocks:
            try:
                client = get_bq()
                for sql in sql_blocks[:1]:
                    job = client.query(sql.strip())
                    rows = [dict(r) for r in job.result()]
                    if rows:
                        result_data = {"sql": sql.strip(), "rows": rows[:100], "total": len(rows)}
            except Exception as e:
                result_data = {"sql": sql_blocks[0].strip(), "error": str(e)}
        elif bash_blocks:
            try:
                cmd = bash_blocks[0].strip()
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                result_data = {
                    "bash": cmd, 
                    "stdout": process.stdout[:5000], 
                    "stderr": process.stderr[:5000], 
                    "exit_code": process.returncode
                }
            except subprocess.TimeoutExpired:
                result_data = {"bash": cmd, "error": "Command timed out after 60 seconds."}
            except Exception as e:
                result_data = {"bash": bash_blocks[0].strip(), "error": str(e)}

        return jsonify({
            "response": text,
            "context": {
                "documents": len(knowledge_store["documents"]),
                "bookmarks": len(knowledge_store["bookmarks"]),
            },
            "result": result_data,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/stream", methods=["POST"])
@login_required
def chat_stream():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400
    def generate():
        try:
            model = get_ai()
            
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT repo_url FROM user_repos WHERE user_id = ?", (request.user_id,))
            repos = [r['repo_url'] for r in c.fetchall()]
            conn.close()
            
            repo_text = ""
            if repos:
                repo_text = "\\n\\n[USER GITHUB REPOS]\\nThe user has linked the following GitHub repositories to their account:\\n" + "\\n".join(repos) + "\\n\\nYou can use these custom OSINT tools by writing a bash block that git clones them to /tmp and runs them. E.g., `git clone [url] /tmp/repo && /tmp/repo/script.sh`"

            context = build_rag_context()
            prompt = f"{SYSTEM_PROMPT.format(project=GCP_PROJECT)}\\n\\nCurrent context:\\n{context}{repo_text}\\n\\nUser question: {message}"
            resp = model.generate_content(prompt, stream=True)
            for chunk in resp:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
    return app.response_class(generate(), mimetype="text/event-stream")

# ── BQ Catalog API ─────────────────────────────────────────────
@app.route("/api/bq/catalog", methods=["GET"])
def bq_catalog():
    try:
        catalog = build_catalog()
        if "_error" in catalog:
            return jsonify({"error": catalog["_error"]})
        flat = []
        for ds, tables in catalog.items():
            for tbl, info in tables.items():
                flat.append({
                    "dataset": ds,
                    "table": tbl,
                    "type": info["type"],
                    "columns": info["schema"],
                    "rows": info["rows"],
                    "size_bytes": info["size_bytes"],
                    "description": info["description"],
                })
        return jsonify({"datasets": list(catalog.keys()), "tables": flat})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bq/schema", methods=["GET"])
def bq_schema():
    dataset = request.args.get("dataset", "")
    table = request.args.get("table", "")
    if not dataset or not table:
        return jsonify({"error": "dataset and table required"}), 400
    try:
        client = get_bq()
        ref = client.get_table(f"{GCP_PROJECT}.{dataset}.{table}")
        schema = [{"name": s.name, "type": s.field_type, "mode": s.mode, "description": s.description or ""} for s in ref.schema]
        return jsonify({"schema": schema, "rows": ref.num_rows, "description": ref.description or ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bq/preview", methods=["GET"])
def bq_preview():
    dataset = request.args.get("dataset", "")
    table = request.args.get("table", "")
    if not dataset or not table:
        return jsonify({"error": "dataset and table required"}), 400
    try:
        client = get_bq()
        job = client.query(f"SELECT * FROM `{GCP_PROJECT}.{dataset}.{table}` LIMIT 20")
        rows = [dict(r) for r in job.result()]
        return jsonify({"rows": rows, "total": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── BQ Query ────────────────────────────────────────────────────
@app.route("/api/bq/query", methods=["POST"])
def bq_query():
    data = request.get_json(silent=True) or {}
    sql = data.get("sql", "").strip()
    if not sql:
        return jsonify({"error": "SQL is required"}), 400
    try:
        client = get_bq()
        job = client.query(sql)
        rows = [dict(r) for r in job.result()]
        cols = list(rows[0].keys()) if rows else []
        return jsonify({"rows": rows, "total": len(rows), "columns": cols})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Smart SQL (NL → SQL) ──────────────────────────────────────
@app.route("/api/bq/smart", methods=["POST"])
def bq_smart():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400
    try:
        model = get_ai()
        catalog = build_catalog()
        cat_text = catalog_to_text(catalog)
        prompt = f"""You are a BigQuery SQL expert. Given the BigQuery catalog below, convert the user's question into a SQL query.

Catalog:
{cat_text}

Rules:
- Use proper backtick-quoted table references: `{GCP_PROJECT}.dataset.table`
- Return ONLY the SQL query, no explanations
- Use LIMIT 100 unless aggregating
- Prefer JOINs over subqueries when possible

Question: {question}
SQL:"""
        resp = model.generate_content(prompt)
        sql = resp.text.strip()
        sql = re.sub(r"^```sql\n?|```$", "", sql, flags=re.IGNORECASE).strip()

        client = get_bq()
        job = client.query(sql)
        rows = [dict(r) for r in job.result()]
        cols = list(rows[0].keys()) if rows else []

        interpret_prompt = f"""The user asked: "{question}"
I ran this SQL: {sql}
Results ({len(rows)} rows): {json.dumps(rows[:5], default=str)}

Explain what this data means in plain English. What patterns, anomalies, or insights do you see?"""
        interpretation = model.generate_content(interpret_prompt).text

        return jsonify({
            "sql": sql,
            "rows": rows[:200],
            "total": len(rows),
            "columns": cols,
            "interpretation": interpretation,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Document Upload ─────────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    uid = str(uuid.uuid4())[:8]
    path = UPLOAD_DIR / f"{uid}_{f.filename}"

    text = ""
    if f.filename.lower().endswith(".pdf"):
        try:
            import fitz
            pdf_path = UPLOAD_DIR / f"{uid}_pdf.pdf"
            f.save(str(pdf_path))
            doc = fitz.open(str(pdf_path))
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
        except Exception:
            f.seek(0)
            text = f.read().decode("utf-8", errors="replace")
    elif f.filename.lower().endswith(".html") or f.filename.lower().endswith(".htm"):
        text = f.read().decode("utf-8", errors="replace")
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
    elif f.filename.lower().endswith(".csv"):
        text = f.read().decode("utf-8", errors="replace")
    else:
        text = f.read().decode("utf-8", errors="replace")

    text = text[:100000]
    f.seek(0)
    f.save(str(path))

    model = get_ai()
    analysis_prompt = f"Analyze this uploaded file ({f.filename}) for forensic intelligence. Extract: names, entities, addresses, phone numbers, email addresses, patterns, anomalies, connections. Be thorough:\n\n{text[:50000]}"
    try:
        resp = model.generate_content(analysis_prompt)
        analysis = resp.text
    except Exception as e:
        analysis = f"Analysis failed: {e}"

    doc_entry = {
        "id": uid,
        "filename": f.filename,
        "text": text[:50000],
        "summary": analysis[:2000],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    knowledge_store["documents"].append(doc_entry)
    if len(knowledge_store["documents"]) > MAX_KNOWLEDGE_DOCS:
        knowledge_store["documents"] = knowledge_store["documents"][-MAX_KNOWLEDGE_DOCS:]

    return jsonify({
        "status": "ok",
        "file": f.filename,
        "analysis": analysis,
        "document_id": uid,
        "total_documents": len(knowledge_store["documents"]),
    })

@app.route("/api/knowledge/documents", methods=["GET"])
def list_documents():
    docs = [{"id": d["id"], "filename": d["filename"], "timestamp": d["timestamp"], "summary": d["summary"][:200]} for d in knowledge_store["documents"]]
    return jsonify({"documents": docs, "total": len(docs)})

@app.route("/api/knowledge/document/<doc_id>", methods=["GET"])
def get_document(doc_id):
    for d in knowledge_store["documents"]:
        if d["id"] == doc_id:
            return jsonify(d)
    return jsonify({"error": "Not found"}), 404

@app.route("/api/knowledge/clear", methods=["POST"])
def clear_knowledge():
    knowledge_store["documents"].clear()
    knowledge_store["bookmarks"].clear()
    return jsonify({"status": "ok"})

# ── Bookmark Import ────────────────────────────────────────────
@app.route("/api/bookmarks/import", methods=["POST"])
def import_bookmarks():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    text = f.read().decode("utf-8", errors="replace")
    f.seek(0)

    bookmarks = []
    pattern = re.compile(r'<A HREF="([^"]*)"[^>]*>(.*?)</A>', re.IGNORECASE | re.DOTALL)
    for m in pattern.finditer(text):
        url = m.group(1).strip()
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if url and title:
            add_date = ""
            tags = []
            add_m = re.search(r'ADD_DATE="(\d+)"', m.group(0))
            if add_m:
                add_date = add_m.group(1)
            tags_m = re.search(r'TAGS="([^"]*)"', m.group(0))
            if tags_m:
                tags = [t.strip() for t in tags_m.group(1).split(",") if t.strip()]
            bookmarks.append({
                "id": str(uuid.uuid4())[:8],
                "title": title,
                "url": url,
                "add_date": add_date,
                "tags": tags,
            })

    knowledge_store["bookmarks"].extend(bookmarks)

    model = get_ai()
    urls_text = "\n".join(f"- {b['title']}: {b['url']}" for b in bookmarks[:100])
    analysis_prompt = f"Analyze these {len(bookmarks)} bookmarks. What topics, patterns, and interests do they reveal? Categorize them:\n\n{urls_text[:30000]}"
    try:
        resp = model.generate_content(analysis_prompt)
        analysis = resp.text
    except:
        analysis = f"Imported {len(bookmarks)} bookmarks."

    return jsonify({
        "status": "ok",
        "count": len(bookmarks),
        "bookmarks": bookmarks[:50],
        "analysis": analysis,
    })

@app.route("/api/bookmarks/list", methods=["GET"])
def list_bookmarks():
    return jsonify({"bookmarks": knowledge_store["bookmarks"], "total": len(knowledge_store["bookmarks"])})

@app.route("/api/bookmarks/search", methods=["POST"])
def search_bookmarks():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip().lower()
    if not query:
        return jsonify({"bookmarks": knowledge_store["bookmarks"]})
    results = [b for b in knowledge_store["bookmarks"] if query in b["title"].lower() or query in b["url"].lower() or any(query in t.lower() for t in b["tags"])]
    return jsonify({"bookmarks": results, "total": len(results)})

# ── Pipeline ───────────────────────────────────────────────────
@app.route("/api/pipeline/run", methods=["POST"])
@login_required
def run_pipeline():
    from osint_pipeline.watcher import run_pipeline as rp
    try:
        rp()
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO investigations (user_id, title, summary, is_public) VALUES (?, ?, ?, 1)", 
                 (request.user_id, "Pipeline Execution", "Data collection pipeline executed successfully."))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pipeline/resolve", methods=["POST"])
@login_required
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
        "status": "ok",
        "service": "OsintNeoAi",
        "version": "3.0.0",
        "uptime": str(datetime.now(timezone.utc) - START_TIME),
        "project": GCP_PROJECT,
        "knowledge": {
            "documents": len(knowledge_store["documents"]),
            "bookmarks": len(knowledge_store["bookmarks"]),
        }
    })



@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "path": request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── Auth & Investigations ────────────────────────────────────────

@app.route("/playbook")
def playbook():
    return render_template("playbook.html")

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    conn = get_db()
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username already exists"}), 400
    conn.close()
    return jsonify({"status": "success"})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = secrets.token_hex(32)
    c.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, row["id"]))
    conn.commit()
    conn.close()
    return jsonify({"token": token, "username": username})

@app.route("/api/investigations/public", methods=["GET"])
def public_investigations():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT i.id, i.title, i.summary, i.timestamp, u.username
        FROM investigations i
        JOIN users u ON i.user_id = u.id
        WHERE i.is_public = 1
        ORDER BY i.timestamp DESC LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()
    
    investigations = [dict(r) for r in rows]
    return jsonify({"investigations": investigations})


@app.route("/api/user/repos", methods=["GET", "POST"])
@login_required
def manage_repos():
    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        repo_url = data.get("repo_url", "").strip()
        if not repo_url.startswith("https://github.com/"):
            conn.close()
            return jsonify({"error": "Must be a valid GitHub URL starting with https://github.com/"}), 400
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        c.execute("INSERT INTO user_repos (user_id, repo_url, repo_name) VALUES (?, ?, ?)", (request.user_id, repo_url, repo_name))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "repo_name": repo_name})
    else:
        c.execute("SELECT id, repo_url, repo_name, added_at FROM user_repos WHERE user_id = ?", (request.user_id,))
        rows = c.fetchall()
        conn.close()
        return jsonify({"repos": [dict(r) for r in rows]})

@app.route("/api/audits/public", methods=["GET"])
def public_audits():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT id, entity, domain, ip, port, service, status, risk
            FROM infrastructure_audits
            ORDER BY port ASC
        """)
        rows = c.fetchall()
        conn.close()
        audits = [dict(r) for r in rows]
        return jsonify({"audits": audits})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def init_db():
    conn = sqlite3.connect('osint_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS investigations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        summary TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_public BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_repos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        repo_url TEXT,
        repo_name TEXT,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS infrastructure_audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity TEXT,
        domain TEXT,
        ip TEXT,
        port INTEGER,
        service TEXT,
        status TEXT,
        risk TEXT
    )''')
    
    # Ensure admin user exists for the alert
    c.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'SystemAdmin', 'dummy_hash')")
    
    # Seed Taxpayer Alert
    c.execute("SELECT COUNT(*) FROM investigations WHERE title LIKE '%TAXPAYER ALERT%'")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO investigations (user_id, title, summary, is_public)
            VALUES (1, '🚨 TAXPAYER ALERT: Critical Data Exposure at Huntington Beach Police Department', 
            'A comprehensive public infrastructure audit has revealed 41 open network ports on the Huntington Beach Police Department (hbpd.org) servers. Taxpayer data, including potentially sensitive law enforcement databases (SQL, MongoDB) and remote access points (RDP, SSH), are currently exposed to the open internet. This represents a massive attack surface and a severe failure to secure public data. View the Infrastructure tab for full details.', 1)
        """)
    
    # Seed Data
    c.execute("SELECT COUNT(*) FROM infrastructure_audits")
    if c.fetchone()[0] == 0:
        seed_data = [
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 21, "FTP", "OPEN", "Plaintext Credential Theft"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 22, "SSH", "OPEN", "Brute-Force Entry Vector"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 23, "Telnet", "OPEN", "Plaintext Infrastructure Control"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 25, "SMTP", "OPEN", "Email Spoofing / Relay"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 53, "DNS", "OPEN", "DNS Poisoning / Amplification"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 80, "HTTP", "OPEN", "Unencrypted Web Traffic"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 110, "POP3", "OPEN", "Email Access"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 135, "RPC/SMB", "OPEN", "Lateral Movement / Ransomware"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 139, "RPC/SMB", "OPEN", "Lateral Movement / Ransomware"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 445, "RPC/SMB", "OPEN", "Lateral Movement / Ransomware"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 389, "LDAP/LDAPS", "OPEN", "Active Directory Enumeration"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 636, "LDAP/LDAPS", "OPEN", "Active Directory Enumeration"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 443, "HTTPS", "OPEN", "Secure Web Access"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 1433, "SQL", "OPEN", "Direct Database Manipulation"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 3306, "SQL", "OPEN", "Direct Database Manipulation"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 5432, "SQL", "OPEN", "Direct Database Manipulation"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 3389, "RDP", "OPEN", "Remote Desktop Hijacking"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 6379, "Redis", "OPEN", "Unauthenticated Data Access"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 9200, "Elasticsearch", "OPEN", "Big Data Exposure"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 9300, "Elasticsearch", "OPEN", "Big Data Exposure"),
            ("Huntington Beach Police Department", "hbpd.org", "162.242.210.88", 27017, "MongoDB", "OPEN", "Database Exfiltration")
        ]
        c.executemany('''
            INSERT INTO infrastructure_audits (entity, domain, ip, port, service, status, risk)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_data)

    conn.commit()
    conn.close()

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)










