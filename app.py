import os
import json
import subprocess
import shutil
from flask import Flask, jsonify, request, send_from_directory, abort, Response

app = Flask(__name__, static_folder='.')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_content(candidates):
    for c in candidates:
        for prefix in ['', 'public', 'docs', 'opencode_work', 'data_apps', 'scripts']:
            p = os.path.join(ROOT_DIR, prefix, c) if prefix else os.path.join(ROOT_DIR, c)
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    return f.read()
    return None

@app.route('/')
def root_route():
    content = get_file_content(['hbnc_rico_gis.html', 'badass_osint_map.html', 'index.html'])
    if content:
        return content
    return '<h1>OSINT Neo AI Command Dashboard</h1>', 200

@app.route('/manifest.json')
def manifest_route():
    content = get_file_content(['manifest.json'])
    if content:
        return Response(content, mimetype='application/json')
    return jsonify({'name': 'OsintNeoAi', 'start_url': '/terminal'})

@app.route('/service-worker.js')
def service_worker_route():
    content = get_file_content(['service-worker.js'])
    if content:
        return Response(content, mimetype='application/javascript')
    return Response('// sw', mimetype='application/javascript')

@app.route('/syncfusion')
@app.route('/syncfusion-grid')
@app.route('/grid')
def syncfusion_route():
    content = get_file_content(['syncfusion_grid.html_v2', 'syncfusion_grid.html', 'grid.html'])
    if content:
        return content
    return '<h3>Syncfusion Grid Template Not Found</h3>', 404

@app.route('/tasks')
@app.route('/tasks-engine')
def tasks_route():
    content = get_file_content(['tasks.html', 'tasks_engine.html'])
    if content:
        return content
    return '<h3>Tasks Engine Template Not Found</h3>', 404

