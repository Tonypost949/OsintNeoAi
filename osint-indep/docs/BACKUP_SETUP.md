# Backup Infrastructure Setup Guide

## Google Drive "sharedall" Configuration

### 1. Create Service Account
```bash
# In Google Cloud Console:
# 1. Create project: "osint-indep-backup"
# 2. Enable Google Drive API
# 3. Create Service Account: "osint-backup-sync"
# 4. Grant roles:
#    - Drive File Stream Admin
#    - Drive Metadata Read Access
# 5. Create & download JSON key
# 6. Enable "Domain-wide Delegation" if using shared drives
```

### 2. Configure Shared Drive
```bash
# In Google Drive UI:
# 1. Create Shared Drive: "osint-indep-backup"
# 2. Add service account email as "Content Manager"
# 3. Note the Shared Drive ID from URL:
#    https://drive.google.com/drive/folders/<DRIVE_ID>
#    Example: 0AKEf... (starts with 0A)
```

### 3. Configure rclone
```bash
# Install rclone
# Linux/macOS: curl https://rclone.org/install.sh | sudo bash
# Windows: scoop install rclone / choco install rclone

# Configure
rclone config

# Choose: n) New remote
# Name: gdrive-sharedall
# Type: drive
# Client ID: <from service account>
# Client Secret: <from service account>
# Scope: drive
# Service Account File: /path/to/service-account.json
# Team Drive: true
# Team Drive ID: <DRIVE_ID_FROM_STEP_2>
```

### 4. Test Configuration
```bash
# List shared drive contents
rclone lsd gdrive-sharedall:

# Should show: osint-indep-backup (folder)
rclone lsf gdrive-sharedall:osint-indep-backup
```

---

## Local Backup Directory Setup (Windows)

### 1. Create Directory Structure
```powershell
# Run as Administrator
mkdir C:\osint-indep-backup\snapshots
mkdir C:\osint-indep-backup\latest
mkdir C:\osint-indep-backup\logs

# Set permissions (optional - restrict to your user)
icacls "C:\osint-indep-backup" /inheritance:r /grant:r "%USERNAME%:(OI)(CI)F" /grant:r "SYSTEM:(OI)(CI)F"
```

### 2. Create Scheduled Task
```powershell
# Run as Administrator
$Action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument '-NoProfile -WindowStyle Hidden -File "C:\path\to\osint-indep\scripts\sync-to-local.ps1"'
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
Register-ScheduledTask -TaskName "OSINT-Independent-Local-Sync" -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest -Force
```

---

## Cold Storage Setup (AWS S3 Glacier)

### 1. Create S3 Bucket
```bash
aws s3api create-bucket --bucket osint-indep-cold-storage --region us-east-1
aws s3api put-bucket-versioning --bucket osint-indep-cold-storage --versioning-configuration Status=Enabled
aws s3api put-bucket-lifecycle-configuration --bucket osint-indep-cold-storage --lifecycle-configuration '{
  "Rules": [
    {
      "ID": "GlacierTransition",
      "Status": "Enabled",
      "Filter": {},
      "Transitions": [
        {"Days": 1, "StorageClass": "GLACIER_IR"},
        {"Days": 90, "StorageClass": "GLACIER"},
        {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
      ]
    }
  ]
}'
```

### 2. Configure AWS CLI
```bash
aws configure
# Enter credentials with s3:PutObject, s3:GetObject on osint-indep-cold-storage
```

---

## Cold Storage Setup (Backblaze B2)

### 1. Create B2 Bucket
```bash
# In Backblaze B2 Console:
# 1. Create bucket: osint-indep-cold-storage
# 2. Set lifecycle rules: Hide files after 1 day, Delete after 365 days (or keep forever)
# 3. Create application key with: List Buckets, Read/Write Files
```

### 2. Configure rclone for B2
```bash
rclone config
# n) New remote
# Name: b2-cold
# Type: b2
# Account: <keyID>
# Key: <applicationKey>
```

---

## Service Account Key Security

### Store in 1Password / Bitwarden
```
Item: "OSINT-Independent Backup Service Account"
Fields:
  - service_account.json (file attachment)
  - drive_id: <shared_drive_id>
  - project_id: osint-indep-backup
  - client_email: osint-backup-sync@osint-indep-backup.iam.gserviceaccount.com
```

### Reference in Scripts
```bash
# In sync-to-gdrive.sh, replace hardcoded path:
# SERVICE_ACCOUNT_FILE="${OP_SERVICE_ACCOUNT_FILE:-/path/to/service-account.json}"
# Or inject via environment at runtime
```

---

## Verification Checklist

After setup, verify all tiers:

- [ ] **GitHub**: `git push` works, repo accessible
- [ ] **Google Drive**: `rclone lsf gdrive-sharedall:osint-indep-backup` shows folder
- [ ] **Local**: `C:\osint-indep-backup\latest` exists and writable
- [ ] **Cold Storage**: `aws s3 ls s3://osint-indep-cold-storage` or `rclone lsf b2-cold:osint-indep-cold-storage`
- [ ] **Sync Test**: Run `./scripts/sync-all.sh` - completes without errors
- [ ] **Verify Test**: Run `./scripts/verify-backups.sh` - all green
- [ ] **Resurrection Test**: Quarterly drill passes

---

## Maintenance

| Task | Frequency | Command |
|------|-----------|---------|
| Verify backups | Pre-commit | `./scripts/verify-backups.sh` |
| Full sync | Daily (2 AM) | `./scripts/daily-sync.sh` |
| Weekly full backup | Weekly (Sun 3 AM) | `./scripts/weekly-full-backup.sh` |
| Cold storage upload | Monthly | `./scripts/create-cold-backup.sh` |
| Disaster recovery drill | Quarterly | Manual - follow DISASTER_RECOVERY.md |
| Rotate service account key | Annually | GCP Console → IAM → Service Accounts → Keys |

---

## Troubleshooting

### rclone "Failed to create file system"
```bash
# Check service account permissions
# Ensure Drive API enabled
# Ensure service account added to shared drive as Content Manager
rclone config show gdrive-sharedall
```

### Local backup "Access denied"
```powershell
# Run PowerShell as Administrator
# Check folder permissions
icacls "C:\osint-indep-backup"
```

### Git bundle verify fails
```bash
# Bundle may be incomplete
# Recreate: git bundle create /tmp/fresh.bundle --all
# Check: git bundle verify /tmp/fresh.bundle
```

### Scheduled task not running
```powershell
# Check Task Scheduler history
Get-ScheduledTaskInfo -TaskName "OSINT-Independent-Local-Sync"
# Check event logs
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20
```