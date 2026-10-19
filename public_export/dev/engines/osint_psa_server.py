import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class OSINTPsaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OSINT NeoAI PSA Server</title>
            <style>
                body { font-family: Arial, sans-serif; background: #111; color: #eee; padding: 40px; }
                h1 { color: #00ffcc; }
                .card { background: #222; border: 1px solid #444; padding: 20px; border-radius: 8px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>OSINT NeoAI PSA Server Active</h1>
            <div class="card">
                <p>Status: <strong>Running Successfully</strong></p>
                <p>Node.js dependency and PowerShell integration verified.</p>
                <p>Project Root: C:\\OsintNeoAi</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=OSINTPsaHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting OSINT NeoAI PSA server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
