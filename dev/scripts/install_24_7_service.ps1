# ==============================================================================
# OSINTNeoAi / Makaveli — 24/7 Windows Background Service Installer
# Configures silent automatic startup on system boot (Zero Manual Intervention)
# ==============================================================================

$RootPath = "C:\OSINTNEOAI"
$VbsPath = "$RootPath\scripts\run_silent_bridge.vbs"
$TaskName = "OSINTNeoAi_Makaveli_24_7_Bridge"

# 1. Create Silent VBScript Launcher (Runs with 0 visible terminal windows)
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python C:\OSINTNEOAI\api\fb_ig_agent_bridge.py", 0, False
"@
Set-Content -Path $VbsPath -Value $VbsContent -Encoding ASCII

# 2. Register Windows Scheduled Task for System Startup / Logon
$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "24/7 Background Auto-Reply Bridge for Makaveli OSINT Agent"

Write-Host "================================================================="
Write-Host "✅ SUCCESS: 24/7 Background Service Configured!" -ForegroundColor Green
Write-Host "Task Name: $TaskName"
Write-Host "The Makaveli Agent Bridge will now run silently in the background on boot."
Write-Host "================================================================="
