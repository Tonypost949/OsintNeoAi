# Prepare distribution zip package for OsintNeoAi
$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\OsintNeoAi"
$DistDir = "$ProjectRoot\dist"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ZipTarget = "$DistDir\OsintNeoAi_$Timestamp.zip"
$ZipLatest = "$DistDir\OsintNeoAi_latest.zip"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Packaging OsintNeoAi Deployment Archive  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Project Root : $ProjectRoot"
Write-Host "Output Target: $ZipTarget"

if (!(Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}

$ItemsToZip = @(
    "$ProjectRoot\manifest.json",
    "$ProjectRoot\package.json",
    "$ProjectRoot\README.md",
    "$ProjectRoot\scripts"
) | Where-Object { Test-Path $_ }

Compress-Archive -Path $ItemsToZip -DestinationPath $ZipTarget -Force
Copy-Item -Path $ZipTarget -Destination $ZipLatest -Force

Write-Host "[+] Archive created successfully:" -ForegroundColor Green
Write-Host "    - $ZipTarget"
Write-Host "    - $ZipLatest"
Write-Host "==========================================" -ForegroundColor Cyan
