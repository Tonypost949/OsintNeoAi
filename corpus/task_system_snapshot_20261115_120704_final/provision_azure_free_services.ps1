# Autonomous Free Services Provisioning Script
# Target: Azure Free Services Blade (https://portal.azure.com/#view/Microsoft_Azure_Billing/FreeServicesBlade)
# Subscription: c7c9b67b-33c7-4201-ada2-ae6c0c42fe7e

$ErrorActionPreference = "Continue"
$RG = "rg-free-tier-services-westus"
$LOC = "westus"

Write-Host ">>> Creating Resource Group: $RG in $LOC..."
az group create --name $RG --location $LOC

Write-Host ">>> Registering Core Free Tier Resource Providers..."
az provider register --namespace Microsoft.CognitiveServices
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.DocumentDB
az provider register --namespace Microsoft.Search

Write-Host ">>> 1. Provisioning App Service Plan (SKU F1 Free)..."
az appservice plan create --name "asp-free-f1" --resource-group $RG --location $LOC --sku F1 --is-linux $false

Write-Host ">>> 2. Provisioning Azure Storage Account (Standard LRS Free Tier)..."
$rand = Get-Random -Minimum 10000 -Maximum 99999
$stName = "stfree$rand"
az storage account create --name $stName --resource-group $RG --location $LOC --sku Standard_LRS --kind StorageV2

Write-Host ">>> 3. Provisioning Azure AI Multi-Service Account (F0 Free)..."
az cognitiveservices account create --name "cog-free-ai" --resource-group $RG --location $LOC --kind CognitiveServices --sku F0 --yes

Write-Host ">>> Azure Free Services Provisioning Completed!"
