---
name: remote-vps-browser
description: >
  One-command infrastructure & AI quota sentinel. Probes remote VM (SSH/HTTP),
  local services, and AI provider rate limits (GitHub, Gemini, GCP, Azure) to
  catch unannounced shutdowns before they happen. Use when the user asks to
  "check the VM", "check quota/usage/limits", "is the backend up", or invokes
  /remote-vps-browser.
---

# Remote VPS & AI Quota Sentinel

**Purpose:** Answer one question in under 60 seconds — *is anything about to
die on me?* (VM down, endpoint dead, AI rate limit exhausted.)

This is NOT a fake "browser dashboard scraper". It uses real API probes that
work headlessly and return machine-readable results.

## Quick Run

```powershell
python C:\OsintNeoAi\.agents\skills\remote-vps-browser\scripts\sentinel.py
```

Exit codes: `0` = OK, `1` = WARN, `2` = CRITICAL.

## What It Checks

| Section | Check | Source | Critical? |
|---|---|---|---|
| vm | SSH `osintneoai-vm`, `osint-cloud` | `~/.ssh/config` aliases | azure=yes |
| vm | HTTP `/health` on backend :10000, Firebase, GitHub Pages | direct GET | backend=yes |
| quota | GitHub API rate limit | `gh auth token` → REST | yes |
| quota | Gemini API (live 1-token ping + `x-ratelimit-*` headers) | `GEMINI_API_KEY` from `.env` | yes |
| quota | GCP CPU/disk/address quotas (usage vs limit) | `gcloud compute project-info` | no |
| quota | Azure login + VM inventory | `az` (reports `not_auth` if expired) | no |
| local | CLI hub :5052, map server :10000 | TCP connect | no |

Thresholds: remaining quota **≤20% → WARN**, **≤5% → CRITICAL**. HTTP 429 from
Gemini is immediately CRITICAL.

## Flags

- `--only vm|quota|local` — run one section
- `--markdown` — print markdown table only
- `--no-save` — skip writing report files

## Output

- Console summary with OK/WARN/CRITICAL per check
- `C:\OsintNeoAi\reports\sentinel\latest.md` — human report
- `C:\OsintNeoAi\reports\sentinel\latest.json` — machine report
- Timestamped JSON archive per run

## Workflow When Invoked

1. Run `sentinel.py` full probe (no flags unless user specified).
2. Read exit code / `overall` field.
3. If **CRITICAL**:
   - VM/endpoint down → report which hop failed (SSH vs HTTP) and suggest
     `az vm get-instance-view` / restart steps (requires `az login`).
   - Gemini 429 or quota ≤5% → advise switching keys/backing off; log the
     incident to the task system ledger.
4. If **WARN** → report remaining % and reset time.
5. If **OK** → one line: all green with the tightest quota remaining.

## Browser Step (optional)

Only when API probes are insufficient (e.g. user explicitly wants a screenshot
of a portal dashboard): launch the `/browser` subagent (Chrome DevTools MCP)
against the relevant console. Auth-gated dashboards (Azure Portal, Google AI
Studio) require an existing signed-in browser profile — do not attempt
credential entry. Prefer API probes; the browser is the fallback, not
the default.

## Requirements

- Python 3 (repo `.venv`), `ssh` keys in `~/.ssh/config`
- `gh` authenticated (GitHub quota), `gcloud` (GCP quota)
- `az login` for Azure section (degrades gracefully to `not_auth`)
- `.env` in repo root with `GEMINI_API_KEY`
