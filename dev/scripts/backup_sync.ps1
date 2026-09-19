#!/usr/bin/env powershell
<#
.SYNOPSIS
    Multi-Location Backup Synchronizer for OsintNeoAi Repository
    
.DESCRIPTION
    Syncs OsintNeoAi repository to all 3 backup locations per AGENTS.md CARDINAL RULES:
    1. GitHub (Primary) — Remote repository
    2. Local C:\ Drive — C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\
    3. Sharedall Google Drive — Via rclone to Sharedall/OsintNeoAi/
    
.NOTES
    Requires:
    - Git installed and configured
    - rclone configured with gdrive remote
    - Write access to all three backup locations
    
.EXAMPLE
    .\backup_sync.ps1
    
    Syncs repo to all three locations and generates backup status report.
#>

param(
    [Switch]$SkipGithub,
    [Switch]$SkipLocalBackup,
    [Switch]$SkipGoogleDrive,
    [Switch]$Force
)

# Configuration
$repoPath = "C:\OsintNeoAi"
$localBackupPath = "C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo"
$gdriveRemote = "gdrive:Sharedall/OsintNeoAi"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupLogPath = "$repoPath\.backup_status_$timestamp.log"

# Colors for console output
$colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "Cyan"
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Write-Host $logMessage -ForegroundColor $colors[$Level]
    Add-Content -Path $backupLogPath -Value $logMessage
}

# ============================================================================
# PHASE 1: GITHUB SYNC (Primary)
# ============================================================================

Write-Log "========== PHASE 1: GITHUB SYNC (Primary) ==========" -Level Info

if (-not $SkipGithub) {
    Push-Location $repoPath
    
    try {
        Write-Log "Checking Git status..." -Level Info
        $gitStatus = & git status --short
        
        if ($gitStatus) {
            Write-Log "Uncommitted changes detected:" -Level Warning
            $gitStatus | ForEach-Object { Write-Log "  $_" -Level Info }
            
            if ($Force) {
                Write-Log "FORCE MODE: Stashing changes before push" -Level Warning
                & git stash
            } else {
                Write-Log "Commit changes manually or use -Force flag" -Level Error
                Pop-Location
                exit 1
            }
        }
        
        Write-Log "Fetching from GitHub origin..." -Level Info
        & git fetch origin main 2>&1 | ForEach-Object { Write-Log "  $_" -Level Info }
        
        Write-Log "Pushing to GitHub main..." -Level Info
        $pushOutput = & git push origin main 2>&1
        Write-Log "GitHub push completed: $pushOutput" -Level Success
        
        $commitLog = & git log --oneline -3
        Write-Log "Recent commits:" -Level Info
        $commitLog | ForEach-Object { Write-Log "  $_" -Level Info }
        
    } catch {
        Write-Log "GitHub sync error: $_" -Level Error
    } finally {
        Pop-Location
    }
} else {
    Write-Log "SKIPPED: GitHub sync" -Level Warning
}

# ============================================================================
# PHASE 2: LOCAL C:\ BACKUP
# ============================================================================

Write-Log "`n========== PHASE 2: LOCAL C:\ BACKUP ==========" -Level Info

