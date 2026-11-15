# MUSE_DROPBOX watcher - runs in background, logs new arrivals
$dropbox = "C:\Users\Amd949609\Desktop\MUSE_DROPBOX"
$logFile = "C:\Amd949609_Antigravity_v1\tools\task_system\muse_dropbox_watcher.log"
$lastRunFile = "C:\Amd949609_Antigravity_v1\tools\task_system\muse_watcher_lastrun.txt"

# Record baseline
$baseline = Get-Date
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')] WATCHER STARTED. Baseline snapshot taken." | Out-File $logFile -Append

# Get current state
$snapshot = Get-ChildItem $dropbox -Recurse -File -ErrorAction SilentlyContinue | 
    Select-Object FullName, LastWriteTime, Length

# Check for files newer than 4 hours (last army mobilization)
$cutoff = (Get-Date).AddHours(-4)
$newFiles = $snapshot | Where-Object { $_.LastWriteTime -gt $cutoff }

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] NEW FILES (last 4h): $($newFiles.Count)" | Out-File $logFile -Append
foreach ($f in $newFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 20) {
    "  NEW: $($f.FullName) [$([math]::Round($f.Length/1KB,1)) KB] @ $($f.LastWriteTime)" | Out-File $logFile -Append
}

# Check NEO_TO_AGY_LIVE for new Neo directives
$liveFile = "$dropbox\NEO_TO_AGY_LIVE.txt"
$liveContent = Get-Content $liveFile -ErrorAction SilentlyContinue | Select-String "— Neo" | Select-Object -Last 3
"[$(Get-Date)] LATEST NEO DIRECTIVES:" | Out-File $logFile -Append
$liveContent | Out-File $logFile -Append

# Try Neo host
$neoUp = Test-NetConnection -ComputerName 100.79.79.27 -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue 2>$null
"[$(Get-Date)] NEO HOST 100.79.79.27:22 = $neoUp" | Out-File $logFile -Append

(Get-Date).ToString() | Out-File $lastRunFile

Get-Content $logFile | Select-Object -Last 30
