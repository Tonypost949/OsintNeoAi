#!/bin/bash
# sync-all.sh - Sync repository to all backup tiers
# Runs on post-commit hook and daily cron

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
DATE_STAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$REPO_ROOT/logs/sync-all-$(date +%Y%m%d).log"

mkdir -p "$REPO_ROOT/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Create git bundle
create_bundle() {
    log "Creating git bundle..."
    cd "$REPO_ROOT"
    git bundle create "/tmp/osint-indep-$DATE_STAMP.bundle" --all
    log "Bundle created: /tmp/osint-indep-$DATE_STAMP.bundle"
}

# Sync to Google Drive (Tier 2)
sync_gdrive() {
    log "=== Syncing to Google Drive (Tier 2) ==="
    
    if ! rclone listremotes | grep -q "gdrive-sharedall:"; then
        log "WARNING: gdrive-sharedall remote not configured, skipping"
        return 0
    fi
    
    # Sync latest (mirror)
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
    
    # Create dated snapshot
    rclone copy "/tmp/osint-indep-$DATE_STAMP.bundle" \
        "gdrive-sharedall:osint-indep-backup/snapshots/$DATE_STAMP.bundle" \
        --log-file="$LOG_FILE"
    
    # Cleanup old snapshots (keep 30 daily, 12 monthly, 7 yearly)
    rclone delete "gdrive-sharedall:osint-indep-backup/snapshots" \
        --min-age=30d \
        --dry-run 2>&1 | grep -v "monthly\|yearly" | head -20
    
    log "Google Drive sync complete"
}

# Sync to Local (Tier 3)
sync_local() {
    log "=== Syncing to Local Backup (Tier 3) ==="
    
    LOCAL_DIR="/mnt/c/osint-indep-backup/latest"
    if [ ! -d "$LOCAL_DIR" ]; then
        LOCAL_DIR="C:/osint-indep-backup/latest"
    fi
    
    mkdir -p "$LOCAL_DIR"
    
    # Use rsync if available, otherwise cp
    if command -v rsync &> /dev/null; then
        rsync -av --delete \
            --exclude='.git/objects/pack/*.pack' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='node_modules' \
            --exclude='.pytest_cache' \
            --exclude='*.log' \
            --exclude='venv' \
            --exclude='.venv' \
            "$REPO_ROOT/" "$LOCAL_DIR/" \
            2>&1 | tee -a "$LOG_FILE"
    else
        # Windows robocopy fallback
        if command -v robocopy &> /dev/null; then
            robocopy "$REPO_ROOT" "$LOCAL_DIR" /MIR /XD ".git/objects/pack" "__pycache__" "node_modules" ".pytest_cache" "venv" ".venv" /XF "*.log" "*.pyc" /R:3 /W:5 /LOG+:"$LOG_FILE"
        else
            cp -r "$REPO_ROOT"/* "$LOCAL_DIR/" 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    # Write timestamp
    echo "$TIMESTAMP" > "$LOCAL_DIR/.backup_timestamp"
    
    # Create monthly snapshot
    SNAPSHOT_DIR="/mnt/c/osint-indep-backup/snapshots/$DATE_STAMP"
    if [ ! -d "$SNAPSHOT_DIR" ]; then
        SNAPSHOT_DIR="C:/osint-indep-backup/snapshots/$DATE_STAMP"
    fi
    mkdir -p "$SNAPSHOT_DIR"
    cp "/tmp/osint-indep-$DATE_STAMP.bundle" "$SNAPSHOT_DIR/"
    
    log "Local backup complete: $LOCAL_DIR"
}

# Sync vendor assets (frontend deps, models, build tools)
sync_assets() {
    log "=== Syncing Large Assets (Tier 2) ==="
    
    if ! rclone listremotes | grep -q "gdrive-sharedall:"; then
        log "WARNING: gdrive-sharedall not configured, skipping asset sync"
        return 0
    fi
    
    # Vendor frontend dependencies
    if [ -d "$REPO_ROOT/vendor" ]; then
        rclone sync "$REPO_ROOT/vendor" "gdrive-sharedall:osint-indep-backup/latest/vendor" \
            --progress --log-file="$LOG_FILE" --transfers=4
    fi
    
    # Models
    if [ -d "$REPO_ROOT/models" ]; then
        rclone sync "$REPO_ROOT/models" "gdrive-sharedall:osint-indep-backup/latest/models" \
            --progress --log-file="$LOG_FILE" --transfers=2
    fi
    
    # Build tools
    if [ -d "$REPO_ROOT/build-tools" ]; then
        rclone sync "$REPO_ROOT/build-tools" "gdrive-sharedall:osint-indep-backup/latest/build-tools" \
            --progress --log-file="$LOG_FILE"
    fi
    
    log "Asset sync complete"
}

main() {
    log "=== FULL BACKUP SYNC STARTED ==="
    log "Repository: $REPO_ROOT"
    log "Timestamp: $TIMESTAMP"
    
    create_bundle
    sync_gdrive
    sync_local
    sync_assets
    
    log "=== ALL BACKUP TIERS SYNCED ==="
    log "Next: Run ./scripts/verify-backups.sh to confirm"
}

main "$@"