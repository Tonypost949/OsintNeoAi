#!/usr/bin/env python3
"""
preview_sites.py - Local Preview Server for OsintNeoAi & TaxFunded
Launches local HTTP servers to instantly preview both completed sites.
Part of Amd949609 Antigravity v1.
"""

import http.server
import socketserver
import threading
import os
import sys

def serve_dir(directory, port):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"[PREVIEW SERVER] Serving {directory} at http://localhost:{port}/")
        httpd.serve_forever()

if __name__ == "__main__":
    t1 = threading.Thread(target=serve_dir, args=("/mnt/c/OsintNeoAi", 8080), daemon=True)
    t2 = threading.Thread(target=serve_dir, args=("/mnt/c/TaxFunded/out", 8081), daemon=True)

    t1.start()
    t2.start()

    print("=" * 60)
    print(" Both websites are running live for local preview:")
    print(" 📰 1. OsintNeoAi (The Broadsheet): http://localhost:8080/")
    print(" 🏛️ 2. TaxFunded Portal:            http://localhost:8081/")
    print("=" * 60)
    print("Press Ctrl+C to stop.")

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\nPreview servers stopped.")
