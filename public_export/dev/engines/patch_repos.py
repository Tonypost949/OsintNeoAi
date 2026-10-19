import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update init_db with the new table
new_table_sql = '''    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS user_repos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        repo_url TEXT,
        repo_name TEXT,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )\'\'\')
'''

# Find the end of init_db function and inject it before conn.commit()
content = content.replace('    conn.commit()\n    conn.close()\n\nif __name__ == "__main__":', new_table_sql + '    conn.commit()\n    conn.close()\n\nif __name__ == "__main__":')

# 2. Add the /api/user/repos endpoints
repo_endpoints = '''
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

def init_db():'''

content = content.replace('def init_db():', repo_endpoints)

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)
