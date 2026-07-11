#!/bin/bash
# create-cold-backup.sh - Creates monthly cold storage backup
# Run manually or via monthly cron: 0 3 1 * * /path/to/create-cold-backup.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DATE=$(date +%Y-%m-%d)
COLD_DIR="$REPO_ROOT/../cold-backups/$DATE"
LOG_FILE="$REPO_ROOT/logs/cold-backup-$DATE.log"

mkdir -p "$COLD_DIR"
mkdir -p "$REPO_ROOT/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

main() {
    log "=== COLD STORAGE BACKUP STARTED: $DATE ==="
    
    # 1. Create complete git bundle
    log "Creating full repository bundle..."
    BUNDLE_FILE="$COLD_DIR/osint-indep-full-$DATE.bundle"
    git -C "$REPO_ROOT" bundle create "$BUNDLE_FILE" --all
    
    if git bundle verify "$BUNDLE_FILE" >/dev/null 2>&1; then
        log "Full bundle verified OK"
    else
        log "ERROR: Full bundle verification failed!"
        exit 1
    fi
    
    # 2. Create tarball of vendor/models/build-tools
    log "Archiving large assets..."
    tar -czf "$COLD_DIR/assets-vendor-$DATE.tar.gz" -C "$REPO_ROOT" vendor 2>/dev/null || log "No vendor dir"
    tar -czf "$COLD_DIR/assets-models-$DATE.tar.gz" -C "$REPO_ROOT" models 2>/dev/null || log "No models dir"
    tar -czf "$COLD_DIR/assets-buildtools-$DATE.tar.gz" -C "$REPO_ROOT" build-tools 2>/dev/null || log "No build-tools dir"
    
    # 3. Create manifest
    log "Creating manifest..."
    cat > "$COLD_DIR/MANIFEST.txt" <<EOF
COLD STORAGE BACKUP MANIFEST
Date: $DATE
Git Commit: $(cd "$REPO_ROOT" && git rev-parse HEAD)
Branch: $(cd "$REPO_ROOT" && git branch --show-current)
Repository: $(cd "$REPO_ROOT" && git remote get-url origin)

FILES:
$(ls -la "$COLD_DIR")

VERIFICATION:
Bundle: $(git bundle verify "$BUNDLE_FILE" 2>&1 || echo "FAILED")
Asset vendor: $(test -f "$COLD_DIR/assets-vendor-$DATE.tar.gz" && echo "PRESENT" || echo "MISSING")
Asset models: $(test -f "$COLD_DIR/assets-models-$DATE.tar.gz" && echo "PRESENT" || echo "MISSING")
Asset buildtools: $(test -f "$COLD_DIR/assets-buildtools-$DATE.tar.gz" && echo "PRESENT" || echo "MISSING")

CHECKSUMS:
$(cd "$COLD_DIR" && sha256sum * 2>/dev/null || echo "No files")
EOF
    
    # 4. Calculate checksums
    log "Calculating checksums..."
    (cd "$COLD_DIR" && sha256sum * > "$COLD_DIR/SHA256SUMS.txt")
    
    # 5. Upload to cold storage (S3 Glacier / Backblaze B2)
    log "Uploading to cold storage..."
    
    # AWS S3 Glacier
    if command -v aws >/dev/null 2>&1 && [[ -n "${AWS_S3_COLD_BUCKET:-}" ]]; then
        aws s3 cp "$COLD_DIR" "s3://$AWS_S3_COLD_BUCKET/osint-indep/$DATE/" --recursive --storage-class GLACIER_IR
        log "Uploaded to AWS S3 Glacier"
    fi
    
    # Backblaze B2
    if command -v rclone >/dev/null 2>&1 && rclone listremotes | grep -q "b2-cold:"; then
        rclone copy "$COLD_DIR" "b2-cold:osint-indep-cold/$DATE" --progress
        log "Uploaded to Backblaze B2"
    fi
    
    # Google Cloud Storage (if configured)
    if command -v gsutil >/dev/null 2>&1 && [[ -n "${GCS_COLD_BUCKET:-}" ]]; then
        gsutil -m cp -r "$COLD_DIR" "gs://$GCS_COLD_BUCKET/osint-indep/$DATE/"
        log "Uploaded to Google Cloud Storage"
    fi
    
    log "=== COLD STORAGE BACKUP COMPLETE: $DATE ==="
    log "Local path: $COLD_DIR"
    log "Size: $(du -sh "$COLD_DIR" | cut -f1)"
}

main "$@"