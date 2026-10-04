# OsintNeoAi Azure Deployment Script (PowerShell)
# Run: powershell -ExecutionPolicy Bypass -File deploy-azure.ps1

param(
    [string]$SubscriptionId = "f055033f-83fb-4ae9-9c36-be48f0c86158",
    [string]$Region = "eastus",
    [string]$ResourceGroup = "osintneoai-rg",
    [string]$RegistryName = "osintneoairegistry$(Get-Random -Minimum 1000 -Maximum 9999)",
    [string]$ContainerName = "osintneoai-app"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying OsintNeoAi to Azure..." -ForegroundColor Cyan
Write-Host "Subscription: $SubscriptionId"
Write-Host "Region: $Region"
Write-Host "Resource Group: $ResourceGroup"
Write-Host "Registry: $RegistryName"
Write-Host ""

# Step 1: Login
Write-Host "📝 Step 1: Logging in to Azure..." -ForegroundColor Yellow
az login --use-device-code

# Step 2: Set subscription
Write-Host "📝 Step 2: Setting subscription..." -ForegroundColor Yellow
az account set --subscription $SubscriptionId

# Step 3: Create resource group
Write-Host "📝 Step 3: Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Region

# Step 4: Create container registry
Write-Host "📝 Step 4: Creating Azure Container Registry..." -ForegroundColor Yellow
az acr create `
  --resource-group $ResourceGroup `
  --name $RegistryName `
  --sku Basic `
  --admin-enabled true

# Step 5: Get registry details
Write-Host "📝 Step 5: Getting registry credentials..." -ForegroundColor Yellow
$RegistryUrl = az acr show --name $RegistryName --query loginServer -o tsv
$RegistryUser = az acr credential show --name $RegistryName --query username -o tsv
$RegistryPass = az acr credential show --name $RegistryName --query "passwords[0].value" -o tsv

Write-Host "Registry URL: $RegistryUrl" -ForegroundColor Green
Write-Host "Username: $RegistryUser" -ForegroundColor Green

# Step 6: Build and push
Write-Host "📝 Step 6: Building and pushing Docker image..." -ForegroundColor Yellow
az acr build `
  --registry $RegistryName `
  --image "osintneoai:latest" `
  --file Dockerfile `
  .

# Step 7: Deploy to Container Instances
Write-Host "📝 Step 7: Deploying to Container Instances..." -ForegroundColor Yellow
az container create `
  --resource-group $ResourceGroup `
  --name $ContainerName `
  --image "$RegistryUrl/osintneoai:latest" `
  --registry-login-server $RegistryUrl `
  --registry-username $RegistryUser `
  --registry-password $RegistryPass `
  --ports 10000 `
  --environment-variables `
    PORT=10000 `
    ENVIRONMENT=production `
    LOG_LEVEL=INFO `
  --cpu 2 `
  --memory 2 `
  --restart-policy OnFailure

# Step 8: Get public IP
Write-Host "📝 Step 8: Getting public IP..." -ForegroundColor Yellow
$PublicIp = az container show `
  --resource-group $ResourceGroup `
  --name $ContainerName `
  --query ipAddress.ip -o tsv

Write-Host ""
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "🌐 Access your app at: http://$PublicIp`:10000" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:     az container logs --resource-group $ResourceGroup --name $ContainerName"
Write-Host "  Stop:          az container stop --resource-group $ResourceGroup --name $ContainerName"
Write-Host "  Start:         az container restart --resource-group $ResourceGroup --name $ContainerName"
Write-Host "  Delete all:    az group delete --name $ResourceGroup"
