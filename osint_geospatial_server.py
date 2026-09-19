"""
OsintNeoAi Unified Geospatial Intelligence Server & CLI Suite
Source: Google Maps Platform Code Assist
"""

import os
import sys
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import requests

class OsintGeospatialServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.path = "/osint_3d_viewer.html"
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/search_place":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
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
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(res.content)
        else:
            self.send_error(404)

def run_server(port=8080):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', port)
    httpd = HTTPServer(server_address, OsintGeospatialServer)
    print(f"[+] OsintNeoAi Geospatial Intelligence Server active at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Server shutting down.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OsintNeoAi Geospatial Intelligence Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind the server")
    args = parser.parse_args()
    run_server(args.port)
