#!/usr/bin/env python3
"""
High-performance, multi-threaded HTTP server for tactical 3D GIS maps on port 10000.
Uses ThreadingHTTPServer to handle concurrent requests instantly without blocking.
"""
import os
import sys
import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("PORT", 10000))
ROOT_DIR = Path("C:/OsintNeoAi")

MAP_ROUTES = {
    "/map/master": "master_tactical_gis.html",
    "/map/3d": "maplibre_3d_tactical.html",
    "/map/godseye": "gods_eye_view.html",
    "/map/osinteye": "gods_eye_view.html",
    "/osinteye": "gods_eye_view.html",
    "/map/swipe": "comparison_swipe_map.html",
    "/map/comparison": "comparison_swipe_map.html",
    "/map/kml": "OSINT_MASTER_3D_SURVEILLANCE.kml",
    "/map/badass": "badass_osint_map.html",
    "/map/hbnc": "hbnc_rico_gis.html",
    "/map/coc": "nationwide_coc_map.html",
    "/map/pipeline": "nationwide_pipeline_map.html",
    "/grid": "syncfusion_grid.html_v2",
    "/dashboard": "dashboard.html",
    "/telemetry": "public/live_telemetry.geojson",
    "/chat": "public/workspace_chat.html",
    "/workspace": "public/workspace_chat.html",
    "/workspace_chat.html": "public/workspace_chat.html",
    "/public/workspace_chat.html": "public/workspace_chat.html",
    "/": "master_tactical_gis.html",
    "/index.html": "master_tactical_gis.html",
    "/master_tactical_gis.html": "master_tactical_gis.html",
    "/maplibre_3d_tactical.html": "maplibre_3d_tactical.html",
    "/gods_eye_view.html": "gods_eye_view.html"
}

class ThreadedTacticalMapHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_HEAD(self):
        self._handle(head_only=True)

    def do_GET(self):
        self._handle(head_only=False)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        clean_path = self.path.split("?")[0].rstrip("/")
        if clean_path in ["/api/notebook_dump", "/api/rip_evidence", "/api/extract"]:
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(body)
                
                title = payload.get("title", "untitled_notebook")
                safe_title = "".join(c if c.isalnum() else "_" for c in title).lower()
                
                out_dir = ROOT_DIR / "data" / "chats" / "notebooks" / "extracted"
                out_dir.mkdir(parents=True, exist_ok=True)
                
                filtered_dir = ROOT_DIR / "data" / "filtered_chats"
                filtered_dir.mkdir(parents=True, exist_ok=True)
                
                # Save raw JSON
                json_file = out_dir / f"{safe_title}_dump.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
                
                # Save clean text
                txt_file = filtered_dir / f"{safe_title}_clean.txt"
                raw_text = payload.get("raw_text", "") or payload.get("raw_text_dump", "")
                with open(txt_file, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\nURL: {payload.get('url', '')}\nTimestamp: {payload.get('timestamp', '')}\n\n## Content:\n{raw_text}")
                
                resp = json.dumps({"status": "success", "saved_json": str(json_file.name), "saved_txt": str(txt_file.name)}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                return
            except Exception as e:
                err = json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
                return

        self.send_response(404)
        self.end_headers()

    def _handle(self, head_only=False):
        clean_path = self.path.split("?")[0].rstrip("/")
        if not clean_path:
            clean_path = "/"

        if clean_path == "/health":
            body = b'{"status":"healthy","engine":"MapLibre GL 3D WebGL","port":10000}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
            return

        if clean_path.startswith("/api/inspect"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed.query)
            q = query_params.get("query", [""])[0].lower()
            
            entities_file = ROOT_DIR / "data" / "extracted_evidence_entities.json"
            matches = []
            if entities_file.exists():
                try:
                    with open(entities_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    records = data.get("records", [])
                    for r in records:
                        if not q or q in r.get("filename", "").lower() or q in r.get("relative_path", "").lower():
                            matches.append(r)
                            if len(matches) >= 15:
                                break
                except Exception as e:
                    pass

            resp_json = json.dumps({"query": q, "total_matches": len(matches), "records": matches}, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_json)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if not head_only:
                self.wfile.write(resp_json)
            return

        target_name = MAP_ROUTES.get(clean_path)
        if not target_name:
            candidate = ROOT_DIR / clean_path.lstrip("/")
            if candidate.is_file():
                target_name = str(candidate.relative_to(ROOT_DIR))

        if target_name:
            file_path = ROOT_DIR / target_name
            if not file_path.exists():
                file_path = ROOT_DIR / "maplibre_3d_tactical.html"

            if file_path.exists():
                data = file_path.read_bytes()
                if file_path.suffix == ".kml":
                    mime = "application/vnd.google-earth.kml+xml"
                elif file_path.suffix in [".geojson", ".json"]:
                    mime = "application/json"
                elif file_path.suffix == ".js":
                    mime = "application/javascript"
                elif file_path.suffix == ".css":
                    mime = "text/css"
                else:
                    mime = "text/html; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Connection", "close")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                if not head_only:
                    self.wfile.write(data)
                return

        err_body = b'{"error":"Not Found","available_routes":["/map/master","/map/3d","/map/swipe","/map/kml","/map/badass","/map/hbnc","/map/coc","/map/pipeline"]}'
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(err_body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if not head_only:
            self.wfile.write(err_body)

    def log_message(self, format, *args):
        pass

def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ThreadedTacticalMapHandler)
    server.daemon_threads = True
    print(f"[*] Threaded Tactical Map Server running on http://0.0.0.0:{PORT}...")
    server.serve_forever()

if __name__ == "__main__":
    main()
