# Actionable Task List: Zero Local Compute Matrix (todo.md)

## Phase 1: Local AI Edge Tiering & OpenOSINT MCP Integration

### Task 1: Tiered Ollama Model Profiling & CLI Presets
**Description:** Configure lightweight model profiles in Ollama (`qwen2.5-coder:1.5b` / `0.5b` for ultra-fast local CLI tasks and `ministral`/`olmo` for document parsing) with quick launch aliases.
**Acceptance Criteria:**
- [x] Tiered launcher script or profile allows switching between edge (0.5B/1.5B), mid (7B), and cloud models.
- [x] Fallback logic gracefully handles cases where Ollama service is not running.
- [x] Offline execution verified with zero network latency.
**Verification:**
- [x] Tested `cli/agent_launcher.py` with tiered options `[0-10]`.
**Files touched:**
- `cli/agent_launcher.py`
- `cli/developer_menu.ps1`

---

### Task 2: OpenOSINT Native MCP Server Binding
**Description:** Create and register an OpenOSINT Model Context Protocol (MCP) server configuration connecting the 19 automated reconnaissance modules to Antigravity (`agy`) and local AI agents.
**Acceptance Criteria:**
- [x] `mcp.json` registers the `openosint` tool endpoint.
- [x] 19 reconnaissance tools defined and functional via JSON-RPC stdio.
**Verification:**
- [x] Ran MCP tool validation script: verified 19 active tools.
**Files touched:**
- `mcp.json`
- `tools/openosint_mcp_server.py`

---

## Checkpoint: Edge AI & MCP
- [x] Local Ollama tiering verified
- [x] OpenOSINT MCP tools discovered and registered in `mcp.json`

---

## Phase 2: CLI Standardization & Automated Spatial Telemetry

### Task 3: Python Rich Terminal Interface Standardization
**Description:** Integrate Python `Rich` into core CLI tools (`cli/agent_launcher.py`) to display styled status tables, live progress bars, and formatted syntax.
**Acceptance Criteria:**
- [x] CLI displays clean tables with colored status badges (Ready / Not Installed).
- [x] Graceful fallback to formatted text when Rich is not available.
**Verification:**
- [x] Verified `cli/agent_launcher.py` displays clean table.
**Files touched:**
- `cli/agent_launcher.py`

---

### Task 4: GeoJSON Pipeline & Port 5052 Map Server Hook
**Description:** Build a streaming transformer that converts target reconnaissance and location hits into standardized GeoJSON feature collections, auto-routing to the local map server on Port 5052 / `gods_eye_view.html`.
**Acceptance Criteria:**
- [x] Automatic conversion of GPS/address entities into GeoJSON Point features.
- [x] Live updates write to `public/live_telemetry.geojson` with timezone-aware ISO timestamps.
**Verification:**
- [x] Tested `transforms/geojson_telemetry.py` -> verified 5 GeoJSON features generated.
**Files touched:**
- `transforms/geojson_telemetry.py`
- `public/live_telemetry.geojson`

---

## Checkpoint: CLI UI & Spatial Telemetry
- [x] Rich CLI launcher verified
- [x] GeoJSON spatial telemetry verified

---

## Phase 3: Headless Remote Compute & Mobile Shell Mesh

### Task 5: Remote SSH & Session Persistence Setup (`deploy_headless_compute.sh`)
**Description:** Create bootstrap scripts and deployment configs for a headless remote Linux server running PowerShell 7 (`pwsh`), Antigravity CLI, `tmux` multiplexing, and optional `ttyd` web shell.
**Acceptance Criteria:**
- [x] Automated bootstrap script `scripts/deploy_headless_compute.sh` installs `pwsh`, `agy`, `python3`, `tmux`, and `ttyd`.
- [x] Persistent session manager `attach_workspace.sh` auto-created.
**Verification:**
- [x] Script verified and staged in `scripts/deploy_headless_compute.sh`.
**Files touched:**
- `scripts/deploy_headless_compute.sh`

---

### Task 6: Mobile-to-Linux Mesh Setup (`mobile_termux_tailscale_init.sh`)
**Description:** Create a mobile connection profile and automated Termux startup script for securely connecting mobile devices (JuiceSSH / Termux) to the headless remote compute node over Tailscale.
**Acceptance Criteria:**
- [x] Termux bootstrap script connects directly to the private Tailscale IP of the compute node.
- [x] Auto-attaches to the main `tmux` workspace session upon connection.
**Verification:**
- [x] Script verified in `scripts/mobile_termux_tailscale_init.sh`.
**Files touched:**
- `scripts/mobile_termux_tailscale_init.sh`

---

## Checkpoint: Remote Compute & Mobile Mesh
- [x] Remote deployment scripts verified
- [x] Session persistence architecture ready

---

## Phase 4: Cloud Student Allocations & Enterprise Sandbox Activation

### Task 7: Azure for Students & DigitalOcean Ingestion Relay Templates
**Description:** Create deployment templates for running 24/7 background scrapers, OCR workers, and webhook relay endpoints utilizing Azure for Students ($100/mo) and DigitalOcean ($200) allocations.
**Acceptance Criteria:**
- [x] Azure for Students B2pts ARM deploy script created (`cloud_deploy/azure_student_vm_setup.sh`).
- [x] DigitalOcean Student Droplet deploy script created (`cloud_deploy/digitalocean_relay_setup.sh`).
**Verification:**
- [x] Scripts staged and validated in `cloud_deploy/`.
**Files touched:**
- `cloud_deploy/azure_student_vm_setup.sh`
- `cloud_deploy/digitalocean_relay_setup.sh`

---

### Task 8: M365 E5 Developer & Cognitive Services Endpoint Routing
**Description:** Configure an intelligent routing client that offloads OCR, document parsing, and transcription to free-tier Azure Cognitive Services and M365 E5 Developer sandbox endpoints.
**Acceptance Criteria:**
- [x] Client routes queries dynamically to local Ollama edge/mid or cloud fallbacks.
- [x] OCR passes intelligently routed based on local GPU availability.
**Verification:**
- [x] Ran diagnostic test: `python core/cognitive_router.py` passed with clean fallback handling.
**Files touched:**
- `core/cognitive_router.py`

---

## Final Checkpoint: Complete Execution
- [x] All 8 tasks implemented and verified
- [x] All code committed and pushed to `origin main`
