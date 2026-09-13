<div align="center">

# ⚡ OSINT Neo AI
### Autonomous Open-Source Intelligence & Forensic Knowledge Graph Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GCP BigQuery](https://img.shields.io/badge/Google_Cloud-BigQuery-4285F4.svg?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Ethereum Sepolia](https://img.shields.io/badge/Ethereum-Sepolia_Verified-3C3C3D.svg?style=for-the-badge&logo=ethereum&logoColor=white)](https://sepolia.etherscan.io/)
[![MCP Server](https://img.shields.io/badge/MCP-19_Native_Tools-00DC82.svg?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Zero-Lag ConPTY](https://img.shields.io/badge/Windows_Terminal-wt--dev-4E1A3D.svg?style=for-the-badge&logo=windows-terminal&logoColor=white)](https://github.com/Tonypost949/OsintNeoAi)

<p align="center">
  <b>Enterprise-Grade OSINT Automation • BigQuery Forensic Graph • 3D Tactical Geospatial Cockpit • Web3 Cryptographic Provenance</b>
</p>

[🌐 Live Demo Cockpit](http://localhost:10000/map/osinteye) • [📖 Documentation](docs/MOBILE_REMOTE_SHELL_SETUP.md) • [🛠️ MCP Tool Catalog](tools/openosint_mcp_server.py) • [🚀 Quickstart](#-quickstart)

---

</div>

## 🌟 Executive Overview

**OSINT Neo AI** is a decentralized, hybrid-cloud open-source intelligence and forensic investigation platform. Designed for forensic auditors, investigative journalists, municipal researchers, and national cybersecurity teams, OSINT Neo AI bridges **high-throughput Web2 data pipelines** (Google Cloud BigQuery, Azure Cognitive Services) with **Web3 cryptographic provenance** (Ethereum Sepolia smart contracts) and **autonomous multi-agent AI swarms**.

The platform operates on a **Zero Local Compute** architecture—allowing resource-intensive operations (neural OCR, multi-million node graph traversals, 3D WebGL tactical GIS) to execute seamlessly across headless remote cloud clusters while physical devices (Windows, Linux, Android) act as lightweight, zero-lag terminals.

---

## 🏛️ Core Platform Architecture

```
┌────────────────────────────────────────────────────────┐
│  1. Universal Client & Dumb Terminal Layer             │
│  • Windows Terminal (wt-dev ConPTY Bracketed Paste)    │
│  • Mobile Termux / JuiceSSH via Tailscale Mesh         │
│  • Browser Web-Shell (ttyd / GitHub Codespaces)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  2. AI Orchestration & OpenOSINT MCP Server            │
│  • 19 Native Model Context Protocol (MCP) Tools        │
│  • Tiered Inference: Ollama Qwen 1.5B/7B & Gemini Pro  │
│  • Dynamic Cognitive Router for Image / Document OCR   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  3. Forensic Data Engine & BigQuery Graph              │
│  • Target Accounts Master Registry (32 Targets Synced) │
│  • 3,510 Evidence Documents with SHA-256 Checksums     │
│  • Append-Only Data Ledger (noble-beanbag-497411-m4)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  4. Visualization & Tactical Cockpits                  │
│  • OSINT Eye View: Real-Time GPS Trajectory Playback   │
│  • MapLibre 3D WebGL: Vector Building Extrusions       │
│  • Syncfusion Enterprise Grid: Multi-Column Analytics  │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

### 🛰️ 1. OSINT Eye View & 3D Tactical Geospatial Engine
- **Live Reconnaissance Cockpit**: Real-time interactive spatial map integrating municipal zoning, utility infrastructure, and environmental monitoring nodes.
- **Historical Trajectory Scrubber**: Animated playback scrubber with time-series controls and speed indicators tracking physical entity waypoints.
- **Click-to-Inspect Dossier Drawer**: Dynamic HUD slide-out panel querying the 3,510-document evidence ledger in real-time with zero UI lag.
- **MapLibre 3D WebGL Extrusions**: Hardware-accelerated 3D vector building heights with pitch, bearing, and sun angle simulation.

### 🤖 2. Autonomous Multi-Agent Swarm & OpenOSINT MCP
- **19 Native MCP Tools**: Fully registered in `mcp.json` for Antigravity (`agy`), Claude Code, and Gemini CLI:
  `osint_lookup_person`, `osint_lookup_email`, `osint_lookup_phone`, `osint_lookup_domain`, `osint_lookup_ip`, `osint_search_entity`, `osint_court_records`, `osint_property_records`, `osint_social_footprint`, `osint_crypto_wallet`, `osint_foia_tracker`, `osint_fca_timeline`, `osint_sec_edgar`, `osint_wayback_history`, `osint_geo_telemetry`, `osint_breach_scanner`, `osint_license_lookup`, `osint_charity_990`, `osint_system_health`.
- **Tiered AI Inference**: Ultra-fast offline inference on local open-weight models (Qwen 1.5B/7B) with automatic cloud fallback for complex forensic reasoning.

### 🔒 3. Web3 Cryptographic Provenance & Smart Contracts
- **Verified on Sepolia Testnet**: Immutable chain of custody for digital evidence and whistleblower bounties:
  - **USDC Settlement**: [`0x7236F4982a31537d07f3182A1CdAD3f3E4452A53`](https://sepolia.etherscan.io/address/0x7236F4982a31537d07f3182A1CdAD3f3E4452A53#code)
  - **OSINT Utility Token**: [`0xA74B3fAfd838fC273f7c6e201B6210AC2b3A0296`](https://sepolia.etherscan.io/address/0xA74B3fAfd838fC273f7c6e201B6210AC2b3A0296#code)
  - **StakingGate (Sybil Defense)**: [`0xdA7655b7007a1C7F8191066Bb9A69E4D8987E725`](https://sepolia.etherscan.io/address/0xdA7655b7007a1C7F8191066Bb9A69E4D8987E725#code)
  - **MultiPoolEscrow**: [`0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B`](https://sepolia.etherscan.io/address/0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B#code)

### ☁️ 4. Zero Local Compute & Cloud VM Matrix
- **Headless Cloud Node Deployment**: 1-command bootstrap for Azure for Students, Oracle Cloud Always Free (4 ARM cores, 24GB RAM), and DigitalOcean Droplets.
- **Session Durability**: Persistent `tmux` workspaces keep scrapers, BigQuery batch streams, and agent swarms running 24/7 without terminal dropouts.
- **Mobile Mesh Connect**: Connect from Android Termux or JuiceSSH over encrypted Tailscale private mesh.

---

## ⚡ Quickstart

### Option A: Local Terminal Launch (Windows / Linux / macOS)

```bash
# 1. Clone the repository
git clone https://github.com/Tonypost949/OsintNeoAi.git
cd OsintNeoAi

# 2. Setup Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt rich requests google-cloud-bigquery

# 3. Launch the Interactive Swarm Launcher
python cli/agent_launcher.py
# Or on Windows Terminal: wt-dev
```

### Option B: 1-Command Headless Cloud Server Bootstrap

Deploy to any clean Ubuntu 22.04 / 24.04 or Debian VPS (Azure, Oracle, DigitalOcean, FreeVPS):

```bash
curl -sSL https://raw.githubusercontent.com/Tonypost949/OsintNeoAi/main/scripts/deploy_headless_compute.sh | bash
```

### Option C: Launch the 3D Tactical Map Server

```bash
python simple_map_server.py
```
Open **[http://localhost:10000/map/osinteye](http://localhost:10000/map/osinteye)** in your browser.

---

## 🛠️ MCP (Model Context Protocol) Integration

OSINT Neo AI provides native MCP server support. Add the configuration below to your AI assistant's `mcp.json` (Claude Desktop, Antigravity, Cursor, or Gemini CLI):

```json
{
  "mcpServers": {
    "openosint": {
      "command": "python",
      "args": ["C:\\OsintNeoAi\\tools\\openosint_mcp_server.py"]
    }
  }
}
```

### Sample MCP Tool Invocations:
```python
# Check entity evidence ledger
osint_search_entity(entity_name="Huntington Beach", state="CA")

# Lookup blockchain wallet transactions
osint_crypto_wallet(address="0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B")

# Generate 3D Map Telemetry GeoJSON
osint_geo_telemetry(lat=33.7455, lng=-117.8677, title="Santa Ana Civic Center", category="Municipal")
```

---

## 📊 Live Endpoints & Routes

| Route | Protocol | Description |
| :--- | :--- | :--- |
| `/map/osinteye` | HTTP / HTML | **OSINT Eye View** Reconnaissance Cockpit with animated timeline scrubber |
| `/map/3d` | HTTP / WebGL | **MapLibre 3D** hardware-accelerated vector building extrusions |
| `/grid` | HTTP / HTML | **Syncfusion Enterprise Grid** with multi-column filtering and CSV/Excel export |
| `/dashboard` | HTTP / HTML | **Executive Forensic Dashboard** with ECharts and FCA statutory timeline |
| `/telemetry` | HTTP / GeoJSON | Live GeoJSON telemetry stream for tactical mapping layers |
| `/api/inspect` | REST / JSON | Real-time entity search querying 3,510 evidence documents with SHA-256 hashes |
| `/health` | REST / JSON | Microservice health check and WebGL engine diagnostic |

---

## 🛡️ Security & Evidence Integrity
1. **Chain-of-Custody**: Every ingested document receives an immutable SHA-256 hash at capture time.
2. **Append-Only Storage**: Raw evidence records are immutable in BigQuery versioned datasets (`version_id = 1` raw, `version_id = 2` enriched).
3. **Sybil Resistance**: Web3 Staking Gate collateralizes submissions to eliminate automated spam attacks.
4. **Terminal ConPTY Optimization**: Bracketed paste mode prevents character-by-character clipboard lag and buffer corruption.

---

## 🤝 Contributing & Community

Contributions are welcome! Please follow our established [AGENTS.md](AGENTS.md) multi-agent guidelines and ensure all code submissions include automated test validation.

- **Issues & Bounties**: [GitHub Issues](https://github.com/Tonypost949/OsintNeoAi/issues)
- **Repository**: [https://github.com/Tonypost949/OsintNeoAi](https://github.com/Tonypost949/OsintNeoAi)

---

<div align="center">
  <sub>Built with ❤️ by the OSINT Neo AI Forensic Engineering Team. Licensed under the MIT License.</sub>
</div>
