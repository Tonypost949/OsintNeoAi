# Universal JetBrains Launcher for OsintNeoAi
param (
    [ValidateSet("pycharm", "datagrip", "gateway", "idea")]
    [string]$IDE = "pycharm"
)

$PycharmExe = "C:\Program Files\JetBrains\PyCharm 2026.2.1\bin\pycharm64.exe"
$ToolboxDir = "$env:LOCALAPPDATA\JetBrains\Toolbox\apps"

switch ($IDE) {
    "pycharm" {
        if (Test-Path $PycharmExe) {
            Start-Process $PycharmExe -ArgumentList "C:\OsintNeoAi"
            Write-Host "[+] Launched PyCharm 2026.2 targeting C:\OsintNeoAi" -ForegroundColor Green
        } else {
            $candidate = Get-ChildItem "$env:LOCALAPPDATA\JetBrains\PyCharm*\bin\pycharm64.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($candidate) { Start-Process $candidate.FullName -ArgumentList "C:\OsintNeoAi" }
        }
    }
    "datagrip" {
        $dg = Get-ChildItem "$env:LOCALAPPDATA\JetBrains\DataGrip*\bin\datagrip64.exe", "C:\Program Files\JetBrains\DataGrip*\bin\datagrip64.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($dg) {
            Start-Process $dg.FullName -ArgumentList "C:\OsintNeoAi"
            Write-Host "[+] Launched DataGrip targeting C:\OsintNeoAi" -ForegroundColor Green
        } else {
            Write-Host "[!] DataGrip executable locating..."
        }
    }
    "gateway" {
        $gw = Get-ChildItem "$env:LOCALAPPDATA\JetBrains\JetBrainsGateway*\bin\gateway64.exe", "C:\Program Files\JetBrains\JetBrains Gateway*\bin\gateway64.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($gw) {
            Start-Process $gw.FullName
            Write-Host "[+] Launched JetBrains Gateway (Select 'osintneoai-vm' to connect to Azure VM)" -ForegroundColor Green
        } else {
            Write-Host "[!] JetBrains Gateway executable locating..."
        }
    }
}
