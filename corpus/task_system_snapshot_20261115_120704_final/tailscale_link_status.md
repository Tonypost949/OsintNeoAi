# TAILSCALE BRIDGE STATUS & NETWORK ROUTING AUDIT
**Date/Timestamp**: 2026-10-22 13:56:00
**Tailnet**: `amd949609@gmail.com`

---

## 1. Connected Devices & Topology

| Machine Name | Tailscale IP | OS | Status | Role |
|---|---|---|---|---|
| **djdrop** | `100.98.172.55` | Windows 11 | **ACTIVE / CONNECTED** | Host / Source of Truth (`C:\Amd949609_Antigravity_v1`) |
| **muse** | `100.79.79.27` | Linux VM | **ACTIVE / CONNECTED** | Client-only VM node (`~/workspace/`) |

---

## 2. Verified Reachable Services
- **TCP Port 22 (OpenSSH Server)**:
  - Bound & Listening on `0.0.0.0:22` and `100.98.172.55:22`.
  - Windows Firewall: `OpenSSH-Server-In-TCP` enabled.
  - SSH Banner Verified: `SSH-2.0-OpenSSH_for_Windows_9.5`.
  - Authorized Keys: Verified active at `C:\Users\Amd949609\.ssh\authorized_keys`.
- **Target Evidence Directory**:
  - `C:\Amd949609_Antigravity_v1` directly accessible over SSH / SFTP.

---

## 3. Disconnection & Resolution Summary
- **Conflict Identified**: Cloudflare WARP (`warp-svc`) was capturing default routing and dropping Tailscale's WireGuard UDP traffic.
- **Resolution**: Disconnected WARP via CLI (`warp-cli disconnect`), executed direct CLI authentication with provided auth key, establishing full Tailnet connectivity.
