# TOOLS_LOG — OsintNeoAi tool inventory

Log of OSINT/AI tools for this project: what is installed, where, and its status.
Entries are only marked **installed** after the tool has actually been run and verified.

## Installed & verified

| Tool | Location | Runtime | Status | Verified |
|---|---|---|---|---|
| scanner/redact.py — fail-closed redaction & citation auditor | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed (local copy: ~/workspace/osintneoai/scanner/) | 2026-10-19 — ran in full pipeline |
| scanner/verify_public.py — post-scan verifier (secrets, SSNs, private IPs) | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed | 2026-10-19 — PASS on test input |
| scanner/sanitize_manifest.py — publish-safe manifest generator | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed | 2026-10-19 — ran in full pipeline |
| scanner/citation_report.py — citation coverage reporter | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed | 2026-10-19 — ran in full pipeline |
| scanner/run_scan.sh — pipeline runner | OsintNeoAi repo, `scanner/` | bash + python3 | Installed | 2026-10-19 — end-to-end run, exit 0 |

Dependencies: none beyond Python 3 standard library. No requirements.txt needed.

| Agent-Reach v1.5.0 — multi-platform reader CLI for AI agents (web, YouTube, RSS, GitHub, Twitter/X, Reddit, Facebook, Instagram, LinkedIn, Bilibili, Xiaohongshu, V2EX and more) | https://github.com/Panniantong/Agent-Reach — installed at ~/workspace/tools/Agent-Reach/ (venv) | Python 3.12 venv; deps requests, feedparser, python-dotenv, loguru, pyyaml, rich, yt-dlp | Installed (base package only — optional browser-cookie extraction NOT installed or used) | 2026-10-20 — `agent-reach --help` OK; `agent-reach doctor`: 4/16 channels live out of the box (web via Jina Reader, RSS/Atom, V2EX, Bilibili search). yt-dlp 2026.08.19 present in venv (doctor checks system PATH, so it flags YouTube). GitHub channel needs gh auth; Twitter/Reddit/Facebook/Instagram need login-state setup not yet configured. Run: ~/workspace/tools/Agent-Reach/.venv/bin/agent-reach <command> |

## Logged — not installed

| Tool | Source | Notes |
|---|---|---|
| Edge0 (streaming MoE inference framework) | https://github.com/Edge0-AI/Edge0 (Apache 2.0; arXiv 2609.18063) — cloned for reference at ~/workspace/tools/Edge0/ | NOT installed: no Linux runtime. Python path is macOS Apple Silicon + MLX only; native engines exist for macOS, iOS, Android, Windows (C++/Vulkan). Runs only its own prepared MoE checkpoints (Edge0-35B-A3B-preview, ~2.9 GB active RAM via SSD expert offload; Edge0-8B-A1B-preview) — cannot run dense models such as Qwen3.8-27B. Revisit on the owner's Windows PC, Android phone, or any Apple Silicon machine. |
| Qwen3.8-27B-Uncensored (abliterated builds of Qwen/Qwen3.8-27B) | Hugging Face — junafinity/Qwen-3.8-27B-Uncensored (bf16, ~52 GB, Apache 2.0); FP8 build ~30.9 GB; huihui-ai GGUF quants ~12–19 GB — surfaced via Facebook Reel, 2026-10-20 | Real artifact, verified to exist. NOT installed: cannot run on the Muse VM (2 cores, 7 GB RAM, no GPU). Smallest usable quants need ~12 GB+ RAM; FP8 needs a GPU box. Revisit on hardware with 16 GB+ RAM (GGUF) or a CUDA GPU (FP8/vLLM). |
| OX Alpha / "OpenFinisher" | Facebook Reel claim, 2026-10-19 | Unverified hype claim; no installable artifact identified. Logged for awareness only. |
| OSINTNeoAiCLI (Tonypost949/OSINTNeoAiCLI) | User's own repo (Python) | Sibling project; not yet installed or audited here. |

## Verification runs

- 2026-10-19: run_scan.sh against a Facebook post export (Anthony Greb, Nancy Guthrie case). Result: published, no redactions, verify PASS, citation gap = missing legal_section. Outputs in local output/ (PUBLIC_MANIFEST.json, VERIFY_REPORT.json, CITATION_GAPS.csv).
- 2026-10-20: Agent-Reach v1.5.0 installed per install_gh_repo skill (hype rule) — vetted (MIT, standard deps, cookie extraction left out), cloned to ~/workspace/tools/Agent-Reach, pip-installed into venv, verified via --help and doctor (4/16 channels live).