@app.route('/terminal')
@app.route('/term')
@app.route('/cli')
def terminal_route():
    content = get_file_content(['terminal.html', 'cli.html'])
    if content:
        return content
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>OsintNeoAi — Mobile Cloud CLI Terminal</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#00f2ff">
    <meta name="mobile-web-app-capable" content="yes">
    <style>
        :root { --bg: #0b0f19; --term-bg: #050811; --cyan: #00f2ff; --green: #00ff88; --text: #e2e8f0; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: monospace; }
        body { background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; }
        header { background: #0f172a; padding: 12px; border-bottom: 1px solid #1e293b; color: var(--cyan); font-weight: bold; }
        .chips { padding: 8px; background: #0b1120; display: flex; gap: 8px; overflow-x: auto; }
        .chip { background: #1e293b; color: var(--cyan); padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; cursor: pointer; white-space: nowrap; }
        .term { flex: 1; background: var(--term-bg); padding: 16px; overflow-y: auto; white-space: pre-wrap; font-size: 0.9rem; }
        .bar { background: #0f172a; padding: 10px; display: flex; gap: 8px; border-top: 1px solid #1e293b; }
        input { flex: 1; background: #050811; border: 1px solid #1e293b; color: #fff; padding: 10px; border-radius: 6px; }
        button { background: var(--cyan); color: #000; border: none; padding: 10px 16px; font-weight: bold; border-radius: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <header>⚡ OSINT NEO AI — MOBILE PWA CLOUD TERMINAL</header>
    <div class="chips">
        <span class="chip" onclick="run('pwsh')">pwsh</span>
        <span class="chip" onclick="run('gemini')">gemini</span>
        <span class="chip" onclick="run('agy')">agy</span>
        <span class="chip" onclick="run('opencode')">opencode</span>
        <span class="chip" onclick="run('bash scripts/install_cli_tools.sh')">install tools</span>
        <span class="chip" onclick="run('ls -la')">list files</span>
    </div>
    <div class="term" id="term">======================================================================
⚡ OSINT NEO AI MOBILE CLOUD CLI TERMINAL
======================================================================
Available Commands: pwsh, gemini, agy, antigravity, opencode
----------------------------------------------------------------------
</div>
    <div class="bar">
        <input type="text" id="cmd" placeholder="Enter CLI command..." onkeydown="if(event.key==='Enter') exec()">
        <button onclick="exec()">Run</button>
    </div>
    <script>
        async function exec() {
            const input = document.getElementById('cmd');
            const cmd = input.value.trim();
            if (!cmd) return;
            const term = document.getElementById('term');
            term.innerText += '\n$ ' + cmd + '\n';
            input.value = '';
            try {
                const res = await fetch('/api/cli_exec', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                term.innerText += (data.output || data.message || 'Done') + '\n';
            } catch(e) {
                term.innerText += 'ERROR: ' + e + '\n';
            }
            term.scrollTop = term.scrollHeight;
        }
        function run(c) { document.getElementById('cmd').value = c; exec(); }
    </script>
</body>
</html>''', 200

@app.route('/victims-board')
@app.route('/victims')
def victims_route():
    content = get_file_content(['victims_board.html', 'public_victims_board.html', 'board.html'])
    if content:
        return content
    return '<h3>Victims Board Template Not Found</h3>', 404

@app.route('/gemini')
@app.route('/ai-chat')
def gemini_route():
    content = get_file_content(['gemini_chat.html', 'osint_gemini_gis.html', 'chat.html'])
    if content:
        return content
    return '<h3>Gemini AI Studio Template Not Found</h3>', 404

@app.route('/maps')
def maps_route():
    content = get_file_content(['hbnc_rico_gis.html', 'badass_osint_map.html', 'badass_arcgis_tactical_map.html', 'osint_gemini_gis.html'])
    if content:
        return content
    return '<h3>Maps Hub Template Not Found</h3>', 404

@app.route('/api/tasks')
def api_tasks_route():
    for candidate in [os.path.join(ROOT_DIR, 'data', 'tasks.json'), os.path.join(ROOT_DIR, 'tasks.json')]:
        if os.path.exists(candidate):
            try:
                with open(candidate, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'tasks': [], 'total': 0, 'status': 'empty'})

@app.route('/api/cli_exec', methods=['POST'])
def api_cli_exec_route():
    try:
        data = request.get_json(silent=True) or {}
        cmd = str(data.get('command') or '').strip()
        if not cmd:
            return jsonify({'status': 'error', 'message': 'No command provided'}), 400

        # Auto alias python -> python3 if python not in path
        if cmd.startswith('python ') and not shutil.which('python'):
            cmd = 'python3 ' + cmd[7:]

        env = os.environ.copy()
        bin_dir = os.path.join(ROOT_DIR, 'bin')
        env['PATH'] = f"{bin_dir}:{os.path.expanduser('~/.local/bin')}:/usr/local/bin:/usr/bin:/bin:" + env.get('PATH', '')

        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT_DIR, timeout=30, env=env)
        output = res.stdout
        if res.stderr:
            output += ('\n' if output else '') + res.stderr
        if not output and res.returncode == 0:
            output = '[Command completed successfully with returncode 0]'

        return jsonify({'status': 'success', 'output': output, 'returncode': res.returncode})
    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'output': 'Command execution timed out (30s limit exceeded)', 'returncode': 124})
    except Exception as e:
        return jsonify({'status': 'error', 'output': f'Execution error: {str(e)}', 'returncode': 1})

@app.route('/api/install_tools', methods=['GET', 'POST'])
def api_install_tools():
    try:
        script_path = os.path.join(ROOT_DIR, 'scripts', 'install_cli_tools.sh')
        cmd = f'bash "{script_path}"' if os.path.exists(script_path) else 'python3 -m pip install google-genai'
        env = os.environ.copy()
        bin_dir = os.path.join(ROOT_DIR, 'bin')
        env['PATH'] = f"{bin_dir}:{os.path.expanduser('~/.local/bin')}:/usr/local/bin:/usr/bin:/bin:" + env.get('PATH', '')
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT_DIR, timeout=120, env=env)
        return jsonify({'status': 'success', 'output': res.stdout + '\n' + res.stderr})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/<path:filename>')
def serve_static_file(filename):
    for dir_path in [ROOT_DIR, os.path.join(ROOT_DIR, 'public'), os.path.join(ROOT_DIR, 'docs'), os.path.join(ROOT_DIR, 'opencode_work'), os.path.join(ROOT_DIR, 'data_apps'), os.path.join(ROOT_DIR, 'scripts')]:
        p = os.path.join(dir_path, filename)
        if os.path.exists(p) and os.path.isfile(p):
            return send_from_directory(dir_path, filename)
    abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
