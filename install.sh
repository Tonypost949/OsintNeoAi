#!/usr/bin/env bash
# =====================================================================
#  OSINTNeoAi — Official One-Line Linux/macOS/WSL/Kali Installer
#  Run via: curl -sSL https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/install.sh | bash
# =====================================================================

echo -e "\033[1;36m=====================================================================\033[0m"
echo -e "\033[1;32m   🚀 Installing & Launching OSINTNeoAi Master Intelligence CLI\033[0m"
echo -e "\033[1;36m=====================================================================\033[0m"

REPO_URL="https://github.com/Tonypost949/OsintNeoAi.git"
INSTALL_DIR="$HOME/OsintNeoAi"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "\033[1;31m[-] Git is not installed. Please install Git: sudo apt install -y git\033[0m"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[-] Python 3 is not installed. Please install Python 3: sudo apt install -y python3\033[0m"
    exit 1
fi

# Clone or Update Repo
if [ -d "$INSTALL_DIR" ]; then
    echo -e "\033[1;33m[*] Updating existing installation at $INSTALL_DIR...\033[0m"
    cd "$INSTALL_DIR"
    git pull origin main || true
else
    echo -e "\033[1;33m[*] Cloning OSINTNeoAi to $INSTALL_DIR...\033[0m"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Virtual Environment Setup with Kali / Debian Auto-Fallbacks
VENV_DIR="$INSTALL_DIR/cli/.venv"
PYTHON_BIN="$VENV_DIR/bin/python3"

echo -e "\033[1;33m[*] Configuring Python execution environment...\033[0m"

# If an existing venv is broken (missing pip), clean it up
if [ -f "$PYTHON_BIN" ] && ! "$PYTHON_BIN" -m pip --version &>/dev/null; then
    echo -e "\033[1;33m[*] Detected incomplete virtual environment without pip. Bootstrapping pip...\033[0m"
    curl -sS https://bootstrap.pypa.io/get-pip.py | "$PYTHON_BIN" 2>/dev/null || rm -rf "$VENV_DIR"
fi

# Try creating venv if not present
if [ ! -f "$PYTHON_BIN" ]; then
    python3 -m venv "$VENV_DIR" 2>/dev/null || true
fi

# If standard venv failed to create or has no pip, try minimal venv + get-pip
if [ ! -f "$PYTHON_BIN" ] || ! "$PYTHON_BIN" -m pip --version &>/dev/null; then
    echo -e "\033[1;33m[*] Setting up lightweight environment with get-pip...\033[0m"
    python3 -m venv --without-pip "$VENV_DIR" 2>/dev/null || true
    if [ -f "$PYTHON_BIN" ]; then
        curl -sS https://bootstrap.pypa.io/get-pip.py | "$PYTHON_BIN" 2>/dev/null || true
    fi
fi

# If venv still has no working pip, fallback to direct system python3
if [ ! -f "$PYTHON_BIN" ] || ! "$PYTHON_BIN" -m pip --version &>/dev/null; then
    echo -e "\033[1;33m[*] Using system python3 (PEP 668 compatible)...\033[0m"
    rm -rf "$VENV_DIR" 2>/dev/null || true
    PYTHON_BIN="python3"
fi

# Install dependencies
echo -e "\033[1;33m[*] Installing dependencies (g4f, maltego-trx, bs4, requests, shodan, bigquery)...\033[0m"
if [ "$PYTHON_BIN" = "python3" ]; then
    python3 -m pip install -r "$INSTALL_DIR/cli/requirements.txt" --user --break-system-packages --quiet 2>/dev/null || \
    python3 -m pip install requests beautifulsoup4 g4f pydantic shodan maltego-trx google-cloud-bigquery --user --break-system-packages --quiet 2>/dev/null || true
else
    "$PYTHON_BIN" -m pip install --upgrade pip --quiet 2>/dev/null || true
    "$PYTHON_BIN" -m pip install -r "$INSTALL_DIR/cli/requirements.txt" --quiet 2>/dev/null || \
    "$PYTHON_BIN" -m pip install requests beautifulsoup4 g4f pydantic shodan maltego-trx google-cloud-bigquery --quiet 2>/dev/null || true
fi

# Global command wrapper (osintneoai)
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
WRAPPER="$BIN_DIR/osintneoai"

cat << EOF > "$WRAPPER"
#!/usr/bin/env bash
INSTALL_DIR="\$HOME/OsintNeoAi"
if [ -f "\$INSTALL_DIR/cli/.venv/bin/python3" ]; then
    "\$INSTALL_DIR/cli/.venv/bin/python3" "\$INSTALL_DIR/cli/cli.py" "\$@"
else
    python3 "\$INSTALL_DIR/cli/cli.py" "\$@"
fi
EOF
chmod +x "$WRAPPER"

# Also create osintcli shorthand
cp "$WRAPPER" "$BIN_DIR/osintcli"
chmod +x "$BIN_DIR/osintcli"

# Add ~/.local/bin to PATH in shell rc files
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q '\.local/bin' "$rc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
    fi
done
export PATH="$HOME/.local/bin:$PATH"

echo -e "\n\033[1;32m[+] Installation Complete!\033[0m"
echo -e "\033[1;36m👉 You can now run 'osintneoai' or 'osintcli' from ANY terminal.\033[0m\n"

# Launch OSINTNeoAiCLI Web Discovery Hub & Victims Board in Background
if [ -f "$INSTALL_DIR/OSINTNeoAiCLI.py" ]; then
    echo -e "\033[1;33m[*] Launching OSINTNeoAiCLI Web Server & Public Victims Board...\033[0m"
    nohup "$PYTHON_BIN" "$INSTALL_DIR/OSINTNeoAiCLI.py" > /dev/null 2>&1 &
    echo -e "\033[1;32m🌐 Web Discovery Hub: http://127.0.0.1:5052\033[0m"
    echo -e "\033[1;32m📢 Public Victims Board: http://127.0.0.1:5052/victims-board\033[0m\n"
fi

# Launch Interactive CLI Session in Foreground (Attaching to /dev/tty if stdin was piped)
echo -e "\033[1;32m[*] Starting OSINTNeoAi interactive CLI session...\033[0m\n"
if [ -t 0 ]; then
    "$PYTHON_BIN" "$INSTALL_DIR/cli/cli.py" chat
elif [ -e /dev/tty ]; then
    "$PYTHON_BIN" "$INSTALL_DIR/cli/cli.py" chat < /dev/tty
else
    echo -e "\033[1;36m👉 To start the interactive chat session, run: osintneoai chat\033[0m"
fi
