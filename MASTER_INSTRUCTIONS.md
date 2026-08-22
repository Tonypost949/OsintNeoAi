# Disole Design: Master Creator Operations Manual

## Ecosystem Architecture
- **C:\DisoleDesign** — Creator Company & Command Cockpit
- **C:\OSINTRnDi** — Master OSINT R&D Lab (AIO)
  - `toolstestrepo\` — Staging buffer for pure tools
  - `showtestrepo\` — Staging buffer for case data & exhibits
- **C:\OSINTNeoAi** — Official Tool Version 1
- **C:\RICONWO** — Flagship Case Evidence Showcase & Newsroom

## Daily Workflow Rules
1. Work in `C:\OSINTRnDi` for testing and new features.
2. Use staging subfolders as the safety buffer before syncing.
3. Cryptographically seal all evidence exhibits with SHA-256 before pushing to Show repos.
4. Never commit secrets, credentials, or large binaries (>50MB) to any repo.
5. All evidence must pass through `evidence_locker.py` before public release.

## Repository Purpose Matrix

| Repository | Purpose | Visibility |
|------------|---------|------------|
| DisoleDesign | Company hub, config, operations manual | Private |
| OSINTRnDi | R&D lab, tool testing, data processing | Private |
| OSINTNeoAi | Official released tools | Public |
| RICONWO | Public evidence showcase | Public |

## Deployment Checklist
- [ ] Evidence sealed with SHA-256
- [ ] Large files excluded via .gitignore
- [ ] Sensitive credentials removed
- [ ] README updated with usage instructions
- [ ] Evidence locker script run
