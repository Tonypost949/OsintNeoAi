#!/usr/bin/env python3
"""
Minimal HTTP server for serving tactical GIS maps.
Runs on PORT (default 10000) as a lightweight alternative to the full Flask app.
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("PORT", 10000))
MAPS_DIR = Path(__file__).parent

class MapsHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve map files directly with comprehensive route aliases
        map_files = {
            "/map/master": "master_tactical_gis.html",
            "/maps/master_tactical_gis.html": "master_tactical_gis.html",
            "/map/3d": "maplibre_3d_tactical.html",
            "/maps/maplibre_3d_tactical.html": "maplibre_3d_tactical.html",
            "/map/badass": "badass_osint_map.html",
            "/maps/badass_osint_map.html": "badass_osint_map.html",
            "/map/hbnc": "hbnc_rico_gis.html",
            "/maps/hbnc_rico_gis.html": "hbnc_rico_gis.html",
            "/map/coc": "nationwide_coc_map.html",
            "/maps/nationwide_coc_map.html": "nationwide_coc_map.html",
            "/map/pipeline": "nationwide_pipeline_map.html",
            "/maps/nationwide_pipeline_map.html": "nationwide_pipeline_map.html",
            "/map/comparison": "comparison_swipe_map.html",
            "/map/swipe": "comparison_swipe_map.html",
            "/maps/comparison_swipe_map.html": "comparison_swipe_map.html",
            "/map/kml": "OSINT_MASTER_3D_SURVEILLANCE.kml",
            "/OSINT_MASTER_3D_SURVEILLANCE.kml": "OSINT_MASTER_3D_SURVEILLANCE.kml",
        }
        
        # Strip query parameters if any
        clean_path = self.path.split("?")[0].rstrip("/")
        if not clean_path:
            clean_path = "/"

        if clean_path in map_files:
            map_file = MAPS_DIR / map_files[clean_path]
            if map_file.exists():
                self.send_response(200)
                content_type = "application/vnd.google-earth.kml+xml" if map_file.suffix == ".kml" else "text/html; charset=utf-8"
                self.send_header("Content-type", content_type)
                self.send_header("Cache-Control", "no-cache, must-revalidate")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(map_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, f"Map file not found: {map_file}")
                return
        
        # Health check
        if clean_path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","engine":"MapLibre GL 3D WebGL"}')
            return
        
        # Default root serves master tactical 3D map
        if clean_path == "/":
            master_file = MAPS_DIR / "master_tactical_gis.html"
            if master_file.exists():
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(master_file, "rb") as f:
                    self.wfile.write(f.read())
                return

        return super().do_GET()

def run(server_class=HTTPServer, handler_class=MapsHandler, port=PORT):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"[*] OSINT Tactical GIS Server running on port {port} (all interfaces)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("[*] Server stopped.")

if __name__ == "__main__":
    run()
