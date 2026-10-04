import os
import socket
import threading
import http.server
import socketserver

BRAIN_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
PORT = 8080

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Command Center (Zeus)</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; height: 100vh; background-color: #0f172a; color: #e2e8f0; }
        #sidebar { width: 300px; background-color: #1e293b; padding: 20px; overflow-y: auto; border-right: 1px solid #334155; }
        #content { flex-grow: 1; padding: 40px; overflow-y: auto; background-color: #0f172a; line-height: 1.6; }
        h1, h2 { color: #38bdf8; }
        a { color: #e2e8f0; text-decoration: none; display: block; padding: 10px; margin-bottom: 5px; background-color: #334155; border-radius: 5px; transition: 0.2s; cursor: pointer; }
        a:hover { background-color: #38bdf8; color: #0f172a; }
        pre { background-color: #1e293b; padding: 15px; border-radius: 8px; overflow-x: auto; }
        code { font-family: monospace; }
        blockquote { border-left: 4px solid #38bdf8; margin: 0; padding-left: 15px; color: #cbd5e1; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #334155; padding: 12px; text-align: left; }
        th { background-color: #1e293b; }
        .slide { border: 1px solid #334155; padding: 20px; margin-bottom: 30px; border-radius: 8px; background-color: #1e293b; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 style="color: #ff3333; text-transform: uppercase;">MAKAVELI OSINT HUB</h2>
        <a href="http://{{IP}}:8501" target="_blank" style="background-color: #38bdf8; color: #0f172a; font-weight: bold; text-align: center; margin-bottom: 15px; text-decoration: none; display: block; padding: 10px; border-radius: 5px;">👉 OPEN AI CHAT TERMINAL</a>
        <p style="font-size: 0.8em; color: #94a3b8;">Click a file below to view it on your tablet.</p>
        <div id="file-list"></div>
    </div>
    <div id="content">
        <h1>Welcome to the Command Center</h1>
        <p>Select a document from the left sidebar to load the presentation, legal analysis, or evidence.</p>
    </div>

    <script>
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });

        async function loadFile(filename) {
            try {
                const response = await fetch('/' + filename);
                const text = await response.text();
                
                // Handle our custom carousel slide syntax
                let parsedText = text;
                if (text.includes('<!-- slide -->')) {
                    const slides = text.replace(/````carousel/g, '').replace(/````/g, '').split('<!-- slide -->');
                    parsedText = slides.map((s, i) => `<div class="slide"><h3>Slide ${i+1}</h3>${s}</div>`).join('');
                }

                document.getElementById('content').innerHTML = marked.parse(parsedText);

                // Render mermaid charts
                const mermaidBlocks = document.querySelectorAll('code.language-mermaid');
                mermaidBlocks.forEach((block, index) => {
                    const id = 'mermaid-' + Date.now() + '-' + index;
                    const graphDefinition = block.textContent;
                    const parent = block.parentNode;
                    
                    const div = document.createElement('div');
                    div.className = 'mermaid';
                    div.id = id;
                    parent.replaceWith(div);
                    
                    mermaid.render(id + '-svg', graphDefinition).then(result => {
                        div.innerHTML = result.svg;
                    });
                });
            } catch (error) {
                document.getElementById('content').innerHTML = '<p style="color:red;">Error loading file.</p>';
            }
        }

        // Fetch list of files
        async function loadFileList() {
            try {
                const response = await fetch('/files.json');
                const files = await response.json();
                const list = document.getElementById('file-list');
                files.forEach(f => {
                    const a = document.createElement('a');
                    a.textContent = f;
                    a.onclick = () => loadFile(f);
                    list.appendChild(a);
                });
            } catch(e) {
                console.error(e);
            }
        }

        loadFileList();
    </script>
</body>
</html>
"""

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BRAIN_DIR, **kwargs)

    def do_GET(self):
        import socket
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Try to get local IP dynamically
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('10.255.255.255', 1))
                IP = s.getsockname()[0]
            except Exception:
                IP = '127.0.0.1'
            finally:
                s.close()
                
            templated_html = HTML_TEMPLATE.replace('{{IP}}', IP)
            self.wfile.write(templated_html.encode('utf-8'))
        elif self.path == '/files.json':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Find all MD files in brain dir
            files = [f for f in os.listdir(BRAIN_DIR) if f.endswith('.md')]
            import json
            self.wfile.write(json.dumps(files).encode('utf-8'))
        else:
            super().do_GET()

def start_server():
    os.chdir(BRAIN_DIR)
    
    # Try to get local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()

    print("="*60)
    print("  MAKAVELI COMMAND CENTER DEPLOYED  ")
    print(f"  Access on Tablet/Phone at:  http://{IP}:{PORT}")
    print("="*60)

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()
