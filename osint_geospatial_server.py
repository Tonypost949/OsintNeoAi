"""
OsintNeoAi Unified Geospatial Intelligence & API Bridge Server
Updated to support full local CLI toolchain execution, chat log export endpoints, and forensic queries.
"""

import os
import sys
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import requests
import subprocess
import datetime

CHAT_EXPORT_DIR = r"C:\OsintNeoAi\chat_exports"

class OsintGeospatialServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/":
            self.path = "/osint_3d_viewer.html"
            return super().do_GET()

        elif parsed.path == "/api/scan":
            self._send_json_response({
                "status": "active",
                "clis": ["docker", "gcloud", "bq", "rclone", "python", "uv", "node", "pac"],
                "timestamp": datetime.datetime.now().isoformat()
            })

        elif parsed.path == "/api/maps":
            self._send_json_response({
                "status": "success",
                "maps": ["osint_3d_viewer.html", "288_caltrans_cctv.kml", "master_locations_gis.json"]
            })

        elif parsed.path == "/api/search":
            query = params.get("q", [""])[0]
            self._send_json_response({
                "status": "success",
                "query": query,
                "matches": [
                    {"entity_id": "PER-001", "name": "JOHN DOE", "type": "PERSON"},
                    {"entity_id": "GOV-002", "name": "HUNTINGTON BEACH CITY COUNCIL", "type": "GOVERNMENT"},
                    {"entity_id": "SHL-003", "name": "PACIFIC SHORES LLC", "type": "SHELL_CORP"}
                ]
            })

        elif parsed.path == "/api/export_chat":
            os.makedirs(CHAT_EXPORT_DIR, exist_ok=True)
            exports = []
            for f in os.listdir(CHAT_EXPORT_DIR):
                if f.endswith(".json") or f.endswith(".txt") or f.endswith(".md"):
                    exports.append(f)
            self._send_json_response({
                "status": "success",
                "export_directory": CHAT_EXPORT_DIR,
                "exported_files": exports
            })

        else:
            return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            data = {}

        if parsed.path == "/api/search_place":
            query = data.get("query", "")
            api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
            url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location"
            }
            payload = {"textQuery": query}
            res = requests.post(url, headers=headers, json=payload)
            self._send_json_response(res.json(), status=res.status_code)

        elif parsed.path == "/api/export_chat":
            agent_name = data.get("agent_name", "unknown_agent")
            conversation_id = data.get("conversation_id", "session_001")
            messages = data.get("messages", [])

            os.makedirs(CHAT_EXPORT_DIR, exist_ok=True)
            filename = f"chat_export_{agent_name}_{conversation_id}_{int(datetime.datetime.now().timestamp())}.json"
            filepath = os.path.join(CHAT_EXPORT_DIR, filename)

            export_payload = {
                "agent_name": agent_name,
                "conversation_id": conversation_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "messages": messages
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_payload, f, indent=2)

            self._send_json_response({
                "status": "success",
                "message": f"Chat log exported successfully.",
                "file_path": filepath,
                "export_dir": CHAT_EXPORT_DIR
            })

        elif parsed.path == "/api/submit-victim":
            self._send_json_response({
                "status": "received",
                "submission_id": f"sub_{int(datetime.datetime.now().timestamp())}",
                "data": data
            })

        else:
            self.send_error(404, "Endpoint not found")

    def _send_json_response(self, obj, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

def run_server(port=8080):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', port)
    httpd = HTTPServer(server_address, OsintGeospatialServer)
    print(f"[+] OsintNeoAi Unified API & Export Server active at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Server shutting down.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OsintNeoAi Unified API & Export Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind the server")
    args = parser.parse_args()
    run_server(args.port)
