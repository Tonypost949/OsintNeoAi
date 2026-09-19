# OSINTNEOAI Unified 3-Tier Environment Router Server
import http.server
import socketserver
import os
import sys

PORT = 8095

class UnifiedRouterHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/api/auth/register':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = '{"status": "SUCCESS", "message": "User registered successfully", "workspace_id": "usr_workspace_clean_001", "redirect_url": "/workspace"}'
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

    def do_GET(self):
        if self.path == '/api/auth/session':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = '{"authenticated": true, "user_type": "public_investigator", "workspace_id": "usr_workspace_clean_001", "is_blank_workspace": true, "personal_data_isolated": true}'
            self.wfile.write(response.encode('utf-8'))
            return
        elif self.path == '/' or self.path == '/signup' or self.path == '/landing':
            self.path = '/core/AG2OSINTNEOMAXX/public_landing.html'
        elif self.path == '/workspace' or self.path == '/workspace/' or self.path == '/chat':
            self.path = '/public/workspace_chat.html'
        elif self.path == '/admin' or self.path == '/admin/':
            self.path = '/admin/master_admin_dashboard.html'
        elif self.path == '/dev' or self.path == '/dev/' or self.path == '/3d':
            self.path = '/web/index.html'
            
        return super().do_GET()

def run_server():
    web_dir = r"C:\OsintNeoAi"
    os.chdir(web_dir)
    handler = UnifiedRouterHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"==========================================================")
        print(f"  OSINTNEOAI UNIFIED 3-TIER ROUTER SERVER ACTIVE ON PORT {PORT}")
        print(f"==========================================================")
        print(f"  [1] User Landing & AI Chat Input:  http://localhost:{PORT}/")
        print(f"  [2] Master Admin Backend:          http://localhost:{PORT}/admin")
        print(f"  [3] Full Developer Access Environment: http://localhost:{PORT}/dev")
        print(f"==========================================================")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
