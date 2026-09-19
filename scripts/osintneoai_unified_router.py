# OSINTNEOAI Unified 3-Tier Environment Router Server
import http.server
import socketserver
import os
import sys

PORT = 8095

class UnifiedRouterHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/' or self.path == '/signup' or self.path == '/chat':
            self.path = '/AG2OSINTNEOMAXX/index.html'
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
