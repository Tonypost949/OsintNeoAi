#!/bin/bash
set -euo pipefail

# ==============================================================================
# DEDICATED 24/7 CLOUD MOBILE IDE VM DEPLOYMENT SCRIPT
# Project: noble-beanbag-497411-m4
# Target Machine: e2-medium (2 vCPU, 4GB RAM, 50GB SSD)
# Web Access: code-server (VS Code Web) + ttyd (Mobile Web Terminal)
# ==============================================================================

PROJECT_ID="noble-beanbag-497411-m4"
ZONE="us-central1-a"
VM_NAME="osint-mobile-ide-vm"
WEB_PORT="8080"
TTY_PORT="7681"

echo "=== 1. CREATING GCP FIREWALL RULES ==="
gcloud compute firewall-rules create allow-mobile-ide \
  --project="" \
  --network=default \
  --allow=tcp:8080,tcp:7681,tcp:443,tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=mobile-ide 2>/dev/null || true

echo "=== 2. GENERATING STARTUP CONFIGURATION ==="
cat << 'EOF' > /tmp/startup.sh
#!/bin/bash
exec > /var/log/mobile-ide-startup.log 2>&1
set -x

echo "--- Installing Core Packages ---"
apt-get update && apt-get install -y curl git python3 python3-pip python3-venv build-essential jq nodejs npm ttyd

echo "--- Installing code-server (VS Code Web) ---"
curl -fsSL https://code-server.dev/install.sh | sh

echo "--- Configuring code-server ---"
mkdir -p /root/.config/code-server
cat << 'CFCFG' > /root/.config/code-server/config.yaml
bind-addr: 0.0.0.0:8080
auth: password
password: OsintNeoAi2026!
cert: false
CFCFG

echo "--- Cloning OsintNeoAi Repository ---"
mkdir -p /workspace
git clone https://github.com/Tonypost949/OsintNeoAi.git /workspace/OsintNeoAi || true

echo "--- Setting up Systemd Services ---"
systemctl enable --now code-server@root

# Enable ttyd mobile web terminal on port 7681
cat << 'TTYSVC' > /etc/systemd/system/ttyd.service
[Unit]
Description=Mobile Web Terminal (ttyd)
After=network.target

[Service]
ExecStart=/usr/bin/ttyd -p 7681 -c osint:OsintNeoAi2026! bash
Restart=always
User=root
WorkingDirectory=/workspace/OsintNeoAi

[Install]
WantedBy=multi-user.target
TTYSVC

systemctl daemon-reload
systemctl enable --now ttyd

echo "--- Mobile Cloud VM Setup Complete ---"
EOF

echo "=== 3. CREATING GCP VM INSTANCE () ==="
gcloud compute instances create "" \
  --project="" \
  --zone="" \
  --machine-type=e2-medium \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --tags=mobile-ide \
  --scopes=cloud-platform \
  --metadata-from-file=startup-script=/tmp/startup.sh

echo "=== 4. FETCHING EXTERNAL IP ADDRESS ==="
VM_IP=

echo "======================================================================"
echo "🎉 CLOUD MOBILE IDE VM IS ONLINE & RUNNING 24/7!"
echo "======================================================================"
echo "🌐 VS Code Web IDE:    http:// (Password: OsintNeoAi2026!)"
echo "📱 Mobile Terminal:    http:// (Login: osint / Pass: OsintNeoAi2026!)"
echo "======================================================================"
