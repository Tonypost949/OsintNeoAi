#!/bin/bash
# OsintNeoAi VM — Full CLI Install Script
# Run on: osint-cli-vm (Standard_D2s_v3, East US 2)
# Usage: bash scripts/vm_install_all_clis.sh

set -e
echo "=== OsintNeoAi VM CLI Installer ==="
echo "Start: $(date -u)"

# --- System packages ---
echo "[1/8] System packages..."
sudo apt-get update -y
sudo apt-get install -y \
  git curl wget unzip software-properties-common \
  python3 python3-pip python3-venv \
  nodejs npm \
  docker.io docker-compose \
  nmap whois ffmpeg \
  jq tree htop tmux \
  openssh-client net-tools

sudo systemctl enable docker
sudo usermod -aG docker azureuser

# --- Azure CLI ---
echo "[2/8] Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# --- GitHub CLI ---
echo "[3/8] GitHub CLI..."
(type -p wget >/dev/null || sudo apt-get install wget -y) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(wget -nv -O- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null) \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update -y \
  && sudo apt install gh -y

# --- Google Cloud SDK (no auth needed, just CLI) ---
echo "[4/8] Google Cloud SDK..."
echo "deb [signed-by=/usr/share/keyrings/cloud.google.asc] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo tee /usr/share/keyrings/cloud.google.asc > /dev/null
sudo apt-get update -y && sudo apt-get install -y google-cloud-cli google-cloud-cli-gke-gcloud-auth-plugin

# --- Python packages ---
echo "[5/8] Python packages..."
pip3 install --break-system-packages \
  openai \
  anthropic \
  google-genai \
  google-cloud-vision \
  google-cloud-speech \
  google-cloud-language \
  shodan \
  sherlock-project \
  yt-dlp \
  exiftool \
  pypdf \
  python-docx \
  openpyxl \
  pandas \
  networkx \
  plotly \
  requests \
  beautifulsoup4 \
  playwright \
  reportlab \
  mutagen \
  pillow \
  websocket-client \
  rclone

# --- Node.js global packages ---
echo "[6/8] Node.js global packages..."
sudo npm install -g \
  firebase-tools \
  dataform \
  @anthropic-ai/claude-code \
  typescript \
  vercel \
  netlify-cli

# --- Dev tools ---
echo "[7/8] Dev tools..."
# Terraform
curl -fsSL https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip -o /tmp/terraform.zip
sudo unzip -o /tmp/terraform.zip -d /usr/local/bin/
rm /tmp/terraform.zip

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash

# uv (fast pip)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# --- AI agents ---
echo "[8/8] AI agents..."
# Gemini CLI (agy alternative)
sudo npm install -g @google/gemini-cli

# Ollama (CPU-only for D2s_v3 8GB)
curl -fsSL https://ollama.com/install.sh | sh

# --- Verify ---
echo ""
echo "=== Installation Complete ==="
echo "Time: $(date -u)"
echo ""
echo "=== CLI Status ==="
for cmd in git python3 node npm docker az gh gcloud bq gsutil kubectl helm terraform nmap ffmpeg yt-dlp jq curl wget tmux ollama; do
  if command -v $cmd &>/dev/null; then
    echo "  ✅ $cmd: $(command -v $cmd)"
  else
    echo "  ❌ $cmd: NOT FOUND"
  fi
done

echo ""
echo "=== Docker ==="
sudo docker --version 2>/dev/null || echo "  ❌ Docker not running (reboot needed)"

echo ""
echo "=== Repo ==="
ls /home/azureuser/OsintNeoAi/ | head -20

echo ""
echo "DONE — all CLIs installed on osint-cli-vm"
