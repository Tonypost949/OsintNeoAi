#!/usr/bin/env python3
"""
High-performance, multi-threaded HTTP server for tactical 3D GIS maps on port 10000.
Uses ThreadingHTTPServer to handle concurrent requests instantly without blocking.
"""
import os
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("PORT", 10000))
ROOT_DIR = Path("C:/OsintNeoAi")

MAP_ROUTES = {
    "/map/master": "maplibre_3d_tactical.html",
    "/map/3d": "maplibre_3d_tactical.html",
    "/map/swipe": "comparison_swipe_map.html",
    "/map/comparison": "comparison_swipe_map.html",
    "/map/kml": "OSINT_MASTER_3D_SURVEILLANCE.kml",
    "/map/badass": "badass_osint_map.html",
    "/map/hbnc": "hbnc_rico_gis.html",
    "/map/coc": "nationwide_coc_map.html",
    "/map/pipeline": "nationwide_pipeline_map.html",
    "/": "maplibre_3d_tactical.html",
    "/index.html": "maplibre_3d_tactical.html",
    "/master_tactical_gis.html": "master_tactical_gis.html",
    "/maplibre_3d_tactical.html": "maplibre_3d_tactical.html"
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
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", "0")
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

        target_name = MAP_ROUTES.get(clean_path)
        if not target_name:
            candidate = ROOT_DIR / clean_path.lstrip("/")
            if candidate.is_file():
                target_name = candidate.name

        if target_name:
            file_path = ROOT_DIR / target_name
            if not file_path.exists():
                file_path = ROOT_DIR / "maplibre_3d_tactical.html"

            if file_path.exists():
                data = file_path.read_bytes()
                mime = "application/vnd.google-earth.kml+xml" if file_path.suffix == ".kml" else "text/html; charset=utf-8"
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
