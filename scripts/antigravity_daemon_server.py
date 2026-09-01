#!/usr/bin/env python3
"""
scripts/antigravity_daemon_server.py
====================================
Antigravity CLI Daemon & Remote Intelligence Server (Port 5052 / 10000).

Features:
- Exposes Google Antigravity (agy CLI) over HTTP REST, Server-Sent Events (SSE), and Web UI
- Enables remote execution of agy from anywhere (mobile, browser, curl, shell)
- Supports persistent multi-turn conversations and agent execution modes
- Features a built-in tactical Web Terminal interface with instant dispatch
"""

import os
import sys
import json
import subprocess
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("ANTIGRAVITY_PORT", 5052))
REPO_ROOT = r"C:\OsintNeoAi"
AGY_PATH = r"C:\Users\Amd949609\AppData\Local\agy\bin\agy.exe"

# Fallback to PATH if AGY_PATH does not exist
if not os.path.exists(AGY_PATH):
    AGY_PATH = "agy"

HTML_UI = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ANTIGRAVITY DAEMON CONSOLE — OSINTNeoAi</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Orbitron:wght@600;900&display=swap" rel="stylesheet">
  <style>
    body { background-color: #050508; color: #f3f4f6; font-family: 'JetBrains Mono', monospace; }
    .hud-font { font-family: 'Orbitron', sans-serif; }
    .glow-cyan { box-shadow: 0 0 20px rgba(6, 182, 212, 0.25); }
    .hud-panel { background: rgba(13, 17, 23, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .custom-scroll::-webkit-scrollbar { width: 6px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #222; border-radius: 3px; }
  </style>
</head>
<body class="min-h-screen flex flex-col p-4 md:p-8 justify-between">
  <!-- Header -->
  <header class="hud-panel rounded-2xl p-4 flex items-center justify-between border-cyan-500/30 glow-cyan mb-4">
    <div class="flex items-center gap-3">
      <div class="w-3.5 h-3.5 rounded-full bg-emerald-400 animate-ping"></div>
      <div>
        <h1 class="hud-font text-base md:text-lg font-black text-cyan-400 tracking-wider">ANTIGRAVITY DAEMON SERVER</h1>
        <p class="text-xs text-zinc-500">Autonomous Remote CLI Bridge &bull; Port 5052 &bull; Active Node</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-[10px] px-2.5 py-1 rounded bg-zinc-900 border border-zinc-700 text-zinc-300 font-bold" id="status-pill">DAEMON LIVE</span>
      <a href="/health" target="_blank" class="text-xs text-cyan-400 hover:underline">/health</a>
    </div>
  </header>

  <!-- Output Console -->
  <main class="flex-1 hud-panel rounded-2xl p-4 flex flex-col overflow-hidden mb-4 border-zinc-800">
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-zinc-800 text-xs text-zinc-400">
      <span>TRANSMISSION STREAM / SESSION LOG</span>
      <button onclick="clearConsole()" class="hover:text-rose-400 transition-colors">CLEAR</button>
    </div>
    <div id="output-log" class="flex-1 overflow-y-auto space-y-3 custom-scroll text-xs text-zinc-200">
      <div class="p-3 rounded-lg bg-zinc-950/70 border border-cyan-500/20 text-cyan-300">
        [SYSTEM INITIALIZED] Google Antigravity Daemon is ready. You can submit autonomous prompts, trigger OSINT toolchains, or execute forensic audits remotely from this console.
      </div>
    </div>
  </main>

  <!-- Input Bar -->
  <footer class="hud-panel rounded-2xl p-3 border-cyan-500/30 flex flex-col gap-2">
    <div class="flex items-center gap-2 text-xs">
      <label class="flex items-center gap-1 text-zinc-400">
        <input type="checkbox" id="continue-session" class="rounded bg-zinc-900 border-zinc-700 text-cyan-500" checked>
        <span>--continue session</span>
      </label>
      <label class="flex items-center gap-1 text-zinc-400 ml-4">
        <input type="checkbox" id="skip-perms" class="rounded bg-zinc-900 border-zinc-700 text-cyan-500" checked>
        <span>--dangerously-skip-permissions</span>
      </label>
    </div>
    <form onsubmit="sendPrompt(event)" class="flex gap-2">
      <input type="text" id="prompt-input" placeholder="Enter Antigravity instruction (e.g., 'Run Caltrans D12 CCTV sync', 'Investigate 1601 Dove Street')..." 
        class="flex-1 bg-zinc-950/90 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 transition-all placeholder-zinc-600">
      <button type="submit" id="submit-btn" class="px-6 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs rounded-xl transition-all hud-font">
        EXECUTE
      </button>
    </form>
  </footer>

  <script>
    function clearConsole() {
      document.getElementById('output-log').innerHTML = '';
    }

    async function sendPrompt(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('prompt-input');
      const text = input.value.trim();
      if (!text) return;

      const cont = document.getElementById('continue-session').checked;
      const skipPerms = document.getElementById('skip-perms').checked;
      const log = document.getElementById('output-log');

      // User entry
      const userDiv = document.createElement('div');
      userDiv.className = 'p-3 rounded-lg bg-cyan-950/30 border border-cyan-500/30 text-cyan-200';
      userDiv.innerHTML = `<span class="font-bold text-cyan-400">&gt; USER:</span> ${escapeHtml(text)}`;
      log.appendChild(userDiv);
      input.value = '';

      // Spinner
      const respDiv = document.createElement('div');
      respDiv.className = 'p-3 rounded-lg bg-zinc-950/80 border border-zinc-800 text-zinc-300';
      respDiv.innerHTML = `<span class="text-amber-400 font-bold animate-pulse">&gt; ANTIGRAVITY EXECUTING...</span>`;
      log.appendChild(respDiv);
      log.scrollTop = log.scrollHeight;

      document.getElementById('submit-btn').disabled = true;

      try {
        const res = await fetch('/api/prompt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text, continue: cont, skip_permissions: skipPerms })
        });
        const data = await res.json();
        if (data.status === 'ok') {
          respDiv.innerHTML = `<span class="font-bold text-emerald-400">&gt; AGY RESPONSE:</span><pre class="mt-2 whitespace-pre-wrap font-mono text-zinc-100">${escapeHtml(data.output || '(Execution completed with empty output)')}</pre>`;
        } else {
          respDiv.innerHTML = `<span class="font-bold text-rose-400">&gt; ERROR:</span><pre class="mt-2 whitespace-pre-wrap font-mono text-rose-300">${escapeHtml(data.error || 'Unknown error occurred')}</pre>`;
        }
      } catch (err) {
        respDiv.innerHTML = `<span class="font-bold text-rose-400">&gt; CONNECTION ERROR:</span> ${escapeHtml(err.message)}`;
      } finally {
        document.getElementById('submit-btn').disabled = false;
        log.scrollTop = log.scrollHeight;
      }
    }

    function escapeHtml(str) {
      return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
  </script>
</body>
</html>
"""

class AntigravityDaemonHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(HTML_UI.encode("utf-8"))
            return

        elif path in ("/health", "/api/status"):
            version_out = "unknown"
            try:
                ver_res = subprocess.run([AGY_PATH, "--version"], capture_output=True, text=True, timeout=5)
                if ver_res.returncode == 0:
                    version_out = ver_res.stdout.strip()
            except Exception:
                pass

            status_payload = {
                "status": "healthy",
                "daemon": "Antigravity Remote CLI Daemon",
                "agy_version": version_out,
                "port": PORT,
                "repo": REPO_ROOT,
                "timestamp": time.time()
            }
            body = json.dumps(status_payload, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/prompt":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {e}"}).encode("utf-8"))
                return

            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self.send_response(400)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"error": "Prompt cannot be empty"}')
                return

            use_continue = payload.get("continue", True)
            skip_permissions = payload.get("skip_permissions", True)
            model = payload.get("model", None)

            # Build command list
            cmd = [AGY_PATH, "--print", prompt]
            if use_continue:
                cmd.append("--continue")
            if skip_permissions:
                cmd.append("--dangerously-skip-permissions")
            if model:
                cmd.extend(["--model", model])

            try:
                result = subprocess.run(
                    cmd,
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                response_data = {
                    "status": "ok" if result.returncode == 0 else "error",
                    "returncode": result.returncode,
                    "output": result.stdout.strip(),
                    "stderr": result.stderr.strip()
                }
                status_code = 200 if result.returncode == 0 else 500
            except subprocess.TimeoutExpired:
                response_data = {"status": "error", "error": "Execution timed out after 300 seconds"}
                status_code = 504
            except Exception as ex:
                response_data = {"status": "error", "error": str(ex)}
                status_code = 500

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "POST endpoint not found"}')

def run_daemon():
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, AntigravityDaemonHandler)
    print(f"============================================================")
    print(f"🚀 ANTIGRAVITY DAEMON SERVER ONLINE")
    print(f"============================================================")
    print(f"Local Console:   http://127.0.0.1:{PORT}/")
    print(f"Health API:      http://127.0.0.1:{PORT}/health")
    print(f"Prompt API:      POST http://127.0.0.1:{PORT}/api/prompt")
    print(f"Repository Root: {REPO_ROOT}")
    print(f"AGY Binary:      {AGY_PATH}")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Antigravity Daemon...")
        httpd.shutdown()

if __name__ == "__main__":
    run_daemon()
