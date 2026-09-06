import os

filepath = 'OSINTNeoAiCLI_v2.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

target = '@app.route("/tasks")'
new_routes = '''@app.route("/terminal")
@app.route("/term")
@app.route("/cli")
def terminal_route():
    for candidate in [os.path.join("public", "terminal.html"), "terminal.html"]:
        p = os.path.join(ROOT_DIR, candidate)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return "<h3>Terminal template not found</h3>", 404

@app.route("/api/cli_exec", methods=["POST"])
def api_cli_exec():
    try:
        data = request.get_json(silent=True) or {}
        cmd = str(data.get("command") or "").strip()
        if not cmd:
            return jsonify({"status": "error", "message": "No command provided"}), 400
        
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT_DIR, timeout=30)
        output = res.stdout
        if res.stderr:
            output += "\\n" + res.stderr
        return jsonify({"status": "success", "output": output, "returncode": res.returncode})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/tasks")'''

if '@app.route("/terminal")' not in code:
    code = code.replace(target, new_routes)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS")
else:
    print("ALREADY_PRESENT")
