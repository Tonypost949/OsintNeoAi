#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
#  OSINTNeoAi — Official One-Line Android Termux Installer & Quickstart
#  Run via: 
#  pkg update -y && pkg install -y git python curl && curl -sSL https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/install_termux.sh | bash
# =====================================================================

set -e

echo -e "\033[1;36m=====================================================================\033[0m"
echo -e "\033[1;32m   📱 Installing OSINTNeoAi Mobile Intelligence Suite for Termux\033[0m"
echo -e "\033[1;36m=====================================================================\033[0m"

REPO_URL="https://github.com/Tonypost949/OsintNeoAi.git"
INSTALL_DIR="$HOME/OsintNeoAi"

# 1. Update and install required native Termux packages
echo -e "\033[1;33m[*] Updating Termux repositories and packages...\033[0m"
pkg update -y || true
pkg install -y python git curl clang libffi openssl make || true

# 2. Clone or Update Repository
if [ -d "$INSTALL_DIR" ]; then
    echo -e "\033[1;33m[*] Updating existing repository at $INSTALL_DIR...\033[0m"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo -e "\033[1;33m[*] Cloning OSINTNeoAi to $INSTALL_DIR...\033[0m"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 3. Upgrade pip & wheel
echo -e "\033[1;33m[*] Configuring Python package environment...\033[0m"
python3 -m pip install --upgrade pip setuptools wheel --quiet 2>/dev/null || true

# 4. Install dependencies (with Termux-safe fallbacks)
echo -e "\033[1;33m[*] Installing OSINT dependencies (g4f, maltego-trx, bs4, requests, shodan)...\033[0m"
if [ -f "$INSTALL_DIR/cli/requirements.txt" ]; then
    python3 -m pip install -r "$INSTALL_DIR/cli/requirements.txt" --quiet 2>/dev/null || \
    python3 -m pip install requests beautifulsoup4 g4f pydantic shodan maltego-trx google-cloud-bigquery --quiet 2>/dev/null || true
fi

# 5. Create Global Termux Executable in $PREFIX/bin
BIN_DIR="${PREFIX:-/data/data/com.termux/files/usr}/bin"
WRAPPER="$BIN_DIR/osintneoai"

cat << EOF > "$WRAPPER"
#!/data/data/com.termux/files/usr/bin/bash
INSTALL_DIR="\$HOME/OsintNeoAi"
python3 "\$INSTALL_DIR/cli/cli.py" "\$@"
EOF
chmod +x "$WRAPPER"

# Also create osintcli shorthand
cp "$WRAPPER" "$BIN_DIR/osintcli"
chmod +x "$BIN_DIR/osintcli"

echo -e "\n\033[1;32m[+] Termux Installation Complete!\033[0m"
echo -e "\033[1;36m👉 You can now run 'osintneoai' or 'osintcli' from anywhere in Termux.\033[0m\n"

# 6. Launch Web Discovery Hub & Victims Board in Background
if [ -f "$INSTALL_DIR/OSINTNeoAiCLI.py" ]; then
    echo -e "\033[1;33m[*] Starting OSINT Web Hub & Victims Mutual Aid Board on Android...\033[0m"
    nohup python3 "$INSTALL_DIR/OSINTNeoAiCLI.py" > /dev/null 2>&1 &
    echo -e "\033[1;32m🌐 Mobile Browser URL : http://127.0.0.1:5052\033[0m"
    echo -e "\033[1;32m📢 Public Victims Board: http://127.0.0.1:5052/victims-board\033[0m\n"
fi

# 7. Start Foreground Interactive CLI Session
echo -e "\033[1;32m[*] Starting OSINTNeoAi Mobile Intelligence Session...\033[0m\n"
if [ -t 0 ]; then
    python3 "$INSTALL_DIR/cli/cli.py" chat
elif [ -e /dev/tty ]; then
    python3 "$INSTALL_DIR/cli/cli.py" chat < /dev/tty
else
    echo -e "\033[1;36m👉 To start the interactive chat session, run: osintneoai chat\033[0m"
fi
