import os
import shutil
import subprocess
import json
import re
from flask import Flask, jsonify, request, render_template_string, send_from_directory, abort

app = Flask(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "cli", "data")
VICTIMS_FILE = os.path.join(DATA_DIR, "victim_submissions.json")

KNOWN_CLIS = [
    {"name": "Google Cloud CLI (gcloud)", "cmd": "gcloud", "category": "Google Cloud SDK", "test": "gcloud version", "example": "gcloud auth list", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"), r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd", r"C:\GoogleCloudSDK\google-cloud-sdk\bin\gcloud.cmd", "/usr/bin/gcloud", "/usr/local/bin/gcloud", "/data/data/com.termux/files/usr/bin/gcloud"]},
    {"name": "Google BigQuery (bq)", "cmd": "bq", "category": "Google Cloud SDK", "test": "bq version", "example": "bq ls", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"), r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd", "/usr/bin/bq", "/usr/local/bin/bq"]},
    {"name": "Google Storage (gsutil)", "cmd": "gsutil", "category": "Google Cloud SDK", "test": "gsutil version", "example": "gsutil ls", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd"), r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd", "/usr/bin/gsutil", "/usr/local/bin/gsutil"]},
    {"name": "Azure CLI (az)", "cmd": "az", "category": "Cloud SDK", "test": "az --version", "example": "az account show", "fallback_paths": [r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd", r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd", "/usr/bin/az"]},
    {"name": "GitHub CLI (gh)", "cmd": "gh", "category": "DevOps", "test": "gh --version", "example": "gh auth status", "fallback_paths": [r"C:\Program Files\GitHub CLI\gh.exe", os.path.expanduser(r"~\AppData\Local\Programs\GitHub CLI\gh.exe"), "/usr/bin/gh"]},
    {"name": "Git", "cmd": "git", "category": "DevOps", "test": "git --version", "example": "git status", "fallback_paths": [r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files\Git\bin\git.exe", "/usr/bin/git"]},
    {"name": "Docker", "cmd": "docker", "category": "Containers", "test": "docker --version", "example": "docker ps", "fallback_paths": [r"C:\Program Files\Docker\Docker\resources\bin\docker.exe", "/usr/bin/docker"]},
    {"name": "Node.js", "cmd": "node", "category": "Runtime", "test": "node -v", "example": "node -v", "fallback_paths": [r"C:\Program Files\nodejs\node.exe", os.path.expanduser(r"~\AppData\Roaming\nvm\current\node.exe"), "/usr/bin/node"]},
    {"name": "NPM", "cmd": "npm", "category": "Runtime", "test": "npm -v", "example": "npm list -g", "fallback_paths": [r"C:\Program Files\nodejs\npm.cmd", "/usr/bin/npm"]},
    {"name": "Python", "cmd": "python", "category": "Runtime", "test": "python --version", "example": "python -V", "fallback_paths": [r"C:\Python312\python.exe", r"C:\Python311\python.exe", os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"), "/usr/bin/python3"]},
    {"name": "Antigravity CLI (agy)", "cmd": "agy", "category": "AI Agent", "test": "agy --version", "example": "agy help", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Programs\antigravity\agy.cmd"), os.path.expanduser(r"~\.gemini\antigravity-cli\bin\agy.cmd"), os.path.expanduser(r"~/.local/bin/agy")]},
    {"name": "Visual Studio Code (code)", "cmd": "code", "category": "Editor", "test": "code --version", "example": "code .", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"), r"C:\Program Files\Microsoft VS Code\bin\code.cmd", "/usr/bin/code"]}
]

def scan_clis():
    results = []
    for item in KNOWN_CLIS:
        cmd_name = item["cmd"]
        path_on_system = shutil.which(cmd_name)
        status = "unknown"
        version_output = "N/A"
        exe_path = ""

        if path_on_system:
            status = "in_path"
            exe_path = path_on_system
            version_output = "Installed and active in system PATH"
        else:
            found_fallback = False
            for fb in item.get("fallback_paths", []):
                if os.path.exists(fb):
                    status = "off_path"
                    exe_path = fb
                    version_output = "Installed on disk (NOT added to system PATH!)"
                    found_fallback = True
                    break
            if not found_fallback:
                status = "not_found"
                version_output = "Not Installed"

        if status != "not_found":
            results.append({
                "name": item["name"],
                "cmd": item["cmd"],
                "category": item["category"],
                "status": status,
                "path": exe_path,
                "version": version_output,
                "example": item["example"],
                "fix_cmd": f"$env:PATH += ';{os.path.dirname(exe_path)}'; {item['cmd']}" if os.name == 'nt' and status == 'off_path' else item["example"]
            })
    return results

def get_available_maps():
    maps = []
    for f in os.listdir(ROOT_DIR):
        if f.endswith(".html") and any(k in f.lower() for k in ["map", "gis", "tactical", "swipe", "3d", "dashboard"]):
            maps.append({
                "filename": f,
                "name": f.replace(".html", "").replace("_", " ").title(),
                "url": f"/maps/{f}"
            })
    return maps

HTML_APP = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OSINTNeoAi Master Hub — CLIs, Maps & Intelligence</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Manrope', sans-serif; background-color: #080e1a; color: #e2e8f0; }
    .font-mono { font-family: 'DM Mono', monospace; }
  </style>
</head>
<body class="min-h-screen p-6 md:p-8">
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Top Navigation Bar -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-xl">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-xl shadow-lg shadow-indigo-600/30">
          <i class="fa-solid fa-satellite-dish"></i>
        </div>
        <div>
          <h1 class="text-xl font-bold text-white tracking-tight">OSINTNeoAi Discovery Hub</h1>
          <p class="text-[11px] text-slate-400">Local PC CLIs, Tactical GIS Maps & Mutual Aid</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <a href="/" class="bg-indigo-600 text-white text-xs font-bold px-3 py-2 rounded-lg flex items-center gap-1.5 transition">
          <i class="fa-solid fa-terminal"></i> CLI Hub
        </a>
        <a href="/maps" class="bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-bold px-3 py-2 rounded-lg flex items-center gap-1.5 transition">
          <i class="fa-solid fa-map-location-dot"></i> Tactical Maps
        </a>
        <a href="/victims-board" class="bg-red-950/60 hover:bg-red-900/60 border border-red-500/30 text-red-300 text-xs font-bold px-3 py-2 rounded-lg flex items-center gap-1.5 transition">
          <i class="fa-solid fa-bullhorn"></i> Victims Board
        </a>
        <button onclick="rescan()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold px-3 py-2 rounded-lg flex items-center gap-1.5 transition">
          <i class="fa-solid fa-rotate"></i> Re-Scan
        </button>
      </div>
    </div>

    <!-- Quick Stats & Maps Banner -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <a href="/maps" class="bg-gradient-to-br from-cyan-950/40 to-slate-900 border border-cyan-500/30 rounded-xl p-4 hover:border-cyan-400 transition block">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider"><i class="fa-solid fa-map"></i> Tactical Map Hub</span>
          <span class="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded font-mono">8 Maps Live</span>
        </div>
        <p class="text-xs text-slate-300 mt-2">Open Badass OSINT Map, HBNC Plume GIS, 3D MapLibre & ArcGIS Dashboard.</p>
      </a>
      <a href="/victims-board" class="bg-gradient-to-br from-red-950/40 to-slate-900 border border-red-500/30 rounded-xl p-4 hover:border-red-400 transition block">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-red-400 uppercase tracking-wider"><i class="fa-solid fa-heart-pulse"></i> Mutual Aid Board</span>
          <span class="text-[10px] bg-red-500/20 text-red-300 px-2 py-0.5 rounded font-mono">Public / 0-Login</span>
        </div>
        <p class="text-xs text-slate-300 mt-2">View verified victims, submit mutual aid requests, and 1-tap post to Reddit.</p>
      </a>
      <div class="bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/30 rounded-xl p-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-indigo-400 uppercase tracking-wider"><i class="fa-solid fa-microchip"></i> OSINT Engine</span>
          <span class="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded font-mono">Port 5052</span>
        </div>
        <p class="text-xs text-slate-300 mt-2">980+ Tools Cataloged, 2,207 GraphDB Nodes & Google Gemini 3.6 Flash.</p>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="flex gap-4">
      <div class="relative flex-1">
        <i class="fa-solid fa-search absolute left-4 top-3 text-slate-500 text-sm"></i>
        <input id="searchInput" onkeyup="filterCLIs()" type="text" placeholder="Search discovered CLIs & Google Cloud tools (e.g. gcloud, bq, gsutil, node, docker, python)..."
               class="w-full bg-slate-900 border border-slate-800 rounded-xl pl-11 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" />
      </div>
    </div>

    <!-- Discovered CLI Grid -->
    <div id="cliList" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Injected via JS -->
    </div>
  </div>

  <script>
    let cliData = [];

    async function loadCLIs() {
      const container = document.getElementById('cliList');
      container.innerHTML = '<div class="col-span-2 text-center text-slate-400 py-12"><i class="fa-solid fa-spinner fa-spin text-2xl mb-2"></i><p class="text-xs">Scanning local drives, PATH & Google Cloud SDKs...</p></div>';

      try {
        const res = await fetch('/api/scan');
        cliData = await res.json();
        renderCLIs(cliData);
      } catch (e) {
        container.innerHTML = '<div class="col-span-2 text-center text-red-400 py-8 text-xs">Error scanning system CLIs.</div>';
      }
    }

    function renderCLIs(items) {
      const container = document.getElementById('cliList');
      if (items.length === 0) {
        container.innerHTML = '<div class="col-span-2 text-center text-slate-400 py-8 text-xs">No matching CLIs found.</div>';
        return;
      }
      container.innerHTML = items.map(c => `
        <div class="bg-slate-900/90 border ${c.status === 'in_path' ? 'border-slate-800' : 'border-amber-500/30 bg-amber-500/5'} rounded-xl p-5 space-y-3 shadow-md">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-sm font-bold text-white">${c.name}</h3>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded ${c.status === 'in_path' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}">
                  ${c.status === 'in_path' ? '🟢 Active in PATH / Ready' : '🟠 Off-PATH'}
                </span>
              </div>
              <p class="text-[11px] font-mono text-slate-400 mt-1">${c.version}</p>
            </div>
            <span class="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded font-mono">${c.category}</span>
          </div>

          <div class="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 text-[11px] font-mono text-slate-400 break-all">
            <span class="text-slate-500">Executable Location:</span> ${c.path}
          </div>

          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono text-slate-400">Launch Example:</span>
              <button onclick="copyCmd('${btoa(unescape(encodeURIComponent(c.fix_cmd)))}')" class="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                <i class="fa-solid fa-copy"></i> Copy
              </button>
            </div>
            <div class="bg-slate-950 px-3 py-2 rounded-lg border border-slate-800 text-xs font-mono text-cyan-300 select-all whitespace-pre-wrap">
              ${c.fix_cmd}
            </div>
          </div>
        </div>
      `).join('');
    }

    function filterCLIs() {
      const q = document.getElementById('searchInput').value.toLowerCase();
      const filtered = cliData.filter(c => c.name.toLowerCase().includes(q) || c.cmd.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
      renderCLIs(filtered);
    }

    function copyCmd(b64) {
      const text = decodeURIComponent(escape(atob(b64)));
      navigator.clipboard.writeText(text);
      alert('Copied to clipboard!');
    }

    function rescan() { loadCLIs(); }
    document.addEventListener('DOMContentLoaded', loadCLIs);
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_APP)

@app.route("/maps")
@app.route("/map-hub")
def map_hub():
    hub_path = os.path.join(ROOT_DIR, "maps_hub.html")
    if os.path.exists(hub_path):
        with open(hub_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Maps hub template not found</h3>", 404

@app.route("/maps/<path:filename>")
def serve_map_file(filename):
    if os.path.exists(os.path.join(ROOT_DIR, filename)):
        return send_from_directory(ROOT_DIR, filename)
    abort(404)

@app.route("/victims-board")
@app.route("/board")
def victims_board():
    for candidate in ["victims_board.html", "public_victims_board.html"]:
        p = os.path.join(ROOT_DIR, candidate)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return "<h3>Victims Board template not found</h3>", 404

@app.route("/local-map")
@app.route("/system-map")
def local_system_map_route():
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "cli"))
        from core.local_scanner import scan_local_system, generate_local_system_map_html
        telemetry = scan_local_system(ROOT_DIR)
        return generate_local_system_map_html(telemetry)
    except Exception as e:
        return f"<h3>Error generating local system map: {e}</h3>", 500

@app.route("/api/system")
def api_system():
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "cli"))
        from core.local_scanner import scan_local_system
        return jsonify(scan_local_system(ROOT_DIR))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scan")
def api_scan():
    return jsonify(scan_clis())

@app.route("/api/maps")
def api_maps():
    return jsonify(get_available_maps())

@app.route("/api/submit-victim", methods=["POST"])
def submit_victim():
    try:
        data = request.get_json() or {}
        submissions = []
        if os.path.exists(VICTIMS_FILE):
            with open(VICTIMS_FILE, "r", encoding="utf-8") as f:
                submissions = json.load(f)
        data["id"] = f"SUB-{len(submissions)+1:03d}"
        submissions.insert(0, data)
        os.makedirs(os.path.dirname(VICTIMS_FILE), exist_ok=True)
        with open(VICTIMS_FILE, "w", encoding="utf-8") as f:
            json.dump(submissions, f, indent=2)
        return jsonify({"status": "success", "id": data["id"]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = 5052
    print(f"\n🚀 OSINTNeoAi Master Hub active at http://127.0.0.1:{port}")
    print(f"🗺️  Tactical Map Hub: http://127.0.0.1:{port}/maps")
    print(f"📢 Victims Board: http://127.0.0.1:{port}/victims-board\n")
    app.run(host="127.0.0.1", port=port, debug=False)
