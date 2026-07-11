#!/bin/bash
# verify-backups.sh - Verify all backup tiers are current and intact
# Run in pre-commit hook and daily cron

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LAST_COMMIT="$(git rev-parse HEAD)"
ERRORS=0
WARNINGS=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "✗ ERROR: $*"
    ((ERRORS++))
}

warn() {
    log "⚠ WARNING: $*"
    ((WARNINGS++))
}

ok() {
    log "✓ $*"
}

verify_gdrive() {
    log "=== Verifying Google Drive (Tier 2) ==="
    
    if ! rclone listremotes | grep -q "gdrive-sharedall:"; then
        error "gdrive-sharedall remote not configured"
        return
    fi
    
    # Check latest mirror exists
    if rclone lsf "gdrive-sharedall:osint-indep-backup/latest/.git" >/dev/null 2>&1; then
        # Try to get commit from bundle if available
        if rclone lsf "gdrive-sharedall:osint-indep-backup/latest/.git/HEAD" >/dev/null 2>&1; then
            GDRIVE_COMMIT=$(rclone cat "gdrive-sharedall:osint-indep-backup/latest/.git/HEAD" 2>/dev/null | awk '{print $2}' || echo "unknown")
            if [[ "$GDRIVE_COMMIT" == "$LAST_COMMIT" ]]; then
                ok "Google Drive mirror: Current (commit $GDRIVE_COMMIT)"
            else
                warn "Google Drive mirror: Behind (has $GDRIVE_COMMIT, need $LAST_COMMIT)"
            fi
        else
            ok "Google Drive mirror: Exists (cannot verify commit)"
        fi
    else
        error "Google Drive mirror not found at /osint-indep-backup/latest"
    fi
    
    # Check snapshots exist
    SNAPSHOT_COUNT=$(rclone lsf "gdrive-sharedall:osint-indep-backup/snapshots" 2>/dev/null | wc -l)
    if [[ $SNAPSHOT_COUNT -gt 0 ]]; then
        ok "Google Drive snapshots: $SNAPSHOT_COUNT found"
    else
        warn "Google Drive snapshots: None found"
    fi
    
    # Check vendor/models/build-tools
    for asset in vendor models build-tools; do
        if rclone lsf "gdrive-sharedall:osint-indep-backup/latest/$asset" >/dev/null 2>&1; then
            ok "Google Drive asset '$asset': Present"
        else
            warn "Google Drive asset '$asset': Missing"
        fi
    done
}

verify_local() {
    log "=== Verifying Local Backup (Tier 3) ==="
    
    LOCAL_DIR="/mnt/c/osint-indep-backup/latest"
    if [[ ! -d "$LOCAL_DIR" ]]; then
        LOCAL_DIR="C:/osint-indep-backup/latest"
    fi
    
    if [[ ! -d "$LOCAL_DIR" ]]; then
        error "Local backup directory not found: $LOCAL_DIR"
        return
    fi
    
    ok "Local backup directory exists: $LOCAL_DIR"
    
    # Check timestamp
    if [[ -f "$LOCAL_DIR/.backup_timestamp" ]]; then
        LOCAL_TIME=$(cat "$LOCAL_DIR/.backup_timestamp")
        log "Local backup timestamp: $LOCAL_TIME"
    else
        warn "Local backup timestamp file missing"
    fi
    
    # Check git repo integrity
    if [[ -d "$LOCAL_DIR/.git" ]]; then
        LOCAL_COMMIT=$(cd "$LOCAL_DIR" && git rev-parse HEAD 2>/dev/null || echo "unknown")
        if [[ "$LOCAL_COMMIT" == "$LAST_COMMIT" ]]; then
            ok "Local backup commit: Current ($LOCAL_COMMIT)"
        else
            warn "Local backup commit: Behind (has $LOCAL_COMMIT, need $LAST_COMMIT)"
        fi
    else
        warn "Local backup missing .git directory"
    fi
    
    # Check snapshots
    SNAPSHOT_DIR="/mnt/c/osint-indep-backup/snapshots"
    if [[ ! -d "$SNAPSHOT_DIR" ]]; then
        SNAPSHOT_DIR="C:/osint-indep-backup/snapshots"
    fi
    
    if [[ -d "$SNAPSHOT_DIR" ]]; then
        BUNDLE_COUNT=$(find "$SNAPSHOT_DIR" -name "*.bundle" -type f | wc -l)
        if [[ $BUNDLE_COUNT -gt 0 ]]; then
            ok "Local snapshots: $BUNDLE_COUNT found"
            # Verify latest bundle
            LATEST_BUNDLE=$(find "$SNAPSHOT_DIR" -name "*.bundle" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)
            if [[ -n "$LATEST_BUNDLE" ]]; then
                if git bundle verify "$LATEST_BUNDLE" >/dev/null 2>&1; then
                    ok "Latest local bundle: Valid"
                else
                    error "Latest local bundle: CORRUPT ($LATEST_BUNDLE)"
                fi
            fi
        else
            warn "Local snapshots: None found"
        fi
    else
        warn "Local snapshots directory not found: $SNAPSHOT_DIR"
    fi
}

