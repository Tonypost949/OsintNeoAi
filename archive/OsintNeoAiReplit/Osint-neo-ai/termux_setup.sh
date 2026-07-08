#!/data/data/com.termux/files/usr/bin/bash
# OSINT AI Neo — Termux Setup Script for Android
# Run this once in Termux to install all dependencies

echo "======================================"
echo "  OSINT AI Neo — Android Scanner Setup"
echo "======================================"
echo ""

# Grant storage access
echo "[1/5] Requesting storage permission..."
termux-setup-storage
sleep 2

# Update packages
echo "[2/5] Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install Python and core tools
echo "[3/5] Installing Python and dependencies..."
pkg install -y python python-pip libjpeg-turbo libpng

# Install Python packages
echo "[4/5] Installing Python packages..."
pip install --upgrade pip
pip install openpyxl Pillow mutagen

# Copy scanner to phone storage
echo "[5/5] Installing OSINT Neo scanner..."
mkdir -p ~/storage/shared/OSINT_Neo
cp phone_scanner.py ~/storage/shared/OSINT_Neo/phone_scanner.py

echo ""
echo "======================================"
echo "  Setup complete!"
echo ""
echo "  To run the scanner:"
echo "  python ~/storage/shared/OSINT_Neo/phone_scanner.py"
echo ""
echo "  Results saved to:"
echo "  /storage/emulated/0/OSINT_Neo/scan_results/"
echo "======================================"
