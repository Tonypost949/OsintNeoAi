#!/usr/bin/env bash
# ==============================================================================
# Azure for Students ($100/yr + 750h B1s/B2pts ARM) Automated VM Provisioner
# Requires: Azure CLI (az)
# ==============================================================================

set -euo pipefail

RESOURCE_GROUP="rg-osintneoai-student"
LOCATION="eastus"
VM_NAME="vm-osintneoai-compute"
VM_SIZE="Standard_B2pts_v2" # ARM-based 2 vCPU, 1GB RAM (Free Tier eligible under student allocations)
ADMIN_USER="osintadmin"

echo "⚡ Provisioning Azure for Students Headless Node..."
echo "Resource Group: ${RESOURCE_GROUP} (${LOCATION})"
echo "VM Size: ${VM_SIZE} | Admin: ${ADMIN_USER}"

# 1. Create Resource Group
if ! az group show --name "${RESOURCE_GROUP}" &> /dev/null; then
    az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}"
fi

# 2. Deploy Linux VM
az vm create \
    --resource-group "${RESOURCE_GROUP}" \
    --name "${VM_NAME}" \
    --image "Canonical:ubuntu-24_04-lts:server-arm64:latest" \
    --size "${VM_SIZE}" \
    --admin-username "${ADMIN_USER}" \
    --generate-ssh-keys \
    --public-ip-sku Standard

# 3. Open required ports (SSH + Port 5052/ttyd)
az vm open-port --port 22 --resource-group "${RESOURCE_GROUP}" --name "${VM_NAME}" --priority 1001
az vm open-port --port 5052 --resource-group "${RESOURCE_GROUP}" --name "${VM_NAME}" --priority 1002

IP_ADDRESS=$(az vm list-ip-addresses --resource-group "${RESOURCE_GROUP}" --name "${VM_NAME}" --query "[0].virtualMachine.network.publicIpAddresses[0].ipAddress" -o tsv)

echo "=========================================================="
echo "✅ Azure Node Deployed Successfully!"
echo "Public IP: ${IP_ADDRESS}"
echo "Connect with: ssh ${ADMIN_USER}@${IP_ADDRESS}"
echo "Run bootstrap: ssh ${ADMIN_USER}@${IP_ADDRESS} 'curl -sSL https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/scripts/deploy_headless_compute.sh | bash'"
echo "=========================================================="
