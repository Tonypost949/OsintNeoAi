#!/usr/bin/env bash
# ==============================================================================
# DigitalOcean ($200 Student Pack Credit) Ingestion Relay Provisioner
# Requires: doctl CLI or DigitalOcean Personal Access Token
# ==============================================================================

set -euo pipefail

DROPLET_NAME="do-osintneoai-relay"
REGION="nyc3"
IMAGE="ubuntu-24-04-x64"
SIZE="s-1vcpu-1gb" # $6/mo (uses $200 student credit, ~33 months run time)

echo "⚡ Provisioning DigitalOcean Student Droplet..."
echo "Droplet: ${DROPLET_NAME} | Region: ${REGION} | Size: ${SIZE}"

if command -v doctl &> /dev/null; then
    doctl compute droplet create "${DROPLET_NAME}" \
        --region "${REGION}" \
        --image "${IMAGE}" \
        --size "${SIZE}" \
        --enable-monitoring \
        --wait
    echo "✅ DigitalOcean Droplet created successfully!"
else
    echo "[-] doctl CLI not found. You can deploy directly in DigitalOcean Console:"
    echo "• Image: Ubuntu 24.04 LTS"
    echo "• Plan: Basic ($6/mo - 1GB RAM / 1 vCPU)"
    echo "• User Data: Paste content of scripts/deploy_headless_compute.sh"
fi
