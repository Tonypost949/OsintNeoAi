#!/bin/bash
# 24/7 Cloud VM / VPS Master Startup & Daemon Launch Script
echo "[+] Initializing OsintNeoAi Virtual Cloud VM / VPS Stack..."

WORKSPACE_DIR="$(pwd)"
echo "    Workspace Directory: $WORKSPACE_DIR"

# Step 1: Start 24/7 Background Scraping Daemon
echo "[+] Starting 24/7 Background Scraping Daemon..."
python3 tools/cloudshell_scraping_daemon.py &

# Step 2: Bundle and Launch Master Admin Dashboard HTTP Server
echo "[+] Launching Master Admin Dashboard Web Server on Port 8080..."
python3 -m http.server 8080 --directory opencode_work/cloud_dashboard_dist &

echo "[✓] OsintNeoAi 100% Virtual Cloud VM Stack is LIVE!"
