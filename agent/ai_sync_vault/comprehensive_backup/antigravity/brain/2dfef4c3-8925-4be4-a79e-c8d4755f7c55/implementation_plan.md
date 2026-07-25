# Batch Backup External G: Drive to OneDrive

This plan details how we will safely back up the files from your external `G:` drive to your Personal OneDrive account without running out of space on your main `C:` drive (which only has 17.5 GB free).

## User Review Required

> [!IMPORTANT]
> Because your `C:` drive has only 17.5 GB of free space, we cannot copy all 120 GB of files from your `G:` drive at once. 
> We will use a script that copies folders in **small batches**, waits for them to upload to OneDrive, dehydrates (offloads) them from `C:`, and then moves to the next batch.

## Proposed Changes

We will create and run a PowerShell script to automate this safely.

### [NEW] [backup_external_drive.ps1](file:///C:/Users/HP/.gemini/antigravity/brain/2dfef4c3-8925-4be4-a79e-c8d4755f7c55/scratch/backup_external_drive.ps1)
A script that will:
1. Target `G:\` source folders.
2. Exclude system directories (`$RECYCLE.BIN`, `System Volume Information`, `.gemini`).
3. Copy one folder at a time to `C:\Users\HP\OneDrive\External_Backup\`.
4. Monitor `C:` drive free space. If free space drops below 8 GB:
   * Run `attrib +U -P` on the copied files.
   * Pause and wait for the OneDrive sync engine to upload the files and free up the disk space back above 12 GB.
5. Proceed to the next folder.

## Verification Plan

### Automated Checks
- The script will log its progress, copy status, and current `C:` drive free space.

### Manual Verification
- You can monitor the OneDrive sync icon in your system tray to watch the upload progress.
