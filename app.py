import os
import json
import subprocess
from flask import Flask, jsonify, request, send_from_directory, abort

app = Flask(__name__, static_folder='.')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_content(candidates):
    for c in candidates:
        p = os.path.join(ROOT_DIR, c)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return f.read()
    return None

@app.route('/')
def root_route():
    content = get_file_content(['gods_eye_view_live.html', 'hbnc_rico_gis.html', 'index.html'])
    if content:
        return content
    return '<h1>OSINT Neo AI Command Dashboard</h1>', 200

@app.route('/syncfusion')
@app.route('/syncfusion-grid')
@app.route('/grid')
def syncfusion_route():
    content = get_file_content([os.path.join('public', 'syncfusion_grid.html_v2'), os.path.join('public', 'syncfusion_grid.html'), 'syncfusion_grid.html'])
    if content:
        return content
    return '<h3>Syncfusion Grid Template Not Found</h3>', 404

@app.route('/tasks')
@app.route('/tasks-engine')
def tasks_route():
    content = get_file_content([os.path.join('public', 'tasks.html'), 'tasks.html'])
    if content:
        return content
    return '<h3>Tasks Engine Template Not Found</h3>', 404

@app.route('/terminal')
@app.route('/term')
@app.route('/cli')
def terminal_route():
    content = get_file_content([os.path.join('public', 'terminal.html'), 'terminal.html'])
    if content:
        return content
    return '<h3>Terminal Template Not Found</h3>', 404

@app.route('/victims-board')
@app.route('/victims')
def victims_route():
    content = get_file_content([os.path.join('public', 'victims_board.html'), 'victims_board.html'])
    if content:
        return content
    return '<h3>Victims Board Template Not Found</h3>', 404

@app.route('/gemini')
@app.route('/ai-chat')
def gemini_route():
    content = get_file_content([os.path.join('public', 'gemini_chat.html'), 'gemini_chat.html', 'osint_gemini_gis.html'])
    if content:
        return content
    return '<h3>Gemini AI Studio Template Not Found</h3>', 404

@app.route('/maps')
def maps_route():
    content = get_file_content(['osint_gemini_gis.html', 'hbnc_rico_gis.html', 'maps.html'])
    if content:
        return content
    return '<h3>Maps Hub Template Not Found</h3>', 404

@app.route('/api/tasks')
def api_tasks_route():
    tasks_file = os.path.join(ROOT_DIR, 'data', 'tasks.json')
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
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
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT_DIR, timeout=30)
        output = res.stdout
        if res.stderr:
            output += '\n' + res.stderr
        return jsonify({'status': 'success', 'output': output, 'returncode': res.returncode})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/<path:filename>')
def serve_static_file(filename):
    if os.path.exists(os.path.join(ROOT_DIR, filename)):
        return send_from_directory(ROOT_DIR, filename)
    elif os.path.exists(os.path.join(ROOT_DIR, 'public', filename)):
        return send_from_directory(os.path.join(ROOT_DIR, 'public'), filename)
    abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
