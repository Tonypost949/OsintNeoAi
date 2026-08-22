# Azure Deployment Script for OsintNeoAi
# Fill in YOUR credentials below, then run this script
# ============================================================

# FILL THESE IN:
$GEMINI_API_KEY = "YOUR_NEW_GEMINI_API_KEY_HERE"
$GCP_PROJECT_ID = "YOUR_GCP_PROJECT_ID_HERE"
$GCP_CREDENTIALS_JSON_PATH = "C:\path\to\your\service-account-key.json"
$AZURE_SUBSCRIPTION_ID = "YOUR_AZURE_SUBSCRIPTION_ID_HERE"
$AZURE_RESOURCE_GROUP = "osintneoai-rg"
$AZURE_REGISTRY_NAME = "osintneoairegistry"
$AZURE_CONTAINER_NAME = "osintneoai-container"
$AZURE_INSTANCE_NAME = "osintneoai-instance"
$AZURE_LOCATION = "eastus"

# ============================================================
# Validation
# ============================================================

if ($GEMINI_API_KEY -eq "YOUR_NEW_GEMINI_API_KEY_HERE") {
    Write-Error "ERROR: You must fill in GEMINI_API_KEY"
    exit 1
}

if ($GCP_PROJECT_ID -eq "YOUR_GCP_PROJECT_ID_HERE") {
    Write-Error "ERROR: You must fill in GCP_PROJECT_ID"
    exit 1
}

if ($AZURE_SUBSCRIPTION_ID -eq "YOUR_AZURE_SUBSCRIPTION_ID_HERE") {
    Write-Error "ERROR: You must fill in AZURE_SUBSCRIPTION_ID"
    exit 1
}

if (-not (Test-Path $GCP_CREDENTIALS_JSON_PATH)) {
    Write-Error "ERROR: GCP credentials JSON not found at $GCP_CREDENTIALS_JSON_PATH"
    exit 1
}

Write-Host "✓ All credentials validated. Starting deployment..." -ForegroundColor Green

# ============================================================
# Step 1: Login to Azure
# ============================================================

Write-Host "`n[1/6] Logging into Azure..." -ForegroundColor Cyan
az account set --subscription $AZURE_SUBSCRIPTION_ID
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to set Azure subscription. Make sure you're logged in: az login"
    exit 1
}

# ============================================================
# Step 2: Create Resource Group
# ============================================================

Write-Host "[2/6] Creating resource group: $AZURE_RESOURCE_GROUP" -ForegroundColor Cyan
az group create `
    --name $AZURE_RESOURCE_GROUP `
    --location $AZURE_LOCATION

# ============================================================
# Step 3: Create Container Registry
# ============================================================

Write-Host "[3/6] Creating Azure Container Registry: $AZURE_REGISTRY_NAME" -ForegroundColor Cyan
az acr create `
    --resource-group $AZURE_RESOURCE_GROUP `
    --name $AZURE_REGISTRY_NAME `
    --sku Basic `
    --admin-enabled true

if ($LASTEXITCODE -ne 0) {
    Write-Host "Registry may already exist. Continuing..." -ForegroundColor Yellow
}

# Get registry login credentials
$REGISTRY_URL = "$AZURE_REGISTRY_NAME.azurecr.io"
$REGISTRY_USERNAME = $AZURE_REGISTRY_NAME
$REGISTRY_PASSWORD = $(az acr credential show --resource-group $AZURE_RESOURCE_GROUP --name $AZURE_REGISTRY_NAME --query "passwords[0].value" -o tsv)

Write-Host "Registry URL: $REGISTRY_URL" -ForegroundColor Green

# ============================================================
# Step 4: Build and Push Docker Image
# ============================================================

Write-Host "[4/6] Building Docker image..." -ForegroundColor Cyan
$IMAGE_TAG = "$REGISTRY_URL/osintneoai:latest"

docker build -t $IMAGE_TAG .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}

Write-Host "[4b/6] Logging into Azure Container Registry..." -ForegroundColor Cyan
docker login $REGISTRY_URL -u $REGISTRY_USERNAME -p $REGISTRY_PASSWORD

Write-Host "[4c/6] Pushing image to registry..." -ForegroundColor Cyan
docker push $IMAGE_TAG
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed"
    exit 1
}

Write-Host "✓ Image pushed to $IMAGE_TAG" -ForegroundColor Green

# ============================================================
# Step 5: Read GCP Credentials
# ============================================================

Write-Host "[5/6] Reading GCP credentials..." -ForegroundColor Cyan
$GCP_CREDENTIALS_JSON = Get-Content $GCP_CREDENTIALS_JSON_PATH -Raw
$GCP_CREDENTIALS_JSON_ESCAPED = $GCP_CREDENTIALS_JSON -replace '"', '\"' -replace "`n", "\n"

# ============================================================
# Step 6: Deploy to Azure Container Instances
# ============================================================

Write-Host "[6/6] Deploying to Azure Container Instances..." -ForegroundColor Cyan
az container create `
    --resource-group $AZURE_RESOURCE_GROUP `
    --name $AZURE_INSTANCE_NAME `
    --image $IMAGE_TAG `
    --registry-login-username $REGISTRY_USERNAME `
    --registry-login-password $REGISTRY_PASSWORD `
    --dns-name-label osintneoai `
    --ports 10000 `
    --environment-variables `
        PORT=10000 `
        GCP_PROJECT=$GCP_PROJECT_ID `
        GEMINI_API_KEY=$GEMINI_API_KEY `
        GOOGLE_CREDENTIALS_JSON=$GCP_CREDENTIALS_JSON_ESCAPED `
    --cpu 2 `
    --memory 4

if ($LASTEXITCODE -ne 0) {
    Write-Error "Container deployment failed"
    exit 1
}

# ============================================================
# Success
# ============================================================

Write-Host "`n✓ Deployment complete!" -ForegroundColor Green
Write-Host "`nYour app is now running at:" -ForegroundColor Cyan
Write-Host "http://osintneoai.eastus.azurecontainer.io:10000" -ForegroundColor Yellow

Write-Host "`nTo check status:" -ForegroundColor Cyan
Write-Host "az container show --resource-group $AZURE_RESOURCE_GROUP --name $AZURE_INSTANCE_NAME" -ForegroundColor Gray

Write-Host "`nTo view logs:" -ForegroundColor Cyan
Write-Host "az container logs --resource-group $AZURE_RESOURCE_GROUP --name $AZURE_INSTANCE_NAME" -ForegroundColor Gray
