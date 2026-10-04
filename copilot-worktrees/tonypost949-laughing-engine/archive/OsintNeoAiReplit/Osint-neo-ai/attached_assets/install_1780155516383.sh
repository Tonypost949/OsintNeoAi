#!/bin/bash
# RETRO OSINT v3.0 - Termux Installer
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  🔍 RETRO OSINT v3.0 Installer                                   ║"
echo "║  Low-Bit Visual GUI for Termux                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

set -e

APP_DIR="$HOME/Retro_OSINT"
mkdir -p $APP_DIR/{src,data,exports,assets}

# Install dependencies
echo "[1/3] Installing dependencies..."
pkg update -y
pkg install -y python python-pip clang make libffi openssl git sqlite

# Install Python packages
echo "[2/3] Installing Python packages..."
pip install --upgrade pip
pip install rich prompt-toolkit requests

# Try to install pygame (optional but recommended)
echo "[3/3] Installing pygame (optional, for visuals)..."
pip install pygame || echo "[!] Pygame install failed - will use terminal mode"

# Copy source
cp src/retro_osint_gui.py $APP_DIR/src/

# Create launcher
cat > $APP_DIR/retro-osint << 'LAUNCHER'
#!/bin/bash
cd $HOME/Retro_OSINT
python src/retro_osint_gui.py
LAUNCHER
chmod +x $APP_DIR/retro-osint

# Add alias
if ! grep -q "retro-osint" $HOME/.bashrc 2>/dev/null; then
    echo 'alias retro-osint="$HOME/Retro_OSINT/retro-osint"' >> $HOME/.bashrc
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Installation Complete!                                       ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║  Launch: retro-osint                                             ║"
echo "║  Directory: $APP_DIR                                             ║"
echo "║                                                                  ║"
echo "║  Quick Start:                                                    ║"
echo "║    1. retro-osint                                                ║"
echo "║    2. Type 'demo' (terminal mode) or click entities (GUI)       ║"
echo "║    3. Click SMOKING GUNS for critical evidence                   ║"
echo "║    4. Click EXPORT ALL for Maltego .mtgl file                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
