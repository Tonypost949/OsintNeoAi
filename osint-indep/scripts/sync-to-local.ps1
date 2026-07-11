<#
.SYNOPSIS
    Sync OSINT Independent repo to local C: drive backup
.DESCRIPTION
    Mirrors repository to C:\osint-indep-backup\latest
    Creates timestamped snapshots
    Runs via Task Scheduler hourly
#>

param(
    [string]$RepoRoot = (git rev-parse --show-toplevel),
    [string]$BackupRoot = "C:\osint-indep-backup",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$DateStamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = "$RepoRoot\logs\sync-local-$(Get-Date -Format 'yyyyMMdd').log"

mkdir -p "$RepoRoot\logs" -ErrorAction SilentlyContinue
mkdir -p "$BackupRoot\snapshots" -ErrorAction SilentlyContinue
mkdir -p "$BackupRoot\latest" -ErrorAction SilentlyContinue

function Write-Log {
    param([string]$Message)
    $entry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $entry
    Add-Content -Path $LogFile -Value $entry
}

Write-Log "=== LOCAL SYNC STARTED ==="
Write-Log "Repository: $RepoRoot"
Write-Log "Backup Root: $BackupRoot"
Write-Log "Timestamp: $Timestamp"

# Create git bundle
Write-Log "Creating git bundle..."
cd $RepoRoot
git bundle create "$env:TEMP\osint-indep-$DateStamp.bundle" --all
Write-Log "Bundle created: $env:TEMP\osint-indep-$DateStamp.bundle"

# Robocopy mirror to latest
Write-Log "Mirroring to $BackupRoot\latest..."
$excludeDirs = @(".git\objects\pack", "__pycache__", "node_modules", ".pytest_cache", "venv", ".venv", "*.log", "*.pyc")
$excludeArgs = $excludeDirs | ForEach-Object { "/XD $_" }

robocopy $RepoRoot "$BackupRoot\latest" /MIR /R:3 /W:5 /NP /NDL /LOG+:"$LogFile" $excludeArgs
$exitCode = $LASTEXITCODE
if ($exitCode -gt 7) {
    Write-Log "ERROR: Robocopy failed with exit code $exitCode"
    exit $exitCode
}

# Write timestamp
$Timestamp | Out-File -FilePath "$BackupRoot\latest\.backup_timestamp" -Encoding utf8

# Create snapshot
$SnapshotDir = "$BackupRoot\snapshots\$DateStamp"
mkdir -p $SnapshotDir -ErrorAction SilentlyContinue
Copy-Item "$env:TEMP\osint-indep-$DateStamp.bundle" "$SnapshotDir\osint-indep-$DateStamp.bundle" -Force
Write-Log "Snapshot created: $SnapshotDir\osint-indep-$DateStamp.bundle"

# Cleanup old snapshots (keep 30 daily)
$Cutoff = (Get-Date).AddDays(-30)
Get-ChildItem "$BackupRoot\snapshots\*.bundle" | Where-Object { $_.LastWriteTime -lt $Cutoff } | Remove-Item -Force

# Cleanup old logs (keep 30 days)
$LogCutoff = (Get-Date).AddDays(-30)
Get-ChildItem "$RepoRoot\logs\sync-local-*.log" | Where-Object { $_.LastWriteTime -lt $LogCutoff } | Remove-Item -Force

Write-Log "=== LOCAL SYNC COMPLETE ==="
Write-Log "Backup location: $BackupRoot\latest"
Write-Log "Snapshot: $SnapshotDir"