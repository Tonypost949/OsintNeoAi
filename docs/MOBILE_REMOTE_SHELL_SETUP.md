# Mobile-to-Cloud Remote Shell Setup Guide (Tailscale + Termux)

## Overview
Connect your Android phone or tablet directly to your headless remote compute node (Azure for Students, Oracle Always Free, or DigitalOcean) with zero port-forwarding using private Tailscale mesh networking and persistent `tmux` sessions.

---

## Architecture Flow

```
┌────────────────────────────────────────────────────────┐
│  Mobile Device (Android / Termux / JuiceSSH)           │
│  • Private Tailscale IP: 100.x.y.z                     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ (Encrypted WireGuard Mesh)
┌────────────────────────────────────────────────────────┐
│  Headless Remote Linux Node (Azure / Oracle / DO)      │
│  • Private Tailscale IP: 100.a.b.c                     │
│  • Running Persistent tmux Workspace Session           │
│  • Running Antigravity, pwsh, and BigQuery Pipelines   │
└────────────────────────────────────────────────────────┘
```

---

## 1-Tap Connection Setup on Android (Termux)

1. **Install Prerequisites in Termux:**
   ```bash
   pkg update && pkg install -y git openssh
   ```

2. **Download Connector Script:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/scripts/mobile_termux_tailscale_init.sh -o ~/mobile_connect.sh
   chmod +x ~/mobile_connect.sh
   ```

3. **Connect to Your Node:**
   ```bash
   ~/mobile_connect.sh
   ```
   * On first run, enter your remote cloud node's IP (or 100.x Tailscale IP) and SSH username (`ubuntu` or `root`).
   * The script auto-attaches you to the persistent `tmux` session (`osintneoai`).

4. **Background Session Durability:**
   * If mobile cell signal drops, your running AI agent tasks, BigQuery queries, and OCR jobs continue executing in the cloud without interruption.
   * Re-running `~/mobile_connect.sh` instantly restores your view.
