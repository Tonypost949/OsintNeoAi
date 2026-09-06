# Automated Azure Student Linux VM Deployer (Region-Specific RG & Multi-SKU Fallback)
param (
    [string]$VmName = "osintneoai-dev-vm",
    [string]$AdminUsername = "osintadmin"
)

$Regions = @("eastus2", "centralus", "westus2", "eastus")
$Sizes = @("Standard_B2s", "Standard_B2ms", "Standard_D2s_v3", "Standard_B1s")

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Provisioning Dedicated Azure VM: $VmName " -ForegroundColor Green
Write-Host " Subscription: Azure for Students                         " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$Deployed = $false
$ActiveRG = ""

foreach ($Region in $Regions) {
    if ($Deployed) { break }
    
    $RG = "rg-osintneoai-$Region"
    Write-Host "[*] Creating Resource Group: $RG in $Region..." -ForegroundColor Yellow
    az group create --name $RG --location $Region --output table
    
    foreach ($Size in $Sizes) {
        Write-Host "    [>] Attempting VM creation: $Size in $Region..."
        
        $CreateOutput = az vm create `
            --resource-group $RG `
            --name $VmName `
            --location $Region `
            --image Ubuntu2204 `
            --size $Size `
            --admin-username $AdminUsername `
            --generate-ssh-keys `
            --public-ip-sku Standard `
            --output json 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[+] Successfully created VM $VmName ($Size) in $Region!" -ForegroundColor Green
            $CreateOutput | Out-File -FilePath "C:\OsintNeoAi\azure_vm_credentials.json" -Encoding utf8
            $Deployed = $true
            $ActiveRG = $RG
            break
        } else {
            Write-Host "    [-] SKU $Size failed in $Region. Trying next..." -ForegroundColor DarkGray
        }
    }
}

if ($Deployed) {
    Write-Host "[*] Opening firewall ports (22, 80, 443, 8080)..."
    az vm open-port --resource-group $ActiveRG --name $VmName --port 22 --priority 1001 --output none
    az vm open-port --resource-group $ActiveRG --name $VmName --port 80 --priority 1002 --output none
    az vm open-port --resource-group $ActiveRG --name $VmName --port 443 --priority 1003 --output none
    az vm open-port --resource-group $ActiveRG --name $VmName --port 8080 --priority 1004 --output none

    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " Azure VM Deployment Complete!                           " -ForegroundColor Green
    Write-Host " Connection info saved to: C:\OsintNeoAi\azure_vm_credentials.json" -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Cyan
} else {
    Write-Host "[!] Failed to deploy VM across all test regions and SKUs." -ForegroundColor Red
}
