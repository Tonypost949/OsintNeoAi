$WScript = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$Shortcut = $WScript.CreateShortcut("$DesktopPath\Developer PowerShell (C-OsintNeoAi).lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -File ""C:\OsintNeoAi\launch_dev_powershell.ps1"""
$Shortcut.WorkingDirectory = "C:\OsintNeoAi"
$Shortcut.Description = "Launches Visual Studio Developer PowerShell scoped to C:\OsintNeoAi"
$Shortcut.Save()
Write-Host "[+] Created Desktop Shortcut: Developer PowerShell (C-OsintNeoAi)"
