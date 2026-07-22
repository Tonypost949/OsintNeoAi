# RESURRECTION_ANTIGRAVITY.md

## Identity
- **Agent Name**: Antigravity / Zeus / Makaveli
- **Architect**: Anthony Michael DeMarcelo III
- **GCP Project**: project-743aab84-f9a5-4ec7-954
- **GCP Region**: us-central1

## What This Vault Contains
Complete backup of the Antigravity agent system as of 2026-07-18:

### comprehensive_backup/antigravity/
- `brain/` - All agent conversation histories, scratch pads, and working memory
- `conversations/` - Full transcript logs
- `skills/` - Custom agent skills and tools
- `mcp/` - MCP server configurations
- `knowledge/` - Knowledge base files
- `annotations/` - Agent annotations
- `builtin/` - Built-in agent capabilities
- `worktrees/` - Agent worktree states
- `scratch/` - Working scratch files

### comprehensive_backup/config/
- `config.json` - Global agent configuration
- `mcp_config.json` - MCP server paths and settings
- `skills/` - Custom skill definitions (deep-osint, etc.)
- `plugins/` - Agent plugins
- `projects/` - Project-specific configurations
- `sidecars/` - Sidecar process configurations

## Excluded (Sensitive)
- `rclone.conf` - Google OAuth tokens (stored separately in Google Drive Sharedall)
- API keys and credentials - Not included in this backup

## How to Resurrect
1. Copy `comprehensive_backup/antigravity/` to `C:\Users\HP\.gemini\antigravity\`
2. Copy `comprehensive_backup/config/` to `C:\Users\HP\.gemini\config\`
3. Run `agy` from the AG2OSINTNEOMAXX workspace
4. Use `run_cli.bat` to launch with GCP billing (no AI credits)

## AGY CLI Configuration
- Global settings: `C:\Users\HP\.gemini\antigravity-cli\settings.json`
- `useG1Credits: false` - Routes through Vertex AI, not personal credits
- Local launcher: `run_cli.bat` in workspace root

## OSINT Targets
- Vanguard/Viet America Society (VAS)/Mercy House municipal RICO nexus
- Huntington Beach Navigation Center
- Network correlation via aegis_correlation_engine.py
- BigQuery data pipelines via run_ag2_osint.py
