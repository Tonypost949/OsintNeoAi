#!/bin/bash
set -euo pipefail

# Bulk Cloud Shell Backup Script
# Run this from a GCE Linux VM (backup-vm) after deploying via deploy-workstation.sh
# Usage: bash backup-all-accounts.sh <txtdjdrop_token> <osintneoai_token> <amd949609_token>

BACKUP_DIR="/home/anthonymichaeldimarcello/cloudshell-backups"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"

backup_account() {
  local EMAIL=$1
  local LABEL=$2
  local TOKEN=$3
  local FILE="$BACKUP_DIR/cloudshell-backup-${LABEL}-${DATE}.tar.gz"

  echo "=== BACKING UP $LABEL ($EMAIL) ==="

  export CLOUDSDK_AUTH_ACCESS_TOKEN="$TOKEN"

  echo "Creating tarball on Cloud Shell..."
  gcloud alpha cloud-shell ssh --account="$EMAIL" \
    --command="tar czf /tmp/backup-${LABEL}.tar.gz -C / home 2>/dev/null; echo 'TAR_EXIT:'$?" \
    --force-key-file-overwrite

  echo "Downloading backup..."
  gcloud alpha cloud-shell scp --account="$EMAIL" \
    "cloudshell:/tmp/backup-${LABEL}.tar.gz" "localhost:${FILE}" \
    --force-key-file-overwrite

  if [ -f "$FILE" ]; then
    echo "OK: $(ls -lh "$FILE")"
  else
    echo "FAIL: $LABEL"
  fi
  echo ""
}

# Accounts to backup: email, label, token
backup_account "txtdjdrop@gmail.com" "txtdjdrop" "${1:-}"
backup_account "osintneoai@gmail.com" "osintneoai" "${2:-}"
backup_account "amd949609@gmail.com" "amd949609" "${3:-}"

echo "=== ALL BACKUPS ==="
ls -lh "$BACKUP_DIR/"
