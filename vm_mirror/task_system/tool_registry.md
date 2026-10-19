# TOOL REGISTRY

AI-authored tools (Law 1). One row per tool.

| Date | Tool | Skill | Location | Purpose |
|---|---|---|---|---|
| 2026-10-18 | lf_weblink_fetch.py | laserfiche-weblink-records | `C:\Amd949609_Antigravity_v1\tools\records_portal\lf_weblink_fetch.py` (+ `/home/osintneoai/tools/records_portal/`) | Laserfiche WebLink records retrieval: WARP egress unblock, proxy+browser fetch, ASP.NET endpoint probe, Evidence-Locker output + mirrors |
| 2026-10-19 | run_heretic_auto.py + heretic venv | (none) | `/home/osintneoai/tools/heretic/` (mirror to `C:\Amd949609_Antigravity_v1\tools\heretic\` pending Windows-side sync) | Heretic (p-e-w/heretic) LLM abliteration: CPU torch + heretic-llm v1.4.0 venv, non-interactive driver (COLAB_GPU=1 line-prompt mode), auto best-trial pick, auto save, retry, status.json; validated via mock tests; smoke run Qwen3-0.6B launched 2026-10-19 |

| 2026-10-19 | gemini_ocr.py | - | `/home/osintneoai/tools/records_portal/gemini_ocr.py` | Cloud OCR via Gemini native PDF vision. Default model `gemini-3.5-flash`; global `--rpm` limiter (free tier is a **per-project** 20 req/min ceiling shared across models); self-healing resume that repairs only `[OCR-ERROR pages A-B]` chunks on re-run; `--outdir` fallback to `$HOME/evidence_ocr` when the source tree is read-only; works without pypdf by sending the whole file. |
| 2026-10-19 | find_imageonly_pdfs.py | - | `/home/osintneoai/tools/records_portal/find_imageonly_pdfs.py` | pypdf triage: ranks PDFs by extractable chars/page so cloud OCR quota is spent only on genuinely unreadable scans. Found **54 image-only PDFs** of 296 in the local evidence tree. `--csv` for the full inventory. |
| 2026-10-19 | sync_opencode_vm.sh (RETIRED) | - | (was PC-side `~/tools/sync_opencode_vm.sh` on Kali WSL) | sqlite-backup-API + rsync PC->VM environment sync that migrated this agent to vm-osintneoai-01. **RETIRED as a push tool at 2026-10-19T00:40Z**: the session now executes on the VM and the VM DB is authoritative; re-running it would `--delete` the live VM conversation history. See `/home/osintneoai/tools/PUSH_SYNC_HAZARD.md`. If PC-local opencode is ever needed again, rebuild as VM->PC pull. |
