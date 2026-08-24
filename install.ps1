# =====================================================================
#  OSINTNeoAi — Official One-Line Windows Installer & Quickstart
#  Run via: irm https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/install.ps1 | iex
# =====================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   🚀 Installing & Launching OSINTNeoAi Master Intelligence CLI" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

$RepoUrl = "https://github.com/Tonypost949/OsintNeoAi.git"
$InstallDir = Join-Path $HOME "OsintNeoAi"

# 1. Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Git is not installed. Please install Git: winget install --id Git.Git -e" -ForegroundColor Red
    exit 1
}

# 2. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Python is not installed. Please install Python 3.10+: winget install Python.Python.3.12" -ForegroundColor Red
    exit 1
}

# 3. Clone or Update Repo
if (Test-Path $InstallDir) {
    Write-Host "[*] Updating existing installation at $InstallDir..." -ForegroundColor Yellow
    Set-Location $InstallDir
    git pull origin main
} else {
    Write-Host "[*] Cloning OSINTNeoAi to $InstallDir..." -ForegroundColor Yellow
    git clone $RepoUrl $InstallDir
    Set-Location $InstallDir
}

# 4. Create Virtual Environment
$VenvDir = Join-Path $InstallDir "cli\.venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "[*] Creating isolated Python virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

# 5. Install Dependencies
Write-Host "[*] Installing & verifying dependencies..." -ForegroundColor Yellow
& $PythonExe -m pip install --upgrade pip --quiet
$ReqFile = Join-Path $InstallDir "cli\requirements.txt"
if (Test-Path $ReqFile) {
    & $PythonExe -m pip install -r $ReqFile --quiet
}

# 6. Create Global Command Wrapper (osintneoai.cmd) in User Path
$BinDir = Join-Path $HOME ".local\bin"
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

$CmdWrapper = Join-Path $BinDir "osintneoai.cmd"
$CmdContent = "@echo off`n`"$PythonExe`" `"$InstallDir\cli\cli.py`" %*"
Set-Content -Path $CmdWrapper -Value $CmdContent -Force

# Add to user PATH if not present
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$BinDir", "User")
    $env:PATH = "$env:PATH;$BinDir"
}

Write-Host "`n[+] Installation Complete!" -ForegroundColor Green
Write-Host "👉 You can now run 'osintneoai' or 'osintneoai chat' from ANY terminal.`n" -ForegroundColor Cyan

# 7. Start Interactive Session
Write-Host "[*] Starting interactive CLI session...`n" -ForegroundColor Green
& $PythonExe (Join-Path $InstallDir "cli\cli.py") chat
