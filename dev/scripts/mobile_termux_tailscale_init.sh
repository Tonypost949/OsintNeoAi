#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# OsintNeoAi Mobile Termux & Tailscale Quick Connect
# Auto-attaches mobile device to remote headless compute node over Tailscale
# ==============================================================================

set -e

echo "📱 OsintNeoAi Mobile Terminal Initializer (Termux / Tailscale)"
echo "--------------------------------------------------------"

# 1. Check or install openssh and tailscale in Termux
if ! command -v ssh &> /dev/null; then
    echo "[+] Installing openssh in Termux..."
    pkg update -y && pkg install -y openssh
fi

CONFIG_FILE="${HOME}/.osintneoai_node.conf"

if [ ! -f "${CONFIG_FILE}" ]; then
    echo "Please enter your Remote Cloud Node IP (or Tailscale 100.x.y.z IP):"
    read -r NODE_IP
    echo "Please enter your remote SSH username (e.g. root or ubuntu):"
    read -r NODE_USER
    echo "NODE_IP=${NODE_IP}" > "${CONFIG_FILE}"
    echo "NODE_USER=${NODE_USER}" >> "${CONFIG_FILE}"
    echo "[+] Configuration saved to ${CONFIG_FILE}"
else
    source "${CONFIG_FILE}"
fi

echo "[+] Connecting to ${NODE_USER}@${NODE_IP} over secure mesh..."
echo "[+] Auto-attaching to persistent tmux workspace..."

ssh -t "${NODE_USER}@${NODE_IP}" "bash ~/attach_workspace.sh"
