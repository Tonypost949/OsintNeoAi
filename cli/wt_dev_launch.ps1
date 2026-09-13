# Modern Windows Terminal Launcher for OsintNeoAi DevShell (Zero-Lag Bracketed Paste)
[CmdletBinding()]
param(
    [string]$TabName = "OsintNeoAi VS2022 + AGY",
    [switch]$SplitPane
)

$wtExe = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe"
if (-not (Test-Path $wtExe)) {
    $cmd = Get-Command wt.exe -ErrorAction SilentlyContinue
    if ($cmd) { $wtExe = $cmd.Source }
}

if (Test-Path $wtExe) {
    Write-Host "🚀 Launching modern Windows Terminal with ConPTY & bracketed paste..." -ForegroundColor Green
    if ($SplitPane) {
        Start-Process $wtExe -ArgumentList "-p `"$TabName`" -d `"C:\OsintNeoAi`" `; split-pane -p `"OsintNeoAi VS2022 + AGY`" -d `"C:\OsintNeoAi`""
    } else {
        Start-Process $wtExe -ArgumentList "-p `"$TabName`" -d `"C:\OsintNeoAi`""
    }
} else {
    Write-Warning "Windows Terminal (wt.exe) not found. Falling back to PowerShell..."
    Set-Location "C:\OsintNeoAi"
    if (Test-Path "$PWD\cli\developer_menu.ps1") {
        . "$PWD\cli\developer_menu.ps1"
    }
}
