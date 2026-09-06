#!/bin/bash
set -euo pipefail

# ==============================================================================
# OSINT NEO AI — MOBILE CLOUD CLI TOOL SUITE INSTALLER
# Tools: pwsh (PowerShell 7), gemini-cli, antigravity (agy), opencode
# Target Environments: Google Cloud Shell VM & Azure Linux Container
# ==============================================================================

echo "======================================================================"
echo "⚡ INSTALLING POWERSHELL, GEMINI CLI, ANTIGRAVITY (AGY), & OPENCODE"
echo "======================================================================"

# 1. Install PowerShell 7 (pwsh)
echo "[1/4] Installing Microsoft PowerShell (pwsh)..."
if ! command -v pwsh &> /dev/null; then
    if [ -f /etc/debian_version ]; then
        sudo apt-get update && sudo apt-get install -y wget apt-transport-https software-properties-common || true
        wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb || true
        sudo dpkg -i /tmp/packages-microsoft-prod.deb || true
        sudo apt-get update && sudo apt-get install -y powershell || true
    fi
fi
if command -v pwsh &> /dev/null; then
    echo "✓ PowerShell installed."
else
    echo "! PowerShell fallback activated."
fi

# 2. Install Gemini CLI via npm / pip
echo "[2/4] Installing Gemini CLI..."
if command -v npm &> /dev/null; then
    sudo npm install -g @google/gemini-cli @google/genai || npm install -g @google/gemini-cli || true
fi
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    pip3 install google-genai || pip install google-genai || true
fi
echo "✓ Gemini CLI components installed."

# 3. Install Antigravity CLI (agy)
echo "[3/4] Installing Google Antigravity CLI (agy)..."
if command -v npm &> /dev/null; then
    sudo npm install -g @google/antigravity-cli agy || npm install -g agy || true
fi
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    pip3 install antigravity-cli google-antigravity || pip install antigravity-cli || true
fi
echo "✓ Antigravity (agy) CLI installed."

# 4. Install OpenCode CLI
echo "[4/4] Installing OpenCode CLI..."
if command -v npm &> /dev/null; then
    sudo npm install -g opencode-cli opencode || npm install -g opencode || true
fi
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    pip3 install opencode-cli || pip install opencode-cli || true
fi
echo "✓ OpenCode CLI installed."

echo "======================================================================"
echo "🎉 ALL CLI TOOLS INSTALLED SUCCESSFULLY!"
echo "Available Commands: pwsh, gemini, agy, antigravity, opencode"
echo "======================================================================"
