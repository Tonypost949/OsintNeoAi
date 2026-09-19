#!/bin/bash
# osint-cockpit — Quick Launcher for Termux HUD
# Connects to OsintNeoAi tactical dashboard over Tailscale mesh

echo "======================================================"
echo "⚡ OSINTNEOAI MOBILE HUD QUICK-LAUNCHER (TERMUX / A16)"
echo "======================================================"

TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "127.0.0.1")
SERVER_URL="http://${TAILSCALE_IP}:8080/master_admin_dashboard.html"

echo "Checking connectivity to OsintNeoAi Dashboard..."
echo "Target URL: ${SERVER_URL}"

if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url "${SERVER_URL}"
    echo "[✓] Launched Mobile HUD in default browser!"
else
    echo "[!] Termux browser launcher not found. Open manually:"
    echo "    ${SERVER_URL}"
fi
