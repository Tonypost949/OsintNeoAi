#!/bin/bash
# daily-sync.sh - Runs via cron at 2 AM daily

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOG_FILE="$REPO_ROOT/logs/daily-sync-$(date +%Y%m%d).log"

mkdir -p "$REPO_ROOT/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

main() {
    log "=== DAILY SYNC STARTED ==="
    
    # 1. Pull latest from GitHub (ensure we have latest)
    log "Pulling from GitHub..."
    cd "$REPO_ROOT"
    git fetch origin
    git status
    
    # 2. Verify backups before sync
    log "Verifying current backups..."
    if ! "$REPO_ROOT/scripts/verify-backups.sh" >> "$LOG_FILE" 2>&1; then
        log "WARNING: Backup verification failed, continuing anyway"
    fi
    
    # 3. Full sync to all tiers
    log "Running full sync..."
    "$REPO_ROOT/scripts/sync-all.sh" >> "$LOG_FILE" 2>&1
    
    # 4. Verify assets
    log "Verifying assets..."
    "$REPO_ROOT/scripts/verify-assets.sh" >> "$LOG_FILE" 2>&1
    
    # 5. Health check
    log "Running health check..."
    python -m scripts.health_check >> "$LOG_FILE" 2>&1 || log "Health check had issues"
    
    # 6. Clean old logs (keep 30 days)
    find "$REPO_ROOT/logs" -name "*.log" -mtime +30 -delete
    
    log "=== DAILY SYNC COMPLETE ==="
}

main "$@"