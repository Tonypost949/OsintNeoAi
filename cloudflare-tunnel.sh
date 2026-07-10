#!/bin/bash
# cloudflare-tunnel.sh
# Run: ./cloudflare-tunnel.sh
# Creates a 24hr public tunnel to localhost:8080 via Cloudflare TryCloudflare

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFD="$DIR/cloudflared"

# Download cloudflared if missing
if [[ ! -x "$CFD" ]]; then
    echo "Downloading cloudflared..."
    curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" -o "$CFD"
    chmod +x "$CFD"
fi

# Kill any existing tunnel
pkill -f "cloudflared.*trycloudflare" 2>/dev/null || true
sleep 2

# Start tunnel with HTTP/2 (bypasses QUIC/UDP issues on Windows)
echo "Starting Cloudflare tunnel on http://localhost:8080..."
exec "$CFD" tunnel --url http://localhost:8080 --protocol http2 --no-autoupdate