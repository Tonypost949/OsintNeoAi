#!/usr/bin/env bash
# =====================================================================
#  OSINTNeoAi — Official One-Line Linux/macOS/WSL Installer & Quickstart
#  Run via: curl -sSL https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/install.sh | bash
# =====================================================================

set -e

echo -e "\033[1;36m=====================================================================\033[0m"
echo -e "\033[1;32m   🚀 Installing & Launching OSINTNeoAi Master Intelligence CLI\033[0m"
echo -e "\033[1;36m=====================================================================\033[0m"

REPO_URL="https://github.com/Tonypost949/OsintNeoAi.git"
INSTALL_DIR="$HOME/OsintNeoAi"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "\033[1;31m[-] Git is not installed. Please install Git first.\033[0m"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[-] Python 3 is not installed. Please install Python 3.10+.\033[0m"
    exit 1
fi

# Clone or Update
if [ -d "$INSTALL_DIR" ]; then
    echo -e "\033[1;33m[*] Updating existing installation at $INSTALL_DIR...\033[0m"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo -e "\033[1;33m[*] Cloning OSINTNeoAi to $INSTALL_DIR...\033[0m"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Virtual Environment
VENV_DIR="$INSTALL_DIR/cli/.venv"
PYTHON_BIN="$VENV_DIR/bin/python3"

if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "\033[1;33m[*] Creating Python virtual environment...\033[0m"
    python3 -m venv "$VENV_DIR"
fi

# Install dependencies
echo -e "\033[1;33m[*] Installing dependencies...\033[0m"
"$PYTHON_BIN" -m pip install --upgrade pip --quiet
if [ -f "$INSTALL_DIR/cli/requirements.txt" ]; then
    "$PYTHON_BIN" -m pip install -r "$INSTALL_DIR/cli/requirements.txt" --quiet
fi

# Global command wrapper
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
WRAPPER="$BIN_DIR/osintneoai"

cat << 'EOF' > "$WRAPPER"
#!/usr/bin/env bash
INSTALL_DIR="$HOME/OsintNeoAi"
"$INSTALL_DIR/cli/.venv/bin/python3" "$INSTALL_DIR/cli/cli.py" "$@"
EOF
chmod +x "$WRAPPER"

echo -e "\n\033[1;32m[+] Installation Complete!\033[0m"
echo -e "\033[1;36m👉 You can now run 'osintneoai' from any terminal.\033[0m\n"

# Launch OSINTNeoAiCLI Web Discovery Hub & Victims Board (Background)
if [ -f "$INSTALL_DIR/OSINTNeoAiCLI.py" ]; then
    echo -e "\033[1;33m[*] Launching OSINTNeoAiCLI Web Server & Public Victims Board...\033[0m"
    nohup "$PYTHON_BIN" "$INSTALL_DIR/OSINTNeoAiCLI.py" > /dev/null 2>&1 &
    echo -e "\033[1;32m🌐 Web Discovery Hub: http://127.0.0.1:5052\033[0m"
    echo -e "\033[1;32m📢 Public Victims Board: http://127.0.0.1:5052/victims-board\033[0m\n"
fi

# Launch Interactive CLI Session (Foreground)
echo -e "\033[1;32m[*] Starting OSINTNeoAi interactive CLI session...\033[0m\n"
"$PYTHON_BIN" "$INSTALL_DIR/cli/cli.py" chat
