import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace login_required with SQLite version (or add it)
auth_code = '''import sqlite3
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
'''

content = re.sub(r'GCP_PROJECT = os.getenv\("GCP_PROJECT", "noble-beanbag-497411-m4"\)', 'GCP_PROJECT = os.getenv("GCP_PROJECT", "noble-beanbag-497411-m4")\n' + auth_code, content)

# 2. Add @login_required decorators
content = content.replace('@app.route("/api/chat", methods=["POST"])', '@app.route("/api/chat", methods=["POST"])\n@login_required')
content = content.replace('@app.route("/api/chat/stream", methods=["POST"])', '@app.route("/api/chat/stream", methods=["POST"])\n@login_required')
content = content.replace('@app.route("/api/pipeline/run", methods=["POST"])', '@app.route("/api/pipeline/run", methods=["POST"])\n@login_required')
content = content.replace('@app.route("/api/pipeline/resolve", methods=["POST"])', '@app.route("/api/pipeline/resolve", methods=["POST"])\n@login_required')

# 3. Modify run_pipeline to add investigations
pipeline_code = '''@app.route("/api/pipeline/run", methods=["POST"])
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
        return jsonify({"error": str(e)}), 500'''

content = re.sub(r'@app.route\("/api/pipeline/run", methods=\["POST"\]\)\n@login_required\ndef run_pipeline\(\):.*?return jsonify\(\{"error": str\(e\)\}\), 500', pipeline_code, content, flags=re.DOTALL)


# 4. Remove the override route
content = content.replace('@app.route("/")\n@app.route("/api/status")', '@app.route("/api/status")')
content = content.replace('"index.html"', '"index_v2.html"')

# 5. Append the Auth Endpoints and DB init
endpoints = '''
# ── Auth & Investigations ────────────────────────────────────────

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

def init_db():
    conn = sqlite3.connect('osint_app.db')
    c = conn.cursor()
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )\'\'\')
    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS investigations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        summary TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_public BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )\'\'\')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
'''

content = re.sub(r'if __name__ == "__main__":\n    port = int\(os.environ.get\("PORT", 8080\)\)\n    app.run\(host="0.0.0.0", port=port, debug=False\)', endpoints, content)

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)
