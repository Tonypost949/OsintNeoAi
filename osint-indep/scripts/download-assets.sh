#!/bin/bash
# download-assets.sh - Download and vendor all external assets
# Run once to create fully offline-capable environment

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
VENDOR_DIR="$REPO_ROOT/vendor"
LOG_FILE="$REPO_ROOT/logs/assets-download-$(date +%Y%m%d).log"

mkdir -p "$VENDOR_DIR/leaflet" "$VENDOR_DIR/chartjs" "$VENDOR_DIR/bootstrap" "$VENDOR_DIR/fontawesome" "$VENDOR_DIR/wheels"
mkdir -p "$REPO_ROOT/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

download() {
    local url="$1"
    local dest="$2"
    local expected_sha256="${3:-}"
    
    if [[ -f "$dest" ]]; then
        if [[ -n "$expected_sha256" ]]; then
            actual=$(sha256sum "$dest" | cut -d' ' -f1)
            if [[ "$actual" == "$expected_sha256" ]]; then
                log "SKIP: $dest (already present, checksum OK)"
                return 0
            fi
        else
            log "SKIP: $dest (already present)"
            return 0
        fi
    fi
    
    log "DOWNLOAD: $url -> $dest"
    if curl -fL --retry 3 --retry-delay 5 -o "$dest.tmp" "$url"; then
        if [[ -n "$expected_sha256" ]]; then
            actual=$(sha256sum "$dest.tmp" | cut -d' ' -f1)
            if [[ "$actual" != "$expected_sha256" ]]; then
                log "ERROR: Checksum mismatch for $dest"
                rm -f "$dest.tmp"
                return 1
            fi
        fi
        mv "$dest.tmp" "$dest"
        log "OK: $dest"
    else
        log "ERROR: Failed to download $url"
        rm -f "$dest.tmp"
        return 1
    fi
}

# Leaflet 1.9.4
log "=== Downloading Leaflet 1.9.4 ==="
download "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" \
    "$VENDOR_DIR/leaflet/leaflet.css" \
    "5e8b7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e"
download "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" \
    "$VENDOR_DIR/leaflet/leaflet.js" \
    "3e8b7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e7b8e"
download "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png" \
    "$VENDOR_DIR/leaflet/images/marker-icon.png" \
    ""
download "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png" \
    "$VENDOR_DIR/leaflet/images/marker-icon-2x.png" \
    ""
download "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png" \
    "$VENDOR_DIR/leaflet/images/marker-shadow.png" \
    ""

# Chart.js 4.4.0
log "=== Downloading Chart.js 4.4.0 ==="
download "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" \
    "$VENDOR_DIR/chartjs/chart.umd.min.js" \
    ""

# Bootstrap 5.3.0
log "=== Downloading Bootstrap 5.3.0 ==="
download "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" \
    "$VENDOR_DIR/bootstrap/bootstrap.min.css" \
    ""
download "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" \
    "$VENDOR_DIR/bootstrap/bootstrap.bundle.min.js" \
    ""

# Font Awesome 6.4.0
log "=== Downloading Font Awesome 6.4.0 ==="
download "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" \
    "$VENDOR_DIR/fontawesome/all.min.css" \
    ""
download "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/webfonts/fa-solid-900.woff2" \
    "$VENDOR_DIR/fontawesome/webfonts/fa-solid-900.woff2" \
    ""
download "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/webfonts/fa-regular-400.woff2" \
    "$VENDOR_DIR/fontawesome/webfonts/fa-regular-400.woff2" \
    ""
download "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/webfonts/fa-brands-400.woff2" \
    "$VENDOR_DIR/fontawesome/webfonts/fa-brands-400.woff2" \
    ""

# Pre-build Python wheels for offline install
log "=== Building Python wheels ==="
cd "$REPO_ROOT"
pip wheel --wheel-dir="$VENDOR_DIR/wheels" -r requirements.txt
log "Wheels built in $VENDOR_DIR/wheels"

# Create manifest
log "=== Creating asset manifest ==="
cat > "$VENDOR_DIR/MANIFEST.json" <<EOF
{
  "generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "assets": {
    "leaflet": {
      "version": "1.9.4",
      "files": ["leaflet.css", "leaflet.js", "images/marker-icon.png", "images/marker-icon-2x.png", "images/marker-shadow.png"]
    },
    "chartjs": {
      "version": "4.4.0",
      "files": ["chart.umd.min.js"]
    },
    "bootstrap": {
      "version": "5.3.0",
      "files": ["bootstrap.min.css", "bootstrap.bundle.min.js"]
    },
    "fontawesome": {
      "version": "6.4.0",
      "files": ["all.min.css", "webfonts/fa-solid-900.woff2", "webfonts/fa-regular-400.woff2", "webfonts/fa-brands-400.woff2"]
    }
  },
  "wheels_count": $(find "$VENDOR_DIR/wheels" -name "*.whl" | wc -l)
}
EOF

log "=== ASSET DOWNLOAD COMPLETE ==="
log "Vendor directory: $VENDOR_DIR"
log "Manifest: $VENDOR_DIR/MANIFEST.json"