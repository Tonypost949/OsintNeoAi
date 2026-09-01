# Auto-Deploy to Azure Cloud Webhook App
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 Deploying OSINTNeoAi 24/7 Cloud Engine" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
az.cmd webapp deploy --resource-group neoai-rg --name osintneoai-app-949 --src-path "$CurrentDir" --type zip

Write-Host "`n✅ Cloud Deployment Complete!" -ForegroundColor Green
Write-Host "Webhook URL: https://osintneoai-app-949.azurewebsites.net/webhook"
Write-Host "Verify Token: makaveli_osint_verify_2026"
pause
