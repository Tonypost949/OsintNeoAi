#!/bin/bash
# verify-assets.sh - Verify all bundled and external assets are intact

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ERRORS=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    echo "✗ $*"
    ((ERRORS++))
}

ok() {
    echo "✓ $*"
}

verify_leaflet() {
    local dir="$REPO_ROOT/vendor/leaflet-1.9.4"
    if [[ -d "$dir" ]]; then
        if [[ -f "$dir/leaflet.js" && -f "$dir/leaflet.css" ]]; then
            local size=$(stat -c%s "$dir/leaflet.js" 2>/dev/null || stat -f%z "$dir/leaflet.js" 2>/dev/null)
            if [[ $size -gt 100000 ]]; then
                ok "Leaflet 1.9.4: Complete ($size bytes)"
                return 0
            fi
        fi
        error "Leaflet: Incomplete or corrupted"
        return 1
    else
        error "Leaflet: Not found"
        return 1
    fi
}

verify_chartjs() {
    local dir="$REPO_ROOT/vendor/chartjs-4.4.0"
    if [[ -d "$dir" ]]; then
        if [[ -f "$dir/chart.umd.min.js" ]]; then
            ok "Chart.js 4.4.0: Present"
            return 0
        fi
        error "Chart.js: Missing main file"
        return 1
    else
        error "Chart.js: Not found"
        return 1
    fi
}

verify_bootstrap() {
    local dir="$REPO_ROOT/vendor/bootstrap-5.3.0"
    if [[ -d "$dir" ]]; then
        if [[ -f "$dir/css/bootstrap.min.css" && -f "$dir/js/bootstrap.bundle.min.js" ]]; then
            ok "Bootstrap 5.3.0: Present"
            return 0
        fi
        error "Bootstrap: Incomplete"
        return 1
    else
        error "Bootstrap: Not found"
        return 1
    fi
}

verify_fontawesome() {
    local dir="$REPO_ROOT/vendor/fontawesome-6.4.0"
    if [[ -d "$dir" ]]; then
        if [[ -f "$dir/css/all.min.css" ]]; then
            ok "Font Awesome 6.4.0: Present"
            return 0
        fi
        error "Font Awesome: Incomplete"
        return 1
    else
        error "Font Awesome: Not found"
        return 1
    fi
}

verify_models() {
    local dir="$REPO_ROOT/models"
    if [[ ! -d "$dir" ]]; then
        error "Models directory not found"
        return 1
    fi
    
    local model_count=$(find "$dir" -type f \( -name "*.pt" -o -name "*.bin" -o -name "*.onnx" -o -name "*.pkl" \) | wc -l)
    if [[ $model_count -gt 0 ]]; then
        ok "Models: $model_count model files found"
        # Check each model file has size > 1KB
        find "$dir" -type f \( -name "*.pt" -o -name "*.bin" -o -name "*.onnx" -o -name "*.pkl" \) | while read f; do
            size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null)
            if [[ $size -lt 1024 ]]; then
                error "Model file too small: $f ($size bytes)"
            fi
        done
        return 0
    else
        warn "Models: No model files found (may be OK if using remote)"
        return 0
    fi
}

verify_build_tools() {
    local dir="$REPO_ROOT/build-tools"
    if [[ ! -d "$dir" ]]; then
        error "Build tools directory not found"
        return 1
    fi
    
    local tool_count=0
    for tool in opencode claude-code gemini-cli cursor python node docker; do
        if [[ -d "$dir/$tool" ]]; then
            ok "Build tool: $tool present"
            ((tool_count++))
        fi
    done
    
    if [[ $tool_count -eq 0 ]]; then
        warn "No build tool clones found in build-tools/"
    else
        ok "Build tools: $tool_count found"
    fi
    return 0
}

verify_checksums() {
    local sha_file="$REPO_ROOT/SHA256SUMS.txt"
    if [[ -f "$sha_file" ]]; then
        if sha256sum -c "$sha_file" >/dev/null 2>&1; then
            ok "SHA256 checksums: All valid"
            return 0
        else
            error "SHA256 checksums: MISMATCH"
            return 1
        fi
    else
        warn "No SHA256SUMS.txt found"
        return 0
    fi
}

main() {
    echo "=== ASSET VERIFICATION STARTED ==="
    
    verify_leaflet
    verify_chartjs
    verify_bootstrap
    verify_fontawesome
    verify_models
    verify_build_tools
    verify_checksums
    
    echo
    if [[ $ERRORS -eq 0 ]]; then
        echo "=== ALL ASSETS VERIFIED ==="
        exit 0
    else
        echo "=== VERIFICATION FAILED: $ERRORS ERRORS ==="
        exit 1
    fi
}

main "$@"