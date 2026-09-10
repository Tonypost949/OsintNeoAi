# Universal Visual Studio Developer PowerShell Auto-Detector for OSINT Neo AI
# Auto-detects Visual Studio 2026 or 2022 and loads C++ x64 build toolchain

try {
    Add-Type -MemberDefinition @'
[DllImport("user32.dll")]
public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[DllImport("kernel32.dll")]
public static extern IntPtr GetConsoleWindow();
'@ -Name Win32ConsoleMax -Namespace Win32Utils -ErrorAction SilentlyContinue
    $consoleHwnd = [Win32Utils.Win32ConsoleMax]::GetConsoleWindow()
    if ($consoleHwnd -ne [IntPtr]::Zero) {
        [void][Win32Utils.Win32ConsoleMax]::ShowWindow($consoleHwnd, 3) # 3 = SW_MAXIMIZE
    }
} catch {}

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

Set-Location "C:\OsintNeoAi"
if (Test-Path "C:\OsintNeoAi\cli\developer_menu.ps1") {
    . "C:\OsintNeoAi\cli\developer_menu.ps1"
}

Show-DeveloperMenu
