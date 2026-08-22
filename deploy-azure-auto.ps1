#!/usr/bin/env pwsh
# OsintNeoAi - Automated Azure Deployment
# Deploys to Azure Container Instances with zero manual Azure CLI steps
# ============================================================

param(
    [string]$GeminiKey,
    [string]$GcpProjectId,
    [string]$CredentialsPath,
    [string]$AzureSubId
)

# If no params, prompt interactively
if (-not $GeminiKey) {
    $GeminiKey = Read-Host "Enter your Gemini API Key"
}
if (-not $GcpProjectId) {
    $GcpProjectId = Read-Host "Enter your GCP Project ID"
}
if (-not $CredentialsPath) {
    $CredentialsPath = Read-Host "Enter path to GCP service account JSON"
}
if (-not $AzureSubId) {
    $AzureSubId = Read-Host "Enter your Azure Subscription ID"
}

$ErrorActionPreference = "Stop"
$WarningPreference = "SilentlyContinue"

# Validate
if (-not (Test-Path $CredentialsPath)) {
    Write-Error "Credentials file not found: $CredentialsPath"
    exit 1
}

$RESOURCE_GROUP = "osintneoai-rg"
$REGISTRY_NAME = "osintneoai$(Get-Random -Minimum 1000 -Maximum 9999)"
$CONTAINER_NAME = "osintneoai"
$INSTANCE_NAME = "osintneoai-$(Get-Random -Minimum 100 -Maximum 999)"
$LOCATION = "eastus"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        OsintNeoAi - Automated Azure Deployment             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Step 1: Azure Login Check
Write-Host "`n[1/7] Checking Azure CLI..." -ForegroundColor Yellow
$currentUser = az account show --query user.name -o tsv 2>$null
if (-not $currentUser) {
    Write-Host "Not logged in. Running: az login" -ForegroundColor Yellow
    az login | Out-Null
}
Write-Host "✓ Logged in as: $currentUser" -ForegroundColor Green

# Step 2: Set Subscription
Write-Host "`n[2/7] Setting Azure subscription..." -ForegroundColor Yellow
az account set --subscription $AzureSubId 2>$null
Write-Host "✓ Subscription set" -ForegroundColor Green

# Step 3: Create Resource Group
Write-Host "`n[3/7] Creating resource group: $RESOURCE_GROUP..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION 2>$null | Out-Null
Write-Host "✓ Resource group ready" -ForegroundColor Green

# Step 4: Create Registry
Write-Host "`n[4/7] Creating container registry: $REGISTRY_NAME..." -ForegroundColor Yellow
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true 2>$null | Out-Null
$REGISTRY_URL = "$REGISTRY_NAME.azurecr.io"
$REGISTRY_USER = $REGISTRY_NAME
$REGISTRY_PASS = $(az acr credential show --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --query "passwords[0].value" -o tsv)
Write-Host "✓ Registry: $REGISTRY_URL" -ForegroundColor Green

# Step 5: Build & Push Image
Write-Host "`n[5/7] Building Docker image..." -ForegroundColor Yellow
$IMAGE_TAG = "$REGISTRY_URL/$CONTAINER_NAME:latest"
docker build -t $IMAGE_TAG . --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}
Write-Host "✓ Image built" -ForegroundColor Green

Write-Host "`n[5b/7] Pushing to registry..." -ForegroundColor Yellow
echo $REGISTRY_PASS | docker login $REGISTRY_URL -u $REGISTRY_USER --password-stdin 2>$null | Out-Null
docker push $IMAGE_TAG --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed"
    exit 1
}
Write-Host "✓ Image pushed" -ForegroundColor Green

# Step 6: Prepare Secrets
Write-Host "`n[6/7] Preparing credentials..." -ForegroundColor Yellow
$GcpCredsJson = Get-Content $CredentialsPath -Raw
$GcpCredsJson = $GcpCredsJson -replace '"', '\"' -replace "`n", "\n"
Write-Host "✓ Credentials loaded" -ForegroundColor Green

# Step 7: Deploy Container
Write-Host "`n[7/7] Deploying to Azure Container Instances..." -ForegroundColor Yellow
az container create `
    --resource-group $RESOURCE_GROUP `
    --name $INSTANCE_NAME `
    --image $IMAGE_TAG `
    --registry-login-username $REGISTRY_USER `
    --registry-login-password $REGISTRY_PASS `
    --dns-name-label $INSTANCE_NAME `
    --ports 10000 `
    --environment-variables `
        PORT=10000 `
        GCP_PROJECT=$GcpProjectId `
        GEMINI_API_KEY=$GeminiKey `
        GOOGLE_CREDENTIALS_JSON=$GcpCredsJson `
    --cpu 2 `
    --memory 4 `
    2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Error "Container deployment failed"
    exit 1
}

Write-Host "✓ Container deployed" -ForegroundColor Green

# Final Info
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    DEPLOYMENT COMPLETE                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n🌐 Your app is live at:" -ForegroundColor Cyan
Write-Host "   http://$INSTANCE_NAME.eastus.azurecontainer.io:10000" -ForegroundColor Yellow

Write-Host "`n📊 Check status:" -ForegroundColor Cyan
Write-Host "   az container show -g $RESOURCE_GROUP -n $INSTANCE_NAME" -ForegroundColor Gray

Write-Host "`n📝 View logs:" -ForegroundColor Cyan
Write-Host "   az container logs -g $RESOURCE_GROUP -n $INSTANCE_NAME" -ForegroundColor Gray

Write-Host "`n🗑️  To delete:" -ForegroundColor Cyan
Write-Host "   az group delete -n $RESOURCE_GROUP" -ForegroundColor Gray

Write-Host "`n✓ Done!`n" -ForegroundColor Green
