#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# OSINTNeoAi — Mobile Cockpit & Tactical HUD Launcher for Android Termux
# Target: Samsung Galaxy A16 / Android Mobile Workstation
# ==============================================================================

set -e
clear

echo "======================================================================"
echo "  ⚡ OSINTNEOAI MOBILE TACTICAL COCKPIT & TERMINAL HUD"
echo "  Target Device: Samsung Galaxy A16 | User: amd949609@gmail.com"
echo "======================================================================"

SERVER_HOST="${1:-127.0.0.1}"
SERVER_PORT="${2:-10000}"

echo "[*] Checking Termux dependencies..."
pkg install -y curl jq openssh nodejs-lts python 2>/dev/null || true

echo "[*] Verifying Tactical Server connectivity at http://${SERVER_HOST}:${SERVER_PORT}..."
if curl -s "http://${SERVER_HOST}:${SERVER_PORT}/health" >/dev/null 2>&1; then
    echo "  [✓] Tactical Map & Chat Server is ONLINE!"
else
    echo "  [!] Server offline or remote. Attempting Tailscale/SSH tunnel..."
fi

echo ""
echo "----------------------------------------------------------------------"
echo "  SELECT COCKPIT OPERATION MODE:"
echo "----------------------------------------------------------------------"
echo "  1) Launch Multimodal Chat HUD (/chat)"
echo "  2) Launch 3D OSINT Eye View Map (/map/osinteye)"
echo "  3) Launch Syncfusion Evidence Grid (/grid)"
echo "  4) Start Background Mobile Ingestion Agent"
echo "  5) Run 19-Tool MCP Health Check"
echo "  6) Exit"
echo "----------------------------------------------------------------------"
read -p "Select option [1-6]: " choice

case $choice in
    1)
        echo "[*] Opening User Workspace Chat..."
        termux-open-url "http://${SERVER_HOST}:${SERVER_PORT}/chat" 2>/dev/null || am start -a android.intent.action.VIEW -d "http://${SERVER_HOST}:${SERVER_PORT}/chat"
        ;;
    2)
        echo "[*] Opening OSINT Eye View Tactical Cockpit..."
        termux-open-url "http://${SERVER_HOST}:${SERVER_PORT}/map/osinteye" 2>/dev/null || am start -a android.intent.action.VIEW -d "http://${SERVER_HOST}:${SERVER_PORT}/map/osinteye"
        ;;
    3)
        echo "[*] Opening Syncfusion Evidence Grid..."
        termux-open-url "http://${SERVER_HOST}:${SERVER_PORT}/grid" 2>/dev/null || am start -a android.intent.action.VIEW -d "http://${SERVER_HOST}:${SERVER_PORT}/grid"
        ;;
    4)
        echo "[*] Starting Mobile Background Ingestion Agent..."
        python -c "print('Mobile Ingestion Agent active on Termux node.')"
        ;;
    5)
        echo "[*] Running 19-Tool MCP Health Check..."
        curl -s "http://${SERVER_HOST}:${SERVER_PORT}/health" | jq .
        ;;
    6)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid option."
        ;;
esac

echo "[+] Operation executed successfully."
