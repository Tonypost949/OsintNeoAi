---
name: dev-cli-setup
description: >-
  Audits, installs, updates, and verifies key developer CLI tools (uv, Android CLI, Firebase CLI, gcloud, Node.js/npm) and persists their binary paths to the Windows User PATH registry.
---

# Developer CLI Setup & Audit Tool

## Overview
Automates checking, installing, and configuring essential developer CLI tools on Windows environments. It ensures tools are installed, persists their binary folders to the Windows Registry User `PATH`, and verifies execution with version checks.

## Dependencies
- `uv` skill
- `android-cli` skill
- `firebase-basics` skill
- `gcloud-auth-verification` skill

## Quick Start

### Audit installed tools:
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.gemini\config\skills\dev-cli-setup\scripts\install_clis.ps1" -Audit
```

### Install missing tools & update PATH:
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.gemini\config\skills\dev-cli-setup\scripts\install_clis.ps1" -Install
```

## Utility Scripts

### `install_clis.ps1`
Location: `scripts/install_clis.ps1`

- `-Audit`: Scans environment for `uv`, `android`, `node`, `firebase`, and `gcloud`. Reports status for each.
- `-Install`: Installs missing CLIs using preferred native installers (`astral.sh` for `uv`, `dl.google.com` for `android`, `winget` for `node` and `gcloud`, `npm` for `firebase`).
- `-UpdatePath`: Persists binary directories to `[Environment]::GetEnvironmentVariable("Path", "User")`.

## Common Mistakes
1. **Relying on transient process PATH**: Shell restarts wipe process environment variables if not written to the Windows Registry User `PATH`.
2. **Missing execution policy**: On PowerShell, run with `-ExecutionPolicy Bypass` if script execution is restricted.
