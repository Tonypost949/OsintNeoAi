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
        # Serve map files directly
        map_files = {
            "/map/master": "master_tactical_gis.html",
            "/maps/master_tactical_gis.html": "master_tactical_gis.html",
            "/map/badass": "badass_osint_map.html",
            "/maps/badass_osint_map.html": "badass_osint_map.html",
            "/map/hbnc": "hbnc_rico_gis.html",
            "/maps/hbnc_rico_gis.html": "hbnc_rico_gis.html",
            "/map/coc": "nationwide_coc_map.html",
            "/maps/nationwide_coc_map.html": "nationwide_coc_map.html",
            "/map/pipeline": "nationwide_pipeline_map.html",
            "/maps/nationwide_pipeline_map.html": "nationwide_pipeline_map.html",
            "/map/comparison": "comparison_swipe_map.html",
            "/maps/comparison_swipe_map.html": "comparison_swipe_map.html",
        }
        
        if self.path in map_files:
            map_file = MAPS_DIR / map_files[self.path]
            if map_file.exists():
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                with open(map_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, f"Map file not found: {map_file}")
                return
        
        # Health check
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"healthy"}')
            return
        
        # Root
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'''{"service":"OSINTNeoAi Tactical GIS Maps","version":"1.0","endpoints":{"/map/master":"Master Tactical GIS","/map/badass":"Badass OSINT Map","/map/hbnc":"HBNC RICO GIS","/map/coc":"Chain of Custody","/map/pipeline":"Money Pipeline","/map/comparison":"Comparison Swipe"}}''')
            return
        
        # Not found
        self.send_error(404, f"Not found: {self.path}")
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}", file=sys.stderr)

if __name__ == "__main__":
    try:
        server_address = ("0.0.0.0", PORT)
        httpd = HTTPServer(server_address, MapsHandler)
        print(f"🗺️  OSINTNeoAi Tactical GIS Server running on port {PORT}", file=sys.stderr)
        print(f"   Try: http://localhost:{PORT}/map/master", file=sys.stderr)
        httpd.serve_forever()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
