$Trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Users\Amd949609\.gemini\antigravity-cli\brain\a9c0c03e-11f8-4767-90a5-b59615089fa5\scratch\offhours_backup_manager.py"
Register-ScheduledTask -TaskName "OsintNeoAi_OffHours_Backup" -Trigger $Trigger -Action $Action -Description "Runs off-hours multi-threaded local backups of OsintNeoAi to D: drive." -User $env:USERNAME -Force
Write-Host "[+] Scheduled task 'OsintNeoAi_OffHours_Backup' successfully registered to run daily at 2:00 AM."
