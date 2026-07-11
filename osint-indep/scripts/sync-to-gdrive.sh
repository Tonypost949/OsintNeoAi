#!/bin/bash
# sync-to-gdrive.sh - Sync to Google Drive sharedall drive
# Requires: rclone configured with "gdrive-sharedall" remote

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_STAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$REPO_ROOT/logs/sync-gdrive-$(date +%Y%m%d).log"

mkdir -p "$REPO_ROOT/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

check_rclone() {
    if ! rclone listremotes | grep -q "gdrive-sharedall:"; then
        log "ERROR: rclone remote 'gdrive-sharedall:' not configured"
        log "Run: rclone config"
        return 1
    fi
    return 0
}

sync_latest() {
    log "Syncing repository mirror to gdrive-sharedall:osint-indep-backup/latest..."
    
    rclone sync "$REPO_ROOT" "gdrive-sharedall:osint-indep-backup/latest" \
        --progress \
        --log-file="$LOG_FILE" \
        --log-level=INFO \
        --exclude=".git/objects/pack/*.pack" \
        --exclude="__pycache__/**" \
        --exclude="*.pyc" \
        --exclude="node_modules/**" \
        --exclude=".pytest_cache/**" \
        --exclude="*.log" \
        --exclude="venv/**" \
        --exclude=".venv/**" \
        --transfers=4 \
        --checkers=8 \
        --retries=3 \
        --low-level-retries=10 \
        --max-size=10G
}

sync_assets() {
    log "Syncing large assets..."
    
    for asset_dir in vendor models build-tools; do
        if [ -d "$REPO_ROOT/$asset_dir" ]; then
            log "Syncing $asset_dir..."
            rclone sync "$REPO_ROOT/$asset_dir" \
                "gdrive-sharedall:osint-indep-backup/latest/$asset_dir" \
                --progress \
                --log-file="$LOG_FILE" \
                --transfers=4 \
                --checkers=8 \
                --retries=3
        else
            log "Skipping $asset_dir (not found)"
        fi
    done
}

create_snapshot() {
    log "Creating git bundle snapshot..."
    cd "$REPO_ROOT"
    git bundle create "/tmp/osint-indep-$DATE_STAMP.bundle" --all
    
    log "Uploading snapshot..."
    rclone copy "/tmp/osint-indep-$DATE_STAMP.bundle" \
        "gdrive-sharedall:osint-indep-backup/snapshots/$DATE_STAMP.bundle" \
        --log-file="$LOG_FILE"
}

cleanup_old() {
    log "Cleaning up old snapshots (keep 30 daily, 12 monthly, 7 yearly)..."
    
    # This is complex deletion logic - for now just log
    rclone lsl "gdrive-sharedall:osint-indep-backup/snapshots" \
        --max-age=30d \
        2>&1 | head -20 | while read line; do
        log "Would delete: $line"
    done
}

main() {
    log "=== GOOGLE DRIVE SYNC STARTED ==="
    log "Timestamp: $TIMESTAMP"
    
    check_rclone || exit 1
    sync_latest
    sync_assets
    create_snapshot
    cleanup_old
    
    log "=== GOOGLE DRIVE SYNC COMPLETE ==="
}

main "$@"