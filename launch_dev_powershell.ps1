# Universal Visual Studio Developer PowerShell Auto-Detector for OsintNeoAi
# 1. vsdev FIRST
if (-not $env:VSCMD_VER) {
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
}

# 2. Ensure PATH for all tools & agents
$env:PATH += ";C:\Users\Amd949609\AppData\Local\agy\bin;C:\Users\Amd949609\AppData\Local\Programs\Ollama;C:\Users\Amd949609\AppData\Roaming\npm;C:\OsintNeoAi\bin;C:\TaxFunded\bin;C:\Users\Amd949609\.local\bin;C:\Program Files (x86)\Microsoft Visual Studio\Installer"

# 3. Set Workspace Directory
Set-Location "C:\OsintNeoAi"

# 4. Load aicli Developer Menu THEN
if (Test-Path "C:\OsintNeoAi\cli\developer_menu.ps1") {
    . "C:\OsintNeoAi\cli\developer_menu.ps1"
}

# 5. Launch aicli menu
Show-DeveloperMenu
