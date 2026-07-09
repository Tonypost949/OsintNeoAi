#!/bin/bash
set -euo pipefail

# === CONFIG ===
PROJECT_ID="project-743aab84-f9a5-4ec7-954"
BUCKET="gs://backup-project-743aab84-f9a5-4ec7-954/cloudshell-backups/"
DATE=$(date +%Y%m%d)

backup_account() {
  local ACCOUNT=$1
  local LABEL=$2
  echo "=== BACKING UP $LABEL ($ACCOUNT) ==="
  
  gcloud config set account "$ACCOUNT"
  
  # Start Cloud Shell and get SSH info via REST API
  TOKEN=$(gcloud auth print-access-token)
  ENV=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    https://cloudshell.googleapis.com/v1/users/me/environments/default:start)
  
  SSH_HOST=$(echo "$ENV" | python3 -c "import sys,json; print(json.load(sys.stdin)['response']['environment']['sshHost'])")
  SSH_PORT=$(echo "$ENV" | python3 -c "import sys,json; print(json.load(sys.stdin)['response']['environment']['sshPort'])")
  SSH_USER=$(echo "$ENV" | python3 -c "import sys,json; print(json.load(sys.stdin)['response']['environment']['sshUsername'])")
  
  echo "SSH: $SSH_USER@$SSH_HOST:$SSH_PORT"
  
  # Tar home and upload to GCS directly
  ssh -o StrictHostKeyChecking=no -p "$SSH_PORT" "$SSH_USER@$SSH_HOST" \
    "cd ~ && tar czf /tmp/backup.tar.gz --exclude='.cache' . && \
     gsutil cp /tmp/backup.tar.gz $BUCKET/${LABEL}-${DATE}.tar.gz && \
     echo 'UPLOADED'"
  
  echo "=== DONE: $LABEL ==="
}

# Backup each account
backup_account "anthonymichaeldimarcello@gmail.com" "anthonymichaeldimarcello"
backup_account "txtdjdrop@gmail.com" "txtdjdrop"
backup_account "amd949609@gmail.com" "amd949609"
backup_account "osintneoai@gmail.com" "osintneoai"

echo "=== ALL BACKUPS COMPLETE ==="
gsutil ls -l "$BUCKET"
