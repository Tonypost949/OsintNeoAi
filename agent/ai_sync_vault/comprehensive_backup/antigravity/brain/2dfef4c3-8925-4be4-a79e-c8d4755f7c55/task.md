# Migration Tasks

- [x] Create `Migrated_Workspaces` directory in Personal OneDrive
- [x] Move local workspaces (`OSINT_WORKSPACE`, `Retro_OSINT`, `gemini-gem-labs-clone`, `sentinel_backups`) to Personal OneDrive
- [x] Dehydrate all existing files in Personal OneDrive to free up local disk space
- [/] Run the new strict safe batch backup script `backup_external_drive_safe.ps1` to upload and dehydrate G: drive to OneDrive in 200MB / 500-file increments
- [ ] Monitor the batch backup progress and C: drive free space
