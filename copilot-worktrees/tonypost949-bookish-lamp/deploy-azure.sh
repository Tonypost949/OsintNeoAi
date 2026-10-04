#!/bin/bash

# OsintNeoAi Azure Deployment Script
# Usage: bash deploy-azure.sh

set -e

# Configuration
SUBSCRIPTION_ID="f055033f-83fb-4ae9-9c36-be48f0c86158"
REGION="eastus"
RESOURCE_GROUP="osintneoai-rg"
REGISTRY_NAME="osintneoairegistry"  # Must be globally unique (lowercase, no hyphens after first char)
CONTAINER_NAME="osintneoai-app"
IMAGE_NAME="osintneoai:latest"

echo "🚀 Deploying OsintNeoAi to Azure..."
echo "Subscription: $SUBSCRIPTION_ID"
echo "Region: $REGION"
echo "Resource Group: $RESOURCE_GROUP"

# Step 1: Login to Azure
echo "📝 Step 1: Logging in to Azure CLI..."
az login --use-device-code

# Step 2: Set subscription
echo "📝 Step 2: Setting subscription..."
az account set --subscription "$SUBSCRIPTION_ID"

# Step 3: Create resource group
echo "📝 Step 3: Creating resource group..."
az group create --name "$RESOURCE_GROUP" --location "$REGION"

# Step 4: Create container registry
echo "📝 Step 4: Creating Azure Container Registry..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REGISTRY_NAME" \
  --sku Basic \
  --admin-enabled true

# Step 5: Get registry credentials
echo "📝 Step 5: Getting registry credentials..."
REGISTRY_URL=$(az acr show --name "$REGISTRY_NAME" --query loginServer -o tsv)
REGISTRY_USER=$(az acr credential show --name "$REGISTRY_NAME" --query username -o tsv)
REGISTRY_PASS=$(az acr credential show --name "$REGISTRY_NAME" --query "passwords[0].value" -o tsv)

echo "Registry URL: $REGISTRY_URL"
echo "Username: $REGISTRY_USER"

# Step 6: Build and push image to ACR
echo "📝 Step 6: Building and pushing Docker image to ACR..."
az acr build \
  --registry "$REGISTRY_NAME" \
  --image "$IMAGE_NAME" \
  --file Dockerfile \
  .

# Step 7: Deploy to Container Instances
echo "📝 Step 7: Deploying to Azure Container Instances..."
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CONTAINER_NAME" \
  --image "$REGISTRY_URL/$IMAGE_NAME" \
  --registry-login-server "$REGISTRY_URL" \
  --registry-username "$REGISTRY_USER" \
  --registry-password "$REGISTRY_PASS" \
  --ports 10000 \
  --environment-variables \
    PORT=10000 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
  --cpu 2 \
  --memory 2 \
  --restart-policy OnFailure

# Step 8: Get public IP
echo "📝 Step 8: Getting public IP..."
PUBLIC_IP=$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CONTAINER_NAME" \
  --query ipAddress.ip -o tsv)

echo ""
echo "✅ Deployment complete!"
echo "🌐 Access your app at: http://$PUBLIC_IP:10000"
echo ""
echo "To view logs:"
echo "  az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo ""
echo "To stop the container:"
echo "  az container stop --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME"
echo ""
echo "To delete everything:"
echo "  az group delete --name $RESOURCE_GROUP"
