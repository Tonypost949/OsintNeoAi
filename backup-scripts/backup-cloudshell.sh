#!/bin/bash
set -euo pipefail

# Cloud Shell Backup Script
# Uses GCE backup VM + gcloud alpha cloud-shell with access tokens
# Bypasses ADC quota project issue by using CLOUDSDK_AUTH_ACCESS_TOKEN

PROJECT_ID="project-743aab84-f9a5-4ec7-954"
BACKUP_DIR="/home/anthonymichaeldimarcello/cloudshell-backups"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

backup_account() {
  local ACCOUNT=$1
  local LABEL=$2
  local TOKEN=$3
  local FILE="$BACKUP_DIR/cloudshell-backup-${LABEL}-${DATE}.tar.gz"

  echo "=== BACKING UP $LABEL ($ACCOUNT) ==="

  export CLOUDSDK_AUTH_ACCESS_TOKEN="$TOKEN"

  # Create tarball via Cloud Shell SSH
  gcloud alpha cloud-shell ssh --account="$ACCOUNT" \
    --command="tar czf /tmp/backup-${LABEL}.tar.gz -C / home" \
    --force-key-file-overwrite

  # Download via Cloud Shell SCP
  gcloud alpha cloud-shell scp --account="$ACCOUNT" \
    "cloudshell:/tmp/backup-${LABEL}.tar.gz" "localhost:${FILE}" \
    --force-key-file-overwrite

  echo "Backup saved: $(ls -lh "$FILE")"
  echo "=== DONE: $LABEL ==="
}

# Tokens are passed as args or set via env
if [ $# -ge 3 ]; then
  backup_account "$1" "$2" "$3"
else
  echo "Usage: $0 <email> <label> <access_token>"
  echo "  Or set CLOUDSDK_AUTH_ACCESS_TOKEN then run backup_account"
  echo "Tokens: get from 'gcloud auth print-access-token --account=<email>'"
fi