if (-not $SkipLocalBackup) {
    try {
        # Verify backup directory exists
        if (-not (Test-Path $localBackupPath)) {
            Write-Log "Backup directory does not exist: $localBackupPath" -Level Error
            Write-Log "Creating backup directory..." -Level Info
            New-Item -ItemType Directory -Path $localBackupPath -Force | Out-Null
        }
        
        Write-Log "Syncing to: $localBackupPath" -Level Info
        
        # Create timestamped backup subfolder
        $backupFolder = "$localBackupPath\repo_backup_$timestamp"
        
        Write-Log "Copying repository to: $backupFolder" -Level Info
        if (Test-Path $backupFolder) {
            Write-Log "Backup folder already exists, updating..." -Level Warning
            Remove-Item -Path "$backupFolder\*" -Recurse -Force
        } else {
            New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null
        }
        
        # Use robocopy for reliable large repo sync
        Write-Log "Executing robocopy to sync repository..." -Level Info
        
        $excludeArgs = ".git", ".pytest_cache", "__pycache__", "node_modules", ".venv", "venv", "*.log", "*.tmp"
        $robocopyArgs = @($repoPath, $backupFolder, "/E") + $($excludeArgs | ForEach-Object { "/XD"; $_ }) + @("/XF", "*.log", "*.tmp")
        
        & robocopy @robocopyArgs 2>&1 | ForEach-Object { 
            if ($_ -match "ERROR|error") {
                Write-Log "  ERROR: $_" -Level Error
            } elseif ($_ -match "^\s*[0-9]+" -or $_ -match "New File" -or $_ -match "Newer") {
                Write-Log "  $_" -Level Info
            }
        }
        
        # Verify backup
        $backupSize = (Get-ChildItem -Path $backupFolder -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Log "Backup completed. Size: $([math]::Round($backupSize, 2)) GB" -Level Success
        
        # Create backup index
        $indexFile = "$localBackupPath\BACKUP_INDEX.txt"
        @"
OsintNeoAi Repository Backup Index
Created: $timestamp
Source: $repoPath
Backup Location: $backupFolder
Size (GB): $backupSize

Latest Git Commits:
$(& git -C $repoPath log --oneline -5)

Excluded Items:
- .git directory
- __pycache__ directories
- .pytest_cache
- node_modules
- .venv / venv
- Log files (*.log)
- Temp files (*.tmp)

Restoration Instructions:
1. Copy contents of $backupFolder back to $repoPath
2. Run: git fetch origin main && git reset --hard origin/main
3. Run: python -m venv venv && venv\Scripts\Activate && pip install -r requirements.txt
"@ | Out-File -FilePath $indexFile -Encoding UTF8
        
        Write-Log "Created backup index: $indexFile" -Level Success
        
    } catch {
        Write-Log "Local backup error: $_" -Level Error
    }
} else {
    Write-Log "SKIPPED: Local C:\ backup" -Level Warning
}

# ============================================================================
# PHASE 3: GOOGLE DRIVE BACKUP (via rclone)
# ============================================================================

Write-Log "`n========== PHASE 3: GOOGLE DRIVE BACKUP (via rclone) ==========" -Level Info

if (-not $SkipGoogleDrive) {
    try {
        # Check if rclone is installed
        $rcloneTest = & where.exe rclone 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "rclone not found in PATH. Install via: choco install rclone" -Level Error
            Write-Log "Or download from: https://rclone.org/downloads/" -Level Info
        } else {
            Write-Log "rclone found: $rcloneTest" -Level Info
            
            # Check if gdrive remote is configured
            Write-Log "Checking rclone configuration..." -Level Info
            $remoteList = & rclone listremotes 2>&1
            
            if ($remoteList -match "gdrive:") {
                Write-Log "gdrive remote is configured" -Level Success
                
                # Create timestamped backup folder
                $gdriveBackupFolder = "$gdriveRemote/repo_backup_$timestamp"
                
                Write-Log "Syncing to Google Drive: $gdriveBackupFolder" -Level Info
                
                # Use rclone copy to sync (create new version, don't overwrite)
                $rcloneCmd = "rclone copy `"$repoPath`" `"$gdriveBackupFolder`" --exclude `".git/**`" --exclude `"__pycache__/**`" --exclude `.pytest_cache/**` --exclude `"node_modules/**`" --exclude `.venv/**` --exclude `"*.log`" --exclude `"*.tmp`" -v"
                
                Write-Log "Executing: $rcloneCmd" -Level Info
                Invoke-Expression $rcloneCmd 2>&1 | ForEach-Object { Write-Log "  $_" -Level Info }
                
                Write-Log "Google Drive backup completed successfully" -Level Success
                
            } else {
                Write-Log "gdrive remote not configured. Set up via: rclone config" -Level Error
                Write-Log "Then authenticate with your Google account and select 'Sharedall/OsintNeoAi' shared drive" -Level Info
            }
        }
        
    } catch {
        Write-Log "Google Drive backup error: $_" -Level Error
    }
} else {
    Write-Log "SKIPPED: Google Drive backup" -Level Warning
}

# ============================================================================
# FINAL REPORT
# ============================================================================

Write-Log "`n========== BACKUP SYNC COMPLETE ==========" -Level Success

# Generate final status report
$statusReport = @"
OSINTNEOAI BACKUP SYNC REPORT
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
========================================

BACKUP LOCATIONS STATUS:

1. GitHub (Primary)
   Repository: https://github.com/Tonypost949/OsintNeoAi
   Status: $(if ($SkipGithub) { "SKIPPED" } else { "SYNCED" })
   Branch: main
   
2. Local Backup (C:\ Drive)
   Path: $localBackupPath
   Status: $(if ($SkipLocalBackup) { "SKIPPED" } else { "SYNCED" })
   Latest: $timestamp
   
3. Google Drive (Sharedall)
   Path: $gdriveRemote
   Status: $(if ($SkipGoogleDrive) { "SKIPPED" } else { "SYNCED" })
   Latest: $timestamp

RECENT COMMITS:
$(& git -C $repoPath log --oneline -5)

RESTORATION CHECKLIST:
- [ ] GitHub: All commits pushed to origin/main
- [ ] Local C:\: Full backup in $localBackupPath
- [ ] Google Drive: Full backup in $gdriveRemote
- [ ] All three locations contain current source code
- [ ] No sensitive data (credentials, secrets) in any backup
- [ ] Documentation & tools backups also in place

NOTES:
- If GitHub is unavailable, restore from Local C:\ or Google Drive
- Local backup should be copied to external USB regularly
- Google Drive backup is the "live alternative" if GitHub goes down
- Verify backups by comparing file counts/sizes across locations

Log File: $backupLogPath
"@

$statusReportPath = "$repoPath\.backup_status_report_$timestamp.txt"
$statusReport | Out-File -FilePath $statusReportPath -Encoding UTF8

Write-Log "Status report saved: $statusReportPath" -Level Success
Write-Log "Backup log saved: $backupLogPath" -Level Success

Write-Host $statusReport
