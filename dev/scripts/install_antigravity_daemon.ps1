# ==============================================================================
# OSINTNeoAi — Antigravity Daemon 24/7 Windows Background Service Installer
# Configures silent automatic startup on system logon/boot (Zero Manual Intervention)
# ==============================================================================

$RootPath = "C:\OsintNeoAi"
$VbsPath = "$RootPath\scripts\run_silent_antigravity_daemon.vbs"
$TaskName = "OSINTNeoAi_Antigravity_Daemon_5052"

# 1. Verify VBS script existence
if (-not (Test-Path $VbsPath)) {
    $VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python C:\OsintNeoAi\scripts\antigravity_daemon_server.py", 0, False
"@
    Set-Content -Path $VbsPath -Value $VbsContent -Encoding ASCII
}

# 2. Register Windows Scheduled Task for System Startup / Logon
$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "24/7 Background Daemon Server for Google Antigravity (agy CLI) on Port 5052"

# 3. Start task immediately
Start-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "✅ SUCCESS: Antigravity CLI Daemon 24/7 Service Configured!" -ForegroundColor Green
Write-Host "Task Name: $TaskName"
Write-Host "Endpoint:  http://127.0.0.1:5052/"
Write-Host "Health:    http://127.0.0.1:5052/health"
Write-Host "The Antigravity Daemon will now run silently in the background on boot."
Write-Host "=================================================================" -ForegroundColor Cyan
