# OsintNeoAi Live Deployment Guide

## Prerequisites
- Azure Student Account (free $100/month credit)
- Azure CLI installed (`az --version` to check)
- Docker installed locally
- Git

## Deploy to Azure (5 minutes)

### Option 1: PowerShell (Windows)
```powershell
cd C:\Users\Amd949609\OsintNeoAi
powershell -ExecutionPolicy Bypass -File deploy-azure.ps1
```

### Option 2: Bash (Mac/Linux)
```bash
cd OsintNeoAi
bash deploy-azure.sh
```

## What happens:
1. Creates Azure Resource Group
2. Creates Azure Container Registry (private Docker repo)
3. Builds your image and pushes to registry
4. Deploys to Azure Container Instances on a **public IP**
5. Gives you a live URL: `http://<PUBLIC-IP>:10000`

## After deployment:
- Share the URL with anyone (phone, PC, tablet)
- Upload documents, run queries, use all tools
- Access logs: `az container logs --resource-group osintneoai-rg --name osintneoai-app`

## Cost estimate (Student account):
- **Free tier**: First $100/month
- Container Instances: ~$0.0000015/second (tiny)
- Container Registry: $5/month (included in free tier)
- **Your cost**: $0 if within free tier

## Scaling to Production:
If you outgrow Container Instances, use:
- **Azure App Service**: Better for long-running apps, auto-scaling
- **Azure Kubernetes Service (AKS)**: For high traffic

## Stop the app (saves money):
```bash
az container stop --resource-group osintneoai-rg --name osintneoai-app
```

## Delete everything:
```bash
az group delete --name osintneoai-rg
```
