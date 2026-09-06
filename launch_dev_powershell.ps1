# Universal Visual Studio Developer PowerShell Auto-Detector
# Auto-detects Visual Studio 2026 or 2022 and loads C++ x64 build toolchain

$VsPath = ""
if (Test-Path "${env:ProgramFiles}\Microsoft Visual Studio\2026\Community") {
    $VsPath = "${env:ProgramFiles}\Microsoft Visual Studio\2026\Community"
} elseif (Test-Path "${env:ProgramFiles}\Microsoft Visual Studio\vNext\Community") {
    $VsPath = "${env:ProgramFiles}\Microsoft Visual Studio\vNext\Community"
} else {
    $VsPath = "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community"
}

$DevShellDll = "$VsPath\Common7\Tools\Microsoft.VisualStudio.DevShell.dll"

if (Test-Path $DevShellDll) {
    Import-Module $DevShellDll
    Enter-VsDevShell -VsInstallPath $VsPath -SkipAutomaticLocation -DevCmdArguments "-arch=x64 -host_arch=x64"
}

Set-Location C:\OsintNeoAi
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Visual Studio Developer PowerShell (x64) Ready!      " -ForegroundColor Green
Write-Host "  VS Target Path: $VsPath                               " -ForegroundColor Yellow
Write-Host "  Working Directory: C:\OsintNeoAi                      " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
