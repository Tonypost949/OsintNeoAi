<#
.SYNOPSIS
    Automated auditor, installer, and PATH manager for developer CLIs on Windows.
.DESCRIPTION
    Manages uv, Android CLI, Firebase CLI, Google Cloud SDK, and Node.js/npm.
#>

param (
    [switch]$Audit,
    [switch]$Install,
    [switch]$UpdatePath
)

$ErrorActionPreference = "Continue"

$Tools = @{
    "uv"        = "$env:USERPROFILE\.local\bin\uv.exe"
    "android"   = "$env:USERPROFILE\AppData\AndroidCLI\android.exe"
    "node"      = "C:\Program Files\nodejs\node.exe"
    "firebase"  = "$env:APPDATA\npm\firebase.cmd"
    "gcloud"    = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
}

function Audit-Tools {
    Write-Host "=== Developer CLI Audit ===" -ForegroundColor Cyan
    foreach ($name in $Tools.Keys) {
        $path = $Tools[$name]
        $inPath = Get-Command $name -ErrorAction SilentlyContinue
        $exists = Test-Path $path
        
        if ($inPath) {
            Write-Host "[OK] $name : In PATH ($($inPath.Source))" -ForegroundColor Green
        } elseif ($exists) {
            Write-Host "[WARN] $name : Installed at $path (Not in active shell PATH)" -ForegroundColor Yellow
        } else {
            Write-Host "[MISSING] $name : Not found" -ForegroundColor Red
        }
    }
}

function Install-Tools {
    Write-Host "=== Installing Missing Developer CLIs ===" -ForegroundColor Cyan

    # 1. uv
    if (-not (Test-Path $Tools["uv"])) {
        Write-Host "Installing uv..." -ForegroundColor Yellow
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    } else {
        Write-Host "[OK] uv is already installed." -ForegroundColor Green
    }

    # 2. Android CLI
    if (-not (Test-Path $Tools["android"])) {
        Write-Host "Installing Android CLI..." -ForegroundColor Yellow
        powershell -Command "Invoke-WebRequest -Uri 'https://dl.google.com/android/cli/latest/windows_x86_64/install.cmd' -OutFile '$env:TEMP\install_android.cmd'; & '$env:TEMP\install_android.cmd'"
    } else {
        Write-Host "[OK] Android CLI is already installed." -ForegroundColor Green
    }

    # 3. Node.js & npm
    if (-not (Test-Path $Tools["node"])) {
        Write-Host "Installing Node.js via winget..." -ForegroundColor Yellow
        winget install --id OpenJS.NodeJS --silent --accept-source-agreements --accept-package-agreements
    } else {
        Write-Host "[OK] Node.js is already installed." -ForegroundColor Green
    }

    # 4. Firebase CLI
    if (-not (Test-Path $Tools["firebase"])) {
        Write-Host "Installing Firebase CLI via npm..." -ForegroundColor Yellow
        cmd /c "set PATH=C:\Program Files\nodejs;%PATH% && npm install -g firebase-tools"
    } else {
        Write-Host "[OK] Firebase CLI is already installed." -ForegroundColor Green
    }

    # 5. Google Cloud SDK
    if (-not (Test-Path $Tools["gcloud"])) {
        Write-Host "Installing Google Cloud SDK via winget..." -ForegroundColor Yellow
        winget install --id Google.CloudSDK --silent --accept-source-agreements --accept-package-agreements
    } else {
        Write-Host "[OK] Google Cloud SDK is already installed." -ForegroundColor Green
    }

    Update-UserPath
}

function Update-UserPath {
    Write-Host "=== Updating User PATH Registry ===" -ForegroundColor Cyan
    $newDirs = @(
        "$env:USERPROFILE\.local\bin",
        "$env:USERPROFILE\AppData\AndroidCLI",
        "C:\Program Files\nodejs",
        "$env:APPDATA\npm",
        "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
    )

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $added = 0

    foreach ($dir in $newDirs) {
        if (Test-Path $dir) {
            if ($currentPath -notlike "*$dir*") {
                $currentPath = "$dir;$currentPath"
                $added++
                Write-Host "Added to PATH: $dir" -ForegroundColor Green
            }
        }
    }

    if ($added -gt 0) {
        [Environment]::SetEnvironmentVariable("Path", $currentPath, "User")
        Write-Host "User PATH registry updated successfully ($added directories added)." -ForegroundColor Green
    } else {
        Write-Host "User PATH registry is already up to date." -ForegroundColor Green
    }
}

if ($Audit) {
    Audit-Tools
} elseif ($Install) {
    Install-Tools
} elseif ($UpdatePath) {
    Update-UserPath
} else {
    Audit-Tools
}
