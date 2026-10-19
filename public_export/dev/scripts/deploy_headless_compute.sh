#!/usr/bin/env bash
# ==============================================================================
# OsintNeoAi Universal Headless Compute & Session Persistence Bootstrap
# Supports: Ubuntu, Debian, AlmaLinux on Azure, Oracle, DigitalOcean, FreeVPS
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo "⚡ OsintNeoAi Headless Remote Node Initializer"
echo "=========================================================="

# 1. Update and install foundational tools
echo "[+] Installing system dependencies and runtimes..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y git curl wget tmux htop fail2ban ttyd python3 python3-pip python3-venv jq rclone
elif command -v dnf &> /dev/null; then
    sudo dnf update -y
    sudo dnf install -y git curl wget tmux htop fail2ban python3 python3-pip jq rclone
fi

# 2. Install PowerShell 7 (pwsh)
if ! command -v pwsh &> /dev/null; then
    echo "[+] Installing PowerShell 7 (pwsh)..."
    if command -v apt-get &> /dev/null; then
        # Install prerequisite packages
        sudo apt-get install -y wget apt-transport-https software-properties-common
        # Download Microsoft repository GPG keys
        source /etc/os-release
        wget -q "https://packages.microsoft.com/config/ubuntu/${VERSION_ID}/packages-microsoft-prod.deb" -O /tmp/packages-microsoft-prod.deb
        sudo dpkg -i /tmp/packages-microsoft-prod.deb || true
        sudo apt-get update -y
        sudo apt-get install -y powershell || true
    fi
fi

# 3. Setup workspace directory
TARGET_DIR="${HOME}/OsintNeoAi"
echo "[+] Setting up OsintNeoAi repository at ${TARGET_DIR}..."
if [ ! -d "${TARGET_DIR}" ]; then
    git clone https://github.com/Tonypost949/OsintNeoAi.git "${TARGET_DIR}"
else
    echo "[+] Repository already exists. Pulling latest main..."
    cd "${TARGET_DIR}" && git pull origin main || true
fi

# 4. Setup Python Virtual Environment & Dependencies
echo "[+] Configuring Python environment..."
cd "${TARGET_DIR}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || true
fi
pip install rich requests google-cloud-bigquery || true

# 5. Setup persistent tmux workspace session
TMUX_SCRIPT="${HOME}/attach_workspace.sh"
cat << 'EOF' > "${TMUX_SCRIPT}"
#!/usr/bin/env bash
SESSION_NAME="osintneoai"
tmux has-session -t ${SESSION_NAME} 2>/dev/null
if [ $? != 0 ]; then
    tmux new-session -d -s ${SESSION_NAME} -n "Main"
    tmux send-keys -t ${SESSION_NAME}:Main "cd ~/OsintNeoAi && source .venv/bin/activate" C-m
    tmux send-keys -t ${SESSION_NAME}:Main "python cli/agent_launcher.py" C-m
    tmux new-window -t ${SESSION_NAME} -n "Background"
    tmux send-keys -t ${SESSION_NAME}:Background "cd ~/OsintNeoAi" C-m
fi
tmux attach-session -t ${SESSION_NAME}
EOF
chmod +x "${TMUX_SCRIPT}"

# 6. Add convenience aliases to ~/.bashrc
if ! grep -q "OsintNeoAi Aliases" "${HOME}/.bashrc"; then
cat << 'EOF' >> "${HOME}/.bashrc"

# OsintNeoAi Aliases
alias aicli="cd ~/OsintNeoAi && python3 cli/agent_launcher.py"
alias dev="~/attach_workspace.sh"
alias bqsync="cd ~/OsintNeoAi && python3 core/remote_cloud_ingest.py"
EOF
fi

echo "=========================================================="
echo "✅ Headless Remote Compute Node is Ready!"
echo "• Run '~/attach_workspace.sh' or 'dev' to attach to persistent session."
echo "• Disconnect anytime without interrupting running agent jobs."
echo "=========================================================="
