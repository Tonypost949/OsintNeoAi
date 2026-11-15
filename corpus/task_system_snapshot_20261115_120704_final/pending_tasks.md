# Pending Tasks — Universal AI Laws Law 3

## HIGH — User review queue (daily visibility)

1. **OpenCode Desktop host upgrade pending**: winget `Anomaly.OpenCode.Desktop` 1.19.5 → 2.0.29. **Excluded from batch upgrade deliberately** — it is the running host session; upgrading kills active session. Execute at session end or next cold start: `winget upgrade Anomaly.OpenCode.Desktop`.
2. **Backup artifacts awaiting review/rotation** (Law 14/15 — do not delete without sweep):
   - `C:\Users\Amd949609\AppData\Roaming\npm\*.bak-stale-20261109` + `node_modules.bak-stale-20261109` (stale npm prefix copies; superseded by active prefix)
   - `C:\Users\Amd949609\.local\bin\firebase.exe.bak-corrupt-enospc` (corrupt ENOSPC binary)
   - `C:\Users\Amd949609\AppData\Local\Temp\opencode\gcloud.zip` (79 MB official Google Cloud CLI archive — usable for offline reinstall)
3. **Winget batch upgrade of remaining GUI apps** may partially fail non-interactively (OBS, Notion, JetBrains PyCharm/Toolbox, Docker Desktop, Audacity, PowerToys, scrcpy, superwhisper, OpenToonz, Cloudflare WARP). Log reviewed → rerun failures individually.

## AUTOMATED — Background / off-hours queue

4. **Create `tool_update_audit` AI tool (Law 1 — repeated process must become a tool)**: script `C:\Amd949609_Antigravity_v1\tools\tool_update_audit.ps1` to run off-hours. Checks pending updates for: gcloud components, az, uv, npm -g outdated, winget upgrade list, gh. Emits nag-free report + auto-applies silent updates except running host binaries. Schedule via Task Scheduler.
5. **npm allow-scripts governance**: future `npm install -g` packages shipping install scripts must be added to `C:\Users\Amd949609\.npmrc` allow-scripts list, else silent runtime breakage (root cause of claude.exe stub). Add check to tool_update_audit.
6. **Node.js dual-installation note**: winget has `OpenJS.NodeJS` 26.7.0 (C:\Program Files\nodejs) while active toolchain is v24.19.0 at `C:\Users\Amd949609\AppData\Local\Programs\nodejs` (npm prefix). Decide single source of truth during off-hours audit; avoid upgrading one blindly.
7. **Google Cloud SDK winget registration shows Version "Unknown"** (zip-install overwrote MSI registration). Optional: `winget install Google.CloudSDK` repair to re-register, or ignore since gcloud self-updates via components now.