verify_github() {
    log "=== Verifying GitHub (Tier 1) ==="
    
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "none")
    if [[ "$REMOTE_URL" == "none" ]]; then
        error "No origin remote configured"
        return
    fi
    
    log "Origin: $REMOTE_URL"
    
    # Check if we can reach GitHub
    if git ls-remote --exit-code origin HEAD >/dev/null 2>&1; then
        REMOTE_COMMIT=$(git ls-remote origin HEAD | cut -f1)
        if [[ "$REMOTE_COMMIT" == "$LAST_COMMIT" ]]; then
            ok "GitHub: In sync (commit $REMOTE_COMMIT)"
        else
            warn "GitHub: Diverged (local $LAST_COMMIT, remote $REMOTE_COMMIT)"
        fi
    else
        error "Cannot reach GitHub remote"
    fi
}

verify_assets() {
    log "=== Verifying Repository Assets ==="
    
    # Check vendor directory
    if [[ -d "$REPO_ROOT/vendor" ]]; then
        VENDOR_COUNT=$(find "$REPO_ROOT/vendor" -type f | wc -l)
        ok "Vendor assets: $VENDOR_COUNT files"
    else
        warn "Vendor directory not found"
    fi
    
    # Check models
    if [[ -d "$REPO_ROOT/models" ]]; then
        MODEL_COUNT=$(find "$REPO_ROOT/models" -type f | wc -l)
        ok "Models: $MODEL_COUNT files"
    else
        warn "Models directory not found"
    fi
    
    # Check build-tools
    if [[ -d "$REPO_ROOT/build-tools" ]]; then
        TOOL_COUNT=$(find "$REPO_ROOT/build-tools" -type f | wc -l)
        ok "Build tools: $TOOL_COUNT files"
    else
        warn "Build tools directory not found"
    fi
    
    # Check config
    if [[ -f "$REPO_ROOT/config/default.yaml" ]]; then
        ok "Config template exists"
    else
        error "Config template missing"
    fi
}

verify_bundle() {
    log "=== Verifying Git Bundle Integrity ==="
    
    # Check if we have a recent bundle
    BUNDLE_DIR="/tmp"
    if [[ -f "$BUNDLE_DIR/osint-indep-$(date +%Y-%m-%d)*.bundle" ]]; then
        BUNDLE=$(ls -t "$BUNDLE_DIR"/osint-indep-*.bundle 2>/dev/null | head -1)
        if git bundle verify "$BUNDLE" >/dev/null 2>&1; then
            ok "Recent bundle valid: $(basename "$BUNDLE")"
        else
            error "Recent bundle corrupt: $(basename "$BUNDLE")"
        fi
    else
        warn "No recent bundle found in /tmp"
    fi
}

main() {
    log "=== BACKUP VERIFICATION STARTED ==="
    log "Repository: $REPO_ROOT"
    log "Current commit: $LAST_COMMIT"
    echo
    
    verify_github
    echo
    verify_gdrive
    echo
    verify_local
    echo
    verify_assets
    echo
    verify_bundle
    echo
    
    log "=== VERIFICATION COMPLETE ==="
    log "Errors: $ERRORS | Warnings: $WARNINGS"
    
    if [[ $ERRORS -gt 0 ]]; then
        log "❌ VERIFICATION FAILED - $ERRORS critical errors"
        exit 1
    elif [[ $WARNINGS -gt 0 ]]; then
        log "⚠ VERIFICATION PASSED WITH WARNINGS - $WARNINGS warnings"
        exit 0
    else
        log "✅ ALL CHECKS PASSED"
        exit 0
    fi
}

main "$@"