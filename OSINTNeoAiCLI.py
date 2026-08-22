import os
import sys
import shutil
import subprocess
from pathlib import Path
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

KNOWN_CLIS = [
    {"name": "Python", "cmd": "python", "category": "Language", "test": "python --version", "example": "python -c \"print('Hello World')\""},
    {"name": "Node.js", "cmd": "node", "category": "Runtime", "test": "node --version", "example": "node -v", "fallback_paths": [r"C:\Program Files\nodejs\node.exe", r"C:\Program Files (x86)\nodejs\node.exe", os.path.expanduser(r"~\AppData\Roaming\npm\node.exe")]},
    {"name": "Node Package Manager (npm)", "cmd": "npm", "category": "Package Manager", "test": "npm --version", "example": "npm list -g", "fallback_paths": [r"C:\Program Files\nodejs\npm.cmd"]},
    {"name": "Git", "cmd": "git", "category": "Version Control", "test": "git --version", "example": "git status", "fallback_paths": [r"C:\Program Files\Git\cmd\git.exe"]},
    {"name": "GitHub CLI (gh)", "cmd": "gh", "category": "Version Control", "test": "gh --version", "example": "gh auth status", "fallback_paths": [r"C:\Program Files\GitHub CLI\gh.exe", os.path.expanduser(r"~\AppData\Local\GitHubCLI\gh.exe")]},
    {"name": "Azure CLI (az)", "cmd": "az", "category": "Cloud SDK", "test": "az --version", "example": "az account show", "fallback_paths": [r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd", r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"]},
    
    # Google Cloud CLI Standalone & Python SDKs
    {"name": "Google Cloud CLI (gcloud)", "cmd": "gcloud", "category": "Google Cloud SDK", "test": "gcloud version", "example": "gcloud auth list", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"), r"C:\google-cloud-sdk\bin\gcloud.cmd", r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"]},
    {"name": "Google BigQuery (bq)", "cmd": "bq", "category": "Google Cloud SDK", "test": "bq version", "example": "bq ls --project_id=noble-beanbag-497411-m4", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"), r"C:\google-cloud-sdk\bin\bq.cmd", r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"]},
    {"name": "Google Storage Tool (gsutil)", "cmd": "gsutil", "category": "Google Cloud SDK", "test": "gsutil version", "example": "gsutil ls", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd"), r"C:\google-cloud-sdk\bin\gsutil.cmd", r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd"]},
    
    # Python Google Cloud Libraries
    {"name": "Google Cloud Storage Library", "cmd": "python-storage", "category": "Google Cloud Python SDK", "test": "python -c \"import google.cloud.storage; print(google.cloud.storage.__file__)\"", "example": "from google.cloud import storage\nclient = storage.Client()\nbuckets = list(client.list_buckets())\nprint(buckets)"},
    {"name": "Google Cloud BigQuery Library", "cmd": "python-bigquery", "category": "Google Cloud Python SDK", "test": "python -c \"import google.cloud.bigquery; print(google.cloud.bigquery.__file__)\"", "example": "from google.cloud import bigquery\nclient = bigquery.Client()\nprint('BigQuery client ready')"},
    {"name": "Google Cloud Firestore Library", "cmd": "python-firestore", "category": "Google Cloud Python SDK", "test": "python -c \"import google.cloud.firestore; print(google.cloud.firestore.__file__)\"", "example": "from google.cloud import firestore\nclient = firestore.Client()\nprint('Firestore client ready')"},
    {"name": "Google Cloud Logging Library", "cmd": "python-logging", "category": "Google Cloud Python SDK", "test": "python -c \"import google.cloud.logging; print(google.cloud.logging.__file__)\"", "example": "from google.cloud import logging\nclient = logging.Client()\nprint('Logging client ready')"},
    {"name": "Google Cloud Vision Library", "cmd": "python-vision", "category": "Google Cloud Python SDK", "test": "python -c \"import google.cloud.vision; print(google.cloud.vision.__file__)\"", "example": "from google.cloud import vision\nclient = vision.ImageAnnotatorClient()\nprint('Vision client ready')"},
    {"name": "Google Cloud Translate Library", "cmd": "python-translate", "category": "Google Cloud Python SDK", "test": "python -c \"import google.cloud.translate; print(google.cloud.translate.__file__)\"", "example": "from google.cloud import translate\nclient = translate.TranslationServiceClient()\nprint('Translate client ready')"},

    {"name": "Docker", "cmd": "docker", "category": "Containers", "test": "docker --version", "example": "docker ps", "fallback_paths": [r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"]},
    {"name": "Docker Compose", "cmd": "docker-compose", "category": "Containers", "test": "docker-compose --version", "example": "docker-compose up"},
    {"name": "Kubernetes CLI (kubectl)", "cmd": "kubectl", "category": "DevOps", "test": "kubectl version --client", "example": "kubectl get pods"},
    {"name": "Terraform", "cmd": "terraform", "category": "DevOps", "test": "terraform version", "example": "terraform init"},
    {"name": "Windows Package Manager (winget)", "cmd": "winget", "category": "Package Manager", "test": "winget --version", "example": "winget list"},
    {"name": "Rust Compiler (rustc)", "cmd": "rustc", "category": "Language", "test": "rustc --version", "example": "rustc --version"},
    {"name": "Cargo (Rust)", "cmd": "cargo", "category": "Package Manager", "test": "cargo --version", "example": "cargo build"},
    {"name": "Go Compiler (go)", "cmd": "go", "category": "Language", "test": "go version", "example": "go version"},
    {"name": "Java (java)", "cmd": "java", "category": "Language", "test": "java -version", "example": "java -version"},
    {"name": "cURL", "cmd": "curl", "category": "Networking", "test": "curl --version", "example": "curl -I https://google.com"},
    {"name": "Windows Subsystem for Linux (wsl)", "cmd": "wsl", "category": "OS", "test": "wsl --version", "example": "wsl -l -v"},
    {"name": "PowerShell Core (pwsh)", "cmd": "pwsh", "category": "Shell", "test": "pwsh --version", "example": "pwsh -c \"Get-Host\""},
    {"name": "Antigravity CLI (agy)", "cmd": "agy", "category": "AI Agent", "test": "agy --version", "example": "agy help", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Programs\antigravity\agy.cmd"), os.path.expanduser(r"~\.gemini\antigravity-cli\bin\agy.cmd")]},
    {"name": "Visual Studio Code (code)", "cmd": "code", "category": "Editor", "test": "code --version", "example": "code .", "fallback_paths": [os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"), r"C:\Program Files\Microsoft VS Code\bin\code.cmd"]}
]

def scan_clis():
    results = []
    for item in KNOWN_CLIS:
        cmd_name = item["cmd"]
        path_on_system = None
        if not cmd_name.startswith("python-"):
            path_on_system = shutil.which(cmd_name)
            
        status = "unknown"
        version_output = "N/A"
        exe_path = ""

        if cmd_name.startswith("python-"):
            try:
                out = subprocess.check_output(item["test"], shell=True, stderr=subprocess.STDOUT, timeout=4, text=True)
                status = "in_path"
                exe_path = "Python Package Environment"
                version_output = f"Installed & Ready: {out.strip().split(os.sep)[-1]}"
            except Exception:
                status = "not_found"
                version_output = "Python Package Not Installed"
        elif path_on_system:
            status = "in_path"
            exe_path = path_on_system
            try:
                out = subprocess.check_output(item["test"], shell=True, stderr=subprocess.STDOUT, timeout=3, text=True)
                version_output = out.strip().split("\n")[0][:60]
            except Exception:
                version_output = "Installed (Version check timed out)"
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
                "fix_cmd": f"$env:PATH += ';{os.path.dirname(exe_path)}'; {item['cmd']}" if status == "off_path" else item["example"]
            })
    return results

HTML_APP = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OSINTNeoAiCLI — Windows 11 CLI & Google Cloud Hub</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Manrope', sans-serif; background-color: #080e1a; color: #e2e8f0; }
    .font-mono { font-family: 'DM Mono', monospace; }
  </style>
</head>
<body class="min-h-screen p-8">
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-800 pb-6">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white text-2xl shadow-lg shadow-indigo-600/30">
          <i class="fa-solid fa-terminal"></i>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">OSINTNeoAiCLI</h1>
          <p class="text-xs text-slate-400">Windows 11 CLI Discovery, Google Cloud SDKs & Python Code Hub</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <button onclick="rescan()" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-lg flex items-center gap-2 transition">
          <i class="fa-solid fa-rotate"></i> Re-Scan System
        </button>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="flex gap-4">
      <div class="relative flex-1">
        <i class="fa-solid fa-search absolute left-4 top-3 text-slate-500 text-sm"></i>
        <input id="searchInput" onkeyup="filterCLIs()" type="text" placeholder="Search discovered CLIs & Google Cloud tools (e.g. gcloud, bq, gsutil, storage, node, python)..."
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
      container.innerHTML = '<div class="col-span-2 text-center text-slate-400 py-12"><i class="fa-solid fa-spinner fa-spin text-2xl mb-2"></i><p class="text-xs">Scanning Windows 11 drives, PATH & Google Cloud SDKs...</p></div>';

      const res = await fetch('/api/scan');
      cliData = await res.json();
      renderCLIs(cliData);
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
                  ${c.status === 'in_path' ? '🟢 Active in PATH / Ready' : '🟠 Off-PATH (Needs Env)'}
                </span>
              </div>
              <p class="text-[11px] font-mono text-slate-400 mt-1">${c.version}</p>
            </div>
            <span class="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded font-mono">${c.category}</span>
          </div>

          <div class="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 text-[11px] font-mono text-slate-400 break-all">
            <span class="text-slate-500">Executable / Location:</span> ${c.path}
          </div>

          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono text-slate-400">Command / Python Code to Launch:</span>
              <button onclick="copyCmd('${btoa(unescape(encodeURIComponent(c.fix_cmd)))}')" class="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                <i class="fa-solid fa-copy"></i> Copy Code
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
      alert('Command/Code copied to clipboard! Paste into PowerShell or Python.');
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

@app.route("/api/scan")
def api_scan():
    return jsonify(scan_clis())

if __name__ == "__main__":
    port = 5052
    print(f"\n🚀 OSINTNeoAiCLI active at http://127.0.0.1:{port}\n")
    app.run(host="127.0.0.1", port=port, debug=False)
