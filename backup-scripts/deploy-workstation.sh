#!/bin/bash
set -euo pipefail

# Deploy GCE backup VM for Cloud Shell backups
# This VM serves as a Linux jump box to bypass Windows firewall issues
# with gcloud cloud-shell SSH tunnel (WinError 10053)

PROJECT_ID="project-743aab84-f9a5-4ec7-954"
ZONE="us-central1-a"
VM_NAME="backup-vm"

echo "=== ENABLING APIS (via REST to bypass ADC quota project) ==="
TOKEN=$(gcloud auth print-access-token)
for api in compute.googleapis.com cloudshell.googleapis.com serviceusage.googleapis.com; do
  curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -H "x-goog-user-project: $PROJECT_ID" \
    "https://serviceusage.googleapis.com/v1/projects/$PROJECT_ID/services/$api:enable" > /dev/null
done

echo "=== CREATING FIREWALL RULE ==="
gcloud compute firewall-rules create allow-ssh-backup \
  --project="$PROJECT_ID" \
  --network=default --allow=tcp:22 \
  --source-ranges=0.0.0.0/0 --target-tags=backup-vm 2>/dev/null || true

echo "=== CREATING BACKUP VM ==="
gcloud compute instances create "$VM_NAME" \
  --project="$PROJECT_ID" --zone="$ZONE" \
  --machine-type=e2-micro \
  --boot-disk-size=50 --boot-disk-type=pd-standard \
  --image-family=debian-12 --image-project=debian-cloud \
  --tags=backup-vm \
  --scopes=cloud-platform

echo "=== VM READY ==="
echo "IP: $(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"
echo "SSH: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo ""
echo "Then run: bash backup-scripts/backup-cloudshell.sh <email> <label> <token>"
echo "Get token: gcloud auth print-access-token --account=<email>"
